# TOD-3 — Complete / uncomplete

## Acceptance criteria
1. Each task has a toggle (checkbox).
2. Completed tasks render visually distinct (strikethrough).
3. Toggle state persists across reload.
4. Toggling twice returns to the original state.

## Manifest (files you may touch)
- src/store.ts
- src/store.test.ts
- src/App.tsx
- src/App.test.tsx
- src/index.css

## Design slice
- Toggle mutates `completed` via the store seam and persists.
- Strikethrough is plain CSS on a completed class/attribute.
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- store: toggle flips completed and persists; double-toggle restores.
- component: checkbox toggles; completed task has strikethrough styling;
  state survives reload.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch `tod-3`. Do NOT merge; the human merges.