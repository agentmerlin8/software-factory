# Software Factory Vision — Bounded Round-2 Re-Grill (2026-11-14)

**Reviewer**: DeepSeek-family model (fresh context, cross-family separation)
**Scope**: Verify every round-1 finding's fix landed and is internally consistent; catch new contradictions introduced by the fix pass. Do NOT re-open ratified owner decisions or promote later-phase TASK items into blockers.
**Artifacts consulted**: vision.md (589 lines), open-calls.md (88 lines), lineage.md (50 lines), README.md (36 lines), grill-record-2026-11-14.md, grill-disposition-2026-11-14.md

---

## A. Evidence Ledger — Per-Finding Verification

Each finding is verified against the claim in the disposition table (grill-disposition-2026-11-14.md) and the actual current text of the vision bundle. Disposition types: FOLDED = fix landed in named section; RESOLVED = owner decision recorded; TASK = assigned to a named build phase; NOTED = planner constraint, no fix expected.

### Blockers (2)

| # | Finding | Disposition | Claimed Where | Actual Evidence | Verdict |
|---|---------|-------------|---------------|-----------------|---------|
| 1.1 | P5 vs P7 public-flip contradiction | RESOLVED | vision §11 P5/P7; open-calls OC-1; lineage | vision §11 P5 line 517: "P5 exit = repo goes PUBLIC"; P7 line 526: "The repo is already public since P5; this phase polishes what is public."; OC-1 lines 14-17: "the new repo goes PUBLIC at P5 exit"; lineage line 43: "the new repo flips public at that same milestone"; README line 7: "Private until the demo works end-to-end (P5 exit); then public." All four documents aligned. | **PASS** |
| 2.1 | Board schema undefined | RESOLVED | vision §3.4 board minimum schema; exact state list = TASK P1 | vision §3.4 lines 142-155: full board schema frozen (lane-per-state shape, custom fields Type/Autonomy Level/Stage/Stage group/Tokens-cost/Model used/Cycle time, full-lane + compact-group views). Exact state list explicitly deferred to P1: "The P1 state machine defines the exact set; the shape is intake → planning → ... → closed, plus Blocked." | **PASS** |

### Majors (19 unique)

