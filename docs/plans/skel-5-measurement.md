# SKEL-5 plan — Measurement + seeded-defect calibration (issue #7, OC-16)

**Status:** draft · **Date:** 2026-11-15 · **The LAST skeleton item.**

## What already exists (verified, not rebuilt)

- Per-dispatch metering: `dispatch_completed` ledger events carry role,
  model, tokens (in/out), cost_usd, wall_s, outcome (SKEL-1 used these).
- Per-story metrics + process-overhead-ratio: `factory/metrics.py`
  `harvest()` + `render_comparison()` (used for runs/COMPARISON.md).
- Findings log with escape flags + reviewer precision: `factory/findings.py`.

So acceptance criteria 1 (every dispatch metered) and 3 (overhead ratio per
story) are substantially DONE — SKEL-5 closes the gaps and adds the two
genuinely new pieces.

## Slices (OC-17 sizing)

- **MEA-1: per-dispatch metering completeness + per-story cycle-time split**
  (~120 lines + tests). Extend metrics to report machine-wall vs human-min
  separately per story, and a `dispatch_audit` that flags any dispatch
  missing tokens/model/outcome (fail-closed: an unmetered dispatch is a
  process defect, counted). Verify against the real SKEL-1 ledger.
- **MEA-2: risk-tiering + budget enforcement** (~150 lines + tests).
  `factory/risk.py`: classify a story (small/medium/large) from its manifest
  + AC count + structural signals; small → skip plan review, one reviewer.
  `factory/budget.py`: controller-side spend cap + job timeout + dispatch
  refusal at ceiling (NOT agent self-report). Pure logic + tests.
- **MEA-3: seeded-defect catch-rate test** (experiment + harness). Plant 10
  known defects in a fixture codebase; run the reviewer in three modes
  (same-session, fresh same-family, fresh cross-family); measure catch-rate
  per mode. This is the calibration that gates routing (ECN-3: a reviewer
  that can't catch a known planted defect isn't trusted to route). The
  harness is code; the actual model runs are the experiment.

## Acceptance (issue #7)

- [ ] every dispatch metered (MEA-1 audit against real ledger)
- [ ] seeded-defect catch-rate measured across review modes (MEA-3)
- [ ] process overhead ratio reported per story (exists; MEA-1 confirms)

## The seeded-defect experiment design (MEA-3)

10 defects spanning the classes the factory actually hit (from the findings
log): stale-snapshot concurrency, self-certifying test, untrusted boundary,
silent mutation, stale live-region, contrast, scope creep, unhandled IO,
test-gap, off-by-one/ordering. Each planted in a small fixture with a
ground-truth label. Three review modes:
- **same-session**: reviewer sees the author's reasoning (anchored).
- **fresh same-family**: fresh context, same model family as author.
- **fresh cross-family**: fresh context, different family (the factory default).
Catch-rate = planted defects correctly flagged / 10, per mode. Also count
false positives (precision). The cross-family advantage measured here is
the evidence that justifies the factory's review routing.

## What this does NOT build (cuts)

- No cloud metering dashboard (local ledger + renders suffice for v1).
- No automatic model routing yet — calibration PRODUCES the evidence;
  routing decisions stay owner-gated (OC-4 data-gated promotion).
- No price table (tokens-only until a trusted price table exists).

## Measurement

The catch-rate table (3 modes × 10 defects) is the headline artifact.
Dispatch audit + per-story overhead confirm criteria 1 & 3 on real data.
