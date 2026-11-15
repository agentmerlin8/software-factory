"""Story-spec checks — deterministic intake/planning rules (PRE-3, PRE-4).

A defect that originates in the SPECIFICATION cannot be caught by a coder
who builds exactly what was asked. TOD-1 had four happy-path ACs and no
failure-path AC, so nothing tested the storage-throws path.

These checks run at planning time, before any dispatch is sealed.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Signals that a story touches a fallible boundary.
IO_SIGNALS = re.compile(
    r"\b(localStorage|sessionStorage|IndexedDB|fetch|XMLHttpRequest|axios|"
    r"persist\w*|storage|network|request|upload|download|parse|JSON\.parse|"
    r"readFile|writeFile|database|query|socket|quota)\b", re.I)

# Signals that a failure-mode AC is present. Must describe a SYSTEM/BOUNDARY
# failure, not user-input validation: "empty input is rejected" is an input
# rule, NOT failure handling (that false negative let TOD-1 through).
FAILURE_AC = re.compile(
    r"\b(fails?|failed|failure|throws?|throwing|unavailable|blocked|"
    r"quota|offline|timeout|timed out|corrupt\w*|denied|unwritable|"
    r"read-only|out of (?:space|memory)|error (?:message|state|feedback)|"
    r"storage (?:error|fail\w*)|network (?:error|fail\w*)|"
    r"retry|graceful\w*|degrade\w*|unreadable|unparseable|"
    r"falls? back|fallback|instead of crashing|invalid (?:stored|data|value|"
    r"json|state|input data))\b", re.I)

MAX_ACS = 6  # slice law (DEC-023)


@dataclass
class SpecResult:
    passed: bool
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def named_failures(self) -> str:
        return "; ".join(self.failures) if self.failures else "none"


def _acceptance_section(text: str) -> str:
    m = re.search(r"##\s*Acceptance criteria(.*?)(?=\n##|\Z)", text, re.S | re.I)
    return m.group(1) if m else ""


def check_story(text: str) -> SpecResult:
    """Validate a story spec before it may be dispatched."""
    failures: list[str] = []
    warnings: list[str] = []

    acs = _acceptance_section(text)
    if not acs.strip():
        failures.append("no 'Acceptance criteria' section")
        return SpecResult(False, failures, warnings)

    numbered = re.findall(r"^\s*\d+\.\s+\S", acs, re.M)
    if not numbered:
        failures.append("acceptance criteria are not numbered/testable")
    elif len(numbered) > MAX_ACS:
        failures.append(
            f"{len(numbered)} ACs exceeds the slice limit ({MAX_ACS}); split the story")

    # PRE-3: fallible boundary requires a failure-mode AC
    touches_io = bool(IO_SIGNALS.search(text))
    has_failure_ac = bool(FAILURE_AC.search(acs))
    if touches_io and not has_failure_ac:
        failures.append(
            "story touches a fallible boundary (I/O/storage/parse) but has NO "
            "failure-mode AC — add one ('when X fails, the user sees Y and "
            "loses no data')")

    if not re.search(r"##\s*Manifest", text, re.I):
        failures.append("no Manifest section (scope cannot be gated)")

    if not re.search(r"##\s*Named tests", text, re.I):
        warnings.append("no 'Named tests' section; the gate cannot verify test intent")

    return SpecResult(passed=not failures, failures=failures, warnings=warnings)