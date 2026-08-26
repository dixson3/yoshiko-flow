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
  `scoping | investigating | drafting | review | ready-for-approval | approved | executing | reconciling | complete | abandoned`,
  advanced only via `plan_manager.py update-status`, which appends a phase-log line.
  `ready-for-approval` is the distinct pre-approval state a plan enters only when `ready-check`
  (REQ-PLAN-066) is green; it is **not** execute-eligible — only `approved` (with a fresh
  fingerprint) is. `abandoned` is the terminal-but-not-successful state for a plan deliberately
  stopped: it is **not** execute-eligible and **not** `parked`.
- **REQ-PLAN-002** the phase machine shall be `UPSTREAM → SCOPE ↔ INVESTIGATE → PLAN → INTAKE →
  (session boundary) → EXECUTE → RECONCILE → COMPLETE`; there is **no EXECUTE→PLAN transition**.
  **Abandonment is an edge off that machine, not a stage in it:** a plan may enter `abandoned`
  from **any** status except `complete`, and leaves it by **exactly one** edge — `abandoned →
  drafting`, which resumes ordinary drafting. There is explicitly **no `abandoned → complete`
  edge**: a plan that was stopped did not finish, and letting it claim completion is the silent
  misreport this vocabulary exists to prevent.
- **REQ-PLAN-003** *(testable)* every invocation except `init` shall run the preflight
  (`yf preflight yf-plan`) and branch on `ok | ignored | system_deps_missing | bd_not_initialized | rule_*`.

### 2.2 Plan folder & portability (see `spec/portability.md`, `spec/data.md`)

- **REQ-PLAN-010** *(testable)* `init` shall create an OKF-PLAN plan bundle under `docs/plans/<plan-id>/`
  (or `Incubator/<slug>/plans/<plan-id>/`) with `plan.md`, the OKF-reserved `index.md` and `log.md`
  (replacing the legacy `README.md` and in-`plan.md` phase log — REQ-PORT-001, REQ-DATA-012),
  `context.md`, `findings/`, `diagrams/`, `assets/`, `references/`, `reviews/`; every non-reserved
  `.md` carries `type` + `okf_spec: OKF-PLAN` frontmatter (REQ-PORT-050). Plan-id numbering is global
  across roots.
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
  drives the transition). The red-team shall be **re-run after any major-concern revision**: a
  `REVISE` verdict blocks the plan from reaching `ready-for-approval` until a later red-team cycle
  returns `APPROVE`. Readiness keys on the **last recorded** red-team verdict being `APPROVE` — an
  earlier APPROVE followed by a REVISE (whose revisions were never re-reviewed) is **not** ready.
  Both agents are **read-only with respect to the repository under review**; the main session writes
  files. A sandbox spike outside that repository is authorized (REQ-AGENT-043/045).
- **REQ-PLAN-031** *(testable)* at red-team presentation the main session shall write
  `reviews/pass-N.md` **and** append the `log.md` `review:` line atomically (create-on-present),
  preserving `count(reviews/pass-*.md) == count(log.md review: lines)` (REQ-PORT-006).
- **REQ-PLAN-032** a `pass-N.md` shall be mutable until all concerns resolve, then frozen; each
  full REVISE cycle yields exactly one pass file.
- **REQ-PLAN-071** *(testable)* **verdict-line contract.** The canonical verdict line in a
  `reviews/pass-N.md` is a level-2 ATX heading — `## Verdict: <APPROVE|REVISE|INVESTIGATE-MORE>`.
  The red-team agent template (`agents/red-team.md`) shall **emit** that form, and the
  `ready-check` parser shall **accept** it. Template and parser are a single contract: a review
  written exactly as the template prescribes must parse. Because a silent mismatch between the two
  is unobservable (it degrades to "no verdict"), the parser shall additionally accept a level-3
  heading (`^#{2,3}\s+Verdict:`) as defence in depth — a tolerance for a template that drifts back,
  not a second canonical form. Emitting `###` remains non-conformant.
