"""Findings-log tests — classification stability and the mining queries."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.findings import CLASSES, Finding, FindingsLog, classify


def _f(**kw):
    base = dict(ts="2026-11-15T00:00:00Z", repo="o/r", pr=1, round=1,
                source="copilot", klass="contrast-text", severity="major",
                summary="x")
    base.update(kw)
    return Finding(**base)


def test_classification_is_stable_across_wordings():
    """The same class must survive rewording, or recurrence is invisible."""
    a = classify("Light-theme secondary text below minimum contrast")
    b = classify("Increase contrast for the footer text (WCAG 4.5:1)")
    assert a == b == "contrast-text"


def test_specific_classes_win_over_generic_contrast():
    assert classify("::selection text contrast too low") == "contrast-selection"
    assert classify("focus outline contrast below 3:1") == "contrast-focus-indicator"
    assert classify("Add label contrast in hover state on gradient") == "contrast-gradient-state"


def test_refuted_claims_are_their_own_class():
    assert classify("anything at all", verified="refuted") == "false-positive"


def test_boundary_and_io_classes():
    assert classify("Validate stored task entries: [null] crashes") == "untrusted-boundary"
    assert classify("storage quota failure aborts submission") == "unhandled-io-failure"


def test_announcement_classes_are_distinct():
    assert classify("not announced to screen-reader users") == "silent-mutation"
    assert classify("identical titles leave the live-region text unchanged") == "stale-live-region"


def test_unknown_falls_to_other():
    assert classify("the widget is blue") == "other"


def test_append_and_read_roundtrip(tmp_path):
    log = FindingsLog(tmp_path / "f.jsonl")
    log.append(_f(summary="first"))
    log.append(_f(summary="second", klass="test-gap"))
    rows = log.read()
    assert len(rows) == 2
    assert rows[0]["summary"] == "first"


def test_unknown_class_rejected(tmp_path):
    log = FindingsLog(tmp_path / "f.jsonl")
    with pytest.raises(ValueError, match="unknown class"):
        log.append(_f(klass="not-a-class"))


def test_empty_log_renders(tmp_path):
    log = FindingsLog(tmp_path / "absent.jsonl")
    assert log.read() == []
    assert "No findings" in log.render()


def test_recurring_and_coverage(tmp_path):
    log = FindingsLog(tmp_path / "f.jsonl")
    log.append(_f(klass="contrast-text", gate_check="contrast", summary="a"))
    log.append(_f(klass="contrast-text", gate_check="contrast", round=2, summary="b"))
    log.append(_f(klass="test-gap", summary="c"))
    assert log.recurring() == [("contrast-text", 2)]
    assert log.uncovered_classes() == ["test-gap"]


def test_escape_rate_by_round(tmp_path):
    log = FindingsLog(tmp_path / "f.jsonl")
    log.append(_f(round=1, escaped_gate=True, escaped_review=True,
                  disposition="fixed", summary="a"))
    log.append(_f(round=1, escaped_gate=True, summary="b"))
    log.append(_f(round=2, escaped_gate=False, summary="c"))
    rates = log.escape_rate_by_round()
    assert rates[1] == {"total": 2, "escaped_gate": 2, "escaped_review": 1, "fixed": 1}
    assert rates[2]["escaped_gate"] == 0


def test_render_reports_uncovered_as_backlog(tmp_path):
    log = FindingsLog(tmp_path / "f.jsonl")
    log.append(_f(klass="test-gap"))
    text = log.render()
    assert "NO deterministic check" in text
    assert "test-gap" in text


def test_all_classes_have_descriptions():
    assert all(isinstance(v, str) and v for v in CLASSES.values())

def test_false_positives_are_not_gate_candidates(tmp_path):
    log = FindingsLog(tmp_path / "f.jsonl")
    log.append(_f(klass="false-positive", summary="a"))
    log.append(_f(klass="other", summary="b"))
    log.append(_f(klass="test-gap", summary="c"))
    assert log.uncovered_classes() == ["test-gap"]


def test_reviewer_precision(tmp_path):
    log = FindingsLog(tmp_path / "f.jsonl")
    log.append(_f(source="cross-family", klass="false-positive", summary="a"))
    log.append(_f(source="cross-family", klass="test-gap", summary="b"))
    log.append(_f(source="copilot", klass="contrast-text", summary="c"))
    p = log.reviewer_precision()
    assert p["cross-family"] == {"real": 1, "refuted": 1}
    assert p["copilot"] == {"real": 1, "refuted": 0}
    assert "precision" in log.render()


def test_append_is_idempotent(tmp_path):
    log = FindingsLog(tmp_path / "f.jsonl")
    log.append(_f(summary="same finding"))
    log.append(_f(summary="same finding"))
    assert len(log.read()) == 1


def test_different_round_is_a_new_finding(tmp_path):
    log = FindingsLog(tmp_path / "f.jsonl")
    log.append(_f(summary="same wording", round=1))
    log.append(_f(summary="same wording", round=2))
    assert len(log.read()) == 2
