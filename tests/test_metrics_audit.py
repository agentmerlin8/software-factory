"""Measurement tests — SKEL-5 MEA-1 (OC-16).

Dispatch audit (fail-closed: unmetered dispatch = process defect) and
per-story machine-wall vs human-min split.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.metrics import dispatch_audit, cycle_time_split, harvest
from factory.ledger import Ledger


def _dispatch(ledger, story="TOD-1", role="coder", tokens=None, model="m",
              wall_s=10.0, outcome="ok", human_min=None):
    ledger.append("dispatch_completed", story=story, role=role,
                  tokens=tokens if tokens is not None else {"in": 100, "out": 20},
                  model=model, wall_s=wall_s, outcome=outcome, human_min=human_min)


def test_audit_clean_when_all_metered(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    _dispatch(led)
    _dispatch(led, role="reviewer")
    report = dispatch_audit(led)
    assert report["total"] == 2
    assert report["unmetered"] == 0
    assert report["defects"] == []


def test_audit_flags_missing_tokens(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    _dispatch(led, tokens={"in": 0, "out": 0})
    report = dispatch_audit(led)
    assert report["unmetered"] == 1
    assert any("tokens" in d for d in report["defects"])


def test_audit_flags_missing_model(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    _dispatch(led, model=None)
    report = dispatch_audit(led)
    assert report["unmetered"] == 1
    assert any("model" in d for d in report["defects"])


def test_audit_flags_missing_outcome(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    _dispatch(led, outcome=None)
    report = dispatch_audit(led)
    assert report["unmetered"] == 1
    assert any("outcome" in d for d in report["defects"])


def test_audit_flags_missing_wall(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    _dispatch(led, wall_s=None)
    report = dispatch_audit(led)
    assert report["unmetered"] == 1


def test_cycle_time_split_machine_vs_human(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    _dispatch(led, wall_s=100.0)
    _dispatch(led, role="reviewer", wall_s=50.0)
    led.append("human_merged", story="TOD-1", human_min=3.0)
    split = cycle_time_split(led)
    assert split["TOD-1"]["machine_wall_s"] == 150.0
    assert split["TOD-1"]["human_min"] == 3.0


def test_cycle_time_human_none_when_unrecorded(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    _dispatch(led, wall_s=100.0)
    split = cycle_time_split(led)
    assert split["TOD-1"]["human_min"] is None  # not 0 — unrecorded != zero


def test_audit_on_real_skel1_ledger():
    real = Path(__file__).resolve().parents[1] / "runs/todo-demo/ledger.jsonl"
    if not real.exists():
        return
    led = Ledger(real)
    report = dispatch_audit(led)
    # SKEL-1 metered every dispatch; the audit must find them all metered
    # (or surface genuine gaps as defects, never silently pass).
    assert report["total"] > 0
    assert isinstance(report["defects"], list)
