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
> - **plan-034 (2026-07-23):** post-plan-033 follow-ups. Added §3.10 **`REQ-YF-TUNE-026`** — the
>   read-only `yf doctor` settings-drift axis (`SettingsDriftCheck`, `REQ-YF-TUNE-009`) runs for every
>   config-profile harness (codex/opencode) via `from_env` registration reusing the shipped
>   harness-generic check (not a new engine, and `harness/drift.rs`/`REQ-YF-TUNE-008` untouched), plus
>   a new **per-harness managed-block drift** check reported distinctly from the aggregate `rule_drift`
>   (each codex/opencode/pi AGENTS.md yf-managed block vs `minimize::irreducible_core_bundle()`); both
>   read-only — the `REQ-YF-TUNE-009` analog `REQ-YF-TUNE-011` had deferred. Added **`REQ-YF-TUNE-027`**
>   — a codex `project_doc_max_bytes` block-size-budget **warning** (never truncate/block): projected
>   global `~/.codex/AGENTS.md` size (content + managed block) vs the effective on-disk cap (read from
>   `~/.codex/config.toml`, default **32768** when absent — not the profile's 65536), warning at ≥90%
>   and naming cap + projected size, with a documented single-file scope limitation (the global file
>   only, not codex's full multi-file concatenation). Revised **`REQ-YF-TUNE-011`**'s deferral note to
>   record the `-009` drift axis **delivered** (its follow-on bead closed). Closes local follow-on beads
>   `yf-252c` (drift axis) and `yf-297v` (budget check); the `web/` documentation buildout (a
>   workflow-vocabulary glossary, a beads & `yf-beads-*` concepts doc, `yf-plan`/`yf-research`
>   subagent+workflow docs, and a managed-files reference) is documentation of shipped behavior and
>   ships no new REQ. Engine work lands in later epics — this entry records the SPEC-first Epic 1
>   amendment.
> - **plan-037 (#116):** added **`REQ-PLAN-071`** (verdict-line contract — the red-team template and
>   the `ready-check` parser are one contract: the template emits `## Verdict:`, the parser accepts
>   `^#{2,3}\s+Verdict:` as defence in depth) and **`REQ-PLAN-072`** (a malformed verdict fails loud —
>   `review_pass > 0` with an unparseable verdict is reported as a malformed-review error naming the
>   file, never as a null verdict). Driven by a live defect: the template emitted `### Verdict:` while
>   the parser matched `## Verdict:`, so a review written exactly as prescribed was silently
>   unparseable and `ready-check` reported `review_pass: 2` alongside `verdict: null`.
> - **plan-037 (#110, partial):** added the **`yf-herdr`** skill (`skills/yf-herdr/SPEC.md`, spec key
>   `HERDR`, group `utility`) to the §4 catalog — delegating an approved `yf-plan` or gated
>   `yf-research` to a subordinate session in a new herdr tab and observing it. Authored outside
>   version control in `~/.claude/skills/` and imported here; its `REQ-HERDR-*` requirements carry
>   over unchanged, plus `REQ-HERDR-040/041` recording the third-party-`herdr` dependency posture
>   (`depends-on-tool`, never `depends-on-skill`; prose soft-dep). Delivers the *skill surface* of
>   #110 only — the `herdr agent *` fan-out primitive it proposes stays open.
> - **plan-037 (#100, #107, #101):** revised **`REQ-YF-PRE-004`** from two-tier first-match-wins to a
>   **three-tier key-by-key merge**, and added **`REQ-YF-PRE-004a`** introducing the **committed**
>   `.yf/<short>/config.json` tier — the single carve-out in the otherwise fully-ignored `.yf/` tree,
>   for decisions that are properties of the repository rather than of a checkout. Added
>   **`REQ-PLAN-079`** (configurable, import-safe `plans-root` / `incubator-root`;
>   allocated under the number **073** at the time and renumbered by plan-053 / #214 to resolve
>   an id collision with the `stamp-tracker` requirement — plan-037-era records cite it under the
>   old number). `plan_manager.py`
>   is now aligned to the binary: same three tiers, short-name `.yf/plan/` state with migration from
>   the full-name dir; `change_validation.py`'s `validate-cmd` seed reads the same reader (#101).
>   Operator decision recorded at `docs/plans/plan-037-james-dixson-cab694/decisions/config-tier.md`.
>   Does **not** settle #102 — it carves out one file rather than generalizing the rule.
> - **plan-038 (2026-08-14, #129/#106/#117/#105):** `yf-beads-upstream` made to enforce its own
>   never-hand-run invariant, and its push machinery corrected. Added **`REQ-BUP-050`** — emitted
>   `bd <backend> push` commands use **space-separated** positional ids (a comma-joined list matches
>   **zero** beads while exiting 0, measured on bd 1.1.2) and any sequence with a destructive
>   follow-on stage is **fail-closed**, verifying the push matched the expected bead count before
>   the `bd close` tombstone runs. Records the output-parse as an explicitly bd-version-dependent
>   assumption whose failure mode is safe (unrecognized output ⇒ unverified ⇒ halt). Added
>   **`REQ-BUP-051`** (the first-class `push` verb — dry-run first, scoped `--issues`, inline auth,
>   `--apply`-only idiom, and the #105 owner-claimed warning surfaced inline), **`REQ-BUP-052`**
>   (the propose-only `closable` verb on the per-bead `External:` signal, with its coarse-tracker
>   gap recorded — #117 stays **open**), and **`REQ-BUP-053`** (the mechanical procedure/explanation
>   boundary: fenced ` ```bash ` blocks in the Push step and Backend generalization sections are
>   procedure; prose, tables, and blockquotes — including the invariant statements that quote the
>   forbidden command *in order to forbid it* — are explanation). Added guardrails **`GR-BUP-005`**
>   (never document a hand-run push as the procedure; never check it with a global grep),
>   **`GR-BUP-006`** (a zero-exit `bd` push is not evidence of a push), and **`GR-BUP-007`**
>   (emitted-command tests assert a contract, never the emitted string — the defect that let #129
>   survive a green suite). Engine work lands in later epics — this entry records the SPEC-first
>   Epic 1 amendment.
> - **plan-039 (2026-08-15, #112/#113/#114):** yf-plan review-quality hardening along the structural
>   and factual axes. Added **`REQ-AGENT-046`** (red-team **gate reachability** — a `Condition`
>   depending on evidence produced inside its own `Blocks` set is a cycle; gate the mutating step),
>   **`REQ-AGENT-047`** (red-team **precondition cross-check** — each issue's assumed artifacts,
>   tools, and capabilities are produced by a declared `depends-on` predecessor or established by a
>   gate; #113's cheap branch, explicitly **without** a `requires:` schema key or a DAG-walk engine,
>   which measurement against the same corpus found unjustified), and **`REQ-AGENT-048`** (red-team
>   **premise check** — measured vs inferred, corroboration, and *what would falsify this and was it
>   checked*). Revised **`REQ-AGENT-021`** so investigator findings mark load-bearing conclusions
>   `measured` or `inferred` and require corroboration for any inference the plan builds on. All
>   four are prompt-level contracts: the evidence is that four of the five structural defects
>   observed in d3-pxe plan-013 — including an unsatisfiable gate that survived conformance and two
>   red-team cycles — had their preconditions written out in prose and only the dependency edge
>   missing.
> - **plan-039 (2026-08-15, #108):** revised **`REQ-CLI-015`** to the corrected deliverable-class
>   classifier contract — the scan region is the Epics / Upstream Issues / Success Criteria sections
>   rather than the whole file; fenced blocks and inline code spans are stripped before matching (a
>   quoted token is not a claim); negative-context guards ship with an explicit stop rule; a
>   `ci-release` suggestion **requires a high-tier signal**, with low-only matches reported
>   informationally; and the result carries an `evidence` basis (`path-backed` | `prose-only`)
>   because `confidence` is constant at intake, where `--changed` is empty. Measured on 53 real
>   plans: the prior heuristic suggested `ci-release` on 40, and on the 17 operator-labeled plans it
>   was wrong 16 times with zero correct negatives, at `confidence: high`. `FN=0` is preserved at
>   every step — a false negative silently disarms `complete-gate`, so recall is the safety-critical
>   direction.
> - **plan-039 (2026-08-15, frontmatter integrity):** added **`REQ-YF-EMBED-003`** — every embedded
>   `skills/*/SKILL.md` and `skills/*/agents/*.md` carries a well-formed, **terminated** YAML
>   frontmatter block, enforced repo-wide by `scripts/check_frontmatter.py` in the fast and full
>   validation tiers. Homed in §3.2 Embedding rather than under a per-skill key because the
>   invariant constrains the shape of the whole embedded `skills/` tree. Prompted by
>   `skills/yf-plan/agents/reviewer.md`, whose closing `---` had been replaced by `:--` — a GFM
>   table-alignment marker — leaving the block unterminated and the agent's metadata unparsed, with
>   no visible symptom. Audited at the time across all 20 skills: it was the only offender.
> - **plan-040 (2026-08-16, #133/#117/#131/#132):** `yf-beads-upstream` upstream writes moved from
>   `bd <backend> push` to **gh-direct** — `bd` reads bead content, `gh` writes the issue,
>   `bd update --external-ref` records the mapping — across all three write paths
>   (`push`/`hoist`/`land`), plus the read and coverage sides of the same `external_ref` mechanism.
>   Added **`REQ-BUP-054`** (the bead→issue **field mapping**, specified for the first time: title
>   and description verbatim, `type::`/`priority::` derived labels with the full numeric→word
>   table including the unmapped P0/P4 rows, `notes`/`design` explicitly not synced, `external_ref`
>   written back; the mapping existed nowhere in the repo and is reverse-engineered from two
>   measured samples) and **`REQ-BUP-055`** (bd **1.1.2 version floor** for `--external-ref` and for
>   `bd list --all --json` carrying `external_ref` — labelled an **assertion**, since it is the only
>   version verified rather than the version below which failure was shown, plus the measured
>   **omitempty** serialization caveat that forbids a key-presence read).
>   *Premise falsified first (plan-040 Issue 1.1, behind a scratch-write capability gate):* `gh
>   issue create --label <nonexistent>` **fails, exit 1, atomically** — no orphan issue — while `bd
>   github push` **creates the label on demand**. So restrict-and-drop is a **deliberate divergence**
>   from bd, not parity. Incidentally measured: bd's `--dry-run` also prints `✓ Pushed 1 issues`,
>   confirming that success string is not evidence of a write.
>   Added **`REQ-BUP-056`** + **`GR-BUP-008`** (**restrict-and-drop**: emit only labels that already
>   exist, never create one; every drop **reported** on the push preview naming the bead and the
>   label, because that report line — not memory — is the revisit trigger for a policy justified by
>   a population of **3 beads in 991**).
>   Revised **`REQ-BUP-030`** / **`GR-BUP-001`** — the never-hand-run invariant **survives, its
>   rationale replaced**: it was written against a *destructive* mechanism (a bare `bd sync`
>   re-imports every upstream issue as a duplicate bead and pushes the whole local DB), and a raw
>   `gh issue create` has no such blast radius. It now rests on **routing** — a hand-run write skips
>   enumeration, the create-vs-update decision, the label policy, and the fail-closed guard, and
>   **records no `external_ref`**, producing exactly the invisible issue #117/#131 exist to
>   eliminate. `protocols/UPSTREAM_TRACKING.md` revised and **re-stamped in the same change-set**
>   (`1.3.0` → `1.4.0`; the rule is hash-pinned, so a revision without a re-stamp is a preflight
>   `rule_drift` failure for every consuming repo). Also corrected a pre-existing misreference at
>   `skills/yf-beads-upstream/SPEC.md` §2.5, which attributed the hand-run-push anti-pattern to
>   `GR-BUP-002` (the token/inline-auth guardrail); the correct id is `GR-BUP-001`. #133 inherited
>   the same misnaming. Revised the requirements the swap **invalidates**, so nothing is implemented
>   against a requirement still mandating the deleted mechanism: **`REQ-BUP-040`** / **`GR-BUP-004`**
>   (GitHub-only — `--backend` and `BACKEND_AUTH` deleted; this **removes a stub surface** rather
>   than withdrawing support, since all three of REQ-BUP-040, GR-BUP-004 and `spec/backends.md`
>   REQ-BE-001 already said GitLab/Jira were unverified config-only stubs), **`REQ-BUP-031`** /
>   **`GR-BUP-002`** (the **auth model**: the skill no longer supplies a token inline — `gh` owns
>   its own credential store, so the skill handles no token at all; a behavior and invariant change,
>   which is why it lands in the requirements and not in a prose pass), **`REQ-BUP-041`**
>   (superseded — the scoped-push translation table is dead, retained as history because a future
>   "add a backend" still needs to know backend CLIs do not share a flag vocabulary),
>   **`REQ-BUP-051`** (the `push` verb and its `--apply`-only idiom survive; every clause beneath
>   them is replaced, and only **fail-closed** must not be read as relaxed), and **`REQ-BUP-052`**
>   (`closable`: one universe query and **zero** per-bead lookups as a scale-independent invariant,
>   plus the coarse-tracker gap discharged `yf-plan`-side). Added **`REQ-BUP-057`** (the gh-direct
>   core: `create_or_update` keyed on `external_ref`, a **locally rendered** preview absent
>   `--apply`, and **structural** verification — a returned issue URL, not a scraped success line)
>   and **`REQ-BUP-059`** (a removed `--backend` fails **informatively**, naming the removal and
>   pointing at #51/#52/#53). The two **sibling spec files** written entirely in `bd <backend>` terms
>   were updated in the same pass — `spec/safety.md` (`REQ-SAFE-001` no-bd-write / rationale
>   replacement, `REQ-SAFE-002` auth) and `spec/backends.md` (`REQ-BE-001` GitHub-only, `REQ-BE-002`
>   superseded-but-retained-as-history, `REQ-BE-003` two backend states). On the coverage side,
>   added **`REQ-PLAN-073`** (`yf-plan` stamps the coarse tracker URL onto the plan epic as
>   `external_ref` at §5.2a, immediately after `record-epic`, and again on the §5.2b resume as a
>   repair) — idempotent, non-clobbering, and **fail-soft at exit 0** on every failure path, because
>   it runs inside the pour sequence where "no tracker yet" is a normal state. This discharges
>   #117's coarse signal with **no `plans-root` coupling in either direction**: a stamped tracker is
>   just an ordinary mapped bead. Placement is a **correction to #131 as filed**, which specifies
>   §4.5 — impossible, since §4.5 runs at INTAKE, §4.6 states "No pour happened at intake", and
>   §5.2 owns the pour, so no epic id exists there to stamp. Live round-trip verified: after
>   stamping, plan-040's own tracker #138 appears in `closable` output for the first time.
>   Implementation: `upstream.py` gains `create_or_update` / `plan_write` / `apply_write` and loses
>   `BACKEND_AUTH`, `push_command_sequence`, `verified_push`, `parse_pushed_count`, `plan_push` and
>   the `--backend` flag; `cmd_push`/`cmd_hoist`/`cmd_land` all route through the one core, with
>   `hoist`/`land`'s destructive `bd close -r` stage now reachable only after every write verified.
>   Guarded by a new `check_gh_direct.py` acceptance check (code-vs-comment boundary, so the
>   comments recording *why* the mechanism was deleted survive) wired into both validation tiers.
> - **plan-041 (2026-08-16, #137 — the embed addition blind spot):** added
>   **`REQ-YF-EMBED-004`** — a build shall observe **additions** under `skills/`, so a newly added
>   file or directory reaches the embedded tree without a manual cache-bust. This is the first
>   requirement to constrain the *build's* observation of `skills/`, as opposed to the embedded
>   tree's contents (`-001`/`-002`) or its shape (`-003`). Prompted by a **measured** defect:
>   `skills/` sits outside the `yf/` package and `rust-embed` is a **proc macro**, so it emits no
>   `cargo:rerun-if-changed` and structurally cannot; its only staleness signal is the
>   `include_bytes!` dep-info the macro expands to, which tracks **file content** but never **the
>   directory listing**. Consequence, measured on this repo: a file *added* under `skills/` is
>   invisible to an incremental release rebuild (`Finished in 0.10s`, new file absent from the
>   binary), while content edits, deletes **and** renames all propagate correctly — the defect is
>   **addition-scoped**, not universal. A second, distinct defect shares the root cause: `build.rs`
>   never re-runs on a skills-only change, so `YF_GIT_HASH` / `YF_GIT_DIRTY` go stale even when the
>   embed is fresh. Both are closed by two lines in `yf/build.rs`
>   (`rerun-if-changed=../skills` plus `rerun-if-changed=.`); see the `REQ-YF-PRE-009` constraint
>   below for why the second line is load-bearing rather than decorative.
>   Resolved in the same pass a **pre-existing, undocumented conformance violation**:
>   `REQ-YF-EMBED-001`/`-002` say "from the binary alone", but `rust-embed` is declared **without**
>   `debug-embed`, so a **debug** binary reads `skills/` from disk at runtime and does not satisfy
>   them. Rather than silently tolerate it, §3.2 gains an explicit **profile carve-out**: `-001`/
>   `-002` bind the **release** artifact (what cargo-dist, Homebrew and `self install --from-build`
>   ship), the debug profile is a deliberate development-loop trade, and the new opt-in
>   **`embed-in-debug`** feature is the named mechanism by which conformance is *demonstrated* under
>   `cargo test`. `REQ-YF-EMBED-003`'s invariant needed no rewording, but its **enforcement
>   surfaces** did: the on-disk repo check and the baked-tree embed test are complementary, and the
>   on-disk check alone can be green while the shipping binary carries a stale payload.
>   **`REQ-YF-PRE-009` is not amended** — a **constraint** is recorded under it instead. The earlier
>   draft of this plan claimed PRE-009 carried a "deliberately emit no `rerun-if-changed`" stance;
>   it does not (`grep -n "rerun-if\|build\.rs" SPEC.md` returned nothing before this amendment).
>   That stance lived only in a `build.rs` **comment**, which cites PRE-009 because narrowing the
>   watch would break the `YF_GIT_DIRTY` value PRE-009's first short-circuit consumes. The comment
>   is rewritten in `build.rs`; the SPEC records the constraint, the residual `HEAD`-movement limit,
>   and the `cargo package` caveat. One believed-but-unmeasured claim was **refuted by probe** in the
>   same pass: `yf/profiles/`, the second `rust-embed` root, does **not** share the addition blind
>   spot — it sits *inside* the `yf/` package, so the implicit whole-package watch already covers it
>   (measured: 6.74 s recompile and the new profile present, against a 0.17 s no-op with the marker
>   absent for the `skills/` control). The `rerun-if-changed=.` line therefore **preserves** that
>   coverage rather than adding it, which makes it a regression guard rather than the "free coverage"
>   the plan had assumed.
> - **plan-043 (2026-08-16, #136/#140/#145 — the Phase 6.4 close-step contract):** amended
>   `spec/phases.md` **`REQ-COMPLETE-001`** from a *"fixed three-step order"* to an **extensible
>   ordered gate chain** defined by four named **ordering constraints** (read-before-write,
>   reconcile-before-verification, cascade-before-completion-gate, status-transition-last) rather
>   than by a step count, and de-positionalised its `Verification:` clause. The prior wording was
>   *count-bearing and positional*: it named an exact sequence and pinned complete-gate to an exact
>   slot, so **any** additional step made the requirement false the moment it landed. Three separate
>   issues each need to add a step there, so one amendment unblocks all three rather than each
>   re-amending the same sentence. Added **`REQ-COMPLETE-003`**, the **step convention** every chain
>   step honours: a single verdict envelope emitted as JSON **to stdout on every path** (stderr is a
>   contract violation, because SKILL.md's documented `X=$(…)` idiom captures stdout only); a
>   **tri-state** `verdict: pass|fail|inconclusive` with `passed` retained as a *derived*
>   compatibility key; the halting rule stated per state — **`inconclusive` never halts and is
>   always reported**; two step classes on the **halting axis alone** (`halting`/`advisory`); and
>   **remediation-kind** (`command|prose|adjudication`) as a **separate** attribute, with all six
>   combinations legal and **`halting` + `prose` explicitly permitted**. The axis split is
>   load-bearing, not tidiness: a single fail-loud/propose-only axis cannot classify a step that
>   must *enforce* while its remediation is *authoring* — the shape #145's escape capture needs —
>   and conflating the two is a category error. The tri-state is likewise load-bearing: the first
>   new halting step calls the network, so without `inconclusive` a GitHub outage would halt
>   completion on healthy work. Also required a **bounded timeout** on any network-calling step
>   (expiry → `inconclusive`), since an unbounded call can hang land-the-plane, which is worse than
>   either verdict. Corrected `spec/cli.md` **`REQ-CLI-016`**, which already *claimed*
>   `complete-gate` mirrors `close_cascade.py` while `complete-gate` in fact wrote its fail verdict
>   to **stderr** — a **measured live defect** that silently emptied the documented capture on
>   exactly the path that matters. The contract's enforcement is deliberately **mechanical rather
>   than prose**: `scripts/test_close_contract.py` **enumerates every script invocation** in
>   SKILL.md's §6.4 block from source (boundary `### 6.4` → next `###`), requiring each to be
>   envelope-capturing or on a named exempt list. Enumerating only the capture idiom would be
>   circular — it would see only steps *already shaped like* conformant ones, while the likeliest
>   non-conformance is an author who adds a step *without* the idiom, which takes less effort. This
>   is the plan's own thesis applied to itself: its central finding is that a prose instruction that
>   already existed (`reconciler.md` step 4) was skipped, so a contract enforced only by "a future
>   author will read it" would reproduce the defect it exists to fix.

> - **plan-043 Epic 3 (2026-08-16 — adjacent close-step defects):** three defects the §6.4 surface
>   audit surfaced, each of which would bite a chain step. Added **`REQ-PLAN-076`** — the reconcile
>   step bead shall be **re-derived from `bd`**, scoped to the plan epic, instead of read from a
>   shell variable bound only on the pour path, with the close's exit code checked. The variable is
>   assigned in exactly one place (§5.2a) and the **resume** branch never re-derives it, so any
>   resumed execution reaches the close step with it unset. The plan had recorded this as *inferred
>   from grep, not run live*, and required live verification before any fix — that verification
>   **confirmed the defect and corrected its severity**: `bd close` with no id argument does not
>   fail, it exits **0 and closes a different in-progress bead**, then reports success. The probe
>   closed the very bead running the probe. The resume path therefore does not skip the reconcile
>   close, it **silently closes the wrong bead and asserts success** — the same false-success shape
>   as the reconcile defect this plan exists to fix, one step away from it. Revised
>   **`REQ-PLAN-067`** so `close_cascade.py` **distinguishes "`bd` answered, bead absent" (a `fail`,
>   exit non-zero — a typo'd root otherwise walks an empty tree and reports a clean cascade over
>   nothing) from "`bd` did not answer" (`inconclusive`, reported, never halting). `_bd()` collapsed
>   `CalledProcessError`, `FileNotFoundError` **and** `OSError` into an empty list, so a typo, a
>   missing binary and a wedged Dolt DB were indistinguishable; without the split, fixing the
>   silent-pass would have converted a `bd` outage into a hard completion halt on healthy work.
>   Added **`REQ-DATA-017`** — `update-status` is **idempotent per (date, status token, message)**,
>   so the documented "resolve and re-run §6.4" recovery no longer appends a duplicate
>   `- complete:` bullet. Not cosmetic: `log.md` bullets are what the status, review-count and
>   grandfather-date parsers read. Idempotence suppresses re-emission, not history — a later date or
>   a different message still appends.
> - **plan-042 (2026-08-17, #157 — install-time sync for `self install` / `self update`):** five
>   SPEC items, all landed before any implementation. Revised **`REQ-YF-SELF-005`** from *"A
>   from-build install shall NOT auto-refresh"* to the **install-time sync contract**, specifying
>   `yf self update` and `yf self install --from-build` **separately** (they start from different
>   states, so an undifferentiated requirement would be untestable) and each over all three
>   sub-operations — skills, rules aggregate, harness config. The measured gap was **asymmetric**:
>   the vendor path deployed skills + rules but never config, the developer path deployed **none of
>   the three**. Exec-the-captured-path and fail-soft are preserved, with *fail-soft ≠ silent* made
>   explicit — the non-zero exit on the sync alone is required, since omitting it recreates the
>   silent-divergence defect the requirement now forbids. Added **`REQ-YF-SELF-008`** — the sync
>   contract surface: `--no-sync` on both commands (`--binary-only` retained as a documented alias);
>   a **config-home-directory** presence predicate that is explicitly **not**
>   `effective_harnesses`/`detect_from_env` (a binary on `PATH` is not evidence a harness was ever
>   configured) and must not regress the incumbent `~/.agents/{skills,rules}` signal; the consent
>   gate keyed on the settings **read classification** rather than `path.exists()` (a whitespace-only
>   file classifies absent and takes the consent-required branch); a consent flag **distinct from
>   `--yes`**, whose fan-out-bypass meaning is unchanged; `CI` suppression of the config half via
>   `--rules-only`; and the caller's obligation to treat **any** `tune.status` other than `"ok"` as a
>   failure — both `confirmation_required` **and** `refused`. That last clause is measured, not
>   defensive: `install --tune --json` without `--harness` writes **no rules and no config** and
>   **exits 0**, having written skill *bodies* first, so the exit code alone is not evidence of
>   success. Amended **`REQ-YF-TUNE-001`** so a profile entry may carry an optional
>   **`consent_required`** boolean (default `false`) — a schema change to a REQ that enumerates the
>   entry fields **exhaustively**, hence SPEC-first rather than an implementation detail. Consent is
>   **profile-declared, not key-path-matched**: a `permissions.*` prefix test is claude-code-specific
>   and would silently auto-apply codex's `approval_policy = "never"` and opencode's `permission.* =
>   "allow"` — the profiles' own rationale text already called both *"the analog of claude-code's
>   `bypassPermissions`"*, so the codebase knew they were one class and the predicate did not. Added
>   **`REQ-YF-TUNE-028`** — a **rules-only** tune mode, recorded as a **named exception to
>   `REQ-YF-TUNE-012`** (which requires tune own *both* sub-operations per harness); it is what makes
>   the sync's safe half (skills + rules) shippable independently of its consent-bearing half, and is
>   the mechanism implementing `CI` suppression. Amended **`REQ-YF-TUNE-023`** **honestly** rather
>   than by loophole: the sync path *may* write to detected harnesses without a per-run fan-out
>   prompt — the prohibited *outcome* does occur, and passing explicit `--harness` flags after
>   auto-detecting is that outcome by another name — so the requirement now names the exception and
>   its five compensating controls instead of claiming the prohibition is preserved intact.
>   Implementation lands in later epics; this entry records the SPEC-first Epic 0 amendment.
> - **plan-044 (2026-08-17, #159/#160/#156/#154/#155/#144/#142/#143):** the *silent-success*
>   defect clusters — an operation that reports success without verifying its own postcondition.
>   Added **`REQ-YF-DOCTOR-006`** (a `--repair` step shall re-run its own detecting predicate and
>   `FAIL` rather than report `ok`), **`REQ-YF-INSTALL-010`** (opt-in `install --prune`, fanning
>   out across every resolved destination, with a `--dry-run` preview that does not under-report),
>   **`REQ-YF-MARK-005`** (one residue ignore-list applied **symmetrically to four** surfaces —
>   tree hash, extra-deployed-files, prune, **and the embed exclusion list**; omitting the fourth
>   ships a developer's `.scratch/sandbox.env` inside the released binary),
>   **`REQ-YF-FLOW-008`** (`skills upgrade` is **rules-neutral**, leaving `tune` the aggregate's
>   sole writer), and **`REQ-YF-TUNE-029`** (a rules-side revert guard: record the aggregate's
>   `sha256` on every write, and on mismatch **keep and report** rather than delete).
>
>   **Amendments, stated rather than smuggled.** **`REQ-YF-MARK-004`** now names prune as
>   default-on for `upgrade` / opt-in for `install` over **one** implementation.
>   **`REQ-YF-FLOW-004`** is **scoped**: its *unconditional* drop/delete clause applies to
>   **`skills remove` only** — and its "no hand-edit tolerance" property is **explicitly carved
>   out on the `--revert` path** (D-9). That carve-out is recorded here because leaving it implicit
>   would leave FLOW-004 and the new TUNE-029 flatly contradicting each other; the reasoning is
>   that regenerating a section is cheap while deleting un-backed-up content is unrecoverable.
>   **`REQ-YF-TUNE-022`** now says plainly that its touched-since-tune guard governs **config**
>   keys and that the rules side does **not** inherit those semantics implicitly — TUNE-029 is
>   where they are specified.
>
>   **Declared deferral (D-11).** `REQ-YF-TUNE-020`'s **`agents`** rule-target row is **deferred**
>   to plan-044 Issue 2.2 and is deliberately **not** amended here. Epic 0 executes *before* that
>   issue's probe, so the correct destination is unknowable at this point, and
>   §3.10's own binding precedent — *a rule target shall NOT be a compiled-in guess* — forbids
>   filling it in speculatively. Issue 2.2 measures what the `agents` surface actually loads and
>   then owns the resulting edit under **either** outcome: add a `RULE_TARGETS` row *carrying that
>   evidence*, **or** declare `agents` a skills-only bare surface in `REQ-YF-FLOW-008`. The
>   deferral is logged so the post-Epic-0 SPEC edit is **declared, not smuggled**.
>
>   All five new requirements use bare *(testable)*; each is bridged by a temporary `coverage.rs`
>   `ALLOWLIST` row that is removed **in the same commit** as the `// REQ-…` tag that supersedes
>   it (D-7) — `coverage.rs` fails on a *stale* row as well as a missing test, so the bridge must
>   not outlive its tag by even one commit. Implementation lands in Epics 1–3; this entry records
>   the SPEC-first Epic 0 amendment.
> - **plan-051 (2026-08-23, #182/#184/#165):** yf-plan **review contract**. Added
>   **`REQ-AGENT-049`** (the adversarial red-team pass **shall be dispatched as a sub-agent**, not
>   performed by the main session — Phase 2 said *spawn* and Phase 3 said *perform*, so following
>   Phase 3 literally produced a self-review; it carries an explicit honesty clause that the
>   requirement constrains the specifying TEXT, never reviewer conduct, which has no exit code).
>   Amended **`REQ-AGENT-043`** and **`REQ-AGENT-045`** to scope read-only to *the repository under
>   review* and to **authorize the sandbox spike** — `red-team.md` never forbade building something
>   in `$(mktemp -d)` and running it, so #182 is a **clarification of under-specification, not a
>   reversal** (D-1); the carve-out is applied to both review agents together because `reviewer.md`
>   carried the identical sentence (D-8). All three `Verification:` lines are retargeted to the
>   **executable** whole-line-command shape (#165, scoped to this plan's own REQs — the corpus-wide
>   sweep stays open): `uv run skills/yf-plan/scripts/test_review_agent_contract.py` conjoined with
>   `grep -qF` literal/path pairs, so each line is run rather than read. Measured: 1 of 251
>   corpus `Verification:` clauses executes today. The three lines are RED from this commit until
>   the Epic 1/2 agent-file rewordings land — that is the intended SPEC-first order, not a defect.
>   Implementation lands in Epics 1–3; this entry records the SPEC-first Epic 0 amendment.
> - **plan-054 (2026-08-26, release readiness for v0.5.0):** the **harness-resolution** and
>   **read-set** amendments the v0.5.0 release depends on. Added **`REQ-YF-CLI-005`** — a top-level
>   `yf skill-dir <name>` verb resolving an installed skill across **all five** harness
>   destinations, with a three-valued 0/1/2 exit contract and an **existence-only** predicate
>   (it asserts a directory exists and asserts nothing about its contents). The verb exists because
>   the `SKILL_DIR` `find` idiom embedded in **19** files searches six roots, and neither
>   `~/.pi/agent/skills` nor `~/.config/opencode/skills` is among them: on a pi-only machine every
>   script-backed skill dies, and on a mixed machine it silently resolves to the *claude-code* copy
>   while the install reports success either way (EXP-002, reproduced live). Added
>   **`REQ-YF-TUNE-030`** — a per-profile `settings_read_layers` decoupling the **audit read set**
>   from the single **write target**, because `opencode` reads both `opencode.json` and
>   `opencode.jsonc` with `.jsonc` at **higher** precedence, so today's agreement is coincidence and
>   an audit narrower than the harness's own read set reports green over an override it cannot see
>   (EXP-003, which **refuted** the scoping hypothesis: `drift.rs` never opens a config file).
>   Added **`REQ-YF-EMBED-006`** — a decision-of-record that `allowed-tools` is **claude-only** and
>   is not a cross-harness scoping mechanism (zero occurrences in either the pi or the opencode
>   bundle format; ten shipped `SKILL.md` files carry it). Amended **`REQ-YF-TUNE-022`** with a
>   **symlink-aware delete**: revert's rules-side delete branch unlinks the *symlink* rather than
>   the content while reporting success (EXP-006), so it shall resolve the target or refuse and
>   report, and never claim a successful revert for a link it merely unlinked.
>
>   **The `find` idiom is REPLACED, not extended (D-1, amended at pass-1 C8).** EXP-001 measured
>   `find` exiting **1 on a missing root even when it found the target**, masked today by
>   `| head -1`. Widening the root list guarantees a missing root on most machines, and #203
>   proposes mandating `set -o pipefail` — so retaining the idiom as a fallback would ship a
>   resolver that fails precisely once the exit-code discipline this same release adds takes effect.
>   The fallback is a pure-bash existence loop over a cwd-inclusive superset of yf's own anchors.
>
>   Implementation lands in Epics 1–5; this entry records the SPEC-first Epic 0 amendment.

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
- **REQ-YF-CLI-003** *(testable)* *(amended plan-054 / #203)* every subcommand shall support
  `--json` for machine-readable output and shall exit non-zero on failure. The exit contract is
  **three-valued** and is the repo-wide convention, not a per-plan asset: **`0`** the assertion
  holds · **`1`** it does not · **`2`** the instrument **could not run** (INCONCLUSIVE). `2` is a
  statement about the *instrument*, never about the subject, and is deliberately distinct from
  `1` — a caller that collapses them cannot tell "failed" from "could not look".
  **An instrument shall not report failure in its OUTPUT and success in its EXIT CODE.** Measured
  five times in five separate instruments (#203), three of them tools this repo wrote: a scripted
  caller reads `$?`, sees `0`, and proceeds, so the failure is not merely missed — it is converted
  into a positive signal. Two corollaries, each costing one line: a shipped harness script sets
  `set -o pipefail` (without it a pipeline returns the LAST command's status, and a real exit `1`
  is read as `0`), and any instrument this repo ships has a **failure-path arm** in its tests —
  an instrument never observed failing is not known to be able to fail.

  The **bare** `*(testable)*` marker is retained deliberately: `coverage.rs`'s enforced set is
  bare-only, so folding the amendment note into the marker would drop this requirement out of the
  gate and strand its ALLOWLIST row — measured, while making this very edit.
- **REQ-YF-CLI-004** *(testable)* `yf version` shall print the semver version (and build metadata
  when available).
- **REQ-YF-CLI-005** *(testable)* `yf` shall expose a top-level **`skill-dir`**
  verb, `yf skill-dir <name>`, which resolves an installed skill directory across **every** harness
  destination `yf` itself installs to (`claude-code`, `codex`, `opencode`, `pi`, `agents`), in both
  `user` and `project` scope, and prints the resolved absolute path on stdout. Its exit contract
  shall be **three-valued**: **0** — exactly one directory resolved, path printed; **1** — no
  directory resolved (the skill is not installed at any known destination); **2** — the lookup could
  not be performed at all (INCONCLUSIVE: an unreadable root, an indeterminate scope). The resolution
  predicate is **existence-only**: the verb asserts that a directory of that name exists at a known
  destination and asserts **nothing** about its contents — it performs no marker-file check, no
  `SKILL.md` presence check, and no integrity or version verification. A caller needing those
  guarantees shall check them itself.

### 3.2 Embedding (`REQ-YF-EMBED`)

> **Profile carve-out (added plan-041).** `REQ-YF-EMBED-001` and `-002` bind the **distribution
> artifact** — any `--release` build, which is what `cargo-dist`, Homebrew, and `yf self
> install --from-build` promote. They do **not** bind the default `--debug` build. `rust-embed` is
> declared **without** its `debug-embed` feature, so a debug binary resolves embedded paths from
> `skills/` **on disk at runtime**: it does not satisfy "from the binary alone" and would fail
> - **plan-047 (2026-08-19, #175):** mechanically parseable artifact documents — added
>   `REQ-DATA-018` (stable `SC<n>[a-z]` criterion ids, insertable without renumbering, plus the
>   fixed `Discharged-by` / Risks table columns), `REQ-DATA-019` (a closed gate `Blocks:` referent
>   alphabet), `REQ-DATA-024` (the `document_types/<type>.toml` schema format and the
>   `PASS|FAIL|INCONCLUSIVE` linter-engine contract), `REQ-DATA-025` (the hash-neutral normalizer
>   postcondition), `REQ-DATA-026` (pour fidelity — `plan_issue` bead metadata plus a comparator
>   close gate), `REQ-DATA-027` (the `source:`/`retrieved:` vendored-content marker), and
>   `REQ-DATA-028` (`update-status` refuses `approved` on a red `ready-check`); **amended
>   `REQ-PORT-006`** so the count-equality invariant keys on red-team pass presentations rather than
>   on every `log.md` `review:` bullet. Also fixed `yf-plan` `SKILL.md`'s plan.md-structure block —
>   measured the single most-drifted artifact in the investigation — and made it **generated** from
>   `_shared/plan_template.py` through `sync.py`'s marker fence, so it cannot drift from
>   `seed_plan_md` again.
> - **plan-050 (2026-08-20, #178/#179/#180/#181/#186/#187 — six mechanical process defects):**
>   added **six** requirements, one per behaviour change, SPEC-first ahead of every implementing
>   commit. `REQ-PLAN-077` — resolving the start gate closes the wrapper task in the **same step**
>   with a generated `close_reason`, via one verb, and explicitly **not** by weakening
>   `close_cascade.py`'s `_bead_is_terminal` (measured: 49 of 49 wrappers ever poured were closed
>   by hand, with 29 distinct improvised reasons). `REQ-COMPLETE-004` — `close-reconcile-step`
>   asserts the reconcile gate is resolved first **with an exit code**, and SKILL.md §6.4 must
>   **read** that exit code, which it did not: the block captured the verb with `RSTEP=$(…)` and
>   only echoed it. `REQ-DATA-061` — `doc_lint.py` gains a **`classify` preflight mode** emitting
>   a `class` of `selected | empty | not-selected | no-such-path`, closing #181's silent green
>   without touching the lint's own reporting (three earlier scopes were each refuted by
>   measurement, all three because they mutated it). `REQ-CLI-025` — `plan_manager.py grant`
>   generates the upstream-write authorization proposal from the Upstream Issues table, reading
>   the **same** per-disposition requirement table as `_verify_row`. `REQ-DATA-062` — title
>   fidelity: an extracted title equals its source span verbatim, captured by **offset-slicing**
>   the unmasked line, never by re-matching against it. `REQ-DATA-063` — the issue `detail` field,
>   carrying continuation prose minus the parsed sub-key bullets, so §5.2a's mechanical pour can
>   populate `--description`.
>
>   Also **amended `REQ-DATA-024`**, scoped to its **exit-contract sentence only**. It read that
>   the contract is "binary at every binding point"; `classify` gives the same executable a second
>   `0/1/2` vocabulary, so the sentence became false on landing. The **verdict** vocabulary is
>   untouched and remains closed — `classify` emits a `class`, never a verdict. The same sentence
>   is **restated in three places outside the spec** and all three moved with it:
>   `_shared/doc_lint.py`'s module banner, its vendored copy
>   `skills/yf-plan/scripts/doc_lint.py`, and `_shared/document_types/README.md`. Amending the
>   spec alone would have left three documents agreeing with each other and none agreeing with the
>   code — the plan-049 D-9 shape that `DRIFT-CHECK.md`'s fixed-authority `e-doclint-spec` edge,
>   which names the engine's own module banner explicitly, exists to catch.
> outside a repo checkout. That is a deliberate development-loop trade (a skills edit costs no
> recompile), and it is recorded here rather than left as a silent latent violation. The
> **`embed-in-debug` cargo feature** (`yf/Cargo.toml`, opt-in, added plan-041) re-enables baking
> under the debug profile and is **how `-001`/`-002`/`-003` conformance is demonstrated under
> `cargo test`** — a CI job runs `cargo test --workspace --features yf/embed-in-debug` so the
> embed tests assert against the **baked** tree rather than the on-disk one. The feature ships
> **opt-in, not on by default**: enabling it by default would import the `REQ-YF-EMBED-004`
> addition defect into the dev loop (measured: profile-independent, it reproduces in debug with
> `debug-embed` on) while costing the zero-rebuild skills-edit loop.

- **REQ-YF-EMBED-001** *(testable, carve-out plan-041)* the binary shall embed the entire `skills/`
  tree at build time (no network or repo clone required to install). Binds the release profile; see
  the profile carve-out above.
- **REQ-YF-EMBED-002** *(testable, carve-out plan-041)* `yf` shall enumerate embedded skill names
  and per-skill file lists, and read any embedded file, from the binary alone. Binds the release
  profile; see the profile carve-out above.
- **REQ-YF-EMBED-003** *(testable)* every embedded `skills/*/SKILL.md` and `skills/*/agents/*.md`
  shall carry a well-formed, **terminated** YAML frontmatter block — an opening `---` on line 1, a
  closing `---` delimiter, and a body that parses as YAML. A repo check shall enforce this across
  the whole `skills/` tree and run in the fast and full validation tiers. Rationale: the block is
  the file's only machine-readable metadata (a skill's `name`/`description` triggers, an agent's
  `name`/`role`/`stance`), and a corrupted delimiter fails **silently** — the file still renders as
  markdown while its metadata stops parsing. The observed corruption replaced a closing `---` with
  `:--`, a GFM table-alignment marker, consistent with a table-alignment autofix applied to a
  frontmatter delimiter; it went undetected until a human read the file. The invariant is repo-wide
  rather than per-skill because the failure mode is identical in every skill and a rule homed under
  one skill's key would be undiscoverable from the others.
  **Two enforcement surfaces, not one (clarified plan-041).** The requirement is stated over the
  **embedded** files, and it is enforced from both sides: (a) the repo check
  (`scripts/check_frontmatter.py`, fast + full tiers) walks the **on-disk** `skills/` tree, which is
  the authoring-time guard and the only one that runs on every edit; and (b) the embed tests, when
  run under `--features yf/embed-in-debug`, assert the same invariant against the **baked** tree.
  These are complementary rather than conflicting: (a) catches a bad file the moment it is written,
  (b) catches a baked payload that disagrees with the tree it was built from — the failure class
  `REQ-YF-EMBED-004` addresses. No wording change to the invariant itself was required; only the
  enforcement surface needed stating, because (a) alone can be green while the shipping binary
  carries a stale payload.
- **REQ-YF-EMBED-004** *(testable, added plan-041)* a build shall observe **additions** under
  `skills/`: a file or directory newly added to the tree shall reach the embedded payload without
  a manual cache-bust (no `touch`, no `cargo clean`), on an **incremental** rebuild of an
  already-built target directory. Rationale: `skills/` lives outside the `yf/` package, and
  `rust-embed` is a proc macro that cannot emit `cargo:rerun-if-changed` — its only staleness
  signal is the `include_bytes!` dep-info it expands to, which tracks each embedded file's
  **content** but never the **directory listing**, so cargo has no reason to re-expand the macro
  when a *new* path appears. Measured: content edits, deletes and renames propagate correctly;
  additions do not. The requirement is stated over the **build**, not over `yf`'s runtime, because
  the failure is invisible from the binary alone — the embedded tree is internally consistent, it
  is merely one file short. Verification shall exercise the **addition** case specifically: a
  content-edit test passes with the defect present and is therefore not a guard for this
  requirement.
- **REQ-YF-EMBED-005** *(testable, added plan-053 / #210)* every **script path referenced in a
  skill instruction document** shall resolve under an installed `SKILL_DIR`. The scope is the
  instruction surface a *consumer* reads — `skills/*/SKILL.md`, `skills/*/README.md`,
  `skills/*/agents/*.md`, `skills/*/protocols/*.md`, `skills/*/reference/*.md` — and a reference
  is any invocation naming a script (`uv run …`, `bash …`, `python …`) inside a shell fence. The
  path shall be **rooted at `${SKILL_DIR}/`** (or another consumer-resolvable root), never at a
  path that exists only in *this* repository's working tree. A repo check shall enforce this
  across the whole `skills/` tree and run in the **fast and full** validation tiers, with its own
  path in scope so that **deleting** the check fires it.
  The `_shared/` prefix is the measured instance. `_shared/` is a directory in this repository; it
  is not one of the six roots the `SKILL_DIR` resolver searches, so an operator following such a
  line verbatim in any other repository gets a file-not-found. A second, distinct failure shape
  shares the requirement: a path may be *correctly rooted* and still name a script that was never
  vendored into the skill at all (`missing-in-repo`) — `pour_fidelity.py` had **no vendored copy**,
  so rewriting its `SKILL.md` line alone would have produced a rooted path that still did not
  resolve. Both shapes are in scope.

  The check shall carry the standard three-valued exit contract (`0` clean, `1` violations, `2`
  the check could not run), emit `--json`, offer an `--all` mode, carve out **illustrative** (as
  opposed to executable) invocations, honour an explicit
  `<!-- skill-script-refs: allow <why> -->` opt-out marker for deliberate external references,
  and exclude `skills/*/scripts/fixtures/**`, which holds corpus fixture documents carrying
  arbitrary invocations by design.

  **It is a repo-level guard (`scripts/`), not a shipped skill script** — the precedent is
  `scripts/check_frontmatter.py`, and shipping the check *inside* a skill would make it
  self-referential. Rationale: this is the **second** instance of one mechanism — plan-050 fixed
  exactly this break for `plan_extract.py` and did not close the class, so the remedy is the one
  plan-052's `RE-002` prescribes: when successive fixes to one defect are each refuted by the same
  mechanism, stop iterating on the fix and put a check in front of the failing component. The
  justification is a **mutation**, not volume: re-inserting plan-050's original bug makes the
  check go red, which is the evidence that it would have caught the first instance. False-positive
  surface was measured at **zero** over the tree at authoring time.

- **REQ-YF-EMBED-006** *(added plan-054, decision-of-record)* the `allowed-tools` frontmatter key in
  a shipped `SKILL.md` is **claude-code-only** and shall **not** be treated as a cross-harness tool
  scoping mechanism. Measured: `allowed-tools` occurs **zero** times in either the `pi` or the
  `opencode` skill bundle format, while **ten** shipped `SKILL.md` files carry it. A skill that
  relies on `allowed-tools` to constrain what it may do is therefore **unconstrained** under every
  harness but claude-code. The key is retained for claude-code's benefit; no requirement in this
  spec shall depend on it for a portability, safety, or scoping guarantee, and any such guarantee
  shall be specified by a harness-independent mechanism instead.

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

- **REQ-YF-INSTALL-010** *(testable)* `yf harness skills install` shall accept an **opt-in
  `--prune`** flag that removes deployed files absent from the embedded tree, subject to the
  ignore-list of `REQ-YF-MARK-005`. Prune shall fan out across **every** resolved destination
  (`REQ-YF-INSTALL-002`), and `--dry-run --prune` shall report the exact per-destination set it
  would remove — a preview that under-reports is a defect, not a convenience. Prune operates on
  **files**, so a hand-added skill *directory* survives. Pruning is **default-on for `upgrade` and
  opt-in for `install`** (`REQ-YF-MARK-004`), sharing **one** implementation. `--prune` shall
  **not** be wired into the `REQ-YF-SELF-005` install-time sync, which would otherwise delete
  operator files on every `yf self install`.

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
- **REQ-YF-FLOW-004** *(testable)* the aggregate is a fully `yf`-managed
  artifact (S3): acted-on sections are **always** rewritten to the embedded source (no `--force`
  gate). The **unconditional drop/delete** clause is scoped to **`yf harness skills remove`**: it —
  and only it — drops the named skills' sections **unconditionally** (even a drifted section) and
  deletes `YOSHIKO_FLOW.md` when its last section is removed (S6). **Carve-out (plan-044, D-9):**
  the "no hand-edit tolerance" property does **not** extend to the `--revert` path, which is
  explicitly **conservative-keep** on a hand-edited aggregate per `REQ-YF-TUNE-029`. This is a
  narrow, deliberate grant of hand-edit tolerance on one path, stated here so the two requirements
  do not contradict each other: rewriting a section the operator can regenerate is cheap; deleting
  a file whose pre-tune content `yf` never backed up is unrecoverable.
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

- **REQ-YF-FLOW-008** *(testable)* `yf harness skills upgrade` shall be **rules-neutral**: it
  shall write **no** `YOSHIKO_FLOW.md` on any harness, leaving `yf harness tune` as the aggregate's
  **sole writer** (`REQ-YF-FLOW-007` already imposes this on `install`; upgrade is the remaining
  second writer). Two writers of one path is the defect: a guard or managed block added by `tune`
  is clobbered by the other writer. **`yf harness skills remove` is explicitly NOT rules-neutral**
  and retains its rules write — `REQ-YF-FLOW-002` reconcile-prunes on the **embedded** set, so
  without `remove`'s write nothing would ever drop a removed skill's section and a later `tune`
  would retain it. *(Honest limit: `remove` writes the **skills-sibling** `rules/` dir, which
  coincides with the tune-managed surface **only on claude-code**; on the other four harnesses it
  prunes a file nothing reads while the real section survives. That residual is recorded as a
  follow-on, not claimed fixed.)* Removing upgrade's write is a **behavior change**, not a pure
  removal: the doctor/preflight rule-candidate resolution shall be reconciled so non-claude
  harnesses do not regress to `rule_missing`.

  **The `agents` surface is SKILLS-ONLY** *(plan-044 Issue 2.2, discharging the Issue 0.1
  deferral with measurement rather than a guess)*. `agents` shall receive **skill bodies only**
  and **no rules file at any target**; it gains no `REQ-YF-TUNE-020` rule-target row, and
  `~/.agents/rules` is not a rule-candidate location. Evidence: `agents` is absent from the
  harness **detection** table (never auto-detected), carries **identical** skills subpaths to
  `codex`, is referred to in-code as *"the `agents` alias"* of the shared `.agents` dir, and has
  **no binary** that could load a rules file; on a machine running `yf` with skills deployed to
  `~/.agents/skills/`, **neither** `~/.agents/rules/` **nor** `~/.agents/AGENTS.md` exists. The
  skills installed there are consumed by **codex**, whose rules already deploy to
  `~/.codex/AGENTS.md` — so declaring `agents` skills-only removes a write that served no reader
  rather than orphaning one. Reversing this requires first-party evidence of an actual reader,
  carried on the row, exactly as pi's target does (§3.10).

### 3.4 Integrity marker & up-to-date detection (`REQ-YF-MARK`)

- **REQ-YF-MARK-001** *(testable)* `yf` shall compute a per-skill **tree hash** = SHA256 over each
  file (sorted by relpath) as `relpath-bytes ++ file-bytes`, with `SKILL.md` **marker-stripped
  before hashing**, so a deployed marked copy hashes identically to the embedded source.
- **REQ-YF-MARK-002** *(testable)* on install/upgrade `yf` shall inject a single marker into the
  deployed `SKILL.md` after the YAML frontmatter: `<!-- yf-skills: v=<version> tree=<sha256> -->`.
- **REQ-YF-MARK-003** *(testable)* `yf skills status` shall report per skill: `installed`,
  `up-to-date` (deployed marker hash == embedded tree hash), `complete` (all embedded files
  present), `unmodified` (recomputed deployed hash, marker-stripped, == embedded).
- **REQ-YF-MARK-004** *(testable)* `yf skills upgrade` shall rewrite files,
  re-inject the marker, and **prune** deployed files absent from the embedded tree. Pruning is
  **default-on for `upgrade`** and **opt-in for `install`** (`--prune`, `REQ-YF-INSTALL-010`); both
  verbs shall share **one** prune implementation and honour the same `REQ-YF-MARK-005` ignore-list,
  so prune and the tree hash can never disagree about what counts as a deployed file.
- **REQ-YF-MARK-005** *(testable)* `yf` shall carry a single **ignore-list** of generated/residue
  paths — at minimum `__pycache__/**`, `*.pyc`, `.pytest_cache/**`, `.DS_Store`, `**/.scratch/**`
  and `**/test-harness/topology.txt` — and shall apply it **symmetrically** to **all four** surfaces
  that enumerate skill files: the tree-hash walk (`REQ-YF-MARK-001`), the extra-deployed-files
  computation, the prune walk (`REQ-YF-MARK-004` / `REQ-YF-INSTALL-010`), and the **embed
  exclusion list** (`REQ-YF-EMBED`). Applying it to only the read-side surfaces is non-conformant:
  an unexcluded residue file is **baked into the released binary** and shipped to every user. The
  list is self-consistent by construction — a file excluded from the embed becomes an *extra
  deployed file*, which the same list then spares from prune.

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
  `.yf/<short>/` state dir. `read_config` shall resolve **three** tiers and merge them
  **key by key**, the highest tier present winning each key (revised plan-037):
  1. the canonical local override `.yf/<short>/config.local.json` — gitignored, machine-specific;
  2. the canonical **committed** `.yf/<short>/config.json` — the shared, repo-carried tier
     (REQ-YF-PRE-004a);
  3. the legacy root dotfile named by the skill's `config_basename` descriptor field
     (e.g. `.yf-plan.local.json`) — a read-time fallback that is never removed.

  Merge is **per key**, not whole-file first-match: a local override setting one key shall not
  mask the committed tier's other keys. With a single tier present the two semantics coincide, so
  the revision is backward-compatible.
- **REQ-YF-PRE-004a** *(testable, plan-037)* the **committed** config tier
  `.yf/<short>/config.json` shall hold decisions that are properties of the **repository** rather
  than of a checkout — layout being the motivating case (`plans-root` / `incubator-root`,
  REQ-PLAN-079). It is the single exception to the otherwise fully-ignored `.yf/` tree: the
  gitignore shall keep `/.yf/` ignored and carve out **only** `.yf/<short>/config.json`, never
  state and never a `*.local.json`. Both the kernel (`preflight.rs`) and any skill-side reader
  (`plan_manager.py`) shall implement the same three-tier merge — two readers disagreeing about
  precedence is the drift REQ-YF-PRE-004 exists to remove.

  The **short name** is resolved by a single centralized `resolve_skill` (skill-arg → `(dir,
  short)`); `migrate` shall consume the **same** resolver so the state dir it writes and the state
  dir preflight reads agree (fixing the historical full-name `.yf/yf-plan/` vs short-name
  `.yf/plan/` disagreement). The state short-name and the config **basename** are distinct axes:
  standardizing the state short-name shall **not** misroute config resolution.
- **REQ-YF-PRE-005** *(testable, revised plan-037)* the kernel shall scaffold a single top-level
  gitignore anchor (`/.yf/`) idempotently — one anchor covers both config
  (`.yf/<short>/config.local.json`) and state (`.yf/<short>/preflight.json`); no per-skill
  top-level dotfile anchors. It shall additionally scaffold the **carve-out** that makes the
  committed tier (REQ-YF-PRE-004a) committable: `!/.yf/`, `!/.yf/*/`, `/.yf/*/*`,
  `!/.yf/*/config.json`, emitted **in that order after** `/.yf/`. Git does not descend into an
  ignored directory, so the two directory un-ignores are required before the file rule, and the
  `/.yf/*/*` re-ignore keeps everything else — all state, every `*.local.json` — ignored. Scaffold
  changes are picked up by an existing repo via a `SCAFFOLD_VERSION` bump.
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
  **Build-observation constraint on the `YF_GIT_DIRTY` input (recorded plan-041, #137).** This
  requirement is **not amended** — its dirty-build short-circuit stands unchanged. What plan-041
  records is that PRE-009 *consumes* `YF_GIT_DIRTY`, a value stamped by `yf/build.rs`, and therefore
  **constrains how `build.rs` may declare its watches**. Emitting **any** `cargo:rerun-if-changed`
  disables cargo's implicit whole-package watch; a `build.rs` that emitted only
  `rerun-if-changed=../skills` would stop re-running on changes under `yf/` itself, leaving
  `YF_GIT_DIRTY` stale and this short-circuit reading a value that no longer describes the tree.
  Measured: with only the `../skills` line, `touch yf/src/main.rs` left `build.rs` un-re-run. The
  companion `cargo:rerun-if-changed=.` line re-declares the package directory and restores that
  coverage — it is **load-bearing, not decorative**, and exists precisely to hold this requirement's
  input honest. Three consequences are recorded rather than left to be rediscovered:
  - **Residual limit (not closed).** The two lines make the stamp current for changes under `yf/`
    and `skills/` **only**. `HEAD` moving for any other reason — a docs-only commit, a `SPEC.md`
    commit, a `git checkout`, a rebase — touches nothing watched, so an incremental build can still
    carry a stale hash. Watching `.git/` was considered and rejected. The `yf --version` vs `HEAD`
    check remains the only detector for this residue, which is why it survives in `AGENTS.md` as a
    one-line sanity note.
  - **`cargo package` / `publish` caveat.** `../skills` does not exist inside a packaged crate, and
    cargo treats a missing `rerun-if-changed` path as **permanently dirty** (the build script
    re-runs every time). Harmless today: `#[folder = "../skills"]` already precludes publishing this
    crate. Recorded so a future packaging attempt is not mystified by it.
  - **`yf/profiles/` — the second `rust-embed` root — is NOT affected, measured.**
    `yf/src/cmd/harness/profile.rs:26` declares `#[folder = "profiles"]`, and plan-041 initially
    *believed* it carried the same addition blind spot as `skills/`. **A probe refuted that.**
    Because `yf/profiles/` sits **inside** the `yf/` package, cargo's implicit whole-package watch
    already observes additions there: adding a new `yf/profiles/*.json` to a warm release target
    recompiled the crate (6.74 s, not a 0.27 s no-op) and the new profile **reached the embedded
    payload** — whereas the identical control against `skills/` was a 0.17 s no-op with the marker
    **absent**. The blind spot is specific to `skills/` *because it is outside the package*. This
    inverts the significance of the `.` line for this root: it is not free *new* coverage, it is
    what **preserves existing** coverage that emitting `../skills` alone would have silently
    removed — a regression, not an improvement, and one no test would have caught.
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

- **REQ-YF-DOCTOR-006** *(testable)* every `yf doctor --repair` step shall **verify its own
  postcondition** before reporting success: after applying a repair, the step shall re-run the
  read-only predicate that detected the condition and report `FAIL` (non-zero, surfaced under
  `REQ-YF-DOCTOR-002`) when the predicate still holds. A repair step shall **never** report `ok`
  on the basis of having *attempted* the repair. Concretely, the `--remove-remote` step shall
  re-run `has_local_only_remote` after applying and fail when a Dolt remote survives; and an
  **underivable or ambiguous** Dolt repo root shall propagate as an error (`REQ-BINIT-026`) rather
  than being swallowed into a silent `ok`.

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
- **REQ-YF-SELF-005** *(testable, revised plan-042)* both install paths shall leave the machine's
  **deployed** surface matching the binary they just promoted, by running an **install-time sync**.
  The two commands are specified **separately** because they start from different states, and each
  is specified over all **three** sub-operations (skills, rules aggregate, harness config):

  - **`yf self update`** (vendor path) — unless `--no-sync` (or its retained alias `--binary-only`),
    after a successful vendor update `yf` shall deploy **skills**, the **rules aggregate**, and
    **harness config** (subject to the `REQ-YF-SELF-008` consent gate) for every harness the sync's
    presence predicate selects. This replaces the former once-per-`--surface` refresh, whose
    `--surface claude` / `--surface agents` alias spanned only two of the five supported harnesses.
  - **`yf self install --from-build`** (developer path) — unless `--no-sync`, a from-build install
    shall run **the same sync**, via the same single shared implementation. This **supersedes** the
    former *"A from-build install shall NOT auto-refresh"*, which is the defect plan-042 exists to
    fix: the from-build path previously deployed none of the three.

  In both cases the sync shall exec the **swap-destination** binary (the path captured before the
  swap, NOT a post-swap `current_exe()`), because the running binary is precisely the one that may
  carry a stale embed. A sync failure shall be **fail-soft**: reported with the manual re-run
  command, exiting non-zero on the sync alone, **never** rolling back the (successful) swap.
  Fail-soft is **not** silent — the non-zero exit is required, since a silent sync failure recreates
  the binary/deployment divergence this requirement now forbids.
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
- **REQ-YF-SELF-008** *(testable, plan-042)* the `REQ-YF-SELF-005` install-time sync shall expose the
  following contract surface, shared by **one** implementation across both commands:

  - **Opt-out.** `--no-sync` shall be accepted on **both** `yf self install --from-build` and `yf
    self update`, suppressing all three sub-operations. `--binary-only` shall be **retained as a
    documented alias** on `yf self update` so existing usage does not break. The opt-out shall land
    **with or before** the sync wiring it guards — never trailing it.
  - **Presence predicate.** The sync shall select its target harnesses by an existing **config home
    directory**, **not** by a binary on `PATH` (i.e. **not** `effective_harnesses` /
    `REQ-YF-INSTALL-009`'s `detect_from_env`). A machine carrying a harness binary but no config home
    has never been configured, and creating one as a side effect of promoting a binary is precisely
    the surprise the consent gate exists to prevent. The predicate shall be defined explicitly for
    every supported harness id, and shall not regress the incumbent `~/.agents/{skills,rules}` signal
    — a machine with `~/.agents/skills` and no `~/.codex` shall still be refreshed.
  - **The consent gate.** The config sub-operation shall apply automatically **only** when the target
    config file already **exists** *and* the **computed change set** contains no entry declaring
    `consent_required: true` (`REQ-YF-TUNE-001`). Otherwise the sync shall print the config **delta**
    — the per-key change set, not merely the affected file paths — and require an **explicit consent
    flag**. Existence shall be determined by the settings **read classification**, not by
    `path.exists()`: a whitespace-only or otherwise unparseable file classifies as absent and shall
    take the consent-required branch.
  - **A distinct consent flag.** The consent flag shall be **separate from `--yes`**, whose existing
    meaning (bypass the `REQ-YF-TUNE-023` multi-harness fan-out prompt) is preserved **unchanged**.
    `--yes` alone shall **never** authorize a `consent_required` write. Two gates that authorize
    materially different things shall not share one token.
  - **`CI` / non-interactive suppression.** Under `CI` or a non-interactive context (reusing the
    `REQ-YF-SELF-006` precedent), the **config** sub-operation shall be suppressed while **skills and
    the rules aggregate still deploy** — implemented by emitting `--rules-only`
    (`REQ-YF-TUNE-028`), not by a second suppression mechanism. Without this the consent flag could
    never be satisfied non-interactively and the sync would hang or hard-fail in CI.
  - **Non-`ok` tune status is a caller-side failure.** The sync shall treat **any** `tune.status`
    other than `"ok"` as a **failure** — explicitly including both `"confirmation_required"` **and**
    `"refused"` (the malformed-settings fail-safe path). Both return `Ok(())` and exit 0 while
    writing **no rules and no config**, so an exit code alone is not evidence of success. Skill
    *bodies* are written first in that case, which is what makes the false success plausible.

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

- **REQ-YF-TUNE-001** *(testable, revised plan-042)* `yf` shall embed a **machine-readable settings
  profile** as the
  single source of truth for the recommended Claude Code baseline. Each profile **entry** shall
  carry: a JSON **path** (e.g. `permissions.deny`, `todoFeatureEnabled`), a recommended **value**, a
  **kind** (`scalar` or `set-valued`), a one-line **rationale**, and an optional
  **`consent_required`** boolean (**default `false`** when absent, so every existing entry and every
  existing profile file remains valid unchanged). An entry with `consent_required: true` declares
  that applying it materially escalates the operator's security posture, and is the sole signal the
  `REQ-YF-SELF-008` consent gate tests the computed change set against.

  The flag is **profile-declared rather than key-path-matched** by design. A syntactic
  `permissions.*` prefix test is claude-code-specific: the same class of autonomy lever is
  `approval_policy = "never"` on codex and `permission.* = "allow"` (singular) on opencode, neither
  of which matches that prefix — so a prefix test would auto-apply a blanket-allow on two of the
  three config-bearing harnesses with no consent. Declaring the requirement **per entry** is
  self-maintaining: a newly added lever declares its own consent requirement instead of relying on a
  prefix that only ever matched one harness. Boolean **polarity** is encoded
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
  **yf-up7s**. Pi **config** remains deferred (`REQ-YF-TUNE-017`). **Delivered (plan-034):** the
  per-harness `yf doctor` settings-drift axis (the `REQ-YF-TUNE-009` analog for codex/opencode), plus
  a new per-harness managed-block drift check, are now **delivered** by `REQ-YF-TUNE-026` (the
  follow-on bead this note deferred is closed). The `REQ-YF-TUNE-008` analog (a per-harness
  `docs/recommended-settings.md` reference-baseline drift test) remains out of scope — those harnesses
  carry per-harness prose only, no reference-baseline block. The plan-032 Claude-Code drift/doctor
  axes remain in force unchanged.
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
- **REQ-YF-TUNE-022** *(testable, plan-033, amended plan-044)* `yf harness tune --revert` shall reverse **only** yf's
  own additions recorded in the ownership manifest (`REQ-YF-TUNE-021`): it restores each recorded
  prior scalar value (or removes a key that had none), removes only the set elements yf unioned in
  (leaving operator entries), and removes the rule managed blocks (leaving surrounding prose). Revert
  shall apply a **touched-since-tune guard**: before reverting a key, it compares the key's current
  on-disk value to the recorded **yf-written** value; if they differ (an operator hand-edited it
  since the tune), the key is **conservative-kept and reported**, never clobbered. Revert shall be
  idempotent, fail-safe on a malformed target, and preserve the `Agent`-never-denied invariant.
  The touched-since-tune guard described above governs **config** keys; the **rules** side has its
  own guard with the same conservative-keep semantics, specified separately as `REQ-YF-TUNE-029`.
  Revert's config half is manifest-driven and per-key; its rules half shall not be assumed to
  inherit those semantics without that requirement.
  **Symlink-aware delete (amended plan-054, EXP-006).** Where revert's rules half takes its
  **delete** branch, it shall resolve the target before unlinking. When the recorded rule target is
  a **symlink** — the shape a surface-symlinked install produces — unlinking the link removes the
  operator's *pointer* while leaving the content orphaned, and today that path **reports success**
  while having reverted nothing at the real location. Revert shall therefore either operate on the
  **resolved** path or **refuse and report** the symlink, and shall never report a successful revert
  for a target it only unlinked at the link.
- **REQ-YF-TUNE-023** *(testable, plan-033)* `--tune` on `yf harness skills install` shall remain an
  **opt-in bridge** — install and tune stay **separable**: without `--tune`, install is skills-only
  and reports that tuning is available (`REQ-YF-INSTALL-008`); with `--tune`, the bridge also runs
  `yf harness tune` for the acted-on harnesses. The canonical bridge is `yf harness skills install
  --tune` (the deprecated `yf skills install --tune` alias also works during deprecation). With
  **no** `--harness`, `--tune` shall provision every **auto-detected** harness (`REQ-YF-INSTALL-009`)
  end-to-end; the no-`--harness` multi-harness auto path shall **print the resolved target set and
  require confirmation, or run dry-run-then-apply**, before writing config/rules — it shall **never**
  fan out writes to all detected harnesses unconfirmed.

  **Named exception (plan-042): the install-time sync.** The `REQ-YF-SELF-005` sync path **may write
  to multiple detected harnesses without a per-run fan-out prompt**. This is stated plainly rather
  than framed as compliance: the sync passes an explicit `--harness` per harness, which bypasses the
  no-`--harness` confirmation branch by construction, so the *prohibited outcome* — unconfirmed
  writes to a set of auto-detected harnesses — does occur, and calling that "a SPEC-compliant call
  shape" would be loophole-lawyering. The prohibition above is **not** preserved intact for this
  path; it is superseded by the following **compensating controls**, which are what make the
  exception acceptable:

  1. **Explicit per-harness selection** — the sync resolves its own target set via the
     `REQ-YF-SELF-008` presence predicate (an existing config **home directory**, not a binary on
     `PATH`) and passes each id explicitly; it never falls through to tune's hard-coded default.
  2. **The consent gate** (`REQ-YF-SELF-008`, `REQ-YF-TUNE-001` `consent_required`) — no
     consent-declaring entry is applied, and no config file is created, without the explicit consent
     flag, which is **distinct from `--yes`** (whose fan-out-bypass meaning is unchanged).
  3. **`--no-sync`** — a documented opt-out on both commands.
  4. **The config delta report** — the change set is printed before it is applied.
  5. **`CI`/non-interactive suppression** of the config sub-operation.

  Interactive `yf harness skills install --tune` invocations retain the unchanged separability and
  fan-out-confirmation contract above; the exception is scoped to the sync path alone.
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
- **REQ-YF-TUNE-026** *(testable, plan-034)* the read-only `yf doctor` settings-drift axis
  (`SettingsDriftCheck`, `REQ-YF-TUNE-009`) shall run for **every harness that ships a config
  profile** — codex and opencode, not only claude-code — diffing each harness's on-disk merged
  config against its embedded profile via the format-aware read (`REQ-YF-TUNE-013`/`-014`). Because
  the check is already harness-generic and the read is already format-aware, this is **registration**
  (`from_env("codex")` / `from_env("opencode")`) **+ tests**, reusing the shipped check — **not** a new
  engine — and it does **not** touch `yf/src/cmd/harness/drift.rs` (the separate `REQ-YF-TUNE-008` CI
  doc↔profile agreement test). **Separately**, a new **per-harness managed-block drift** check shall
  report — **distinctly from**, named to disambiguate (e.g. "managed-block drift"), and never
  double-counting — the existing aggregate `rule_drift` axis already emitted by `doctor/checks.rs`,
  whether each rule-target AGENTS.md harness's (codex, opencode, pi) yf-managed `BEGIN`/`END` block
  (`REQ-YF-TUNE-019`/`-020`) matches the current minimized irreducible-core bundle
  (`REQ-YF-TUNE-018`, `minimize::irreducible_core_bundle()`): a stale/hand-edited block — or an absent
  block where tune would deploy one — is reported as drift. Both halves are strictly **read-only**:
  they report divergence and never write (remediation is "run `yf harness tune`"), decoupled from `yf
  doctor --repair` per `REQ-YF-TUNE-009`. This is the `REQ-YF-TUNE-009` analog `REQ-YF-TUNE-011`
  deferred.
- **REQ-YF-TUNE-027** *(testable, plan-034)* codex rule deployment (and the drift axis,
  `REQ-YF-TUNE-026`) shall compute the **projected size of the global `~/.codex/AGENTS.md`** — its
  existing on-disk content plus the yf-managed block (`REQ-YF-TUNE-019`) — against the **effective
  on-disk** `project_doc_max_bytes`, read from the operator's `~/.codex/config.toml` and **falling
  back to codex's documented 32768-byte default when the key is absent** (NOT the profile's tuned
  65536, which applies only after a tune), and shall emit a **warning** — never truncate, never block
  — when the projected size reaches a documented threshold (**≥ 90%** of the effective cap), naming
  **both** the cap and the projected size so the warning is actionable. The requirement documents a
  deliberate **single-file scope limitation**: the check covers only the global `~/.codex/AGENTS.md`
  yf writes, **not** the full multi-file `AGENTS.md` concatenation codex assembles (the project/cwd
  `AGENTS.md` the operator controls are out of yf's lane) — a chosen single-file scope, not an
  oversight.
- **REQ-YF-TUNE-028** *(testable, plan-042)* `yf harness tune` shall support a **rules-only mode** —
  a `--rules-only` flag (and the equivalent internal parameter on the tune bridge) that runs the
  **rule optimization + deployment** sub-operation (`REQ-YF-TUNE-018..020`) **without** the config
  alignment sub-operation (`REQ-YF-TUNE-004..006`). A rules-only run shall write the rules aggregate
  to the correct per-harness target and shall **touch no config file** — neither creating one nor
  modifying an existing one — and shall report config as **skipped** (distinct from the pi
  **deferred** verdict of `REQ-YF-TUNE-017`, which reflects an absent profile rather than an operator
  request).

  This is a **named exception to `REQ-YF-TUNE-012`**, which requires that tune *"own **two**
  sub-operations per harness… reporting a per-harness verdict covering both"*. Rules-only runs
  exactly one of the two by design. The exception exists because `tune_one_harness_at` unconditionally
  runs both, making "deploy rules without config" unreachable by any verb — and the `REQ-YF-SELF-005`
  sync needs precisely that capability to deploy its **safe half** (skills + rules, which carry no
  security semantics) independently of the **consent-bearing half** (config, which can write
  `permissions.defaultMode: "bypassPermissions"`). Rules-only is also the mechanism by which the
  `REQ-YF-SELF-008` `CI` suppression is implemented — not a second, separate suppression path.

- **REQ-YF-TUNE-029** *(testable)* `yf harness tune --revert` shall apply a **rules-side guard**
  with the same conservative-keep semantics `REQ-YF-TUNE-022` gives config keys. The ownership
  manifest's rule record shall carry the **`sha256`** of the aggregate as yf wrote it, recorded on
  **every** rules write. On revert, if the on-disk aggregate's sha256 differs from the recorded
  value (an operator hand-edited it since the tune), the file shall be **kept and the mismatch
  reported** — never deleted. Revert shall **not** delete a file whose pre-tune content `yf` never
  backed up: restoring content requires a real backup, and deletion is not restoration. The
  aggregate's revert branch shall match its `kind` **explicitly**, never via a catch-all arm, so a
  future artifact kind cannot silently inherit delete semantics. This is the narrow hand-edit
  tolerance `REQ-YF-FLOW-004` carves out.

- **REQ-YF-TUNE-030** *(testable)* every harness profile shall carry a
  **`settings_read_layers`** field: the ordered list of config files that harness *itself* reads,
  highest precedence first. The **read** set shall be **decoupled from the single write target** —
  `yf` writes exactly one config file per harness (unchanged), but every audit-class consumer
  (`yf doctor`, the settings-drift axis, `yf harness tune`'s pre-write inspection) shall read
  **every** layer in `settings_read_layers`, not the write target alone. Rationale, measured:
  `opencode` reads both `opencode.json` and `opencode.jsonc`, and **`.jsonc` has the higher
  precedence**; today's agreement between yf's write target and the harness's effective config is
  therefore **coincidence**, and an audit whose read set is narrower than the harness's own will
  report a green while a higher-precedence layer overrides everything it just checked. An audit that
  cannot see a layer the harness obeys shall report **INCONCLUSIVE** for that key, never `ok`.

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
| yf-herdr                | _(new, plan-037)_    | utility  | HERDR    | `skills/yf-herdr/SPEC.md`                |
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