| # | Finding | Disposition | Claimed Where | Actual Evidence | Verdict |
|---|---------|-------------|---------------|-----------------|---------|
| 2.2 | Feature-acceptance gate failure path | FOLDED | vision §4 flow FAIL branch; §11 P1 | §4 lines 197-198: "gate FAIL → auto-create fix stories in Backlog → feature BLOCKED → fix stories follow the normal pipeline → re-run the gate"; §11 P1 lines 489-490: "feature-acceptance failure path (BLOCKED + auto-created fix stories)". | **PASS** |
| 2.3 | Gate-to-transition catalog | TASK P1 | vision §11 P1 (transition catalog requirement) | §11 P1 lines 481-484: "complete transition catalog: every state → event → next-state tuple tagged with gate type (none \| deterministic \| llm-review \| human-approval) and autonomy-level override rules." Requirement correctly named in owning phase. | **PASS** |
| 2.4 | Escalation mechanism | FOLDED | vision §6 principle 4; §4 BLOCKED block | §6 principle 4 lines 328-332: "Escalation = the story enters BLOCKED... with an auto-created issue linking the full review record; a human or an authorized agent (per autonomy policy) must disposition it"; §4 BLOCKED lines 204-208: same disposition paths. "Human OR authorized agent" matches Randy's answer. | **PASS** |
| 2.5 | Intake Engine in architecture | FOLDED | vision §5 Intake Engine | §5 lines 241-248: "Intake Engine = a stateful session manager, distinct from the fire-and-forget dispatch pipeline: it drives the question flow, Storybook wireframe generation, and PRD production." Also shown in architecture sketch line 230: "CLI · core agents · Intake Engine ·". | **PASS** |
| 2.6 | Claim-lock vs ephemeral Actions | FOLDED | vision §5 claim leases; §6 principle 9 | §5 lines 277-281: "Claim leases: every claim carries a TTL (default 30m cloud, 10m local), auto-renewed by the holding process; an expired claim auto-releases with an audit event"; §6 principle 9 lines 349-350: "claim leases (TTL + auto-renew + audited auto-release) so ephemeral sessions never strand a claim." | **PASS** |
| 2.7/5.6 | Drag-to-dispatch placement | RESOLVED | vision §3.4 + §11 P5 | §3.4 line 139: "Drag-to-dispatch (board column-move → CLI dispatch) is a P5 capability."; §11 P5 lines 515-517: "Board drag-to-dispatch lands here (depends on P2 board sync + P3 cloud adapter)." | **PASS** |
| 2.8 | Demo repo location | FOLDED | vision §8 demo repo bullet | §8 lines 408-411: "Demo repo: a separate repository (agentmerlin8/software-factory-demo), created in P5 and onboarded as the factory's first target repo. Separate so the factory repo stays clean and the demo is independently forkable." | **PASS** |
| 2.9 | Model roles/tiers | FOLDED+TASK | vision §5 model routing; §11 P1 | §5 lines 260-265: "Minimum roles = planner, coder, reviewer, intake-agent, feature-refiner; tiers = budget, standard, frontier. The full matrix… lives in environment config; P1 freezes the schema, P3 populates." §11 P1 line 492: "model-routing schema (roles × tiers)". Schema frozen in vision; population is TASK P3. | **PASS** |
| 2.10 | Self-host workspace | FOLDED | vision §5 workspace self-host (.factory/) | §5 lines 253-256: "Self-host (dogfood): the factory builds itself using the single-repo pattern with its workspace at .factory/ (hidden, to avoid colliding with the product source tree); ledger stories target the factory repo's own code." | **PASS** |
| 3.1 | "Right questions" unmeasurable | FOLDED | vision §1 success bullet (PRD approval) | §1 lines 22-25: "completes a structured intake (platform, stack, features, look-and-feel), shows live Storybook wireframes, and iterates until the user approves the PRD. ('Right questions' is measured by PRD approval, not judged subjectively.)" Observable signal defined; subjective language removed. | **PASS** |
| 3.2 | Level-3 promotion thresholds | TASK P6 | vision §7 + §11 P6 (≥3 features of data) | §7 lines 389-391: "Promotion thresholds... are defined in P6; no Level 3 activation without threshold data from at least 3 completed features." §11 P6 lines 521-522: "Level-3 promotion thresholds defined here (no activation without data from ≥3 features)." Requirement correctly named in owning phase. | **PASS** |
| 3.3 | Quality/cost dimensions | FOLDED | vision §1 + new §10 Measurement | §1 lines 31-35: "cost (calls × context) and quality (review-finding severity, rework loops, defect escapes) are measured per stage and recorded in the ledger"; new §10 Measurement (lines 440-464): full section with per-dispatch recording, per-story/feature/run derivation, statistics view, schema/metering/dashboard phasing. | **PASS** |
| 4.1 | Feature vs story state | FOLDED | vision §5 feature state computed render | §5 lines 273-276: "Feature state is a computed render from story states (all stories merged + acceptance gate passed = feature done); feature-level gate events (acceptance-pass / acceptance-fail) ARE first-class ledger events for audit. Story events remain the only state-driving events." | **PASS** |
| 4.2 | Storybook exposure tiers | FOLDED | vision §5 Intake Engine LIVE/LINK/SCREENSHOT | §5 lines 246-249: "Storybook exposure degrades by harness capability in three tiers: LIVE (embedded/bridged running-Storybook URL), LINK (clickable URL), SCREENSHOT (static image fallback). The protocol queries harness capability and picks the best tier." | **PASS** |
| 4.3 | Board sync direction | FOLDED | vision §5 board sync one-way + webhook trigger | §5 lines 290-293: "Board sync direction: primarily one-way (ledger → board). Drag-to-dispatch is a board column-move webhook → CLI factory dispatch; the ledger records the dispatch event only after the CLI receives it. The board triggers the action; the ledger remains the sole source of truth." | **PASS** |
| 4.4 | Ephemeral Actions vs review loops | FOLDED | vision §5 per-step dispatch + checkpoints | §5 lines 286-289: "each pipeline step (plan, code, review, proof) is a SEPARATE Actions job; state is checkpointed in the ledger between steps; no single job spans multiple stages. Jobs are idempotent — replay the dispatch, not the session." | **PASS** |
| 5.1 | Story failure/rejection lifecycle | FOLDED | vision §4 BLOCKED block; §6 principle 4; §11 P1 | §4 lines 207-208: "accept-with-known-issues / re-scope into new stories (with lineage) / reject (CLOSED-WONT-FIX)"; §6 principle 4 lines 331-332: same three dispositions; §11 P1 lines 487-488: "story failure lifecycle: rework loop, 2-loop cap, BLOCKED, human/authorized-agent disposition paths (accept / re-scope / reject)." | **PASS** |
| 5.2 | Feature-gate fail → who dispatches fix stories | FOLDED | vision §4 flow | §4 lines 197-198: "gate FAIL → auto-create fix stories in Backlog → feature BLOCKED → fix stories follow the normal pipeline → re-run the gate." Fix stories follow the same dispatch process as regular stories. | **PASS** |
| 5.3 | Onboarding command | FOLDED | vision §5 onboarding | §5 lines 294-298: "factory init [--guided] — creates the workspace, onboards a target repo, generates an environment-config template, and validates the setup with factory doctor. --guided asks setup questions interactively for non-developers." | **PASS** |

