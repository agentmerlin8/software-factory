"""CSS surface discovery — audit what the stylesheet DECLARES, not a hardcoded list.

Root cause across rounds 2-4: every gate version enumerated specific selectors,
so each round surfaced a selector nobody had listed (::selection, then the
focus outline). Three rounds of the same family means close the FORM SPACE:
derive the audit set from the CSS itself so a new styled control is covered the
moment it is written.

This module walks the stylesheet and emits checks for:
  - every rule with a `color` + a resolvable background (flat or gradient)
  - ::selection pairs
  - :focus-visible / :focus outlines (non-text, 3:1, alpha-composited)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .a11y import (ContrastCheck, GradientCheck, NonTextCheck, SelectionCheck,
                   audit, audit_gradients, audit_non_text, audit_selection,
                   dark_blocks, dark_rule_overrides, theme_variables)

_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
_COLOR = re.compile(r"(?:^|;)\s*color\s*:\s*([^;]+)", re.S)
_BG = re.compile(r"(?:^|;)\s*background(?:-color)?\s*:\s*([^;]+)", re.S)
_OUTLINE = re.compile(r"outline\s*:\s*([^;]+)", re.S)
def _func_args(text: str, fname: str) -> str | None:
    """Extract the argument list of `fname(...)` with BALANCED parens.

    A regex stops at the first ')' — which lands inside the first var() of a
    gradient and silently truncates the stop list.
    """
    i = text.find(fname + "(")
    if i == -1:
        return None
    j = i + len(fname) + 1
    depth = 1
    while j < len(text):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[i + len(fname) + 1:j]
        j += 1
    return None
_VAR_REF = re.compile(r"var\(\s*(--[A-Za-z0-9-]+)\s*\)")
_MEDIA_DARK = re.compile(r"prefers-color-scheme:\s*dark")

# Pseudo-elements/states that are not standalone text surfaces.
_SKIP_SELECTOR = re.compile(r"::?(before|after|placeholder|marker|backdrop)\b")


@dataclass
class Discovery:
    flat: list[ContrastCheck] = field(default_factory=list)
    gradients: list[GradientCheck] = field(default_factory=list)
    selections: list[SelectionCheck] = field(default_factory=list)
    focus: list[NonTextCheck] = field(default_factory=list)

    def total(self) -> int:
        return (len(self.flat) + len(self.gradients)
                + len(self.selections) + len(self.focus))


def _strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _root_background(css: str, dark: bool = False) -> str:
    """The page backdrop for rules that declare no background of their own.

    A layered body background (decorative radial washes over a solid base)
    must resolve to the SOLID base — picking the first var() grabs a
    translucent wash and every inherited-text check then measures garbage.
    Prefer an explicit solid token; fall back to the last opaque layer.

    For literal-hex themes the body background is redeclared per rule inside
    @media dark; when dark=True, apply that rule-level override so the dark
    backdrop is measured (not the baked light hex).
    """
    v = theme_variables(css, dark=dark)
    for token in ("--paper", "--bg", "--surface"):
        if token in v:
            val = v[token].strip()
            if val.startswith("#"):
                # Return the TOKEN, not the resolved light-theme hex: baking a
                # hex here makes every dark-theme check measure the light value.
                return f"var({token})"
            if val.startswith("var("):
                return val
    # Literal-hex path: read the body background, applying dark rule overrides.
    body_bg = None
    m = re.search(r"\bbody\s*\{([^{}]*)\}", css, re.S)
    if m:
        bg = _BG.search(m.group(1))
        if bg:
            body_bg = bg.group(1).strip()
    if dark:
        over = dark_rule_overrides(css).get("body", {})
        if "background" in over:
            body_bg = over["background"]
    if body_bg:
        if body_bg.startswith("#"):
            return body_bg
        if body_bg.startswith("var("):
            return body_bg
        # last declared var() in a layered background is the base layer
        refs = _VAR_REF.findall(body_bg)
        for ref in reversed(refs):
            cand = v.get(ref, "")
            if cand.strip().startswith("#"):
                return f"var({ref})"
    return "#ffffff"


def _surrounding_surfaces(css: str) -> list[str]:
    v = theme_variables(css, dark=False)
    out = []
    for token in ("--paper", "--surface", "--surface-raised", "--bg"):
        if token in v:
            out.append(f"var({token})")
    return out or [_root_background(css)]


def discover(css: str) -> Discovery:
    """Derive the audit set from the stylesheet's own declarations."""
    css = _strip_comments(css)
    # Exclude the dark @media block from rule walking: theme_variables already
    # overlays those declarations, and walking them twice double-counts.
    # dark_blocks must run on the SAME stripped text — a block extracted from
    # raw CSS (comments intact) never matches the stripped walkable, so dark
    # overrides leak into the light walk and get re-measured against the dark
    # backdrop (TOD-5 control-arm false failure: .error 2.72:1).
    walkable = css
    for blk in dark_blocks(css):
        walkable = walkable.replace(blk, "")

    d = Discovery()
    page_bg = _root_background(css)
    surfaces = _surrounding_surfaces(css)
    seen_flat: set[tuple[str, str, str]] = set()
    seen_focus: set[tuple[str, str]] = set()

    for sel_raw, body in _RULE.findall(walkable):
        sel = " ".join(sel_raw.split())
        if not sel or sel.startswith("@") or _MEDIA_DARK.search(sel):
            continue

        # --- ::selection ---
        if "::selection" in sel:
            fg = _COLOR.search(body)
            bg = _BG.search(body)
            if fg and bg:
                d.selections.append(SelectionCheck(
                    "::selection", fg.group(1).strip(), bg.group(1).strip()))
            continue

        # --- focus indicators (non-text, 3:1) ---
        if ":focus-visible" in sel or re.search(r":focus\b", sel):
            ol = _OUTLINE.search(body)
            if ol:
                parts = ol.group(1).strip().split()
                color = next((p for p in parts
                              if p.startswith(("#", "var(", "rgb"))), None)
                if color:
                    for surf in surfaces:
                        key = (sel, color + surf)
                        if key in seen_focus:
                            continue
                        seen_focus.add(key)
                        d.focus.append(NonTextCheck(
                            f"{sel} outline vs {surf}", color, surf))
            continue

        if _SKIP_SELECTOR.search(sel):
            continue

        # --- gradient-filled controls ---
        bg = _BG.search(body)
        fg = _COLOR.search(body)
        if bg and fg:
            grad_args = _func_args(bg.group(1), "linear-gradient")
            if grad_args is not None:
                stops = _VAR_REF.findall(grad_args)
                if len(stops) >= 2:
                    d.gradients.append(GradientCheck(
                        sel, fg.group(1).strip(),
                        f"var({stops[0]})", f"var({stops[-1]})"))
                continue
            bg_val = bg.group(1).strip()
            if bg_val in ("transparent", "inherit", "none", "unset"):
                bg_val = page_bg
            elif bg_val.startswith(("linear", "radial", "url(")):
                continue
            key = (sel, fg.group(1).strip(), bg_val)
            if key not in seen_flat:
                seen_flat.add(key)
                d.flat.append(ContrastCheck(sel, fg.group(1).strip(), bg_val,
                                            selector=sel))
            continue

        # --- text with an inherited background ---
        if fg and not bg:
            val = fg.group(1).strip()
            if val in ("inherit", "currentColor", "transparent"):
                continue
            key = (sel, val, page_bg)
            if key not in seen_flat:
                seen_flat.add(key)
                d.flat.append(ContrastCheck(f"{sel} (on page)", val, page_bg,
                                            selector=sel, inherited_bg=True))

    return d


def audit_stylesheet(css: str) -> list:
    """Full discovered audit: flat + gradient + selection + focus, both themes."""
    d = discover(css)
    findings = []
    findings += audit(css, d.flat)
    findings += audit_gradients(css, d.gradients)
    findings += audit_selection(css, d.selections)
    findings += audit_non_text(css, d.focus)
    return findings