# SKEL-3 plan — Controller-writer security (issue #5, OC-14)

**Status:** SEC-1/SEC-2/SEC-3 implemented (2026-11-15) — identity pair live and
proven end-to-end; awaiting owner review of slice 3 · **Date:** 2026-11-15
**Threat model:** a model-driven job (or injected content inside one) must
never be able to write the state repo. Security must NOT depend on branch
protection (works on Free; protection is defense-in-depth now that repos
are public). Push contention (MRG-1) is fixed by the same mechanism: one
serialized writer.

## Current identity landscape (verified 2026-11-15)

- `mie-factory-bot` (app 5239072): contents/issues/PRs/org-projects write,
  installed on ALL org repos. Used for board sync + MIE. **Too broad to be
  the agent identity for state-repo security** — it can write everything.
- `entire` (app 2626939): checks/contents/workflows/PRs write + admin read.
- **Pair created 2026-11-15** (org-owned, manifest flow):
  `agentmerlin8-factory-agent` (app 5777949; contents/PR write, metadata read;
  install selection=selected, ONLY factory-todo-demo) and
  `agentmerlin8-factory-controller` (app 5777982; contents/checks write,
  metadata read; install selection=selected, ONLY software-factory).
  Secrets wired stdin-only: `CONTROLLER_APP_ID` + `CONTROLLER_PEM` on the state
  repo. Product-repo agent secrets (`AGENT_APP_ID`/`AGENT_PEM`) land with the
  first agent workflow — factory-todo-demo has none yet.
- Names: `factory-agent` / `factory-controller` were globally taken, hence the
  `agentmerlin8-` prefix. Code keys off the App ID, not the name.

## Design (v1 minimum)

**Two NEW GitHub Apps, least privilege, repo-scoped installs:**

1. **`factory-agent` App** — the identity model-driven jobs run under.
   - Permissions: `contents: write`, `pull_requests: write`, `metadata: read`.
   - Installed ONLY on product repos (factory-todo-demo, future products).
   - **NOT installed on the state repo at all** → it cannot mint a token
     for the state repo. The refusal is structural (no installation), not
     a policy hope.
2. **`factory-controller` App** — the sole state-repo writer.
   - Permissions: `contents: write`, `checks: write`, `metadata: read`.
   - Installed ONLY on the state repo.
   - Its private key lives ONLY as the `CONTROLLER_PEM` Actions secret on
     the state repo, consumed ONLY by the controller workflow — a job
     that runs no model output and no product code (pure Python validator).

**Flow:**
- Agent job (factory-agent identity) emits a result artifact: a JSON
  "ledger submission" pushed to a branch in the PRODUCT repo (or uploaded
  as an Actions artifact), never to the state repo.
- Controller workflow (state repo, `workflow_dispatch` + repository_dispatch
  from the product repo) fetches the submission, VALIDATES it (schema,
  hash-chain continuity, event-type allowlist, policy file), and appends
  to the ledger. One concurrency group (`controller-writer`, no
  cancel-in-progress) serializes all appends → MRG-1 contention gone.
- Validation policy (`controller-policy.json`) lives in the state repo;
  changes to it require a human-reviewed PR (CODEOWNERS + protection on
  that path where available; the controller refuses submissions that
  attempt to modify policy).

## Slices (OC-17 sizing)

- **SEC-1: submission schema + validator** (~250 lines + tests). Pure
  Python: `factory/controller.py` — validate a submission (schema, chain,
  allowlist), append to a ledger copy, refuse policy mutations. No GitHub
  calls in the core; fully unit-testable. THE SECURITY CORE.
- **SEC-2: controller workflow + contention test** (~120 lines YAML +
  script). State-repo workflow: mint controller token, fetch submission,
  run validator, commit+push under one concurrency group. Contention
  test: N parallel dispatches → all land, zero exhausted retries, chain
  intact.
- **SEC-3: the two Apps + negative proof** (setup + evidence). Create
  factory-agent + factory-controller via manifest flow (2 owner clicks
  each), repo-scoped installs, secrets wired stdin-only. NEGATIVE TEST:
  mint an agent token, attempt a state-repo push → must fail (403/404).
  POSITIVE: controller token appends via the workflow. Evidence recorded.

## SEC-3 evidence (executed 2026-11-15)

- Agent token scope from a real installation token: `['agentmerlin8/factory-todo-demo']`
  (total_count 1, selection=selected).
- Negative, write path: `git push --dry-run` to software-factory -> HTTP 403;
  `POST /git/refs` -> 403 "Resource not accessible by integration".
  Positive control: read of factory-todo-demo -> 200.
- Nuance: the state repo is PUBLIC, so the agent token can READ it (any token
  can). The isolation we rely on is on WRITES — which is what the ledger needs.
  `--dry-run` authenticates and negotiates with the server but writes nothing,
  so it is the safe way to prove a write decision.
- Controller token scope: `['agentmerlin8/software-factory']`; `git push
  --dry-run` to the state repo accepted (rc 0); push to the product repo
  refused.
- Positive end-to-end: `controller-writer` run 43797143412 (workflow_dispatch,
  submission hosted in the product repo at
  `runs/proofs/sec-3-submission.json`) completed success; the state repo gained
  commit `d5d63a7` authored by `factory-controller[bot]` and the ledger went
  119 -> 120 rows with the chain intact.
- **Independent re-confirmation (second session, 2026-11-15):** controller run
  43797734014 appended a second probe (ledger 120 -> 121, chain intact, commit
  `2d0093e` by factory-controller[bot]). Direct API negative proof
  (`runs/sec-3-independent-proof.json`): agent PUT to the state ledger -> 403,
  agent create state ref -> 403; controller read state -> 200; agent create
  product ref -> 201 (cleaned up). `scripts/proof-identity.py` re-run for BOTH
  identities with correct args -> RESULT: PASS each (agent: push product OK,
  push state refused; controller: push state OK, push product refused).
  NOTE on script usage: arg3 = must-fail repo, arg4 = push-target the token
  SHOULD be able to push (owner/repo form, not a URL).

## Acceptance (issue #5)

- [x] agent cannot write the state repo directly (negative proof above)
- [x] controller is the sole state-repo writer (workflow + identity map)
- [x] contention test: parallel writers, no exhausted retries (SEC-2 local
      harness: 12 writers x 5 events, all 60 land, chain intact, zero retries)

## Owner touchpoints (cannot be automated)

- 2 App creations (manifest confirmation click each) + 2 repo-scoped
  installs. I'll stage the manifest helper and hand you the exact clicks.
- The state repo itself: **DECIDED (Randy, 2026-11-15): keep state in
  software-factory for v1** (`runs/` + `state/`, SKEL-1 precedent). The
  controller workflow lives there; the dedicated state-repo split (OC-8)
  comes later per OC-13. The security model is identical either way:
  factory-agent is not installed on software-factory's STATE paths —
  enforcement is via the controller-only write path + CODEOWNERS on
  runs/ + state/, since the agent App needs repo access for product work
  in sibling repos but gets NO install on software-factory itself.

## What this does NOT build (cuts)

- No claim leases, no distributed CAS — one concurrency group is the
  platform's own guarantee (prefer it over clever mechanisms).
- No webhook receiver — repository_dispatch + workflow_dispatch suffice
  for v1 (the Apps are writer-only identities, events: []).
- No paid plan, no ruleset dependency.
