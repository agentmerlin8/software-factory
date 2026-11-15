"""Mutation verification — does a regression test actually catch the bug?

Round 9 (Copilot, on MY OWN test): "The concurrency regression test masks lost
updates by merging the other tab's task into the outgoing payload and bypassing
the original write, allowing an unsafe read/append/save implementation to pass."

It was right. The test passed against the buggy code. A green suite that cannot
fail is worse than no suite: it certifies a defect.

The rule this enforces: **a regression test is only evidence if it FAILS on the
pre-fix code (or a deliberate mutant of the fix).** Run it both ways. This is
the test-side analogue of "execute load-bearing claims" — and it applies to
tests an AGENT wrote, which is exactly where self-certification creeps in.

Usage:
    verify_regression(workdir, mutate, restore, test_cmd)
`mutate` reintroduces the defect; `restore` puts the fix back. The test command
must FAIL after mutate and PASS after restore. Anything else is a finding about
the TEST, not the product.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class MutationResult:
    verdict: str            # verified | test-too-weak | test-broken | inconclusive
    mutant_failed: bool
    fixed_passed: bool
    detail: str = ""
    failing_tests: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.verdict == "verified"


def _run(cmd: list[str], workdir: Path, timeout_s: int = 600) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=str(workdir), capture_output=True,
                           text=True, timeout=timeout_s)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except FileNotFoundError as exc:
        return 127, str(exc)


def _failed_names(out: str) -> list[str]:
    names = []
    for line in out.splitlines():
        t = line.strip()
        if t.startswith("×"):
            names.append(t.lstrip("× ").split("  ")[0][:120])
    return names


def verify_regression(workdir: Path, *, mutate: Callable[[], None],
                      restore: Callable[[], None],
                      test_cmd: list[str],
                      timeout_s: int = 600) -> MutationResult:
    """Prove a regression test can fail.

    Order matters: mutate FIRST (so a crash leaves the tree dirty and obvious),
    and ALWAYS restore in a finally block.
    """
    workdir = Path(workdir)
    mutant_code, mutant_out = 1, ""
    try:
        mutate()
        mutant_code, mutant_out = _run(test_cmd, workdir, timeout_s)
    finally:
        restore()
    fixed_code, fixed_out = _run(test_cmd, workdir, timeout_s)

    mutant_failed = mutant_code != 0
    fixed_passed = fixed_code == 0

    if mutant_failed and fixed_passed:
        return MutationResult(
            "verified", True, True,
            "test fails on the mutant and passes on the fix — it is evidence",
            _failed_names(mutant_out))
    if not mutant_failed and fixed_passed:
        return MutationResult(
            "test-too-weak", False, True,
            "test PASSES on the defective code — it cannot detect the bug it "
            "claims to cover (round-9 class: self-certifying test)")
    if mutant_failed and not fixed_passed:
        return MutationResult(
            "test-broken", True, False,
            "test fails on the FIX too — the test or the fix is wrong",
            _failed_names(fixed_out))
    return MutationResult(
        "inconclusive", False, False,
        f"test failed on both (mutant={mutant_code}, fixed={fixed_code}); "
        f"check the suite baseline first")