# SKEL-4 plan — Merge protocol (issue #6, OC-15)

**Status:** draft · **Date:** 2026-11-15
**Principle:** prefer the platform's own guarantee over clever mechanisms.
EXP-1 proved squash-tree equivalence (rename + CRLF); EXP-3 proved the
strict up-to-date gate works on public+Free. The product repo
(factory-todo-demo) ALREADY has `strict: true` + required `ci` check.
SKEL-4 wires the operational protocol around that guarantee and verifies
it on ONE REAL product PR.

## What's already true (verified, not re-litigated)

- Squash tree == merge-tree(main, branch); when the branch is up to date,
  that equals the reviewed head tree (EXP-1 cases A/C). Stale branch →
  squash ≠ head (case B) — update-before-review is load-bearing.
- Strict gate refuses stale merges (405) ONLY when a real check is
  required; empty checks list = no-op (EXP-3 gotcha). Product repo has
  `ci` required, so the gate bites.
- CRLF + rename survive squash byte-for-byte (EXP-1).

## Slices (OC-17 sizing)

- **MRG-1: merge-protocol tooling** (~200 lines + tests). Pure functions in
  `factory/merge_protocol.py`:
  - `staleness(repo, pr)` → is the branch behind main? (base.sha vs main tip)
  - `update_before_review(workdir, branch)` → merge main into the branch,
    return the new head (the real commit CI + review run on).
  - `squash_equivalence(repo, pr)` → post-merge ALARM: compare the landed
    squash tree to the reviewed head tree; mismatch = alarm, NOT auto-revert.
  - `needs_rereview(story_manifest, main_delta_paths, story_diff_changed)` →
    re-review only if the story's own diff changed OR main's delta touches
    its manifest (avoids quadratic re-review).
  - `red_main_response(repo)` → block dispatches + prepare a revert PR
    description for the inbox (one-click human decision; no auto-revert).
- **MRG-2: the verification PR** (experiment, not code). One real PR on
  factory-todo-demo exercising rename + line-ending:
  1. Branch from main; rename a file + edit a CRLF file + a normal change.
  2. Move main forward (a disjoint commit) → branch is now STALE.
  3. Attempt merge → must be REFUSED (405, mergeable_state=behind).
  4. Update-before-review (merge main in) → CI green on the new head →
     merge SUCCEEDS.
  5. Post-merge: squash tree == reviewed head tree (server-side confirm).
  6. CRLF + rename preserved byte-level in the landed tree.
  Record all six as evidence; this satisfies issue #6 acceptance.

## Acceptance (issue #6)

- [ ] verified on one real PR (rename + line-ending case)
- [ ] strict up-to-date setting confirmed to refuse stale merges
- [ ] squash tree == reviewed head tree confirmed server-side

## What this does NOT build (OC-15 cuts)

- No merge-tree protocol (the platform's squash + strict gate IS the
  mechanism).
- No post-merge auto-revert (no identity was allowed to do it; MRG-4).
  Post-merge compare is a cheap ALARM; red main → block + prepared revert
  PR in the inbox as a one-click human decision.
- No re-review on every main move — only when the story diff changed or
  main's delta touches the story manifest (fixes quadratic re-review, MRG-5).

## Measurement

The verification PR's six checks are the evidence. Tooling gets unit tests
(staleness detection, re-review decision logic, alarm comparison) with
fixture git repos — no live GitHub calls in the core.
