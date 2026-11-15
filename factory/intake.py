"""Intake state machine — SKEL-2 INT-1 (harness-agnostic, OC-7).

The CLI owns intake STATE; any chat harness drives the conversation.
A session moves: questioning → validated → prd_ready. The PRD is
assembled DETERMINISTICALLY from the validated answer set — no model in
this module (the intake agent drafts the conversation; the CLI pins and
validates the answers and renders the one design doc, OC-13).

Fail-closed: a missing category, an empty value, an unknown session, or
generating before validation is an error, never a silent default.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

# The guided question flow covers exactly these categories (vision §3.2).
# acceptance/persistence/data_model were added after the INT-4 engineer
# review (round 1) flagged them as BLOCKERS a builder would have to invent.
REQUIRED_CATEGORIES = ("platform", "stack", "features", "look",
                       "persistence", "data_model", "acceptance")

_STATUSES = ("questioning", "validated", "prd_ready")


class IntakeError(ValueError):
    """An intake operation was refused (fail-closed)."""


@dataclass
class IntakeSession:
    session_id: str
    description: str
    status: str = "questioning"
    answers: dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "description": self.description,
            "status": self.status,
            "answers": self.answers,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def load(cls, root: Path, session_id: str) -> "IntakeSession":
        path = Path(root) / session_id / "session.json"
        if not path.exists():
            raise IntakeError(f"unknown intake session: {session_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    def save(self, root: Path) -> Path:
        d = Path(root) / self.session_id
        d.mkdir(parents=True, exist_ok=True)
        path = d / "session.json"
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False),
                        encoding="utf-8")
        return path


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def start_session(root: Path, *, description: str) -> IntakeSession:
    if not description or not description.strip():
        raise IntakeError("a plain-language description is required to start intake")
    s = IntakeSession(
        session_id=uuid.uuid4().hex[:12],
        description=description.strip(),
        created_at=_now(),
        updated_at=_now(),
    )
    s.save(root)
    return s


def _validate_answers(answers: dict) -> None:
    missing = [c for c in REQUIRED_CATEGORIES if c not in answers]
    if missing:
        raise IntakeError(f"missing answer categories: {', '.join(missing)}")
    for c in REQUIRED_CATEGORIES:
        v = answers[c]
        if c == "acceptance":
            continue  # validated below against the feature list
        if isinstance(v, str):
            if not v.strip():
                raise IntakeError(f"empty answer for category: {c}")
        elif isinstance(v, list):
            if not v or not all(isinstance(x, str) and x.strip() for x in v):
                raise IntakeError(f"empty/invalid list answer for category: {c}")
        else:
            raise IntakeError(f"answer for {c} must be a string or list of strings")
    # Acceptance criteria must cover EVERY feature (INT-4 engineer blocker:
    # a feature with no AC forces the builder to invent "done").
    features = answers["features"]
    if isinstance(features, str):
        features = [features]
    acc = answers["acceptance"]
    if not isinstance(acc, dict):
        raise IntakeError("acceptance must be an object mapping feature -> criteria")
    uncovered = [f for f in features if f not in acc]
    if uncovered:
        raise IntakeError(f"acceptance criteria missing for features: {', '.join(uncovered)}")
    for f, criteria in acc.items():
        if not isinstance(criteria, str) or not criteria.strip():
            raise IntakeError(f"empty acceptance criteria for feature: {f}")


def answer_questions(root: Path, session_id: str, answers: dict) -> IntakeSession:
    s = IntakeSession.load(root, session_id)
    _validate_answers(answers)
    s.answers = answers
    s.status = "validated"
    s.updated_at = _now()
    s.save(root)
    return s


def _render_prd(s: IntakeSession) -> str:
    a = s.answers
    features = a["features"]
    if isinstance(features, str):
        features = [features]
    feature_lines = "\n".join(f"- {f}" for f in features)
    acc = a["acceptance"]
    ac_lines = "\n".join(f"- **{f}:** {acc[f]}" for f in features)
    assumptions = a.get("assumptions", "").strip()
    assumptions_block = (
        f"\n## Assumptions & resolved ambiguities\n\n{assumptions}\n"
        if assumptions else ""
    )
    return f"""# PRD — generated by factory intake (SKEL-2)

**Session:** {s.session_id} · **Generated:** {s.updated_at}
**Status:** awaiting engineer approval (the ONE approval, OC-13)

## Original description

> {s.description}

## Platform

{a['platform']}

## Stack

{a['stack']}

## Features

{feature_lines}

## Acceptance criteria (per feature)

{ac_lines}

## Data model

{a['data_model']}

## Persistence

{a['persistence']}

## Look and feel

{a['look']}
{assumptions_block}
## Delivery

Each feature above becomes a story slice (OC-17 sizing) carried through
the factory pipeline: plan → fresh-context review → code → cross-family
review → gate → PR → Copilot approval → human merge. Wireframes for the
UI features are viewable at the local Storybook URL before approval.

## Approval

🧑 Engineer approval required. Reply "approved" (or with changes).
Approval is recorded as an `intake_approved` ledger event with elapsed
time and the reviewer identity.
"""


def generate_prd(root: Path, session_id: str) -> Path:
    s = IntakeSession.load(root, session_id)
    if s.status not in ("validated", "prd_ready"):
        raise IntakeError(
            f"cannot generate PRD from status '{s.status}' — session must be validated")
    text = _render_prd(s)
    d = Path(root) / s.session_id
    d.mkdir(parents=True, exist_ok=True)
    path = d / "PRD.md"
    path.write_text(text, encoding="utf-8")
    if s.status != "prd_ready":
        s.status = "prd_ready"
        s.updated_at = _now()
        s.save(root)
    return path
