# SPEC — Beads Authoring (`yf-beads-authoring`)

> **Status: DRAFT (primed).** Per-skill SPEC for the beads-skill authoring conventions
> (currently `beads-authoring`, renamed to `yf-beads-authoring` by the plan-010 rename). Operator
> to review/edit. Composed by the root macro `SPEC.md` §4 under spec key **BAUTH**. This is the
> requirement-numbered layer; it **references** the existing topical design docs under `spec/*.md`
> rather than restating them.

## 1. Purpose & scope

`yf-beads-authoring` is the conventions skill for **building** Claude Code skills that orchestrate
work through beads (`bd`): how to author a `.formula.toml`, run the `bd mol pour` lifecycle, attach
agent metadata, fan out dynamically, write the coordinator dispatch loop and its resilience
contract, and implement a `coordinate` subcommand with gate auto-detection. It is design guidance
for skill authors — not a runtime tool. `bdplan`/`bdresearch` (→ `yf-plan`/`yf-research`) are the
in-repo worked examples.

**In scope:** formula authoring + right-sizing, the stage/pour/remove formula lifecycle, post-pour
agent-metadata wiring, dynamic fan-out, the coordinator loop, the coordinator resilience contract
(resume detection, stuck-bead sweep, stale-run threshold, blocked-gate draining, discovered-work
re-entry, completion/git handoff), and the `coordinate` subcommand.

**Out of scope:** routine `bd` CLI use (the `beads` skill); direct-CLI gotchas and `--json`
parsing (`yf-beads-extra`); general skill layout/token rules (`yf-skill-authoring`); issue storage
(that is `bd`). `user-invocable: false` — this skill is conventions, never directly invoked.

## 2. Requirements (`REQ-BAUTH-NNN`)

### 2.1 Structure & self-location (see `spec/structure.md`)

- **REQ-BAUTH-001** *(testable)* a beads-backed skill shall resolve its own directory at runtime
  via the `SKILL_DIR` find idiom that includes the real `.agents/skills` path (not only the
  symlinked `.claude/skills`), because BSD `find` does not follow a symlinked start path; all
  skill-internal paths use the `${SKILL_DIR}/` prefix. (`spec/structure.md` REQ-STRUCT-001.)
- **REQ-BAUTH-002** formulas (`formulas/*.formula.toml`) shall define *what work exists and how it
  connects* (the DAG); agent files (`agents/*.md`) shall define *how to execute* a step; the two
  are not conflated. (REQ-STRUCT-002.)
- **REQ-BAUTH-003** SKILL.md shall own orchestration (prerequisites, scoping, planning, pour,
  handoff, coordinate); per-step execution lives in agent files. Multi-session skills shall hand
  off to a `coordinate` subcommand run in a new session rather than continuing inline after pour.
  (REQ-STRUCT-004, REQ-STRUCT-005.)

### 2.2 Formula authoring (see `spec/formulas.md`)

- **REQ-BAUTH-010** *(testable)* a `.formula.toml` shall be bundled with its consumer skill
  (`<skill>/formulas/`), staged transiently into `.beads/formulas/` only during pour, then removed
  — keeping the source of truth in the skill while satisfying `bd`'s fixed formula search path.
  (REQ-STRUCT-003.)
- **REQ-BAUTH-011** *(testable)* a `type = "gate"` step shall be treated as pouring to **two**
  beads, both surfaced in `id_mapping`: `<formula>.<step-id>` (a `task` wrapper, `Begin: …`, the
  key downstream `needs`/`--deps` reference) and `<formula>.gate-<step-id>` (the actual `gate`, the
  key `bd gate resolve` targets). (REQ-FORMULA-001; cross-ref `yf-beads-extra` REQ-BEXTRA-CLI-007.)
- **REQ-BAUTH-012** *(testable)* a formula's `[[steps]]` shall encode only the **stable, declared
  shape** — work that always exists at pour time and always wires identically; dynamic structure
  (per-run epics, fan-out, runtime gates) is injected post-pour, wiring *beside* declared edges,
  never rewriting or removing one (the right-sizing test). (REQ-FORMULA-002.)
