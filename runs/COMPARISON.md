# SKEL-1 comparison — factory vs control (OC-16)

**Date:** 2026-11-15 · **Run:** todo-demo (factory) vs todo-control (control)
**Same inputs:** identical scaffold (`947db84`), same design doc, same 5 story
specs, same coder model (`qwen4-max-preview`). Control = ONE `hermes -z`
session, no gates, no intermediate review. Factory = per-story dispatch +
deterministic gate + cross-family review + Copilot approval + human merge.

## Headline numbers (verified from the ledgers)

| Metric | Factory | Control | Multiple |
|---|---|---|---|
| Coder tokens (in+out) | 5,133,955 | 2,625,505 | 1.96× |
| Reviewer tokens | 4,828,353 | 2,334,011¹ | — |
| **Total tokens** | **9,962,308** | **2,625,505** | **3.79×** |
| Process-overhead ratio (non-coder/coder) | 0.94 | n/a² | — |
| Dispatch wall-time (s) | 5,271 | 1,115³ | 4.7× |
| Coder dispatches | 5 | 1 | — |
| Tests at finish | 141 | 77 | — |
| Review rounds per story | 11 / 2 / 4 / 4 / 3 | 0 (single pass) | — |

¹ The control's "reviewer" tokens are the **post-hoc evaluation review** run by
the controller to count escaped defects — NOT part of the control build. The
control build itself is the single 2.63M-token session.
² The control has no factory process; its overhead ratio is undefined by design.
³ Control session wall-time (1,115s); the 1,666s ledger figure includes the
post-hoc evaluation review.

## Defects — the decisive axis

**Factory: 0 escaped defects at merge.** Every story merged with Copilot
APPROVED and a clean cross-family review. 17 defects were found **and fixed
during the loop** (counted in the ledger as `defect_found`), so none reached
main. The review-surface budget (OC-17) and the deterministic gates caught
them before merge.

**Control: 6 escaped defects shipped to green tests** (77/77 passing, build
green), found only by the post-hoc review:

| Severity | Count | Defect |
|---|---|---|
| **BLOCKER** | 1 | Stale-snapshot overwrite in **all three mutations** (add/toggle/delete): a concurrent cross-tab write between read and write is silently clobbered. **Data loss.** Controller probe-verified (3/3 red). |
| MAJOR | 1 | Self-certifying concurrency test: writes the concurrent task *before* the read, not between read and write — green but proves nothing. |
| MINOR | 2 | `isTask` accepts empty-string titles (broken aria-labels); storage-failure alert mentions a "draft" for toggle/delete/filter where none exists. |
| NIT | 2 | Dead `subscribe`/`emit` scaffold code; filter announcement count from render-time state (latent race). |

The BLOCKER is exactly the defect the factory arm caught and fixed during
TOD-3's review loop (write-boundary re-read + merge). In the single-pass
build it escaped to a green suite — the concurrency test *certified* it.

## Measurement gaps (honest)

- **human_min: not recorded for either arm.** The owner's merge time and
  in-run attention were not instrumented. This is one of the two kill-criterion
  axes, so the go/no-go below rests on the **defects** axis, which IS measured.
- **cost_usd: 0.00 / "unknown"** — the provider returns no price; tokens are
  the cost proxy (per the standing convention: tokens-only until a trusted
  price table exists).
- Control defects are counted post-hoc by the same cross-family reviewer the
  factory used, so the detection method is symmetric; the factory's defects
  were caught *before* merge, the control's *after* shipping.

## Kill criterion (OC-16) verdict

> Factory must win on human-minutes **OR** escaped defects at a cost multiple
> the owner accepts — else STOP and reconsider.

- **Escaped defects: factory wins decisively** — 0 vs 6, including a data-loss
  BLOCKER and a self-certifying test in the control.
- **Cost multiple: ~3.8× tokens, ~4.7× dispatch wall-time.** Whether that is
  "acceptable" is the owner's call.
- **Human-minutes: not measured** — cannot claim a win on this axis.

**Recommendation: GO, conditional on owner acceptance of the ~3.8× token
multiple.** The factory demonstrably prevents a data-loss defect that the
single-pass build ships with green tests. The cost is real and ~4×; the
value is zero escaped defects vs six. The decision is the owner's trade-off.

**Caveat for the owner:** the factory's *own* remediation rounds introduced
defects three times (TOD-4 ×2, TOD-5 ×1), each caught by the next review
round. The loop is self-correcting but not free — the overhead ratio (0.94)
and the 11-round TOD-1 calibration are the price of that assurance.