- **REQ-PLAN-072** *(testable)* **a malformed verdict shall fail loud.** `ready-check` shall
  distinguish *no review exists* from *a review exists but its verdict did not parse*. When
  `review_pass > 0` and no verdict parses, it shall report a **malformed-review error naming the
  offending file** rather than a null verdict. The `review_pass > 0 && verdict == null` state is a
  contradiction and shall never be presented as a merely-absent verdict.
- **REQ-PLAN-033** *(testable)* the portability `audit` shall be a **precondition of the approval
  prompt**, not a post-approval step: it runs as the last PLAN step, before the operator is asked to
  approve, so approval is consent to an already-verified plan (not "approve, then verify"). The
  approval prompt is solicited only when `ready-check` (REQ-PLAN-066) is green; INTAKE proceeds only
  on `pass` (or explicit `--force`, which logs a phase-log override).
- **REQ-PLAN-066** *(testable)* a `ready-check` verb shall gate the approval prompt: it verifies
  **both** preconditions — the **last recorded** red-team verdict is `APPROVE` (REQ-PLAN-030) **and**
  the portability audit passes (REQ-PLAN-033) — returns `{ready, reasons:[...]}` JSON, and exits
  non-zero (`3`) when not ready (mirroring the audit gate). A plan reaches status
  `ready-for-approval` and the operator sees the approval prompt only when `ready-check` is green.
  Operator approval is the single act of consent that transitions `ready-for-approval → approved`.
  `ready-check` and the approval transition are **adjacent** — `ready-check` re-runs at approval so
  no content edit can slip between a green check and the fingerprint write (REQ-PLAN-034).
- **REQ-PLAN-034** *(testable)* approval shall write the fingerprint under the dual field set
  (`fingerprint` frontmatter key + `**Fingerprint:**` line, REQ-DATA-015) over the plan's content
  sections — everything before the first `## ` (frontmatter, `**Field:**` lines, and the now-relocated
  log) is positionally excluded, along with `reviews/`, the Resolutions tables, and the
  `## Upstream Issues` section; a subsequent content edit marks the plan **stale-approved** and
  blocks EXECUTE until a fresh conformance → red-team → portability cycle re-approves it (or a logged
  `--force`). See `spec/portability.md` REQ-PORT-040/041.

### 2.5 Intake (see `spec/cli.md`, `beads-extra`)

- **REQ-PLAN-040** *(testable)* INTAKE shall **not** pour the molecule; it writes the content
  fingerprint (REQ-PLAN-034), auto-commits the plan locally (REQ-PLAN-064), and lands it per the
  landing strategy. The `plan-execute` pour and bead-DAG creation are deferred to EXECUTE start
  (REQ-PLAN-054); duplicate-pour and resume are one guard there (REQ-RESUME-004).
- **REQ-PLAN-041** child epics shall be created `--parent` only (never blocked by the start-gate
  task — a task→epic block is rejected); entry leaf issues shall depend on the start gate;
  downstream issues inherit it transitively.
- **REQ-PLAN-042** all dependency-edge wiring shall be a single `bd batch` call, never individual
  `bd dep add` shell commands.

### 2.6 Execute: worktree, resume, gates (see `spec/phases.md`, plan-009/plan-004)

- **REQ-PLAN-050** *(testable)* EXECUTE shall default to an isolated worktree
  (`.worktrees/<plan-id>`, branch `<plan-id>-execute`) cut from a pinned base (REQ-PLAN-055); a
  non-viable verdict falls back to in-place execution without regression.
- **REQ-PLAN-055** *(testable)* the worktree base and the §6.1 merge target shall be pinned to a
  known branch — `main` (default) or feature `<plan-id>` — via a `landing-strategy` config switch
  (`_resolve_landing_strategy`), never ambient HEAD. Named per-phase branches
  (`<plan-id>-development` / feature `<plan-id>` / `<plan-id>-execute`) replace the single bare
  `<plan-id>`; teardown preserves the feature branch under the feature-branch strategy. See
  `spec/phases.md` REQ-BRANCH-001..004.
