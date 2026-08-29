---
type: Reference
okf_spec: OKF-PLAN
description: "Draft closing comment for #233 — the OKF walk now has a member-declared path-exclusion concept, applied at all five walk sites."
---
**Fixed and closing.** The real defect was the one this issue names in its body: the OKF walk had
**no path-exclusion concept at all**, which `doc_lint` had already solved twice with per-schema
`exclude` lists.

**`REQ-OKF-CHK-003`** adds it:

- **Member-declared.** A per-skill `OKF-EXTENSION.md` may carry a **§3b Excluded paths** table of
  bundle-relative globs. `skills/yf-plan/OKF-EXTENSION.md` now declares `assets/fixtures/**` and
  `findings/okf-migration-samples/**` — the two deliberate fixture corpora.
- **`fnmatch`, never `_glob_match`.** `_glob_match` is `PurePosixPath.match`, which has **no
  recursive `**`** — so `assets/fixtures/**` would have matched `fixtures/x.md` and *not*
  `fixtures/deep/x.md`, silently excluding one level and inspecting the rest. A matcher that cannot
  express the patterns it is handed is a control that cannot fire.
- **All FIVE walk sites**, enumerated in the requirement: `okf.py`'s `check_conformance`, `migrate`
  and `_listing_members`, plus `plan_manager.py`'s `okf_spec` scan and its `dangling-refs` scan.
  Fixing only the engine's walks would have left `audit-close` still reporting, which is where you
  saw it. Migration matters most: stamping frontmatter on a deliberate non-conformant fixture does
  not merely produce a spurious finding, it **destroys the fixture**.
- **`--no-exclude` is the positive control**, mirroring `doc_lint`'s flag. An exclusion nothing can
  turn off is indistinguishable from a check that never fired.

**Measured, before and after.** `audit-close` on `plan-053`: **25** `okf:` findings under a fixture
path → **0**, with the walk demonstrably still live — `--no-exclude` restores **28** error findings.
`scripts/checks/check-fixture-carveout.sh` asserts both halves, and its liveness arm uses
`--no-exclude` rather than requiring a non-fixture finding to exist, because plan-053 is genuinely
clean off the fixture path and the naive form would be unsatisfiable there.

The two exclusion lists (`doc_lint`'s and `§3b`'s) are **independently declared** — different
coordinate systems, repo-relative vs bundle-relative — and an overlap-invariant test pins their
relationship *and* asserts both lists are non-empty, since the invariant holds trivially when either
side is empty.

Plan: `docs/plans/plan-056-james-dixson-473dba/`
