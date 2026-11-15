# SKEL-1 — Walking skeleton + control arm: implementation plan

> **For Hermes:** execute phase by phase; dispatch coder/reviewer roles via
> the Hermes adapter; human gates are marked 🧑. Issue #3. OC-12/OC-13/OC-16.

**Goal:** the minimum factory that runs 5 real to-do stories end-to-end with
a control arm, and produces the go/no-go evidence against the kill criterion.

**Architecture:** Python 3 stdlib control plane (`factory/`) + git + gh.
Dispatch packages (markdown) are the universal execution interface; the
Hermes adapter (`hermes -z --usage-file`) is the one v1 execution binding.
JSONL ledger = machine truth; generated markdown = human view. Product repo
is separate from this control repo. Human merges every PR (mode 1).

**Tech stack:** Python 3.14 (stdlib only), git, gh, Node 26 + Vite + React +
TypeScript + Vitest (demo product), Hermes CLI (adapter).

**Verified foundations (do not re-verify):**
- `hermes -z "<prompt>" -m <model> --usage-file <path> -t ""` runs headless,
  writes token/cost/model JSON. Probe passed 2026-11-14 (qwen3.8-flash).
- Model pool (alibaba-token-plan): qwen3.8-max/flash, qwen3.7-max/plus,
  qwen4-max-preview, deepseek-v4-pro/-flash, deepseek-v4.1-flash, glm-5.2/5.3.
- EXP-1/2/3 results in docs/experiments/ — merge gate works on public Free.

---

## Phase 0 — Design doc + the one approval 🧑

**Objective:** one design document for the to-do demo (OC-13: one doc, one
approval). Randy approves before any story runs.

**Files:**
- Create: `runs/todo-demo/design.md`

**Content contract (the doc must contain):**
1. Product description: browser to-do app, local-first (localStorage), no
   backend. Plain description → this doc is the intake artifact for SKEL-1
   (full guided intake is SKEL-2).
2. The 5 stories, each a vertical slice with ≤6 acceptance criteria:
   - **TOD-1** Add a task (input + enter/button; empty input rejected;
     persists across reload)
   - **TOD-2** List tasks (newest first; empty state message; counts)
   - **TOD-3** Complete/uncomplete (toggle; visual state; persists)
   - **TOD-4** Delete task (remove; persists; undo NOT in scope)
   - **TOD-5** Filter view (all/active/completed; counts update; persists
     selection)
3. Architecture: Vite + React + TS, Vitest + Testing Library, localStorage
   persistence layer behind one module, no router, no state library.
4. Test strategy: unit tests for the store module; component tests per
   story; one Playwright-free smoke (Vitest + jsdom).
5. Definition of done per story: tests green, build green, one squash
   commit, human merge.

**Step 1:** write the doc. **Step 2:** present to Randy (🧑 approval gate —
the ONE design approval). **Step 3:** on approval, record
`design_approved` event in the ledger with Randy's approval reference
(issue comment or chat timestamp). Commit the doc.

**Acceptance:** Randy says approved; event recorded; doc committed.

---

## Phase 1 — Control-plane skeleton (TDD)

**Objective:** the minimum machinery to dispatch, meter, gate, and record.
Every module: failing test first, then implementation, then commit.

**Files (all under `factory/`, tests under `tests/`):**
- `factory/ledger.py` — JSONL append/read/validate
- `factory/dispatch.py` — package assembly + adapter invocation
- `factory/gates.py` — deterministic pre-review checks
- `factory/inbox.py` — GitHub issue creation (label + assignee)
- `factory/metrics.py` — usage harvest + comparison render
- `factory/cli.py` — `python -m factory <cmd>` entry
- `factory/adapters/hermes.py` — the one adapter
- `tests/test_*.py` — one per module
- `runs/todo-demo/` — ledger.jsonl, dispatch/, evidence/, metrics/

### Task 1.1 — Ledger schema v0 + append/read

**Schema v0 (every event):**
```json
{"schema": 0, "ts": "<iso8601>", "event": "<type>", "story": "TOD-N|null",
 "role": "coder|reviewer|controller|human|null",
 "repo": "owner/name", "sha": "<40-hex>|null",
 "model": "<id>|null", "tokens": {"in":0,"out":0}|null,
 "cost_usd": 0.0|null, "wall_s": 0.0|null, "human_min": 0.0|null,
 "outcome": "ok|fail|blocked|null", "detail": {}, "prev": "<sha256-of-prev-line>|null"}
```
Event types v0: `run_started`, `design_approved`, `story_planned`,
`dispatch_sealed`, `dispatch_started`, `dispatch_completed`, `gate_passed`,
`gate_failed`, `review_completed`, `pr_opened`, `human_merged`,
`story_done`, `defect_found`, `run_completed`, `correction`.

