# DSH-2 — Data layer + derived metrics (pure TS)

## Acceptance criteria
1. Typed fetch/parse of the three API endpoints (/api/runs, /api/ledger,
   /api/findings) into view models; a per-source {error} response is surfaced
   as a typed error state, never thrown, never fabricated rows.
2. Exact derived-metric formulas (from the approved PRD):
   - escaped defects per repo = findings where (escaped_gate OR escaped_review)
     AND klass != 'false-positive' AND disposition != 'rejected' AND summary
     does NOT start with 'RESOLVED'.
   - per-story tokens/wall/human-min = metrics.py harvest semantics over
     dispatch_completed (+ correction re-attribution by story/role).
   - overhead ratio: per-story = noncoder/coder (null when coder==0);
     HEADLINE = AGGREGATE sum(noncoder)/sum(coder) across scope (null when
     total coder==0), NOT mean of per-story ratios.
   - mean review rounds = mean over FACTORY-arm stories in scope (control
     excluded).
3. Nulls render as 'not recorded' — the data layer returns null (never 0)
   for missing measurements; a fmt helper renders null -> 'not recorded'.
4. All logic is PURE functions (no React, no fetch side effects in the
   metric functions); fully unit-tested against fixture ledger/findings
   data that mirrors the real schemas.
5. Scope filtering: a function selects rows by run/repo; 'all' = everything.

## Manifest (files you may touch)
- src/data/types.ts, src/data/api.ts, src/data/metrics.ts, src/data/format.ts
- src/data/metrics.test.ts, src/data/api.test.ts, src/data/fixtures.ts
- src/App.tsx, src/App.test.tsx (only if a smoke wiring is needed)

## Design slice
- The metric functions take parsed rows as input (pure); api.ts does the
  fetch + parse and returns {rows} | {error}. Keep them separable so the
  formulas are testable without a server.
- Fixture data must include: a correction event re-attributing tokens,
  a false-positive finding, a rejected finding, a RESOLVED-marker finding,
  a control-arm story, a story with coder_tokens==0 (overhead null), and
  missing human_min (null, not 0).
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- escaped-defect formula excludes false-positive/rejected/RESOLVED.
- overhead per-story null when coder==0; headline is aggregate not mean.
- mean rounds excludes control arm.
- correction re-attribution counted.
- null human_min stays null; fmt(null)=='not recorded'.
- api error response -> typed error, no throw.
- scope filter selects subset; 'all' returns everything.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch dsh-2. Do NOT merge; the human merges.
