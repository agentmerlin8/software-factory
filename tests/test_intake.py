"""Intake state machine tests — SKEL-2 INT-1 (harness-agnostic, OC-7)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.intake import (
    IntakeSession, start_session, answer_questions, generate_prd,
    REQUIRED_CATEGORIES, IntakeError,
)


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
    answers = {
        "platform": "web browser",
        "stack": "React + Vite + TypeScript",
        "features": ["add task", "list tasks", "complete task"],
        "look": "clean, warm paper theme",
    }
    s2 = answer_questions(tmp_path, s.session_id, answers)
    assert s2.status == "validated"
    assert s2.answers == answers


def test_answer_rejects_missing_category(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    with pytest.raises(IntakeError, match="missing"):
        answer_questions(tmp_path, s.session_id, {"platform": "web"})


def test_answer_rejects_empty_category_value(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    answers = {c: "x" for c in REQUIRED_CATEGORIES}
    answers["features"] = []
    with pytest.raises(IntakeError):
        answer_questions(tmp_path, s.session_id, answers)


def test_generate_requires_validated(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    with pytest.raises(IntakeError, match="validated"):
        generate_prd(tmp_path, s.session_id)


def test_generate_produces_prd_with_all_sections(tmp_path):
    s = start_session(tmp_path, description="I want a to-do app")
    answers = {
        "platform": "web browser",
        "stack": "React + Vite + TypeScript",
        "features": ["add task", "list tasks", "complete task"],
        "look": "clean, warm paper theme",
    }
    answer_questions(tmp_path, s.session_id, answers)
    prd_path = generate_prd(tmp_path, s.session_id)
    text = prd_path.read_text()
    assert "I want a to-do app" in text
    assert "web browser" in text
    assert "React + Vite + TypeScript" in text
    for f in answers["features"]:
        assert f in text
    assert "clean, warm paper theme" in text
    # status advances to prd_ready
    s3 = IntakeSession.load(tmp_path, s.session_id)
    assert s3.status == "prd_ready"


def test_generate_is_deterministic(tmp_path):
    s = start_session(tmp_path, description="a to-do app")
    answers = {c: f"val-{c}" for c in REQUIRED_CATEGORIES}
    answers["features"] = ["f1", "f2"]
    answer_questions(tmp_path, s.session_id, answers)
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
        answer_questions(tmp_path, "nope", {c: "x" for c in REQUIRED_CATEGORIES})
