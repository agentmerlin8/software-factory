# TOD-2 — List tasks

## Acceptance criteria
1. Tasks render newest-first (by createdAt descending).
2. Empty state shows a friendly message (not a blank page).
3. A live count shows total tasks.
4. The list survives reload (reads the same store TOD-1 writes).
5. When stored data is corrupt or unreadable, the app renders the empty state
   instead of crashing.

## Manifest (files you may touch)
- src/store.ts
- src/store.test.ts
- src/App.tsx
- src/App.test.tsx
- src/index.css

## Design slice
- Read tasks via the store seam (`loadTasks`), never localStorage directly.
- Newest-first ordering is a pure function in store.ts (testable).
- The count reflects ALL tasks (filtering is TOD-5, not here).
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- store: ordering helper returns newest-first; stable for equal timestamps.
- component: renders tasks newest-first; empty-state message when none;
  count matches task total; reload restores the list.
- failure: corrupt stored JSON -> empty state, no crash.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch `tod-2`. Do NOT merge; the human merges.