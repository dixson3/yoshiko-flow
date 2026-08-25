# plan-052 — deploy verification (SC24)

Recorded **after** the final commit and a rebuild, per Issue 7.5. Deploy is the **first point**
`yf self install` is permitted (R6/R7): this plan edits the skill it executes under, and
`plan_manager.py` is re-invoked per call, so a mid-execution deploy would run **new scripts
against old prose**.

## Evidence

| Fact | Value | How it was obtained |
| :-- | :-- | :-- |
| Merge commit | `53e1a87` | `git rev-parse --short HEAD` |
| Stamp BEFORE deploy | `ee2a449-dirty` | `yf --version` |
| Stamp AFTER deploy | `53e1a87` | `yf --version` |
| Stamp matches HEAD | yes | `ctl-deploy-stamp` |
| Harnesses synced | claude-code, agents, codex, opencode, pi | `yf self install --from-build --force` |
| Deployed tree vs source | no drift | `ctl-deploy-stamp` |

The config half was **not** authorized: `--allow-permissions-write` was deliberately not
passed, so skills and the rules aggregate deployed while harness config was left alone.

## Two corrections to `ctl-deploy-stamp`, both made here

The control was measuring **deployment artifacts as drift**. Both fixes narrow what it
inspects; neither weakens what it catches, and that was verified by execution — injecting a
real one-line change into a deployed script makes it exit **1**, and reverting returns it to
**0**.

1. **The injected provenance banner.** The installer adds
   `<!-- yf-skills: v=... tree=... -->` to every deployed `SKILL.md` **by design**. It is
   present in the deployed copy and absent from source **by construction**, so a naive diff
   reported *every* skill as drifted on *every* deploy — measured at 4 skills, where that one
   line was the **only** content difference in each. A control that fires on its own deployment
   mechanism reports a constant, and a constant carries no information.
2. **Binaries were being grepped.** The banner filter ran over `*.png` too, mangling both sides
   differently and reporting a difference on `spec/worktree-execute-lifecycle.png` where `cmp`
   says the files are **byte-identical**. Only `.md` files are normalized now; everything else
   is compared with `cmp`.

`__pycache__`, `.pytest_cache` and `*.pyc` are excluded as build and test residue.
