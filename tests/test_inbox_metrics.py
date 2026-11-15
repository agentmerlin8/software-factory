"""Inbox + metrics tests."""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory import inbox, metrics
from factory.ledger import Ledger


def test_escalate_builds_labeled_issue():
    fake = mock.Mock(returncode=0, stdout="https://github.com/o/r/issues/1\n",
                     stderr="")
    with mock.patch.object(inbox.subprocess, "run", return_value=fake) as m:
        res = inbox.escalate("o/r", story="TOD-1", reason="gate failed",
                             evidence="build red", assignee="randy")
    assert res.ok
    assert res.url.endswith("/issues/1")
    cmd = m.call_args[0][0]
    assert "--label" in cmd and inbox.INBOX_LABEL in cmd
    assert "--assignee" in cmd and "randy" in cmd
    assert "[inbox] TOD-1" in cmd[cmd.index("--title") + 1]


def test_escalate_failure_reported():
    fake = mock.Mock(returncode=1, stdout="", stderr="nope")
    with mock.patch.object(inbox.subprocess, "run", return_value=fake):
        res = inbox.escalate("o/r", story="TOD-1", reason="x", evidence="y")
    assert not res.ok
    assert "nope" in res.error


def _ledger_with_dispatches(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    led.append("dispatch_completed", story="TOD-1", role="coder",
               tokens={"in": 1000, "out": 500}, wall_s=10.0, cost_usd=0.02)
    led.append("dispatch_completed", story="TOD-1", role="reviewer",
               tokens={"in": 800, "out": 200}, wall_s=5.0, cost_usd=0.01)
    led.append("defect_found", story="TOD-1", detail={"sev": "minor"})
    led.append("human_merged", story="TOD-1", human_min=3.0)
    return led


def test_harvest_folds_roles(tmp_path):
    led = _ledger_with_dispatches(tmp_path)
    m = metrics.harvest(led)["TOD-1"]
    assert m.coder_tokens == 1500
    assert m.noncoder_tokens == 1000
    assert m.defects == 1
    assert m.human_min == 3.0
    assert abs(m.overhead_ratio - 1000 / 1500) < 1e-9


def test_overhead_none_when_no_coder(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    led.append("dispatch_completed", story="TOD-2", role="reviewer",
               tokens={"in": 10, "out": 5})
    m = metrics.harvest(led)["TOD-2"]
    assert m.overhead_ratio is None


def test_render_nulls_not_zero(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    led.append("dispatch_completed", story="TOD-1", role="coder",
               tokens={"in": 100, "out": 50})
    fac = metrics.harvest(led)
    text = metrics.render_comparison(fac, {})
    assert "not recorded" in text  # human_min missing -> not recorded
    assert "TOD-1" in text


def test_write_comparison(tmp_path):
    led = _ledger_with_dispatches(tmp_path)
    fac = metrics.harvest(led)
    p = metrics.write_comparison(tmp_path / "C.md", fac, {})
    assert p.exists()
    assert "process-overhead-ratio" in p.read_text()