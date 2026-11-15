"""Intake state machine tests — SKEL-2 INT-1 (harness-agnostic, OC-7).

The required categories grew after the INT-4 engineer review (round 1):
acceptance criteria, persistence, and data model were BLOCKERS a builder
would have to invent, so the intake flow now REQUIRES them.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.intake import (
    IntakeSession, start_session, answer_questions, generate_prd,
    REQUIRED_CATEGORIES, IntakeError,
)


def full_answers():
    return {
        "platform": "web browser",
        "stack": "React + Vite + TypeScript",
        "features": ["add task", "list tasks", "complete task"],
        "look": "clean, warm paper theme",
        "persistence": "localStorage, single JSON key; in-memory fallback on write failure",
        "data_model": "Task { id: string, title: string, completed: boolean, createdAt: number }",
        "acceptance": {
            "add task": "Enter or Add submits; empty/whitespace rejected; appears at top",
            "list tasks": "newest-first; live count; friendly empty state",
            "complete task": "checkbox toggles; strikethrough; persists; double-toggle restores",
        },
        "assumptions": "'daily' means an app used daily, not daily-recurrence (out of scope)",
    }


def test_start_creates_questioning_session(tmp_path):
    s = start_session(tmp_path, description="I want a to-do app")
    assert s.status == "questioning"
    assert s.description == "I want a to-do app"
    assert s.session_id
    assert (tmp_path / s.session_id / "session.json").exists()


def test_start_requires_description(tmp_path):
    with pytest.raises(IntakeError):
        start_session(tmp_path, description="   ")


def test_answer_records_and_advances_to_validated(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    answers = full_answers()
    s2 = answer_questions(tmp_path, s.session_id, answers)
    assert s2.status == "validated"
    assert s2.answers == answers


def test_answer_rejects_missing_category(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    with pytest.raises(IntakeError, match="missing"):
        answer_questions(tmp_path, s.session_id, {"platform": "web"})


def test_answer_rejects_empty_category_value(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    answers = full_answers()
    answers["features"] = []
    with pytest.raises(IntakeError):
        answer_questions(tmp_path, s.session_id, answers)


def test_acceptance_must_cover_every_feature(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    answers = full_answers()
    del answers["acceptance"]["complete task"]
    with pytest.raises(IntakeError, match="acceptance"):
        answer_questions(tmp_path, s.session_id, answers)


def test_acceptance_value_must_be_nonempty(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    answers = full_answers()
    answers["acceptance"]["add task"] = "  "
    with pytest.raises(IntakeError):
        answer_questions(tmp_path, s.session_id, answers)


def test_generate_requires_validated(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    with pytest.raises(IntakeError, match="validated"):
        generate_prd(tmp_path, s.session_id)


def test_generate_produces_prd_with_all_sections(tmp_path):
    s = start_session(tmp_path, description="I want a to-do app")
    answers = full_answers()
    answer_questions(tmp_path, s.session_id, answers)
    prd_path = generate_prd(tmp_path, s.session_id)
    text = prd_path.read_text()
    assert "I want a to-do app" in text
    assert "web browser" in text
    assert "React + Vite + TypeScript" in text
    for f in answers["features"]:
        assert f in text
    assert "clean, warm paper theme" in text
    # The engineer-review blockers must now appear in the PRD body:
    assert "localStorage" in text                      # persistence
    assert "createdAt" in text                          # data model
    assert "Enter or Add submits" in text               # acceptance criteria
    assert "daily-recurrence" in text                   # assumptions
    s3 = IntakeSession.load(tmp_path, s.session_id)
    assert s3.status == "prd_ready"


def test_generate_is_deterministic(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    answer_questions(tmp_path, s.session_id, full_answers())
    p1 = generate_prd(tmp_path, s.session_id)
    first = p1.read_text()
    p2 = generate_prd(tmp_path, s.session_id)
    assert p2.read_text() == first


def test_session_roundtrips_through_disk(tmp_path):
    s = start_session(tmp_path, description="round trip")
    loaded = IntakeSession.load(tmp_path, s.session_id)
    assert loaded.description == "round trip"
    assert loaded.status == "questioning"


def test_load_unknown_session_fails_closed(tmp_path):
    with pytest.raises(IntakeError):
        IntakeSession.load(tmp_path, "nope")


def test_answer_unknown_session_fails_closed(tmp_path):
    with pytest.raises(IntakeError):
        answer_questions(tmp_path, "nope", full_answers())
