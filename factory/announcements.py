"""Announcement coverage — the round-5 escape class (PRE-7).

Round 5: a successful add updated the list visually but announced nothing to
screen readers. Errors were covered (`role="alert"`), successes were not.

The general rule: **every state mutation a sighted user can see must be
announced to an assistive-tech user.** Error-only live regions are the common
failure shape — the author remembers the sad path and forgets the happy one.

This is a static check over the component source: it finds mutation handlers
and verifies a live region exists AND that success paths feed it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# A live region: role=status / aria-live (polite or assertive).
_LIVE_REGION = re.compile(
    r'role\s*=\s*["\']status["\']|aria-live\s*=\s*["\'](?:polite|assertive)["\']')
# Includes the conditional JSX form role={cond ? "alert" : undefined}, which
# is how error-only announcement is usually written.
_ASSERTIVE_ONLY = re.compile(
    r'role\s*=\s*["\']alert["\']|aria-live\s*=\s*["\']assertive["\']|'
    r'role\s*=\s*\{[^}]*["\']alert["\'][^}]*\}')

# Handlers that mutate persisted state (the store seam calls).
_MUTATION = re.compile(
    r"\b(addTask|saveTasks|deleteTask|removeTask|toggleTask|updateTask|"
    r"setTasks|saveFilter|clearTasks)\s*\(")

# Evidence a success path announces: a setter feeding the live region.
_ANNOUNCE_SETTER = re.compile(
    r"\bset(Announcement|Status|Message|LiveMessage|Notice)\s*\(\s*[^)\s]")


@dataclass
class AnnouncementResult:
    passed: bool
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def named_failures(self) -> str:
        return "; ".join(self.failures) if self.failures else "none"


def check_file(path: Path) -> AnnouncementResult:
    """A component that mutates state must announce success, not just errors."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    failures: list[str] = []
    warnings: list[str] = []

    if not _MUTATION.search(text):
        return AnnouncementResult(True)  # no mutations, nothing to announce

    has_live = bool(_LIVE_REGION.search(text))
    has_assertive_only = bool(_ASSERTIVE_ONLY.search(text)) and not has_live

    if not has_live:
        if has_assertive_only:
            failures.append(
                f"{p.name}: mutates state and has an ASSERTIVE error region but "
                f"NO polite status/aria-live region — successful mutations are "
                f"silent to screen readers (error-only announcement)")
        else:
            failures.append(
                f"{p.name}: mutates state but declares NO live region "
                f"(role=status / aria-live) — changes are invisible to "
                f"assistive tech")
        return AnnouncementResult(False, failures, warnings)

    if not _ANNOUNCE_SETTER.search(text):
        failures.append(
            f"{p.name}: has a live region but nothing feeds it on success "
            f"(no announcement setter call) — an empty live region announces "
            f"nothing")

    return AnnouncementResult(passed=not failures, failures=failures,
                              warnings=warnings)


def check_tree(root: Path, glob: str = "src/**/*.tsx") -> AnnouncementResult:
    failures: list[str] = []
    warnings: list[str] = []
    for p in sorted(Path(root).glob(glob)):
        if ".test." in p.name:
            continue
        r = check_file(p)
        failures.extend(r.failures)
        warnings.extend(r.warnings)
    return AnnouncementResult(passed=not failures, failures=failures,
                              warnings=warnings)