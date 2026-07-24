---
type: Finding
okf_spec: OKF-PLAN
---
# Finding: EXP-05 planning-framework survey

**Experiment:** Survey the current (2025–2026) landscape of planning / spec-driven /
"prompt-the-plan" frameworks for coding agents, steelman each, and articulate how
yf-plan differs. Feeds a new "Why yf-plan" web section.

**Method:** Live web research (Exa + WebSearch) against primary sources (repos, docs,
author posts). Popularity signals as of mid-2026; star counts are approximate and
change fast. yf-plan claims verified against `skills/yf-plan/SKILL.md` (read directly).

**Epistemic note:** Where I could not find an authoritative star count I say so rather
than invent one. "Widely adopted" vs "niche" is called out per framework.

---

## Frameworks surveyed

Each: what it is · source · popularity signal · 1–2 sentence steelman.

### Widely adopted / heavily discussed

**GitHub Spec Kit (Spec-Driven Development / SDD)**
- What: an open-source CLI (`specify`) + slash-command harness (`/speckit.specify` →
  `.plan` → `.tasks` → `.implement` → `.converge`, with optional `.clarify`,
  `.checklist`, `.analyze` quality gates) that makes a Markdown *specification* the
  executable center of the workflow. Each phase emits a Markdown artifact that feeds the
  next. Ships a resumable YAML *workflow* engine with human review gates and
  per-step state persistence.
- Source: https://github.com/github/spec-kit ·
  https://github.github.io/spec-kit/ · GitHub blog:
  https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
- Popularity: **very high** — ~110k–120k GitHub stars by mid-2026 (grew ~71k→111k
  Feb→Jun 2026), 35 agent integrations, 130+ community extensions. GitHub-backed.
- Steelman: Spec Kit institutionalizes "intent before code" — the spec is a living,
  version-controlled artifact that generates implementation rather than being discarded,
  and its phase checkpoints (clarify/checklist/analyze/converge) force human validation
  and cross-artifact consistency before the agent writes code. Agent-agnostic, so teams
  aren't locked to one CLI.

**Kiro (AWS)**
- What: a proprietary VS Code-fork IDE + headless CLI (built on Bedrock/Claude) whose
  core is spec-driven development: a prompt becomes three files — `requirements.md`
  (user stories + acceptance criteria), `design.md` (architecture + sequence diagrams),
  `tasks.md` (trackable tasks) — then the agent implements. Adds property-based testing,
  automated-reasoning contradiction/gap checks on requirements, agent Hooks (file-change
  triggers), Steering files, and a **task dependency-graph → concurrent "waves"** executor.
- Source: https://kiro.dev/ · https://kiro.dev/docs/specs/ ·
  https://github.com/kirodotdev/Kiro · InfoQ:
  https://www.infoq.com/news/2025/08/aws-kiro-spec-driven-agent/
- Popularity: **high** — AWS-operated, launched preview mid-2025, $20/mo pricing;
  enterprise positioning (IAM/SSO, indemnity).
- Steelman: Kiro pushes SDD past prose — automated reasoning catches spec contradictions
  *before* design, property-based tests catch edge cases unit tests miss, and specs stay
  synced with the evolving codebase. Enterprise-grade controls and a dependency-aware
  parallel executor make it the most "product" of the SDD tools.

