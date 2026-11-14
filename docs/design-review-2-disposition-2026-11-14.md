# Design review 2 disposition — issue #2 (Fable 5.2, 2026-11-14)

Second adversarial review. Verdict: **build with cuts; redesign the
state-repo write path and the merge-integrity protocol before any contract
freezes; replace the P1 freeze with a walking-skeleton experiment.**

Unlike round 1, this review TESTED its central claims (git 2.51.1) and
attacked the trust boundary as a whole. Two findings refute things our
round-4 reviewer certified as closed. The orchestrator independently
reproduced the load-bearing experiment and verified the org plan before
dispositioning.

## Independently verified by orchestrator (not taken on faith)

- **A1 REPRODUCED.** Two clones of one bare repo, appending to DIFFERENT
  files (story-A.jsonl / story-B.jsonl) on the same branch `main`: second
  push rejected `! [rejected] main -> main (fetch first)`. Git's
  non-fast-forward rejection is per-REF, not per-file. The round-3/round-4
  claim "per-story files eliminate cross-story contention" is FALSE.
  (git 2.56.0, scratch bare-repo test.)
- **B5 VERIFIED + ESCALATED.** Org `agentmerlin8` is on the **Free plan**.
  `GET /branches/main/protection` and `/rulesets` both return 403 "Upgrade
  to GitHub Pro or make this repository public." On private repos, NONE of
  the branch-protection anchoring (required reviews, status checks,
  up-to-date-before-merge, CODEOWNERS enforcement) is enforceable today.
  This is a hard constraint the design assumed away.

## Disposition key

ACCEPT = real, fold/cut · VERIFY-THEN-DECIDE = needs the throwaway-repo
experiment · OWNER-CALL = strategic decision for Randy · NOTED.

## A. Merge integrity + per-story ledger

- **A1 (blocker, tested+reproduced)** — ACCEPT. Per-story files do NOT
  remove push contention. Fix: single controller writer to the state repo
  (one concurrency group), OR one ref per story for true per-story CAS.
  Couples with B1. The retry must be fetch→rebase→re-validate→push, not a
  blind re-push.
- **A2 (blocker, tested)** — ACCEPT. Nothing deterministic tests the merged
  tree; only an LLM reads it before it lands. The round-1 promise "re-run
  gates on the merge result" was dropped in the round-3 rewrite. Real gap.
- **A3 (major, recommended cut)** — ACCEPT. Replace the merge-tree protocol
  with: merge main into the story branch BEFORE review, test + review that
  head, enable "require branches up to date before merging." GitHub refuses
  the merge if main moved; squash tree = reviewed head by construction.
  Removes the race, the post-merge mismatch path, and the auto-revert.
  Keep post-merge tree compare as a cheap alarm, not a control. VERIFY the
  strict setting + server-side squash equivalence on a real PR.
- **A4 (major)** — ACCEPT. Auto-revert has no identity allowed to do it
  (protected main; giving the App bypass voids approval anchoring). With A3
  the mismatch-revert disappears; for red main, block dispatches + put a
  prepared revert PR in the inbox as a one-click human decision.
- **A5 (major)** — ACCEPT. Re-review on every main advance is quadratic
  (N(N-1)/2 panel reviews). Fix: re-review only when the story's own diff
  changed or main's delta touches the story's manifest; else deterministic
  gates only.
- **A6 (minor, tested)** — ACCEPT. merge-tree conflict path unspecified
  (exit 1, tree with conflict markers). Moot if A3 adopted; else specify.
