# To-Do Demo — Design Document (SKEL-1)

**Status:** awaiting owner approval (the ONE design approval, OC-13)
**Run:** todo-demo · **Issue:** #3 · **Date:** 2026-11-14

## 1. Product

A browser to-do app. Local-first: all state in `localStorage`, no backend,
no accounts. One page. The point is NOT the app — it's the five real stories
the factory must carry from description to merged PR.

## 2. The five stories (vertical slices, ≤6 ACs each)

### TOD-1 — Add a task
- Input field + Add button; Enter also submits.
- Empty/whitespace input is rejected (no task created, input keeps focus).
- New task appears in the list immediately.
- Task persists across page reload.
- AC count: 4.

### TOD-2 — List tasks
- Tasks render newest-first.
- Empty state shows a friendly message (not a blank page).
- A live count shows total tasks.
- List survives reload (reads the same store TOD-1 writes).
- AC count: 4.

### TOD-3 — Complete / uncomplete
- Each task has a toggle (checkbox).
- Completed tasks render visually distinct (strikethrough).
- Toggle state persists across reload.
- Toggling twice returns to the original state.
- AC count: 4.

### TOD-4 — Delete a task
- Each task has a delete control.
- Deleting removes it from the list and the store.
- Deletion persists across reload.
- Deleting the last task returns to the empty state.
- AC count: 4. (Undo is explicitly OUT of scope.)

### TOD-5 — Filter view
- Three filters: All / Active / Completed.
- The visible list respects the filter; the count reflects the FILTERED set.
- Filter selection persists across reload.
- Switching filters never mutates task data.
- AC count: 4.

**Dependency order:** TOD-1 → TOD-2 → TOD-3 → TOD-4 → TOD-5 (each builds on
the store the previous ones establish). Expand-first: every story is
independently mergeable; main stays deployable after each.

## 3. Architecture

- **Stack:** Vite + React + TypeScript. Node 26.
- **Persistence:** one module `src/store.ts` — the ONLY place that touches
  `localStorage`. Pure functions + a thin subscription hook. Every story
  extends this module; no story reads/writes localStorage directly.
- **State:** React `useState`/`useSyncExternalStore` over the store. No
  router, no state library, no CSS framework (plain CSS).
- **Tests:** Vitest + Testing Library (jsdom). Unit tests for `store.ts`;
  component tests per story; the store is the seam every story's tests hit.
- **CI:** GitHub Actions — `npm run build` + `npx vitest run` on every PR;
  registered as the REQUIRED status check `ci` (EXP-3: empty checks = no-op).
- **Branch protection:** strict up-to-date + required `ci` check (public
  repo, Free plan — verified working in EXP-3).

## 4. Test strategy

- TDD per story: the story's named tests are written FIRST, verified red,
  then implemented green (the coder's dispatch contract enforces this).
- Store unit tests: add/list/toggle/delete/filter + persistence round-trip.
- Component tests: one per AC that is observable in the DOM.
- No E2E browser suite in v1 (cut); jsdom component tests are the ceiling.

## 5. Definition of done (per story)

1. Story's named tests green; full suite green; build green.
2. Deterministic gate passes (build, tests, manifest, secret scan).
3. Cross-family fresh-context review verdict PASS (or PASS-WITH-NITS fixed).
4. One squash commit on main; human merge (mode 1).
5. Ledger events + usage + evidence recorded.

## 6. What this run measures (OC-16)

Per story: tokens, wall-time, human-minutes, escaped defects, cost.
Headline: process-overhead-ratio (non-coder tokens / coder tokens).
Control arm: same 5 stories, one coding-agent session, same model + doc.
Kill criterion: factory must win on human-minutes OR defects at a cost
multiple the owner accepts — else STOP.

## 7. Approval

🧑 **Owner approval required before Phase 1.** Reply "approved" (or with
changes). Approval is recorded as a `design_approved` ledger event.