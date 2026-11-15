"""Escalation adjudication — is a human ACTUALLY required? (OC-10 made concrete)

Randy's question (2026-11-15, on Copilot's round-8 "Human assessment is needed"):
is human review truly required, or can an agent resolve it?

OC-10 already says escalation is by DETERMINISTIC DECISION CLASS, not by a
model's self-reported confidence. A reviewer saying "human needed" is exactly
such a self-report — it is a CLAIM, and claims get executed before they are
believed (the lesson rounds 2-8 kept teaching).

The test that separates the two:
  A finding is AGENT-RESOLVABLE when an agent can (a) reproduce the defect with
  a deterministic probe, (b) apply a fix, and (c) prove the fix with the same
  probe — without needing a preference, a policy, or an irreversible action.
  A finding needs a HUMAN when resolving it requires choosing between values
  (scope, cost, product trade-off), accepting residual risk, or taking an
  action no agent is authorized to take.

"Concurrent writes can lose data" sounds scary and human-shaped. It is not:
it is a reproducible interleaving with a mechanical fix and a falsifiable
test. Measured on round 8: reproduced (["FromB"], task A lost), fixed
(merge-on-write), proven (true-interleave probe passes). Zero human judgment.

This module encodes that adjudication so the factory stops escalating on
adjectives.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Classes an agent can close on evidence alone.
AGENT_RESOLVABLE = frozenset({
    "contrast-text", "contrast-gradient-state", "contrast-selection",
    "contrast-focus-indicator", "untrusted-boundary", "unhandled-io-failure",
    "silent-mutation", "stale-live-region", "test-gap", "state-integrity",
    "concurrency-lost-update",
})

# Classes that genuinely require a human decision.
HUMAN_REQUIRED = frozenset({
    "scope-change",          # differs from the PRD: only the owner re-scopes
    "cost-tradeoff",         # spend/latency/quality trade-off is a preference
    "product-behavior",      # which behavior is *desired* is not derivable
    "security-policy",       # trust boundary / authorization policy
    "irreversible-action",   # data migration, deletion, publish, deploy
    "dependency-addition",   # new external dependency (OC-10 class list)
    "reviewer-disagreement", # two reviewers conflict: adjudication is a call
})

# Reviewer phrasing that ASSERTS human need. These are claims, not verdicts.
_HUMAN_CLAIM = re.compile(
    r"human (assessment|review|judgment|decision|evaluation) (is |may be )?"
    r"(needed|required|recommended|necessary)|"
    r"needs? (a )?human|requires? human|manual (review|verification)|"
    r"cannot be (automatically|deterministically) (verified|tested)",
    re.I)

# Evidence that a finding is mechanically reproducible.
_REPRODUCIBLE = re.compile(
    r"race|concurren|interleav|lost update|clobber|stale|crash|throw|"
    r"contrast|wcag|aria|announce|null|undefined|malformed|duplicate|"
    r"overflow|off-by-one|leak", re.I)


@dataclass
class Adjudication:
    """The verdict on one finding, with the evidence that produced it."""
    needs_human: bool
    reason: str
    decision_class: str
    reviewer_claimed_human: bool = False
    evidence: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "needs_human": self.needs_human,
            "reason": self.reason,
            "decision_class": self.decision_class,
            "reviewer_claimed_human": self.reviewer_claimed_human,
            "evidence": self.evidence,
        }


def adjudicate(*, summary: str, klass: str | None = None,
               reproduced: bool = False, fix_verified: bool = False,
               irreversible: bool = False,
               changes_scope: bool = False) -> Adjudication:
    """Decide whether a finding needs a human, from evidence not adjectives.

    `reproduced` / `fix_verified` must come from ACTUALLY RUNNING a probe —
    passing them on a reviewer's say-so re-introduces the self-report problem
    this function exists to remove.
    """
    claimed = bool(_HUMAN_CLAIM.search(summary))
    evidence: list[str] = []
    if claimed:
        evidence.append("reviewer asserted human assessment is needed (a claim)")

    # Hard human classes win regardless of reproducibility.
    if irreversible:
        return Adjudication(True, "irreversible action: no agent is authorized",
                            "irreversible-action", claimed,
                            evidence + ["action cannot be undone by retry"])
    if changes_scope:
        return Adjudication(True, "changes agreed scope: owner re-scopes",
                            "scope-change", claimed,
                            evidence + ["differs from the approved design/PRD"])
    if klass in HUMAN_REQUIRED:
        return Adjudication(True, f"decision class {klass} requires an owner call",
                            klass, claimed, evidence)

    # Mechanically closable: demand the evidence, ignore the adjective.
    if klass in AGENT_RESOLVABLE or _REPRODUCIBLE.search(summary):
        cls = klass if klass in AGENT_RESOLVABLE else "state-integrity"
        if reproduced and fix_verified:
            evidence.append("defect reproduced by a deterministic probe")
            evidence.append("fix proven by the same probe")
            return Adjudication(
                False,
                "agent-resolvable: reproduced and fix verified by execution"
                + (" — reviewer's human-need claim overridden by evidence"
                   if claimed else ""),
                cls, claimed, evidence)
        if reproduced:
            evidence.append("defect reproduced; fix not yet verified")
            return Adjudication(
                False, "agent-resolvable: reproduced, verify the fix next",
                cls, claimed, evidence)
        evidence.append("no probe run yet — reproduce before escalating")
        return Adjudication(
            False,
            "agent-resolvable in principle: run a probe before claiming "
            "human need", cls, claimed, evidence)

    # Unknown class: do NOT silently escalate, and do NOT silently close.
    return Adjudication(
        True, "unclassified finding: triage to a decision class first",
        "unclassified", claimed,
        evidence + ["neither a known mechanical class nor a known owner class"])