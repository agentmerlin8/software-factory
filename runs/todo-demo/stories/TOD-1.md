# TOD-1 — Add a task

## Acceptance criteria
1. Input field + Add button; pressing Enter also submits.
2. Empty/whitespace-only input is rejected: no task created, input keeps focus.
3. A new task appears in the list immediately after adding.
4. The task persists across page reload (localStorage via the store seam).
5. When storage fails (quota exceeded or blocked), the user sees an accessible
   error, the draft is retained, and no partial task is added.
6. Malformed stored entries (`[null]`, partial objects, wrong field types) are
   dropped at the storage boundary and never crash the render.

## Visual acceptance (any styled control)
- Text on every control meets WCAG AA 4.5:1 in BOTH themes and in ALL states
  (normal, hover, active) across every gradient stop. Compute it; do not eyeball.

## Manifest (files you may touch)
- src/store.ts
- src/store.test.ts
- src/App.tsx
- src/App.test.tsx
- src/index.css

## Design slice
- All persistence goes through `src/store.ts` — the ONLY module touching
  localStorage. Extend it; do not bypass it.
- Task shape: `{ id, title, completed, createdAt }` (already in store.ts).
- Use `newId()` for ids, `saveTasks`/`loadTasks` for persistence.
- React state via `useState` + the store's `subscribe` if needed; no router,
  no state library, plain CSS.
- TDD: write the story's named tests FIRST, verify they fail, then implement.

## Named tests (must exist and pass)
- store: `addTask` appends and persists; empty title rejected at the UI layer.
- component: typing + Add creates a visible task; Enter submits; whitespace
  rejected; reload restores the task (simulate via store round-trip).
- failure: mock storage setItem to throw -> accessible alert, draft kept, no task.

## Definition of done
- `npm run build` green; `npx vitest run` green (all tests, not just yours).
- One commit on branch `tod-1`. Do NOT merge; the human merges.