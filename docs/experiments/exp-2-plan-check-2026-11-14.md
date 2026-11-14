# EXP-2 — Throwaway-repo plan check (settles all "verify" items)

**Date:** 2026-11-14 · **Issue:** #9 · **Status:** DONE — all five items tested
**Evidence repo:** `agentmerlin8/factory-exp-throwaway` (private, org Free plan)
**Identity:** `mie-factory-bot` App (id 5239072), installed org-wide (`selection=all`),
token perms: `contents/issues/pull_requests: write`, `organization_projects: write`, **no checks**.
**Scripts:** `~/.hermes/cache/scratch/factory-exp/exp2-*.py` + probe workflows in the evidence repo.

## Results

### 1. Branch protection on Free private — CONFIRMED UNAVAILABLE
- `PUT /branches/main/protection` → **403** "Upgrade to GitHub Pro or make this repository public".
- `POST /rulesets` → **403**, same message.
- OC-14's premise holds: security must NOT depend on branch protection.

### 2. Approval counting — SPLIT result
- **GITHUB_TOKEN approval: REFUSED.** `POST /pulls/5/reviews` with the Actions
  token → **422 "GitHub Actions is not permitted to approve pull requests."**
  Repo toggle `can_approve_pull_request_reviews=true` → **409** (org policy
  forbids it); org policy API needs `admin:org` (not held). On this org,
  GITHUB_TOKEN can never approve — B4's "Actions approval setting OFF" is
  enforced by org policy, stronger than expected.
- **App approval: WORKS.** Same call with an App installation token → **200**,
  recorded `APPROVED by mie-factory-bot[bot]`, PR `mergeable_state=clean`.
  The controller App can approve/merge; mode-1 human-merge remains policy.

### 3. Check posting without checks:write — REFUSED (as designed)
- `POST /check-runs` with the App token → **403 "Resource not accessible by integration"**.
- Bonus probe: commit **statuses** API also **403** (needs `statuses:write`, absent).
- **SKEL-3 requirement:** the controller App manifest must add `checks: write`
  (check runs) or `statuses: write` (commit statuses) — neither is granted today.

### 4. App token deleting refs/factory/* — PASS
- Create `refs/factory/exp2-test` → 201; read → 200; **DELETE → 204**; read-after → 404.
- `contents: write` suffices. The evidence-tag/ref namespace design is viable
  with the current App permissions.

### 5. Concurrency group — third queued run CANCELS the second (confirmed)
Three `workflow_dispatch` runs ~3s apart, one group, `cancel-in-progress: false`:
- run 1: in_progress → success;
- run 2: **cancelled, 0 jobs executed** (new arrival cancels the *pending* run);
- run 3: pending while run 1 ran → success after run 1 finished.
- **Implication for OC-14:** one concurrency group serializes the controller,
  but queued controller runs do NOT accumulate — a newer dispatch cancels the
  pending one. The controller needs idempotent re-dispatch/retry (or a queue
  outside Actions), not "fire and forget" queuing.

## Acceptance

- [x] each "verify" item tested on a throwaway private repo
- [x] results recorded; design assumptions confirmed or corrected

## Design deltas for SKEL-3 / SKEL-4

1. Controller App manifest: add `checks: write` (or `statuses: write`).
2. Up-to-dateness is controller-enforced (EXP-1), not a repo setting.
3. Controller dispatch must tolerate concurrency cancellation (retry/requeue).
4. GITHUB_TOKEN approvals are org-blocked — no configuration can enable them;
   the two-identity model (OC-14) is the only approval path besides humans.