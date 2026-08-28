---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-layer-ownership-boundary
description: The two engines overlap on 6 frontmatter keys on 56 files out of 48 checks and 1105+ documents — D-3's retain-both is confirmed by measurement, not judgement.
---

# Finding: Map the concrete overlap surface between `doc_lint` and `okf.check_conformance`

### Approach Tested

Read both engines end to end (`doc_lint.py` 1171 L, `okf.py` 1633 L), enumerated all 17 schemas / 48
checks, resolved the `OKF-PLAN` extension programmatically, ran `audit-close` on four real bundles and
`doc_lint --type plan-relations` corpus-wide, and built a git-init'd sandbox bundle in `$(mktemp -d)`
to drive both layers over one controlled defect set. No repo file modified.

### Result

**measured:** — there is EXACTLY ONE genuine BOTH surface: the 6 frontmatter keys on `plan.md`.
`okf.resolve_extension('yf-plan').required_keys` is byte-identical to `plan.toml`'s
`identity-frontmatter` value list. Everything else already partitions cleanly.

**measured:** — and the duplicate is invisible only by accident. A `plan.md` missing `created` yields
an OKF `warning REQ-OKF-FAM-001` and a doc_lint `[E] missing frontmatter key(s): created`. Only one
surfaces at the audit, because `_OKF_PORT050_REQS` excludes `REQ-OKF-FAM-001` and the binding drops
non-`error`. That is a filter, not a design.

**measured:** — four axes of divergence, plus a fifth the brief missed:

| axis | doc_lint | OKF |
| :-- | :-- | :-- |
| severity | `E`/`W`/`R`, plus `declared_severity` | `error`/`warning`; **`info` appears once, in a docstring — never emitted** |
| exit contract | mode-keyed `0/1/2`, `2` = INCONCLUSIVE | `0 if ok else 1` — **no INCONCLUSIVE at all** |
| path selection | repo-root-relative globs, per-schema `exclude`, `--no-exclude`, `--classify` | bundle-relative `rglob("*.md")`, **no exclusion of any kind** |
| requirement ids | `check` id, **no req id** | `req` id, **no check id** |
| **status awareness** | `STATUS_SEVERITY` + `statuses` + `promote` | **none** |

**measured:** — OKF folds INCONCLUSIVE into FAIL. `REQ-OKF-071` (malformed frontmatter, unreadable,
binary) is emitted at `error` *and* is in `_OKF_PORT050_REQS`, so an unreadable file is a bundle
`fail`. doc_lint classifies the identical condition as exit 2, bound to `warn` by `REQ-DATA-057`. This
is the same defect class the whole exit-contract work exists to remove, still live on the OKF side.

**measured:** — #233 reproduces exactly and is generic, not one plan's problem. plan-053 audit-close:
`{'fail': 26, 'warn': 19}`, 25 of the 26 OKF-prefixed and all under `assets/fixtures/corpus/**`. A
1-line frozen fixture is sufficient to reproduce. **Second independent instance:** plan-029 carries 49
OKF findings, **34 inside `findings/okf-migration-samples/**`** — a different directory, which shows
the gap is generic. Those are `warn` only because plan-029 is OKF-legacy; an OKF-native plan would show
34 `fail`.

**measured:** — exclusion lists must be INDEPENDENTLY DECLARED, not derived. Three reasons: the
coordinate systems differ (repo-root vs bundle-relative, so a shared literal is wrong on one side by
construction); the granularity differs (per-document-type vs per-member, no 1:1 mapping); and
**derivation would miss the actual bug** — `assets/fixtures/**` appears in *no* doc_lint exclude list,
because doc_lint is silent there by **non-selection**, not exclusion.

