# Open calls — ALL CLOSED (Randy, 2026-11-14)

All seven calls ratified 2026-11-14. This file is the decision record;
the vision's locked-decisions table carries the same facts.

## OC-1 — Relationship to the old public repo — CLOSED

**Decision (Randy, 2026-11-14): keep the old repo and make it private.**
No archive. `agentmerlin8/ai-software-factory` visibility flipped to private
(executed + verified 2026-11-14); it remains the read-only salvage source
for proven control-plane machinery (ledger, controller, gates, review
lane). The new repo stays ground-up; nothing is imported wholesale.

## OC-2 — Cloud agent runtime — CLOSED

**Decision (Randy, 2026-11-14): GitHub-native.** GitHub Actions–backed agent
sessions first: the CLI triggers a workflow that runs an agent in a
container with repo-scoped credentials. The adapter seam keeps other cloud
runtimes swappable later. Board drag → dispatch lives in the same place.

## OC-3 — Branch/integration strategy — CLOSED

**Decision (Randy, 2026-11-14): trunk-based — Option 1.** Every story merges
straight to main; feature branches are NOT used. Chosen explicitly for
least agent friction:

- One canonical base: every dispatch branches from origin/main at a pinned
  SHA; no feature-branch base resolution, no drift sync.
- Conflicts stay small and early (slice law: one structural signal,
  expand-first, independently mergeable); no big-bang feature merge — the
  event agents handle worst.
- One delivery milestone: MERGED = merged to main. Ledger states, board
  Stage, provenance, review records keep their proven shape; one human
  merge gate per story.
- Squash merges, one commit per story on main: clean evidence pinning and
  single-commit reverts.

The isolation a feature branch would have provided is replaced by gates:

1. **Feature-acceptance gate** — a feature is not "released" until ALL its
   stories are merged AND feature-level validation passes (acceptance
   tests / staging deploy / integrated UI approval). Validation gate, not
   branching gate.
2. **Expand-only or flagged** for user-visible incomplete flows — the
   discipline that keeps main always deployable.

All constraints satisfied: main always deployable (gates + flags), real
feature-validation surface (acceptance gate), slices independently
mergeable (trunk is the shape the slice law was written for), one human
merge gate per story, expand-first ordering, single-commit reverts.

## OC-4 — Autonomy levels: operating rules — CLOSED

**Decision (Randy, 2026-11-14): as recommended.** Levels are gate policy
(which transitions require a human actor), one pipeline, no separate code
paths. Factory's own build starts at Level 1; Level 2 is the default for
target repos once the demo passes; Level 3 only behind measured promotion
criteria + an escalation contract (confidence threshold, question channel,
BLOCKED-while-waiting). Merge autonomy remains the last gate, if ever.

## OC-5 — Dogfooding cutoff — CLOSED

**Decision (Randy, 2026-11-14): as recommended.** Dogfooding starts at P3
exit — one story driven end-to-end by the factory itself (dispatch → code →
review → merged PR) with the ledger intact, even if intake is still
human-driven. From then: NEW factory features go through the factory;
control-plane changes stay structured-vibe until the review lane is proven
on itself.

## OC-6 — Storybook intake spike — CLOSED

**Decision (Randy, 2026-11-14): as recommended.** Early bounded spike
(P0/P1): one agent session, running Storybook in the workspace,
screenshot-back first, then the live-link UX. Evaluate 2–3 model/adapter
combos on a fixed script ("build a to-do app UI from this conversation");
pick on evidence.

## OC-7 — Where the interactive intake lives — CLOSED

**Decision (Randy, 2026-11-14): as recommended.** Harness-agnostic intake
protocol (the CLI exposes intake state; any chat harness drives it), first
implementation in Hermes chat. The end-user product surface (web chat?
desktop?) stays open until the demo works.