---
type: Plan
okf_spec: OKF-PLAN
id: plan-033-james-dixson-46aca2
author: james-dixson
created: '2026-07-22'
status: approved
deliverable_class: standard
fingerprint: b7e5727c53e7a9eb34ffd2d54d3b057cde9989427478f2e2d6e65d0ace837a42
---
# Plan: yf multi-harness provisioning — harness skills install (--harness) + harness tune (config + rule deployment) + --tune bridge + --revert

**ID:** plan-033-james-dixson-46aca2
**Author:** james-dixson
**Created:** 2026-07-22
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** b7e5727c53e7a9eb34ffd2d54d3b057cde9989427478f2e2d6e65d0ace837a42

## Objective
Turn `yf` into a **multi-harness provisioning actor** across three surfaces — skills install,
config tuning, and always-loaded rule deployment — for **claude-code, codex, opencode, and pi**
(with Pi *config* deferred). This supersedes the plan-032 Claude-Code-only, JSON-only base and the
narrower "extend tune to codex/opencode" framing. Six capabilities, each grounded in
`findings/exp-001-architecture-seam.md`, `findings/exp-002-naba-harness-model.md`, and
`docs/research/002-harness-global-rule-minimization/Summary.md`:

1. **`yf harness skills install|upgrade|remove|status` (skills-only).** **All four** skills
   sub-verbs now live under `yf harness`: the canonical group is `yf harness skills
   install|upgrade|remove|status` (sub-verbs matching the existing `yf skills` style), with `install`
   taking `[--tune] [--harness <name>...] [--scope ...]` (no `--revert` — revert is a
   `yf harness tune` flag only). The **entire top-level `yf skills` group** is retained as a
   **deprecated alias** → `yf harness skills <verb>`, verb-for-verb (kept until the next major release
   of `yf`). Replace `--surface {claude,agents}` with `--harness {claude-code,codex,opencode,pi,agents}`
   on a **naba-style descriptor table** (`exp-002`); `install` deploys **skill bodies only** (no rules).
   `--surface` stays a **deprecated alias** (`claude`→`claude-code`, `agents`→`agents`, passthrough +
   legacy `.<id>/skills` fallback). `--harness` is repeatable and **deduped by resolved absolute
   path** (codex and agents both resolve to `.agents/skills`). Per-harness skills paths and pi's
   `lowercase-hyphen,max64` name transform come from the `exp-002` table; a **SPEC↔code parity test**
   guards the descriptor.

2. **`yf harness tune` owns TWO sub-operations** (`exp-001`, `exp-002`, research-002):
   **(a) config alignment** (the existing kind-aware engine) for **claude-code, codex, opencode**
   — codex via a **new TOML delta-replay engine**, opencode via the reused JSON engine, `merge.rs`
   byte-for-byte unchanged; **Pi config deferred** (`[uncertain]` per research-002 Q6);
   **(b) rule optimization + deployment** — the aggregation of acted-on skills' `protocols/*.md`,
   its **minimization** to the irreducible-core (research-002 verdict table), and **per-harness
   global placement** as a marker-delimited managed block.

3. **The YOSHIKO_FLOW.md aggregation MOVES out of `yf harness skills install` into `yf harness tune`.**
   `install` becomes skills-only; the existing install-time aggregation
   (`common.rs::install_rules_aggregate`, `REQ-YF-FLOW-001..006`) is invoked by `tune` instead,
   with backward-compat for existing installs that already wrote `YOSHIKO_FLOW.md`.

4. **`--tune` opt-in bridge + harness auto-detection.** `--tune` (REQ-YF-TUNE-010) stays opt-in —
   install and tune remain **separable** (a skills-only install is a legitimate case). NEW:
   **auto-detection** — with no `--harness`, detect installed harnesses (user scope by home-dir /
   `PATH` binary probe; project scope by dot-dir presence) and act on all detected; explicit
   `--harness` overrides. First-run provisioning = `yf harness skills install --tune` (the
   `yf skills install --tune` alias still works during deprecation). The `--tune` bridge also runs
   `yf harness tune`.

5. **`--revert`** on tune — a sidecar `.yf/` ownership manifest (gitignored in project scope)
   recording yf-written config keys (prior + yf-written value) and rule managed-block markers;
   revert removes only yf's additions under a **touched-since-tune guard**.

6. **Code-accurate `web/` docs + diagrams + a doc↔code agreement test** — publish the install
   matrix (harness × scope → skills dir) and the tune matrix (harness × scope → {config file, rule
   target}) with Pi config = deferred, and a test (reusing the `harness/drift.rs` pattern) that
   derives real destinations from the descriptor table / `dest.rs` / profiles and **fails on
   divergence**.

**Pi is split.** Pi gets **skills install AND rule deployment now** (skills path + rule target are
first-party or operator-decided), but Pi **config tuning is deferred**: research-002 Q6 marks Pi's
config surface `[uncertain]` (questionable-tier sources only), and profiles are rust-embedded, so
shipping a guessed `pi` config profile would commit a guess into a released binary (correctable only
by a point release, not a config edit). `REQ-YF-TUNE-017` documents the config deferral; a follow-on
bead tracks Pi config re-verification.

