# Design review disposition — issue #1 (2026-11-14)

External review by Fable 5.2 (session run by Randy), scope: README + docs/
at commit e91d4a5. Dispositioned by Merlin with two verification steps the
review itself recommended:

1. The three "verify" platform claims were checked against GitHub's own
   documentation — **all three confirmed** (evidence below).
2. Every finding was cross-checked against the **MIE reference
   implementation** (the salvage source). The review only saw the new
   repo's docs; several concerns are already solved in the machinery we
   are carrying forward. Those are marked SALVAGE.

Disposition key: **ACCEPT** = folded into the design, owning phase named ·
**SALVAGE** = already solved in MIE; port the proven pattern ·
**OWNER-CALL** = new decision OC-8…OC-11 opened, recommendation given ·
**VERIFIED** = platform claim confirmed against docs.

---

## Section 1 — issues that will break the design as written

### 1.1 Reviewed code is not the code that merges — ACCEPT (P1 contract)

Confirmed real. Squash produces a new SHA; `refs/pull/N/head` is not
fetched by a fresh clone, so commit-SHA-only evidence fails portability.

Folded into the design:
- Evidence pinned by **tree hash AND commit SHA**.
- Branch must be **up to date with main** before merge (or merge queue);
  deterministic gates re-run on the merge result.
- Squash commit recorded with a check that **its tree equals the reviewed
  tree**.
- Durable evidence refs under `refs/factory/*`, fetched by ledger tooling.

Extends MIE's immutable `review_context` event (already pins full
base/reviewed SHAs + context-manifest SHA-256) — not a fresh invention.

### 1.2 Ledger write location — OWNER-CALL OC-8 (P1; shapes the schema)

Confirmed real. MIE keeps `factory/ledger/events.jsonl` in-repo and pushes
it with story work; serial single-story runs made that tolerable.
Trunk-based delivery + the deployability guard + concurrent appends +
lease-renewal pushes break it, exactly as the review says.

Recommendation (OC-8): dedicated orphan ref `refs/factory/ledger`; git's
non-fast-forward rejection as the compare-and-swap primitive for appends
and claims; an Actions `concurrency` group per story as the cloud mutex.
Lease TTL stays the liveness signal, not a push cadence. The ledger never
touches main; main keeps one commit per story.

### 1.3 Human approval can be forged — ACCEPT (P1) + partial SALVAGE

SALVAGE part: MIE's surface already makes `approve`/`answer` **human-only**
via GitHub issue comments with positive-only actor trust
(OWNER/MEMBER/COLLABORATOR + one allowlisted App); a bot can never answer
a human gate.

The core point still stands: the agent token can write the ledger, the
gate code, and the override file. Folded:
- Human approvals anchored in **GitHub objects the agent token cannot
  forge** — a human PR review/merge, or an Actions environment with
  required reviewers. The ledger records a reference; a gate verifies it
  through the API.
- **CODEOWNERS + branch protection** on control-plane paths
  (`.github/workflows/`, gate catalog, autonomy policy, override file).
- Agent token gets **no `workflows` permission**.

### 1.4 No threat model — ACCEPT (P1 contract list)

Confirmed absent. Folded:
- Threat-model document as a P1 deliverable.
- **Network egress allowlist** for agent jobs; keys **scoped per job**.
- Deterministic **new-dependency gate**: package exists, has age/usage,
  allowed licence, lockfile committed. New dependency = human touchpoint
  at Levels 1–2.
- Board-write = spend authorization: **who may dispatch is named**
  (positive-only actor trust, same as the command surface).
- **Secret-scanning gate before push.**

### 1.5 GitHub mechanics — VERIFIED (all three) + ACCEPT

- **GITHUB_TOKEN events don't trigger workflows** — confirmed (GitHub
  docs, "Triggering a workflow from a workflow"; the pull_request
  exception lands in approval-required state, not auto-run). SALVAGE: the
  MIE gateway already uses `actions/create-github-app-token@v3` — the App
  token pattern ports directly.
- **projects_v2_item is org-only and not an Actions trigger** — confirmed
  (GitHub webhook docs: Availability = organization; gh-aw#25336
  investigation re-confirmed Oct 2026). **Amendment:** the dispatch
  trigger becomes a `/factory dispatch` issue comment or a `factory:run`
  label (the proven MIE kickoff pattern, P3). Board drag-to-dispatch
  becomes an **optional later UX** (P6+) requiring an org-owned board +
  App webhook relay — it may be dropped. The vision's P5 line is amended
  accordingly.
- **Actions artifacts expire (90 days default)** — confirmed (GitHub
  retention docs). Evidence store decided in P1: durable refs/branch under
  `refs/factory/*` — not Actions artifacts, not product-tree bloat.

---

## Section 2 — the human will be the bottleneck

### 2.1 Serial behind the merge gate — OWNER-CALL OC-9

The sharpest finding: 20 stories = 20 interruptions contradicts the
Level 3 promise. Recommendation (OC-9): an **intermediate merge policy** —
stories that are expand-only or flagged with all gates green merge
automatically; the human approves at the **feature-acceptance gate**, the
release boundary where user-visible behavior ships. One human decision per
release, not per commit. Independent stories (no dependency edge) may
proceed while another waits at the gate — the claim lock is per story and
decomposition is already dependency-aware, so this is a bounded policy
change, not free-for-all concurrency.

Regardless of OC-9: **measure first** — cycle time split into machine time
vs waiting-on-human time; "human minutes per merged story" becomes a
headline metric (folded into §10).

