# Software Factory

Ground-up rewrite of the AI software factory: **idea → deployable artifact**,
with the human involved at exactly the right steps.

Status: Vision grilled (rounds 1–4) + two Fable external reviews
dispositioned. **All owner calls OC-1…OC-16 ratified 2026-11-14.** Strategy
per Fable review 2: **build with cuts** — a v1 walking skeleton + control
arm replaces the contract-freeze-first roadmap; controller-writer security;
update-before-review merge protocol; baseline/kill criterion. Next: build
SKEL-1. Private until the demo works end-to-end; then public.

## What this is

A CLI-driven factory that takes a plain description of software someone wants,
guides them through the questions that flesh it out (including clickable
Storybook wireframes of the UI), decomposes it into features and stories, runs
the stories through a plan → review → code → review → test pipeline with
adversarial fresh-context review, and carries the work through merged PRs and
CI/CD — involving the human only where the system cannot confidently decide.

## Read order

1. [docs/vision.md](docs/vision.md) — the consolidated vision (sources, goals,
   architecture, principles, measurement, walking-skeleton roadmap).
2. [docs/open-calls.md](docs/open-calls.md) — owner decisions: OC-1…OC-16
   all ratified 2026-11-14.
3. [docs/design-review-2-disposition-2026-11-14.md](docs/design-review-2-disposition-2026-11-14.md)
   — disposition of Fable review 2 (issue #2): build with cuts, OC-12…16.
4. [docs/design-review-disposition-2026-11-14.md](docs/design-review-disposition-2026-11-14.md)
   — disposition of Fable review 1 (issue #1).
5. [docs/grill-round4-2026-11-14.md](docs/grill-round4-2026-11-14.md) —
   round-4 confirmation (APPROVE, 21/21).
6. [docs/grill-round3-2026-11-14.md](docs/grill-round3-2026-11-14.md) —
   round-3 feasibility grill (approve_with_fixes).
7. [docs/grill-record-2026-11-14.md](docs/grill-record-2026-11-14.md) +
   [grill-disposition](docs/grill-disposition-2026-11-14.md) +
   [round-2 re-grill](docs/grill-regrill-round2-2026-11-14.md) — rounds 1–2.
8. [docs/lineage.md](docs/lineage.md) — what we keep from the prior factory
   work and what we scrap.

## Visibility — the board

Work is tracked on the **[Software Factory board](https://github.com/orgs/agentmerlin8/projects/5)**
(org project #5). Every work item is an issue in this repo. Three fields
tell you everything at a glance:

- **Status** — Backlog / In Progress / Done (overall).
- **Stage** — Planning / Coding / Reviewing / Testing / Merging / Blocked /
  Done (what state the active work is in right now).
- **Work Type** — Feature / Story / Experiment / Review / Bug.

Views: **Board** (by Status), **Pipeline** (by Stage), **Backlog** (table).
Labels on issues mirror this (`factory`, `v1`, `stage:coding`, etc.). The
ledger is the machine truth; the board is a render. New `factory`-labeled
issues auto-add via `.github/workflows/auto-add-to-board.yml` (needs the
`BOARD_PAT` secret — a classic PAT with `project` scope).

## Lineage

Replaces the `ai-software-factory` kit effort (kept, now private). Lessons
learned there (MIE pipeline v3.2, kit v0.1, workspace model v0.3, Warp study)
carry forward; the code and Copilot-era assumptions do not. See docs/lineage.md.