- **REQ-PLAN-051** code edits shall target the worktree while bead tracking and plan-folder
  bookkeeping stay primary-side (the two-address-space model).
- **REQ-PLAN-052** *(testable)* on resume, the guard shall detect an existing epic
  (`resume-scan`), re-attach the worktree, run the orphan sweep (reset stuck beads to `open`;
  report, never auto-close, the unclassifiable) **before** the ready loop, and never re-resolve an
  already-resolved start gate.
- **REQ-PLAN-053** capability gates shall be first-class `-t gate` beads resolved with
  `bd gate resolve`; blocked gates are reported only after all unblocked work is drained.
- **REQ-PLAN-054** *(testable)* EXECUTE shall pour the `plan-execute` molecule at execute-start (the
  relocated INTAKE pour): `resume-scan` `found=false` pours once and writes the epic↔plan linkage
  atomically (`record-epic` + epic `metadata.plan_dir`) immediately after the pour, then resolves the
  start gate; `found=true` resumes without re-pouring. The former INTAKE duplicate-pour guard and the
  resume guard are one code path — the pour-once/resume gate (see `spec/phases.md` REQ-RESUME-004).

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
  reconciler agent), then close the reconcile step + epic and set status `complete`; the container
  cascade-close (REQ-PLAN-067) runs as part of this close step so no stale open epic/molecule
  survives completion.
