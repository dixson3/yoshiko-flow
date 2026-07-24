# SPEC — Beads Init (`yf-beads-init`)

> **Status: Active.** Per-skill SPEC for the beads verify/initialize/repair skill. The `yf-beads-init` rename is complete and the
> skill is shipped; this SPEC tracks the live behavior. Requirements use RFC-2119 "shall"; composed
> by the root `SPEC.md` macro spec.

## 1. Purpose & scope

`yf-beads-init` verifies, initializes, and repairs a functioning beads (`bd`) configuration in a
repository, and is the shared **dependency-verification home** that every other beads-backed
skill's preflight routes to when its own preflight reports missing deps, an uninitialized repo, or
a corrupted DB. It is also invoked directly (`/yf-beads-init`) when standing up beads in a new repo.

The verify/repair/status engine lives in the compiled `yf` kernel — `yf preflight yf-beads-init
--json` (verify) and `yf doctor --repair [--local-only] [--remove-remote]` (repair). **The `yf`
kernel is the reference implementation**; the `REQ-BINIT-*` requirements below describe that kernel
behavior. `scripts/beads_init.py` is a **retired shim** kept only for back-compat (it prints the new
`yf` invocation and exits non-zero), not a live engine.

**In scope:** the `verify`/`repair`/`status` engine; the false-negative classification (parse
`bd status --json` for an `error` **key**, not the exit code); the **mode-aware** repair sequence
for a wedged schema migration (server vs embedded storage); idempotent
gitignore/hooks/permissions/JSONL hardening; the local-only
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
  absent (`bd` ≥ 1.1.0, `uv`, `git`), and `not_initialized` only when there is no usable `.beads/`
  (genuinely uninitialized), so a wedged repo is never routed to `bd init` (which would risk
  clobbering real data).

### 2.2 Repair — sequence & safety

- **REQ-BINIT-010** *(testable)* `repair` shall default to a **dry-run** that prints the fix plan;
  `repair --apply` shall apply the standard repairs; exit is zero only when the post-repair
  re-verify returns `ok`.
- **REQ-BINIT-011** *(testable)* the wedged-schema-migration fix shall be **mode-aware**. In both
  modes the migration tail is `bd migrate schema` → `bd migrate`; they differ only in the
  working-set flush that precedes it:
  - **server mode:** `bd dolt stop` (flush the in-memory working set) → `bd migrate schema` →
    `bd migrate` (byte-for-byte the prior sequence).
  - **embedded mode** (`.beads/embeddeddolt/`, no Dolt server): a data-preserving working-set
    commit (REQ-BINIT-016) → `bd migrate schema` → `bd migrate`. `bd dolt stop` shall **not** be
    used — it errors in embedded mode (`not supported in embedded mode (no Dolt server)`) and
    `bd migrate schema` then fails against the dirty on-disk working set.

  The repair shall not route the flush through `bd vc commit`. **Version note (bd ≥ 1.1.0,
  REQ-BINIT-017):** the historical rationale — "`bd vc commit` cannot open the wedged DB
  (chicken-and-egg)" — held **only for bd < 1.1.0**. On bd ≥ 1.1.0 both `bd dolt commit` and
  `bd vc commit` *do* open a wedged embedded DB and commit the dirty working set, bypassing the
  migration guard (verified, EXP-001); `bd dolt commit` is in fact the fix bd's own wedge error
  now prescribes. The mode-aware flush above is retained as the version-agnostic default (raw
  `dolt` works on every bd line); what changes on 1.1.0 is only that the embedded commit *may*
  be the supported `bd dolt commit` (REQ-BINIT-016), not that `bd migrate schema` becomes safe —
  it still fails against a dirty set in all versions. (Macro `REQ-YF-PRE-007`.)
