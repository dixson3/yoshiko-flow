# Plan: Rename skills to `yf-` prefix and build the `yf` Rust CLI

**ID:** plan-010-james-dixson-73eebd
**Author:** James Dixson
**Created:** 2026-06-14
**Status:** reconciling
**Epic:** beads-skills-mol-yvv
**Phase log:**
- 2026-06-14 scoping: initial scope captured
- 2026-06-14 investigating: reference recon complete (naba/tap/install.py); 4 scoping decisions resolved
- 2026-06-14 drafting: plan v1 presented
- 2026-06-14 review: plan v1 presented
- 2026-06-14 review: pass-2 presented (REVISE → addressed in v3)
- 2026-06-14 approved: Gate G0 sealed — SPEC.md + GUARDRAILS.md operator-approved; INTAKE unblocked
- 2026-06-14 approved: operator approved; G0 sealed
- 2026-06-14 intake: epic beads-skills-mol-yvv poured
- 2026-06-14 executing: start gate resolved; worktree execution begun
- 2026-06-15 executing: all build/test beads closed incl INV-1 self-rename (Issue 3.7, last); G1+G2 gates resolved (operator-approved, tests green)
- 2026-06-16 executing: operator follow-up — SPEC REQ-YF-PRE-004 config-path typo ratified; GFM markdown-lint enforcement added to yf-plan/yf-research/yf-incubator; yf-research Obsidian citations → GFM
- 2026-06-16 reconciling: merged plan branch into local main (--no-ff); merged-state re-validated green (yf 97 tests, G1 install round-trip, G2 preflight parity, 18+8 python tests, markdown lint); worktree + ephemeral branch torn down (branch was merged, no commits lost). DEFERRED per operator (no push): upstream push (bd dolt push + git push), §6.3 upstream reconcile (Issue 5.3 land yvv.5.4 — close #14 / comment #15 / file tracking issue), G3 release dry-run (token added), G4 docs hosting

## Objective

Two coupled deliverables for the beads-skills repo (`dixson3/yoshiko-flow`):

1. **Rename every skill** to a `yf-` prefix. Two special-cases: `bdplan → yf-plan`,
   `bdresearch → yf-research`. All others take the bare prefix (`beads-extra → yf-beads-extra`,
   `drift-check → yf-drift-check`, …). Invocations become `/yf-plan`, `/yf-research`, etc.
2. **Build `yf`**, a Rust CLI distributed via Homebrew, that (a) embeds the skill tree in its
   binary and manages the skill install/upgrade lifecycle (`yf skills …`, modeled on
   `naba skills`), (b) provides `yf doctor`, and (c) hosts the **shared preflight/config
   kernel** that today lives in per-skill Python `check`/`verify` functions. `yf` replaces
   `install.sh`/`install.py`.

## Motivation

The skills are branded around `bd`/`beads` internals (`bdplan`, `bdresearch`) and installed by a
Python script (`install.py`) that users must clone the repo to run. The project is graduating to a
named product surface — **Yoshiko Flow** (`yf`) — with a single, brew-installable entrypoint.
A consistent `yf-` namespace makes the skill family legible as one product; a compiled `yf`
binary gives a zero-clone install (`brew install dixson3/tap/yf && yf skills install`),
transitively pulls the `bd`/`uv` toolchain via Homebrew dependencies, and centralizes the
duplicated preflight/tool-check logic (upstream #15) currently copy-pasted across `install.py`,
`plan_manager.py`, `research_manager.py`, and `beads_init.py`. This supersedes the `install.py`
group-installer (upstream #14) with a distributable tool.

## Upstream Issues

| Issue | Title                                                             | Disposition            | Notes                                                                                                                                                      | Resolved By    |
| :---- | :---------------------------------------------------------------- | :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------- |
| #14   | Install groups: frontmatter contract + dependency-aware installer | supersede              | `install.py`'s group/closure logic is reimplemented in `yf skills`; `install.py` is removed                                                                | Epic 1, Epic 5 |
| #15   | Consolidate duplicated Python helpers (tool-presence check)       | partial                | The `shutil.which` tool-check + bd-version + rule-hash logic consolidates into the `yf` preflight kernel; remaining Python-domain helpers are out of scope | Epic 2         |
| (new) | yf rename + CLI tracking issue (plan-010)                         | file at land-the-plane | Coarse-granularity per AGENTS.md (one issue per plan)                                                                                                      | Epic 5         |

## Investigation Findings

See `findings/exp-001-reference-recon.md`. Highlights:

- **naba is Go + goreleaser**, not Rust — its *behavior* is the model, its *toolchain* is not.
  Rust analogs chosen: `rust-embed` (skill embed), **cargo-dist** (release + Homebrew publish).
- naba's behavioral model to replicate: `skills {install,upgrade,remove,status}` with
  `--scope/--surface/--target/--dry-run`; dest resolution identical to `install.py`; a
  **tree-hash integrity marker** injected into `SKILL.md` (`<!-- yf-skills: v=… tree=… -->`);
  stale-file prune on upgrade; `doctor` with per-axis checks and `--json`.
- **Dependencies resolve from homebrew-core**: `bd` ships as the **`beads`** formula; `uv` is
  `uv`. So `depends_on "beads"` + `depends_on "uv"` — no custom tap for deps. Tap is
  `dixson3/tap` (repo `dixson3/homebrew-tap`).
- **Two integrity axes coexist** and `yf` must keep both: naba-style **whole-tree freshness**
  (drives `skills status`/`upgrade`/`doctor`) and the existing **per-rule `manifest.json`
  sha256+semver** (drives preflight `rule_missing/rule_drift/rule_deprecated`).
- `install.py` responsibilities (frontmatter parse → group compute → transitive `depends-on-skill`
  closure → tool check → dest resolve → copy → companion-rule install) are fully enumerated and
  portable to Rust.
- Preflight/config kernel to move: `plan_manager.py check`, `research_manager.py check`,
  `beads_init.py verify`/`repair`. Domain logic (init/audit/pour/worktree, research index, etc.)
  stays in Python. **The `bd status --json` "inspect for `error` key, not exit code" invariant**
  must port faithfully.

## Approach

**Decisions (operator-ratified):**

- **A — Release:** cargo-dist (Rust-native release matrix + Homebrew formula publish to
  `dixson3/homebrew-tap`, semver from git tags).
- **B — Preflight depth:** *shared kernel only*. `yf` owns tool detection, bd-version gate,
  rule-hash/semver verification, `.<skill>.local.json` config reads, `.yf/` state scaffold +
  gitignore anchors, and beads-init verify/repair. Per-skill SKILL.md preflight calls `yf`
  instead of `uv run …check`. Python domain logic stays.
- **C — Rename:** clean break, no aliases. Config files rename (`.bdplan.local.json →
  .yf-plan.local.json`); **the runtime-state root renames `.state/ → .yf/`** (per-skill subdir
  keyed by new name, e.g. `.yf/yf-plan/preflight.json`). A one-time migration note covers repos
  carrying old config/state (including this repo).
- **D — Location:** `yf` Cargo crate at the **root of this repo**; embeds `skills/` at build;
  releases tagged here; formula pushed to `dixson3/homebrew-tap`.
- **D5 — Docs deployment (operator-pending):** Docusaurus source lives in-monorepo (`website/`);
  the publish target is **`yoshiko-flow.github.io`** via GitHub Pages, but the exact strategy
  (org-site repo vs. project pages, branch, custom domain) is confirmed by the operator before
  Issue 7.3 enables the deploy workflow.
- **NAME — `yf` (operator-ratified; see exp-003).** The binary is **`yf`**. The IP check on `yf`
  is **clear on the axes that matter for a 2-letter command**: no Homebrew formula (or formula
  shipping a `yf` binary), no shell builtin/alias/standard binary, and crates.io/RubyGems/Go are
  free. The only namesake is an abandoned 21★ Yahoo-Finance `yf` CLI (no brew formula, finance-
  adjacent — irrelevant to us); npm/PyPI `yf` slugs are dormant non-CLI placeholders. `yf` also
  cleanly matches the `yf-` skill prefix (`yf skills install`, `yf doctor`). The earlier `yflow`
  option was dropped due to an active same-domain PyPI `yflow` CLI (exp-002). Product/brand name
  remains **Yoshiko Flow**; the binary, the `yf-skills` marker, and the runtime state dir **`.yf/`**
  are all consistently `yf`.

**Sequencing rationale.** The rename (Epic 3) must land before `yf` embeds/describes the final
tree, but `yf`'s scaffolding (Epic 1 crate/CLI mechanics) is name-agnostic and can begin in
parallel. Preflight (Epic 2) consumes both the binary and the renamed skills. Distribution
(Epic 4) needs a building binary. Crate verification (Epic 6) backs the capability gates.
Decommission (Epic 5) is last. Capability gates guard the irreversible steps (deleting
`install.py`, cutting a real release).

**Self-rename isolation (INV-1).** The skill *driving* this plan is `bdplan`, installed at
`~/.claude/skills/bdplan`, with a hardcoded `SKILL_DIR` resolver (`find … -name bdplan`) and a
`.state/bdplan/` runtime root. Renaming `bdplan → yf-plan` (and `bdresearch → yf-research`) in the
**canonical repo tree** mid-execution would diverge the running orchestrator from its renamed
source and break any bdplan subcommand that re-resolves `SKILL_DIR` or reads `.state/bdplan/`.
Invariant: **the driving session runs from the installed `~/.claude/skills/bdplan` copy (never the
repo tree), and the self-renaming step (Issue 3.7) is the LAST execution step**, performed in the
plan-009 merge-back worktree and landed only at Phase 6. The installed copy is untouched by the
plan; a separate `yf skills install` (post-land) is what migrates the operator's own
environment to `yf-plan`/`yf-research`. (R7.)

## Specification & Guardrails (pre-intake — sealed before the epics are intaked)

These two artifacts are authored **during PLAN and sealed before INTAKE**, not as execution epics.
bdplan has no EXECUTE→PLAN transition, so a spec that could reshape epics must be settled *before*
the Epic 1–7 beads are poured. The downstream epics are written against the **sealed** spec, and
Epic 6's tests reference its `REQ-…` ids (which therefore exist before those beads are created).

- **`SPEC.md`** (repo root) — the **macro spec**: numbered, testable `yf`-tool requirements
  (`REQ-YF-*`) for skills `install/upgrade/remove/status`, the SKILL.md hash/marker up-to-date
  semantics, the `yf preflight` JSON contract + kernel checks, `doctor` axes, rename invariants
  (incl. INV-1), and the distribution contract — **plus a composition model**: the macro spec is
  *inferred* from this root + the union of **per-skill `skills/<skill>/SPEC.md`** files
  (`REQ-<KEY>-NNN`). Each testable requirement is the anchor a later integration/system test names.
- **Per-skill SPECs** — every skill carries `skills/<skill>/SPEC.md` (schema:
  `skills/SPEC-TEMPLATE.md`). The macro spec's §4 catalog references them. **All 13 are primed
  pre-intake as drafts** (`REQ-<KEY>-NNN`, grounded in each skill's SKILL.md + `spec/*.md`); Issue
  3.8 refreshes them to final state when the skill dirs rename (the SPEC moves with its dir) and
  wires the per-skill `SPEC.md ↔ SKILL.md` drift edges. Catalog paths are the post-rename targets
  (`skills/yf-<skill>/SPEC.md`); the drafts currently live at the pre-rename `skills/<old>/SPEC.md`.
- **`GUARDRAILS.md`** (repo root) — counterfactual / out-of-domain boundaries that keep the project
  from drifting: what `yf` is **not** (not a general package manager, not a `bd`/Dolt replacement,
  not an AI/skill *runtime*, not a markdown/doc engine); scope fixed to skill-lifecycle management +
  the shared preflight/config kernel + distribution. Each guardrail states the tempting drift and
  the rule that forbids it. Made non-inert by the SPEC↔GUARDRAILS↔README drift edge (Issue 5.4).
- **Pre-intake Gate G0** (see Gates) seals both. If review reshapes them, the epics below are
  edited **in PLAN** (native — they are not yet intaked); only after sign-off does INTAKE pour the
  beads. This replaces the earlier (incorrect) in-execution G0 + EXECUTE→PLAN loop.

## Epics

> **Gating note.** The epics below are **poured only after Gate G0 seals SPEC.md + GUARDRAILS.md**
> (pre-intake). Because sealing happens before any bead exists, no epic carries a bead-level
> dependency on G0 — the seal gates the INTAKE step itself. Epic 6's tests reference the sealed
> `REQ-…` ids.

### Epic 1: `yf` CLI foundation — embed + skills lifecycle + doctor
Name-agnostic; may start immediately once the spec is sealed.
- Issue 1.1: Cargo crate at repo root (`yf`), clap CLI skeleton, `yf version` (semver +
  build git info), workspace/`.gitignore` wiring. **entry**
- Issue 1.2: Embed `skills/` via `rust-embed` (or `include_dir`); embedded-tree enumeration API
  (skill names, per-skill file list, read-file). depends-on: 1.1
- Issue 1.3: Frontmatter parser (`name`, `skill-group`, `depends-on-tool`, `depends-on-skill`,
  `user-invocable`) over embedded `SKILL.md`s; group computation; transitive `depends-on-skill`
  closure with cross-group/external logging (install.py parity). depends-on: 1.2
- Issue 1.4: **SKILL.md hash/marker — the canonical up-to-date check (naba strategy).** Dest
  resolution (`--scope {user,project}`, `--surface {claude,agents}`, `--target`) plus the marker
  engine: compute a per-skill **tree hash** = SHA256 over each file (sorted by relpath) as
  `relpath-bytes ++ file-bytes`, with `SKILL.md` **marker-stripped before hashing** so a deployed
  (marked) copy hashes identically to the embedded source. On install, inject a single HTML-comment
  marker into `SKILL.md` after the YAML frontmatter: `<!-- yf-skills: v=<yf ver>
  tree=<sha256> -->`. Provide inject / strip / parse / verify and `EmbeddedTreeHash(skill)` +
  `DeployedTreeHash(dir)`. depends-on: 1.2
- Issue 1.5: `yf skills install` — copy skill tree + companion rules (`protocols/*.md →
  <surface>/rules/`), inject the 1.4 marker into the deployed `SKILL.md`, `--group`, positional
  names, `--strict`, `--dry-run`, `--force`. depends-on: 1.3, 1.4
- Issue 1.6: `yf skills {upgrade,remove,status}` — **status/up-to-date detection driven by the
  1.4 marker**: parse the deployed `SKILL.md` marker hash and compare to the embedded tree hash →
  report `installed` (SKILL.md present), `up-to-date` (deployed marker hash == embedded), `complete`
  (all embedded files present), `unmodified` (recomputed deployed hash, marker-stripped, ==
  embedded — detects local tampering). `upgrade` rewrites + re-injects the marker + **prunes stale
  files**. depends-on: 1.5
- Issue 1.7: `yf doctor` (`version`, `bd`+version≥1.0.5, `uv`, `git`, per-skill `skills:<name>`
  health **via the 1.6 marker comparison** — flags `not installed` / `outdated (run yf skills
  upgrade)` / `incomplete` / `modified`, companion-rule presence/hash), human + `--json`, nonzero
  exit on fail. depends-on: 1.6
- **Capability Gate G1**: `yf skills install` round-trips before Epic 5 deletes `install.py`.

### Epic 2: Preflight/config kernel in `yf`
Depends on Epic 1 (binary + embed) and Epic 3 (final skill names in descriptors).
- Issue 2.1: Define the **`yf preflight <skill> --json` contract** — a superset status schema
  matching today's outputs (`ok | ignored | system_deps_missing | bd_not_initialized |
  rule_missing | rule_drift | rule_deprecated | manifest_*`) plus `scaffold_added`,
  `instructions`. **entry**
- Issue 2.2: Per-skill preflight descriptor — extend SKILL.md frontmatter (or a sidecar) with the
  data the kernel needs (companion-rule name, min-bd-version, config-file basename); embedded and
  read by `yf`. depends-on: 2.1
- Issue 2.3: Kernel checks in Rust — tool detection, bd-version gate, **rule-hash/semver
  verification against embedded `manifest.json`**, `.<skill>.local.json` read (incl.
  `ignore-skill`), `.yf/<skill>/` state cache, gitignore-anchor scaffold. depends-on: 2.2
- Issue 2.4: Port `beads-init` **verify** to Rust — including the `bd status --json` *parse-for-
  `error`-key-not-exit-code* invariant and wedged-migration classification. depends-on: 2.3
- Issue 2.5: Port `beads-init` **repair** (`bd dolt stop → migrate schema → migrate`; idempotent
  gitignore/hooks/perms/JSONL hardening; local-only assertion). De-risk: if the Rust port slips,
  `yf` may shell to the existing embedded Python repair as a bounded fallback (risk R5).
  depends-on: 2.4
- Issue 2.6: Rewire each skill's `SKILL.md` preflight step to call `yf preflight <skill>`
  instead of `uv run …check`; remove/retire the moved Python (`plan_manager.py check`,
  `research_manager.py check`, `beads_init.py` verify/repair) leaving domain subcommands intact.
  depends-on: 2.3, 2.4, 2.5
- Issue 2.7: **Idempotent legacy-state migration** — `yf` reads any legacy `.state/<oldname>/`
  and `.<oldname>.local.json` once and migrates them to `.yf/<newname>/` and
  `.<newname>.local.json` (safe to re-run; no-op when already migrated). Covers the executing repo,
  not just downstream users. depends-on: 2.3
- **Capability Gate G2** (backed by Epic 6): `yf preflight yf-plan --json` reproduces the legacy
  `check` status schema across **all three** states.

### Epic 3: Systematic rename to `yf-` prefix
Largely independent of the binary; must land before Epic 1/2 final integration.
- Issue 3.1: Rename the **11 non-driving** skill directories + `SKILL.md` `name:` fields to
  `yf-<name>`. The two special-cases (`bdplan → yf-plan`, `bdresearch → yf-research`) are
  **deferred to Issue 3.7** (INV-1 self-rename isolation); other skills may forward-reference the
  `yf-plan`/`yf-research` names as text in 3.2/3.4 before 3.7 lands the dirs. **entry**
- Issue 3.2: Update intra-SKILL.md couplings — `SKILL_DIR` `find … -name <skill>` globs (13),
  `depends-on-skill` chains (7 edges: bdplan, bdresearch, beads-init, beads-upstream,
  beads-authoring, and incubator → beads-extra/-authoring; optimal-instructions → skill-authoring),
  cross-skill backtick refs + trigger text (~26), command examples (`/bdplan → /yf-plan`).
  depends-on: 3.1
- Issue 3.3: Python rename coupling — `SKILL_NAME` constants (plan_manager.py, research_manager.py)
  and derived `CONFIG_FILE` (`.yf-plan.local.json`) + `STATE_DIR` (**`.yf/yf-plan/`**);
  formula filenames + `.beads/formulas/*` references. depends-on: 3.1
- Issue 3.4: Companion-rule content — command examples and cross-skill names inside `PLANS.md`,
  `RESEARCH.md`, `BEADS_INIT.md`, `UPSTREAM_TRACKING.md`, `INSTRUCTIONS.md`,
  `DRIFT-CHECK-TRIGGER.md`, `MARKDOWN_LINT.md`; **refresh every `manifest.json` sha256+version**
  after edits (`manifest_update.py`). (Rule *filenames* stay domain-named, e.g. `PLANS.md`.)
  depends-on: 3.2
- Issue 3.5: Repo-internal references — `AGENTS.md`, `DRIFT-CHECK.md` manifest globs,
  `docs/diagrams/skill-ecosystem.d2` node ids (+ re-render PNG), README skill names.
  depends-on: 3.2
- Issue 3.6: `.gitignore` anchors (`/.yf/`, `/.yf-plan.local.json`, …) and a one-time
  **migration note** (old skill dirs, old `.state/`/`.bdplan.local.json`, user `CLAUDE.md`
  references to `/bdplan`,`/bdresearch`). depends-on: 3.3
- Issue 3.8: **Per-skill SPECs — finalize.** The 13 per-skill `SPEC.md` drafts are primed
  pre-intake; this issue moves each with its renamed dir, refreshes content to the final `yf-<skill>`
  surface, reconciles the macro `SPEC.md` §4 catalog paths, and wires the per-skill
  `SPEC.md ↔ SKILL.md` drift edge (folds into Issue 5.4). depends-on: 3.1
- Issue 3.7: **Self-renaming skills, performed LAST (INV-1).** Rename `bdplan → yf-plan` and
  `bdresearch → yf-research` (dirs, `SKILL.md name:`, `SKILL_DIR` globs, `SKILL_NAME`/`STATE_DIR`/
  config) only after all other plan-010 execution work is complete, inside the plan-009 merge-back
  worktree, landed at Phase 6. Keeps the driving orchestrator stable during execution.
  depends-on: 3.2, 3.3, 3.4, 3.5, 3.6

### Epic 4: Homebrew distribution + CI/release (cargo-dist)
Depends on Epic 1 (building binary).
- Issue 4.1: `cargo-dist` init — release matrix (`{darwin,linux}×{amd64,arm64}`), checksums,
  semver from git tags. **entry**
- Issue 4.2: Homebrew publish config — formula generated to `dixson3/homebrew-tap`,
  `depends_on "beads"` + `depends_on "uv"`, `test do … yf version`, `HOMEBREW_TAP_TOKEN`
  wiring. depends-on: 4.1
- Issue 4.3: CI workflow (`cargo fmt --check`, `clippy -D warnings`, `cargo test`) on PR; release
  workflow on `v*` tag. depends-on: 4.1
- Issue 4.4: README install path (`brew install dixson3/tap/yf && yf skills install`).
  depends-on: 4.2
- **Capability Gate G3 (human)**: `HOMEBREW_TAP_TOKEN` secret present on the repo; cargo-dist
  release **dry-run** renders a valid formula with both `depends_on`s. Blocks any real tag.

### Epic 6: `yf` crate verification (backs G1/G2)
Co-developed with the relevant Epic 1/2 issues. The sealed SPEC (pre-intake) exists before these
beads are poured, so each test **names the `REQ-…` it verifies**. (Honest scope: this gives
forward REQ→test coverage, enforced by Issue 6.5 — it does not, and cannot, mechanically prove a
test asserts the requirement's *intent* rather than current behavior.)
- Issue 6.1: Unit tests for the install kernel — frontmatter parse + transitive `depends-on-skill`
  closure **parity vs `install.py`** (golden-file over the real `skills/` tree), group computation,
  cross-group/external logging; each test tagged with its `REQ-…`. depends-on: 1.3 **entry**
- Issue 6.5: A `SPEC.md` **coverage check** — assert every `REQ-…` marked testable maps to at least
  one integration/system test (a simple grep/registry test that fails on an unmapped requirement).
  depends-on: 6.1, 6.2, 6.3
- Issue 6.2: Tree-hash determinism + marker inject/strip/verify + stale-file prune correctness.
  depends-on: 1.4, 1.6
- Issue 6.3: Preflight tests — the `bd status --json` error-key classifier (incl. wedged-migration
  case), and **three-state fixtures** (ok / system_deps_missing via missing-tool / rule_drift via
  tampered-rule) asserting the exact legacy status strings. depends-on: 2.3, 2.4
- Issue 6.4: CI runs `cargo test` (meaningful suite from 6.1–6.3), `cargo fmt --check`,
  `clippy -D warnings`. depends-on: 6.1, 6.2, 6.3 (consolidates with Issue 4.3)

### Epic 7: User-facing documentation site (Docusaurus, in-monorepo)
Poured after the spec is sealed; content depends (via real edges below) on Epics 1 + 3 being final.
- Issue 7.1: Scaffold **Docusaurus** in the monorepo under `website/` (Node/npm project, base
  config: title "Yoshiko Flow", `url`/`baseUrl` provisioned for `yoshiko-flow.github.io`,
  `.gitignore` for `node_modules`/`build`). **entry**
- Issue 7.2: Author user-facing pages — landing/overview, **install** (`brew install
  dixson3/tap/yf` → `yf skills install` → `yf doctor`), `yf` command reference (skills
  lifecycle, doctor, preflight), the **`yf-*` skill catalog** (one entry per skill), the
  preflight/config model, and a **migration guide** (old `bdplan`/`bdresearch` → `yf-plan`/
  `yf-research`, legacy state/config). Content references SPEC requirements where relevant.
  depends-on: 7.1, **1.7** (commands final), **3.5** (skill catalog / repo-internal names final)
- Issue 7.3: GitHub Pages deploy workflow — a GitHub Actions job that builds Docusaurus and
  publishes to **`yoshiko-flow.github.io`**. Scaffold a **disabled** workflow + a `CNAME`/`baseUrl`
  placeholder; **enabling it is blocked by Gate G4** (operator confirms target repo/branch/domain —
  D5). depends-on: 7.2

### Epic 5: Decommission `install.{sh,py}` + repo refactor + land
Depends on Epics 1–4, Epic 6, Epic 7, and Gate G1.
- Issue 5.1: Remove `install.sh`, `install.py`; excise their references from README/AGENTS/docs.
  depends-on: G1, 4.4
- Issue 5.2: Final docs pass — README operational model (brew → `yf skills install` →
  `yf doctor`), AGENTS.md update. depends-on: 5.1
- Issue 5.4: Make the specs enforceable — add `DRIFT-CHECK.md` manifest edges
  **`SPEC.md` ↔ `GUARDRAILS.md` ↔ `README.md`** (macro) and **per-skill `SPEC.md` ↔ `SKILL.md`** so
  a guardrail/spec/doc/skill disagreement is caught by the existing drift-check engine (turns the
  specs + GUARDRAILS from inert prose into verified constraints). depends-on: 5.2, 3.8
- Issue 5.3: Land-the-plane — run Issue 2.7 legacy-state migration on this repo (checklist item);
  **re-read GUARDRAILS.md against the shipped surface** (sign-off checklist item); file the coarse
  upstream tracking issue (plan-010); **close #14**; **comment-and-leave-open #15** noting the
  residual Python-helper scope. depends-on: 5.2, 5.4

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Pre-intake Gate G0: SPEC + GUARDRAILS sign-off (gates INTAKE, not execution) — ✅ SEALED 2026-06-14
- Type: human, **resolved during PLAN before INTAKE** (like plan approval; not an EXECUTE-phase
  capability gate — bdplan has no EXECUTE→PLAN transition, so a spec that can reshape epics is
  sealed before any bead is poured).
- Approvers: operator
- Condition: `SPEC.md` and `GUARDRAILS.md` exist at repo root, are complete (numbered `REQ-…`
  requirements + function contracts; counterfactual guardrails), and the operator has reviewed and
  approved both.
- Test: `test -f SPEC.md && test -f GUARDRAILS.md && grep -qE '^REQ-' SPEC.md` (existence +
  shape); the substantive approval is the operator's manual review.
- Gates: the **INTAKE step** — no Epic 1–7 beads are poured until G0 is signed off.
- On change: if review reshapes SPEC/GUARDRAILS, the epics are edited **in PLAN** (native, since
  they are not yet intaked) and the conformance + portability audit re-run, then INTAKE proceeds.
  No in-place EXECUTE→PLAN amend, no "RECONCILE" overload.

### Capability Gate G1: yf installs skills
- Type: human
- Approvers: operator
- Condition: a freshly built `yf` installs the (renamed) skill tree + companion rules to a
  scratch `--target`, `yf skills status` reports up-to-date, and the Epic 6.1 closure-parity
  suite is green.
- Test: `cargo test -p yf && cargo build --release && ./target/release/yf skills install --target /tmp/yf-skills --dry-run && ./target/release/yf skills install --target /tmp/yf-skills && ./target/release/yf skills status --target /tmp/yf-skills`
- Blocks: Epic 5 (decommission install.py)
- Depends on: Epic 6.1, 6.2
- Instructions: build the crate, run the round-trip against a temp dir.

### Capability Gate G2: preflight parity
- Type: human
- Approvers: operator
- Condition: `yf preflight yf-plan --json` reproduces the legacy `plan_manager.py check` status
  schema across **all three** states — ok, system_deps_missing, rule_drift — proven by the Epic 6.3
  fixtures, not a single happy-path run.
- Test: `cargo test -p yf preflight_parity` (the 6.3 three-state suite asserting exact legacy
  status strings) **and** a smoke check `./target/release/yf preflight yf-plan --json | jq -e '.status'`
- Blocks: Issue 2.6 (rewiring SKILL.md preflight)
- Depends on: Epic 6.3

### Capability Gate G3: release dry-run + tap token
- Type: human
- Approvers: operator
- Condition: `HOMEBREW_TAP_TOKEN` secret exists on `dixson3/yoshiko-flow`; `cargo dist` plan/
  build dry-run produces a formula carrying `depends_on "beads"` and `depends_on "uv"`.
- Test: `cargo dist plan` (and inspect generated formula); confirm secret in repo settings.
- Blocks: cutting the first real `v*` tag (Issue 4.2 completion)
- Instructions: add the token secret; run the dry-run; eyeball the formula.

### Capability Gate G4: docs-deploy enablement (D5)
- Type: human
- Approvers: operator
- Condition: the operator confirms the docs-deploy strategy — target (org-site repo vs. project
  pages), branch, and custom domain — and the scaffolded workflow's `baseUrl`/`CNAME` are resolved
  to that decision (no placeholders).
- Test: `grep -q 'yoshiko-flow.github.io' website/docusaurus.config.* && ! grep -RnE 'PLACEHOLDER|TODO' website/.github 2>/dev/null` (workflow references a resolved target, no placeholder left).
- Blocks: **enabling** the deploy workflow (Issue 7.3 ships it disabled until this gate).
- Instructions: decide the hosting model, fill the config, then enable the workflow.

## Risks & Mitigations

- **R1 — cargo-dist Homebrew `depends_on` support.** goreleaser's `brews:` block makes
  `depends_on` trivial; cargo-dist's formula generation may need explicit config or a
  post-generation patch. *Mitigation:* prove it in Gate G3 dry-run before any tag; fall back to a
  formula-patch step in the release workflow if cargo-dist can't inject both deps natively.
- **R2 — Bootstrapping circularity.** Skills' preflight now needs `yf`; but `yf` is what
  installs the skills, so it is always present post-install. Domain scripts still need `uv`
  (formula `depends_on "uv"`). No real cycle. *Mitigation:* `yf doctor` asserts the toolchain.
- **R3 — Config/state orphaning.** Renaming `.bdplan.local.json → .yf-plan.local.json` and
  `.state/ → .yf/` orphans existing operator config (this repo included). *Mitigation:* a
  **defined** idempotent migration (Issue 2.7) — `yf` reads the legacy path once and migrates —
  run on this repo at land (Issue 5.3), plus the migration note (Issue 3.6).
- **R4 — Dual integrity model drift.** Tree-marker and per-rule manifest are separate axes; a
  rename that edits rule content without refreshing `manifest.json` yields false `rule_drift`.
  *Mitigation:* Issue 3.4 mandates `manifest_update.py` refresh; Gate G2 catches regressions.
- **R5 — beads-init repair port cost.** The repair engine is the most stateful port.
  *Mitigation:* stage it (Issue 2.5) with a Python-shell fallback if the Rust port slips, without
  blocking the rest of Epic 2.
- **R6 — Out-of-repo references.** Installed global rules and the user's `CLAUDE.md` name
  `bdplan`/`bdresearch`. *Mitigation:* migration note + `yf skills install` reinstalls renamed
  rules; CLAUDE.md edit is a manual, operator-owned step (flagged, not auto-edited).
- **R7 — Self-rename of the driving orchestrator.** Renaming `bdplan → yf-plan` in the canonical
  tree while `/bdplan execute` drives plan-010 would diverge the running orchestrator from its
  source (hardcoded `SKILL_DIR` resolver + `.state/bdplan/`). *Mitigation:* INV-1 — driving session
  runs from the installed `~/.claude/skills/bdplan` copy; Issue 3.7 defers the two self-renames to
  the final step in the merge-back worktree, landed at Phase 6; the operator's own environment
  migrates via a post-land `yf skills install`.
- **R8 — Binary-name collision (resolved → `yf`).** The original `yflow` name collided with an
  active same-domain PyPI `yflow` CLI (exp-002), so the binary is **`yf`** (exp-003): clear on
  Homebrew, shell builtin/alias/binary, crates.io, RubyGems, and Go; the only namesake is an
  abandoned finance-adjacent `yf` (irrelevant). *Residual:* `yf` is a short token a user could
  alias personally (unavoidable for any 2-letter name) and the npm/PyPI `yf` slugs are taken (no
  bin) — neither blocks a Homebrew-distributed binary. Re-check at submission time.
- **R9 — SPEC/GUARDRAILS churn reworking epics.** Spec review may change scope after the epics are
  drafted. *Mitigation:* SPEC/GUARDRAILS are sealed **pre-intake** (Gate G0). Any reshaping edits
  the epics **in PLAN** — where epic editing is native and the conformance/portability audits exist
  — *before* the beads are poured. No mid-execution epic surgery, no EXECUTE→PLAN loop.

## Success Criteria

1. All 13 skills are renamed to `yf-*` (with `yf-plan`/`yf-research` specials); `/yf-plan` and
   `/yf-research` invoke correctly; no stale `bdplan`/`bdresearch` references remain in canonical
   sources (drift-check clean).
2. `brew install dixson3/tap/yf` installs `yf` and transitively `beads` + `uv`;
   `yf skills install` deploys the renamed skills + companion rules; `yf doctor` is green.
3. `yf skills upgrade` prunes stale files and updates the tree-hash marker; `yf skills
   status` distinguishes installed/up-to-date/complete/unmodified.
4. Each skill's preflight runs via `yf preflight <skill>` with status parity to the retired
   Python `check`/`verify`; the duplicated tool/bd/rule-hash logic exists once, in `yf`.
5. `install.sh`/`install.py` are removed; README documents the brew-based operational model.
6. A tagged `v*` release builds the binary matrix and updates `dixson3/homebrew-tap` automatically
   via cargo-dist; the formula declares `depends_on "beads"` and `depends_on "uv"`.
7. `cargo test -p yf` runs a meaningful suite (closure parity vs `install.py` golden file,
   tree-hash determinism + prune, marker inject/strip/verify, `bd status` error-key classifier,
   preflight three-state fixtures) and is green in CI.
8. The macro `SPEC.md` + `GUARDRAILS.md` exist at repo root, were operator-approved pre-intake
   (Gate G0), and the macro spec composes a per-skill `skills/<skill>/SPEC.md` for every skill;
   every testable `REQ-…` maps to ≥1 integration/system test (Issue 6.5 forward-coverage check is
   green); and the specs are enforceable, not inert — the `DRIFT-CHECK.md` SPEC↔GUARDRAILS↔README
   and per-skill SPEC↔SKILL.md edges (Issue 5.4) are wired and clean.
9. A Docusaurus site builds from `website/` (install, command reference, `yf-*` skill catalog,
   migration guide); the deploy workflow ships disabled and is enabled only after Gate G4 resolves
   the `yoshiko-flow.github.io` hosting strategy.
