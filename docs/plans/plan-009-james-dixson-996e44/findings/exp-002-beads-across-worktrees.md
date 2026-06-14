# Finding INV-2: beads (bd / dolt) behavior across git worktrees

**Date:** 2026-06-14 · **Method:** clean /tmp experiment, bd 1.0.5 + dolt 2.1.6

## Result — ONE shared DB, native worktree support (favorable)

A bead created from the worktree and a claim made from the worktree were immediately
visible from the primary checkout with no sync step. Direct Dolt query on the primary DB
confirms it holds all issues regardless of which working tree issued the command.

**Resolution mechanism:**
- The Dolt DB lives in `.beads/embeddeddolt/` in the **primary** working tree, which is
  **gitignored** (`.beads/.gitignore` ignores `dolt/`, `embeddeddolt/`). The worktree's
  checked-out `.beads/` has NO `embeddeddolt/` of its own.
- `BD_DEBUG=1 bd list` from the worktree shows bd loading config from BOTH the worktree and
  primary `.beads/config.yaml`. bd detects the worktree (`git rev-parse --git-common-dir` →
  primary `.git`) and routes DB access to the primary's `.beads/`.
- `.beads/.gitignore` documents a `redirect` file ("relative path to main repo's
  `.beads/`") — bd has **first-class, intentional worktree support**.

**No merge-back / JSONL conflict risk (this setup):** bead state is NOT in git — it's the
gitignored Dolt DB only. In bd 1.0.5 default config, `bd export` goes to stdout, NOT an
auto-written tracked `issues.jsonl`. Both branches track identical `.beads/` files
(config/hooks/metadata). No per-branch divergent bead-state file → nothing to conflict on
merge-back; bead state is branch-independent.

**All ops work from the worktree:** list, ready, create, update --claim, close, show — all
land in the shared DB.

## Implications for Plan (plan-009)
- The core worry is resolved favorably: **bead writes always land in the single primary
  DB regardless of which worktree runs `bd`.** Tracking is automatically correct across the
  boundary; the coordinator need NOT marshal bead ops back to the primary.
- No "two DBs / divergent per-branch issue state" failure mode to design around.
- Beads created/closed during execution are not tied to the plan branch and won't
  appear/disappear on merge — desired for cross-session tracking.

## Recommendations
- **Coordinator MAY run all `bd` ops directly inside the plan worktree.** Simpler
  architecture; bd supports it natively.
- **Preconditions to assert** in `bdplan execute`:
  1. The worktree is a real `git worktree` of the primary (shares `--git-common-dir`), NOT
     an independent clone (a clone gets its own DB).
  2. The primary's `.beads/embeddeddolt/` exists and is healthy before spawning the
     worktree (route through `beads-init` verify if unsure).
- **Do not** `rm -rf` / deep-clean the primary `.beads/` while a worktree is live — shared.
- **Concurrency caveat (flag, not blocking):** all worktrees write the same embedded Dolt
  DB through one `.lock`. Sequential writes tested fine. If plan-009 ever runs
  bead-writing agents in PARALLEL processes against the same DB, validate lock behavior.
- **Version caveat:** verified on bd 1.0.5 (JSONL export to stdout, not tracked). If a
  future bd/config enables auto-export to a git-tracked `issues.jsonl`, re-test the
  per-branch divergence question.
