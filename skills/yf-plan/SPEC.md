# SPEC — Plan (`yf-plan`)

> **Status: Active.** Per-skill SPEC for the planning skill. The `yf-plan` rename is complete and the
> skill is shipped; this SPEC tracks the live behavior. Requirements use RFC-2119 "shall"; composed
> by the root `SPEC.md` macro spec.

## 1. Purpose & scope

`yf-plan` is the structured planning skill: it turns an objective into a portable, versioned plan
folder and a beads-tracked DAG of execution work, with adversarial review gates and upstream-issue
reconciliation. It **replaces native plan mode**. Task tracking is always `bd` — never `TodoWrite`,
markdown checklists, or inline lists.

**In scope:** the phase pipeline (scope → investigate → plan → intake → execute → reconcile →
complete), the plan-folder portability contract, capability/start/reconcile gates, worktree-based
execution with merge-back, crash-resume, and upstream triage/reconciliation.

**Out of scope:** running the resulting code (the harness/coordinator does), issue storage (that is
`bd`), and research pipelines (that is `yf-research`).

## 2. Requirements (`REQ-PLAN-NNN`)

### 2.1 Lifecycle & phases (see `spec/phases.md`)

- **REQ-PLAN-001** *(testable)* a plan shall carry a `status` from
  `scoping | investigating | drafting | review | approved | executing | reconciling | complete`,
  advanced only via `plan_manager.py update-status`, which appends a phase-log line.
- **REQ-PLAN-002** the phase machine shall be `UPSTREAM → SCOPE ↔ INVESTIGATE → PLAN → INTAKE →
  (session boundary) → EXECUTE → RECONCILE → COMPLETE`; there is **no EXECUTE→PLAN transition**.
- **REQ-PLAN-003** *(testable)* every invocation except `init` shall run the preflight
  (`yf preflight yf-plan`) and branch on `ok | ignored | system_deps_missing | bd_not_initialized | rule_*`.

### 2.2 Plan folder & portability (see `spec/portability.md`, `spec/data.md`)

- **REQ-PLAN-010** *(testable)* `init` shall create a plan folder under `docs/plans/<plan-id>/` (or
  `Incubator/<slug>/plans/<plan-id>/`) with `plan.md`, `README.md`, `context.md`, `findings/`,
  `diagrams/`, `assets/`, `references/`, `reviews/`; plan-id numbering is global across roots.
- **REQ-PLAN-011** *(testable)* `plan.md` shall contain the required portability sections
  (Objective, Motivation, Upstream Issues, Investigation Findings, Approach, Epics, Gates, Risks &
  Mitigations, Success Criteria); `audit` shall return `pass|fail` and block INTAKE on `fail`.
- **REQ-PLAN-012** a plan folder shall be self-contained — a cold reader in another repo can
  understand it from the folder alone (the portability contract).

### 2.3 Scope & investigate

- **REQ-PLAN-020** SCOPE shall capture objective, constraints, investigation needs, boundaries, and
  success criteria into `plan.md` (inline for ≤3 questions; via `scope-answers.md` otherwise).
- **REQ-PLAN-021** INVESTIGATE shall dispatch one sub-agent per unknown (worktree-isolated), writing
  each result to `findings/exp-NNN-*.md` **before** the next sub-agent spawns.

### 2.4 Plan & review (see `spec/agents.md`)

- **REQ-PLAN-030** *(testable)* Review shall run two passes in order: **conformance** (mechanical,
  `PASS|INCOMPLETE`, a gate) then **adversarial red-team** (`APPROVE|REVISE|INVESTIGATE-MORE`, which
  drives the transition). Both agents are **read-only**; the main session writes files.
- **REQ-PLAN-031** *(testable)* at red-team presentation the main session shall write
  `reviews/pass-N.md` **and** append the phase-log `review:` line atomically (create-on-present),
  preserving `count(reviews/pass-*.md) == count(phase-log review: lines)`.
- **REQ-PLAN-032** a `pass-N.md` shall be mutable until all concerns resolve, then frozen; each
  full REVISE cycle yields exactly one pass file.
- **REQ-PLAN-033** *(testable)* the portability `audit` shall run as the last PLAN step; INTAKE
  proceeds only on `pass` (or explicit `--force`, which logs a phase-log override).

### 2.5 Intake (see `spec/cli.md`, `beads-extra`)

- **REQ-PLAN-040** *(testable)* INTAKE shall pour the `plan-execute` molecule once (duplicate-pour
  guard via `resume-scan`), persist the plan↔epic linkage (epic `metadata.plan_dir` + `plan.md`
  `**Epic:**` field), and create the bead DAG.
- **REQ-PLAN-041** child epics shall be created `--parent` only (never blocked by the start-gate
  task — a task→epic block is rejected); entry leaf issues shall depend on the start gate;
  downstream issues inherit it transitively.
- **REQ-PLAN-042** all dependency-edge wiring shall be a single `bd batch` call, never individual
  `bd dep add` shell commands.

