message "Give the task a name — blank tasks don’t count." which is not required by ACs, but it's a nice touch.

Now, I need to decide verdict. Since I found a blocker (the subscriber notification), it's FAIL. But if we assume the scaffold already had notification in saveTasks, then it's not a blocker. However, we can't assume. Let's read the diff of store.test.ts: the test "notifies subscribers when a task is added, not when rejected" uses subscribe directly. It doesn't call saveTasks. It calls addTask. So it expects that addTask, not saveTasks, triggers the subscriber. So even if saveTasks notifies, that would fire. But wait: if saveTasks notifies, then addTask would trigger notification because it calls saveTasks. So the test would pass. So the missing notification might be in saveTasks. But we don't know if saveTasks notifies. The safest is to flag as a potential issue: I'll state that I cannot verify from the diff whether saveTasks triggers subscribers; if not, the test fails. But as a reviewer, I'd require confirmation. So I could give PASS-WITH-NITS with the condition that the subscriber notification is verified. But the instructions say "be adversarial: try to break the acceptance criteria." If I suspect it's broken, I should mark it as a finding and possibly FAIL. But I can decide to give a FAIL if I believe it's broken. Since I don't have the full store.ts, I can look at the store.ts diff context: it shows `@@ -58,4 +58,23 @@`. The previous file had 58 lines. The functions loadTasks, saveTasks, loadFilter, saveFilter, newId, and subscribe were likely defined. The saveTasks function may just be `localStorage.setItem(...)` without notification. The subscribe function probably is a simple pub/sub that isn't automatically called by saveTasks. The named exports from the original store: the test imports `subscribe`. So it's there. But the original test block "store persistence seam" didn't test subscriber notification. So it's plausible that saveTasks does not notify. Therefore, the test added in this PR will fail. I'll count that as a blocker.

But let's double-check: Could the `subscribe` function be implemented as a wrapper around `window.addEventListener('storage', handler)`? That would only fire for cross-tab changes, not same-tab. So it would not fire when addTask calls saveTasks locally. So that would not work. So that's unlikely. So the subscribe is likely a manual pub/sub. So addTask must call it.

Thus, it's a defect.

Now, to be adversarial, I'll also examine the test "reload restores the task". It uses `unmount()` and then `render(<App />)`. But what if the App component had some internal state that survived unmount? No. The test ensures localStorage is used. Good. However, the test does not verify that the task appears with the same data (id, etc). Not necessary.

Now, another adversarial thought: The `addTask` in store.ts uses `Date.now()` for id and createdAt. That could cause collisions if two tasks are added in the same millisecond, but the id includes random part, so extremely unlikely. Fine.

Now, the design doc says "TDD: write the story's named tests FIRST, verify they fail, then implement." The order of commits might show that, but we can't see. Not relevant.

Now, the verdict: I'll go with FAIL because of the missing subscriber notification causing test failure. But if I want to be precise, I could say PASS-WITH-NITS if I consider that fixable. However, a test that fails is a blocker, so FAIL.

But let's see if the test might pass anyway: maybe the `subscribe` function is implemented to intercept any call to `saveTasks` via a proxy? That's unlikely. So I'll stick with FAIL.

I'll list the findings with file:line.

Now, I need to print the complete review as final message.

Structure: Start with verdict. Then list findings with severity, description, evidence (file:line). Then summary.

Now, let's write.

Severity levels: blocker (must fix to meet ACs or DoD), major (defect that impacts functionality but could be fixed after merge?), minor (improvement), nit (style). Since the subscriber test is part of the PR and would prevent "full suite green", it's a blocker.

I'll include the finding about the possible double-submit as a major, because it could lead to data integrity issues (duplicate tasks) and there's no debounce. But maybe it's minor.

Also, check if the store's addTask correctly updates the store and returns the task. The component then adds to state. That works. But what about if multiple components use the store? Not an issue.

Now, also check: the store's addTask returns null for empty title, but the test "empty input is rejected" uses loadTasks() to confirm no tasks. That's good.

Now, write.

But wait, I recall the design slice says "React state via useState + the store's subscribe if needed". So subscribe is optional. The coder chose not to use subscribe in the component, but that's fine. The store's addTask should still notify subscribers for other potential consumers. So it's part of the store contract. But the story doesn't require a subscribe test. However, the coder added that test, so it must pass. So it's self-inflicted.

Now, I'll produce the review.

But the user asked to "Print the complete review as your final message." I'll output plain text.

I'll include a note that I cannot run the tests, but based on diff the test is likely to fail.

Let's also check the test file for App.test.tsx: it imports `loadTasks` from store. That's allowed. It uses `loadTasks()` in tests to verify store state. That's fine.

Now, I'll also note that the store test "notifies subscribers" uses `subscribe` which is imported. If the store doesn't export subscribe, that would be a build error. But we see subscribe in the import, so it must be exported.

Now, finalize.

But I want to mention the possibility that saveTasks already notifies. If that's the case, my blocker would be invalid. As a reviewer, I could request clarification. But since I'm to produce a review, I'll state it as a potential issue and ask for verification. I could downgrade to major if I'm uncertain. I'll phrase it: "If saveTasks does not trigger subscribers, then addTask lacks notification, causing the subscriber test to fail." I'll mark it as blocker because it's a failing test.

I'll also include a recommendation to either implement notification in addTask or remove the test if subscribe is not intended for this story.

