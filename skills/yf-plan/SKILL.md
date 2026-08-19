---
name: yf-plan
description: >
  Structured planning with beads-tracked execution and upstream issue reconciliation.
  TRIGGER when: /yf-plan invoked, user uses planning-intent language ("let's plan",
  "let's design", "how should we build", "let's architect"), or native plan mode triggers.
  OVERRIDE: replaces EnterPlanMode/ExitPlanMode — never use native plan mode.
user-invocable: true
skill-group: workflows
depends-on-tool: [bd, uv, git]
depends-on-skill: [yf-beads-extra, yf-beads-authoring]
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
  - AskUserQuestion
preflight:
  companion-rule: PLANS.md
  min-bd-version: 1.1.0
  config-basename: .yf-plan.local.json
---

# yf-plan

**OVERRIDE:** Replaces native plan mode. Do not use EnterPlanMode/ExitPlanMode.

**Operator hardening (recommended):** so the model cannot reach for the mechanisms this skill
replaces, deny them in `~/.claude/settings.json` — `EnterPlanMode`/`ExitPlanMode` (native plan
mode), `EnterWorktree`/`ExitWorktree` (this skill runs its own git worktree), the `Task*` tools
and `todoFeatureEnabled: false` (beads is the only task tracker), `disableWorkflows: true`. See
[docs/recommended-settings.md](https://github.com/dixson3/yoshiko-flow/blob/main/docs/recommended-settings.md).

## SKILL_DIR

```bash
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
SKILL_DIR=$(find ~/.claude/skills ~/.agents/skills "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" .claude/skills .agents/skills -maxdepth 1 -name yf-plan -type d 2>/dev/null | head -1)
[ -z "$SKILL_DIR" ] && { echo "ERROR: yf-plan skill directory not found"; exit 1; }
```

All skill-internal paths use `${SKILL_DIR}/` prefix.

## Reference skills

yf-plan is a beads-backed skill. It does not re-document `bd` usage — it relies on three
companion skills and points at them where a `bd` pattern needs explanation:

- **`beads`** — the canonical routine loop (`bd prime`, `ready`, `show`, `claim`, `create`,
  `close`). Baseline, installed by `bd init`.
- **`yf-beads-extra`** — direct-CLI gotchas this skill's commands depend on: issue-type and
  gate semantics, dependency-edge mutation (`bd dep add` is additive; there is no
  `bd update --deps`), defensive `--json` parsing, transactional `bd batch`, and the
  `bd mol pour` output shape (`new_epic_id`, `id_mapping`).
- **`yf-beads-authoring`** — the formula / `mol pour` / coordinator / `coordinate`
  conventions this skill is built on.

When in doubt about a `bd` behavior, consult `yf-beads-extra` rather than inferring from
the snippets below.

## Invocation

- `/yf-plan init` — initialize yf-plan for this project
- `/yf-plan <objective>` — new plan
- `/yf-plan continue [<plan-id>]` — resume open plan
- `/yf-plan capture [<plan-id>] [--retro]` — audit plan folder portability and draft missing contract files; `--retro` also mines the current session's conversation (re-entrant, does not advance status)
- `/yf-plan execute [<plan-id>] [--checkpoint | --autonomous] [--sweep-gates=probe|all]` — begin execution (new session); the autonomy tokens are a per-invocation override of the configured level, and `--sweep-gates` widens the execute-start sweep
- `/yf-plan status [<plan-id>]` — show progress
- `/yf-plan list` — list all plans

## Pre-flight

**Run on every invocation except `/yf-plan init`.** Run the preflight and branch on its
status (it follows the Skill Surface Convention — see the `yf-skill-authoring` skill):

```bash
yf preflight yf-plan --json
```

(The `yf preflight` JSON is a superset of the legacy `plan_manager.py` preflight schema —
same status values and fields — so the branch logic below is unchanged; only the command
moved into the `yf` kernel. See docs/yf/preflight-contract.md.)

- **`ignored`** (operator set `"ignore-skill": true` in `.yf-plan.local.json`): exit
  silently, fall back to native plan mode.
- **`ok`**: proceed to the requested command. On `ok`, preflight also ensures the
  idempotent project scaffold (the `docs/plans` dir + a single `/.yf/` gitignore
  anchor); anything it created is listed in `scaffold_added`. The
  ensure is additive-only and runs once per scaffold version (gated by `scaffold-ensured`
  state) — it will not re-add an anchor an operator later removes. (`instructions` may
  carry a non-blocking `update available` note for `PLANS.md`.)
- **`system_deps_missing` / `bd_not_initialized`**: tell the user to run `/yf-plan init` to
  set up the project. Stop.
- **`rule_missing` / `rule_drift` / `rule_deprecated` / `manifest_*`**: follow the
  `instructions` in the result. The companion rule is installed by the repo installer, so
  these point at `install.sh` (e.g. re-run `install.sh --force` to restore a drifted rule),
  not `init`. Stop.

Config vs state: **config** is operator decision — `ignore-skill`, `plans-root`,
`incubator-root`, `execute.worktree`, `validate-cmd`, `landing-strategy`, `autonomy`,
`sweep-gates`, `max-attempts`, `max-review-cycles` — read by `_read_config()` from
`.yf/plan/config.local.json` > `.yf/plan/config.json` > the legacy root `.yf-plan.local.json`,
**canonical first**, merged key by key. Inspect the resolved value and its winning tier with
`plan_manager.py config-resolve --json`. **State** is runtime cache: the `yf` preflight kernel
writes `.yf/plan/preflight.json`, and the manager's own state (`landing.lock`) also lives under
`.yf/plan/` — both short-name, matching the `yf` binary. `yf migrate` moves legacy → canonical;
preflight does not auto-migrate. *(dixson3/yoshiko-flow#100 delivered both the canonical-first
read and the short-name layout, and is closed; text describing either as pending was stale.)* The companion rule is installed by the repo installer
(`install.sh`) to the scope+surface rules dir (user-scope `~/.<surface>/rules/PLANS.md`,
project-scope `<git-root>/.<surface>/rules/PLANS.md`; `.claude` or `.agents`); preflight
resolves it in precedence order (user/global copy first) and hash-checks it against
`protocols/manifest.json`.

## /yf-plan init

Initialize yf-plan for the current project. Spawn a sub-agent (`Agent` with `subagent_type="general-purpose"`) with this prompt:

```
Run yf-plan init for Claude Code:

1. Run `yf preflight yf-plan --json` and parse the JSON.
   On status "ok", preflight has already ensured the idempotent scaffold (the docs/plans dir
   plus a single `/.yf/` gitignore anchor); `scaffold_added` lists
   what it created. Per-incubator plan roots (`Incubator/<slug>/plans/`) are created lazily.
   The companion rule `PLANS.md` is installed by the repo installer (`install.sh`), not here —
   never write to AGENTS/ and never edit CLAUDE.md.
2. If status is "system_deps_missing" or "bd_not_initialized", return the JSON as-is. Do nothing
   else. (The scaffold is intentionally NOT ensured until the project is ready.)
3. Return JSON: {"status":"ready","actions":<the check's `scaffold_added` array, or []>,"rule":<the check's `rule` object>}
```

Handle the sub-agent result:

- **"ready"**: print actions taken. If the returned `rule.outcome` is not `ok`/`update_available` (e.g. `rule_missing`/`rule_drift`), tell the user the companion rule is missing or drifted and to re-run the repo installer — `install.sh` (add `--force` to clobber a drifted/hand-edited copy); init does not install rules. Then show usage.
- **"system_deps_missing"** or **"bd_not_initialized"**: print the missing items and instructions. Ask: "Would you like to (1) stop and fix the prerequisites, or (2) ignore yf-plan in this project?" If ignore, write `{"ignore-skill":true}` to `.yf-plan.local.json` at the repo root, and ensure `/.yf-plan.local.json` is in `.gitignore`, then exit.

**Rule:** All task tracking uses `bd`. Never use TodoWrite, markdown checklists, or inline task lists.

After editing `protocols/PLANS.md`, refresh the manifest hash:
`uv run ${SKILL_DIR}/scripts/manifest_update.py ${SKILL_DIR}/protocols` (add `--minor`/`--major` for non-patch bumps), and commit the rule + `manifest.json` together.

## Phase Model

```
UPSTREAM --> SCOPE <--> INVESTIGATE --> PLAN --> INTAKE
                                                  |
                                          === session boundary ===
                                                  |
                                              EXECUTE --> RECONCILE --> COMPLETE
```

- SCOPE <-> INVESTIGATE: investigation may revise scope
- PLAN -> SCOPE/INVESTIGATE: draft plan may need more experiments
- PLAN -> INTAKE: only on explicit operator approval

Status values: `scoping | investigating | drafting | review | ready-for-approval | approved | executing | reconciling | complete`

(`ready-for-approval` is the gated pre-approval state reached only when `ready-check` is green —
last red-team `APPROVE` + audit `pass`; approval transitions it to `approved`. This line is the
declared source of truth for the `DRIFT-CHECK.md` `e-status-values` edge — status values used in
`update-status` calls and agent prompts must be a subset of it.)

---

## Phase 0: UPSTREAM DISCOVERY

Runs once per project (persisted to CLAUDE.md), re-validated at start of each new plan.

### 0.1 — Auto-detect

```bash
REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null)
if echo "$REMOTE_URL" | grep -qE 'github\.com'; then
  gh auth status 2>/dev/null && UPSTREAM="github"
elif echo "$REMOTE_URL" | grep -qE 'gitlab\.com|gitlab\.' ; then
  glab auth status 2>/dev/null && UPSTREAM="gitlab"
fi
grep -q "## Upstream Tracking" CLAUDE.md 2>/dev/null && UPSTREAM="configured"
```

### 0.2 — Probe for issues (if no config)

```bash
gh issue list --limit 5 --json number,title,state 2>/dev/null
glab issue list --per-page 5 2>/dev/null
```

### 0.3 — Confirm with operator (ONLY when undetermined)

**Skip this entirely when §0.1 already resolved the upstream** — a detected `## Upstream
Tracking` block in `CLAUDE.md`/`AGENTS.md`, or an authenticated `gh`/`glab` against a matching
remote, *is* the answer. Asking anyway spends an interaction to be told what was just read.

Ask only when detection was genuinely inconclusive: use GitHub Issues, GitLab Issues, Jira,
Linear, or none?

### 0.4 — Persist to CLAUDE.md

```markdown
## Upstream Tracking

- **Source:** github
- **Repo:** <owner>/<repo>
- **Tool:** `gh issue`
- **Notes:** <operator instructions>
```

On subsequent plans, read existing config. Re-validate if remote URL changed.

---

## Phase 1: SCOPE

Planning runs in the `<plan-id>-development` worktree (the planning worktree — the first of
the three named per-phase branches, alongside feature `<plan-id>` and `<plan-id>-execute`).
The plan folder itself stays **primary-side** (under `docs/plans/` or `Incubator/<slug>/plans/`),
so the plan artifacts are readable from the primary checkout while drafting proceeds on the
development branch.

### 1.1 — Check for existing plans

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py list --json-output
```

If match found, ask: continue existing or start fresh?

### 1.2 — Determine plan root (incubator routing)

Before creating the plan directory, decide whether it belongs in a per-incubator root or the vault-default `docs/plans/`.

1. **Auto-detect from CWD.** If `pwd` is inside `Incubator/<slug>/...`, propose `<slug>` as the incubator.
2. **Confirm with the operator — ONLY when auto-detect was ambiguous.** When `pwd` is
   unambiguously inside a single existing `Incubator/<slug>/...`, take that slug and proceed
   without asking; likewise take `docs/plans/` without asking when `pwd` is outside `Incubator/`
   entirely. Both cases have exactly one defensible answer, and the operator can still redirect
   after the fact — the plan folder is a `git mv` away, so the cost of a wrong auto-detect is
   far below the cost of an interaction on every plan.

   Ask when it is genuinely ambiguous: *"Is this plan scoped to an incubator? If yes, which?
   (detected: `<slug or none>`)"* Accept the slug, `none` for `docs/plans/`, or a different
   incubator name. **Always confirm before CREATING an incubator that does not yet exist** —
   that is a new directory in the operator's vault, not a routing choice.
3. **Pass the answer to init.** Use `--incubator <slug>` (or omit for `docs/plans/`).

### 1.3 — Create plan directory

```bash
# Pass --incubator <slug> when the plan is incubator-scoped; omit otherwise.
PLAN_JSON=$(uv run ${SKILL_DIR}/scripts/plan_manager.py init "${objective}" ${incubator:+--incubator "${incubator}"})
plan_id=$(echo "$PLAN_JSON" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get plan_id)
plan_dir=$(echo "$PLAN_JSON" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get plan_dir)
```

Plan dirs land under `Incubator/<slug>/plans/<plan-id>/` when an incubator was named, otherwise under `docs/plans/<plan-id>/`. Numbering is global across all roots.

Creates `${plan_dir}/`, `findings/`, `diagrams/` (d2 diagrams per the `yf-diagram-authoring` skill), `assets/` (attachments, not diagrams), `references/`, `reviews/`, initial `plan.md` with `status: scoping`, the OKF-reserved `index.md` (bundle listing / orientation, replacing the legacy `README.md`) and `log.md` (update history), and `context.md` (tool-inventory snapshot with hostname+date header). Tool detection is best-effort — missing tools are recorded as `not present` and never block init.

### 1.4 — Upstream issue scan

If upstream tracking configured (not `none`):

```bash
gh issue list --search "<objective keywords>" --json number,title,body,labels,state --limit 20 > /tmp/yf-plan-issues.json
uv run ${SKILL_DIR}/scripts/plan_manager.py triage "${plan_dir}" "${objective}" --issues-json /tmp/yf-plan-issues.json
```

Present matches with disposition options: `[include] [exclude] [partial] [supersede] [deferred]`

For <=5 issues, present inline. For >5, direct operator to edit the generated `upstream-triage.md`.

Record decisions in plan.md **Upstream Issues** section.

`triage` also writes `references/upstream-<N>.md` — one file per issue, containing the full (untruncated) body, URL, labels, and state. These files are **regenerated on every re-triage**; operator hand-edits will be clobbered. The 200-char truncation remains in `upstream-triage.md` for readability.

### 1.5 — Scoping

- **Simple** (<=3 questions): ask directly about objective, constraints, investigation needs, scope boundaries, and success criteria. Update plan.md after each.
- **Complex**: generate questionnaire:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py scope "${plan_dir}" "${objective}"
```

Direct operator to fill in `scope-answers.md` and say "answers ready".

### 1.6 — Flush plan.md

Write all scoping decisions. Update status:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py update-status "${plan_dir}" "investigating" -m "N experiments identified"
```

Transition to INVESTIGATE if unknowns exist, PLAN if none.

---

## Phase 2: INVESTIGATE

### Pre-investigation checkpoint

Before spawning sub-agents, write to plan.md:
- List of experiments with questions
- Scoping decisions so far
- Approach hypothesis (if any)

### Dispatch experiments

Spawn a sub-agent per unknown using `Agent` with `isolation="worktree"`, `mode="bypassPermissions"`. Read `${SKILL_DIR}/agents/investigator.md` for the agent's role, output format, and behavioral rules. Prompt structure:

```
Read ${SKILL_DIR}/agents/investigator.md and follow its instructions.

EXPERIMENT: {question}
CONSTRAINTS: {constraints}
PLAN CONTEXT: {scoping decisions and approach hypothesis}
```

Independent experiments run in parallel.

Track via wisp. Capture the wisp id so it can be burned after investigation (§4.7). No per-call
formula staging is needed — `yf preflight` OWNS staging (REQ-YF-PRE-011): it writes this skill's
embedded `formulas/*` into the project `.beads/formulas/` on every preflight, so `bd mol wisp`
just resolves the proto:

```bash
INVESTIGATION_WISP_ID=$(bd mol wisp plan-investigate \
  --var objective="${objective}" --var plan_dir="${plan_dir}" --json \
  | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get new_epic_id)
```

### Post-investigation

After each sub-agent returns:
1. Write finding to `findings/exp-NNN-<slug>.md`
2. Update plan.md Investigation Findings
3. Both writes BEFORE next sub-agent spawns

### Transitions

- Findings invalidate scope -> SCOPE
- Findings sufficient -> PLAN
- Operator can direct: "rethink the scope", "draft the plan"

---

## Phase 3: PLAN

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py update-status "${plan_dir}" "drafting" -m "synthesizing plan"
```

### Synthesize plan

Read `${SKILL_DIR}/agents/planner.md` and follow its synthesis procedure. The planner reads scope answers, findings, upstream triage, and current plan.md, then writes the complete plan document per the structure below.

### plan.md structure

A conformant `plan.md` is the **skeleton** below plus the **Epics-and-Gates grammar** that
follows it. The skeleton's heading set, required fields and section order are the same ones
`seed_plan_md` writes at `init` (REQ-DATA-010/011/015); the grammar is what an author fills the
`## Epics` and `## Gates` sections with.

<!-- >>> BEGIN plan.md skeleton — GENERATED from _shared/plan_template.py by _shared/sync.py; do not edit by hand -->
```markdown
---
type: Plan
okf_spec: OKF-PLAN
id: plan-NNN-user-hash
author: <git-user>
created: YYYY-MM-DD
status: drafting
---
# Plan: <Objective>

**ID:** plan-NNN-user-hash
**Author:** <git-user>
**Created:** YYYY-MM-DD
**Status:** drafting

## Objective
<what and why>

## Motivation
<why this plan exists — the problem, who is affected, what triggered the work.
Required by the portability contract (spec/portability.md REQ-PORT-004).
Either this section or a motivation.md file must be present and non-empty.>

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings
<summary of experiments, key decisions>

## Approach
<chosen approach with rationale>

## Epics
<one `### Epic N: <name>` per epic, each with `- Issue N.M:` bullets — see the grammar below>

## Gates
<the mandatory Start Gate, plus any capability gates and the Reconcile Gate — see the grammar below>

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | <what could go wrong> | high \| med \| low | <what this plan does about it> |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | <what must be true when the plan is done> | <how it is checked> | <issue id(s)> |
```
<!-- <<< END plan.md skeleton -->

**The header metadata is dual-represented** (REQ-DATA-015): the YAML frontmatter block **and**
the `**Field:**` lines, both above the first `## `, both written by one writer from one model.
Do not author one without the other.

**There is no `**Phase log:**` block.** The phase history is the OKF-reserved bundle-root
`log.md` (REQ-DATA-012) — newest-first, grouped under `## YYYY-MM-DD` headings, one
`- <status>: <message>` bullet per entry. `update-status` writes it; never hand-maintain a
phase log inside `plan.md`.

Criterion ids are stable and insertable without renumbering (`SC1`, `SC1b`, `SC2`, …) and the
`Discharged-by` column names the issue(s) that discharge each criterion — the bidirectional
completeness rule (REQ-DATA-018). The Risks table columns are fixed (REQ-DATA-018's sibling
convention: `# | Risk | Severity | Mitigation`).

#### Epics and Gates grammar

The `## Epics` and `## Gates` bodies are the plan's machine-read payload — the extractor and the
pour both parse them, so the grammar is exact:

```markdown
## Epics
### Epic 1: <name>
- Issue 1.1: <description>
- Issue 1.2: <description>
  - depends-on: 1.1
  - resolves-upstream: #142 (include)

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: <name>
- Type: human | auto
- Condition: <what must be true>
- Test: <bash command to verify>
- Blocks: <issue refs>
- Instructions: <how to satisfy>

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step
```

Rules the parsers depend on:

- An issue bullet is `- Issue <N>.<M>[a-z]: <description>` at column 0 of the `## Epics` body;
  its continuation lines are indented two spaces.
- `- depends-on:` and `- resolves-upstream:` are **two-space-indented bullets under their
  issue**, and take a comma-separated list of issue ids / `#<n> (<disposition>)` respectively.
  A `depends-on` value carrying a prose tail is forbidden — the rationale belongs in the body.
- `- Blocks:` takes issue ids, the explicit `epic:<N>` form, or the reserved sentinel
  `reconcile step` (REQ-DATA-019). No wildcards, no prose referents, no trailing parenthetical
  on the sentinel.
- A `- Test:` value is a single bash command on one physical line. It is executed by the gate
  resolver and judged by its **exit code alone**.

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py update-status "${plan_dir}" "review" -m "plan v1 presented"
```

### Review

Two passes, in order. Both agents are read-only (REQ-AGENT-043); the main session acts on their verdicts.

1. **Conformance** — read `${SKILL_DIR}/agents/reviewer.md` and run its mechanical checklist. Verdict `PASS | INCOMPLETE`. On `INCOMPLETE`, resolve the listed gaps and re-run before proceeding — this is a mechanical gate, not a phase transition. It does not produce a `pass-N.md`.
2. **Adversarial** — once conformance is `PASS`, read `${SKILL_DIR}/agents/red-team.md` and perform a structured adversarial review. **Its verdict drives the phase transition** and owns the `pass-N.md` lifecycle below. Under the **autonomous default**, *the main session* resolves the concerns and re-runs the red-team itself, cycling to `APPROVE` **without an operator acknowledgement per cycle** — bounded by `max_review_cycles`. Report the verdict and concerns; do not stop for them. Under `checkpointed`, present them to the operator and wait.

- **APPROVE**: run the portability audit, then the `ready-check` gate (below) before the approval prompt
- **REVISE**: **the main session** addresses the concerns, stays in PLAN, and **re-runs the red-team** (a new cycle → new `pass-(N+1).md`). This is the same autonomy the conformance step above already has — it is a mechanical loop, not a phase transition, and needs no per-cycle acknowledgement. It is bounded: see `max_review_cycles` below.
- **INVESTIGATE-MORE**: return to INVESTIGATE for additional experiments

**The review loop is BOUNDED (`max_review_cycles`, 2.4a).** Before each autonomous
re-run, check the bound — an unbounded self-resolving loop is exactly the shape D-8 forbids:

```bash
RL=$(uv run ${SKILL_DIR}/scripts/plan_manager.py review-loop-check "${plan_dir}" --json) || true
ESCALATES=$(echo "$RL" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get escalates)
```

Exit `3` (`escalates: true`) is **stop class 4** — a mechanical counter threshold, not a
judgement call. Report the verdict's `remediation` and stop the loop. The plan sits in
`review` with its REVISE verdict, which is a **legal state, not a wedge**: REQ-PLAN-030 bars
only `ready-for-approval`.

The counter is `len(glob('reviews/pass-*.md'))` — **not** the `log.md` `review:` bullet count,
which is a different number that can and does diverge. It is **monotonic** (pass files are
never deleted), so it does **not** auto-reset: the operator's only exit is a per-invocation
`--max-review-cycles <n>` raise, echoed to `log.md` per §5.0. That is deliberate — a plan that
has burned `N` review cycles should not silently resume.

**Mandatory re-run after any major-concern revision (REQ-PLAN-030).** A `REVISE` verdict blocks the plan from reaching `ready-for-approval` until a *later* red-team cycle returns `APPROVE`. Readiness keys on the **last recorded** verdict — an earlier APPROVE followed by a REVISE whose revisions were never re-reviewed is **not** ready. Do not solicit approval on a REVISE'd-but-unre-reviewed plan.

**Red-team is read-only** (REQ-AGENT-043). The agent never writes files — the main session does.

**Write the report at presentation (create-on-present).** The moment the red-team presents — *before* anything is resolved — the main session writes `${plan_dir}/reviews/pass-N.md` **and** appends a `log.md` **`- review-pass:`** bullet, as a **single atomic step**. The token is `review-pass:`, **not** `review:` — a `review:` bullet is what a *status transition into the review phase* writes, and counting both against the pass-file total made a correct bundle hard-fail the audit (REQ-PORT-006 as amended by plan-047 Issue 0.9b/2.7). Like `intake:` and `validated:`, `review-pass:` is a recognized non-status token: it never advances `status`. The file captures, verbatim:

- **Verdict** (APPROVE / REVISE / INVESTIGATE-MORE)
- **Strengths**
- **Concerns** — each with severity (high/medium/low) and recommendation, verbatim
- **Missing** sections
- **Gate Assessment** and **Upstream Assessment**
- A **Resolutions** table with one row per concern and status `unresolved`, in this shape
  (renamed from *Operator Resolutions*, which asserted a fixed resolver the autonomous loop
  contradicts; the `actor` column carries the information the old title implied):

  | Concern | Severity | Resolution | Actor | Status |
  | :-- | :-- | :-- | :-- | :-- |
  | C1 … | high | *(filled on resolution)* | `main-session` \| `operator` | `unresolved` |


Writing at presentation makes the verdict portable the instant it exists: a plan parked in `review` with an outstanding REVISE keeps its report on disk, not only in the drafting conversation (#4).

**Pass numbering is fixed at presentation.** `N` is the count of `review-pass:` `log.md` bullets *immediately after* this review's bullet is appended. Because the file and the phase-log line land in the same atomic step, the REQ-PORT-006 invariant `count(reviews/pass-*.md) == count(log.md review-pass: bullets)` holds *while the plan sits in `review`* — exactly the state #4 makes portable.

**Update in place on resolution.** As each concern is resolved — by the main session under the autonomous default, by the operator under `checkpointed` — the main session edits the **same** `pass-N.md`: fill that concern's row in the Resolutions table with the resolution, record who resolved it in the `actor` column, and flip its status from `unresolved` to `resolved`, then set the file's final status when all concerns are resolved. Do **not** create a new file and do **not** append a second `review-pass:` bullet — both were already written at presentation (above).

**Lifecycle: mutable until resolved, then frozen.** The strict "never overwrite" rule relaxes to: the in-flight `pass-N.md` is **mutable** until every concern is resolved, then **frozen**. A frozen pass file is never edited again.

**REVISE loops produce one file per cycle.** On REVISE, the operator addresses concerns and the red-team runs *again* — that is a new review cycle: a new `pass-(N+1).md` is written at the next presentation (with its own `log.md` `review-pass:` bullet), updated in place, then frozen. Each full review cycle yields exactly one file; files are updated in place within a cycle, never replaced across cycles. The REQ-PORT-006 count-equality (`count(pass-*.md) == count(log.md review-pass: bullets)`) is preserved at every step because file and phase-log line are written together at each presentation.

### Portability audit (last step of PLAN)

Once the **last** red-team verdict is APPROVE, run the portability audit — it is a **precondition of the approval prompt** (REQ-PLAN-033), not a post-approval step: the operator is not asked to approve until the audit passes, so approval is consent to an already-verified plan. The audit is idempotent — safe to run multiple times during plan development. It is a **script exit-code check, not a bd gate**. Any `fail` finding blocks reaching `ready-for-approval`; the operator fixes the gaps (or runs `/yf-plan capture`) and re-runs the audit.

```bash
AUDIT_JSON=$(uv run ${SKILL_DIR}/scripts/plan_manager.py audit "${plan_dir}" --json-output)
AUDIT_STATUS=$(echo "$AUDIT_JSON" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get status)
if [ "$AUDIT_STATUS" != "pass" ]; then
  echo "$AUDIT_JSON" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get report
  echo "Plan cannot advance to INTAKE. Remediate the failures above (or run /yf-plan capture), then re-approve."
fi
```

On audit pass, transition to INTAKE. On audit fail, stay in PLAN — the operator remediates, re-approves, and the audit re-runs. This loop is idempotent: the audit reads plan state, produces a verdict, and has no side effects.

**Override.** The operator may bypass the audit with explicit `--force` (e.g., "approve --force"). The override appends a phase-log entry recording the bypass and the operator's stated reason:

```
- YYYY-MM-DD approved: portability audit overridden — reasoning: <operator reason>
```

**Grandfather clause.** Plans whose first `scoping:` phase-log entry is before the activation date (`PORTABILITY_ACTIVATION_DATE` in `plan_manager.py`, also recorded in `spec/portability.md`) have missing scaffolding downgraded to `warn` findings instead of `fail`. Audit passes; operator sees the gaps. New plans (first scoped on/after activation) get hard failures. See `spec/portability.md` for the activation date.

### Ready-for-approval gate (before the approval prompt)

Do **not** solicit operator approval until the plan is genuinely *ready*. Run `ready-check` — it verifies **both** preconditions in one place: the **last recorded** red-team verdict is `APPROVE` (REQ-PLAN-030) **and** the portability audit passes (REQ-PLAN-033). It exits `3` (not ready) or `0` (ready):

```bash
READY_JSON=$(uv run ${SKILL_DIR}/scripts/plan_manager.py ready-check "${plan_dir}" --json) || true
READY=$(echo "$READY_JSON" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get ready)
if [ "$READY" != "True" ]; then
  echo "$READY_JSON" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get reasons
  echo "Plan is not ready for approval. Resolve the reasons above (re-run the red-team on a REVISE, or fix audit findings), then re-check."
fi
```

On **not ready**, stay in PLAN — resolve each reason (a REVISE needs a fresh red-team cycle; an audit fail needs remediation or `/yf-plan capture`), then re-run `ready-check`. On **ready**, transition to `ready-for-approval` and only then present the approval prompt:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py update-status "${plan_dir}" "ready-for-approval" -m "ready-check green — last red-team APPROVE + audit pass"
```

`ready-for-approval` is **not** execute-eligible — it is the gated state that *precedes* the operator's single act of consent. Approval (Phase 4) transitions `ready-for-approval → approved`; `ready-check` re-runs at approval (adjacent to the fingerprint write) so no content edit can slip between a green check and the fingerprint.

### Iteration

- Operator overrides red-team verdict at their discretion
- "what about X?" -> may return to INVESTIGATE or SCOPE
- "change approach to Y" -> revise, stay in PLAN (a major-concern revision requires a red-team re-run)
- "approve" / "looks good" -> only after `ready-check` is green and the plan is in `ready-for-approval`; then advance to INTAKE

---

## Phase 4: INTAKE

On operator approval of a plan already in `ready-for-approval` (Phase 3's ready-check gate). **INTAKE does not pour the molecule** (REQ-PLAN-040): the pour and the
whole bead DAG are deferred to EXECUTE start (Phase 5). INTAKE's job is to freeze the approved
content, commit it locally, land it per the landing strategy, and file the upstream tracking
issue. Execution eligibility across the session boundary is carried by the plan's
`**Fingerprint:**`, not by a pre-poured epic (REQ-PHASE-002).

### 4.1 — Transition `ready-for-approval → approved`

Approval is the operator's single act of consent on an already-verified plan. **Re-run `ready-check` immediately before flipping the status** (REQ-PLAN-066 adjacency) so no content edit slipped between the Phase-3 green check and this transition; only then set `approved`:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py ready-check "${plan_dir}" >/dev/null || { echo "ready-check no longer green — return to PLAN"; exit 1; }
uv run ${SKILL_DIR}/scripts/plan_manager.py update-status "${plan_dir}" "approved" -m "operator approved"
```

### 4.1.5 — Classify & confirm the deliverable class (REQ-PLAN-069a)

Determine whether this plan's **primary deliverable is CI/infra/release configuration**
(`ci-release`) — runner-only-observable behavior that the merged-state validation cannot exercise
— or an ordinary `standard` plan (the default). Run the heuristic, present its suggestion, and on
operator confirmation write the class. The field is fingerprint-excluded (a `**Field:**` header
line above the first `## `, REQ-PORT-040), so writing it here does **not** perturb the §4.2
fingerprint; it is durable across later field-block rewrites because it is a registered dual-write
field (REQ-DATA-015).

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py classify-deliverable "${plan_dir}" --json
# → {suggested_class, signals, confidence, evidence}
uv run ${SKILL_DIR}/scripts/plan_manager.py set-deliverable-class "${plan_dir}" "<ci-release|standard>"
```

**Do NOT prompt here on a `prose-only` suggestion — record `standard` and move on.** This
section's own text already says the confidence signal is *"effectively always `low` here, which
makes it useless for deciding"*: at intake no merged tree exists, so the only non-prose marker
(`.github/workflows/**`) cannot fire, and every suggestion is `prose-only` by construction.
Asking the operator to adjudicate a signal the skill documents as uninformative is the clearest
case of a low-information prompt in the whole flow.

Two things make dropping it safe rather than merely cheaper:

- The class is **re-confirmed at reconcile** (§6.4) once changed paths exist — and that is the
  *only* point where `evidence: path-backed` is reachable, so it is where the decision actually
  has information behind it.
- The completion gate is a **strict no-op** for `standard`, so the default costs nothing.

**Still prompt when `evidence` is `path-backed`** — a `.github/workflows/**` path really
matched, which at intake means the plan folder itself already carries one. That is rare and
genuinely informative, so it earns the interaction.

**Read `evidence`, not `confidence` (REQ-CLI-015).** At intake no merged tree exists yet, so
`--changed` is empty and the `.github/workflows/**` path marker — the only non-prose signal —
cannot fire. `confidence` is therefore **effectively always `low` here**, which makes it useless
for deciding. `evidence` is the field that carries information:

| `evidence` | Means | How to read it |
| :-- | :-- | :-- |
| `path-backed` | a `.github/workflows/**` path matched | strong; the plan really does touch runner-only config |
| `prose-only` | keywords matched in the plan's Epics / Upstream Issues / Success Criteria | **weak** — check the quoted signals before accepting |

A `prose-only` suggestion is a prompt to look, not a verdict. A plan whose *subject* is releases,
signing, or the deliverable class itself will match in ordinary prose — the **self-reference
class**, a structural limit of keyword matching that no blocklist closes. Confirm `ci-release`
only when the plan's *deliverable* is CI/release configuration, not when its *text discusses* one.

The class is **re-confirmable at reconcile** (§6.4) once changed paths are available. When unset the
completion gate is a strict no-op — a `standard` plan is never gated. See
`spec/ci-release-completion.md` for the criterion and the `workflow_dispatch` no-publish test-build
pattern.

### 4.2 — Write the content fingerprint

Approval binds to *reviewed content*. Write a `**Fingerprint:**` header field over the plan's
content sections — the `##` bodies from **Objective** through **Success Criteria**, excluding
the self-trigger set (all `**Field:**` header lines, the phase log, `reviews/`, the Operator
Resolutions tables, and the entire `## Upstream Issues` section) so review/pour bookkeeping
cannot flip the hash mid-execution (REQ-PLAN-034, `spec/portability.md` REQ-PORT-040):

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py fingerprint write "${plan_dir}" --json
```

This is the **stale-approved gate**: a later content edit makes the stored fingerprint no
longer match, and `resume-scan` blocks EXECUTE until a fresh conformance → red-team →
portability cycle re-approves (re-writing the fingerprint), or the operator passes `--force`
(REQ-PORT-041). No `bd mol pour` happens here — the fingerprint is the execution-eligibility
token.

### 4.3 — Auto-commit the plan locally

Commit the approved plan **locally** so a fresh execute session (or a fresh clone after a
crash) inherits a committed base (REQ-PLAN-064). `commit-plan` does a scoped `git add` over an
explicit pathspec (never `git add -A`) — always `${plan_dir}`, plus `.beads/` **only when it is
tracked / not gitignored** (a local-only beads repo gitignores `.beads/`, so it is skipped with a
`beads_note` rather than failing, #71) — a local commit (message `plan-NNN: <phase> —
<objective>`), and **never a push**:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py commit-plan "${plan_dir}" --json
```

`commit-plan` **refuses on the repository's default branch** (`main`/`master`) and fail-closed
on a detached HEAD or empty branch name (REQ-PLAN-065) — the refusal is a JSON verdict, not a
warning. This is the only automated commit yf-plan makes; the remote push stays conservative
and authorized-only (GR-PLAN-003).

### 4.4 — Land per landing strategy

Land the committed plan per the project's `landing-strategy` switch (resolved by
`_resolve_landing_strategy`, from `.yf-plan.local.json`, `main` default):

- **`main` (default)** — merge the plan commit to `main`; plans integrate trunk-based.
- **`feature-branch`** — push/keep the feature `<plan-id>` branch (preserved for later
  operator integration); do **not** merge to `main`.

The landing strategy chosen here also pins the EXECUTE worktree base and the §6.1 merge target
(REQ-PLAN-055) — the two must agree.

### 4.5 — Create the upstream tracking issue

File the single coarse tracking issue for this plan-scale effort — title
`plan-<plan-id> execution tracking` (not the past-tense-glancing "Complete execution of …",
which reads as if the work already shipped, #86) — linking the plan folder and (once poured)
its epic, with any `resolves-upstream` dependency links from the plan's Upstream Issues. Per
the project Upstream Tracking convention (AGENTS.md), file ONE issue per plan, not one per
execution bead.

### 4.6 — Handoff

**No pour happened at intake.** Report: the plan is fingerprinted, committed locally, and
landed per the landing strategy; the upstream tracking issue is filed. Instruct the operator to
run `/yf-plan execute <plan-id>` **in a new session** — the `plan-execute` pour, the bead DAG,
and the start-gate resolution all happen there (Phase 5), across the session boundary. Restore
the primary checkout to a known branch before ending the session (never leave it on a plan
branch — REQ-BRANCH-004).

---

## Phase 5: EXECUTE

By default, EXECUTE runs the plan in an isolated git worktree (`.worktrees/<plan-id>`,
branch `<plan-id>-execute`, cut from a **pinned base**) and lands it via merge-back +
merged-state re-validation in Phase 6. The two address spaces (primary checkout vs. worktree)
and the §5.3→§6.2 flow:

![yf-plan worktree execution lifecycle](spec/worktree-execute-lifecycle.png)

**EXECUTE start owns the pour.** Under the intake-at-execute model the `plan-execute` molecule
is poured here, not at INTAKE. There is exactly **one** pour-once/resume decision point (§5.2),
driven by `resume-scan`: an absent epic is the normal first execution (pour), a present epic is
a resume (do not pour). This single gate replaces the two historically separate guards — the
old INTAKE duplicate-pour guard and the EXECUTE resume guard (REQ-RESUME-004).

On `/yf-plan execute [<plan-id>]` in a new session:

### 5.0 — Resolve autonomy (per-invocation override)

Execution is **autonomous by default**: the coordinator continues to the next ready bead
without operator input, an epic boundary is a **report, not a stop**, and halts are confined
to the declared five-class stop set (REQ-AGENT-064). The operator can override that for one
run with `--checkpoint` (consult at the points autonomy would pass through) or `--autonomous`
(force the default even where config sets `checkpointed`).

**Detection is necessarily prose.** A slash-command path has no `argv` — there is nothing for
a script to parse — so this step follows the `capture --retro` seam: **prose detects the
token, the script validates and resolves it, and the coordinator consumes only resolved
JSON.** Never branch on the token you *think* you read; branch on what `config-resolve`
returned.

```bash
# Only when a token was detected in the invocation; otherwise skip and take the config value.
AUTONOMY_JSON=$(uv run ${SKILL_DIR}/scripts/plan_manager.py config-resolve \
  --autonomy "<checkpointed|autonomous>" --plan-dir "${plan_dir}" --json)
AUTONOMY=$(echo "$AUTONOMY_JSON" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get keys autonomy value)
```

`--plan-dir` makes the script **echo the resolved value into `log.md`**, so a misdetection is
auditable after the fact. The echo records what the script *resolved*, not what the prose
*thought it saw* — those two differing is precisely the misdetection the line exists to
expose. The bullet is inert: it matches neither the `review:` nor the `scoping:` audit token,
so it cannot perturb the REQ-PORT-006 count-equality.

An unrecognised token is **rejected**, not silently ignored: `config-resolve` returns an
`error` key (still JSON on stdout, still exit 0 — REQ-CLI-016) and no override is installed.
A silently-ignored token would be indistinguishable from no token at all, which is the failure
mode the echo exists to prevent.

This risk is identical in kind to today's prose-detected `--force`, and is mitigated the same
way. With no token, the level comes from `flag > config.local > config.json > legacy >
default` — inspect it any time with `plan_manager.py config-resolve --json`, which reports
each key's value **and its source**.

### 5.1 — Select plan

If no ID given:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py list --json-output
```

Filter for plans with status `approved` and a **fresh (non-stale) fingerprint** — a
stale-approved plan (stored `**Fingerprint:**` no longer matches its content) **cannot
execute** until re-approved or `--force` (REQ-PORT-041). No pre-poured epic is required — the
fingerprint, not a poured start gate, is the eligibility token. A plan already in `executing`
(a prior, possibly crashed, session already poured and resolved its start gate) is also a valid
`/yf-plan execute` target — it routes through the resume branch of the gate below.

### 5.2 — Pour-once / resume gate

This section is yf-plan's implementation of the yf-beads-authoring resilience contract
(REQ-ORCH-008 resume detection, REQ-ORCH-009 stuck-bead sweep) **and** the relocated INTAKE
pour. One scan drives the whole decision — pour-once when the epic is absent, resume when it is
present:

```bash
SCAN=$(uv run ${SKILL_DIR}/scripts/plan_manager.py resume-scan "${plan_dir}" --json)
FOUND=$(echo "$SCAN" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get found)
STALE=$(echo "$SCAN" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get stale_approved)
```

`resume-scan` reads the epic from plan.md's `**Epic:**` field (persisted by `record-epic` at
the pour, below), falling back to the `metadata.plan_dir` stamp for plans poured before that
field existed. It reports descendant bead counts, the `stuck` list (`in_progress`/claimed beads
a crash left behind), and `stale_approved`.

**Stale-approved hard gate (REQ-PORT-041).** If `STALE` is `true`, the plan's content changed
since approval (stored `**Fingerprint:**` no longer matches). **Refuse to pour/execute** and
route the operator back through a fresh conformance → red-team → portability cycle (which
re-writes the fingerprint at re-approval). The only bypass is an explicit `/yf-plan execute
--force`, which proceeds **and logs the override** as a phase-log line:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py update-status "${plan_dir}" "${current_status}" \
  -m "stale-approval overridden (--force) — reasoning: <operator reason>"
```

- **`found` is `false`** — no epic yet. Under intake-at-execute this is the **normal first
  execution**: pour the molecule and create the beads (§5.2a).
- **`found` is `true`** — an epic already exists (a prior, possibly crashed, execute session).
  Do **not** pour or create a second epic (the duplicate-epic failure #2 guards against).
  Prompt the operator with `AskUserQuestion`: **Resume** the existing epic (recommended) or
  treat as **New**. On **New**, stop and tell the operator a fresh run requires a fresh pour —
  execute cannot fabricate a second epic. On **Resume**, run the resume path (§5.2b).

#### 5.2a — Pour + create beads (found = false)

**Pour the molecule.** The gate-type formula step yields TWO beads: a task wrapper (key
`plan-execute.start-gate`, what downstream TASK `--deps` reference — never an epic) and the
real gate (key `plan-execute.gate-start-gate`, what `bd gate resolve` must target). See
`yf-beads-authoring` → *Formula gate steps*.

`yf preflight` already staged this skill's embedded `formulas/*` into `.beads/formulas/`
(REQ-YF-PRE-011), so the pour resolves the proto with no per-call `cp`/`rm` staging:

```bash
RESULT=$(bd mol pour plan-execute --var objective="${objective}" --var plan_dir="${plan_dir}" --json)

EPIC=$(echo "$RESULT" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get new_epic_id)
START_GATE=$(echo "$RESULT" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id_mapping "plan-execute.start-gate")
START_GATE_BEAD=$(echo "$RESULT" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id_mapping "plan-execute.gate-start-gate")
```

`new_epic_id` and `id_mapping` are the pour result keys — see `yf-beads-extra` →
*`bd mol pour` output shape*. `json-get` is yf-plan's hardened defensive JSON parser
(`bd` output may be a multi-document array; see `yf-beads-extra` → *`--json` is not always a
single JSON document*). Use `${START_GATE}` for entry-issue `--deps` wiring (tasks only, never
epics) and `${START_GATE_BEAD}` for `bd gate resolve` (below).

**Write the epic↔plan linkage ATOMICALLY, immediately after the pour** (REQ-RESUME-004) — a
crash between the pour and this write must never orphan the epic, so it is the very next step.
Two writes, both keyed on `${EPIC}`:

```bash
# (a) Stamp the epic with its plan_dir so a plan with no **Epic:** field is still
#     findable by resume-scan on a resumed session.
bd update ${EPIC} --metadata "$(jq -nc --arg d "${plan_dir}" '{plan_dir:$d}')" -q

# (b) Record the epic ID in plan.md: an **Epic:** header field plus an inert
#     `- DATE intake: epic <id> poured` phase-log line (matches neither the
#     review: nor scoping: audit regexes). Idempotent.
uv run ${SKILL_DIR}/scripts/plan_manager.py record-epic "${plan_dir}" "${EPIC}"

# (c) Stamp the coarse tracker URL onto the epic as `external_ref` (REQ-PLAN-073, #131).
#     This is the FIRST MOMENT the epic id exists, which is why the stamp lives here and
#     not at §4.5 — see below. Fail-soft: no tracker yet is a normal state, never a pour
#     failure.
uv run ${SKILL_DIR}/scripts/plan_manager.py stamp-tracker "${plan_dir}" --json
```

**Why the stamp is here and not at §4.5 (REQ-PLAN-073).** #131 as filed asks for the stamp
"in Phase 4.5, after creating the tracking issue". That is **impossible**: §4.5 runs at INTAKE,
§4.6 states *"No pour happened at intake"*, and §5.2 owns the pour — §4.5's own text says the
issue links the plan folder and *"(once poured)"* its epic. There is no epic id at §4.5 to stamp.

Without the stamp, a coarse tracker is **structurally invisible** to `upstream.py closable`,
which groups beads by `external_ref`: `yf-plan` files the tracker with a bare `gh issue create`
and records the URL on no bead. Five trackers have gone stale and been closed by hand (#103,
#95, #96, #98, #134). The stamp makes the tracker an **ordinary mapped bead** — no new signal, no
`plan.md`-status reader, and no `plans-root` coupling in either direction.

`stamp-tracker` is **idempotent and fail-soft**: it re-runs harmlessly, refuses to overwrite a
different existing ref, and returns a skip verdict (exit 0) when there is no epic, no tracker, or
no `bd`. It is **forward-looking only** — pre-existing unstamped trackers stay invisible until
backfilled.

**Create beads from plan.md.** Never block a child epic on the start gate: `${START_GATE}` is a
task, and bd rejects a task blocking an epic (`epics can only block other epics, not tasks` —
see `yf-beads-extra` → *Epic blocking rule*). Child epics are containers: create them with
`--parent` only. Gate the epic's **entry leaf issues** (those with no intra-plan predecessor)
on `${START_GATE}`; downstream issues depend on their predecessors and inherit the gate
transitively.

**Every task bead carries `plan_issue: "<id>"` in its METADATA** (REQ-DATA-026 / D-10). This
is what makes the pour checkable at all: EXP-003 measured three plans (006, 007, 036) where no
bead title carries its issue id, leaving the plan↔bead mapping unreconstructable — those three
account for 43 of the 45 apparently-dropped edges purely as an artifact of missing identity.
Metadata is strictly better than a title convention **because titles get rewritten**, and the
comparator prefers it, falling back to a leading title token only for pre-metadata plans.

```bash
# Child epic — parent only, NO start-gate dep (task→epic block is rejected).
EPIC_BEAD=$(bd create "Epic: ${epic_name}" \
  --description="${epic_description}" -t epic -p 2 \
  --parent ${EPIC} \
  --json | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id)

# Entry issue (no intra-plan predecessor) — gate on the start-gate wrapper task.
ISSUE_BEAD=$(bd create "Issue ${issue_id}: ${entry_issue_description}" \
  --description="${issue_detail}" -t task -p 2 \
  --parent ${EPIC_BEAD} --deps "${START_GATE}" \
  --metadata "$(jq -nc --arg i "${issue_id}" --arg p "${plan_id}" \
      '{plan_issue:$i, plan:$p}')" \
  --json | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id)

# Downstream issue — depends on predecessor(s) only; gate inherited transitively.
ISSUE_BEAD=$(bd create "Issue ${issue_id}: ${issue_description}" \
  --description="${issue_detail}" -t task -p 2 \
  --parent ${EPIC_BEAD} --deps "${dependency_beads}" \
  --metadata "$(jq -nc --arg i "${issue_id}" --arg p "${plan_id}" \
      '{plan_issue:$i, plan:$p}')" \
  --json | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id)
```

**Derive the DAG mechanically, do not transcribe it.** `_shared/plan_extract.py` reads
`plan.md` into JSON — epics, issues, edges, gates — and reports anything it cannot parse in
`unparsed[]` rather than degrading. Use it to drive the `bd create` calls above:

```bash
uv run _shared/plan_extract.py "${plan_dir}" --json --strict
```

`--strict` exits **2 (INCONCLUSIVE)**, never 1, on a non-empty `unparsed[]` (REQ-DATA-043):
the extractor did not *see* part of the plan, which is a different claim from the plan being
wrong. Treat it as "this instrument could not read the document" — fix the document (or widen
the reading grammar) rather than hand-transcribing around it, and never let a partially
extracted DAG drive the pour, since a DAG missing an edge silently reorders execution.

**Attach upstream metadata** to issues that resolve an upstream issue:

```bash
bd update ${ISSUE_BEAD} --metadata '{"upstream":"#142","disposition":"include"}' -q
```

**Create capability gates (if any).** Gates are first-class beads (`-t gate`); resolve with
`bd gate resolve`. See `yf-beads-extra` → *Gates*. Create each gate individually (creates need
IDs, cannot be batched).

**Structure the gate at creation — this is what makes the sweep mechanical.** Carry
`gate_type`, `test`, `test_class` and `cwd` as **metadata fields**, so the §5.2b sweep reads
fields instead of regexing prose. Measured on the live corpus: only **33%** of gates yield a
runnable command to a regex, and a `Type:` line appears on **3 of 113** beads. **Without this
structure, do not build the sweep** — a sweep over prose is a sweep that silently sees a third
of its input.

```bash
printf -v GATE_DESC 'Condition: %s\nTest: %s\nInstructions: %s' \
  "${condition}" "${test_cmd}" "${instructions}"

CAP_GATE=$(bd create "Gate: ${gate_name}" \
  --description="${GATE_DESC}" \
  -t gate --parent ${EPIC} \
  --metadata "$(jq -nc \
      --arg gt "${gate_type}" --arg t "${test_cmd}" \
      --arg tc "${test_class}" --arg cwd "${gate_cwd}" \
      '{gate_type:$gt, test:$t, test_class:$tc, cwd:$cwd}')" \
  --json | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id)
```

**Field vocabulary.**

| Field | Values | Meaning |
| :-- | :-- | :-- |
| `gate_type` | `human` \| `auto` | Who may resolve it. **Absent → treat as `human`** — the safe default, since a mis-typed gate must never be auto-resolvable. |
| `test` | shell command, or absent | The command establishing the Condition. Absent → the sweep reports **INCONCLUSIVE**, never FAIL. |
| `test_class` | `probe` \| `build` \| `consent` \| `manual` | What it costs and whether the sweep may run it unattended. |
| `cwd` | `repo-root` \| `worktree` | Which address space the test runs in (§5.3). |

**`probe` means CHEAP AND SELF-CLEANING — not read-only.** A probe **may** create and remove
its own scratch state, and **must** leave none behind **on either exit path**. Anything that
mutates *shared or operator* state is `consent`, never `probe`. This definition is load-bearing
because §5.2b auto-runs the entire `probe` class unattended.

*Worked example.* A gate that creates a `--no-focus` throwaway tab and closes it is testing
against **its own scratch state**, removed on both exit paths → `probe`. The same test writing
to the operator's existing config would be `consent`, however cheap it is: cost is not the
criterion, ownership of the mutated state is.

`build` is cheap-to-classify but expensive to run (the multi-minute class §6.1.5 reserves for
once-per-land); `consent` is a human authorization a green test can never substitute for;
`manual` has no runnable command at all.

Wire all dep-add links in a single `bd batch` call after all gates and issues exist:

```bash
# Accumulate dep-add ops for all gate/issue pairs:
DEP_OPS=""
DEP_OPS+="dep add ${ISSUE_BEAD_1} ${CAP_GATE}\n"
DEP_OPS+="dep add ${ISSUE_BEAD_2} ${CAP_GATE}\n"
# ... one line per dep link ...
printf '%b' "${DEP_OPS}" | bd batch -m "plan-${plan_id} dep wiring"
```

**Rule:** Never call `bd dep add A B` as individual shell commands — always accumulate into `DEP_OPS` and pipe once through `bd batch`. An empty `DEP_OPS` is a no-op (skip the printf). For why (single dolt transaction, atomic rollback) see `yf-beads-extra` → *Bulk intake*.

**Create the reconcile gate and step** — only when upstream issues are incorporated (any
non-exclude disposition):

```bash
RECONCILE_GATE=$(bd create "Gate: Reconcile upstream" \
  --description="Blocks reconciliation until execution complete." \
  -t gate --parent ${EPIC} \
  --json | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id)

RECONCILE_STEP=$(bd create "Reconcile: update upstream issues" \
  --description="Update upstream issues per plan dispositions." \
  -t task -p 1 --parent ${EPIC} --deps "${RECONCILE_GATE}" \
  --metadata "{\"agent\":\"agents/reconciler.md\",\"context\":[\"plan.md\"]}" \
  --json | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get id)
```

**Burn the investigation wisp** (captured in §2 as `INVESTIGATION_WISP_ID`). `--force` is
required — `bd mol burn` otherwise prompts `[y/N]` and defaults to No in a non-interactive
context, silently orphaning the wisp:

```bash
bd mol burn ${INVESTIGATION_WISP_ID} --force 2>/dev/null || true
```

**Resolve the start gate and set status `executing`** (this is a new session — the human start
gate can only be released here, REQ-SESSION-001):

```bash
bd gate resolve ${START_GATE_BEAD}   # the gate-* bead, not the wrapper task ${START_GATE}
uv run ${SKILL_DIR}/scripts/plan_manager.py update-status "${plan_dir}" "executing" -m "start gate resolved"
```

**Create the execution worktree (default-on, D2).** This is the **viability check + opt-out
gate**:

```bash
WT=$(uv run ${SKILL_DIR}/scripts/plan_manager.py worktree ensure "${plan_dir}" --json)
VIABLE=$(echo "$WT" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get viable)
BASE=$(echo "$WT" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get base)
```

- **`viable` is `true`** — `worktree ensure` created `.worktrees/<plan-id>` on branch
  `<plan-id>-execute`, cut from the **pinned base** it reports in `base` (`main` under the
  default strategy, feature `<plan-id>` under `feature-branch` — never ambient HEAD,
  REQ-BRANCH-002), and ensured `/.worktrees/` is gitignored. Surface `base` so the operator
  sees the pinned start-point. The coordinator now runs in worktree mode (§5.3): **code edits
  target the worktree**, while bead tracking and the plan folder stay primary-side (see the
  address-space model below).
- **`viable` is `false`** — a **safe in-place fallback**. Print a one-line reason from the
  verdict (`reason` ∈ `opted-out`, `not-a-git-repo`, `beads-not-initialized`, `dirty-locked`,
  `base-unresolved`, `bd-db-unresolved`) and run the coordinator **in-place exactly as before**
  — no regression in fallback mode. `opted-out` is the operator's `"execute.worktree": false`
  in `.yf-plan.local.json`; `base-unresolved` means the pinned base could not be resolved
  (missing feature branch / indeterminate default); the rest are environment conditions
  (`bd-db-unresolved` is the INV-2 runtime fallback, M4).

**Run the execute-start gate sweep (§5.2c), then** proceed to §5.3 (run coordinator).

#### 5.2c — The execute-start gate sweep (frontloading)

**Placed here — after `worktree ensure`, before §5.3 — and the ordering is forced.** The §5.3
address-space model routes *code* tests to the worktree and *plan-folder* tests primary-side,
and the sweep cannot route a test until the worktree it might run in exists.

**Enumerate** every gate under `${EPIC}` (with metadata — see `coordinator.md` →
*Enumerating gates*, and **pass an explicit `--limit`**: the default page truncates at 50 with
exit 0):

```bash
bd list --type gate --limit 500 --json
```

**Classify** each with the shared evaluate-gate routine (`coordinator.md` → *Evaluating a
gate*), then:

1. **Run the `probe` class — and ONLY the `probe` class — unattended.** Probes are cheap and
   self-cleaning by definition (3.1), so running them costs seconds: exp-003 timed twelve at
   ~3s total. `build` is opt-in via `--sweep-gates=all` (§5.2d), because execute start must not
   inherit the multi-minute cost §6.1.5 reserves for once-per-land.
2. **Batch EVERYTHING ELSE INTO ONE PROMPT**, presented **before any coding work begins**.
   That single prompt is the frontloading: the operator answers once, up front, instead of
   being interrupted at the point each gate happens to sit in the DAG.
3. **Then run everything the failed gates do not block.** A failed gate narrows the runnable
   set; it does not stop the run.

#### 5.2d — `--sweep-gates=probe|all` (default `probe`)

The sweep's class scope is a per-invocation flag, resolved through the same machinery as
§5.0's autonomy token:

```bash
SG=$(uv run ${SKILL_DIR}/scripts/plan_manager.py config-resolve \
  --sweep-gates "<probe|all>" --plan-dir "${plan_dir}" --json)
SWEEP=$(echo "$SG" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get keys sweep-gates value)
```

- **`probe` (default)** — run only the cheap, self-cleaning class. Execute start stays in
  seconds.
- **`all`** — additionally run the `build` class.

`build` is opt-in rather than default because §6.1.5 explicitly reserves the multi-minute suite
for **once per land**. Making it default would move that cost to **every execute start**,
including a resume — paying the land-the-plane price repeatedly for a check whose result is
only actionable once. `consent` and `manual` are **never** run by either setting: neither is a
cost question, and no flag value makes a green test into authorization.

**`gate_type: human` is NEVER auto-resolved, however green its test.** A green test establishes
that a *condition holds*; it can never establish that a *human authorized* something. Auto-
resolving on a green test would have granted publish authorization on **at least three**
historical gates in this repo. `gate_type` absent → treat as `human`, so the failure mode of a
mis-structured gate is a needless prompt, never an unauthorized action.

**A non-command test yields INCONCLUSIVE, not FAIL.** A gate with no runnable `test`, or
`test_class: manual`, has established nothing *in either direction*; calling that FAIL would
manufacture blockers, and calling it PASS would manufacture consent.


#### 5.2b — Resume (found = true)

Do **not** pour or re-resolve the start gate (the prior session already did both). Run the
resume path in order: **re-attach → sweep → loop**.

**Worktree re-attach.** Re-attach the plan's `<plan-id>-execute` worktree (idempotent — it
never creates a second worktree) and **surface** any dirty prior state without resolving it:

```bash
WT=$(uv run ${SKILL_DIR}/scripts/plan_manager.py worktree ensure "${plan_dir}" --json)
# viable=true → action "reattached-worktree"/"reattached-branch"; dirty=true means a crashed
# session left uncommitted changes. Report dirty_files to the operator; never auto-stash/discard.
# viable=false → run in-place this resume (the §5.2a fallback rationale applies).
```

If the verdict is `dirty`, report the `dirty_files` list and pause for the operator (the
*crashed-worktree* mitigation in plan-009 §Risks) — do not auto-resolve. A non-viable verdict
means this resume runs in-place (worktree mode off for the session). On re-attach the `base`
field is `null` — the base was pinned when the branch was first created.

**Tracker stamp (repair-on-resume).** Run the same idempotent stamp on the resume branch, so a
plan whose tracker was filed *after* its pour — or whose stamp failed — is repaired on the next
execute rather than staying invisible forever:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py stamp-tracker "${plan_dir}" --json
```

**Orphan sweep.** Run it **strictly before the ready loop and before any reconcile-trigger
evaluation** — resetting beads keeps the epic non-terminal, so reconcile cannot fire on a
resumed-but-incomplete plan. Follow the procedure in `agents/coordinator.md` → *Resume orphan
sweep*: **reset** each `stuck` bead from the scan (`bd update <id> --status open`, making it
re-workable) and **report** — never auto-close — any bead the sweep cannot positively classify,
leaving the close decision to the operator. No bead is auto-closed: there is no reliable
bd-state signal separating disposable scratch from real `discovered-from` work.

Then proceed to §5.3 (run coordinator).

### 5.3 — Run coordinator

Read `${SKILL_DIR}/agents/coordinator.md` and follow its execution loop. The coordinator
drives the bead DAG to completion, handles capability gates, and triggers reconciliation.

**Autonomy (REQ-AGENT-064).** Under the autonomous default the coordinator **continues to the
next ready bead without operator input**, and **an epic boundary is a report, not a stop** —
report progress and keep going in the same turn. It halts only on the five declared stop
classes: (1) an outward-facing/irreversible write; (2) a capability gate whose `Test:` exits
non-zero; (3) a declared destructive local operation; (4) a mechanical counter threshold
(`yf_attempts >= N`, or `max_review_cycles >= N` in the plan phase); (5) a declared mechanical
check that exits non-zero — validation FAIL, audit/`ready-check` fail, merge conflict, dirty
worktree, or a corrupted bead DB (which routes to `yf-beads-init`). Every class is an exit code
or a counter; none is reachable by prose judgement alone.

**Execution address-space model (worktree mode).** There are **two** address spaces and
operations are explicitly routed (resolves plan-009 red-team C1/M1):

- **Primary checkout (repo root, where `/yf-plan execute` ran).** The coordinator IS the
  main session; its cwd is **not** changed per-plan. Primary-side: the **plan folder**
  (`plan.md`, `reviews/`, phase-log, `findings/`), every `plan_manager.py <verb>
  "${plan_dir}"` call (`plan_dir` is relative to cwd), and all **`bd`** calls (INV-2: the
  shared Dolt DB lives in the primary's `.beads/` and is reached from anywhere).
- **Worktree (`.worktrees/<plan-id>`, branch `<plan-id>-execute`).** Only **project code/build
  artifacts** the plan edits. Reach it via `git -C .worktrees/<plan-id>` or by giving an
  agent-backed bead that worktree as its **cwd**. Only these commits land on `<plan-id>-execute`.

So **bead tracking and plan-folder bookkeeping happen primary-side; only code changes
accumulate on the plan branch.** The coordinator never `cd`s into the worktree. In
fallback (in-place) mode there is one address space — the primary — and all edits land
there as today.

**`uv` inside the worktree.** When running `uv run …` with cwd in `.worktrees/<plan-id>`,
prefix it with `env -u VIRTUAL_ENV` (e.g. `env -u VIRTUAL_ENV uv run …`) so uv resolves the
worktree's own environment instead of an inherited `VIRTUAL_ENV` from the primary checkout.
Do **NOT** follow uv's `--active` suggestion inside a worktree — `--active` targets the
active (primary) venv, the wrong address space.

### 5.4 — Blocked gates

Drain all unblocked work first, and **route around** a blocked gate rather than stopping at it —
reporting is not stopping. Only when no other work can proceed has the DAG genuinely stalled;
that is **stop class 2**, reached by an exit code rather than by judgement. Include gate
condition, test result, and unblock instructions. A gate whose own `Instructions:` define a
deferral mechanism is not a stall — execute it and continue.

### 5.5 — Reconcile gate

Auto-resolves when all execution beads close. Proceed to Phase 6.

---

## Phase 6: RECONCILE

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py update-status "${plan_dir}" "reconciling" -m "post-execution reconciliation"
```

**Phase 6 is reordered (plan-009 INV-4): merge-back FIRST, then validate the MERGED
state, then push.** The old order validated pre-merge, which cannot catch class-(b)
integration regressions (each change individually green, broken when integrated). All
Phase-6 steps run **primary-side** (you cannot check out the base branch in two
worktrees at once — §5.3 address-space model).

**In-place (fallback) mode skips the merge.** If §5.2a fell back to in-place, there is no
execute branch to merge — changes are already on the base. Skip §6.1's merge; §6.1.5 still
validates the working tree before the §6.2 handoff.

### 6.1 — Merge-back (worktree mode)

The merge target is **pinned per landing strategy** (REQ-PLAN-055 / REQ-BRANCH-002), resolved
by `_resolve_landing_strategy` — the same strategy that pinned the §5.2a execute base, so the
two always agree:

- **`main` (default)** — the merge target is `main`; `<plan-id>-execute` lands on trunk.
- **`feature-branch`** — the merge target is the feature `<plan-id>` branch (preserved by
  teardown for later operator integration); `<plan-id>-execute` merges into it, not into `main`.

Acquire the single-machine landing lock, check out the pinned target from the **primary
checkout**, bring it current, and merge the execute branch into it:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py landing-lock acquire "${plan_id}" --json
# exit 3 → held; report the holder and wait. Stale same-host locks self-reclaim.
# MERGE_TARGET = _resolve_landing_strategy():  main → "main";  feature-branch → "${plan_id}"
git checkout "${MERGE_TARGET}"              # restore the primary to the pinned target branch
git pull --rebase                           # bring the target current (other plans may have landed)
git merge --no-ff "${plan_id}-execute"      # --no-ff: auditable merge commit, clean revert (M2)
# defer committing the merge until §6.1.5 validates it (merge leaves it staged/in-progress)
```

`--no-ff` defines the merged tree §6.1.5 validates and keeps the landing as one
revertable commit. The first changes land before any push, so the lock serializes
merge-backs across concurrent plans on this machine. Between phases the primary checkout is
restored to a known branch (the pinned target above) — never left on a plan branch
(REQ-BRANCH-004).

### 6.1.5 — Validate the merged state

Before any push, validate the merged tree. **Layer (a)** — the plan's own Gate `Test:`
commands — runs against the merged checkout in the §5.3 coordinator loop, not here.
This step owns **layer (b)**, the cross-plan safety net, via a 3-tier precedence:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py validate-merged "${plan_dir}" --json
# layer (b) precedence (the `engine` key reports which tier ran). status fail → halt.
```

**Layer-(b) precedence** (first match wins):

1. **`yf-change-validation` engine** — an **approved** repo-root `CHANGE-VALIDATION.md`
   plus a resolvable engine → delegates to `change_validation.py run --tier full` over
   the merged tree (`engine: "change-validation"`). An absent/unresolvable engine, or a
   manifest with `§0 approved: no` (clean `refused`), falls THROUGH to tier 2 — not a fail.
2. **else `validate-cmd`** — the static `validate-cmd` from `.yf-plan.local.json` (Issue
   3.3) as the thin middle fallback (`engine: "validate-cmd"`).
3. **else** — no project suite runs; emit the verbatim cross-plan-not-checked notice
   (`engine: "none"`).

This is a **prose soft-dep**: present → delegate, absent → fallback. NEVER add
`yf-change-validation` to this skill's frontmatter `depends-on-skill` — that is
force-install, the wrong coupling.

- **Fail** → halt with the lock **still held** (so the operator fixes under serialization),
  report the failing command. Do not push.
- **Pass** → commit the merge (`git commit` if the merge is still in progress), then
  **release the lock immediately** — the base is now green and the §6.2 push must not hold
  the global lock across the operator-authorization wait (Issue 3.5):

  ```bash
  uv run ${SKILL_DIR}/scripts/plan_manager.py landing-lock release "${plan_id}" --json
  ```

**Honest scope (plan-009 C2).** When **neither** the engine nor `validate-cmd` is
configured (tier 3), `validate-merged` runs **no** layer-(b) suite at all and emits a
**prominent cross-plan-not-checked notice** — surface it verbatim; never present a bare
green as integration-safe. Layer (a) (the plan's own Gate `Test:` commands, run in the
§5.3 loop) alone cannot catch class-(b) regressions; the engine or `validate-cmd` is the
real cross-plan safety net.

### 6.2 — Push handoff (conservative) + teardown

Push authority stays **conservative** (D4, ratified): everything through merge-back +
local re-validation is automated; the upstream push is **reported and run only on explicit
operator/team-maintainer authorization** (yf-beads-authoring REQ-ORCH-014). This is a
**separate primary-side step that does NOT hold the landing lock** (released at §6.1.5).

```bash
git status   # show the merge commit + changed files under ${plan_dir} and .beads/
# Propose (run only when authorized):
#   bd dolt push && git push     # OMIT `bd dolt push` when `dolt.local-only` is set
```

**Local-only guard (REQ-BINIT-027).** Check `bd config get dolt.local-only` first; when it is
`true`, propose `git push` **alone** and never `bd dolt push` — the repo declares it has no Dolt
replication target. Key the check on the **config flag**, never on whether a remote is present: a
stray remote under local-only is the #160 misconfiguration itself, so a presence-keyed guard
green-lights exactly what it should catch. Upstream *issue* tracking is orthogonal and routes to
`/yf-beads-upstream`.

On an authorized push **rejection** (remote advanced): `git pull --rebase`, then
**re-validate** (re-run §6.1.5) before retrying the push — never push an unvalidated
rebase. After the push is authorized and completed, tear the worktree down:

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py worktree teardown "${plan_dir}" --json
# remove worktree + delete the now-merged `<plan-id>-execute` branch (-d) + prune. Refuses on
# a dirty tree without --force (INV-1); a clean merged plan tears down cleanly. Teardown
# targets ONLY `<plan-id>-execute`; under the feature-branch strategy it PRESERVES the feature
# `<plan-id>` branch for later operator integration (REQ-BRANCH-004).
```

> **Full-auto push is NOT the shipped default.** It remains an operator-configurable
> future option (plan-009 Issue 3.6); until ratified, the push is always reported and
> operator-authorized.

Reconciliation (6.3) references pushed commits, so it proceeds only after the push is
authorized and completed.

### 6.3 — Reconcile upstream issues

Read `${SKILL_DIR}/agents/reconciler.md` and follow its procedure. The reconciler parses plan.md dispositions, verifies execution, updates upstream issues, and reports results.

### 6.4 — Close (the ordered gate chain, terminating in `set complete`)

The close step runs an **extensible ordered gate chain** (REQ-COMPLETE-001) — a sequence of
contract-conformant steps (REQ-COMPLETE-003) governed by ordering constraints rather than by a
step count, terminating in `update-status complete`. The constraints, in force here: observing
steps run above every plan-folder writer (including the `classify-deliverable` block, which
contains the `set-deliverable-class` dual-write); reconcile-verifying steps run after the
reconcile bead closes and before the first destructive step; cascade-close precedes
complete-gate; and `update-status complete` is last and is the sole status writer.

Close the reconcile step, then **cascade-close every container in the plan tree** —
intermediate epics **and the top-level plan molecule** `${EPIC}` — whose children are all
terminal, bottom-up. The cascade **replaces the bare `bd close ${EPIC}`**: leaving intermediate
epics open under a closed molecule is exactly the #73 defect (stale "ready" containers polluting
`bd ready`). A container with any still-open child is a **hard failure** — the cascade exits
non-zero and completion **halts** (never a silent close, never a silent `complete`).

**Reconcile-time re-confirm of the deliverable class (C5, REQ-PLAN-069a).** Before the gate runs,
the merged-tree changed paths are now available (they may have been absent at intake §4.1.5).
Re-run the classifier with those paths and, if the suggestion disagrees with the stored class,
present it and let the operator confirm/override:

**Close-time bundle-conformance audit (ADVISORY, REQ-PLAN-075 / #140) — runs FIRST.** Its
position is the chain's read-before-write constraint (REQ-COMPLETE-001 constraint 1): it must
sit **above the `classify-deliverable` block below**, because that block contains the
`set-deliverable-class` **plan.md dual-write**. Placing it merely above the `log.md` write is
not enough, and placing it at the *bottom* of this block would make it judge artifacts the
close step itself wrote microseconds earlier — a real, previously-observed failure.

```bash
AUDIT=$(uv run ${SKILL_DIR}/scripts/plan_manager.py audit-close "${plan_dir}" --json)
echo "$AUDIT"
# ADVISORY: exits 0 unconditionally and NEVER gates `set complete`. Findings are a
# recommendation to run `/yf-plan capture <plan-id>`, not a halt. Do NOT add a
# `FAIL-LOUD:` banner here — that vocabulary is reserved for halting steps.
```

> **Grandfathering caveat.** The audit's legacy downgrade keys on `log.md`'s `scoping:`
> entries. A `log.md` write that drops them silently promotes `warn` findings to `fail` — which
> is another reason this step reads *before* the close step writes.

**Close-time retrospective report (ADVISORY, 4.4) — runs before the `classify-deliverable`
block below.** Its position is the same read-before-write constraint (REQ-COMPLETE-001
constraint 1) that puts `audit-close` first: it is an **observing** step, and the block below
contains the `set-deliverable-class` plan.md dual-write.

```bash
RETRO=$(uv run ${SKILL_DIR}/scripts/plan_manager.py retrospective-report "${plan_dir}" --json)
echo "$RETRO"
# ADVISORY: exits 0 unconditionally and NEVER gates `set complete`. An ABSENT
# plan-retrospective.md is a legitimate state, not a finding. Do NOT add a `FAIL-LOUD:`
# banner here — that vocabulary is reserved for halting steps.
```

```bash
CHANGED=$(git diff --name-only "${MERGE_TARGET}"...HEAD 2>/dev/null)   # merged-tree paths
uv run ${SKILL_DIR}/scripts/plan_manager.py classify-deliverable "${plan_dir}" \
  $(printf ' --changed %q' ${CHANGED}) --json
# On operator override:
# uv run ${SKILL_DIR}/scripts/plan_manager.py set-deliverable-class "${plan_dir}" "<ci-release|standard>"
```

**This is the one place `evidence` can be `path-backed`.** At intake `--changed` is empty, so a
suggestion there is always `prose-only` (§4.1.5). Here the merged tree exists, so a
`.github/workflows/**` path can actually match — and `evidence: path-backed` with
`confidence: high` is the only combination that carries real weight. A re-confirm that still
reports `prose-only` says the merged tree touched no runner-only config, which is evidence
*against* `ci-release` however many keywords the plan's prose contains.

```bash
# Close the reconcile bead, RE-DERIVED from bd (REQ-PLAN-076) — never from a shell
# variable. `RECONCILE_STEP` is bound only on the §5.2a pour path; the §5.2b resume path
# never re-derives it, and `bd close` with an empty id does not fail — it exits 0 and
# closes a DIFFERENT in-progress bead, then reports success (measured).
RSTEP=$(uv run ${SKILL_DIR}/scripts/plan_manager.py close-reconcile-step "${plan_dir}" --json)
echo "$RSTEP"

# Verify RECONCILE actually reached each row's upstream end state (REQ-PLAN-074, #136).
# HALTING. Runs after the reconcile bead closes and before the first destructive step —
# the only point where §6.3 is done and nothing has been torn down yet.
VERIFY=$(uv run ${SKILL_DIR}/scripts/plan_manager.py verify-reconcile "${plan_dir}" --json)
VERIFY_RC=$?
echo "$VERIFY"
if [ "$VERIFY_RC" -ne 0 ]; then
  echo "FAIL-LOUD: an upstream row did not reach the end state its disposition requires."
  echo "Completion HALTS; do NOT set 'complete'. Run the exact 'gh' commands in the verdict's"
  echo "'remediation' field, then re-run §6.4."
  exit 1
fi
# NOTE: an `inconclusive` verdict exits 0 and does NOT halt — a `gh` outage must never block
# completion on healthy work (R1). It is still printed above; read it.

# Cascade-close all-terminal containers under the plan molecule (incl. ${EPIC} itself).
# "Terminal" = closed, or a resolved/verified gate; an unsatisfied gate is a genuine open
# child (never force-closed). Exit 0 = clean; exit 2 = fail-loud (blocked set non-empty).
CASCADE=$(uv run ${SKILL_DIR}/scripts/close_cascade.py ${EPIC} --plan "${plan_id}" --json)
CASCADE_RC=$?
echo "$CASCADE"
if [ "$CASCADE_RC" -ne 0 ]; then
  echo "FAIL-LOUD: cascade-close reported open children (or a close error) — a container in"
  echo "the plan tree still has a non-terminal child. Completion HALTS; do NOT set 'complete'."
  echo "Resolve the blocked beads reported above, then re-run §6.4."
  exit 1
fi

# Completion gate (REQ-PLAN-069): AFTER cascade-close, BEFORE set complete. No-op for a
# standard/unset deliverable class; for ci-release it fail-louds (non-zero) unless a log.md
# '- validated:' attestation OR an open out-of-tree deferred-validation bead exists.
GATE=$(uv run ${SKILL_DIR}/scripts/plan_manager.py complete-gate "${plan_dir}" --json)
GATE_RC=$?
echo "$GATE"
if [ "$GATE_RC" -ne 0 ]; then
  echo "FAIL-LOUD: completion gate blocked a ci-release plan — its runner-only-observable"
  echo "behavior is unverified. Completion HALTS; do NOT set 'complete'. Follow the gate's"
  echo "'remediation': either attest one green run (attest-validation; see the workflow_dispatch"
  echo "no-publish pattern in spec/ci-release-completion.md) OR file a standalone out-of-tree"
  echo "deferred-validation bead and push it individually upstream, then re-run §6.4."
  exit 1
fi

# Pour fidelity (REQ-DATA-026 / plan-047 Issue 5.5): the beads that were executed must be
# the beads the plan declared. HALTING for THIS plan only (`--plan`), so a historical
# divergence elsewhere in the corpus can never block an unrelated completion.
bd list --all --include-gates --limit 5000 --json > /tmp/yf-beads.json
FIDELITY=$(uv run _shared/pour_fidelity.py /tmp/yf-beads.json "${plan_dir}" \
             --strict --plan "${plan_id}" --json)
FIDELITY_RC=$?
echo "$FIDELITY"
if [ "$FIDELITY_RC" -ne 0 ]; then
  echo "FAIL-LOUD: the poured bead DAG does not match the plan's declared DAG."
  echo "Read the three populations separately — a 'no-mapping' verdict is an identity"
  echo "artifact, a 'dropped' edge means a bead was marked ready BEFORE its declared"
  echo "predecessor. Completion HALTS; do NOT set 'complete'."
  exit 1
fi

# Cascade clean AND completion gate satisfied. Only now set complete.
uv run ${SKILL_DIR}/scripts/plan_manager.py update-status "${plan_dir}" "complete" -m "plan complete"
```

**Filing the deferred-validation bead (option b).** When a real green run is not yet achievable,
file a **standalone, out-of-tree** bead — never a child of `${EPIC}`, or cascade-close fail-louds
on it first — and push it individually upstream (a deliberate per-bead exception to the coarse
upstream convention):

```bash
bd create "Deferred validation: ${plan_id} <deliverable> not yet run green" \
  -t task -p 1 --label deferred-validation --metadata "{\"plan\":\"${plan_id}\"}"
```

The cascade is self-contained (`skills/yf-plan/scripts/close_cascade.py`); `_shared/` extraction
is deferred until a genuine second in-repo runtime consumer exists (REQ-PLAN-067). yf-beads-authoring
carries a doctrine cross-reference to this pattern (Issue 2.5), not a code dependency.

---

## Phase: CAPTURE (manual)

**Invocation:** `/yf-plan capture [<plan-id>] [--retro] [--force]`

Re-entrant and status-agnostic — runs in any phase before intake (`scoping`, `investigating`, `drafting`, `review`). Purely side-effecting on the plan folder; **does NOT advance plan status** and does NOT touch beads.

### Retro mode (`--retro`)

`--retro` extends — does **not** replace — folder-state capture by additionally mining the **current session's conversation** for context that never made it into the plan folder. It is for plans drafted before the portability contract existed, or rescoped mid-draft, where load-bearing context lives only in the drafting conversation.

**Live-session boundary (hard).** `--retro` can only mine the conversation the operator runs it in. It **cannot resurrect a conversation already gone** — run it in a session that still holds the drafting context. Without `--retro`, capture mines folder state only (the default). When the drafting conversation is gone, fall back to plain `/yf-plan capture` (folder-state capture remains the fallback).

Under `--retro` the captor mines the conversation for the seven portability classes: **motivation**, **project environment**, **adjacent-concept glossary**, **reviewer verdicts/resolutions**, **upstream issue bodies**, **scope-change history**, and **runtime/environment assumptions**.

### Flow

1. **Audit.** Run the portability audit and present findings to the operator:
   ```bash
   uv run ${SKILL_DIR}/scripts/plan_manager.py audit "${plan_dir}" --json-output
   ```
2. **Draft missing files.** For each `fail` finding, dispatch the captor agent to draft the missing file from current plan state. Read `${SKILL_DIR}/agents/captor.md` and follow its procedure. The captor reads `plan.md`, `findings/`, `upstream-triage.md`, phase log, and (for upstream references) runs `gh issue view <N>`; it returns draft content. **When `--retro` is set, also pass the current conversation** so the captor mines it for the seven portability classes above (folder state still takes precedence; the conversation only fills gaps). **Captor never writes files** — the main session does.
3. **Operator review.** Present each draft in full to the operator before writing. Never overwrite an existing file without `--force`.
4. **Write.** On operator approval, write each file. Re-run the audit to confirm progress.

### Rules

- `/yf-plan capture` does not call `update-status`. Plan status is unchanged.
- No bead mutations. No molecule pour.
- Existing files are preserved unless the operator passes `--force`.
- If no findings are `fail`, report "already portable" and exit.
- `--retro` mines the **current** session only. It never claims to recover a conversation that is gone; folder-state capture is the fallback.

---

## Commands

### /yf-plan continue [<plan-id>]

1. If plan-id given: read its plan.md, resume at current phase
2. If no argument, one open plan: auto-select
3. If multiple: present choices
4. Fuzzy-match objective text if ambiguous

plan.md is self-contained for cold resume.

### /yf-plan list

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py list
```

`list` renders a `⏸ PARKED` tag on any **parked** plan — approved but never executed
(status `approved` with a present-and-fresh fingerprint, REQ-PLAN-068). The `--json-output`
form carries a `parked` boolean per plan.

### /yf-plan status [<plan-id>]

Show plan.md header + `bd show <epic-id> --json` + bead progress.
Without plan-id: show all plans with bead counts.

**Parked-plan nudge (#86).** After the per-plan progress, surface parked plans (approved but
not executed) so an intake'd-but-unexecuted plan is never silently forgotten:

```bash
PARKED=$(uv run ${SKILL_DIR}/scripts/plan_manager.py parked --json)
COUNT=$(echo "$PARKED" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get count)
```

If `count > 0`, print: `N plan(s) approved but not executed — run /yf-plan execute <id>.`
listing each parked plan id. A parked plan is distinct from a **stale-approved** one (which
needs re-review, not execution); the two tags are mutually exclusive.

### Land-the-plane parked check

On a land-the-plane / session-close gate, enumerate parked plans and surface the same nudge,
so an approved-but-unexecuted plan is caught before the session ends. This is a **portable,
documented script-verb step** — never a harness hook or scheduler:

```bash
PARKED=$(uv run ${SKILL_DIR}/scripts/plan_manager.py parked --json)
COUNT=$(echo "$PARKED" | uv run ${SKILL_DIR}/scripts/plan_manager.py json-get count)
# COUNT > 0 → report: "N plan(s) approved but not executed — run /yf-plan execute <id>."
```

## Retrospective emit (`plan-retrospective.md`)

Every stop and every deviation is recorded, so the corpus that later analysis reads is
built as the work happens rather than reconstructed afterwards. **Emit-only here**:
this skill writes entries; measurement, adjudication and the frontloading consumer are
out of scope (a consumer built today would read an empty corpus).

```bash
uv run ${SKILL_DIR}/scripts/plan_manager.py retrospective-append "${plan_dir}" \
  --kind stop --stop-class <1-5> \
  --asked "<what the operator was asked, verbatim>" \
  --answered "<what they answered, verbatim>" \
  --frontloadable "<yes|no|partial>" \
  --detected-by "<self-report|operator|mechanical-check>" \
  --evidence "<the command + output behind any state claim, or 'unverified'>" \
  --json
```

`--detected-by` and `--evidence` are the two fields that make an entry trustworthy.
`evidence` defaults to the literal `unverified` rather than to blank, so an
unsubstantiated entry is **self-identifying** instead of merely quiet.

### Write sites

Every stop class has at least one site here, so the stop set and the write-site list are
derivable from each other:

| Site | Kind | Stop class |
| :-- | :-- | :-- |
| The coordinator's blocked-gate halt (`coordinator.md` → *Blocked gates*) | `stop` | 2 |
| §3 review resolution — each concern resolved autonomously | `deviation` | — |
| `review-loop-check` escalation (§3, `max_review_cycles`) | `stop` | 4 |
| `yf_attempts >= N` escalation (coordinator step 6a) | `stop` | 4 |
| Portability `audit` / `ready-check` failure | `stop` | 5 |
| §5.2 resume — a stuck-bead sweep or a **dirty worktree** | `stop` | 5 |
| §6.1.5 `validate-merged` FAIL, or a §6.1 merge conflict | `stop` | 5 |
| §6.4 chain halt — `verify-reconcile`, cascade-close, completion gate | `stop` | 5 |
| A destructive local operation requiring confirmation | `stop` | 3 |
| **Every `--force` override** (stale-approval, audit bypass) | `deviation` | — |

A `--force` override already logs a reason to `log.md`; mirror that reason into
`--asked`/`--answered` so the retrospective and the log agree.

**Stop class 1 has NO write site, and that is the whole of the exclusion.** Class 1 is
"a declared outward-facing or irreversible write" — and *every* instance of it in this skill
is a **consent gate by design**: the §6.2 `git push` / `bd dolt push` handoff, the §4.5
`gh issue create` for the coarse tracker, and the §6.4 `closable` proposal of
`gh issue close`. In each case the operator is asked because an outward-facing write
genuinely requires authorization, not because the system failed to anticipate something.

Recording those as stops would pollute the corpus with precisely the interactions that
should never be optimized away — and a later consumer mining for "stops to frontload" would
dutifully propose removing them. So the class-1 row is empty **by construction**, not by
omission: if a class-1 stop ever arises that is *not* a designed consent gate, it belongs in
the table above.

*(The plan's SC3 names only "§6.2 push consent" as this exception. That understates it —
`gh issue create` and `gh issue close` are the same class for the same reason. The exception
is the category, not the one site.)*

**The `deviation` kind is not a stop at all.** It records a defect that did *not* halt the
run — a wrong claim, a missed check, a resolution that over-stated what it verified. Those
rows carry no `stop_class`, which is why the two lists above are not identical.

## Markdown output convention

Every markdown artifact this skill writes (`plan.md`, `index.md`, `context.md`,
`findings/*.md`, `reviews/*.md`, `upstream-triage.md`) is plain **GFM** — never Obsidian
`[[wikilinks]]` or `![[embeds]]`. Use GFM links (`[text](path)` / `[text](file.md#anchor)`)
and GFM tables with explicit alignment markers (`:--` left, `:-:` center, `--:` right) and
variable, content-sized column widths (never fixed-width padding). Lint each generated `.md`
with the `yf-markdown-lint` authoring subset (`ML001,ML002,ML005,ML006,ML007,ML008`) and resolve any
violation before handoff.
