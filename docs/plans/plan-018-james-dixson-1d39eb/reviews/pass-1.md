# Review pass-1 — plan-018

**Reviewer:** red-team (adversarial) · **Date:** 2026-06-30 · **Plan status at review:** review

## Verdict: REVISE

The architecture is sound and genuinely low-risk (production pipeline unchanged, all new code
consumer-side). But the plan and all three findings repeatedly mis-state two load-bearing facts
about the *actual* cargo-dist output, and treat both as resolved when they are not. The fixes are
localized and well-understood, so this is REVISE, not INVESTIGATE-MORE.

## Strengths
- Reframing (production half already met by cargo-dist 0.32.0) is **correct and verified**:
  `[workspace.metadata.dist]` declares exactly the 4 targets, `checksum="sha256"`,
  `installers=["shell","homebrew"]`, `tap`, `publish-jobs`; `release.yml` is genuinely
  dist-generated and uploads per-target archives + `.sha256` + `dist-manifest.json` (v0.3.0, v0.3.2).
- Keeping cargo-dist and owning only the consumer side is the right call; `dist-toolchain` gate
  appropriate (`dist` genuinely not installed).
- `classify_source` (canonicalize-then-prefix, Cellar + `/usr/local/Cellar` + linuxbrew) is robust
  against the symlink case.
- Splitting `yf self update` (binary) from `yf skills upgrade` (skills) is correct/non-breaking;
  `self` namespace verified free.
- Upstream dispositions well-justified.

## Concerns

1. **[HIGH] Assets are `.tar.xz`, not `.tar.gz` — extraction is a missing dep, step, and issue.**
   v0.3.2 ships `yf-<triple>.tar.xz` + `.tar.xz.sha256`; `dist-manifest.json` lists
   `executable-zip` as `.tar.xz`. Plan + findings say `.tar.gz`. 3.4's deps were only
   `ureq+self-replace` with **no extraction step**; O3's `flate2` is gzip and cannot read xz (xz =
   `lzma-rs`/`liblzma`/`xz2`). No issue owned extraction.
   *Recommendation:* add an extraction issue before 3.4's swap; correct `.tar.gz`→`.tar.xz`
   throughout; if shelling to system `tar` (handles `.xz`), state it + the tooling assumption.

2. **[HIGH] Receipt contract (3.1) assumes a schema/filename cargo-dist does not produce, and the
   installer is non-editable.** Actual: `~/.config/yf/yf-receipt.json` (filename `yf-receipt.json`,
   NOT `install-receipt.json`), fixed schema `{binaries, binary_aliases, cdylibs, cstaticlibs,
   install_layout, install_prefix, modify_path, provider, source, version}`; `source` is a nested
   repo descriptor, NOT an install classifier. 3.1 invented `{schema, source, version, install_path,
   target, installed_at, installer}` and falsely claimed "Epic 1's installer writes it." O2 genuinely
   unresolved.
   *Recommendation:* re-spec 3.1 to read the real `yf-receipt.json` (derive "vendor" from
   `install_prefix`, not a `source` field); reserve a yf-authored receipt for `--from-build` only;
   or decide vendor-vs-Homebrew purely by canonicalized `current_exe()` path and demote the receipt
   to a from-build marker.

3. **[MEDIUM] EXP-001's "bundles axoupdater (`yf-update` companion)" is factually wrong; real
   receipt-trigger is unacknowledged coupling.** No `yf-update` asset exists; `_updater_name=""`
   everywhere — **no duelling-updater problem** (decision 6 / EXP-001 motivation moot). But the
   receipt is written only `if INSTALL_UPDATER=1` (default 1). Disabling the updater in dist config
   may **silently stop writing the receipt** the design depends on.
   *Recommendation:* drop the axoupdater framing; note in 1.3 that disabling the updater must not
   disable receipt emission; verify post-`dist generate`.