### Minors (13)

| # | Finding | Disposition | Claimed Where | Actual Evidence | Verdict |
|---|---------|-------------|---------------|-----------------|---------|
| 1.2 | Flow diagram missing expand-only/flagged | FOLDED | vision §4 (note under main merge) | §4 flow line 193: "(incomplete user-visible flows stay expand-only or flagged)" — now directly under the main merge block in the flow diagram. | **PASS** |
| 1.3 | "Review BEFORE the PR" wording | FOLDED | vision §4 (review on branch → PR opened) | §4 flow lines 186-190: "adversarial code review on the branch (fresh context, cross-model) → proof artifacts → PR opened/updated → human merge gate." Review happens on the branch first; then PR is opened/updated. Old ambiguous phrasing removed. | **PASS** |
| 1.4 | README stale open-calls status | FOLDED | README read order + status | README lines 23-24: "docs/open-calls.md — ratified owner decisions (all seven closed 2026-11-14)." No longer says "decisions awaiting the owner." | **PASS** |
| 2.11 | Story format schema | TASK P1 | vision §11 P1 story schema | §11 P1 lines 485-486: "story schema: id, feature ref, ACs anchored to the PRD, structural-signal count, dependencies, target repo, state." Requirement correctly named in owning phase. | **PASS** |
| 2.12 | Who creates board feature items | FOLDED | vision §3.4 (P0 manual, P4+ auto) | §3.4 lines 152-155: "P0: the backlog's feature items are created on the board from the feature list (human/Merlin). From P4, the intake engine auto-creates feature items when a PRD is produced." | **PASS** |
| 3.4 | Main-deployability verification | FOLDED | vision §11 P3 deployability guard | §11 P3 lines 504-506: "Deployability guard: CI on every main push runs build + smoke tests; red main = BLOCKED new dispatches until green." | **PASS** |
| 3.5 | "Randy keeps architecture" unmeasurable | NOTED | process principle — no change needed | §6 principle 15 lines 364-366: unchanged; correct disposition — this is a governance principle, not a product success claim. | **PASS** |
| 4.5 | Storybook spike throwaway vs reusable | FOLDED | vision §11 P0 (throwaway exploration) | §11 P0 lines 473-476: "throwaway exploration: hardcoded setup, fixed conversation script, output = model/adapter evaluation data, not reusable code. P4 builds the real intake on P1 schemas, informed by the spike." | **PASS** |
| 4.6 | Workspace dir collision | FOLDED | vision §5 (configurable; self-host .factory/) | §5 lines 251-256: "default factory/, configurable via environment config... self-host uses .factory/ (hidden)." Both fixes present: configurability + self-host namespace. | **PASS** |
| 5.4 | Dependency management | FOLDED | vision §5 dependency policy | §5 lines 299-302: "Dependency policy: agents may modify dependency manifests as part of story code; all dependency changes must be committed with the story; factory doctor flags uncommitted manifest changes; CI installs from committed manifests." | **PASS** |
| 5.5 | CI/CD boundary | FOLDED | vision §12 deferred | §12 deferred lines 535-537: "the factory generates a baseline CI config (build, test, lint) for target repos at P5; repos may customize it; factory doctor validates CI presence." | **PASS** |
| 5.7 | "Live proof" undefined | FOLDED | vision §4 (automated post-deploy evidence) | §4 flow lines 200-201: "live proof (automated post-deploy evidence: screenshot + smoke-test log, pinned in the ledger)." Term defined; no longer ambiguous. | **PASS** |
| 5.8 | Adapter priorities | TASK P6 | vision §11 P6 | §11 P6 lines 522-524: "remaining adapters (priority: api-direct, claude-code, codex, copilot-cli; the human adapter exists from P2 as the CLI itself)." Priorities named; implementation is TASK P6. | **PASS** |

### Informational (3)

