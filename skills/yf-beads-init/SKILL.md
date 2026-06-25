---
name: yf-beads-init
description: >
  Verify, initialize, and repair a functioning beads (`bd`) configuration in a repository,
  and the shared dependency-verification home that other beads skills' preflights route to.
  TRIGGER when: /yf-beads-init invoked; a repository is being set up for beads and `bd` is
  present but the repo's beads configuration is **non-existent, incorrect, or appears
  corrupted** (e.g. `bd status` errors, `bd doctor` reports errors, a wedged schema
  migration, or `bd ready`/`bd list` work while `bd status` does not); or another beads
  skill's preflight reports `system_deps_missing` / `bd_not_initialized` / a corrupted DB.
  SKIP when: bd is healthy (`yf preflight yf-beads-init --json` returns `ok`) and you only
  need routine issue operations (use the `beads` skill); for direct-CLI gotchas use `yf-beads-extra`.
user-invocable: true
skill-group: beads
depends-on-tool: [bd, uv, git]
depends-on-skill: [yf-beads-extra]
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
preflight:
  companion-rule: BEADS_INIT.md
  min-bd-version: 1.0.5
  config-basename: .yf-beads-init.local.json
---

# yf-beads-init

The dependency-verification and repair home for a functioning beads configuration. Other
beads-backed skills (`yf-plan`, `yf-research`, `yf-beads-upstream`, …) verify prerequisites in
their own preflight; when that preflight reports missing deps, an uninitialized repo, or a
corrupted DB, it routes here. This skill is also invoked directly when standing up beads in a
new repository.

## SKILL_DIR

```bash
GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo .)
SKILL_DIR=$(find ~/.claude/skills ~/.agents/skills "$GIT_ROOT/.claude/skills" "$GIT_ROOT/.agents/skills" .claude/skills .agents/skills -maxdepth 1 -name yf-beads-init -type d 2>/dev/null | head -1)
[ -z "$SKILL_DIR" ] && { echo "ERROR: yf-beads-init skill directory not found"; exit 1; }
```

## The engine

The verify/repair engine moved into the `yf` kernel (plan-010); invoke it via `yf`:

```bash
yf preflight yf-beads-init --json     # READ-ONLY health check (canonical "is bd usable?")
yf doctor --repair                    # apply the standard repairs
yf doctor --repair --local-only       # also assert local-only Dolt
yf doctor --repair --local-only --remove-remote  # also CLEAR any configured Dolt remote
yf doctor                             # one-line human status
```

`yf preflight yf-beads-init --json` is the canonical preflight check; the richer beads
verdict (`status ∈ {ok, deps_missing, not_initialized, corrupted}` with `diagnostics` and
`remediations`) is carried in its output. The retired `scripts/beads_init.py` is now a thin
shim that points stale callers at these `yf` commands.

## The one correction that matters most

`bd status --json` can return an **error JSON with exit code 0**. A preflight that trusts the
exit code — or that maps any `bd status` failure to "not initialized" — produces a **false
negative**: the repo *is* initialized, just wedged. The classic signature:

- `bd ready` / `bd list` / `bd create` all work, **but** `bd status` returns
  `{"error": "...pending schema migrations alter pre-existing dirty tables..."}`.
- `bd doctor` shows the DB version behind the CLI version.

`verify` inspects the parsed JSON for an `error` key instead of trusting the exit code, so it
classifies this as `corrupted` (repairable), never `not_initialized`.

## Procedure

1. **Verify.** Run `yf preflight yf-beads-init --json`. Branch on the beads `status`:
   - `ok` — nothing to do.
   - `deps_missing` — install the listed tools (`bd` ≥ 1.0.5, `uv`, `git`); stop.
   - `not_initialized` — no usable `.beads/`. Confirm intent, then `yf doctor --repair` runs
     `bd init --skip-hooks --skip-agents` (cruft-suppressed init, see below), then go to step 3.
   - `corrupted` — initialized but wedged/broken; go to step 2.
