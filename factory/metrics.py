"""Metrics — per-story comparison + process-overhead-ratio (OC-16).

Nulls render as "not recorded", never 0 (a missing measurement is not a
zero measurement). The headline metric is non-coder tokens / coder tokens.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .ledger import Ledger


@dataclass
class StoryMetrics:
    story: str
    coder_tokens: int = 0
    noncoder_tokens: int = 0
    wall_s: float = 0.0
    human_min: float | None = None
    cost_usd: float = 0.0
    defects: int = 0
    dispatches: int = 0

    @property
    def overhead_ratio(self) -> float | None:
        if self.coder_tokens == 0:
            return None
        return self.noncoder_tokens / self.coder_tokens


def harvest(ledger: Ledger) -> dict[str, StoryMetrics]:
    """Fold dispatch_completed + defect_found events into per-story metrics."""
    out: dict[str, StoryMetrics] = {}
    for row in ledger.read():
        story = row.get("story")
        if not story:
            continue
        m = out.setdefault(story, StoryMetrics(story=story))
        ev = row["event"]
        if ev == "dispatch_completed":
            m.dispatches += 1
            tok = row.get("tokens") or {}
            total = (tok.get("in") or 0) + (tok.get("out") or 0)
            role = row.get("role")
            if role == "coder":
                m.coder_tokens += total
            else:
                m.noncoder_tokens += total
            if row.get("wall_s"):
                m.wall_s += row["wall_s"]
            if row.get("cost_usd"):
                m.cost_usd += row["cost_usd"]
            if row.get("human_min") is not None:
                m.human_min = (m.human_min or 0.0) + row["human_min"]
        elif ev == "correction":
            d = row.get("detail") or {}
            tok = d.get("tokens") or {}
            total = (tok.get("in") or 0) + (tok.get("out") or 0)
            if total:
                # corrections re-attribute a dispatch's usage (path-bug recovery)
                role = row.get("role")
                if role == "coder":
                    m.coder_tokens += total
                else:
                    m.noncoder_tokens += total
                if d.get("cost_usd"):
                    m.cost_usd += d["cost_usd"]
        elif ev == "defect_found":
            m.defects += 1
        elif ev == "human_merged" and row.get("human_min") is not None:
            m.human_min = (m.human_min or 0.0) + row["human_min"]
    return out


def _fmt(v, suffix: str = "") -> str:
    if v is None:
        return "not recorded"
    if isinstance(v, float):
        return f"{v:.2f}{suffix}"
    return f"{v}{suffix}"


def render_comparison(factory: dict[str, StoryMetrics],
                      control: dict[str, StoryMetrics]) -> str:
    stories = sorted(set(factory) | set(control))
    lines = ["# SKEL-1 comparison — factory vs control", ""]
    lines.append("| story | arm | tokens (coder/non) | overhead | wall_s | human_min | defects | cost_usd |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for s in stories:
        for arm, data in (("factory", factory), ("control", control)):
            m = data.get(s)
            if m is None:
                lines.append(f"| {s} | {arm} | not recorded | — | — | — | — | — |")
                continue
            ratio = _fmt(m.overhead_ratio)
            lines.append(
                f"| {s} | {arm} | {m.coder_tokens}/{m.noncoder_tokens} "
                f"| {ratio} | {_fmt(m.wall_s)} | {_fmt(m.human_min)} "
                f"| {m.defects} | {_fmt(m.cost_usd)} |")
    lines.append("")
    lines.append("## Headline: process-overhead-ratio (non-coder / coder tokens)")
    for arm, data in (("factory", factory), ("control", control)):
        ct = sum(m.coder_tokens for m in data.values())
        nt = sum(m.noncoder_tokens for m in data.values())
        ratio = f"{nt/ct:.3f}" if ct else "not recorded (no coder tokens)"
        lines.append(f"- {arm}: {nt} / {ct} = {ratio}")
    lines.append("")
    lines.append("## Kill criterion (OC-16)")
    lines.append("Factory must win on human-minutes OR escaped defects at a")
    lines.append("cost multiple the owner accepts — else STOP and reconsider.")
    return "\n".join(lines) + "\n"


def write_comparison(path: Path, factory: dict[str, StoryMetrics],
                     control: dict[str, StoryMetrics]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_comparison(factory, control), encoding="utf-8")
    return path


def dispatch_audit(ledger: Ledger) -> dict:
    """Fail-closed metering audit (SKEL-5 MEA-1, OC-16).

    Every dispatch_completed that RAN (outcome != 'fail' at launch) must
    carry tokens (non-zero), model, outcome, and wall_s. A dispatch missing
    any is an UNMETERED dispatch = a process defect, counted and named.

    Two honest exclusions:
    - a dispatch that FAILED TO LAUNCH (outcome='fail' with no tokens, e.g.
      E2BIG at spawn) never consumed tokens — not a metering defect;
    - tokens recovered by a later `correction` event for the same
      story/role count as metered (the usage-path-bug recovery pattern).
    """
    rows = ledger.read()
    # corrections that re-attribute usage to a story/role
    corrected = set()
    for row in rows:
        if row.get("event") == "correction":
            d = row.get("detail") or {}
            tok = d.get("tokens") or {}
            if (tok.get("in") or 0) + (tok.get("out") or 0):
                corrected.add((row.get("story"), row.get("role")))
    total = 0
    defects = []
    for row in rows:
        if row.get("event") != "dispatch_completed":
            continue
        total += 1
        tok = row.get("tokens") or {}
        has_tokens = bool((tok.get("in") or 0) + (tok.get("out") or 0))
        # failed-to-launch: never ran, no tokens expected
        if row.get("outcome") == "fail" and not has_tokens and not row.get("wall_s"):
            continue
        missing = []
        if not has_tokens and (row.get("story"), row.get("role")) not in corrected:
            missing.append("tokens")
        if not row.get("model"):
            missing.append("model")
        if not row.get("outcome"):
            missing.append("outcome")
        if not row.get("wall_s"):
            missing.append("wall_s")
        if missing:
            defects.append(
                f"{row.get('story')}/{row.get('role')} @ {row.get('ts')}: "
                f"missing {', '.join(missing)}")
    return {"total": total, "metered": total - len(defects),
            "unmetered": len(defects), "defects": defects}


def cycle_time_split(ledger: Ledger) -> dict:
    """Per-story machine-wall vs human-min split (SKEL-5 MEA-1).

    machine_wall_s = sum of dispatch wall_s; human_min = recorded human
    attention (dispatch human_min + human_merged human_min). Unrecorded
    human time is None, never 0 (a missing measurement is not a zero).
    """
    out: dict[str, dict] = {}
    for row in ledger.read():
        story = row.get("story")
        if not story:
            continue
        s = out.setdefault(story, {"machine_wall_s": 0.0, "human_min": None})
        if row.get("event") == "dispatch_completed":
            if row.get("wall_s"):
                s["machine_wall_s"] += row["wall_s"]
            if row.get("human_min") is not None:
                s["human_min"] = (s["human_min"] or 0.0) + row["human_min"]
        elif row.get("event") == "human_merged":
            if row.get("human_min") is not None:
                s["human_min"] = (s["human_min"] or 0.0) + row["human_min"]
    return out