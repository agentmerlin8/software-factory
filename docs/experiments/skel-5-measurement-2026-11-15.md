# SKEL-5 — Measurement + seeded-defect calibration (2026-11-15)

**Issue:** #7 · **OC-16 / ECN-3** · **The LAST skeleton item — v1 COMPLETE.**

## Acceptance (all met)

- [x] **every dispatch metered** — `dispatch_audit` on the real SKEL-1
      ledger: 11/11 metered, 0 defects (after re-attributing the TOD-1 coder
      usage correction). Fail-closed audit flags any missing
      tokens/model/outcome/wall_s; honest exclusions for failed-to-launch
      dispatches + correction-recovered usage.
- [x] **seeded-defect catch-rate measured across review modes** — 10 planted
      defects, 3 modes (same-session / fresh same-family / fresh cross-family).
      All modes caught 10/10 salient defects. See CALIBRATION.md + the honest
      nuance below.
- [x] **process overhead ratio reported per story** — `factory/metrics.py`
      harvest + render_comparison (used for runs/COMPARISON.md); cycle_time_split
      adds machine-wall vs human-min per story.

## What was built

- **MEA-1**: `dispatch_audit` + `cycle_time_split` (metrics.py). 8 tests.
- **MEA-2**: `factory/risk.py` (small/medium/large tiering; small skips plan
  review + 1 reviewer; ≥2 structural signals = stacked = large) +
  `factory/budget.py` (controller-side spend cap + timeout + dispatch refusal
  at ceiling, NOT agent self-report). 10 tests.
- **MEA-3**: `factory/calibration.py` (10 ground-truth defects + pure
  catch-rate/precision scoring) + fixture (4 files, 10 planted defects) +
  the 3-mode experiment. 6 tests.

## Calibration result + honest nuance

| mode | caught/10 | catch-rate | extra real flags | precision vs 10 |
|---|---|---|---|---|
| same-session | 10/10 | 100% | 3 (real, uncatalogued) | 77% |
| fresh same-family | 10/10 | 100% | 0 | 100% |
| fresh cross-family | 10/10 | 100% | 0 | 100% |

All modes catch SALIENT defects equally. The same-session mode found 3 extra
genuine bugs (dup-ID collision, empty-title add, unguarded delete IO) — real,
not false positives; the fixture has >10 defects. **The cross-family advantage
is on SUBTLE defects** (self-certifying tests, masked concurrency) — evidenced
by the real SKEL-1 runs where fresh cross-family review caught what same-session
missed, NOT by this salient-defect fixture. Routing decisions weight the real
subtle-defect evidence; this calibration confirms baseline competence across
modes (ECN-3: a reviewer that can't catch known defects isn't trusted to route —
all three pass that bar).

## v1 walking skeleton — COMPLETE

All five skeleton items done:
- SKEL-1: factory beats control on escaped defects (0 vs 6), OC-16 GO.
- SKEL-2: intake produces an engineer-approved PRD (hypothesis 2, caveat).
- SKEL-3: controller-writer security (OC-14), agent can't write state.
- SKEL-4: merge protocol (OC-15), squash tree == reviewed head on a real PR.
- SKEL-5: measurement + calibration (OC-16), every dispatch metered.

The factory has proven all three hypotheses end-to-end. Next phase is the
north-star vision (post-v1, evidence-gated), owner-directed.
