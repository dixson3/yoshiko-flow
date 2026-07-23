# SPEC — Yoshiko Flow (`yf`)

> **Living spec.** Originally sealed at Gate G0 (2026-06-14, operator) from plan-010 INTAKE; it now
> **evolves by amendment** — each substantive change lands alongside the plan (or release) that
> makes it and is recorded in the amendment log below. Requirements use RFC-2119 "shall". Per-skill
> `skills/<skill>/SPEC.md` carry their own `REQ-<KEY>-*`.
>
> **Amendment log:**
> - **2026-06-14 — G0 seal** (plan-010 intake): initial macro spec.
> - **plan-010 follow-ups:** `REQ-YF-PRE-004` config-path typo ratified; `REQ-YF-DIST-003` waived
>   (no Homebrew `test do` block — cargo-dist limitation).
> - **plan-011:** aggregated ruleset `YOSHIKO_FLOW.md` (`REQ-YF-FLOW-001..006`); `REQ-YF-INSTALL-005`
>   revised and `-006` superseded (no hand-edit tolerance).
> - **plan-012 (#29):** `yf-beads-hygiene` added to the skill catalog.
> - **v0.3.1:** Homebrew formula dropped its runtime `depends_on` (the SPEC `REQ-YF-DIST-002` text
>   was not updated until plan-018 — the lag this audit corrected).
> - **plan-018 (2026-06-30, #55):** vendor install + self-update — added `REQ-YF-DIRS-001`,
>   `REQ-YF-SELF-001..006`; revised `REQ-YF-CLI-001` (+`self`, +`migrate`), `REQ-YF-DIST-001`
>   (XDG `~/.local/bin` + `.tar.gz`), `REQ-YF-DIST-002` (no `depends_on`), `REQ-YF-DOCTOR-001`
>   (the `--repair` mutation surface + homebrew-shadow axis), `REQ-YF-PRE-002` (per-skill
>   `min-bd-version`), and `GUARDRAILS` GR-007 (update-check carve-out) / GR-011 (self-update deps).
> - **plan-018 audit pass (2026-06-30):** added `yf-change-validation` to the §4 catalog (was
>   missing); swept the stale `DRAFT (primed)`/"renamed by plan-010" banner from all per-skill SPECs;
>   per-skill drift fixes (notably `yf-beads-init` — the engine moved to the `yf` kernel, the Python
>   script is a retired shim).
> - **plan-019 (2026-07-02, #62-adjacent):** preflight self-update offer + cache version-invalidation
>   — added `REQ-YF-PRE-008` (generating-version stamp + full-reset invalidation), `REQ-YF-PRE-009`
>   (cache-only, vendor-only, dirty-build-bypassed self-update offer on the `ok` path), and
>   `REQ-YF-SELF-007` (`yf self update` invalidates preflight caches *via* the PRE-008 stamp — no
>   explicit clear). Added build-time `YF_GIT_DIRTY` capture (`git status --porcelain`, best-effort)
>   surfaced as a `-dirty` suffix on `VERSION_LINE`; `VERSION` stays `CARGO_PKG_VERSION`. SELF-007 is
>   a non-action REQ covered by the shared PRE-008 stamp-mismatch test.
> - **plan-021 (2026-07-02, #47/#63/#64):** yf-plan lifecycle rework — intake-at-execute. Relocated
>   the `plan-execute` pour from INTAKE to EXECUTE start and unified the duplicate-pour + resume
>   guards into one pour-once/resume gate (added `REQ-RESUME-004`, `REQ-PLAN-054`; revised
>   `REQ-PHASE-002`, `REQ-RESUME-001`, `REQ-PLAN-040`). Base-pinned named per-phase branches
>   (`<plan-id>-development` / feature `<plan-id>` / `<plan-id>-execute`) + a `landing-strategy`
>   config switch (`REQ-PLAN-05x`, Epic 2). Local auto-commit at the plan→execute boundary with a
>   default-branch fail-closed guard and a `GR-PLAN-003` carve-out (added `REQ-PLAN-064/065`).
>   Content-fingerprint-bound approval / stale-approved re-review gate (added `REQ-PORT-040/041`,
>   mirror `REQ-PLAN-034`).
> - **plan-023 (2026-07-05, #58/#67/#66/#57):** beads infra / local-only hardening. Added
>   `REQ-YF-PRE-010` (canonical **minimal-local beads profile** — per-repo local-server +
>   worktree-shared + local-only/no-remote — with read-only drift detection folded into
>   `detect_canonicalization_drift`, split into **correctable** local-only/no-remote vs
>   **detect/warn-only** engine-mode; embedded engine-mode is surfaced-with-guidance, never
>   auto-migrated) and the paired `REQ-BINIT-025` (repair corrects only the safe axes). Revised
>   `REQ-YF-PRE-004` and `REQ-YF-MIGRATE-001` for the `.yf/<short>/config.local.json` config
>   namespace (co-located with the `.yf/<short>/` state dir; resolution precedence subdir → flat
>   `.yf/<short>.local.json` → legacy root dotfile) and the **short-name standardization** — one
>   centralized `resolve_skill` shared by preflight and `migrate`, fixing the full-name
>   `.yf/yf-plan/` vs short-name `.yf/plan/` state-dir disagreement — and collapsed the top-level
>   gitignore anchors to one `/.yf/`. Revised `REQ-BINIT-023` to add `interactions.jsonl` to the
>   `.beads/.gitignore` top-up set (untracked **and** ignored, no `?? .beads/interactions.jsonl`
>   resurface). Reworded the `UPSTREAM_TRACKING.md` close-time Safety invariant to be
>   routing-primary (invoke `/yf-beads-upstream`), no longer a standalone hand-CLI recipe (#57).
> - **plan-020 (2026-07-02, #56):** mode-aware wedged-migration repair — revised `REQ-YF-PRE-007`
>   and `REQ-BINIT-011` to a **mode-aware** working-set flush (server `bd dolt stop` unchanged;
>   embedded storage uses a data-preserving raw-`dolt add -A && dolt commit` in the derived
>   Dolt-repo cwd, since `bd dolt stop` errors with no server); added `REQ-BINIT-016` (embedded-mode
>   detection via `metadata.json.dolt_mode` with a `dolt-server.*` filesystem fallback, derived
>   dolt-repo path with a zero/>1-candidate guard, clean-tree no-op, never `reset --hard`/
>   `--allow-empty`, and the commit-ok-migrate-fail partial-failure outcome); clarified
>   `GR-BINIT-002` that the embedded raw-`dolt` escape hatch is distinct from the forbidden
>   `bd vc commit`. Engine: `yf/src/beads_init.rs` gains a `dolt-commit-embedded` native
>   `apply_native` verb + mode-aware `Corrupted`-branch wiring.
> - **plan-023 follow-up (2026-07-05, yf-zlcq):** removed the transitional flat
>   `.yf/<short>.local.json` config tier now that the `.yf/<short>/config.local.json` migration is
>   ubiquitous. `REQ-YF-PRE-004` drops read-precedence tier 2 (now subdir → legacy root dotfile);
>   `REQ-YF-MIGRATE-001` drops the flat config migration source (config migrates only the legacy
>   root dotfile `.<old>.local.json`). Engine: `read_config` (`preflight.rs`) and `migrate`
>   (`migrate.rs`) drop the flat tier.
> - **plan-027 (2026-07-11, #84):** beads formula-staging kernel hardening. Added
>   `REQ-YF-PRE-011` — preflight **owns formula staging**: it writes each beads-backed skill's
>   embedded `formulas/*.formula.toml` into the project `.beads/formulas/` (verify-destination-
>   every-run unconditional copy, so a deleted destination re-stages — not a source-hash-only
>   skip), records ownership in a yf-owned staged-manifest marker (`.beads/formulas/.yf-staged.json`),
>   and gitignores `/.beads/formulas/` via the **root** `.gitignore` `ensure_scaffold` path (never
>   the bd-managed `.beads/.gitignore`); `SCAFFOLD_VERSION` bumped so already-preflighted repos get
>   the new anchor. Staging is best-effort scaffold-class — no new preflight status, so
>   `docs/yf/preflight-contract.md` §2 is unchanged. Added `REQ-YF-DOCTOR-004` — a static read-only
>   `FormulaCheck` axis over the **embedded** tree (concrete `bd mol (pour|wisp) <name>` tokens
>   inside **runnable bash fences**, excluding placeholders/prose) asserting each has a shipped
>   `formulas/<name>.formula.toml`; plus **provenance-tracked GC** behind its own
>   `yf doctor --prune-formulas` affordance (NOT plain `--repair`), removing only marker-attributed
>   yf-staged formulas no embedded skill still declares, never a foreign/unmarked proto, and nothing
>   at all with no marker. `FormulaCheck` is embedded-tree-based **by design** and does not use the
>   on-disk single-scope doctor path (`mod.rs`); the "both scopes per-repo" requirement is met by
>   embedded==verified-byte-identical-install coverage (no on-disk 2×2 enumeration added). Motivated
>   by the plan-026 `bd mol wisp plan-investigate` `proto not found` failure (a skill shipping a
>   formula it never staged, failing silently); this amendment makes the silent-omission bug class
>   structurally impossible (preflight stages) and statically detectable (doctor). Engine:
>   `yf/src/preflight.rs` (staging step + `SCAFFOLD_VERSION` bump), `yf/src/cmd/doctor/`
>   (`FormulaCheck` in `checks()` + `--prune-formulas` GC path). Fleet SKILL.md `cp`/`rm` staging
>   brackets removed (yf-plan `plan-execute`/`plan-investigate`, yf-research `yf-research`); the
>   permanent `--force` on `bd mol burn` retained.
> - **plan-026 (2026-07-15):** dependency-guarding for the markdown renderers. Added
>   `REQ-YF-DOCTOR-005` — a per-skill **`depends-on-tool`** doctor axis that reads each embedded
>   skill's `depends-on-tool` frontmatter and reports any declared tool missing from `PATH` (reusing
>   the `BinCheck` PATH-probe, install-hint format matching `REQ-MDPDF-003`), read-only, complementing
>   preflight's `system_deps_missing` enforcement. Paired per-skill: `REQ-MDHTML-005` (md2html run
>   entrypoint fail-closed `check_deps()` guard when `pandoc` is absent). Added `yf-markdown-html`
>   (`MDHTML`) and `yf-markdown-format` (`MDFMT`) to the §4 catalog — two new `markdown`-group skills;
>   `convert_wikilinks.py` moved from `yf-markdown-lint` to `yf-markdown-format`.
> - **plan-028 (2026-07-15, #87/#86):** two small skill fixes. **#87 (yf-research):** added
>   `REQ-RESEARCH-024` — the credibility scorer normalizes tz-naive publication dates to UTC (no
>   more `TypeError` crash on naive ISO dates) and tiers official vendor-documentation domains at
>   Tier 2 via both an explicit allowlist and a `docs.*` / `.dev` heuristic (evaluated after the
>   exact-tier loop, before the unknown-domain fallback, never downgrading Tier-1). **#86
>   (yf-plan):** amended `REQ-PLAN-064`'s intake commit-message format so an **approved-phase**
>   intake subject signals plan *state* (awaiting `/yf-plan execute`) rather than reading as
>   shipped work, and added a parked-plan detection requirement — a plan is *parked* when its
>   status is `approved` and its stored content fingerprint is present and fresh — surfaced via
>   `list` / `/yf-plan status` and a land-the-plane check, plus the Phase 4.5 tracking-issue title
>   `plan-NNN execution tracking`. See the per-skill `skills/yf-research/SPEC.md` and
>   `skills/yf-plan/SPEC.md` for the requirement text.
> - **plan-029 (2026-07-18):** OKF adoption — added the `yf-okf` skill (`skills/yf-okf/SPEC.md`,
>   the OKF-BASELINE ∪ OKF-YF-EXTENSIONS ∪ OKF-`<member>` family engine, vendored whole-file as
>   `_shared/okf.py` → `skills/{yf-plan,yf-research,yf-incubator,yf-okf}/scripts/okf.py`) and made
>   it the standard artifact-folder model for yf-plan, yf-research, and yf-incubator bundles. The
>   OKF-reserved `index.md` replaces the legacy seeded `README.md`/`_index.md`; the reserved
>   `log.md` (newest-first ISO-8601 phase history) replaces the in-`plan.md` `**Phase log:**` block
>   and the research ledger; every non-reserved bundle `.md` carries YAML frontmatter with `type` +
>   `okf_spec`; `plan.md`'s existing `**Field:**` header lines are dual-written with their
>   frontmatter mirror keys (one writer, both representations, never authored independently);
>   single-file incubator notes are OKF-exempt (no forced bundle dir); and `Incubator/INDEX.md`
>   remains a cross-bundle catalog, not a per-bundle `index.md`. Per-skill requirement text lives in
>   `skills/yf-plan/SPEC.md` (`REQ-PORT-050`, `REQ-DATA-015`), `skills/yf-research/SPEC.md`
>   (`REQ-RESEARCH-012`, with `REQ-PORT-007/008/009` in its `spec/portability.md`), and
>   `skills/yf-incubator/SPEC.md`
>   (`REQ-INCUB-040..043`); the family/engine REQs are `REQ-OKF-*` in `skills/yf-okf/SPEC.md`. Note:
>   incubator frontmatter round-trips value/order-preserving, not literally byte-for-byte (a
>   YAML flow-style block may re-serialize to block style). `DRIFT-CHECK.md` gained the
>   `okf-canonical` → `okf-copy-{plan,research,incubator,okf}` value-equal edges.
> - **plan-030 (2026-07-20, #89):** yf-plan CI/infra/release completion criterion. Added
>   **`REQ-PLAN-069`** (+ supporting **`REQ-PLAN-069a`** detection, **`REQ-PLAN-069b`** evidence) to
>   `skills/yf-plan/SPEC.md` §2.7: for a plan whose deliverable class is `ci-release`, the RECONCILE
>   close step (§6.4) hard-gates `complete` — after cascade-close (REQ-PLAN-067) and before
>   `update-status complete`, a new `complete-gate` verb halts completion (fail-loud, mirroring
>   `close_cascade.py`) unless **one** of: a `log.md` `- validated:` green-execution attestation, or
>   an open **out-of-tree** `deferred-validation` bead (label + `{"plan":...}` metadata, discovered by
>   label filter — never a plan-tree child, so cascade-close does not fail-loud on it first). Detection
>   is a **registered canonical dual-write field** `deliverable_class`↔`**Deliverable-class:**`
>   (fingerprint-excluded, durable across field-block rewrites), suggested by a `classify-deliverable`
>   heuristic and operator-confirmed; a `standard`/unset class makes the gate a strict no-op. Evidence
>   is an operator-attested `log.md` bullet (`validated:` joins `intake:` as a recognized non-status
>   token). Also codified the `workflow_dispatch` no-publish "test build" pattern
>   (`spec/ci-release-completion.md`). New spec text: `REQ-DATA-016`, `spec/phases.md`
>   `REQ-COMPLETE-001/002`, `spec/cli.md` `REQ-CLI-015/016/017`. Lesson driver: pybridge plan-010 CI
>   signing shipped `complete` unexecuted (`merged` is not `works`). Per-skill requirement text in
>   `skills/yf-plan/SPEC.md`.
> - **workflows install group (2026-07-22):** promoted `workflows` to a formal `skill-group`.
>   `yf-plan`, `yf-research`, and `yf-incubator` moved from `beads` to `skill-group: workflows`;
>   the `beads` install group is now the five `yf-beads-*` support skills. `REQ-YF-INSTALL-003`
>   group list gains `workflows`; `REQ-YF-INSTALL-004` clarified that a `--group` install closes over
>   its members' `depends-on-skill` closure, so `--group workflows` also installs the `beads` skills
>   the workflows depend on (no engine change — `resolve_selection` already applies the closure to a
>   group base; the `install-parity.json` golden and the `computed_groups` unit test were regenerated
>   for the new membership).
> - **plan-032 (2026-07-22, #95):** harness settings tuning. Added §3.10 **`REQ-YF-TUNE-001..011`** —
>   a machine-readable Claude Code settings profile (single source of truth, embedded via a separate
>   embed root; each entry carries path/value/kind/rationale with polarity in the value), a new top-
>   level `yf harness tune --harness <name> [--project [--committed]] [--force] [--dry-run] [--json]`
>   command with a **kind-aware** merge (scalar add-missing/conflict-report-vs-`--force`; set-valued
>   union that never removes user entries), the `Agent`-never-denied invariant, fail-safe refusal on
>   unparseable input, `bd setup claude` hook-block preservation, an assert-agreement drift test on the
>   `docs/recommended-settings.md` reference-baseline `jsonc` block, a **read-only** `yf doctor`
>   settings-drift axis over the effective merged view across precedence layers (decoupled from
>   `--repair`), and a `yf skills install --tune` opt-in (no interactive prompt). Multi-harness is a
>   forward-compat dimension only — Claude Code is implemented; concrete non-Claude profiles are a
>   follow-on gated on the `yf-2gyv` research (`yf-8agh`), unknown `--harness` refuses cleanly.
> - **plan-033 (2026-07-23):** yf multi-harness provisioning. Turned `yf` into a multi-harness
>   provisioner across three surfaces — skills install, config tuning, and always-loaded rule
>   deployment — for **claude-code, codex, opencode, and pi** (Pi *config* deferred). Relocated
>   **all four** skills sub-verbs under a canonical `yf harness skills install|upgrade|remove|status`,
>   making the **entire** top-level `yf skills` group a **deprecated alias** (kept until the next
>   major release) — revised `REQ-YF-CLI-001`, `REQ-YF-CLI-002`, `REQ-YF-TUNE-002` (the `harness`
>   group gains a `skills` subcommand alongside `tune`). Replaced `--surface {claude,agents}` with
>   repeatable `--harness {claude-code,codex,opencode,pi,agents}` over a per-harness **descriptor
>   table** (new `REQ-YF-INSTALL-007`, 5 rows, SPEC↔code parity test, pi `lowercase-hyphen,max64`
>   transform); generalized destination resolution (`REQ-YF-INSTALL-002` revised — dedupe-by-
>   resolved-path); made install **skills-only** with a bare-install rules-not-deployed warning (new
>   `REQ-YF-INSTALL-008`; `REQ-YF-INSTALL-001` revised); and added harness **auto-detection** with an
>   injected `PATH` (new `REQ-YF-INSTALL-009`). Moved the `YOSHIKO_FLOW.md` aggregation **invocation**
>   from install to `yf harness tune` (`REQ-YF-FLOW-001..006` invocation-site revised; new
>   `REQ-YF-FLOW-007` with backward-compat for existing installs — mechanics / byte-stability
>   unchanged). Added §3.10 `REQ-YF-TUNE-012..025`: the two-sub-operation `tune` (`-012`); the
>   format-aware `SettingsFormat` engine with TOML delta-replay while `merge.rs` stays
>   `serde_json::Value`-pure (`-013`); profile-driven scope/path resolution (`-014`); codex-TOML /
>   opencode-JSON profiles (`-015`/`-016`); the **Pi config deferral** (`-017`); rule
>   **minimization** from `protocols/*.md` with a bundle↔source agreement assertion (`-018`); the
>   `BEGIN`/`END` managed-block engine (`-019`); the per-harness rule target map with **Pi's target
>   pinned by Issue 1.5** — a verified first-party choice xor an explicit `--pi-rule-target` opt-in,
>   never a compiled-in guess (`-020`); the sidecar `.yf/` ownership manifest (`-021`); `--revert`
>   with a touched-since-tune guard (`-022`); the `--tune` opt-in bridge + auto-detect first-run
>   provisioning with a confirmed multi-harness blast radius (`-023`); the code-accurate `web/`
>   install/tune matrices (`-024`); and the doc↔code assert-agreement test (`-025`). Revised
>   `REQ-YF-TUNE-011` to record the follow-on **delivered** and to **explicitly defer** the
>   per-harness `yf doctor` / `docs/recommended-settings.md` drift axis (the 008/009 analogs) to a
>   filed follow-on bead. Closes `yf-8agh` (multi-harness) and `yf-up7s` (`--revert`); reconciles
>   local web beads `yf-8ayq` / `yf-ij06`. Engine work lands in later epics — this entry records the
>   SPEC-first Epic 1 amendment.

## 1. Purpose & scope

Yoshiko Flow is a family of portable, cross-harness agent **skills** plus a single compiled CLI,
**`yf`**, that installs, upgrades, verifies, and preflights those skills and the toolchain they
depend on. 

**In scope:** skill install/upgrade/remove/status lifecycle; embedded skill payload + integrity
markers; the shared preflight/config kernel (tool/version checks, companion-rule hash verification,
local config + state, beads-init verify/repair); `doctor`; Homebrew/cargo-dist distribution.

**Out of scope:** see `GUARDRAILS.md`. `yf` does **not** run skills, track issues (that is `bd`),
or render markdown/diagrams (those are skills).

## 2. Composition model (macro spec ← per-skill specs)

This root SPEC is the **macro spec**. It owns the `yf` tool requirements (`REQ-YF-*`) and
**composes** the per-skill specs by reference. Every skill ships its own
`skills/<skill>/SPEC.md` with `REQ-<SKILL>-NNN` requirements (see `skills/SPEC-TEMPLATE.md`). The
macro spec is *inferred* from this root plus the union of per-skill specs — no behavioral
requirement lives only in code (GUARDRAILS GR-010).

- **Authority:** a per-skill SPEC is authoritative for that skill's behavior; the macro spec is
  authoritative for `yf` and for cross-skill invariants (naming, install surface, portability).
- **Verification:** every `REQ-…` marked *(testable)* is the anchor a later integration/system test
  names (forward coverage enforced by plan-010 Issue 6.5). Tests cite the REQ id; the spec, not the
  code, is the reference.
- **Drift:** `SPEC.md ↔ GUARDRAILS.md ↔ README.md` is a drift-check edge (plan-010 Issue 5.4);
  per-skill `SPEC.md ↔ SKILL.md` SHOULD be a per-skill drift edge.

## 3. `yf` tool requirements

### 3.1 CLI surface (`REQ-YF-CLI`)

- **REQ-YF-CLI-001** *(testable, revised plan-033)* `yf` shall expose subcommands `harness` (the
  **canonical** home for `skills` and `tune` — `REQ-YF-TUNE-002`), `skills`, `self` (with
  `update|install|uninstall`), `doctor`, `preflight`, `migrate` (`REQ-YF-MIGRATE-001`), and
  `version`. The **canonical** skills lifecycle home is `yf harness skills` (carrying
  `install|upgrade|remove|status`); the top-level `skills` subcommand (with the same
  `install|upgrade|remove|status`) is retained as a **deprecated alias group** that delegates
  verb-for-verb to `yf harness skills <verb>` with identical behavior (kept until the next major
  release of `yf`, emitting a deprecation notice). The `self` namespace manages the **binary**
  lifecycle and is distinct from `skills`/`harness skills`, which manage the embedded skills/rules.
- **REQ-YF-CLI-002** *(testable, revised plan-033)* the canonical skills group `yf harness skills`
  shall carry all four sub-verbs `install|upgrade|remove|status` (matching the existing top-level
  `yf skills` sub-verb style); the `install` sub-verb shall accept `[--tune] [--harness <name>...]
  [--scope {user,project}]` (there is **no** `--revert` on `install` — `--revert` is a
  `yf harness tune` flag only, `REQ-YF-TUNE-022`). Skills sub-verbs shall accept `--scope
  {user,project}` (default `user`), repeatable `--harness {claude-code,codex,opencode,pi,agents}`,
  `--target <path>`, and `--dry-run`. `--surface {claude,agents}` shall be retained as a
  **deprecated alias** for `--harness` (`claude`→`claude-code`, `agents`→`agents`, passthrough for
  an unknown id + the legacy `.<id>/skills` fallback). The **entire** top-level `yf skills` group
  (`install|upgrade|remove|status`) shall remain a **deprecated alias** delegating verb-for-verb to
  `yf harness skills <verb>` with identical behavior, kept until the next major release of `yf`.
- **REQ-YF-CLI-003** *(testable)* every subcommand shall support `--json` for machine-readable
  output and shall exit non-zero on failure.
- **REQ-YF-CLI-004** *(testable)* `yf version` shall print the semver version (and build metadata
  when available).

### 3.2 Embedding (`REQ-YF-EMBED`)

- **REQ-YF-EMBED-001** *(testable)* the binary shall embed the entire `skills/` tree at build time
  (no network or repo clone required to install).
- **REQ-YF-EMBED-002** *(testable)* `yf` shall enumerate embedded skill names and per-skill file
  lists, and read any embedded file, from the binary alone.

### 3.3 Install / groups / dependency closure (`REQ-YF-INSTALL`)

- **REQ-YF-INSTALL-001** *(testable, revised plan-033)* `yf harness skills install` (canonical;
  `yf skills install` a deprecated alias) shall copy a skill's tree to the resolved destination. It
  writes **skill bodies only** (`REQ-YF-INSTALL-008`); surfacing companion rules (`protocols/*.md`)
  into the sibling `rules/` surface as the aggregated `YOSHIKO_FLOW.md` (`REQ-YF-FLOW-001`) is
  performed by `yf harness tune` (`REQ-YF-FLOW-007`), no longer by install.
- **REQ-YF-INSTALL-002** *(testable, revised plan-033)* destination resolution shall be driven by
  the **per-harness descriptor table** (`REQ-YF-INSTALL-007`): `--target` wins; else the resolved
  skills destination is `<anchor>/<harness.subpath>`, where `<harness.subpath>` is the descriptor's
  `user_subpath` (anchor = `$HOME`, user scope) or `project_subpath` (anchor = git-root/cwd,
  project scope). Repeatable `--harness` values shall be **deduped by resolved absolute path** (e.g.
  `codex` and `agents` both resolve to `.agents/skills`, yielding a single write). Install writes
  **skill bodies only** (`REQ-YF-INSTALL-008`); the rules surface is written by `yf harness tune`
  (`REQ-YF-FLOW-007`), not by install.
- **REQ-YF-INSTALL-003** *(testable)* `yf` shall parse SKILL.md frontmatter (`name`, `skill-group`,
  `depends-on-tool`, `depends-on-skill`, `user-invocable`) and compute install groups from
  `skill-group` (current: `workflows`, `beads`, `utility`, `markdown`) — computed as the union of
  all skills' values, never a hardcoded set.
- **REQ-YF-INSTALL-004** *(testable)* installing a skill **or a `--group`** shall transitively
  include the `depends-on-skill` closure of the selected set; unresolved/external deps shall be
  logged, not fatal. A group therefore installs the other groups it depends on: `--group workflows`
  (the `yf-plan` / `yf-research` / `yf-incubator` user workflows) pulls in the `beads` support
  skills its members depend on.
- **REQ-YF-INSTALL-005** *(testable)* `--group <g>`, explicit positional skill names, and `--strict`
  (fail on missing `depends-on-tool`) shall behave as in the retired `install.py`. `--force` shall
  **no longer overwrite rule content**: the aggregated ruleset is a fully `yf`-managed artifact whose
  acted-on sections are **always** regenerated to the embedded source (`REQ-YF-FLOW-004`), so
  `--force` is inert on the rule axis (M2; supersedes the old "overwrite existing rules" behavior).
- **REQ-YF-INSTALL-006** *(superseded by `REQ-YF-FLOW-004`)* the legacy "companion-rule install shall
  preserve an existing rule unless `--force`" no longer holds: under the aggregated ruleset there is
  no hand-edit tolerance (S3) — acted-on sections are always rewritten to the embedded source.
- **REQ-YF-INSTALL-007** *(testable, plan-033)* `yf` shall carry a **harness descriptor table** as
  the single source of truth for per-harness skills destinations — exactly **five rows**:
  `claude-code`, `codex`, `opencode`, `pi`, and `agents`. Each row shall carry an `id`, a
  `user_subpath`, a `project_subpath`, and an optional `name_transform`: claude-code `.claude/skills`
  (both scopes); opencode `.config/opencode/skills` (user) / `.opencode/skills` (project); pi
  `.pi/agent/skills` (user) / `.pi/skills` (project) with a `lowercase-hyphen,max64`
  `name_transform`; codex **and** agents both `.agents/skills` (both scopes — hence the
  `REQ-YF-INSTALL-002` dedupe-by-resolved-path). A **SPEC↔code parity test** shall parse this table
  from the SPEC and assert it equals the shipped descriptor (id, both subpaths, `name_transform`,
  and row count); pi's `lowercase-hyphen,max64` transform shall be validated against yf's long skill
  names (e.g. `yf-change-validation`).
- **REQ-YF-INSTALL-008** *(testable, plan-033)* `yf harness skills install` (and its deprecated
  `yf skills install` alias) shall deploy **skill bodies only** — it shall write **no** rules: it
  shall not write `YOSHIKO_FLOW.md`, fold standalone rule files, or otherwise touch the `rules/`
  surface (the aggregation is owned by `yf harness tune`, `REQ-YF-FLOW-007`). A **bare** install run
  **without** `--tune` shall emit a **skills-only warning** ("skills-only — run `yf harness tune` to
  deploy always-loaded rules") and its success output shall **state that rules were not deployed**.
- **REQ-YF-INSTALL-009** *(testable, plan-033)* when **no** `--harness` is given, `yf` shall
  **auto-detect** installed harnesses and act on all detected: at **user** scope by probing each
  harness's home dir (`~/.claude`, `~/.codex`, `~/.config/opencode`, `~/.pi`) **or** its binary on
  `PATH` (`claude`, `codex`, `opencode`, `pi`); at **project** scope by dot-dir presence (`.claude`,
  `.opencode`, `.agents`, `.pi`). An explicit `--harness` shall **override** detection. The detection
  routine shall take **`PATH` as an injected parameter** (not read from the ambient process
  environment) so tests control both the home-dir probe (sandboxed `HOME`) and the binary probe
  (injected `PATH`) hermetically.

### 3.3.1 Aggregated ruleset (`REQ-YF-FLOW`)

`yf` surfaces every rule-bearing skill's companion protocol as **one** operator-facing file in the
rules dir, `YOSHIKO_FLOW.md`, instead of a scatter of standalone `*.md` files. The format is owned
end-to-end by the `flow` module (as `marker` owns the SKILL.md marker).

**Invocation (revised plan-033):** the aggregation engine below (`REQ-YF-FLOW-001..006`) is invoked
by **`yf harness tune`**, not by `yf harness skills install` — install is skills-only
(`REQ-YF-INSTALL-008`). Only the **invocation site** moved (install → tune); the aggregation
**mechanics are unchanged** (byte-stable serialization, reconcile-prune, `sha256` sections), per
`REQ-YF-FLOW-007`.

- **REQ-YF-FLOW-001** *(testable)* the aggregate file shall carry a fixed do-not-edit banner, a
  deterministic `yf`-version generated-on note (never a wall-clock timestamp), and one HTML-comment
  fenced section per protocol — `<!-- yf-flow: skill=… protocol=… version=… sha256=… -->` … body …
  `<!-- yf-flow:end protocol=… -->` — ordered alphabetically by `protocol`. Each section body is the
  protocol file **verbatim**, so its `sha256` equals the `manifest.json` file sha256. `version` is
  omitted for a manifest-less protocol.
- **REQ-YF-FLOW-002** *(testable)* every write shall **reconcile-prune**: a section whose
  `(skill, protocol)` is no longer embedded, or whose manifest entry is `deprecated:true`, is dropped;
  a section for a skill merely **not selected** this run is retained (reconcile keys on the embedded
  set, never on the invocation selection).
- **REQ-YF-FLOW-003** *(testable, invocation revised plan-033)* on **any** `yf harness tune`
  rule-deploy write, every `yf`-owned standalone rule file present in the rules dir — including protocols for skills **not** named this run — shall be
  folded into `YOSHIKO_FLOW.md` and the standalone deleted (C4a migration); non-`yf` files are never
  touched; the fold is idempotent and preserves a folded standalone's bytes.
- **REQ-YF-FLOW-004** *(testable)* the aggregate is a fully `yf`-managed artifact (S3, no hand-edit
  tolerance): acted-on sections are **always** rewritten to the embedded source (no `--force` gate);
  `remove` drops the named skills' sections **unconditionally** (even a drifted section) and deletes
  `YOSHIKO_FLOW.md` when its last section is removed (S6).
- **REQ-YF-FLOW-005** *(testable)* `doctor` and `preflight` shall read a protocol's installed content
  from the aggregate **section body** when `YOSHIKO_FLOW.md` is present (authoritative), falling back
  to a legacy standalone file only when the aggregate is absent (transition release, S5). `doctor`'s
  axis stays presence + content-hash vs embedded (`rule_missing`/`rule_drift`/ok); `preflight`'s axis
  preserves **all seven** outcomes (`ok | update_available | drift | deprecated | missing |
  manifest_schema_unknown | manifest_missing`) by feeding the section body through the unchanged
  `manifest.json` semver machinery.
- **REQ-YF-FLOW-006** *(testable)* serialization shall be deterministic: `serialize → parse →
  serialize` is byte-stable (the generated-on note carries the `yf` version, not a timestamp), and
  section sha256 is over the body only, so header churn never perturbs a doctor/preflight verdict.
- **REQ-YF-FLOW-007** *(testable, plan-033)* `yf harness skills install` shall **no longer** write
  `YOSHIKO_FLOW.md`; the aggregate, its minimization, and its per-harness placement are owned by
  `yf harness tune` (`REQ-YF-TUNE-018..020`), which invokes the unchanged aggregation engine
  (`REQ-YF-FLOW-001..006`) — byte-stable serialization / reconcile-prune / `sha256` mechanics
  unchanged, only the invocation site moving from install to tune. **Backward-compat:** an existing
  install's already-written `YOSHIKO_FLOW.md` shall be left **byte-untouched** by the now-skills-only
  install, and **adopted/reconciled** by `tune` on its first run (no orphaned or double-written
  aggregate).

### 3.4 Integrity marker & up-to-date detection (`REQ-YF-MARK`)

- **REQ-YF-MARK-001** *(testable)* `yf` shall compute a per-skill **tree hash** = SHA256 over each
  file (sorted by relpath) as `relpath-bytes ++ file-bytes`, with `SKILL.md` **marker-stripped
  before hashing**, so a deployed marked copy hashes identically to the embedded source.
- **REQ-YF-MARK-002** *(testable)* on install/upgrade `yf` shall inject a single marker into the
  deployed `SKILL.md` after the YAML frontmatter: `<!-- yf-skills: v=<version> tree=<sha256> -->`.
- **REQ-YF-MARK-003** *(testable)* `yf skills status` shall report per skill: `installed`,
  `up-to-date` (deployed marker hash == embedded tree hash), `complete` (all embedded files
  present), `unmodified` (recomputed deployed hash, marker-stripped, == embedded).
- **REQ-YF-MARK-004** *(testable)* `yf skills upgrade` shall rewrite files, re-inject the marker,
  and **prune** deployed files absent from the embedded tree.

### 3.5 Preflight/config kernel (`REQ-YF-PRE`)

- **REQ-YF-PRE-001** *(testable)* `yf preflight <skill> --json` shall return a status from the
  superset schema `ok | ignored | system_deps_missing | bd_not_initialized | rule_missing |
  rule_drift | rule_deprecated | manifest_*`, plus `scaffold_added` and `instructions`, matching the
  legacy per-skill Python `check` output.
- **REQ-YF-PRE-002** *(testable)* the kernel shall detect required tools and enforce a minimum `bd`
  version read from each skill's `min-bd-version` frontmatter (the per-skill threshold, currently
  `1.0.5` across beads skills); a skill without that field imposes no `bd` floor.
- **REQ-YF-PRE-003** *(testable)* the kernel shall verify a companion rule against the skill's
  embedded `manifest.json` (sha256 + semver). The installed content is read from the aggregate
  `YOSHIKO_FLOW.md` **section body** when present, with a legacy standalone fallback when it is absent
  (`REQ-YF-FLOW-005`). All seven outcomes are preserved — `ok | update_available | drift | deprecated |
  missing | manifest_schema_unknown | manifest_missing` — so a section body matching a
  `previous_versions[].sha256` still yields `update_available`, a `deprecated:true` entry yields
  `deprecated`, and an unknown `schema_version` yields `manifest_schema_unknown`. This per-rule axis is
  **distinct** from the §3.4 whole-tree marker.
- **REQ-YF-PRE-004** *(testable, revised #67)* the kernel shall read per-skill config (including
  `ignore-skill`) and maintain runtime state under the **short-name** `.yf/<short>/` namespace.
  The **canonical** config location is `.yf/<short>/config.local.json` — co-located with the
  `.yf/<short>/` state dir. `read_config` shall resolve in precedence order, first match wins:
  1. the canonical subdir `.yf/<short>/config.local.json`;
  2. the legacy root dotfile named by the skill's `config_basename` descriptor field
     (e.g. `.yf-plan.local.json`).

  The **short name** is resolved by a single centralized `resolve_skill` (skill-arg → `(dir,
  short)`); `migrate` shall consume the **same** resolver so the state dir it writes and the state
  dir preflight reads agree (fixing the historical full-name `.yf/yf-plan/` vs short-name
  `.yf/plan/` disagreement). The state short-name and the config **basename** are distinct axes:
  standardizing the state short-name shall **not** misroute config resolution.
- **REQ-YF-PRE-005** *(testable)* the kernel shall scaffold a single top-level gitignore anchor
  (`/.yf/`) idempotently — one anchor covers both config (`.yf/<short>/config.local.json`) and
  state (`.yf/<short>/preflight.json`); no per-skill top-level dotfile anchors.
- **REQ-YF-PRE-006** *(testable)* beads-init **verify** shall classify a repo by parsing
  `bd status --json` for an `error` **key** (not exit code), distinguishing `not_initialized` from a
  wedged-but-initialized `corrupted` repo.
- **REQ-YF-PRE-007** beads-init **repair** shall apply the idempotent sequence with a **mode-aware**
  working-set flush (server: `bd dolt stop`; embedded storage: a data-preserving raw-`dolt`
  working-set commit — never `bd dolt stop`, which errors with no server) → `bd migrate schema →
  bd migrate`; gitignore/hooks/perms/JSONL hardening; local-only assertion. The per-skill
  `REQ-BINIT-011`/`REQ-BINIT-016` carry the mode-detection and data-preserving-commit detail.
- **REQ-YF-PRE-008** *(testable)* the kernel shall stamp each `.yf/<skill>/preflight.json` with the
  **generating `yf` version** (`yf-version`, the running `crate::VERSION` / `CARGO_PKG_VERSION` —
  the git hash and the `-dirty` marker are deliberately excluded, so a same-`CARGO_PKG_VERSION`
  clean↔dirty transition does not churn the cache). At the top of a preflight run, a stamped
  version differing from the running `crate::VERSION` (or an absent stamp) shall be treated as a
  **full cache miss**: the kernel shall **overwrite** the state file to drop `prereqs-present` and
  `scaffold-ensured` **before** the cold logic runs (never a merge that preserves the stale
  bool/int), then re-probe system deps + bd and re-run the idempotent scaffold ensure.
  `prereqs-present: true` shall be (re)persisted **only after** a successful probe on that run, so
  an early `system_deps_missing` return leaves the cache empty (re-probes next run) rather than
  stamping a new version over a stale-true flag. Verified by a test tagged `REQ-YF-PRE-008`.
- **REQ-YF-PRE-009** *(testable)* on an `ok` verdict, the kernel shall fold a **self-update offer**
  string into `instructions` when **all** hold: the running build is **not dirty**, the update check
  is not suppressed (`YF_NO_UPDATE_CHECK` / `CI` per `REQ-YF-SELF-006`), the install `Source` is
  **vendor** (`nag_eligible()`), and a **cache-only** read of `~/.cache/yf/update-check.json` yields
  `UpdateAvailable`. The **dirty-build check shall be the first short-circuit** — a `dirty` build
  (`YF_GIT_DIRTY`, whose normative probe is **`git status --porcelain`**: whole-repo, includes
  untracked files, best-effort/degrades to not-dirty when git is unavailable) unconditionally
  suppresses the offer, since it signals an operator actively managing `yf` locally. The offer is
  **cache-only** — preflight performs **no** network call (the offer is eventually consistent,
  appearing once the throttled `yf version`/`yf doctor` path refreshes the shared cache) and **no**
  mutation beyond the gitignore scaffold. The offer names `yf self update` (noting it also refreshes
  skill definitions/rules) and that the operator likely needs `/reload-skills` afterward. Verified by
  a test tagged `REQ-YF-PRE-009`.
- **REQ-YF-PRE-010** *(testable, #58)* the kernel shall assert a canonical **minimal-local beads
  profile** and **detect** drift from it **read-only** (no silent mutation), folded into
  `detect_canonicalization_drift`. The profile is three invariants:
  1. **per-repo local-server engine mode** — `bd` runs a Dolt server for this repo
     (`.beads/dolt-server.{pid,port}` present, or `dolt_mode: "server"` in `.beads/metadata.json`).
     Server-files-present ⇒ conformant. This is the **only read-only-observable** engine-mode
     signal — there is no `--shared-server`/host-port config, so "per-repo vs a hypothetical
     shared server" has **no observable** and is **not** an asserted axis.
  2. **worktree-shared** — automatic: `bd` resolves the canonical `.beads/` via git-common-dir, so
     every worktree reaches the one per-repo server. Not a separately-detected axis (it follows
     from invariant 1).
  3. **local-only / no-remote** — `dolt.local-only true`, zero `dolt_remotes` rows, no
     `sync.remote` (the plan-022 machinery: `has_local_only_remote`).

  The profile splits into two axis classes:
  - **Correctable** (invariant 3): missing `dolt.local-only` or a stray Dolt remote — surfaced as a
    canonicalization-drift string that **offers** `yf doctor --repair` (already the existing gap-3
    offer); `doctor --repair` corrects these via `REQ-BINIT-025` / the plan-022 machinery.
  - **Detect/warn-only** (invariant 1): an **embedded** store (`dolt_mode: "embedded"` / no
    `dolt-server.*`) is drift the kernel **warns** about with guidance, but **never auto-migrates**
    — engine-mode migration (server↔embedded) is **out of scope** (invasive, unproven). The warn
    names no `--repair` action (there is no safe correction to offer).

  This repo (local-server) is conformant, not drift. Verified by tests tagged `REQ-YF-PRE-010`:
  missing-local-only / stray-remote → detect + offer-repair; embedded → detect/warn (no mutation,
  no repair offer); local-server → conformant (no drift). No shared-server fixture (no observable)
  and no engine-migration fixture (out of scope).
- **REQ-YF-PRE-011** *(testable, plan-027)* the kernel shall **own formula staging** for
  beads-backed skills. On a skill's preflight, for each `formulas/*.formula.toml` embedded under
  that skill, the kernel shall write the file into the project's `.beads/formulas/` directory,
  **verifying destination existence on every run** — an unconditional copy keyed on destination
  presence/content, **not** a source-hash-only cache, so a destination deleted after any prior
  stage is re-created (never a stale "already staged" skip that leaves `bd mol pour|wisp` failing
  `proto not found`). The kernel shall record the basenames it staged in a **yf-owned
  staged-manifest marker** (`.beads/formulas/.yf-staged.json`) so ownership is provenance-tracked
  (consumed by `REQ-YF-DOCTOR-004` GC); the marker records, per staged basename, the declaring
  embedded skill(s). The kernel shall ensure `/.beads/formulas/` is gitignored via the **root**
  `.gitignore` `ensure_scaffold` path — **never** the bd-managed `.beads/.gitignore` — so staged
  protos are never committed. Staging is a **best-effort scaffold-class side effect** running
  beside the existing `ensure_scaffold` step and, like it, does **not** by itself change the
  returned preflight status (no new status enum value is surfaced, so
  `docs/yf/preflight-contract.md` §2 is unchanged); a staging I/O failure is reported in
  `instructions`, not by a fatal status. Because staging now writes a new scaffold anchor, the
  scaffold-ensure short-circuit version (`SCAFFOLD_VERSION`) shall be **bumped** so already-
  preflighted repos (whose `scaffold-ensured` cache equals the old version) receive the new
  `/.beads/formulas/` anchor rather than silently skipping it. Verified by tests tagged
  `REQ-YF-PRE-011`: fresh stage, idempotent re-run, source-changed re-copy,
  destination-deleted-but-cached re-stage, and gitignore anchor added on a repo carrying a
  pre-existing older scaffold state.

### 3.6 Doctor (`REQ-YF-DOCTOR`)

- **REQ-YF-DOCTOR-001** *(testable)* `yf doctor` shall check, per axis: `version`, `bd`
  (present + ≥ 1.0.5), `uv`, `git`, a **homebrew-shadow** warning (a tool on `PATH` shadowed by a
  Homebrew copy), each `skills:<name>` (via §3.4 marker comparison →
  `not installed`/`outdated`/`incomplete`/`modified`), and companion-rule presence/hash
  (`rules:<name>`).
- **REQ-YF-DOCTOR-002** *(testable)* `yf doctor` shall support `--json` and exit non-zero if any
  axis fails.
- **REQ-YF-DOCTOR-003** the read-only axes are the default; `yf doctor --repair` (explicit opt-in)
  shall **short-circuit** the read-only axes and instead apply the `yf-beads-init` repair sequence
  (`REQ-YF-PRE-007`) against the cwd repo, with `--local-only` (assert local-only Dolt) and
  `--remove-remote` (clear a configured Dolt remote) as opt-in modifiers. This is the one `doctor`
  path that mutates; without `--repair`, `doctor` never modifies the repo.
- **REQ-YF-DOCTOR-004** *(testable, plan-027)* `yf doctor` shall include a **static, read-only**
  `FormulaCheck` axis over the **embedded** skill tree (not on-disk scope enumeration — the
  embedded tree is the verified byte-identical install source, so a static check transitively
  covers every install scope). For each embedded skill that ships a `formulas/` directory, the
  check shall extract every concrete molecule name referenced as `bd mol (pour|wisp) <name>`
  **inside a runnable bash code fence** of that skill's `SKILL.md`, **excluding** placeholder
  tokens (`<name>`, `<formula>`, and other angle-bracketed metavariables) and any mention outside a
  runnable fence (prose, templates, comments). Every extracted name shall have a shipped
  `formulas/<name>.formula.toml`; a runnable `bd mol pour|wisp <name>` with no shipped formula is a
  **failure** (reported with remediation). A skill that references `bd mol pour|wisp` only in
  prose/templates (e.g. `yf-beads-authoring`, `yf-beads-extra`) **passes**. This axis needs no repo
  handle and never mutates. Separately, **provenance-tracked formula GC** shall be available behind
  its **own explicit affordance** — a distinct `yf doctor --prune-formulas` flag, **not** plain
  `--repair` (so a wedged-DB `--repair` can never trigger formula deletion). GC is cwd-scoped:
  using the `REQ-YF-PRE-011` staged-manifest marker (`.beads/formulas/.yf-staged.json`), it removes
  only `.beads/formulas/` entries the marker attributes to yf that **no** currently-embedded skill
  declares (an entry is kept if **any** embedded skill declares that basename). It shall **never**
  delete a formula not recorded in the marker (a foreign/local/bd-authored proto), and with **no
  marker present** it deletes nothing (fail-safe). Verified by tests tagged `REQ-YF-DOCTOR-004`:
  runnable-pour-without-formula flagged; prose-only pour passes; yf-staged orphan pruned under
  `--prune-formulas`; foreign (unmarked) formula NOT deleted.
- **REQ-YF-DOCTOR-005** *(testable)* `yf doctor` shall include a per-skill **`depends-on-tool`**
  axis: for each embedded skill it shall read the skill's `depends-on-tool` frontmatter and report
  any declared tool missing from `PATH`, **reusing the existing PATH-probe logic** (`BinCheck`),
  with an install hint matching `yf-markdown-pdf`'s missing-tool message format (REQ-MDPDF-003). A
  declared tool absent from `PATH` is a **failure** (surfaced under `REQ-YF-DOCTOR-002` exit-non-
  zero); a skill declaring no `depends-on-tool` passes. This axis is **read-only** and never
  mutates — it surfaces in the `doctor` report the same system-dependency gap that preflight
  already enforces as `system_deps_missing`.

### 3.7 Distribution (`REQ-YF-DIST`)

- **REQ-YF-DIST-001** *(testable)* `yf` shall be released via cargo-dist for `{darwin,linux} ×
  {amd64,arm64}` with sha256 checksums and semver derived from git tags. The generated `curl|sh`
  installer shall target `~/.local/bin` (XDG, `REQ-YF-DIRS-001`) and unix archives shall be
  `.tar.gz` (so the self-update consumer extracts with a pure-Rust gzip+tar decoder —
  `REQ-YF-SELF-003`). Linux targets build on native `ubuntu-22.04`/`ubuntu-22.04-arm` runners
  (glibc 2.35 floor; aarch64 is NOT cross-compiled).
- **REQ-YF-DIST-002** *(testable)* the release shall publish/update a Homebrew formula in
  `dixson3/homebrew-tap`. The formula declares **no** runtime `depends_on` lines: `bd` (beads) and
  `uv` are intentionally **not** Homebrew dependencies of `yf` (provisioned out-of-band via vendor
  installers / the dotfiles bootstrap), so neither the `curl|sh` installer nor the formula installs
  them. *(Revised — the original `depends_on "beads"`/`"uv"` block was dropped in v0.3.1.)*
- **REQ-YF-DIST-003** *(WAIVED — operator-ratified 2026-06-16)* the cargo-dist-generated Homebrew
  formula carries **no** `test do` block: cargo-dist (`dist` 0.32.0) emits a minimal formula and
  exposes no test-block knob, so `brew test yf` is not provided. `yf`'s behavior is verified
  instead by the crate test suite and the G1 install round-trip (build + `yf skills install` +
  `yf skills status`). Adding a test block would require a post-publish formula patch, intentionally
  not adopted (keeps the formula fully cargo-dist-managed).

### 3.7.1 XDG directories (`REQ-YF-DIRS`)

- **REQ-YF-DIRS-001** *(testable)* `yf` shall resolve its own directories via an **XDG** layout on
  **both** Unix and macOS (deliberately NOT macOS's `~/Library`), routed through one dirs module:
  config → `~/.config/yf`, cache → `~/.cache/yf`, data → `~/.local/share/yf`, bin → `~/.local/bin`.
  Resolution shall honor `XDG_CONFIG_HOME` / `XDG_CACHE_HOME` / `XDG_DATA_HOME` / `XDG_BIN_HOME`
  (ignoring non-absolute values per the XDG Base Directory spec), be total (a missing `$HOME` falls
  back, never panics), and expose a stubbed Windows arm (Windows is a follow-on target). These are
  **home-scoped** dirs, distinct from git-root-anchored **project** state; `yf` keeps no
  self-contained `~/.yf` home.

### 3.7.2 Vendor install & self-update (`REQ-YF-SELF`)

- **REQ-YF-SELF-001** *(testable)* `yf self` shall expose `update`, `install`, and `uninstall`, each
  supporting `--json`. The `curl|sh` installer shall write an install receipt to
  `~/.config/yf/yf-receipt.json` (cargo-dist's fixed schema; the load-bearing field is
  `install_prefix`).
- **REQ-YF-SELF-002** *(testable)* `yf self update` shall fetch the latest release's
  `dist-manifest.json`, compare the announcement tag to the running version, select the host
  triple's `executable-zip` (`yf-<triple>.tar.gz`) and its `checksum` artifact (format-driven),
  download the archive + `.sha256`, **verify the sha256** against the manifest checksum, **extract**
  the inner binary with a pure-Rust gzip+tar decoder (no system `tar`/`xz`), and **atomically
  replace** the running binary. `--check` shall report availability without downloading or swapping.
- **REQ-YF-SELF-003** *(testable)* install-source classification shall be **path-primary** on the
  canonicalized `current_exe()` (canonicalizing **both** the exe and the receipt-derived vendor
  prefix before the containment test, so a symlinked install dir does not false-refuse): a Homebrew
  (Cellar) copy shall be **refused** (directing to `brew upgrade`) and never updated even with
  `--force`; a from-build or unknown copy shall be refused unless `--force`; a vendor copy shall
  proceed. Classification shall survive a missing/`INSTALL_UPDATER=0` receipt (the canonicalized path
  is authoritative; the receipt only corroborates and its `source` field is a repo descriptor, not a
  classifier).
- **REQ-YF-SELF-004** *(testable)* `yf self install --from-build [--release|--debug] [--build]
  [--force]` shall promote the local `cargo build` output to `~/.local/bin/yf` and write a
  yf-authored from-build marker (`~/.config/yf/yf-from-build.json`) that suppresses the upgrade nudge;
  `yf self update --force` shall round-trip back to a vendor release. `yf self uninstall` shall remove
  the binary, the yf-owned XDG dirs, and the installer's `PATH` line, and shall **never** touch
  installed skills/rules (`~/.claude`, `~/.agents`).
- **REQ-YF-SELF-005** *(testable)* after a successful vendor update — unless `--binary-only` — `yf`
  shall re-deploy user-scope skills/rules by exec'ing the **swap-destination** binary (the path
  captured before the swap, NOT a post-swap `current_exe()`) once per **present** surface
  (`--surface claude` / `--surface agents`). A refresh failure shall be **fail-soft**: reported with
  the manual re-run command, exiting non-zero on the refresh alone, **never** rolling back the
  (successful) swap. A from-build install shall NOT auto-refresh.
- **REQ-YF-SELF-006** *(testable)* `yf version` and `yf doctor` shall emit a **throttled** (24h),
  **fail-open** (short timeout, errors swallowed), **vendor-only** upgrade nudge to stderr after the
  real output, cached in `~/.cache/yf/update-check.json`, suppressed by `YF_NO_UPDATE_CHECK=1` and
  auto-skipped under `CI`. The nudge is notify-only — it never downloads or swaps.
- **REQ-YF-SELF-007** *(testable)* `yf self update` shall invalidate stale preflight caches **by
  virtue of the `REQ-YF-PRE-008` version stamp** — the swapped-in binary reports a new
  `crate::VERSION`, so the next preflight run in any repo finds a mismatched (or, across the swap,
  differing) `yf-version` stamp and performs a full re-validation. There is **no** explicit
  cache-clear in `update.rs` (correct, since `yf self update` runs from an arbitrary cwd, not
  necessarily inside a beads repo). This is a **non-action** requirement (it asserts `update.rs`
  does nothing special); it is covered by the shared `REQ-YF-PRE-008` stamp-mismatch test — the
  coverage gate matches a REQ id wherever it is named in a `.rs` source, so a single test may tag
  both `REQ-YF-PRE-008` and `REQ-YF-SELF-007`.

### 3.8 Rename invariants (`REQ-YF-RENAME`)

- **REQ-YF-RENAME-001** all skills shall be named `yf-<skill>`; `bdplan → yf-plan`,
  `bdresearch → yf-research`; invocations become `/yf-<skill>`.
- **REQ-YF-RENAME-002 (INV-1)** the rename of the self-driving skills (`yf-plan`, `yf-research`)
  shall be the **last** execution step, performed in an isolated worktree, so the orchestrator
  driving the work runs from the installed copy and is not mutated mid-flight.
- **REQ-YF-RENAME-003** *(testable)* no canonical source shall retain a stale `bdplan`/`bdresearch`
  reference after the rename (drift-check clean).

### 3.9 Legacy migration (`REQ-YF-MIGRATE`)

- **REQ-YF-MIGRATE-001** *(testable, revised #67)* `yf` shall idempotently migrate legacy per-skill
  state and config into the canonical `.yf/<short>/` namespace:
  - **state**: `.state/<old>/` → `.yf/<short>/` (short name, matching what preflight reads — not
    the full `.yf/<skill>/` the pre-#67 migrator wrote);
  - **config**: the legacy root dotfile `.<old>.local.json` → `.yf/<short>/config.local.json`.

  Migration is idempotent and **never-clobber** (an existing dest is left untouched, source
  reported `skipped`), safe to re-run, and preserves values. `migrate` shall use the centralized
  `resolve_skill` (REQ-YF-PRE-004) for the short name so its dest matches preflight's read path.
  Migration shall also collapse legacy top-level per-skill gitignore anchors to the single `/.yf/`
  anchor (REQ-YF-PRE-005).

### 3.10 Harness settings tuning (`REQ-YF-TUNE`)

The yf-* skills assume the operator has turned **off** the competing Claude Code built-ins (native
plan mode, `TodoWrite`/`Task*`, native workflows, bundled skills, Claude-only memory/dream/upload).
Today that assumption lives only in prose (`docs/recommended-settings.md`). This section makes `yf`
the actor: it aligns a harness's settings to the skill contracts on demand (`yf harness tune`) and
surfaces drift on inspection (`yf doctor`). The command surface carries a **harness dimension**, and
as of plan-033 (`REQ-YF-TUNE-012..025`) the **multi-harness** model is **implemented**:
`yf harness tune` runs two sub-operations per harness — **config alignment** (claude-code + opencode
over the JSON engine; codex over a TOML delta-replay engine; the `merge.rs` decision engine is
byte-for-byte unchanged and stays pure over `serde_json::Value`) and **rule deployment** (the
minimized irreducible-core managed block into each harness's always-loaded global-rule surface) —
with a sidecar `.yf/` ownership manifest and a `--revert` that reverses only yf's own additions.
**Pi config remains deferred** (`REQ-YF-TUNE-017`): its config surface is `[uncertain]` and a
rust-embedded profile would commit a guess into a released binary; Pi still receives skills **and**
rule deployment.

- **REQ-YF-TUNE-001** *(testable)* `yf` shall embed a **machine-readable settings profile** as the
  single source of truth for the recommended Claude Code baseline. Each profile **entry** shall
  carry: a JSON **path** (e.g. `permissions.deny`, `todoFeatureEnabled`), a recommended **value**, a
  **kind** (`scalar` or `set-valued`), and a one-line **rationale**. Boolean **polarity** is encoded
  in the entry's value itself (mixed: `disable*` keys are `true`; `*Enabled` off-switches are
  `false`), so it cannot be hand-fumbled. The profile shall be embedded via a **separate embed root**
  (NOT under `../skills`, which treats every top-level dir as a skill and would pollute
  tree-hash/marker logic) and exposed through a typed loader.
- **REQ-YF-TUNE-002** *(testable, revised plan-033)* `yf` shall expose a top-level `yf harness`
  command group carrying **both** a `skills` subcommand (the canonical skills lifecycle —
  `install|upgrade|remove|status`, `REQ-YF-CLI-002`) **and** a `tune --harness <name> [--project
  [--committed]] [--force] [--dry-run] [--revert] [--json]` subcommand — the group is no longer
  `tune`-only. An **unknown** `--harness` (no embedded profile) on a `tune` **config** operation
  shall be a **clean refusal** (a reported verdict, not a stub write and not a crash); a harness with
  a rule target but no config profile (e.g. pi, `REQ-YF-TUNE-017`) shall run rule deployment and
  report config as **deferred**, not as a failure.
- **REQ-YF-TUNE-003** *(testable)* `yf harness tune` scope resolution shall default to **user**
  (`~/.claude/settings.json`), matching the skill-install default and staying disjoint from the
  project-scope beads hook `bd setup claude` owns. `--project` shall target project scope; the
  project default shall be the personal, gitignored `settings.local.json`, with `--committed` to
  target the shared `settings.json`. (The safe default is the gitignored file.)
- **REQ-YF-TUNE-004** *(testable)* the merge shall be **kind-aware**. A **scalar** entry shall be
  **add-missing**: an absent key is written; an existing key with a **different** value is **reported
  as a conflict and left untouched** unless `--force` (which overwrites it). A **set-valued** entry
  (an array, e.g. `permissions.deny`) shall be a **non-destructive union**: the profile's missing
  elements are added and **no** existing element is ever removed (preserving the operator's custom
  denies and `rm -rf` safety globs); union needs no `--force` because it cannot clobber.
- **REQ-YF-TUNE-005** *(testable)* the merge shall be **idempotent** (a second run over an
  already-tuned file writes nothing), shall **preserve** existing JSON structure and key order
  (`serde_json` `preserve_order`), and shall **never** deny or disable the `Agent` tool — every yf
  coordinator/investigator/reviewer fans out through it. The `Agent`-never-denied invariant holds
  even under `--force`.
- **REQ-YF-TUNE-006** *(testable)* on a **malformed / unparseable** settings.json the writer shall
  **refuse and report** (a verdict, never an overwrite) so no data is lost, mirroring
  `prune_empty_settings`. When it writes, it shall **preserve** any `bd setup claude` hook block
  (the beads `SessionStart` hook) untouched — tune writes only its own profile keys.
- **REQ-YF-TUNE-007** *(testable)* `yf harness tune` shall support `--dry-run` (compute and print the
  diff — added keys, unioned set elements, and scalar conflicts — without writing) and `--json`
  (machine-readable result: the file acted on, the changes, and any conflicts).
- **REQ-YF-TUNE-008** *(testable)* the fenced **reference-baseline** block in
  `docs/recommended-settings.md` (a `jsonc` fence carrying hand-authored `//` rationale comments)
  shall be **drift-checked against the profile** by an **assert-agreement** test: a JSONC-tolerant
  parse (strip `//` comments) compares the block's keys, scalar values, and array membership to the
  embedded profile and **fails** on divergence. The test shall **not** regenerate the block — the
  `//` comments are hand-authored prose and are preserved; only the key/value data is checked.
- **REQ-YF-TUNE-009** *(testable)* `yf doctor` shall include a **read-only** settings-drift axis for
  the Claude Code profile, computed over the **effective merged view** across the precedence layers
  (user ← project `settings.json` ← `settings.local.json`) so a recommended key set in a *different*
  layer is **not** a false "missing". It shall report missing recommended entries, scalar conflicts,
  and an accidentally **denied `Agent`**. The profile is its own reference set (no marker). The axis
  is **report-only** — its remediation is "run `yf harness tune`" — and is **decoupled** from `yf
  doctor --repair` (which short-circuits to the beads-init repair per REQ-YF-DOCTOR-003 and shall
  **not** gain a settings write).
- **REQ-YF-TUNE-010** *(testable)* `yf skills install` shall gain a `--tune` opt-in that runs `yf
  harness tune` after a successful install. There shall be **no** interactive prompt (install runs
  non-interactively and the `yf` binary has no prompt precedent); **without** `--tune`, install shall
  report that tuning is available and make **no** change to any settings.json.
- **REQ-YF-TUNE-011** *(revised plan-033)* the plan-032 multi-harness **follow-on is now delivered**:
  the format-aware engine (`REQ-YF-TUNE-013`), generalized scope/path resolution (`REQ-YF-TUNE-014`),
  and concrete codex-TOML / opencode-JSON profiles (`REQ-YF-TUNE-015..016`) land the codex/opencode
  config engines the original text pre-declared as "a new engine, not merely a new profile"; rule
  deployment (`REQ-YF-TUNE-018..020`) and `--revert` (`REQ-YF-TUNE-021..022`) close **yf-8agh** and
  **yf-up7s**. Pi **config** remains deferred (`REQ-YF-TUNE-017`). **Explicitly deferred:** the
  per-harness `yf doctor` / `docs/recommended-settings.md` settings-drift axis (the `REQ-YF-TUNE-008`
  / `REQ-YF-TUNE-009` analogs for codex/opencode) is **out of scope** here and tracked by a filed
  follow-on bead (Epic 10); the plan-032 Claude-Code drift/doctor axes remain in force unchanged.
- **REQ-YF-TUNE-012** *(testable, plan-033)* `yf harness tune --harness <name>` shall own **two
  sub-operations** per harness: **(a) config alignment** (the kind-aware merge engine,
  `REQ-YF-TUNE-004..006`) and **(b) rule optimization + deployment** (the minimized irreducible-core
  managed block, `REQ-YF-TUNE-018..020`), reporting a per-harness verdict covering both. A harness
  with no config profile (pi, `REQ-YF-TUNE-017`) shall run only the rule sub-operation and report
  config as **deferred**, cleanly, not as a failure.
- **REQ-YF-TUNE-013** *(testable, plan-033)* the config engine shall be **format-aware** via a
  `SettingsFormat` (`Json` | `Toml`). `merge.rs` shall remain **pure over `serde_json::Value`** and
  byte-for-byte unchanged. The TOML write path shall be **delta-replay**: parse the target
  `config.toml` into a `toml_edit::DocumentMut` (retaining comments, key order, and trivia),
  **separately** derive a `serde_json::Value` for the merge **decision only**, run the unchanged
  `merge()` to obtain a `MergeReport`, then **replay only the report's deltas** (`ScalarAdded` /
  `ScalarForced` / `SetUnioned`, keyed by dot-path) onto the `DocumentMut` and serialize **that
  document** — never the `Value` (which cannot round-trip TOML datetimes, int-vs-float distinctions,
  or trivia).
- **REQ-YF-TUNE-014** *(testable, plan-033)* per-harness scope/path resolution shall be
  **generalized off the profile** rather than Claude-hardwired: the `Profile` shall carry a `format`
  field (`REQ-YF-TUNE-013`) plus its surface-directory / filename fields, and `settings.rs` read /
  write / path resolution shall dispatch by profile (surface dir + filenames + format), preserving
  the fail-safe read (`Absent` / `Parsed` / `Malformed`) per format.
- **REQ-YF-TUNE-015** *(testable, plan-033)* `yf` shall embed a **codex** config profile with
  `format: toml` targeting `~/.codex/config.toml` (user scope) and its project-scope form,
  exercising the `REQ-YF-TUNE-013` TOML delta-replay path. A codex tune shall honor the unchanged
  kind-aware / idempotent / `Agent`-never-denied merge contract and preserve pre-existing operator
  comments in `config.toml`.
- **REQ-YF-TUNE-016** *(testable, plan-033)* `yf` shall embed an **opencode** config profile with
  `format: json` targeting `~/.config/opencode/opencode.json` (user scope) and its project-scope
  form, reusing the existing JSON merge path unchanged; an opencode tune shall be idempotent.
- **REQ-YF-TUNE-017** *(testable, plan-033)* **Pi config tuning is deferred.** No `pi` **config**
  profile shall ship: research-002 Q6 marks Pi's config surface `[uncertain]` (questionable-tier
  sources only), and because profiles are rust-embedded a guessed Pi config path/format would commit
  a guess into a released binary (correctable only by a point release, not a config edit). Pi
  **skills** (`REQ-YF-INSTALL-007`) and Pi **rules** (`REQ-YF-TUNE-020`) ship now; a `yf harness
  tune` targeting pi shall perform rule deployment and return a **clean config-deferred** verdict
  (not a stub write, not a crash). A follow-on bead (filed per Epic 10) tracks Pi config
  re-verification against first-party Pi docs.
- **REQ-YF-TUNE-018** *(testable, plan-033)* `yf harness tune` shall deploy a **minimized
  irreducible-core** rule bundle — the rules a skill `description` cannot carry (the `yf-plan` /
  `yf-research` native-override mandates, the two `bd`-usage mandates, the `yf-beads-upstream`
  close-time push, and the deterministic must-fire trigger invariants). The bundle shall be
  **derived from the skills' `protocols/*.md` sources** (the same sources `YOSHIKO_FLOW.md`
  aggregates), passed through a **minimization classifier** that keeps only the irreducible rules and
  drops the reducible on-edit engine rules (which stay prose cross-harness — no `paths`/hook analog
  is attested outside Claude Code). The derivation shall be **forward-looking and re-runnable**: a
  new skill's new `protocols/` rule automatically enters the same analysis. A **bundle↔source
  agreement assertion** shall hold for the current corpus and **fail loudly** when a selected
  `protocols/` section drifts or a new unclassified `protocols/` rule appears.
- **REQ-YF-TUNE-019** *(testable, plan-033)* the rule bundle shall be deployed as a **marker-
  delimited managed block** with `BEGIN` / `END` sentinels: append the block when absent, replace
  **only** the span between the markers when present, and **never** modify surrounding operator
  prose. The block merge shall be **idempotent** (a second deploy of the same bundle writes nothing)
  and **fail-safe** on partial or duplicate markers — refuse and report rather than corrupt the file.
- **REQ-YF-TUNE-020** *(testable, plan-033)* `yf` shall carry a **per-harness global-rule target
  map** naming each harness's always-loaded rule destination: claude-code `~/.claude/rules/`, codex
  `~/.codex/AGENTS.md`, opencode `~/.config/opencode/AGENTS.md`. **Pi's rule target shall NOT be a
  compiled-in guess:** it is **to be pinned by Issue 1.5** to **one** concrete first-party-verified
  choice (`~/.pi/agent/AGENTS.md` **xor** `~/.pi/agent/APPEND_SYSTEM.md`) against a first-party Pi
  source, gated by the "Pi rule target verified" capability gate. **Resolved (Issue 1.5, OUTCOME 1
  — first-party evidence found):** Pi's rule target is **`~/.pi/agent/AGENTS.md`**. The `--pi-rule-
  target` opt-in fallback described below is therefore **not** the operative path. **Fallback (now
  moot):** if the Issue 1.5 investigation had found **no first-party evidence**, Pi rules would ship
  **only** behind an explicit `--pi-rule-target {agents-md|append-system}` opt-in accompanied by a
  **loud "unverified target" notice** — never a silent compiled-in default. Pi **does** receive rule
  deployment, but only against a verified-or-explicitly-opted-in target. *(Pi target pinned by Issue
  1.5: `~/.pi/agent/AGENTS.md`. First-party source: earendil-works/pi official docs
  `packages/coding-agent/docs/usage.md`, "Context Files" — "Pi loads `AGENTS.md` or `CLAUDE.md` at
  startup from: `~/.pi/agent/AGENTS.md` for global instructions". `APPEND_SYSTEM.md` is rejected as
  the target because its global auto-discovery is unimplemented per earendil-works/pi issue #748,
  "`APPEND_SYSTEM.md` auto-discovery not implemented".)*
- **REQ-YF-TUNE-021** *(testable, plan-033)* `yf harness tune` shall record its writes in a **sidecar
  `.yf/` ownership manifest** beside the tuned surface (user: `<surface_dir>/.yf/harness-tune-
  manifest.json`; project: `<project-root>/.yf/…`). The manifest shall record, per file/scope: each
  config dot-path yf added (with **both** the **prior** scalar value where one existed **and** the
  **yf-written** value), the set elements yf **unioned in**, and the rule managed-block markers — the
  record the `--revert` guard (`REQ-YF-TUNE-022`) consumes. In **project** scope `.yf/` shall be
  **gitignored**.
- **REQ-YF-TUNE-022** *(testable, plan-033)* `yf harness tune --revert` shall reverse **only** yf's
  own additions recorded in the ownership manifest (`REQ-YF-TUNE-021`): it restores each recorded
  prior scalar value (or removes a key that had none), removes only the set elements yf unioned in
  (leaving operator entries), and removes the rule managed blocks (leaving surrounding prose). Revert
  shall apply a **touched-since-tune guard**: before reverting a key, it compares the key's current
  on-disk value to the recorded **yf-written** value; if they differ (an operator hand-edited it
  since the tune), the key is **conservative-kept and reported**, never clobbered. Revert shall be
  idempotent, fail-safe on a malformed target, and preserve the `Agent`-never-denied invariant.
- **REQ-YF-TUNE-023** *(testable, plan-033)* `--tune` on `yf harness skills install` shall remain an
  **opt-in bridge** — install and tune stay **separable**: without `--tune`, install is skills-only
  and reports that tuning is available (`REQ-YF-INSTALL-008`); with `--tune`, the bridge also runs
  `yf harness tune` for the acted-on harnesses. The canonical bridge is `yf harness skills install
  --tune` (the deprecated `yf skills install --tune` alias also works during deprecation). With
  **no** `--harness`, `--tune` shall provision every **auto-detected** harness (`REQ-YF-INSTALL-009`)
  end-to-end; the no-`--harness` multi-harness auto path shall **print the resolved target set and
  require confirmation, or run dry-run-then-apply**, before writing config/rules — it shall **never**
  fan out writes to all detected harnesses unconfirmed.
- **REQ-YF-TUNE-024** *(testable, plan-033)* the `web/` site shall publish **code-accurate**
  provisioning matrices: an **install matrix** (harness × scope → resolved skills dir, from the
  descriptor table / `dest.rs` / `REQ-YF-INSTALL-002`) and a **tune matrix** (harness × scope →
  {config file, rule target}), with **Pi config = deferred** (`REQ-YF-TUNE-017`) and **Pi rules =
  the verified/opted-in target** per Issue 1.5 (`REQ-YF-TUNE-020`), plus the **auto-detect** behavior
  (`REQ-YF-INSTALL-009`). The docs shall call out that a **bare install without `--tune`** is
  non-functional for trigger-based engine skills until `tune` runs.
- **REQ-YF-TUNE-025** *(testable, plan-033)* a **doc↔code assert-agreement test** (mirroring the
  `REQ-YF-TUNE-008` / `yf/src/cmd/harness/drift.rs` pattern) shall derive the real
  destinations/targets from the **code oracle** — the descriptor table / `dest.rs` for install, and
  the profiles (`surface_dir` / `settings_filename` / `settings_local_filename` / `format`) + the
  rule-deploy target map for tune — and **fail** if the published `REQ-YF-TUNE-024` matrices diverge
  (missing row, wrong path, wrong file). Code is the oracle; the doc is the checked artifact.

## 4. Skill catalog (per-skill specs)

The macro spec composes these. `REQ-<KEY>-*` ids live in each skill's `SPEC.md`.

| Skill (`yf-`)           | Was                  | Group    | Spec key | Per-skill SPEC                           |
| :---------------------- | :------------------- | :------- | :------- | :--------------------------------------- |
| yf-plan                 | bdplan               | beads    | PLAN     | `skills/yf-plan/SPEC.md`                 |
| yf-research             | bdresearch           | beads    | RESEARCH | `skills/yf-research/SPEC.md`             |
| yf-beads-authoring      | beads-authoring      | beads    | BAUTH    | `skills/yf-beads-authoring/SPEC.md`      |
| yf-beads-extra          | beads-extra          | beads    | BEXTRA   | `skills/yf-beads-extra/SPEC.md`          |
| yf-beads-init           | beads-init           | beads    | BINIT    | `skills/yf-beads-init/SPEC.md`           |
| yf-beads-hygiene        | _(new, #29)_         | beads    | HYG      | `skills/yf-beads-hygiene/SPEC.md`        |
| yf-beads-upstream       | beads-upstream       | beads    | BUP      | `skills/yf-beads-upstream/SPEC.md`       |
| yf-incubator            | incubator            | beads    | INCUB    | `skills/yf-incubator/SPEC.md`            |
| yf-change-validation    | _(new)_              | utility  | CHGVAL   | `skills/yf-change-validation/SPEC.md`    |
| yf-diagram-authoring    | diagram-authoring    | utility  | DIAG     | `skills/yf-diagram-authoring/SPEC.md`    |
| yf-drift-check          | drift-check          | utility  | DRIFT    | `skills/yf-drift-check/SPEC.md`          |
| yf-optimal-instructions | optimal-instructions | utility  | OPTINST  | `skills/yf-optimal-instructions/SPEC.md` |
| yf-skill-authoring      | skill-authoring      | utility  | SKAUTH   | `skills/yf-skill-authoring/SPEC.md`      |
| yf-markdown-lint        | markdown-lint        | markdown | MDLINT   | `skills/yf-markdown-lint/SPEC.md`        |
| yf-markdown-pdf         | markdown-pdf         | markdown | MDPDF    | `skills/yf-markdown-pdf/SPEC.md`         |
| yf-markdown-html        | markdown-html        | markdown | MDHTML   | `skills/yf-markdown-html/SPEC.md`        |
| yf-markdown-format      | markdown-format      | markdown | MDFMT    | `skills/yf-markdown-format/SPEC.md`      |

> Several skills already ship topical design docs under `skills/<skill>/spec/*.md` (e.g. `cli.md`,
> `data.md`, `phases.md`, `portability.md`). The per-skill `SPEC.md` is the **requirement-numbered**
> contract; it MAY reference those design docs rather than restate them.

## 5. Verification

- Each *(testable)* requirement maps to ≥1 integration/system test naming its REQ id (plan-010
  Epic 6; coverage enforced by Issue 6.5).
- `yf`-tool requirements are verified by the crate test suite; per-skill requirements by that
  skill's own checks/tests where present.

## 6. References

- `GUARDRAILS.md` — the out-of-domain boundaries this spec operates within.
- `docs/plans/plan-010-james-dixson-73eebd/plan.md` — the plan that produces `yf`.
- `skills/SPEC-TEMPLATE.md` — the per-skill SPEC schema.
