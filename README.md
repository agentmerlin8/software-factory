# Software Factory

Ground-up rewrite of the AI software factory: **idea → deployable artifact**,
with the human involved at exactly the right steps.

Status: **vision synthesis under review** (2026-11-14). Private until something
works end-to-end; then public.

## What this is

A CLI-driven factory that takes a plain description of software someone wants,
guides them through the questions that flesh it out (including clickable
Storybook wireframes of the UI), decomposes it into features and stories, runs
the stories through a plan → review → code → review → test pipeline with
adversarial fresh-context review, and carries the work through merged PRs and
CI/CD — involving the human only where the system cannot confidently decide.

## Read order

1. [docs/vision.md](docs/vision.md) — the consolidated vision (sources, goals,
   architecture, principles, roadmap).
2. [docs/open-calls.md](docs/open-calls.md) — decisions awaiting the owner.
3. [docs/lineage.md](docs/lineage.md) — what we keep from the prior factory
   work and what we scrap.

## Lineage

Replaces the public `ai-software-factory` kit effort. Lessons learned there
(MIE pipeline v3.2, kit v0.1, workspace model v0.3, Warp study) carry forward;
the code and Copilot-era assumptions do not. See docs/lineage.md.