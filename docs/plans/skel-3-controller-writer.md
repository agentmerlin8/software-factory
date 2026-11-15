# SKEL-3 plan — Controller-writer security (issue #5, OC-14)

**Status:** draft for owner review · **Date:** 2026-11-15
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
- No dedicated agent/controller pair exists yet.

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

## Acceptance (issue #5)

- [ ] agent cannot write the state repo directly (negative proof)
- [ ] controller is the sole state-repo writer (workflow + identity map)
- [ ] contention test: parallel writers, no exhausted retries

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
