"""Seeded-defect calibration harness — SKEL-5 MEA-3 (OC-16, ECN-3).

Plants 10 known defects (ground-truth labels) spanning the classes the
factory actually hit, then measures reviewer catch-rate across three modes:
same-session, fresh same-family, fresh cross-family. A reviewer that can't
catch a known planted defect isn't trusted to route (calibration BEFORE
routing starts).

This module builds the fixture + scoring; the actual model runs are the
experiment (dispatched separately). Scoring is pure: given a reviewer's
flagged defect IDs and the ground truth, compute catch-rate + precision.
"""
from __future__ import annotations

from dataclasses import dataclass

# The 10 planted defects, each with a stable ID, class, and the file/line
# where it lives in the fixture. These mirror the real findings-log classes.
SEEDED_DEFECTS = [
    {"id": "SD-01", "klass": "concurrency-lost-update",
     "desc": "mutation overwrites from a stale snapshot (no write-boundary re-read)",
     "file": "store.ts", "hint": "addTask/toggleTask read once then write"},
    {"id": "SD-02", "klass": "self-certifying-test",
     "desc": "regression test passes on the defective code (leading null masks the guard)",
     "file": "store.test.ts", "hint": "corrupt-data test payload led by null"},
    {"id": "SD-03", "klass": "untrusted-boundary",
     "desc": "stored array elements not validated (isTask accepts empty title)",
     "file": "store.ts", "hint": "isTask missing title.length check"},
    {"id": "SD-04", "klass": "silent-mutation",
     "desc": "successful delete updates list but announces nothing to screen readers",
     "file": "App.tsx", "hint": "handleDelete success path has no setAnnouncement"},
    {"id": "SD-05", "klass": "stale-live-region",
     "desc": "same-title adds produce identical announcement text (no re-announce)",
     "file": "App.tsx", "hint": "add announcement lacks a distinguishing count/sequence"},
    {"id": "SD-06", "klass": "contrast-text",
     "desc": "muted text below WCAG AA 4.5:1 on its background",
     "file": "theme.css", "hint": ".muted color too light on paper"},
    {"id": "SD-07", "klass": "scope-creep",
     "desc": "unrequested theme restyle shipped with no AC behind it",
     "file": "theme.css", "hint": "extra gradient/theme rules beyond the brief"},
    {"id": "SD-08", "klass": "unhandled-io-failure",
     "desc": "storage write failure swallowed silently (no alert, no revert)",
     "file": "App.tsx", "hint": "toggle catch block empty"},
    {"id": "SD-09", "klass": "test-gap",
     "desc": "named test asserts presence but not the actual ordering AC",
     "file": "App.test.tsx", "hint": "list test checks count not order"},
    {"id": "SD-10", "klass": "state-integrity",
     "desc": "off-by-one in filter: completed filter includes one active task",
     "file": "store.ts", "hint": "filterTasks completed branch uses wrong predicate"},
]

SEEDED_IDS = {d["id"] for d in SEEDED_DEFECTS}


@dataclass
class CatchRate:
    mode: str
    caught: int
    total: int
    false_positives: int
    flagged: int

    @property
    def catch_rate(self) -> float:
        return self.caught / self.total if self.total else 0.0

    @property
    def precision(self) -> float:
        return self.caught / self.flagged if self.flagged else 0.0


def score_review(mode: str, flagged_ids: list[str]) -> CatchRate:
    """Score a reviewer's flagged defect IDs against ground truth.

    caught = flagged IDs that are real seeded defects; false_positives =
    flagged IDs that aren't seeded defects. Pure — no model calls.
    """
    flagged = set(flagged_ids)
    caught = len(flagged & SEEDED_IDS)
    fp = len(flagged - SEEDED_IDS)
    return CatchRate(mode=mode, caught=caught, total=len(SEEDED_DEFECTS),
                     false_positives=fp, flagged=len(flagged))


def render_calibration(results: list[CatchRate]) -> str:
    lines = ["# Seeded-defect catch-rate calibration (SKEL-5 MEA-3)", "",
             "| mode | caught/10 | catch-rate | false-pos | precision |",
             "|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r.mode} | {r.caught}/{r.total} | {r.catch_rate:.0%} "
                     f"| {r.false_positives} | {r.precision:.0%} |")
    lines.append("")
    lines.append("Calibration gates routing (ECN-3): a reviewer that can't catch")
    lines.append("known planted defects isn't trusted to route. Cross-family")
    lines.append("advantage measured here justifies the factory's review routing.")
    return "\n".join(lines) + "\n"