**measured:** — #246: the spec should change, not the schema. `data.md:330` says the `R*` family ships
`W` "uniformly"; `plan-relations.toml` ships `R1-closeout`/`R2a-closeout` at `E` scoped by
`statuses`, and the same file's line-7 banner contradicts itself. `grep` for "closeout" across the
spec returns **zero hits** — the binding is documented nowhere, and `REQ-BUP-070`, which the toml
names as its authority, is about `closable`'s proposal rules. Enumerating all 48 checks against
`STATUS_SEVERITY` at `complete`: **2 can produce `E`, 46 cannot, and the 2 are exactly these.**
Deleting them would make doc_lint structurally incapable of failing at `complete`. REQ-DATA-044's
rationale (R1b would hard-fail in-flight plans) does not apply to `statuses`-scoped close-out checks —
**that mechanism did not exist when REQ-DATA-044 was written.**

**measured:** — removing OKF's identity checks WOULD lose real coverage. Across `docs/plans/*/`: 1105
non-reserved `.md`, of which 56 are root `plan.md`. **doc_lint checks `type`/`okf_spec` on `plan.md`
alone** — `plan.toml` is the only schema mentioning `okf_spec`. So **1049 files (94.9%) are covered
for identity frontmatter by OKF and nothing else**, plus all 5 research bundles. The reverse is a
*severity* loss only, not a coverage loss — and it is the single genuinely redundant check in the
system.

**measured:** — `ExtensionRuleset.reserved_subdirs` is parsed and consumed by no check, only by a test.

**measured:** — the two stale-authority strays both confirmed: `yf-beads-init/README.md` lines
89/104-107/140 present `beads_init.py` as a live engine while its SPEC calls it a retired shim; and
`GUARDRAILS.md` GR-006 describes a two-surface install world against a five-harness SPEC.

### Implications for Plan

**D-3 is confirmed by measurement.** The merge D-3 rejected would have bought almost nothing — the
overlap is 6 keys on 56 files out of 48 checks and 1105+ documents — while each engine covers a
population the other structurally cannot reach.

**#233's fix is larger than "add a glob."** It needs a declared exclusion concept applied at 3-4 sites
in `okf.py` plus 2 in `plan_manager.py`, with a correct matcher. Scoping it as a one-line filter
leaves `dangling-refs` and `REQ-OKF-CHK-002` still firing.

**#246 must be resolved TOWARD the schema.** Those two checks are the only thing keeping doc_lint able
to fail at `complete`.

### Recommendations

1. **Write the boundary document as THREE axes**: container-vs-content, status-aware-vs-status-blind,
   repo-rooted-vs-bundle-relative. Cite 1049/1105 and 2/48 — the numbers are what make the split
   non-arbitrary.
2. **#233:** add `exclude_globs` to `ExtensionRuleset`, parsed from a new `OKF-EXTENSION.md` §3b;
   apply at `okf.py:827`, `:1202`, `:1309` and `plan_manager.py:5256`, `:5340`; use **`fnmatch`, not
   `_glob_match`** (`PurePosixPath.match` does not do recursive `**`); ship `--no-exclude` as the
   positive control. Seed §3b with `assets/fixtures/**`, `findings/okf-migration-samples/**`.
3. **Independently declared, shared mechanism**, plus a test asserting the overlap invariant.
   plan-029's 34 findings are the ready-made RED fixture.
4. **#246: amend the spec, keep the schema.** Amend REQ-DATA-044's severity bullet, add a REQ declaring
   the close-out binding, fix the line-7 banner in the same change-set. File the two strays separately.
5. **Resolve the one real duplicate explicitly** rather than leaving it to a filter — a future widening
   of `_OKF_PORT050_REQS` would silently double-report.
6. **Four properties should move to OKF** (`okf_spec` value correctness, index-is-listing,
   dual-write agreement — all three currently in `plan_manager.py`), and `plan-relations` stays with
   doc_lint but forces the boundary wording to be *"per-bundle document content"*, not *"per-document"*.
7. **Out of scope, worth a bead:** give `okf.py check` an INCONCLUSIVE exit so `REQ-OKF-071` stops
   reporting instrument failure as bundle failure.
