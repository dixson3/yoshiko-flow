# Plan: Consolidate per-skill protocol rule install into a single aggregated YOSHIKO_FLOW.md rule file with per-protocol hash-bearing HTML-comment fences for selective version update/removal

**ID:** plan-011-james-dixson-dd21e3
**Author:** james-dixson
**Created:** 2026-06-19
**Status:** approved
**Epic:** beads-skills-mol-r8z
**Phase log:**
- 2026-06-19 scoping: initial scope captured
- 2026-06-19 investigating: scope ratified; blast-radius scan of test/parity/doctor surface
- 2026-06-19 drafting: blast radius known; synthesizing epics/gates
- 2026-06-19 review: plan v1 presented
- 2026-06-20 approved: operator approved (red-team concerns resolved, audit pass)
- 2026-06-20 intake: epic beads-skills-mol-r8z poured

## Objective
Consolidate per-skill protocol rule install into a single aggregated YOSHIKO_FLOW.md rule file with per-protocol hash-bearing HTML-comment fences for selective version update/removal

## Motivation
Today `yf skills install` surfaces each skill's companion protocol rule as a
**separate file** in the rules dir (`~/.<surface>/rules/<NAME>.md`), one per
rule-bearing skill (7 today: `BEADS_INIT.md`, `UPSTREAM_TRACKING.md`,
`DRIFT-CHECK-TRIGGER.md`, `MARKDOWN_LINT.md`, `INSTRUCTIONS.md`, `PLANS.md`,
`RESEARCH.md`). Every one of these is always-loaded instruction context, so the
rules dir accretes a scatter of `yf`-owned files intermixed with files `yf` does
not own (e.g. `BEADS.md` from `bd init`), with no single place that says "this is
the Yoshiko Flow ruleset" and no way to tell at a glance which protocols/versions
are active. The operator (James) wants the always-loaded `yf` ruleset
consolidated into **one** `yf`-managed file, `YOSHIKO_FLOW.md`, whose per-protocol
sections carry hash-bearing fences so `yf` can update/remove individual protocols
and stay fully in sync with the embedded skill set (including dropping protocols
that were deprecated/removed upstream). Triggered by James's 2026-06-19 request.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| _none_ | — | n/a | No existing upstream issue matches. Coarse-granularity tracking issue filed at land-the-plane per AGENTS.md. | — |

## Scope Decisions (operator-ratified 2026-06-19)

- **S1 — What consolidates.** Only the rule-bearing protocols `yf` embeds/installs
  merge into a single `YOSHIKO_FLOW.md` in the resolved rules dir. Rules `yf` does
  not own (e.g. `BEADS.md` from `bd init`) are never touched.
- **S1+ — Reconcile to the embedded set.** A section is **valid** iff its protocol
  still exists in the binary's embedded skill tree **and** is not `deprecated:true`
  in its `protocols/manifest.json`. Any write operation prunes invalid sections, so
  a protocol deprecated/removed upstream is dropped from `YOSHIKO_FLOW.md`.
- **S2 — Fence format.** Paired HTML-comment fences per protocol, sections ordered
  deterministically (alphabetical by protocol filename) for stable diffs:

  ```text
  <!-- yf-flow: skill=yf-beads-init protocol=BEADS_INIT.md version=1.0.1 sha256=<body-hash> -->
  …protocol body verbatim…
  <!-- yf-flow:end protocol=BEADS_INIT.md -->
  ```

  `sha256` is over the section body, which is the protocol file **verbatim**, so it
  equals the `manifest.json` file sha256 — preflight reuses the same hash basis.
- **S3 — No hand-edit tolerance.** `YOSHIKO_FLOW.md` is a fully `yf`-managed
  generated artifact. Per-section hashes remain so `status`/`doctor`/`preflight`
  can **report** drift, but the write policy is **always rewrite the acted-on
  sections to the embedded version**; `--force` no longer gates rule content. (This
  supersedes the old "preserve existing rule unless `--force`" semantics — REQ
  change, see Risks.)
- **S4 — Migrate existing standalone rules.** On install/upgrade, fold any existing
  standalone rule file (`BEADS_INIT.md`, etc.) into `YOSHIKO_FLOW.md` and delete the
  standalone file. Migration is unconditional for the rules `yf` owns (S3: no
  hand-edit tolerance).
- **S5 — Preflight `check_rule`.** Rewrite to locate the protocol's section inside
  `YOSHIKO_FLOW.md` and hash the section body against `manifest.json`, with a
  **legacy fallback** to a standalone rule file when `YOSHIKO_FLOW.md` is absent
  (one transition release).
