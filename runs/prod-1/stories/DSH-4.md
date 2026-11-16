# DSH-4 — Per-story table

## Acceptance criteria
1. One row per story in the selected scope: story id, arm/run, coder tokens,
   non-coder tokens, overhead ratio, wall time, human-min, escaped defects,
   review rounds, model(s). Data from DSH-2's harvestStories (reuse, no
   reimplementation). Matches the approved wireframe (StoryTable): warm-paper
   theme, light + dark, contrast AA, semantic <table> with <th scope>.
2. Sortable by rounds, escaped defects, and wall time (three sort columns;
   other columns static in v1, per the approved PRD). Clicking a sort header
   toggles ascending/descending; the active sort is indicated (aria-sort);
   sortable headers are real buttons with :focus-visible rings.
3. Nulls render 'not recorded', never 0 (fmt helper). A recorded zero renders
   0. Cost is NOT a table column (cost is a headline card only).
4. The table reacts to scope changes (rows = stories in scope). Empty scope
   shows a friendly empty state, not a blank table.
5. Per-story escaped defects: attribute findings to the story's repo+pr
   (the findings join), null when findings source failed.
6. Sorting is a pure function over StoryMetrics[], unit-tested; the component
   renders from it (no inline sort logic in the JSX).

## Manifest (files you may touch)
- src/components/StoryTable.tsx, src/components/StoryTable.test.tsx
- src/App.tsx, src/App.test.tsx, src/index.css
- src/data/metrics.ts (only if a per-story escaped-defect join helper is needed)
- src/data/types.ts (only if a view-model field is needed)

## Design slice
- Reuse DSH-2 harvestStories + the escaped-defect formula; the per-story
  escaped count joins findings on repo+pr (storyRounds already does this join
  for rounds — follow the same pattern).
- The wireframe StoryTable is the visual reference; match structure/classes.
- Sorting is pure (a sort function over StoryMetrics[]), unit-tested.
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- rows render per story in scope; nulls -> 'not recorded', recorded 0 -> 0.
- sort by rounds/escaped/wall toggles asc/desc; aria-sort set on active column.
- scope change updates rows; empty scope -> empty state.
- per-story escaped defects join on repo+pr; findings null -> 'not recorded'.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch dsh-4. Do NOT merge; the human merges.
