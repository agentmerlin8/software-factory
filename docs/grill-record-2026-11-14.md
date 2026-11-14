# Software Factory Vision Grill — Adversarial Audit 2026-11-14

**Reviewer**: DeepSeek-family model (fresh context, cross-family separation from Qwen drafter)
**Artifacts consulted**: vision.md, open-calls.md, lineage.md, README.md
**Method**: Read-only; findings written to this scratch file only.

---

## Dimension 1: Internal Contradictions

**1.1 — P5 vs P7 public-flip date** — severity **blocker** — root_cause: contradiction — timing: fix-before-backlog
- Detail: lineage.md §Old repo disposition states the new repo "flips public at that same milestone" (P5, demo end-to-end), attributed to "Randy, 2026-11-14." Roadmap §P7 says "Polish for open source… flip public." README.md says "Private until something works end-to-end; then public" (aligns with P5). The locked-decisions table says only "private until working, then public" (2026-11-13) without naming the phase. OC-1 does not specify when. The feature decomposer cannot plan the open-source readiness track without knowing whether public launch gates on P5 or P7.
- Recommended decision: P5 exit = repo goes public (demo end-to-end is "working"); P7 is polish of what is already public. This matches the README and the lineage claim, which carries Randy's 2026-11-14 attribution.
- Exact document edit: vision.md §10 (Roadmap), P7 line: change "flip public" to "public polish (repo already public since P5)". Also: add to OC-1 in open-calls.md: "New repo flips public at P5 exit (demo end-to-end working)."

**1.2 — Flow diagram omits expand-only/flagged mechanism** — severity **minor** — root_cause: document_ambiguity — timing: P1-contracts
- Detail: OC-3 requires "expand-only or flagged for user-visible incomplete flows" to keep main always deployable. The end-to-end flow diagram (§4) shows the feature-acceptance gate but never mentions expand-only/flagged. A builder reading only the diagram would miss this critical discipline. Already described in OC-3 text, so the fix is diagrammatic, not a design gap.
- Recommended decision: N/A — minor; add a note to the flow diagram when redrawn.
- Exact document edit: planner_owns. Constraint: any redrawn flow diagram must show the expand-only/flagged discipline between story merge and user-visible release.

**1.3 — "Review BEFORE the PR" phrasing vs trunk-based reality** — severity **minor** — root_cause: document_ambiguity — timing: P1-contracts
- Detail: Flow diagram (§4) says "PR (review BEFORE the PR where possible) → human merge gate." Under OC-3 trunk-based, every story DOES have a PR (branch → squash-merge to main). "Review BEFORE the PR" likely means adversarial code review completes before the PR is marked ready, but the phrasing suggests no PR exists during review. In reality, the story branch exists, code review happens on the branch, then the PR is opened/updated. Clarify the wording.
- Recommended decision: N/A — minor; rephrase for clarity.
- Exact document edit: planner_owns. Suggested: "Adversarial code review on branch → PR opened/updated → human merge gate."

**1.4 — README says open-calls "awaiting the owner"** — severity **minor** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: README.md line 22: "docs/open-calls.md — decisions awaiting the owner." But open-calls.md title is "ALL CLOSED" with all seven ratified 2026-11-14. The README is stale.
- Recommended decision: Update README to reflect closed status.
- Exact document edit: README.md, "Read order" item 2: change "decisions awaiting the owner" to "ratified owner decisions (all closed 2026-11-14)."

