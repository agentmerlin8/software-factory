"""Calibration scoring tests — SKEL-5 MEA-3."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.calibration import score_review, render_calibration, SEEDED_IDS, SEEDED_DEFECTS


def test_ten_defects_defined():
    assert len(SEEDED_DEFECTS) == 10
    assert len(SEEDED_IDS) == 10


def test_perfect_catch():
    r = score_review("cross-family", list(SEEDED_IDS))
    assert r.caught == 10
    assert r.catch_rate == 1.0
    assert r.false_positives == 0
    assert r.precision == 1.0


def test_partial_catch():
    r = score_review("same-session", ["SD-01", "SD-02", "SD-03"])
    assert r.caught == 3
    assert r.catch_rate == 0.3
    assert r.false_positives == 0


def test_false_positives_counted():
    r = score_review("same-session", ["SD-01", "BOGUS-1", "BOGUS-2"])
    assert r.caught == 1
    assert r.false_positives == 2
    assert r.precision == 1 / 3


def test_zero_flagged():
    r = score_review("same-session", [])
    assert r.caught == 0
    assert r.catch_rate == 0.0
    assert r.precision == 0.0


def test_render_has_all_modes():
    results = [score_review("same-session", ["SD-01"]),
               score_review("fresh-same-family", list(SEEDED_IDS)[:5]),
               score_review("fresh-cross-family", list(SEEDED_IDS))]
    text = render_calibration(results)
    assert "same-session" in text
    assert "fresh-cross-family" in text
    assert "10/10" in text
