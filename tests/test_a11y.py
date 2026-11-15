"""a11y contrast gate tests — includes the REAL TOD-1 regression.

The before/after CSS fixtures are the actual shipped defect: 9 sub-4.5:1
pairs that our gate + cross-family reviewer both passed.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.a11y import (ContrastCheck, audit, contrast_ratio, luminance,
                          resolve_color, theme_variables)

# --- the real defect, reduced to the tokens that mattered ---
BAD_CSS = """
:root {
  --paper: #f7f1e5;
  --surface-raised: #fffefb;
  --ink: #2b2118;
  --ink-soft: #6f6353;
  --ink-faint: #a2957f;
  --persimmon: #d94f04;
  --persimmon-deep: #b23e02;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #191410;
    --surface-raised: #2a221b;
    --ink: #f0e7d8;
    --ink-soft: #b3a68f;
    --ink-faint: #7d715c;
    --persimmon: #ff7a2f;
    --persimmon-deep: #ff9254;
  }
}
"""

# the fix: alias the faint token to the soft one, deepen the eyebrow
GOOD_CSS = BAD_CSS.replace("--ink-faint: #a2957f;", "--ink-faint: var(--ink-soft);") \
                  .replace("--ink-faint: #7d715c;", "--ink-faint: var(--ink-soft);")

CHECKS = [
    ContrastCheck("placeholder", "var(--ink-faint)", "var(--surface-raised)"),
    ContrastCheck("add-hint", "var(--ink-faint)", "var(--paper)"),
    ContrastCheck("task-count", "var(--ink-faint)", "var(--paper)"),
    ContrastCheck("footer", "var(--ink-faint)", "var(--paper)"),
]


def test_known_wcag_ratios():
    assert contrast_ratio("#000000", "#ffffff") == pytest.approx(21.0)
    assert contrast_ratio("#ffffff", "#ffffff") == pytest.approx(1.0)
    assert luminance("#000000") == 0.0
    assert luminance("#ffffff") == pytest.approx(1.0)


def test_short_hex_expands():
    assert contrast_ratio("#000", "#fff") == pytest.approx(21.0)


def test_var_alias_chain_resolves():
    css = ":root { --a: #123456; --b: var(--a); --c: var(--b); }"
    v = theme_variables(css, dark=False)
    assert resolve_color("var(--c)", v) == "#123456"


def test_var_fallback_used():
    v = {"--x": "var(--missing)"}
    assert resolve_color("var(--x, #abcdef)", v) == "#abcdef"


def test_unresolvable_is_none():
    assert resolve_color("var(--nope)", {}) is None
    assert resolve_color("rgb(1,2,3)", {}) is None


def test_dark_theme_overlays_light():
    v = theme_variables(BAD_CSS, dark=True)
    assert v["--paper"] == "#191410"
    assert v["--ink-soft"] == "#b3a68f"


def test_real_tod1_defect_is_caught():
    """The regression: 8 failing pairs across both themes (4 selectors x 2)."""
    findings = audit(BAD_CSS, CHECKS)
    assert len(findings) == 8, [str(f) for f in findings]
    assert all(f.ratio < 4.5 for f in findings)
    assert {f.theme for f in findings} == {"light", "dark"}


def test_real_tod1_fix_passes():
    assert audit(GOOD_CSS, CHECKS) == []


def test_eyebrow_defect_caught_and_fixed():
    bad = audit(BAD_CSS, [ContrastCheck("eyebrow", "var(--persimmon)", "var(--paper)")])
    # light fails (3.68:1), dark passes (7.03:1)
    assert len(bad) == 1
    assert bad[0].theme == "light"
    assert bad[0].ratio == pytest.approx(3.68, abs=0.01)
    good = audit(BAD_CSS, [ContrastCheck("eyebrow", "var(--persimmon-deep)", "var(--paper)")])
    assert good == []


def test_large_text_relaxed_threshold():
    # 3.68:1 fails normal (4.5) but passes large (3.0)
    checks = [ContrastCheck("eyebrow", "var(--persimmon)", "var(--paper)", large_text=True)]
    assert audit(BAD_CSS, checks) == []


def test_unresolvable_token_fails_closed():
    findings = audit(BAD_CSS, [ContrastCheck("ghost", "var(--nope)", "var(--paper)")])
    assert len(findings) == 2  # both themes, fail-closed
    assert all(f.ratio == 0.0 for f in findings)


def test_finding_str_is_actionable():
    f = audit(BAD_CSS, CHECKS)[0]
    text = str(f)
    assert ":1" in text and "needs 4.5:1" in text and f.label in text


# --- TOD-5 false-failure class: translucent wash backgrounds ---
WASH_CSS = BAD_CSS + """
:root {
  --persimmon-wash: rgba(217, 79, 4, 0.09);
}
@media (prefers-color-scheme: dark) {
  :root {
    --persimmon-wash: rgba(255, 122, 47, 0.12);
  }
}
"""


def test_translucent_wash_background_is_composited_not_zero():
    # The pressed filter button: deep persimmon text on a 9%-alpha wash.
    # Old gate resolved the rgba to None and reported 0.00:1 (false fail);
    # composited over the real backdrop it passes AA in both themes.
    checks = [ContrastCheck('pressed[aria-pressed="true"]',
                            "var(--persimmon-deep)", "var(--persimmon-wash)")]
    findings = audit(WASH_CSS, checks)
    assert findings == [], [str(f) for f in findings]


def test_translucent_wash_still_fails_when_text_is_weak():
    # Fail-closed direction: faint text on the same wash must still fail.
    checks = [ContrastCheck("weak-on-wash",
                            "var(--ink-faint)", "var(--persimmon-wash)")]
    findings = audit(WASH_CSS, checks)
    assert len(findings) == 2  # both themes
    assert all(0.0 < f.ratio < 4.5 for f in findings)


# --- control-arm false-failure class: literal-hex rule-level dark overrides ---
# No CSS variables: colors are literal hex, redeclared per rule in @media dark.
LITERAL_CSS = """
body { background: #f7f1e5; }
.error { color: #b42318; }
@media (prefers-color-scheme: dark) {
  body { background: #16171d; }
  .error { color: #fda29b; }
}
"""


def test_literal_hex_dark_override_not_false_failed():
    # .error light #b42318 on #f7f1e5 passes; dark #fda29b on #16171d passes.
    # Without rule-level dark resolution the gate measured the LIGHT hex on
    # the DARK backdrop (2.72:1) and false-failed. Both themes must pass.
    checks = [ContrastCheck(".error (on page)", "#b42318", "#f7f1e5",
                            selector=".error", inherited_bg=True)]
    findings = audit(LITERAL_CSS, checks)
    assert findings == [], [str(f) for f in findings]


def test_literal_hex_dark_override_still_fails_when_dark_color_weak():
    # Fail-closed direction: a dark override that is itself too weak must fail.
    css = LITERAL_CSS.replace(".error { color: #fda29b; }",
                              ".error { color: #5a2a26; }")
    checks = [ContrastCheck(".error (on page)", "#b42318", "#f7f1e5",
                            selector=".error", inherited_bg=True)]
    findings = audit(css, checks)
    assert len(findings) == 1
    assert findings[0].theme == "dark"
    assert findings[0].ratio < 4.5