# PROD-1 story decomposition — factory dashboard (v1, approved PRD)

**PRD:** runs/prod-1/intake/c61b6d2bab46/PRD.md (APPROVED, 2 rounds)
**Product repo:** agentmerlin8/factory-dashboard (to create, public)
**Dependency order:** DSH-1 → DSH-2 → DSH-3 → DSH-4 → DSH-5 → DSH-6
(expand-first; each independently mergeable; main deployable after each)

## DSH-1 — Scaffold + thin data server (infrastructure slice)
- Vite+React+TS+Vitest scaffold; Python stdlib server.py (loopback, GET-only).
- Endpoints: /api/runs, /api/ledger?run=<id>, /api/findings. 405 on non-GET.
- Per-source error format {error: "<file>: <reason>"}; corrupt file never crashes.
- Server tests (Python) + CI (build + vitest + server tests).
- Structural signal: new external provider? No — local files only. 1 signal max.

## DSH-2 — Data layer + derived metrics (pure TS)
- Fetch + parse API responses; typed view models.
- Exact PRD formulas: escaped-defect count (findings, escaped_gate OR
  escaped_review, excl false-positive/rejected/RESOLVED), per-story harvest
  semantics, overhead per-story + AGGREGATE headline, mean rounds factory-only.
- Nulls -> 'not recorded' convention in the data layer (never 0).
- Pure functions, fully unit-tested against fixture ledger/findings data.

## DSH-3 — Headline cards + scope selector
- 5 cards from DSH-2 aggregates; scope selector discovered from /api/runs.
- Scope change recomputes cards; prefs persist 'factory-dash:prefs'.
- Empty scope -> empty state; per-source error -> error state (file+reason).

## DSH-4 — Per-story table
- Rows per story in scope; sortable by rounds/escaped/wall (3 columns only).
- 'not recorded' rendering; matches DSH-2 harvest output.

## DSH-5 — Trend views
- 3 charts: rounds-per-story, escaped-per-story (factory arm + control),
  model-mix tokens. Hand-rolled SVG (no chart dep). Tooltips exact values.
- Empty scope -> friendly empty state. Cycle-time trend: documented v2 cut.

## DSH-6 — Composite wiring + a11y polish
- Full dashboard: scope above all views, all react; keyboard/focus/contrast
  gates; error + empty states exercised end-to-end against the real server.

## Human-minutes instrumentation (this run)
Every owner touchpoint logged with elapsed minutes: intake Q&A, PRD
approvals, Storybook approvals, merges, escalations. Ledger human_min on
the relevant events. First run to measure the human side.
