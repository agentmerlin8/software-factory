# Software Factory

Ground-up rewrite of the AI software factory: **idea → deployable artifact**,
with the human involved at exactly the right steps.

Status: **VISION APPROVED** — grill round 1 APPROVE WITH FIXES (72/100), fix
pass applied, round-2 re-grill **APPROVE (37/37 verified, 0 new findings)**
2026-11-14. Private until the demo works end-to-end (P5 exit); then public.

## What this is

A CLI-driven factory that takes a plain description of software someone wants,
guides them through the questions that flesh it out (including clickable
Storybook wireframes of the UI), decomposes it into features and stories, runs
the stories through a plan → review → code → review → test pipeline with
adversarial fresh-context review, and carries the work through merged PRs and
CI/CD — involving the human only where the system cannot confidently decide.

## Read order

1. [docs/vision.md](docs/vision.md) — the consolidated vision (sources, goals,
   architecture, principles, measurement, roadmap).
2. [docs/open-calls.md](docs/open-calls.md) — ratified owner decisions (all
   seven closed 2026-11-14).
3. [docs/grill-record-2026-11-14.md](docs/grill-record-2026-11-14.md) — the
   round-1 vision grill (findings, verdict, owner-decision list).
4. [docs/grill-disposition-2026-11-14.md](docs/grill-disposition-2026-11-14.md)
   — how every grill finding was dispositioned in the fix pass.
5. [docs/grill-regrill-round2-2026-11-14.md](docs/grill-regrill-round2-2026-11-14.md)
   — the round-2 re-grill (APPROVE, 37/37 verified).
6. [docs/lineage.md](docs/lineage.md) — what we keep from the prior factory
   work and what we scrap.

## Lineage

Replaces the `ai-software-factory` kit effort (kept, now private). Lessons
learned there (MIE pipeline v3.2, kit v0.1, workspace model v0.3, Warp study)
carry forward; the code and Copilot-era assumptions do not. See docs/lineage.md.