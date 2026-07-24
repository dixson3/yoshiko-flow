# Phase Model Specification

## Phase Sequence

REQ-PHASE-001: The skill implements 7 phases: UPSTREAM, SCOPE, INVESTIGATE, PLAN, INTAKE, EXECUTE, RECONCILE.
Rationale: Each phase has a distinct responsibility; skipping phases produces incomplete plans or broken execution.
Verification: `grep -c '## Phase [0-6]' skills/yf-plan/SKILL.md` returns 7.

REQ-PHASE-002: PLAN-approval and EXECUTE are separated by a session boundary. Under the **intake-at-execute** model the molecule is **not** poured during INTAKE; INTAKE writes the content fingerprint (REQ-PORT-040), auto-commits the plan (REQ-PLAN-064), and lands it. The `bd mol pour` and its human start gate are created at **EXECUTE start** (`/yf-plan execute`, a new session), where the start gate is resolved in the same session immediately after the pour. Execution eligibility across the boundary is carried by the plan's `**Fingerprint:**` (the stale-approved gate), not by a pre-poured epic.
Rationale: Pouring at intake split plan artifacts and beads across the session boundary and forced a standalone duplicate-pour guard. Relocating the pour to execute-start means a planning-phase edit has no poured beads to reconcile, and the fingerprint — not a sticky status — gates execution. The operator still consciously begins execution in a fresh session.
Verification: SKILL.md Phase 4 has no `bd mol pour`; Phase 5 execute-start pours on the epic-absent branch and resolves the start gate; Phase 5 heading states "in a new session".

REQ-PHASE-003: SCOPE and INVESTIGATE are bidirectional — investigation findings may revise scope.
Rationale: Experiments can reveal that the original scope was wrong or incomplete.
Verification: SKILL.md Phase 2 Transitions includes "Findings invalidate scope -> SCOPE".

REQ-PHASE-004: PLAN may return to SCOPE or INVESTIGATE if the draft reveals gaps.
Rationale: Plan synthesis is when gaps become visible; the model must be able to backtrack.
Verification: SKILL.md Phase 3 Iteration includes return-to-INVESTIGATE and return-to-SCOPE paths.

