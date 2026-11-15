# HANDOFF — SKEL-1 COMPLETE (both arms run; OC-16 go/no-go awaits owner)

**Updated:** 2026-11-15 · supersedes the work-item table in `HANDOFF.md` §5.
**Read `HANDOFF.md` first** for cold-start, decisions, board IDs, conventions.

## Where the experiment stands

SKEL-1 (issue #3) = 5 to-do stories through the factory + a control arm.
**BOTH ARMS ARE COMPLETE.** All 5 factory stories merged with Copilot
approval (TOD-5 squash `0759dae`). The control arm (one session, same
model/design/scaffold) built all 5 stories to green tests, then a post-hoc
cross-family review found **6 escaped defects including a data-loss BLOCKER**.
The OC-16 comparison is written: `runs/COMPARISON.md`.

**THE OPEN DECISION IS THE OWNER'S:** the factory wins decisively on escaped
defects (0 vs 6) at a **~3.8× token / ~4.7× wall-time** multiple. human_min
was NOT instrumented for either arm. Recommendation in COMPARISON.md is GO
conditional on Randy accepting the cost multiple. Do not re-litigate the
measured numbers; the call is the cost trade-off.

- Product repo: `agentmerlin8/factory-todo-demo` (public), main `0759dae`.
  Local clone: `~/.hermes/cache/scratch/factory-exp/todo-demo`.
- Control repo: `agentmerlin8/factory-todo-control` (public), main `f7ac685`.
  Local clone: `~/.hermes/cache/scratch/factory-exp/todo-control`.
- Run state: `runs/todo-demo/` + `runs/todo-control/` (ledgers, evidence, dispatch).
- Comparison: `runs/COMPARISON.md`. Findings log: `state/findings.jsonl`.

## Story outcomes (factory arm)

| Story | Rounds | Merged | Notes |
|---|---|---|---|
| TOD-1 add | 11 | `d4297a3` | calibration case: 522 unrequested CSS lines drove 6/10 findings |
| TOD-2 list | 2 | `1a29e3c` | OC-17 sizing held (166 lines, 0 CSS); cross-family EXECUTED claim refuted by execution |
| TOD-3 toggle | 4 | `503e8c0` | storage-failure class dominated (6/10 findings); committed-snapshot contract born here |
| TOD-4 delete | 4 | `7df778a` | 2/7 findings were defects in the prior round's own remediation |
| TOD-5 filter | 3 | `0759dae` | round-2 finding was a defect introduced by the round-1 fix (pattern 3x); harness fixed: contrast wash compositing + rule-level dark overrides + by-reference dispatch (128KiB argv cap) |

## Control arm outcome

One `hermes -z` session, 2.63M tokens, 1,115s, 77 tests green, build green.
Post-hoc review verdict **FAIL**: stale-snapshot overwrite in all 3 mutations
(concurrent cross-tab write clobbered — probe-verified 3/3 red), a
self-certifying concurrency test, empty-title validation gap, misleading
alert copy, dead code, latent state race. The BLOCKER is the exact defect
the factory caught and fixed in TOD-3's loop. Gate on the control tree: 8/9
(pr_size REAL over-budget: 503 product+visual lines, 153 CSS).

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

## Next action: OWNER DECISION on OC-16, then close out SKEL-1

Both arms are run and the comparison is written (`runs/COMPARISON.md`).
The remaining step is Randy's go/no-go on the kill criterion:

- Factory wins on **escaped defects: 0 vs 6** (control shipped a data-loss
  BLOCKER + self-certifying test to green tests).
- Cost: **~3.8× tokens, ~4.7× dispatch wall-time.** Acceptable? Owner's call.
- **human_min was not instrumented** for either arm — the other kill axis is
  unmeasured. If Randy wants a human-minutes comparison, that requires a
  re-run with attention tracking; do not fabricate it.

On GO: record the decision (DEC-### in docs/open-calls.md or a decision
event), mark issue #3 Done, move the board Stage to Done, and proceed to the
next skeleton item (SKEL-2 intake spike is the highest product risk). On
NO-GO: STOP per OC-16 and reconsider the factory design — the comparison
file is the evidence base.

**Do not re-run the arms or re-litigate the measured numbers without an
explicit owner request.** The experiment is complete; the decision is open.

## Board

Issue #3 In Progress / Coding. Issues #8/#9 (EXP-1/2) Done.
Board IDs and the `printf -v` GraphQL pattern are in `HANDOFF.md` §6.