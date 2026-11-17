# DSH-5 — Trends (rounds, escaped defects, model mix)

## Acceptance criteria
1. Review-rounds bar chart: one bar per factory-arm story in scope, height
   proportional to rounds (max-normalized), label = story id, title tooltip
   "STY: N rounds". Data from harvestStories (reuse). role=img with aria-label.
2. Escaped-defects bar chart: one bar per story (all arms) in scope, height
   proportional to escaped defects (max-normalized, min divisor 1), distinct
   bar color, label distinguishes control arm. Null escaped -> bar height 0
   with a 'not recorded' title, never a fabricated count.
3. Model-mix bars: tokens aggregated by model across the scope (coder +
   non-coder), one row per model with a proportional width bar and a formatted
   token total. Models with no recorded usage are excluded (not shown as 0).
4. All three charts react to scope changes; an empty scope shows a friendly
   empty state, not blank charts. Nulls render 'not recorded', never 0.
5. Matches the approved wireframe (Trends): warm-paper theme, light + dark,
   contrast AA, bar colors meet contrast against the card background.
6. Aggregation is pure unit-tested functions (rounds-per-story, escaped-per-
   story, tokens-by-model); the component renders from them, no inline math.

## Manifest (files you may touch)
- src/components/Trends.tsx, src/components/Trends.test.tsx
- src/App.tsx, src/App.test.tsx, src/index.css
- src/data/metrics.ts (only if aggregation helpers are added)
- src/data/types.ts (only if a view-model field is needed)

## Design slice
- Reuse harvestStories + the escaped-defect formula; tokens-by-model sums
  dispatch/correction tokens grouped by row.model (only hasUsage rows).
- The wireframe Trends is the visual reference; match structure/classes.
- Bar heights/widths are percentages of the max (guard max=0 -> no bars or
  zero-height, never divide-by-zero / NaN).
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- rounds bars: factory-arm only, height proportional, max-normalized.
- escaped bars: all arms, null -> 0-height + not-recorded title, control label.
- model mix: tokens grouped by model, no-usage models excluded, widths sum sane.
- scope change updates charts; empty scope -> empty state; max=0 no NaN.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch dsh-5. Do NOT merge; the human merges.
