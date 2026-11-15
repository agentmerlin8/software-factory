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

TOD-2 round 1 (cross-family reviewer): a component corrupt-data test led its
payload with `null`, which threw into loadTasks' outer catch and masked a
missing per-entry guard — the test passed on the mutant. The class recurred
because this module was NOT wired into the pre-review gate. `boundary_mutants`
below closes that gap: for each untrusted-boundary guard in the diff, generate
a deletion mutant and require the suite to kill it.
"""
from __future__ import annotations

import json
import re
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


def boundary_mutants(workdir: Path, base: str,
                     test_cmd: list[str] | None = None,
                     timeout_s: int = 300) -> MutationResult:
    """Deterministic self-certifying-test gate (TOD-2 round-1 class).

    DISCOVERY-DRIVEN, not instance-patched: find every loop that iterates a
    parsed collection (`for (const x of parsed)`) and every guard call inside
    it (`if (!isTask(x) || ...)`, `if (!validate(x)) continue`, ...). Delete
    each guard call in turn and require the story's CHANGED test files to go
    RED. A component corrupt-data test whose payload throws into an outer
    catch (leading `null`) passes on the mutant and certifies the defect —
    the full suite can stay green via store-level tests while the component
    test proves nothing. Scoping the run to the changed test files is what
    exposes that; a whole-suite run hides it.

    Fail-closed: a survivor blocks the gate. Refuse to report on a red
    baseline (every mutant would look killed).
    """
    workdir = Path(workdir)
    if test_cmd is None:
        test_cmd = ["npx", "vitest", "run"]
    code, out = _run(["git", "diff", "--name-only", base, "HEAD"], workdir)
    if code != 0:
        return MutationResult("inconclusive", False, False,
                              f"git diff failed: {out[-200:]}")
    changed = [ln.strip() for ln in out.splitlines() if ln.strip()]
    test_files = [f for f in changed if re.search(r"\.(test|spec)\.[jt]sx?$", f)]
    src_files = [f for f in changed
                 if re.search(r"\.[jt]sx?$", f) and f not in test_files]
    if not test_files:
        return MutationResult("verified", False, True,
                              "no changed test files; boundary-mutation gate skipped")

    sites = _discover_boundary_guards(workdir, src_files)
    if not sites:
        return MutationResult("verified", False, True,
                              "no per-entry boundary guard in diff; nothing to mutate")

    # Discover which INDIVIDUAL tests claim element-validation coverage
    # (seed parsed-but-malformed arrays). Per-FILE runs mask a weak test when
    # a sibling in the same file kills the mutant — TOD-2 M1 proved that.
    claims: list[tuple[str, str]] = []
    for tf in test_files:
        claims.extend(_boundary_claims(tf, (workdir / tf).read_text(encoding="utf-8")))
    if not claims:
        return MutationResult("verified", False, True,
                              "no changed test claims element-validation coverage; "
                              "nothing to verify")

    cmd = test_cmd + test_files
    base_code, _ = _run(cmd, workdir, timeout_s)
    if base_code != 0:
        return MutationResult("inconclusive", False, False,
                              "red baseline — refusing to report sweep results")

    survivors: list[str] = []
    killed = 0
    for p, original, start, end, label in sites:
        mutant = original[:start] + original[end:]
        try:
            p.write_text(mutant, encoding="utf-8")
            for tf, name in claims:
                f_code, f_out = _run(test_cmd + [tf, "-t", re.escape(name)],
                                     workdir, timeout_s)
                counts = _vitest_counts(f_out)
                if f_code in (124, 127) or counts is None or sum(counts) != 1:
                    return MutationResult(
                        "inconclusive", False, False,
                        f"could not isolate test '{name}' in {tf} "
                        f"(exit={f_code}, counts={counts})")
                passed, failed = counts
                if failed:
                    killed += 1
                else:
                    survivors.append(
                        f"{tf} :: '{name}' seeds malformed entries yet PASSES "
                        f"with guard '{label}' deleted (self-certifying)")
        finally:
            p.write_text(original, encoding="utf-8")
    if survivors:
        return MutationResult(
            "test-too-weak", False, True,
            "; ".join(survivors) + " — a changed test passes on the defective "
            "code (self-certifying-test class)")
    return MutationResult("verified", True, True,
                          f"{killed} boundary-guard mutant/test pair(s) killed")


_SEED = re.compile(
    r"localStorage\.setItem\(\s*[^,]+,\s*(['\"`])((?:\\.|(?!\1).)*)\1", re.S)
_STRINGIFY_ARRAY = re.compile(r"JSON\.stringify\(\s*\[", re.S)


def _stringify_arrays(text: str):
    """Yield the element-list source of each JSON.stringify([...]) call,
    scanning to the MATCHING close bracket (a non-greedy regex stops at the
    first nested object's `]`)."""
    for m in _STRINGIFY_ARRAY.finditer(text):
        depth = 1
        i = m.end()
        while i < len(text) and depth > 0:
            if text[i] == "[":
                depth += 1
            elif text[i] == "]":
                depth -= 1
            i += 1
        if depth == 0:
            yield text[m.end():i - 1]
_IT = re.compile(r"\bit\(\s*(['\"`])((?:\\.|(?!\1).)*)\1")


def _vitest_counts(out: str) -> tuple[int, int] | None:
    """(passed, failed) from vitest's summary line, or None if absent.

    Example: 'Tests  1 passed | 54 skipped (55)' / 'Tests  1 failed | 2 passed (3)'.
    Skipped tests are ignored; a run that selected zero tests returns None so
    the caller fails closed instead of reading a vacuous green.
    """
    m = re.search(r"Tests\s+(.+)", out)
    if not m:
        return None
    passed = failed = 0
    for n, kind in re.findall(r"(\d+)\s+(passed|failed)", m.group(1)):
        if kind == "passed":
            passed += int(n)
        else:
            failed += int(n)
    if passed + failed == 0:
        return None
    return passed, failed


def _boundary_claims(test_file: str, text: str) -> list[tuple[str, str]]:
    """(file, test-name) pairs whose bodies seed ELEMENT-malformed storage.

    Discovery-driven: parse it() blocks, inspect the actual setItem payloads.
    A claim requires data that PARSES as an array but holds entries a
    per-entry guard would reject (null / non-object / partial objects).
    Unparseable-JSON payloads claim the PARSE boundary, not the element
    guard — deleting the element guard legitimately leaves those green, so
    they are not claims here. Direct guard-call probes (isTask({...})) are
    excluded too: deleting the guard FUNCTION breaks them at import time,
    which is a compile kill, not behavioral evidence.
    """
    claims: list[tuple[str, str]] = []
    matches = list(_IT.finditer(text))
    for i, m in enumerate(matches):
        name = m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        if _body_claims_element_validation(body):
            claims.append((test_file, name))
    return claims


def _body_claims_element_validation(body: str) -> bool:
    for m in _SEED.finditer(body):
        payload = m.group(2).replace('\\"', '"').replace("\\'", "'")
        try:
            data = json.loads(payload)
        except (json.JSONDecodeError, ValueError):
            continue  # parse-boundary claim, not element claim
        if _malformed_array(data):
            return True
    for body_arr in _stringify_arrays(body):
        if _stringify_array_malformed(body_arr):
            return True
    return False


def _malformed_array(data) -> bool:
    """True if the array holds an UNMASKED malformed entry.

    The storage loop processes entries in order; a null entry throws on
    `.id` access and aborts to the outer catch, so every later entry is
    unreachable. A payload led by null is catch-path coverage, NOT an
    element-guard claim — its test legitimately passes with the guard
    deleted (TOD-2 M1's masked variant; the reviewer lens covers that one).
    """
    if not isinstance(data, list):
        return False
    keysets = set()
    for el in data:
        if el is None:
            return False  # throwing entry masks everything after it
        if not isinstance(el, dict):
            return True  # number/string/bool: .id is undefined, no throw
        if any(v is None for v in el.values()):
            return True  # null field value: guard rejects, no throw
        keysets.add(frozenset(el.keys()))
        if len(keysets) > 1:
            return True  # partial objects with inconsistent fields
    return False


def _stringify_array_malformed(body: str) -> bool:
    """Heuristic for JSON.stringify([...]) literals. Variable elements are
    unknown (assumed valid); a leading null literal masks the rest."""
    depth = 0
    elements: list[str] = []
    cur = ""
    for ch in body:
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        if ch == "," and depth == 0:
            elements.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        elements.append(cur.strip())
    keysets = set()
    for el in elements:
        if not el:
            continue
        if re.fullmatch(r"[A-Za-z_$][\w$]*", el):
            keysets.add(None)  # variable: key set unknown
            continue
        if el == "null":
            return False  # masked
        if not el.startswith("{"):
            return True  # numeric/string/bool/array literal
        if re.search(r":\s*null\b", el):
            return True
        keys = frozenset(re.findall(r"(\w+)\s*:", el))
        keysets.add(keys)
    # Unknown (None) alongside any known key set, or two different known
    # key sets, means partial/inconsistent entries.
    if len(keysets) > 1:
        return True
    return False


_LOOP = re.compile(r"for\s*\(\s*(?:const|let|var)\s+(\w+)\s+of\s+(\w+)\s*\)")
_NEG_GUARD = re.compile(r"!\s*([A-Za-z_$][\w$]*)\s*\(\s*(\w+)\s*\)")


def _discover_boundary_guards(workdir: Path, src_files: list[str]
                              ) -> list[tuple[Path, str, int, int, str]]:
    """(path, text, start, end, label) for each deletable guard call inside a
    loop over a collection. The guard must test the loop variable; the
    collection must look parsed/loaded (not a literal)."""
    sites: list[tuple[Path, str, int, int, str]] = []
    for rel in src_files:
        p = workdir / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        offsets = [0]
        for ln in lines:
            offsets.append(offsets[-1] + len(ln))
        for i, ln in enumerate(lines):
            loop = _LOOP.search(ln)
            if not loop:
                continue
            var = loop.group(1)
            # Scan the loop body (brace-balanced) for negated guard calls on
            # the loop variable.
            depth = 0
            started = False
            for j in range(i, len(lines)):
                depth += lines[j].count("{") - lines[j].count("}")
                if "{" in lines[j]:
                    started = True
                if started and depth <= 0:
                    body_end = j
                    break
            else:
                body_end = len(lines) - 1
            for j in range(i, body_end + 1):
                for m in _NEG_GUARD.finditer(lines[j]):
                    if m.group(2) != var:
                        continue
                    s = offsets[j] + m.start()
                    e = offsets[j] + m.end()
                    # Swallow a following `|| ` so the mutant stays parseable.
                    tail = re.match(r"\s*\|\|\s*", text[e:e + 8])
                    if tail:
                        e += tail.end()
                    sites.append((p, text, s, e, m.group(0).strip()))
    return sites


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