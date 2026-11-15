"""Dispatch package tests — determinism, content addressing, structure."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.dispatch import seal, Package


def _pkg(story="TOD-1", role="coder"):
    return seal(
        story=story, role=role, model="qwen4-max-preview",
        instruction="Implement the story TDD.",
        inputs={"story": "Add a task", "design": "localStorage store"},
        expected_outputs=["code committed", "tests green"],
        repo="agentmerlin8/factory-todo-demo", sha="a" * 40,
        manifest=["src/store.ts", "src/App.tsx"],
    )


def test_deterministic_bytes():
    a, b = _pkg(), _pkg()
    assert a.body == b.body
    assert a.sha256 == b.sha256


def test_input_order_does_not_matter():
    a = seal(story="TOD-1", role="coder", model="m", instruction="i",
             inputs={"z": "1", "a": "2"}, expected_outputs=[], repo="r",
             sha="s", manifest=[])
    b = seal(story="TOD-1", role="coder", model="m", instruction="i",
             inputs={"a": "2", "z": "1"}, expected_outputs=[], repo="r",
             sha="s", manifest=[])
    assert a.sha256 == b.sha256


def test_content_change_changes_hash():
    a = _pkg()
    b = seal(story="TOD-1", role="coder", model="qwen4-max-preview",
             instruction="DIFFERENT", inputs={"story": "Add a task",
             "design": "localStorage store"}, expected_outputs=["code committed",
             "tests green"], repo="agentmerlin8/factory-todo-demo",
             sha="a" * 40, manifest=["src/store.ts", "src/App.tsx"])
    assert a.sha256 != b.sha256


def test_package_contains_required_sections():
    body = _pkg().body
    for section in ("Role instruction", "Pinned inputs", "Manifest",
                    "Expected outputs", "Stop rules", "Resume preamble"):
        assert section in body
    assert "qwen4-max-preview" in body
    assert "a" * 40 in body


def test_write_creates_named_file(tmp_path):
    p = _pkg()
    path = p.write(tmp_path, seq=1)
    assert path.name == "TOD-1-coder-01.md"
    assert path.read_text() == p.body


def test_stop_rules_forbid_state_repo_writes():
    body = _pkg().body
    assert "state/control repo" in body
    assert "force-push" in body