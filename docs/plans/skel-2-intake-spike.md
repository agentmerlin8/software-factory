# SKEL-2 plan — Intake spike (issue #4)

**Status:** draft for owner review · **Date:** 2026-11-15
**Thesis under test (hypothesis 2):** guided intake produces a PRD an
engineer who is NOT the owner approves, in tolerable time.

## What gets built (v1 minimum, OC-13 cuts applied)

1. **`factory intake` CLI** — harness-agnostic intake state (OC-7):
   - `intake start --description "<plain text>"` → creates a session record
     (JSON in `runs/<project>/intake/`), status `questioning`.
   - `intake answer --session <id> --answers <json>` → records answers,
     advances status. The CLI owns STATE; any chat harness drives the
     conversation (first implementation: Hermes chat).
   - `intake generate --session <id>` → deterministically assembles the
     ONE design doc (PRD) from the validated conversation. Template-driven,
     no model in the CLI itself (the agent drafts sections; the CLI pins
     and validates them).
   - `intake status` → where the session sits.
2. **Guided question flow** — an intake-agent role package (dispatch
   package, same machinery as SKEL-1): platform, stack, features,
   look-and-feel. Bounded: ≤2 rounds, ≤12 questions, every question
   carries options + a recommendation (the grill discipline). The agent
   asks; the human answers; the CLI records.
3. **Storybook wireframes** — a minimal Vite+React+Storybook workspace
   generated from the validated feature list. Local URL only (OC-13: no
   LIVE/SCREENSHOT tiers). Wireframes are clickable mock-data stories,
   one per screen, built BEFORE the PRD is finalized (the Storybook-first
   rule). The engineer clicks through the URL during approval.
4. **One approval** — the engineer reviews the Storybook URL + the single
   PRD and approves or requests changes. Approval + elapsed time recorded
   as ledger events (`intake_approved`, `human_min`).

## Acceptance (from issue #4)

- [ ] intake produces a PRD from a plain to-do-app description
- [ ] local Storybook wireframes viewable via URL
- [ ] tested with ≥1 non-owner engineer; approval + time recorded

## Slices (OC-17 sizing — each independently mergeable)

- **INT-1: intake state machine + CLI** (~250 lines product + tests).
  start/answer/generate/status, session JSON schema, fail-closed on
  missing answers. No model, no Storybook. Pure state + deterministic
  PRD assembly from a validated answer set.
- **INT-2: intake-agent role package + question flow** (~150 lines +
  prompt). The dispatch package that drives the conversation in Hermes
  chat; bounded rounds; records answers via the CLI. Dogfood on the
  to-do description.
- **INT-3: Storybook wireframe workspace** (~200 lines + stories).
  Scaffold generator from the feature list; one story per screen with
  mock data; `npm run storybook` serves the local URL. Contrast/focus
  gates apply (reuse SKEL-1's a11y gate).
- **INT-4: the engineer test** (experiment, not code). Run the full
  intake with ≥1 non-owner engineer on a plain to-do description; record
  approval + time + questions asked + rework rounds. Write the result to
  `docs/experiments/skel-2-intake-<date>.md`.

## The engineer-test decision (Randy, 2026-11-15)

**DECIDED: fresh-context agent engineer persona** as the PRD reviewer —
weaker evidence than a human (same-model-family blind spots possible),
but unblocks the spike now. The persona gets ONLY the PRD + Storybook
URL + the original plain description (never the intake conversation —
context isolation), reviews as an independent engineer, and returns
approve / request-changes with reasons. Approval + time recorded.
**Caveat recorded in the experiment writeup:** this measures the
artifact's clarity to a fresh reader, NOT human acceptance; a real
non-owner engineer test remains the stronger follow-up when available.

## What this spike does NOT build (OC-13 cuts)

- No cloud adapter, no web-chat product surface (Hermes chat first, OC-7).
- No LIVE/SCREENSHOT wireframe tiers — local Storybook URL only.
- No four-doc approval — ONE design doc, ONE approval.
- No auto-feature-creation on the board (that's P4) — the spike records
  the PRD; board integration comes later.

## Measurement

Per the OC-16 discipline: tokens (intake-agent dispatch), wall-time,
**human-minutes (instrumented this time — the gap SKEL-1 exposed)**,
questions asked, rework rounds, approval verdict. The engineer's approval
time is the headline number.
