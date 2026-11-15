"""Discovery-driven CSS audit tests — the round-2/3/4 regressions in one place.

The point of discovery: a selector nobody enumerated must still be audited.
Each test below is a defect that a hardcoded-list gate missed.
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.css_audit import audit_stylesheet, discover

REPO = Path.home() / ".hermes/cache/scratch/factory-exp/todo-demo"

BASE = """
:root {
  --paper: #f7f1e5;
  --surface: #fffcf5;
  --surface-raised: #fffefb;
  --ink: #2b2118;
  --persimmon: #d94f04;
  --persimmon-deep: #b23e02;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #191410;
    --surface: #221c16;
    --surface-raised: #2a221b;
    --ink: #f0e7d8;
    --persimmon: #ff7a2f;
    --persimmon-deep: #ff9254;
  }
}
body { background: var(--paper); color: var(--ink); }
"""


def test_discovers_selection_without_being_told():
    css = BASE + "::selection { background: var(--persimmon); color: var(--surface); }"
    d = discover(css)
    assert len(d.selections) == 1
    findings = audit_stylesheet(css)
    assert any("::selection" in f.label for f in findings)


def test_selection_fixed_passes():
    css = BASE + "::selection { background: var(--persimmon-deep); color: var(--surface); }"
    findings = [f for f in audit_stylesheet(css) if "::selection" in f.label]
    assert findings == []


def test_discovers_translucent_focus_outline():
    css = BASE + """
    :root { --focus-ring: rgba(217, 79, 4, 0.35); }
    .btn:focus-visible { outline: 3px solid var(--focus-ring); outline-offset: 2px; }
    """
    d = discover(css)
    assert d.focus, "focus outline must be discovered"
    findings = audit_stylesheet(css)
    focus = [f for f in findings if "outline" in f.label]
    assert focus, "translucent ring fails 3:1 and must be reported"
    assert all(f.threshold == 3.0 for f in focus)
    assert any("alpha" in f.label for f in focus)


def test_opaque_focus_indicator_passes():
    css = BASE + """
    :root { --focus-indicator: #b23e02; }
    @media (prefers-color-scheme: dark) {
      :root { --focus-indicator: #ff9254; }
    }
    .btn:focus-visible { outline: 3px solid var(--focus-indicator); }
    """
    findings = [f for f in audit_stylesheet(css) if "outline" in f.label]
    assert findings == []


def test_discovers_gradient_button():
    css = BASE + """
    .btn { color: #fff8f0;
           background: linear-gradient(160deg, var(--persimmon) 0%, var(--persimmon-deep) 100%); }
    """
    d = discover(css)
    assert len(d.gradients) == 1
    findings = [f for f in audit_stylesheet(css) if ".btn" in f.label]
    assert findings, "bright gradient + near-white label must fail"


def test_discovers_plain_text_on_page_background():
    css = BASE + ".hint { color: #a2957f; }"
    d = discover(css)
    assert any(".hint" in c.label for c in d.flat)
    assert any(".hint" in f.label for f in audit_stylesheet(css))


def test_new_selector_is_covered_automatically():
    """The whole point: an unlisted control is audited the moment it exists."""
    css = BASE + ".brand-new-widget { color: #bbbbbb; background: #ffffff; }"
    findings = audit_stylesheet(css)
    assert any(".brand-new-widget" in f.label for f in findings)


def test_decorative_pseudo_elements_skipped():
    css = BASE + "body::before { color: #ccc; background: #fff; }"
    d = discover(css)
    assert not any("::before" in c.label for c in d.flat)


@pytest.mark.skipif(not REPO.exists(), reason="product repo not cloned")
def test_real_round4_prefix_is_caught():
    old = subprocess.run(["git", "show", "89a491b:src/index.css"], cwd=REPO,
                         capture_output=True, text=True)
    if old.returncode != 0:
        pytest.skip("commit unavailable")
    findings = audit_stylesheet(old.stdout)
    labels = " ".join(f.label for f in findings)
    assert "::selection" in labels, "round-4 selection defect must be caught"
    assert "outline" in labels, "round-4 focus defect must be caught"


@pytest.mark.skipif(not REPO.exists(), reason="product repo not cloned")
def test_real_fixed_stylesheet_is_clean():
    css = (REPO / "src/index.css").read_text()
    findings = audit_stylesheet(css)
    assert findings == [], [str(f) for f in findings]