REQ-PHASE-005: PLAN advances to INTAKE only on explicit operator approval, and the approval prompt is solicited only once the plan is in `ready-for-approval` (i.e. `ready-check` is green: last red-team `APPROVE` + audit `pass`). Approval transitions `ready-for-approval → approved`.
Rationale: The operator must review and approve the plan before any beads are created or work begins — and approval must be consent to an already-verified plan, not "approve, now verify". Gating the prompt on `ready-check` prevents soliciting approval on an unverified plan (a REVISE'd-but-unre-reviewed draft, or one whose audit has not passed).
Verification: SKILL.md Phase 3 runs `ready-check` before the approval prompt and the `review -> ready-for-approval -> approved` sequence; Phase 3 Iteration: `"approve" / "looks good" -> advance to INTAKE`.

## Status Values

REQ-STATUS-001: Exactly 9 status values exist: `scoping`, `investigating`, `drafting`, `review`, `ready-for-approval`, `approved`, `executing`, `reconciling`, `complete`.
Rationale: Status drives phase transitions and plan selection; extra or missing values break the state machine. `ready-for-approval` is the distinct pre-approval state a plan enters only when `ready-check` is green (last red-team `APPROVE` + audit `pass`); operator approval then transitions it to `approved`. It is not execute-eligible.
Verification: `grep 'Status values:' skills/yf-plan/SKILL.md` lists all 9.

REQ-STATUS-002: Every phase transition sets status via `plan_manager.py update-status`.
Rationale: Centralizing status updates in one script prevents format drift between SKILL.md and plan.md.
Verification: `grep -c 'py update-status' skills/yf-plan/SKILL.md` returns 9 — the 8 non-initial status transitions (now including `ready-for-approval` set at the end of PLAN when `ready-check` is green, plus the `ready-for-approval → approved` transition at INTAKE) plus the conditional stale-approval `--force` override re-log in §5.2 (which re-stamps the *current* status to append an audit phase-log line, REQ-PORT-041, and is not a new transition); the bare `update-status` prose mention in the CAPTURE phase is excluded.

REQ-STATUS-003: Initial status `scoping` is set by `plan_manager.py init`, not by a separate `update-status` call.
Rationale: Plan creation and initial status are atomic — a plan.md without status is invalid.
Verification: `grep 'scoping' skills/yf-plan/scripts/plan_manager.py` appears in `seed_plan_md`.

## Session Boundary

REQ-SESSION-001: The start gate is a human-type gate requiring operator resolution.
Rationale: Prevents automated execution without explicit human intent.
Verification: plan-execute.formula.toml `[steps.gate]` has `type = "human"`.

REQ-SESSION-002: `/yf-plan execute` is the only entry point for the EXECUTE phase.
Rationale: Ensures the session boundary is respected; no other command can begin execution.
Verification: SKILL.md Phase 5 heading and 5.3 (resolve start gate) are only reached via `/yf-plan execute`.

## Branch & Worktree Model (#47)

REQ-BRANCH-001: yf-plan uses **named per-phase branches**: `<plan-id>-development` (the planning worktree), feature `<plan-id>` (the landed, approved plan under the feature-branch landing strategy), and `<plan-id>-execute` (the execution worktree). The single bare `<plan-id>` branch of the prior model is replaced everywhere it was derived (`_worktree_path`, `_plan_id_from_dir`, `_worktree_teardown`).
Rationale: A single bare `<plan-id>` collided across the planning, landed-plan, and execution roles, producing branch-of-a-branch topology. Distinct names make each phase's branch unambiguous.
Verification: `_worktree_path` / `_worktree_teardown` in plan_manager.py derive `<plan-id>-execute`; `test_worktree.py` asserts the named-branch scheme.

REQ-BRANCH-002: The execute worktree shall be cut from a **known pinned base** — `main` (default strategy) or feature `<plan-id>` (feature-branch strategy) — never ambient HEAD. `_worktree_ensure` passes an explicit start-point to `git worktree add -b <branch> <base>`. The §6.1 merge target is likewise pinned to the same strategy-derived base, not ambient.
Rationale: Cutting from ambient HEAD (whatever branch happened to be checked out) is the #47 root cause — it produced branch-of-a-branch topology and a mismatched merge target. Pinning **both** the base and the merge target closes #47.
Verification: `_worktree_ensure` receives a base start-point; `test_worktree.py` asserts worktree base == configured base (not HEAD); SKILL.md §6.1 pins the merge target per strategy.

REQ-BRANCH-003: A project-config **`landing-strategy`** switch (`main` default | `feature-branch`) drives both the execute base and the merge target, resolved by `_resolve_landing_strategy()` (parallel to `_resolve_validate_cmd`, read from the legacy root `.yf-plan.local.json` today; canonical `.yf/plan/config.local.json` after `dixson3/yoshiko-flow#100`). Under `main`, plans land by merging to `main`; under `feature-branch`, plans land on feature `<plan-id>` (preserved by teardown) for later operator integration.
Rationale: Teams differ on trunk-based vs feature-branch integration; a single switch selects the topology without per-plan improvisation.
Verification: `_resolve_landing_strategy` returns `main|feature-branch` defaulting to `main`; `test_worktree.py` covers the strategy switch.

REQ-BRANCH-004: Between phases the primary checkout is restored to a known branch (never left on a plan branch). Teardown re-points its unmerged guard **per branch**: under `feature-branch` it deletes only `<plan-id>-execute` and **preserves** feature `<plan-id>`; under `main` it deletes `<plan-id>-execute` after merge. Teardown must never delete a still-needed feature branch.
Rationale: Leaving the primary on a plan branch reintroduces ambient-HEAD drift for the next plan; deleting a feature branch that still needs integration loses work.
Verification: `_worktree_teardown` branches on strategy; `test_worktree.py` asserts feature-branch preservation and execute-branch deletion.

## Crash Recovery (Resume Guard + Orphan Sweep)

REQ-RESUME-001: Before pouring or entering the coordinator loop, EXECUTE runs `plan_manager.py resume-scan` to detect whether the plan's epic already exists. Under intake-at-execute, `found=false` is the **normal first execution** — no epic has been poured yet — and execute pours the molecule (REQ-RESUME-004) then resolves the start gate. `found=true` means an epic already exists (a prior, possibly crashed, execute session); execute must **not** pour again and instead prompts the operator (resume vs. new) via `AskUserQuestion`, never fabricating a second epic. Detection is deterministic: `resume-scan` reads plan.md's `**Epic:**` field, falling back to a bead whose `metadata.plan_dir` matches.
Rationale: Relocating the pour to execute-start makes "epic absent" the expected first-run state rather than an anomaly. A single scan drives both the pour-once decision (absent → pour) and crash-resume (present → resume), unifying the former INTAKE duplicate-pour guard and the resume guard into one code path. Deterministic detection (persisted ID, metadata fallback) makes resume reliable even for plans intaken before the `**Epic:**` field existed.
Verification: SKILL.md §5.2/§5.3 branch on resume-scan `found` (absent → pour + resolve gate; present → resume prompt); `_resume_scan` in plan_manager.py resolves the epic via plan.md then metadata.

REQ-RESUME-002: On resume, the orphan sweep runs **strictly before the ready loop and before any reconcile-trigger evaluation**. The sweep **resets** stuck (`in_progress`/claimed) beads to `open` and **reports** — never auto-closes — any bead it cannot positively classify. No bead is ever auto-closed.
Rationale: The ready loop skips `in_progress` beads, so a crash silently strands them; resetting makes them re-workable. Auto-closing is unsafe — there is no bd-state signal separating disposable scratch from real `discovered-from` work — so the close decision stays with the operator.
Verification: SKILL.md §5.2 "Orphan sweep" and `agents/coordinator.md` → "Resume orphan sweep" specify reset-not-close and report-unclassifiable; ordering "before the ready loop and before reconcile-trigger evaluation" is stated in both.

REQ-RESUME-003: Resetting stuck beads (rather than closing them) keeps the epic non-terminal, so the reconcile gate cannot auto-fire on a resumed-but-incomplete plan.
Rationale: Closing the last stuck bead would satisfy the reconcile gate's "all execution beads closed" condition and trigger premature upstream reconciliation.
Verification: SKILL.md §5.2 and coordinator.md "Resume orphan sweep" both state reset keeps the epic non-terminal / prevents premature reconcile.

## Pour-once / Resume Gate (intake-at-execute)

REQ-RESUME-004: EXECUTE start has exactly **one** pour-once/resume decision point driven by `resume-scan`. `found=false` → pour the `plan-execute` molecule, write the epic↔plan linkage atomically (`record-epic` inserting the `**Epic:**` field **and** the epic's `metadata.plan_dir`) immediately after the pour, then resolve the start gate and continue. `found=true` → do **not** pour; run the resume path (worktree re-attach → orphan sweep → ready loop). The linkage write is atomic with the pour so a crash between them cannot orphan the epic.
Rationale: A single gate replaces the two historically separate guards — the INTAKE duplicate-pour guard and the EXECUTE resume guard — eliminating both the double-epic failure and the no-bead run. Writing the linkage immediately after the pour makes the pour crash-safe: a resumed session always re-finds the epic.
Verification: SKILL.md §5.3 pours only on `found=false` and calls `record-epic` immediately after `bd mol pour`; a second `/yf-plan execute` re-scans `found=true` and does not pour; `scripts/test_worktree.py` asserts single-pour (no second epic on re-execute).

## Completion Gate (ci-release deliverables, §6.4)

REQ-COMPLETE-001: The RECONCILE close step (§6.4) runs a fixed three-step order: **cascade-close → complete-gate → set complete**. `close_cascade.py` (REQ-PLAN-067) closes every all-terminal container bottom-up and fail-louds on any open plan-tree child; only if that succeeds does `plan_manager.py complete-gate` run; only if *that* passes does `update-status complete` run. The complete-gate is inserted **after** cascade-close and **before** the status transition, mirroring the `close_cascade.py` fail-loud contract (exit non-zero + JSON verdict halts completion).
Rationale: cascade-close and complete-gate are distinct concerns — container-closure vs. behavioral-validation — so complete-gate is its own verb, not folded into `close_cascade.py`. Ordering cascade-close first means the plan tree is already closed when complete-gate consults the out-of-tree deferred bead by label filter.
Verification: SKILL.md §6.4 calls `complete-gate` between the cascade-close block and `update-status complete`, halting on non-zero exactly as the cascade block does; `scripts/test_complete_gate.py` asserts the halt/pass/no-op verdicts.

REQ-COMPLETE-002: `complete-gate` is a strict **no-op** (clean pass) for a plan whose `deliverable_class` is `standard` or absent (REQ-PLAN-069a); it hard-gates only `ci-release` plans. For a `ci-release` plan it passes iff **either** a `log.md` `- validated:` bullet exists (REQ-PLAN-069b / REQ-DATA-016) **or** an open, out-of-tree bead with label `deferred-validation` + metadata `{"plan":"<plan-id>"}` exists; otherwise it halts with an actionable message (how to attest, or how to file the standalone deferred bead). At reconcile the `deliverable_class` is re-confirmable from the now-available merged-tree changed paths before the gate runs (paths may be absent at intake time — REQ-PLAN-069a).
Rationale: ordinary plans, whose deliverable is observable in merged-state validation (REQ-PLAN-060), are never gated — the criterion targets only runner-only-observable CI/infra/release behavior. The two satisfaction paths let an operator either attest a real green run or explicitly carry the unverified behavior forward as tracked debt.
Verification: `scripts/test_complete_gate.py` covers ci-release-halt-with-neither, pass-with-`validated:`-bullet, pass-with-out-of-tree-deferred-bead, and no-op-for-standard/absent.
