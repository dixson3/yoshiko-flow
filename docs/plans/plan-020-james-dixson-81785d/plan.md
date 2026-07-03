# Plan: Fix yf-beads-init embedded-mode wedged-migration repair: data-preserving dirty-working-set commit

**ID:** plan-020-james-dixson-81785d
**Author:** james-dixson
**Created:** 2026-07-02
**Status:** reconciling
**Epic:** yf-mol-gee
**Phase log:**
- 2026-07-02 scoping: initial scope captured
- 2026-07-02 investigating: scope + pre-probes captured; E1-E4 dispatched
- 2026-07-02 drafting: approach + epics synthesized from exp-001
- 2026-07-02 review: pass-1 conformance PASS; red-team REVISE → 5 concerns + 2 notes resolved in-place
- 2026-07-02 review: pass-1 resolved; audit pass; awaiting operator approval
- 2026-07-02 approved: operator approved
- 2026-07-02 intake: epic yf-mol-gee poured
- 2026-07-02 executing: start gate resolved
- 2026-07-02 reconciling: post-execution reconciliation

## Objective
Fix yf-beads-init embedded-mode wedged-migration repair: data-preserving dirty-working-set commit

## Motivation
The yf-beads-init repair engine (`yf/src/beads_init.rs::repair`, mirrored in the SPEC as
REQ-BINIT-011 / GR-BINIT-002 / REQ-YF-PRE-007) hardcodes the wedged-schema-migration fix as
`bd dolt stop` → `bd migrate schema` → `bd migrate`. That premise — "`bd dolt stop` flushes and
clears the in-memory Dolt working set" — only holds in dolt **server** mode. For the
embedded-storage layout (`.beads/embeddeddolt/`, the cruft-suppressed default this skill itself
creates), `bd dolt stop` errors ("not supported in embedded mode (no Dolt server)") and
`bd migrate schema` fails against a **dirty on-disk Dolt working set** ("pending schema migrations
alter pre-existing dirty tables: config, events, issues"). The repo cannot self-heal — `yf doctor
--repair` reports three FAILs.

Observed live in `dixson3/yoshiko-flow` on 2026-06-30 after a beads 1.0.0 → 1.0.5 upgrade (the
upgrade carried a schema migration adding `wisp_*` tables that must alter config/events/issues,
but those tables held an uncommitted working set from a prior session — Dolt refuses to alter
dirty tables). This is an **upgrade artifact** and will recur on the next beads schema-bump for
any embedded repo whose prior session left an unflushed working set. Affects every operator whose
project uses the skill's default embedded layout.

The manually-verified fix: commit the embedded working set directly (`cd
.beads/embeddeddolt/<db> && dolt add -A && dolt commit`), bypassing bd's wedged migration gate,
**then** `bd migrate schema` → `bd migrate`. Data-preserving (`commit`, never `reset --hard` — the
working set can hold real issue data).

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| [#56](references/upstream-56.md) | yf-beads-init repair: embedded-mode wedged-migration fix can't clear a dirty Dolt working set | include | The whole plan; `type::bug`, `priority::high` | Epic 1 / Issue 1.1 (`resolves-upstream: #56`) |

## Scope

**In scope**
- Make the wedged-migration repair path **mode-aware**: detect embedded-storage vs server mode
  and, for embedded, run a **data-preserving working-set commit** before `bd migrate schema`.
- Update the SPEC surfaces FIRST (SPEC-first): `skills/yf-beads-init/SPEC.md` (REQ-BINIT-011,
  GR-BINIT-002, new REQ + living-amendment-log entry), repo-root `SPEC.md` (REQ-YF-PRE-007), and
  `docs/yf/preflight-contract.md`.
- Implement in the Rust engine (`yf/src/beads_init.rs::repair` + a new `apply_native` verb) with a
  tagged test.
- Sync the prose surfaces: `skills/yf-beads-init/SKILL.md`, `protocols/BEADS_INIT.md` (+ re-stamp
  `manifest.json`, refresh the installed rule via `install.sh --force`), `CHANGELOG.md`.

**Out of scope**
- Rewriting bd's own migration logic (bd is the authority; we only sequence around it).
- The `--remove-remote` canonicalization-drift cleanup (issue #61, separate).
- Any change to the server-mode path beyond leaving it intact.

## Investigation Findings

### Pre-scope probes (this session, on the affected repo)
- **Standalone `dolt` is on PATH** here: `/opt/homebrew/bin/dolt` v2.1.10. Not guaranteed on
  every install — the engine cannot assume a homebrew dolt.
- **`bd dolt commit` exists as a passthrough** (`bd dolt … commit — Commit pending changes`). bd
  1.0.5 help says "Beads uses a dolt sql-server for all database operations. The server is
  auto-started transparently." So bd may run a server even over the `embeddeddolt/` layout.
- **Layout differs from the issue's assumption.** The issue wrote `cd
  .beads/embeddeddolt/<dbname>`; the real layout here is `.beads/embeddeddolt/dolt/` alongside live
  `dolt-server.{pid,port,lock,log}`. The raw-`dolt` working directory / `<dbname>` derivation must
  be nailed down, and the embedded-vs-server distinction in 1.0.5 is subtler than the issue states.

### Resolved experiments — [exp-001](findings/exp-001-embedded-wedge-escape-hatch.md)
- **E1 (crux) → raw `dolt`.** Both `bd dolt commit` and raw `dolt add -A && dolt commit` clear a
  merely-dirty working set. A genuine wedge could **not** be reproduced with a single bd 1.0.5
  binary (absence finding), so `bd dolt commit`-while-wedged is unverified. The real-world fix used
  raw `dolt` deliberately (bd was wedged); raw `dolt` structurally bypasses bd's migration gate and,
  in embedded mode (no server), faces no lock contention. **Decision: raw `dolt add -A && dolt
  commit` with a derived cwd. Never `reset --hard`.**
- **E2 → derive the path, never hardcode.** Dolt repo root = the unique dir under `.beads/`
  containing a `.dolt/` child (`find .beads -type d -name .dolt` → parent). Fallback:
  `metadata.json.dolt_database` under the data-dir base. Guard: if zero or >1 candidates, do not
  guess — surface an error and leave the repo for manual repair.
- **E3 → `metadata.json` `dolt_mode`.** Detect embedded mode by reading `.beads/metadata.json`'s
  `dolt_mode == "embedded"` (filesystem-only, no exit-code inference). Corroborated by absence of
  `dolt-server.*`. Do **not** infer mode from `bd dolt stop`'s exit code.
- **E4 → unit + idempotency (operator-approved).** A deterministic end-to-end wedge fixture is not
  cheaply constructible. Cover with (1) plan-shape unit assertions and (2) native-step idempotency
  against a real `bd init` embedded repo with a synthetically-dirtied working set.

## Approach

**Mode-aware wedged-migration repair, SPEC-first.** Keep the server-mode path
(`bd dolt stop` → `bd migrate schema` → `bd migrate`) exactly as-is. For the embedded-storage
layout, replace the failing `bd dolt stop` with a **data-preserving working-set commit** run via
raw `dolt` in the derived dolt-repo cwd, before `bd migrate schema`:

```
embedded:  [native] dolt-commit-embedded  →  bd migrate schema  →  bd migrate
server:    bd dolt stop                    →  bd migrate schema  →  bd migrate   (unchanged)
```

The commit is a **new native `apply_native` verb** (`dolt-commit-embedded`), not a shelled `bd`
step — it must run raw `dolt` with cwd = the derived dolt-repo root (the flat argv/shelled model
has no cwd field, and it must bypass bd). The verb:
1. Reads `.beads/metadata.json`; if `dolt_mode != "embedded"`, no-op (server path handles it). **If
   `dolt_mode` is missing/empty** (a stale pre-`dolt_mode` `metadata.json` — plausible on the very
   upgrade that triggers a wedge), **fall back to the filesystem probe**: absence of
   `dolt-server.{pid,port}` ⇒ treat as embedded. Do not default a keyless repo to the server path
   (that is the path that fails) — RT-3.
2. Derives the dolt-repo root (`.dolt/`-parent search; fallback `dolt_database`); on zero/>1
   candidates, returns a non-zero rc with a clear "manual repair needed" message (never guesses).
3. Runs `dolt add -A`; checks `dolt status`; runs `dolt commit -m "<repair marker>"` **only if
   dirty** (tolerates the clean-tree "no changes added" as success). Never `--allow-empty`, never
   `reset --hard`.
4. **Escape-hatch fallback chain** (RT-2): prefer raw `dolt` (derived cwd) — it structurally cannot
   share bd's wedge; **if `dolt` is absent from PATH, attempt `bd dolt commit` as a last resort**
   before hard-failing (worst case it fails identically to today; best case it recovers a repo that
   would otherwise be left for manual repair). Only when both are unavailable/fail does the verb
   return a clear rc with remediation ("install dolt or commit the embedded working set manually").

Plan-build time detection: `repair()` inspects `metadata.json` (with the keyless→filesystem-probe
fallback above) when building the `Corrupted` branch and emits either the embedded native step or
the server `bd dolt stop`. Deterministic and plan-shape-testable.

**Partial-failure outcome (RT-4).** If the working-set commit succeeds but `bd migrate schema`
still fails, the apply loop continues and re-verify reports **FAIL / Corrupted** — acceptable and
expected: the working set is now safely committed (recoverable), and the operator gets a
manual-repair remediation. This is the most likely real-world non-happy path (the genuine wedge is
unreproducible), so it is called out explicitly rather than left implicit.

**SPEC-first ordering.** The SPEC amendments (Epic 1) land before the engine change (Epic 2), per
the project SPEC-first convention.

## Epics

### Epic 1: SPEC amendments (SPEC-first — lands before code)
- Issue 1.1: Revise `skills/yf-beads-init/SPEC.md` — make REQ-BINIT-011 mode-aware (server vs
  embedded sequence); add a new testable REQ (e.g. **REQ-BINIT-016**) for embedded-mode detection
  via `metadata.json` + the data-preserving derived-cwd commit (never `reset --hard`, clean-tree
  no-op); clarify GR-BINIT-002 that the embedded raw-`dolt commit` escape hatch is distinct from the
  forbidden `bd vc commit`; add a living-amendment-log entry.
  - resolves-upstream: #56 (include)
- Issue 1.2: Mirror the sequence change in repo-root `SPEC.md` (REQ-YF-PRE-007) and
  `docs/yf/preflight-contract.md` (§5 repair-sequence prose + REQ-YF-PRE-007 reference).
  - depends-on: 1.1

### Epic 2: Engine implementation (`yf/src/beads_init.rs`)
- Issue 2.1: Add embedded-mode detection + dolt-repo-path derivation helpers (read
  `metadata.json`; `.dolt/`-parent search with zero/multiple-candidate guard).
  - depends-on: 1.1
- Issue 2.2: Add the `dolt-commit-embedded` native verb in `apply_native` (raw `dolt add -A` +
  dirty-guarded `dolt commit`; no-op when clean; clear rc when `dolt` absent or path ambiguous).
  - depends-on: 2.1
- Issue 2.3: Wire the `Corrupted` branch in `repair()` to emit the embedded native step vs the
  server `bd dolt stop` by mode. Also make the **user-facing `verify()` remediation string**
  (`beads_init.rs:252`, shown on `WEDGED_MARKERS` match) mode-aware — it currently advises the exact
  `bd dolt stop` that fails in embedded mode (RT-1). Update the stale server-only doc-comments
  (lines ~340-341, ~417) and the `beads_init.py repair` reference at `beads_init.rs:331` (that
  script is a retired stub — repair now lives in the `yf` kernel; the comment is drift).
  - depends-on: 2.2

### Epic 3: Tests (plan-shape + idempotency)
- Issue 3.1: Plan-shape unit test — an embedded `Corrupted` repo's plan has
  `dolt-commit-embedded` → `bd migrate schema` → `bd migrate`, **no** `bd dolt stop`, and a derived
  (not hardcoded) path; extend/parallel `corrupted_plan_has_migration_order`. Tag to REQ-BINIT-016.
  - depends-on: 2.3
- Issue 3.2: Native-step idempotency integration test — `bd init` embedded repo in a tempdir,
  dirty via `dolt sql`, run the verb → assert clean + data preserved; re-run on clean tree → assert
  safe no-op; assert mode detection reads `metadata.json`. (Skip/guard cleanly if `bd`/`dolt` absent
  in CI.)
  - depends-on: 2.3

### Epic 4: Prose-surface sync
- Issue 4.1: Update `skills/yf-beads-init/SKILL.md` wedged-schema-migration section **and
  `skills/yf-beads-init/README.md:36`** (also hardcodes the server-only sequence — RT-5) to the
  mode-aware sequence.
  - depends-on: 1.1
- Issue 4.2: Update `skills/yf-beads-init/protocols/BEADS_INIT.md` wedged bullet; re-stamp
  `protocols/manifest.json` (`manifest_update.py`); note `install.sh --force` refresh of the
  installed rule copy.
  - depends-on: 1.1
- Issue 4.3: `CHANGELOG.md` entry.
  - depends-on: 2.3

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate (upstream #56 incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
- **`dolt` not on PATH at repair time.** The native verb needs a standalone `dolt`. Mitigation:
  detect and return a clear rc with remediation rather than a silent pass; document that dolt is a
  bd runtime dependency. (Cannot fall back to `bd dolt commit` — it may share the wedge.)
- **Genuine wedge unreproducible → no true end-to-end coverage.** Mitigation: plan-shape +
  idempotency tests (E4); the sequence itself is the manually-verified real-world fix. Documented
  absence finding.
- **Server-mode path untouched but also unexercised by this change.** Mitigation: the change is
  strictly additive on the embedded branch; server path bytes are unchanged. Called out so review
  doesn't assume server-mode was re-validated.
- **Path-derivation ambiguity (zero/multiple `.dolt/` dirs).** Mitigation: explicit guard — never
  guess; surface a manual-repair message.
- **Data loss via wrong clear mechanism.** Mitigation: hard invariant — `add -A && commit` only,
  never `reset --hard`, never `--allow-empty`.
- **No golden fixture from the real 2026-06-30 wedge.** The live wedged DB was manually repaired
  (state gone; a pre-fix snapshot may survive under `.beads/embeddeddolt/backup/` but is not a
  reliable, portable, version-pinned fixture). True end-to-end coverage is therefore
  **closed-by-decision**, not by omission: the sequence shipped is the manually-verified real-world
  fix, covered by plan-shape + idempotency tests (E4). (RT missing-item.)

## Success Criteria
- A wedged **embedded** repo self-heals via `yf doctor --repair --apply` (or `beads_init repair`):
  the working set is committed (data preserved), migrations apply, and re-verify returns `ok`.
- Partial failure is safe: if the commit succeeds but migration still fails, repair reports FAIL
  with the working set **committed (recoverable)** and a manual-repair remediation (RT-4).
- The server-mode wedged path is byte-for-byte unchanged.
- `repair()` derives the dolt-repo path (no hardcoded `.beads/embeddeddolt/dolt`) and detects mode
  from `metadata.json`.
- SPEC surfaces (REQ-BINIT-011, new REQ-BINIT-016, GR-BINIT-002, REQ-YF-PRE-007) describe the
  mode-aware sequence, landed **before** the code; the amendment log records it.
- Plan-shape + idempotency tests pass and are tagged to the new REQ.
- Prose surfaces (SKILL.md, BEADS_INIT.md + re-stamped manifest, CHANGELOG) agree with the SPEC.
- Issue #56 reconciled/closed with a pointer to the fix.