- **S6 — `remove`.** Remove the selected skills' sections from `YOSHIKO_FLOW.md`;
  delete the file entirely when its last section is removed.
- **Header.** `YOSHIKO_FLOW.md` carries a top-of-file banner:
  `<!-- managed by yf — do not edit by hand, edit sections at your own risk -->`
  plus a generated-on note.

## Investigation Findings
See `findings/exp-001-blast-radius.md`. Key results:

- **Bounded, single-binary change.** New `flow.rs` module (aggregate parse/serialize/
  reconcile) + rewrites of the four rule write/read paths (`install`, `upgrade`, `remove`,
  `doctor.check_rules`) + `preflight.check_rule`, plus spec/README/docs sync.
- **Parity golden is NOT affected.** `parity.rs` / `install-parity.json` cover only
  frontmatter/group/closure computation (REQ-YF-INSTALL-003/004), not rule install. No
  regeneration.
- **`manifest.json` unchanged.** The section body is the protocol file verbatim, so its
  sha256 equals the manifest file sha256 — preflight/doctor reuse the same hash basis.
- **Drift-checked spec↔doc edges.** `SPEC.md` (fixed authority) and `README.md` are bound
  by `DRIFT-CHECK.md` edge `e-spec-readme`; the install-behavior change must land in both
  together. `docs/MIGRATION.md` and `docs/yf/preflight-contract.md` also reference the rule
  axis.
- **Riskiest seams:** (a) the transition-release legacy fallback in `preflight`/`doctor`,
  and (b) reconcile-prune distinguishing "not selected this run" (keep) from "no longer
  embedded / deprecated" (drop).

## Approach

A new `yf/src/flow.rs` module owns the aggregate-file format end to end — exactly as
`marker.rs` owns the SKILL.md marker. It provides: parse `YOSHIKO_FLOW.md` → ordered
sections; per-section body sha256; serialize sections (+ banner, alpha-by-protocol order);
`upsert_section`, `remove_section`, and `reconcile(embedded_valid_set)` (prune sections
whose protocol is absent from the embedded tree or `deprecated:true`). The fence carries
`skill`, `protocol`, `version`, `sha256`.

The four command paths delegate to `flow.rs`:

- **install** — for each selected rule-bearing skill, upsert its current section; migrate
  (fold-in + delete) any standalone file for that protocol; reconcile-prune; write the file.
- **upgrade** — same as install (S3: always rewrite acted-on sections), plus reconcile is
  authoritative over the whole file.
- **remove** — drop the selected skills' sections; delete `YOSHIKO_FLOW.md` when empty.
- **doctor `check_rules`** / **preflight `check_rule`** — read the section body from the
  aggregate (legacy fallback to a standalone file when the aggregate is absent), then apply
  the existing verdict logic against the embedded bytes / manifest sha unchanged.

`SPEC.md` gains a `REQ-YF-FLOW-*` group for the aggregate format, reconcile-prune, banner,
and migration; REQ-YF-INSTALL-001/006 and REQ-YF-PRE-003 are amended. `README.md`,
`docs/MIGRATION.md`, and `docs/yf/preflight-contract.md` are updated in the same change to
satisfy the drift-check edges.

## Epics

### Epic 1: `flow.rs` — the aggregate-file format module
The self-contained, well-tested core. No command wiring yet; pure functions + unit tests,
so the risky format/reconcile logic is proven before anything calls it.

- Issue 1.1: Define the fence grammar + `FlowSection { skill, protocol, version, sha256, body }`
  and the banner constant. Implement `parse(text) -> Vec<FlowSection>` (tolerant of a
  missing/garbled banner; recovers sections by fences) and `serialize(sections) -> String`
  (banner + generated-on note + alpha-by-`protocol` ordering). Round-trip + golden tests.
- Issue 1.2: `section_body_sha256` (equals the manifest file sha256 for a verbatim body) and
  `upsert_section` / `remove_section` (idempotent; upsert replaces in place, preserving the
  order invariant). Unit tests incl. re-upsert-is-replace and remove-missing-is-noop.
  - depends-on: 1.1
- Issue 1.3: `reconcile(sections, embedded_valid) -> (kept, pruned)` where `embedded_valid`
  is the set of `(skill, protocol)` present in the embedded tree AND not `deprecated:true`.
  Prunes by-protocol-not-embedded and by-deprecated; KEEPS sections merely not selected this
  run. Unit tests for both prune reasons + the keep case.
  - depends-on: 1.1
- Issue 1.4: `generated-on` determinism decision — the note must not cause spurious drift on
  re-serialize. Either omit the timestamp from the body hash basis (hash sections only) or
  make the banner inert to hashing. Test: serialize→parse→serialize is hash-stable.
  - depends-on: 1.1