- **REQ-BAUTH-013** formulas shall stay flat — no step nests another step as a structural parent —
  honoring bd's rule that a task cannot block an epic. (REQ-FORMULA-003; cross-ref
  `yf-beads-extra` REQ-BEXTRA-CLI-005.)
- **REQ-BAUTH-014** *(testable)* dynamic fan-out shall use the hybrid pattern: pour the fixed
  skeleton, then inject N dynamic beads (`bd create --parent --deps`) and batch their downstream
  edges (`bd batch`). (REQ-FORMULA-004.)
- **REQ-BAUTH-015** *(testable)* a formula shall be validated with `bd mol pour <name> --dry-run`
  before wiring the full pipeline. (REQ-FORMULA-005.)

### 2.3 Metadata & coordinator (see `spec/orchestration.md`)

- **REQ-BAUTH-020** *(testable)* agent wiring shall be attached **post-pour** via
  `bd update --metadata` carrying `agent` (skill-relative path, loaded as `${SKILL_DIR}/${agent}`)
  and `context` (work-dir files); `[steps.metadata]` in TOML is not propagated by pour, step
  `description` is. (REQ-ORCH-001.)
- **REQ-BAUTH-021** *(testable)* metadata JSON shall be built with `jq -nc --arg`, never shell
  interpolation into a `--metadata '{...}'` string; consumer-specific keys are namespaced
  (`<skill>_<field>`) or `x_`-prefixed. (REQ-ORCH-002, REQ-ORCH-003.)
- **REQ-BAUTH-022** *(testable)* the dispatch loop shall live in `agents/coordinator.md` and drive
  `bd ready → claim → read metadata (defensive JSON) → load agent file → read context → spawn
  subagent → close`, terminating on `bd ready` empty — **not** on the initial bead set closing — so
  `discovered-from` beads created mid-run execute in the same session. (REQ-ORCH-004, REQ-ORCH-013.)
- **REQ-BAUTH-023** all in-skill task tracking shall use `bd` — never TodoWrite, markdown
  checklists, or inline lists; discovered sub-work creates beads with
  `--deps discovered-from:<parent-id>`. (REQ-ORCH-007.)

### 2.4 Coordinator resilience contract (see `spec/orchestration.md` → *Resilience contract*)

- **REQ-BAUTH-030** *(testable)* before pouring/creating an epic, a re-invokable coordinator shall
  detect an existing epic for the same work unit and resume it — never pour a second — via a
  durable pointer (epic ID in the skill's work artifact) with a metadata fallback (epic stamped
  with its work-dir at pour). (REQ-ORCH-008.)
- **REQ-BAUTH-031** *(testable)* on resume, **before the ready loop and before evaluating any
  terminal/auto gate**, the coordinator shall reset each `in_progress`/claimed durable bead to
  `open` and **report — never auto-close** any bead it cannot positively classify. (REQ-ORCH-009.)
- **REQ-BAUTH-032** the resume sweep MAY auto-close ephemeral (vapor-phase) operational beads but
  MUST NOT auto-close durable (liquid-phase) work beads; the line is the formula `phase` field.
  (REQ-ORCH-010.)
- **REQ-BAUTH-033** a coordinator re-triggered on an interval shall treat a prior run whose epic
  age exceeds **2× the interval** as dead (close the stale epic, start fresh); one-shot
  operator-invoked skills skip this. (REQ-ORCH-011.)
- **REQ-BAUTH-034** *(testable)* gate-type beads encountered in the loop shall be handled in place
  (`bd gate resolve` on pass, mark blocked on fail), and the coordinator shall **drain all
  unblocked work before reporting blocked gates** — never halt at the first blocked gate.
  (REQ-ORCH-012.)
- **REQ-BAUTH-035** the run is complete when `bd ready` is empty **and** no resettable stuck beads
  remain; the coordinator then resolves/verifies terminal auto-gates, closes the epic, and performs
  the git handoff **per the project's git authority** — conservative default: report changed files
  + proposed commit / `bd dolt push` / push commands; commit or push only under explicit operator
  or team-maintainer authority. (REQ-ORCH-014.)

