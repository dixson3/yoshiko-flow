# Upstream #39: beads: auto-canonicalize yf projects on preflight/init (strip stray hooks, untrack runtime jsonl) — upstream sink is the only knob

- **Number:** 39
- **Title:** beads: auto-canonicalize yf projects on preflight/init (strip stray hooks, untrack runtime jsonl) — upstream sink is the only knob
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement, type::feature

## Body

## Summary

When a beads preflight runs — or `/yf-beads-init`, `/yf-beads-extra`,
`/yf-beads-upstream`, or `/yf-beads-hygiene` is invoked — yf-enabled repos should
be **canonicalized automatically** to the standard local-only + upstream-sink end
state. Today the cleanup is partly manual: a real session (rc-files,
2026-06-24) found several stray artifacts that `yf doctor --repair` did **not**
remove, and the operator had to drive the rest by hand.

Goal: a fresh or drifted yf project converges to the canonical state with **zero
per-project manual cleanup**. The *only* configuration knob should be the choice
of upstream sink (github now; gitlab/jira/linear are future, not yet enabled).

## Canonical end state (the target invariant)

For every yf-enabled repo, after preflight/init/repair:

- **Dolt local-only:** `dolt.local-only true`, `bd dolt remote list` empty, no
  `sync.remote`. No git-sync of the DB.
- **Upstream sink configured (one choice):** `custom.upstream.enabled true` +
  `custom.upstream.backend <github|...>` with the backend's owner/repo keys.
  GitHub is the only enabled backend today; gitlab/jira/linear are stubs/future.
- **No stray git hooks:**
  - `core.hooksPath` at the git default (not explicitly pinned).
  - No beads `bd hooks run …` shims tracked under `.beads/hooks/*`.
  - No beads-installed `.claude/settings.json` (the `bd prime` PreCompact/
    SessionStart hooks) — pruned if the file becomes empty.
  - No `.codex/`, no `.agents/skills/beads/`, no managed blocks in CLAUDE.md/AGENTS.md.
- **No stray jsonl / runtime artifacts tracked in git:**
  - `.beads/interactions.jsonl` (runtime activity log, declared "not versioned"
    in `.beads/.gitignore`) must be **untracked** (`git rm --cached`) — it is
    often tracked from before the ignore rule existed and churns on every change.
  - Dolt artifacts (`embeddeddolt/`, `backup/`, `export-state.json`,
    `push-state.json`, `dolt-server.*`) stay gitignored + untracked.
  - `.beads/issues.jsonl` handling follows the chosen durability model (default:
    GitHub-Issues-only → leave it excluded via `.git/info/exclude` fork
    protection; do not commit beads data).

## Gaps found in the live session (what repair missed)

`yf doctor --repair --local-only` did the config flip and most cruft removal, but
the operator still had to manually:

1. `git rm --cached .beads/interactions.jsonl` — repair added the ignore rule but
   left the already-tracked runtime log tracked (so it kept showing as modified).
2. `git rm .beads/hooks/*` — 5 dormant `bd hooks run` shims remained **tracked in
   git** even after `bd hooks uninstall` + `core.hooksPath` reset. Repair de-wires
   hooks but does not remove the tracked shim files.
3. Remove the Dolt remote / `sync.remote` — the repo had an active `git+ssh`
   git-sync remote auto-pushing the whole DB every 15 min; `--local-only` asserted
   the flag but the operator confirmed+removed the remote interactively.

## Proposed work

- Extend the repair/canonicalize engine so a single preflight/repair pass reaches
  the full end state above — specifically **untracking** (not just gitignoring)
  runtime jsonl, and **removing tracked `.beads/hooks/*` shims**, idempotently.
- Make the upstream-sink choice the sole interactive decision; everything else is
  derived/automatic. Default-deny stays (sink unconfigured ⇒ disabled).
- Ensure all four entry points (preflight, `yf-beads-init`, `yf-beads-extra`,
  `yf-beads-upstream`, `yf-beads-hygiene`) route through this same canonicalization
  so any of them converges a drifted repo.
- Keep every step idempotent and a no-op on an already-canonical repo (no churn,
  never re-install hooks).

## Acceptance

- A drifted yf repo (tracked interactions.jsonl, tracked `.beads/hooks/*`, a Dolt
  git-sync remote, a `bd prime` `.claude/settings.json`) converges to the canonical
  end state in one repair pass with no manual `git rm`.
- An already-canonical repo: repair is a clean no-op.
- Re-running across many yf projects "automagically" canonicalizes each, with the
  only variation being the configured upstream backend.

---
Filed from a live rc-files session (2026-06-24) where this cleanup was done by hand.

