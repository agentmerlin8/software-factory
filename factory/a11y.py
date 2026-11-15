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
WCAG_NON_TEXT = 3.0

_VAR_DECL = re.compile(r"(--[A-Za-z0-9-]+)\s*:\s*([^;{}]+)")
_VAR_USE = re.compile(r"var\(\s*(--[A-Za-z0-9-]+)\s*(?:,\s*([^)]*))?\)")
_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGBA = re.compile(r"^rgba?\(([^)]+)\)$")
_DARK_BLOCK = re.compile(
    r"prefers-color-scheme:\s*dark[^{]*\{(.*?)\n\s*\}", re.S)


def dark_blocks(css: str) -> list[str]:
    """Bodies of ALL dark @media blocks, by balanced braces.

    Two failure modes this avoids: a non-greedy regex stops at the first inner
    '}' (leaking later rules), and taking only the FIRST block leaks every
    subsequent dark block into the light-theme walk.
    """
    out: list[str] = []
    for m in re.finditer(r"@media[^{]*prefers-color-scheme:\s*dark[^{]*\{", css):
        i = m.end()
        depth = 1
        j = i
        while j < len(css):
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
                if depth == 0:
                    out.append(css[i:j])
                    break
            j += 1
        else:
            out.append(css[i:])
    return out


def dark_block(css: str) -> str:
    """Concatenated bodies of every dark @media block (see dark_blocks)."""
    return "\n".join(dark_blocks(css))


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


def parse_rgba(value: str) -> tuple[int, int, int, float] | None:
    """Parse rgb()/rgba() into (r,g,b,alpha). Returns None for other forms."""
    m = _RGBA.match(value.strip())
    if not m:
        return None
    parts = [p.strip() for p in m.group(1).replace("/", ",").split(",") if p.strip()]
    if len(parts) < 3:
        return None
    try:
        rgb = tuple(int(float(p)) for p in parts[:3])
        alpha = float(parts[3]) if len(parts) > 3 else 1.0
    except ValueError:
        return None
    return (*rgb, alpha)  # type: ignore[return-value]


def composite(fg: tuple[int, int, int, float],
              bg: tuple[int, int, int]) -> tuple[int, int, int]:
    """Source-over alpha compositing.

    Round-4 root cause: a translucent focus ring's contrast is meaningless
    until it is composited over its REAL backdrop. rgba(...,0.35) measured
    1.61:1, not the ~4:1 its opaque base color would suggest.
    """
    a = fg[3]
    return tuple(round(fg[i] * a + bg[i] * (1 - a)) for i in range(3))  # type: ignore[return-value]


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
    blocks = dark_blocks(css)
    light_css = css
    for blk in blocks:
        light_css = light_css.replace(blk, "")
    base = {k: v.strip() for k, v in _VAR_DECL.findall(light_css)}
    if dark:
        for blk in blocks:
            base.update({k: v.strip() for k, v in _VAR_DECL.findall(blk)})
    return base


_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
_COLOR_DECL = re.compile(r"(?:^|;)\s*color\s*:\s*([^;]+)", re.S)
_BG_DECL = re.compile(r"(?:^|;)\s*background(?:-color)?\s*:\s*([^;]+)", re.S)


def dark_rule_overrides(css: str) -> dict[str, dict[str, str]]:
    """Per-selector color/background overrides declared inside dark @media.

    Literal-hex themes (no CSS variables) redeclare colors per rule in a dark
    block, e.g. `.error { color:#b42318 }` light and `.error { color:#fda29b }`
    dark. theme_variables only overlays :root custom properties, so without
    this the audit measures the LIGHT hex against the DARK backdrop and
    false-fails (control-arm .error 2.72:1, actually ~9:1). Returns
    {normalized_selector: {"color": val, "background": val}} for dark rules.
    """
    out: dict[str, dict[str, str]] = {}
    for blk in dark_blocks(css):
        for sel_raw, body in _RULE_RE.findall(blk):
            sel = " ".join(sel_raw.split())
            if not sel or sel.startswith("@") or sel == ":root":
                continue
            entry = out.setdefault(sel, {})
            c = _COLOR_DECL.search(body)
            if c:
                entry["color"] = c.group(1).strip()
            b = _BG_DECL.search(body)
            if b:
                entry["background"] = b.group(1).strip()
    return out


