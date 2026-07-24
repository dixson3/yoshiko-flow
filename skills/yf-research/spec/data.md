# Data Specification

Anchors on-disk layout, the credibility model, and config. Verified against SKILL.md,
`scripts/index_manager.py`, `scripts/credibility_scorer.py`, and
`scripts/research_manager.py`.

REQ-DATA-001: Research outputs live under one of two roots — `docs/research/<NNN>-<slug>/` (default) or `Incubator/<slug>/research/<NNN>-<slug>/` (incubator-scoped). The `<NNN>` index is global across both roots.
Rationale: Global numbering keeps cross-references unambiguous regardless of root.
Verification: SKILL.md Phase 2 (root detection + global `count`).

REQ-DATA-002: Each research topic uses the layout: `plan.yaml`, `Summary.md`, `sources.json`, `index.md`, `log.md`, `scripts/`, `artifacts/` (with `cluster-<name>.md`, `triangulation.md`, `critique.md`). The reserved index is `index.md` (renamed from the legacy `_index.md`) and the reserved newest-first ISO-8601 ledger is `log.md`; the bundle conforms to OKF-RESEARCH per `spec/portability.md` REQ-PORT-007..009. The non-reserved `.md` files (`Summary.md`, `artifacts/*.md`, `sources.md`) carry OKF frontmatter (`type` + `okf_spec: OKF-RESEARCH`); the non-`.md` sidecars (`plan.yaml`, `sources.json`) are excluded from that rule (REQ-PORT-008).
Rationale: A fixed layout lets the coordinator and a cold reader locate every artifact; the OKF-native `index.md`/`log.md` split gives the manifest and the ledger each a single writer.
Verification: SKILL.md Phase 3 (`mkdir`); `index_manager.py`; `agents/*.md` outputs; `spec/portability.md` REQ-PORT-007..009.

REQ-DATA-003: `sources.json` holds every source with a credibility score; every factual claim in `Summary.md`/artifacts carries an inline `[N]` that resolves to a `sources.json` entry.
Rationale: Citations are the contract; an unresolved citation is a defect.
Verification: `spec/epistemics.md`; `agents/packager.md` citation check.

REQ-DATA-004: Source credibility is a 4-factor weighted model — domain authority 35%, currency 20%, expertise 25%, bias neutrality 20% — categorizing sources as `high_trust | verify | questionable | avoid`.
Rationale: A fixed rubric makes scores reproducible and independently checkable by the red-team.
Verification: `scripts/credibility_scorer.py`.

REQ-DATA-005: `index.md` (renamed from the legacy `_index.md`) is the OKF bundle listing / artifact manifest, and `log.md` is the newest-first ISO-8601 update ledger; both are created/updated only via `index_manager.py` (`init`, `add`). Both reserved files carry no OKF `type`/`okf_spec` frontmatter (REQ-PORT-009). The legacy single timestamped `_index.md` table served both roles; the OKF model splits them (listing → `index.md`, ledger → `log.md`), with the content split completed by the Epic-4 adapter — see `spec/portability.md` REQ-PORT-009 and OKF-EXTENSION §5.
Rationale: A single writer prevents drift in the manifest format; separating the listing from the timestamped ledger gives each a stable single-purpose format.
Verification: `scripts/index_manager.py`; coordinator/packager call sites; `spec/portability.md` REQ-PORT-009.

REQ-DATA-006: Per the Skill Surface Convention, operator config (`ignore-skill`) lives at `.yf/research/config.local.json` (repo root `.yf/`, gitignored), with the legacy root dotfile `.yf-research.local.json` surviving as a read-time fallback (declared by `config-basename`); runtime state (`prereqs-present` and `scaffold-ensured` caches) lives at `.yf/research/preflight.json`; the installed rule (in the scope+surface rules dir, e.g. `~/.<surface>/rules/RESEARCH.md`, installed by `install.sh`) is hash-checked against `protocols/manifest.json` (schema_version 1). A single anchored `.gitignore` entry `/.yf/` (no globs) — covering both config and state — is ensured by preflight, not by `/yf-research init` — additive-only, gated by `scaffold-ensured` so it is written once per scaffold version (Surface Convention §7). `yf migrate` moves legacy → canonical; preflight does not auto-migrate.
Rationale: Config = operator decisions a fresh clone needs; state = recomputable cache tied to one checkout; the manifest hash detects rule drift/staleness. Conflating these commits machine-local state or loses operator intent. Ensuring the anchors in preflight (not init) makes it self-healing rather than dependent on init having been run.
Verification: `research_manager.py` `CONFIG_FILE` vs `STATE_FILE`; `_read_config()`/`_read_state()`/`_update_state()`; `_ensure_scaffold()` (GITIGNORE_ANCHORS, additive append, scaffold-ensured gate) invoked from `_check_prerequisites()` on `ok`; `_check_rule()` + `MANIFEST_FILE`; `protocols/manifest.json`; SKILL.md Pre-flight `ok` bullet.

REQ-DATA-007: `plan.yaml` carries `topic`, `mode`, `priority`, `research_dir`, `questions` (primary/secondary), `source_clusters`, `tooling_needed`, `execution`.
Rationale: The plan is the single approved input the pipeline executes against.
Verification: SKILL.md Phase 2 plan.yaml structure.
