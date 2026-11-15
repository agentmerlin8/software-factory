# SKEL-2 — Intake spike result (2026-11-15)

**Issue:** #4 · **Hypothesis 2:** guided intake produces a PRD an engineer
approves. **Verdict: the hypothesis HOLDS, with a measured caveat.**

## What was built

- **INT-1** `factory intake` CLI — harness-agnostic state machine
  (start/answer/generate/status), deterministic PRD assembly, fail-closed.
- **INT-2** intake-agent role package — bounded question flow (≤2 rounds,
  ≤12 questions, options + recommendations), CLI owns state (OC-7).
- **INT-3** Storybook wireframe template — 7 clickable mock-data stories
  (Add/List/ListEmpty/Toggle/Delete/Filter/Full composite), local URL,
  contrast gate 0 findings both themes.
- **INT-4** the engineer test — fresh-context independent engineer persona
  (Randy's decision; cross-family `deepseek-v4-pro`), context-isolated
  (PRD + original description + wireframe source ONLY, never the intake
  conversation).

## The result

| Round | Verdict | Wall | Findings |
|---|---|---|---|
| 1 | REQUEST-CHANGES | 139s | 2 blocker, 2 major, 3 minor |
| 2 | **APPROVE with notes** | 87s | all 7 round-1 concerns RESOLVED; 5 new minor/nit |

**Total engineer review time: 226s across 2 rounds.** Round-2 engineer:
"No blocker remains. An engineer can build this."

## The key finding — the spike surfaced its own product risk

The round-1 PRD (thin template: platform/stack/features/look only) was
**rejected** by the independent engineer for real gaps a builder would
have to invent:
- **BLOCKER:** no acceptance criteria per feature
- **BLOCKER:** persistence mechanism unspecified
- **MAJOR:** the "daily tasks" ambiguity silently dropped
- **MAJOR:** data model only in wireframe code, not the PRD

This is exactly hypothesis-2's risk materializing — and the independent
review caught it BEFORE any builder invented answers. The fix made these
**structural**: acceptance/persistence/data_model are now REQUIRED intake
categories, and acceptance must cover EVERY feature (the CLI refuses
uncovered features). The PRD template renders per-feature ACs, data model,
persistence, and an explicit assumptions section. Round 2 approved.

**The intake process improved itself through the same independent-review
dynamic that made the factory arm win SKEL-1.** The thin template was the
defect; the engineer review was the gate; the enriched schema is the fix.

## Caveat (recorded per Randy's decision)

The reviewer is an **agent persona, not a human engineer**. This measures
the artifact's clarity to a fresh, independent reader — NOT human
acceptance. Same-model-family blind spots are possible (mitigated by
cross-family choice). A real non-owner engineer test remains the stronger
follow-up when one is available. human_min is therefore "not applicable"
for this run; the headline number is the 226s review time + 2 rounds.

## Remaining minor notes (round 2, for the code-phase spec)

- B: wireframe FullApp uses String(Date.now()) for id; PRD says
  crypto.randomUUID (PRD wins — wireframe is illustrative).
- C: FullApp composite empty message is generic vs FilterView's per-filter.
- D: AddTask wireframe shows no rejection-feedback visual state.
- E: "accessible error" mechanism — now specified as role="alert" (gap A
  closure also added the separate filter persistence key).

## Acceptance (issue #4)

- [x] intake produces a PRD from a plain to-do-app description
- [x] local Storybook wireframes viewable via URL (localhost:6006)
- [x] tested with ≥1 non-owner engineer (agent persona, caveat recorded);
      approval + time recorded (APPROVE, 226s, 2 rounds)

## Artifacts

- `runs/skel-2/ledger.jsonl` — intake_approved event + per-round dispatches
- `runs/skel-2/evidence/PRD-v2.md` — the approved PRD
- `runs/skel-2/engineer-review.output.txt` / `-r2.output.txt` — both verdicts
- `templates/wireframes/` — the reusable Storybook template
- `process/intake-agent.md` — the enriched role package
