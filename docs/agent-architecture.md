# Agent architecture — ephemeral workers, thin orchestrator, runtime-built instructions

**Status:** design direction endorsed by Randy (2026-11-16) · grounded in
SKEL-1…SKEL-5 evidence, not theory.

## The decision

The factory uses a **hybrid**: a thin, long-lived **orchestrator** holds the
run plan and coordinates; **workers are ephemeral LLM sessions** launched
with **instructions built at run time** (sealed dispatch packages). There
are no static, long-lived worker agents and no agent-resident memory.

```
orchestrator (long-lived, thin)
  │  holds: run plan, story order, gate results, dispositions, budget
  │  does:  dispatch, verify-by-execution, route findings, escalate
  │  never: product code authorship at scale, state-repo writes (OC-14)
  ▼
dispatch.seal(role package + pinned inputs @ SHA + manifest + stop rules)
  ▼
ephemeral worker  =  hermes -z <package> -m <model> --yolo
  │  lives minutes, dies clean; output + usage persist, the agent does not
  ▼
deterministic gates → findings → disposition by execution → next dispatch
```

## Why ephemeral workers (evidence, not preference)

- **Isolation is structural.** A fresh session cannot see the author's
  reasoning — it is not in its window. SKEL-1: the control arm (one long
  session, same model) shipped a data-loss blocker + a self-certifying
  test to green tests; the factory's fresh cross-family reviews caught
  both classes before merge. 0 escaped defects vs 6.
- **Instructions pinned to reality.** `dispatch.seal()` embeds the live
  story spec, design slice, manifest, and base SHA at dispatch time.
  Same inputs → same bytes → same sha256. No stale-docs drift; every
  dispatch is replayable from `runs/<run>/dispatch/*.md`.
- **Least privilege per task.** The package carries only this story's
  manifest and stop rules. Scope is enforced by package content, not by
  hoping a generic persona remembers its role.
- **Model routing is a parameter.** Coder/reviewer models swap per story
  or risk tier without rework (the MEA-3 calibration ran three modes by
  changing one flag).
- **No state to corrupt.** The ledger — not the agent — is truth.

## Why a thin long-lived orchestrator

Coordination benefits from continuity: story order, gate history, which
findings are dispositioned, budget remaining, what the human is waiting
on. Re-deriving that per dispatch would cost more than it saves. The
orchestrator is the one place warm context pays for itself.

**Constraints on the orchestrator (learned the hard way):**
- It verifies every load-bearing claim by execution — reviewer EXECUTED
  labels were refuted by probe in SKEL-1 (TOD-2) and SKEL-2. Trust
  findings, verify verdicts.
- When it applies fixes itself, those fixes get the SAME adversarial
  pass as any worker's: 3× in SKEL-1 a remediation round introduced its
  own defect, each caught by the next review. The orchestrator is not
  exempt from the loop.
- It never holds state-repo write credentials (OC-14); submissions go
  through the controller.

## Where memory lives: the repo, not the agent

Ephemeral agents don't accumulate skill — so accumulation is
**externalized into tested, reviewed artifacts**:
- **Gates** (`mutation.py`, `announcements.py`, `boundaries.py`, …) —
  each discovered defect class becomes a deterministic check, proven
  fail-before/pass-after. The class can't escape again.
- **Findings log** (`state/findings.jsonl`) — stable class slugs, escape
  flags, reviewer precision. The measurement surface for tuning.
- **Contracts in packages** — lessons carried story-to-story as explicit
  dispatch inputs (TOD-3's contracts came from TOD-2's findings).
- **Process docs** (`process/`, this file) — the reusable role knowledge.

This is the synthesis: isolation AND accumulation, because accumulation
lives in things that are tested, not in a model's head.

## Known costs and mitigations (honest)

| Cost | Evidence | Mitigation |
|---|---|---|
| Re-exploration per dispatch | coder token burn in SKEL-1 | seam-recon prep + pinned context bundles (build the exploration ONCE, upstream, into the package) |
| Package-builder is a single point of failure | a bad seal() bugs every dispatch | test it like product code; determinism (sha256) makes regressions visible |
| Cold-start latency per worker | minutes per dispatch | risk-tiering (MEA-2): small stories get fewer dispatches |
| Post-hoc debugging only | agent is gone after exit | sealed package + output + usage = full replay trail |
| No automatic skill accumulation | lessons must be curated | the prevention loop: every finding → gate or contract, same round |

## What exists today vs what's next

**Exists:** `dispatch.py` + `adapters/hermes.py` (launcher), the gate
suite, controller/ledger/metrics/risk/budget, `process/intake-agent.md`
(the one reusable role package so far). SKEL-1's coder/reviewer
instructions were hand-built per dispatch — the loop is proven, the
role library is not yet standing.

**Next (owner-directed):** a runtime-neutral role library — coder,
cross-family reviewer, plan-reviewer, test-planner, decomposer,
orchestrator runbook — as `process/*.md` templates that `dispatch.seal()`
composes with pinned inputs. Roles stay runtime-neutral (lineage.md:
no Copilot `.agent.md` coupling); any harness drives them. Build the
library just-in-time as the next real product needs each role, not all
eight up front.

## Rejected alternative: static worker agents

Warm context and accumulated skill are real benefits, but they undercut
the isolation that demonstrably won SKEL-1: context drift, anchoring on
prior decisions, stale instructions, hidden effective prompts,
corruptible state. The control arm WAS effectively a static single
session — it lost on escaped defects. Static workers are rejected for
this factory; the hybrid keeps warmth only where coordination needs it.
