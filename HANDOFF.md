# HANDOFF — Software Factory rewrite

**For a fresh session picking up remotely. Read this first, then the docs.**
Last updated: 2026-11-14 · repo HEAD `97d6ddd` · `main` == `origin/main`, clean.

## 0. Cold start (do this before anything else)

```bash
cd ~/Work/software-factory
git fetch -q origin && git status -sb        # expect: clean, main == origin/main
gh issue list --repo agentmerlin8/software-factory --state open
```

- Repo: `agentmerlin8/software-factory` (PRIVATE), local `~/Work/software-factory`.
- Old repo `agentmerlin8/ai-software-factory` is PRIVATE, kept as a read-only
  salvage source. Do NOT refactor it.
- Board: https://github.com/orgs/agentmerlin8/projects/5 (org project #5).
- This is a META/design session's product. The next work is BUILD (experiments
  + walking skeleton), not more design review.

## 1. What this project is

A CLI-driven "software factory": plain description → guided intake with live
Storybook wireframes → PRD + design docs → features → stories → plan / fresh-
context review / code / cross-family review / test → merged PR → CI/CD →
deployable artifact. Trunk-based. GitHub-native control plane. All state in a
dedicated state repo (Obsidian-vault shaped), separate from product repos.
Target audience: **engineering professionals** building software autonomously.
First demo: a to-do app built from a description, not pre-specced.

**The current strategy (Fable review 2, ratified): BUILD WITH CUTS.** Do not
freeze contracts before executing. Build a minimum factory (v1), run 5 real
to-do stories locally with a control arm, and test whether the factory beats a
coding agent directly. If it doesn't win on human-minutes or defects at an
acceptable cost multiple, STOP and reconsider (the kill criterion, OC-16).

## 2. Read order (the repo is the state)

1. `README.md` — overview + board guide.
2. `docs/vision.md` — the design, 13 sections. §11 is the walking-skeleton
   roadmap (v1 first); §5 is the full architecture (north star, marked).
3. `docs/open-calls.md` — **all 16 owner calls (OC-1…OC-16) RATIFIED.** This is
   the decision record. Do not re-litigate ratified calls.