### 2.2 No inbox — ACCEPT (P2)

`factory inbox`: one queue of everything waiting on the human, ordered by
how much downstream work each item blocks; decision cards (question,
options, agent recommendation, evidence links, consequence of silence);
pushed via GitHub assignment/mentions so phone notifications come free.
Agreed with the review: the single most valuable addition for the mission.

### 2.3 Confidence is not reportable — OWNER-CALL OC-10

Model self-reported confidence is poorly calibrated — accepted.
Recommendation (OC-10): escalation by **decision class, checked
deterministically** (irreversible actions, scope change vs PRD, new
dependencies, security-sensitive paths, budget overrun, reviewer
disagreement). Everything else proceeds on a **recorded assumption**; the
human reviews the assumption log when convenient; a veto creates a rework
story. Most blocking questions become non-blocking.

### 2.4 Escalation too early — ACCEPT

Folded: loop two retries on the **next model tier**; a failure classed as
a **contract defect routes back to the plan or PRD**, not the coder.
Blocker dispositions extended: **amend-spec** and **retry-at-higher-tier**
join accept / re-scope / reject.

### 2.5 Upstream gates + persona — ACCEPT (gates) + OWNER-CALL OC-11

Folded: engineering design, UI/UX design, test strategy, and story
decomposition get **fresh-context review + human approval touchpoints**
(architecture, data model, decomposition). Principle 15 ("Randy keeps the
architecture") becomes a gate, not a note.

Persona recommendation (OC-11): **engineer-primary through P6**;
touchpoints as a **profile**; the non-developer profile comes later
without a redesign. The two personas want different touchpoints; naming
the primary one now prevents a muddled default.

### 2.6 No path for changing requirements — ACCEPT (P1)

PRD is **versioned**; a gate flags in-flight stories whose pinned criteria
changed; amendments recorded as DECs with re-pin or re-scope.

---

## Section 3 — robustness and reliability (all ACCEPT; phases named)

| Item | Disposition | Lands |
|---|---|---|
| Budgets enforced, not just measured (hard ceilings per dispatch/story/feature/day, retry budget, job timeouts, `factory pause`) | ACCEPT | P1 contract, P3 enforcement |
| Test-gaming gate (deleted tests / new skips / fewer assertions fail; AC→named-test traceability fixed in plan) | ACCEPT | P1 gate spec, P3 live |
| Reviewer catch-rate calibration (seeded-defect runs) | ACCEPT | P6 |
| Factory regression suite (fixed stories, known outcomes, replay before process change; process + prompt version sealed into dispatch identity) | ACCEPT | P1 schema fields, P6 suite |
| Red main has no owner → auto-revert offending commit, story reopened | ACCEPT | P3 |
| Flag lifecycle (registry + auto cleanup story on feature acceptance) | ACCEPT | P1 schema, P5 live |
| Idempotent replay semantics (side effects = upserts keyed by dispatch id; replay resets branch to pinned base) | ACCEPT | P1 contract |
| Board drift (reconcile command; sync failure = visible state) | SALVAGE — MIE surface already reconciles human card moves; port + `factory board reconcile` | P2 |
| Cross-family review vs bring-your-own subscription → reduced-assurance mode, recorded as such in the review record | ACCEPT | P1 review-lane contract |
| Freeze contracts only after one hand-run story (human adapter); schema version on every ledger event from commit one | ACCEPT | P0/P1 |
| Greenfield lasts one story → maintained architecture + conventions doc, updated by a merge gate (pulled forward from deferred bootstrapping) | ACCEPT | P1 doc, P3 gate |

---

## Section 4 — on the review process itself

ACCEPT. This review is exactly the feasibility pass the two grill rounds
did not do (they tested consistency, by design). After OC-8…OC-11 close
and the amendments fold, a **round-3 grill** verifies the amended sections
in fresh context, cross-family.

## Owner calls — RATIFIED (Randy, 2026-11-14)

- **OC-8** — state lives OUT of the product repo in a **dedicated
  factory-state repo that spans projects, structured as an Obsidian vault**
  (JSONL ledger = machine truth; generated markdown = human view).
  Supersedes "ledger lives with the code." Evidence bound by repo@sha
  resolved against each product repo's object DB; CAS + per-story
  concurrency mutex. Kept separate from the personal ~/Notes vault (sync
  conflict). *One interpretation flagged, not blocking: read as a NEW state
  repo, not literally inside ~/Notes — confirmed at round-3 grill.*
- **OC-9** — **configurable**: merge policy (human-every-story /
  auto-merge-green-expand-only-with-human-at-feature-acceptance /
  full-auto-opt-in) **alongside Copilot review requirements (on/off) and
  remediation mode**, per workspace, controller-enforced. Amends the old
  blanket "Copilot review is never a gate" into a policy knob; the factory
  still owns the gate.
- **OC-10** — deterministic decision-class escalation + recorded-assumption
  log with veto→rework (as recommended).
- **OC-11** — **engineering professionals are the target audience**,
  enabling people like Randy to build software autonomously. Supersedes
  non-developer-first as the primary target; architecture/data-model/
  decomposition approval gates first-class; touchpoints remain a profile.

All folded into docs/vision.md and docs/open-calls.md. Round-3 grill of the
amended sections next. Nothing here reverses OC-1…OC-7; OC-8 deliberately
supersedes the kit's ledger-location law (owner's call), and OC-9 amends
merge granularity + the Copilot-review rule within OC-3/OC-4's policy
framework.