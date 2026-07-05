# Upstream #58: Define + enforce a canonical 'minimal local' beads profile (embedded/local-server, per-project, local-only, worktree-shared) via yf preflight

- **Number:** 58
- **Title:** Define + enforce a canonical 'minimal local' beads profile (embedded/local-server, per-project, local-only, worktree-shared) via yf preflight
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

Define a single **canonical "minimal local" beads profile** and have `yf preflight`
**confirm / enforce / correct** it for every beads-backed skill (`yf-plan`, `yf-research`,
and any call that leverages `bd`). Today each repo's `bd` config is whatever `bd init` left
behind, and the engine mode in particular drifts (see "Observed" below) — there is no single
profile that the preflight asserts and repairs.

## Desired behavior (the profile)

The simplest local beads configuration that satisfies all of:

1. **One database per repository** — not shared with other clones of the same repo, and not
   a global/shared server across unrelated repos (`--shared-server` OFF, per-project).
2. **Reachable from every worktree of that repo** — a `git worktree` (e.g. yf-plan's
   `.worktrees/<plan-id>/`) must read/write the *same* DB as the primary checkout, so plan
   execution in a worktree is tracked in the one repo DB. (This is yf-plan's current INV-2:
   "the shared Dolt DB lives in the primary's `.beads/` and is reached from anywhere.")
3. **Never synced upstream** — `dolt.local-only = true`; no Dolt remote, no `bd dolt push`/
   `pull`. (Issue *tracking* still goes to GitHub via `yf-beads-upstream`; that is orthogonal
   — only the Dolt DB itself is non-synced.)

Stated as a counterfactual invariant: *a beads-backed skill MUST find the repo on exactly
one per-repo, local-only Dolt DB that all of the repo's worktrees share; it MUST NOT find a
shared-across-repos server or a remote-synced DB.*

## Engine mode: the open design question

The requester's instinct is **embedded** Dolt engine (no server process) as "the simplest."
That is likely right for goals (1) and (3), but it is in tension with goal (2):

- **Embedded** Dolt is single-process file access. Two `bd` clients (one in the primary
  checkout, one inside a worktree) accessing the same `.beads/dolt` **concurrently** can
  contend on file locks. A local **server** exists precisely to allow concurrent multi-client
  access — which is why both of the requester's repos are currently on **server** mode.
- yf-plan's current design sidesteps concurrency by running **all `bd` calls primary-side**
  (the coordinator never `cd`s into the worktree). Under that discipline, embedded is
  probably sufficient: `.worktrees/<id>/` is nested under the repo root, so `bd`'s
  upward `.beads/` discovery from a worktree still resolves to the primary DB, and access is
  serialized by convention.

**Decision needed:** is **embedded + "bd always runs primary-side"** the minimal profile that
meets goal (2), or is a **local, per-project, bd-managed server** (what the repos run today)
the minimal *robust* choice once any skill might invoke `bd` from inside a worktree? The
profile should pick one and document why. (If embedded is chosen, the worktree-discovery and
no-concurrent-writer assumptions become invariants the preflight should also guard.)

## Enforcement requirement

Extend `yf-beads-init`'s verify/repair (now in the `yf` kernel: `yf preflight yf-beads-init`)
so that, in addition to "config present and DB healthy," it asserts the canonical profile and
**corrects drift**:

- engine mode == the chosen canonical (embedded or local-server) ;
- `--shared-server` OFF (per-project) ;
- `dolt.local-only == true` ;
- (if embedded chosen) worktree-discovery / single-writer assumptions hold.

`yf-plan`, `yf-research`, and any beads-leveraging skill already route their preflight through
`yf-beads-init` (the shared dependency-verification home). So binding the profile check there
makes it apply everywhere automatically. Behavior on drift should match the existing
verify→repair contract: `ok` → silent no-op; drift → offer/apply a correction (idempotent,
safe to re-run); never clobber real data.

Open sub-questions:
- **Correct vs. confirm-only:** should a wrong engine mode be auto-migrated, or only flagged?
  Migrating embedded↔server moves data — likely propose-with-confirm, not silent auto-fix.
- Where does the canonical profile live — `bd` config keys, a `yf` profile doc, or both?

## Observed (motivation)

- Across two repos (`dixson3/emacs.d`, `dixson3/yoshiko-flow`) the *only* meaningful config
  differences were `schema_version` (11 vs 9) and the repo-specific prefix/name — but **both
  run server mode (`embedded: false`)**, which is **not** `bd init`'s default (`bd init`
  defaults to embedded). So the engine mode was a deliberate-but-undocumented setup choice,
  and nothing currently asserts it. A canonical profile + preflight enforcement would make the
  intended mode explicit and self-correcting instead of init-time happenstance.
- Verified during yf-plan plan-004 worktree execution that worktree work is tracked in the
  primary `.beads/` DB (INV-2) — the behavior this profile should formalize and guarantee.

## Environment

- Surface: Claude Code; yf-skills v0.3.2
- `bd init` reports: "Dolt is the default (and only supported) storage backend … By default,
  beads uses an embedded Dolt engine; pass `--server` for an external dolt sql-server."
  Axes: embedded vs server · bd-managed vs `--external` · per-project vs `--shared-server` ·
  local-only vs `--remote`.

