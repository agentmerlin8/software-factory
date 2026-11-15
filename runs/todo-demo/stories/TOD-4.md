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

CSS scope (OC-17): reuse existing classes. Add a delete-control rule ONLY if
genuinely needed (target ≤15 CSS lines, contrast-safe, themed focus ring if
the control is focusable). No restyling, no theme variants.

## Design slice
- Delete removes by id via the store seam and persists.
- Empty state is the same one TOD-2 introduced.
- TDD: tests first, verify red, implement green.

## Contracts from TOD-3 (do not relearn these — the review loop will check)
- Mutation reads use `readTasksStrict` (propagate storage ACCESS errors);
  `loadTasks` stays tolerant for rendering only.
- Re-read + merge by id at the write boundary (appendTasks discipline) —
  never overwrite from a stale snapshot; a concurrent tab's commit must
  survive. Return the COMMITTED snapshot from the mutation and render from
  it — no post-write readback (a fallible read after a successful save can
  wipe the visible list).
- Every successful mutation is announced in the existing polite live region
  with text that DIFFERS per operation (include a count if wording could
  repeat). Failures use the shared assertive alert; clear any pending
  blank-input `rejected` flag so it cannot mask the storage error.
- New focusable controls carry the theme's opaque `:focus-visible` ring.

## Named tests (must exist and pass)
- store: delete removes the right task and persists; deleting absent id is a no-op.
- component: delete control removes the task; last delete shows empty state;
  deletion survives reload.
- failure: storage throws on delete -> no silent data loss.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch `tod-4`. Do NOT merge; the human merges.