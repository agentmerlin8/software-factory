# Software Factory Vision — Round-4 Bounded Confirmation Grill

**Grill type:** Cross-family fresh-context bounded confirmation (DeepSeek-family reviewer, Qwen-family author)
**Documents reviewed:** vision.md (fixed, 2026-11-14), grill-round3-2026-11-14.md, open-calls.md (OC-1…OC-11 RATIFIED, frozen)
**Fix-pass commit:** 8956672 (claimed)
**Date:** 2026-11-14

---

## Evidence Ledger — Round-3 Finding Verification

### BLOCKERS (6)

| ID | Finding | Fix Present? | Correct? | Feasible? | Verdict |
|----|---------|-------------|----------|-----------|---------|
| 1.1 | Cross-repo evidence validation protocol unspecified | Yes — §5 "Cross-repo evidence validation" L367-377 | Yes — step-by-step: read ledger repo@sha → fetch product repo → resolve SHA+refs/factory/* → missing=BLOCKED evidence-unreachable | Yes — uses standard git fetch; validator needs network/cached clones; factory doctor --deep for SHA liveness | **PASS** |
| 1.2 | CAS retry semantics missing | Yes — §5 "Ledger write location + layout" L378-388 | Yes — per-story files + 3× backoff (1s/2s/4s) + exhaustion=BLOCKED cas-contention | Yes — per-story files eliminate cross-story CAS contention entirely; retry+backoff handles same-story races | **PASS** |
| 2.1 | Squash tree vs up-to-date contradiction | Yes — §4 flow L213-228 + §5 "Evidence integrity" L345-361 | Yes — compute merge-result tree via `git merge-tree --write-tree` BEFORE review; review that tree; verify main hasn't advanced; no rebase after review; squash tree = reviewed merge-result tree | Yes — contradiction resolved: reviewed tree IS merge result, equality by construction | **PASS** |
| 3.1 | Token permission boundary hand-waved | Yes — §5 "Human approval anchoring" L421-432 | Yes — concrete App permission set: contents:w, PRs:w (create/update), issues:w, metadata:r, NO workflows; App never approver/CODEOWNERS; human-only CODEOWNERS branch-protected; GitHub self-approval block | Yes — no residual forgery path: App can't approve own PRs, can't modify CODEOWNERS on main, can't create human-attributed reviews | **PASS** |
| 5.2 | Cross-story CAS contention unaddressed | Yes — §5 "Ledger write location" L378-388 (coupled with 1.2) | Yes — per-story files eliminate cross-story contention; only same-story writes collide, serialized by per-story concurrency group | Yes — contention surface eliminated by design | **PASS** |
| 6.1 | Specification shells in P1 contract list | Yes — §11 P1 L719-722 | Yes — no-shell-freeze rule: "every contract below ships with a concrete example + data schema + validation rule in pseudocode before freeze; a name with no internals is not a frozen contract" | Yes — rule is declarative; actual expansion deferred to P1 freeze (correct per the rule) | **PASS** |

### MAJORS (11)

| ID | Finding | Verdict | Evidence |
|----|---------|---------|----------|
| 1.3 | Scope enforcement mechanism missing | **PASS** | §5 L289-298: enforcement = state repo's GitHub visibility + collaborator/team permissions; scope field declarative, validated by factory doctor against GitHub API |
| 1.4 | Force-push breaks ledger SHAs | **PASS** | §5 L375-377: factory doctor --deep checks all ledger SHAs resolve; board sync spot-checks recent SHAs; force-push detection is visibility/audit, not hard gate |
| 2.2 | refs/factory/* fetch refspec unspecified | **PASS** | §5 L364-366: factory init configures `git config --add remote.origin.fetch '+refs/factory/*:refs/factory/*'`; ledger tooling does targeted fetch |
| 2.3 | Two-tree pinning model underspecified | **PASS** | §5 L345-361: explicit reviewed_tree + merge_tree fields; ledger links `reviewed_tree → review_context → merge_tree → squash_commit` |
| 3.2 | Actions environment vs PR review confusion | **PASS** | §5 L413-420: two mechanisms separated — code-merge gate (human PR review/merge) vs agent-dispatch gate (Actions environment required reviewers) |
| 3.3 | Egress allowlist not native on GitHub runners | **PASS** | §5 L433-446: egress deferred to P6; P3 accepts risk with per-job credential scoping + secret scanning as compensating controls; documented as accepted risk in P1 threat model |
| 3.4 | Secret-scanning location ambiguous | **PASS** | §5 L443-446: pre-push deterministic gate in agent's coding session before branch push (gitleaks/trufflehog, tool frozen P1) |
| 4.2 | Inbox ordering algorithm underspecified | **PASS** | §3 L157-167: blocked_count = transitively blocked stories (direct+indirect) from dependency DAG; tiebreak oldest-first |
| 5.3 | Branch protection for auto-merge unspecified | **PASS** | §5 L405-412: factory init configures per mode: Mode 1 = 1 human review + status checks; Mode 2/3 = factory gate status checks ONLY. GitHub self-approval block prevents agent deadlock |
| 5.5 | Claim lease split-brain unaddressed | **PASS** | §5 L447-456: (1) background timer renewal independent of agent loop; (2) pre-side-effect lease re-check → immediate fail with lease-expired; (3) effective TTL includes grace period (TTL + 2× renewal interval) |
| 6.2 | Single-story hand-run insufficient | **PASS** | §11 P0 L708-715: two pre-freeze validations — (1) single-story hand-run AND (2) concurrency smoke test (two independent stories, same target repo, separate state repo) |
| 6.3 | State-repo bootstrap unspecified | **PASS** | §5 L480-494: factory init --state-repo <url>, clone-or-create, discover/join for subsequent inits, root layout (workspaces/<name>/, ledger/stories/<id>.jsonl, templates/) |

### MINORS (4)

| ID | Finding | Verdict | Evidence |
|----|---------|---------|----------|
| 1.5 | State-repo outage behavior unspecified | **PASS** | §11 P3 L789-791: push failures retry 3×; exhaustion → fails with state-repo-unreachable; dispatch replayable |
| 3.4 | (Duplicate of major above) | **PASS** | (same as 3.4 major) |
| 4.1 | Level-3 touchpoint count | **PASS** | Finding was confirmation that design is sound; no fix required per round-3 recommendation ("Not a design change") |
| 5.4 | Board GraphQL scope fallback | **PASS** | §11 P2 L779-783: factory board sync detects writability, falls back to issue labels+body; custom fields best-effort; ledger records regardless |

### Task-to-Phase Verification

All round-3 items deferred to specific phases are correctly placed with the no-shell rule applied:

| Item | Phase | Location | Correct? |
|------|-------|----------|----------|
| 1.3 Scope enforcement | P1 state-repo layout contract | §11 P1 L744-746 | ✓ |
| 1.4 Force-push liveness | P2 (doctor --deep) | §5 L375-377, §11 P2 L774 | ✓ |
| 2.2 Refspec config | P1 evidence integrity | §5 L364-366, §11 P1 L753-757 | ✓ |
| 2.3 Two-tree model | P1 evidence integrity | §5 L345-361, §11 P1 L753-757 | ✓ |
| 3.2 Gate separation | P1 human approval anchoring | §5 L413-420, §11 P1 L758-763 | ✓ |
| 3.3 Egress deferral | P3 accepted risk / P6 hardening | §5 L433-446, §11 P3 L795-797 | ✓ |
| 3.4 Pre-push secret scanning | P1 threat model | §5 L443-446, §11 P1 L762-763 | ✓ |
| 4.2 Inbox ordering | P1 story schema (deps) / P2 inbox | §3 L157-167, §11 P1 L728-730, P2 L778-779 | ✓ |
| 5.3 Branch protection rulesets | P1 workspace policy | §5 L405-412, §11 P1 L747-749 | ✓ |
| 5.5 Lease split-brain guards | P1 claim-lease semantics | §5 L447-456, §11 P1 L738-739 | ✓ |
| 6.2 Concurrency smoke test | P0 pre-freeze validations | §11 P0 L708-715 | ✓ |
| 6.3 State-repo bootstrap | P1 state-repo layout | §5 L480-494, §11 P1 L739-744 | ✓ |
| 1.5 State-repo outage | P3 | §11 P3 L789-791 | ✓ |
| 5.4 Board fallback | P2 | §11 P2 L779-783 | ✓ |

---

## New-Problem Scan — Amended Sections

### Merge-Tree Protocol

**N1 — Merge-tree bridging mechanism is implicit** — severity: **minor** — root_cause: document_ambiguity — timing: clarify-during-P1-contract

- Detail: The protocol computes the merge-result tree via `git merge-tree --write-tree`, reviews it, then opens/updates a PR. The PR branch still carries its original tree (not the merge-result tree). GitHub's squash-merge applies the branch's diff to main's HEAD, producing a tree that SHOULD equal the merge-result tree (same diff applied to same base), but this equivalence is an implicit assumption — the protocol doesn't explain that GitHub squash-merge and `git merge-tree` produce equivalent trees for clean merges. A skeptical builder would ask "how does the reviewed merge-result tree become the squash tree?" The answer is that GitHub's squash-merge independently computes the same merge result from the same inputs, and the post-merge verification step (`merge_tree == squash_tree`) catches any discrepancy. The protocol text should make this explicit.
- Recommended decision: Add a sentence to §5 Evidence integrity: "GitHub's squash-merge independently computes the merge result from the PR branch's commits; for clean merges this produces the same tree as `git merge-tree`. The post-merge verification (`merge_tree == squash_tree`) confirms equivalence; a mismatch triggers recompute + re-review."
- Exact document edit: vision.md §5 "Evidence integrity" L358 — after "The squash commit's tree is verified equal to `reviewed_tree` (`merge_tree == squash_tree`)" add a note explaining the equivalence mechanism.

**N2 — TOCTOU between merge-base check and actual merge** — severity: **minor** — root_cause: acceptable_gap — timing: P1-contract

- Detail: The protocol says "Before merge, verify main has not advanced past the reviewed merge base." Between this check and the actual merge (or PR squash), another story could merge to main, advancing it. The resulting squash tree would differ from the reviewed merge-result tree. The protocol handles this: the post-merge equality verification would fail, and the flow says "if main has advanced, recompute merge-tree + re-review." However, by the time the verification fails, the merge has already landed (the squash commit exists on main with the wrong tree). The protocol should clarify that the pre-merge check + git's non-fast-forward push protection both guard against this. Or: the post-merge verification detects it and triggers a corrective action (revert + recompute). The protocol text doesn't specify whether the verification is pre-merge or post-merge.
- Recommended decision: Clarify the merge gate sequence: (a) pre-push check (verify main hasn't advanced), (b) if advanced → recompute + re-review, (c) merge via GitHub PR (squash), (d) post-merge verification (`merge_tree == squash_tree`), (e) if mismatch → auto-revert + reopen story, treat as a detected anomaly. Git's non-fast-forward protection provides a second pre-merge guard. Freeze the exact sequence in the P1 evidence integrity contract.
- Exact document edit: vision.md §4 flow — split "squash tree verified equal to reviewed merge-result tree" into pre-merge check + post-merge verification as separate steps.

### Per-Story Ledger

No new problems. Per-story files eliminate cross-story contention. Rollup/index is explicitly a derived render (not a write target), so it can always be regenerated from the immutable per-story files. Claim leases live in the same per-story file. Inbox ordering reads all per-story files to compute the dependency DAG — straightforward and bounded by story count. No contention surface introduced.

### Token Boundary

No new problems. The concrete permission set (contents:w, PRs:w create/update, issues:w, metadata:r, no workflows) + App-never-approver + human-only CODEOWNERS + branch protection + GitHub self-approval block form a complete defense chain. No residual forgery path identified:
- App cannot approve own PRs (GitHub hard block)
- App cannot modify CODEOWNERS on main (branch-protected)
- App cannot create human-attributed reviews (only App-token, not user-to-server)
- App cannot trigger workflows (no workflows permission)
- Gate verifies human approval through GitHub API (not trust in App-created artifacts)

### Cross-Repo Validation

No new problems. The protocol is concrete: read ledger → fetch product repo → resolve SHA + refs/factory/* → missing = BLOCKED evidence-unreachable. Edge cases handled:
- Unreachable product repo: network error surfaced, not silent
- Missing SHA (force-push): doctor --deep detects; board sync spot-checks
- Partial clones: product repos use full clones (refs/factory/* keeps objects reachable; not a concern)
- Multiple product repos: validator needs network/cached clones; performance, not correctness

### Additional Checks

- **CAS retry with per-story files** — 3× backoff handles same-story races; per-story concurrency group prevents simultaneous same-story jobs. Lease guards against split-brain. Consistent.
- **Rollup consistency** — derived render; regenerated by scanning per-story files. No write contention. Consistent.
- **Branch protection mode 2/3** — status checks only, factory gate IS approval. GitHub self-approval block means requiring a PR review would deadlock; status-check-only avoids this. Correct.
- **P1 contract list scope** — ~25 items identified with the no-shell rule. Ambitious but feasible; the rule ensures quality. No feasibility gap — it's a discipline rule.
- **No OC re-litigation** — All OC-1…OC-11 remain frozen. No new argument touches them.

---

## Verdict

| Metric | Count |
|--------|-------|
| **Round-3 findings verified** | 21 |
| **Round-3 findings PASS** | 21 |
| **Round-3 findings FAIL** | 0 |
| **New findings** | 2 (both minor) |
| **OC re-litigations** | 0 |

**New findings:**
- N1: Merge-tree bridging mechanism is implicit (minor — clarify the squash-tree equality assumption)
- N2: TOCTOU between merge-base check and merge (minor — specify pre/post-merge verification sequence)

**Final verdict: APPROVE**

**Summary:** All 21 round-3 findings are verified PASS — every fix is present, correct, and feasible. The merge-tree protocol resolves the central contradiction cleanly. The per-story ledger eliminates cross-story contention. The token boundary is concrete with no residual forgery path. Two minor new findings (N1, N2) relate to the merge-tree protocol's implicit assumptions about squash-merge equivalence and the TOCTOU between the pre-merge main-advanced check and actual merge; both are documentation clarifications for the P1 contract, not design defects. No OC decision is re-litigated. The vision is buildable and the P1 freeze can proceed.

---

**Artifact path:** /home/merlin/.hermes/cache/scratch/sf-vision-grill-round4-2026-11-14.md