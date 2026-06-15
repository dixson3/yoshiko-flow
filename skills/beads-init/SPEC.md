# SPEC — Beads Init (`yf-beads-init`)

> **Status: DRAFT (primed).** Per-skill SPEC for the beads verify/initialize/repair skill
> (currently `beads-init`, renamed to `yf-beads-init` by the plan-010 rename). Operator to
> review/edit. Composed by the root macro `SPEC.md` §4 under spec key **BINIT**. This skill's
> verify/repair engine is exactly what macro `REQ-YF-PRE-006` / `REQ-YF-PRE-007` port into the
> compiled `yf` binary; those macro requirements are authoritative for the ported kernel, and the
> requirements below are authoritative for the skill's current Python engine and behavior.

## 1. Purpose & scope

`yf-beads-init` verifies, initializes, and repairs a functioning beads (`bd`) configuration in a
repository, and is the shared **dependency-verification home** that every other beads-backed
skill's preflight routes to when its own preflight reports missing deps, an uninitialized repo, or
a corrupted DB. It is also invoked directly (`/beads-init`) when standing up beads in a new repo.

**In scope:** the `verify`/`repair`/`status` engine; the false-negative classification (parse
`bd status --json` for an `error` **key**, not the exit code); the standard repair sequence for a
wedged schema migration; idempotent gitignore/hooks/permissions/JSONL hardening; the local-only
assertion; and the preflight-routing contract carried by the companion rule.

**Out of scope:** routine issue operations once bd is healthy (the `beads` skill); direct-CLI
gotchas (`yf-beads-extra`); upstream issue tracking and Dolt remotes (`yf-beads-upstream`); issue
storage (that is `bd`).

## 2. Requirements (`REQ-BINIT-NNN`)

### 2.1 Verify — classification

- **REQ-BINIT-001** *(testable)* `verify` shall return a status from
  `ok | deps_missing | not_initialized | corrupted`, with `diagnostics` and `remediations`, and
  shall be the canonical read-only preflight check (no mutation). `--json-output` emits the
  machine-readable form; exit is zero only on `ok`.
- **REQ-BINIT-002** *(testable)* `verify` shall classify by inspecting the **parsed
  `bd status --json` for an `error` key**, not by trusting the `bd status` exit code: a repo whose
  `bd status` returns an error JSON with exit 0 (e.g. a pending schema migration blocked by a dirty
  Dolt working set) while `bd ready`/`bd list`/`bd create` work shall be classified `corrupted`
  (initialized-but-wedged, repairable), **never** `not_initialized`. (This is the macro
  false-negative invariant `REQ-YF-PRE-006`.)
- **REQ-BINIT-003** *(testable)* `verify` shall return `deps_missing` when a required tool is
  absent (`bd` ≥ 1.0.5, `uv`, `git`), and `not_initialized` only when there is no usable `.beads/`
  (genuinely uninitialized), so a wedged repo is never routed to `bd init` (which would risk
  clobbering real data).

### 2.2 Repair — sequence & safety

- **REQ-BINIT-010** *(testable)* `repair` shall default to a **dry-run** that prints the fix plan;
  `repair --apply` shall apply the standard repairs; exit is zero only when the post-repair
  re-verify returns `ok`.
- **REQ-BINIT-011** *(testable)* the wedged-schema-migration fix shall be, in order,
  `bd dolt stop` → `bd migrate schema` → `bd migrate`, and shall **not** attempt `bd vc commit`
  first (it cannot open the wedged DB — chicken-and-egg). (Macro `REQ-YF-PRE-007`.)
- **REQ-BINIT-012** *(testable)* repair hardening shall be idempotent and safe to re-run:
  permissions (`chmod 700 .beads`), git hooks (`bd hooks install --force`), gitignore drift
  (`bd doctor --fix` plus the engine's top-up patterns for `.beads/.gitignore` and project
  `.gitignore`), and a portable JSONL export (`bd export -o .beads/issues.jsonl`, not itself
  gitignored).
- **REQ-BINIT-013** `not_initialized` repair shall confirm intent before `bd init`, then harden;
  `deps_missing` shall stop with the install list (no destructive action on a deps gap).
- **REQ-BINIT-014** *(testable)* `repair` shall re-verify after applying and report the resulting
  status; the operator runs `bd doctor` expecting 0 errors, with `Remote Consistency: No remotes
  configured` accepted by design on a local-only repo and `Dolt Status` / `Git Working Tree`
  warnings treated as transient (clear on commit).

### 2.3 Local-only & preflight routing

- **REQ-BINIT-020** *(testable)* `repair --apply --local-only` shall assert
  `bd config set dolt.local-only true`, keep `bd dolt remote list` empty, and never `bd dolt push`;
  upstream issue tracking is `yf-beads-upstream`'s job.
