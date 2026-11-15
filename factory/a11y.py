"""WCAG contrast computation — deterministic a11y gate (PRE-1).

Contrast ratio is arithmetic over hex colors, not a judgment call. This
module resolves CSS custom properties (including var() alias chains) per
theme and computes real WCAG 2.x ratios, so the gate can FAIL a build that
an LLM reviewer would wave through as "cosmetic".

Root cause this prevents: TOD-1 shipped 9 sub-4.5:1 text pairs that both the
deterministic gate and the cross-family reviewer passed (see
docs/experiments/tod-1-escaped-defects-2026-11-15.md).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

WCAG_AA_NORMAL = 4.5
WCAG_AA_LARGE = 3.0

_VAR_DECL = re.compile(r"(--[A-Za-z0-9-]+)\s*:\s*([^;{}]+)")
_VAR_USE = re.compile(r"var\(\s*(--[A-Za-z0-9-]+)\s*(?:,\s*([^)]*))?\)")
_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_DARK_BLOCK = re.compile(
    r"prefers-color-scheme:\s*dark[^{]*\{(.*?)\n\s*\}", re.S)


def _channel(c: int) -> float:
    x = c / 255.0
    return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4


def luminance(hexcolor: str) -> float:
    h = hexcolor.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(fg: str, bg: str) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def resolve_color(value: str, variables: dict[str, str],
                  _depth: int = 0) -> str | None:
    """Resolve a color value (hex or var() chain) to a literal hex, or None."""
    if _depth > 12 or value is None:
        return None
    value = value.strip()
    if _HEX.match(value):
        return value.lower()
    m = _VAR_USE.fullmatch(value)
    if m:
        name, fallback = m.group(1), m.group(2)
        if name in variables:
            got = resolve_color(variables[name], variables, _depth + 1)
            if got:
                return got
        if fallback:
            return resolve_color(fallback, variables, _depth + 1)
    return None


def theme_variables(css: str, *, dark: bool) -> dict[str, str]:
    """Light (:root) variables, optionally overlaid with the dark-theme block."""
    m = _DARK_BLOCK.search(css)
    dark_block = m.group(1) if m else ""
    light_css = css.replace(dark_block, "") if dark_block else css
    base = {k: v.strip() for k, v in _VAR_DECL.findall(light_css)}
    if dark and dark_block:
        base.update({k: v.strip() for k, v in _VAR_DECL.findall(dark_block)})
    return base


@dataclass
class ContrastCheck:
    """One foreground/background pairing to audit.

    `fg`/`bg` may be a token name (--ink-faint), a var() expression, or hex.
    `large_text` relaxes the threshold to 3:1 (>=18.66px bold or >=24px).
    """
    label: str
    fg: str
    bg: str
    large_text: bool = False

    @property
    def threshold(self) -> float:
        return WCAG_AA_LARGE if self.large_text else WCAG_AA_NORMAL


@dataclass
class ContrastFinding:
    theme: str
    label: str
    fg: str
    bg: str
    ratio: float
    threshold: float

    def __str__(self) -> str:
        return (f"{self.theme} {self.label}: {self.fg} on {self.bg} = "
                f"{self.ratio:.2f}:1 (needs {self.threshold}:1)")


def audit(css: str, checks: list[ContrastCheck]) -> list[ContrastFinding]:
    """Return every failing pairing across light and dark themes.

    Unresolvable colors are reported as failures (fail-closed): a token we
    cannot resolve is a token we cannot certify.
    """
    findings: list[ContrastFinding] = []
    for dark in (False, True):
        variables = theme_variables(css, dark=dark)
        theme = "dark" if dark else "light"
        for chk in checks:
            fg = resolve_color(chk.fg, variables)
            bg = resolve_color(chk.bg, variables)
            if not fg or not bg:
                findings.append(ContrastFinding(
                    theme=theme, label=chk.label, fg=chk.fg, bg=chk.bg,
                    ratio=0.0, threshold=chk.threshold))
                continue
            r = contrast_ratio(fg, bg)
            if r < chk.threshold:
                findings.append(ContrastFinding(
                    theme=theme, label=chk.label, fg=fg, bg=bg,
                    ratio=r, threshold=chk.threshold))
    return findings