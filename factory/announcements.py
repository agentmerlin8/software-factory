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

# A flag that drives a CONDITIONAL assertive alert, e.g.
#   role={rejected || storageFailed ? "alert" : undefined}
# Any such flag left true after a successful mutation shows a stale error
# (TOD-2/3/4 recurring class: the shared alert prioritizes the flag).
_ALERT_FLAG_ROLE = re.compile(
    r'role\s*=\s*\{\s*([^}]*?)\s*\?\s*["\']alert["\']')

_HANDLER = re.compile(r"function\s+(handle\w+)\s*\([^)]*\)\s*\{")


def _handler_bodies(text: str) -> list[tuple[str, str]]:
    """(name, body) for each top-level handle* function, brace-balanced."""
    out = []
    for m in _HANDLER.finditer(text):
        depth = 0
        i = m.end() - 1  # at the opening brace
        start = i
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    out.append((m.group(1), text[start:i + 1]))
                    break
            i += 1
    return out


def _success_region(body: str) -> str:
    """The handler body up to its failure branch (`} catch {`), or all of it.
    Mutation handlers without try/catch are entirely success path."""
    idx = body.find("} catch")
    return body[:idx] if idx != -1 else body


def check_stale_alert_flags(text: str, name: str) -> list[str]:
    """Every flag gating a conditional assertive alert must be cleared on
    every mutation handler's success path — else a successful mutation
    leaves a stale error visible (and assertively announced)."""
    flags: set[str] = set()
    for m in _ALERT_FLAG_ROLE.finditer(text):
        flags.update(re.findall(r"[A-Za-z_$][\w$]*", m.group(1)))
    if not flags:
        return []
    failures = []
    for hname, body in _handler_bodies(text):
        if not _MUTATION.search(body):
            continue
        success = _success_region(body)
        for flag in sorted(flags):
            clear = re.compile(
                r"\bset" + flag[0].upper() + re.escape(flag[1:]) + r"\s*\(\s*false\s*\)")
            if not clear.search(success):
                failures.append(
                    f"{name}: {hname} mutates state but its success path never "
                    f"clears '{flag}' — a stale assertive alert can survive a "
                    f"successful mutation (stale-alert-flag class)")
    return failures


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

    # TOD-4 round-1 class (recurred across TOD-2/3/4): a flag gating the
    # shared assertive alert must be cleared on every mutation success path.
    failures.extend(check_stale_alert_flags(text, p.name))

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