# Plan Red-Team — pass-1

**Plan:** plan-011-james-dixson-dd21e3
**Date:** 2026-06-19
**Conformance pass:** PASS (mechanical, prior)

## Verdict: REVISE

The plan is well-scoped, the blast-radius finding is accurate, and the
`flow.rs`-mirrors-`marker.rs` architecture is sound. One high-severity correctness gap
(a verdict axis the "verdict logic unchanged" claim silently drops) plus several mediums
that would surface during execution. None fatal; all fixable by amending scope/issues
before approval.

## Strengths

- Blast-radius finding verified accurate against source: `parity.rs` has no rule/protocol
  coverage; the `manifest.json` sha256 basis equals a verbatim section body; the four
  write/read paths named are the right ones.
- The `flow.rs` module boundary mirrors the proven `marker.rs` pattern; Epic 1 isolating
  format/reconcile behind unit tests before wiring is correct sequencing.
- R2 (reconcile keys on embedded set) and R3 (timestamp out of hash basis) are real risks
  with correct mitigations and dedicated tests.
- Drift-check edge `e-spec-readme` correctly identified; plan lands SPEC+README together.

## Concerns

- **C1 — The `update_available` / `previous_versions` verdict axis is unaddressed.**
  severity: high
  `preflight::check_rule` (REQ-YF-PRE-003) computes seven outcomes — `ok | update_available
  | drift | deprecated | missing | manifest_schema_unknown | manifest_missing`.
  `update_available` fires when installed bytes match a `manifest.json`
  `previous_versions[].sha256` (present in `skills/yf-beads-init/protocols/manifest.json`).
  The plan asserts "verdict logic unchanged" but only reasons about ok-vs-drift. The verdict
  is preservable (a verbatim section body can still match a `previous_versions` sha) only if
  the implementer extracts the section body and feeds it through the existing
  `outcome_for`/`rank` machinery instead of `sha256_file(whole_path)`. As written, an
  implementer could collapse it to ok/drift and silently regress REQ-YF-PRE-003.
  Recommendation: Add an explicit scope note + acceptance criterion that `check_rule`
  preserves all seven outcomes by feeding the **extracted section body** through the existing
  `outcome_for`/`rank`/`previous_versions`/`deprecated`/`schema_version` logic unchanged. Add
  an `update_available`-on-aggregate unit test to Issue 3.2. Name
  `previous_versions`/`update_available`/`deprecated` in REQ-YF-PRE-003's amendment (4.1).

- **C2 — `doctor::check_rules` and `preflight::check_rule` use different hash bases — the
  plan treats them as one.** severity: medium
  `doctor::check_rules` compares on-disk bytes against **embedded protocol bytes** and does
  not consult manifest semver (by design). `preflight::check_rule` compares against
  **manifest sha256 + semver**. The Approach lumps them ("apply the existing verdict logic").
  Recommendation: Split the read-path description — Issue 3.1 (doctor: section body vs
  embedded bytes, ok/missing/drift only) and Issue 3.2 (preflight: section body vs manifest,
  all seven outcomes) state distinct comparison bases. Confirm doctor does not inherit the
  semver axis.

- **C3 — JSON output contract (`rules_written`, `rules_kept`, `rules_removed`) changes shape
  but is not specified.** severity: medium
  Under S3, `kept` (preserve-unless-force) becomes meaningless and per-basename
  `rules_written` is ambiguous (now sections in one file). Issue 2.4 mentions reporting but
  doesn't define the new shape or flag `rules_kept` removal — a consumer-visible break.
  Recommendation: Issue 2.4 specifies the post-change JSON schema explicitly (e.g.
  `rules_upserted`, `rules_pruned`, `rules_migrated`, single `flow_file`; drop/redefine
  `rules_kept`). Add to a success criterion. Check downstream JSON consumers.

- **C4 — Migration (S4) over-narrow trigger: only acted-on protocols folded.** severity:
  medium
  Issue 2.2 folds standalone files only "for an acted-on protocol." `yf skills install beads`
  leaves standalone files for non-selected skills (`RESEARCH.md`, `PLANS.md`) orphaned beside
  `YOSHIKO_FLOW.md`, and preflight for those hits legacy fallback indefinitely. Success
  criterion #1 ("no standalone rule files that yf owns") then holds only after a full-set op.
  Recommendation: Decide migration breadth. (a) fold **all** yf-owned standalone files present
  in the rules dir on any write (cleaner, matches "one ruleset"); or (b) scope SC#1 to
  full-set ops and accept lingering standalones for non-selected skills. (a) preferred.