### 2.6 Execute: worktree, resume, gates (see `spec/phases.md`, plan-009/plan-004)

- **REQ-PLAN-050** *(testable)* EXECUTE shall default to an isolated worktree
  (`.worktrees/<plan-id>`, branch `<plan-id>`); a non-viable verdict falls back to in-place
  execution without regression.
- **REQ-PLAN-051** code edits shall target the worktree while bead tracking and plan-folder
  bookkeeping stay primary-side (the two-address-space model).
- **REQ-PLAN-052** *(testable)* on resume, the guard shall detect an existing epic
  (`resume-scan`), re-attach the worktree, run the orphan sweep (reset stuck beads to `open`;
  report, never auto-close, the unclassifiable) **before** the ready loop, and never re-resolve an
  already-resolved start gate.
- **REQ-PLAN-053** capability gates shall be first-class `-t gate` beads resolved with
  `bd gate resolve`; blocked gates are reported only after all unblocked work is drained.

### 2.7 Reconcile & land (see `spec/phases.md`)

- **REQ-PLAN-060** *(testable)* RECONCILE shall **merge-back first, then validate the merged state,
  then push**: acquire the landing lock, `git merge --no-ff <plan-id>`, run merged-state validation
  (gate `Test:` commands + configured `validate-cmd`); on fail, halt with the lock held.
- **REQ-PLAN-061** when `validate-cmd` is unset, validation shall emit a prominent
  cross-plan-not-checked notice (never present a bare green as integration-safe).
- **REQ-PLAN-062** push authority shall be **conservative** — report the handoff and push only on
  explicit operator/team-maintainer authorization; the landing lock is released before the push
  wait.
- **REQ-PLAN-063** RECONCILE shall update upstream issues per `plan.md` dispositions (the
  reconciler agent), then close the reconcile step + epic and set status `complete`.

### 2.8 Capture (manual)

- **REQ-PLAN-070** `capture` shall be re-entrant and status-agnostic (pre-intake phases only), purely
  side-effecting on the plan folder, advancing no status and touching no beads; `--retro`
  additionally mines the current session's conversation for the portability classes.

## 3. Interfaces

- **CLI / scripts:** preflight is `yf preflight yf-plan` (the `yf` kernel, not `plan_manager.py`);
  `scripts/plan_manager.py` — `init`, `scope`, `triage`, `update-status`, `record-epic`,
  `resume-scan`, `audit`, `worktree {ensure,path,teardown}`,
  `landing-lock {acquire,release,status}`, `validate-merged`, `json-get`; `manifest_update.py`. Full
  surface in `spec/cli.md`; data shapes in `spec/data.md`. **Preflight/config moves to `yf`** per
  macro `REQ-YF-PRE-*`; the domain subcommands stay in Python.
- **Companion rule:** `protocols/PLANS.md` (+ `protocols/manifest.json`, sha256+semver) — the
  always-loaded trigger contract; verified by the preflight `rule_*` outcomes.
- **Config / state:** `.yf-plan.local.json` (operator config incl. `ignore-skill`,
  `execute.worktree`, `validate-cmd`); runtime state under `.yf/yf-plan/` (e.g. `preflight.json`).
  Legacy `.bdplan.local.json` / `.state/bdplan/` migrate via macro `REQ-YF-MIGRATE-001`.

## 4. Guardrails (`GR-PLAN-NNN`)

- **GR-PLAN-001** *Drift:* using native plan mode / `TodoWrite` / markdown task lists. *Rule:* all
  planning is `yf-plan`; all task tracking is `bd`. *Why:* one tracker, portable plans.
- **GR-PLAN-002** *Drift:* review agents editing the plan. *Rule:* conformance + red-team are
  **read-only**; only the main session writes. *Why:* auditable, deterministic review.
- **GR-PLAN-003** *Drift:* auto-committing/pushing on land. *Rule:* git authority is conservative —
  report and await authorization. *Why:* the operator owns the remote.
- **GR-PLAN-004** *Drift:* an in-place EXECUTE→PLAN re-plan loop. *Rule:* there is none; scope
  changes that need epic surgery re-enter PLAN before INTAKE. *Why:* the phase machine forbids it
  (REQ-PLAN-002).

## 5. Verification

- Portability/phase invariants are checked by `plan_manager.py audit` and the
  `count(pass-*.md) == count(review: lines)` invariant (REQ-PLAN-031). Worktree/landing-lock
  behavior has `scripts/test_worktree.py`. Preflight parity (REQ-PLAN-003) is verified by the macro
  spec's Epic 6.3 three-state fixtures once preflight moves to `yf`.

## 6. References

- `skills/yf-plan/SKILL.md`; `spec/phases.md`, `spec/agents.md`, `spec/cli.md`, `spec/data.md`,
  `spec/portability.md`, `spec/prerequisites.md`; `spec/worktree-execute-lifecycle.{d2,png}`.
- `protocols/PLANS.md`.
- Root `SPEC.md` §4 (PLAN) and `GUARDRAILS.md` (GR-002, GR-005).