- **REQ-BINIT-021** as a preflight dependency, another beads skill shall run its own
  system-deps/rule checks first, then on a beads-config failure (`bd_not_initialized`, a corrupted
  DB, or a `bd status` error JSON) route to `/beads-init` / `beads_init.py verify`+`repair` rather
  than re-deriving the repair steps; the companion rule `protocols/BEADS_INIT.md` carries this
  trigger so it fires regardless of the active skill.
- **REQ-BINIT-022** when `verify` returns `ok`, the preflight trigger shall be a **silent no-op** —
  no prompt, nag, or re-run; bootstrap/repair is offered only on an actual failure or explicit
  `/beads-init`.

## 3. Interfaces

- **CLI / scripts:** `scripts/beads_init.py` (run via `uv`), subcommands:
  - `verify [--json-output]` — read-only health check returning
    `ok|deps_missing|not_initialized|corrupted` (REQ-BINIT-001/002/003).
  - `repair [--apply] [--local-only] [--json-output]` — dry-run plan by default; `--apply` runs the
    standard repairs; `--local-only` also asserts no Dolt remote (REQ-BINIT-010–014, REQ-BINIT-020).
  - `status` — one-line human status (`initialized`/`functional` flags).
  Under macro `REQ-YF-PRE-006`/`REQ-YF-PRE-007` the verify/repair engine ports into the `yf` binary
  (`yf preflight` kernel); the skill's Python script remains the reference for the engine semantics.
- **Companion rule:** `protocols/BEADS_INIT.md` — the always-loaded preflight-routing + safety
  trigger — with `protocols/manifest.json` (sha256 + semver; current `BEADS_INIT.md` v1.0.0).
  Verified against the macro per-rule hash axis (`REQ-YF-PRE-003`).
- **Config / state:** none of its own today (the engine operates on `.beads/` and repo gitignore).
  After the rename, any per-repo config/runtime state would live at `.yf-beads-init.local.json` /
  `.yf/yf-beads-init/` per macro `REQ-YF-PRE-004`/`REQ-YF-PRE-005`; legacy `.bdinit.local.json` /
  `.state/beads-init/` (if any) migrate via macro `REQ-YF-MIGRATE-001`.

## 4. Guardrails (`GR-BINIT-NNN`)

- **GR-BINIT-001** *Drift:* inferring "not initialized" from `bd status`'s exit code and routing a
  wedged repo to `bd init`. *Rule:* classify by the parsed `error` **key**; a wedged-but-initialized
  repo is `corrupted`, repaired in place — never re-initialized (REQ-BINIT-002). *Why:* `bd init`
  on real data risks clobbering it.
- **GR-BINIT-002** *Drift:* `bd vc commit` before clearing the wedged migration. *Rule:* the fix
  order is `bd dolt stop → bd migrate schema → bd migrate`; `bd vc commit` cannot open the wedged
  DB (REQ-BINIT-011). *Why:* it deadlocks the repair.
- **GR-BINIT-003** *Drift:* adding a Dolt remote / `bd dolt push` to "fix" a local-only repo's
  `No remotes configured` warning. *Rule:* on local-only, assert `dolt.local-only true`, keep
  remotes empty, route upstream tracking to `yf-beads-upstream` (REQ-BINIT-020). *Why:* the warning
  is accepted by design; adding a remote changes the repo's storage model.
- **GR-BINIT-004** *Drift:* nagging or re-running repairs on a healthy repo. *Rule:* on
  `verify == ok` the preflight trigger is a silent no-op (REQ-BINIT-022). *Why:* repair is offered
  only on failure or explicit invocation.

## 5. Verification

- `verify`'s classification (REQ-BINIT-001/002/003) is verifiable with fixture repos: a healthy
  repo → `ok`; a repo whose `bd status --json` returns `{"error": …}` with exit 0 while
  `bd ready`/`bd list` work → `corrupted` (the false-negative regression); a repo with no `.beads/`
  → `not_initialized`; a missing tool → `deps_missing`. `repair`'s idempotence (REQ-BINIT-012) is
  verifiable by applying twice and asserting no second-pass change; the wedged-migration sequence
  (REQ-BINIT-011) by asserting the three-command order and that re-verify returns `ok`. The
  companion-rule hash (REQ-BINIT-021) is verified against `protocols/manifest.json`. These map to
  the macro spec's preflight three-state fixtures (`REQ-YF-PRE-006`, plan-010 Epic 6) once the
  engine ports to `yf`.

## 6. References

- `skills/beads-init/SKILL.md`; `skills/beads-init/scripts/beads_init.py`.
- `protocols/BEADS_INIT.md` (preflight-routing + safety trigger) and `protocols/manifest.json`.
- Root `SPEC.md` §3.5 (`REQ-YF-PRE-006`/`REQ-YF-PRE-007` — the ported verify/repair kernel), §3.9
  (`REQ-YF-MIGRATE-001`), §4 (BINIT), and `GUARDRAILS.md`.
- Sibling specs: `yf-beads-extra` (BEXTRA) for direct-CLI gotchas; `yf-beads-upstream` (BUP) for
  upstream tracking on a local-only DB.
