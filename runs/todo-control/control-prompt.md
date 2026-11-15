You are a CODING AGENT building a small to-do app. Implement ALL FIVE stories below (TOD-1 through TOD-5) in this repository, in dependency order, on branch main. The scaffold (Vite + React + TypeScript + Vitest, store seam in src/store.ts) already exists — extend it.

Rules:
- Follow the design document and each story's acceptance criteria exactly.
- Write tests for the behavior you build (Vitest + Testing Library, jsdom); run them.
- Definition of done: `npm run build` green and `npx vitest run` green (full suite).
- Commit your work with clear messages (one commit per story is fine). Do NOT push.
- Work only in this repository. If something is ambiguous, make a reasonable choice and note it in the commit message.

When all five stories are implemented and the suite is green, print a final summary listing: what you built per story, the test count, and any decisions you made.

=== DESIGN DOCUMENT ===
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

=== STORIES ===
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

# TOD-2 — List tasks

## Acceptance criteria
1. Tasks render newest-first (by createdAt descending).
2. Empty state shows a friendly message (not a blank page).
3. A live count shows total tasks.
4. The list survives reload (reads the same store TOD-1 writes).
5. When stored data is corrupt or unreadable, the app renders the empty state
   instead of crashing. This includes MALFORMED ARRAY ELEMENTS (e.g. `[null]`,
   `[{}]`, wrong field types), not just unparseable JSON — validate every entry
   at the storage boundary.

## Manifest (files you may touch)
- src/store.ts
- src/store.test.ts
- src/App.tsx
- src/App.test.tsx

Note: `src/index.css` is intentionally EXCLUDED (OC-17 sizing, 2026-11-15).
The theme already exists; reuse its classes. Do NOT restyle, add theme
variants, or write new CSS — unrequested visual work is out of scope.

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

# TOD-3 — Complete / uncomplete

## Acceptance criteria
1. Each task has a toggle (checkbox).
2. Completed tasks render visually distinct (strikethrough).
3. Toggle state persists across reload.
4. Toggling twice returns to the original state.
5. When persisting the toggle fails, the UI does not silently show a state that
   was not saved (revert or show an accessible error).

## Manifest (files you may touch)
- src/store.ts
- src/store.test.ts
- src/App.tsx
- src/App.test.tsx
- src/index.css

CSS scope (OC-17): the theme has NO completed-task rule yet, so AC2 requires
one. Add ONLY the minimal completed-state rule (strikethrough + any contrast-
safe muted color for completed titles). No restyling, no theme variants, no
other selectors. Target ≤15 CSS lines; the visual budget is 120.

## Design slice
- Toggle mutates `completed` via the store seam and persists.
- Strikethrough is plain CSS on a completed class/attribute.
- TDD: tests first, verify red, implement green.

## Named tests (must exist and pass)
- store: toggle flips completed and persists; double-toggle restores.
- component: checkbox toggles; completed task has strikethrough styling;
  state survives reload.
- failure: storage throws on toggle -> no silent unsaved state.

## Definition of done
- `npm run build` green; `npx vitest run` green (full suite).
- One commit on branch `tod-3`. Do NOT merge; the human merges.

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