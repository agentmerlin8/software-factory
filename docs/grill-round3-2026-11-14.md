# Software Factory Vision — Round-3 Feasibility Grill

**Grill type:** Cross-family fresh-context feasibility review (DeepSeek-family reviewer, Qwen-family author)
**Documents reviewed:** vision.md, open-calls.md, design-review-disposition-2026-11-14.md, lineage.md
**Ratified decisions tested (not re-litigated):** OC-8, OC-9, OC-10, OC-11 + all prior OC-1…OC-7
**Date:** 2026-11-14

---

## DIMENSION 1: STATE-REPO MECHANICS (OC-8)

**1.1 — Cross-repo evidence validation protocol is unspecified** — severity: **blocker** — root_cause: feasibility_gap — timing: fix-before-P1-freeze
- Detail: The design states "every event pins `repo@sha`; validation resolves each SHA against THAT product repo's object database" and "Evidence refs live under a durable `refs/factory/*` namespace that ledger tooling fetches." But the state-repo ledger and the product-repo evidence refs live in DIFFERENT repositories. A fresh clone of the state repo has NO access to product-repo SHAs. The validation protocol — step by step: what is fetched, from where, in what order, how failures surface, whether the validator needs all product repos cloned or fetches objects on demand — is absent. A P1 builder given only the vision text must invent the entire cross-repo evidence validation mechanism. In the MIE reference implementation, the ledger and evidence were co-located in one repo; this cross-repo model is new and untested.
- Recommended decision: Specify the validation protocol as a concrete sequence: (1) read ledger entry for `repo@sha`, (2) `git fetch <product-repo> <sha>` (or verify if already present), (3) resolve `refs/factory/<story-id>/*` from the product repo for evidence artifacts, (4) surface missing-object errors as BLOCKED with `evidence-unreachable` reason. State that the validator requires network access to all referenced product repos (or a cached clone). Freeze this as a P1 contract section.
- Exact document edit: vision.md §5 "Evidence binding across repos" paragraph — add the step-by-step validation protocol. Also add to the P1 freeze list in §11 under "evidence integrity."

**1.2 — CAS retry semantics for cross-story ledger contention are missing** — severity: **blocker** — root_cause: feasibility_gap — timing: fix-before-P1-freeze
- Detail: The design uses two-tier concurrency: Actions `concurrency` group per story (serializes within a story) + git non-fast-forward rejection as CAS (serializes across stories). But the concurrency group is PER STORY — two jobs for different stories racing on the same monolithic ledger file WILL collide. Git non-fast-forward rejection causes one push to fail, but the design never specifies: (a) what the retry mechanism is (built-in loop in the CLI? Actions job re-run?), (b) retry count and backoff, (c) what happens when retries are exhausted (BLOCKED with a CAS-contention reason? Silent drop?). Without this, a P1 builder must invent the retry protocol, and the wrong choice (e.g., no retry, just fail) makes multi-story pipelines break under any real load.
- Recommended decision: Specify: CLI retries non-fast-forward pushes up to 3 times with exponential backoff (1s, 2s, 4s); exhaustion → story enters BLOCKED with `cas-contention` reason surfaced in the inbox. Or, alternatively, design the ledger as per-story files (`ledger/stories/<story-id>.jsonl`) so cross-story appends never contend — only claim leases on the same story collide. The per-story file design is simpler and avoids the CAS-contention surface entirely; recommend that.
- Exact document edit: vision.md §5 "Ledger write location" paragraph + §11 P1 contract list "ledger schema" — specify whether the ledger is one monolithic file or per-story files; specify CAS retry semantics.

**1.3 — Person/team/org scope model has no enforcement mechanism** — severity: **major** — root_cause: document_ambiguity — timing: P1-contract
- Detail: OC-8 says "the state vault can be scoped to a person, a team, or an organization. That scope sets ownership and visibility of the state and who may mine it." The design describes scope as a label, but labels don't enforce. Is enforcement via GitHub repo visibility (private = person, team-owned = team, org-owned = org)? Or is it a config field in the workspace policy that the controller enforces by checking actor identity against GitHub API? The natural mechanism is GitHub repo permissions — the state repo's visibility and collaborator set IS the scope enforcement. But the design doesn't connect the scope model to GitHub's permission model. A builder would invent an ad-hoc scope system that might not align with GitHub's actual access controls.
- Recommended decision: Scope enforcement = the state repo's GitHub visibility and collaborator/team permissions. A `person` scope = a private repo with one collaborator. A `team` scope = a private repo shared with a GitHub team. An `org` scope = an internal/private org repo. The `scope` field in workspace config is declarative (records intent); the controller validates it against the GitHub API on `factory doctor`. Freeze this binding in P1.
- Exact document edit: vision.md §5 "Scope + mining" paragraph — add the GitHub-permission binding. Also add "scope enforcement" to the P1 contract list under "factory-state repo layout (OC-8)."

