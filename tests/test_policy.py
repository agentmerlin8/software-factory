"""Workspace policy tests — the Copilot-review lever (OC-9)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.policy import WorkspacePolicy, load_policy


def test_default_is_optional():
    p = WorkspacePolicy()
    assert p.copilot_review == "optional"
    assert p.request_copilot is True
    assert p.block_on_copilot_approval is False


def test_required_blocks_on_approval():
    p = WorkspacePolicy(copilot_review="required")
    assert p.request_copilot is True
    assert p.block_on_copilot_approval is True


def test_off_never_requests():
    p = WorkspacePolicy(copilot_review="off")
    assert p.request_copilot is False
    assert p.block_on_copilot_approval is False


def test_invalid_value_rejected():
    with pytest.raises(ValueError):
        WorkspacePolicy(copilot_review="always")


def test_load_missing_file_defaults(tmp_path):
    p = load_policy(tmp_path / "nope.json")
    assert p.copilot_review == "optional"
    assert p.human_merge is True


def test_load_reads_file(tmp_path):
    f = tmp_path / "workspace.json"
    f.write_text(json.dumps({"copilot_review": "off", "human_merge": True}))
    p = load_policy(f)
    assert p.copilot_review == "off"
    assert p.request_copilot is False


def test_load_partial_file_defaults_rest(tmp_path):
    f = tmp_path / "workspace.json"
    f.write_text(json.dumps({"copilot_review": "required"}))
    p = load_policy(f)
    assert p.copilot_review == "required"
    assert p.human_merge is True