### 2.5 Coordinate subcommand & gate auto-detection (see `spec/orchestration.md`)

- **REQ-BAUTH-040** *(testable)* the `coordinate` subcommand shall auto-detect gates via
  `bd gate list --json` scoped to this skill's poured epics: 0 open → warn/exit; 1 → auto-select,
  resolve, begin; N → present via `AskUserQuestion`, resolve the selected gate, begin. (REQ-ORCH-005.)
- **REQ-BAUTH-041** gate resolution shall use `bd gate resolve <gate-id>` (or `bd close`); there is
  no `bd gate approve` in bd 1.0.5. (REQ-ORCH-006; cross-ref `yf-beads-extra` REQ-BEXTRA-CLI-003.)

## 3. Interfaces

- **CLI / scripts:** none owned by this skill — it is authoring guidance. It prescribes that a
  consumer skill extract multi-step `bd` orchestration into its own `scripts/<skill>_manager.py`
  (worked examples: `plan_manager.py`, `research_manager.py`) and bundle formulas under
  `<skill>/formulas/`. It ships `agents/reviewer.md`, a read-only anti-pattern auditor run over a
  beads-backed skill's `SKILL.md` + `agents/*.md` + `spec/*.md` + `formulas/*.toml`.
- **Companion rule:** none — `user-invocable: false`, no always-loaded trigger rule.
- **Config / state:** none of its own. After the rename, a consumer skill's config/state become
  `.yf-<skill>.local.json` / `.yf/yf-<skill>/` per macro `REQ-YF-PRE-004`; this skill carries no
  per-repo config.

## 4. Guardrails (`GR-BAUTH-NNN`)

- **GR-BAUTH-001** *Drift:* restating the `bd` CLI gotchas (gate verbs, dep mutation, `--json`
  shape, `bd batch`, pour output). *Rule:* those belong to `yf-beads-extra`; this skill **cites**
  them. *Why:* one source of truth per `bd`-version-sensitive fact.
- **GR-BAUTH-002** *Drift:* over-encoding a formula with dynamic structure. *Rule:* `[[steps]]`
  hold only the stable declared shape; dynamic edges wire in post-pour beside declared ones
  (REQ-BAUTH-012). *Why:* a formula whose declared `needs=` edge must be rewritten at intake is
  wrong-sized.
- **GR-BAUTH-003** *Drift:* a coordinator auto-closing ambiguous or durable work on resume, or
  auto-committing/pushing on completion. *Rule:* reset (never auto-close) durable stuck beads,
  report the unclassifiable, and keep git authority conservative (REQ-BAUTH-031, REQ-BAUTH-035).
  *Why:* the operator owns disposition and the remote.

## 5. Verification

- The formula/coordinator/resilience requirements are auditable items in `agents/reviewer.md`,
  which walks them read-only over a beads-backed skill and returns findings. The right-sizing
  invariant (REQ-BAUTH-012) is checked by `--require-step` plus the post-pour "never rewrites a
  declared edge" test in `spec/formulas.md`. The gate-step two-bead shape (REQ-BAUTH-011) and the
  pour output shape are exercised by `bd mol pour <name> --dry-run` against the consumer skill's
  formula. Each *(testable)* item is the anchor a later plan-010 Epic 6 integration test names.

## 6. References

- `skills/yf-beads-authoring/SKILL.md`; `skills/yf-beads-authoring/spec/structure.md`,
  `spec/formulas.md`, `spec/orchestration.md`; `skills/yf-beads-authoring/agents/reviewer.md`.
- `protocols/` — none (no companion rule).
- Root `SPEC.md` §4 (BAUTH) and `GUARDRAILS.md`.
- Sibling specs: `yf-beads-extra` (BEXTRA) for the `bd` CLI gotchas this skill cites; worked
  examples `yf-plan` (PLAN) and `yf-research` (RESEARCH).