4. **[MEDIUM] Testing against v0.3.2 assets does not exercise download/verify/extract/self-replace
   by default.** Local version == latest (`0.3.2`), so `yf self update` hits already-latest and never
   swaps. Must force the path (lower local version, or `--force`/`YF_VERSION`).
   *Recommendation:* add the forcing mechanism to 3.4 acceptance; it also exercises xz extraction
   (surfacing Concern 1).

5. **[LOW] `install-path = ~/.local/bin` for cargo-dist 0.32 plausible but unconfirmed.** Correctly
   routed to 1.1 (`dist plan`). When set, `install_prefix` becomes the vendor signal — key vendor
   detection on that path (ties to Concern 2).

## Missing
- No issue for archive extraction (xz + untar) — largest net-new runtime capability after HTTP.
- No issue reconciling cargo-dist's fixed receipt schema with the desired classification fields.
- Cross-epic sequencing edge gap: 1.3 (`depends-on 1.2`) and 3.1 (`depends-on 2.1`) had **no edge
  between them**, yet 1.3 claimed to "write the Epic-3 schema." Add an edge or hoist the schema.
- `dist-manifest.json` parse path named in 3.4 but no issue specifies the `executable-zip`/`.tar.xz`
  artifact-selection shape.

## Gate Assessment
Gates appropriate and minimal. `dist-toolchain` genuinely needed (`dist` not installed; dist block
hand-authored). `dist --version` == `0.32.0` valid. Start (human) + Reconcile (auto) correctly
scoped. No over-gating.

## Upstream Assessment
Dispositions reasonable and verified against AGENTS.md coarse-granularity: #55 include; #54 partial
correctly carved to install/getting-started docs (wired to 5.1 `resolves-upstream: #54 (partial)`);
#41/#40 excluded on a defensible axis. Consistent with the one-coarse-issue-per-plan precedent
(#13/#14/#16). Only correction: strike the "axoupdater already bundled" motivation (Concern 3) — no
disposition changes.

## Operator Resolutions
| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| 1 | `.tar.xz` not `.tar.gz`; extraction missing | high | Added **Issue 3.4a** (xz+untar, default system `tar`); 3.4 now selects the `executable-zip` `.tar.xz` artifact + extracts before swap; corrected `.tar.gz`→`.tar.xz` in plan + finding correction banners; GR-011 risk row updated | resolved |
| 2 | Receipt schema/filename wrong; false "installer writes it" | high | Re-spec'd **3.1** to read cargo-dist's real `yf-receipt.json` and derive vendor from canonicalized `install_prefix`; **3.3** made path-primary (receipts corroborate); yf-authored marker reserved for `--from-build` (3.1b); removed the false "Epic-1 writes Epic-3 schema" claim from 1.3 | resolved |
| 3 | "axoupdater bundled" wrong; receipt gated on `INSTALL_UPDATER=1` | medium | Struck the axoupdater/duelling-updater framing (findings banner + reframing block); **1.3** now verifies receipt emission is not disabled by retargeting; path-primary detection (3.3) means a missing receipt no longer breaks classification | resolved |
| 4 | v0.3.2 test won't exercise the swap path | medium | **3.4 acceptance** now requires forcing the path (sub-version build or `--force`/`YF_VERSION`), which also exercises xz extraction | resolved |
| 5 | `install-path=~/.local/bin` unconfirmed | low | Left in **1.1** (`dist plan`); 1.1 captures whether `~/.local/bin` is honored + what `install_prefix` reads; vendor detection keys on it | resolved |
| 6 | Sequencing edge (1.3 ↔ 3.1) + manifest artifact-selection | — | Inverted: **3.1 now `depends-on 1.1`** (spec receipt-reading after dist output is known); 1.3 no longer claims to write our schema; **3.4** specifies `executable-zip`/`.tar.xz` selection | resolved |

**Disposition:** all six addressed in plan v2 (this revision). Re-presented for operator approval.