@dataclass
class ContrastCheck:
    """One foreground/background pairing to audit.

    `fg`/`bg` may be a token name (--ink-faint), a var() expression, or hex.
    `large_text` relaxes the threshold to 3:1 (>=18.66px bold or >=24px).
    `selector` (when set) lets the audit apply rule-level dark @media color
    overrides for this exact selector — literal-hex themes redeclare colors
    per rule rather than via variables.
    """
    label: str
    fg: str
    bg: str
    large_text: bool = False
    selector: str | None = None
    # True when bg is the inherited page backdrop (rule declares no background).
    # The audit re-resolves it per theme so literal-hex dark body overrides apply.
    inherited_bg: bool = False

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
    cannot resolve is a token we cannot certify. Translucent backgrounds
    (rgba washes) are alpha-composited over the page backdrop per theme —
    resolving them to None and reporting 0.00:1 was a false-failure class
    (TOD-5: the pressed filter button's 9%-alpha wash actually passes AA).
    """
    from .css_audit import _root_background
    dark_over = dark_rule_overrides(css)
    findings: list[ContrastFinding] = []
    for dark in (False, True):
        variables = theme_variables(css, dark=dark)
        theme = "dark" if dark else "light"
        page_bg = _root_background(css, dark=dark)
        backdrop = _resolve_rgba(page_bg, variables) or (255, 255, 255, 1.0)
        backdrop_rgb = composite(backdrop, (255, 255, 255))
        for chk in checks:
            fg_val, bg_val = chk.fg, chk.bg
            # Inherited background: re-resolve the page backdrop per theme so
            # literal-hex dark body overrides apply (not the baked light hex).
            if chk.inherited_bg:
                bg_val = page_bg
            # Rule-level dark overrides: literal-hex themes redeclare colors
            # per selector inside @media dark. Apply them so we measure the
            # DARK color, not the light hex on the dark backdrop.
            if dark and chk.selector:
                over = dark_over.get(" ".join(chk.selector.split()), {})
                if "color" in over:
                    fg_val = over["color"]
                if "background" in over:
                    bg_val = over["background"]
            fg = _resolve_rgba(fg_val, variables)
            bg = _resolve_rgba(bg_val, variables)
            if not fg or not bg:
                findings.append(ContrastFinding(
                    theme=theme, label=chk.label, fg=fg_val, bg=bg_val,
                    ratio=0.0, threshold=chk.threshold))
                continue
            bg_rgb = composite(bg, backdrop_rgb)
            fg_rgb = composite(fg, bg_rgb)
            r = ratio_rgb(fg_rgb, bg_rgb)
            if r < chk.threshold:
                findings.append(ContrastFinding(
                    theme=theme, label=chk.label,
                    fg=f"rgb{fg_rgb}", bg=f"rgb{bg_rgb}",
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


@dataclass
class NonTextCheck:
    """A focus indicator / UI boundary: WCAG 2.2 non-text contrast needs 3:1.

    `fg` may be translucent — it is composited over `bg` before measuring.
    """
    label: str
    fg: str
    bg: str
    threshold: float = WCAG_NON_TEXT


@dataclass
class SelectionCheck:
    """::selection text — normal text rules apply (4.5:1)."""
    label: str
    fg: str
    bg: str
    threshold: float = WCAG_AA_NORMAL


def _resolve_rgba(value: str, variables: dict[str, str],
                  _depth: int = 0) -> tuple[int, int, int, float] | None:
    if _depth > 12 or value is None:
        return None
    value = value.strip()
    m = _VAR_USE.fullmatch(value)
    if m:
        name, fallback = m.group(1), m.group(2)
        if name in variables:
            got = _resolve_rgba(variables[name], variables, _depth + 1)
            if got:
                return got
        if fallback:
            return _resolve_rgba(fallback, variables, _depth + 1)
        return None
    hexed = resolve_color(value, variables, _depth)
    if hexed:
        return (*_hex_to_rgb(hexed), 1.0)  # type: ignore[return-value]
    return parse_rgba(value)


def audit_non_text(css: str,
                   checks: list[NonTextCheck]) -> list[ContrastFinding]:
    """Audit focus indicators and other non-text UI against 3:1.

    Translucent colors are alpha-composited over the declared backdrop first.
    """
    findings: list[ContrastFinding] = []
    for dark in (False, True):
        variables = theme_variables(css, dark=dark)
        theme = "dark" if dark else "light"
        for chk in checks:
            fg = _resolve_rgba(chk.fg, variables)
            bg = _resolve_rgba(chk.bg, variables)
            if not fg or not bg:
                findings.append(ContrastFinding(
                    theme=theme, label=chk.label, fg=chk.fg, bg=chk.bg,
                    ratio=0.0, threshold=chk.threshold))
                continue
            bg_rgb = composite(bg, (255, 255, 255))
            fg_rgb = composite(fg, bg_rgb)
            r = ratio_rgb(fg_rgb, bg_rgb)
            if r < chk.threshold:
                note = f" (alpha {fg[3]})" if fg[3] < 1.0 else ""
                findings.append(ContrastFinding(
                    theme=theme, label=f"{chk.label}{note}",
                    fg=f"rgb{fg_rgb}", bg=f"rgb{bg_rgb}", ratio=r,
                    threshold=chk.threshold))
    return findings


def audit_selection(css: str,
                    checks: list[SelectionCheck]) -> list[ContrastFinding]:
    """Audit ::selection text pairs (4.5:1) across themes."""
    return audit_non_text(css, [
        NonTextCheck(c.label, c.fg, c.bg, c.threshold) for c in checks])
