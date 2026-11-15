"""Hermes adapter tests — command shape, usage harvest, timeout, oversize."""
import json
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.adapters import hermes
from factory.adapters.hermes import AdapterError, build_command, run


def test_command_shape(tmp_path):
    cmd = build_command("PROMPT", "qwen4-max-preview", tmp_path,
                        tmp_path / "u.json", "terminal,file")
    assert cmd[0] == "hermes"
    assert "--usage-file" in cmd
    i = cmd.index("-z")
    assert cmd[i + 1] == "PROMPT"
    assert cmd[cmd.index("-m") + 1] == "qwen4-max-preview"
    assert cmd[cmd.index("--in") + 1] == str(tmp_path)
    assert "--yolo" in cmd


def test_run_harvests_usage(tmp_path):
    pkg = tmp_path / "pkg.md"
    pkg.write_text("do the thing")
    usage = tmp_path / "u.json"
    usage.write_text(json.dumps({
        "input_tokens": 100, "output_tokens": 50,
        "estimated_cost_usd": 0.01, "model": "qwen4-max-preview",
        "completed": True}))

    fake = mock.Mock(returncode=0, stdout="done", stderr="")
    with mock.patch.object(hermes.subprocess, "run", return_value=fake) as m:
        res = run(pkg, model="qwen4-max-preview", workdir=tmp_path,
                  usage_path=usage)
    assert res.ok
    assert res.tokens == {"in": 100, "out": 50}
    assert res.model == "qwen4-max-preview"
    assert res.cost_usd == 0.01
    # the package text was passed via -z, cwd is the product repo
    args = m.call_args[0][0]
    assert args[args.index("-z") + 1] == "do the thing"
    assert m.call_args[1]["cwd"] == str(tmp_path)


def test_run_timeout(tmp_path):
    pkg = tmp_path / "pkg.md"
    pkg.write_text("x")
    import subprocess
    with mock.patch.object(hermes.subprocess, "run",
                           side_effect=subprocess.TimeoutExpired("hermes", 1)):
        res = run(pkg, model="m", workdir=tmp_path,
                  usage_path=tmp_path / "u.json", timeout_s=1)
    assert res.exit_code == 124
    assert "TIMEOUT" in res.stderr


def test_oversize_package_refused(tmp_path):
    pkg = tmp_path / "big.md"
    pkg.write_text("x" * (hermes.MAX_PACKAGE_BYTES + 1))
    with pytest.raises(AdapterError, match="exceeds"):
        run(pkg, model="m", workdir=tmp_path, usage_path=tmp_path / "u.json")


def test_missing_usage_file_is_empty(tmp_path):
    pkg = tmp_path / "pkg.md"
    pkg.write_text("x")
    fake = mock.Mock(returncode=0, stdout="", stderr="")
    with mock.patch.object(hermes.subprocess, "run", return_value=fake):
        res = run(pkg, model="m", workdir=tmp_path,
                  usage_path=tmp_path / "absent.json")
    assert res.usage == {}
    assert res.tokens == {"in": 0, "out": 0}


def test_large_package_dispatched_by_reference(tmp_path):
    # TOD-5: a 151KB package died with E2BIG — Linux caps a SINGLE argument
    # at 128KiB. Above the inline limit, argv must carry a compact pointer
    # to the sealed package, not the package itself.
    pkg = tmp_path / "big.md"
    pkg.write_text("x" * (hermes.MAX_INLINE_BYTES + 1))
    fake = mock.Mock(returncode=0, stdout="done", stderr="")
    with mock.patch.object(hermes.subprocess, "run", return_value=fake) as m:
        res = run(pkg, model="m", workdir=tmp_path,
                  usage_path=tmp_path / "u.json")
    assert res.ok
    args = m.call_args[0][0]
    prompt = args[args.index("-z") + 1]
    assert len(prompt.encode("utf-8")) < hermes.MAX_INLINE_BYTES
    assert str(pkg.resolve()) in prompt
    assert "read it FIRST" in prompt


def test_small_package_still_inline(tmp_path):
    pkg = tmp_path / "pkg.md"
    pkg.write_text("do the thing")
    fake = mock.Mock(returncode=0, stdout="", stderr="")
    with mock.patch.object(hermes.subprocess, "run", return_value=fake) as m:
        run(pkg, model="m", workdir=tmp_path, usage_path=tmp_path / "u.json")
    args = m.call_args[0][0]
    assert args[args.index("-z") + 1] == "do the thing"