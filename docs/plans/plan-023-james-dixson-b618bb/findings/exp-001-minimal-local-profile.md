# EXP-001 — Minimal-local beads profile surface (#58) + config-resolution/migration facts (#67)

**Plan:** plan-023-james-dixson-b618bb · **Date:** 2026-07-05 · **bd:** 1.1.0 (Homebrew)
**Method:** read-only source inspection of `yf/src/` + `skills/yf-*/` + a throwaway `bd init` /
`git worktree` experiment under a sandboxed `$HOME` (never touched the real repo's `.beads/`).

## Finding: the surface for a canonical MINIMAL-LOCAL profile

The three profile invariants (#58) are each expressible in signals the `yf` kernel already reads,
and the engine-mode question resolves decisively to **embedded** on empirical evidence. The
detect/offer/correct hooks already exist (REQ-BINIT-023 / `detect_canonicalization_drift`); a
profile-drift check folds into them without new preflight-mutation surface.

---

## A. Profile config expression — the exact knobs per invariant

### Recommended profile definition (the canonical MINIMAL-LOCAL profile)

| # | Invariant | Canonical value | Where recorded / how detected |
| :-- | :-- | :-- | :-- |
| 1 | One DB per repo (per-project, NOT shared-server) | `dolt_mode: "embedded"` + `.beads/embeddeddolt/<db>/` present, NO `.beads/dolt-server.{pid,port}` | `.beads/metadata.json` `dolt_mode` key; filesystem probe |
| 2 | Reachable from every worktree | (automatic — git-common-dir resolution; see §B) | no config knob; `bd list` non-zero-exit probe from the worktree |
| 3 | Never synced upstream | `dolt.local-only: true`; zero rows in `dolt_remotes`; no `sync.remote` config key | `bd config get dolt.local-only --json`; raw `dolt remote`; `bd config get sync.remote --json` |

### Invariant 1 — engine mode: server vs embedded vs shared-server

- **Where mode is recorded.** `.beads/metadata.json` carries `"dolt_mode"`. Empirical `bd init`
  output (throwaway repo):
  ```json
  { "database": "dolt", "backend": "dolt", "dolt_mode": "embedded",
    "dolt_database": "repo", "project_id": "5040558d-..." }
  ```
  Server mode is instead signalled by `.beads/dolt-server.{pid,port}` files on disk.
- **How the kernel decides mode** (`yf/src/beads_init.rs:630` `decide_embedded`): an explicit
  `dolt_mode` of `"embedded"`/`"server"` wins; a missing/empty/unknown value falls back to the
  filesystem probe — **absence of the `dolt-server.*` files ⇒ embedded** (`beads_init.rs:646`
  `is_embedded_mode`). Mode is *never* inferred from a `bd` exit code (REQ-BINIT-016).
- **"shared-server" / `--shared-server`:** no such flag/signal appears anywhere in `yf/src/` or the
  skills. `grep` for `shared-server`/`shared_server` finds nothing. "Per-project, not shared across
  repos" is therefore detected positively as **embedded storage under this repo's own `.beads/`**
  (an `embeddeddolt/<db>/` dir with a `.dolt/` child, derived by `derive_dolt_repo_root`,
  `beads_init.rs:704`), i.e. the DB is a child of the repo — not a machine-global server the config
  points at. There is no port/host config to point elsewhere.
- **Recommendation: EMBEDDED is the canonical choice** (evidence in §B decides it):
  1. It is what `bd init` produces by **default** (no server, no port) — the least-config path.
  2. It is inherently **per-project** — the store lives at `.beads/embeddeddolt/<db>/` under the
     repo, so it cannot be a cross-repo shared server.
  3. It **already satisfies worktree-sharing** via git-common-dir (§B) with the DB stored **once**
     (no per-worktree duplicate).
  4. The whole repair/verify kernel is already mode-aware and treats embedded as the primary path
     (REQ-BINIT-016; the keyless-fallback in `decide_embedded` deliberately biases to embedded).

  A local-server repo *could* also satisfy per-project + local-only + worktree-shared, but it adds a
  running daemon, port files, and the `bd dolt stop` flush path — strictly more moving parts for no
  gain on a single-operator local-only repo. **Recommend the profile assert `dolt_mode == embedded`
  and flag server mode as drift** (correcting it is an engine-mode *migration* — the plan's noted
  "riskiest correction", gate behind explicit `--repair`, never automatic).

### Invariant 3a — local-only

Confirmed `dolt.local-only` bd config, read via `bd config get dolt.local-only --json`
(`beads_init.rs:962` `bd_config_value`, using the `--json` form because the plain-text form prints a
`(not set …)` sentinel at exit 0, #43). Repair asserts it with
`bd config set dolt.local-only true` (`beads_init.rs:496`, and at init `:457`). SPEC:
**REQ-BINIT-020** (`skills/yf-beads-init/SPEC.md:143`) — "`repair --apply --local-only` shall assert
`bd config set dolt.local-only true` and never `bd dolt push`."

### Invariant 3b — no remote

Two layers, per plan-022 EXP-002, encoded in `has_local_only_remote` (`beads_init.rs:993`):
- **Decisive layer:** the Dolt-DB-level remote — a row in `dolt_remotes`, enumerated via raw
  `dolt remote` in the derived Dolt-repo cwd (`dolt_remote_names`, `beads_init.rs:1014`). The bd
  1.1.0 remote-migrate gate keys **solely** on this (SPEC REQ-BINIT-020, `SPEC.md:149`:
  `SELECT COUNT(*) FROM dolt_remotes`).
- **Secondary layer:** the `sync.remote` config key (`bd config get sync.remote`).
The `--remove-remote` opt-in clears both (`remove_dolt_remote`, `beads_init.rs:1149`): raw
`dolt remote remove` + data-preserving commit for layer 1, raw `config.yaml` edit for layer 2 (both
bd subcommands are themselves gated on a wedged DB — SPEC.md:153 "Wedged-DB caveat").

---

## B. Worktree-shared — the load-bearing engine-mode evidence

**Empirical test (throwaway repo, embedded mode):** created bead `repo-aze` in the primary
checkout, `git worktree add`, then from the worktree:
- `bd list` from the worktree **saw `repo-aze`** (the primary's bead).
- `bd create worktree-bead-beta` from the worktree → the primary's `bd list` then showed **both**
  `repo-aze` and `repo-4u3` (bidirectional, same DB).
- The worktree's `.beads/` had **no `embeddeddolt/`** dir (`ls` → "No such file or directory"): the
  Dolt store is **NOT duplicated** — it lives once, in the primary.
- The worktree's `.git` is a file: `gitdir: …/repo/.git/worktrees/wt`; `git rev-parse
  --git-common-dir` from the worktree resolves to the **primary's** `…/repo/.git`.

**Mechanism.** bd resolves the canonical `.beads/` via **git-common-dir**, so a worktree reaches the
primary's single embedded Dolt store automatically. This is exactly yf-plan's **INV-2**, stated in
`skills/yf-plan/scripts/plan_manager.py:1178`: *"Beads (INV-2): the worktree shares the primary's
single Dolt DB via git-common-dir."* The runtime probe is `_bd_resolves_from` (`plan_manager.py:1352`
— `bd list --json` from the worktree, success = resolves), and viability requires the **primary** to
own `.beads/` (`_worktree_viability`, `:1389`: "No .beads → bd not initialized here").

Note: the tracked `.beads/` metadata (`config.yaml`, `metadata.json`, `.gitignore`, `hooks/`,
`interactions.jsonl`, `README.md` — confirmed via `git ls-files`) is materialized into the worktree
by git, but the **live Dolt data** (`embeddeddolt/`, gitignored) resolves back to the primary. The
tracked metadata is not what makes sharing work — git-common-dir is.

**Conclusion (decides §A):** embedded mode does **NOT** break worktree-sharing — it shares the one
DB with zero duplication. This removes the only hypothetical argument for preferring a local-server.
**Embedded is canonical.**

---

## C. What yf preflight/doctor already inspects — the integration points

### Read-only preflight (never mutates)

`yf/src/preflight.rs` — the shared kernel every beads skill converges through (`run_with_env`,
`:245`). On the beads-healthy `ok` path it computes a **read-only** drift offer:

- `detect_canonicalization_drift(repo_root)` — `preflight.rs:709`, called at `:330`. Inspects
  tracked git state + bd config and returns `instructions` strings (never mutates). Today it detects
  three gaps and offers `yf doctor --repair`:
  1. tracked runtime `.beads/` artifacts (via `tracked_canonicalization_drift`, `beads_init.rs:932`);
  2. tracked `.beads/hooks/*` bd shims;
  3. a Dolt remote under local-only (`has_local_only_remote`, `beads_init.rs:993`).

  **This is the fold-in point for a #58 profile-drift check** (REQ-BINIT-023 / #39 hook). A new
  signal — e.g. `dolt_mode != "embedded"`, or `dolt.local-only != true`, or a stray `dolt_remotes`
  row — is added as another `out.push("Canonicalization drift: …")` here. All the reader helpers it
  needs already exist: `is_embedded_mode` (`beads_init.rs:646`), `bd_config_value` (`:962`),
  `dolt_remote_names` (`:1014`), `read_dolt_database` (`:655`).

- Verify itself: `beads_init::verify` (`beads_init.rs:179`), wired into preflight via `bd_init_status`
  (`preflight.rs:619`). Reads `.beads/` presence, `bd status --json` (classified by the `error`-key
  parse, not exit code — REQ-BINIT-002), `.beads` perms, and `bd doctor` output.

### Mutating doctor (`--repair`, operator-authorized)

`yf/src/cmd/doctor/mod.rs` — read-only by default (DEC-1, `mod.rs:6`). `--repair` short-circuits the
read-only axes (`mod.rs:34`) and calls `beads_init::repair(repo, apply=true, local_only,
remove_remote)` (`mod.rs:122` `run_repair`). The repair plan (`beads_init.rs:407`) is where a
profile *correction* step is added.

**The read-only vs mutating convention (cite):** preflight performs **NO** canonicalizing mutation —
"the only sanctioned preflight write remains `ensure_scaffold`" and "the offer is an instruction
string the operator acts on by explicitly running `yf doctor --repair`" (`preflight.rs:320-328`).
Doctor is read-only by default and only `--repair` (explicit opt-in) mutates (`doctor/mod.rs:6-11`).
SPEC REQ-BINIT-023 (`SPEC.md:171`): "The preflight kernel shall additionally OFFER `yf doctor
--repair` (read-only) when it detects this drift, **performing no mutation itself**." So a #58
profile check follows the same split: **preflight detects + offers (read-only); doctor --repair
corrects (mutating, operator-authorized).**

---

## D. Config resolution + migration facts (for #67)

### Current config resolution

`read_config` (`preflight.rs:430`) precedence (contract §7):
1. **New:** `.yf/<short>.local.json` at repo root (e.g. `.yf/plan.local.json`) — note this is a
   file **directly under `.yf/`**, NOT inside a per-skill subdir.
2. **Legacy fallback:** `.<config-basename>` at repo root, where `config-basename` comes from the
   skill's SKILL.md frontmatter (`frontmatter.rs:144`). Every skill declares one, all root-level
   dotfiles: `.yf-plan.local.json`, `.yf-research.local.json`, `.yf-beads-init.local.json`,
   `.yf-beads-upstream.local.json`, `.yf-optimal-instructions.local.json`. **This is exactly #67's
   complaint** — each new skill adds another top-level dotfile + gitignore anchor.

Runtime **state** path (distinct from config): `state_path` (`preflight.rs:451`) =
`.yf/<short>/preflight.json`, using the **short** name (`plan`, not `yf-plan`) from `resolve_skill`
(`preflight.rs:221`). So state is *already* namespaced under `.yf/<short>/`; #67 proposes moving
config alongside it as `.yf/<skill>/config.local.json`.

### REQ-YF-MIGRATE-001 — the reusable migration mechanism

`yf/src/migrate.rs` (`yf migrate`, REQ-YF-MIGRATE-001). Idempotent legacy→new mover with three
guarantees (`migrate.rs:12`): no-op when source absent; **never clobber an existing dest** (reports
`DestExists`, leaves source); safe to re-run. Core: `plan_and_apply` (`:118`) classifies each
source→dest pair and `move_path` (`:149`) does an atomic rename with copy+remove cross-fs fallback.
Driven by a static `SKILL_MAP` (`:30`) of `(old, new)` name pairs. It currently migrates two kinds:
- `.state/<old>/` → `.yf/<new>/`
- `.<old>.local.json` → `.yf-<new>.local.json`

**#67 can extend this directly:** add a third migration kind (root-level `.<skill>.local.json` /
`.yf-<skill>.local.json` → `.yf/<skill>/config.local.json`) to the same `plan_and_apply` loop; the
idempotency + never-clobber machinery is reused verbatim.

### Shortname mapping — present, but NOT centralized (a #67 hazard)

There **is** a shortname map in the kernel: `resolve_skill` (`preflight.rs:221`) maps
`plan|yf-plan|bdplan → (dir="yf-plan", short="plan")` and generically strips a `yf-` prefix. State
uses the **short** name → `.yf/plan/`.

**But there are two inconsistencies #67 must reconcile:**
1. `migrate.rs` has its **own** `SKILL_MAP` (`:30`) whose *new* names are the **full** `yf-plan`,
   `yf-research`, … — it does NOT strip the prefix. So `yf migrate` sends state to **`.yf/yf-plan/`**,
   while the live `preflight.rs` reads/writes state at **`.yf/plan/`**. These disagree (full vs short
   name). The shortname mapping is not shared between the two modules.
2. The preflight-contract §7 documents the "new" config path as `.yf-<skill>.local.json` (still a
   **root dotfile**, just `yf-`-prefixed) — while the *code* (`read_config`) already prefers
   `.yf/<short>.local.json`. #67's proposed `.yf/<skill>/config.local.json` is a third shape. The
   contract table, `read_config`, `ensure_scaffold` (the config-basename gitignore anchor,
   `preflight.rs:944`), and `migrate.rs` all need to converge on one location under `.yf/<short>/`.

The single `/.yf/` gitignore anchor already exists (`YF_ANCHOR`, `preflight.rs:50`), so collapsing
per-skill anchors to one is mostly a matter of stopping `ensure_scaffold` from also adding the
per-`config-basename` anchor (`preflight.rs:944-947`).

---

## Recommendations for the plan

1. **Profile (#58):** assert the three invariants as `dolt_mode == embedded` (metadata + fs probe),
   `dolt.local-only == true`, and empty `dolt_remotes` + no `sync.remote`. Worktree-sharing needs
   **no** asserted knob — it is automatic under embedded via git-common-dir; optionally assert the
   `_bd_resolves_from`-style probe as a health check, not a config value.
2. **Engine mode:** canonical = **embedded**. Detect `dolt_mode == "server"` (or `dolt-server.*`
   present) as drift. Correcting it is an engine-mode migration — the riskiest correction; keep it
   behind explicit `yf doctor --repair` confirmation, never automatic (matches the plan's risk note).
3. **Detect/correct wiring:** fold the profile check into `detect_canonicalization_drift`
   (`preflight.rs:709`, read-only offer) and add the correction step to `beads_init::repair`
   (`beads_init.rs:407`, mutating under `--repair`). Reuse `is_embedded_mode`, `bd_config_value`,
   `dolt_remote_names`, `has_local_only_remote`.
4. **#67:** extend `migrate.rs`'s `plan_and_apply` loop with a config→`.yf/<skill>/config.local.json`
   kind; reconcile the `.yf/yf-plan/` (migrate.rs) vs `.yf/plan/` (preflight.rs) name mismatch by
   centralizing the shortname map; update `read_config` precedence and the preflight-contract §7
   table together; drop the per-config-basename gitignore anchor in favor of the single `/.yf/`.
