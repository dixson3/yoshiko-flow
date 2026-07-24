`yf-beads-init` verifies, initializes, and repairs a working beads (`bd`) configuration
in a repository. It is the shared dependency-verification home the other beads skills
route to: when [`/yf-plan`](/skills/yf-plan/), [`/yf-research`](/skills/yf-research/),
or [`yf-beads-upstream`](/skills/yf-beads-upstream/) runs its preflight and finds
missing tools, an uninitialized repo, or a corrupted DB, it sends the operator here.
You also invoke it directly when standing up beads in a new repository. Once `bd` is
healthy — `yf preflight yf-beads-init --json` returns `ok` — you do not need it; routine
issue operations use the canonical `beads` skill.

## The correction that matters most

`bd status --json` can return an **error JSON with exit code 0**. A preflight that
trusts the exit code, or that maps any `bd status` failure to "not initialized",
produces a false negative: the repo *is* initialized, just wedged. The classic
signature is that `bd ready`, `bd list`, and `bd create` all work, but `bd status`
returns `{"error": "…pending schema migrations…"}` and `bd doctor` shows the DB version
behind the CLI version. Verification inspects the parsed JSON for an `error` key
instead of trusting the exit code, so it classifies this as `corrupted` (repairable),
never `not_initialized`. That distinction is load-bearing: misclassifying a wedged repo
as uninitialized would send the operator to `bd init` and risk clobbering real data.

## The engine

The verify/repair engine lives in the `yf` kernel. You drive it through `yf`:

| Command | What it does |
| :------ | :----------- |
| `yf preflight yf-beads-init --json` | read-only health check — the canonical "is bd usable?" |
| `yf doctor --repair` | apply the standard repairs |
| `yf doctor --repair --local-only` | also assert local-only Dolt (no remote) |
| `yf doctor --repair --local-only --remove-remote` | also clear any configured Dolt remote |
| `yf doctor` | one-line human status |

The preflight carries the richer beads verdict — `status ∈ {ok, deps_missing,
not_initialized, corrupted}` with diagnostics and remediations — in its output.

## The procedure

1. **Verify.** Run the preflight and branch on `status`. `ok` — nothing to do.
   `deps_missing` — install the listed tools and stop. `not_initialized` — no usable
   `.beads/`; confirm intent, then repair runs a cruft-suppressed init.
   `corrupted` — initialized but wedged; go to repair.
2. **Repair.** `yf doctor --repair` applies the standard fixes in order.
3. **Re-verify.** Run the preflight again and expect `ok`, then `bd doctor` for zero
   errors. `Remote Consistency: No remotes configured` is accepted by design when the
   repo is intentionally local-only.

The central repair is the wedged schema migration, and it is **mode-aware**. It flushes
the working set, then runs `bd migrate schema` (applies pending migrations) followed by
a bare `bd migrate` (updates the DB metadata version). The flush differs by storage
mode:

- **Server mode** — `bd dolt stop` flushes and clears the in-memory Dolt working set.
- **Embedded storage** (`.beads/embeddeddolt/`, no server) — there is no server to
  stop, so repair commits the working set directly with a data-preserving raw
  `dolt add -A && dolt commit`, never a `reset --hard`. A clean tree is a no-op.

`bd migrate schema` always fails against a dirty set, so the flush must come first.

## Cruft suppression

`bd init`'s defaults inject boilerplate that fights these conventions — beads git
hooks, managed blocks in `CLAUDE.md` and `AGENTS.md`, a `.codex/` directory, and a
`.claude/settings.json` hook. yf-beads-init suppresses all of it at init time with
`bd init --skip-hooks --skip-agents`, then sets `dolt.local-only true` and silences the
now-irrelevant git-hooks doctor warning. On an already-dirtied repo, repair runs the
idempotent bd-native removers — every one a no-op on a clean repo, so re-running repair
never churns and never re-installs hooks. Repair only ever *removes* hooks; it never
installs them.

## Local-only repositories

yf beads are intentionally local-only: issues live upstream in an issue tracker, not in
a Dolt remote. Repair asserts `bd config set dolt.local-only true` under `--local-only`
and never *adds* a Dolt remote. The opt-in `--remove-remote` flag (valid only alongside
`--local-only`) is the one step that *clears* an existing remote. This matters on
`bd` ≥ 1.1.0, where a state-aware remote-migrate gate treats a configured remote as
remote-backed and refuses to auto-apply pending schema migrations — wedging `bd status`
on the next upgrade even with `dolt.local-only true` set. For a genuinely local-only
repo the fix is to hold no remote. Upstream issue tracking is
[`yf-beads-upstream`](/skills/yf-beads-upstream/)'s job, not a Dolt remote's.
