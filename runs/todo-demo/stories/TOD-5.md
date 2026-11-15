# TOD-5 — Filter view

## Acceptance criteria
1. Three filters: All / Active / Completed.
2. The visible list respects the filter; the count reflects the FILTERED set.
3. Filter selection persists across reload.
4. Switching filters never mutates task data.
5. When the stored filter value is invalid or unreadable, the app falls back to
   All instead of crashing or showing an empty list.

## Manifest (files you may touch)
- src/store.ts
- src/store.test.ts
- src/App.tsx
- src/App.test.tsx
- src/index.css

## Design slice
- Filter state via `loadFilter`/`saveFilter` in the store seam.
- Filtering is a pure function (testable) over tasks + filter.
- The count now reflects the filtered set (changes TOD-2's total count).
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- store: filter helper returns correct subsets; persist round-trip.
- component: each filter shows the right tasks; count matches filtered set;
  selection survives reload; switching filters leaves data unchanged.
- failure: invalid stored filter -> falls back to All.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch `tod-5`. Do NOT merge; the human merges.