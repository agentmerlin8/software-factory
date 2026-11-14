# Software Factory

Ground-up rewrite of the AI software factory: **idea → deployable artifact**,
with the human involved at exactly the right steps.

Status: Vision APPROVED by grill rounds 1–2; **Fable 5.2 external design
review (issue #1) dispositioned 2026-11-14** — accepted fixes folded, four
owner calls open (OC-8…OC-11). Private until the demo works end-to-end
(P5 exit); then public.

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
2. [docs/open-calls.md](docs/open-calls.md) — owner decisions: OC-1…OC-7
   ratified 2026-11-14; OC-8…OC-11 open (from the design review).
3. [docs/design-review-disposition-2026-11-14.md](docs/design-review-disposition-2026-11-14.md)
   — disposition of the Fable 5.2 external design review (issue #1).
4. [docs/grill-record-2026-11-14.md](docs/grill-record-2026-11-14.md) — the
   round-1 vision grill (findings, verdict, owner-decision list).
5. [docs/grill-disposition-2026-11-14.md](docs/grill-disposition-2026-11-14.md)
   — how every grill finding was dispositioned in the fix pass.
6. [docs/grill-regrill-round2-2026-11-14.md](docs/grill-regrill-round2-2026-11-14.md)
   — the round-2 re-grill (APPROVE, 37/37 verified).
7. [docs/lineage.md](docs/lineage.md) — what we keep from the prior factory
   work and what we scrap.

## Lineage

Replaces the `ai-software-factory` kit effort (kept, now private). Lessons
learned there (MIE pipeline v3.2, kit v0.1, workspace model v0.3, Warp study)
carry forward; the code and Copilot-era assumptions do not. See docs/lineage.md.