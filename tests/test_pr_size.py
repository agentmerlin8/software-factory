"""PR-size budget tests — calibrated against the REAL TOD-1 overrun."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.pr_size import DiffStat, check, check_repo

REPO = Path.home() / ".hermes/cache/scratch/factory-exp/todo-demo"


def _s(path, a, d=0):
    return DiffStat(path, a, d)


def test_small_slice_passes():
    b = check([_s("src/store.ts", 40), _s("src/store.test.ts", 60),
               _s("src/App.tsx", 50)])
    assert b.passed, b.named_failures()


def test_visual_churn_is_the_expensive_surface():
    """TOD-1's actual shape: modest logic, huge unrequested CSS."""
    b = check([_s("src/App.tsx", 130), _s("src/store.ts", 50),
               _s("src/index.css", 520)])
    assert not b.passed
    assert "visual/CSS" in b.named_failures()
    assert any("theming" in a for a in b.advice)


def test_total_budget_enforced():
    b = check([_s("src/a.ts", 500)])
    assert not b.passed
    assert "review budget" in b.named_failures()


def test_file_count_enforced():
    b = check([_s(f"src/f{i}.ts", 10) for i in range(8)])
    assert not b.passed
    assert "file budget" in b.named_failures()


def test_tests_counted_separately_from_product():
    b = check([_s("src/store.ts", 50), _s("src/store.test.ts", 200)])
    assert b.tests == 200
    assert b.product == 50


def test_visual_classification():
    assert _s("src/index.css", 1).is_visual
    assert _s("src/theme.scss", 1).is_visual
    assert not _s("src/App.tsx", 1).is_visual


def test_test_classification():
    assert _s("src/App.test.tsx", 1).is_test
    assert _s("tests/test_x.py", 1).is_test
    assert not _s("src/App.tsx", 1).is_test


@pytest.mark.skipif(not REPO.exists(), reason="product repo not cloned")
def test_real_tod1_is_over_budget():
    """The empirical calibration: this PR took 7+ rounds and must be flagged."""
    b = check_repo(REPO, "main")
    assert not b.passed, "TOD-1 (934 lines, 522 CSS) must exceed the budget"
    assert b.visual > 400
    assert "visual/CSS" in b.named_failures()