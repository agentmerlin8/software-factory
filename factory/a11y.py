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


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def apply_brightness(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    """CSS `filter: brightness(f)` — per-channel multiply, clamped to [0,255]."""
    return tuple(min(255, max(0, round(c * factor))) for c in rgb)  # type: ignore[return-value]


def mix_rgb(a: tuple[int, int, int], b: tuple[int, int, int],
            t: float) -> tuple[int, int, int]:
    """Linear interpolation between two gradient stops (t in [0,1])."""
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def ratio_rgb(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    def _lum(c: tuple[int, int, int]) -> float:
        return (0.2126 * _channel(c[0]) + 0.7152 * _channel(c[1])
                + 0.0722 * _channel(c[2]))
    a, b = _lum(fg), _lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


@dataclass
class GradientCheck:
    """A label over a GRADIENT fill, audited across stops AND state filters.

    Round-3 lesson: a flat-color contrast gate passes a button whose gradient
    start (or hover-brightened fill) fails. Audit every stop under every
    interactive-state brightness factor, in both themes.
    """
    label: str
    fg: str
    fill_from: str
    fill_to: str
    brightness_factors: tuple[float, ...] = (1.0, 1.07, 0.96)
    stops: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)
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

def audit_gradients(css: str,
                    checks: list[GradientCheck]) -> list[ContrastFinding]:
    """Audit gradient-filled controls across stops, states, and themes."""
    findings: list[ContrastFinding] = []
    for dark in (False, True):
        variables = theme_variables(css, dark=dark)
        theme = "dark" if dark else "light"
        for chk in checks:
            fg_hex = resolve_color(chk.fg, variables)
            a_hex = resolve_color(chk.fill_from, variables)
            b_hex = resolve_color(chk.fill_to, variables)
            if not (fg_hex and a_hex and b_hex):
                findings.append(ContrastFinding(
                    theme=theme, label=chk.label, fg=chk.fg,
                    bg=f"{chk.fill_from}->{chk.fill_to}", ratio=0.0,
                    threshold=chk.threshold))
                continue
            fg = _hex_to_rgb(fg_hex)
            a, b = _hex_to_rgb(a_hex), _hex_to_rgb(b_hex)
            worst = float("inf")
            worst_ctx = ""
            for factor in chk.brightness_factors:
                for t in chk.stops:
                    bg = apply_brightness(mix_rgb(a, b, t), factor)
                    r = ratio_rgb(fg, bg)
                    if r < worst:
                        worst = r
                        worst_ctx = f"stop {t:.0%} @brightness {factor}"
            if worst < chk.threshold:
                findings.append(ContrastFinding(
                    theme=theme, label=f"{chk.label} ({worst_ctx})",
                    fg=fg_hex, bg=f"{a_hex}->{b_hex}", ratio=worst,
                    threshold=chk.threshold))
    return findings
