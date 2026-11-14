# Open calls — status (updated 2026-11-14)

**6 of 7 closed by Randy 2026-11-14.** OC-3 (branching) stays open — Randy
has other ideas; discussion in progress.

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

## OC-3 — Branch/integration strategy — OPEN (in discussion)

Randy has other ideas (2026-11-14) — talking it through before deciding.
The tentative sketch from his notes: stories → feature branch → validate →
main. Merlin's earlier recommendation (story PRs into a feature branch,
feature validation, then PR to main, human gates at both levels) is on the
table but NOT ratified. Constraints any answer must satisfy:

- main always deployable (the demo promises a deployable artifact)
- feature-level validation has a real integration surface
- story slices stay independently mergeable (slice-sizing law)
- human merge gate maps cleanly onto whatever levels exist
- expand-first ordering for dependency chains; reverts stay tractable

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