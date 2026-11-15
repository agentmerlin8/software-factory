# HANDOFF — SKEL-1 + SKEL-2 DONE (next is SKEL-3)

**Updated:** 2026-11-15 · supersedes the work-item table in `HANDOFF.md` §5.
**Read `HANDOFF.md` first** for cold-start, decisions, board IDs, conventions.

## Where the experiment stands

- **SKEL-1 (issue #3) DONE — OC-16 GO.** Factory 0 escaped defects vs
  control 6 (incl. data-loss BLOCKER) at ~3.8× tokens; cost accepted.
- **SKEL-2 (issue #4) DONE — hypothesis 2 HOLDS (caveat).** Intake CLI +
  intake-agent role + Storybook wireframes built. Independent engineer
  persona: round 1 REQUEST-CHANGES (2 blockers: no ACs, no persistence) →
  made acceptance/persistence/data_model REQUIRED categories → round 2
  APPROVE, all 7 concerns resolved. 2 rounds, 226s review time.
  **Caveat:** agent persona, not a human engineer — measures artifact
  clarity, not human acceptance; a real non-owner test is the follow-up.
  Evidence: `docs/experiments/skel-2-intake-2026-11-15.md`, `runs/skel-2/`.

**NEXT WORK: SKEL-3 (issue #5) — controller-writer security (OC-14).**
Agents never hold a state-repo write token; a separate controller job (no
model output, no product code) validates + appends; two identities (agent
App / controller App); single controller writer serialized by one
concurrency group. Works on Free plan. Read issue #5 + OC-14 before scoping.

- Product repo: `agentmerlin8/factory-todo-demo` (public), main `0759dae`.
- Control repo: `agentmerlin8/factory-todo-control` (public), main `f7ac685`.
- Intake artifacts: `factory/intake.py`, `process/intake-agent.md`,
  `templates/wireframes/`, `runs/skel-2/`.
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

## Next action: SKEL-3 (controller-writer security)

SKEL-1 (GO) and SKEL-2 (intake, hypothesis 2 holds) are closed. Do not
re-open them or re-run their arms without an explicit owner request. The
next skeleton item is **SKEL-3 (issue #5): controller-writer security
(OC-14)** — agents never hold a state-repo write token; a separate
controller job (no model output, no product code) validates + appends; two
identities (agent App / controller App); single controller writer
serialized by one concurrency group (fixes ledger contention, MRG-1).
Works on the Free plan. Read issue #5 + OC-14 + the github-apps skill
before scoping. Same discipline: fresh run chat, repo is the state, slice
law (OC-17 sizing), Copilot approval + human merge.

**SKEL-2 follow-up (when a human is available):** a real non-owner engineer
test of the intake PRD — the agent-persona approval is the weaker evidence
(Randy's decision); the human test is the stronger signal.

**Tuning backlog Randy named (shrink the ~3.8× multiple):** agent tuning +
forthcoming token optimizations. The overhead ratio (0.94) and the 11-round
TOD-1 calibration are the baseline to improve against. The findings log's
uncovered-class list and the recurring "remediation introduced its own
defect" pattern (3×) are the concrete prevention targets.

## Board

Issues #3 (SKEL-1) and #4 (SKEL-2) Done (Status=Done, Stage=Done).
Issues #8/#9 (EXP-1/2) Done. Issues #5/#6/#7 (SKEL-3/4/5) Backlog.
Board IDs and the `printf -v` GraphQL pattern are in `HANDOFF.md` §6.