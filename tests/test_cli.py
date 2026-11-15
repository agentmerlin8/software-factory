"""CLI tests — fail-closed status, doctor, dispatch dry-run."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.cli import main
from factory.ledger import Ledger


def test_status_missing_ledger_refused(tmp_path, capsys):
    rc = main(["status", "--ledger", str(tmp_path / "absent.jsonl")])
    assert rc == 2
    assert "REFUSED" in capsys.readouterr().err


def test_status_empty_ledger(tmp_path, capsys):
    led = Ledger(tmp_path / "l.jsonl")
    led.append("run_started")
    rc = main(["status", "--ledger", str(tmp_path / "l.jsonl")])
    assert rc == 0
    assert "run events: 1" in capsys.readouterr().out


def test_status_invalid_ledger_refused(tmp_path, capsys):
    p = tmp_path / "bad.jsonl"
    p.write_text('{"schema":0}\n')
    rc = main(["status", "--ledger", str(p)])
    assert rc == 2
    assert "REFUSED" in capsys.readouterr().err


def test_dispatch_dry_run_seals_and_records(tmp_path, capsys):
    story = tmp_path / "story.md"
    story.write_text(
        "# TOD-1 — Add a task\n\n## Acceptance criteria\n"
        "1. Input submits.\n2. Empty rejected.\n"
        "3. When storage fails, the user sees an error and keeps the draft.\n\n"
        "## Manifest\n- src/store.ts\n\n## Named tests\n- storage failure\n")
    led = tmp_path / "l.jsonl"
    rc = main([
        "dispatch", "--ledger", str(led),
        "--story", "TOD-1", "--role", "coder", "--model", "qwen4-max-preview",
        "--instruction", "Implement TDD", "--story-file", str(story),
        "--repo", "o/r", "--sha", "a" * 40, "--manifest", "src/store.ts",
        "--dispatch-dir", str(tmp_path / "dispatch"),
        "--workdir", str(tmp_path), "--dry-run",
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "sealed" in out and "dry-run" in out
    rows = Ledger(led).read()
    assert [r["event"] for r in rows] == ["dispatch_sealed"]
    assert rows[0]["detail"]["sha256"]


def test_doctor_runs(capsys):
    rc = main(["doctor"])
    out = capsys.readouterr().out
    assert "doctor:" in out
    assert rc in (0, 1)

def test_dispatch_refuses_bad_spec(tmp_path, capsys):
    """PRE-3 enforcement: a spec with no failure-mode AC cannot be dispatched."""
    story = tmp_path / "bad.md"
    story.write_text(
        "# TOD-9\n\n## Acceptance criteria\n"
        "1. Saves to localStorage.\n2. Reloads.\n\n"
        "## Manifest\n- src/store.ts\n")
    rc = main([
        "dispatch", "--ledger", str(tmp_path / "l.jsonl"),
        "--story", "TOD-9", "--role", "coder", "--model", "m",
        "--instruction", "i", "--story-file", str(story),
        "--repo", "o/r", "--sha", "a" * 40, "--manifest", "src/store.ts",
        "--dispatch-dir", str(tmp_path / "d"), "--workdir", str(tmp_path),
        "--dry-run",
    ])
    assert rc == 2
    assert "failure-mode AC" in capsys.readouterr().err
