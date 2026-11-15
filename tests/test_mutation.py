"""Mutation-verification tests — including the round-9 self-certifying test."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.mutation import verify_regression


def _write(p: Path, text: str):
    p.write_text(text, encoding="utf-8")


def test_verified_when_mutant_fails_and_fix_passes(tmp_path):
    target = tmp_path / "v.py"
    good = "VALUE = 2\n"
    bad = "VALUE = 1\n"
    _write(target, good)
    # a test that genuinely asserts the fixed behavior
    cmd = [sys.executable, "-c",
           f"import runpy; m=runpy.run_path(r'{target}'); "
           "assert m['VALUE']==2, 'wrong'"]
    r = verify_regression(
        tmp_path, mutate=lambda: _write(target, bad),
        restore=lambda: _write(target, good), test_cmd=cmd)
    assert r.verdict == "verified"
    assert r.ok


def test_detects_a_self_certifying_test(tmp_path):
    """The round-9 class: the test passes even on the defective code."""
    target = tmp_path / "v.py"
    good, bad = "VALUE = 2\n", "VALUE = 1\n"
    _write(target, good)
    # a vacuous test — always true, proves nothing
    cmd = [sys.executable, "-c", "assert True"]
    r = verify_regression(
        tmp_path, mutate=lambda: _write(target, bad),
        restore=lambda: _write(target, good), test_cmd=cmd)
    assert r.verdict == "test-too-weak"
    assert not r.ok
    assert "cannot detect" in r.detail


def test_detects_a_broken_test(tmp_path):
    target = tmp_path / "v.py"
    good, bad = "VALUE = 2\n", "VALUE = 1\n"
    _write(target, good)
    cmd = [sys.executable, "-c", "assert False, 'always fails'"]
    r = verify_regression(
        tmp_path, mutate=lambda: _write(target, bad),
        restore=lambda: _write(target, good), test_cmd=cmd)
    assert r.verdict == "test-broken"


def test_restore_runs_even_if_the_test_crashes(tmp_path):
    target = tmp_path / "v.py"
    good, bad = "GOOD\n", "BAD\n"
    _write(target, good)
    cmd = [sys.executable, "-c", "raise SystemExit(3)"]
    verify_regression(tmp_path, mutate=lambda: _write(target, bad),
                      restore=lambda: _write(target, good), test_cmd=cmd)
    assert target.read_text() == good, "restore must always run"


def test_restore_runs_even_if_mutate_raises(tmp_path):
    target = tmp_path / "v.py"
    _write(target, "GOOD\n")

    def boom():
        _write(target, "BAD\n")
        raise RuntimeError("mutate blew up")

    try:
        verify_regression(tmp_path, mutate=boom,
                          restore=lambda: _write(target, "GOOD\n"),
                          test_cmd=[sys.executable, "-c", "assert True"])
    except RuntimeError:
        pass
    assert target.read_text() == "GOOD\n"