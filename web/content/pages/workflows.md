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

```
UPSTREAM --> SCOPE <--> INVESTIGATE --> PLAN --> INTAKE
                                                  |
                                          === session boundary ===
                                                  |
                                              EXECUTE --> RECONCILE --> COMPLETE
```

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
  `ready-check` gate must both pass before the operator is asked to approve. Output: a plan in
  `ready-for-approval`.
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
- **EXECUTE** — Runs the plan. A single pour-once/resume gate (driven by `resume-scan`) decides:
  an absent epic is the normal first execution (pour the `plan-execute`
  [molecule](/glossary/#molecule), create the beads, resolve the start
  [gate](/glossary/#gate)); a present epic is a resume (re-attach the worktree, sweep stuck
  beads, do not re-pour). A **stale-approved hard gate** refuses to execute a
  [stale-approved](/glossary/#stale-approved) plan — one whose content changed after approval so
  the stored fingerprint no longer matches — until it is re-approved or `--force`d. Execution
  runs in an isolated git worktree (`.worktrees/<plan-id>`, branch `<plan-id>-execute`, cut from
  a pinned base) driven by the **coordinator**; code edits target the worktree while bead
  tracking and the plan folder stay primary-side. A safe in-place fallback runs the coordinator
  without a worktree when one is not viable. Output: a drained bead DAG on the execute branch.
- **RECONCILE** — Lands and squares up. The order is merge-back **first**, then validate the
  **merged** state, then push: acquire the landing lock, merge `<plan-id>-execute` into the
  pinned target with `--no-ff`, run the cross-plan `validate-merged` safety net (which delegates
  to [yf-change-validation](/architecture/) when an approved manifest exists), and only on pass
  commit the merge and release the lock. The push stays conservative (reported,
  operator-authorized). The **reconciler** subagent then updates the incorporated upstream issues
  per their dispositions. See [reconcile](/glossary/#reconcile).
- **COMPLETE** — Closes out in a fixed order: **cascade-close → complete-gate → set complete**.
  [cascade-close](/glossary/#cascade-close) closes every container in the plan tree
  (intermediate epics and the top-level plan molecule) whose children are all terminal,
  bottom-up, and is **fail-loud** — a container with any still-open child halts completion. The
  completion gate is a no-op for a `standard` plan and fail-louds for a `ci-release` plan whose
  runner-only-observable behavior is unattested. Only when both pass is status set to `complete`.

**Status values:** `scoping | investigating | drafting | review | ready-for-approval |
approved | executing | reconciling | complete`. `ready-for-approval` is the gated pre-approval
state reached only when `ready-check` is green (last red-team `APPROVE` plus audit `pass`);
approval transitions it to `approved`.

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
`skills/yf-plan/agents/<name>.md`. The review agents are **read-only** — they never write files;
the main session acts on their verdicts.

- **investigator** (`investigator.md`) — Runs a single experiment in a disposable worktree to
  answer one planning unknown. Reads the experiment question, constraints, and scoping context;
  returns structured findings (approach tested, result with evidence, implications, and a
  recommendation). "Inconclusive" is a valid finding. No code from its worktree lands in the
  project. Dispatched one-per-unknown, in parallel for independent experiments, with
  `isolation="worktree"`.
- **planner** (`planner.md`) — Synthesizes scope answers, findings, and upstream triage into the
  full `plan.md`: chooses the approach (referencing specific findings), decomposes into epics and
  issues, wires dependencies, links upstream issues to resolving beads, adds capability gates only
  where genuinely required, and authors a d2 structure diagram for non-trivial plans. Writes
  **only** to the resolved `plan_dir`. Not read-only (it produces the plan document).
- **reviewer** (`reviewer.md`) — Mechanical conformance/completeness check that runs **first** in
  review, as a gate before red-team. Walks a fixed checklist (every epic has an issue, the
  dependency graph is acyclic, success criteria are verifiable, upstream includes are wired,
  gates declare type and approvers, all portability sections are present). Verdict:
  `PASS | INCOMPLETE`. Read-only; makes no quality judgments (that is red-team's job).
- **red-team** (`red-team.md`) — Adversarial review with fresh eyes (no access to investigation
  worktrees), run **after** conformance passes. Evaluates completeness, feasibility, risk, gate
  necessity, and upstream dispositions; returns `APPROVE | REVISE | INVESTIGATE-MORE` with
  strengths, severity-tagged concerns and recommendations, and gaps. **Its verdict drives the
  phase transition.** Read-only — the main session writes `reviews/pass-N.md` at presentation and
  updates it in place as concerns are resolved.
- **coordinator** (`coordinator.md`) — Orchestrates EXECUTE. Drives the poured bead DAG to
  completion: on a resume, first sweeps stuck beads (resetting `in_progress`/claimed beads to
  open, never auto-closing); then loops `bd ready` → resolve gates by running their test commands
  → claim → dispatch (spawning the metadata-named subagent, or executing directly) → close.
  Routes code edits to the worktree and bead/plan bookkeeping primary-side. Triggers reconcile
  when all execution beads close, then hands back to the main session — it does **not** close the
  epic, merge, or push.
- **reconciler** (`reconciler.md`) — Updates upstream issues after execution completes and changes
  are pushed. Reads `plan.md`'s Upstream Issues table, verifies each resolving bead is actually
  closed (flags mismatches rather than guessing), then closes `include` issues, comments on
  `partial`, and closes `supersede` with rationale — always referencing the plan ID and commit.
  Reports a closed/commented/skipped/flagged summary.
- **captor** (`captor.md`) — Drafts missing portability-contract files for a plan folder (invoked
  by `/yf-plan capture`, not part of the linear phase flow). Reads current plan state (and, under
  `--retro`, the live session's conversation) and drafts absent files — `index.md`, `context.md`,
  a `## Motivation`, `references/upstream-<N>.md`, `reviews/pass-<N>.md` — for operator review.
  **Never writes files** (the main session does) and never invents reviewer verdicts or tool
  versions.

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
  preferred provider (with a Tavily/Perplexity/WebSearch fallback chain); retrieval is
  API-first — never scraping or link-walking. Inputs: the cluster assignment. Outputs:
  `sources.json` entries (with verbatim quotes and preliminary credibility) and a
  `artifacts/cluster-<name>.md` per cluster. A cluster with no usable sources documents what was
  searched rather than fabricating.
- **triangulate** — Cross-references claims across every cluster via the **triangulator**
  subagent. Scores each source for credibility (domain authority, currency, expertise, bias
  neutrality), flags contradictions, and identifies consensus (3+ independent sources agreeing).
  Inputs: all `cluster-*.md` and `sources.json` (excludes `plan.yaml`). Output:
  `artifacts/triangulation.md` with a confidence level and supporting quotes per finding;
  under-supported findings are marked `[insufficient evidence]`.
- **synthesize** — Builds the narrative report answering each research question via the
  **synthesizer** subagent, working from triangulated findings only. Every factual claim carries
  an inline GFM citation resolving into `sources.md`, backed by a direct quote. Inputs:
  `plan.yaml` questions and `artifacts/triangulation.md` (excludes raw retrieval artifacts).
  Output: draft `Summary.md`.
- **critique** — Red-teams the draft via the **red-team** subagent, deliberately **without**
  `plan.yaml` to prevent confirmation bias. Checks that all claims are cited and quote-backed,
  that credibility scores hold up, and flags logical gaps, source-selection bias, uncited
  "model-knowledge" claims, and unresolved `[uncertain]` tags. Inputs: `Summary.md` and
  `sources.json`. Output: `artifacts/critique.md` — actionable items for the refiner.
- **refine** — Addresses each critique item via the **refiner** subagent, editing `Summary.md`
  for fixes possible from existing sources and creating new `discovered-from` retrieve beads
  (wired into the package step) for gaps needing fresh evidence. `[uncertain]` tags are removed
  only when a claim gains 2+ independent sources scoring ≥ 60; unfillable gaps are noted
  explicitly rather than softened. Inputs: `Summary.md`, `critique.md`, `plan.yaml`.
- **package** — Finalizes via the **packager** subagent: verifies every citation resolves and no
  claim is uncited, cross-checks research questions against the report, authors a d2 structure
  diagram for non-trivial reports, generates `sources.md` and normalizes citation links, updates
  `index.md`, and closes the epic. Ends with a **conservative git handoff** — it reports changed
  files and the proposed commit/push commands but does not commit or push without explicit
  authorization.

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

- **coordinator** (`coordinator.md`) — Drives the research molecule to completion. Runs a
  pre-loop stuck-bead sweep (resetting stranded beads on a resume, never auto-closing), then
  loops `bd ready` → claim → read the bead's `agent`/`context` metadata → dispatch that subagent
  with only its declared context files → record the artifact in `index.md` → close. Feeds each
  agent only its declared context and enforces the epistemic rules. On completion, reports a
  conservative git handoff rather than committing.
- **toolsmith** (`toolsmith.md`) — Creates and validates the scripts declared in `plan.yaml`'s
  `tooling_needed`. Writes PEP 723 Python scripts (topic-specific into `research_dir/scripts/`,
  reusable ones into the skill's own `scripts/`), tests each with `uv run <script> --help`, and
  enforces rate-limit and graceful-failure conventions for API callers. Runs before retrieval so
  its tools are available. Not read-only (produces scripts).
- **retriever** (`retriever.md`) — Gathers sources for **one** cluster (dispatched N-up, one per
  cluster). Sees only `plan.yaml` and its cluster config; excludes other clusters' artifacts.
  Prefers Exa MCP with a documented fallback chain, is strictly API-first (no scraping/link
  walking), and writes `sources.json` entries and `artifacts/cluster-<name>.md` with per-claim
  direct quotes. Not read-only.
- **triangulator** (`triangulator.md`) — Cross-references and credibility-scores the gathered
  sources. Reads all `cluster-*.md` and `sources.json` (excludes `plan.yaml`), runs
  `credibility_scorer.py`, and writes `artifacts/triangulation.md`. Introduces no claims absent
  from the retrieval artifacts — it synthesizes existing evidence only. Not read-only.
- **synthesizer** (`synthesizer.md`) — Writes the narrative `Summary.md` from
  `triangulation.md`, answering each `plan.yaml` question with inline GFM citations and direct
  quotes, tagging single-source and uncertain claims. Excludes raw retrieval artifacts. Not
  read-only.
- **red-team** (`red-team.md`) — Critiques the draft on its own merits, deliberately **excluding**
  `plan.yaml` to avoid confirmation bias. Reads `Summary.md` and `sources.json`, validates
  citations, quote-backing, credibility scores, and bias, and writes `artifacts/critique.md`. An
  evaluate-stance agent, but it does write the critique artifact.
- **refiner** (`refiner.md`) — Works through each critique item: edits `Summary.md` for
  in-source fixes and creates new `discovered-from` retrieve beads for evidence gaps (wiring them
  ahead of the package step). Reads `Summary.md`, `critique.md`, and `plan.yaml`. Not read-only.
- **packager** (`packager.md`) — Finalizes the report and closes the molecule: verifies all
  citations resolve, cross-checks questions, generates `sources.md` and normalizes links, updates
  `index.md`, closes the epic, and reports the conservative git handoff (no auto-commit/push).
  Sees all files in the research directory. Not read-only.
