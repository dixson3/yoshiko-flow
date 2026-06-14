# Plan: Make bdplan execute run plans in a git worktree by default, with merge-back/re-validate/push land-the-plane flow

**ID:** plan-009-james-dixson-996e44
**Author:** james-dixson
**Created:** 2026-06-14
**Status:** complete
**Epic:** beads-skills-mol-bjf
**Phase log:**
- 2026-06-14 scoping: initial scope captured
- 2026-06-14 investigating: 5 experiments identified
- 2026-06-14 drafting: synthesizing plan from 5 findings
- 2026-06-14 review: plan v1 presented
- 2026-06-14 approved: operator approved; D4 conservative ratified
- 2026-06-14 intake: epic beads-skills-mol-bjf poured
- 2026-06-14 executing: start gate resolved
- 2026-06-14 reconciling: execution complete; entering land-the-plane
- 2026-06-14 complete: plan complete; upstream #23 filed; committed locally (push deferred per operator)

## Objective
Make `bdplan execute` run a plan inside a dedicated git worktree by default. On
execute-begin, create a worktree + branch (proposed `.git/worktree/<plan>` on branch
`<plan>`); the coordinator works the plan there (changes, tests, commits); at
land-the-plane time, merge changes back into the originating branch (e.g. local `main`),
**re-validate the merged result** (other plans/changes may have landed first), re-commit,
then push fully upstream.

## Motivation
Today `bdplan execute` runs in-place on the operator's working branch. Two problems:

1. **No isolation.** Execution mutates the live working tree. A long-running, multi-bead
   plan leaves the operator's branch in an intermediate state and cannot run concurrently
   with other work.
2. **No merge-time regression safety.** Each plan/change passes *its own* gates against
   the base it branched from. When several changes land concurrently, each can be
   individually green yet the **merged** result breaks — and nothing today re-validates
   the integrated state before it is pushed upstream. The operator's explicit concern:
   "before changes are pushed to a remote upstream, all changes must be revalidated /
   regression tested."

Worktree-based execution gives isolation; a merge-back + re-validate step gives
integration safety. The open architectural question is how to factor this across skills.

## Scope decisions (operator, 2026-06-14)

- **D1 — Architecture (embed vs distinct skill): INVESTIGATE.** Whether worktree
  lifecycle lives inside bdplan (subcommand / coordinator subagent) or in a distinct
  `worktree` skill that bdplan softly depends on (present → worktree flow; absent →
  current in-place behavior) is an open question to be resolved by investigation, with the
  recommendation chosen by operator at PLAN review. Precedent favoring the soft-dep skill:
  plan-008 (diagram-authoring is a distinct skill softly depended on by bdplan/bdresearch).
- **D2 — Default scope: DEFAULT-ON with opt-out + safe fallback.** Every `bdplan execute`
  uses a worktree when viable. Auto-fallback to current in-place behavior when: not a git
  repo, repo state makes a worktree unsafe, or the worktree capability is absent. Per-plan
  / config opt-out is available.
- **D3 — Re-validation (the deep one): INVESTIGATE the regression/acceptance model.**
  Re-validation must cover not just *this* plan's gate tests but **regression across all
  changes merged after this plan started but before it merges back**. Individually-green
  concurrent changes may fail when integrated. This may imply a project-level
  integration/acceptance suite — possibly a **third skill** (`acceptance` / `regression`)
  that bdplan + the worktree skill coordinate with — that must pass before any upstream
  push. To be investigated and designed.
- **D4 — Push authority: CONSERVATIVE (ratified by operator 2026-06-14).** Automate
  worktree → commit → merge to local base → re-validate, then STOP and report the proposed
  `bd dolt push && git push` for operator authorization. Full-auto-including-push is NOT
  adopted; it remains a future operator-configurable option (Issue 3.6) but the shipped
  default is conservative.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

