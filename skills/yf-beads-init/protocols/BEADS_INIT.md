# Beads Initialization & Health Protocol

Always-loaded trigger contract for the `yf-beads-init` skill. The procedure (verify/repair
engine, the wedged-migration fix, gitignore/hooks/permissions hardening, local-only config)
lives in the skill's `SKILL.md`; this rule binds only the triggers a description cannot
reliably catch. It is the shared **dependency-verification home** for every beads-backed
skill, and — as the sole skill-owned always-loaded beads surface — also carries the two
general bd-usage mandates below.

## Preflight trigger (all beads skills)

Before relying on `bd` in a repository — and as the first step of any beads skill's preflight
(`yf-plan`, `yf-research`, `yf-beads-upstream`, the `beads` loop) — the beads configuration must be
**verified functional**, not merely present. If verification fails, invoke `yf-beads-init`
(`beads_init.py verify`, then `repair`) before proceeding.

A beads config counts as needing `yf-beads-init` when, with `bd` on PATH, the repo config is:

- **non-existent** — no usable `.beads/` (`bd init` needed); or
- **incorrect** — outdated hooks, gitignore drift, stale DB metadata, wrong permissions; or
- **corrupted / wedged** — `bd status` fails while `bd ready`/`bd list` work.

## The false-negative invariant

**Never infer "bd not initialized" from `bd status`'s exit code alone.** `bd status --json`
can return an **error JSON with exit 0** (e.g. a pending schema migration blocked by a dirty
Dolt working set). Inspect the parsed JSON for an `error` key. An initialized-but-wedged repo
must be classified **corrupted** (repairable via `yf-beads-init`), never **not_initialized** —
the latter would wrongly send the operator to `bd init` and risk clobbering real data.

## Repair safety invariants

- The wedged-migration fix is `bd dolt stop` → `bd migrate schema` → `bd migrate`. Do **not**
  attempt `bd vc commit` first — it cannot open the wedged DB.
- Hardening (hooks, gitignore, metadata, perms, JSONL export) is idempotent and safe to re-run.
- For local-only repos, never add a Dolt remote or `bd dolt push`; assert
  `bd config set dolt.local-only true`. Upstream issue tracking routes to `yf-beads-upstream`.

## Silent no-op

When `beads_init.py verify` returns `ok`, this trigger is a **silent no-op** — do not prompt,
nag, or re-run repairs. Bootstrap/repair is offered only on an actual failure or explicit
`/yf-beads-init` invocation.

## General bd-usage mandates

Always-needed bd invariants with no other skill-owned home (folded from the retired orphan
rule `~/.claude/rules/BEADS.md`):

- **Use `bd` for ALL task tracking.** Never markdown TODOs, `TodoWrite`, or inline task lists.
  Issue-type/priority semantics and `bd create`/`bd dep`/`--json` mechanics route to the
  `yf-beads-extra` skill; the routine `bd ready` → `--claim` → `bd close` loop is the canonical
  `beads` skill.
- **Use non-interactive shell flags** so an `-i` alias can't hang on a confirmation prompt:
  `rm -f` / `rm -rf`, `cp -f`, `mv -f`; `ssh`/`scp -o BatchMode=yes`; `apt-get -y`;
  `HOMEBREW_NO_AUTO_UPDATE=1` for `brew`.

For the close-time / land-the-plane push (push open + deferred beads upstream before a session
or plan closes), see the `yf-beads-upstream` skill's companion rule `UPSTREAM_TRACKING.md` —
do not restate the sequence here.

For the verify/repair engine, the full repair sequence, and local-only setup, see the
`yf-beads-init` `SKILL.md`.
