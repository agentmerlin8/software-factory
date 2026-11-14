# Grill disposition — round 1 → fix pass (2026-11-14)

Maps EVERY round-1 finding to its disposition. Nothing silently dropped.
Owner answers: Randy 2026-11-14 (board = lane-per-state + CLI moves;
failures clearable by human OR authorized agent; measurement = cycle time,
cost, models, all statistics; all other recommendations accepted, plus the
13 minors as recommended).

Disposition key: **FOLDED** = fixed in the vision/docs now (section given) ·
**RESOLVED** = owner decision recorded · **TASK** = assigned to a build phase
(named) · **DEFERRED** = explicitly out of early scope · **NOTED** =
planner-owned constraint recorded, no blocker.

## Blockers

| # | Finding | Disposition | Where |
|---|---------|-------------|-------|
| 1.1 | P5 vs P7 public-flip contradiction | RESOLVED (Randy: P5) | vision §11 P5/P7; open-calls OC-1; lineage |
| 2.1 | Board schema undefined | RESOLVED (Randy: lane-per-state, CLI moves) | vision §3.4 board minimum schema; exact state list = TASK P1 |

## Majors

| # | Finding | Disposition | Where |
|---|---------|-------------|-------|
| 2.2 | Feature-acceptance gate failure path | FOLDED | vision §4 flow FAIL branch; §11 P1 |
| 2.3 | Gate-to-transition catalog | TASK P1 | vision §11 P1 (transition catalog requirement) |
| 2.4 | Escalation mechanism | FOLDED (Randy: human OR authorized agent) | vision §6 principle 4; §4 BLOCKED block |
| 2.5 | Intake Engine in architecture | FOLDED | vision §5 Intake Engine |
| 2.6 | Claim-lock vs ephemeral Actions | FOLDED (Randy: yes to leases) | vision §5 claim leases; §6 principle 9 |
| 2.7 / 5.6 | Drag-to-dispatch placement (duplicate) | RESOLVED | vision §3.4 + §11 P5 |
| 2.8 | Demo repo location | FOLDED | vision §8 demo repo bullet |
| 2.9 | Model roles/tiers | FOLDED (schema) + TASK P1/P3 | vision §5 model routing; §11 P1 |
| 2.10 | Self-host workspace | FOLDED | vision §5 workspace self-host (.factory/) |
| 3.1 | "Right questions" unmeasurable | FOLDED | vision §1 success bullet (PRD approval) |
| 3.2 | Level-3 promotion thresholds | TASK P6 | vision §7 + §11 P6 (≥3 features of data) |
| 3.3 | Quality/cost dimensions | FOLDED (Randy: expanded) | vision §1 + new §10 Measurement |
| 4.1 | Feature vs story state | FOLDED | vision §5 feature state computed render |
| 4.2 | Storybook exposure tiers | FOLDED | vision §5 Intake Engine LIVE/LINK/SCREENSHOT |
| 4.3 | Board sync direction | FOLDED | vision §5 board sync one-way + webhook trigger |
| 4.4 | Ephemeral Actions vs review loops | FOLDED | vision §5 per-step dispatch + checkpoints |
| 5.1 | Story failure/rejection lifecycle | FOLDED | vision §4 BLOCKED block; §6 principle 4; §11 P1 |
| 5.2 | Feature-gate fail → who dispatches fix stories | FOLDED | vision §4 flow (auto-create in Backlog, normal pipeline) |
| 5.3 | Onboarding command | FOLDED | vision §5 onboarding (factory init [--guided]) |

## Minors (planner-owned; recorded, not blocking)

| # | Finding | Disposition | Where |
|---|---------|-------------|-------|
| 1.2 | Flow diagram missing expand-only/flagged | FOLDED | vision §4 (note under main merge) |
| 1.3 | "Review BEFORE the PR" wording | FOLDED | vision §4 (review on branch → PR opened) |
| 1.4 | README stale open-calls status | FOLDED | README read order + status |
| 2.11 | Story format schema | TASK P1 | vision §11 P1 story schema |
| 2.12 | Who creates board feature items | FOLDED | vision §3.4 (P0 manual, P4+ auto) |
| 3.4 | Main-deployability verification | FOLDED | vision §11 P3 deployability guard |
| 3.5 | "Randy keeps architecture" unmeasurable | NOTED | process principle, not a product claim — no change needed |
| 4.5 | Storybook spike throwaway vs reusable | FOLDED | vision §11 P0 (throwaway exploration) |
| 4.6 | Workspace dir collision | FOLDED | vision §5 (configurable; self-host .factory/) |
| 5.4 | Dependency management | FOLDED | vision §5 dependency policy |
| 5.5 | CI/CD boundary | FOLDED | vision §12 deferred (factory generates baseline CI at P5) |
| 5.7 | "Live proof" undefined | FOLDED | vision §4 (automated post-deploy evidence) |
| 5.8 | Adapter priorities | TASK P6 | vision §11 P6 (api-direct, claude-code, codex, copilot-cli) |

## Informational (no action)

6.1, 6.2, 6.3 — OCs mutually consistent, aligned with 2026-11-13 locked
decisions and the lineage salvage boundary. Confirmed; no change.

## Aggregate

- 2 blockers: both RESOLVED (1.1, 2.1).
- 19 unique majors: 15 FOLDED (2.2, 2.4, 2.5, 2.6, 2.8, 2.10, 3.1, 3.3, 4.1,
  4.2, 4.3, 4.4, 5.1, 5.2, 5.3), 3 TASK (2.3→P1, 2.9→P1/P3, 3.2→P6),
  1 RESOLVED (2.7/5.6). Every one has a named home; none left open.
- 13 minors: 10 FOLDED (1.2, 1.3, 1.4, 2.12, 3.4, 4.5, 4.6, 5.4, 5.5, 5.7),
  2 TASK (2.11→P1, 5.8→P6), 1 NOTED (3.5). All recorded.
- 3 informational: confirmed.

Total: 37 findings (2 + 19 + 13 + 3), all dispositioned.

No finding dropped. Round-2 re-grill scope: verify the FOLDED edits landed
and are internally consistent; do NOT re-open ratified owner decisions or
promote later-phase TASK items into blockers.