"""Untrusted-boundary checks — the round-3 crash class (PRE-6).

TOD-1 round 3: `loadTasks()` checked only `Array.isArray`, so `[null]` reached
the render and threw during mount. The storage boundary is UNTRUSTED (older
versions, other tabs, devtools, quota-truncated writes).

Rule: any function that parses external data into a typed collection must
validate the ELEMENTS, not just the container. This is a static, deterministic
check — no model judgment required.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# A parse boundary: JSON.parse / storage read feeding a typed return.
_PARSE = re.compile(r"JSON\.parse\s*\(")
# Container-only validation: `Array.isArray(x) ? (x as T[]) : []`
_CAST_ONLY = re.compile(
    r"Array\.isArray\s*\(\s*(\w+)\s*\)\s*\?\s*\(\s*\1\s+as\s+\w+\[\]\s*\)")
# Evidence of element-level validation somewhere in the module.
# NOTE: `isArray` must NOT count as an element guard — it is the container
# check itself, and matching it lets the defect vouch for itself.
_ELEMENT_GUARD = re.compile(
    r"\b(is(?!Array\b)[A-Z]\w*|validate\w*|assert\w*)\s*\(|"
    r"\.filter\s*\(\s*\w+\s*=>|"
    r"typeof\s+\w+\.\w+\s*===|"
    r"\bfor\s*\(\s*const\s+\w+\s+of\b")


@dataclass
class BoundaryResult:
    passed: bool
    failures: list[str] = field(default_factory=list)

    def named_failures(self) -> str:
        return "; ".join(self.failures) if self.failures else "none"


def _enclosing_function(text: str, at: int) -> str:
    """Return the source of the function containing offset `at`.

    Scoping matters: a module-wide guard search lets an unrelated `for` loop
    or `typeof` elsewhere in the file vouch for an unvalidated parse.
    """
    start = text.rfind("function ", 0, at)
    arrow = text.rfind("=>", 0, at)
    if start == -1 and arrow == -1:
        return text
    if arrow > start:
        start = max(text.rfind("const ", 0, arrow), text.rfind("export ", 0, arrow), 0)
    depth = 0
    i = text.find("{", start)
    if i == -1:
        return text[start:]
    j = i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[start:j + 1]
        j += 1
    return text[start:]


def check_file(path: Path) -> BoundaryResult:
    """Flag container-only validation at a JSON parse boundary."""
    text = Path(path).read_text(encoding="utf-8")
    failures: list[str] = []
    for m in _CAST_ONLY.finditer(text):
        fn = _enclosing_function(text, m.start())
        if not _PARSE.search(fn):
            continue
        if not _ELEMENT_GUARD.search(fn):
            failures.append(
                f"{Path(path).name}: JSON.parse result cast to a typed array "
                f"with only Array.isArray ({m.group(0)[:60]}…) — validate "
                f"ELEMENTS at the boundary (malformed entries crash the render)")
    return BoundaryResult(passed=not failures, failures=failures)


def check_tree(root: Path, glob: str = "src/**/*.ts*") -> BoundaryResult:
    failures: list[str] = []
    for p in sorted(Path(root).glob(glob)):
        if p.name.endswith((".test.ts", ".test.tsx")):
            continue
        failures.extend(check_file(p).failures)
    return BoundaryResult(passed=not failures, failures=failures)