### Epic 2: Command-path rewrite (install / upgrade / remove)
Wire `flow.rs` into the lifecycle. Behind Epic 1 so the format is settled first.

- Issue 2.1: Rewrite `common::install_rules` (and add the aggregate read/write helper) to
  upsert selected skills' sections into `YOSHIKO_FLOW.md`, then reconcile-prune, then write.
  Drop the `--force`/`kept` rule semantics (S3). Update callers' return-shape expectations.
  - depends-on: 1.2, 1.3
- Issue 2.2: Migration (S4, **C4 option (a)** — operator-ratified 2026-06-20). On **any**
  install/upgrade write, fold **every** `yf`-owned standalone rule file present in the rules
  dir (not only acted-on protocols) into the aggregate and delete each standalone, so
  `YOSHIKO_FLOW.md` is the sole `yf` ruleset after any write. Idempotent. Unit tests:
  multiple standalones present (incl. for non-selected skills) → all folded + deleted; second
  run → no-op.
  - depends-on: 2.1
- Issue 2.3: `upgrade` path — regenerate acted-on sections + authoritative reconcile over the
  whole file. `remove` path — drop the named skills' sections **unconditionally** (**C5**: S3
  supersedes the old byte-match-to-remove guard; a drifted section is still `yf`-owned and
  dropped); evaluate "empty" **after** pruning those sections and delete `YOSHIKO_FLOW.md`
  when no sections remain. Rewrite the `status.rs` test block accordingly.
  - depends-on: 2.1
- Issue 2.4: `install.rs` / `upgrade` / `remove` dry-run + JSON/plain reporting (**C3**).
  Define the post-change JSON schema explicitly: `flow_file` (single target path),
  `rules_upserted`, `rules_pruned`, `rules_migrated` (sections folded from standalones); the
  legacy `rules_written` / `rules_kept` / `rules_removed` keys are **removed/redefined** (S3
  makes `kept` meaningless). Grep for downstream consumers of the old keys before dropping.
  Plain output reports section upserts, prunes, migrations, and the one `YOSHIKO_FLOW.md`
  target (not per-base file paths).
  - depends-on: 2.1, 2.3

### Epic 3: Read paths — doctor + preflight (with legacy fallback)
**C2** — these are two distinct comparison axes; keep them separate:

- Issue 3.1: `doctor::check_rules` extracts each protocol's **section body** from
  `YOSHIKO_FLOW.md` and compares it against the **embedded protocol bytes** (`common::embedded_rules`),
  yielding `rule_missing` / `rule_drift` / ok only — it must **not** acquire the manifest
  semver axis (doctor is deliberately presence + content-hash vs embedded). Legacy fallback to
  a standalone file when the aggregate is absent. Update doctor tests.
  - depends-on: 1.2
- Issue 3.2: `preflight::check_rule` (**C1**) locates the section in `YOSHIKO_FLOW.md`,
  extracts the **section body**, and feeds it through the **existing** `outcome_for` / `rank` /
  `previous_versions` / `deprecated` / `schema_version` machinery **unchanged** — preserving
  ALL seven outcomes (`ok | update_available | drift | deprecated | missing |
  manifest_schema_unknown | manifest_missing`), not just ok/drift. The section body equals the
  protocol file verbatim, so a body matching a `previous_versions[].sha256` still yields
  `update_available`. Legacy fallback to standalone (S5). Update the four affected preflight
  tests + the preflight parity test, and **add an `update_available`-on-aggregate unit test**
  (body == a `previous_versions` sha → `update_available`).
  - depends-on: 1.2

### Epic 4: Spec + docs sync (drift-checked edges)
- Issue 4.1: `SPEC.md` — add the `REQ-YF-FLOW-*` group (aggregate format, banner,
  reconcile-prune, migration); amend REQ-YF-INSTALL-001 (single `YOSHIKO_FLOW.md`),
  **REQ-YF-INSTALL-005** (**M2** — `--force` no longer overwrites a standalone rule; rule
  content is always regenerated), REQ-YF-INSTALL-006 (supersede preserve-unless-force), and
  REQ-YF-PRE-003 (section-aware + legacy fallback; **C1** — explicitly name
  `previous_versions` / `update_available` / `deprecated` / `schema_version` as preserved
  outcomes). Update `coverage.rs` rows.
  - depends-on: 2.3, 3.2
- Issue 4.2: `README.md` (lines re: per-file rules + `--force`), `docs/MIGRATION.md`,
  `docs/yf/preflight-contract.md` — bring into agreement with the new behavior. Satisfies
  `DRIFT-CHECK.md` edge `e-spec-readme`.
  - depends-on: 4.1

