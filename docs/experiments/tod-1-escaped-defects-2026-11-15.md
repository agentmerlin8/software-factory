# SKEL-1 / TOD-1 — Escaped-defect analysis: what Copilot caught that we didn't

**Date:** 2026-11-15 · **PR:** factory-todo-demo#1 · **Trigger:** Randy ran
Copilot review + "fix with Copilot" on our first factory story.
**Verdict:** Copilot found **4 real defects** our gate AND our cross-family
reviewer both passed. All four verified by controller execution, not trust.

## 1. The four findings (verified)

| ID | Sev | What | Verified how |
|---|---|---|---|
| storage-failure-aborts-submit | major | `localStorage.setItem` throws (quota/blocked) → uncaught → submission aborts, no feedback, draft lost | fault-injection test (mock `setItem` to throw) — now passes at `0ceb1d2` |
| contrast-light-secondary | major | `--ink-faint #a2957f` = **2.61–2.92:1** on light surfaces; placeholder/hint/count/footer | WCAG math: 4 selectors fail 4.5:1 |
| contrast-dark-secondary | major | `--ink-faint #7d715c` = **3.27–3.82:1** on dark surfaces | WCAG math: 4 selectors fail |
| contrast-light-eyebrow | major | `--persimmon #d94f04` = **3.68:1** at 0.72rem | WCAG math |

**9 concrete contrast failures** at head `04428d6` — the exact head our
deterministic gate passed and our reviewer dispositioned. After the fix:
**0 failures**. Probe: `verify-contrast2.py` (resolves `var()` aliases,
computes real ratios per theme per surface).

Copilot's fix is correct and complete: aliases `--ink-faint: var(--ink-soft)`,
switches eyebrow to `--persimmon-deep`, wraps submit in try/catch with an
accessible `role="alert"` + draft retention, and adds a real fault-injection
test. Suite 18/18 green, build green, CI green.

## 2. Root causes — five distinct process failures

### RC-1: We DEFERRED the scope that contained 3 of 4 defects
Our reviewer flagged the ~340-line unrequested "paper-ledger" theme as a
**nit** ("exceeds the functional brief"). The controller dispositioned it
**DEFERRED — cosmetic, no AC impact**. That was the single worst call in the
run: the "cosmetic" CSS held three real accessibility defects.
**"Cosmetic" is not a severity — it is an unreviewed scope.**

### RC-2: Contrast is COMPUTED, and we asked an LLM to eyeball it
Contrast ratio is deterministic arithmetic over hex values. No model should
judge it by reading CSS. Our gate checked build/tests/manifest/secrets —
nothing computable about the UI. **A deterministic property checked by a
probabilistic reviewer is a gate gap, not a reviewer failure.**

### RC-3: No AC covered failure paths, so nothing tested them
TOD-1's four ACs are all happy-path. The store seam does I/O that can throw.
Neither the story, the test plan, nor the DoD mentioned failure. The coder
built exactly what was asked; the defect was in the *specification*.

### RC-4: The reviewer dispatch ANCHORED the adversarial lens
The dispatch said: *"behavioral correctness (edge cases: empty input,
whitespace, reload persistence)"*. Enumerating three edge cases told the
reviewer those were the edge cases. It checked exactly those three and
stopped. **We handed a checklist to an adversary and got a checklist back.**

### RC-5: Diff-only + no tools made the reviewer guess
The reviewer got the diff but not the unchanged base files, and ran with
`--toolsets ""` (no ability to execute). Consequences, both directions:
- **2 FALSE findings** (subscriber "blocker", double-submit "major") — it
  couldn't see `saveTasks` already calls `emit()`, so it speculated. Both
  refuted by controller execution.
- **4 MISSED findings** — it couldn't run anything, so it never computed a
  contrast ratio or injected a storage fault.

**Fresh context means blind to the author's REASONING, not blind to the CODE.**
We conflated isolation with powerlessness.

## 3. Preventions (concrete, ordered by leverage)

### PRE-1 — Deterministic a11y gate (implemented)
`factory/gates.py: check_contrast()` — parses CSS custom properties per
theme, resolves `var()` chains, computes WCAG ratios for normal-size text
against actual surfaces, fails under 4.5:1. Runs in `pre_review` BEFORE any
LLM. Verified: 9 failures at the old head, 0 at the fixed head.
**Class prevented: every computable UI property (contrast today; extend to
focus-visible, alt text, label association, heading order).**

### PRE-2 — Reviewer package: full files + tools + open lens
- Pin the **full post-change files**, not just the diff (kills RC-5 false
  positives).
- Give reviewers **read + run tools** so they can execute their own
  hypotheses (kills speculation in both directions).
- Replace enumerated edge cases with **lenses**: "try to break this —
  failure modes, resource limits, hostile input, a11y, concurrency". Never
  hand an adversary a finite list.

### PRE-3 — Failure-path AC requirement (intake/planning rule)
Any story touching I/O, persistence, network, or parsing MUST carry at least
one failure-mode AC ("when X fails, the user sees Y and loses no data").
Enforced at planning, checked by the gate as a named-test requirement.

### PRE-4 — Unrequested-scope rule (kills the DEFERRED-cosmetic escape)
Work not traceable to an AC is either **cut** or **gets its own ACs**.
"Cosmetic/deferred" is not a valid disposition for unreviewed scope. The
manifest is a *permission* list, not a *scope contract* — passing the
manifest gate says nothing about whether the work was asked for.

### PRE-5 — Reviewer findings must be executed before disposition
Already learned in EXP/Fable review 2 and applied to the two false findings —
now extend it to **accepting** findings too: a reviewer's PASS on a
computable property is not evidence. The gate must compute it.

## 4. What this means for the experiment (OC-16)

Recorded as **4 escaped defects, TOD-1, caught_by=copilot-pr-review,
escaped_gate=true, escaped_cross_family_review=true**. This is exactly the
measurement the kill criterion needs — and it is honest data against the
factory arm on story 1.

It also sharpens hypothesis #3: cross-family fresh-context review did NOT
catch what a platform bot caught. The differentiator was not model family —
it was **deterministic computation + full-file context + execution ability**.
That is a design fix, not a model-routing fix.

**Copilot review stays a non-gate signal** (OC-9 default): it is not
reproducible and cannot be a required check we control. The answer is to
make OUR gate catch these classes deterministically, not to depend on a bot.

## 5. Also found: bot-authored commits can strand the merge gate

Copilot's fix commit left CI at `action_required` with **0 jobs** — GitHub
held the run, so the required `ci` check never reported and the PR sat
BLOCKED. A manual rerun cleared it. **SKEL-4 must detect a required check
that never started (not just one that failed) and re-trigger or escalate**,
or a bot/human edit can silently wedge the pipeline.