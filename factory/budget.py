"""Budget enforcement — SKEL-5 MEA-2 (OC-16).

Controller-side spend cap + job timeout + dispatch refusal at ceiling.
NOT agent self-report: the controller holds the budget and refuses a
dispatch that would exceed it, before any model tokens are spent. The
agent never decides its own budget.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class BudgetError(RuntimeError):
    """A dispatch was refused because it would exceed the budget."""


@dataclass
class Budget:
    spend_cap_usd: float
    job_timeout_s: int
    spent_usd: float = 0.0

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.spend_cap_usd - self.spent_usd)

    def record_spend(self, usd: float) -> None:
        """Record actual spend after a dispatch completes."""
        if usd < 0:
            raise ValueError("spend cannot be negative")
        self.spent_usd += usd

    def check_dispatch(self, *, estimated_usd: float) -> None:
        """Refuse a dispatch whose estimated cost would exceed the cap.

        Fail-closed: at or over the ceiling, refuse. The estimate is a
        conservative pre-check; actual spend is recorded post-dispatch.
        """
        if self.spent_usd + estimated_usd > self.spend_cap_usd:
            raise BudgetError(
                f"dispatch refused: spent {self.spent_usd:.4f} + estimated "
                f"{estimated_usd:.4f} > cap {self.spend_cap_usd:.4f} USD")

    def effective_timeout(self, *, requested_s: int) -> int:
        """Cap a requested job timeout at the budget's ceiling."""
        return min(requested_s, self.job_timeout_s)
