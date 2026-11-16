# SKEL-4 — Merge protocol verification (2026-11-15)

**Issue:** #6 · **OC-15** · **Verdict: ALL ACCEPTANCE CRITERIA PASS on a real PR.**

## Method

One real PR on the product repo `agentmerlin8/factory-todo-demo` (PR #6,
branch `mrg2-verify`), exercising a file rename, a CRLF file, and a normal
change. The repo has `strict: true` + required `ci` check (public+Free,
per EXP-3). Main was moved forward with a disjoint README commit to create
staleness, then the protocol was exercised end-to-end.

## The six checks (all executed, all PASS)

| # | Check | Result |
|---|---|---|
| 1 | Rename + CRLF + normal change on the branch | `store.test.ts → store.spec.ts`, `settings.ini` (CRLF), css note; 141 tests + build green |
| 2 | **Stale merge refused** | main moved to `fa329c1`; PR `mergeStateStatus=BEHIND`; `gh pr merge --squash` → "the head branch is not up to date with the base branch" (REFUSED) |
| 3 | Update-before-review | `factory.merge_protocol.update_before_review` merged main in → new head `c268af5`; `is_stale` True→False; 141 tests + build green on the new head |
| 4 | Updated merge succeeds | CI green on `c268af5`, `mergeStateStatus=CLEAN`; squash merge → `bd5642e` |
| 5 | **Squash tree == reviewed head tree (server-side)** | reviewed `12c5479aa74af690a4b647258b76e15d6e10fe1a` == landed `12c5479aa74af690a4b647258b76e15d6e10fe1a` (IDENTICAL) |
| 6 | CRLF + rename preserved byte-level | `od -c` on landed `settings.ini`: `\r\n` intact; squash diff shows `src/{store.test.ts => store.spec.ts}` with 0 content changes |

## Acceptance (issue #6)

- [x] verified on one real PR (rename + line-ending case) — PR #6, all six checks
- [x] strict up-to-date setting confirmed to refuse stale merges — check 2 (BEHIND, refused)
- [x] squash tree == reviewed head tree confirmed server-side — check 5 (identical hashes)

## Tooling (MRG-1)

`factory/merge_protocol.py`: `is_stale` (ancestry form), `update_before_review`
(merge main in, abort+raise on conflict, clean tree), `needs_rereview`
(story diff changed OR main delta touches manifest — MRG-5 anti-quadratic),
`main_delta_paths`, `trees_equal`/`head_tree` (post-merge ALARM, no
auto-revert — MRG-4). 11 unit tests on fixture repos; 199 total green.

## What this confirms

The platform's own guarantee IS the mechanism (no merge-tree protocol):
strict up-to-date + a real required check refuses stale merges; GitHub's
squash of an up-to-date branch lands a tree byte-identical to the reviewed
head, preserving renames and CRLF. Update-before-review is load-bearing —
it is exactly what makes reviewed tree == landed tree. EXP-1/3's throwaway
results now hold on the real product repo.

## Cuts honored (OC-15)

No merge-tree protocol, no post-merge auto-revert (alarm only), re-review
only when the story diff changed or main's delta touches its manifest.
