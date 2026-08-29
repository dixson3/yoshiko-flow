---
type: Finding
okf_spec: OKF-PLAN
---
# EXP-002: Does remove-remote-alone clear the bd 1.1.0 remote-migrate gate?

Plan: plan-022, Issue 4.2 (#61). Load-bearing for Epic 4 reframe (canonicalization
makes the gate moot; `BD_ALLOW_REMOTE_MIGRATE` stays operator-gated / never auto-run).

Date: 2026-07-05. Host: byid-mba-dixson3 (darwin/arm64).

## Verdict

**VERDICT YES — with a precise decomposition and one important operational caveat.**

Removing the remote **clears the bd 1.1.0 state-aware remote-migrate gate with NO
`BD_ALLOW_REMOTE_MIGRATE`**. Decomposition of *which* remote layer matters:

- The gate keys **solely on the Dolt-DB-level remote** (`dolt_remotes` table,
  `SELECT COUNT(*) FROM dolt_remotes`). Removing `origin` from `dolt_remotes` is the
  **decisive and sufficient** action.
- The `sync.remote` **config key is irrelevant to the gate**. Removing it alone does
  **not** clear the gate; leaving it in place does **not** re-arm the gate once the
  Dolt remote is gone.
- Removing **both** layers (the plan's Epic-4 canonicalization) clears the gate — this
  is a superset of the sufficient action, so it is safe/correct, just belt-and-suspenders
  on the `sync.remote` side.

**CAVEAT (new, load-bearing for Epic 4.3 impl):** bd 1.1.0's **own** `config unset` and
`dolt remote remove` subcommands are **themselves gated** on a wedged DB — they hit the
same refusal and perform no mutation. Canonicalization therefore **must** use **raw
`dolt remote remove`** (in `.beads/embeddeddolt/<db>/`) and a **raw `config.yaml` edit**,
**not** `bd config unset` / `bd dolt remote remove`. See Test 1a and Test 2a below.

Net for the plan: Epic 4.3 impl proceeds as designed (canonicalization clears the gate;
override stays operator-gated-only), **provided** the canonicalization removes the
**Dolt-level** remote via **raw dolt**, not via bd subcommands. SC-3 holds.

## Environment

```
$ bd version
bd version 1.1.0 (Homebrew)          # /opt/homebrew/bin/bd (only 1.1.0 installed)
$ go version   -> go1.26.4 darwin/arm64
$ dolt version -> dolt version 2.1.10
```

Old bd built from source for the fixture (CGO+ICU, ~1 min each):

```
ICU=/opt/homebrew/opt/icu4c
CGO_ENABLED=1 CGO_CPPFLAGS="-I$ICU/include" \
CGO_LDFLAGS="-L$ICU/lib -licuuc -licui18n -licudata" \
go install github.com/steveyegge/beads/cmd/bd@v1.0.5
# -> bd version 1.0.5 (dev)
```

(Module path is `github.com/steveyegge/beads`, not `gastownhall`. A plain
`CGO_ENABLED=0` build compiles but cannot open embedded Dolt — it errors
"embedded Dolt requires a CGO build" — so the ICU-linked CGO build is required.)

All work under `/private/tmp/exp002/…`. The live project `.beads` was never touched.

## Method — building a genuine wedge fixture

### First attempt failed: 1.0.5 -> 1.1.0 has no DDL gap

An embedded DB created by bd 1.0.5 is already at **numeric schema v53**, identical to
1.1.0. Opening it with 1.1.0 is only a version-**string** bump, never a DDL migration —
so it does **not** wedge even with both remotes configured:

```
$ bd migrate     # (1.1.0, on a 1.0.5 DB, both remotes set)
Updating Dolt schema version: 1.0.5 → 1.1.0
✓ Version updated
```

The gate fires on **pending numeric DDL migrations** (`schema_migrations` table), which
this pair does not have. Confirmed via the DB directly:

```
$ dolt sql -q "SELECT MAX(version) FROM schema_migrations"   # 1.0.5 DB
53
```

### Working fixture: roll the recorded schema version back to v49

To synthesize the wedge condition ("older-schema DB with pending migrations + a remote"),
the recorded schema version was rolled back by deleting the newest four rows from the
Dolt `schema_migrations` table (no DDL reverted — the gate is checked *before* any
migration is applied, so this exactly reproduces the pre-apply wedge state):

```
$ dolt sql -q "DELETE FROM schema_migrations WHERE version > 49"
$ dolt sql -q "SELECT MAX(version) FROM schema_migrations"   # -> 49
$ dolt add -A && dolt commit -m "roll back schema to v49 for wedge fixture"
```

Both remote layers were then configured on this v49 DB:

```
# Dolt-DB-level remote (raw dolt, in .beads/embeddeddolt/tst/):
$ dolt remote add origin https://example.com/x.git
$ dolt sql -q "SELECT name FROM dolt_remotes"     # -> origin

# sync.remote config layer (via bd 1.0.5 to avoid touching 1.1.0):
$ bd config set sync.remote "git+https://example.com/x.git"
Set sync.remote = git+https://example.com/x.git (in config.yaml)
```

## Wedge reproduced (baseline)

```
$ bd migrate            # bd 1.1.0, plain, NO override
refusing to auto-apply 4 pending schema migrations to a remote-backed database
(v49 -> v53): migrating clones independently forks the schema (#4259)
  ...
    • BD_ALLOW_REMOTE_MIGRATE=1 bd migrate
      bd dolt push
    • bd bootstrap   (adopt)
```

`bd status --json` on the wedged DB returns **error-JSON with exit 0** (the false-negative
invariant from YOSHIKO_FLOW.md — an `error` key, not a non-zero exit):

```json
{
  "error": "refusing to auto-apply 4 pending schema migrations to a remote-backed database (v49 -> v53): migrating clones independently forks the schema (#4259)",
  "remote_migrate_gate": {
    "current_version": 49,
    "latest_version": 53,
    "pending": 4,
    "observed": "4 pending schema migration(s) and a configured remote",
    "human_decision_required": true,
    "severity": "blocking",
    "options": [
      { "id": "migrate", "commands": ["BD_ALLOW_REMOTE_MIGRATE=1 bd migrate", "bd dolt push"], "when": "you are the single designated migrator ... and no other clone has migrated yet" },
      { "id": "adopt",   "commands": ["bd bootstrap"], "when": "another machine has already migrated and pushed" }
    ]
  }
}
```

Note the gate presents **only** `migrate` (with the override) and `adopt` — it does **not**
itself suggest "remove the remote". The canonicalization strategy is an operator move
*outside* the gate's presented options; this experiment proves it works.

## The tests (each from a fresh copy of the wedged fixture)

### Test 1 — remove `sync.remote` config ONLY (keep Dolt remote) -> STILL WEDGED

`sync.remote` removed by raw `config.yaml` edit; `dolt_remotes` still has `origin`.

```
$ grep -c sync.remote .beads/config.yaml        # 0  (removed)
$ dolt sql -q "SELECT COUNT(*) FROM dolt_remotes"  # 1  (kept)
$ bd migrate          # plain, no override
refusing to auto-apply 4 pending schema migrations to a remote-backed database
(v49 -> v53): ... (#4259)
```

**Conclusion:** the gate does **not** key on `sync.remote`.

### Test 1a — bd 1.1.0 `config unset sync.remote` is itself gated

Before the raw edit, `bd config unset sync.remote` (the natural canonicalization command)
was tried on the wedged DB:

```
$ bd config unset sync.remote
      Re-cloning replaces your local database: any local issues you have not
      pushed are LOST. ...                       # <- the gate refusal text
$ grep -n sync.remote .beads/config.yaml
68:sync.remote: "git+https://example.com/x.git"  # <- NOT removed
```

The config op printed the migration refusal and **did not modify config.yaml**.

### Test 2 — remove Dolt remote ONLY (keep `sync.remote` config) -> CLEARED

Dolt remote removed via **raw dolt**; `sync.remote` config left in place.

```
$ dolt remote remove origin                      # raw, in embeddeddolt/tst/
$ dolt sql -q "SELECT COUNT(*) FROM dolt_remotes" # 0
$ grep -c sync.remote .beads/config.yaml          # 1  (still present)
$ bd migrate          # plain, NO override
Updating Dolt schema version: 1.0.5 → 1.1.0
✓ Version updated
$ dolt sql -q "SELECT MAX(version), COUNT(*) FROM schema_migrations"
53   53                                           # all 4 pending applied
$ bd status --json    # exit 0, real summary, no error key
{ "schema_version": 1, "summary": { "open_issues": 1, ... } }
```

**Conclusion:** removing the **Dolt-level remote alone** clears the gate with no override,
**even though `sync.remote` config is still present**. The Dolt remote is the decisive layer.

### Test 2a — bd 1.1.0 `dolt remote remove` is itself gated

Before the raw removal, `bd dolt remote remove origin` was tried on the wedged DB:

```
$ bd dolt remote remove origin
refusing to auto-apply 4 pending schema migrations to a remote-backed database
(v49 -> v53): ... (#4259)
$ dolt sql -q "SELECT COUNT(*) FROM dolt_remotes"   # 1  (NOT removed)
```

Like `config unset`, `bd dolt remote remove` hits the gate and performs no mutation.

### Test 3 — remove BOTH layers (the Epic-4 canonicalization) -> CLEARED

```
$ grep -c sync.remote .beads/config.yaml          # 0 (raw edit)
$ dolt remote remove origin ; dolt sql -q "SELECT COUNT(*) FROM dolt_remotes"  # 0
$ bd migrate          # plain, NO override
Updating Dolt schema version: 1.0.5 → 1.1.0
✓ Version updated
$ dolt sql -q "SELECT MAX(version) FROM schema_migrations"   # 53
```

**Conclusion:** both-layers removal clears the gate with no override (superset of Test 2).

## Decomposed inspection (bd binary strings) — corroborates the empirical result

`strings /opt/homebrew/bin/bd` shows the gate reads the **Dolt `dolt_remotes` table** to
decide "remote-backed", and defaults to "no remote" when it cannot read it:

```
SELECT COUNT(*) FROM dolt_remotes
remote-migrate gate: read remotes: %w
Warning: remote-migrate gate could not inspect %s for persisted remotes (assuming none): %v
refusing to auto-apply %d pending schema %s to a remote-backed database (v%d -> v%d):
    migrating clones independently forks the schema (#4259)
Smart gate (%s): auto-applying %d pending deterministic schema %s to a remote-backed
    database (v%d, remote at same version ...        # state-aware safe-first-mover path
NEW: the state-aware remote-migrate gate is enabled by default; safe first-mover
    migrations proceed, while remote-ahead or content-skew cases still stop ... (#4516)
BD_ALLOW_REMOTE_MIGRATE=1 bd migrate
```

The gate's "remote-backed" predicate is `COUNT(*) FROM dolt_remotes > 0` — not the
`sync.remote` config key. This matches Tests 1/2 exactly. The gate is **state-aware**
(#4515/#4516): a safe first-mover *can* auto-apply even remote-backed, but only when it
can confirm "remote at same version". With a placeholder/unreachable local-only remote it
cannot confirm that, so it conservatively **blocks** — which is precisely the local-only
wedge this plan targets, and precisely why remove-remote (making the DB not remote-backed)
is the clean fix.

## Implications for the plan

1. **Epic 4.3 proceeds as designed.** Canonicalization (remove the remote) makes the gate
   moot on a local-only repo; `BD_ALLOW_REMOTE_MIGRATE` is **not** needed on the
   canonicalization path and should remain **operator-gated, documented, never auto-run**.
   SC-3 holds.
2. **Impl must remove the DOLT-level remote, and must do it with raw dolt.** The decisive
   layer is `dolt_remotes`, not `sync.remote`. And because bd 1.1.0's own
   `config unset` / `dolt remote remove` are gated on a wedged DB, the fix must:
   - `dolt remote remove <name>` executed **inside** `.beads/embeddeddolt/<db>/` (raw
     dolt), then `dolt add -A && dolt commit` (embedded working-set flush, matching the
     existing embedded escape-hatch invariant); and
   - remove `sync.remote` from `.beads/config.yaml` by **raw edit** (belt-and-suspenders;
     not strictly required to clear the gate, but keeps config canonical).
   Do **not** rely on `bd config unset` / `bd dolt remote remove` for the wedged-DB path.
3. **After canonicalization, a plain `bd migrate` (no env override) completes** and
   `bd status` returns to a normal exit-0 summary — verified end-to-end (Tests 2 and 3).

## What was and wasn't testable

- **Testable and tested:** full wedge reproduction on bd 1.1.0 (v49->v53, remote-backed),
  and the three removal decompositions, all with the real gate. The wedge was synthesized
  by rolling back `schema_migrations` on a real bd-1.0.5 embedded DB (the gate is evaluated
  pre-apply, so this is faithful to a natural older-clone wedge).
- **Not exercised:** a *reachable* Dolt remote at an equal/newer version (the state-aware
  "safe first-mover auto-apply" and "remote already migrated / adopt" branches). Out of
  scope for a local-only repo, and irrelevant to the canonicalization verdict — with the
  remote removed there is no remote to be ahead of. The placeholder-remote wedge used here
  is the correct model for the local-only case.
