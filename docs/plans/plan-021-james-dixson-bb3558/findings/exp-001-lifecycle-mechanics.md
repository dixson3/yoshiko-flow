# EXP-1 — yf-plan lifecycle mechanics (#47 crux)

**Question:** How do intake (the `bd mol pour`) and the worktree/branch lifecycle work today, and how
invasive is the full #47 model (relocate pour to execute-start; named branches; pinned base;
landing-strategy config)?

**Method:** read-only map of `~/.claude/skills/yf-plan/` — `scripts/plan_manager.py` (Click CLI),
`SKILL.md`, `formulas/plan-execute.formula.toml`, `spec/`, `scripts/test_worktree.py`.

## Findings

### Root cause confirmed (one line)
`_worktree_ensure` (`plan_manager.py:1115`) does `git worktree add <path> -b <branch>` with **no
start-point** → base = whatever the primary checkout's HEAD is. `branch = plan_id` verbatim
(`:1087`). There is **no `git checkout`/`switch`/`merge`/`pull` anywhere in the script** — the entire
branch topology (merge target, base) is orchestrated by **SKILL.md main-session bash**, not script
logic. The script only does `worktree add/remove`, `branch -d/-D`, `worktree prune`.

### Topology is ambient, not hardcoded-main
SKILL §6.1 merge-back (`git merge --no-ff "${plan_id}"`, no preceding `git checkout main`) merges the
plan branch into **whatever branch is currently checked out**. So there are **two** ambient-HEAD
dependencies to fix for #47: (a) the worktree base (`:1115`) and (b) the merge target (§6.1). Fixing
only one half-closes the issue.

### Pour relocation = SKILL prose + guard-collapse, no new verbs
The pour happens today at approval (SKILL §4.2, "On operator approval"). §4.2–4.6 create the whole
bead DAG (epic, start-gate task+gate pair, child epics/issues, upstream metadata, reconcile gate/step)
and persist the plan↔epic linkage (`record-epic` writes `**Epic:**` + an inert `intake:` phase-log
line; plus a `metadata.plan_dir` stamp). Relocating means moving §4.2–4.6 into Phase 5 (execute-start,
before/at §5.3 gate-resolve). The `record-epic`/`resume-scan`/`metadata.plan_dir` mechanics are reused
verbatim — only the **timing** changes. No new plan_manager verb is strictly required for the move.

**Guard collapse:** today two guards enforce pour-once across the session boundary — §4.2
(duplicate-pour) and §5.2 (`resume-scan found`). Post-relocation they become one branch at
execute-start: **epic absent → pour; epic present → resume**. `record-epic` must be written
atomically right after the relocated pour or a crash strands an unlinkable epic.

### Config surface is trivially extensible
`.yf-plan.local.json` read by `_read_config()` (`:637`). Existing keys: `ignore-skill`,
`execute.worktree` (`_worktree_opted_out`, `:953`), `validate-cmd` (`_resolve_validate_cmd`, `:968`).
A new `landing-strategy` (main|feature-branch) key = one constant + one resolver parallel to
`_resolve_validate_cmd`, consumed by `_worktree_ensure` (base) and SKILL §6.1 (merge target).

### The formula is minimal
`plan-execute.formula.toml` pours exactly **one** bead: a human start-gate (yields the task-wrapper +
gate-bead pair via `id_mapping` keys `plan-execute.start-gate` / `plan-execute.gate-start-gate`).
Everything else is injected dynamically by SKILL §4.3–4.6. The formula travels with whichever phase
calls `bd mol pour` — no formula change needed for relocation.

### Test surface
`test_worktree.py` (477 lines, pytest) covers path/id, gitignore idempotency, viability fallbacks,
ensure/teardown idempotency, landing-lock contention/reclaim, validate-merged tiers. **No test pins
the worktree base commit** — #47 adds test surface (assert base == configured base, not HEAD) rather
than modifying much. Tests do **not** tag REQ ids.

## Synthesis — minimal change set (by file)
1. `plan_manager.py _worktree_ensure:1115` — pin base start-point from `_resolve_landing_strategy()`.
2. `plan_manager.py` branch helpers (`_plan_id_from_dir:979`, `_worktree_path:986`, teardown `:1162`)
   — introduce `<plan-id>-development` / feature `<plan-id>` / `<plan-id>-execute` (today all bare
   `plan_id`).
3. `plan_manager.py` config (~`:949`) — `CONFIG_KEY_LANDING_STRATEGY` + `_resolve_landing_strategy()`.
4. `SKILL.md` — move §4.2–4.6 to Phase 5 execute-start; unify the §4.2/§5.2 pour-once guards; rewrite
   §6.1 to pin merge target per strategy + commit-plan-after-portability + restore-default-checkout
   between phases; Phase 1 planning worktree.
5. `spec/phases.md` — REQ-PHASE-002 / REQ-RESUME-001 reworded (gate created at execute; found=false now
   means not-yet-poured) + new REQ; base-pinning + landing-strategy REQ.
6. `test_worktree.py` — base-pin test + named-branch + strategy-switch; tag REQ ids.

## Top risks
1. **Ambient-checkout/merge-target.** Two separate ambient-HEAD deps (base + merge target). "Restore
   default checkout between phases" is what makes ambient state deterministic.
2. **Pour-once guard collapse.** Merging §4.2 + §5.2 wrong reintroduces double-epic (failure #2) or a
   no-bead fresh run. Linkage must be atomic post-pour.
3. **Branch-name collision & teardown.** Feature `<plan-id>` (landed) vs `<plan-id>-execute` (worktree)
   must not reuse the single `plan_id` the script assumes in 3 places; teardown's `branch -d`
   unmerged-refusal must point at the right ref per strategy.
