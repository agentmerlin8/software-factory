# Automating the review-remediation loop (SKEL-4a)

**Date:** 2026-11-15 · **Trigger:** Randy — "this is a loop that we perform often
and I would like to eventually have this handled automatically by the factory."
**Status:** design + first mechanical pieces shipped; full autonomy is a slice.

## What the loop actually is

Observed over three rounds on factory-todo-demo#1:

```
detect new review → verify each finding by EXECUTION → triage
  → fix the CLASS (not the instance) → add regression tests
  → close the gate hole that let it escape → commit/push
  → reply + resolve threads → re-request review → repeat
```

Round history: 4 findings → 4 resolved + 2 previously-missed → (round 3 in flight).
Every round so far surfaced a **real** defect, and every round also exposed a
**gate blind spot**. That second part is the factory's actual job.

## The two loops, and why only one should be automated first

1. **Remediation loop (mechanical, automatable now):** fetch → verify → fix →
   test → push → reply → resolve → re-request. Deterministic control flow;
   the only model work is authoring the fix.
2. **Prevention loop (the valuable one):** after each round, ask "which
   deterministic check would have caught this?" and add it. This is what
   converts a recurring cost into a shrinking one.

Automating (1) without (2) just makes the factory faster at paying the same
bill. **Ship them together or the loop never converges.**

## Design

### Trigger
`pull_request_review` / `check_run` events are unreliable for Copilot (see
`pr-review-rounds`: REST re-requests can no-op; a pass can land in pieces).
Use a **poller** keyed on the review OBJECT:

- `latest_review_id > state.last_review_id` AND
  `review.user.login == copilot-pull-request-reviewer[bot]` AND
  `review.commit_id == current_pr_head`
- Never gate on the workflow run: it completes before comments ingest.

### State (ledger, not a side file)
Reuse the JSONL ledger. New event types:
`review_detected`, `finding_verified`, `finding_dispositioned`,
`remediation_pushed`, `gate_extended`, `review_requested`, `loop_converged`.
Each pins `repo@sha` + review id, so a crashed worker resumes exactly.

### Per-round worker
1. **Verify before fixing.** Every finding gets an executable probe. Round 2
   proved why: 2 of 4 reviewer findings were FALSE (diff-only reasoning), and
   round 3 proved the inverse: a reported 4.38:1 was actually 15/18 combos
   failing at 1.96:1. Trust neither direction.
2. **Triage:** FIX / ALREADY-FIXED (cite sha) / DISPUTE (reply, leave open) /
   HUMAN (owner decision). Never silently drop.
3. **Fix the class.** One finding is usually a family: the contrast finding
   was one button, but the class was "every control × every state × every
   theme". Sweep siblings in the same pass.
4. **Extend the gate.** For each verified finding, either a deterministic
   check exists (then it was a coverage gap — widen it) or one can be written
   (write it). Record `gate_extended` with the before/after proof:
   **the new check MUST fail the pre-fix head and pass the fixed head.**
5. Push one commit per round; reply with the real sha; resolve threads via
   GraphQL; re-request via `requestReviewsByLogin` (the form that registers).

### Convergence + budget
- **Converged** = a review at the current head with **no open AND no
  previously-missed issues**, and zero unresolved threads. Copilot never
  submits a formal `APPROVED` state — that clean COMMENTED review IS the
  achievable approval. Do not loop waiting for a state that never comes.
- **Budget law:** Copilot bills per generation (~$3 measured). Default
  **initial + ≤2 re-reviews per PR**; an unbounded drive-to-clean needs an
  explicit recorded owner call. Randy's standing directive for this run:
  drive to a clean verdict (recorded 2026-11-15).
- Escalate to the human on: >20 findings in one round, a disputed
  security-shaped finding, or 3 consecutive rounds returning the same family
  (that means the class-closing pass is needed, not another instance fix).

### What stays human
Merge. Always. The loop never merges and never touches `main` (OC-9 mode 1).

## Shipped so far (this round)

- `factory/a11y.py::audit_gradients` — gradient stops × brightness × themes.
- `factory/boundaries.py` — container-only parse-cast detection.
- Both wired into `pre_review`, both proven fail-before/pass-after.
- Story ACs now carry malformed-element and all-states visual requirements.

## Next slice (SKEL-4a)

`factory review-loop <pr>` — the poller + worker above, driven by the ledger,
with `--max-rounds` (default 3) and `--dry-run`. Reuse
`review-remediation-loop`'s proven watcher/worker split; the factory version
adds the **gate-extension step** and the execution-verification requirement,
which are the two things that made these rounds converge instead of churn.