_Upstream scan (search "worktree execute bdplan") returned no existing issue. Per AGENTS.md
coarse granularity, one tracking issue was filed against `dixson3/beads-backed-skills` at
land-the-plane:_ **[#23](https://github.com/dixson3/beads-backed-skills/issues/23)**
_(bdplan: worktree-based execute with merge-back + merged-state re-validation)._

## Investigation Findings

Five experiments ran; full evidence in `findings/exp-00{1..5}-*.md`. Key results:

- **INV-1 (`exp-001`) — worktree mechanics.** **Reject the proposed `.git/worktree/<plan>`
  placement** — it nests a live working tree inside the gitdir, one segment from git's
  reserved `.git/worktrees/` admin area; functional but fragile, zero upside. Use a
  gitignored top-level **`.worktrees/<plan-id>`**, branch = plan id verbatim (`[a-z0-9-]`,
  no length issue). Merge-back must run **from the primary checkout** (`git merge <plan>`) —
  you cannot check out the base branch in two worktrees at once. Idempotent create/resume:
  `git worktree add <wt> -b <plan>` (fresh) vs `... <plan>` without `-b` (re-attach).
  `worktree remove` refuses on a dirty tree; branch deletion is a separate explicit step.
- **INV-2 (`exp-002`) — beads across worktrees: FAVORABLE.** `bd` has **native worktree
  support** — one shared Dolt DB in the **primary's** gitignored `.beads/embeddeddolt/`,
  resolved via `git rev-parse --git-common-dir`. The worktree has no DB of its own; all
  `bd` writes from inside the worktree land in the single primary DB and are immediately
  visible everywhere. **No per-branch bead divergence, no merge-time JSONL conflict** (bead
  state is out-of-git). The coordinator MAY run `bd` directly from inside the worktree.
  Precondition: the worktree must be a real `git worktree` of the primary (shared
  git-common-dir), not an independent clone. (Caveat: verified on bd 1.0.5; single embedded
  Dolt lock → safe for sequential writes, flag parallel writers.)
- **INV-3 (`exp-003`) — execution model.** Single shared **persistent** worktree;
  coordinator + any sub-agents run with **cwd = `.worktrees/<plan-id>`**, using **explicit
  `git worktree`** — NOT harness `EnterWorktree`/`isolation` primitives (those are
  disposable/auto-cleaned under `.claude/worktrees/`, the wrong lifecycle for a
  persist-then-merge plan worktree). EXECUTE sub-agents must **not** use
  `isolation="worktree"` (reserved for INVESTIGATE). Lifecycle maps to existing phases:
  CREATE at §5.3, RE-ATTACH on resume at §5.2, MERGE-BACK + TEARDOWN at §6.1/§6.2. Gap to
  close: a resume-time **dirty-worktree check** (`git -C <wt> status --porcelain`) the
  current docs don't specify.
- **INV-4 (`exp-004`) — merge-time regression model.** The gap is "test-the-merge, not the
  branch": per-plan gates validate against the fork-point, but the merged
  `base@now + plan` can break (class b — clean merge, semantic regression). Prior art (Bors
  / GitHub merge queue / GitLab merge trains / Zuul) all solve it by **validating the
  prospective merged state** and **serializing landings**. **v1 contract:** after merge-back,
  before push, run (a) the plan's own Gate `Test:` commands against the merged state **+**
  (b) a configured project **`validate-cmd`** (warn-skip when unset). Defer (c) replaying
  other active plans' gates and speculative parallelism to v2. Requires **reordering Phase 6**
  (today's §6.1 "tests pass" runs before the §6.2 `pull --rebase` — wrong order). Add a
  **local landing lock** to serialize merge-backs. On push rejection, require
  `pull --rebase` + **re-validate** before retry.
- **INV-5 (`exp-005`) — D1 resolved: embed-with-seam.** `install.py` has **no
  optional-dependency concept** (`depends-on-skill` is hard/force-install only; confirmed in
  plan-008 EXP-002), and the repo's only soft-dep precedent (diagram-authoring) is
  **instruction-level prose**, never a frontmatter edge. With **one consumer** (bdplan
  execute) and a lifecycle **tightly policy-coupled** to bdplan's §5.2/5.3/6.1/6.2, a
  distinct skill would ≈2x v1 surface for zero present reuse. **Recommendation: embed in
  bdplan behind a `plan_manager.py worktree {ensure,path,teardown}` verb seam; extract a
  standalone `worktree` skill only on a committed second consumer** (rule of three).

## Approach

**Embed-with-seam (D1 = option C).** Add worktree-based execution to bdplan directly, behind
two clean extraction seams so a future standalone skill is a cheap lift-and-shift:

1. **Worktree mechanics** → a self-contained `plan_manager.py worktree {ensure,path,teardown}`
   `--json` verb cluster taking only `(repo_root, plan_dir/plan_id)`, modeled on
   `diagram-authoring/scripts/render.py`'s subparser surface. No bdplan phase state inside.
2. **Validation** → a `validate-cmd` resolved from `.bdplan.local.json` (the layer-(b)
   project-suite seam).

**Lifecycle, mapped onto the existing phase model** (default-on, D2):

```
EXECUTE
  §5.1 select plan
  §5.2 resume guard ── on resume: worktree ensure (re-attach, no -b) + dirty-state check
  §5.3 resolve start gate (fresh) ── worktree ensure (create -b <plan>)  [VIABILITY CHECK]
  §5.4 run coordinator (main session stays at repo root — see address-space model);
       code/build/commit ops target the worktree via `git -C`/sub-agent cwd; commits
       accumulate on branch <plan>. Sub-agents: NO isolation="worktree".
  ...  bead work
RECONCILE  (REORDERED per INV-4; all steps run PRIMARY-side)
  §6.1   acquire landing lock; bring local base current; `git merge --no-ff <plan>` into base
  §6.1.5 VALIDATE MERGED STATE: (a) plan Gate Test: cmds + (b) configured validate-cmd
         fail → halt, report (lock held for fix); pass → commit merge, RELEASE lock
  §6.2   conservative push handoff (separate primary-side step; report proposed
         `bd dolt push && git push`; D4); on authorized push rejection → pull --rebase +
         RE-VALIDATE before retry; then worktree teardown (remove + branch -d + prune)
COMPLETE
```

**Execution address-space model (resolves red-team C1 / M1 — the blocking design point).**
There are **two** distinct address spaces and operations must be explicitly routed:

- **Primary checkout (repo root, where `/bdplan execute` was invoked).** The coordinator IS
  the main session — its cwd is NOT changed per-plan. All of these stay primary-side:
  the **plan folder** (`plan.md`, `reviews/`, phase-log, `findings/`) and every
  `plan_manager.py <verb> "${plan_dir}"` call (`plan_dir` is a **relative** path resolved
  against cwd — moving cwd would break it); **`.beads/`** (INV-2: the shared Dolt DB already
  lives in the primary's `.beads/embeddeddolt/` and is reached from anywhere via
  git-common-dir); the §6.1 merge, §6.1.5 validation, and the §6.2 push handoff.
- **Worktree (`.worktrees/<plan-id>`, branch `<plan>`).** Only **project code/build
  artifacts** the plan edits. Reached via `git -C .worktrees/<plan-id>` or by giving an
  agent-backed bead that worktree as its cwd. Only these commits land on branch `<plan>`
  and merge back.

So: **bead tracking and plan-folder bookkeeping happen primary-side; only code changes
accumulate on the plan branch.** The plan folder is intentionally NOT committed to `<plan>`
— it evolves on the primary branch as it does today. The coordinator never `cd`s into the
worktree; it directs file edits there with explicit `git -C`/cwd and keeps `bd` +
`plan_manager.py` at the repo root.

![worktree execute lifecycle](diagrams/worktree-execute-lifecycle.png)

**Default-on with safe fallback (D2).** `bdplan execute` uses a worktree unless a
**viability check** fails — not a git repo, primary repo's `.beads` not a real worktree
parent, an un-resolvable dirty/locked state — or the operator opts out
(`.bdplan.local.json` key, e.g. `"execute.worktree": false`, or a per-invocation flag). On
fallback, execute runs in-place exactly as today, with a one-line warning naming the reason.

**Validation coverage — honest scope (resolves red-team C2).** The operator's stated concern
is class-(b) regression (A renames `foo()`; B calls it; each individually green, broken when
merged). Layer (a) (this plan's own gates) does **not** reliably catch class (b) — in the
canonical case the *other* plan's gates are what would catch it. So the concern is genuinely
covered **only when `validate-cmd` is configured with a project-wide suite** (layer b). When
`validate-cmd` is unset, §6.1.5 runs layer (a) only and emits a **prominent land-time notice**
("merged-state validation ran plan gates only; no project suite configured — cross-plan
regressions NOT checked") — never a bare green that could be mistaken for integration safety.
Replaying other active plans' gates (layer c) stays deferred to v2; this is acceptable
precisely because a configured `validate-cmd` is the real safety net (confirm at review).

**Push authority stays conservative (D4, working assumption).** Everything through
merge-back + local re-validation is automated; the upstream push is reported and run only on
operator authorization, preserving bdplan's REQ-ORCH-014 posture. (Confirm or relax at review.)

**Deferred to v2 (explicitly, so absence isn't read as oversight):** replaying other active
plans' gates (INV-4 layer c); speculative/parallel pre-merge testing; a fully automated
rebase-revalidate-retry loop; extraction of a standalone `worktree` and/or `acceptance` skill
(triggered by a committed second consumer).

## Epics

### Epic 1: Worktree lifecycle engine (the seam)
- Issue 1.1: Add `worktree {ensure,path,teardown}` `--json` verbs to `plan_manager.py`
  (idempotent create vs re-attach per INV-1; `.worktrees/<plan-id>`; teardown =
  remove + `branch -d` if merged + `prune`). Pure `(repo_root, plan_dir)` inputs; no phase
  state. Model on `render.py` subparsers.
- Issue 1.2: `.worktrees/` gitignore management — ensure the entry exists (append if absent)
  as part of `ensure`; idempotent.
- Issue 1.3: Viability + dirty-state probes — `worktree ensure` returns a structured
  verdict (`viable` / `fallback:<reason>`); resume dirty-worktree check
  (`git status --porcelain`) surfaced, not auto-resolved. The `fallback:<reason>` set
  includes: not-a-git-repo, primary `.beads` not a real worktree parent, unresolved
  dirty/locked state, **and `bd` shared-DB resolution failing from the created worktree**
  (INV-2 is version/config-fragile — runtime fallback, not only the one-time gate; M4).
- Issue 1.4: Unit tests for the verb cluster (create, re-attach idempotency, teardown
  refuse-on-dirty, non-git fallback, branch-name = plan id). depends-on: 1.1, 1.2, 1.3

### Epic 2: EXECUTE-phase integration (default-on + fallback)
- Issue 2.1: Wire `worktree ensure` (create) into SKILL.md §5.3 fresh-run path, after
  start-gate resolve, before coordinator. depends-on: 1.4
- Issue 2.2: Wire re-attach + dirty-state check into the §5.2 resume guard (compose with the
  orphan sweep: re-attach → sweep → loop). depends-on: 1.4
- Issue 2.3: Run coordinator (§5.4) and any agent-backed beads with cwd = worktree;
  update `agents/coordinator.md` step 5 to set sub-agent cwd and **forbid
  `isolation="worktree"`** for EXECUTE. depends-on: 2.1
- Issue 2.4: Viability gate + opt-out — `.bdplan.local.json` `execute.worktree` key and
  in-place fallback with a one-line reason. depends-on: 1.3, 2.1
- Issue 2.5: **Dogfood acceptance run** (resolves C4) — a concrete named checklist run on a
  throwaway follow-up plan: create worktree → run a no-op bead → merge-back `--no-ff` →
  validate → teardown; assert `plan_dir`/`plan_manager.py` ops stayed primary-side, beads
  landed in the shared DB, code landed on `<plan>`. Ties to Success Criteria 1–6. The D2
  **default-on flip is GATED behind this passing** — ship worktree mode opt-in until the
  dogfood passes, then flip the default. depends-on: 2.3, 3.5

### Epic 3: RECONCILE merge-back + re-validation (Phase 6 reorder)
- Issue 3.1: Reorder Phase 6 — bring base current → `git merge --no-ff <plan>` from the
  **primary checkout** (M2: `--no-ff` for auditability / clean revert; defines the merged
  tree §6.1.5 validates) → then validate (today's order tests pre-pull; fix it).
  depends-on: 1.4
- Issue 3.2: Add §6.1.5 "Validate merged state" — run plan Gate `Test:` cmds + configured
  `validate-cmd` against the merged tree; halt on fail. When `validate-cmd` is unset, run
  layer (a) only and emit the **prominent cross-plan-not-checked land-time notice** (C2),
  not a silent warn. depends-on: 3.1
- Issue 3.3: `validate-cmd` config seam in `.bdplan.local.json` + resolution helper +
  docs. depends-on: 3.2
- Issue 3.4: Landing lock (resolves C3) — `.state/bdplan/landing.lock`, **atomic acquisition
  (`O_EXCL`/`mkdir`)**, recording **hostname + PID + plan-id + timestamp**. Staleness =
  hostname matches AND PID dead → reclaimable; a lock from another host is **never
  auto-broken** (surface to operator). **Single-machine serialization scope** (v1
  single-developer assumption; cross-machine concurrent landing out of scope). Ensure
  `.state/` is gitignored/unsynced. Contention unit test in 1.4/3.4. depends-on: 3.1
- Issue 3.5: Conservative push handoff + teardown ordering (resolves M3). Lock lifetime:
  acquire at §6.1; **release immediately after a green local validate + committed merge**
  (base is already green) — the §6.2 push is a **separate primary-side step** that does NOT
  hold the global landing lock across the operator-authorization wait. On push rejection
  require `pull --rebase` + re-validate before retry; `worktree teardown` after authorized
  push. depends-on: 3.2, 3.4
- Issue 3.6: Push-authority confirmation (D4) — encode conservative default; note the
  full-auto option as operator-configurable if ratified. depends-on: 3.5

### Epic 4: Docs, drift, portability
- Issue 4.1: Update `SKILL.md` (Phase 5/6 prose), `agents/coordinator.md`, and the phase-model
  diagram to describe the worktree lifecycle; bump manifest if the `PLANS.md` rule changes.
  depends-on: 2.4, 3.6
- Issue 4.2: Lifecycle d2 diagram in `diagrams/` (per `diagram-authoring`) referenced from
  SKILL.md / plan.md.
- Issue 4.3: Record the **rule-of-three extraction triggers** (worktree verbs → `worktree`
  skill; validation → `acceptance` skill) as inline notes; ensure DRIFT-CHECK manifest covers
  the new SKILL↔script edges. depends-on: 4.1
- Issue 4.4: Update README / Prerequisites and file the single coarse upstream tracking issue
  at land-the-plane (AGENTS.md coarse granularity). depends-on: 4.1

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: bd worktree support present
- Type: human
- Condition: `bd` resolves the shared DB via git-common-dir from inside a worktree (INV-2
  precondition), and `git worktree` is available.
- Test: `git worktree list >/dev/null 2>&1 && bd version` (and, in a scratch worktree,
  `bd list` succeeds against the primary DB).
- Blocks: Epic 1 issues that assume native bd worktree support.
- Instructions: Ensure `bd` >= 1.0.5 and Dolt present; if `bd` lacks worktree DB
  resolution, fall back to running `bd` from the primary checkout (revisit INV-2).
- Note: this gate fires once at intake; it is **complemented by a runtime viability
  fallback** (Issue 1.3 / M4) for the same condition, since INV-2 marks bd worktree DB
  resolution as version/config-fragile.

### Capability Gate: dogfood acceptance passed (blocks D2 default-on flip)
- Type: human
- Condition: the Issue 2.5 dogfood acceptance checklist passes on a throwaway follow-up plan.
- Test: run the 2.5 checklist; assert SC 1–6 hold (worktree create/merge/teardown,
  primary-side `plan_dir`/bead ops, code-only on `<plan>`).
- Blocks: flipping `execute.worktree` default to on (D2).
- Instructions: ship worktree mode opt-in; flip the default only after this passes.

## Risks & Mitigations

- **Bootstrapping / dogfooding.** This plan modifies `bdplan execute` itself. Its OWN first
  execution cannot use the not-yet-built worktree feature — the first run is in-place;
  worktree mode applies to subsequent plans. Unit tests (1.4) cover the verb cluster only,
  not the SKILL.md/coordinator.md wiring or the cwd address-space split. *Mitigation:* the
  **named dogfood acceptance checklist (Issue 2.5)** on a throwaway follow-up plan is the
  exit test for SC 1–6, and the **D2 default-on flip is gated behind it passing** (ship
  opt-in first, then flip).
- **bd version / config drift (INV-2 caveat).** Native worktree DB resolution verified on
  bd 1.0.5 with default config (JSONL export to stdout). A future bd or a project enabling a
  git-tracked `issues.jsonl` could reintroduce per-branch divergence. *Mitigation:* the
  Capability Gate test; re-test if bd config changes; document the assumption.
- **Parallel bead writers on one Dolt lock.** Only sequential writes tested. *Mitigation:*
  v1 coordinator writes are sequential; flag parallel-writer validation as out of scope.
- **Soft-dep drifting into a hard edge.** If extracted later, someone may add `worktree` to
  `depends-on-skill` (force-install, forbidden). *Mitigation:* explicit "never add
  `depends-on-skill`" note (the plan-008 mitigation pattern), recorded in Issue 4.3.
- **Phase-6 reorder regressions.** Reordering RECONCILE could break the existing
  conservative handoff or upstream reconcile sequencing. *Mitigation:* preserve §6.3/§6.4
  ordering; the reorder only inserts merge + validation before the push handoff.
- **Dirty/abandoned worktree on crash.** A crashed session may leave a dirty/un-merged
  worktree. *Mitigation:* resume-time dirty-state check (Issue 2.2) surfaces to operator;
  `git worktree prune` housekeeping; teardown never `--force` without confirmation.
- **Landing lock left held.** A crash mid-landing could strand the lock. *Mitigation:* lock
  carries PID + plan-id; stale-lock detection + operator override.

## Success Criteria

1. `bdplan execute` runs a plan in an isolated `.worktrees/<plan-id>` worktree (branch =
   plan id) **by default**, with commits accumulating on that branch.
2. Bead tracking remains correct from inside the worktree (single shared primary DB; INV-2).
3. Resume re-attaches to the existing worktree (never creates a second) and surfaces a dirty
   prior state to the operator.
4. At land-the-plane: base is brought current, `<plan>` merges into it, and the **merged
   state** is re-validated (plan gates + configured `validate-cmd`) **before** any push.
5. Push remains conservative (reported, operator-authorized; D4) unless explicitly
   reconfigured; on push rejection, re-validation is required before retry.
6. Safe in-place fallback (with a stated reason) when worktrees are not viable or are opted
   out; no regression to current behavior in fallback mode.
7. Worktree mechanics live behind the `plan_manager.py worktree` verb seam; extraction
   triggers for a standalone skill are documented.
8. Docs/diagram/DRIFT-CHECK updated; one coarse upstream tracking issue filed at land.
