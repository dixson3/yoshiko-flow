Title: workflows
Slug: workflows
Subtitle: the yf-plan and yf-research multi-phase pipelines and the subagents that run them

`yf-plan` and `yf-research` are the two `workflows`-group skills. Neither does its work
inline: each decomposes a job into a beads-tracked DAG and drives it to completion by
dispatching **subagents** — focused, single-purpose prompts under `skills/<skill>/agents/`,
spawned via the `Agent` tool with declared inputs and outputs. This page documents both
pipelines phase by phase and every subagent each dispatches.

It complements the [lifecycle](/lifecycle/) page (which covers the shared five-stage skill
lifecycle — install, preflight, invoke, coordinate/execute, land the plane) and the
[glossary](/glossary/) (which defines the recurring vocabulary). Workflow terms link to the
glossary on first use.

## yf-plan

`yf-plan` turns an objective into a reviewed, approved plan and then executes it. Its defining
property is a **session boundary**: planning and approval happen in one session, execution in a
fresh one, and eligibility to cross that boundary is carried by a content
[fingerprint](/glossary/#fingerprint), not by in-memory state.

### The phases

The phase model is the designer's orchestration abstraction. The runtime never narrates it:
no "now entering PLAN" banner is ever printed. You observe the phases only indirectly, through
three surfaces:

- **status values**, shown by `/yf-plan status` and recorded in `plan.md`;
- **phase-log entries** in the plan folder's `log.md`;
- **gate prompts** at the session boundary and at approval.

The phases are genuinely present in the machinery — each has a distinct responsibility and a
distinct status footprint. They are simply never announced as discrete events.

![The yf-plan phase model: seven phases with their status footprints, backtrack edges, the session boundary, and the terminal complete status](/images/phase-model.png)

*The yf-plan phase model. UPSTREAM discovery runs once per project. The six per-plan phases each
own one or more status values. `complete` is the terminal status of RECONCILE, not an eighth
phase. Phases surface only as status values, `log.md` phase-log entries, and gate prompts —
never as narrated announcements.*

yf-plan has **seven phases**: UPSTREAM, SCOPE, INVESTIGATE, PLAN, INTAKE, EXECUTE, RECONCILE.

- **UPSTREAM** — Discovers project-level context (the upstream tracker, conventions) and persists
  it to `CLAUDE.md`. Runs **once per project**, not once per plan. Each new plan re-validates the
  persisted context rather than re-running discovery, so UPSTREAM is a preamble to the per-plan
  sequence, not an equal step in it.
- **SCOPE** — Establishes the objective, constraints, scope boundaries, and success criteria.
  Runs in the `<plan-id>-development` planning worktree; the plan folder itself stays
  primary-side under `docs/plans/<plan-id>/` or `Incubator/<slug>/plans/<plan-id>/`. Also scans
  the upstream issue tracker for related issues and records a disposition
  (`include`/`exclude`/`partial`/`supersede`) for each. Output: `plan.md` with `status: scoping`
  and the scoping decisions captured. Investigation may revise scope, so SCOPE and INVESTIGATE
  form a loop.
- **INVESTIGATE** — Resolves the plan's unknowns. One **investigator** subagent is dispatched
  per experiment, each in a disposable worktree; findings are written to
  `findings/exp-NNN-<slug>.md` before the next subagent spawns. The investigation sub-tree is
  tracked with a [wisp](/glossary/#wisp) (burned at execute). Inputs: the experiment questions
  and scoping context. Output: findings that feed the plan. Findings can invalidate scope
  (back to SCOPE) or prove sufficient (forward to PLAN).
- **PLAN** — Synthesizes scope answers and findings into the full plan document (epics, issues,
  dependency graph, gates, risks, success criteria) via the **planner** subagent, then reviews
  it. Review is two ordered read-only passes: a mechanical **reviewer** conformance check
  (`PASS`/`INCOMPLETE`), then the adversarial **red-team** ([red-team](/glossary/#red-team))
  whose verdict (`APPROVE`/`REVISE`/`INVESTIGATE-MORE`) drives the transition and owns the
  `reviews/pass-N.md` lifecycle. A `REVISE` mandates a fresh red-team cycle; readiness keys on
  the *last recorded* verdict. Once the last verdict is `APPROVE`, a portability audit and a
  `ready-check` gate must both pass before the operator is asked to approve. PLAN owns **three**
  status values in sequence: `drafting` (synthesis), then `review` (the two review passes), then
  `ready-for-approval` (the gated pre-approval state). Output: a plan in `ready-for-approval`.
- **INTAKE** — Freezes the approved plan. On operator approval, [intake](/glossary/#intake)
  transitions `ready-for-approval → approved`, writes the content
  [fingerprint](/glossary/#fingerprint) over the reviewed sections, commits the plan locally on
  its branch (never on `main`, never a push), lands it per the landing strategy, and files the
  single coarse upstream tracking issue. **Intake does not pour the molecule** — the
  [pour](/glossary/#pouring-beads-pour) and the whole bead DAG are deferred to EXECUTE. Output:
  a fingerprinted, committed, execution-eligible plan and a handoff instruction to run
  `/yf-plan execute` in a new session.
- **(session boundary)** — The operator starts a fresh session. Execution eligibility is carried
  entirely by the plan's fingerprint.
- **EXECUTE** — Runs the plan. Four mechanisms govern it:
  - **Pour-once/resume gate** (driven by `resume-scan`) — an absent epic is the normal first
    execution: pour the `plan-execute` [molecule](/glossary/#molecule), create the beads, and
    resolve the start [gate](/glossary/#gate). A present epic is a resume: re-attach the
    worktree, sweep stuck beads, and do not re-pour.
  - **Stale-approved hard gate** — refuses to execute a
    [stale-approved](/glossary/#stale-approved) plan (one whose content changed after approval,
    so the stored fingerprint no longer matches) until it is re-approved or `--force`d.
  - **Worktree execution** — runs in an isolated git worktree (`.worktrees/<plan-id>`, branch
    `<plan-id>-execute`, cut from a pinned base) driven by the **coordinator**. Code edits
    target the worktree; bead tracking and the plan folder stay primary-side.
  - **In-place fallback** — runs the coordinator without a worktree when one is not viable.

  Output: a drained bead DAG on the execute branch.
- **RECONCILE** — Lands and squares up. It merges back **first**, then validates the **merged**
  state, then pushes, in a fixed order:
  1. Acquire the landing lock.
  2. Merge `<plan-id>-execute` into the pinned target with `--no-ff`.
  3. Run the cross-plan `validate-merged` safety net (which delegates to
     [yf-change-validation](/architecture/) when an approved manifest exists).
  4. On pass, commit the merge and release the lock.

  The push stays conservative (reported, operator-authorized). The **reconciler** subagent then
  updates the incorporated upstream issues per their dispositions. See
  [reconcile](/glossary/#reconcile).

  RECONCILE then closes out through an **extensible ordered gate chain** — steps governed by
  ordering constraints rather than a fixed count, terminating in `set complete`. Today's chain
  includes cascade-close and the completion gate:
  - [cascade-close](/glossary/#cascade-close) closes every container in the plan tree
    (intermediate epics and the top-level plan molecule) whose children are all terminal,
    bottom-up. It is **fail-loud**: a container with any still-open child halts completion.
  - The completion gate is a no-op for a `standard` plan, and fail-louds for a `ci-release` plan
    whose runner-only-observable behavior is unattested.
  - Only when both pass does RECONCILE set the status to `complete`.

**`complete` is a status, not a phase.** There is no eighth phase. `complete` is the terminal
*status* that RECONCILE sets at the end of its close-out step. The seven phases are UPSTREAM
through RECONCILE; `complete` marks the plan as finished from inside RECONCILE.

**Status values.** yf-plan uses nine status values, mapped to phases many-to-one:

| Phase       | Status value(s)                                              |
| :---------- | :----------------------------------------------------------- |
| UPSTREAM    | (none — precedes the status vocabulary)                      |
| SCOPE       | `scoping`, then `investigating`                              |
| INVESTIGATE | `investigating`                                              |
| PLAN        | `drafting` → `review` → `ready-for-approval`                 |
| INTAKE      | `approved`                                                   |
| EXECUTE     | `executing`                                                  |
| RECONCILE   | `reconciling`, then terminal `complete`                      |
| (any phase) | `abandoned` — terminal, deliberately stopped                 |

`ready-for-approval` is the gated pre-approval state reached only when `ready-check` is green
(last red-team `APPROVE` plus audit `pass`); approval transitions it to `approved`.

`abandoned` is the terminal state for a plan deliberately stopped. It is reachable from any
non-`complete` status and leaves by **exactly one** edge — back to `drafting`. There is no
`abandoned → complete` edge: a plan that was stopped did not finish, and letting it claim
completion is the silent misreport the vocabulary exists to prevent. An abandoned plan is not
execute-eligible and is not *parked*.

**Overlays, not statuses.** Two labels you may see on an `approved` plan are *derived overlays*
on the `approved` status, not members of the nine-value set. Both are computed from the content
fingerprint and the execution history:

- **stale-approved** — the plan's content changed after approval, so the stored fingerprint no
  longer matches. This overlay blocks EXECUTE until re-approval or `--force`.
- **parked** — the plan is `approved` with a fresh fingerprint but has never executed.

**The nine values are documented, not enum-enforced.** `update-status` is a free-form writer. It
accepts any status string and does **not** validate against a fixed set — there is no enum and no
transition guard in the code. A typo'd or invented status would be written silently. The
nine-value vocabulary is the source of truth in the spec and tests, verified by a `grep` check,
never by a runtime guard.

**Key mechanics:**

- **Content-fingerprint-bound approval.** Approval binds to *reviewed content*. The fingerprint
  hashes the plan's content sections (excluding self-trigger bookkeeping like the phase log and
  review tables). A later content edit makes the stored fingerprint stale and blocks EXECUTE
  until a fresh conformance → red-team → portability cycle re-approves.
- **Intake-at-execute pour.** No molecule exists until EXECUTE start. There is exactly one
  pour-once/resume decision point, which subsumes the old separate intake-duplicate and
  execute-resume guards.
- **Worktree execution.** Code changes accumulate on `<plan-id>-execute` in a persistent git
  worktree; the coordinator never `cd`s into it and never uses the `isolation="worktree"`
  harness primitive (that is reserved for INVESTIGATE experiments).
- **Merge-back + merged-state validation.** Phase 6 validates the *integrated* tree, catching
  regressions that are individually green but broken when merged — a class the old
  validate-before-merge order could not catch.
- **Cascade-close completion.** Completion never bare-closes the epic; it cascade-closes every
  container bottom-up and halts loudly on any open child.

### The yf-plan subagents

All are dispatched by the main session via the `Agent` tool, reading their prompt from
`skills/yf-plan/agents/<name>.md`. The review agents are **read-only with respect to the repository under
review** — they never write files in it, though a sandbox spike outside it is authorized;
the main session acts on their verdicts.

| Subagent | Role | Inputs | Output | Read-only? |
| :------- | :--- | :----- | :----- | :--------- |
| **investigator** (`investigator.md`) | Runs a single experiment in a disposable worktree to answer one planning unknown. Dispatched one-per-unknown, in parallel for independent experiments, with `isolation="worktree"`. | The experiment question, constraints, and scoping context | Structured findings (approach tested, result with evidence, implications, recommendation); "inconclusive" is valid. No worktree code lands in the project. | No |
| **planner** (`planner.md`) | Chooses the approach (citing specific findings), decomposes into epics and issues, wires dependencies, links upstream issues to resolving beads, adds capability gates only where genuinely required, and authors a d2 structure diagram for non-trivial plans. | Scope answers, findings, upstream triage | The full `plan.md`, written **only** to the resolved `plan_dir` | No |
| **reviewer** (`reviewer.md`) | Mechanical conformance/completeness check that runs **first**, as a gate before red-team. Walks a fixed checklist (every epic has an issue, graph acyclic, criteria verifiable, upstream includes wired, gates declare type and approvers, all portability sections present). Makes no quality judgments — that is red-team's job. | The drafted `plan.md` | Verdict `PASS \| INCOMPLETE` | Yes |
| **red-team** ([red-team](/glossary/#red-team), `red-team.md`) | Adversarial review with fresh eyes (no access to investigation worktrees), run **after** conformance passes. Evaluates completeness, feasibility, risk, gate necessity, and upstream dispositions. **Its verdict drives the phase transition.** | The conformance-passed `plan.md` | Verdict `APPROVE \| REVISE \| INVESTIGATE-MORE` with strengths, severity-tagged concerns and recommendations, and gaps. The main session writes and updates `reviews/pass-N.md`. | Yes |
| **coordinator** (`coordinator.md`) | Orchestrates EXECUTE. On a resume, first sweeps stuck beads (resetting `in_progress`/claimed beads to open, never auto-closing); then loops `bd ready` → resolve gates by running their test commands → claim → dispatch (spawning the metadata-named subagent, or executing directly) → close. Routes code edits to the worktree, bead/plan bookkeeping primary-side. Triggers reconcile when all execution beads close, then hands back — it does **not** close the epic, merge, or push. | The poured bead DAG | A drained bead DAG on the execute branch | No |
| **reconciler** (`reconciler.md`) | Updates upstream issues after execution completes and changes are pushed. Verifies each resolving bead is actually closed (flags mismatches rather than guessing), then closes `include` issues, comments on `partial`, and closes `supersede` with rationale — always referencing the plan ID and commit. | `plan.md`'s Upstream Issues table | Updated upstream issues; a closed/commented/skipped/flagged summary | No |
| **captor** (`captor.md`) | Drafts missing portability-contract files for a plan folder (invoked by `/yf-plan capture`, not part of the linear phase flow). Drafts absent `index.md`, `context.md`, a `## Motivation`, `references/upstream-<N>.md`, `reviews/pass-<N>.md`. Never invents reviewer verdicts or tool versions. | Current plan state (and, under `--retro`, the live session's conversation) | Drafted files for operator review; **never writes files** itself (the main session does) | Yes |

## yf-research

`yf-research` decomposes a research topic into a beads-tracked DAG and produces a structured,
citation-backed report with source credibility scoring. Interactive SCOPE and PLAN phases
produce a `plan.yaml` and pour the molecule; execution then runs the retrieve → triangulate →
synthesize → critique → refine → package pipeline under a **coordinator**. Depth is chosen at
scope — `quick` (auto-resolved gate, same session) through `standard`/`deep`/`ultradeep` (a
manual [gate](/glossary/#gate) and a fresh `/yf-research coordinate` session).

### The phases

The pipeline steps below are the poured formula's beads; each is dispatched by the coordinator
to its named subagent when it becomes ready.

- **retrieve** — Gathers sources, one **retriever** subagent per source cluster (academic,
  industry, community, news, code, …), fanned out dynamically from `plan.yaml`. Exa MCP is the
  preferred provider, with a Tavily/Perplexity/WebSearch fallback chain. Retrieval is
  API-first — never scraping or link-walking. Inputs: the cluster assignment. Outputs:
  `sources.json` entries (with verbatim quotes and preliminary credibility) and one
  `artifacts/cluster-<name>.md` per cluster. A cluster with no usable sources documents what was
  searched rather than fabricating.
- **triangulate** — Cross-references claims across every cluster via the **triangulator**
  subagent. It scores each source for credibility (domain authority, currency, expertise, bias
  neutrality), flags contradictions, and identifies consensus (3+ independent sources agreeing).
  Inputs: all `cluster-*.md` and `sources.json` (excludes `plan.yaml`). Output:
  `artifacts/triangulation.md` with a confidence level and supporting quotes per finding.
  Under-supported findings are marked `[insufficient evidence]`.
- **synthesize** — Builds the narrative report answering each research question via the
  **synthesizer** subagent, working from triangulated findings only. Every factual claim carries
  an inline GFM citation resolving into `sources.md`, backed by a direct quote. Inputs:
  `plan.yaml` questions and `artifacts/triangulation.md` (excludes raw retrieval artifacts).
  Output: draft `Summary.md`.
- **critique** — Red-teams the draft via the **red-team** subagent, deliberately **without**
  `plan.yaml` to prevent confirmation bias. It checks that all claims are cited and quote-backed
  and that credibility scores hold up. It flags logical gaps, source-selection bias, uncited
  "model-knowledge" claims, and unresolved `[uncertain]` tags. Inputs: `Summary.md` and
  `sources.json`. Output: `artifacts/critique.md` — actionable items for the refiner.
- **refine** — Addresses each critique item via the **refiner** subagent. It edits `Summary.md`
  for fixes possible from existing sources, and creates new `discovered-from` retrieve beads
  (wired into the package step) for gaps needing fresh evidence. An `[uncertain]` tag is removed
  only when a claim gains 2+ independent sources scoring ≥ 60; unfillable gaps are noted
  explicitly rather than softened. Inputs: `Summary.md`, `critique.md`, `plan.yaml`.
- **package** — Finalizes via the **packager** subagent. It verifies every citation resolves and
  no claim is uncited, cross-checks research questions against the report, authors a d2 structure
  diagram for non-trivial reports, generates `sources.md` and normalizes citation links, updates
  `index.md`, and closes the epic. It ends with a **conservative git handoff**: it reports
  changed files and the proposed commit/push commands, but does not commit or push without
  explicit authorization.

**Epistemic rules** apply to every agent and every artifact:

1. **Absence is a valid finding.** If a question cannot be answered from available sources, state
   "No evidence found" with what was searched and where — never fabricate or pad with general
   knowledge.
2. **Direct quotes over paraphrase.** Cite with a direct quote (`> "..." [N]`) and inline
   citation; paraphrase only when the original is excessively long, still cited.
3. **No uncited assertions.** Every factual claim carries an inline citation `[N]` resolving to a
   `sources.json` entry. Methodology/structure statements are exempt; anything else that cannot be
   cited is flagged `[uncited]`.

### The yf-research subagents

Each is dispatched by the coordinator via the `Agent` tool, reading its prompt from
`skills/yf-research/agents/<name>.md` with a strictly declared context — **context isolation is
enforced per-agent** (for example, the red-team must not see `plan.yaml`).

| Subagent | Role | Inputs | Output | Read-only? |
| :------- | :--- | :----- | :----- | :--------- |
| **coordinator** (`coordinator.md`) | Drives the research molecule to completion. Runs a pre-loop stuck-bead sweep (resetting stranded beads on a resume, never auto-closing), then loops `bd ready` → claim → read the bead's `agent`/`context` metadata → dispatch that subagent with only its declared context files → record the artifact in `index.md` → close. Enforces the epistemic rules. | The poured research molecule | A completed molecule; a conservative git handoff rather than a commit | No |
| **toolsmith** (`toolsmith.md`) | Creates and validates the scripts declared in `plan.yaml`'s `tooling_needed`. Writes PEP 723 Python (topic-specific into `research_dir/scripts/`, reusable ones into the skill's own `scripts/`), tests each with `uv run <script> --help`, and enforces rate-limit and graceful-failure conventions for API callers. Runs before retrieval so its tools are available. | `plan.yaml`'s `tooling_needed` | Validated scripts | No |
| **retriever** (`retriever.md`) | Gathers sources for **one** cluster (dispatched N-up, one per cluster). Prefers Exa MCP with a documented fallback chain; strictly API-first (no scraping or link-walking). | `plan.yaml` and its cluster config (excludes other clusters' artifacts) | `sources.json` entries and `artifacts/cluster-<name>.md` with per-claim direct quotes | No |
| **triangulator** (`triangulator.md`) | Cross-references and credibility-scores the gathered sources via `credibility_scorer.py`. Introduces no claims absent from the retrieval artifacts — synthesizes existing evidence only. | All `cluster-*.md` and `sources.json` (excludes `plan.yaml`) | `artifacts/triangulation.md` | No |
| **synthesizer** (`synthesizer.md`) | Writes the narrative `Summary.md`, answering each `plan.yaml` question with inline GFM citations and direct quotes, tagging single-source and uncertain claims. | `triangulation.md` and `plan.yaml` questions (excludes raw retrieval artifacts) | Draft `Summary.md` | No |
| **red-team** (`red-team.md`) | Critiques the draft on its own merits, deliberately **excluding** `plan.yaml` to avoid confirmation bias. Validates citations, quote-backing, credibility scores, and bias. | `Summary.md` and `sources.json` | `artifacts/critique.md` | Writes the critique artifact only |
| **refiner** (`refiner.md`) | Works through each critique item: edits `Summary.md` for in-source fixes and creates new `discovered-from` retrieve beads for evidence gaps (wiring them ahead of the package step). | `Summary.md`, `critique.md`, `plan.yaml` | Edited `Summary.md`; new retrieve beads | No |
| **packager** (`packager.md`) | Finalizes the report and closes the molecule: verifies all citations resolve, cross-checks questions, generates `sources.md` and normalizes links, updates `index.md`, closes the epic, and reports the conservative git handoff (no auto-commit/push). | All files in the research directory | Finalized report; a git handoff | No |