- **REQ-BINIT-016** *(testable)* for the **embedded-storage** layout, repair shall detect mode from
  the filesystem and clear the dirty working set with a **data-preserving commit** before
  `bd migrate schema`:
  - **Mode detection.** Read `.beads/metadata.json` and treat `dolt_mode == "embedded"` as
    embedded. When the key is missing/empty (a stale pre-`dolt_mode` metadata — plausible on the
    very upgrade that triggers the wedge), fall back to a filesystem probe: absence of
    `.beads/dolt-server.{pid,port}` ⇒ embedded. Mode shall **not** be inferred from a `bd` exit
    code, and a keyless repo shall **never** default to the server path (that is the path that
    fails).
  - **Path derivation.** Derive the Dolt-repo root as the unique directory under `.beads/`
    containing a `.dolt/` child (fallback: `metadata.json.dolt_database` under the data-dir base).
    On zero or more-than-one candidate the step shall **not guess** — it returns a non-zero rc with
    a "manual repair needed" message.
  - **Data-preserving commit.** In the derived cwd it shall run raw `dolt add -A`, then
    `dolt commit` **only if the working set is dirty** (a clean tree is a success no-op). It shall
    **never** `reset --hard` and **never** `--allow-empty`. When `dolt` is absent from PATH it shall
    attempt `bd dolt commit` before hard-failing with a remediation ("install dolt or commit the
    embedded working set manually"). **bd ≥ 1.1.0 (REQ-BINIT-017):** `bd dolt commit` is no longer
    merely a `dolt`-absent last resort — it is a *supported* commit of a wedged embedded working
    set (the command bd's own wedge error prescribes) and is data-preserving. Raw `dolt add -A &&
    dolt commit` is retained as the **bd < 1.1.0 fallback** and as the default when `dolt` is on
    PATH; no runtime bd-version floor is asserted, so the raw-`dolt` path shall never be removed
    outright.
  - **Partial-failure outcome.** If the commit succeeds but `bd migrate schema` still fails, repair
    shall report **FAIL / `corrupted`** with the working set **committed (recoverable)** and a
    manual-repair remediation — an acceptable, data-safe outcome (the genuine wedge is
    unreproducible, so this is the most likely real-world non-happy path).
- **REQ-BINIT-017** *(testable, #68)* the skill's guidance **shall be certified against bd 1.1.x**
  (the shipped Homebrew line; skills previously pinned 1.0.5). The certification records the
  empirically-verified 1.1.0 delta relevant to repair (EXP-001, plan-022): (a) on bd ≥ 1.1.0,
  `bd dolt commit` **and** `bd vc commit` open a wedged **embedded** DB and commit the dirty
  working set, **bypassing** the migration guard (bd's own wedge error prescribes `bd dolt
  commit`); (b) `bd migrate schema` still fails against a dirty working set in all versions (the
  chicken-and-egg is real for *that* command only); (c) the false-negative invariant
  (`REQ-BINIT-002`) still holds on 1.1.0 (a remote-migrate-gated `bd status` returns error-JSON
  with exit 0). No document shall carry the pre-1.1.0 blanket claim that `bd vc commit` "cannot
  open the wedged DB" without a version qualifier. **No hard runtime bd-version floor is
  asserted** — the raw-`dolt` embedded path (REQ-BINIT-016) is retained for bd < 1.1.0.
- **REQ-BINIT-012** *(testable)* repair hardening shall be idempotent and safe to re-run:
  permissions (`chmod 700 .beads`), gitignore drift (`bd doctor --fix` plus the engine's top-up
  patterns for `.beads/.gitignore` and project `.gitignore`), and a portable JSONL export
  (`bd export -o .beads/issues.jsonl`, not itself gitignored). Repair shall **not** install beads
  git hooks: the former `bd hooks install --force` step is removed (#31) — it is the inverse of
  the init-time `--skip-hooks` suppression and would re-dirty a clean repo.
- **REQ-BINIT-013** `not_initialized` repair shall confirm intent before init, then run
  `bd init --skip-hooks --skip-agents` (cruft-suppressed init, REQ-BINIT-015) and harden;
  `deps_missing` shall stop with the install list (no destructive action on a deps gap).
- **REQ-BINIT-015** *(testable, #31)* repair shall **suppress and clean** the cruft `bd init`
  injects so a fresh/repaired repo matches conventions automatically:
  - **Init-time:** the `not_initialized` path shall init with `--skip-hooks --skip-agents`
    (suppressing all four cruft classes: beads git hooks, the CLAUDE.md/AGENTS.md managed blocks,
    `.codex/`, `.agents/skills/beads/`, and the `.claude/settings.json` SessionStart hook), then
    assert `dolt.local-only true` and `doctor.suppress.git-hooks true`.
  - **Repair-time:** for an already-dirtied repo, repair shall run the idempotent, bd-native
    removers — `bd hooks uninstall` + reset `core.hooksPath` to the git default;
    `bd setup claude --remove`; `bd setup codex --remove`; `rm -rf .agents/skills/beads/`; a
    marker-scoped strip of the `<!-- BEGIN/END BEADS INTEGRATION -->` / `BEADS CODEX SETUP`
    blocks from CLAUDE.md & AGENTS.md — and shall prune `.claude/settings.json` **entry-scoped**,
    deleting the file **only when it becomes empty** (never wholesale, so a recommended-settings
    baseline, #30, is never clobbered). It shall likewise prune `.codex/config.toml`, deleting it
    **only when effectively empty** — the bare `[features]` residual `bd setup codex --remove`
    leaves once it strips `hooks = true`; a config holding any real key is preserved (dqo). Every
    remover shall be a no-op on a clean repo (re-running repair never churns).
- **REQ-BINIT-014** *(testable)* `repair` shall re-verify after applying and report the resulting
  status; the operator runs `bd doctor` expecting 0 errors, with `Remote Consistency: No remotes
  configured` accepted by design on a local-only repo and `Dolt Status` / `Git Working Tree`
  warnings treated as transient (clear on commit).

### 2.3 Local-only & preflight routing

- **REQ-BINIT-020** *(testable)* `repair --apply --local-only` shall assert
  `bd config set dolt.local-only true` and never `bd dolt push`; upstream issue tracking is
  `yf-beads-upstream`'s job. Repair never *adds* a Dolt remote. With the additional opt-in
  `--remove-remote` (valid only alongside `--local-only`), repair shall clear a configured remote
  at **both layers in one invocation (#61):** (a) the **Dolt-DB-level** remote (each row in
  `dolt_remotes`) — the **decisive** layer, and (b) the `sync.remote` **config** key — a secondary
  cleanliness step. **The remote-migrate gate keys solely on the Dolt-DB remote** (EXP-002:
  `SELECT COUNT(*) FROM dolt_remotes`); removing `sync.remote` alone leaves the repo still gated,
  and removing the Dolt remote alone clears it. Each layer is a no-op when already empty. Without
  `--remove-remote` any configured remote is left untouched.
  - **Wedged-DB caveat (EXP-002, load-bearing for the impl).** On a **wedged** DB (pending
    migrations) bd's *own* `bd config unset` and `bd dolt remote remove` are themselves gated and
    perform **no** mutation. Canonicalization on a wedged repo shall therefore remove the Dolt
    remote via **raw `dolt`** — `dolt remote remove <name>` in the derived `.beads/embeddeddolt/<db>/`
    (or server data dir), followed by the data-preserving `dolt add -A && dolt commit` of
    REQ-BINIT-016 — and edit `sync.remote` out of `config.yaml` **raw**, never via the gated bd
    subcommands. On a healthy DB the bd subcommands are acceptable.
- **REQ-BINIT-024** *(testable, #61)* the **instruction string** the preflight/doctor emits when it
  detects local-only remote drift shall name the command that actually clears it —
  `yf doctor --repair --local-only --remove-remote` — **including `--local-only`** (which
  `--remove-remote` requires; the prior string omitted it, making the suggested command a no-op).
  The **remote-migrate gate is cleared by canonicalization, not by an override:** once the
  **Dolt-DB remote** is removed (REQ-BINIT-020, via raw `dolt` on a wedged DB), a local-only repo
  is no longer "remote-backed" and bd auto-migrates on the next open **with no override**
  (EXP-002: all 4 pending migrations applied after a raw `dolt remote remove`, no
  `BD_ALLOW_REMOTE_MIGRATE`). `BD_ALLOW_REMOTE_MIGRATE=1 bd migrate` remains an **operator-gated**
  escape hatch for the case where a remote is *intentionally* retained — repair shall **never**
  auto-run it (it is the human coordination decision of REQ-BINIT-002's gate).
- **REQ-BINIT-023** *(testable, #39, #66)* repair shall include three idempotent canonicalization
  steps that are clean no-ops when nothing is tracked: (a) `git rm --cached` the pinned runtime
  set (`.beads/interactions.jsonl`, `.beads/embeddeddolt/`, `.beads/backup/`,
  `.beads/export-state.json`, `.beads/push-state.json`, `.beads/dolt-server.*`), keeping working
  files; (b) remove tracked `.beads/hooks/*` files **only** when content carries the `bd hooks run`
  shim signature (never a hand-edited hook); (c) the `--remove-remote` remote clear of (020). The
  preflight kernel shall additionally OFFER `yf doctor --repair` (read-only) when it detects this
  drift, performing no mutation itself.
  - **#66 — untrack ⇒ ignore parity.** `.beads/interactions.jsonl` is in the (a) untrack set but,
    pre-#66, was **not** in the `.beads/.gitignore` top-up set, so after `git rm --cached` it
    immediately resurfaced as `?? .beads/interactions.jsonl` noise. Repair's `.beads/.gitignore`
    top-up shall therefore also include `interactions.jsonl`, so a bead file that repair untracks
    is **also ignored** — after repair the file is untracked **and** ignored, with no
    `?? .beads/interactions.jsonl` resurfacing on the next `git status`.
- **REQ-BINIT-021** as a preflight dependency, another beads skill shall run its own
  system-deps/rule checks first, then on a beads-config failure (`bd_not_initialized`, a corrupted
  DB, or a `bd status` error JSON) route to `/yf-beads-init` / `yf preflight yf-beads-init --json`
  + `yf doctor --repair` rather than re-deriving the repair steps; the companion rule `protocols/BEADS_INIT.md` carries this
  trigger so it fires regardless of the active skill.
- **REQ-BINIT-022** when `verify` returns `ok`, the preflight trigger shall be a **silent no-op** —
  no prompt, nag, or re-run; bootstrap/repair is offered only on an actual failure or explicit
  `/yf-beads-init`.
- **REQ-BINIT-025** *(testable, #58)* repair is the correction half of the canonical minimal-local
  beads profile (`REQ-YF-PRE-010`). It shall correct **only the safe axes** — the local-only /
  no-remote invariant — reusing the plan-022 machinery: assert `dolt.local-only` (REQ-BINIT-020)
  and, under `--remove-remote`, clear a stray Dolt remote at both layers (REQ-BINIT-020/024).
  Repair shall **never migrate engine mode**: an **embedded** store (`dolt_mode: "embedded"` / no
  `dolt-server.*`) is **detect/warn-only** drift (surfaced by preflight with guidance, per
  REQ-YF-PRE-010), never converted server↔embedded — that conversion is invasive, unproven, and
  out of scope. A per-repo **local-server** store is conformant; repair applies no engine-mode
  action to it. Verified by fixtures tagged `REQ-BINIT-025`: missing-local-only / stray-remote →
  corrected; embedded → no mutation (warn only); local-server → conformant no-op.

## 3. Interfaces

- **CLI / kernel:** the verify/repair/status engine is the compiled `yf` kernel
  (`REQ-YF-PRE-006`/`REQ-YF-PRE-007`), invoked as:
  - `yf preflight yf-beads-init --json` — read-only health check returning
    `ok|deps_missing|not_initialized|corrupted` with `diagnostics`/`remediations`
    (REQ-BINIT-001/002/003).
  - `yf doctor --repair [--local-only] [--remove-remote]` — applies the standard repairs;
    `--local-only` asserts local-only Dolt; `--remove-remote` (with `--local-only`) additionally
    CLEARS a configured remote (REQ-BINIT-010–014, REQ-BINIT-020, REQ-BINIT-023).
  - `yf doctor` — one-line human status (`initialized`/`functional` flags).
  The `yf` kernel is the **reference implementation** for these requirements.
  `scripts/beads_init.py` is a retired back-compat shim that points stale callers at the `yf`
  commands above and exits non-zero — it is not a live engine.
- **Companion rule:** `protocols/BEADS_INIT.md` — the always-loaded preflight-routing + safety
  trigger — with `protocols/manifest.json` (sha256 + semver; current `BEADS_INIT.md` v1.0.3).
  Verified against the macro per-rule hash axis (`REQ-YF-PRE-003`).
- **Config / state:** none of its own today (the engine operates on `.beads/` and repo gitignore).
  After the rename, any per-repo config/runtime state would live at the canonical short-name
  `.yf/beads-init/config.local.json` / `.yf/beads-init/` per macro `REQ-YF-PRE-004`/`REQ-YF-PRE-005`
  (with the legacy root dotfile `.yf-beads-init.local.json` as a read-time fallback); legacy
  `.bdinit.local.json` / `.state/beads-init/` (if any) migrate to the canonical layout via macro
  `REQ-YF-MIGRATE-001` (`yf migrate`; preflight does not auto-migrate).

## 4. Guardrails (`GR-BINIT-NNN`)

- **GR-BINIT-001** *Drift:* inferring "not initialized" from `bd status`'s exit code and routing a
  wedged repo to `bd init`. *Rule:* classify by the parsed `error` **key**; a wedged-but-initialized
  repo is `corrupted`, repaired in place — never re-initialized (REQ-BINIT-002). *Why:* `bd init`
  on real data risks clobbering it.
- **GR-BINIT-002** *Drift:* routing the wedged-migration flush through `bd vc commit`. *Rule:* the
  fix order is a **mode-aware** working-set flush — server: `bd dolt stop`; embedded: a
  data-preserving raw `dolt add -A && dolt commit` in the derived Dolt-repo cwd (REQ-BINIT-016) —
  then `bd migrate schema → bd migrate`. The embedded escape hatch commits via **raw `dolt`**
  (default; the bd < 1.1.0 path) structurally bypassing bd's wedged migration gate. *Why:* on
  **bd < 1.1.0**, `bd vc commit` could not open the wedged DB and deadlocked the repair.
  **Version note (bd ≥ 1.1.0, REQ-BINIT-017):** this is no longer a hard prohibition — `bd dolt
  commit` (and `bd vc commit`) *do* open a wedged embedded DB on 1.1.0, and `bd dolt commit` is
  the supported, bd-prescribed commit (REQ-BINIT-016). The remaining rule is only that
  `bd migrate schema` must not run against a still-dirty set (it fails in every version) — flush
  first, by whichever commit the bd line supports.
- **GR-BINIT-003** *Drift:* adding a Dolt remote / `bd dolt push` to "fix" a local-only repo's
  `No remotes configured` warning. *Rule:* on local-only, assert `dolt.local-only true`, keep
  remotes empty, route upstream tracking to `yf-beads-upstream` (REQ-BINIT-020). Repair only ever
  *clears* a remote, and only under the explicit `--remove-remote` opt-in (REQ-BINIT-023) — it never
  *adds* one. *Why:* the warning is accepted by design; adding a remote changes the repo's storage
  model.
- **GR-BINIT-004** *Drift:* nagging or re-running repairs on a healthy repo. *Rule:* on
  `verify == ok` the preflight trigger is a silent no-op (REQ-BINIT-022). *Why:* repair is offered
  only on failure or explicit invocation.
- **GR-BINIT-005** *Drift:* (re-)installing beads git hooks during repair, or wholesale-deleting
  `.claude/settings.json` during cruft cleanup. *Rule:* repair never runs `bd hooks install`
  (only `bd hooks uninstall`); settings.json cleanup is entry-scoped and deletes the file only
  when empty (REQ-BINIT-015). *Why:* installing hooks inverts cruft suppression and re-dirties a
  clean repo; a wholesale settings.json delete would clobber a #30 recommended-settings baseline.

## 5. Verification

- `verify`'s classification (REQ-BINIT-001/002/003) is verifiable with fixture repos: a healthy
  repo → `ok`; a repo whose `bd status --json` returns `{"error": …}` with exit 0 while
  `bd ready`/`bd list` work → `corrupted` (the false-negative regression); a repo with no `.beads/`
  → `not_initialized`; a missing tool → `deps_missing`. `repair`'s idempotence (REQ-BINIT-012) is
  verifiable by applying twice and asserting no second-pass change; the wedged-migration sequence
  (REQ-BINIT-011) by asserting the mode-aware command order — server plans carry `bd dolt stop`,
  embedded plans carry the `dolt-commit-embedded` native step (never `bd dolt stop`) with a
  **derived** (not hardcoded) path — ahead of `bd migrate schema` → `bd migrate`, and that
  re-verify returns `ok`. The embedded native step's data-preserving commit + clean-tree no-op +
  mode detection (REQ-BINIT-016) is verifiable against a real `bd init` embedded repo with a
  synthetically-dirtied working set. The two-layer `--remove-remote` (REQ-BINIT-020) and the corrected instruction string
  (REQ-BINIT-024) are verifiable against a fixture repo with **both** a `sync.remote` config key
  and a Dolt-DB-level `origin` remote: after `repair --local-only --remove-remote`, `bd config get
  sync.remote` and `bd dolt remote list` are both empty, and the emitted drift instruction reads
  `yf doctor --repair --local-only --remove-remote`. The plan-022 micro-experiment (Issue 4.2)
  records that removing both layers clears bd 1.1.0's remote-migrate gate without
  `BD_ALLOW_REMOTE_MIGRATE`. The 1.1.0 certification (REQ-BINIT-017) is verified by
  EXP-001 (plan-022 `findings/exp-001-embedded-wedged-commit.md`): a genuine wedged embedded
  fixture (schema-49 embedded DB reopened by bd 1.1.0 with real pending migrations 0050–0053) on
  which `bd dolt commit`/`bd vc commit` open and commit the dirty set while `bd migrate schema`
  still fails — and by a repo-wide check that no document carries the unqualified
  "`bd vc commit` cannot open the wedged DB" claim. The
  companion-rule hash (REQ-BINIT-021) is verified against `protocols/manifest.json`. These map to
  the macro spec's preflight three-state fixtures (`REQ-YF-PRE-006`, plan-010 Epic 6) once the
  engine ports to `yf`.

## 6. References

- `skills/yf-beads-init/SKILL.md`; `skills/yf-beads-init/scripts/beads_init.py`.
- `protocols/BEADS_INIT.md` (preflight-routing + safety trigger) and `protocols/manifest.json`.
- Root `SPEC.md` §3.5 (`REQ-YF-PRE-006`/`REQ-YF-PRE-007` — the ported verify/repair kernel), §3.9
  (`REQ-YF-MIGRATE-001`), §4 (BINIT), and `GUARDRAILS.md`.
- Sibling specs: `yf-beads-extra` (BEXTRA) for direct-CLI gotchas; `yf-beads-upstream` (BUP) for
  upstream tracking on a local-only DB.
