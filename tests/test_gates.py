"""Gate tests — manifest + secrets on a real fixture git repo; build/tests mocked."""
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory import gates


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "a.txt").write_text("base\n")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=tmp_path, check=True)
    return tmp_path


def test_manifest_pass_when_in_scope(repo):
    (repo / "a.txt").write_text("changed\n")
    subprocess.run(["git", "commit", "-qam", "edit"], cwd=repo, check=True)
    ok, detail = gates.check_manifest(repo, "HEAD~1", ["a.txt"])
    assert ok, detail


def test_manifest_fail_when_out_of_scope(repo):
    (repo / "b.txt").write_text("new\n")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "add b"], cwd=repo, check=True)
    ok, detail = gates.check_manifest(repo, "HEAD~1", ["a.txt"])
    assert not ok
    assert "b.txt" in detail


def test_secrets_clean(repo):
    (repo / "a.txt").write_text("hello world\n")
    subprocess.run(["git", "commit", "-qam", "edit"], cwd=repo, check=True)
    ok, _ = gates.check_secrets(repo, "HEAD~1")
    assert ok


def test_secrets_detected(repo):
    (repo / "a.txt").write_text("token = ghp_" + "x" * 30 + "\n")
    subprocess.run(["git", "commit", "-qam", "leak"], cwd=repo, check=True)
    ok, detail = gates.check_secrets(repo, "HEAD~1")
    assert not ok
    assert "secret-like" in detail


def test_pre_review_aggregates(repo):
    (repo / "a.txt").write_text("ok\n")
    subprocess.run(["git", "commit", "-qam", "edit"], cwd=repo, check=True)
    with mock.patch.object(gates, "check_build", return_value=(True, "")), \
         mock.patch.object(gates, "check_tests", return_value=(True, "")):
        res = gates.pre_review(repo, base="HEAD~1", manifest=["a.txt"])
    assert res.passed
    assert res.checks == {"build": True, "tests": True,
                          "manifest": True, "secrets": True,
                          "boundaries": True}


def test_pre_review_fails_closed(repo):
    (repo / "a.txt").write_text("ok\n")
    subprocess.run(["git", "commit", "-qam", "edit"], cwd=repo, check=True)
    with mock.patch.object(gates, "check_build", return_value=(False, "boom")), \
         mock.patch.object(gates, "check_tests", return_value=(True, "")):
        res = gates.pre_review(repo, base="HEAD~1", manifest=["a.txt"])
    assert not res.passed
    assert "build" in res.named_failures()