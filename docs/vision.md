# Software Factory — Vision (consolidated 2026-11-14)

Status: Vision APPROVED by grill rounds 1–2; Fable 5.2 external design
review (issue #1) dispositioned; all owner calls OC-1…OC-11 RATIFIED
2026-11-14. **Round-3 feasibility grill returned approve_with_fixes
(48/100); fix pass applied 2026-11-14** (merge-tree integrity protocol,
per-story ledger, cross-repo evidence validation, concrete token boundary,
scope enforcement, concurrency smoke test, no-shell-freeze rule). Round-4
confirmation pending. See
[grill-round3-2026-11-14.md](grill-round3-2026-11-14.md),
[design-review-disposition-2026-11-14.md](design-review-disposition-2026-11-14.md),
[grill-record-2026-11-14.md](grill-record-2026-11-14.md),
[grill-disposition-2026-11-14.md](grill-disposition-2026-11-14.md),
[grill-regrill-round2-2026-11-14.md](grill-regrill-round2-2026-11-14.md).

## 1. Goal

Build software from **idea to deployable artifact autonomously, involving the
human at the right steps** — the human answers what the AI cannot confidently
answer on its own. (Randy, 2026-11-13)

End state: a polished, open-source product for **engineering professionals**
— enabling people like Randy to build software autonomously, with the
architecture kept in human hands (OC-11, ratified 2026-11-14; supersedes the
earlier non-developer-first wording). Users describe the software they want,
answer guided clarification questions, watch the UI take shape as clickable
wireframes, approve the architecture and decomposition, and receive working,
deployed software. Users bring their own model subscriptions; it runs at
home, in a home lab, or in a corporate environment. (2026-10-18, amended by
OC-11)

Success looks like:

- A user says "I want a to-do app" and the factory completes a structured
  intake (platform, stack, features, look-and-feel), shows live Storybook
  wireframes, and iterates until the user approves the PRD. ("Right
  questions" is measured by PRD approval, not judged subjectively.)
- The validated description becomes a PRD → engineering design + UI/UX +
  test strategy → features → stories → merged PRs → CI/CD → deployable
  artifact, with full visibility on a GitHub board at every step.
- Human involvement is dial-able (three-level scale, §7); Level 3 — "only
  interrupt me when you can't answer confidently" — is the goal.
- Cost and quality are measured per stage and recorded in the ledger:
  cycle time, cost (calls × context), which models were used, review-finding
  severity, rework loops, defect escapes — a clear statistics view for
  tuning model selection. Data-driven, not vibes. (Randy, 2026-11-14:
  measurement is a first-class requirement.)

## 2. Source material reviewed

All of Randy's factory thinking, reviewed 2026-11-14 (vault paths relative
to `~/Notes`):

**The rewrite direction (newest, 2026-11-13):**
- `Meetings/2026-11/2026-11-13_AI Software Factory Strategy and Implementation Plan.md`
  — new repo, demo to-do app (React/Vite/browser), guided intake from a plain
  description, live Storybook wireframes, CLI drives everything incl. cloud
  agent sessions, GitHub Boards exclusively, dogfooding ASAP, 3-level autonomy.
- `Meetings/2026-11/2026-11-13_Continuing on that thought...md` — end-user UX:
  describe → refine → prototype UI in Storybook → screenshot or (better) a
  button/link from the chat harness exposing the live Storybook so the user
  clicks through wireframes as if the app were running.
- `Meetings/2026-11/2026-11-13_Factory Workflow Planning Stories, CICD, and Dogfooding Risks.md`
  — PRD after user validation; feature branch ← stories → validate → main
  (tentative); first round = foundational workflow + contracts + agents +
  skills via structured vibe coding; dogfooding risk = Copilot agent
  inheritance; fallback = "vibe code plus" (structured vibe coding).

**Design foundations (Sept–Oct):**
- `Projects/Factory Kit — Vision.md` (2026-09-28) — runtime-agnostic kit,
  dispatch package as universal interface, ledger lives with the code,
  ownership/claim lock, human merge gate default, onboarding hardening.
- `Projects/Factory — Workspace Model (WIP).md` (ACCEPTED v0.3, 2026-10-23) —
  factory repo (CLI + core agents + skills) · workspaces bind target repos ·
  environments configure HOW not WHAT · declarative-first build order.
- `Meetings/2026-10/2026-10-18_Open-Source Software Factory Vision...md` —
  non-developer end state, demo-as-getting-started, fork-and-adapt, mechanical
  scripted onboarding, solid CLI underneath, board drag → cloud agents.
- `Meetings/2026-10/2026-10-18_AI Models, Hermes Orchestration...md` —
  Hermes preferred orchestrator but must be portable; Grill Me is a weak
  point; personalized agents may infer requirements; Randy must retain
  architecture understanding.
- `Meetings/2026-10/2026-10-18_AI Credit Planning...md` — sessions created
  mechanically through the CLI, parameter-driven model selection matched to
  task.
- `Projects/Warp Factories — Design Lessons for Our Factory.md` (2026-09-28)
  — adopt list: contract triplets, evidence-before-apply, typed gate
  artifacts, review schema + model diversity, guarded self-improvement,
  honesty vocabulary, trust posture. Meta-rule: a rule without a gate
  doesn't hold.

**Process DNA (June–Sept):**
- `Projects/Agentic Software Factory — Benchmark Architecture.md` — the
  7-agent pipeline + fresh-context plan review.
- `Projects/Software Factory - Grill Me Process.md` — persona comprehension
  verification + misconception→doc-fix loop.
- `Meetings/2026-09/2026-09-15_*` (4 notes) — context bundle contracts
  (PRD first, everything ties to PRD acceptance criteria), predictable
  outputs require predictable inputs, feature-readiness agent, story
  orchestrator focus, factory vs SpecKit use cases (factory = greenfield),
  AI lies — make it prove its work.
- `Meetings/2026-08/2026-08-21_Crawl, Walk, Run...md` — the autonomy lever
  applied across the SDLC (crawl = manual agents, walk = story orchestrator,
  run = feature orchestrator).
- `Meetings/2026-08/2026-08-18_*` (2 notes) — expensive models plan, cheap
  models code; rubrics stop critic loops; cross-vendor review finds bugs;
  plans-in-repo prevent plan corruption; devcontainers for agentic work.
- `Projects/Software Factory Research Report 2026-06-30.md` + Synthesis —
  OSS landscape gaps: codebase bootstrapping, spec→workitem pipeline,
  instruction transcoding, self-improvement loop.

Work-side (CLA/ADO) notes informed the principles but this repo is the
personal, open-source product — no ADO, no client specifics.

## 3. What we are building (the product)

One product, four surfaces:

1. **The CLI (`factory`)** — the spine. Drives every part of the factory:
   intake, workspace management, dispatching agent sessions (local or cloud),
   gates, ledger, renders, board sync. Parameter-driven model selection
   (role → tier → concrete model per environment). Invocable by a human, by
   an interactive agent session, and by GitHub Actions. Everything else is a
   surface over this CLI. (2026-10-18, 2026-11-13)

2. **The interactive intake experience** — a guided agent session where the
   user describes what they want; the agent asks the clarifying questions
   (platform, stack, features, look), builds **live Storybook wireframes as
   the UI conversation happens**, and exposes them to the user (screenshot
   first; better: a link/button to click through the running Storybook).
   Iterates until the user validates interface + rules → produces the PRD.
   (2026-11-13, both notes)

3. **The pipeline** — feature refinement → story decomposition → per-story
   test plan → impl plan → fresh-context plan review → code → build/tests →
   fresh-context adversarial code review → proof → PR → merge gate → CI/CD.
   Contracts at every seam; evidence at every gate. (process DNA, §6)

4. **The visibility layer** — GitHub Boards exclusively, and the board is a
   **clear visual of where each piece of work sits in the factory process**:
   **one lane per lifecycle state**, and **the CLI moves work through the
   states** (Randy, 2026-11-14). The ledger stays machine truth; the board is
   a derived mirror written only by the sync tool at each transition — never
   inferred, never hand-edited. Two views: the full state lanes (every
   lifecycle state) and a compact group view (Backlog / In flight / Waiting
   on human / Done) for the at-a-glance read. Queue order, what's in
   development, what's done, what's blocked — visible at a glance.
   **Failures surface here**: any blocked story/feature lands in the Blocked
   lane with an auto-created issue linking the evidence, where a human OR an
   authorized agent (per autonomy policy) reviews and clears it.
   Dispatch is triggered by `/factory dispatch` comment or `factory:run`
   label (P3); board drag-to-dispatch is an optional later UX (P6+, may be
   dropped — see §5). (2026-11-13, 2026-10-18; board shape ratified
   2026-11-14; dispatch trigger amended per design review 1.5)

   **The inbox (design review 2.2)**: `factory inbox` — one queue of
   everything waiting on the human, ordered by how much downstream work
   each item blocks. **Ordering algorithm (round-3 4.2):** `blocked_count` =
   the number of stories transitively blocked (direct + indirect
   dependencies) by this item, computed from the story dependency DAG;
   tiebreak oldest-first. Simple, computable, and directly answers "what
   should I look at first to unblock the most work." Each item is a decision
   card: the question, the options, the agent's recommendation, evidence
   links, and what happens if nobody answers. Pushed via GitHub
   assignment/mentions so phone notifications come free. The board shows
   where work is; the inbox shows what needs YOU. Lands in P2 (story
   dependencies recorded in the P1 schema so ordering works).

   **Board minimum schema (frozen for P0; exact state list frozen in P1):**
   - Lanes: one per story lifecycle state. The P1 state machine defines the
     exact set; the shape is intake → planning → plan-review → coding →
     code-review → testing/proof → merge-eligible → merged → live-proven →
     closed, plus **Blocked** as a first-class lane. Features aggregate their
     stories' states (computed render, §5).
   - Custom fields: Type (Feature | Story), Autonomy Level (1 | 2 | 3),
     Stage (the lifecycle state), Stage group (derived compact group),
     Tokens/cost, Model(s) used, Cycle time.
   - Views: full state lanes + compact group view.
   - P0: the backlog's feature items are created on the board from the
     feature list (human/Merlin). From P4, the intake engine auto-creates
     feature items when a PRD is produced. Board moves are CLI/sync-driven
     from P2; before that, moves are manual and recorded.

Plus the **demo app** (§8) as the getting-started path and the factory's
first end-to-end test subject.

## 4. End-to-end flow

```
USER: "I want to build X"
  │  interactive intake session (agent guides)
  ▼
Clarifying questions ── platform? stack? features? look?
  │  live Storybook wireframes while the UI is discussed
  │  user clicks through / reacts / iterates
  ▼
User validates interface + rules
  ▼
PRD (high-level, acceptance criteria = the anchor)
  ▼
Engineering design + UI/UX design + test strategy (context bundle;
  PRD first, eng↔UI/UX dependencies explicit)
  ▼
Feature(s) on the GitHub board
  ▼
Feature refinement → readiness check (gaps/open items?)
  ▼
Story decomposition (sequenced, dependency-aware, slice-sized)
  ▼
Per story: test plan → impl plan → plan review (fresh context)
  │   plan review FAIL → rework (≤2 loops) → 2-loop cap → BLOCKED
  ▼
Code (TDD) → build + story tests green → compute the merge-result tree
  (git merge-tree --write-tree branch main) → adversarial code review on
  THAT merge-result tree (fresh context, cross-model) → proof artifacts
  │   code review FAIL → rework: loop 1 same tier, loop 2 next model tier;
  │   contract-class defects route back to the plan/PRD, not the coder
  │   2-loop cap → BLOCKED
  ▼
Verify main has not advanced past the reviewed merge base (if it has,
  recompute merge-tree + re-review) → PR opened/updated → merge gate
  (policy-configurable, OC-9)
  ▼
main — trunk-based, squash, one commit per story   (RATIFIED OC-3)
  │   squash tree verified equal to the reviewed merge-result tree;
  │   evidence pinned by tree hash + commit SHA under durable
  │   refs/factory/* refs (no rebase after review — the reviewed tree IS
  │   the merge result, so the equality holds by construction)
  │   (incomplete user-visible flows stay expand-only or flagged)
  ▼
Feature-acceptance gate: all feature stories merged + feature-level
validation (acceptance tests / staging / integrated UI approval)
  │   gate FAIL → auto-create fix stories in Backlog → feature BLOCKED
  │   → fix stories follow the normal pipeline → re-run the gate
  ▼
CI/CD → deployable artifact → live proof (automated post-deploy evidence:
screenshot + smoke-test log, pinned in the ledger) → closeout

BLOCKED (any gate's 2-loop cap, or feature-gate failure):
  → Blocked lane on the board + auto-created issue linking the full
    review/evidence record
  → a human OR an authorized agent (per autonomy policy) reviews and
    clears: accept-with-known-issues / re-scope into new stories (with
    lineage) / amend-the-spec / retry-at-higher-tier / reject
    (CLOSED-WONT-FIX)
```

Trunk-based integration (OC-3, ratified 2026-11-14): no feature branches.
Every story merges straight to main; incomplete user-visible flows stay
expand-only or flagged. The feature-acceptance gate — not a branch — is
what preserves "main always deployable" and the deployable-artifact
promise. Chosen for least agent friction: one canonical base, small early
conflicts, one delivery milestone, one merge gate per story.

Human touchpoints by default: UI/Storybook approvals, PR merges, and
clearing blockers. At higher autonomy levels the first two become
policy-gated (§7); blocker-clearing may be delegated to an authorized agent
only where the autonomy policy explicitly allows it — escalations that
exceed the policy's confidence always reach a human.

## 5. Architecture sketch

Carried from the accepted workspace model (v0.3) + kit vision, adapted to
the rewrite:

```
software-factory repo        CLI · core agents · Intake Engine ·
                             skills/process rules · templates · adapters ·
                             onboarding   (versioned, the PROCESS)
factory-state repo           dedicated control home, spans ALL projects;
                             structured as an Obsidian vault
   └─ workspace(s)           per project: bindings + config + ledger +
                             story records + dispatch packages + renders
        └─ target repo(s)    product code ONLY · story branches · PRs · CI
                             (evidence pinned as repo@sha)
```

- **Factory repo** = this repo. One versioned home for the process; target
  repos are onboarded to it.
- **Factory-state repo (OC-8, RATIFIED 2026-11-14)** = a DEDICATED repo,
  separate from every product repo AND from the personal ~/Notes vault,
  that holds ALL factory state and spans projects. Structured as an
  **Obsidian vault**: machine truth is the append-only JSONL ledger; the
  human-facing view is generated markdown (state.md / DASHBOARD.md /
  PROVENANCE.md / story records) browsable in Obsidian. **State never lives
  in the product repo** — this supersedes the kit's old "ledger lives with
  the code" law. Kept separate from ~/Notes so high-frequency machine writes
  don't fight its Syncthing/cron sync.
  - **Scope (Randy, 2026-11-14):** a state vault is scoped to a **person, a
    team, or an organization**. Scope sets ownership, visibility, and who
    may dispatch/mine. One person may have a personal vault; a team shares
    one; an org runs one across many teams/projects. **Enforcement = the
    state repo's GitHub visibility + collaborator/team permissions**
    (round-3 1.3): person = private repo, one collaborator; team = private
    repo shared with a GitHub team; org = internal/private org repo. The
    `scope` field in workspace config is declarative (records intent); the
    controller validates it against the GitHub API on `factory doctor`.
    The scope/ownership model is frozen in P1.
  - **Mining (Randy, 2026-11-14):** because state is an Obsidian vault of
    generated markdown + ledger, **tools can mine it to see how things were
    built** — provenance, decisions, recurring patterns, cost/cycle history.
    The vault is a queryable knowledge substrate, not just a state store.
    Mining tools are a later-phase capability built on top, feeding the
    statistics view (§10) and the "how was this built" provenance story.
- **Intake Engine** = a stateful session manager, distinct from the
  fire-and-forget dispatch pipeline: it drives the question flow, Storybook
  wireframe generation, and PRD production, and owns the conversation state.
  It sits behind the harness-agnostic intake protocol (OC-7) and uses the
  same adapter seam for LLM calls. Storybook exposure degrades by harness
  capability in three tiers: **LIVE** (embedded/bridged running-Storybook
  URL), **LINK** (clickable URL), **SCREENSHOT** (static image fallback).
  The protocol queries harness capability and picks the best tier; Hermes
  targets LIVE, a plain terminal gets LINK/SCREENSHOT.
- **Workspace** = a project's control home INSIDE the factory-state repo;
  binds one or more target repos (stories can span repos). Single-repo and
  multi-repo projects both live in the state repo — there is no in-repo
  control home anymore. **Self-host (dogfood):** the factory's own build is
  just another workspace in the state repo whose target repo is the
  software-factory repo itself; no special casing.
- **Evidence binding across repos (OC-8)**: every ledger event pins
  `repo@sha`; validation resolves each SHA against THAT product repo's
  object database; provenance joins across the repo set. Atomicity comes
  from pinning exact product SHAs, not from co-locating files. (This is the
  accepted workspace-model v0.3 mechanism, now the universal default.)
- **Environments** = where a workspace runs (this machine / cloud runner /
  client). Per-env config: runtime, dispatch mechanism, models per tier,
  credential refs, limits. Environments resolve HOW, never WHAT.
  **Model routing:** minimum roles = planner, coder, reviewer, intake-agent,
  feature-refiner; tiers = budget, standard, frontier. The full matrix
  (role × tier → provider + model) lives in environment config; P1 freezes
  the schema, P3 populates real models. Every dispatch's resolved
  provider/model is sealed into its identity and recorded for the statistics
  view.
- **Adapters** = execution bindings: hermes, copilot-cli, claude-code, codex,
  api-direct (OpenAI-compatible → Foundry/locked-down), human. The dispatch
  package (role + pinned inputs + expected outputs + stop rules) is the
  universal interface — same package through any adapter.
- **Deterministic control plane**: python3 stdlib + git + gh; controller,
  ledger, gates, renders, board sync. Never needs an AI — that's what makes
  human mode and portability real. AI only ever sits behind a dispatch
  package. **Feature state is a computed render** from story states (all
  stories merged + acceptance gate passed = feature done); feature-level
  gate events (acceptance-pass / acceptance-fail) ARE first-class ledger
  events for audit. Story events remain the only state-driving events.
- **Evidence integrity (design review 1.1; round-3 2.1/2.2/2.3)**: evidence
  is pinned by **tree hash AND commit SHA**. The merge-integrity protocol
  resolves the round-1 "squash tree = reviewed tree" vs "up to date with
  main" contradiction by reviewing the MERGE RESULT, not the bare branch:
  1. After build + story tests green, compute the merge-result tree with
     `git merge-tree --write-tree <branch> main` (plumbing; touches neither
     working tree nor index — verified).
  2. The adversarial review runs on THAT merge-result tree. The ledger
     records `reviewed_tree` (the merge-result tree reviewed) and the
     `review_context` (base/reviewed SHAs + manifest digest).
  3. Before merge, verify main has not advanced past the reviewed merge
     base; if it has, recompute merge-tree and re-review. **No rebase after
     review.**
  4. The squash commit's tree is verified equal to `reviewed_tree`
     (`merge_tree == squash_tree`); the equality holds by construction
     because the reviewed tree IS the merge result. The ledger links
     `reviewed_tree → review_context → merge_tree → squash_commit`.
  Evidence refs live under a durable `refs/factory/*` namespace — never
  Actions artifacts (90-day expiry), never `refs/pull/*` (not fetched by a
  fresh clone). `factory init` configures the fetch refspec in each product
  repo (`git config --add remote.origin.fetch '+refs/factory/*:refs/factory/*'`);
  ledger tooling does targeted `git fetch origin '+refs/factory/<story>/*'`.
- **Cross-repo evidence validation (OC-8; round-3 1.1/1.4)**: the ledger is
  in the state repo, the code/evidence in product repos. Validation
  protocol: (1) read the ledger entry's `repo@sha`; (2) ensure the product
  repo is available (cached clone or `git fetch <product-repo> <sha>`);
  (3) resolve the SHA + `refs/factory/<story>/*` against THAT product repo's
  object DB; (4) a missing/unresolvable object surfaces as BLOCKED with
  `evidence-unreachable` reason — never a silent pass. The validator needs
  network access to referenced product repos (or cached clones).
  `factory doctor --deep` checks all ledger SHAs still resolve (detects
  product force-push dangling refs); board sync spot-checks recent story
  SHAs. Force-push detection is visibility/audit, not a hard gate.
- **Ledger write location + layout (OC-8, RATIFIED; round-3 1.2/5.2)**: the
  ledger lives in the dedicated factory-state repo, never in a product repo
  and never on product main. **Per-story ledger files**
  (`workspaces/<name>/ledger/stories/<story-id>.jsonl`) — chosen so different
  stories NEVER contend on append; only same-story writes collide, and the
  per-story Actions concurrency group already serializes those. A
  per-workspace index/rollup is a derived render, not a write target.
  Concurrency within a story: git non-fast-forward rejection as
  compare-and-swap; the CLI retries a rejected push up to 3× with
  exponential backoff (1s/2s/4s); exhaustion → BLOCKED with `cas-contention`
  reason surfaced in the inbox. The state repo absorbs the write traffic.
- **Workspace policy config (OC-9, RATIFIED)**: per-workspace, frozen as
  schema in P1, enforced by the controller —
  - **merge policy**: (1) human-merges-every-story (Level 1 default for the
    factory's own build); (2) auto-merge expand-only/flagged stories with
    all gates green, human approves at feature-acceptance (recommended
    production default once metrics earn it); (3) full auto-merge (explicit
    opt-in only). Independent stories may proceed while another waits at a
    gate, under any policy.
  - **Copilot review requirements**: on/off per workspace. On = a Copilot
    review is a REQUIRED input to the review gate (requested, waited on,
    findings dispositioned like panel findings). Off (factory default) =
    the factory's own fresh-context panel is the gate. The factory OWNS the
    gate either way; a bot comment alone never merges anything.
  - **remediation**: in-session coder fix loops (default) / separate
    remediation dispatch / human-directed fixes; loop caps + tier
    escalation per policy.
  - **branch protection rulesets per merge mode (round-3 5.3)**: `factory
    init` configures branch protection via the GitHub API to match the mode.
    Mode 1: require 1 human PR review + the factory gate status checks.
    Mode 2/3: require the factory gate status checks ONLY (no human-review
    requirement) — the factory review gate IS the approval, so auto-merge
    isn't blocked waiting for a review the policy says isn't needed.
    (GitHub hard-blocks self-approval — an author can't approve its own PR —
    so requiring a review on agent-authored PRs would deadlock auto-merge.)
- **Human approval anchoring (design review 1.3; round-3 3.1/3.2)**: "a human
  approved" is tied to a GitHub object the agent identity cannot forge. Two
  DISTINCT mechanisms, mapped to distinct gates:
  - **Code-merge gate** → a human PR review/merge by a human account.
  - **Agent-dispatch gate** → an Actions environment with required reviewers
    (a human approves before an agent session runs against a protected
    environment, e.g. production deploy or a Level 2→3 transition).
  The ledger records a reference; a gate verifies it through the API.
  **Concrete agent token boundary (frozen in the P1 threat model):** the
  factory App is granted `contents: write`, `pull_requests: write`
  (create/update PRs), `issues: write` (board sync + inbox mentions),
  `metadata: read` — and **no `workflows` permission**. The App identity is
  **never a required approver** and is **never listed in CODEOWNERS**;
  CODEOWNERS lists only human handles and is itself branch-protected (the
  App cannot push to it on main). GitHub's hard self-approval block backs
  this: the agent authors the PR, so it cannot approve it. Control-plane
  paths (`.github/workflows/`, gate catalog, autonomy policy, override file)
  are CODEOWNERS + branch-protection guarded. The proven human-only
  comment-gate pattern (positive-only actor trust) ports from the reference
  implementation as the command surface, with this anchoring underneath.
- **Security posture (design review 1.4; round-3 3.3/3.4)**: a threat model
  is a P1 deliverable. Keys are scoped per job. **Egress allowlist is
  deferred to P6** (Randy, 2026-11-14): GitHub-hosted runners cannot filter
  network egress natively; P3 accepts that risk with per-job credential
  scoping + the secret-scanning gate as compensating controls, documented as
  an accepted risk in the threat model; true egress filtering arrives with
  self-hosted/proxy-capable runners at P6. A deterministic new-dependency
  gate checks existence,
  age/usage, allowed licence, and committed lockfile; a new dependency is a
  human touchpoint at Levels 1–2. Board-write/dispatch authority is named
  (positive-only actor trust). **Secret scanning runs pre-push** (round-3
  3.4): a deterministic gate in the agent's coding session before the branch
  push (gitleaks/trufflehog, tool frozen in P1) — secrets never reach
  GitHub; detection fails the gate and the agent remediates.
- **Claim leases (round-3 5.5)**: every claim carries a TTL (default 30m
  cloud, 10m local), auto-renewed by the holding process; an expired claim
  auto-releases with an audit event, so a dead ephemeral session never holds
  a story hostage. Split-brain guards: (1) renewal runs on a background
  timer, independent of the main agent loop yielding; (2) before EVERY
  side-effect operation (branch push, PR open/update) the job re-checks its
  lease in the ledger and fails immediately with `lease-expired` if lost;
  (3) the effective TTL includes a grace period (TTL + 2× renewal interval)
  for clock skew. The fail-closed human override file remains the emergency
  release, not the normal path.
- **Cloud execution**: GitHub Actions–backed agent sessions (RATIFIED
  OC-2, 2026-11-14): the CLI triggers a workflow running an agent in a
  container with repo-scoped credentials. Agent jobs use a **GitHub App
  token** (events created with the default GITHUB_TOKEN do not trigger
  workflows — verified). Adapter seam keeps other cloud runtimes
  swappable. **Dispatch model:** each pipeline step (plan, code, review,
  proof) is a SEPARATE Actions job; state is checkpointed in the ledger
  between steps; no single job spans multiple stages. Jobs are idempotent:
  side effects (branch push, PR, issue) are upserts keyed by dispatch id; a
  replay resets the branch to the pinned base — replay the dispatch, not
  the session. **Dispatch trigger (design review 1.5, verified):** a
  `/factory dispatch` issue comment or a `factory:run` label — the proven
  command-surface pattern. Board drag-to-dispatch is an OPTIONAL later UX
  (P6+): projects_v2_item webhooks are organization-only and not an Actions
  trigger (verified), so drag requires an org-owned board + App webhook
  relay; it may be dropped.
- **Board sync direction**: primarily one-way (ledger → board). A
  `factory board reconcile` command detects and repairs drift from human
  card moves (proven pattern from the reference implementation); sync
  failure is a visible state, never silent. Dispatch triggers arrive as
  comment/label commands (see Cloud execution); the ledger records the
  dispatch event only after the CLI receives it. The board triggers the
  action; the ledger remains the sole source of truth.
- **Onboarding + state-repo bootstrap (round-3 6.3)**: `factory init
  [--guided] --state-repo <url>` — creates the workspace in the
  factory-state repo, onboards a target repo (configures the
  `refs/factory/*` fetch refspec + branch protection per merge mode),
  generates an environment-config template, and validates with `factory
  doctor`. If the state repo isn't present locally it's cloned; if the URL
  doesn't exist on GitHub, `--create-state-repo` creates it via `gh repo
  create`. **Discover/join:** subsequent `factory init` calls with the same
  `--state-repo` ADD a workspace to the existing repo (the state repo spans
  projects). State-repo root layout: `workspaces/<name>/` (per project,
  each with `ledger/stories/<story-id>.jsonl` + config + records + renders)
  and shared `templates/`. `--guided` asks setup questions interactively (a
  lower-touch profile; the primary audience is engineers, OC-11). Onboarding
  is scripted/mechanical first; the guide is an adapter, never the sole
  installer.
- **Dependency policy**: agents may modify dependency manifests
  (package.json, requirements.txt, etc.) as part of story code; all
  dependency changes must be committed with the story; `factory doctor`
  flags uncommitted manifest changes; CI installs from committed manifests.

Judgment calls I'm making explicit so Randy can unmake them:
- Python for the control plane (proven in MIE/kit; stdlib-only, portable).
- TypeScript/Node for the demo app and Storybook intake tooling (React/Vite
  per the notes). The CLI itself stays Python — one language for the spine.
- Hermes is the first adapter (it's what we run), but nothing in the core
  may depend on it; portability is a test, not a hope.

## 6. Principles carried forward (non-negotiables)

Distilled from five months of runs and studies. These survive the rewrite:

1. **Predictable outputs require predictable inputs.** Contracts at every
   seam: PRD contract, context-bundle contracts, dispatch contracts. Agents
   make judgment calls inside defined parameters; they don't invent.
2. **The PRD is the anchor.** Everything ties back to PRD acceptance
   criteria; PRD established before the other bundle docs; eng design and
   UI/UX dependencies explicit.
3. **Make the AI prove it.** Build green + named tests green + evidence
   artifacts before any review or "done" claim. Never write intent as
   though it were a result; expectations vs observations; nulls render as
   "not recorded: reason", never zeros.
4. **Fresh-context adversarial review.** Reviewers never see the author's
   reasoning; cross-model-family panels; structured findings, each
   dispositioned; review record pinned to the exact head; 2-loop cap then
   escalate. Rubrics stop critic loops. Rework is tiered: loop 1 same tier,
   loop 2 next model tier; contract-class defects route back to the plan or
   PRD, not the coder. **Escalation = the story enters BLOCKED** (Blocked
   lane on the board) **with an auto-created issue linking the full review
   record; a human or an authorized agent (per autonomy policy) must
   disposition it** — accept-with-known-issues, re-scope into new stories
   with lineage, amend-the-spec, retry-at-higher-tier, or reject
   (CLOSED-WONT-FIX). **Reduced-assurance mode:** a user with a single
   provider cannot run a cross-family panel; the review runs single-family
   and the record is marked reduced-assurance — recorded, never silent
   (design review §3).
5. **Plans are design contracts, not code.** Manifest, signatures, test
   names, decisions & rejected alternatives. Coder is sole code author.
6. **Cheapest model sufficient per role.** Tier routing, complete matrix
   (unrouted dispatch = defect), parameter-driven selection sealed at
   dispatch; expensive models plan, cheap models code; upgrades data-gated
   on reasoning-class defects.
7. **Cost ≈ calls × context-per-call.** Fewer child calls, smaller child
   context, deterministic context assembly, meter every dispatch or it
   didn't happen.
8. **Slice sizing.** Stories are slices: ≤1 structural signal, ≤6 top-level
   ACs, independently mergeable, expand-first ordering. Stacked specs are
   intake defects.
9. **Ledger = machine truth; the state repo = state.** Append-only events,
   evidence SHAs validated against the product repo's object DB (pinned as
   repo@sha), corrections are events never edits; sessions disposable,
   state durable; push-per-gate to the dedicated factory-state repo (OC-8 —
   supersedes "ledger lives with the code"); claim lock (one owner per
   story, handover events, fail-closed human override file) with **claim
   leases** (TTL + auto-renew + audited auto-release) so ephemeral sessions
   never strand a claim.
10. **A rule without a gate doesn't hold.** Enforcement > discipline;
    deterministic gates before LLM gates; checkers must be able to fail.
11. **Human touchpoints stay** (until autonomy policy says otherwise):
    Storybook/UI approvals, merge gate, escalations. Merge is a human
    decision by default.
12. **Runtime-agnostic process.** Process lives in-repo, versioned; any
    runtime (or a human with a shell) executes the same dispatch packages.
13. **Honest failure.** Blame split (agent vs platform), retryable as data,
    BLOCKED first-class; refuse, don't fall back; failed mirrors never show
    a state main never recorded.
14. **Trust posture.** All inbound artifacts untrusted data; positive-only
    actor trust; human-gated transitions refuse non-human actors by
    configuration.
15. **Randy keeps the architecture.** Briefings before automation; decision
    calls walked through in plain language; the owner understands what's
    being built (2026-10-18). **This is a gate, not a note (design review
    2.5):** engineering design, UI/UX design, test strategy, and story
    decomposition each get fresh-context review AND a human approval
    touchpoint (architecture, data model, decomposition) — the upstream
    stages where mistakes are most expensive. The touchpoint set is a
    profile (primary persona = engineers, OC-11 ratified).
16. **Requirements change safely (design review 2.6).** The PRD is
    versioned; a gate flags in-flight stories whose pinned acceptance
    criteria changed; amendments are recorded as DECs with re-pin or
    re-scope. Nothing silently re-bases a story onto a new spec.
17. **The codebase is maintained, not just generated (design review §3).**
    Greenfield lasts one story — after the first merge every story works on
    an existing codebase. An architecture + conventions document is
    maintained and updated by a gate at merge, well before the deferred
    codebase-bootstrapping feature.

## 7. Autonomy model — three levels (rules RATIFIED OC-4)

Randy's scale (2026-11-13), aligned with the earlier crawl/walk/run lever
(2026-08-21):

| Level | Name | Human involvement |
|---|---|---|
| 1 | Crawl | Developer reviews every piece; agents run stage-by-stage with human approval at each gate |
| 2 | Walk | Human approves at the three touchpoints only: UI/Storybook, merges, escalations |
| 3 | Run | "I gave you my description — only interrupt me when you can't answer confidently." Goal state. |

RATIFIED (OC-4, 2026-11-14): levels are gate policy, one pipeline, measured
promotion; details below.
- Levels are **policy configuration**, not separate code paths: same
  pipeline, gate policy decides which transitions need a human actor.
- Level 3 escalation contract (OC-10, RATIFIED 2026-11-14): escalate by
  **deterministic decision class**, checked by code — not self-reported
  confidence (design review 2.3: model confidence is poorly calibrated).
  Classes: irreversible actions, scope change vs PRD, new dependencies,
  security-sensitive paths, budget overrun, reviewer disagreement; the
  class list is extendable policy config. Everything else proceeds on a
  **recorded assumption**; the human reviews the assumption log via the
  inbox (§3.4) when convenient; a veto creates a rework story. BLOCKED
  first-class while a question waits.
- Autonomy is earned with data: per-level metrics (intervention rate, defect
  escape rate, cost) gate promotion. Level 3 for a repo/class of work is a
  measured decision, not a flag flip. **Promotion thresholds** (max
  intervention rate, max defect escape rate, cost ceiling) are defined in P6;
  no Level 3 activation without threshold data from at least 3 completed
  features.
- Merge autonomy is the last gate to automate, if ever (kit default: human
  merge stays; autonomous merge only as explicit opt-in policy).

## 8. Demo app

A small but robust **to-do app — React + Vite, browser** (Randy, 2026-11-13).

- NOT pre-specified: the factory's intake must produce its specs from a
  plain description ("I want a to-do app...") through guided questions. The
  demo exercises intake → wireframes → PRD → pipeline end-to-end.
- The demo repo is the getting-started path for users: here's the app, here
  are the prompts/conversation that built it, fork it and adapt (2026-10-18).
- Small enough to run the full pipeline cheaply and repeatedly; robust
  enough to exercise real gates (state, persistence choice, edge cases,
  tests, CI/CD deploy).
- The demo's own build is the factory's first acceptance test.
- **Demo repo**: a separate repository (`agentmerlin8/software-factory-demo`),
  created in P5 and onboarded as the factory's first target repo. Separate so
  the factory repo stays clean and the demo is independently forkable as the
  getting-started template.

## 9. Build strategy: structured vibe coding → dogfooding

Randy's direction (2026-11-13):

- **Round 1 = make the factory's actual workings operational**: foundational
  workflow, contracts defined, agents and skills built. Built via
  **structured vibe coding** ("vibe code plus") — fast agent-driven building,
  but every story tracked and visible on the board, walked through with
  Randy.
- **Dogfood as soon as practical** — use the factory to build the factory.
  Cutoff RATIFIED (OC-5, 2026-11-14): P3 exit — one story end-to-end by the
  factory itself with the ledger intact; then NEW features go through the
  factory, control-plane changes stay structured-vibe until the review lane
  is proven on itself.
- **Known risk: Copilot agent inheritance.** If the target repo contains an
  agent with the same name as the agent under development, Copilot inherits
  the repo's version; changing agent files mid-build confuses the process.
  Candidate mitigations: naming structure; restrict dogfooding to NEW
  features/instance skills; or abandon Copilot as the dogfood runtime.
  **The runtime-agnostic design de-risks this**: dogfood through the Hermes
  (or other non-Copilot) adapter and the inheritance problem doesn't apply.
  If no robust path exists, structured vibe coding remains the fallback —
  it is not a failure state.
- Work organized feature-by-feature with a full backlog on GitHub Boards;
  timeline + implementation plan + clear feature structure (this repo's
  docs/backlog become that plan once the vision is approved).

## 10. Measurement & statistics (first-class — Randy, 2026-11-14)

Measurement is a product requirement, not an afterthought: a very clear view
of **cycle time, cost, which models were used, and all statistics**, so model
selection can be tuned on data.

- **Recorded per dispatch** (ledger events, harvested from the runtime or
  reported by the executor; nulls render as "not recorded: reason", never
  zeros): role, resolved provider + model (sealed at dispatch), input/output
  tokens, cost, wall time, outcome, loop tags.
- **Derived per story / feature / run**: cycle time per stage and end-to-end
  (idea → merged → live-proven), **split into machine time vs
  waiting-on-human time** (design review 2.1), total cost, model mix,
  revision-loop count and class (mechanical / reasoning / contract / nit),
  review-finding severity distribution, first-try pass rate, defect escapes
  post-merge, human-intervention count, blocked-time. **"Human minutes per
  merged story" is a headline metric alongside cost** — it measures whether
  the factory actually frees the human.
- **Budgets are enforced, not just measured (design review §3)**: hard
  ceilings per dispatch, story, feature, and day as stop rules; a retry
  budget for platform failures; job timeouts; and a `factory pause` kill
  switch. The two-loop cap covers review loops, not an agent stuck inside
  one session — the ceilings do.
- **The statistics view**: `factory stats` (CLI) + a rendered dashboard in
  the repo, plus board fields (Tokens/cost, Model(s) used, Cycle time) so
  the numbers are visible where the work is. Per-model and per-role
  breakdowns are the tuning surface: which model is cheapest-sufficient for
  which role, where loops concentrate, where cycle time hides.
- **Schema frozen in P1, metering live in P3, dashboard polished with the
  demo (P5).** Baseline frozen before any efficiency change; a change is
  KEPT only if the target metric moves and reasoning-class loops don't rise.
- Cost stays tokens + a versioned price table until that table is trusted;
  dollars are derived, never invented.

## 11. Roadmap (candidate phases)

Candidate phases — order follows the accepted declarative-first principle;
each phase ends in something demonstrable.

- **P0 — Vision & contracts (now).** Vision grilled and approved; feature
  backlog + board created (lane-per-state schema, §3); repo scaffolding.
  Storybook spike (OC-6, ratified) starts here as **throwaway exploration**:
  hardcoded setup, fixed conversation script, output = model/adapter
  evaluation data, not reusable code. P4 builds the real intake on P1
  schemas, informed by the spike. **Two pre-freeze validations (round-3
  6.2):** (1) run one story through by hand with the human adapter
  (exercises story schema, transition catalog, evidence integrity); AND
  (2) a **concurrency smoke test** — two independent stories dispatched
  simultaneously against the same target repo with the state repo separate
  (exercises per-story ledger CAS, claim leases, cross-repo evidence). A
  single-story hand-run cannot catch contention or cross-repo bugs; both
  must pass before P1 freezes. Hand-run with two terminal sessions suffices.
- **P1 — Declarative core.** Workspace + environment config schemas,
  ledger schema (incl. measurement fields, §10), story lifecycle state
  machine, dispatch-package contract. No execution yet — the contracts
  everything else obeys. **No specification shell may freeze (round-3
  6.1):** every contract below ships with a concrete example + data schema
  + validation rule in pseudocode before freeze; a name with no internals
  is not a frozen contract. P1 must freeze:
  - the **complete transition catalog**: every state → event → next-state
    tuple tagged with gate type (none | deterministic | llm-review |
    human-approval) and autonomy-level override rules (which levels skip
    the human); ships with sample tuples covering the happy path + each
    failure/escalation path;
  - the **story schema**: id, feature ref, ACs anchored to the PRD (with
    PRD version pin), structural-signal count, dependencies (for inbox
    ordering), target repo, state;
  - the **story failure lifecycle**: rework loop (tiered), 2-loop cap,
    BLOCKED, human/authorized-agent disposition paths (accept / re-scope /
    amend-spec / retry-higher-tier / reject);
  - the **feature-acceptance failure path** (BLOCKED + auto-created fix
    stories) and feature-state computation rules (computed render; gate
    pass/fail are ledger events);
  - the **model-routing schema** (roles × tiers) and claim-lease semantics
    (background renewal, pre-side-effect lease check, grace period);
  - the **factory-state repo layout (OC-8)**: dedicated state repo as an
    Obsidian vault, the exact directory tree (`workspaces/<name>/` +
    `ledger/stories/<story-id>.jsonl` + shared `templates/`), bootstrap +
    discover/join procedure, repo@sha cross-repo evidence validation
    protocol, per-story ledger CAS + retry/backoff, per-story concurrency
    mutex; no in-repo control home; **scope/ownership model (person | team |
    organization)** bound to GitHub permissions, validated by `factory
    doctor`;
  - the **workspace policy schema (OC-9)**: merge policy (3 modes) + the
    branch-protection ruleset per mode, Copilot review requirements (on/off),
    remediation mode — all controller-enforced;
  - the **escalation decision-class list + assumption-log schema (OC-10)**;
  - **schema version on every ledger event from the first commit** (later
    changes are migrations);
  - **evidence integrity**: the merge-tree protocol (compute merge-result
    tree → review it → no rebase after review → squash tree = reviewed
    merge-result tree), two-tree pinning (`reviewed_tree`/`merge_tree`),
    durable `refs/factory/*` store + fetch-refspec config, cross-repo
    validation + force-push liveness check;
  - **human approval anchoring** (the exact App permission set; App never a
    required approver / never in CODEOWNERS; human-only CODEOWNERS +
    branch protection; no-`workflows` token; code-merge vs agent-dispatch
    gate mechanisms) and the **threat model** (per-job keys, dependency
    gate, pre-push secret scanning + tool choice, dispatch authority,
    egress-allowlist accepted-risk posture for P3 + P6 hardening path);
  - **budget ceilings** as stop rules; **idempotent-replay semantics**
    (idempotency-key format, upsert targets = branch/PR/issue keyed by
    dispatch id, reset-to-pinned-base procedure); **process + prompt version
    sealed into dispatch identity**; **flag registry + lifecycle**; **PRD
    versioning mechanism + changed-criteria gate algorithm**; **test-gaming
    gate** (the diff algorithm + baseline: deleted tests / new skips / fewer
    assertions fail; AC→named-test traceability); **reduced-assurance review
    mode**; the maintained **architecture + conventions doc**; **inbox
    ordering** (blocked_count over the dependency DAG).
  Storybook spike continues.
- **P2 — CLI read path + control plane.** `factory status/doctor` (incl.
  `--deep` SHA-liveness check), controller/ledger/gates/renders ported
  genericized from the kit work; board sync (visibility first — Randy needs
  to SEE the work); one-way ledger→board mirror with the sync tool as sole
  writer + `factory board reconcile`; **`factory inbox`** (decision cards,
  blockage-ordered, pushed via GitHub mentions). **Board write fallback
  (round-3 5.4):** Projects V2 GraphQL field writes need org-level project
  scope; `factory board sync` detects writability and falls back to issue
  labels + body for Stage tracking where unavailable — custom fields are
  best-effort, the ledger records them regardless.
- **P3 — Execution seam.** One adapter end-to-end (Hermes local first):
  dispatch → agent session → artifacts → evidence → transitions. Then the
  GitHub Actions cloud adapter (OC-2 ratified), per-step dispatch with
  ledger checkpoints + claim leases, App-token events, comment/label
  dispatch trigger. Parameter-driven model routing from day one; metering
  live (§10); budget enforcement live. **State-repo reachability (round-3
  1.5):** push failures retry 3×; exhaustion → job fails with
  `state-repo-unreachable`, dispatch replayable. **Deployability guard:** CI
  on every main push runs build + smoke tests; red main = BLOCKED new
  dispatches until green, and **the offending commit is auto-reverted with
  its story reopened** (design review §3 — red main has an owner).
  Architecture + conventions doc updated by a merge gate. Egress allowlist
  NOT enforced here (accepted risk, §5); per-job key scoping + pre-push
  secret scanning are the compensating controls. **P3 exit = dogfood cutoff
  (OC-5 ratified).**
- **P4 — Intake & Storybook.** Guided intake session (harness-agnostic
  protocol, Hermes first — OC-7 ratified), question flow, wireframe
  generation + exposure to the user via the LIVE/LINK/SCREENSHOT tiers,
  PRD generation; intake engine auto-creates feature items on the board.
  Builds on the P0/P1 spike results (OC-6 ratified).
- **P5 — Demo end-to-end.** To-do app from plain description to deployed
  artifact through the full pipeline at Level 1/2, in the separate demo
  repo. Factory generates a baseline CI config (build/test/lint) for the
  target repo; live proof = automated post-deploy evidence; flag-cleanup
  stories auto-created on feature acceptance. Statistics dashboard
  polished. **P5 exit = repo goes PUBLIC** (Randy, 2026-11-14) —
  "something working" is the bar.
- **P6 — Dogfood expansion.** Factory builds factory features (started at
  P3 exit per OC-5); autonomy-level policy + metrics; **Level-3 promotion
  thresholds defined here** (no activation without data from ≥3 features);
  onboarding hardening + fresh-repo test-out; remaining adapters
  (priority: api-direct, claude-code, codex, copilot-cli; the human adapter
  exists from P2 as the CLI itself); **factory regression suite** (fixed
  stories with known outcomes, replayed before any process change) and
  **reviewer catch-rate calibration** (seeded-defect runs); optional board
  drag-to-dispatch UX (org board + App webhook relay) if still wanted.
- **P6+ — State-vault mining.** Tools that mine the factory-state vault to
  show **how things were built**: provenance queries, decision history,
  recurring patterns, cost/cycle trends across projects and scopes. Built on
  the generated markdown + ledger; feeds §10 statistics and the "how was
  this built" story. Scope-aware (person/team/org). A capability on top of
  the state substrate, not a blocker to the pipeline.
- **P7 — Public polish.** Engineer-focused getting-started, fork-and-adapt
  demo, scripted onboarding, docs. The repo is already public since P5;
  this phase polishes what is public.

## 12. Explicitly deferred

Written down so they don't get built early:

- **End-user hosting strategy** (free/cheap/paid hosting of the software the
  factory builds) — later-round concern; first round is the factory's
  workings. (2026-11-13) **CI/CD boundary:** the factory generates a
  baseline CI config (build, test, lint) for target repos at P5; repos may
  customize it; `factory doctor` validates CI presence.
- **Mobile/native targets** — demo is browser-first; phone targets wait
  until the pipeline works and deploys.
- **Non-GitHub forges** (GitLab, Bitbucket, ADO repos) — GitHub is the forge.
  ADO state integration stays a work-side concern, not this product.
- **True concurrent story scheduling** — claim lock prevents it; revisit
  only with trial data.
- **Autonomous merge** — off by default; explicit opt-in policy only, if ever.
- **Hash-chain tamper evidence, central warehouse/cross-project rollups** —
  later, derived-only.
- **Codebase bootstrapping for existing repos** (auto-generate context
  bundle from a live codebase) — the June research gap; valuable, but the
  rewrite targets greenfield first (factory = greenfield use case,
  2026-09-15). Existing-repo intake is a later feature.
- **Self-improvement loop** (factory edits its own instructions) — guarded
  design from the Warp study; only after the base pipeline is proven and
  metered.
- **Merlin desktop hardware agent** — separate project (2026-11-13 note);
  not part of this repo.

## 13. Decisions already locked (from the notes)

Locked by Randy's notes (no re-litigation without new direction):

| Date | Decision |
|---|---|
| 2026-11-13 | New repo `software-factory`, ground-up rewrite; replaces the public ai-software-factory effort; private until working, then public |
| 2026-11-13 | Demo = to-do app, React + Vite, browser; intake starts from a plain description, NOT prewritten specs |
| 2026-11-13 | Live Storybook wireframes during UI discussion are a key part of intake |
| 2026-11-13 | CLI drives everything, spawns agent sessions (incl. cloud), invocable from an interactive agent session |
| 2026-11-13 | GitHub Boards exclusively for the backlog; visibility is a first-class requirement |
| 2026-11-13 | End-to-end path: idea → features → stories → merged PR → CI/CD |
| 2026-11-13 | Three-level autonomy scale, Level 3 the goal (levels' operating rules still open) |
| 2026-11-13 | Round 1: foundational workflow + contracts + agents + skills via structured vibe coding; dogfood ASAP with a defined cutoff |
| 2026-10-23 | Workspace model v0.3: factory repo / workspaces / environments; multi-repo default = dedicated workspace repo; N human merges tracked as a set; declarative-first build order |
| 2026-10-18 | End state: non-developer usable, open source, bring-your-own subscriptions; demo = getting started; mechanical/scripted onboarding preferred; solid CLI underneath |
| 2026-10-18 | Sessions created mechanically via CLI, parameter-driven model selection |
| 2026-09-28 | Ledger lives with the code; dispatch package = universal interface; human merge gate + Storybook approvals default; claim lock + fail-closed override; extract from prior work read-only |
| 2026-09-06 | Cheapest sufficient model per role; frontier budget for meta-advice only; review gates owned by the factory, not platform bots |
| 2026-11-14 | OC-1: keep old ai-software-factory repo, made PRIVATE (done); read-only salvage source, no archive |
| 2026-11-14 | OC-2: cloud execution GitHub-native — Actions-backed agent sessions first, adapter seam for others |
| 2026-11-14 | OC-3: trunk-based integration — stories merge straight to main (squash, one commit per story); no feature branches; feature-acceptance gate (all stories merged + feature-level validation) before a feature is released; expand-only/flagged for incomplete user-visible flows; chosen for least agent friction |
| 2026-11-14 | OC-4: autonomy levels = gate policy, one pipeline, measured promotion; Level 1 for factory's own build, Level 2 default for target repos after demo, Level 3 behind metrics + escalation contract |
| 2026-11-14 | OC-5: dogfood starts at P3 exit (one story end-to-end by the factory, ledger intact); new features through factory, control-plane changes structured-vibe until review lane proven on itself |
| 2026-11-14 | OC-6: Storybook intake spike early (P0/P1), screenshot-back first then live link, 2–3 model/adapter combos evaluated on a fixed script |
| 2026-11-14 | OC-7: harness-agnostic intake protocol, Hermes chat first implementation; end-user surface decided after demo |
| 2026-11-14 | Grill fix: repo goes PUBLIC at P5 exit (demo end-to-end working); P7 is public polish |
| 2026-11-14 | Grill fix (Randy): board = one lane per lifecycle state, CLI moves work through states; full-lane + compact-group views; failures surface in a Blocked lane with an auto-issue, clearable by a human OR an authorized agent per autonomy policy |
| 2026-11-14 | Grill fix: claim leases (TTL 30m cloud / 10m local, auto-renew, audited auto-release); each pipeline step a separate Actions job with ledger checkpoints |
| 2026-11-14 | Grill fix: story failure = 2-loop cap → BLOCKED + issue → disposition (accept/re-scope/reject); feature-gate fail → auto fix stories in Backlog, feature BLOCKED until gate re-passes |
| 2026-11-14 | Grill fix: Intake Engine = stateful component behind harness-agnostic protocol; Storybook exposure tiers LIVE/LINK/SCREENSHOT; demo in separate repo software-factory-demo (P5); onboarding = factory init [--guided]; drag-to-dispatch = P5 |
| 2026-11-14 | Grill fix: feature state = computed render (gate pass/fail are ledger events); board sync one-way ledger→board, drag = webhook→CLI trigger; self-host workspace at .factory/ |
| 2026-11-14 | Grill fix (Randy): measurement first-class — cycle time, cost, models used, all statistics per dispatch/story/feature; factory stats + dashboard + board fields; schema P1, metering P3, dashboard P5; Level-3 thresholds in P6 (≥3 features of data) |
| 2026-11-14 | Design review (Fable 5.2, issue #1) accepted: evidence pinned by tree hash + SHA under durable refs/factory/*; up-to-date-with-main + gate re-run before merge; squash tree = reviewed tree; human approval anchored in unforgeable GitHub objects + CODEOWNERS + no-workflows agent token; threat model + dependency gate + egress allowlist + secret scanning (P1) |
| 2026-11-14 | Design review accepted: dispatch trigger = /factory dispatch comment or factory:run label (App token); board drag-to-dispatch demoted to optional P6+ UX (projects_v2_item is org-only, not an Actions trigger — verified); factory inbox (P2); machine-vs-human cycle-time split + human-minutes-per-story headline metric; budget ceilings + factory pause; red-main auto-revert; tiered rework + contract-defect routing; upstream design/decomposition review gates; PRD versioning; maintained architecture doc; reduced-assurance review mode; hand-run story before P1 freeze; schema version from commit one |
| 2026-11-14 | Design review OPEN owner calls: OC-8 ledger write location (rec: dedicated ref + CAS + concurrency mutex), OC-9 merge policy (rec: auto-merge green expand-only/flagged stories, human at feature-acceptance), OC-10 escalation model (rec: deterministic decision classes + assumption log), OC-11 primary persona (rec: engineer-primary through P6, touchpoint profiles) |
| 2026-11-14 | OC-8 RATIFIED (Randy): state lives OUT of the product repo in a DEDICATED factory-state repo that spans projects, structured as an Obsidian vault (JSONL ledger = machine truth, generated markdown = human view); supersedes "ledger lives with the code"; evidence bound by repo@sha resolved against each product repo's object DB; CAS + per-story concurrency mutex; separate from the personal ~/Notes vault |
| 2026-11-14 | OC-9 RATIFIED (Randy): merge policy CONFIGURABLE per workspace (human-every-story / auto-merge-green-expand-only-with-human-at-feature-acceptance / full-auto-opt-in), alongside configurable Copilot review requirements (on = required gate input; off = factory panel owns the gate) and configurable remediation mode; controller-enforced policy schema in P1 |
| 2026-11-14 | OC-10 RATIFIED (Randy): deterministic decision-class escalation + recorded-assumption log with veto→rework; class list is extendable policy config |
| 2026-11-14 | OC-11 RATIFIED (Randy): engineering professionals are the target audience — enabling people like Randy to build software autonomously; supersedes non-developer-first as the primary target; architecture/data-model/decomposition approval gates first-class; touchpoints remain a profile |
| 2026-11-14 | OC-8 confirmed + extended (Randy): state vault is a NEW dedicated repo separate from ~/Notes; scoped to a person, team, or organization (sets ownership/visibility/dispatch+mine authority); tools mine the vault to see how things were built (provenance/decisions/patterns/cost history) — a queryable knowledge substrate; scope model P1, mining tools P6+ |
| 2026-11-14 | Round-3 feasibility fix pass (Randy agreed all): merge-integrity via git merge-tree (review the merge-result tree, no rebase after review, squash tree = reviewed merge-result tree — resolves the round-1 contradiction); per-story ledger files (workspaces/<name>/ledger/stories/<id>.jsonl) eliminate cross-story CAS contention + 3× backoff retry; cross-repo evidence validation protocol (repo@sha fetch, evidence-unreachable BLOCKED) + force-push liveness check; concrete App token boundary (contents/PR/issues write, no workflows, never a required approver, human-only CODEOWNERS); scope enforced via GitHub permissions; branch-protection rulesets per merge mode; claim-lease split-brain guards; inbox blocked_count ordering; state-repo bootstrap/discover-join; egress allowlist deferred to P6 (P3 accepted risk + compensating controls); pre-push secret scanning; two pre-freeze validations (single-story hand-run + two-story concurrency smoke test); no-specification-shell-freezes rule (example+schema+pseudocode) |