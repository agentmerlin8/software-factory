# HANDOFF — SKEL-1 in flight (TOD-1/2/3/4 merged, TOD-5 awaiting human merge)

**Updated:** 2026-11-15 · supersedes the work-item table in `HANDOFF.md` §5.
**Read `HANDOFF.md` first** for cold-start, decisions, board IDs, conventions.

## Where the experiment stands

SKEL-1 (issue #3) = 5 to-do stories through the factory + a control arm.
**Stories 1–4 of 5 are MERGED. Story 5 (the LAST) is CONVERGED — Copilot
APPROVED at `11861ea`, PR #5, CI green, 0 unresolved threads, CLEAN.
Waiting on Randy's merge (mode 1).** After that merge: the control arm
and the kill-criterion comparison — the experiment's finish line.

- Product repo: `agentmerlin8/factory-todo-demo` (public), main `7df778a`.
  Local clone: `~/.hermes/cache/scratch/factory-exp/todo-demo`.
- Run state: `runs/todo-demo/` (ledger.jsonl, design.md, stories/, dispatch/, evidence/).
- Findings log: `state/findings.jsonl` + generated `state/FINDINGS.md`.
- Control repo (not created yet): `agentmerlin8/factory-todo-control`.

## Story outcomes so far

| Story | Rounds | Merged | Notes |
|---|---|---|---|
| TOD-1 add | 11 | `d4297a3` | calibration case: 522 unrequested CSS lines drove 6/10 findings |
| TOD-2 list | 2 | `1a29e3c` | OC-17 sizing held (166 lines, 0 CSS); cross-family EXECUTED claim refuted by execution |
| TOD-3 toggle | 4 | `503e8c0` | storage-failure class dominated (6/10 findings); committed-snapshot contract born here |
| TOD-4 delete | 4 | `7df778a` | 2/7 findings were defects in the prior round's own remediation |
| TOD-5 filter | 3 | pending | round-2 finding was a defect introduced by the round-1 fix (pattern now 3x); harness fixed: contrast wash compositing + by-reference dispatch (128KiB argv cap) |

## TOD-1 outcome

Merged with **Copilot APPROVED** at `a0991868b` → squash `d4297a3`.
Squash tree == approved head (verified empty diff). 44 tests.

**11 review rounds — over the OC-17 target of <5.** Root cause, measured:
1031-line diff of which **522 lines were unrequested theme CSS**, and **6 of 10**
Copilot findings landed in that CSS. TOD-1 is the calibration case, not the
baseline to repeat.

## What the loop built (all in `factory/`, 136 tests green)

Every gate below was proven **fail-before / pass-after** on real heads:

| module | catches |
|---|---|
| `a11y.py` + `css_audit.py` | WCAG contrast, **discovery-driven**: every text pair, gradient×state, ::selection, focus indicator, both themes, rgba composited |
| `boundaries.py` | container-only parse casts (`Array.isArray(x) ? x as T[]`) |
| `announcements.py` | mutations with no live region / error-only / empty region |
| `mutation.py` | regression tests that PASS on the defective code |
| `guard_sweep.py` | validation guards no test reaches (triage vacuous vs redundant) |
| `pr_size.py` | OC-17 budget: ≤400 lines, ≤120 visual/CSS, ≤6 files |
| `spec.py` | stories touching I/O with no failure-mode AC (blocks dispatch) |
| `escalation.py` | adjudicates "human needed" claims by evidence, not adjectives |
| `findings.py` | mineable findings log: recurrence, escape rate, rounds/PR, precision |

CLI: `python -m factory doctor|status|gate|dispatch|findings|log-finding|metrics`
Use `.venv/bin/python` (pytest lives there).

## Hard-won lessons (do not relearn these)

1. **Execute every claim, in both directions.** Copilot's defect findings were
   right 10/10, but its *labels* were not: it called a mechanical race
   "human assessment needed", and rounds 8–10 found defects in **my own
   verification** (a fake fix, a circular test, a vacuous test).
2. **A green test that cannot fail certifies the bug.** Mutation-verify every
   regression test: it must FAIL on the defect. Two of my probes were circular.
3. **A surviving mutant is not always a test gap.** Triage: vacuous coverage
   (add a test) vs redundant guard (no test CAN kill it — document, don't fake).
4. **Fresh context ≠ blind to the code.** Reviewers need full files + run tools;
   diff-only + no tools produced 2 false findings AND 4 misses.
5. **Don't enumerate edge cases in a reviewer prompt** — it anchors the
   adversary to that list. Give lenses.
6. **Unrequested visual work is the expensive kind.** It adds review surface
   with zero ACs. Cut it or give it its own story.
7. **Copilot approvals are a SETTING** (repo → Settings → Copilot → Code review
   → Auto-approval), UI-only, off by default, dismissed on new commits. Enabled
   on both repos. `requestReviewsByLogin` GraphQL is the re-request that registers.

## Next action: merge TOD-5, then the CONTROL ARM

**TOD-5 outcome (2026-11-15):** PR #5 converged in **3 rounds** (target <5).
Round 1 (pre-PR, cross-family): announcements spoke full counts under a
filter; filtered-empty conflated with truly-empty; pressed-state wash
contrast backdrop-dependent. All fixed @5e691ba. Round 2 (Copilot): the
round-1 filtered-count fix INTRODUCED a stale-live-region defect — under
Completed, same-title adds never re-announced (visible count can't change).
Fixed @11861ea with a monotonic addition sequence. **Third time a remediation
round shipped its own defect — the control arm should be measured against
this reality, not an idealized factory.**
Harness fixes this story (both committed with tests): contrast audit
composites translucent washes (was false-failing 0.00:1); adapter passes
>100KB packages by reference (Linux MAX_ARG_STRLEN = 128KiB per argument).
**Randy merges PR #5 (squash). Then verify squash tree == approved head,
record human_merged + story_done + run-level milestone.**

Then the CONTROL ARM (OC-16): same 5 stories, ONE `hermes -z` session,
same model (qwen4-max-preview) + same design doc, in a fresh repo
`agentmerlin8/factory-todo-control` from the same scaffold. Measure
human-minutes, escaped defects, tokens/cost per story. Then
`factory metrics --control-ledger …` → COMPARISON.md → go/no-go against
the kill criterion: factory must win on human-minutes OR defects at an
acceptable cost multiple, else STOP and reconsider.

## Board

Issue #3 In Progress / Coding. Issues #8/#9 (EXP-1/2) Done.
Board IDs and the `printf -v` GraphQL pattern are in `HANDOFF.md` §6.