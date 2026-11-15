# HANDOFF — SKEL-1 in flight (TOD-1 merged, TOD-2 awaiting human merge)

**Updated:** 2026-11-15 · supersedes the work-item table in `HANDOFF.md` §5.
**Read `HANDOFF.md` first** for cold-start, decisions, board IDs, conventions.

## Where the experiment stands

SKEL-1 (issue #3) = 5 to-do stories through the factory + a control arm.
**Story 1 of 5 is DONE. Story 2 is CONVERGED — Copilot APPROVED at `488c661`,
PR #2, CI green, 0 unresolved threads, mergeStateStatus CLEAN. Waiting on
Randy's merge (mode 1).** Stories 3–5, the control arm, and the kill-criterion
comparison remain.

- Product repo: `agentmerlin8/factory-todo-demo` (public), main `d4297a3`.
  Local clone: `~/.hermes/cache/scratch/factory-exp/todo-demo`.
- Run state: `runs/todo-demo/` (ledger.jsonl, design.md, stories/, dispatch/, evidence/).
- Findings log: `state/findings.jsonl` + generated `state/FINDINGS.md`.
- Control repo (not created yet): `agentmerlin8/factory-todo-control`.

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

## Next action: merge TOD-2, then TOD-3

**TOD-2 outcome (2026-11-15):** PR #2 converged in **2 rounds** (target <5).
166 lines / 4 files / **0 CSS** — OC-17 sizing held. Round 1 (pre-PR,
cross-family): PASS-WITH-NITS; M1 self-certifying test fixed + mutation-proven;
N3 deferred to TOD-5. Round 2 (Copilot): real test-gap — deleting the post-add
sort left 55/55 green; fixed @488c661, mutation-proven. **The cross-family
reviewer's "EXECUTED" claim on that mutation was REFUTED by execution —
correction logged; trust findings, verify execution labels.** Gate extended:
`boundary_mutants` (per-test isolation; masked null-led payloads are
reviewer-lens territory — evidence/TOD-2-gate-extension-proof.py).
**Randy merges PR #2 (squash). Then verify squash tree == approved head,
record human_merged + story_done, and dispatch TOD-3.**

Then TOD-3 (complete), TOD-4 (delete), TOD-5 (filter), then the control arm
(same 5 stories, ONE `hermes -z` session, same model + design doc), then
`factory metrics` → COMPARISON.md → go/no-go against OC-16.

## Board

Issue #3 In Progress / Coding. Issues #8/#9 (EXP-1/2) Done.
Board IDs and the `printf -v` GraphQL pattern are in `HANDOFF.md` §6.