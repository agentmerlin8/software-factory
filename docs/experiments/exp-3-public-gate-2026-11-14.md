# EXP-3 — Public + Free unlocks the native merge gate (OC-15 restored)

**Date:** 2026-11-14 · **Trigger:** Randy — "we should not be on a free plan…
lets just make it public then" · **Evidence repo:** `agentmerlin8/factory-exp-throwaway`
(now PUBLIC), PRs #6–#9 · **Scripts:** `~/.hermes/cache/scratch/factory-exp/exp3-*.py|sh`

## Question

Does making the repo PUBLIC (staying on the Free plan) unlock branch
protection / rulesets / the strict up-to-date gate that EXP-1 found 403 on
private Free?

## Results — YES, verified end-to-end

1. **Visibility flip:** private → public. The 403 "Upgrade to GitHub Pro"
   disappears immediately.
2. **Branch protection PUT → 200** (was 403 private). `strict: true` accepted.
3. **Ruleset POST → 201** (was 403 private). `required_status_checks` with
   `strict_required_status_checks_policy: true` accepted, enforcement=active.
4. **Stale PR merge → REFUSED (405)** "Required status check … is expected",
   `mergeable_state=behind`. The gate blocks a stale branch.
5. **Updated PR merge → SUCCESS** once the branch is up to date and the
   required check is green (`mergeable_state=clean`).

**Conclusion: OC-15's ORIGINAL mechanism works on public Free.** The
controller-enforced amendment proposed after EXP-1 is NO LONGER NEEDED —
the platform's own "require branches up to date" guarantee is available.
This is the "prefer the platform's own guarantee over clever mechanisms"
lesson (Fable review 2) applied.

## Two configuration gotchas (both cost a false-negative during testing)

- **`strict: true` with an EMPTY required-checks list is a NO-OP.** A stale
  PR merged straight through (PRs #6, #7, #8). The strict up-to-date
  enforcement only bites when at least one status check is REQUIRED.
  → The factory must register a real required check (the controller's
  review-gate / CI check) for the gate to mean anything.
- **`enforce_admins: true` also blocks direct pushes to main** (GH006
  "Protected branch update failed"). Fine for the factory (trunk-based via
  PR), but test scaffolding that pushes main directly must disable
  protection first.

## Decision recorded

Randy (2026-11-14): make the factory repo PUBLIC rather than upgrade the
org. OC-14 already anticipated "public-earlier" as the Free-plan escape
hatch. The org stays Free; the repo goes public; native branch protection
is restored.

## Acceptance

- [x] public + Free unlocks protection (200) and rulesets (201)
- [x] strict up-to-date gate refuses stale merge (405) and passes updated merge
- [x] configuration gotchas documented (empty-checks no-op; enforce_admins blocks pushes)

## Follow-up

- Flip `agentmerlin8/software-factory` to public (Randy approved).
- OC-15: revert to the original "enable require-branches-up-to-date" mechanism;
  drop the controller-enforced amendment. Record the ratification.
- SKEL-4: register a real required status check so `strict` is not a no-op.