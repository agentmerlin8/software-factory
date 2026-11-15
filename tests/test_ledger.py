"""Ledger tests — schema v0, hash chain, fail-closed reads."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.ledger import Ledger, LedgerError, canonical, validate_event


@pytest.fixture
def ledger(tmp_path):
    return Ledger(tmp_path / "ledger.jsonl")


def test_append_and_read_roundtrip(ledger):
    ledger.append("run_started", detail={"run": "todo-demo"})
    ledger.append("design_approved", story=None, role="human",
                  detail={"by": "randy"})
    ledger.append("story_planned", story="TOD-1", role="controller")
    rows = ledger.read()
    assert [r["event"] for r in rows] == [
        "run_started", "design_approved", "story_planned"]
    assert rows[0]["schema"] == 0
    assert rows[2]["story"] == "TOD-1"


def test_chain_hashes_link(ledger):
    ledger.append("run_started")
    ledger.append("story_planned", story="TOD-1")
    rows = ledger.read()
    assert rows[0]["prev"] is None
    assert rows[1]["prev"] is not None
    assert len(rows[1]["prev"]) == 64  # sha256 hex


def test_tamper_detected(ledger):
    ledger.append("run_started")
    ledger.append("story_planned", story="TOD-1")
    # Tamper: rewrite the first line's detail.
    lines = ledger.path.read_text().splitlines()
    row = json.loads(lines[0])
    row["detail"] = {"tampered": True}
    lines[0] = canonical(row)
    ledger.path.write_text("\n".join(lines) + "\n")
    with pytest.raises(LedgerError, match="broken chain"):
        ledger.read()


def test_malformed_row_rejected(ledger):
    ledger.path.write_text('{"schema": 0}\n')  # missing ts/event
    with pytest.raises(LedgerError, match="missing required field"):
        ledger.read()


def test_unknown_event_rejected(ledger):
    with pytest.raises(LedgerError, match="unknown event type"):
        ledger.append("not_a_real_event")


def test_bad_schema_rejected():
    with pytest.raises(LedgerError, match="unsupported schema"):
        validate_event({"schema": 99, "ts": "x", "event": "run_started"})


def test_empty_ledger_reads_empty(ledger):
    assert ledger.read() == []


def test_missing_ledger_reads_empty(ledger):
    assert ledger.read() == []  # fail-closed for status is CLI's job


def test_canonical_is_deterministic():
    a = canonical({"b": 1, "a": 2})
    b = canonical({"a": 2, "b": 1})
    assert a == b == '{"a":2,"b":1}'


def test_story_rows_filter(ledger):
    ledger.append("story_planned", story="TOD-1")
    ledger.append("story_planned", story="TOD-2")
    ledger.append("gate_passed", story="TOD-1")
    assert len(ledger.story_rows("TOD-1")) == 2
    assert len(ledger.story_rows("TOD-2")) == 1