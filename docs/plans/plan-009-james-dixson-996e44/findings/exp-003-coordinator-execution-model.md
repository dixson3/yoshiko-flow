# Finding INV-3: coordinator & sub-agent execution model relative to the worktree

**Date:** 2026-06-14 · **Method:** read bdplan SKILL.md, coordinator.md, agent docs, formula, harness tool schemas

## Result

**1. Current dispatch & cwd.** The coordinator (`coordinator.md:40-51`) is a single-session
ready-loop, not a per-bead worktree fan-out. Most beads execute **inline**; only beads whose
metadata names an `agent` file spawn a sub-agent — and EXECUTE sub-agents specify **no
isolation** (contrast INVESTIGATE §268 which uses `isolation="worktree"`). **cwd today is the
repo root**: all `bd`, `git status`, the §6.2 push sequence, and `git add "${plan_dir}"
.beads/` are repo-root-relative. The phase model + formula have no worktree concept.

**2. The two worktree models / the tension.** Harness `isolation="worktree"` gives each agent
its **own disposable, auto-cleaned** worktree on its **own** branch under `.claude/worktrees/`
("No code from this worktree lands in the project"). plan-009 needs **one persistent** plan
worktree shared by the whole execution, on branch `<plan>`, merged back at land time. If
EXECUTE sub-agents each used `isolation`, their edits would scatter across N throwaway
branches and evaporate — never accumulating on `<plan>`. Isolation's lifecycle (auto-clean)
and topology (per-agent/per-branch) both contradict plan-009's needs.

**3. Recommended execution model: option (a).** Coordinator + all execution run with
**cwd = `.worktrees/<plan>`**, NOT per-agent harness isolation. Coherent with the existing
single inline driver: every inline `bd close`/edit/commit lands on `<plan>` automatically.
INV-2 confirms `bd` works natively from inside the worktree (one shared DB). Agent-backed
beads (e.g. reconciler) must **inherit the same cwd** (mechanism (b)); explicitly forbid
`isolation="worktree"` for EXECUTE sub-agents (reserve it for INVESTIGATE).

**4. Harness primitives vs explicit `git worktree`: use explicit `git worktree`.** Harness
`EnterWorktree`/`ExitWorktree`/`isolation` worktrees are disposable (`.claude/worktrees/`,
auto-clean, session-end keep/remove prompt) — wrong lifecycle for a persist-then-merge plan
worktree, and `EnterWorktree` is gated on explicit user instruction. A bdplan-managed
`git worktree add .worktrees/<plan> <plan>` persists regardless of harness/session lifecycle,
is gitignored (INV-1), torn down by explicit bdplan teardown, and is portable across harnesses
(AGENTS.md requirement). Optional ergonomic: a sub-agent MAY `EnterWorktree(path=...)` to enter
the existing bdplan worktree, but passing cwd achieves the same without coupling. **Create &
teardown stay explicit `git worktree`.**

**5. Lifecycle → phase mapping.**
- **CREATE** at EXECUTE **§5.3** (resolve start gate, fresh runs only): `git worktree add
  .worktrees/<plan> -b <plan>` → launch coordinator (§5.4) with cwd = worktree.
- **MERGE-BACK + TEARDOWN** at RECONCILE **§6.1/§6.2**: re-validate on `<plan>`; propose
  `git merge <plan>` + push under existing conservative authority; `git worktree remove` after
  authorized merge; close at §6.4.

**6. Resume (§5.2).** §5.2 already bypasses §5.3 on resume, so the fresh `add -b` is correctly
skipped. Resume path must **re-attach**: `git worktree add .worktrees/<plan> <plan>` WITHOUT
`-b` (idempotent: if `git worktree list` already shows it, just set cwd). Orthogonal to the
orphan sweep (a `bd`-DB op) — compose: re-attach worktree → orphan sweep → loop. **Gap the
current docs don't cover (plan-009 must close):** a prior session may crash mid-merge or leave
**uncommitted** changes in the worktree — add a resume-time `git -C .worktrees/<plan> status
--porcelain` check that surfaces dirty/un-merged state to the operator rather than proceeding.

## Implications for Plan
- Single shared worktree via cwd; explicit `git worktree` for create/re-attach/teardown; NOT
  harness primitives.
- Touch points: SKILL.md §5.3 (create), §5.2 (re-attach + dirty check), §5.4 (launch with
  cwd), §6.1/§6.2 (merge+teardown), coordinator.md step 5 (sub-agents inherit cwd, no isolation).
