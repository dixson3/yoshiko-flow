# Free `REQ-*` ids — repo-wide allocation table

> **Issue 0.1 of plan-060.** No issue in this plan may allocate a `REQ-*` id before this
> file lands (the plan-049 precedent).

**Computed:** 2026-08-29  
**Roots scanned:** `skills/`, `SPEC.md`, `yf/src`, `scripts/`, `_shared/` (507 files)  
**Excluded:** `docs/plans/**` — the frozen plan bundles. A `REQ-*` id quoted inside a
frozen bundle is a *citation*, not an *allocation*; counting them would let a plan that
merely discusses an id block its reuse.

**Method — deliberately NOT `grep`.** Computed by a Python scan
(`re.finditer(rb'REQ-([A-Z]+)-(\d+)')` over `find <root> -type f`), because `grep` in
this repository's interactive **and** Bash-tool shells resolves to a **ugrep shell
function** that honours `.gitignore` — verified this session with `type grep`. That is
R13's shell-dependence in its allocation-table form: a `grep -r` table would silently
under-count any family defined only under an ignored path. The scan reads every file byte
stream directly and de-duplicates ids in a `set`, so a family is never double-counted
across files.

## Table

| Family | Max allocated | Next free | In-block gaps | Ids in use |
| :-- | --: | --: | :-- | --: |
| `REQ-AGENT-*` | 64 | **65** | 7-9, 14-19, 22-29, 32-39, 52-59 | 31 |
| `REQ-APPLY-*` | 6 | **7** | none | 6 |
| `REQ-BAUTH-*` | 41 | **42** | 4-9, 16-19, 24-29, 36-39 | 21 |
| `REQ-BE-*` | 5 | **6** | none | 5 |
| `REQ-BINIT-*` | 27 | **28** | 4-9, 18-19 | 19 |
| `REQ-BRANCH-*` | 4 | **5** | none | 4 |
| `REQ-BUP-*` | 73 | **74** | 5-9, 17-19, 22-29, 33-39, 65-69 | 45 |
| `REQ-CHECK-*` | 7 | **8** | none | 7 |
| `REQ-CHGVAL-*` | 24 | **25** | 17-19 | 21 |
| `REQ-CLI-*` | 29 | **30** | none | 29 |
| `REQ-COMPLETE-*` | 4 | **5** | none | 4 |
| `REQ-DATA-*` | 76 | **77** | 8-9, 29, 32-39, 46-50, 64-69 | 54 |
| `REQ-DIAG-*` | 43 | **44** | 5-9, 12-19, 23-29, 32-39 | 15 |
| `REQ-DOC-*` | 3 | **4** | none | 3 |
| `REQ-DRIFT-*` | 30 | **31** | 7-9, 14-19, 23-29 | 14 |
| `REQ-ENGINE-*` | 10 | **11** | none | 10 |
| `REQ-EPIST-*` | 6 | **7** | none | 6 |
| `REQ-FORMULA-*` | 5 | **6** | none | 5 |
| `REQ-HERDR-*` | 41 | **42** | 4-9, 16-19, 29, 34-39 | 24 |
| `REQ-HYG-*` | 16 | **17** | none | 16 |
| `REQ-INCUB-*` | 43 | **44** | 5-9, 15-19, 22-29, 33-39 | 18 |
| `REQ-INFER-*` | 5 | **6** | none | 5 |
| `REQ-INT-*` | 5 | **6** | none | 5 |
| `REQ-JSON-*` | 4 | **5** | none | 4 |
| `REQ-MDFMT-*` | 21 | **22** | 7-9, 15-19 | 13 |
| `REQ-MDHTML-*` | 31 | **32** | 6-9, 12-19, 27-29 | 16 |
| `REQ-MDLINT-*` | 20 | **21** | 8-9, 13-19 | 11 |
| `REQ-MDPDF-*` | 51 | **52** | 5-9, 13-19, 22-29, 33-39, 45-49 | 19 |
| `REQ-OKF-*` | 72 | **73** | 5-9, 13-19, 23-29, 35-49, 52-59, 62-69 | 22 |
| `REQ-OKFH-*` | 10 | **11** | none | 10 |
| `REQ-OP-*` | 15 | **16** | none | 15 |
| `REQ-OPTINST-*` | 30 | **31** | 7-9, 14-19, 25-29 | 16 |
| `REQ-ORCH-*` | 14 | **15** | none | 14 |
| `REQ-PHASE-*` | 7 | **8** | none | 7 |
| `REQ-PLAN-*` | 82 | **83** | 4, 6-9, 13-19, 22-29, 35-39, 43-49, 56-59, 78 | 45 |
| `REQ-PORT-*` | 54 | **55** | 13-19, 21-29, 34-39, 42-49 | 24 |
| `REQ-PREREQ-*` | 23 | **24** | 8-9, 12-19 | 13 |
| `REQ-RESEARCH-*` | 40 | **41** | 4-9, 13-19, 25-29, 32-39 | 14 |
| `REQ-RESUME-*` | 4 | **5** | none | 4 |
| `REQ-SAFE-*` | 5 | **6** | none | 5 |
| `REQ-SCHEMA-*` | 8 | **9** | none | 8 |
| `REQ-SESSION-*` | 2 | **3** | none | 2 |
| `REQ-SKAUTH-*` | 60 | **61** | 3-9, 13-19, 23-29, 34-39, 43-49, 51-59 | 17 |
| `REQ-STATUS-*` | 3 | **4** | none | 3 |
| `REQ-STRUCT-*` | 5 | **6** | none | 5 |

## The ids plan-060 allocates

Each is the family's **next free** number above, and each is verified against this table
rather than against prose:

| Id | Family next free | Owning file | Allocated by |
| :-- | --: | :-- | :-- |
| `REQ-LAND-001`..`REQ-LAND-026` | new family (26 allocated) | `skills/yf-plan/spec/landing.md` | Issue 0.2 |
| `REQ-CLI-030` | 30 | `skills/yf-plan/spec/cli.md` | Issue 0.3 |
| `REQ-AGENT-065` | 65 | `skills/yf-plan/spec/agents.md` | Issue 0.4 |
| `REQ-COMPLETE-005` | 5 | `skills/yf-plan/spec/phases.md` | Issue 0.5 |
| `REQ-PLAN-083` | 83 | `skills/yf-plan/SPEC.md` | Issue 0.6 |

> **Successor value, added during execution.** This table is a **dated snapshot taken against
> `main` before Epic 0**, so its family count is **45**. Issue 0.2 then created `REQ-LAND-*`,
> bringing the post-Epic-0 tree to **46**. The snapshot is deliberately not rewritten — it is the
> record of what was free *at allocation time*, which is the question it exists to answer. The
> live figure is tracked by `cited-figures.md`'s `req-families` row, whose first run reported
> exactly this drift.

**`REQ-LAND-*` is a NEW family** — it appears nowhere in the table above, so it starts at
`001`. A new spec key is precedented: plan-057 added `REQ-OKFH-001`..`010` the same way,
and `REQ-OKFH` appears in this table as a family with max 10.

**`REQ-PLAN-083`, never `082` and never `078`.** `082` is *consumed* at
`plan_manager.py:7330` and *defined nowhere*, so the scan above sees it (max = 82) even
though no requirement text owns it; reusing it would collide with a live reference. `078`
is retired. The table's `Next free` column is therefore correct as printed, and the
reasoning behind skipping `082` is recorded here rather than left to be re-derived.

