"""Review findings log — a mineable record of what reviewers catch (OC-8, OC-16).

Randy's idea (2026-11-15): keep a log of Copilot findings so we can measure
improvement over time and find recurring problems.

Design:
- One append-only JSONL log, separate from the run ledger (it spans projects
  and outlives any single run — that is the OC-8 "mineable state" shape).
- Every finding is classified by CLASS (a stable slug), not by its wording.
  Recurrence is only visible if the same defect class maps to the same key
  across rounds, repos, and reviewers.
- Each row records who caught it, whether OUR gate/review had already passed
  it (an escape), whether a deterministic check now covers the class, and the
  fix sha. That is what makes "did we improve?" answerable rather than anecdotal.

Derived questions this answers:
- escape rate over time (are we shipping fewer defects per story?)
- recurring classes (what keeps coming back?)
- gate coverage (which classes are now mechanically prevented?)
- time-to-clean per PR / rounds-to-converge (is the loop getting cheaper?)
- reviewer value (what does the bot catch that our own review misses?)
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = 0

# Stable defect classes. Keys are intentionally coarse: a class must survive
# rewording by a different reviewer, or recurrence is invisible.
CLASSES = {
    "contrast-text": "Text below WCAG AA 4.5:1 against its background",
    "contrast-gradient-state": "Text on a gradient/interactive state below 4.5:1",
    "contrast-selection": "::selection text below 4.5:1",
    "contrast-focus-indicator": "Focus indicator below the 3:1 non-text minimum",
    "untrusted-boundary": "External data parsed without element validation",
    "unhandled-io-failure": "I/O failure uncaught: action aborts, no feedback",
    "silent-mutation": "State change not announced to assistive tech",
    "stale-live-region": "Live region text unchanged, so no re-announcement",
    "test-gap": "Named test does not assert the acceptance criterion",
    "false-positive": "Reviewer claim refuted by execution (not a real defect)",
    "state-integrity": "Duplicate/racy mutation corrupts state",
    "scope-creep": "Unrequested work shipped without its own ACs",
    "other": "Unclassified — add a class when a pattern recurs",
}

# Ordered patterns: first match wins, most specific first.
_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("contrast-selection", re.compile(r"::selection|selected task text|selection background", re.I)),
    ("contrast-focus-indicator", re.compile(r"focus.{0,30}(outline|indicator|ring)|outline.{0,30}focus", re.I)),
    ("contrast-gradient-state", re.compile(r"gradient|hover|brightness|active state", re.I)),
    ("contrast-text", re.compile(r"contrast|WCAG|4\.5:1|3:1|readab", re.I)),
    ("stale-live-region", re.compile(r"(unchanged|identical|same|repeat\w*).{0,60}(live.region|announce)|"
                                     r"live.region.{0,60}(unchanged|identical|repeat)", re.I)),
    ("silent-mutation", re.compile(r"announce|screen.?reader|live.region|aria-live|assistive", re.I)),
    ("untrusted-boundary", re.compile(r"malformed|validate.{0,30}(stored|entries|entry)|"
                                      r"isArray|null.{0,20}crash|corrupt", re.I)),
    ("unhandled-io-failure", re.compile(r"storage.{0,30}(fail|full|quota|block)|throws?|uncaught|"
                                        r"persistence.{0,20}fail", re.I)),
    ("test-gap", re.compile(r"test.{0,40}(does not|doesn't|missing|never assert)|regression test", re.I)),
    ("state-integrity", re.compile(r"duplicate|double.?submit|race|idempot", re.I)),
    ("scope-creep", re.compile(r"unrelated|not required by|exceeds the.{0,20}brief|out of scope", re.I)),
]


def classify(text: str, *, verified: str | None = None) -> str:
    """Map a finding's wording to a stable class slug.

    A claim REFUTED by execution is recorded as `false-positive` regardless of
    its wording: reviewer precision is a metric we want to mine, and burying
    refuted claims in `other` hides it.
    """
    if verified == "refuted":
        return "false-positive"
    for slug, pat in _PATTERNS:
        if pat.search(text):
            return slug
    return "other"


@dataclass
class Finding:
    """One reviewer finding, normalized for mining."""
    ts: str
    repo: str
    pr: int
    round: int
    source: str                      # copilot | cross-family | human | gate
    klass: str
    severity: str                    # blocker | major | minor | nit | unknown
    summary: str
    path: str | None = None
    head_sha: str | None = None      # the head the reviewer saw
    escaped_gate: bool = False       # our deterministic gate had passed it
    escaped_review: bool = False     # our own reviewer had passed it
    verified: str = "unverified"     # executed | reasoned | refuted | unverified
    disposition: str = "open"        # fixed | rejected | deferred | open
    fix_sha: str | None = None
    gate_check: str | None = None    # deterministic check now covering the class
    comment_id: int | None = None
    schema: int = SCHEMA
    extra: dict[str, Any] = field(default_factory=dict)


class FindingsLog:
    """Append-only JSONL log of reviewer findings, spanning runs and repos."""

    def __init__(self, path: Path):
        self.path = Path(path)

    def _key(self, row: dict) -> tuple:
        """Identity of a finding: same PR/round/source/wording = same finding.

        Re-logging (a retried closeout, a resumed worker) must not inflate the
        counts — recurrence metrics are only trustworthy if appends dedupe.
        """
        return (row.get("repo"), row.get("pr"), row.get("round"),
                row.get("source"), row.get("summary"))

    def append(self, finding: Finding) -> Finding:
        if finding.klass not in CLASSES:
            raise ValueError(f"unknown class: {finding.klass}")
        row = asdict(finding)
        key = self._key(row)
        for existing in self.read():
            if self._key(existing) == key:
                return finding  # idempotent: already recorded
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(finding), sort_keys=True,
                                ensure_ascii=False) + "\n")
            fh.flush()
        return finding

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        rows = []
        for n, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"findings log line {n}: {exc}") from exc
        return rows

    # -- mining ----------------------------------------------------------
    def by_class(self) -> Counter:
        return Counter(r["klass"] for r in self.read())

    def recurring(self, min_count: int = 2) -> list[tuple[str, int]]:
        return [(k, n) for k, n in self.by_class().most_common() if n >= min_count]

    def escape_rate_by_round(self) -> dict[int, dict[str, int]]:
        """Per round: total findings vs those that escaped our own checks."""
        out: dict[int, dict[str, int]] = defaultdict(
            lambda: {"total": 0, "escaped_gate": 0, "escaped_review": 0, "fixed": 0})
        for r in self.read():
            b = out[r["round"]]
            b["total"] += 1
            b["escaped_gate"] += bool(r.get("escaped_gate"))
            b["escaped_review"] += bool(r.get("escaped_review"))
            b["fixed"] += (r.get("disposition") == "fixed")
        return dict(sorted(out.items()))

    # Not gate candidates: a refuted claim is a reviewer-precision metric,
    # and unclassified rows need a class before they need a check.
    _NOT_GATED = frozenset({"false-positive", "other"})

    def uncovered_classes(self) -> list[str]:
        """Real defect classes with NO deterministic check yet — the backlog."""
        covered: dict[str, bool] = {}
        for r in self.read():
            k = r["klass"]
            if k in self._NOT_GATED:
                continue
            covered[k] = covered.get(k, False) or bool(r.get("gate_check"))
        return sorted(k for k, has in covered.items() if not has)

    def reviewer_precision(self) -> dict[str, dict[str, int]]:
        """Per source: real defects vs claims refuted by execution."""
        out: dict[str, dict[str, int]] = defaultdict(
            lambda: {"real": 0, "refuted": 0})
        for r in self.read():
            b = out[r["source"]]
            if r["klass"] == "false-positive" or r.get("verified") == "refuted":
                b["refuted"] += 1
            else:
                b["real"] += 1
        return dict(out)

    def by_source(self) -> Counter:
        return Counter(r["source"] for r in self.read())

    def render(self) -> str:
        rows = self.read()
        if not rows:
            return "# Review findings\n\nNo findings recorded yet.\n"
        lines = ["# Review findings — mined view", "",
                 f"{len(rows)} findings · "
                 f"{len({r['repo'] for r in rows})} repo(s) · "
                 f"{len({(r['repo'], r['pr']) for r in rows})} PR(s)", ""]

        lines += ["## Recurring classes (what keeps coming back)", "",
                  "| class | count | meaning |", "|---|---|---|"]
        for k, n in self.by_class().most_common():
            lines.append(f"| `{k}` | {n} | {CLASSES.get(k, '')} |")

        lines += ["", "## Escape rate by round (are we improving?)", "",
                  "| round | findings | escaped gate | escaped review | fixed |",
                  "|---|---|---|---|---|"]
        for rnd, b in self.escape_rate_by_round().items():
            lines.append(f"| {rnd} | {b['total']} | {b['escaped_gate']} "
                         f"| {b['escaped_review']} | {b['fixed']} |")

        uncovered = self.uncovered_classes()
        lines += ["", "## Classes with NO deterministic check yet", ""]
        if uncovered:
            lines += [f"- `{k}` — {CLASSES.get(k, '')}" for k in uncovered]
            lines += ["", "_Each of these is a gate-extension candidate: the next "
                      "occurrence is preventable, not just fixable._"]
        else:
            lines.append("All observed classes are covered by a deterministic check.")

        lines += ["", "## Who catches what (and how often they are wrong)", "",
                  "| source | real defects | refuted by execution | precision |",
                  "|---|---|---|---|"]
        for src, b in sorted(self.reviewer_precision().items()):
            total = b["real"] + b["refuted"]
            pct = f"{100 * b['real'] / total:.0f}%" if total else "—"
            lines.append(f"| {src} | {b['real']} | {b['refuted']} | {pct} |")
        lines += ["", "_Precision here means 'survived execution', not 'was useful' — "
                  "a refuted claim still costs a verification cycle._"]
        return "\n".join(lines) + "\n"