- **REQ-PLAN-064** *(testable)* at the PLAN→EXECUTE landing boundary (after the portability audit and
  the fingerprint write, REQ-PLAN-034), the plan shall be auto-committed **locally** via
  `plan_manager.py commit-plan`: a scoped `git add` over an explicit pathspec (never `git add -A`) —
  always `${plan_dir}`, and `.beads/` **only when it is tracked / not gitignored**. On a local-only
  beads repo `.beads/` is intentionally gitignored (gh-only interchange), where co-adding it would
  fail; commit-plan shall skip the `.beads/` pathspec (surfacing a `beads_note`) rather than erroring
  (#71). Then a local commit, and **never a push**. This
  is the #63 clean-handoff boundary — a fresh execute session inherits a committed base, and intake
  artifacts survive a crash or fresh clone. **Commit-subject state signalling (#86):** when the
  resolved phase is `approved` (the intake landing commit), the subject shall signal that the plan is
  *approved but not yet executed* — `plan-NNN: INTAKE approved (awaiting /yf-plan execute) — <objective>`
  — so a `git log` scan cannot misread an intake'd-but-unexecuted plan as shipped work; the objective
  moves to the commit body. All other phases keep the plain `plan-NNN: <phase> — <objective>` subject.
- **REQ-PLAN-065** *(testable)* `commit-plan` shall refuse to commit on the repository's default
  branch. Default-branch resolution is `git symbolic-ref --short refs/remotes/origin/HEAD` →
  `git config init.defaultBranch` → `main`/`master`. A **detached HEAD or an empty current-branch
  name is fail-closed = refuse** (never commit). The guard is a hard refusal returned as a JSON
  verdict, not a warning.
- **REQ-PLAN-067** *(testable)* on COMPLETE (the RECONCILE close step, REQ-PLAN-063), yf-plan shall
  **cascade-close every container in the plan's tree** — intermediate epics **and the top-level plan
  molecule** — whose children are **all terminal**, walked **bottom-up**, with a close reason
  referencing the plan. A container with **any still-open child** while the plan is being marked
  `complete` is a **hard failure**: it must surface loudly (a non-empty `blocked` set halts
  completion), never a silent close or a silent leave. **"Terminal"** is defined consistently with
  `resume-scan`'s gate accounting: a child is terminal when it is `status: closed` **or** it is a
  **resolved/verified gate** (even if not `status: closed`), so a resolved gate never triggers a
  false hard failure; an **unsatisfied** gate is a genuine open child (part of the fail-loud signal,
  never auto-forced). The walk ships as a self-contained helper `skills/yf-plan/scripts/close_cascade.py`
  consumed by yf-plan §6.4; extraction to `_shared/` is **deferred** until a genuine second in-repo
  runtime consumer exists (rule-of-three — yf-beads-authoring carries a doctrine cross-reference
  only, not a code consumer). Cross-reference REQ-PLAN-063 (the reconcile/close step this hardens).
  **Root resolution (plan-043 Epic 3).** The cascade shall **distinguish "`bd` answered and the
  root bead does not exist" from "`bd` did not answer"**, and shall not collapse them. A root that
  `bd` positively reports absent is a **`fail`**: it exits non-zero, because a typo'd or stale root
  otherwise walks an empty tree and reports a clean cascade over nothing — a silent pass that looks
  exactly like success. A root that could not be resolved **because `bd` was unavailable** (binary
  absent, non-zero exit, wedged DB, unparseable output) is **`inconclusive`** under
  REQ-COMPLETE-003: it is reported loudly and does **not** halt. Collapsing the two would convert a
  `bd` outage into a hard completion halt on healthy work — the same failure mode the network-calling
  halting step is required to avoid, and a regression this requirement's own fix would otherwise
  introduce.
- **REQ-PLAN-068** *(testable)* yf-plan shall detect and surface **parked** plans — approved-but-never-
  executed plans that otherwise silently masquerade as complete (#86). A plan is **parked** iff its
  status is `approved` (coarse filter) **and** its stored content fingerprint is **present and fresh**
  (`bool(stored) and stored == current` — the same execute-eligibility signal, **not** the "not stale"
  test, which is also true when no fingerprint is stored). This deliberately excludes `executing` /
  `complete` (fail the status filter), stale-approved plans (fail freshness — they already carry the
  `stale_approved` tag), and `approved` plans with no stored fingerprint (which would otherwise get a
  contradictory execute nudge). The parked state shall be exposed as a `parked` flag in `list --json`
  and a rendered tag alongside the stale tag, surfaced by `/yf-plan status`, and enumerable by a
  `plan_manager.py parked --json` verb consumed by a **portable** land-the-plane SKILL.md step (a
  documented script-verb call, never a harness hook or scheduler). The Phase 4.5 coarse tracking issue
  shall be titled `plan-NNN execution tracking` (not the past-tense-glancing "Complete execution of
  plan-NNN"). Amendment-log entry: root `SPEC.md` `plan-028` (authored by plan-028 Issue 1.1; this
  requirement references it).
- **REQ-PLAN-069** *(testable)* on COMPLETE (the RECONCILE close step, REQ-PLAN-063), for a plan whose
  **deliverable class is `ci-release`** (REQ-PLAN-069a) yf-plan shall **hard-gate `complete`** on
  evidence that the deliverable's runner-only-observable behavior has been exercised: after the
  container cascade-close (REQ-PLAN-067) and **before** `update-status complete`, a `complete-gate`
  verb shall **halt completion** (exit non-zero + JSON verdict **on stdout** + actionable message,
  mirroring the `close_cascade.py` fail-loud contract and honouring the REQ-COMPLETE-003 envelope —
  the mirroring is now literal; both failing paths previously wrote to stderr, which the documented
  `GATE=$(…)` capture idiom cannot see) unless **at least one** of — (a) a **green-execution
  attestation**: a `log.md` `- validated:` bullet (REQ-PLAN-069b) recording one observed green run;
  **or** (b) an **open, out-of-tree, upstream-tracked deferred-validation bead** carrying the
  unverified-behavior signal forward (a standalone `bd` issue with label `deferred-validation` and
  metadata `{"plan":"<plan-id>"}`, discovered by a `bd list --label` filter — **never** a plan-tree
  child, so `close_cascade` does not fail-loud on it first). For a `standard`/unset deliverable class
  the gate is a strict **no-op** — ordinary plans (whose deliverable is observable in merged-state
  validation, REQ-PLAN-060) are never gated. The lesson driving this gate: CI/infra/release config is
  only correct when it *runs on the target*, and `merged` is not `works` (upstream #89). Parallel to
  REQ-PLAN-067; the deferred bead's out-of-tree placement is a deliberate per-bead exception to the
  coarse-granularity upstream convention.
- **REQ-PLAN-069a** *(testable)* **detection.** A plan's deliverable class shall be a **registered
  canonical dual-write field** `deliverable_class`↔`**Deliverable-class:**` (REQ-DATA-015 field set,
  `PLAN_FIELD_ORDER` immediately after `status`), with values `ci-release` (the gated class) or
  `standard` (default). Being a **registered** field — not a raw header line — it survives every
  `update-status`/`record-epic` field-block rewrite (`_rebuild_field_block` re-emits only registered
  fields) while remaining fingerprint-excluded (positionally above the first `## `, REQ-PORT-040), so
  writing it post-approval does not stale the plan. A `classify-deliverable` verb shall **suggest** a
  class by scanning the plan's epics/upstream/success-criteria text and (when available) merged-tree
  changed paths for ci-release signals (`.github/workflows/**`, `release`/`notarize`/`sign`/`deploy`
  keywords, self-hosted-runner references) returning `{suggested_class, signals, confidence}`
  (`high` = a workflow path or release/sign/notarize signal; `low` = keyword-only); the operator
  **confirms or overrides**, and the confirmed value is written via the dual-write field setter. The
  class is re-confirmable at reconcile when changed paths are available (they may be absent at intake).
- **REQ-PLAN-069b** *(testable)* **evidence.** One green execution shall be recorded as a `log.md`
  bullet `- validated: <run URL/id> — <note>` under the current `## YYYY-MM-DD` heading, written via
  `okf.append_log` (helper: `attest-validation`; a hand-written bullet is equally valid). Evidence is
  **operator-attested and trust-based** — no CI-API coupling. `complete-gate` reads `log.md` (with a
  `plan.md` `**Phase log:**` fallback for un-migrated bundles) and matches the `- validated:` bullet
  form. `validated:` shall be a recognized **non-status** `log.md` token (alongside `intake:`): no
  review-count (REQ-PORT-006), grandfather-date, or status parser keys on it.

- **REQ-PLAN-074** *(testable, plan-043 / #136)* on COMPLETE (the §6.4 ordered gate chain,
  REQ-COMPLETE-001), yf-plan shall **verify that RECONCILE actually reached the upstream end
  state each disposition promises**, via a `verify-reconcile` verb that is a **`halting`** step
  with **`command`** remediation-kind, honouring the REQ-COMPLETE-003 envelope. It runs **after**
  the reconcile bead is closed and **before** the first destructive step (cascade-close). For
  every **non-`exclude`** row of plan.md's `## Upstream Issues` table it shall assert:
  `include` → the issue is **CLOSED and carries a comment mentioning the plan id**;
  `supersede` → **CLOSED with `stateReason == NOT_PLANNED`**; `partial` → **OPEN and carries a
  plan-id mention**; `deferred` → **OPEN → `pass`, with NO plan-id-mention requirement;
  not-OPEN → `fail`** *(plan-048 D-7, Issue 0.2)*. A `deferred` row is a **non-action**: it
  records a scoping decision taken in the *deferring* plan, not work done on the issue, so
  there is nothing to attribute upstream — demanding a mention would make every deferring plan
  halt its own reconcile. The not-OPEN direction is still a real assertion, not a waiver: an
  issue the plan declared it would come back to, which is closed by the time reconcile runs,
  contradicts the disposition and is `fail`. `deferred` is **not** the same as `tracker`
  (`spec/cli.md` REQ-CLI-018), which is `inconclusive` **by construction** because the coarse
  tracker is closed by the land-the-plane sweep rather than by reconciliation; the two are
  report-only for different reasons and neither may be collapsed into the other. `exclude`
  rows remain skipped entirely. The mention requirement is not redundant with state: state alone would
  **pass** the very defect this requirement exists to catch, since the issue in question is
  CLOSED today — closed by a human 15 hours later as manual repair. Matching may be normalized
  (case/punctuation tolerant) but shall **never** be a time-window heuristic, which would also
  have passed it. The verdict shall carry **per-row** results
  `rows: [{issue, disposition, verdict, detail}]` with the aggregate rule stated explicitly:
  **any row `fail` → `fail` (halt), even alongside `inconclusive` rows**; inconclusive-only →
  `inconclusive` (report, never halt). Every checker failure — binary absent, non-zero exit,
  unparseable output, or timeout on the REQ-COMPLETE-003(f) bound — shall be `inconclusive`, so
  an outage never halts completion on healthy work. The table shall be parsed by the **single
  shared parser** (`parse_upstream_rows`), never a second one: this step is fail-loud, so two
  parsers disagreeing on row shape would produce a fail-loud **false positive**.
  Rationale: `agents/reconciler.md` step 4 already prescribed this verification **in prose** and
  it was skipped anyway — not via a swallowed error, filtering, or non-dispatch, but via a
  **false success assertion**: the reconciler parsed the table correctly, then reported success
  without performing the writes. Adding a sixth instruction to a five-instruction list that was
  partially ignored is a null change, so the check is mechanical.
  Verification: `scripts/test_verify_reconcile.py` covers each disposition's pass and fail case,
  the historical scenario (correct state, **no** plan-id mention) **failing**, `exclude` rows
  skipped, a checker error yielding `inconclusive` rather than `fail`, the **mixed** case (one
  row `fail` + one `inconclusive` → aggregate `fail`), row-shape variants (`[#N]` vs `#N`)
  pinning the shared parser, and — per plan-048 Issue 3.4a — each of the **five** recognised
  literals returning its declared verdict, including `deferred` OPEN → `pass` / not-OPEN →
  `fail` and `tracker` → `inconclusive` in both directions. An **unrecognised** disposition is
  `fail`, not `inconclusive`: a literal no producer offers is a typo in the table, and a
  fail-loud step must not silently pass one. No network in tests.

- **REQ-PLAN-075** *(testable, plan-043 / #140)* on COMPLETE (the §6.4 ordered gate chain,
  REQ-COMPLETE-001), yf-plan shall run the **bundle-conformance audit at close** via an
  `audit-close` verb that is an **`advisory`** step with **`prose`** remediation-kind, honouring
  the REQ-COMPLETE-003 envelope. It shall report the **absolute** finding set and shall **never**
  gate `set complete`: it exits **0 unconditionally**, with no option to make that conditional.
  It shall reuse the existing `_audit_plan` engine rather than reimplement it, so close-time and
  plan-time findings cannot diverge. Its position in the chain is governed by REQ-COMPLETE-001
  constraint 1: it runs **above the `classify-deliverable` block**, which contains the
  `set-deliverable-class` plan.md dual-write — above the *dual-write*, not merely above the
  `log.md` write. It shall not use the `FAIL-LOUD:` banner vocabulary reserved for halting steps.
  Rationale: the plan-phase `audit` runs at Phase 3 and in `/yf-plan capture`, both **before**
  INTAKE — but `references/` and `reviews/` are largely authored during EXECUTE, so those files
  are created *after* the only gate that would check them and no later gate re-runs it. Close is
  where the evidence is complete. Advisory rather than halting because a fail-loud close-time
  audit, measured against the completed corpus, would have blocked **22%** of plans that
  legitimately completed — including one **proven false positive** (a Windows-drive-letter regex
  matching inside a quoted fixture body) and one failure the close step **inflicted on itself**
  via its own `log.md` write. The absolute set rather than a delta-since-approval because the
  plan-phase audit is a *precondition of approval*, making the stored baseline an empty fail set
  by construction on every non-`--force` approval — the delta would equal the absolute set in the
  normal path, and a step that cannot block pays nothing for noise. The ordering constraint is
  not theoretical: the audit's grandfather downgrade keys on `log.md` `scoping:` entries, so a
  close-step `log.md` write that drops them silently promotes `warn` findings to `fail`.
  Verification: `scripts/test_audit_close.py` asserts a failing bundle still exits 0 and that
  `set complete` proceeds; that the verdict is never `halting` regardless of findings; that
  findings match the plan-phase `audit` engine exactly; and that the §6.4 invocation order places
  `audit-close` above the `classify-deliverable`/`set-deliverable-class` block, parsed from
  SKILL.md source.

- **REQ-PLAN-076** *(testable, plan-043 / Epic 3)* the §6.4 close of the **reconcile step bead**
  shall **re-derive that bead from `bd`**, scoped to the plan's epic, rather than relying on a
  shell variable bound only on the pour path (§5.2a). It shall **check the close's exit code**,
  and shall treat a reconcile bead it cannot resolve as a REQ-COMPLETE-003 verdict rather than
  proceeding silently.
  Rationale: the variable is assigned in exactly one place — the pour branch — and the **resume**
  branch (§5.2b) never re-derives it, so on any resumed execution the close step runs with it
  **unset**. The consequence was **measured live, and it is worse than an unset-variable failure**:
  `bd close` with no id argument does not error — it exits **0** and closes a *different*,
  in-progress bead, then reports success. During this plan's own verification probe it closed the
  very bead that was running the probe. So the resume path does not merely skip the reconcile
  close; it **silently closes the wrong bead and asserts success** — structurally the same
  false-success shape as the reconcile defect this plan exists to fix, in the step immediately
  adjacent to it. This is why the fix re-derives from `bd` rather than propagating the variable:
  a propagated variable can still be empty, and an empty one is actively destructive here.
  Verification: `scripts/test_reconcile_step_resolution.py` asserts the reconcile bead is resolved
  from the epic rather than from an environment variable, that an unresolvable reconcile bead
  yields a reported verdict rather than a bare `bd close`, and — as a regression pin on the
  measured behavior — that no code path can emit a `bd close` whose id argument is empty.

- **REQ-PLAN-079** *(testable, plan-037 / #107)* the plan and incubator roots shall be
  **configurable**, not hard-coded: `plans-root` (default `docs/plans`) and `incubator-root`
  (default `Incubator`) are read through the **same** three-tier config reader as every other
  yf-plan config key (REQ-YF-PRE-004), with the committed `.yf/plan/config.json` as their
  expected home (REQ-YF-PRE-004a) — they are a repository-level decision, since plan-id numbering
  is global across roots. Resolution shall be **import-safe**: the roots are bound before most of
  the module exists, so the reader used for them shall be dependency-free, shall fall back to the
  defaults when no config is present, and shall tolerate malformed JSON at import rather than
  raising. Motivating case (#107): a repo that is also an Obsidian vault, where a visible
  top-level `Incubator/` trips the vault's structure linter.
  Note on the id (#214): plan-037 allocated this requirement the number **073**, which was
  independently allocated to the `stamp-tracker` requirement (`spec/phases.md`). plan-053
  renumbered *this* one to `079` and left the stamp meaning at its original number. Frozen
  plan-037-era bundles cite this requirement under **073**; they are records that are never
  rewritten, so that citation stands as written and resolves here. This note deliberately
  spells the retired number bare, so it is not itself a citation of the retired id.

### 2.8 Capture (manual)

- **REQ-PLAN-070** `capture` shall be re-entrant and status-agnostic (pre-intake phases only), purely
  side-effecting on the plan folder, advancing no status and touching no beads; `--retro`
  additionally mines the current session's conversation for the portability classes.

## 3. Interfaces

- **CLI / scripts:** preflight is `yf preflight yf-plan` (the `yf` kernel, not `plan_manager.py`);
  `scripts/plan_manager.py` — `init`, `scope`, `triage`, `update-status`, `record-epic`,
  `resume-scan`, `audit`, `ready-check`, `fingerprint {write,check}`, `commit-plan`,
  `worktree {ensure,path,teardown}`,
  `landing-lock {acquire,release,status}`, `validate-merged`,
  `classify-deliverable`, `set-deliverable-class`, `complete-gate`, `attest-validation`,
  `json-get`; `manifest_update.py`. Full
  surface in `spec/cli.md`; data shapes in `spec/data.md`. **Preflight/config moves to `yf`** per
  macro `REQ-YF-PRE-*`; the domain subcommands stay in Python.
- **Companion rule:** `protocols/PLANS.md` (+ `protocols/manifest.json`, sha256+semver) — the
  always-loaded trigger contract; verified by the preflight `rule_*` outcomes.
- **Config / state:** canonical operator config is `.yf/plan/config.local.json` (`ignore-skill`,
  `plans-root`, `incubator-root`, `execute.worktree`, `validate-cmd`, `landing-strategy`,
  `autonomy`, `sweep-gates`, `max-attempts`, `max-review-cycles`), canonical runtime state is
  `.yf/plan/preflight.json` — both short-name (`plan`), as the `yf` binary emits them.
  `plan_manager.py` **matches this layout**: `SKILL_SHORT = "plan"` puts its own state (e.g.
  `landing.lock`) under `.yf/plan/`, and `_read_config()` merges `.yf/plan/config.local.json` >
  `.yf/plan/config.json` > the legacy root `.yf-plan.local.json`, canonical first. Both halves of
  `dixson3/yoshiko-flow#100` are delivered and the issue is closed. The legacy
  `.yf-plan.local.json` remains a supported read-time fallback; legacy `.bdplan.local.json` /
  `.state/bdplan/` migrate via macro `REQ-YF-MIGRATE-001`.

## 4. Guardrails (`GR-PLAN-NNN`)

- **GR-PLAN-001** *Drift:* using native plan mode / `TodoWrite` / markdown task lists. *Rule:* all
  planning is `yf-plan`; all task tracking is `bd`. *Why:* one tracker, portable plans.
- **GR-PLAN-002** *Drift:* review agents editing the plan. *Rule:* conformance + red-team are
  **read-only with respect to the repository under review**; only the main session writes. A
  sandbox spike outside that repository is authorized. *Why:* auditable, deterministic review.
- **GR-PLAN-003** *Drift:* auto-**pushing**, or committing to the default branch. *Rule:* git
  authority is conservative for the **remote** — report and await authorization before any push.
  **Carve-out:** a **local** commit at the PLAN→EXECUTE boundary is permitted (REQ-PLAN-064), scoped
  to `${plan_dir}` + `.beads/` and **refused on the default branch** (REQ-PLAN-065); the push stays
  authorized-only. *Why:* the operator owns the remote; a clean local handoff does not touch it.
- **GR-PLAN-004** *Drift:* an in-place EXECUTE→PLAN re-plan loop. *Rule:* there is none; scope
  changes that need epic surgery re-enter PLAN before INTAKE. *Why:* the phase machine forbids it
  (REQ-PLAN-002).

## 5. Verification

- Portability/phase invariants are checked by `plan_manager.py audit` and the
  `count(pass-*.md) == count(review: lines)` invariant (REQ-PLAN-031). Worktree/landing-lock
  behavior has `scripts/test_worktree.py`. The REQ-PLAN-069 completion criterion
  (`classify-deliverable` detection, `complete-gate` halt/pass/no-op, `deliverable_class`
  round-trip survival, out-of-tree deferred-bead agreement, `validated:` non-status token) is
  covered by `scripts/test_complete_gate.py` (Tier-1, tagged REQ-PLAN-069). Preflight parity
  (REQ-PLAN-003) is verified by the macro spec's Epic 6.3 three-state fixtures once preflight moves
  to `yf`.

## 6. References

- `skills/yf-plan/SKILL.md`; `spec/phases.md`, `spec/agents.md`, `spec/cli.md`, `spec/data.md`,
  `spec/portability.md`, `spec/prerequisites.md`, `spec/ci-release-completion.md`;
  `spec/worktree-execute-lifecycle.{d2,png}`.
- `protocols/PLANS.md`.
- Root `SPEC.md` §4 (PLAN) and `GUARDRAILS.md` (GR-002, GR-005).
