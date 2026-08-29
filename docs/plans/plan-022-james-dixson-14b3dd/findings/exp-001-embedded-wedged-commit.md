---
type: Finding
okf_spec: OKF-PLAN
---
# EXP-001: Do `bd vc commit` / `bd dolt commit` bypass migration guards on a wedged EMBEDDED Dolt DB (bd 1.1.0)?

## Verdict

**VERDICT A — the escape hatch is REPLACEABLE.**

On bd 1.1.0, both `bd dolt commit` and `bd vc commit` **CAN open a wedged embedded-storage
Dolt DB** (pending schema migrations + dirty working set) and **commit the dirty working set at
the current schema, data-preservingly, without applying the migration first** — resolving the
chicken-and-egg. This is precisely what the yf-beads-init hand-rolled raw `dolt add -A && dolt
commit` escape hatch does, but via a supported bd command.

- **Recommended replacement command: `bd dolt commit`** (this is the exact command bd 1.1.0's own
  wedge error message tells the operator to run).
- The SKILL.md warning *"Do not try `bd vc commit` first — it cannot open the wedged DB
  (chicken-and-egg)"* is **now provably FALSE on bd 1.1.0** and must be corrected. `bd vc commit`
  succeeds identically.
- `bd migrate schema` still **fails** on the wedged DB (chicken-and-egg) — that half of the
  SKILL.md description remains accurate.

Fidelity note: this was tested against a **genuine** wedged fixture — a real schema-49 embedded DB
(created by bd 1.0.5) with a real dirty Dolt working set, opened by bd 1.1.0 which has real pending
migrations 0050–0053. Not a simulation.

## Environment

- `bd version 1.1.0 (Homebrew)` at `/opt/homebrew/bin/bd` (the only installed release).
- `dolt version 2.1.10` at `/opt/homebrew/bin/dolt`.
- Old-schema fixture generator: `bd version 1.0.5 (dev)`, built from source
  (`go install github.com/steveyegge/beads/cmd/bd@v1.0.5`, module path is `steveyegge/beads`, not
  `gastownhall/beads`) with ICU CGO flags (`-I/opt/homebrew/opt/icu4c@78/include`, `-std=c++17`).
- All work in throwaway dirs under `/private/tmp`; the live project `.beads` was never touched.

## How the wedge was reproduced (this was the hard part)

Key mechanism discovered: **bd applies pending schema migrations automatically on store open**
(`bd migrate schema --help`: "Schema migrations also run automatically on store open"). So a naive
1.0.5→1.1.0 open on a *clean* working set silently auto-migrates and never wedges. The wedge only
occurs when the working set is **dirty at the old schema** when 1.1.0 first opens the DB.

Migration delta between the two releases (from module source):

```
diff (v1.0.5 migrations) vs (v1.1.0 migrations)
> 0050_dependencies_deterministic_id
> 0051_drop_aux_id_defaults
> 0052_add_date_indexes
> 0053_repair_rig_wisps
```

A fresh 1.0.5 embedded init sits at schema **v49**; bd 1.1.0's head is **v53**. Fixture build:

```
$ bd(1.0.5) init --non-interactive -p wg --skip-agents --skip-hooks   # Mode: embedded, schema v49
$ bd(1.0.5) create "seed issue" -t task -p 1                          # wg-9cc
# dirty the working set at schema 49 WITHOUT a dolt commit, via raw dolt (no 1.1.0 open yet):
$ (cd .beads/embeddeddolt/wg && dolt sql -q "update issues set title='dirtied2' where id='wg-9cc'")
$ dolt status
On branch main
Changes not staged for commit:
	modified:         issues
$ dolt sql -q "select max(version) from schema_migrations"   ->  49
```

This yields a genuine wedge candidate: **schema v49 + dirty working set, never opened by 1.1.0.**

## Evidence — the tests (each against a fresh copy of the dirty@49 fixture)

### 1. Confirm the wedge exists — `bd status` (1.1.0) fails to open

```
$ bd status --json          # bd 1.1.0
Error: failed to open database: embeddeddolt: init schema: embeddeddolt: migrate:
pending schema migrations alter pre-existing dirty tables: issues;
run 'bd dolt commit' to commit the working set at the current schema, then re-run
the migration (gastownhall/beads#4566)
# (exit code 0 — note the false-negative invariant: error surfaced in output, exit 0)
# working set still dirty; schema still 49
```

bd's own error message prescribes `bd dolt commit` as the fix.

