"""Guard-sweep tests — reproduces the round-10 vacuous-guard finding."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.guard_sweep import find_guards, sweep

GUARDED = '''def is_task(t):
    return (
        isinstance(t.get("id"), str) and
        len(t["id"]) > 0 and
        isinstance(t.get("n"), (int, float)) and
        t["n"] == t["n"] and
        True
    )
'''


def _setup(tmp_path, test_body):
    mod = tmp_path / "m.py"
    mod.write_text(GUARDED, encoding="utf-8")
    test = tmp_path / "t.py"
    test.write_text(
        f"import runpy\nm = runpy.run_path(r'{mod}')\nis_task = m['is_task']\n"
        + test_body, encoding="utf-8")
    return mod, [sys.executable, str(test)]


def test_find_guards_scopes_to_function(tmp_path):
    mod = tmp_path / "m.py"
    mod.write_text(GUARDED, encoding="utf-8")
    guards = find_guards(mod, within="def is_task")
    assert len(guards) == 4
    assert any("len(" in g.text for g in guards)


def test_sweep_finds_the_vacuous_guard(tmp_path):
    """Only id-type is asserted -> the other guards survive deletion."""
    mod, cmd = _setup(tmp_path, "assert is_task({'id': 'x', 'n': 1})\n"
                                "assert not is_task({'id': 5, 'n': 1})\n")
    r = sweep(mod, workdir=tmp_path, test_cmd=cmd, within="def is_task")
    assert not r.ok
    survived = " ".join(g.text for g in r.survivors)
    assert "len(" in survived, survived
    assert "survived" in r.summary().lower() or "SURVIVED" in r.summary()


def test_sweep_all_killed_when_fully_asserted(tmp_path):
    mod, cmd = _setup(tmp_path, """
assert is_task({'id': 'x', 'n': 1})
assert not is_task({'id': 5, 'n': 1})
assert not is_task({'id': '', 'n': 1})
assert not is_task({'id': 'x', 'n': 'str'})
assert not is_task({'id': 'x', 'n': float('nan')})
""")
    r = sweep(mod, workdir=tmp_path, test_cmd=cmd, within="def is_task")
    assert r.ok, [g.text for g in r.survivors]
    assert len(r.killed) == 4


def test_original_always_restored(tmp_path):
    mod, cmd = _setup(tmp_path, "assert is_task({'id': 'x', 'n': 1})\n")
    before = mod.read_text()
    sweep(mod, workdir=tmp_path, test_cmd=cmd, within="def is_task")
    assert mod.read_text() == before


def test_red_baseline_is_inconclusive_not_all_killed(tmp_path):
    mod, cmd = _setup(tmp_path, "assert False, 'baseline red'\n")
    r = sweep(mod, workdir=tmp_path, test_cmd=cmd, within="def is_task")
    assert r.killed == []
    assert len(r.inconclusive) == 4