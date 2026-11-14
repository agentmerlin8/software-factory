# Open calls — ALL CLOSED (OC-1…OC-11 ratified by Randy 2026-11-14)

OC-1…OC-7 ratified 2026-11-14 (vision grill). OC-8…OC-11 opened by the
Fable 5.2 external design review (issue #1) and ratified by Randy
2026-11-14. This file is the decision record; the vision's locked-decisions
table carries the same facts.

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

## OC-8 — Where ledger writes go — CLOSED

**Decision (Randy, 2026-11-14): state lives OUT of the product repo, in a
dedicated state repo that spans projects, using an Obsidian vault.** This
deliberately supersedes the kit's old "ledger lives with the code" law.

Design as carved:
- A **dedicated factory-state repo** is the control home for ALL projects
  (single- and multi-repo alike) — not just multi-repo. It holds the
  workspaces, the append-only ledger, story records, dispatch packages, and
  the generated renders. The product repo stays pure product code.
- The state repo is **structured as an Obsidian vault**: machine truth is
  the append-only JSONL ledger; the human-facing view is generated markdown
  (state.md / DASHBOARD.md / PROVENANCE.md / story records) browsable in
  Obsidian. One state repo can span many projects.
- **Evidence binding across repos** (the mechanism that replaces "ledger
  lives with the code"): every event pins `repo@sha`; validation resolves
  each SHA against THAT product repo's object database; provenance joins
  across the repo set. This is the accepted workspace-model v0.3 mechanism,
  now the universal default. Atomicity is preserved by pinning exact product
  SHAs, not by co-locating files.
- Concurrency: git non-fast-forward rejection as compare-and-swap for ledger
  appends and claims; an Actions concurrency group per story as the cloud
  mutex. The state repo, not main, absorbs the write traffic.

**One interpretation flagged for Randy (not blocking):** "a dedicated repo"
is read as a NEW factory-state repo, kept separate from the personal
`~/Notes` vault — because high-frequency machine ledger writes would
conflict with that vault's Syncthing + cron auto-backup sync. If Randy meant
literally inside the existing personal vault, the sync-conflict problem must
be designed around first. See the round-3 grill.

## OC-9 — Merge policy + review/remediation policy — CLOSED

**Decision (Randy, 2026-11-14): configurable.** Merge policy is not a fixed
choice — it is per-workspace policy configuration, alongside **Copilot
review requirements and remediation**.

Design as carved:
- **Merge-policy spectrum** (per workspace, per autonomy level):
  1. human-merges-every-story (Level 1 default for the factory's own build);
  2. auto-merge stories that are expand-only/flagged with all gates green,
     human approves at the feature-acceptance gate (the recommended
     production default once metrics earn it);
  3. full auto-merge (explicit opt-in only; merge autonomy stays the last
     gate, per OC-4).
  Independent stories (no dependency edge) may proceed while another waits
  at a gate, under any policy. Machine-time vs waiting-on-human-time is
  measured regardless, so policy changes are data-driven.
- **Copilot review requirements — configurable** (on/off per workspace):
  when enabled, a Copilot review is a REQUIRED input to the review gate —
  requested, waited on, and its findings dispositioned like any panel
  finding. When disabled (the factory default), the factory's own
  fresh-context panel is the gate and platform bot reviews are not waited
  on. This amends the old blanket "Copilot review is never a gate" rule
  into a policy knob — the factory still OWNS the gate either way; a bot
  comment alone never merges anything.
- **Remediation — configurable**: how review findings are fixed —
  in-session coder fix loops (default), a separate remediation dispatch,
  or human-directed fixes; loop caps and tier escalation per policy.
- All three live in the workspace policy config, frozen as schema in P1,
  enforced by the controller (gate policy = OC-4's mechanism).

## OC-10 — Escalation model: confidence vs decision class — CLOSED

**Decision (Randy, 2026-11-14): as recommended.** Escalation by
**deterministic decision class**, checked by code — not self-reported
confidence. Classes: irreversible actions, scope change vs the PRD, new
dependencies, security-sensitive paths, budget overrun, reviewer
disagreement. Everything else proceeds on a **recorded assumption**; the
human reviews the assumption log when convenient (via the inbox); a veto
creates a rework story. The class list is policy config, extendable per
workspace. This is the Level 3 escalation contract.

## OC-11 — Primary persona — CLOSED

**Decision (Randy, 2026-11-14): engineering professionals are the target
audience — enabling people like Randy to build software autonomously.**
Not non-developer-first. The earlier "complete non-developer" end-state
wording (2026-10-18) is superseded as the PRIMARY target: the product is
for engineers who want autonomous leverage, with the architecture kept in
human hands (principle 15 as a gate). Touchpoints remain a profile, so a
lower-touch profile can exist later — but the engineer is the design
center through the roadmap, and the architecture/data-model/decomposition
approval gates are first-class, not hidden.