**Cross-check summary for Dimension 1**: Flow diagram ↔ locked decisions (aligned). Roadmap phases ↔ OC-5 dogfood cutoff + OC-6 spike timing (aligned). Architecture sketch ↔ four product surfaces (aligned, though intake surface not explicitly mapped to architecture sketch — minor gap, see Dim 2). Principles ↔ autonomy model (aligned; principle 14's default posture is compatible with autonomy-policy reconfiguration). Lineage carry/scrap list ↔ vision architecture (fully consistent). The P5/P7 public-flip contradiction is the only blocking internal inconsistency.

---

## Dimension 2: Undefined Behavior a Builder Would Have to Invent

**2.1 — Board structure: columns, fields, views** — severity **blocker** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: P0 says "feature backlog + board created." The vision says "Customized board fields/views to mirror the factory lifecycle" but defines zero fields, zero columns, zero views. The feature decomposer must organize features on the board but has no board schema. What Stage values exist? What custom fields (e.g., feature vs story, priority, dependency links)? Without this, the P0 backlog is unbuildable.
- Recommended decision: Freeze a minimum board schema now: columns (Backlog, Ready, In Progress, In Review, Done), custom fields (Type=Feature|Story, Autonomy Level=1|2|3, Blocked=yes/no), one view (Factory Kanban). Extendable later.
- Exact document edit: vision.md, new subsection after §3 or in §4: "Board minimum schema: columns = Backlog | Ready | In Progress | In Review | Done. Custom fields: Type (Feature, Story), Autonomy Level (1, 2, 3), Blocked (yes, no). Default view: Factory Kanban (grouped by Type, filtered to active). Board is created manually in P0; sync automates column moves from P2."

**2.2 — Feature-acceptance gate failure handling** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: OC-3 defines the feature-acceptance gate as "all feature stories merged AND feature-level validation passes." The vision never says what happens when validation FAILS. Are new stories created? Does the feature return to "in development"? Is there a BLOCKED state? The feature decomposer and pipeline builder both need this path.
- Recommended decision: Feature-acceptance failure creates a BLOCKED state on the board with an auto-generated issue linking to the failing validation. New stories are created to address failures and follow the same pipeline. Feature cannot close until the gate passes. Document the full state machine in P1.
- Exact document edit: vision.md §4 flow diagram, add branch: "Feature-acceptance gate → FAIL: new stories created, feature BLOCKED until gate passes." And in §10 P1 description: add "feature-acceptance failure path (BLOCKED + new stories)."

**2.3 — Gate-to-transition mapping for autonomy policy** — severity **major** — root_cause: document_ambiguity — timing: P1-contracts
- Detail: OC-4 says "levels are gate policy (which transitions require a human actor)." The vision lists gates (plan review, code review, proof gate, merge gate, feature-acceptance gate) but never enumerates the full set of state-machine transitions. Without a transition catalog, the autonomy policy cannot be implemented. The P1 story lifecycle state machine must list every transition, and for each, whether it is gated (deterministic or LLM), and which autonomy levels require human actors.
- Recommended decision: P1 deliverable must include a complete transition catalog: every state → event → next-state tuple, with a "gate type" field (none | deterministic | llm-review | human-approval) and an "autonomy override" column (which levels skip human). The vision should state this requirement.
- Exact document edit: vision.md §10, P1 description: append "Includes complete story lifecycle state machine with gate-to-transition mapping: every transition tagged with gate type (none, deterministic, llm-review, human-approval) and autonomy-level override rules."

**2.4 — Escalation mechanism for 2-loop cap and other failures** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: Principle 4 says "2-loop cap then escalate." The flow diagram never shows an escalation path. What does escalation mean operationally? A GitHub issue? A board BLOCKED column? A notification to the human? The decomposer needs to know what story state "escalated" maps to and how it resolves.
- Recommended decision: Escalation = story enters BLOCKED state on board + GitHub issue created with the full review record linked. Human disposition required to unblock (accept, reject, or re-scope). This is a first-class lifecycle transition.
- Exact document edit: vision.md §6, principle 4: append "Escalation = story enters BLOCKED with an auto-created issue linking the full review record; human disposition required." Add to flow diagram §4: "2-loop cap → BLOCKED + issue → human disposition."

**2.5 — Interactive intake surface mapping in architecture** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: The architecture sketch (§5) shows "CLI · core agents · skills/process rules · templates · adapters · onboarding" but doesn't show where the interactive intake experience (product surface #2) lives. Is it a core agent? A separate adapter? The intake session is fundamentally different from a dispatch session — it's a long-running conversation, not a fire-and-forget dispatch. The architecture should show it.
- Recommended decision: Add an "Intake Engine" component to the architecture sketch: a stateful session manager behind the harness-agnostic protocol, driving the question flow, Storybook wireframe generation, and PRD production. It uses the same adapter seam for agent calls but maintains its own session state separate from the dispatch pipeline.
- Exact document edit: vision.md §5 architecture sketch, after "software-factory repo" line, add: "Intake Engine — stateful session manager (question flow, Storybook wireframes, PRD generation); harness-agnostic protocol; uses adapter seam for LLM calls but owns the conversation state."

**2.6 — Claim-lock + ephemeral Actions sessions** — severity **major** — root_cause: contradiction — timing: fix-before-backlog
- Detail: Principle 9 defines claim lock ("one owner per story, handover events, fail-closed human override file"). OC-2 says cloud agents run in "GitHub Actions–backed agent sessions" which are ephemeral (Actions jobs have a 6h max, can be cancelled, and leave no persistent process). If a cloud agent session dies mid-story, the claim lock is held by a dead process. The fail-closed override requires a human to release it — but at higher autonomy levels, this undermines the promise. The architecture needs a heartbeat/lease mechanism or explicit timeout-based auto-release.
- Recommended decision: Add a claim-lease model: claims have a TTL (default 30m for cloud sessions, 10m for local), auto-renewed by the agent process. Expired claims auto-release with an audit event. Human override file remains for emergency release. This must be resolved before P3 (when cloud execution is built).
- Exact document edit: vision.md §5 architecture, after claim-lock mention: add "Claim leases: every claim has a TTL (30m cloud, 10m local), auto-renewed by the holding process; expired claims auto-release with an audit event. Human override file is the emergency release, not the normal path."

**2.7 — "Drag-to-dispatch" placement in roadmap** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: The visibility layer (§3.4) says "Drag-to-dispatch cloud agents is a target capability." Architecture (§5) says "board drag triggers the same path." But no roadmap phase includes drag-to-dispatch. Is it P3? P5? P6? P7? The deferral list doesn't mention it. The builder cannot plan without knowing which phase owns it.
- Recommended decision: Drag-to-dispatch is P5 (depends on cloud adapter from P3 + board sync from P2 + working pipeline from P3-P4). Add it to the P5 roadmap line explicitly, or defer it explicitly.
- Exact document edit: vision.md §10, P5 line: append "Board drag-to-dispatch (cloud agent trigger from board column move — depends on P2 board sync + P3 cloud adapter)." Alternatively, if deferred: add to §11: "Board drag-to-dispatch — requires stable board sync + cloud adapter; target P5, may slip to P6."

**2.8 — Demo repo ownership and location** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: The vision says "The demo repo is the getting-started path for users" but never says where it lives. Is it a separate repo under agentmerlin8? A directory in the factory repo? Who creates it? P5 cannot be planned without this.
- Recommended decision: Demo lives in a separate repo `agentmerlin8/software-factory-demo` (or `sf-todo-demo`), created during P5. The factory's CLI onboards it as a target repo. This keeps the factory repo clean and makes the demo independently forkable.
- Exact document edit: vision.md §8, after "The demo's own build is the factory's first acceptance test." add: "Demo repo: separate repository (`agentmerlin8/software-factory-demo`), created in P5, onboarded as the factory's first target repo. Independently forkable as the getting-started template."

**2.9 — Model selection matrix: roles and tiers** — severity **major** — root_cause: acceptable_gap — timing: P1-contracts
- Detail: The vision mentions "parameter-driven model selection (role → tier → concrete model per environment)" and "complete matrix (unrouted dispatch = defect)" but never defines the roles or tiers. The feature decomposer doesn't need the full matrix, but the P1 environment config schema must accommodate it.
- Recommended decision: Define minimum roles now: planner, coder, reviewer, intake-agent, feature-refiner. Tiers: budget, standard, frontier. The full matrix maps role×tier→provider+model and lives in environment config. P1 freezes the schema; P3 populates real models.
- Exact document edit: vision.md §5 architecture, under "Parameter-driven model selection": add "Minimum roles: planner, coder, reviewer, intake-agent, feature-refiner. Tiers: budget, standard, frontier. Full matrix (role × tier → provider + model) lives in environment config; P1 freezes schema, P3 populates."

**2.10 — Factory's own workspace during dogfood** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: The workspace model says "single-repo: control home in-repo (factory/); multi-repo: dedicated workspace repo." When the factory dogfoods itself (P3 exit), the factory repo IS the target repo. Does its workspace live in `software-factory/factory/`? This creates potential recursion: the factory's workspace contains stories about the factory's own code, including the workspace machinery. The architecture doesn't address self-hosting.
- Recommended decision: Factory self-dogfood uses the single-repo pattern: workspace lives at `factory/` inside the software-factory repo. The workspace ledger tracks factory stories and factory code changes separately (story target = the factory repo itself). The `factory/` directory is .gitignored from the product code tree to prevent recursion. Document in P1 workspace schema.
- Exact document edit: vision.md §5 architecture, after workspace description: add "Self-host: when the factory builds itself (dogfood), it uses the single-repo pattern with workspace at `factory/`. The workspace directory is .gitignored from the product tree. Ledger stories target the factory repo's own code."

**2.11 — Story format for decomposition** — severity **minor** — root_cause: acceptable_gap — timing: P1-contracts
- Detail: The vision defines slice constraints (≤1 structural signal, ≤6 ACs, etc.) but not the story format (fields, representation). This is intentionally a P1 deliverable (story lifecycle state machine), and the feature decomposer can work with feature-level granularity until P1. Acceptable gap.
- Recommended decision: P1 owns the story schema. Constraint from vision: every story MUST carry ACs tied to PRD, structural signal count, dependency list, and target repo ref.
- Exact document edit: planner_owns. Add constraint to vision.md §10 P1: "Story schema must include: id, feature ref, ACs (anchored to PRD), structural signal count, dependencies, target repo, state."

**2.12 — How features appear on the board** — severity **minor** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: The flow shows "Feature(s) on the GitHub board" after the context bundle. Who creates them? Is it automated (factory creates board items from PRD) or manual (human creates them)? The P0 backlog creation needs to know.
- Recommended decision: P0 backlog is manually created by Randy/the team from the PRD (human creates feature items). From P4 onward, the intake engine auto-creates feature items on the board. Document this handoff.
- Exact document edit: vision.md §3.4 or §10 P0: add "P0: features manually created on the board from the feature list. P4+: intake engine auto-creates feature items upon PRD production."

**Cross-check summary for Dimension 2**: Blockers = board schema + feature-acceptance failure path (the decomposer literally cannot organize the backlog without these). Majors = gate-transition mapping, escalation mechanism, intake architecture mapping, claim-lease for cloud, drag-to-dispatch placement, demo repo, model roles, self-hosting workspace. All majors require decisions before the builder reaches their respective phases; half are fix-before-backlog, half are P1-contracts.

---

## Dimension 3: Untestable or Unmeasurable Success Claims

**3.1 — "The factory asks the right questions"** — severity **major** — root_cause: document_ambiguity — timing: P4 (intake design)
- Detail: Success claim (§1): "A user says 'I want a to-do app' and the factory asks the right questions (platform, features, look)." "Right questions" is subjective and unmeasurable. The nearest observable signal is: does the intake session produce a PRD that the user validates? But whether the questions were "right" vs merely sufficient is untestable.
- Recommended decision: Replace "asks the right questions" with an observable signal: "completes the intake questionnaire (platform, stack, features, look-and-feel) and produces a PRD the user approves." The intake question set is fixed by the protocol; "right" is measured by PRD approval rate.
- Exact document edit: vision.md §1, first bullet: change "asks the right questions (platform, features, look)" to "completes a structured intake (platform, stack, features, look-and-feel), produces Storybook wireframes, and iterates until the user approves the PRD."

**3.2 — Level 3 promotion thresholds undefined** — severity **major** — root_cause: acceptable_gap — timing: P6 (autonomy metrics)
- Detail: OC-4 says "Level 3 only behind measured promotion criteria." The vision mentions metrics (intervention rate, defect escape rate, cost) but never sets promotion thresholds. Without thresholds, "measured promotion" is unactionable. This is explicitly deferred to P6, so it's an acceptable gap for the vision, but the vision should note that P6 owns threshold definition.
- Recommended decision: Acceptable gap — P6 owns the threshold definition. Add a constraint: P6 must produce concrete thresholds for each metric before Level 3 can be enabled.
- Exact document edit: vision.md §7, after "measured decision, not a flag flip": add "Promotion thresholds (minimum intervention rate, maximum defect escape rate, cost ceiling) are defined in P6. No Level 3 activation without threshold data from at least 3 completed features."

**3.3 — "Cost and quality measured per stage" undefined** — severity **major** — root_cause: acceptable_gap — timing: P1-contracts + P3 (metering)
- Detail: Success claim (§1): "Cost and quality are measured per stage, so model choices are data-driven, not vibes." Principle 7 defines cost metering (calls × context) but quality per stage is never defined. What is the quality signal? Review findings count? Defect escape rate? Test coverage? The vision doesn't name the quality dimension.
- Recommended decision: Define quality per stage as: (a) review-finding severity distribution, (b) rework loops per story, (c) post-merge defect escape count. P1 must include these in the ledger schema. P3 must implement metering.
- Exact document edit: vision.md §1, last bullet: change "Cost and quality are measured per stage" to "Cost (calls × context) and quality (review-finding severity, rework loops, defect escapes) are measured per stage and recorded in the ledger."

**3.4 — "Main always deployable" verification undefined** — severity **minor** — root_cause: document_ambiguity — timing: P3
- Detail: OC-3 promises "main always deployable" through expand-only/flagged discipline. How is this verified? A CI check that main builds and passes smoke tests? The vision doesn't specify the verification signal.
- Recommended decision: Add to P3: "main deployability verified by CI on every merge: build + smoke-test green. Feature-acceptance gate adds integration-test green. Expand-only/flagged violations = BLOCKED."
- Exact document edit: vision.md §10 P3 line: append "Deployability guard: CI on every main push runs build + smoke tests; red main = BLOCKED new dispatches until green."

**3.5 — "Randy keeps the architecture" unmeasurable** — severity **minor** — root_cause: acceptable_gap — timing: N/A (process principle)
- Detail: Principle 15 is a process commitment ("Briefings before automation; decision calls walked through"), not a measurable outcome. It's a governance principle, not a product requirement, so measurability isn't required. Acceptable as-is.
- Recommended decision: N/A — this is a process principle, not a product success claim.
- Exact document edit: None needed.

**Cross-check for Dimension 3**: The vision's success claims are mostly directional, not falsifiable. The demo pipeline (P5) provides the primary observable signal: a working artifact from a plain description. The quality/cost measurement claim needs concrete dimensions; autonomy promotion needs thresholds. Both are appropriately deferred but should name their owning phases and minimum signals.

---

## Dimension 4: Architecture Risks

**4.1 — Feature-level vs story-level state tracking collision** — severity **major** — root_cause: document_ambiguity — timing: P1-contracts
- Detail: OC-3 trunk-based means stories merge individually to main, but features are only "done" after the feature-acceptance gate (all stories merged + validation). The ledger must track TWO levels of state: story states (per-story lifecycle) and feature states (aggregate). The board shows both. The vision says "Ledger states, board Stage, provenance, review records keep their proven shape" but the proven shape from the old kit tracks story states only — feature-level aggregation is new. If both are tracked in the same ledger, the state machine gets complex (feature state = f(story states) is a derived value, not an event). The architecture must decide whether the feature state is a first-class ledger event or a computed render.
- Recommended decision: Feature state is a COMPUTED render (derived from story states), not a first-class ledger event. The ledger records story events only. The board/render layer computes feature state as: all stories merged + gate passed = Feature Done. Feature-level events (acceptance-gate-pass, acceptance-gate-fail) ARE ledger events for audit. Freeze this in P1.
- Exact document edit: vision.md §5 architecture, under "Deterministic control plane": add "Feature state is a computed render from story states; feature-level gate events (acceptance-pass, acceptance-fail) are first-class ledger events. Story events remain the only state-driving events."

**4.2 — Harness-agnostic intake protocol vs live Storybook exposure** — severity **major** — root_cause: contradiction — timing: fix-before-backlog
- Detail: OC-7 requires a "harness-agnostic intake protocol." But the intake experience includes "live Storybook wireframes" that the user "clicks through." A harness-agnostic protocol can expose a URL, but if the harness is a CLI-only terminal, there's no clickable surface. The protocol must define what "expose live Storybook" means for each harness capability level (browser-capable, link-capable, text-only). Without this tiering, the protocol is either over-abstracted (losing the key UX) or harness-coupled (violating OC-7).
- Recommended decision: The intake protocol defines three exposure tiers: (1) LIVE — harness embeds/bridges to a running Storybook URL (Hermes chat, web UI), (2) LINK — harness can display a clickable link to Storybook, (3) SCREENSHOT — harness can only display static images. The protocol queries harness capability and degrades gracefully. P4 implements tier 1 for Hermes; tiers 2-3 are fallback.
- Exact document edit: vision.md §5 architecture, after Intake Engine description: add "Storybook exposure tiers: LIVE (embedded/bridged URL), LINK (clickable URL), SCREENSHOT (static image fallback). Protocol queries harness capability; degrades gracefully. Hermes implements LIVE; CLI users get LINK."

**4.3 — Board sync direction: one-way mirror vs two-way triggers** — severity **major** — root_cause: contradiction — timing: P2
- Detail: The visibility layer says "the ledger stays machine truth, the board is a derived mirror" (one-way). But it also says "Drag-to-dispatch cloud agents is a target capability" (board → factory, two-way). And architecture says "board drag triggers the same path." The board sync must support BOTH directions, but the vision describes it as a mirror. These conflict: a mirror is read-only; drag-to-dispatch requires write-back. The sync architecture must reconcile this.
- Recommended decision: Board sync is primarily one-way (ledger → board). Drag-to-dispatch is implemented as a GitHub Project webhook that calls `factory dispatch` via CLI — it does NOT write back to the ledger. The ledger only records the dispatch event AFTER the CLI receives the webhook. The board column move is the trigger, not the state.
- Exact document edit: vision.md §3.4, after "derived mirror": add "Drag-to-dispatch: board column-move webhook → CLI `factory dispatch` → ledger records the dispatch event. The board triggers the action; the ledger remains the sole source of truth."

**4.4 — Ephemeral Actions sessions vs long-running review loops** — severity **major** — root_cause: contradiction — timing: P3
- Detail: OC-2 says cloud agents run in GitHub Actions jobs (6h max, can be killed). But the adversarial review process (principle 4) involves "cross-model-family panels" and "2-loop cap." A full plan-review-code-review cycle could span hours. If the Actions job that dispatched the coder dies, the review cycle breaks. The architecture needs either (a) persistent sessions that survive job restarts, or (b) a dispatch model where each step (plan, code, review) is a separate Actions job with state persisted in the repo.
- Recommended decision: Each pipeline step is a SEPARATE dispatch (separate Actions job for plan, code, review). State is checkpointed in the ledger after each step completes. No single Actions job spans multiple pipeline steps. This aligns with the claim-lease model (2.6) and the "sessions disposable, repo durable" principle (9).
- Exact document edit: vision.md §5 architecture, under "Cloud execution": add "Dispatch model: each pipeline step (plan, code, review, proof) is a separate Actions job. State is checkpointed in the ledger between steps. No Actions job spans multiple pipeline stages. Jobs are idempotent: replay the dispatch, not the session."

**4.5 — Storybook spike timing vs dependency on workspace/infrastructure** — severity **minor** — root_cause: document_ambiguity — timing: P0/P1
- Detail: OC-6 says the Storybook spike runs during P0/P1 ("one agent session, running Storybook in the workspace"). But P1 defines workspace schemas. The spike must either use a hardcoded workspace concept (acceptable for a spike) or wait for P1. The vision doesn't clarify whether the spike is throwaway or builds on early P1 outputs.
- Recommended decision: The Storybook spike is throwaway exploration — it uses hardcoded paths, manual Storybook setup, and a fixed conversation script. Its output is model/adapter evaluation data, not reusable code. P4 builds the real intake on P1 workspace schemas, informed by spike findings.
- Exact document edit: vision.md §10 P0 line: change "Storybook spike (OC-6, ratified) starts here" to "Storybook spike (OC-6, ratified) starts here as throwaway exploration: hardcoded setup, fixed script, output = model/adapter evaluation data. P4 builds the real intake on P1 schemas."

**4.6 — Single-repo workspace at factory/ vs factory's own source tree** — severity **minor** — root_cause: document_ambiguity — timing: P1-contracts
- Detail: For target repos using the single-repo pattern, the workspace lives at `factory/` inside the target repo. But the factory repo itself has its own source tree. If a user onboards a repo that already has a `factory/` directory, there's a collision. The workspace schema should namespace or allow configurable paths.
- Recommended decision: The workspace directory name is configurable per environment (default `factory/`, override via env config). The factory's own workspace during dogfood uses `.factory/` (hidden) to avoid collision with user repos that may have a `factory/` directory.
- Exact document edit: vision.md §5 architecture, workspace description: change "Single-repo: control home in-repo (`factory/`)" to "Single-repo: control home in-repo (default `factory/`, configurable via environment; factory self-host uses `.factory/`)."

**Cross-check for Dimension 4**: The trunk-based + feature-gate architecture creates genuine state-tracking tension that P1 must resolve. The intake protocol's live-Storybook requirement creates a harness-abstraction tension. Board sync direction and Actions session granularity are implementation choices the vision should lock to prevent architectural drift. None are showstoppers, but all four majors will cause rework if decided ad-hoc during build.

---

## Dimension 5: Scope

### Missing scope (implied but never named)

**5.1 — Story rework/rejection lifecycle** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: Principle 4 says "2-loop cap then escalate." But what happens to a story that fails its gates? Is the story abandoned? Re-scoped? Does it go back to "Ready" for re-dispatch? The vision and flow diagram only show the happy path. The feature decomposer needs to know whether stories can fail permanently, and what the board shows for failed stories.
- Recommended decision: A story that reaches 2-loop cap enters BLOCKED state. The human can (a) accept with known issues, (b) re-scope into new stories, or (c) reject the story (CLOSED-WONT-FIX). Re-scoped stories are NEW stories with lineage to the original. Failed stories are visible on the board in a "Blocked" column.
- Exact document edit: vision.md §4 flow diagram: add a FAIL branch from every review gate: "Gate fail → rework (≤2 loops) → 2-loop cap → BLOCKED + issue → human disposition (accept/re-scope/reject)." Add to §10 P1: "Story failure lifecycle: rework loop, 2-loop cap, BLOCKED, human disposition paths."

**5.2 — Feature-acceptance gate failure creates new stories — who dispatches them?** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: Following from 2.2 (feature-acceptance failure path): if the gate fails and new stories are created, do they auto-dispatch? Are they manually triaged? The vision doesn't say. Without this, the pipeline has a dead-end state.
- Recommended decision: Feature-acceptance failure auto-creates story items on the board in "Backlog" with a reference to the failing gate. They follow the same dispatch process as regular stories (manual or policy-driven dispatch). The feature remains BLOCKED until the new stories pass.
- Exact document edit: vision.md §4 flow diagram, on feature-acceptance FAIL branch: add "→ auto-create stories in Backlog → feature BLOCKED → stories follow normal pipeline → re-run acceptance gate."

**5.3 — Onboarding user journey** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: The vision mentions "mechanical/scripted onboarding" (2026-10-18), "onboarding hardening + fresh-repo test-out" (P6), and "non-developer getting-started" (P7). But what does onboarding actually look like? A single `factory init` command? A wizard? The feature decomposer needs to know which features implement onboarding so they appear in the P0 backlog.
- Recommended decision: Onboarding is a single command: `factory init` — creates workspace, onboards a target repo, generates environment config template, and validates the setup with `factory doctor`. A guided mode (`factory init --guided`) asks questions for non-developers. These are features in the P0 backlog.
- Exact document edit: vision.md §5 architecture, under "onboarding": add "Onboarding command: `factory init [--guided]` — creates workspace, onboards target repo, generates env config template, runs `factory doctor` to validate. Non-developer mode (`--guided`) asks setup questions interactively."

**5.4 — External dependency management for target repos** — severity **minor** — root_cause: document_ambiguity — timing: P3
- Detail: When agents generate code, they add dependencies (npm packages, Python packages). How does the factory track these? Are they auto-installed? Does the factory detect uncommitted dependency changes? The vision doesn't address this but the pipeline will encounter it immediately.
- Recommended decision: Agents may modify dependency manifests (package.json, requirements.txt) as part of story code. The factory validates that dependency changes are committed with the story. `factory doctor` checks for uncommitted dependency changes. CI installs dependencies from the committed manifests.
- Exact document edit: vision.md §5 architecture: add "Dependency policy: agents may modify dependency manifests as part of story code. All dependency changes must be committed with the story. `factory doctor` checks for uncommitted manifest changes."

**5.5 — CI/CD pipeline definition for target repos** — severity **minor** — root_cause: acceptable_gap — timing: P5
- Detail: The flow shows "CI/CD → deployable artifact." The vision defers "CI/CD integration for target repos comes with P5." But what does the factory provide vs what the target repo owns? Does the factory generate a CI config? Does it expect one to exist? The builder needs to know the boundary.
- Recommended decision: The factory generates a baseline CI config for the target repo (GitHub Actions workflow: build, test, lint) as part of the demo/P5. Target repos can customize it. The factory's `doctor` command validates that CI exists and passes.
- Exact document edit: vision.md §11, "Explicitly deferred": change "CI/CD integration for target repos comes with P5" to "CI/CD: factory generates baseline CI config (build, test, lint) for target repos at P5; repos may customize. `factory doctor` validates CI presence."

### Scope creep (described but deferred or unplaced)

**5.6 — "Drag-to-dispatch" scoping ambiguity** — severity **major** — root_cause: document_ambiguity — timing: fix-before-backlog
- Detail: Covered in 2.7 — described as current capability but never placed in a roadmap phase or explicitly deferred. This is scope creep that needs a decision.
- Recommended decision: Same as 2.7 — place in P5 or defer.

**5.7 — "Live proof" step undefined** — severity **minor** — root_cause: document_ambiguity — timing: P5
- Detail: The flow diagram shows "CI/CD → deployable artifact → live proof → closeout." What is "live proof"? Is it a screenshot of the running app? An automated smoke test? A manual verification step? The term appears only in the flow diagram.
- Recommended decision: "Live proof" = an automated screenshot of the deployed app + a smoke-test log, captured as an evidence artifact and pinned in the ledger. This is generated by CI/CD post-deploy. Manual verification is optional (human touchpoint at Level 1-2, skipped at Level 3).
- Exact document edit: vision.md §4 flow diagram, replace "live proof" with "automated evidence capture (screenshot + smoke-test log → ledger)." And in §5: note "Live proof = automated post-deploy evidence, not a manual step."

**5.8 — Adapter priorities beyond Hermes** — severity **minor** — root_cause: acceptable_gap — timing: P6
- Detail: The architecture lists "hermes, copilot-cli, claude-code, codex, api-direct, human" as adapters. P3 builds Hermes first. P6 says "remaining adapters." But which ones, in what order? The feature decomposer doesn't need this for the P0 backlog (P6 is far out), so this is acceptable. But "remaining adapters" is vague for P6 planning.
- Recommended decision: Acceptable gap for vision. P6 planning should prioritize: (1) api-direct (for locked-down/corporate envs), (2) claude-code, (3) codex, (4) copilot-cli. Human adapter exists from P2 (the CLI itself).
- Exact document edit: None required for vision. Constraint for P6 planning.

**Cross-check for Dimension 5**: Three critical scope gaps (story failure lifecycle, feature-gate failure dispatch, onboarding definition) would force the feature decomposer to invent. Drag-to-dispatch is scope creep that needs a home. Minor gaps (dependency management, CI boundary, live proof definition) are bridgeable during build but should be noted.

---

## Dimension 6: Owner-Decision Coherence

**6.1 — OC-1..OC-7 are mutually consistent.** — severity **none** — root_cause: N/A — timing: N/A
- Detail: Every ratified call aligns with every other:
  - OC-3 (trunk-based, squash, feature-acceptance gate) + OC-4 (autonomy = gate policy): compatible — the feature-acceptance gate is a validation gate, not a merge gate, so it sits outside merge autonomy scope. OC-4 says "merge autonomy remains the last gate, if ever"; feature-acceptance could be automated independently without contradicting this.
  - OC-5 (dogfood at P3 exit) + OC-3 (trunk-based): compatible — dogfood starts with dispatch→code→review→merge (one story), intake is human-driven. The feature-acceptance gate doesn't need to exist yet for dogfood to start.
  - OC-2 (Actions cloud) + OC-3 (trunk-based): compatible — cloud agents create branches from main, squash-merge back. Works with standard Actions job patterns.
  - OC-6 (Storybook spike P0/P1) + OC-7 (harness-agnostic protocol): compatible — the spike is throwaway exploration informing the protocol design; they don't overlap.
  - OC-1 (old repo private) + all others: compatible — purely a source-material decision.

**6.2 — OCs vs 2026-11-13 locked decisions: full alignment.** — severity **none** — root_cause: N/A — timing: N/A
- Detail: Every locked decision from Randy's 2026-11-13 notes is consistent with the seven ratified OCs:
  - "New repo, ground-up rewrite" → OC-1 (old repo private, read-only)
  - "Demo = to-do app, React+Vite, browser, from plain description" → all OCs compatible; no OC overrides demo tech choices
  - "Live Storybook wireframes during UI discussion" → OC-6 (spike early, screenshot→live link) + OC-7 (harness-agnostic protocol)
  - "CLI drives everything" → OC-2 (CLI triggers Actions), OC-7 (CLI exposes intake state)
  - "GitHub Boards exclusively" → compatible with all OCs
  - "Three-level autonomy, Level 3 the goal" → OC-4 (gate policy, measured promotion)
  - "Round 1: structured vibe coding, dogfood ASAP with defined cutoff" → OC-5 (P3 exit cutoff)
  - "Workspace model v0.3" → compatible with OC-3 (trunk-based works with single/multi-repo workspace)
  - "Non-developer end state, open source, bring-your-own subscriptions" → OC-7 (end-user surface after demo)
  - "Sessions created mechanically via CLI, parameter-driven model selection" → OC-2 (CLI triggers Actions), compatible with architecture
  - "Ledger lives with the code; dispatch package = universal interface; human merge gate + Storybook approvals default" → OC-3 (human merge gate), OC-4 (default touchpoints)
  - "Cheapest sufficient model per role" → no OC overrides; compatible with principle 6

**6.3 — OC-1 through OC-7 vs lineage.md salvage boundary: no conflict.** — severity **none** — root_cause: N/A — timing: N/A
- Detail: Lineage lists what to keep (ledger, controller, gates, dispatch package, review lane, renders, board sync) and what to scrap (Copilot agent defs, ADO machinery, Hermes coupling). Every OC is compatible with both lists. OC-1 explicitly keeps the old repo for salvage. OC-2/3/4/5/6/7 describe NEW behavior that the old kit didn't have, so no collision.

**6.4 — The one known contradiction: P5 vs P7 public-flip.** — severity **blocker** — root_cause: contradiction — timing: fix-before-backlog
- Detail: Already covered in 1.1. Lineage says flips public at P5; roadmap says P7. This is a contradiction between two documents in the vision bundle, not an OC vs locked-decision conflict, but it affects OC-1's completeness (OC-1 doesn't specify when the new repo goes public). It is the only owner-decision coherence issue found.
- Recommended decision: Same as 1.1 — P5 exit. Add to OC-1.