4. `docs/design-review-2-disposition-2026-11-14.md` — Fable review 2 (issue #2),
   the "build with cuts" verdict, OC-12…16.
5. `docs/design-review-disposition-2026-11-14.md` — Fable review 1 (issue #1).
6. `docs/grill-round3-…`, `grill-round4-…`, `grill-record-…`,
   `grill-disposition-…`, `grill-regrill-round2-…` — the four grill rounds.
7. `docs/lineage.md` — what we salvage vs scrap from the old kit.
8. `docs/fable-review-2-prompt.md` — the prompt used for Fable review 2.

## 3. The 16 ratified decisions (summary — full text in open-calls.md)

- OC-1: keep old repo, private, read-only salvage.
- OC-2: cloud = GitHub Actions (north star; CUT from v1).
- OC-3: trunk-based, squash, one commit per story; feature-acceptance gate.
- OC-4: autonomy = gate policy, measured promotion (Level 3 CUT from v1).
- OC-5: dogfood after one story end-to-end (north star).
- OC-6: Storybook spike early (informs SKEL-2).
- OC-7: harness-agnostic intake, Hermes first.
- OC-8: state in a DEDICATED state repo (Obsidian vault), separate from product
  repos AND from ~/Notes; scoped person/team/org; mineable. (team/org + mining
  CUT from v1.)
- OC-9: merge/Copilot-review/remediation policy configurable (modes 2/3 + knobs
  CUT from v1; v1 = mode 1 human-merges-every-story).
- OC-10: escalation by deterministic decision class + assumption log (not
  confidence).
- OC-11: engineers are the audience; architecture approval gates first-class.
- OC-12: **walking skeleton replaces the P1 contract freeze.** Contracts v0;
  freeze after ~10 real stories; intake pulled forward.
- OC-13: **v1 cut list** (see §4).
- OC-14: **controller-writer security** — agents never hold a state-repo write
  token; a controller job (no model/product code) validates+appends; two
  identities (agent App / controller App); works on Free plan.
- OC-15: **merge = update-before-review + "require branches up to date"**; cut
  merge-tree protocol + auto-revert; post-merge compare is an alarm only.
- OC-16: **baseline + kill criterion** — control arm; stop if factory doesn't
  win; process-overhead-ratio metric; seeded-defect calibration moved to v1.

## 4. v1 scope (OC-13 cuts) — what NOT to build yet

CUT from v1: cloud adapter; merge modes 2/3 + Level 3; claim leases; team/org
scope; state-vault mining; multi-repo stories; flag registry; board custom
fields (use labels); LIVE/SCREENSHOT wireframe tiers (use a local Storybook
URL); Copilot-review/remediation knobs; PRD-versioning gate / reduced-assurance
/ regression suite (add on first real case); 4 design approvals (use 1);
Obsidian renders beyond one status file. Full vision = north star, post-v1.

## 5. Current work items (the board)

| Issue | Item | Status | Stage | Next |
|---|---|---|---|---|
| #3 | SKEL-1 walking skeleton + control arm | In Progress | Planning | the first build |
| #4 | SKEL-2 intake spike | Backlog | Planning | highest product risk |
| #5 | SKEL-3 controller-writer security | Backlog | Planning | |
| #6 | SKEL-4 merge protocol | Backlog | Planning | verify via EXP-1 first |
| #7 | SKEL-5 measurement + seeded-defect | Backlog | Planning | |
| #8 | EXP-1 squash equivalence on a real PR | Backlog | Planning | cheap, de-risks SKEL-4 |
| #9 | EXP-2 throwaway-repo plan check | Backlog | Planning | settles "verify" items |
| #1, #2 | Fable reviews 1 & 2 | Done | Done | dispositioned |

**Recommended next action:** run EXP-1 and EXP-2 (cheap verification
experiments), then build SKEL-1. EXP-2 is important: the org is on the **Free
plan** — private-repo branch protection/rulesets return 403 (verified). The
controller-writer model (OC-14) is designed to NOT depend on branch protection.

## 6. Board mechanics (IDs for scripting)

- Project node id: `PVT_kwDOFE6csM4Brohy` (org project #5).
- Status field `PVTSSF_lADOFE6csM4Brohyzhp6VnA`: Backlog `4d1655fd`,
  In Progress `f5520423`, Done `410c13ad`.
- Stage field `PVTSSF_lADOFE6csM4Brohyzhp6V2g`: Planning `2376bfca`,
  Coding `2dae1f9f`, Reviewing `302d7aae`, Testing `5205f969`, Merging
  `8fb99c10`, Blocked `0ee7a97b`, Done `ebf1d14d`.
- Work Type field `PVTSSF_lADOFE6csM4Brohyzhp6WD8`: Feature `ed990710`,
  Story `b7adc3d9`, Experiment `95a2e295`, Review `aa34d067`, Bug `b6e8794a`.
- Auto-add workflow `.github/workflows/auto-add-to-board.yml` is LIVE and
  verified (open→Backlog, close→Done). Needs `BOARD_PAT` secret (set; classic
  PAT, `project`+`repo` scopes). GITHUB_TOKEN cannot access Projects v2.
- **GraphQL gotcha:** inline object literals; build mutations with `printf -v`
  (escaped multiline quotes break in the Actions shell — this bug was fixed).
  Load the `github-projects-v2` skill before board scripting.
- Group-by columns are UI-only (one-time human click): Board view → Group →
  Status; Pipeline view → Group → Stage. May already be done.
- When moving an item through the pipeline, set its Stage field (and the
  `stage:*` label) so the board reflects reality. The ledger is truth; the
  board is a render.

## 7. Standing conventions (IMPORTANT)

- **Labeling rule (Randy):** NEVER 1–2 letter IDs for questions/answers/
  decisions/findings/notes. Use 3+ letter acronyms or short words (OC-, MRG-,
  SEC-, ECN-, HUM-, OVR-, PRD-, SKEL-, EXP-). Skill:
  `randy-labeling-convention`. Re-label external short IDs on intake.
- **Memory cap:** user/memory stores have char limits (raised to 2000/3000).
  Procedures → skills; project state → repo; only small always-relevant facts
  → memory. Don't loop on memory-save failures.
- **Process lessons (Fable review 2, accepted):** EXECUTE load-bearing claims
  in reviews (don't just check text presence — a 20-line script refuted a
  claim two review rounds passed); require a cut list each round (100%
  acceptance is a warning); prefer the platform's own guarantee over clever
  mechanisms; threat-model the whole token→repo map.
- Randy has ADHD tendencies: batch questions, drive threads to done, don't
  make him repeat himself. Replies in English. Persona: wizened old mage,
  warm/measured/plain-spoken.
- Factory runs start in FRESH chats; repo is the state. This handoff is the
  bridge.

## 8. Environment

- Host: Linux (Omarchy). gh authenticated as `agentmerlin8-ops` (scopes incl.
  project, repo, workflow, read:org). Org `agentmerlin8` = **Free plan**.
- Models: session on alibaba-token-plan (Qwen/DeepSeek/GLM pool). Cross-family
  review pairs available in-pool. Delegation pinning: see `subagent-model-
  pinning` skill (pin → spawn → restore, one step each; verify the model line).
- Relevant skills: agentic-software-factory, runtime-agnostic-factory,
  github-projects-v2, github-auth, subagent-model-pinning, spec-intake-grill,
  project-idea-intake, randy-labeling-convention, long-document-authoring.

## 9. Vault note

`~/Notes/Projects/Software Factory (rewrite) — Vision.md` mirrors the status.
Update it when milestones land. Vault commits: Agent Merlin
<agentmerlin8@gmail.com>.