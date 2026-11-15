"""JSONL ledger — schema v0, hash-chained, append-only.

Every event pins repo@sha when it concerns product code. The chain (`prev`
= sha256 of the previous raw line) makes tampering detectable; corrections
are new `correction` events, never edits (runtime-agnostic-factory law).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

SCHEMA = 0

EVENT_TYPES = frozenset({
    "run_started", "design_approved", "story_planned",
    "dispatch_sealed", "dispatch_started", "dispatch_completed",
    "gate_passed", "gate_failed", "review_completed",
    "pr_opened", "human_merged", "story_done", "defect_found",
    "run_completed", "correction",
    # SKEL-4a review-loop events (docs/plans/skel-4a-review-loop-automation)
    "review_detected", "finding_verified", "finding_dispositioned",
    "remediation_pushed", "gate_extended", "review_requested",
    "loop_converged",
    # SKEL-2 intake events (docs/plans/skel-2-intake-spike)
    "intake_approved",
})

REQUIRED_FIELDS = ("schema", "ts", "event")


class LedgerError(ValueError):
    """A malformed or invalid ledger row/event."""


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _line_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def canonical(event: dict[str, Any]) -> str:
    """Deterministic single-line JSON for an event (sorted keys)."""
    return json.dumps(event, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def validate_event(event: dict[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        if field not in event:
            raise LedgerError(f"missing required field: {field}")
    if event["schema"] != SCHEMA:
        raise LedgerError(f"unsupported schema: {event['schema']} (want {SCHEMA})")
    if event["event"] not in EVENT_TYPES:
        raise LedgerError(f"unknown event type: {event['event']}")
    if not isinstance(event["ts"], str) or not event["ts"]:
        raise LedgerError("ts must be a non-empty string")


@dataclass
class Ledger:
    path: Path

    def __post_init__(self) -> None:
        self.path = Path(self.path)

    # -- write -----------------------------------------------------------
    def append(self, event: str, *, story: str | None = None,
               role: str | None = None, repo: str | None = None,
               sha: str | None = None, model: str | None = None,
               tokens: dict | None = None, cost_usd: float | None = None,
               wall_s: float | None = None, human_min: float | None = None,
               outcome: str | None = None, detail: dict | None = None) -> dict:
        """Append one event; returns the stored row (with prev hash)."""
        if event not in EVENT_TYPES:
            raise LedgerError(f"unknown event type: {event}")
        prev = self._last_hash()
        row: dict[str, Any] = {
            "schema": SCHEMA, "ts": _now(), "event": event,
            "story": story, "role": role, "repo": repo, "sha": sha,
            "model": model, "tokens": tokens, "cost_usd": cost_usd,
            "wall_s": wall_s, "human_min": human_min, "outcome": outcome,
            "detail": detail or {}, "prev": prev,
        }
        validate_event(row)
        raw = canonical(row)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(raw + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        return row

    def _last_hash(self) -> str | None:
        last = None
        if self.path.exists():
            with open(self.path, encoding="utf-8") as fh:
                for line in fh:
                    if line.strip():
                        last = line.rstrip("\n")
        return _line_hash(last) if last is not None else None

    # -- read ------------------------------------------------------------
    def read(self, *, verify_chain: bool = True) -> list[dict]:
        rows = list(self._iter_rows())
        if verify_chain:
            self._verify_chain(rows)
        return rows

    def _iter_rows(self) -> Iterator[dict]:
        if not self.path.exists():
            return
        with open(self.path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise LedgerError(f"line {n}: invalid JSON: {exc}") from exc
                validate_event(row)
                yield row

    def _verify_chain(self, rows: list[dict]) -> None:
        if not rows:
            return
        prev: str | None = None
        # Re-derive hashes from the raw file to compare against `prev`.
        raws = [ln.rstrip("\n") for ln in
                self.path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        for n, (row, raw) in enumerate(zip(rows, raws)):
            if row.get("prev") != prev:
                raise LedgerError(
                    f"line {n+1}: broken chain (prev={row.get('prev')!r}, "
                    f"expected {prev!r})")
            prev = _line_hash(raw)

    # -- derived views ---------------------------------------------------
    def events(self, event: str) -> list[dict]:
        return [r for r in self.read() if r["event"] == event]

    def story_rows(self, story: str) -> list[dict]:
        return [r for r in self.read() if r.get("story") == story]