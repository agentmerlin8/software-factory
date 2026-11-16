"""Workspace policy — per-workspace levers (OC-9 configurable merge/review).

The factory OWNS its gates. Platform settings (Copilot auto-approval) are
NOT the policy — the factory decides whether to request a bot review at
all, per workspace. OC-17's blanket "Copilot approval required" is hereby
scoped to the workspace that ratified it (todo-demo), not universal.

Levers (workspace.json at the state-repo root or runs/<run>/):
  copilot_review: "required" | "optional" | "off"
      required — request Copilot, wait for APPROVED before human merge
      optional — request Copilot, treat findings as input, don't block on
                 the APPROVED state (factory's own review lane is the gate)
      off      — never request Copilot; factory review lane alone gates
  human_merge: true (v1 mode 1; modes 2/3 are OC-9 north-star, cut)

Default: copilot_review="optional" — the factory's deterministic gates +
fresh-context cross-family review are the real gate (proven in SKEL-1);
the bot is a second opinion, not a dependency on a platform UI setting.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

VALID_COPILOT = ("required", "optional", "off")


@dataclass
class WorkspacePolicy:
    copilot_review: str = "optional"
    human_merge: bool = True

    def __post_init__(self):
        if self.copilot_review not in VALID_COPILOT:
            raise ValueError(
                f"copilot_review must be one of {VALID_COPILOT}, "
                f"got {self.copilot_review!r}")

    @property
    def request_copilot(self) -> bool:
        return self.copilot_review in ("required", "optional")

    @property
    def block_on_copilot_approval(self) -> bool:
        return self.copilot_review == "required"


def load_policy(path: Path | None = None) -> WorkspacePolicy:
    """Load workspace.json policy; missing file = defaults (fail-open to the
    safe default: optional bot review, human merge)."""
    if path is None:
        path = Path("workspace.json")
    if not path.exists():
        return WorkspacePolicy()
    data = json.loads(path.read_text(encoding="utf-8"))
    return WorkspacePolicy(
        copilot_review=data.get("copilot_review", "optional"),
        human_merge=data.get("human_merge", True),
    )
