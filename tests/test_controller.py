"""Controller validator tests — SKEL-3 SEC-1 (OC-14 security core).

The controller is the SOLE state-repo writer. It runs no model output and
no product code: it validates a submission against schema + hash-chain +
event allowlist + policy, then appends. These tests pin the refusal rules.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.controller import (
    validate_submission, append_submission, ControllerError,
    DEFAULT_POLICY,
)
from factory.ledger import Ledger


def make_submission(events):
    return {"schema": 0, "source": "agent", "events": events}


def ev(event="dispatch_completed", story="TOD-1", **kw):
    base = {"event": event, "story": story, "role": "coder",
            "detail": {"note": "test"}}
    base.update(kw)
    return base


@pytest.fixture
def ledger(tmp_path):
    return Ledger(tmp_path / "ledger.jsonl")


def test_valid_submission_appends(ledger):
    sub = make_submission([ev()])
    append_submission(ledger, sub)
    rows = ledger.read()
    assert len(rows) == 1
    assert rows[0]["event"] == "dispatch_completed"
    assert rows[0]["story"] == "TOD-1"


def test_chain_continuity_preserved(ledger):
    append_submission(ledger, make_submission([ev()]))
    append_submission(ledger, make_submission([ev(event="gate_passed")]))
    rows = ledger.read()  # read() verifies the chain
    assert len(rows) == 2
    assert rows[1]["prev"] is not None


def test_rejects_unknown_event_type(ledger):
    sub = make_submission([ev(event="totally_bogus")])
    with pytest.raises(ControllerError, match="event"):
        append_submission(ledger, sub)
    assert ledger.read() == []


def test_rejects_missing_required_field(ledger):
    bad = {"event": "dispatch_completed"}  # no story/role/detail is ok, but schema/ts added by controller
    sub = make_submission([{"event": "dispatch_completed", "story": "X"}])
    # valid minimal — should pass; now break the event field entirely
    sub2 = make_submission([{"story": "X"}])
    with pytest.raises(ControllerError):
        append_submission(ledger, sub2)


def test_rejects_policy_mutation_attempt(ledger):
    sub = make_submission([ev(event="correction",
                              detail={"policy_change": {"allow": "*"}})])
    with pytest.raises(ControllerError, match="policy"):
        append_submission(ledger, sub)


def test_rejects_non_object_event(ledger):
    sub = make_submission(["not an object"])
    with pytest.raises(ControllerError):
        append_submission(ledger, sub)


def test_rejects_empty_submission(ledger):
    with pytest.raises(ControllerError):
        append_submission(ledger, make_submission([]))


def test_rejects_wrong_schema(ledger):
    sub = make_submission([ev()])
    sub["schema"] = 99
    with pytest.raises(ControllerError, match="schema"):
        append_submission(ledger, sub)


def test_rejects_missing_source(ledger):
    sub = make_submission([ev()])
    del sub["source"]
    with pytest.raises(ControllerError, match="source"):
        append_submission(ledger, sub)


def test_atomic_all_or_nothing(ledger):
    # second event invalid -> NOTHING appended (no partial write)
    sub = make_submission([ev(), ev(event="bogus_event")])
    with pytest.raises(ControllerError):
        append_submission(ledger, sub)
    assert ledger.read() == []


def test_controller_stamps_ts_and_source(ledger):
    append_submission(ledger, make_submission([ev()]))
    row = ledger.read()[0]
    assert row["ts"]
    assert row["detail"]["_source"] == "agent"


def test_agent_cannot_forge_prev_hash(ledger):
    # a submission carrying its own 'prev' must be ignored/overwritten by
    # the controller's chain computation, not trusted
    append_submission(ledger, make_submission([ev()]))
    forged = ev()
    forged["prev"] = "0" * 64
    append_submission(ledger, make_submission([forged]))
    rows = ledger.read()  # verifies chain — forged prev would break it
    assert len(rows) == 2


def test_policy_allowlist_enforced(ledger):
    policy = {"allowed_events": ["gate_passed"], "schema": 0}
    sub = make_submission([ev(event="dispatch_completed")])
    with pytest.raises(ControllerError, match="allowlist"):
        append_submission(ledger, sub, policy=policy)
    ok = make_submission([ev(event="gate_passed")])
    append_submission(ledger, ok, policy=policy)
    assert len(ledger.read()) == 1
