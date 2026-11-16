"""PR-size budget — keep review rounds under the owner's target (OC-17).

Randy (2026-11-15): "Copilot approval should be required the whole way through.
We are going to have to tune our PR sizes so we don't get in a loop on a large
PR that could go 20 rounds. The ideal stat is less than 5 review rounds."

Measured evidence from TOD-1 (the first factory story):
  934-line diff, 522 lines of it UNREQUESTED theme CSS.
  6 of 10 Copilot findings landed in that CSS; 4 in the component.
  7 review rounds and still not approved.

The driver is not "lines" alone — it is REVIEW SURFACE: how many distinct
things a reviewer must scrutinize. Unrequested visual work multiplies surface
without adding acceptance criteria, so it buys rounds without buying value.

This module budgets a change BEFORE dispatch, so an oversized story is split
at planning time rather than discovered in round 6.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# Owner target: converge in fewer than 5 review rounds.
TARGET_MAX_ROUNDS = 5

# Budgets calibrated on TOD-1 (934 lines / 522 CSS -> 7+ rounds).
MAX_TOTAL_LINES = 400
MAX_CSS_LINES = 120          # visual surface is the expensive kind
MAX_FILES = 6
MAX_UNREQUESTED_LINES = 60   # work with no AC behind it

_VISUAL = re.compile(r"\.(css|scss|sass|less|styl)$", re.I)
# Test files: JS/TS .test./.spec., __tests__/ or tests/ dirs, AND Python
# test_*.py / *_test.py unittest convention (DSH-1: test_server.py was
# miscounted as product, false-failing the size budget).
_TEST = re.compile(r"(\.test\.|\.spec\.|__tests__|(^|/)tests?/|(^|/)test_[^/]*\.py$|_test\.py$)", re.I)


@dataclass
class DiffStat:
    path: str
    added: int
    deleted: int

    @property
    def churn(self) -> int:
        return self.added + self.deleted

    @property
    def is_visual(self) -> bool:
        return bool(_VISUAL.search(self.path))

    @property
    def is_test(self) -> bool:
        return bool(_TEST.search(self.path))


@dataclass
class SizeBudget:
    passed: bool
    total: int = 0
    visual: int = 0
    product: int = 0
    tests: int = 0
    files: int = 0
    failures: list[str] = field(default_factory=list)
    advice: list[str] = field(default_factory=list)

    def named_failures(self) -> str:
        return "; ".join(self.failures) if self.failures else "none"


def diff_stats(workdir: Path, base: str = "origin/main",
               head: str = "HEAD") -> list[DiffStat]:
    """Per-file numstat for base...head."""
    p = subprocess.run(["git", "diff", "--numstat", base, head],
                       cwd=str(workdir), capture_output=True, text=True)
    if p.returncode != 0:
        return []
    out: list[DiffStat] = []
    for line in p.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        a, d, path = parts
        # binary files report '-'
        out.append(DiffStat(path, int(a) if a.isdigit() else 0,
                            int(d) if d.isdigit() else 0))
    return out


def check(stats: list[DiffStat], *,
          max_total: int = MAX_TOTAL_LINES,
          max_visual: int = MAX_CSS_LINES,
          max_files: int = MAX_FILES) -> SizeBudget:
    """Budget a change against the <5-round target.

    The line budget applies to PRODUCT + VISUAL churn; test churn is
    counted and reported separately (owner policy, agentic-software-factory
    skill: "Count test churn separately from product churn; a well-tested
    slice is not an oversized one"). TOD-3 round 1 exposed the drift: a
    467-line diff of which 357 were regression tests was being blocked.
    """
    total = sum(s.churn for s in stats)
    visual = sum(s.churn for s in stats if s.is_visual)
    tests = sum(s.churn for s in stats if s.is_test)
    product = total - visual - tests
    review_surface = product + visual
    failures: list[str] = []
    advice: list[str] = []

    if review_surface > max_total:
        failures.append(
            f"{review_surface} product+visual changed lines exceeds the "
            f"{max_total}-line review budget (tests: {tests}, counted separately)")
        advice.append("split the story: one vertical slice per PR")
    if visual > max_visual:
        failures.append(
            f"{visual} lines of visual/CSS churn exceeds the {max_visual}-line "
            f"budget — visual surface is the highest-cost review surface")
        advice.append(
            "move theming/styling to its own story with its own ACs, or cut it")
    if len(stats) > max_files:
        failures.append(
            f"{len(stats)} files exceeds the {max_files}-file budget")
        advice.append("narrow the manifest; unrelated files belong in another slice")

    return SizeBudget(passed=not failures, total=total, visual=visual,
                      product=product, tests=tests, files=len(stats),
                      failures=failures, advice=advice)


def check_repo(workdir: Path, base: str = "origin/main", *,
               head: str = "HEAD", **kw) -> SizeBudget:
    return check(diff_stats(Path(workdir), base, head), **kw)