**1.4 — Product-repo force-push breaks ledger SHAs silently** — severity: **major** — root_cause: feasibility_gap — timing: P1-contract
- Detail: If a product repo receives a force-push (rewriting history), SHAs pinned in the state-repo ledger become dangling — they no longer resolve in the product repo's object database. The design includes no mechanism to detect or surface this. Since the product repo holds only code (not factory state), a force-push is a normal git operation that could happen (e.g., fixing a bad merge, cleaning history). The ledger would silently reference nonexistent objects, and provenance queries would fail with opaque git errors. This is a real failure mode that needs a detection gate.
- Recommended decision: `factory doctor` includes a `--deep` check that validates all ledger SHAs resolve in their referenced product repos; unresolvable SHAs produce warnings. The board sync tool checks the most recent N story SHAs on each sync. Not a blocking gate (force-pushes are rare and often intentional), but a visibility/audit concern.
- Exact document edit: vision.md §5 "Evidence binding across repos" — add a sentence about SHA-liveness checking. Add to P2 `factory doctor` spec.

**1.5 — State-repo outage mid-story has no specified behavior** — severity: **minor** — root_cause: acceptable_gap — timing: later-phase
- Detail: If the state repo is unreachable during a pipeline step, the agent job can't checkpoint. The design implies jobs are idempotent (replay resets), but doesn't specify whether the job fails immediately, buffers locally, or retries. Since GitHub and the state repo are both on GitHub.com, a state-repo outage likely coincides with an Actions outage, making this a correlated failure. Acceptable gap for now; the idempotent-replay semantics cover recovery. Specify behavior in P3 when cloud execution is built.
- Recommended decision: State-repo push failures are retried 3 times; exhaustion → job fails with `state-repo-unreachable` exit code; the dispatch is replayable. Freeze in P3.
- Exact document edit: P3 contract list — add state-repo reachability semantics.

---

## DIMENSION 2: EVIDENCE + MERGE INTEGRITY