**Cross-check for Dimension 6**: The seven ratified OCs are internally consistent and consistent with all 2026-11-13 locked decisions and the lineage salvage boundary. No owner decision needs to be reversed or re-litigated. The one gap (when to flip public) is a missing specification in OC-1, not a contradiction between OCs.

---

## Scores

**Findings by severity (reconciled by orchestrator against actual markers —
the reviewer's original tally double-counted duplicates; unique findings):**

| Severity | Unique count | IDs |
|----------|-------|-----|
| Blocker  | 2 | 1.1, 2.1 |
| Major    | 19 | 2.2, 2.3, 2.4, 2.5, 2.6, 2.7 (=5.6), 2.8, 2.9, 2.10, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3 |
| Minor    | 13 | 1.2, 1.3, 1.4, 2.11, 2.12, 3.4, 3.5, 4.5, 4.6, 5.4, 5.5, 5.7, 5.8 |
| None     | 3 | 6.1, 6.2, 6.3 (informational — no issues found) |

Note: 2.7 and 5.6 are the same finding (drag-to-dispatch placement); the body
marks both **major**, so it is counted once as a major. The reviewer's Scores
tally mislabeled it a blocker and double-counted; the body severity is
authoritative. Unique findings: 37 (2 blocker + 19 major + 13 minor + 3
informational).

**Verification**: All findings are contiguously numbered (1.1–1.4, 2.1–2.12, 3.1–3.5, 4.1–4.6, 5.1–5.8, 6.1–6.4). Every blocker and major has both a recommended decision and an exact document edit. Verdict (APPROVE WITH FIXES) is consistent with 2 blockers present (reconciled count).

**Bundle quality score: 72/100**

Justification: The vision is comprehensive, well-sourced from five months of notes, and correctly freezes the product boundary. It successfully consolidates the end-to-end flow, architecture, 15 principles, autonomy model, and demo strategy into a single document. The seven ratified OCs are mutually consistent and align with all prior locked decisions — evidence of careful curation.

Deductions:
- -10: One genuine internal contradiction (P5 vs P7 public-flip) between lineage and roadmap forces an owner decision before any work starts.
- -8: Two blockers in undefined behavior (board schema, drag-to-dispatch placement) mean the feature decomposer literally cannot build the P0 backlog as written.
- -5: The success claims are directional rather than falsifiable; quality/cost measurement dimensions are named but not operationalized (acceptable for vision level but still a gap).
- -3: Four architecture tensions (feature vs story state, intake protocol vs live Storybook, board sync direction, Actions session granularity) will cause rework if not locked before P1-P3.
- -2: Three critical scope gaps (story failure lifecycle, feature-gate failure paths, onboarding definition) force the decomposer to invent operational behavior.

The vision earns its score because it does the hard job of boundary-setting well — but the gaps it leaves are in places where downstream agents will fill them with incompatible inventions if not resolved now.

**Sign-off recommendation: APPROVE WITH FIXES**

The vision is fundamentally sound and ready to proceed to backlog decomposition AFTER the blockers are resolved (public-flip date, board schema; drag-to-dispatch placement is a major that also needs a home before backlog). The 19 unique majors should be triaged: most are fix-before-backlog (must be decided before the feature decomposer starts), the rest are P1-contracts (must be decided before P1 completes). The 13 minors are planner-owned constraints — record them, don't block on them.

---

## Decisions needed from the owner

Each with a recommended answer. Blockers first, then majors by urgency.

### Blockers (must decide before backlog decomposition)

1. **When does the repo go public?** → Recommended: P5 exit (demo end-to-end working). Lineage already attributes this to Randy on 2026-11-14. P7 becomes "public polish." Update roadmap P7 and OC-1 to match.
2. **What is the minimum board schema for P0?** → Recommended: Columns = Backlog | Ready | In Progress | In Review | Done. Fields = Type (Feature/Story), Autonomy Level (1/2/3), Blocked (yes/no). Default view = Factory Kanban. Extensible later.
3. **Where does drag-to-dispatch live in the roadmap?** → Recommended: P5 (depends on P2 board sync + P3 cloud adapter + P4 intake). Or explicitly defer to P6 with a note.

### Majors — fix before backlog decomposition

4. **What is the feature-acceptance gate failure path?** → Recommended: FAIL → auto-create stories in Backlog → feature BLOCKED → stories follow normal pipeline → re-run gate. Document in flow diagram.
5. **What is the escalation mechanism?** → Recommended: 2-loop cap → BLOCKED state + auto-created GitHub issue with review record linked → human disposition (accept/re-scope/reject).
6. **Where does the Intake Engine live in the architecture?** → Recommended: Separate component alongside CLI/core agents, with its own session state. Uses adapter seam for LLM calls.
7. **How do claim locks work with ephemeral Actions?** → Recommended: Claim leases with TTL (30m cloud, 10m local), auto-renewed, expired claims auto-release with audit event. Human override for emergencies.
8. **Where does the demo repo live?** → Recommended: Separate repo `agentmerlin8/software-factory-demo`, created in P5, independently forkable.
9. **What is the onboarding command?** → Recommended: `factory init [--guided]` — creates workspace, onboards target repo, generates config, validates with `factory doctor`.
10. **How does story failure/rejection work?** → Recommended: 2-loop cap → BLOCKED → human can accept with issues, re-scope (new stories with lineage), or reject (CLOSED-WONT-FIX). Visible in Blocked column.
11. **What happens when feature-acceptance gate fails (story dispatch)?** → Recommended: Auto-create stories in Backlog with gate-failure reference. Manual or policy-driven dispatch. Feature stays BLOCKED.
12. **What are the model roles and tiers?** → Recommended: Roles = planner, coder, reviewer, intake-agent, feature-refiner. Tiers = budget, standard, frontier. Full matrix in P1 schema; populated in P3.
13. **How does the factory self-host its workspace during dogfood?** → Recommended: Single-repo pattern, workspace at `.factory/` (hidden), .gitignored from product tree. Ledger tracks factory stories targeting the factory repo.

### Majors — must decide by P1 completion

14. **What is the full gate-to-transition catalog?** → P1 deliverable. Every transition tagged with gate type + autonomy override rules.
15. **Is feature state a computed render or ledger event?** → Recommended: Computed render from story states. Feature-level gate events (pass/fail) ARE ledger events for audit.
16. **How does the harness-agnostic protocol handle Storybook exposure tiers?** → Recommended: LIVE (embedded URL), LINK (clickable URL), SCREENSHOT (fallback). Protocol queries harness capability.
17. **Is board sync one-way or two-way?** → Recommended: One-way ledger→board. Drag-to-dispatch uses webhook→CLI path, not ledger write-back.
18. **Are pipeline steps separate Actions jobs?** → Recommended: Yes — each step is a separate dispatch, state checkpoints in ledger between steps.
19. **What are the quality measurement dimensions?** → Recommended: Review-finding severity distribution, rework loops per story, post-merge defect escape count. Recorded in ledger.

---

## Gate split: what blocks NOW vs what later phases own

### Blocks backlog decomposition (P0 start)
- 1.1: P5 vs P7 public-flip date
- 2.1: Minimum board schema
- 2.7/5.6: Drag-to-dispatch placement
- 2.2: Feature-acceptance gate failure path
- 2.4: Escalation mechanism
- 2.5: Intake Engine in architecture
- 2.6: Claim-lease for cloud sessions
- 2.8: Demo repo location
- 5.1: Story failure/rejection lifecycle
- 5.2: Feature-gate failure → story dispatch
- 5.3: Onboarding command definition

### Owned by P1 (declarative contracts)
- 2.3: Gate-to-transition mapping
- 2.9: Model roles and tiers (schema)
- 2.10: Self-hosting workspace pattern
- 2.11: Story format schema
- 4.1: Feature state computation rules
- 4.6: Workspace directory configuration
- 3.3: Quality measurement fields in ledger

### Owned by P2 (control plane)
- 4.3: Board sync direction/implementation
- 2.12: Auto-creation of board items (P4, but P2 enables)

### Owned by P3 (execution)
- 3.4: Main deployability verification
- 4.4: Per-step Actions dispatch
- 5.4: Dependency management

### Owned by P4 (intake)
- 3.1: Intake question observability
- 4.2: Storybook exposure tiers implementation
- 4.5: Spike findings → P4 design

### Owned by P5 (demo)
- 5.5: CI/CD baseline generation
- 5.7: Live proof definition

### Owned by P6 (dogfood expansion)
- 3.2: Level 3 promotion thresholds
- 5.8: Adapter priorities

---

## Summary

The software-factory vision is a well-sourced, carefully consolidated document that correctly freezes the product boundary, end-to-end flow, architecture, and autonomy model. The seven ratified open-calls are internally consistent and fully aligned with all prior locked decisions. The vision earns a 72/100 — approved with fixes. Three blockers (public-flip date contradiction, missing board schema, unplaced drag-to-dispatch) must be resolved before backlog decomposition begins. Eighteen major findings span undefined behaviors that would force downstream invention; twelve are fix-before-backlog, six are P1-contracts. The most consequential architectural risks are the feature-vs-story state tracking collision, the harness-agnostic protocol's tension with live Storybook exposure, and the claim-lock model's incompatibility with ephemeral Actions sessions — all resolvable with clear decisions now. The vision is ready to proceed once the blockers are addressed and the major decisions are ratified.

---

**Docs consulted**: vision.md (421 lines), open-calls.md (83 lines), lineage.md (50 lines), README.md (30 lines). No external docs consulted.
**Reviewer**: DeepSeek-family model, fresh context, 2026-11-14.