### 2. `bd dolt commit` — BYPASSES the guard, commits the wedged working set

```
$ bd dolt commit -m "commit working set at current schema (wedge escape)"   # bd 1.1.0
Warning: pending schema migrations alter pre-existing dirty tables: issues;
run 'bd dolt commit' to commit the working set at the current schema, then re-run
the migration (gastownhall/beads#4566)
  Committing the working set at the current schema; when it completes,
  re-run 'bd migrate'.
Committed.
# exit 0
$ dolt status      -> nothing to commit, working tree clean
$ dolt sql "max(version)" -> 49         # committed AT current schema, migration NOT yet applied
# then re-open completes the migration cleanly:
$ bd status        -> Total Issues: 1
$ dolt sql "max(version)" -> 53         # migration 50-53 applied on next clean open
```

The pending-migration message is downgraded from a fatal `Error` (in the guard) to a `Warning`;
the commit proceeds. This is the guard being bypassed.

### 3. `bd vc commit` — identical bypass behavior

```
$ bd vc commit -m "vc commit wedge escape test"   # bd 1.1.0
Warning: pending schema migrations alter pre-existing dirty tables: issues; ...
  Committing the working set at the current schema; when it completes, re-run 'bd migrate'.
Created commit 8fka5717
# exit 0 ; working tree clean ; next open -> schema 53, Total Issues: 1
```

So the SKILL.md singling-out of `bd vc commit` as unusable is wrong on 1.1.0.

### 4. `bd migrate schema` — still fails (chicken-and-egg still real for THIS command)

```
$ bd migrate schema     # bd 1.1.0, wedged DB
Error: failed to open database: embeddeddolt: init schema: embeddeddolt: migrate:
pending schema migrations alter pre-existing dirty tables: issues; run 'bd dolt commit' ...
# working set still dirty — migrate can't self-unwedge
```

Confirms the SKILL.md claim that `bd migrate schema` fails against the dirty working set.

### 5. Data preservation

```
$ dolt sql -q "select id,title from issues"     # after bd dolt commit + migration to v53
+--------+----------+
| id     | title    |
| wg-9cc | dirtied2 |     # the dirty working-set edit survived; data-preserving
+--------+----------+
```

## Supporting facts (baseline, non-wedged)

- Embedded is the **default** mode (`bd init` with no `--server`); metadata shows
  `"dolt_mode": "embedded"` and a `.beads/embeddeddolt/<db>` Dolt repo.
- With no pending migration, `bd dolt commit` already commits a dirty embedded working set
  (batch-mode create → dirty → `bd dolt commit` → `Committed.`, clean). The wedge tests above add
  the pending-migration dimension on top of this.
- No `--help` text for `bd vc commit` / `bd dolt commit` / `bd migrate schema` documents an explicit
  "bypass migration guard" flag; the bypass is **implicit behavior** of the commit commands (they
  commit at the current schema and defer migration), not a flag. The CHANGELOG behavior is real but
  surfaces only at runtime, as shown.

## Implications for the plan

Replace the yf-beads-init embedded-storage escape hatch:

- **Was:** raw `dolt add -A && dolt commit` in the derived `.beads/embeddeddolt/<db>` dir, plus the
  warning that `bd vc commit` cannot open the wedged DB.
- **Now (bd ≥ 1.1.0):** `bd dolt commit` (run from the repo root — bd finds the embedded DB itself),
  followed by `bd migrate` on the next open. This drops the raw-dolt dependency, the need to derive
  the Dolt-repo subdir, and the mode-specific `bd dolt stop` vs raw-dolt branch collapses toward the
  bd-native command.

Caveats to carry into the SKILL.md edit:

- Keep the server-mode branch as-is; this experiment only covers embedded.
- The commit leaves schema at the old version and prints a `Warning` + "re-run 'bd migrate'"; the
  repair sequence must therefore be **`bd dolt commit` → `bd migrate`** (a subsequent open/`bd
  migrate` applies 50→53). A one-shot `bd dolt commit` alone does not finish the migration.
- If the project must support bd < 1.1.0, the raw-dolt hatch is still needed as a fallback (this
  bypass behavior is a 1.1.0 feature). If bd ≥ 1.1.0 is a hard floor, the raw-dolt path can be
  removed outright.
- The SKILL.md sentence *"Do not try `bd vc commit` first — it cannot open the wedged DB"* is
  factually wrong on 1.1.0 and must be deleted/rewritten regardless of whether the hatch itself is
  swapped.