**BMAD-METHOD (Breakthrough Method for Agile AI-Driven Development)**
- What: a multi-agent *agile team* framework. 12+ specialized agent personas (Analyst,
  PM, Architect, Scrum Master, Developer, QA…) drive a 4-phase SDLC (Analysis → Planning
  → Solutioning → Implementation). Docs (PRD, architecture, stories) are the source of
  truth; a Scrum Master sub-agent "shards" monolithic PRDs into atomic per-story files so
  the Dev agent loads only what a story needs. Scale-adaptive ("Quick Flow" vs "Enterprise
  Flow"). V6 adds a Skills architecture and sub-agents.
- Source: https://github.com/bmad-code-org/BMAD-METHOD · https://docs.bmad-method.org/
- Popularity: **high / heavily discussed** (tens of thousands of stars; exact count not
  verified here). Active module ecosystem (Builder, Test Architect, Game Dev, CIS).
- Steelman: BMAD is the most complete "org-as-agents" model — role separation with scoped
  context permissions prevents domain contamination (the Dev agent can't rewrite the
  Architect's schema), story-sharding fights context limits, and scale-adaptive planning
  depth means a bug fix isn't forced through enterprise ceremony. It solves "how to
  organize an AI team," not just "how to write a good prompt."

**Taskmaster / claude-task-master**
- What: an MCP-server + CLI task-management system that parses a **PRD** into a dependency-
  aware `tasks.json` graph, then drives a `next → show → implement → set-status` loop.
  Supports complexity analysis, task expansion, research mode (Perplexity), tags/
  workstreams for git-branch contexts, and an RPG (Repository Planning Graph) PRD template.
  Drops into Cursor, Windsurf, Roo, Claude Code, etc.
- Source: https://github.com/eyaltoledano/claude-task-master ·
  https://docs.task-master.dev/
- Popularity: **high** — ~28k GitHub stars; broad editor support.
- Steelman: Taskmaster externalizes the task graph into a durable, dependency-ordered
  `tasks.json` the agent consults every session — turning a PRD into topologically
  ordered, individually testable units with an explicit "what's next" so the agent never
  loses the thread across a long build.

**Aider architect mode**
- What: a two-model chat mode. An "architect" (reasoning) model describes the solution in
  natural language; an "editor" model translates that into precise file edits. Also `ask`/
  `code` modes for a lighter plan-then-act flow with one model.
- Source: https://aider.chat/docs/usage/modes.html ·
  https://aider.chat/2024/09/26/architect.html
- Popularity: **high** (Aider is a very popular OSS coding CLI). Architect mode set SOTA
  on Aider's edit benchmark (~85%).
- Steelman: Separating "code reasoning" from "code editing" lets each model do what it's
  best at, measurably improving edit accuracy — a clean, minimal division of labor that
  needs no project scaffolding.

**Cline / Roo Code — Plan & Act modes**
- What: a read-only *Plan* mode (explore, search, strategize, no file writes) that carries
  full conversation context into an *Act* mode that executes. Cline: two modes + a
  `/deep-planning` command; Roo (a Cline fork): Code/Ask/Architect/Debug/Orchestrator +
  custom modes with per-mode tool/file permissions. Separate models per mode supported.
- Source: https://docs.cline.bot/core-workflows/plan-and-act · https://cline.bot/ ·
  https://linuru.com/documents/cline-vs-roo-code-shortcuts/
- Popularity: **high** — two of the most popular VS Code AI agents.
- Steelman: The read-only planning posture is cheap insurance — think first with no risk
  of file mutation, then act with the plan as retained context; Roo's per-mode permissions
  give fine-grained control over what the agent may touch when.

**Ralph / Ralph Wiggum loop**
- What: "Ralph is a Bash loop" (Geoffrey Huntley). Restart the *same* agent with the *same*
  prompt repeatedly; each iteration gets a **fresh context**, reads durable state from disk
  (`tasks.json`, `LOG.md`, git history), does exactly **one** task, verifies it (tests),
  commits, exits. Stops on an explicit completion-promise tag or an iteration cap. Shipped
  as an official Anthropic Claude Code plugin (Stop-hook implementation) and as
  `ralph.sh` / `@pageai/ralph-loop`.
- Source: https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum ·
  https://ralphloop.sh/blog/what-is-the-ralph-technique/
- Popularity: **high / viral** — official Anthropic plugin; famous "built a programming
  language overnight" anecdote.
- Steelman: Ralph makes the *iteration* (not the chat session) the unit of work, which
  structurally defeats context rot — state lives in files and git, so an agent can grind a
  long task list for hours/days, crash-survivable, with every task an atomic reviewable
  commit gated behind tests.

### Niche / emerging (named in the brief or found alongside)

**grill-me (Matt Pocock)**
- What: a ~3-sentence Claude Code skill that inverts the flow — the agent *interrogates*
  your plan one branch of the decision tree at a time, one question per turn, with a
  recommended answer each, exploring the codebase to answer what it can rather than asking.
  Output is a plan with hidden assumptions surfaced. Pairs with native plan mode.
- Source: https://agentpatterns.ai/agent-design/grill-me-technique/ ·
  https://claudecodesessions.com/claude-code-grill-me-plan-mode/ · mattpocock/skills
- Popularity: **niche but widely shared**; a technique/prompt more than a framework.
- Steelman: It resolves expensive branch decisions *before* any code commits to them, at
  the cheapest possible moment, and the one-question-with-recommendation cadence keeps the
  interrogation productive instead of a 15-item questionnaire.

**GSD (Get Stuff Done) — chudeemeke/get-stuff-done**
- What: a Claude Code "context-engineering layer" with Plan / Execute / Verify phases,
  each in its **own fresh session**. State lives entirely in files (`PROJECT.md`,
  `STATE.md`, `ROADMAP.md`, `PLAN.md`, `REQUIREMENTS.md`). A thin orchestrator spawns
  parallel sub-agents (researcher/planner/executor/verifier) with isolated 200k contexts;
  "resume" rebuilds context from files. Slash commands `/gsd:new-project`, `plan-phase`,
  `execute-phase`, `verify-work`. A `GSD-T` teams fork adds contracts + agent teams.
- Source: https://github.com/chudeemeke/get-stuff-done ·
  https://www.mindstudio.ai/blog/gsd-framework-claude-code-plan-build-applications ·
  https://thenewstack.io/beating-the-rot-and-getting-stuff-done/
- Popularity: **niche/emerging** (npm-distributed; press coverage on The New Stack).
- Steelman: GSD's clean phase/session separation plus file-resident state keeps the main
  context lean (~30%) while heavy work runs in fresh sub-agent contexts — an explicit,
  reusable answer to context rot that survives session boundaries.

**The Claude Protocol / claude-protocol (weselow, fork of AvivK5498)**
- What: **the closest analog to yf-plan.** An enforcement-first Claude Code orchestration
  that uses the **Beads (`bd`) CLI** for persistent task tracking, "one task = one worktree
  = one PR," a `bd prime` session-start hook, and hooks that *block* (not instruct): edits
  on `main` blocked, completion without a checked checklist blocked, `git --no-verify`
  blocked. Plan → size-check → create beads → dispatch → worktree → PR → merge → close.
  Adversarial code-reviewer agent, LEARNED knowledge base.
- Source: https://github.com/weselow/claude-protocol · original:
  https://github.com/AvivK5498/The-Claude-Protocol · https://www.npmjs.com/package/claude-protocol
- Popularity: **niche** (npm/GitHub, modest following) — but directly relevant: it shares
  yf-plan's beads-and-worktree DNA.
- Steelman: It makes structure survive context loss by putting all tasks in beads (never
  markdown/TodoWrite) and enforcing discipline with hooks rather than prose — "constraints
  > instructions" — so the agent physically cannot skip the workflow.

> Note: "The Claude Protocol" as a phrase also names a looser *methodology* (context-first,
> human-in-the-loop, plan-mode-no-code, artifact consistency via `CLAUDE.md` +
> `settings.json`) described in vendor/blog posts, distinct from the beads repo above.

**OpenSpec** (found via popularity search, not in brief)
- What: a lightweight, tool-agnostic SDD framework enforcing a strict three-phase state
  machine (proposal → apply → archive) before code.
- Source: https://openspec.pro/ · https://github.com/topics/openspec
- Popularity: **high** — ~52k stars mid-2026. Included for completeness as a major SDD
  peer to Spec Kit.

---

## Common patterns across the field

1. **Plan/act separation is universal.** Every framework separates "decide what to build"
   from "write the code" — via modes (Aider, Cline/Roo), phases (Spec Kit, Kiro, BMAD,
   GSD), or a prompt inversion (grill-me).
2. **Spec/PRD as durable artifact.** Most put a Markdown spec, PRD, or requirements doc at
   the center (Spec Kit, Kiro, BMAD, Taskmaster, GSD). "Docs are the source of truth; code
   is downstream."
3. **Task decomposition into a dependency-aware graph.** Kiro (waves), Taskmaster
   (`tasks.json`), BMAD (stories), GSD (plans in waves) all topologically order work.
4. **Context rot is the shared enemy.** Ralph, GSD, claude-protocol, and the "two-phase
   workflow" all exist primarily to survive context degradation — fresh context per
   iteration/phase, state on disk, resume from files.
5. **Verification/review as a distinct step.** Spec Kit (`analyze`/`converge`), Kiro
   (property tests), GSD (verify phase), BMAD (QA agent), claude-protocol (adversarial
   reviewer), Ralph (test gate before commit).
6. **Worktree / one-PR-per-task isolation** is emerging (claude-protocol explicitly;
   Taskmaster tags approximate it).
7. **Human gates** appear as review checkpoints (Spec Kit workflow gates, Cline's approve-
   every-step, grill-me's whole premise).

---

## How yf-plan differs (honest, non-strawman contrast)

The field is strong. yf-plan is **not** the only tool doing plan/act separation, spec-
first, task graphs, worktrees, or context-rot survival — those are table stakes now. Its
distinctiveness is in **which of these it combines and how rigorously it enforces the
seams**, verified against `SKILL.md`:

1. **Beads-tracked DAG execution as the ONLY task tracker, with a molecule/formula pour.**
   Like claude-protocol and Taskmaster, yf-plan externalizes tasks — but into a **Dolt-
   backed `bd` graph** poured from a `plan-execute` formula (`bd mol pour`), with epics,
   gate beads, and dependency edges wired in one transactional `bd batch`. It bans
   TodoWrite/markdown TODOs outright. *Differs from:* SDD tools that keep tasks in a
   `tasks.md`/`tasks.json` file (mutable, no gate semantics, no DAG-typed gates).

2. **SPEC-first as a hard sequencing rule, not just "spec before code."** yf-plan's parent
   project mandates the `SPEC.md` requirement (new `REQ-*` id + living-amendment-log entry)
   land *ahead of* implementation in the same change-set, enforced by a coverage gate.
   Spec Kit/Kiro generate a spec artifact; yf-plan treats the spec as a **governed,
   requirement-ID'd contract** with tagged tests. (This is a project convention layered on
   the skill, but it's load-bearing to the "why.")

3. **Cross-session resumability keyed on a content FINGERPRINT, not just files-on-disk.**
   Everyone stores state in files. yf-plan additionally writes a `**Fingerprint:**` hash
   over the reviewed content sections at approval. A later content edit makes the stored
   fingerprint stale and **`resume-scan` hard-blocks EXECUTE** until a fresh review cycle
   re-approves (or explicit `--force`). This is a **stale-approved gate**: approval binds
   to *reviewed content*, so execution can't silently run a plan that changed after sign-
   off. No surveyed framework has this content-binding approval gate.

4. **Portable plan folders as an OKF bundle with a mechanical audit.** The plan directory
   (reserved `index.md` + `log.md`, `context.md`, `findings/`, `references/`, `reviews/`,
   `plan.md`) is designed so a **cold reader in a different repo/harness** can understand
   the plan from the folder alone, and a `plan_manager.py audit` mechanically enforces the
   portability contract (motivation present, review-file/phase-log count-equality, etc.)
   *before* approval is even offered. GSD/claude-protocol keep state in files too, but as
   working memory, not as a portability-audited, cross-harness bundle.

5. **Red-team review as a gating verdict with a create-on-present, count-equality'd
   `reviews/pass-N.md` lifecycle.** Two ordered passes: mechanical conformance, then an
   **adversarial red-team whose verdict drives the phase transition**. A REVISE blocks
   `ready-for-approval` until a *later* cycle returns APPROVE (readiness keys on the *last*
   verdict). Reports are written the moment the red-team presents — portable before the
   operator resolves anything. claude-protocol and BMAD have adversarial reviewers, but not
   a verdict-gated, last-verdict-wins, fingerprint-adjacent readiness gate.

6. **Worktree execution + MERGED-STATE re-validation (merge-back FIRST, then validate).**
   claude-protocol does one-worktree-per-task; yf-plan runs execution in
   `.worktrees/<plan-id>` from a *pinned base*, then in RECONCILE **merges to the pinned
   target first and validates the merged tree** (via an approved `CHANGE-VALIDATION.md`
   engine or a `validate-cmd` fallback) — catching class-(b) integration regressions that
   pre-merge validation cannot. A single-machine landing lock serializes concurrent plans.
   No surveyed framework validates the *post-merge* integrated state as a distinct gate.

7. **Upstream-issue reconciliation as a first-class phase.** yf-plan scans the issue
   tracker at scope time, records per-issue dispositions (include/exclude/partial/
   supersede), attaches `resolves-upstream` metadata to beads, files ONE coarse tracking
   issue per plan, and RECONCILE updates upstream per disposition. Spec Kit has a one-way
   `taskstoissues`; none do bidirectional triage → resolve reconciliation.

8. **Two-way phase model with explicit backward transitions and human approval as consent
   to an already-verified plan.** SCOPE↔INVESTIGATE, PLAN→SCOPE, PLAN→INTAKE only on
   operator approval *after* ready-check is green. Approval is a single act of consent on a
   plan that is *already* red-team-APPROVE'd + audit-passed + fingerprinted — not an open-
   ended "looks good."

**The single sharpest differentiator:** *Approval is cryptographically bound to reviewed
content and enforced across the session boundary.* Every other framework's "plan" is a
living file the agent can (and does) drift from; yf-plan's fingerprint + stale-approved
resume gate makes the reviewed-and-approved plan the **only** thing that can execute, or the
whole review cycle must re-run. Plan/act separation elsewhere is a *posture*; in yf-plan
it's an *enforced contract with a hash*.

---

## Does the survey support "these treat planning as single-session / single-machine"?

**Partially — with an important honest caveat.**

- **Single-session:** TRUE for the mode-based and prompt tools (Aider architect, Cline/Roo
  Plan/Act, grill-me) — planning and acting happen in one conversational session; there's
  no durable resumable plan object. It is **increasingly FALSE** for the serious
  frameworks: Spec Kit's workflow engine persists state and has `workflow resume`; Kiro
  syncs specs across sessions; GSD, Ralph, BMAD, and claude-protocol *explicitly* store
  state on disk to survive session boundaries and were built for multi-day runs. So the
  claim "planning is single-session" is a fair characterization of the *lightweight* tools
  but a **strawman if aimed at the whole field**. yf-plan's edge here is narrower and
  truer: not "we resume and they don't," but "**resumption is gated on a content
  fingerprint** so a drifted plan can't silently execute" — a stronger claim that holds.

- **Single-machine:** TRUE more broadly. Most frameworks store state in the local repo/
  filesystem; portability across machines/harnesses is rarely a design goal. yf-plan's
  portable OKF plan bundle + Dolt-backed beads (replicable) + audit for cross-harness
  readability is genuinely differentiated. Even claude-protocol (the closest analog) ties
  to Claude Code hooks; Spec Kit is agent-agnostic but its *state* isn't presented as a
  portable, audited bundle. **This claim is well supported.**

**Recommendation for the web copy:** Lead with the *single-machine / non-portable* and
*drift-uncontrolled* contrasts (strong, defensible) rather than a blanket *single-session*
claim (easy to falsify with Spec Kit/GSD/Ralph). Frame yf-plan as "resumable like the best
of them, but the resumption is **content-bound and portability-audited** — the plan you
approved is the plan that runs, from any machine, or it goes back through review."

---

## Recommended "Why" section content (draft prose + comparison table)

### Draft prose

> **The planning landscape is crowded — and mostly right.** Spec-first development
> (GitHub Spec Kit, Kiro, OpenSpec), PRD-to-task-graph systems (Taskmaster), agent-team
> methods (BMAD), plan/act modes (Cline, Roo, Aider), and context-rot loops (Ralph, GSD)
> have all converged on the same good instincts: decide before you build, keep state in
> files, decompose into a dependency graph, verify separately, and survive long runs.
> yf-plan agrees with all of it.
>
> **What yf-plan adds is enforcement at the seams.** A plan isn't a living document the
> agent drifts from — at approval it's fingerprinted, and if its content changes, execution
> **hard-stops** until a fresh red-team + portability audit re-approves it. The plan you
> reviewed is the only plan that runs. Tasks aren't a `tasks.md` the agent edits freely —
> they're a beads-tracked DAG with typed gates, poured once and resumed deterministically
> across the session boundary. Execution isn't validated where it was written — it's merged
> to the pinned target and **the integrated tree is re-validated**, catching regressions
> that only appear after merge. And the whole plan is a portable bundle a teammate on
> another machine — or another agent harness — can pick up cold, because a mechanical audit
> guarantees it.
>
> yf-plan is the choice when "the agent mostly followed the plan" isn't good enough.

### Comparison table

| Capability | Spec Kit | Kiro | BMAD | Taskmaster | Cline/Roo | Aider | Ralph | GSD | claude-protocol | **yf-plan** |
|---|---|---|---|---|---|---|---|---|---|---|
| Plan/act separation | Phases | Phases | Phases | Loop | Modes | Modes | Loop | Phases | Phases | **Phases (2-way)** |
| Spec/PRD as artifact | Yes | Yes | Yes | Yes (PRD) | No | No | Task list | Yes | Beads | **Yes (SPEC-first, REQ-ID'd)** |
| Task graph / DAG | tasks.md | Waves | Stories | tasks.json | Todo | No | tasks.json | Plans/waves | **Beads** | **Beads DAG + typed gates** |
| Resumable across sessions | Workflow resume | Spec sync | Files | Files | No | No | Files+git | Files | Beads | **Yes, fingerprint-gated** |
| Drift-controlled approval | Analyze/converge | Reasoning check | — | — | — | — | — | — | Checklist hook | **Content fingerprint hard-gate** |
| Adversarial review gate | analyze | Property tests | QA agent | — | — | — | Test gate | Verifier | Reviewer agent | **Red-team verdict gates phase** |
| Worktree isolation | — | — | — | Tags | — | git | git | git | **1 WT/task** | **WT + pinned base** |
| Merged-state re-validation | — | — | — | — | — | — | — | — | — | **Yes (merge-first)** |
| Upstream issue reconcile | tasks→issues (1-way) | — | — | — | — | — | — | — | — | **2-way triage→resolve** |
| Portable / cross-harness bundle | Agent-agnostic | No (IDE) | Web bundles | Editor-agnostic | No | No | No | Files | No (CC hooks) | **OKF bundle + audit** |

> Table is a directional summary from mid-2026 docs; cells compress nuance (e.g. Spec Kit's
> workflow gates are real but not content-hash-bound). Verify before publishing as marketing.

---

## Sources

- GitHub Spec Kit — https://github.com/github/spec-kit ·
  https://github.github.io/spec-kit/ · https://github.github.io/spec-kit/quickstart.html ·
  https://github.com/github/spec-kit/tree/main/workflows ·
  https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/
- Spec Kit / OpenSpec popularity — https://www.star-history.com/github/spec-kit/ ·
  https://github.com/github/spec-kit/discussions/1482 · https://openspec.pro/ ·
  https://github.com/topics/openspec · Augment Code roundup:
  https://www.augmentcode.com/tools/best-spec-driven-development-tools
- Kiro — https://kiro.dev/ · https://kiro.dev/docs/specs/ ·
  https://github.com/kirodotdev/Kiro · https://aws.amazon.com/documentation-overview/kiro/ ·
  https://www.infoq.com/news/2025/08/aws-kiro-spec-driven-agent/
- BMAD-METHOD — https://github.com/bmad-code-org/BMAD-METHOD ·
  https://docs.bmad-method.org/ · https://docs.bmad-method.org/reference/agents/ ·
  https://github.com/bmad-code-org/BMAD-METHOD/blob/aa573bdb/docs/reference/workflow-map.md ·
  https://redreamality.com/garden/notes/bmad-method-guide/
- Taskmaster — https://github.com/eyaltoledano/claude-task-master ·
  https://docs.task-master.dev/capabilities/rpg-method · https://docs.task-master.dev/
- Aider architect mode — https://aider.chat/docs/usage/modes.html ·
  https://aider.chat/2024/09/26/architect.html ·
  https://deepwiki.com/Aider-AI/aider/5.5-architect-mode
- Cline / Roo — https://docs.cline.bot/core-workflows/plan-and-act · https://cline.bot/ ·
  https://linuru.com/documents/cline-vs-roo-code-shortcuts/
- Ralph — https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md ·
  https://ralphloop.sh/blog/what-is-the-ralph-technique/ ·
  https://ralphloop.sh/blog/run-ai-coding-agent-overnight/ ·
  https://claudefa.st/blog/guide/mechanics/ralph-wiggum-technique
- grill-me — https://agentpatterns.ai/agent-design/grill-me-technique/ ·
  https://claudecodesessions.com/claude-code-grill-me-plan-mode/ ·
  https://agentcookbooks.com/skills/grill-me/ · https://coey.dev/prompts/grill-me
- GSD — https://github.com/chudeemeke/get-stuff-done ·
  https://www.mindstudio.ai/blog/gsd-framework-claude-code-plan-build-applications ·
  https://thenewstack.io/beating-the-rot-and-getting-stuff-done/ ·
  https://github.com/Tekyz-Inc/get-stuff-done-teams
- The Claude Protocol / claude-protocol — https://github.com/weselow/claude-protocol ·
  https://github.com/AvivK5498/The-Claude-Protocol · https://www.npmjs.com/package/claude-protocol ·
  https://developersvoice.com/blog/ai/claude-code-architect-sdlc/
- yf-plan claims verified against: `skills/yf-plan/SKILL.md` (this repo)

---

## Implications for Plan

1. **Positioning is defensible but must be worded carefully.** Do NOT claim rivals are
   "single-session" as a blanket — Spec Kit (`workflow resume`), Ralph, GSD, and BMAD are
   explicitly multi-session. Lead instead with the two claims the survey *supports*:
   (a) **non-portable / single-machine** state, and (b) **uncontrolled plan drift** (no
   content-bound approval gate). These are true across the field and are yf-plan's real
   moat.
2. **Name claude-protocol explicitly as the honest closest analog** (beads + worktrees +
   enforcement hooks). The "Why" page is more credible if it acknowledges it and draws the
   real distinctions (fingerprint gate, merged-state validation, portability audit, upstream
   reconcile, SPEC-first REQ-IDs) rather than pretending yf-plan is sui generis.
3. **The comparison table needs a fact-check pass before it ships** as marketing — a few
   cells (Spec Kit workflow gates, Kiro reasoning checks) compress nuance and a competitor
   could nitpick. Consider footnoting or softening to "as of mid-2026."
4. **Lead the "Why" with the enforcement-at-the-seams thesis**, not a feature checklist —
   the field has feature parity on individual capabilities; yf-plan's story is the
   *combination* + *hard gates* (fingerprint, red-team verdict, merged-state, audit).
5. **Star counts drift fast** (Spec Kit moved ~40k stars in 4 months). If the page cites
   numbers, date-stamp them or omit them.
6. **Consider a short "we agree with the field" paragraph** (intellectual honesty) before
   the differentiators — it disarms the "yet another planning framework" reaction and makes
   the specific claims land harder.