| # | Finding | Disposition | Verdict |
|---|---------|-------------|---------|
| 6.1 | OC-1..OC-7 mutually consistent | Confirmed; no change | **PASS** — all OCs still consistent; no contradiction introduced. |
| 6.2 | OCs vs 2026-11-13 locked decisions aligned | Confirmed; no change | **PASS** — locked-decisions table (§13) carries all OC-1..OC-7 plus grill fixes, fully aligned with the 2026-11-13 decisions. |
| 6.3 | OCs vs lineage salvage boundary no conflict | Confirmed; no change | **PASS** — lineage keep/scrap lists still consistent with all OCs. |

---

## B. New-Contradiction Scan

Systematic check: did the fix pass introduce any NEW internal contradiction?

### B.1 — Section numbering and cross-references (§10/§11/§12/§13)

The fix pass inserted a new §10 (Measurement), renumbering the old §10 Roadmap → §11, §11 Deferred → §12, §12 Decisions → §13.

Every cross-reference in vision.md was verified against the current section numbering:

| Reference | Points to | Current section | Match? |
|-----------|----------|-----------------|--------|
| "three-level scale, §7" (line 29) | Autonomy model | §7 | ✓ |
| "process DNA, §6" (line 125) | Principles | §6 | ✓ |
| "computed render, §5" (line 147) | Architecture sketch | §5 | ✓ |
| "demo app (§8)" (line 157) | Demo app | §8 | ✓ |
| "policy-gated (§7)" (line 220) | Autonomy model | §7 | ✓ |
| "lane-per-state schema, §3" (line 472) | What we are building | §3 | ✓ |
| "measurement fields, §10" (line 478) | Measurement & statistics | §10 | ✓ |
| "metering live (§10)" (line 504) | Measurement & statistics | §10 | ✓ |

Every disposition-table reference also resolves correctly: "vision §11 P5/P7" → §11 is Roadmap which contains P5/P7. "vision §12 deferred" → §12 is Explicitly deferred. Zero stale references.

### B.2 — Flow diagram vs locked-decisions table vs architecture sketch

- Flow diagram §4: trunk-based, squash-merge, feature-acceptance gate, BLOCKED path, expand-only/flagged, live-proof definition → all match OC-3 (trunk-based), the locked-decisions table (§13), and the architecture sketch's claim-lease + per-step-dispatch model.
- Architecture sketch §5: CLI, Intake Engine, workspace, adapters, claim leases, cloud execution, board sync, onboarding → all present; no component claimed in the flow that the architecture omits.
- The flow diagram does not explicitly show per-step dispatch checkpoints between plan→code→review→proof, but the architecture text (§5 lines 286-289) resolves this. The flow diagram remains the logical (not deployment) view. No contradiction — the flow diagram was always a logical pipeline, and the architecture clarifies the deployment model.

### B.3 — Board schema vs autonomy/failure rules

- Board has Blocked as a first-class lane (§3.4 lines 137-138: "any blocked story/feature lands in the Blocked lane with an auto-created issue").
- §4 BLOCKED: a human OR an authorized agent (per autonomy policy) clears blockers (line 207).
- §7 autonomy model: "Levels are gate policy (which transitions require a human actor)" (line 381).
- Board schema P0 says "board moves are CLI/sync-driven from P2; before that, moves are manual and recorded" (lines 154-155).
- At higher autonomy levels, blocker-clearing by an authorized agent is allowed → this is bounded by the autonomy policy and the confidence/escalation contract in §7. Consistent chain: blocker → Blocked lane + issue → autonomy policy determines who clears → if agent can't confidently clear, escalates to human per §7 contract.

### B.4 — "Human OR authorized agent clears blockers" vs trust posture (principle 14)

Principle 14 states: "All inbound artifacts untrusted data; positive-only actor trust; human-gated transitions refuse non-human actors by configuration" (lines 362-363).

The phrase "by configuration" is the key: the default configuration gates transitions to human-only. The autonomy policy (§7) is the mechanism for reconfiguring which transitions are human-gated. At Level 1, blocker clearance is human-gated. At Level 3, the policy may allow an authorized agent — but only where the autonomy policy explicitly allows it (§4 lines 220-222: "blocker-clearing may be delegated to an authorized agent only where the autonomy policy explicitly allows it — escalations that exceed the policy's confidence always reach a human"). This is a reconfiguration of the default, not a violation of it. **No contradiction.**

### B.5 — Lane-per-state board vs "feature state is a computed render"

- Board lanes are per STORY lifecycle state (§3.4: "one lane per lifecycle state", "one lane per story lifecycle state").
- Features aggregate story states: §3.4 line 146-147: "Features aggregate their stories' states (computed render, §5)."
- §5 lines 273-276: "Feature state is a computed render from story states... Story events remain the only state-driving events."
- The board has story-level lanes; feature state is computed/displayed as an aggregate, not occupying a lane of its own. **Fully consistent.**

