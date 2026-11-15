"""Guard mutation sweep — find vacuous tests mechanically (round-10 class).

Round 10 (Copilot): "the non-finite timestamp test does not exercise the
finite-number validation guard." True — `createdAt: null` fails the typeof
check first, so `Number.isFinite` was never reached; deleting it left 41/41
green.

The lesson generalizes: a validation guard with no test that reaches it is
DEAD WEIGHT that reads like protection. Review finds these one at a time; a
sweep finds them all at once. This module deletes each guard in turn and
reports which deletions the suite fails to notice.

Round-10 sweep on the real store found a SECOND vacuous guard the reviewer had
not reported (`id.length > 0`) — which is the argument for sweeping rather
than patching the cited instance.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Guard:
    """One deletable boolean clause in a validation expression."""
    line_no: int
    text: str
    source_line: str


@dataclass
class SweepResult:
    survivors: list[Guard] = field(default_factory=list)   # deletion NOT caught
    killed: list[Guard] = field(default_factory=list)      # deletion caught
    inconclusive: list[Guard] = field(default_factory=list)

    # A survivor is NOT automatically a test gap. Two very different causes:
    #   (a) VACUOUS COVERAGE — no test reaches the guard (round-10: the
    #       finite-number guard; also id.length). Add a test.
    #   (b) REDUNDANT GUARD — another clause already rejects the same inputs
    #       (e.g. `typeof x === "number"` when Number.isFinite(x) follows, or
    #       `typeof id === "string"` when id.length > 0 follows). Behaviour is
    #       unchanged, so no test CAN kill it. The honest disposition is
    #       "redundant, kept for clarity" or "remove the clause" — NOT
    #       "write a test", which would be unkillable by construction.
    # Triage each survivor by probing the mutant's behaviour before acting.
    redundant: list[Guard] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.survivors

    def summary(self) -> str:
        total = (len(self.survivors) + len(self.killed)
                 + len(self.inconclusive) + len(self.redundant))
        return (f"{total} guards swept: {len(self.killed)} killed, "
                f"{len(self.survivors)} SURVIVED (triage: vacuous vs redundant), "
                f"{len(self.redundant)} redundant, "
                f"{len(self.inconclusive)} inconclusive")


# A boolean clause ending in && (JS/TS) or `and` (Python) inside a multi-line
# validation expression. Comments are excluded in both languages.
_CLAUSE = re.compile(r"^\s*(?!\s*(?://|\*|#))(.+?)\s*(?:&&|and)\s*$")


def find_guards(path: Path, *, within: str | None = None) -> list[Guard]:
    """Collect deletable `expr &&` clauses, optionally inside one function."""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    start, end = 0, len(lines)
    if within:
        for i, ln in enumerate(lines):
            if within in ln:
                start = i
                if "{" in ln or any("{" in x for x in lines[i:i + 3]):
                    # Brace-delimited (JS/TS/C-like): walk to the matching close.
                    depth = 0
                    for j in range(i, len(lines)):
                        depth += lines[j].count("{") - lines[j].count("}")
                        if depth == 0 and j > i:
                            end = j + 1
                            break
                else:
                    # Indentation-delimited (Python): the body ends at the first
                    # non-blank line at or below the def's own indentation.
                    base = len(ln) - len(ln.lstrip())
                    end = len(lines)
                    for j in range(i + 1, len(lines)):
                        cur = lines[j]
                        if not cur.strip():
                            continue
                        if len(cur) - len(cur.lstrip()) <= base:
                            end = j
                            break
                break
    out: list[Guard] = []
    for i in range(start, end):
        m = _CLAUSE.match(lines[i])
        if m and not lines[i].strip().startswith(("//", "*")):
            out.append(Guard(i + 1, m.group(1).strip(), lines[i]))
    return out


def _run(cmd: list[str], workdir: Path, timeout_s: int) -> int:
    try:
        p = subprocess.run(cmd, cwd=str(workdir), capture_output=True,
                           text=True, timeout=timeout_s)
        return p.returncode
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 124


def sweep(path: Path, *, workdir: Path, test_cmd: list[str],
          within: str | None = None, timeout_s: int = 600,
          baseline_required: bool = True) -> SweepResult:
    """Delete each guard in turn; report deletions the suite does not catch.

    The original file is ALWAYS restored, including on error.
    """
    path = Path(path)
    original = path.read_text(encoding="utf-8")
    result = SweepResult()

    if baseline_required and _run(test_cmd, Path(workdir), timeout_s) != 0:
        # A red baseline makes every mutant look "killed" — refuse to report.
        result.inconclusive.extend(find_guards(path, within=within))
        return result

    guards = find_guards(path, within=within)
    try:
        for g in guards:
            lines = original.splitlines()
            del lines[g.line_no - 1]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            code = _run(test_cmd, Path(workdir), timeout_s)
            if code == 0:
                result.survivors.append(g)
            elif code in (124, 127):
                result.inconclusive.append(g)
            else:
                result.killed.append(g)
    finally:
        path.write_text(original, encoding="utf-8")
    return result