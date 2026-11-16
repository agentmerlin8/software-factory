"""Deterministic pre-review gates (Fable adoption #2: run BEFORE the LLM).

Checks, each named on failure:
  build    — `npm run build` exits 0
  tests    — the story's named tests pass (`npx vitest run <filter>`)
  manifest — the diff touches only declared files
  secrets  — no credential patterns in the diff

No model output is trusted here; these are mechanical checks on the real
product tree at the reviewed head.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

SECRET_PATTERNS = [
    r"ghp_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"gho_[A-Za-z0-9]{20,}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"xox[baprs]-[A-Za-z0-9-]{10,}",
    r"AKIA[0-9A-Z]{16}",
    r"sk-[A-Za-z0-9]{20,}",
]
_SECRET_RE = re.compile("|".join(SECRET_PATTERNS))


@dataclass
class GateResult:
    passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)

    def named_failures(self) -> str:
        return ", ".join(self.failures) if self.failures else "none"


def _run(cmd: list[str], cwd: Path, timeout_s: int = 300) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True,
                           text=True, timeout=timeout_s)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout_s}s"
    except FileNotFoundError as exc:
        return 127, str(exc)


def check_build(workdir: Path) -> tuple[bool, str]:
    code, out = _run(["npm", "run", "build"], workdir)
    return code == 0, out[-2000:]


def check_tests(workdir: Path, test_filter: str | None = None) -> tuple[bool, str]:
    cmd = ["npx", "vitest", "run"]
    if test_filter:
        cmd.append(test_filter)
    code, out = _run(cmd, workdir, timeout_s=600)
    return code == 0, out[-2000:]


def check_manifest(workdir: Path, base: str, manifest: list[str]) -> tuple[bool, str]:
    code, out = _run(["git", "diff", "--name-only", base, "HEAD"], workdir)
    if code != 0:
        return False, f"git diff failed: {out[-500:]}"
    changed = {ln.strip() for ln in out.splitlines() if ln.strip()}
    allowed = set(manifest)
    # A story may also touch its own test files; manifest should list them.
    unexpected = changed - allowed
    if unexpected:
        return False, f"files outside manifest: {sorted(unexpected)}"
    return True, f"{len(changed)} file(s) changed, all in manifest"


def check_secrets(workdir: Path, base: str) -> tuple[bool, str]:
    code, out = _run(["git", "diff", base, "HEAD"], workdir)
    if code != 0:
        return False, f"git diff failed: {out[-500:]}"
    hits = _SECRET_RE.findall(out)
    if hits:
        return False, f"secret-like patterns in diff: {len(hits)} hit(s)"
    return True, "no secret patterns"


def check_contrast(workdir: Path, css_rel: str = "src/index.css",
                   checks: list | None = None) -> tuple[bool, str]:
    """Deterministic WCAG gate — DISCOVERY-DRIVEN (rounds 2-4 lesson).

    Earlier versions enumerated selectors, so each review round surfaced one
    more nobody had listed (::selection, then focus outlines). Now the audit
    set is derived from the stylesheet itself: every text pair, gradient
    control, selection pair, and focus indicator, in both themes, with
    translucent colors alpha-composited over their real backdrop.
    """
    from .css_audit import audit_stylesheet, discover

    css_path = Path(workdir) / css_rel
    if not css_path.exists():
        return True, f"no {css_rel}; contrast gate skipped"
    css_text = css_path.read_text(encoding="utf-8")
    findings = audit_stylesheet(css_text)
    if findings:
        return False, "; ".join(str(f) for f in findings)
    d = discover(css_text)
    return True, (f"{d.total()} discovered pairings "
                  f"({len(d.flat)} text, {len(d.gradients)} gradient, "
                  f"{len(d.selections)} selection, {len(d.focus)} focus) "
                  f"x 2 themes pass WCAG AA")


def pre_review(workdir: Path, *, base: str, manifest: list[str],
               test_filter: str | None = None,
               skip_build: bool = False) -> GateResult:
    """Run all gates; return a named result. Fail-closed: any failure blocks."""
    workdir = Path(workdir)
    checks: dict[str, bool] = {}
    failures: list[str] = []

    if not skip_build:
        ok, detail = check_build(workdir)
        checks["build"] = ok
        if not ok:
            failures.append(f"build: {detail[-300:]}")

    ok, detail = check_tests(workdir, test_filter)
    checks["tests"] = ok
    if not ok:
        failures.append(f"tests: {detail[-300:]}")

    ok, detail = check_manifest(workdir, base, manifest)
    checks["manifest"] = ok
    if not ok:
        failures.append(f"manifest: {detail}")

    ok, detail = check_secrets(workdir, base)
    checks["secrets"] = ok
    if not ok:
        failures.append(f"secrets: {detail}")

    # OC-17: review surface is budgeted so a PR converges in <5 rounds.
    from .pr_size import check_repo as check_size
    sres = check_size(Path(workdir), base)
    checks["pr_size"] = sres.passed
    if not sres.passed:
        failures.append(f"pr_size: {sres.named_failures()}")

    # Round-5 class: successful mutations must be announced, not just errors.
    from .announcements import check_tree as check_announcements
    ares = check_announcements(Path(workdir))
    checks["announcements"] = ares.passed
    if not ares.passed:
        failures.append(f"announcements: {ares.named_failures()}")

    # Round-3 class: untrusted parse boundaries must validate ELEMENTS.
    from .boundaries import check_tree
    bres = check_tree(Path(workdir))
    checks["boundaries"] = bres.passed
    if not bres.passed:
        failures.append(f"boundaries: {bres.named_failures()}")

    # TOD-2 round-1 class: a changed test must FAIL when a boundary guard is
    # deleted (self-certifying tests pass on the defect). Discovery-driven.
    from .mutation import boundary_mutants
    mres = boundary_mutants(Path(workdir), base)
    checks["boundary_mutants"] = mres.ok
    if not mres.ok:
        failures.append(f"boundary_mutants: {mres.verdict}: {mres.detail}")

    # SEC-GATE: computable security/protocol classes (DSH-1 rounds 1-6).
    # Risk-tiered: network checks activate only on network-surface code.
    from .security import security_gate
    sec_failures = []
    sec_network = False
    for m in manifest:
        p = Path(workdir) / m
        if p.suffix in (".py", ".ts", ".js", ".tsx") and p.exists():
            sr = security_gate(p.read_text(encoding="utf-8"))
            sec_network = sec_network or sr.network_surface
            sec_failures.extend(f"{m}: {f}" for f in sr.failures)
    checks["security"] = not sec_failures
    if sec_failures:
        failures.append(f"security: {'; '.join(sec_failures)}")

    if any(m.endswith(".css") for m in manifest):
        ok, detail = check_contrast(workdir)
        checks["contrast"] = ok
        if not ok:
            failures.append(f"contrast: {detail}")

    return GateResult(passed=all(checks.values()), checks=checks,
                      failures=failures)