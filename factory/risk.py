"""Risk-tiering — SKEL-5 MEA-2 (OC-16, OC-4 data-gated promotion).

Classify a story's review risk from its manifest size, AC count, and
structural signals. Small stories skip plan review and use one reviewer;
large stories get the full panel. This is the routing EVIDENCE producer —
actual promotion stays owner-gated (OC-4), never a flag flip.

Slice law (OC-17 / DEC-023): >=2 structural signals = a stacked story =
large regardless of line count (split before dispatch).
"""
from __future__ import annotations

# Structural signals (DEC-023): schema migration, backfill, new queue/worker,
# new external provider, controlled cutover. >=2 means stacked -> large.
LARGE_FILE_COUNT = 6      # >6 files = at least medium, likely large
LARGE_AC_COUNT = 6        # 6 ACs is the slice ceiling
MEDIUM_FILE_COUNT = 4     # >4 files = medium
MEDIUM_AC_COUNT = 4       # >4 ACs = medium


def classify_risk(*, manifest: list[str], ac_count: int,
                  structural_signals: int) -> str:
    """Return 'small' | 'medium' | 'large'."""
    if structural_signals >= 2:
        return "large"  # stacked story — split before dispatch
    files = len(manifest)
    if files > LARGE_FILE_COUNT or ac_count >= LARGE_AC_COUNT or structural_signals == 1 and files > MEDIUM_FILE_COUNT:
        return "large"
    if files > MEDIUM_FILE_COUNT or ac_count > MEDIUM_AC_COUNT or structural_signals == 1:
        return "medium"
    return "small"


def review_plan(tier: str) -> dict:
    """The review configuration for a risk tier.

    small  -> skip plan review, one reviewer (cross-family still applies)
    medium -> plan review, one reviewer
    large  -> plan review, cross-family panel (>=2 reviewers)
    """
    if tier == "small":
        return {"plan_review": False, "reviewers": 1}
    if tier == "medium":
        return {"plan_review": True, "reviewers": 1}
    if tier == "large":
        return {"plan_review": True, "reviewers": 2}
    raise ValueError(f"unknown risk tier: {tier!r}")
