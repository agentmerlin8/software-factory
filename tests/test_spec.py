"""Story-spec check tests — the REAL TOD-1 spec must now be refused."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.spec import check_story

REPO = Path(__file__).resolve().parents[1]

GOOD = """# TOD-X — Add a task

## Acceptance criteria
1. Input + Add button submits.
2. Empty input rejected.
3. Task persists across reload.
4. When storage fails (quota/blocked), the user sees an accessible error and keeps the draft.

## Manifest
- src/store.ts

## Named tests
- storage failure retains draft
"""


def test_good_story_passes():
    r = check_story(GOOD)
    assert r.passed, r.named_failures()


def test_real_tod1_spec_is_now_refused():
    """The regression: TOD-1 as shipped had 4 happy-path ACs and no failure AC."""
    p = REPO / "runs/todo-demo/stories/TOD-1.md"
    if not p.exists():
        pytest.skip("story file not present")
    r = check_story(p.read_text())
    assert not r.passed
    assert any("failure-mode AC" in f for f in r.failures), r.failures


def test_missing_ac_section():
    r = check_story("# T\n\n## Manifest\n- a\n")
    assert not r.passed
    assert any("Acceptance criteria" in f for f in r.failures)


def test_too_many_acs_refused():
    acs = "\n".join(f"{i}. thing" for i in range(1, 9))
    text = f"# T\n\n## Acceptance criteria\n{acs}\n\n## Manifest\n- a\n"
    r = check_story(text)
    assert not r.passed
    assert any("slice limit" in f for f in r.failures)


def test_missing_manifest_refused():
    text = "# T\n\n## Acceptance criteria\n1. thing\n"
    r = check_story(text)
    assert not r.passed
    assert any("Manifest" in f for f in r.failures)


def test_non_io_story_needs_no_failure_ac():
    text = ("# T\n\n## Acceptance criteria\n1. Renders newest-first.\n"
            "2. Shows a count.\n\n## Manifest\n- src/App.tsx\n")
    r = check_story(text)
    assert r.passed, r.named_failures()


def test_named_tests_warning_only():
    text = ("# T\n\n## Acceptance criteria\n1. Renders.\n\n"
            "## Manifest\n- src/App.tsx\n")
    r = check_story(text)
    assert r.passed
    assert any("Named tests" in w for w in r.warnings)