## Motivation
`yf harness tune` (plan-032, #95) made `yf` the actor that aligns a harness to the yf skill
contracts — but only for Claude Code, only over `settings.json`, with no undo, and with rule
aggregation coupled into `skills install`. REQ-YF-TUNE-011 explicitly deferred concrete non-Claude
support "gated on the yf-2gyv research," and the plan-032 red-team deferred both multi-harness
engines (pass-1 #5) and a reversal path (pass-1 #7/#12). Two inputs now reshape the target beyond a
simple engine extension: **research-002** finds that non-Claude config surfaces are
enforcement/visibility-only while **always-loaded AGENTS.md prose** is the real cross-harness
substrate — so provisioning must deploy *rules*, not just config; and **naba** (`exp-002`) has
already shipped the `--surface`→`--harness` descriptor-table refactor and demonstrates the clean
skills-vs-config-vs-rules boundary yf should adopt. Operators running yf skills under
codex/opencode/pi today have no supported way to install skills idiomatically per harness, to align
each harness's config or rules, or to reverse a tune. This plan makes `yf` a first-class
multi-harness provisioner — one command topology under `yf harness` (`harness skills install`
skills-only, with `yf skills install` a deprecated alias; `harness tune` config+rules; `--tune`
bridge; `--revert`) with auto-detection — closing beads **yf-8agh**
(multi-harness) and **yf-up7s** (`--revert`), and reconciling the local web beads **yf-8ayq** and
**yf-ij06**. Pi config lands as a documented deferral with a filed follow-on.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| #95 | plan-032 execution tracking: yf harness tune (settings alignment) | related | Predecessor. plan-033 is the follow-on; files its own coarse tracking issue at intake, referencing #95. | — |

## Investigation Findings

**`findings/exp-001-architecture-seam.md`** (inline investigation of `yf/src/cmd/harness/*` +
SPEC §3.10):
- The kind-aware merge engine (`merge.rs`) is **pure over `serde_json::Value`** and reusable as-is
  if TOML is bridged to `Value` for the merge *decision* — the engine need not change; only a
  per-format read/write adapter is new. TOML must be written via **delta-replay** (the `Value`
  cannot round-trip TOML datetimes/int-vs-float or trivia).
- `profile.rs` embeds profiles from a **separate** rust-embed root (`yf/profiles/`, distinct from
  `../skills`); `settings.rs` scope/path resolution is JSON-hardwired and per-harness paths differ
  (codex `~/.codex/`, opencode `~/.config/opencode/`, pi `~/.pi/agent/`).
- REQ-YF-TUNE-011 **pre-declares** this exact seam ("a future harness … needs a new engine, not
  merely a new profile"), so the engine work extends an anticipated point, not a retrofit.
- JSON/TOML key-value formats carry **no yf-ownership signal**, so `--revert` needs a **sidecar
  ownership manifest**; AGENTS.md rule deployment is a **distinct capability**, delimited by a
  managed marker block, not a settings profile.

**`findings/exp-002-naba-harness-model.md`** (read-only study of naba's `--harness` model):
- naba already did the `--surface`→`--harness` refactor: a **harness-as-data descriptor table**
  (`src/harness.rs`), `surface_alias()` deprecation mapping + legacy `.<id>/skills` fallback,
  **repeatable `--harness` deduped by resolved path**, and a **SPEC↔code parity test** — all
  directly transferable to yf's skills-install half. Per-harness skills paths: claude-code
  `.claude/skills`; opencode `.config/opencode/skills` (user) / `.opencode/skills` (project); pi
  `.pi/agent/skills` (user) / `.pi/skills` (project, `lowercase-hyphen,max64`); codex + agents both
  `.agents/skills` (hence dedupe is mandatory).
- **Net-new for yf** (no naba precedent): (1) a **rules/instructions axis** — yf already aggregates
  `YOSHIKO_FLOW.md` at install (`common.rs::install_rules_aggregate`, `REQ-YF-FLOW-001..006`);
  naba deploys skills only. (2) **config tuning** — no naba analogue; naba's clean boundary
  (install writes only skill files, never config) is the principle to preserve — keep `tune` a
  distinct opt-in step. (3) **auto-detection** — designed fresh here.
- **Operator directives carried from `exp-002`:** rule optimization/placement **moves into
  `yf harness tune`** (protocols → aggregate → minimized per-harness rules); config tuning =
  claude-code + codex + opencode with **Pi config deferred**, but **Pi IS supported for skills +
  rules**; `--tune` stays opt-in (separable) with auto-detect making first-run easy.

**`docs/research/002-harness-global-rule-minimization/Summary.md`** (the minimization source of
truth): per-harness always-loaded surfaces are AGENTS.md (codex `~/.codex/AGENTS.md`, opencode
`~/.config/opencode/AGENTS.md`, pi `~/.pi/agent/AGENTS.md` or `APPEND_SYSTEM.md` `[uncertain]`),
while claude-code reads `CLAUDE.md`/`.claude/rules`, **not** AGENTS.md. The **irreducible-core**
(rules a `description` cannot carry) = PLANS/RESEARCH native-override, the two bd mandates,
UPSTREAM close-time push, and the deterministic must-fire invariants; the **on-edit engine rules
stay prose** cross-harness ("0 sources attest" a `paths`/hook analog outside Claude Code). Config
is universally an enforcement/visibility lever, never a trigger supplier. **Pi config surface is
`[uncertain]`** (questionable-tier only) — the basis for the Pi config deferral.

## Approach

Rebuild the harness surface into a **three-way command topology** grounded in `exp-001`
(the config-engine seam), `exp-002` (naba's `--harness` descriptor model + the clean skills /
config / rules boundary), and research-002 (the per-harness rule-placement + minimization verdict):

- **`yf harness skills install|upgrade|remove|status`** — the four skills sub-verbs, skills-only,
  `--harness`-driven (5-row descriptor table), auto-detecting, with `--tune` a flag on the `install`
  sub-verb. The **entire top-level `yf skills` group** is retained as a **deprecated alias** →
  `yf harness skills <verb>`, verb-for-verb (kept until the next major release, mirroring the
  `--surface`→`--harness` alias treatment) — so **all** harness ops now live under `yf harness`.
- **`yf harness tune`** — the config+rules actor: **(a)** config alignment over the reused
  kind-aware engine (JSON for opencode, a new TOML delta-replay adapter for codex; `merge.rs`
  untouched) and **(b)** rule optimization + minimized-managed-block deployment; the
  `YOSHIKO_FLOW.md` aggregation **moves here from install**.
- **`--revert`** — a sidecar `.yf/` ownership manifest reverses config keys and rule blocks under a
  touched-since-tune guard.

![Multi-harness provisioning topology](diagrams/architecture.png)

**SPEC-first (project AGENTS.md mandate).** SPEC changes land **first**, as **Epic 1**, before any
implementation: `REQ-YF-CLI-002` (revised for both the `--harness` refactor **and** the relocation of
**all four** skills sub-verbs under `yf harness skills install|upgrade|remove|status`, with the whole
top-level `yf skills` group a deprecated alias), plus **`REQ-YF-CLI-001`** (top-level `skills` now a
deprecated alias group; `yf harness skills` canonical) and **`REQ-YF-TUNE-002`** (the `harness` group
gains a `skills` subcommand alongside `tune`); `REQ-YF-INSTALL-002` revised;
`REQ-YF-INSTALL-007..009` (descriptor table + parity, skills-only install, auto-detection);
`REQ-YF-FLOW-001..006` revised + `REQ-YF-FLOW-007` (aggregation moves install→tune, with
backward-compat); `REQ-YF-TUNE-012..025`; `REQ-YF-TUNE-011` revised to record the follow-on
delivered; and the living-amendment-log entry (plan-033). The per-harness `yf doctor`/drift axis
(the 008/009 analogs) is **explicitly deferred** with a filed follow-on. Every later epic writes
code **plus a tagged test against a REQ id landed in Epic 1**; the dependency wiring (Epics 2–10 all
depend on Epic 1) enforces the ordering mechanically, and the SPEC is the coverage gate's source of
truth.

Design pillars, each grounded in a finding:

1. **Skills-install `--harness` refactor, skills-only (Epic 2).** Replace `Surface` with a
   naba-style **harness descriptor table** (`exp-002`): claude-code, codex, opencode, pi, agents —
   each a data row with `user_subpath` / `project_subpath` / optional `name_transform`. `--surface`
   becomes a **deprecated alias** (`surface_alias()`: `claude`→`claude-code`, `agents`→`agents`,
   passthrough + legacy `.<id>/skills` fallback). `--harness` is repeatable and **deduped by
   resolved absolute path** (codex and agents both → `.agents/skills`). Pi's `lowercase-hyphen,
   max64` transform is **validated against yf's long skill names** (`yf-change-validation`, …). A
   **SPEC↔code parity test** (naba `harness.rs:154-223` pattern) parses the SPEC table and asserts
   it equals the shipped descriptor. **Install deploys skill bodies only** — no rules
   (`REQ-YF-INSTALL-008`). **Auto-detection** (`REQ-YF-INSTALL-009`, net-new — no naba precedent):
   with no `--harness`, probe each harness's home dir / `PATH` binary (user scope) or dot-dir
   presence (project scope) and act on all detected; explicit `--harness` overrides.

2. **The FLOW aggregation moves install→tune (Epic 3).** naba's clean boundary (`exp-002`) — install
   writes only skill files — is adopted: the existing `common.rs::install_rules_aggregate`
   (`REQ-YF-FLOW-001..006`) is **no longer invoked by `install`** and is invoked by `tune` instead
   (`REQ-YF-FLOW-007`). The aggregation *mechanics* are unchanged (byte-stable serialization,
   reconcile-prune, `sha256` sections); only the **invocation site** relocates. **Backward-compat:**
   an existing install that already wrote `YOSHIKO_FLOW.md` is left untouched by the now-skills-only
   install; `tune` adopts/reconciles that file on first run (no orphaned or double-written aggregate).

3. **Format-aware config engine, merge untouched (Epic 4).** Introduce `SettingsFormat`
   (`Json | Toml`) carried on the `Profile`. The merge stays `serde_json::Value`-based and
   byte-for-byte unchanged (`exp-001`); the TOML bridge is a **delta-replay** adapter: parse
   `config.toml` into a `toml_edit::DocumentMut` (retains comments/trivia/key-order) **and
   separately** derive a `serde_json::Value` for the merge **decision only**; run the unchanged
   `merge()` for a `MergeReport`; **replay only the report's deltas
   (`ScalarAdded`/`ScalarForced`/`SetUnioned`, keyed by dot-path) onto the `DocumentMut`** and
   serialize *that document* — never the `Value` (it cannot round-trip TOML datetimes / int-vs-float
   / trivia). opencode (JSON) reuses the existing path unchanged. `settings.rs` scope/path resolution
   is generalized off the profile (`surface_dir` / filenames) instead of Claude-hardwired.

4. **Per-harness config profiles (Epic 5).** Data-only per `exp-001`. Codex is the first TOML
   consumer (`~/.codex/config.toml`); opencode reuses JSON (`~/.config/opencode/opencode.json`).
   **Pi config is deferred** (`REQ-YF-TUNE-017`): research-002 Q6 marks its config surface
   `[uncertain]`, and rust-embedded profiles would commit a guess into a released binary — a
   follow-on bead tracks Pi config re-verification. (Pi still gets skills + rules — Epics 2, 6.)

5. **Rule optimization + minimized deployment (Epic 6).** research-002's actual recommendation: the
   load-bearing cross-harness surface is **always-loaded prose**. `tune` deploys the **minimized
   irreducible-core** bundle — the rules a `description` cannot carry (PLANS/RESEARCH native-override,
   the two bd mandates, UPSTREAM close-time push, the deterministic must-fire invariants); the
   **on-edit engine rules stay prose** ("0 sources attest" a `paths`/hook analog outside Claude
   Code). **Provenance is forward-looking and re-runnable:** the source of truth is the skills'
   `protocols/*.md` sections (from which `YOSHIKO_FLOW.md` is itself aggregated), passed through a
   **minimization classifier** that keeps only the irreducible rules; a **new** skill's new
   `protocols/` rule automatically enters the same analysis. **Implementer note:** the "classifier"
   is a *curated selection guarded by an agreement test*, not an autonomous irreducibility oracle —
   the irreducible-vs-reducible call is the curatorial judgment research-002 performed manually; the
   **bundle↔source agreement assertion** catches *content drift* of the selected rules and fails
   loudly when a new `protocols/` rule is unclassified. The bundle lands as a **marker-delimited
   managed block** (`BEGIN/END` sentinels) into each harness's **global-rule target** — claude-code
   `~/.claude/rules/`, codex `~/.codex/AGENTS.md`, opencode `~/.config/opencode/AGENTS.md`. **Pi's
   rule target is NOT a compiled-in guess:** it is resolved to **one** concrete choice
   (`~/.pi/agent/AGENTS.md` **xor** `APPEND_SYSTEM.md`) by the Issue 1.5 investigation against a
   first-party Pi source and gated by the "Pi rule target verified" capability gate; if no first-party
   evidence surfaces, Pi rules ship **only** behind an explicit `--pi-rule-target` opt-in with a loud
   "unverified target" notice (never a silent default). Pi **does** get rule deployment (Epic 6.3),
   but only against a verified-or-opted-in target. Deployment is **non-clobbering** of user prose
   (append if absent, replace only between markers, fail-safe on ambiguity).

6. **`--tune` bridge + auto-detection orchestration (Epic 7).** `tune` ties its two sub-operations
   together per harness (config alignment where supported + rule deployment) and reuses the Epic 2
   detection module. `--tune` stays **opt-in** (`REQ-YF-TUNE-023`) — a skills-only install that
   never touches config/rules is a legitimate, recorded case. The bridge is canonically
   `yf harness skills install --tune` (the `yf skills install --tune` alias still works during
   deprecation). First-run provisioning = `yf harness skills install --tune` with no `--harness`:
   detect + install skills + tune config (where supported) + deploy rules, for every detected harness.

7. **Ownership manifest + `--revert` (Epic 8).** JSON/TOML formats carry no yf-ownership signal
   (`exp-001`), so a **sidecar `.yf/` manifest** records the config dot-paths yf wrote (with their
   **prior** *and* **yf-written** values), the set elements yf **unioned in**, and the rule
   managed-block markers — per file/scope. In project scope `.yf/` is **gitignored**. `--revert`
   removes **only yf's additions** under a **touched-since-tune guard**: if a key's current on-disk
   value differs from the recorded yf-written value (operator hand-edited since the tune), it is
   **conservative-kept and reported**, not clobbered. Idempotent; `Agent`-never-denied structurally
   preserved. Closes **yf-up7s**.

8. **Code-accurate web docs, guarded by an agreement test (Epic 9).** The `web/` Pelican site
   publishes the **install matrix** (harness × scope → skills dir, from the descriptor table /
   `dest.rs` / `REQ-YF-INSTALL-002`) and the **tune matrix** (harness × scope → {config file, rule
   target}, with Pi config = deferred and Pi rules = the verified/opted-in target per Issue 1.5) plus
   the auto-detect behavior, with diagrams; a **doc↔code assert-agreement test** (reusing the `harness/drift.rs`
   `REQ-YF-TUNE-008` pattern) derives the real destinations from the descriptor table / `dest.rs` /
   profiles / target map and **fails on divergence**. Reconciles web beads **yf-8ayq** (recommended
   settings block) and **yf-ij06** (per-harness deployment targets).

**No reconcile gate/step.** The only upstream issue (#95) has disposition `related` (not a
non-exclude incorporation), and the web beads (yf-8ayq / yf-ij06) are **local**, not upstream
incorporations — so no reconcile gate is created and Phase-6 reconciliation is a no-op on that axis.
**One capability gate (Pi rule target).** The `toml` / `toml_edit` crates are ordinary Cargo
dependencies with no environmental prerequisite, so **no TOML-toolchain gate** is created. But Pi's
always-loaded rule target is a hidden-unknown (`~/.pi/agent/AGENTS.md` vs `APPEND_SYSTEM.md` are
semantically different and unverified), so a **capability gate — "Pi rule target verified"** — blocks
the Epic 6 Pi-rule-deployment issue (6.3) until the Issue 1.5 investigation resolves the target to a
single first-party-checked choice (or adopts the explicit `--pi-rule-target` opt-in fallback). No
compiled-in Pi-target guess ships. `d2` is present (0.7.1) — the topology diagram above is authored,
not degraded.

## Epics

### Epic 1: SPEC amendment (SPEC-first gate)
Land every new/revised requirement in `SPEC.md` **before** any code. This epic is the mechanical
enforcement of the SPEC-first mandate: Epics 2–10 depend on it. IDs are allocated contiguously from
the existing max (`REQ-YF-TUNE-011`) plus revisions to the CLI / install / FLOW requirements the
`--harness` refactor and the aggregation-move touch.

- Issue 1.1: **Skills sub-verb relocation + `--harness` refactor requirements.**
  Revise `REQ-YF-CLI-002`: (a) the canonical skills group is `yf harness skills
  install|upgrade|remove|status` (all four sub-verbs, matching the existing `yf skills` style), with
  `install` taking `[--tune] [--harness <name>...] [--scope ...]` (**no `--revert`** — revert is a
  `yf harness tune` flag only) — all harness ops (`skills`, `tune`) now live under
  `yf harness`; (b) the **entire top-level `yf skills` group** (`install`/`upgrade`/`remove`/`status`)
  is **deprecated** — each verb becomes a **deprecated alias** → `yf harness skills <verb>`,
  verb-for-verb, kept until the **next major release** of `yf` (mirroring the `--surface`→`--harness`
  alias treatment); (c) `harness skills` accepts repeatable
  `--harness {claude-code,codex,opencode,pi,agents}`; `--surface` retained as a **deprecated alias** —
  `claude`→`claude-code`, `agents`→`agents`, passthrough + legacy `.<id>/skills` fallback. **Also
  revise `REQ-YF-CLI-001`** (the top-level command enumeration): the top-level `skills` subcommand is
  now a **deprecated alias group**, and `yf harness skills` is the **canonical** home carrying
  `install|upgrade|remove|status`. **Also revise `REQ-YF-TUNE-002`** (the `yf harness` command group):
  the `harness` group gains a **`skills` subcommand** alongside the existing `tune` — the group is no
  longer `tune`-only. Revise `REQ-YF-INSTALL-002` (destination resolution generalized to a
  per-harness descriptor table; `--target` still wins; repeatable harnesses **deduped by resolved
  absolute path**). Add `REQ-YF-INSTALL-007` (**harness descriptor table** — 5 rows, single source
  of truth, with a **SPEC↔code parity test**; pi `lowercase-hyphen,max64` name transform validated
  against yf's long skill names), `REQ-YF-INSTALL-008` (**install deploys skill bodies only** — no
  rules; a bare install without `--tune` emits a skills-only warning and states rules were not
  deployed), and `REQ-YF-INSTALL-009` (**harness auto-detection** — no `--harness` ⇒ probe home
  dir/`PATH` binary for user scope, dot-dir presence for project scope; explicit `--harness`
  overrides; detection takes `PATH` as an injected parameter).
- Issue 1.2: **FLOW aggregation-move requirements.** Revise `REQ-YF-FLOW-001..006` so the aggregation
  engine's **invocation moves from `yf harness skills install` to `yf harness tune`** (mechanics unchanged).
  Add `REQ-YF-FLOW-007` (install no longer writes `YOSHIKO_FLOW.md`; `tune` owns the aggregate +
  minimization + placement; **backward-compat** — an existing install's `YOSHIKO_FLOW.md` is left
  untouched by the skills-only install and adopted/reconciled by `tune` on first run).
  - depends-on: 1.1
- Issue 1.3: **Config-engine + profile requirements.** Add `REQ-YF-TUNE-012` (`yf harness tune
  --harness <name>` owns **two sub-operations** — config alignment and rule optimization/deployment),
  `REQ-YF-TUNE-013` (format-aware engine `SettingsFormat` Json|Toml; `merge.rs` stays pure over
  `serde_json::Value`; TOML write path is **delta-replay** — parse to `toml_edit::DocumentMut`,
  derive a `Value` for the merge decision only, replay `MergeReport` deltas onto the document; the
  `Value` cannot round-trip TOML datetimes/int-vs-float/trivia), `REQ-YF-TUNE-014` (per-harness
  scope/path resolution generalized off the profile; `format` field on `Profile`), `REQ-YF-TUNE-015`
  (codex TOML profile / `config.toml`), `REQ-YF-TUNE-016` (opencode JSON profile / `opencode.json`),
  and `REQ-YF-TUNE-017` (**Pi config deferral** — Pi config surface is `[uncertain]` per research-002
  Q6 and rust-embedded profiles commit a guess into a released binary; Pi **skills + rules ship now**
  but Pi config is out of scope, tracked by a follow-on bead filed in Epic 10).
  - depends-on: 1.1
- Issue 1.4: **Rule-deployment + revert + docs requirements.** Add `REQ-YF-TUNE-018` (rule
  **minimization** — irreducible-core bundle **derived from the skills' `protocols/*.md` sources**
  via a minimization classifier, forward-looking/re-runnable as new skills add `protocols/` rules;
  **bundle↔source agreement assertion**; on-edit engine rules stay prose cross-harness),
  `REQ-YF-TUNE-019` (managed-block `BEGIN/END` markers + idempotent non-clobbering block merge),
  `REQ-YF-TUNE-020` (**per-harness global-rule target map** — claude-code `~/.claude/rules/`, codex
  `~/.codex/AGENTS.md`, opencode `~/.config/opencode/AGENTS.md`; **pi's rule target is NOT a
  compiled-in guess** — it is resolved to **one** concrete choice (`~/.pi/agent/AGENTS.md`
  **xor** `APPEND_SYSTEM.md`) by the Issue 1.5 investigation against a first-party Pi source and
  gated by the "Pi rule target verified" capability gate. **Fallback:** if the investigation finds
  **no first-party evidence**, Pi rules ship **only** behind an explicit
  `--pi-rule-target {agents-md|append-system}` opt-in with a **loud "unverified target" notice** —
  never a silent compiled-in default. Pi **does** get rule deployment, but only against a
  verified-or-explicitly-opted-in target), `REQ-YF-TUNE-021`
  (sidecar `.yf/` ownership manifest, gitignored in project scope; records prior + yf-written value
  for the revert guard, and rule block markers), `REQ-YF-TUNE-022` (`--revert` with a
  **touched-since-tune guard**), `REQ-YF-TUNE-023` (`--tune` **opt-in bridge** — install/tune stay
  separable — plus auto-detection first-run provisioning), `REQ-YF-TUNE-024` (**code-accurate `web/`
  docs** — the install matrix harness × scope → skills dir, and the tune matrix harness × scope →
  {config file, rule target}, with Pi config = deferred and Pi rules = the verified/opted-in target
  per Issue 1.5, plus the auto-detect behavior), and `REQ-YF-TUNE-025` (**doc↔code assert-agreement test** — the
  published matrices are checked against `dest.rs` / the descriptor table / the profiles / the
  target map and **fail** on divergence). Revise `REQ-YF-TUNE-011` to record the follow-on
  **delivered**; **explicitly defer** the per-harness `yf doctor`/`docs/recommended-settings.md`
  drift axis (008/009 analogs) with a filed follow-on bead. Add the living-amendment-log entry
  (plan-033).
  - depends-on: 1.1
- Issue 1.5: **INVESTIGATE Pi's real always-loaded rule target (resolves the AGENTS.md-vs-
  APPEND_SYSTEM.md fork to ONE SPEC choice).** Resolve Pi's real always-loaded rule target
  (`~/.pi/agent/AGENTS.md` vs `APPEND_SYSTEM.md` — these are semantically different files) **against a
  first-party Pi source** (Pi's own docs / source / release notes, not questionable-tier hearsay).
  Produce **one** concrete choice recorded in `REQ-YF-TUNE-020`, **or** conclude that **no first-party
  evidence exists**. On a resolved target: pin `REQ-YF-TUNE-020` to that single file. On no evidence:
  the `REQ-YF-TUNE-020` **fallback** activates — Pi rules ship only behind the explicit
  `--pi-rule-target {agents-md|append-system}` opt-in with a loud "unverified target" notice, and the
  Pi-rules-target verification is filed as a follow-on bead (Epic 10.2). This issue's output
  **resolves the "Pi rule target verified" capability gate** that blocks the Epic 6 Pi-rule-deployment
  issue (6.3). No code ships from this issue — it is a SPEC-resolving investigation.
  - depends-on: 1.4

### Epic 2: All four skills sub-verbs relocate under `yf harness skills` + `--harness` refactor (skills-only) + auto-detection
Relocate **all four** skills sub-verbs (`install`/`upgrade`/`remove`/`status`) under the
`yf harness skills` subcommand, deprecate the **entire** top-level `yf skills` group as an alias,
and replace `Surface` with a naba-style harness descriptor table; install deploys skill bodies only.
Grounded in `exp-002`.

- Issue 2.1: **`yf harness skills install|upgrade|remove|status` sub-verbs + whole `yf skills`
  alias-group + descriptor table + `--surface` deprecation.** Add a `harness skills` subcommand with
  **four sub-verbs** — `install|upgrade|remove|status` — matching the existing `yf skills` sub-verb
  style; `--tune` is a flag on the `install` sub-verb (no `--revert` here — revert is a
  `yf harness tune` flag). Keep the **entire top-level `yf skills` group** (`install`/`upgrade`/
  `remove`/`status`) working as a **deprecated alias** delegating verb-for-verb to
  `yf harness skills <verb>` (removed at the next major release, mirroring the `--surface` alias),
  emitting a deprecation notice. Introduce a `HarnessDescriptor` table (claude-code, codex, opencode,
  pi, agents) with `user_subpath`/`project_subpath`/optional `name_transform`, replacing the
  `Surface` enum in `cli.rs` / `dest.rs`. Add `surface_alias()` (`claude`→`claude-code`,
  `agents`→`agents`, passthrough) + legacy `.<id>/skills` fallback for unknown ids. Tagged test
  `REQ-YF-CLI-002`: each `yf skills <verb>` alias delegates to `yf harness skills <verb>` (identical
  behavior). Tagged test `REQ-YF-INSTALL-007`: a **SPEC↔code parity test** (naba pattern) parses
  the SPEC descriptor table and asserts it equals the shipped table (id, both subpaths,
  name_transform, count); pi's `lowercase-hyphen,max64` transform is exercised against a long yf
  skill name (`yf-change-validation`).
  - depends-on: 1.1
- Issue 2.2: **Repeatable `--harness`, path dedupe, skills-only install + bare-install warning.**
  Accept repeatable `--harness`, resolve each to its `(scope, subpath)` destination, and **dedupe by
  resolved absolute path** (codex + agents both → `.agents/skills`). Ensure `install` writes **skill
  bodies only** — the `install_rules_aggregate` call is removed from the install path (its relocation
  is Epic 3). **Documented behavior change (F5):** a bare `yf harness skills install` (no `--tune`)
  and the deprecated `yf skills install` alias emit a **warning** ("skills-only — run
  `yf harness tune` to deploy always-loaded rules"), and the install success output **states rules
  were NOT deployed**. Tagged tests `REQ-YF-INSTALL-002` (dedupe: `--harness codex --harness agents`
  yields one write) and `REQ-YF-INSTALL-008` (install touches no rules dir / writes no
  `YOSHIKO_FLOW.md`; bare install emits the skills-only warning + rules-not-deployed notice).
  - depends-on: 2.1
- Issue 2.3: **Harness auto-detection module (`PATH` injected for hermetic tests).** With no
  `--harness`, detect installed harnesses — user scope by probing each harness's home dir
  (`~/.claude`, `~/.codex`, `~/.config/opencode`, `~/.pi`) or `PATH` binary (`claude`, `codex`,
  `opencode`, `pi`); project scope by dot-dir presence (`.claude`/`.opencode`/`.agents`/`.pi`) — and
  act on all detected; explicit `--harness` overrides. **The detection module takes `PATH` as an
  injected parameter** (not read from the ambient process env) so Tier-2 tests control both the
  home-dir probe (sandboxed `HOME`) **and** the binary probe (injected `PATH`) hermetically. Factor
  detection into a reusable module (Epic 7 reuses it for the `--tune` bridge). Tagged test
  `REQ-YF-INSTALL-009`: under a sandboxed `HOME` **and injected `PATH`**, a seeded `~/.codex` is
  detected and an absent harness is not; explicit `--harness` bypasses detection.
  - depends-on: 2.1

### Epic 3: FLOW aggregation moves install→tune
Relocate the `YOSHIKO_FLOW.md` aggregation invocation from install to tune; mechanics unchanged.
Grounded in `exp-002` (naba's clean skills/config/rules boundary).

- Issue 3.1: **Invoke the aggregation from `tune`; drop it from `install`.** Move the
  `common::install_rules_aggregate` call out of `install.rs` and into the `harness::tune` rule-deploy
  path (Epic 6 consumes it). Preserve the engine's byte-stable serialization / reconcile-prune /
  `sha256` sections (`REQ-YF-FLOW-001..006` unchanged in mechanics). Tagged test `REQ-YF-FLOW-007`:
  a skills-only `install` writes no aggregate; a subsequent `tune` produces the identical aggregate
  the old install-time path produced (byte-stable).
  - depends-on: 1.2, 2.2
- Issue 3.2: **Backward-compat for existing installs.** An existing `YOSHIKO_FLOW.md` (written by a
  pre-plan-033 install) is left untouched by the now-skills-only install and **adopted/reconciled**
  by `tune` on first run — no orphaned or double-written aggregate. Tagged test `REQ-YF-FLOW-007`:
  a pre-seeded aggregate is reconciled (not duplicated) on first `tune`, and a skills-only re-install
  over it leaves it byte-identical.
  - depends-on: 3.1

### Epic 4: Format-aware config engine (JSON | TOML)
Introduce the format abstraction and the TOML delta-replay adapter; generalize scope/path
resolution. `merge.rs` is **not** modified — its existing tests must still pass. Grounded in
`exp-001`.

- Issue 4.1: **`SettingsFormat` + TOML delta-replay adapter.** Add a `SettingsFormat` enum and a TOML
  write adapter: parse `config.toml` into a `toml_edit::DocumentMut` (trivia/key-order) **and
  separately** derive a `serde_json::Value` for the merge decision; run the unchanged `merge()` for a
  `MergeReport`; **replay only the report's deltas (`ScalarAdded`/`ScalarForced`/`SetUnioned`, keyed
  by dot-path) onto the `DocumentMut`** and serialize *that document* (never the `Value`). Tagged test
  `REQ-YF-TUNE-013`: a merge decision computed over a TOML `Value` is replayed onto the `DocumentMut`
  and serialized to valid `config.toml` **preserving a pre-existing comment** (only passable under
  delta-replay).
  - depends-on: 1.3
- Issue 4.2: **Profile `format` field + generalized scope/path resolution.** Carry `format` on
  `Profile`; generalize `settings.rs` read/write and `settings_path_at` so scope resolution is
  profile-driven (not `.claude`-hardwired) and dispatches by format. Keep the fail-safe read
  (`Absent`/`Parsed`/`Malformed`) per format. Tagged test `REQ-YF-TUNE-014`: a TOML profile resolves
  to `~/.codex/config.toml` and a JSON profile to its own surface path; format dispatch selects the
  right adapter.
  - depends-on: 4.1

### Epic 5: Per-harness config profiles (codex TOML, opencode JSON; Pi config deferred)
Add the two embedded config profiles and wire `available_harnesses`. Codex exercises the Epic 4 TOML
path. Grounded in `exp-001` + research-002.

- Issue 5.1: `yf/profiles/codex.json` — `format: toml`, `config.toml` surface, entries per the
  research-002 codex mechanism/config surface. Tagged test `REQ-YF-TUNE-015`: profile loads, format
  is Toml, a fresh tune writes a valid `config.toml` honoring the kind-aware / idempotent /
  `Agent`-never-denied contract.
  - depends-on: 4.2
- Issue 5.2: `yf/profiles/opencode.json` — `format: json`, `~/.config/opencode/opencode.json`
  surface. Tagged test `REQ-YF-TUNE-016`: loads, reuses the JSON path, tune is idempotent.
  **Pi config deferral** is recorded (`REQ-YF-TUNE-017`) — no `pi` config profile ships; the loader
  returns a clean refusal for a Pi *config* tune while Pi skills/rules remain supported.
  - depends-on: 4.2

### Epic 6: Rule optimization + minimized managed-block deployment
The second `tune` sub-operation — minimize the aggregate to the irreducible-core and deploy it as a
managed block per harness. Grounded in research-002.

- Issue 6.1: **Minimization classifier + bundle↔source agreement assertion.** Derive the **minimized
  irreducible-core** bundle from the skills' `protocols/*.md` sources (from which `YOSHIKO_FLOW.md`
  is aggregated) via a **curated minimization classifier** that keeps only the irreducible rules
  (PLANS/RESEARCH override, the two bd mandates, UPSTREAM close-time, must-fire invariants) and drops
  the reducible on-edit engine rules (which stay prose cross-harness). **Implementer note:** the
  classifier is a *curated selection guarded by the agreement test*, not an autonomous oracle — the
  irreducible-vs-reducible call is the curatorial judgment research-002 made manually. Tagged test
  `REQ-YF-TUNE-018`: the **bundle↔source agreement assertion** passes for the current corpus and
  **fails loudly** when a `protocols/` section drifts or a new unclassified `protocols/` rule appears.
  - depends-on: 1.4, 3.1
- Issue 6.2: **Managed-block marker engine + per-harness target map (non-Pi).** `BEGIN/END`
  sentinels; append when absent, replace only the span between markers when present, never touch
  surrounding prose; fail-safe on partial/duplicate markers (refuse, don't corrupt). Define the
  per-harness **global-rule target map** for the **verified** harnesses (claude-code `~/.claude/rules/`,
  codex `~/.codex/AGENTS.md`, opencode `~/.config/opencode/AGENTS.md`). **Pi's target is deliberately
  excluded here** — it lands in the gated Issue 6.3. Tagged tests `REQ-YF-TUNE-019` (deploy into an
  AGENTS.md with pre-existing user prose preserves it; a second deploy is idempotent; a content change
  replaces only the managed span) and `REQ-YF-TUNE-020` (the target map resolves each **non-Pi**
  harness's rule path).
  - depends-on: 6.1
- Issue 6.3: **Pi rule-deployment target (gated on the verified/opted-in Pi target).** Wire Pi into
  the target map using the **single** rule target resolved by the Issue 1.5 investigation
  (`~/.pi/agent/AGENTS.md` **xor** `APPEND_SYSTEM.md`) — **never a compiled-in guess**. If Issue 1.5
  found no first-party evidence, Pi rules deploy **only** behind the explicit
  `--pi-rule-target {agents-md|append-system}` flag with a loud "unverified target" notice, and are
  otherwise skipped. Tagged test `REQ-YF-TUNE-020`: the resolved Pi target (or the explicit
  `--pi-rule-target` opt-in) drives a non-clobbering managed-block deploy; absent both a verified
  target and the opt-in flag, Pi rule deployment is refused with the unverified-target notice (never a
  silent default write).
  - depends-on: 6.2, 1.5, gate:pi-rule-target-verified

### Epic 7: `tune` orchestration — two sub-operations + `--tune` bridge + auto-detection
Wire `yf harness tune` to run both sub-operations per harness and bridge from `--tune` on install.
Grounded in `exp-002` (separable install/tune; auto-detect first-run).

- Issue 7.1: **Two-sub-operation orchestration.** `yf harness tune --harness <name>` runs config
  alignment (where a config profile exists — claude-code/codex/opencode) **and** rule deployment
  (all harnesses incl. pi), reporting a per-harness verdict; a Pi tune performs rule deployment and a
  clean config-deferred notice (rule deployment for pi goes through the gated Issue 6.3 target).
  `mod.rs` + CLI wiring. Tagged test `REQ-YF-TUNE-012`: a codex tune writes both `config.toml` and the
  `~/.codex/AGENTS.md` block; a pi tune writes only the rule block (against the verified/opted-in
  target) and reports config-deferred.
  - depends-on: 5.1, 5.2, 6.2, 6.3
- Issue 7.2: **`--tune` opt-in bridge + auto-detection first-run.** `--tune` on `harness skills
  install` stays opt-in (`REQ-YF-TUNE-023`) — without it, install is skills-only and reports that
  tuning is available; with it, the bridge also runs `yf harness tune`. The canonical bridge is
  `yf harness skills install --tune` (the `yf skills install --tune` alias still works during
  deprecation). `yf harness skills install --tune` with no `--harness` reuses the Epic 2 detection
  module to detect + install skills + tune every detected harness. **Bounded blast radius (F6):** the
  no-`--harness --tune` multi-harness auto path **prints the resolved target set and requires
  confirmation, or runs dry-run-then-apply**, before writing config/rules to every detected harness —
  it never fans out writes to all detected harnesses unconfirmed. Tagged test `REQ-YF-TUNE-023`: a
  skills-only install touches no config/rules; `harness skills install --tune` with a seeded
  harness runs both sub-operations for it (and so does the `yf skills install --tune` alias); the
  no-`--harness` multi-harness path surfaces the resolved target set for confirmation before any
  write; install and tune are separable.
  - depends-on: 7.1, 2.3

### Epic 8: Ownership manifest + `--revert`
Record what yf wrote and reverse it precisely. Closes yf-up7s.

- Issue 8.1: **Sidecar ownership manifest.** Record, per file/scope, the config dot-paths yf added
  (with both the **prior scalar value** where one existed **and the yf-written value**), the set
  elements yf **unioned in**, and the rule managed-block markers. The manifest lives under a `.yf/`
  dir beside the tuned surface (user: `<surface_dir>/.yf/harness-tune-manifest.json`; project:
  `<project-root>/.yf/…`); in project scope add `.yf/` to `.gitignore`. Wire the manifest write into
  both `tune` sub-operations. Tagged test `REQ-YF-TUNE-021`: after a tune, the manifest lists exactly
  the added keys (prior + yf-written values) + union deltas + block markers; project-scope `.yf/` is
  gitignored.
  - depends-on: 7.1
- Issue 8.2: **`--revert` with touched-since-tune guard.** `--revert` reads the manifest and removes
  **only** yf's added keys (restoring recorded prior scalar values), yf's union-added set elements
  (leaving operator entries), and managed blocks; fail-safe on a malformed target; idempotent.
  **Touched-since-tune guard:** before reverting a key, compare its current on-disk value to the
  recorded **yf-written value**; if they differ, **conservative-keep and report**, do not clobber.
  CLI flag + `mod.rs` wiring. Tagged test `REQ-YF-TUNE-022`: a tune→revert round-trip restores prior
  state (modulo reserialization); a key hand-edited since the tune is conservative-kept and reported;
  a rule-block revert preserves user prose; `Agent`-never-denied holds.
  - depends-on: 8.1

### Epic 9: Code-accurate web docs + diagrams + doc↔code agreement test
Publish, on the `web/` Pelican site, exactly what the two commands do per harness × scope — and lock
the docs to the code with an agreement test. Reconciles web beads `yf-8ayq` + `yf-ij06`.

- Issue 9.1: **Install matrix page.** Document `yf harness skills install` (canonical) on the
  `web/` site — noting `yf skills install` as the **deprecated alias** kept until the next major
  release — for each **harness** (claude-code, codex, opencode, pi, agents) × **scope** (user=`$HOME`
  / project=git-root), the resolved **skills** dir (per the descriptor table / `dest.rs` /
  `REQ-YF-INSTALL-002`) and the auto-detect behavior. **Call out (F5)** that a **bare install**
  (without `--tune`) is **non-functional for trigger-based engine skills** (yf-change-validation,
  yf-drift-check, yf-markdown-lint, yf-beads-upstream close-time) — those need the always-loaded rules
  that only `yf harness tune` deploys — so a first-run should use `install --tune` (or run
  `yf harness tune` after). Extend `web/content/pages/install.md`. Reconcile web bead `yf-8ayq`.
  Tagged `REQ-YF-TUNE-024`.
  - depends-on: 2.2
- Issue 9.2: **Tune matrix page + diagrams.** New `web/content/pages/harness-tune.md` documenting,
  per **harness** × **scope**, the exact config file `yf harness tune` writes (`~/.codex/config.toml`,
  `~/.config/opencode/opencode.json`, and their project-scope forms; **Pi config = deferred**), the
  rule managed-block target (claude-code `~/.claude/rules/`, codex/opencode AGENTS.md, **pi's
  verified/opted-in target per Issue 1.5** — one of `~/.pi/agent/AGENTS.md` / `APPEND_SYSTEM.md`, or
  the `--pi-rule-target` opt-in if unverified), the `.yf/` ownership manifest, and `--revert`.
  Enumerate **all three
  tune scopes** per config harness (user / project-local `settings_local_filename` / project-committed
  `settings_filename`) so the 9.3 test can check both filename fields. Author/adapt d2 diagrams (an
  install-matrix diagram and a tune-matrix diagram) into the web images dir per `yf-diagram-authoring`
  (reuse `diagrams/architecture.png` where apt). Reconcile web bead `yf-ij06`. Tagged `REQ-YF-TUNE-024`.
  - depends-on: 7.2, 8.2, 9.1
- Issue 9.3: **Doc↔code agreement test.** An assert-agreement test that derives the *actual*
  destinations/targets from the code — keyed to the canonical `yf harness skills install` command
  (the relocated command path), the descriptor table + `dest.rs` for install; profile
  `surface_dir`/`settings_filename`/`settings_local_filename`/`format` + the rule-deploy target map
  for tune — and **fails** if the published matrices in 9.1/9.2 diverge (missing row, wrong path,
  wrong file). Mirrors the **existing `yf/src/cmd/harness/drift.rs`** `REQ-YF-TUNE-008`
  doc-agreement pattern (reads the doc via `env!("CARGO_MANIFEST_DIR")`-relative path, diffs against
  the code oracle). **Implementer notes:** (a) code is the oracle, doc is the checked artifact;
  (b) assert **structural invariants** (descriptor subpaths; profile filename fields) rather than
  env-resolved absolute paths, scoped to the no-`--target` matrix. Tagged `REQ-YF-TUNE-025`.
  - depends-on: 9.2

### Epic 10: Integration, reference docs, and deferred follow-ons
Reviewable wrap-up: a cross-harness integration test, reference-doc/`--help` updates, and the filed
deferrals.

- Issue 10.1: **Cross-harness integration test + reference docs.** Under a sandboxed `HOME` (per
  project `TESTING.md` Tier-2 discipline), install skills per harness, tune (config where supported +
  rules) each of claude-code/codex/opencode then `--revert`, and tune-rules for pi then `--revert`,
  asserting round-trip restoration and no cross-harness path bleed. Update `docs/recommended-settings.md`
  per-harness reference blocks (**prose only** — the 008/009 drift axis is deferred), the SPEC §3.10
  intro prose (multi-harness now implemented), and CLI `--help`.
  - depends-on: 8.2, 9.3
- Issue 10.2: **File the deferred follow-on beads.** File: (a) **Pi config re-verification** (Pi
  config profile + config tune, gated on first-party Pi docs — the `REQ-YF-TUNE-017` deferral);
  (b) the deferred **per-harness `yf doctor`/drift axis** (008/009 analogs); (c) the **codex
  `project_doc_max_bytes` (32 KiB) block-size-budget check** (R8 — a managed block in
  `~/.codex/AGENTS.md` competing with operator content could push docs past the concatenation cap);
  (d) **conditionally** the **Pi-rules-target verification** follow-on — filed **only if** Issue 1.5
  found no first-party evidence and Pi rules shipped behind the `--pi-rule-target` opt-in (if 1.5
  resolved a verified target, this follow-on is unnecessary). Close **yf-8agh** and **yf-up7s**; mark
  web beads **yf-8ayq** / **yf-ij06** reconciled (Epic 9).
  - depends-on: 10.1

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Pi rule target verified (`gate:pi-rule-target-verified`)
- Type: capability
- Blocks: Issue 6.3 (Pi rule-deployment target)
- Condition: Pi's real always-loaded rule target is resolved to **one** concrete choice
  (`~/.pi/agent/AGENTS.md` **xor** `APPEND_SYSTEM.md`) against a first-party Pi source, **or** the
  investigation concludes no first-party evidence exists and the explicit `--pi-rule-target` opt-in
  fallback (with loud "unverified target" notice) is adopted in `REQ-YF-TUNE-020`.
- Test: Issue 1.5 has produced a single recorded SPEC target in `REQ-YF-TUNE-020` (verified path) or
  the fallback opt-in is documented and the Pi-rules-target follow-on is queued for Epic 10.2.
- Unblock: complete Issue 1.5; pin `REQ-YF-TUNE-020` to the resolved target (or the opt-in fallback);
  then Issue 6.3 may proceed. **No compiled-in guess may ship** while this gate is unresolved.

_(No reconcile gate: the sole upstream issue #95 is `related`, not a non-exclude incorporation, and
the web beads yf-8ayq/yf-ij06 are **local**, not upstream incorporations. The `toml`/`toml_edit`
crates are ordinary Cargo deps with no environmental prerequisite — no TOML-toolchain capability
gate is needed; the one capability gate above is the Pi-rule-target verification, per F1.)_

## Risks & Mitigations

| # | Risk | Mitigation |
|:--|:-----|:-----------|
| R1 | TOML reserialization loses operator comments / key order in `config.toml`; a merged `serde_json::Value` carries no trivia and cannot round-trip TOML datetimes / int-vs-float, so serializing it from scratch preserves nothing. | **Delta-replay** write path: parse `config.toml` into a `toml_edit::DocumentMut` (retains trivia/key-order) and separately derive a `Value` for the merge **decision only**; run the unchanged `merge()`, then replay only the `MergeReport` deltas (`ScalarAdded`/`ScalarForced`/`SetUnioned`, keyed by dot-path) onto the `DocumentMut` and serialize *that*. The `Value` is never the write source. Fail-safe refuse on a malformed `config.toml`, mirroring the JSON path (REQ-YF-TUNE-006). Tagged in Issue 4.1 (comment-survival test). |
| R2 | Rule aggregation moving out of `install` into `tune` breaks existing installs that already wrote `YOSHIKO_FLOW.md`, or double-writes / orphans the aggregate. | **Backward-compat contract** (`REQ-YF-FLOW-007`, Epic 3.2): the skills-only install leaves an existing aggregate byte-identical; `tune` adopts/reconciles it on first run; the aggregation *mechanics* are unchanged, only the invocation site moves. Tagged: pre-seeded aggregate is reconciled not duplicated. |
| R3 | The AGENTS.md managed block clobbers user prose. | Strict `BEGIN/END` sentinels; never edit outside the marked span; append-when-absent; **fail-safe refuse** on partial/duplicate/ambiguous markers rather than corrupt. Tagged in Issue 6.2. |
| R4 | `--revert` clobbers an operator's since-tune hand-edit: yf wrote `K=v` (revert would delete K), but the operator changed it to `K=v'` between tune and revert; a naive revert deletes their `v'`. Set-valued unions are similarly ambiguous. | **Touched-since-tune guard** (Issue 8.2): before reverting a key, compare its current on-disk value to the manifest's recorded **yf-written value**; if they differ, do **not** revert — report + conservative-keep. Set unions remove only the elements yf **added** (the merge report's `added` list); a recorded prior scalar is restored from its captured `from` value. Tagged in Issue 8.2. |
| R5 | **Auto-detection false positives / negatives + wide blast radius** — a stray `~/.codex` dir triggers an unwanted tune, a `PATH`-only install with no home dir is missed, or a no-`--harness --tune` run fans out writes to every detected harness unconfirmed. Also a non-injected `PATH` probe makes Tier-2 tests host-dependent (flaky). | Detection is **advisory + overridable**: explicit `--harness` always wins; user scope probes **both** home dir **and** `PATH` binary (either hits), project scope keys on dot-dir presence. **`PATH` is an injected parameter** so Tier-2 tests are hermetic (Issue 2.3). **Bounded blast radius (F6):** the no-`--harness --tune` multi-harness auto path **prints the resolved target set and requires confirmation, or dry-run-then-apply**, before any config/rule write (Issue 7.2). `--dry-run` surfaces the detected set. Tagged in Issues 2.3 / 7.2. |
| R6 | Pi config surface/paths are `[uncertain]` (research-002 Q6, questionable-tier sources only), and rust-embedded profiles commit any guessed path/format into a released binary. | **Defer Pi config only.** No `pi` config profile ships (`REQ-YF-TUNE-017`); Pi **skills + rules** *are* supported (skills path first-party). Epic 10.2 files a Pi config re-verification follow-on gated on first-party Pi docs. |
| R7 | Wrong per-harness rule/config target writes to the wrong file — claude-code's rule target is `~/.claude/rules/`, **not** `AGENTS.md`; and **Pi's rule target is a hidden-unknown** (`~/.pi/agent/AGENTS.md` vs `APPEND_SYSTEM.md` — semantically different; a wrong choice writes to a file Pi never reads and rules **silently don't load**). | The non-Pi target map is **data**, unit-tested against the research-002 mechanism table (Issue 6.2, incl. the claude-code-`rules`-vs-AGENTS.md distinction). **Pi's target is NOT a compiled-in guess (F1):** the "Pi rule target verified" **capability gate** blocks Issue 6.3 until Issue 1.5 resolves it to **one** first-party-checked choice, else Pi rules ship only behind an explicit `--pi-rule-target` opt-in with a loud "unverified target" notice. |
| R8 | The codex `project_doc_max_bytes` (32 KiB) concatenation cap — a managed block in `~/.codex/AGENTS.md` competes with existing operator content (research S-CX-1); a large block could push docs past the cap and silently truncate. | The irreducible-core bundle is *minimized* (only rules a `description` can't carry), keeping the block small. A **block-size-budget check follow-on is filed in Epic 10.2 (F7)**. |
| R9 | Implementation drifts ahead of the SPEC (violates the SPEC-first mandate). | Epic 1 lands all REQs first; Epics 2–10 `depend-on` Epic 1; every implementation issue ships a **tagged test** against a landed REQ id (the coverage gate's source of truth). |
| R10 | Modifying `merge.rs` regresses the plan-032 kind-aware/idempotent/`Agent`-never-denied contract. | `merge.rs` is **not** touched — the format work is purely adapter-side; its existing test suite is the regression guard and must stay green (Epic 4). |
| R11 | The `web/` install/tune docs drift from what the binary actually does (the operator's stated top concern). | The **doc↔code assert-agreement test** (Issue 9.3, `REQ-YF-TUNE-025`) derives the real destinations/targets from the descriptor table / `dest.rs` / the profiles / the target map and **fails CI on any divergence**. Diagrams accompany but the agreement test guards the tabular truth. |
| R12 | The `--surface`→`--harness` refactor + codex/agents both resolving to `.agents/skills` double-writes or breaks legacy `--surface` callers. | naba-proven pattern (`exp-002`): `surface_alias()` maps legacy values, unknown ids fall back to `.<id>/skills`, and repeatable harnesses are **deduped by resolved absolute path**. The SPEC↔code parity test (Issue 2.1) guards the descriptor. |
| R13 | Relocating skills ops under `yf harness skills` breaks users/scripts that call `yf skills <verb>` (a hard command rename would be a breaking change). | **Deprecated alias-group, not a rename** (`REQ-YF-CLI-002`/`REQ-YF-CLI-001`, Issue 2.1): the whole top-level `yf skills` group (`install`/`upgrade`/`remove`/`status`) keeps working, delegating verb-for-verb to `yf harness skills <verb>`, kept until the **next major release** of `yf` (mirroring the `--surface`→`--harness` alias treatment), emitting a deprecation notice. A test asserts each alias delegates with identical behavior (Issue 2.1); the doc↔code agreement test (9.3) documents the canonical command + the alias. |
| R14 | **Bare-install degraded state (behavior change from plan-032).** Moving the `YOSHIKO_FLOW.md` aggregation to `tune` means a fresh `yf harness skills install` (or the deprecated `yf skills install`) **without `--tune`** deploys skill bodies but **no always-loaded rules** — so trigger-based engine skills (yf-change-validation, yf-drift-check, yf-markdown-lint, yf-beads-upstream close-time) are **inert until `tune` runs**. Distinct from R2 (which only covers not-corrupting existing files). | **Explicit, documented behavior change (F5):** a bare install emits a **warning** ("skills-only — run `yf harness tune` to deploy always-loaded rules") and the success output **states rules were NOT deployed** (Issue 2.2, `REQ-YF-INSTALL-008`); Epic 9 web docs **call out** that a bare install is non-functional for trigger-based engine skills until `tune` runs (Issue 9.1). First-run guidance is `install --tune`. |

## Success Criteria

- `SPEC.md` carries the revised `REQ-YF-CLI-001` / `REQ-YF-CLI-002` / `REQ-YF-TUNE-002` /
  `REQ-YF-INSTALL-002`, new `REQ-YF-INSTALL-007..009`, revised `REQ-YF-FLOW-001..006` + new
  `REQ-YF-FLOW-007`, and new `REQ-YF-TUNE-012..025`; `REQ-YF-TUNE-011` is revised to record the
  follow-on delivered; `REQ-YF-TUNE-020` pins Pi's rule target to a single Issue 1.5-resolved choice
  (or the `--pi-rule-target` opt-in fallback); the per-harness `yf doctor`/drift axis (008/009
  analogs) is explicitly deferred with a follow-on bead; a plan-033 living-amendment-log entry is
  present. (Epic 1)
- `yf harness skills install --harness {claude-code,codex,opencode,pi,agents}` installs **skill
  bodies only** to the per-harness destination (descriptor table), dedupes codex+agents to one
  `.agents/skills` write, honors `--surface` as a deprecated alias, and auto-detects installed
  harnesses when no `--harness` is given; a SPEC↔code parity test guards the descriptor. A **bare
  install without `--tune`** emits the skills-only warning and states rules were **not** deployed
  (F5). (`REQ-YF-INSTALL-002/007/008/009`, `REQ-YF-CLI-002`; Epic 2)
- **All four** skills sub-verbs (`install`/`upgrade`/`remove`/`status`) live under
  `yf harness skills`; the **entire top-level `yf skills` group** is a **deprecated alias** mapping
  verb-for-verb to `yf harness skills <verb>` (kept until the next major release) and is covered by a
  test asserting each alias delegates with identical behavior — so **all** harness ops now live under
  `yf harness`. (`REQ-YF-CLI-001/002`, `REQ-YF-TUNE-002`; Epic 2)
- The `YOSHIKO_FLOW.md` aggregation is invoked by `yf harness tune`, not `yf harness skills install`; a
  skills-only install writes no aggregate and an existing aggregate is reconciled (not duplicated) on
  first tune. (`REQ-YF-FLOW-001..007`; Epic 3)
- `yf harness tune --harness {claude-code,codex,opencode}` aligns each harness's config — codex via a
  **TOML** delta-replay engine over `config.toml`, opencode + claude-code via the reused JSON path —
  honoring the **unchanged** kind-aware / idempotent / `Agent`-never-denied merge contract; a codex
  `config.toml` with operator comments survives a tune. (`REQ-YF-TUNE-012..016`; Epics 4–5, 7)
- `yf harness tune` deploys the minimized irreducible-core rule bundle (derived from the skills'
  `protocols/*.md` sources, with a bundle↔source agreement assertion) as a marker-delimited **managed
  block** into each harness's global-rule target — claude-code `~/.claude/rules/`, codex/opencode
  AGENTS.md — idempotent and non-clobbering of user prose. **Pi's rule target is not a compiled-in
  guess:** the "Pi rule target verified" **capability gate** blocks Issue 6.3 until the Issue 1.5
  investigation resolves it to **one** first-party-checked choice (`~/.pi/agent/AGENTS.md` **xor**
  `APPEND_SYSTEM.md`), else Pi rules ship only behind the explicit `--pi-rule-target` opt-in with a
  loud "unverified target" notice (F1). (`REQ-YF-TUNE-018..020`; Epics 1, 6–7)
- `yf harness skills install --tune` (no `--harness`, alias `yf skills install --tune`) provisions
  every detected harness end-to-end — but the no-`--harness` multi-harness auto path **prints the
  resolved target set and requires confirmation (or dry-run-then-apply)** before writing (F6);
  without `--tune`, install is skills-only and reports tuning is available — install and tune stay
  separable. Detection takes `PATH` as an injected parameter for hermetic Tier-2 tests.
  (`REQ-YF-TUNE-023`; Epic 7)
- `yf harness tune --revert` removes **only** yf-written config keys / union deltas / managed blocks
  and restores recorded prior values via the sidecar `.yf/` manifest, applying the **touched-since-tune
  guard** (a hand-edited-since-tune key is conservative-kept, not clobbered); a tune→revert round-trip
  restores prior state and a second revert is a no-op. Closes **yf-up7s** and **yf-8agh**.
  (`REQ-YF-TUNE-021/022`; Epic 8)
- **Pi config is deferred** (not implemented) — no `pi` config profile ships; `REQ-YF-TUNE-017`
  documents the deferral and a follow-on bead tracks Pi config re-verification. Pi **skills + rules**
  are supported. (Epics 1, 5, 10)
- The `web/` site publishes the **install matrix** (harness × scope → skills dir) and the **tune
  matrix** (harness × scope → {config file, rule target}, Pi config = deferred), with diagrams; a
  **doc↔code assert-agreement test** fails on any divergence from the descriptor table / `dest.rs` /
  the profiles / the target map. Web beads `yf-8ayq` and `yf-ij06` are reconciled. (`REQ-YF-TUNE-024/025`;
  Epic 9)
- Every new requirement has at least one **tagged test**; `cargo test` is green; `merge.rs` is
  unmodified and its existing tests still pass. (all epics)
- The multi-harness topology d2 diagram is authored at `diagrams/architecture.{d2,png}`; the web
  install-matrix and tune-matrix diagrams are authored into the `web/` images dir. (this plan / Epic 9)
