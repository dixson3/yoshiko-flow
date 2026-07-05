# Upstream #68: Confirm/certify yf beads skills against bd 1.1.x (currently pinned to 1.0.5)

- **Number:** 68
- **Title:** Confirm/certify yf beads skills against bd 1.1.x (currently pinned to 1.0.5)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Goal

Confirm and certify the yf beads skills against **bd 1.1.x** (`gastownhall/beads`). Both skills currently pin to **1.0.5**; the installed Homebrew build is already **1.1.0**.

- `yf-beads-extra` carries a literal "Verified against bd 1.0.5" banner.
- `yf-beads-init` sets `min-bd-version: 1.0.5`.

## 1.0.5 → 1.1.0 delta (context)

The entire 1.1.0 line is one theme: **safe schema-migration and upgrade path**. The everyday CLI surface (create/types/gates/dep-mutation/`--json` shape/`batch`/`mol pour`) is unchanged; changes concentrate in the machinery `yf-beads-init`'s repair engine drives.

| Area | Change (1.1.0, consolidating rc.1/rc.2) |
| :-- | :-- |
| Interrupted migrations | Now **recoverable in-tool**; repairs the v52/v53 drift classes that broke real upgrades |
| Wedged-DB commits | `bd dolt commit` **and `bd vc commit` now bypass migration guards** — run against a DB with pending migrations |
| Dirty working sets | No longer deadlock migration recovery in embedded mode |
| Remote-migrate gate | **State-aware, on by default** (`BD_SMART_GATE`); same-schema first-mover auto-migrates without `BD_ALLOW_REMOTE_MIGRATE`, remote-ahead still stops |
| `bd doctor` | Adds a **migration-content-skew check** (local `schema_migrations` vs cached remote-tracking refs) |
| `child_counters` bug | One orphaned row that could **brick every `bd create`** is fixed (clone-local migration) |
| Internal | Composite indexes on `issues`; per-migration content hash in `schema_migrations` |

## `yf-beads-init` impact (high — its domain)

- [ ] **Re-verify the `bd vc commit` claim.** SKILL.md step 2 (embedded path) states: *"Do not try `bd vc commit` first — it cannot open the wedged DB (chicken-and-egg)."* In 1.1.0 `bd vc commit`/`bd dolt commit` explicitly **bypass migration guards**. If that now opens a wedged embedded DB, the hand-rolled raw `dolt add -A && dolt commit` escape hatch could be replaced by a supported command. **Verify empirically before changing** — most likely simplification.
- [ ] **Assess whether the mode-aware flush → `bd migrate schema` → `bd migrate` sequence is still necessary** for the common case now that 1.1.0 has in-tool interrupted-migration recovery. Should still work; question is redundancy.
- [ ] **Confirm the false-negative invariant still holds** (it should): `bd status --json` error-JSON-with-exit-0, and "`bd doctor` shows DB version behind CLI version". The new `bd doctor` skew check *adds* a diagnostic, doesn't invalidate the existing one.
- [ ] **Local-only / `--remove-remote` note:** the remote-migrate gate default flip is benign for local-only, but if a remote is still configured during repair the gate can now block auto-migration unless schema versions match (`BD_SMART_GATE=0` opts out). Consider a one-line note in the local-only section.

## `yf-beads-extra` impact (low)

Structurally unaffected 1.0.5 → 1.1.0 — every documented gotcha (issue types, gate verbs, additive `bd dep`, no `--update --deps`, epic-blocking rule, `--json` array shape, `bd batch`, `bd mol pour` shape) is unchanged. Cosmetic-only:

- [ ] Bump the "Verified against bd 1.0.5" banner to note 1.1.0 verification.
- [ ] The batch-section "if a create returns empty, stop and fix" warning had a real 1.0.x cause (orphaned `child_counters` bricking `bd create`) that is **fixed in 1.1.0**. Keep the defensive advice; note the specific failure mode is retired.

## Acceptance

- [ ] `bd vc commit` / `bd dolt commit` behavior on a wedged embedded DB verified on 1.1.0.
- [ ] `yf-beads-init` repair sequence validated end-to-end against 1.1.0 (wedged-migration fixture).
- [ ] Version pins bumped: `yf-beads-init` `min-bd-version`, `yf-beads-extra` banner.
- [ ] Any SKILL.md text made false by 1.1.0 corrected.

---
_Filed from a bd-version audit; findings captured as-is. Repo: `gastownhall/beads`, CHANGELOG: https://github.com/gastownhall/beads/blob/main/CHANGELOG.md_

