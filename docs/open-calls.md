# Open calls — OC-1…OC-7 CLOSED; OC-8…OC-11 OPEN (2026-11-14)

OC-1…OC-7 ratified by Randy 2026-11-14. OC-8…OC-11 opened by the Fable 5.2
external design review (issue #1); recommendations recorded, awaiting
Randy. This file is the decision record; the vision's locked-decisions
table carries the ratified facts.

## OC-1 — Relationship to the old public repo — CLOSED

**Decision (Randy, 2026-11-14): keep the old repo and make it private.**
No archive. `agentmerlin8/ai-software-factory` visibility flipped to private
(executed + verified 2026-11-14); it remains the read-only salvage source
for proven control-plane machinery (ledger, controller, gates, review
lane). The new repo stays ground-up; nothing is imported wholesale.

**Public-flip timing (grill fix 1.1, Randy 2026-11-14): the new repo goes
PUBLIC at P5 exit** — demo end-to-end working is the "something working"
bar. P7 is polish of an already-public repo. (Resolves the lineage-vs-roadmap
contradiction the round-1 grill found.)

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

---

# Opened by the Fable 5.2 design review (issue #1, 2026-11-14)

## OC-8 — Where ledger writes go — OPEN

The ledger lives in the product repo and pushes at every gate. If those
pushes go to main they collide with the human merge gate and branch
protection, fire the deployability CI on every event, break "one commit
per story," and race on concurrent appends. Claim-lease renewal would mean
a push every few minutes. MIE's in-repo-on-main ledger tolerated this only
because runs were serial.

- **Recommended: dedicated ref + compare-and-swap.** Ledger on an orphan
  ref (`refs/factory/ledger`); git's non-fast-forward rejection is the CAS
  primitive for both appends and claims. Cloud jobs use an Actions
  `concurrency` group per story as the mutex (simpler than a renewed
  lease); the lease TTL stays the liveness signal, not a push cadence. The
  ledger never touches main. Reason: keeps trunk clean, makes concurrent
  appends safe by construction, and the ref is fetchable for evidence
  validation on any machine.
- Stricter: keep the ledger on main but batch pushes at gates only. Simpler
  ref model, but still fires deployability CI and still races; rejected.
- **Must be decided before P1 freezes the ledger schema.**

## OC-9 — Merge policy: human per story vs per release — OPEN

Serial stories behind a human merge gate = one interruption per story
(20 stories = 20 interruptions), which contradicts the Level 3 promise.

- **Recommended: intermediate merge policy.** Stories that are
  expand-only or flagged AND have all gates green merge automatically;
  the human approves at the **feature-acceptance gate** — the release
  boundary where user-visible behavior ships. One human decision per
  release, not per commit. Independent stories (no dependency edge) may
  proceed while another waits at the gate; the claim lock is per story and
  decomposition is dependency-aware, so this is bounded, not free-for-all
  concurrency. Measure machine-time vs waiting-on-human-time regardless.
  Reason: keeps a human decision on every release while removing the
  per-commit bottleneck; fits OC-3 (trunk) and OC-4 (gate policy) — it
  amends merge-gate granularity, which is why it's an owner call.
- Stricter: keep human-merges-every-story (current OC-3 default). Safest,
  but the human is the bottleneck and Level 3 is unreachable at this
  granularity.
- This amends OC-3/OC-4's merge-gate granularity within their policy
  framework; it does not reverse trunk-based delivery.

## OC-10 — Escalation model: confidence vs decision class — OPEN

The Level 3 contract rests on "can't answer confidently," but model
self-reported confidence is poorly calibrated — it will either interrupt
constantly or miss what matters.

- **Recommended: deterministic decision-class escalation.** Escalate on
  defined classes checked by code, not self-reported confidence:
  irreversible actions, scope change vs the PRD, new dependencies,
  security-sensitive paths, budget overrun, reviewer disagreement.
  Everything else proceeds on a **recorded assumption**; the human reviews
  the assumption log when convenient; a veto creates a rework story. Turns
  most blocking questions into non-blocking ones. Reason: deterministic,
  auditable, and actually implementable; matches "a rule without a gate
  doesn't hold."
- Stricter: keep a confidence threshold. Simpler to state, but unreliable
  in practice; rejected.

## OC-11 — Primary persona: engineer vs non-developer — OPEN

The vision's end state is a "complete non-developer," but the mission
Randy describes is an engineering professional. The two want different
touchpoints (an engineer approves architecture/data-model/decomposition;
a non-developer wants those hidden).

- **Recommended: engineer-primary through P6, touchpoints as a profile.**
  Name the engineer as the primary persona now; make the set of human
  touchpoints a configurable profile so the non-developer profile can come
  later without a redesign. This also turns principle 15 ("Randy keeps the
  architecture") into a real gate on architecture/decomposition approval.
  Reason: matches who actually uses it first and what Randy needs; avoids
  building a muddled default that serves neither.
- Stricter: design non-developer-first now. Matches the end-state wording,
  but hides the architecture gates Randy explicitly wants and delays the
  engineer use case.