- **A7 (major)** — ACCEPT. Lease check is not a fence (check-then-act across
  two repos isn't atomic; TTL clock unspecified). For v1 CUT leases: Actions
  job timeouts + concurrency group (cloud), single operator (local). If
  kept, fence with `git push --force-with-lease`.
- **A8 (major, docs)** — ACCEPT. Concurrency group default cancels queued
  jobs (use `queue: max`); group is repo-scoped, doesn't cover multi-repo
  stories. Moot for v1 if cloud + multi-repo are cut.

## B. State repo + security

- **B1 (blocker)** — ACCEPT. OC-8 put the control plane (policy, ledger,
  dispatch packages) in a repo agents push to directly; App contents:write
  is repo-wide, not path-scoped. One injection can flip merge policy across
  projects. Fix: agents NEVER hold a state-repo write token; agent emits
  results as artifact/branch in the product repo; a separate controller job
  (no model output, no product code) validates + appends; policy changes
  only by human-reviewed PR; block force-push on state main. This is a
  consequence of OC-8, not an argument against it — state repo stays.
- **B2 (blocker for modes 2/3, docs)** — ACCEPT. Posting required checks
  needs checks:write (not in the token list); adding it to the agent App
  lets the agent mint its own required check = self-approval moved into
  modes 2/3. Fix: two identities (agent App pushes branches/PRs; controller
  App posts checks + merges), pin the required check to the controller.
  Moot for v1 if modes 2/3 cut.
- **B3 (major)** — ACCEPT. Token + untrusted code share a job; per-job keys
  don't help when the job is the attacker; pre-push secret scanning misses
  network exfil. Fix: token scoped to one product repo; push in a separate
  step consuming a patch; per-workspace model key with provider-side spend
  cap. Re-examine hosted-runner egress filtering (Fable says it exists).
- **B4 (major, verify)** — ACCEPT. "Human review" in mode 1 is really "any
  non-author identity"; GITHUB_TOKEN can approve if the Actions setting is
  on; pull_requests:write does NOT sub-scope create-vs-approve (round 4
  wrongly passed this). Fix: CODEOWNERS `*` → human handles + code-owner
  review required; Actions approval setting OFF; permissions:{} on agent
  jobs; controller checks reviewer against a human allowlist.
- **B5 (major, docs → VERIFIED)** — ACCEPT, ESCALATED. Org is Free; private
  repos cannot enforce branch protection/rulesets at all (403 confirmed).
  refs/factory/* can't be protected (rulesets target branches/tags). Fix:
  evidence under a tag namespace or controller-written state repo; state
  the paid-plan requirement; OR rely on the controller-writer model (B1)
  which doesn't depend on branch protection. OWNER-CALL: plan upgrade vs
  controller-enforced security vs public-earlier.
- **B6 (major)** — ACCEPT. Agent text reaches privileged readers in 4
  places: decision cards (render from structured fields, quote+cap agent
  text), comment commands (parse from humans only), Obsidian renders
  (escape agent text; remote-image/plugin exfil), mining (output to humans
  + stats only; anything into a dispatch package human-promoted + pinned).
- **B7 (major)** — ACCEPT for v1. Person/team/org scope gives no isolation
  inside one vault (one collaborator list). CUT team/org scope from v1; one
  state repo per trust boundary.
- **B8 (major)** — ACCEPT. Self-hosting needs the special casing the design
  denies: factory runs from a pinned human-released tag (not the story
  branch); process/prompts/gates/controller under CODEOWNERS; classify
  control-plane stories; release is a human action.
- **B9 (minor)** — ACCEPT. Dependency gate covers top-level only; add
  lockfile-diff gate + install with scripts disabled (transitive deps,
  install scripts, version bumps).

## C. Economics + Goodhart

- **C1 (major, strategic)** — ACCEPT. No cost model; ~8 model sessions per
  story minimum, ~160 for 20 stories before rework; one-job-per-step works
  against the calls×context rule. Fix: measure on story 1; add "process
  overhead ratio" headline metric; tier pipeline by risk (small stories
  skip plan review, one reviewer).
- **C2 (major)** — ACCEPT. Budget ceilings are decoration (values in
  agent-writable repo; enforcement point unspecified; self-reported token
  counts). Real controls: provider-side spend cap on per-workspace key,
  timeout-minutes on every job, controller refuses dispatch at ceiling.
- **C3 (major, strategic)** — ACCEPT. Promotion/routing metrics are
  gameable: intervention rate falls when agents record assumptions instead
  of escalating; 2 of 6 escalation classes aren't code-checkable; demo has
  no users so defect-escape is unobserved; routing selects lenient
  reviewers; seeded-defect calibration is P6 (after routing starts P3) —
  move to P3; assertion-count test-gaming is trivial — separate test-author
  dispatch or mutation score.

## D. The human

- **D1 (major)** — ACCEPT. A week away → stall (mode 1) or unbounded
  assumption drift (mode 2). Fix: assumption-debt limit that pauses the
  workspace; explicit absence mode; daily digest; expiry on waiting items.
- **D2 (major)** — ACCEPT. Too many approvals before first story (wireframe
  + PRD + 4 design approvals). Collapse the 4 design approvals into one
  document, one approval (esp. for the demo).
- **D3 (minor, strategic)** — NOTED, fair. 11 owner calls + 4 grills + 1
  external review ratified in a day sits uneasily with principle 15. The
  walking skeleton (E1) is the corrective — real execution, not more paper.

## E. Over-engineering + roadmap

- **E1 (blocker, strategic)** — ACCEPT. The roadmap is the longest
  defensible path to the demo; the hand-run tests the ledger, not the 3
  risky hypotheses (agent produces mergeable stories at tolerable cost;
  intake produces an approveable PRD; cross-family review catches defects).
  Intake (highest product risk) is scheduled 4th. "Freeze" contradicts
  schema-version-on-every-event. Fix: replace P1 freeze with a walking
  skeleton; contracts = v0; freeze after ~10 real stories.
- **E2 (recommendation)** — ACCEPT as the v1 target. Minimum factory: one
  repo, JSONL ledger on a branch/local dir; local execution, one adapter;
  one coder + one cross-family reviewer; human merges every PR; one design
  doc + one approval; inbox = issues with label+assignee; provider spend
  cap.
- **E3 (minor)** — ACCEPT. vision.md accumulated contradictions across
  rounds (concurrency deferred vs allowed; confidence wording post-OC-10;
  stale §13 history rows; "product code ONLY" vs evidence/CODEOWNERS in
  repo; dashboard repo unspecified; README omits rounds 3/4). Fix: split
  into a short current-state spec + a separate decision log.

## F. Product thesis

- **F1 (major, strategic)** — ACCEPT. No baseline. The claim to test:
  factory uses fewer human-minutes or ships fewer defects per story than
  one engineer + coding agent + spec tool, at an acceptable cost multiple.
  Add a CONTROL ARM to the first experiment; if the factory doesn't win,
  stop and reconsider. Moats assessed: ledger matters to regulated teams
  more than solo; routing needs volume a solo user lacks; guided intake +
  wireframes is most distinctive and built last.
- **F2 (major, strategic)** — ACCEPT. Portability is real for model
  runtimes only; every safety property is a GitHub feature, several
  plan-gated. Narrow the claim to "model-runtime-agnostic, GitHub-only."
  Sealed dispatch identity needs the harness version (system prompt/tools/
  compaction differ). Headless subscription use in CI is a per-provider
  terms question (verify).

## G. Correlated blind spots — ACCEPT (process lessons)

- Reviews checked text presence, not truth (A1 passed twice; a 20-line
  script refuted it). → Future grills must EXECUTE load-bearing claims.
- Every round added mechanisms, none removed; 100% reviewer acceptance is
  a warning sign (round 1 included). → Require a cut list each round.
- The cleverer fix was preferred to the plainer (merge-tree vs a branch
  setting). → Prefer the platform's own guarantee.
- "Verified" conflated docs-checked with reasoned-from-text. → Label which.
- Nobody attacked the trust boundary as a whole. → Threat-model the whole
  token→repo map, not controls one at a time.

## Owner calls opened (strategic — for Randy)

- **OC-12 — Roadmap: walking skeleton vs P1 freeze.** REC: adopt E1/E2 —
  replace the P1 contract freeze with a 5-story local walking skeleton +
  control arm; contracts v0; freeze after ~10 real stories.
- **OC-13 — v1 cut list.** REC: adopt Fable's cuts (cloud adapter, merge
  modes 2/3 + Level 3, leases, team/org scope, mining, multi-repo, flag
  registry, board custom fields → labels, wireframe tiers → local URL,
  Copilot/remediation knobs, 4 design approvals → 1). Keep the full vision
  as the north star; v1 is the minimum that proves the thesis.
- **OC-14 — Security model given Free plan.** REC: controller-writer model
  (B1/B2) so security doesn't depend on branch protection; decide paid-plan
  upgrade vs public-earlier separately. Two identities (agent/controller).
- **OC-15 — Merge protocol.** REC: adopt A3 (update-before-review + strict
  up-to-date setting), cut merge-tree + auto-revert; verify on a real PR.
- **OC-16 — Baseline / kill criterion.** REC: adopt F1 — control arm in the
  first experiment; explicit stop-and-reconsider if the factory doesn't win
  on human-minutes or defects at an acceptable cost multiple.

## Experiments to run (Fable's "what would convince me", cheapest first)

1. Ledger contention under load (1h) — A1 already reproduced at N=2;
   extend to 5 writers + the retry policy.
2. Squash equivalence on GitHub (1h) — one real PR, rename + line-ending.
3. Throwaway private repo on the real plan (half day) — settles every
   "verify": protection enforceability, App/GITHUB_TOKEN approval, checks
   without checks:write, refs/factory deletion, queued-job cancellation.
4. Walking skeleton + control arm (2-3 days) — 5 to-do stories local
   minimum factory vs single coding-agent session; tokens/wall/human-min.
5. Seeded-defect review test (1 day) — 10 bugs; same-session vs fresh
   same-family vs cross-family.
6. Intake spike with 3 non-owner engineers.
7. Injection canary (dependency README + issue → assumption log/card?).
8. Absence simulation (48h unanswered inbox).