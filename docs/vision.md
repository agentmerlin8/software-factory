# Software Factory — Vision (consolidated 2026-11-14)

Status: 6 of 7 open calls ratified by Randy 2026-11-14 (see
[open-calls.md](open-calls.md)); OC-3 (branching) in discussion. Vision
grill still pending before build starts.

## 1. Goal

Build software from **idea to deployable artifact autonomously, involving the
human at the right steps** — the human answers what the AI cannot confidently
answer on its own. (Randy, 2026-11-13)

End state: a polished, open-source product where a **complete non-developer**
can describe the software they want, answer guided clarification questions,
watch the UI take shape as clickable wireframes, and receive working,
deployed software. Users bring their own model subscriptions; it runs at
home, in a home lab, or in a corporate environment. (Randy, 2026-10-18)

Success looks like:

- A user says "I want a to-do app" and the factory asks the right questions
  (platform, features, look), shows live Storybook wireframes, and iterates
  until the user validates the interface and rules.
- The validated description becomes a PRD → engineering design + UI/UX +
  test strategy → features → stories → merged PRs → CI/CD → deployable
  artifact, with full visibility on a GitHub board at every step.
- Human involvement is dial-able (three-level scale, §7); Level 3 — "only
  interrupt me when you can't answer confidently" — is the goal.
- Cost and quality are measured per stage, so model choices are data-driven,
  not vibes.

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

4. **The visibility layer** — GitHub Boards exclusively: features, stories,
   queue order, what's in development / done / waiting, at a glance.
   Customized board fields/views to mirror the factory lifecycle; the ledger
   stays machine truth, the board is a derived mirror. Drag-to-dispatch cloud
   agents is a target capability. (2026-11-13, 2026-10-18)

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
  ▼
Code (TDD) → build + story tests green → code review (fresh context,
  cross-model) → proof artifacts
  ▼
PR (review BEFORE the PR where possible) → human merge gate
  ▼
Feature branch integration → feature validation → main   (tentative, OC-3)
  ▼
CI/CD → deployable artifact → live proof → closeout
```

Human touchpoints by default: UI/Storybook approvals, PR merges,
escalations. At higher autonomy levels the first two become policy-gated
(§7); escalations always stay human.

## 5. Architecture sketch

Carried from the accepted workspace model (v0.3) + kit vision, adapted to
the rewrite:

```
software-factory repo        CLI · core agents · skills/process rules ·
                             templates · adapters · onboarding   (versioned)
   └─ workspace              control home for a project: bindings + config +
                             ledger + story records + dispatch packages
        └─ target repo(s)    product code · story branches · PRs · CI
                             (evidence pinned as repo@sha)
```

- **Factory repo** = this repo. One versioned home for the process; target
  repos are onboarded to it.
- **Workspace** = control home; binds one or more target repos (stories can
  span repos). Single-repo: control home in-repo (`factory/`); multi-repo:
  dedicated workspace repo. Ledger lives with the product — always.
- **Environments** = where a workspace runs (this machine / cloud runner /
  client). Per-env config: runtime, dispatch mechanism, models per tier,
  credential refs, limits. Environments resolve HOW, never WHAT.
- **Adapters** = execution bindings: hermes, copilot-cli, claude-code, codex,
  api-direct (OpenAI-compatible → Foundry/locked-down), human. The dispatch
  package (role + pinned inputs + expected outputs + stop rules) is the
  universal interface — same package through any adapter.
- **Deterministic control plane**: python3 stdlib + git + gh; controller,
  ledger, gates, renders, board sync. Never needs an AI — that's what makes
  human mode and portability real. AI only ever sits behind a dispatch
  package.
- **Cloud execution**: GitHub Actions–backed agent sessions (RATIFIED
  OC-2, 2026-11-14): the CLI triggers a workflow running an agent in a
  container with repo-scoped credentials; board drag triggers the same
  path. Adapter seam keeps other cloud runtimes swappable.

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
   escalate. Rubrics stop critic loops.
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
9. **Ledger = machine truth; repo = state.** Append-only events, evidence
   SHAs validated against the object DB, corrections are events never
   edits; sessions disposable, repo durable; push-per-gate; claim lock
   (one owner per story, handover events, fail-closed human override file).
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
    being built (2026-10-18).

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
- Level 3 requires a confidence/escalation contract: what counts as "can't
  answer confidently", how questions reach the human (board? issue? chat?),
  and what happens while waiting (BLOCKED first-class).
- Autonomy is earned with data: per-level metrics (intervention rate, defect
  escape rate, cost) gate promotion. Level 3 for a repo/class of work is a
  measured decision, not a flag flip.
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

## 10. Roadmap (candidate phases)

Candidate phases — order follows the accepted declarative-first principle;
each phase ends in something demonstrable.

- **P0 — Vision & contracts (now).** Vision grilled and approved; OC-3
  closed; feature backlog + board created; repo scaffolding. Storybook
  spike (OC-6, ratified) starts here.
- **P1 — Declarative core.** Workspace + environment config schemas,
  ledger schema, story lifecycle state machine, dispatch-package contract.
  No execution yet — the contracts everything else obeys. Storybook spike
  continues.
- **P2 — CLI read path + control plane.** `factory status/doctor`,
  controller/ledger/gates/renders ported genericized from the kit work;
  board sync (visibility first — Randy needs to SEE the work).
- **P3 — Execution seam.** One adapter end-to-end (Hermes local first):
  dispatch → agent session → artifacts → evidence → transitions. Then the
  GitHub Actions cloud adapter (OC-2 ratified). Parameter-driven model
  routing from day one. **P3 exit = dogfood cutoff (OC-5 ratified).**
- **P4 — Intake & Storybook.** Guided intake session (harness-agnostic
  protocol, Hermes first — OC-7 ratified), question flow, wireframe
  generation + exposure to the user (screenshot → live link), PRD
  generation. Builds on the P0/P1 spike results (OC-6 ratified).
- **P5 — Demo end-to-end.** To-do app from plain description to deployed
  artifact through the full pipeline at Level 1/2. This is the "something
  working" bar for going public.
- **P6 — Dogfood expansion.** Factory builds factory features (started at
  P3 exit per OC-5); autonomy-level policy + metrics; onboarding hardening
  + fresh-repo test-out; remaining adapters.
- **P7 — Polish for open source.** Non-developer getting-started, fork-and-
  adapt demo, scripted onboarding, docs; flip public.

## 11. Explicitly deferred

Written down so they don't get built early:

- **End-user hosting strategy** (free/cheap/paid hosting of the software the
  factory builds) — later-round concern; first round is the factory's
  workings. CI/CD integration for target repos comes with P5. (2026-11-13)
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

## 12. Decisions already locked (from the notes)

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
| 2026-11-14 | OC-4: autonomy levels = gate policy, one pipeline, measured promotion; Level 1 for factory's own build, Level 2 default for target repos after demo, Level 3 behind metrics + escalation contract |
| 2026-11-14 | OC-5: dogfood starts at P3 exit (one story end-to-end by the factory, ledger intact); new features through factory, control-plane changes structured-vibe until review lane proven on itself |
| 2026-11-14 | OC-6: Storybook intake spike early (P0/P1), screenshot-back first then live link, 2–3 model/adapter combos evaluated on a fixed script |
| 2026-11-14 | OC-7: harness-agnostic intake protocol, Hermes chat first implementation; end-user surface decided after demo |