**Test:** append 3 events, read back, validate chain (`prev` hashes),
reject malformed row (missing schema/event/ts) with named error.
**Impl:** append-only file, fsync, hash chain. Read = parse + validate.
**Commit:** `feat(ledger): JSONL schema v0 + hash-chained append/read`

### Task 1.2 — Dispatch package assembly

**Test:** given a story file + design doc + role, produce a markdown package
with: role instruction, pinned inputs (story text, design excerpt, repo@sha),
expected outputs, stop rules, resume preamble. Package content is
deterministic (same inputs → same bytes → same sha256).
**Impl:** `dispatch.py:seal(story, role, inputs) -> Package` writes
`runs/todo-demo/dispatch/<story>-<role>-<n>.md`, records `dispatch_sealed`
with package sha256.
**Commit:** `feat(dispatch): deterministic package assembly`

### Task 1.3 — Hermes adapter

**Test:** mock subprocess; assert command line is
`hermes -z <package> -m <model> --usage-file <path> -t <toolsets> --yolo`
with `--in <product-repo>`; assert usage JSON parsed into ledger fields.
**Impl:** `adapters/hermes.py:run(package, model, workdir, usage_path)` →
subprocess, timeout (default 600s), capture exit + usage file, return
`DispatchResult`. Never passes state-repo write credentials (OC-14: the
adapter runs in the PRODUCT repo only).
**Commit:** `feat(adapter): hermes headless dispatch + usage harvest`

### Task 1.4 — Deterministic gates

