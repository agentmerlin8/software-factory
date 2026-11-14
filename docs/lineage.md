# Lineage — what carries forward, what gets scrapped

The rewrite is ground-up, but five months of runs produced hard-won
mechanics. This file records the salvage boundary (read-only extraction;
the old repos are never refactored as part of this build).

## Keep (copy + genericize when needed)

From `agentmerlin8/ai-software-factory` (kit S1/S2/S3.5, merged) and the MIE
reference implementation:

- Ledger schema + append-only event discipline + evidence-SHA validation
- Controller / state machine / claim lock / fail-closed override file
- Deterministic gates (digest, pre-review) + gate catalog pattern
- Dispatch-package / context-bundle assembly (pinned inputs at SHA)
- Review lane: package determinism, findings schema, disposition ledger,
  record pinned to head, cross-family panel
- Renders: state / dashboard / provenance / story card
- Board sync (Stage fields, derived mirrors, sync-only writes)
- Token-efficiency rules (metering, routing matrix completeness, seam recon)
- Workspace + environment declarative schemas (accepted v0.3)
- Process rules now living in Hermes skills → move in-repo as `process/`

## Scrap (do not carry)

- Copilot `.github/agents/*.agent.md` layout as the primary agent definition
  (agent inheritance risk; runtime coupling). Agent role packages become
  runtime-neutral; Copilot flavor, if ever, is one adapter's export.
- The kit v0.1 grill debt / pending owner calls — superseded by this
  vision's open calls; old findings get a disposition pass, not a fix pass.
- ADO work-item state machinery (work-side only).
- Benchmark-repo scaffolding as product structure (benchmarks become a
  capability, not the repo's shape).
- Hermes-specific coupling: config writes for routing, runtime-DB usage
  harvest as the only metering path (adapter-scoped instead).

## Old repo disposition

**RATIFIED (OC-1, Randy 2026-11-14): keep it, make it private.**
`agentmerlin8/ai-software-factory` was flipped to private 2026-11-14
(verified). No archive. It stays untouched during the build and serves as
the read-only salvage source. A README notice pointing to the successor
goes in once `software-factory` reaches P5 (demo end-to-end); the new repo
flips public at that same milestone (Randy, 2026-11-14).

## Boundary rule

This repo is generic from commit one: no MIE/product-specific names, no
client identities, no private-repo references in docs or templates.
Field lessons carry; identities don't.