### B.6 — Measurement section (§10) vs ledger principles

- §10 "Recorded per dispatch (ledger events...)" matches principle 9: "Append-only events, evidence SHAs."
- §10 "nulls render as 'not recorded: reason', never zeros" matches principle 3: same language.
- §10 cost = "tokens + a versioned price table until that table is trusted; dollars are derived, never invented" is a refinement of principle 7's "Cost ≈ calls × context-per-call" — the "≈" in the principle acknowledges approximation; §10 provides the implementation detail. **Compatible.**

### B.7 — Claim leases + per-step dispatch vs per-gate push

Principle 9 says "push-per-gate" (line 350). Claim leases say claims auto-renew and expired claims auto-release. Per-step dispatch says each pipeline step is a separate Actions job with ledger checkpoints. If a story moves from plan→code, the plan step pushes to the ledger, then releases (or the lease expires). The code step claims the story fresh. This means each step is its own claim lifecycle. The "push-per-gate" principle is satisfied because evidence is pushed at each gate transition. **Consistent.**

### B.8 — Drag-to-dispatch P5 vs P2 board sync

§3.4: "Board moves are CLI/sync-driven from P2" (one-way). Drag-to-dispatch is P5 (two-way trigger). The distinction is clear: P2 sync is read-only visibility; P5 drag adds write-back triggering. The architecture §5 clarifies the webhook→CLI path. **No contradiction.**

### B.9 — Storybook spike: "throwaway" vs OC-6 "screenshot-back first, then live-link"

OC-6 says: "Early bounded spike (P0/P1): one agent session, running Storybook in the workspace, screenshot-back first, then the live-link UX." The vision §11 P0 says: "throwaway exploration: hardcoded setup, fixed conversation script, output = model/adapter evaluation data, not reusable code." These are compatible: the spike explores screenshot→live-link flow but with throwaway code. The real intake (P4) learns from the spike but doesn't reuse its code. **Consistent.**

### B.10 — All seven OCs still mutually consistent

Reviewed OC-1 through OC-7 with the fix-pass changes applied:
- OC-1 now includes public-flip timing → no contradiction with OC-2..OC-7
- OC-3 (trunk-based) + OC-4 (autonomy = gate policy) + the new BLOCKED/clearance rules: the feature-acceptance gate is a validation gate (not a merge gate), so it sits outside merge autonomy scope; blocker clearance is separate from merge — both are gate-policy-controlled. ✓
- OC-5 (dogfood P3) + OC-6 (spike P0/P1) + OC-7 (harness-agnostic protocol): all compatible. ✓

---

## C. Verdict

### PASS/FAIL counts

| Severity | PASS | FAIL | Total |
|----------|------|------|-------|
| Blocker  | 2    | 0    | 2     |
| Major    | 19   | 0    | 19    |
| Minor    | 13   | 0    | 13    |
| Informational | 3 | 0   | 3     |
| **Total** | **37** | **0** | **37** |

### New findings

**0 new findings.** The fix pass introduced no new internal contradictions. Cross-references are correct. Section renumbering (§9→§10→§11→§12→§13) is clean. The board schema, autonomy rules, trust posture, measurement section, claim leases, per-step dispatch, and board sync direction form a consistent whole.

### Final verdict: **APPROVE**

### Summary

All 37 round-1 findings verified: every FOLDED fix landed correctly in the vision bundle, every TASK item names its owning phase and requirement, both RESOLVED blocker decisions are recorded, and the one NOTED minor (3.5, governance principle) remains correctly unchanged. The fix pass introduced zero new contradictions — section numbering is clean, every cross-reference resolves to the correct section, and the board schema / autonomy / trust-posture / measurement / claim-lease / dispatch-model rules form a consistent mesh. The "human OR authorized agent clears blockers" rule stays consistent with trust posture (principle 14) because the autonomy policy is the configuration mechanism that reconfigures which transitions are human-gated. The lane-per-state board schema correctly treats feature state as a computed render from story states without giving features their own lanes. No later-phase TASK items were promoted to blockers. Ready for backlog decomposition.

**Docs consulted**: vision.md (589 lines), open-calls.md (88 lines), lineage.md (50 lines), README.md (36 lines), grill-record-2026-11-14.md, grill-disposition-2026-11-14.md.
**Reviewer**: DeepSeek-family model, fresh context, 2026-11-14.