2. **Diagnose & repair.** Run `yf doctor --repair` (add `--local-only` to also assert local-only
   Dolt; add `--remove-remote` to additionally CLEAR a configured remote — see below). The
   standard repairs, in order:
   - **Wedged schema migration** (the common case): `bd dolt stop` flushes and clears the
     in-memory Dolt working set; then `bd migrate schema` applies pending migrations; then
     bare `bd migrate` updates the DB metadata version. *Do not* try `bd vc commit` first —
     it cannot open the wedged DB (chicken-and-egg).
   - **Permissions:** `chmod 700 .beads` (bd warns at `0750`).
   - **Git hooks:** repair **never installs** beads git hooks. The former
     `bd hooks install --force` step was removed (#31) — it contradicted cruft suppression
     and re-dirtied a clean repo. Repair only ever *removes* hooks (next bullet).
   - **Gitignore drift:** `bd doctor --fix`, then top up any patterns it misses (the engine
     adds them): `.beads/.gitignore` ← `.env, export-state.json, embeddeddolt/, proxieddb/,
     dolt-server.activity, daemon.*, *.lock, *.corrupt.backup/, .beads-credential-key,
     proxied_server_client_info.json`; project `.gitignore` ← `.beads-credential-key,
     .beads/proxieddb/`.
   - **Portable record:** `bd export -o .beads/issues.jsonl` (ensure it is **not** gitignored).
   - **Cruft cleanup (#31, idempotent — no-op on a clean repo):** `bd hooks uninstall` +
     reset `core.hooksPath` to the git default; `bd setup claude --remove` (CLAUDE.md managed
     block + the entry-scoped `.claude/settings.json` hook); `bd setup codex --remove`
     (`.agents/skills/beads/`, the codex AGENTS.md block, `.codex/`); `rm -rf
     .agents/skills/beads/` (residual); a **marker-scoped** strip of the
     `<!-- BEGIN/END BEADS INTEGRATION -->` / `BEADS CODEX SETUP` blocks from CLAUDE.md &
     AGENTS.md; an **entry-scoped** `.claude/settings.json` prune (deleted **only if it
     becomes empty** — never wholesale, so it can't clobber a recommended-settings baseline);
     and a `.codex/config.toml` prune (deleted **only if effectively empty** — the bare
     `[features]` residual `bd setup codex --remove` leaves behind once it strips `hooks =
     true`; never a config that still holds a real key).
   - **Canonicalization cleanup (#39, idempotent — no-op when nothing is tracked):** `git rm
     --cached` the pinned runtime/derived `.beads/` set so it is never committed (working files
     are kept): `.beads/interactions.jsonl`, `.beads/embeddeddolt/`, `.beads/backup/`,
     `.beads/export-state.json`, `.beads/push-state.json`, and any tracked `.beads/dolt-server.*`.
     Remove tracked `.beads/hooks/*` files **only** when their content carries the `bd hooks run`
     shim signature (a hand-edited hook is never removed). And — **only** under
     `--local-only --remove-remote` — clear the Dolt `sync.remote` config (see below).
3. **Re-verify.** Run `yf preflight yf-beads-init --json` again; expect `ok`. Then `bd doctor` — 0 errors. Classify
   remaining warnings: *accepted by design* vs *actionable*. `Remote Consistency: No remotes
   configured` is **accepted** when the repo is intentionally local-only (resolving it would
   add a Dolt remote); `Dolt Status` / `Git Working Tree` warnings are transient (clear on
   commit).

## Cruft suppression & cleanup (#31)

`bd init`'s defaults inject boilerplate that fights our conventions (AGENTS.md hand-authored;
manual `bd dolt push`; no beads git hooks). yf-beads-init suppresses it at init time and cleans
it on repair:

- **Init-time suppression** (`not_initialized` path): `bd init --skip-hooks --skip-agents`
  suppresses all four cruft classes in one shot — beads git hooks; the CLAUDE.md/AGENTS.md
  managed blocks; `.codex/`; `.agents/skills/beads/`; and the `.claude/settings.json`
  SessionStart hook. Then `bd config set dolt.local-only true` (no Dolt remote) and
  `bd config set doctor.suppress.git-hooks true` (silence the doctor warning now that hooks
  are intentionally absent).
- **Repair-time cleanup** (already-dirtied repos): the idempotent, bd-native removers listed in
  step 2's "Cruft cleanup" bullet. Every remover is a no-op on a clean repo, so re-running
  repair never churns and never re-installs hooks.
- **Reference target:** this repo is the "correct" end state — `core.hooksPath` at the git
  default, no `.codex/`, no `.agents/skills/beads/`, no beads `.claude/settings.json` hook, and
  AGENTS.md hand-authored (no beads managed block).

## Local-only repositories

When beads is intentionally local-only (issues live upstream, e.g. GitHub, not in a Dolt
remote): `bd config set dolt.local-only true`, keep `bd dolt remote list` empty, and never
`bd dolt push`. `yf doctor --repair --local-only` sets the flag.

Repair never *adds* a Dolt remote. The opt-in `--remove-remote` flag (valid only alongside
`--local-only`) is the one repair step that *clears* an existing remote: when a non-empty
`sync.remote` is configured under local-only, `yf doctor --repair --local-only --remove-remote`
unsets it (a no-op when no remote is set). It is OFF by default — without `--remove-remote`,
repair leaves any configured remote untouched. Upstream issue tracking is the `yf-beads-upstream`
skill's job.

## As a preflight dependency for other beads skills

This skill is the home for "is bd usable here?". A beads skill's preflight should:

1. Run its own system-deps + rule checks.
2. On a beads-config failure (`bd_not_initialized`, a corrupted DB, or a `bd status` error
   JSON), route the operator to `/yf-beads-init` (or run `yf preflight yf-beads-init --json`
   / `yf doctor --repair`) rather than re-deriving the repair steps. The always-loaded companion rule
   `protocols/BEADS_INIT.md` carries this trigger so it fires regardless of which skill is
   active. It also folds in two general bd-usage mandates (use-bd-for-all-tracking;
   non-interactive shell-flag safety) consolidated from the now-retired orphan rule
   `~/.claude/rules/BEADS.md` — an unowned user-scoped rule no skill installed or upgraded.
   That orphan is retired by a manual `rm -f ~/.claude/rules/BEADS.md` after install (it is
   not repo-tracked; CLI detail routed to `yf-beads-extra`, the land-the-plane push stays in
   `yf-beads-upstream`'s `UPSTREAM_TRACKING.md`).

## Reference skills

- **`beads`** — routine `bd` loop once the config is healthy.
- **`yf-beads-extra`** — direct-CLI gotchas (issue types, dep edges, `--json` parsing).
- **`yf-beads-upstream`** — push open/deferred beads to a GitHub/GitLab/Jira tracker (local-only DB).
