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

CSS scope (OC-17): reuse existing classes. Filter controls may need ONE
minimal rule set (target ≤15 CSS lines, contrast-safe in both themes,
themed opaque :focus-visible ring on any focusable control). No restyling,
no theme variants.

## Design slice
- Filter state via `loadFilter`/`saveFilter` in the store seam.
- CARRY-FORWARD (TOD-2 review N3, deferred): `loadFilter` currently has no
  try/catch — a throwing `localStorage.getItem` crashes. Wrap it as part of
  AC5; add a named test that forces getItem to throw.
- Filtering is a pure function (testable) over tasks + filter.
- The count now reflects the filtered set (changes TOD-2's total count).
- TDD: tests first, verify red, implement green.

## Contracts from TOD-3/TOD-4 (the review loop will check each)
- Any NEW mutation path uses `readTasksStrict` (propagate storage ACCESS
  errors), re-reads + merges by id at the write boundary, and returns the
  COMMITTED snapshot for rendering — no post-write readback. (Filter
  switching itself must NOT write task data — AC4.)
- Every successful mutation is announced in the polite live region with
  text that differs per operation; filter switches announce the new view
  and its count. Failures use the shared assertive alert.
- Every flag gating the conditional assertive alert (`rejected`,
  `storageFailed`) must be cleared on EVERY mutation/filter success path —
  the deterministic gate now enforces this (stale-alert-flag class).
- Deleting/toggling while a filter is active must keep the view consistent
  with the committed snapshot; focus management follows TOD-4's pattern
  (surviving control, input fallback when the lookup misses).

## Named tests (must exist and pass)
- store: filter helper returns correct subsets; persist round-trip.
- component: each filter shows the right tasks; count matches filtered set;
  selection survives reload; switching filters leaves data unchanged.
- failure: invalid stored filter -> falls back to All.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch `tod-5`. Do NOT merge; the human merges.