# Upstream Issue Triage: shared package active-set classifier duplication

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #15 — Consolidate duplicated Python helpers across skills (PEP 723 shared package route)

> ## Context

The `shutil.which`-based tool-presence check is duplicated across at least three places:
`install.py`, `skills/bdplan/scripts/plan_manager.py` (`_SYSTEM_DEPS`), and
`skills/bdresearch/scri...

**Disposition:**
**Notes:**

## #27 — yf-change-validation: per-repo change-set validation skill (supersede static validate-cmd)

> Spun out of plan-011's land-the-plane follow-up (bead `beads-skills-tr0`). Forward design — not yet scoped into a plan.

## Problem

plan-011 added `validate-cmd` to `.bdplan.local.json` so yf-plan's ...

**Disposition:**
**Notes:**

## #25 — Doc guidance: use 'env -u VIRTUAL_ENV uv run …' when running uv inside a git worktree

> ## Context

When executing work inside a git **worktree** (e.g. bdplan's `.worktrees/<plan-id>` execution worktree), `uv run` emits:

\`\`\`
warning: \`VIRTUAL_ENV=/path/to/primary/.venv\` does not ma...

**Disposition:**
**Notes:**
