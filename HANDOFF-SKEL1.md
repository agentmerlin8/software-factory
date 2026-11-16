# HANDOFF — v1 WALKING SKELETON COMPLETE (all 5 SKEL items done)

**Updated:** 2026-11-15 · supersedes the work-item table in `HANDOFF.md` §5.
**Read `HANDOFF.md` first** for cold-start, decisions, board IDs, conventions.

## v1 is COMPLETE — all three hypotheses proven end-to-end

- **SKEL-1 (#3) DONE — OC-16 GO.** Factory 0 escaped defects vs control 6
  (incl. data-loss BLOCKER) at ~3.8× tokens; cost accepted for stability +
  visibility. Evidence: runs/COMPARISON.md.
- **SKEL-2 (#4) DONE — hypothesis 2 HOLDS (caveat).** Intake CLI + agent
  role + Storybook wireframes; engineer persona APPROVE round 2 (226s).
  Caveat: agent not human; real engineer test is the follow-up.
- **SKEL-3 (#5) DONE — OC-14 security live + proven twice.** controller.py
  validator + serialized writer workflow + 2 least-priv Apps (agent 5777949
  todo-demo-only; controller 5777982 software-factory-only). Agent can't
  write state (403). Proof: scripts/proof-identity.py.
- **SKEL-4 (#6) DONE — OC-15 merge protocol verified on real PR #6.** Stale
  refused, squash tree == reviewed head server-side, CRLF+rename preserved.
  factory/merge_protocol.py.
- **SKEL-5 (#7) DONE — OC-16 measurement + calibration.** dispatch_audit
  (11/11 metered), cycle_time_split, risk.py tiering, budget.py controller
  enforcement, calibration.py + 10-defect fixture + 3-mode experiment
  (all modes 10/10 salient; cross-family edge is on subtle defects per real
  SKEL-1 evidence). 223 tests green.

**NEXT: the north-star vision (post-v1, evidence-gated), OWNER-DIRECTED.**
Do not start north-star work without an explicit owner decision on what to
build next. The v1 thesis is proven; the full vision (docs/vision.md §5+)
returns only when v1 evidence justifies it. Candidate next steps the owner
may choose: a real (non-demo) product through the factory; the dedicated
state-repo split (OC-8); cloud adapter (OC-2); merge modes 2/3 + autonomy
promotion (OC-4/OC-9, data-gated); the SKEL-2 human-engineer follow-up.

**Open follow-ups (not blockers):**
- SKEL-2: real non-owner engineer test of the intake PRD (stronger evidence).
- Tuning backlog (Randy): shrink the ~3.8× token multiple via agent tuning +
  token optimizations; baseline = overhead ratio 0.94, TOD-1 11-round case.
- Findings-log prevention targets: uncovered defect classes + the recurring
  "remediation introduced its own defect" pattern (3×).

- Product repo: agentmerlin8/factory-todo-demo (public), main bd5642e.
- Control repo: agentmerlin8/factory-todo-control (public), main f7ac685.
- State: software-factory runs/ + state/ (v1; OC-8 split later).
- Evidence: docs/experiments/skel-{2,4,5}-*.md, runs/COMPARISON.md,
  runs/skel-5/CALIBRATION.md. Findings log: state/findings.jsonl.

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

## Next action: OWNER DECISION on what to build next (v1 is done)

All five SKEL items are closed and the v1 thesis is proven. Do not re-open
them or re-run their arms without an explicit owner request. The next move
is the owner's: pick a north-star direction (a real product through the
factory, the OC-8 state-repo split, cloud adapter, autonomy promotion) or
a follow-up (SKEL-2 human-engineer test, the token-tuning backlog). The
full vision in docs/vision.md §5+ is evidence-gated and owner-directed —
do not start it unprompted.

## Board

Issues #3 (SKEL-1), #4 (SKEL-2), #5 (SKEL-3), #6 (SKEL-4), #7 (SKEL-5) Done.
Issues #8/#9 (EXP-1/2) Done. The v1 board is fully Done.
Board IDs and the `printf -v` GraphQL pattern are in `HANDOFF.md` §6.