### Epic 5: End-to-end verification
- Issue 5.1: Integration test `flow_install_e2e` (named, so the gate can reference it).
  Covers: install group → assert one `YOSHIKO_FLOW.md` with N fenced, banner-headed,
  alpha-ordered sections and no standalone rule files; upgrade is idempotent; remove of one
  skill drops only its section; remove of all deletes the file. **M3** — add a
  legacy→aggregate **transition test**: pre-seed standalone rule files (incl. for
  non-selected skills), run upgrade, assert all folded into `YOSHIKO_FLOW.md`, standalones
  deleted, and `preflight`/`doctor` verdicts identical before and after. **M1** — assert no
  consumer hardcodes a standalone-rule path (grep the repo for the seven basenames outside
  `skills/*/protocols/` and plan dirs). Then `cargo test`, `cargo clippy`, `cargo fmt --check`,
  and a manual `yf skills install`/`status`/`doctor` smoke against a temp `--target`.
  - depends-on: 4.2

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: build + lint green + behavioral test (final)
- Type: human
- Condition: the named integration test `flow_install_e2e` passes, and `cargo test`,
  `cargo clippy -- -D warnings`, and `cargo fmt --check` all pass. (Referencing the named
  test means a green gate implies the behavioral assertions ran, not just that the crate
  compiles — red-team Gate Assessment.)
- Test: `cd /Users/james/workspace/dixson3/beads-skills && cargo test -q flow_install_e2e && cargo test -q && cargo clippy --all-targets -- -D warnings && cargo fmt --check`
- Blocks: Issue 5.1
- Instructions: Resolve any failure before closing 5.1.

## Risks & Mitigations

- **R1 — REQ change breaks the parity/golden contract.** *Likelihood low* (scan confirmed
  parity covers only frontmatter/groups). *Mitigation:* Issue 5.1 runs the full suite;
  REQ-YF-INSTALL-006 is amended, not deleted, with a documented supersession note.
- **R2 — Reconcile-prune over-deletes** a section for a skill simply not named in this
  invocation. *Mitigation:* `reconcile` keys on the **embedded set**, never on the
  invocation selection; explicit keep-case unit test (Issue 1.3).
- **R3 — Generated-on note causes spurious drift** (every re-serialize changes bytes →
  doctor reports drift forever). *Mitigation:* Issue 1.4 keeps the timestamp out of the hash
  basis; hash-stability test.
- **R4 — Legacy fallback masks a real drift** during the transition release. *Mitigation:*
  fallback is read-only and only when the aggregate is **absent**; once `YOSHIKO_FLOW.md`
  exists it is authoritative. Migration (2.2) removes the standalone so the fallback path
  goes cold after first install/upgrade.
- **R5 — Operator hand-edits silently clobbered** (S3 by design). *Mitigation:* the banner
  states "do not edit by hand"; doctor still reports drift so an edit is visible before the
  next upgrade overwrites it.

## Success Criteria

1. After **any** `yf skills install`/`upgrade` write, the rules dir holds exactly one
   `yf`-owned ruleset file — `YOSHIKO_FLOW.md` — banner-headed, with one alpha-ordered fenced
   section per installed rule-bearing skill, and **no** standalone `yf`-owned `*.md` rule
   files (C4(a): all folded on any write).
2. Each section's fence carries `skill`, `protocol`, `version`, `sha256`, and the body equals
   the embedded protocol verbatim (sha matches `manifest.json`).
3. `upgrade` is idempotent and reconciles: a deprecated/removed protocol's section is dropped;
   a not-selected skill's section is retained.
4. `remove` drops the named skills' sections unconditionally (even if drifted); removing the
   last section deletes the file.
5. `doctor` verdicts (`rule_missing`/`rule_drift`/ok, vs embedded bytes) and `preflight`
   verdicts (all seven outcomes incl. `update_available`/`deprecated`, vs `manifest.json`) are
   computed from the aggregate section body, with legacy standalone fallback when the
   aggregate is absent.
6. `install`/`upgrade`/`remove` `--json` emit the new schema (`flow_file`, `rules_upserted`,
   `rules_pruned`, `rules_migrated`); the legacy `rules_written`/`rules_kept`/`rules_removed`
   keys are gone, with no remaining downstream consumer of them.
7. `SPEC.md` (incl. the new `REQ-YF-FLOW-*` group and amended -001/-005/-006/PRE-003),
   `README.md`, `docs/MIGRATION.md`, `docs/yf/preflight-contract.md` agree with the new
   behavior; the named `flow_install_e2e` test and `cargo test`/`clippy`/`fmt` are green.