Now, let's also check for any other test quality issues: The store test for addTask "appends a task and persists it" uses loadTasks() after two adds. That tests persistence indirectly because loadTasks reads from localStorage. It also checks the returned task equality. Good.

But note: The test "creates well-formed tasks" checks title trimmed, completed false, id, createdAt range. It uses `Date.now()` before and after. That could be flaky if the test runs slow? Not likely.

Now, review the CSS: The diff shows no bypass of localStorage. So fine.

Now, compile the review.

I'll write:

VERDICT: FAIL

Findings:

1. [Blocker] store.ts: addTask does not call subscribers (or saveTasks may not notify), causing the test `notifies subscribers when a task is added` in store.test.ts:95-108 to fail. This violates the requirement that the full test suite passes. Evidence: the implementation of `addTask` (store.ts:70-81) only calls `saveTasks` and returns; no call to `subscribe` or a notification function. The test expects subscribers to be invoked on successful add and not on rejection.

2. [Major] App.tsx: handleSubmit is vulnerable to double-submissions. A rapid double-click on the Add button or fast consecutive Enter presses can add the same task twice because the `title` state may not have been cleared before the second event. Evidence: no debounce, no disable state, and the state update `setTitle("")` is asynchronous. This could lead to duplicate tasks, which while not prohibited by ACs, is a behavioral defect.

3. [Minor] App.test.tsx: the test "Enter submits" (line 22-29) does not assert that the input is cleared after a successful submission. The implementation clears the input, but this lack of assertion could allow a future regression where the input retains text. Recommend adding `expect(input).toHaveValue("")` after the Enter.

4. [Nit] The CSS diff introduces extensive visual branding. While allowed, it adds significant line count unrelated to the functional criteria. This does not violate scope but could be deferred to a later story.

(Other notes: The implementation correctly meets all four ACs, aside from the subscriber issue. The tests are well-structured and properly use jsdom. The store seam is respected. No secrets or localStorage bypass.)

Now, I'll format nicely.

I need to print "the complete review" as final message. So I'll output exactly that.

Let's craft.

But I'm not fully satisfied with the blocker. Let's see if I can deduce what the original store.ts looked like. The diff index 7b8b39c..c24bab3. I could try to fetch the file at that commit? But I'm supposed to work with pinned inputs. The pinned diff is the only source. I can't access the repo. So I must rely on the context.

The store.test.ts before this diff had tests for loadTasks, saveTasks, loadFilter, saveFilter, newId. No subscribe test. So subscribe existed but wasn't tested. The store.ts might have been:

```
export function subscribe(cb) { ... }
export function loadTasks() { ... }
export function saveTasks(tasks) { localStorage.setItem('tasks', JSON.stringify(tasks)); }
```

So saveTasks does NOT call notify. So addTask does NOT notify. So the test will fail. So blocker is solid.

Thus verdict FAIL.

Now, write.VERDICT: FAIL

Findings:

1. [BLOCKER] store.ts — missing subscriber notification breaks the test suite
   File: src/store.ts, lines 70–81 (addTask function)
   The new test "notifies subscribers when a task is added, not when
   rejected" in src/store.test.ts (lines 95–108) expects that a registered
   subscriber callback fires when a task is successfully added, and does NOT
   fire when the title is rejected.  The implementation of addTask calls
   saveTasks() and returns the task, but never invokes any notification
   mechanism.  Unless saveTasks() already triggers subscribers (unlikely
   given the existing store structure), the subscriber test will fail,
   violating the DoD requirement that `npx vitest run` passes *all* tests.
   This must be fixed before merging.

2. [MAJOR] App.tsx — double‑submit hazard allows duplicate tasks
   File: src/App.tsx, handleSubmit (lines 48‑68)
   The form has no debounce, no disable state, and no guard against
   a second rapid submission before React processes setTitle("").  A
   quick double‑click on "Add" or two very fast Enter presses can add
   the same task twice.  While the ACs do not explicitly forbid
   duplicates, the behaviour is a data integrity problem in a local‑
   first app.

3. [MINOR] App.test.tsx — "Enter submits" test does not assert input clearing
   File: src/App.test.tsx, test "Enter submits" (line 22)
   The test verifies the task appears and the store is updated, but it
   never asserts that the input value becomes empty.  The code clears
   the input, so this is a gap that could allow a future regression.
   Recommend adding `expect(input).toHaveValue("")`.

4. [NIT] index.css — large theme addition exceeds the functional brief
   File: src/index.css (entire diff)
   The PR replaces the scaffold CSS with a full branded "paper‑ledger"
   theme (~340 lines of new styles).  The story manifest includes this
   file, so it is in scope, but the visual work is unrelated to the
   acceptance criteria and could have been deferred to a later story.

Positive notes:
- All four acceptance criteria are addressed; the component tests
  directly verify each one (Enter submission, whitespace rejection with
  focus retention, immediate list insertion, reload persistence via the
  store seam).
- Persistence stays inside src/store.ts; no direct localStorage
  access from the UI.
- No secrets, no forbidden APIs, proper accessible markup.

Remediation:
- Either implement subscriber notification inside addTask (or ensure
  saveTasks triggers subscribers) and the test will pass, or remove the
  subscriber test if it is not required for this story.  The double‑
  submit hazard should be mitigated (e.g., disable the button during
  async state update, or use a transient `submitting` flag).
- Add the missing assertion to the Enter‑submits test for input
  clearing.