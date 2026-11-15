# Open calls — ALL CLOSED (OC-1…OC-16 ratified by Randy 2026-11-14)

OC-1…OC-7 ratified 2026-11-14 (vision grill). OC-8…OC-11 opened by Fable
design review 1 (issue #1), ratified 2026-11-14. OC-12…OC-16 opened by
Fable design review 2 (issue #2), ratified by Randy 2026-11-14 ("I agree
with your recommendations"). This file is the decision record; the
vision's locked-decisions table carries the same facts.

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

**Confirmed (Randy, 2026-11-14): a NEW dedicated factory-state repo,
separate from the personal `~/Notes` vault** — high-frequency machine ledger
writes must not fight that vault's Syncthing + cron auto-backup sync.

**Scope + mining (Randy, 2026-11-14):** the state vault can be **scoped to a
person, a team, or an organization**. That scope sets ownership and
visibility of the state and who may mine it. Because the state is an
Obsidian vault of generated markdown + the ledger, **tools can mine it to
see how things were built** — provenance, decisions, patterns, cost/cycle
history — not just read current state. The vault is a queryable knowledge
substrate, not only a state store. The scope/ownership model is frozen in
P1; the mining tools are a capability built on top (later phase), feeding
the measurement/statistics view (§10) and the "how was this built"
provenance story.

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

---

# Opened by Fable design review 2 (issue #2) — ratified 2026-11-14

Finding IDs below use the canonical 3+ letter convention (MRG/SEC/ECN/HUM/
OVR/PRD); Fable's original short labels are kept in parentheses for
traceability only.

## OC-12 — Roadmap: walking skeleton vs P1 freeze — CLOSED

**Decision (Randy, 2026-11-14): walking skeleton.** Replace the P1 contract
freeze with a 5-story local walking skeleton + a control arm. Contracts are
**v0** (schema-versioned, expected to change); freeze only after ~10 real
stories. Rationale (Fable OVR-1 / E1): the hand-run tests the ledger, not
the three risky hypotheses — (1) an agent under these contracts produces
mergeable stories at tolerable cost, (2) intake produces a PRD an engineer
approves, (3) fresh-context cross-family review catches defects a single
session misses. Intake (highest product risk) is pulled forward, not
scheduled fourth. "Freeze before execution" contradicted schema-version-on-
every-event; v0 resolves that.

## OC-13 — v1 cut list — CLOSED

**Decision (Randy, 2026-11-14): adopt the cuts.** The full vision stays the
north star; v1 is the minimum that proves the thesis. CUT from v1:
- GitHub Actions cloud adapter (local-first reaches the demo; removes
  SEC-2/SEC-3/MRG-8 from v1).
- Merge modes 2 & 3 and Level 3 (no data to earn them; mode 1 only).
- Claim leases (one operator + job timeouts suffice; MRG-7).
- Team & org scope (no isolation inside one vault; SEC-7) — person scope
  only, one state repo per trust boundary.
- State-vault mining (stored injection across projects; SEC-6; nothing to
  mine yet).
- Multi-repo stories (breaks the per-story mutex; MRG-8; demo is one repo).
- Flag registry & lifecycle (a to-do app needs no flags).
- Board lane-per-state + custom fields → issue labels + assignee (same
  visibility, no Projects API limits).
- LIVE & SCREENSHOT wireframe tiers → a local Storybook URL.
- Copilot-review knob & remediation modes (configuration with no user
  asking for it).
- PRD-versioning gate, reduced-assurance mode, regression suite (add when
  the first real case appears).
- Four separate upstream design approvals → one design document, one
  approval (HUM-2 / D2).
- Obsidian renders beyond one status file (injection surface + write
  contention for no demo value).

## OC-14 — Security model given the Free plan — CLOSED

**Decision (Randy, 2026-11-14): controller-writer model.** Security must
NOT depend on branch protection (org is Free; private-repo protection/
rulesets return 403 — verified). Design:
- **Agents never hold a write token to the state repo.** An agent job emits
  results as an artifact or a branch in the PRODUCT repo. A separate
  **controller job** — runs no model output and no product code — validates
  and appends to the state repo. (SEC-1 / B1.)
- **Two identities:** an agent App (push story branches, open PRs) and a
  controller App (post checks, merge). The controller key never appears in
  a job that runs model output or product code. (SEC-2 / B2.)
- Policy config changes only by human-reviewed PR; block force-push on
  state main.
- Single controller writer serialized by one concurrency group also fixes
  the ledger push contention (MRG-1 / A1).
- Paid-plan upgrade vs public-earlier is a SEPARATE, optional decision —
  the controller-writer model works on Free.

## OC-15 — Merge protocol — CLOSED

**Decision (Randy, 2026-11-14): update-before-review + strict up-to-date.**
Replace the merge-tree protocol (MRG-2/MRG-3 / A2/A3):
- Merge main into the story branch BEFORE review; run tests AND the review
  on that branch head (a real commit CI can run on — fixes "nothing tests
  the merged tree").
- Enable "require branches to be up to date before merging"; GitHub refuses
  the merge if main moved; the squash tree equals the reviewed head tree by
  construction.
- CUT the post-merge mismatch auto-revert (no identity was allowed to do
  it; MRG-4 / A4). Keep a post-merge tree comparison as a cheap ALARM, not
  a control. For red main: block dispatches + a prepared revert PR in the
  inbox as a one-click human decision.
- Re-review only when the story's own diff changed or main's delta touches
  the story's manifest; else deterministic gates only (fixes quadratic
  re-review; MRG-5 / A5).
- VERIFY the strict setting + server-side squash equivalence on one real PR
  (rename + line-ending case) before relying on it.

## OC-16 — Baseline / kill criterion — CLOSED

**Decision (Randy, 2026-11-14): control arm + kill criterion.** The first
experiment (the walking skeleton) gets a control arm: build the same 5
to-do stories with a single coding-agent session; compare human-minutes
and escaped defects per story, plus cost. **If the factory does not win on
human-minutes or defects at a cost multiple Randy accepts, STOP and
reconsider** — no amount of contract work rescues a factory that isn't
better than using a coding agent directly (PRD-1 / F1). Add "process
overhead ratio" (non-coder tokens / coder tokens) as a headline metric;
tier the pipeline by risk so small stories skip plan review and use one
reviewer (ECN-1 / C1). Move seeded-defect reviewer calibration to P3
(before routing starts), not P6 (ECN-3 / C3).
## Post-ratification amendments (2026-11-14, EXP-1/2/3)

### OC-14 amendment — public-earlier chosen (Randy, 2026-11-14)

Randy: "We should not be on a free plan… lets just make it public then."
Verified: `agentmerlin8` is the only org and is genuinely Free; the repos
were in the right org. Decision: **`software-factory` is now PUBLIC**
(flipped 2026-11-14, full-history secret scan clean). The org stays Free.
EXP-3 verified public+Free unlocks branch protection (200), rulesets (201),
and the strict up-to-date gate (stale merge refused 405, updated merge
passes). The controller-writer model (OC-14) still stands — agents never
hold state-repo write tokens — but branch protection is now AVAILABLE as
defense-in-depth, not unavailable. Evidence:
`docs/experiments/exp-3-public-gate-2026-11-14.md`.

### OC-15 amendment — original mechanism RESTORED (no controller workaround)

EXP-1 proved the strict setting unavailable on private Free and proposed a
controller-enforced up-to-dateness check. EXP-3 (public repo) made that
workaround unnecessary: the native "require branches to be up to date"
gate works. **OC-15 stands as originally ratified** — enable the branch
setting; no controller-side staleness enforcement needed. Two configuration
facts for SKEL-4 (from EXP-3):
- `strict: true` with an EMPTY required-checks list is a no-op — a real
  required status check must be registered or stale merges pass through.
- `enforce_admins: true` blocks direct pushes to main (GH006); factory
  merges go through PRs, so this is fine, but scaffolding must know it.
The controller-enforced amendment proposed after EXP-1 is WITHDRAWN.
