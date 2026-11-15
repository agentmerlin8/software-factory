# TOD-4 — Delete a task

## Acceptance criteria
1. Each task has a delete control.
2. Deleting removes it from the list and the store.
3. Deletion persists across reload.
4. Deleting the last task returns to the empty state.
5. When persisting the deletion fails, the task is not silently lost from the
   store while vanishing from the UI (revert or show an accessible error).

(Undo is explicitly OUT of scope.)

## Manifest (files you may touch)
- src/store.ts
- src/store.test.ts
- src/App.tsx
- src/App.test.tsx
- src/index.css

## Design slice
- Delete removes by id via the store seam and persists.
- Empty state is the same one TOD-2 introduced.
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- store: delete removes the right task and persists; deleting absent id is a no-op.
- component: delete control removes the task; last delete shows empty state;
  deletion survives reload.
- failure: storage throws on delete -> no silent data loss.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch `tod-4`. Do NOT merge; the human merges.