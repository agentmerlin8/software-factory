"""Gradient/state contrast gate tests — the REAL round-3 button regression.

Round 3 escaped because the flat-color gate never looked at the button's
gradient fill or its hover brightness. 15/18 combos failed, including dark
mode at 1.96:1 that the reviewer did not even report.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.a11y import (GradientCheck, apply_brightness, audit_gradients,
                          mix_rgb, ratio_rgb)

# The defective button: near-white label on a bright persimmon gradient,
# identical in both themes (the dark theme never overrode the label).
BAD_CSS = """
:root {
  --persimmon: #d94f04;
  --persimmon-deep: #b23e02;
}
@media (prefers-color-scheme: dark) {
  :root {
    --persimmon: #ff7a2f;
    --persimmon-deep: #ff9254;
  }
}
"""

# The fix: per-theme audited fill/label tokens; dark uses a DARK label.
GOOD_CSS = """
:root {
  --btn-fill-from: #b23e02;
  --btn-fill-to: #8a2f02;
  --btn-label: #fff8f0;
}
@media (prefers-color-scheme: dark) {
  :root {
    --btn-fill-from: #ff7a2f;
    --btn-fill-to: #ff9254;
    --btn-label: #2b1608;
  }
}
"""

BAD_CHECK = [GradientCheck("add-button", "#fff8f0",
                           "var(--persimmon)", "var(--persimmon-deep)")]
GOOD_CHECK = [GradientCheck("add-button", "var(--btn-label)",
                            "var(--btn-fill-from)", "var(--btn-fill-to)")]


def test_brightness_clamps():
    assert apply_brightness((255, 200, 100), 1.07) == (255, 214, 107)
    assert apply_brightness((10, 10, 10), 0.5) == (5, 5, 5)
    assert apply_brightness((250, 250, 250), 2.0) == (255, 255, 255)


def test_mix_endpoints():
    a, b = (0, 0, 0), (255, 255, 255)
    assert mix_rgb(a, b, 0.0) == (0, 0, 0)
    assert mix_rgb(a, b, 1.0) == (255, 255, 255)
    assert mix_rgb(a, b, 0.5) == (128, 128, 128)


def test_ratio_rgb_matches_hex_api():
    assert ratio_rgb((0, 0, 0), (255, 255, 255)) == pytest.approx(21.0)


def test_real_round3_button_defect_is_caught():
    """Both themes fail; dark is far worse than the reviewer reported."""
    findings = audit_gradients(BAD_CSS, BAD_CHECK)
    assert len(findings) == 2
    by_theme = {f.theme: f for f in findings}
    assert by_theme["light"].ratio < 4.5
    assert by_theme["dark"].ratio < 3.0  # measured ~1.96:1
    assert "brightness" in by_theme["dark"].label


def test_real_round3_fix_passes():
    assert audit_gradients(GOOD_CSS, GOOD_CHECK) == []


def test_hover_only_failure_is_detected():
    """A fill that passes at rest but fails under hover brightness."""
    css = """
    :root { --a: #c0460c; --b: #8a2f02; }
    @media (prefers-color-scheme: dark) {
      :root { --a: #c0460c; --b: #8a2f02; }
    }
    """
    # measured: 4.84:1 at rest, 4.33:1 under hover -> must be caught
    at_rest = audit_gradients(css, [GradientCheck(
        "btn", "#fff8f0", "var(--a)", "var(--b)", brightness_factors=(1.0,))])
    with_hover = audit_gradients(css, [GradientCheck(
        "btn", "#fff8f0", "var(--a)", "var(--b)", brightness_factors=(1.07,))])
    assert at_rest == []
    assert len(with_hover) == 2  # hover pushes it under 4.5 in both themes


def test_unresolvable_gradient_fails_closed():
    findings = audit_gradients(BAD_CSS, [GradientCheck(
        "ghost", "#ffffff", "var(--nope)", "var(--also-nope)")])
    assert len(findings) == 2
    assert all(f.ratio == 0.0 for f in findings)