- **C5 — `remove` empty-file deletion vs drifted sections undefined.** severity: low
  Issue 2.3 says "delete the file when empty" but not what happens to a section whose body
  drifted from embedded when its skill is removed. S3 implies drop; the old conservative
  byte-match-to-remove guard isn't reconciled.
  Recommendation: State in 2.3 that `remove` drops named skills' sections unconditionally (S3
  supersedes the old guard), and "empty" is evaluated after pruning those sections.

## Missing

- **M1 — No orphaned-reference check for deleted standalone filenames.** Grep found no
  hardcoded consumer refs (good) but the plan never states it verified this. Add a "no
  hardcoded standalone-rule paths in consumers" verification line to Issue 5.1.
- **M2 — REQ-YF-INSTALL-005 not in the amendment list.** Dropping `kept`/`--force`-overwrite
  ripples to REQ-YF-INSTALL-005 ("`--force` shall behave as in install.py"). Plan amends -001
  and -006 but not -005. Add -005 to Issue 4.1.
- **M3 — No test for the legacy-fallback → aggregate transition.** R4's mitigation is
  asserted; Issue 5.1 covers only fresh install/upgrade/remove. Add a transition test:
  standalones present → upgrade → folded + deleted + preflight/doctor verdicts identical
  before/after.

## Gate Assessment

The single capability gate (`cargo test && clippy -D warnings && fmt --check` blocking 5.1)
is appropriate; test command valid; no gate over-applied. Gap: the gate is purely mechanical
and does not assert the behavioral success criteria. Recommend the gate condition reference
the integration test by name so a green gate implies the behavioral assertions ran.

## Upstream Assessment

Disposition "no match; coarse tracking issue at land-the-plane" is consistent with AGENTS.md
(precedent #13/#14/#16). No supersedes/partials needed. Note: ensure the land-the-plane issue
links both this plan and the `REQ-YF-FLOW-*` SPEC group it introduces.

## Operator Resolutions

Operator approved all resolutions 2026-06-20 (C4 → option (a)).

| # | Concern | Severity | Status | Resolution |
|---|---------|----------|--------|------------|
| C1 | `update_available`/`previous_versions` axis unaddressed | high | resolved | Issue 3.2 rewritten: feed extracted section body through existing `outcome_for`/`rank`/`previous_versions`/`deprecated`/`schema_version` machinery unchanged, preserving all 7 outcomes; `update_available`-on-aggregate unit test added. REQ-YF-PRE-003 amendment (4.1) names the outcomes. |
| C2 | doctor vs preflight different hash bases lumped | medium | resolved | Issues 3.1/3.2 split: doctor compares section body vs **embedded bytes** (no semver, ok/missing/drift); preflight vs **manifest** (all 7). |
| C3 | JSON output contract change unspecified | medium | resolved | Issue 2.4 defines new schema (`flow_file`, `rules_upserted`, `rules_pruned`, `rules_migrated`); legacy keys removed; grep consumers. SC#6 added. |
| C4 | migration over-narrow (acted-on only) | medium | resolved | Option (a): Issue 2.2 folds **all** `yf`-owned standalones on any write. SC#1 reworded to "after any write." |
| C5 | remove vs drifted-section deletion undefined | low | resolved | Issue 2.3: `remove` drops named sections unconditionally (S3 supersedes byte-match guard); "empty" evaluated after pruning. SC#4 reworded. |
| M1 | no orphaned-reference check | — | resolved | Issue 5.1: grep repo for the 7 basenames outside protocols/plan dirs. |
| M2 | REQ-YF-INSTALL-005 not amended | — | resolved | Added to Issue 4.1 amendment list. |
| M3 | no legacy→aggregate transition test | — | resolved | Issue 5.1: transition test (standalones → upgrade → folded/deleted, verdict parity). |

**Gate Assessment** resolved: capability gate now references the named `flow_install_e2e`
integration test, so a green gate implies the behavioral assertions ran.

**Final status:** all concerns resolved → APPROVE.
