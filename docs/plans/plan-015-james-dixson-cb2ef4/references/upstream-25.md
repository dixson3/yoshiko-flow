# Upstream #25: Doc guidance: use 'env -u VIRTUAL_ENV uv run …' when running uv inside a git worktree

- **Number:** 25
- **Title:** Doc guidance: use 'env -u VIRTUAL_ENV uv run …' when running uv inside a git worktree
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Context

When executing work inside a git **worktree** (e.g. bdplan's `.worktrees/<plan-id>` execution worktree), `uv run` emits:

\`\`\`
warning: \`VIRTUAL_ENV=/path/to/primary/.venv\` does not match the project environment path \`.venv\` and will be ignored; use \`--active\` to target the active environment instead
\`\`\`

This happens because the parent shell exports `VIRTUAL_ENV` pointing at the **primary** checkout's `.venv`, while `uv run` in the worktree resolves the **worktree's** own `.venv`. uv correctly ignores the stale `VIRTUAL_ENV` and uses the worktree env — so it is **harmless** (the right environment is used), but the warning is noisy.

## Guidance to document

When running `uv` inside a worktree, drop the inherited var:

\`\`\`bash
env -u VIRTUAL_ENV uv run …
\`\`\`

(or `deactivate` the shell venv before working in the worktree).

**Do NOT** follow uv's suggested `--active` here — that forces the *primary* checkout's venv, which typically lacks the worktree's editable install, and is wrong inside a worktree.

## Where

Add to the worktree / bdplan execution guidance docs (the address-space model section that covers running commands inside `.worktrees/<plan-id>`).
