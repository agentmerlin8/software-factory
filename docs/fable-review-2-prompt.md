# Fable 5.2 — second adversarial review prompt (2026-11-14)

Consult input, versioned with the design it reviews. Target: Fable 5.2
(meta-advisor; fresh window, no workspace context). Design state at time
of dispatch: commit d56f8a3 (vision fully grilled, rounds 1–4 + issue #1
dispositioned). Paste the prompt below; if Fable lacks repo access, paste
the docs listed in it.

---

You are doing an adversarial red-team review of a software design. This is your second pass on this project. Your first review (filed as issue #1 in the repo) found real feasibility, security, and human-attention problems; all were dispositioned and fixed. Your job now is to find what those fixes missed, what the new architecture introduces, and what four rounds of internal review structurally could not see. Be hostile to the design's assumptions. Do not be reassuring.

THE PROJECT
A CLI-driven "software factory" that takes a plain description of software, guides the user through clarifying questions with live Storybook wireframes, produces a PRD and design docs, decomposes into features and stories, and runs each story through plan → fresh-context review → code → fresh-context cross-model review → test → merged PR → CI/CD to a deployable artifact. Trunk-based delivery. GitHub-native control plane. All factory state lives in a dedicated state repo structured as an Obsidian vault, separate from product repos, scoped to a person/team/org and mineable. Autonomy and merge/review policy are configurable. Target audience: engineering professionals who want to build software autonomously. First demo: a to-do app built from a description, not pre-specced. No code exists yet — this is a design review.

CURRENT STATE
Repo: agentmerlin8/software-factory (private), commit d56f8a3. Read in this order:
1. README.md
2. docs/vision.md — the design, 13 sections
3. docs/open-calls.md — OC-1…OC-11, all ratified by the owner (settled decisions)
4. docs/design-review-disposition-2026-11-14.md — how your issue #1 findings were dispositioned
5. docs/grill-round3-2026-11-14.md and docs/grill-round4-2026-11-14.md — the feasibility grill and its confirmation
6. docs/lineage.md
Also read issue #1 itself: your original findings and the disposition comment.

RULES OF ENGAGEMENT
- Ratified decisions OC-1…OC-11 are settled. Do not argue to reverse them. You MAY attack their consequences, their interactions, and anything they leave unexamined.
- Everything else is fair game: architecture, roadmap, process, economics, product thesis, and the review process itself.
- "Delete this" is a valid finding. You may recommend cutting scope, reordering phases, or not building part of the design.
- Cite file + section for every finding. If you assert GitHub/git platform behavior, verify it or mark it "verify" — do not invent platform mechanics.
- Read-only. Do not modify the repo.

ATTACK SURFACES (a floor, not a ceiling — go beyond it)
1. Did the fixes actually fix? Take your issue #1 findings and the round-3 blockers and check the current text. Real mechanisms, or paper? The newest machinery is the merge-integrity protocol (git merge-tree, review the merge result, post-merge tree check with auto-revert) and the per-story ledger — try to break them.
2. The state repo is new since your last review. Attack: cross-repo consistency and failure modes; the bootstrap recursion (the factory builds itself using itself, with its state in a repo it builds against); scope/permission escalation across person/team/org; one project's failure or a malicious input poisoning shared state; the mining path reading untrusted markdown back into an agent's context.
3. Security, deeper than last time: the ledger is now a single high-value target spanning projects; agents add dependencies (supply chain); the assumption log and inbox carry agent-generated text that humans and agents later read (injection); the App token's blast radius. What is the worst a compromised or misbehaving agent can do, and does the design actually contain it?
4. Economics and Goodhart: the process itself costs tokens (panels, grills, reviews of reviews). Does the cost model survive 20 stories? 200? Metrics drive model selection and autonomy promotion — where will they be gamed, by agents or by the process? Are the budget ceilings real controls or decoration?
5. Over-engineering: ~25 contracts must freeze in P1 before any execution exists, and the design has had four review rounds before a line of code. Nothing has been executed — every claim is untested. What is the minimum viable factory that still delivers the demo? What should be cut from v1? Is the roadmap the shortest path to a convincing demo, or the longest defensible one? What is the earliest real evidence that would de-risk the most, and does the plan get it soon enough?
6. Product thesis: why would an engineer adopt this over using Claude Code / Codex / SpecKit / Warp / Factory directly? What is the actual moat? The design claims runtime-agnostic, but the control plane is deeply GitHub-native (App tokens, Actions, Projects, CODEOWNERS) — is the portability claim real or aspirational?
7. The human: the primary operator is one person with limited, interruptible attention. What happens when they are gone for a week? Do the inbox, assumption log, and escalation classes hold the line — or does the factory quietly stall, or quietly proceed wrong?
8. Correlated blind spots: the design was authored by a Qwen-family model and reviewed four rounds by a DeepSeek-family model. You are a third family. What do you see that they structurally could not? What did the internal reviews reward (consistency, completeness) that hides risk?

OUTPUT
- Verdict: build as designed / build with cuts / redesign [scope] / do not build — with reasoning.
- The top 5 things most likely to kill this project, ranked.
- Findings: each with severity (blocker/major/minor), evidence (file + section), why it matters, and a recommended fix OR cut. Distinguish design flaws from specification gaps from strategic risks.
- A cut list: what you would remove from v1 and why.
- What you would need to see to be convinced the design is sound — the cheapest experiments or evidence.
- Prioritize; no padding. If a dimension is genuinely sound, say so in one line and move on.