**Test:** gate checks on a fixture product repo: (a) build green
(`npm run build` exit 0), (b) story's named tests green (`npx vitest run
<filter>`), (c) diff touches only the story's declared manifest, (d) no
secrets in diff (regex scan). Each failure names the check.
**Impl:** `gates.py:pre_review(workdir, story) -> GateResult`. Runs BEFORE
the LLM reviewer (Fable adoption #2).
**Commit:** `feat(gates): deterministic pre-review gate`

### Task 1.5 — Inbox

**Test:** mock gh; assert issue created with `factory-inbox` label +
assignee + story link. **Impl:** `inbox.py:escalate(story, reason, evidence)`
→ `gh issue create`. v1 inbox = issues (OC-13).
**Commit:** `feat(inbox): labeled-issue escalation`

### Task 1.6 — Metrics + comparison

**Test:** given two ledger runs (factory, control), render per-story table:
tokens, wall, human-min, defects, cost; compute process-overhead-ratio
(non-coder tokens / coder tokens). Nulls render "not recorded", never 0.
**Impl:** `metrics.py:compare(factory_ledger, control_ledger) -> markdown`.
**Commit:** `feat(metrics): per-story comparison + overhead ratio`

### Task 1.7 — CLI wiring

**Commands v0:** `status`, `doctor`, `dispatch <story> <role>`,
`gate <story>`, `inbox <story> <reason>`, `metrics`.
**Test:** `status` on empty ledger refuses (fail-closed, not BACKLOG);
`doctor` checks gh auth, node, product repo reachability.
**Commit:** `feat(cli): status/doctor/dispatch/gate/inbox/metrics`

**Phase 1 acceptance:** `python -m factory doctor` all-green; unit tests
pass; a dry-run dispatch of a fixture story produces a sealed package +
ledger events without calling a model (adapter mocked).

---

## Phase 2 — Product repo + the 5 stories (factory arm)

**Objective:** run TOD-1…TOD-5 through the pipeline. Human merges each.

**Files:**
- Create repo: `agentmerlin8/factory-todo-demo` (public — matches factory
  repo visibility; EXP-3 gate available)
- `runs/todo-demo/ledger.jsonl` (events accumulate)
- `runs/todo-demo/evidence/TOD-N/` (packages, usage, gate results, reviews)

### Task 2.1 — Scaffold (controller, not a story)

Vite + React + TS + Vitest scaffold, localStorage store module skeleton,
CI workflow (build + test on PR), branch protection with a REAL required
check (`ci` — EXP-3 gotcha: empty checks list = no-op). One commit, human
merge (🧑 gate #2). Record `run_started`.

### Task 2.2 — Per-story loop (repeat ×5)

For each TOD-N:
1. **Plan** (controller assembles; coder model drafts impl-plan from the
   design doc slice) → `story_planned`.
2. **Dispatch coder** (pin: qwen3.8-max; toolsets: terminal,file; workdir:
   product repo; branch `tod-N` from main). Package = story + design slice +
   manifest + TDD contract. → `dispatch_sealed/started/completed` + usage.
3. **Gate** (deterministic: build, tests, manifest, secrets). Fail → inbox
   + retry once → still fail → BLOCKED. → `gate_passed/failed`.
4. **Update-before-review:** merge main into `tod-N` (OC-15).
5. **Dispatch reviewer** (pin: deepseek-v4-pro — CROSS-FAMILY vs coder;
   fresh context: sees ONLY the diff + story + design slice, never the
   coder's reasoning). Verdict PASS/PASS-WITH-NITS/FAIL. → `review_completed`.
6. **PR open** (gh, from `tod-N`), required check green. → `pr_opened`.
7. 🧑 **Human merge gate** — Randy merges (mode 1). Controller verifies
   squash tree == reviewed head (EXP-1 alarm). → `human_merged`, `story_done`.
8. **Meter:** harvest usage JSON → ledger; record wall + human-min
   (human-min = time from PR-open to merge, measured).

**Loop rules (Fable adoptions):** max 2 revision loops per stage; loop tags
mechanical/reasoning/contract/nit; nit fixes don't consume a loop; escalation
after 2 failures → inbox issue.

### Task 2.3 — Defect log

Every reviewer finding + every post-merge defect → `defect_found` event
with severity + caught-by (gate/reviewer/human/post-merge). This feeds the
kill-criterion comparison.

**Phase 2 acceptance:** 5 stories merged; ledger complete; evidence dirs
populated; per-story metrics recorded.

---

## Phase 3 — Control arm

**Objective:** same 5 stories, ONE coding-agent session, no factory.

**Files:**
- Create repo: `agentmerlin8/factory-todo-control` (public)
- `runs/todo-control/ledger.jsonl`

### Task 3.1 — Single-session run

One `hermes -z` dispatch (pin: qwen3.8-max, same as factory coder): package
= the SAME design doc + all 5 stories + "implement all five, TDD, commit per
story". One session, no plan review, no cross-family review, no gates beyond
the repo's own CI. Human merges the result (🧑 gate, same as factory arm).
Meter identically (usage file, wall, human-min).

**Fairness rules:** same model, same design doc, same stories, same human
merge policy. The ONLY difference is the factory process. Record any
clarifying questions the control session asks (human-min cost).

**Phase 3 acceptance:** control arm complete; ledger + metrics recorded.

---

## Phase 4 — Comparison + go/no-go 🧑

**Objective:** the kill-criterion decision (OC-16).

### Task 4.1 — Render comparison

`python -m factory metrics` → per-story table (factory vs control):
human-minutes, escaped defects, tokens, cost, wall. Headline:
process-overhead-ratio. Write `runs/todo-demo/COMPARISON.md`.

### Task 4.2 — Present to Randy (🧑 decision gate)

Report: does the factory win on human-minutes OR defects at an acceptable
cost multiple? Randy sets the acceptable multiple. **If no → STOP and
reconsider (kill criterion). If yes → SKEL-2.** Record `run_completed` +
the decision.

**Phase 4 acceptance:** COMPARISON.md committed; decision recorded; issue
#3 closed with the verdict; board Done.

---

## Explicitly OUT of scope (OC-13 cuts — do not build)

Cloud adapter; merge modes 2/3; claim leases; team/org scope; mining;
multi-repo; flag registry; board custom fields; wireframe tiers; Copilot
knobs; PRD-versioning gate; 4 design approvals; Obsidian renders beyond one
status file. Intake is a static doc here (guided intake = SKEL-2).

## Risks / open items

- **Cost cap:** provider-side spend cap must be set BEFORE Phase 2 (Randy
  confirms the ceiling; record it in the ledger `run_started`).
- **Human-min measurement:** PR-open→merge wall time is a proxy; Randy's
  actual review time is logged manually per story (one number, asked once).
- **Reviewer family:** deepseek-v4-pro vs qwen coder = cross-family ✓. If
  pool routing fails, fall back to glm-5.3 (still cross-family) and record
  the substitution.