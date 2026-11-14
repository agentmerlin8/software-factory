# Open calls — awaiting Randy (2026-11-14)

Each call: the fork, my recommendation first with its reason, and the
stricter alternative stated honestly. Answer in any order, in fragments.

## OC-1 — Relationship to the old public repo

The notes say "scrap it." The kit work in `ai-software-factory` (control
plane, ledger, gates, review lane — merged S1/S2/S3.5) is proven machinery.

- **Recommended: new repo, read-only salvage.** `software-factory` is the
  clean home; we copy + genericize the proven control-plane pieces as we
  need them (P2), never import the Copilot-era agent layout or the kit's
  in-flight grill debt. Old repo gets an archived/moved notice once the new
  one works. Reason: ground-up clarity without re-earning five months of
  hard-won mechanics.
- Stricter: truly from zero, re-derive everything. Cleaner narrative, but
  we'd rebuild the ledger/controller/gates that already passed real runs.

## OC-2 — Cloud agent runtime

"Cloud agents" is locked as a requirement; the mechanism is not.

- **Recommended: GitHub Actions–backed sessions first** (the CLI triggers a
  workflow that runs an agent in a container with repo-scoped credentials),
  with the adapter seam keeping Copilot coding agent / other clouds
  swappable. Reason: GitHub-native matches "Boards exclusively," no new
  platform dependency, and the board-drag → dispatch story lives in the
  same place.
- Stricter: Copilot cloud coding agents as the primary cloud runtime —
  closer to the work-side pattern, but re-imports the agent-inheritance
  risk and platform coupling we're rewriting away from.

## OC-3 — Branch/integration strategy

Tentative in the notes: stories → feature branch → validate → main.

- **Recommended: story branches → PR into a feature branch → feature
  validation → PR to main**, with the human merge gate at BOTH levels for
  now (story PRs into the feature branch can become policy-auto at Level 2+
  once metrics earn it). Reason: matches Randy's sketch, keeps main always
  deployable, gives feature-level QA a real integration surface.
- Stricter: every story PR straight to main (expand-first, feature flags).
  Simpler machinery, but feature validation happens on main — riskier for
  the demo's "deployable artifact" promise.

## OC-4 — Autonomy levels: operating rules

Scale is locked (1/2/3); the rules are not.

- **Recommended: levels as gate policy** (which transitions require a human
  actor), starting everything at Level 1 for the factory's own build, Level
  2 as the default for target repos once the demo passes; Level 3 only
  behind measured promotion criteria + an escalation contract (confidence
  threshold, question channel, BLOCKED-while-waiting). Reason: one pipeline,
  auditable promotion, no separate code paths.
- Stricter: hard-code Level 2 (three touchpoints) and treat Level 3 as
  research. Less to build now; delays the stated goal.

## OC-5 — Dogfooding cutoff

- **Recommended: dogfood starts when P3 passes** — one story driven
  end-to-end by the factory itself (dispatch → code → review → merged PR)
  with the ledger intact, even if intake is still human-driven. From that
  point, NEW factory features go through the factory; control-plane changes
  stay structured-vibe until the review lane is proven on itself. Reason:
  earliest real feedback without betting the spine on unproven machinery.
- Stricter: wait for P5 (demo end-to-end). Safer, but weeks of building the
  factory without using it — and the dogfood lessons arrive late.

## OC-6 — Storybook intake: the hard nut

Which model/agent can build live wireframes from conversation and show them
to the user?

- **Recommended: spike it in P0/P1 as a bounded experiment** — one agent
  session, a running Storybook in the workspace, screenshot-back first
  (works in any chat harness), then the live-link UX. Evaluate 2–3
  model/adapter combos on a fixed script ("build a to-do app UI from this
  conversation") and pick on evidence. Reason: it's the riskiest UX piece;
  cheap early failure beats late discovery.
- Stricter: defer to P4 as planned and build intake text-only first.
  Lower early risk, but the wireframe loop is core to Randy's vision — a
  late failure reshapes the product.

## OC-7 — Where the interactive intake lives

- **Recommended: harness-agnostic intake protocol + first implementation in
  Hermes chat** (the CLI exposes intake state; any chat harness drives it;
  Hermes is adapter #1). The end-user product surface (web chat? desktop?)
  stays open until the demo works. Reason: matches runtime-agnostic law;
  we can use it ourselves immediately.
- Stricter: build a dedicated web intake UI now. More product-shaped, but
  it's a second frontend before the factory produces anything.