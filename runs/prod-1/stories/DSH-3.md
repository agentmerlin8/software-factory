# DSH-3 — Headline cards + scope selector

## Acceptance criteria
1. Five headline cards render from DSH-2 aggregates over the selected scope:
   total tokens, total cost, escaped defects, mean review rounds (factory-arm
   only), process-overhead ratio (AGGREGATE). Each card shows a real computed
   number or 'not recorded' — never 0 for missing data.
2. COST DISPLAY SEMANTICS (carried from DSH-2 round-9, PRD authoritative):
   cost is tokens-only until a price table exists, so cost_usd null OR 0
   renders 'not recorded'. A nonzero cost renders the value (2 decimals).
   (wall_s zero IS a real measurement and renders 0 — only cost treats 0 as
   unknown.)
3. Scope selector lists runs discovered from GET /api/runs (NOT hardcoded);
   default = all. Changing scope recomputes all cards from that subset.
4. Scope selection persists across reload via localStorage 'factory-dash:prefs'.
5. A scope with no data shows a friendly empty state, not stale numbers; a
   per-source fetch error shows the error state (file + reason), never crashes.
6. Cards match the approved wireframe (templates/dash-wireframes): warm-paper
   theme, light + dark, contrast-audited AA, themed :focus-visible on the
   selector buttons (aria-pressed).

## Manifest (files you may touch)
- src/components/HeadlineCards.tsx, src/components/ScopeSelector.tsx
- src/components/HeadlineCards.test.tsx, src/components/ScopeSelector.test.tsx
- src/hooks/useDashboardData.ts, src/hooks/useDashboardData.test.ts
- src/App.tsx, src/App.test.tsx, src/index.css
- src/data/format.ts (only if a cost-display helper is needed)

## Design slice
- Reuse DSH-2's fetch + metrics functions; do NOT reimplement formulas.
- The wireframe components (templates/dash-wireframes/src/DashWireframes.tsx)
  are the visual reference — match their structure/classes, wire to real data.
- Cost display: a helper costDisplay(costUsd) -> 'not recorded' when null/0,
  else fmt(costUsd). Keep it in format.ts, unit-tested.
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- cards render computed aggregates; missing data -> 'not recorded' not 0.
- cost 0 and null -> 'not recorded'; nonzero cost -> value.
- scope selector options come from /api/runs; change recomputes cards.
- prefs persist across reload; empty scope -> empty state; error -> error state.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch dsh-3. Do NOT merge; the human merges.
