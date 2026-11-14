# EXP-1 — Squash equivalence on a real PR (OC-15 verification)

**Date:** 2026-11-14 · **Issue:** #8 · **Status:** DONE — all acceptance items verified
**Evidence repo:** `agentmerlin8/factory-exp-throwaway` (private, Free plan), PRs #1–#4
**Scripts:** `~/.hermes/cache/scratch/factory-exp/exp1.sh`, `exp1-strict.sh` (logs alongside)

## Method

One throwaway repo, four real PRs squash-merged via the GitHub API. Each case
compares three trees: the story branch head (post update-before-review merge),
the local `git merge-tree --write-tree main <branch>` prediction, and the tree
of GitHub's server-side squash commit. Cases include a rename
(`old-name.txt` → `new-name.txt`) and a CRLF file (`settings.ini`, `\r\n`
line endings) edited on the story branch.

## Results

| Case | Scenario | head tree | merge-tree | squash tree | Verdict |
|---|---|---|---|---|---|
| A | up-to-date, rename + CRLF, disjoint main move | `84c4e9f…` | `84c4e9f…` | `84c4e9f…` | **PASS** — all three equal |
| B | **stale** branch (main moved, no update) | `0b81e18…` | `e9865ed…` | `e9865ed…` | **PASS** — squash == merge-tree ≠ head |
| C | up-to-date, second data point | `e9c2431…` | `e9c2431…` | `e9c2431…` | **PASS** — all three equal |
| D | stale, no protection, merge attempt | — | — | merged | stale merge **succeeds** (see below) |

- **CRLF preserved:** landed `settings.ini` verified byte-level (`od -c`): `\r\n` intact through rename + edit + squash.
- **Rename preserved:** squash diff contains the delete/create pair with identical content to the reviewed head.
- **Case B is the load-bearing result:** when the branch is stale, GitHub's squash performs a real three-way merge — the landed tree equals `merge-tree(main, branch)` and **differs from the reviewed head**. Update-before-review is therefore not optional: it is exactly what makes reviewed tree == landed tree.

## Strict "up to date before merging" — NEGATIVE result (design correction)

- Branch protection PUT → **403** "Upgrade to GitHub Pro or make this repository public".
- Rulesets POST → **403**, same message.
- With no protection, a **stale PR squash-merges successfully** (case D, PR #4).
- **Conclusion: the Free plan has NO native up-to-date gate.** OC-15's "enable
  require-branches-up-to-date" is unavailable on Free private repos. The
  strict check must be **controller-enforced** (fits OC-14's controller-writer
  model). Verified working controller-side checks:
  1. `PR.base.sha == main tip` (REST) — detects staleness;
  2. `git merge-base(main, branch) == main tip` (ancestry form).
  Controller refuses the merge when stale; agent must update + re-review.

## Acceptance

- [x] one real PR merged via squash on a throwaway repo (four, actually)
- [x] merge-tree result == GitHub squash tree (incl. rename + line-ending)
- [x] strict "up to date before merging" behavior confirmed — **confirmed UNAVAILABLE on Free; controller-side enforcement required** (amendment to OC-15 mechanism, see disposition)

## Disposition / follow-up

- OC-15 core assumption (squash equivalence under update-before-review): **CONFIRMED**.
- OC-15 mechanism amendment needed: replace "enable the branch setting" with
  "controller enforces up-to-dateness before merge" (pending owner ratification).
- SKEL-4 must implement the controller-side staleness check, not rely on a
  repo setting.