**2.1 — "Squash tree equals reviewed tree" contradicts "up to date with main"** — severity: **blocker** — root_cause: contradiction — timing: fix-before-P1-freeze
- Detail: This is the most consequential finding. The design states: (a) "the branch is brought up to date with main and the deterministic gates re-run on the merge result" AND (b) "the squash commit's tree is verified equal to the reviewed tree." These cannot both be true when main has advanced. Sequence: branch HEAD at tree T1 is reviewed → branch is rebased/merged with main (now at a later commit) → result tree T2 differs from T1 (main's changes are incorporated) → squash produces tree T2 → check "T2 == T1" FAILS. The only scenarios where T2 == T1 are: (a) main hasn't changed (the update is a no-op, making the step pointless), or (b) the update is a fast-forward rebase with zero conflicts and the main changes don't touch any files the branch touched (possible but not guaranteed). The design has a real logical contradiction that a builder cannot resolve without guidance.
- Recommended decision: Resolve by redefining "reviewed tree" for the purpose of this check: the tree that matters is the tree AFTER updating with main and re-running deterministic gates. The adversarial review happened on a tree that is a SUBSET of the final tree (the branch's own changes). The check becomes: "the squash tree equals the tree on which deterministic gates last passed; any merge-result delta from main is only from main commits, verified by `git diff main...squash` matching the reviewed branch's diff." Alternatively: use `git merge-tree` to compute the merge result BEFORE review, review THAT tree, and then the squash match is direct. Recommend the merge-tree approach: compute the merge result tree first, review that tree, never rebase after review — only verify main hasn't advanced past the merge base before merging. This eliminates the contradiction entirely.
- Exact document edit: vision.md §4 flow diagram (update the merge gate step) + §5 "Evidence integrity" paragraph + §11 P1 "evidence integrity" bullet. Replace "squash tree verified equal to the reviewed tree" with the resolved semantics.

**2.2 — Evidence refs under refs/factory/* require explicit fetch configuration** — severity: **major** — root_cause: document_ambiguity — timing: P1-contract
- Detail: The design correctly notes that `refs/pull/*` is not fetched by a fresh clone and switches to `refs/factory/*`. However, `refs/factory/*` is also a non-standard ref namespace — a fresh clone does NOT fetch it by default. The design says "ledger tooling fetches" but doesn't specify HOW: is it a `git fetch origin '+refs/factory/*:refs/factory/*'` refspec baked into the CLI? Is it configured as a remote fetch refspec in the product repo? If the latter, every product repo must have this refspec configured, which is an onboarding step not mentioned anywhere. A builder would guess; the wrong guess breaks evidence portability.
- Recommended decision: The CLI auto-configures the fetch refspec on `factory init` by running `git config --add remote.origin.fetch '+refs/factory/*:refs/factory/*'` in the product repo. The state-repo ledger tooling uses `git fetch origin '+refs/factory/<story-id>/*'` for targeted fetches. Specify this in P1.
- Exact document edit: vision.md §5 "Evidence integrity" — add the refspec configuration step. Add to the P1 "evidence integrity" contract bullet.

**2.3 — Tree-hash pinning across a squash merge is underspecified** — severity: **major** — root_cause: document_ambiguity — timing: P1-contract
- Detail: The design says evidence is pinned by "tree hash AND commit SHA." For a squash merge: the original branch commits have tree hashes T1, T2, ... Tn; the squash produces one commit with tree hash T_squash. The design says "squash tree verified equal to the reviewed tree." But WHICH reviewed tree? The branch tip tree? The merge-result tree? And where are these tree hashes stored — in the ledger event, in the `refs/factory/*` ref? The interaction between tree-hash pinning and git's tree object model (trees don't carry parent history) means the tree equality check can only verify content, not history. This is correct for the intent (verify the code content didn't change), but the exact objects being compared must be named.
- Recommended decision: The ledger records TWO tree hashes per successful merge: `reviewed_tree` (the tree at branch HEAD when review completed) and `merge_tree` (the tree produced by merging/rebasing onto main). The gate verifies `merge_tree == squash_tree`. The evidence chain links `reviewed_tree` → `review_context` event → `merge_tree` → `squash_commit`. The `reviewed_tree` and `merge_tree` deltas are attributable to main-line changes only. Freeze this object model in P1.
- Exact document edit: vision.md §5 "Evidence integrity" — specify the two-tree model with explicit field names.

---

## DIMENSION 3: SECURITY

**3.1 — "Agent token cannot forge" claim is hand-waved without a concrete permission boundary** — severity: **blocker** — root_cause: feasibility_gap — timing: fix-before-P1-freeze
- Detail: The design claims human approval is tied to "a GitHub object the agent token cannot forge" and that the "agent token carries no `workflows` permission." But it never enumerates what the token DOES carry. A GitHub App token with `contents: write` and `pull_requests: write` CAN: create commits, push branches, open/update PRs, create PR reviews, and — critically — potentially APPROVE PRs if the App installation is configured to allow it. The design doesn't specify that the App MUST NOT have PR approval capability, nor does it specify the exact App permission set. Without a concrete permission boundary, the "cannot forge" claim is aspirational. A builder configuring the App would need to know exactly which permissions to grant and which to deny. Furthermore, the CODEOWNERS + branch protection defense assumes branch protection blocks the App from approving, but branch protection's "require review from CODEOWNERS" is a branch-level setting — the App could be a CODEOWNER if it's listed in the CODEOWNERS file, creating a self-approval path.
- Recommended decision: Freeze the exact GitHub App permission set in P1: `contents: write`, `pull_requests: write` (for PR creation/update only, NOT review approval), `issues: write` (for board sync and inbox mentions), `metadata: read`. Explicitly document that the App MUST NOT have `pull_requests: write` scoped to include review approval; if the GitHub API doesn't separate these, use a separate machine user or accept that a compromised agent could approve and rely on the audit trail. Add: CODEOWNERS file is itself protected by branch protection (the App cannot push to the CODEOWNERS path on main), and the CODEOWNERS file lists only human GitHub handles.
- Exact document edit: vision.md §5 "Human approval anchoring" — add the concrete token permission set. Add to P1 threat model deliverable.

**3.2 — Actions environment required reviewers gate deployment, not merge** — severity: **major** — root_cause: document_ambiguity — timing: P1-contract
- Detail: The design mentions "an Actions environment with required reviewers" as a human-anchoring mechanism alongside "human PR review/merge." But Actions environment required reviewers gate DEPLOYMENTS to that environment — they don't gate PR merges and don't gate code landing on main. If the intent is to use environments to gate agent dispatch (a human must approve before an agent job runs against a protected environment), that works and is useful. But the text places it as a peer to PR review/merge for human approval anchoring, which muddies the concept. The two mechanisms serve different purposes: PR review = human approves code; environment approval = human approves agent execution. They are both valid human-anchoring mechanisms but for different transitions.
- Recommended decision: Clarify the two distinct uses: (1) human PR review/merge anchors the code-merge gate; (2) Actions environment required reviewers anchor the agent-dispatch gate (a human must approve before an agent session starts against a protected environment, e.g., production deployments or Level 2→3 transitions). Specify which gates use which mechanism.
- Exact document edit: vision.md §5 "Human approval anchoring" — separate the two mechanisms with distinct purposes. Map each to specific gates in the transition catalog.

**3.3 — Egress allowlist on GitHub-hosted runners is not a native capability** — severity: **major** — root_cause: feasibility_gap — timing: P1-contract
- Detail: The design states "Agent jobs run behind a network egress allowlist with keys scoped per job." GitHub-hosted runners do not support network egress filtering. To implement this, you must either: (a) use self-hosted runners with network policies, (b) run a proxy sidecar in the Actions job that filters egress, or (c) use a cloud runner provider that supports egress controls (Azure, etc.). The design's adapter seam makes the runtime swappable, but the vision implies this is a standard capability of the GitHub Actions adapter. It is not. The threat model deliverable must address this explicitly, or the requirement must be scoped to "where the runner platform supports it."
- Recommended decision: For P3 (first cloud execution): use GitHub-hosted runners WITHOUT egress allowlist; rely on per-job credential scoping and the secret-scanning gate. Add egress allowlist as a P6 hardening item requiring self-hosted runners or a proxy sidecar. Document this as an accepted risk in the P1 threat model.
- Exact document edit: vision.md §5 "Security posture" — note that egress allowlist requires self-hosted or proxy-capable runners. Add to P1 threat model scope: "Identify which security controls are available on GitHub-hosted runners vs require self-hosted; document the P3 accepted-risk posture."

**3.4 — Secret-scanning gate before push is feasible but location is ambiguous** — severity: **minor** — root_cause: document_ambiguity — timing: P1-contract
- Detail: The design says "secret-scanning gate before push." On GitHub, secret scanning runs post-push (push protection) or on a schedule. A pre-push gate would need to run locally or in the CI job BEFORE `git push`. This is doable (run gitleaks/trufflehog in the agent job before pushing the branch), but the design should specify WHERE it runs: in the agent's coding session (pre-push hook or explicit step) or as a CI check that blocks the PR. The former prevents secrets from ever reaching GitHub; the latter catches them post-push. Given the security posture, pre-push is correct but needs the execution location named.
- Recommended decision: Secret scanning runs as a deterministic gate in the agent's coding session before branch push (pre-push, not post-push CI). If secrets are detected, the story fails the gate and the agent must remediate. Freeze the tool choice (gitleaks or trufflehog) in P1.
- Exact document edit: vision.md §5 "Security posture" + P1 contract list "secret scanning" — specify pre-push location + tool.

---

## DIMENSION 4: HUMAN-ATTENTION ECONOMICS

**4.1 — Level 3 promise is reachable WITH the engineer profile but requires explicit scope** — severity: **minor** — root_cause: acceptable_gap — timing: later-phase
- Detail: Counting mandatory human touchpoints for a 20-story feature under OC-9 mode 2 (auto-merge expand-only/flagged, human at feature-acceptance) with the engineer touchpoint profile (OC-11):
  - Intake/wireframe approval: 1 (PRD sign-off)
  - Architecture/design gates (principle 15): engineering design review + UI/UX review + test strategy review + decomposition review = 4 per feature
  - Per-story merges: 0 (auto-merge under mode 2 when gates are green)
  - Feature-acceptance gate: 1
  - Escalations: variable (stories that hit decision-class triggers or 2-loop cap)
  Total: ~6 mandatory touchpoints for the feature (not per story). This is manageable. Under Level 3 with full-auto-merge (mode 3), the merge and feature-acceptance gates could also be automated, leaving only intake + architecture approvals + escalations. The Level 3 promise "only interrupt me when you can't answer confidently" maps cleanly to OC-10 decision-class escalation: the human is interrupted for irreversible actions, scope changes, new dependencies, security-sensitive paths, budget overruns, and reviewer disagreement. Architecture approvals (principle 15) are BY DESIGN for the engineer persona — the engineer WANTS to approve architecture. This dimension is sound.
- Recommended decision: Document the expected touchpoint count per feature under each policy mode so users can make informed choices. Not a design change.
- Exact document edit: None required. Note for the inbox/statistics: measure actual vs expected touchpoints.

**4.2 — Inbox ordering algorithm ("how much downstream work each item blocks") is computationally underspecified** — severity: **major** — root_cause: document_ambiguity — timing: P1-contract
- Detail: The design says the inbox is ordered by "how much downstream work each item blocks." This is a graph-traversal problem on the story dependency DAG. But the exact metric is unspecified: number of blocked stories? Total story points blocked? Cycle-time impact? Without specification, the P2 builder must invent an ordering algorithm, and different choices produce very different inbox experiences. The inbox is called "the single most valuable addition for the mission" (design review 2.2) — it deserves a concrete algorithm.
- Recommended decision: Order by `blocked_count` = the number of stories that are transitively blocked (direct + indirect dependencies) by this item. Tiebreak by creation time (oldest first). This is simple, computable from the story dependency graph, and directly answers "what should I look at first to unblock the most work." Freeze in P1; implement in P2.
- Exact document edit: vision.md §3 bullet "The inbox" — add the ordering algorithm. Add to P1 "story schema" (dependencies must be recorded for this to work).

---

## DIMENSION 5: GITHUB PLATFORM REALITY

**5.1 — App token event triggering claim is verified and sound** — severity: none — root_cause: verified — timing: n/a
- Detail: The design's use of GitHub App tokens (not GITHUB_TOKEN) to trigger downstream workflows is correct and verified against GitHub documentation in the disposition. No issue.

**5.2 — Concurrency group per story leaves cross-story CAS contention unaddressed** — severity: **blocker** — root_cause: feasibility_gap — timing: fix-before-P1-freeze
- Detail: The Actions `concurrency` group serializes jobs within a story. But the ledger file is shared across ALL stories. When Story A and Story B both finish a gate simultaneously and try to append to the same ledger file, the concurrency groups don't serialize them (they're different stories). The git non-fast-forward CAS causes one to fail, but as noted in 1.2, the retry semantics are unspecified. If the ledger is one monolithic file, this contention grows with pipeline throughput. If the ledger is per-story files (as recommended in 1.2), this problem disappears — only claim-lease updates for the same story contend, and the per-story concurrency group already serializes those.
- Recommended decision: Couple this with finding 1.2. The ledger file layout decision (monolithic vs per-story) directly determines whether this is a blocker. Per-story files eliminate cross-story CAS contention entirely and are the recommended design.
- Exact document edit: See 1.2 edits. If per-story files are chosen, note here that cross-story CAS contention is resolved by design.

**5.3 — Branch protection requirements for auto-merge are unspecified** — severity: **major** — root_cause: document_ambiguity — timing: P1-contract
- Detail: For OC-9 mode 2 (auto-merge green expand-only/flagged stories), the agent must merge the PR. GitHub branch protection can require PR reviews, status checks, and branches to be up to date. If branch protection requires "1 approving review," the agent (as PR author) cannot approve its own PR — even with an App token. The auto-merge path would be blocked waiting for a human review that the policy says shouldn't be needed. The resolution is: branch protection must be configured to NOT require PR reviews and instead require specific status checks (the factory's review gate status check). The design doesn't specify this, and a builder who sets up standard branch protection would break auto-merge.
- Recommended decision: Specify the exact branch protection ruleset per merge policy mode. Mode 1: require 1 human PR review + status checks. Mode 2: require status checks only (no PR review requirement); the factory review gate IS the approval. Mode 3: require status checks only. `factory init` auto-configures branch protection via the GitHub API. Freeze the rulesets in P1.
- Exact document edit: vision.md §5 "Workspace policy config (OC-9)" — add branch protection rulesets per mode. Add to P1 contract list under "workspace policy schema."

**5.4 — GitHub Projects V2 board field writes via API require organization-level permissions** — severity: **minor** — root_cause: feasibility_gap — timing: later-phase
- Detail: The board sync tool writes custom fields (Stage, Tokens/cost, Model(s) used, Cycle time) on project items. The GitHub Projects V2 GraphQL API for updating fields requires `project` scope permissions that are organization-level. For a personal repository, the `projects` scope is available to user-owned projects. For the factory's own development board (on the private `software-factory` repo), this works. But the design mentions it in the context of target product repos — those may not have Projects V2 enabled at the right scope. This is noted in the design's own caveat about `projects_v2_item` being org-only for webhooks, but the WRITE path (GraphQL mutations) has similar scope constraints. Not a blocker (the board is a visibility layer, and CLI→board sync can fall back to issue labels/comments if Projects V2 isn't available), but the board minimum schema's custom fields may not be writable in all contexts.
- Recommended decision: `factory board sync` detects whether the target project's board is writable via GraphQL. If not, it falls back to issue labels + body updates for Stage tracking. The custom fields (Tokens/cost, Model, Cycle time) are recorded in the ledger regardless; board fields are best-effort. Document the fallback in P2.
- Exact document edit: vision.md §3 "Board minimum schema" — add a note on GraphQL scope requirements and the fallback. Add to P2 board sync spec.

**5.5 — Claim lease renewal via Actions job pushes is feasible but has edge cases** — severity: **major** — root_cause: feasibility_gap — timing: P1-contract
- Detail: The design says claim leases auto-renew and auto-release. In a GitHub Actions job, renewal means the job periodically pushes a lease-renewal event to the state-repo ledger. Each push is a git operation with network latency. The 30-minute cloud TTL provides ample margin. But: (a) if the Actions job is compute-bound and doesn't yield for renewal, the lease could expire mid-computation; (b) if the state repo is unreachable, renewal fails, and the lease auto-releases even though the job is still running (split-brain: job thinks it owns the claim, but the lease has expired, and another job could acquire it). The design doesn't address the split-brain scenario or specify whether the job checks lease validity before every side-effect operation.
- Recommended decision: (1) Lease renewal runs on a background timer (separate thread/process), not dependent on the main agent loop yielding. (2) Before every side-effect operation (branch push, PR open/update), the job verifies its lease is still valid by checking the ledger; if expired, the job fails immediately with `lease-expired`. (3) The lease TTL includes a grace period (TTL + 2× renewal interval) to cover clock skew. Freeze these semantics in P1.
- Exact document edit: vision.md §5 "Claim leases" — add renewal-background-thread + pre-side-effect validation + grace period. Add to P1 "claim-lease semantics."

---

## DIMENSION 6: P1 FREEZE READINESS

**6.1 — The P1 contract list is comprehensive but several items are specification shells** — severity: **blocker** — root_cause: feasibility_gap — timing: fix-before-P1-freeze
- Detail: The P1 freeze list names ~20 items. Many are concrete (story schema fields, transition catalog shape, model-routing roles×tiers). But several are specification shells — a name with no internals — and a P1 builder given only the shell must invent the entire design. Specifically:
  - **"Complete transition catalog"** — named but not even a sample tuple is provided. The builder must derive every state, event, gate type, and autonomy override from the flow diagram in §4 and the principles. This is >50 tuples; getting them wrong breaks the state machine.
  - **"Factory-state repo layout"** — says "dedicated state repo as an Obsidian vault, per-project workspaces" but doesn't specify the directory tree. Where do ledger files live relative to workspace dirs? Is there a top-level `ledger/` or `workspaces/<name>/ledger/`? The builder must decide.
  - **"Idempotent-replay semantics"** — says "upserts keyed by dispatch id" but doesn't specify the idempotency key format, the upsert target (branch? PR? issue? all of them?), or the reset procedure.
  - **"PRD versioning + changed-criteria gate"** — names the concept but doesn't specify how PRD versions are tracked (separate file? ledger events? git tags?), how a story pins its ACs to a PRD version, or the gate algorithm.
  - **"Test-gaming gate"** — says "deleted tests / new skips / fewer assertions fail" but doesn't specify the diff algorithm (compare test file tree before/after? count assertions?), the baseline, or the failure threshold.
- Recommended decision: Before freezing P1 contracts, promote these specification shells to full contracts with at minimum: (a) a concrete example, (b) the data schema, (c) the validation rule in pseudocode. The P0 "run one story by hand" step must exercise at least the transition catalog, story schema, and evidence integrity — these are the highest-risk shells.
- Exact document edit: vision.md §11 P1 bullet list — for each under-specified item, either expand inline to a paragraph or reference a separate contract document to be written before P1 freeze.

**6.2 — "Run one story by hand before freezing" does not de-risk concurrency or cross-repo evidence** — severity: **major** — root_cause: feasibility_gap — timing: fix-before-P1-freeze
- Detail: Running one story by hand (P0 step) de-risks the story schema, the transition catalog for a single linear path, and basic evidence pinning. It does NOT de-risk: CAS contention (needs ≥2 concurrent stories), cross-repo evidence validation (needs the state repo separate from the product repo), claim lease renewal (needs a long-running job), or the inbox ordering (needs multiple blocked items). Several of the findings above (1.2, 2.1, 5.2) would survive a single-story hand-run undetected. The design review §3 recommended this step, and it's valuable — but it's insufficient as the sole pre-freeze validation.
- Recommended decision: Add a second pre-freeze validation: a "concurrency smoke test" — two independent stories dispatched simultaneously against the same target repo, with the state repo separate, exercising CAS and claim leases. This doesn't need to be automated; a hand-run with two terminal sessions suffices. Schedule this between P1 schema freeze and P2 CLI build, so schema corrections are still cheap.
- Exact document edit: vision.md §11 P0 — add the concurrency smoke test step after the single-story hand-run. vision.md §11 P1 — note that P1 freeze gates on both the single-story hand-run AND the concurrency smoke test passing.

**6.3 — No specification for the factory-state repo bootstrap procedure** — severity: **major** — root_cause: acceptable_gap (but missing from P1 list) — timing: P1-contract
- Detail: `factory init` is described in §5: "creates the workspace in the factory-state repo, onboards a target repo, generates an environment-config template, and validates the setup with `factory doctor`." But `factory init` must ALSO create the state repo itself if it doesn't exist. The design says the state repo is a dedicated repo, but never specifies who creates it, with what initial structure, or how `factory init` discovers it. If the state repo spans projects (OC-8), then a second project's `factory init` should add a workspace to an EXISTING state repo, not create a new one. This discover/join semantic is unspecified.
- Recommended decision: `factory init` takes a `--state-repo <url>` parameter. If the state repo doesn't exist locally, it's cloned. If the URL doesn't exist on GitHub, `factory init --create-state-repo` creates it via `gh repo create`. The state repo's root layout is: `workspaces/<name>/` (per project), `ledger/` (or per-workspace ledger — see 1.2), `templates/` (shared templates). Subsequent `factory init` calls with the same `--state-repo` add workspaces to the existing repo. Freeze the state-repo layout and bootstrap procedure in P1.
- Exact document edit: vision.md §5 "Onboarding" — expand `factory init` semantics. Add to P1 "factory-state repo layout" contract: the exact directory tree.

---

## Scores

| Metric | Count |
|---|---|
| **Blockers** | 6 (1.1, 1.2, 2.1, 3.1, 5.2, 6.1) |
| **Majors** | 11 (1.3, 1.4, 2.2, 2.3, 3.2, 3.3, 4.2, 5.3, 5.5, 6.2, 6.3) |
| **Minors** | 4 (1.5, 3.4, 4.1, 5.4) |
| **None (verified)** | 1 (5.1) |
| **Total findings** | 21 |

**bundle_quality_score**: 48/100 — the design vision and principles are strong, but the ~6 blockers and ~11 majors mean a builder would be blocked or would invent wrong mechanics on roughly half the P1 contracts. The OC-8 state-repo architecture is the right call but the cross-repo evidence protocol, CAS semantics, and scope enforcement are under-specified. The evidence/merge integrity has a logical contradiction (2.1) that must be resolved before any code is written.

**sign_off_recommendation**: **approve_with_fixes** — all 6 blockers must be resolved before P1 contracts freeze; the 11 majors should be resolved before P1 build starts. The design does NOT need a rewrite — the architecture, principles, and flow are correct. What's needed is specification depth: concrete protocols, exact permission sets, resolved contradictions, and promiting specification shells to full contracts. A single round of owner decisions on the "Decisions needed" list below, followed by a focused edit pass on the ~6 affected sections, would bring this to sign-off.

---

## Decisions needed from owner

Each includes a recommended answer. Blockers first, then majors.

1. **Cross-repo evidence validation protocol (1.1)** — REC: validate by fetching product-repo SHA on demand; unresolvable = BLOCKED `evidence-unreachable`. Freeze step-by-step protocol in P1.
2. **Ledger file layout: monolithic vs per-story (1.2, 5.2)** — REC: per-story files (`ledger/stories/<story-id>.jsonl`), eliminating cross-story CAS contention. Simpler and scales better.
3. **"Squash tree equals reviewed tree" resolution (2.1)** — REC: compute merge-result tree via `git merge-tree` BEFORE review, review that tree, then squash tree = reviewed tree. Eliminates the contradiction.
4. **GitHub App token permission set (3.1)** — REC: freeze exact permissions; the App MUST NOT have PR review approval capability. If GitHub API doesn't separate PR write from PR approve, document the accepted risk and rely on audit trail.
5. **Egress allowlist feasibility (3.3)** — REC: defer to P6 (requires self-hosted runners); P3 accepts risk with per-job credential scoping + secret scanning as compensating controls.
6. **P1 specification shells (6.1)** — REC: before freezing P1, expand the transition catalog (sample tuples), state-repo directory tree, idempotent-replay procedure, PRD versioning mechanism, and test-gaming diff algorithm to full contracts with examples and pseudocode.
7. **Pre-freeze concurrency smoke test (6.2)** — REC: add a two-story concurrent hand-run before P1 freeze, in addition to the single-story hand-run.

---

## Gate split

**Fix before P1 freeze:**
- 1.1 Cross-repo evidence validation protocol
- 1.2 Ledger file layout + CAS retry semantics
- 2.1 Squash tree vs reviewed tree contradiction
- 3.1 Concrete App token permission boundary
- 5.2 Cross-story CAS contention (coupled with 1.2)
- 6.1 Specification shell promotion (transition catalog, state-repo layout, idempotent replay, PRD versioning, test-gaming gate)

**P1 contract (resolve during P1 build):**
- 1.3 Scope enforcement mechanism
- 1.4 Product-repo force-push detection
- 2.2 refs/factory/* fetch refspec configuration
- 2.3 Two-tree evidence pinning model
- 3.2 Actions environment vs PR review anchoring clarity
- 3.3 Egress allowlist scoping to self-hosted runners
- 3.4 Secret-scanning gate location
- 4.2 Inbox ordering algorithm
- 5.3 Branch protection rulesets per merge mode
- 5.5 Claim lease renewal semantics
- 6.2 Concurrency smoke test (add to P0/P1 gate)
- 6.3 State-repo bootstrap procedure

**Later phase:**
- 1.5 State-repo outage behavior (P3)
- 4.1 Level-3 touchpoint documentation (not a design change)
- 5.4 Board GraphQL scope fallback (P2)

---

## Summary

The software-factory vision has a coherent architecture and validated principles, but the feasibility grill exposes 6 blockers — concentrated in cross-repo evidence mechanics, a logical contradiction between "squash tree equals reviewed tree" and "up to date with main," and under-specified security boundaries — that would stop a P1 builder cold. The P1 contract list names the right things but roughly a third are specification shells a builder must invent. The recommended fixes are specification-depth additions, not architectural changes: define the cross-repo validation protocol step by step, switch to per-story ledger files to eliminate CAS contention, resolve the squash/merge-tree contradiction with `git merge-tree` before review, freeze the exact GitHub App permission set, and promote the five weakest specification shells to full contracts with examples and pseudocode before freezing P1. With those resolved, the design is buildable and the OC-8–OC-11 ratified decisions remain sound.