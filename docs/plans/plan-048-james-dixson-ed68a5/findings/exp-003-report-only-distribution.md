---
type: Finding
okf_spec: OKF-PLAN
id: exp-003
status: complete
---
# EXP-003 — Report-only finding distribution: what a mechanical normalizer can retire

**Question:** What are the ~610 report-only linter findings, and what fraction is *structural*
(normalizer-fixable) versus *content* (author-only)? How many survive normalization?

## Approach Tested

Reproduced the corpus figure with the on-main engine; decomposed by type / rule / status / era;
built a **prototype normalizer** and re-ran the linter against the normalized tree (a *measured*
residue, not a projection); separately measured hash-neutrality against
`plan_manager._plan_content_fingerprint` and tested whether a generous heading-alias map could
rescue the `finding` corpus.

## Result

**1. Reproduced exactly — no drift from plan-047.**

```
$ uv run _shared/doc_lint.py --json     # cwd = repo root
{'verdict':'PASS','files_checked':173,'errors':0,'warnings':0,'report_only':610}
```

Denominators: 47 `plan.md`, 123 `finding`, 3 `reference` (of 211 `references/*.md` — the type's
globs reach only `references/user-scope/**`). `reference` contributes **0**.

**2. Breakdown.** All 610 are `plan` (371) + `finding` (239).

| rule | findings | files | rate | type | structural vs content | normalizer-fixable? |
| :-- | --: | --: | --: | :-- | :-- | :-- |
| `plan/risk-ids` | 174 | 39 | 83.0% | plan | STRUCTURAL (cascade of row below) | Yes |
| `finding/measured-marker` | 122 | 122 | **99.2%** | finding | CONTENT (epistemic claim) | **No** |
| `finding/required-sections` | 117 | 117 | **95.1%** | finding | CONTENT (genuinely absent) | **No** |
| `plan/criteria-table-columns` | 46 | 46 | 97.9% | plan | STRUCTURAL (44 list-not-table, 2 missing col) | Yes |
| `plan/criterion-ids` | 44 | 44 | 93.6% | plan | STRUCTURAL (cascade of row above) | Yes |
| `plan/risks-table-columns` | 41 | 41 | 87.2% | plan | STRUCTURAL (18 list, 23 wrong header) | Yes |
| `plan/no-retired-phase-log` | 32 | 32 | 68.1% | plan | STRUCTURAL (preamble block to relocate) | Yes |
| `plan/identity-frontmatter` | 30 | 30 | 63.8% | plan | STRUCTURAL (29 have no frontmatter) | Yes |
| `plan/upstream-table-columns` | 2 | 2 | 4.3% | plan | STRUCTURAL (prose, no table) | Yes |
| `plan/required-sections` | 2 | 2 | 4.3% | plan | STRUCTURAL — **both ordering, zero missing** | Yes |

**Split: 371 structural (60.8%) / 239 content (39.2%)**, perfectly clean along the type axis —
every `plan` finding structural, every `finding` finding content.

**3. Status explains 100% of it — measured.** All 610 carry `bundle_status: complete`.
Rewriting statuses: `drafting` → 314 errors / 296 warnings / **0** report-only (FAIL);
`review` → 610 errors / 0 / 0 (FAIL). **No subset is report-only on its own merits.**

**4. Era: no signal.** Findings-per-plan is flat across plan-001→048 (93/74/84/66/54 per decade).
**46 of 47 `plan.md` are dirty — the only clean one is `plan-047`, the plan that wrote the
schema. 0 of 123 finding files are clean.** Not corpus rot; the schema postdates the corpus.

**5. Post-normalization residue — measured by running it.**

```
NORMALIZED (status=complete): PASS  errors=0  report_only=239
NORMALIZED (status=review):   FAIL  errors=239
  residue = finding/measured-marker 122 + finding/required-sections 117
```

**371 of 610 retired (60.8%); residue 239, 100% in `finding`.**

**Hash-neutrality (measured) — the load-bearing result.** Frontmatter-add and phase-log-strip are
hash-neutral on **47/47** plans (both live in the fingerprint-excluded preamble). **List→table
under `## Success Criteria` is NOT hash-neutral** — it rewrites a fingerprinted content section.
26 of 47 plans carry a stored fingerprint, so the table half flips those to `stale_approved`.

> **Under a strict hash-neutral constraint the normalizer retires ~62 of 371, not 371.**

**Can a normalizer touch the residue?** With a deliberately over-generous heading-alias map, clean
`finding` files go from **6 → 7 of 123**. Renaming buys one file. The corpus has no shared heading
vocabulary: the most common heading is "Recommendations" at 20/123 (16%).

**6. The rule that is probably wrong: `finding/measured-marker` (99.2%).**

- **measured:** exactly **one** file corpus-wide contains `**measured:**`
  (`plan-047/findings/exp-004-type-surface.md`). The schema's own comment says "2 of 117" — a
  stale snapshot.
- **inferred:** the rule tests a *literal string* as proxy for an *epistemic property*.
  `plan-020/findings/exp-001-*.md` is dense with real measurements and states "Verified:" inline —
  it fails anyway. A rule no historical document can pass, and that no script can satisfy without
  **fabricating an epistemic claim**, is the strongest waiver candidate in the set.

## Implications for Plan

- The normalizer is worth ~61% of the 610 **and 0% of the hard part**. It cleanly retires the
  entire `plan.md` structural class and cannot touch the `finding` class at all.
- **"Hash-neutral" and "retires 371" are mutually exclusive.** Strict D-4 drops the yield from
  371 to ~62 (10% of corpus findings). This is the epic's central scoping decision.
- **The retirement is partly hollow.** The linter checks table *header* and *column-0 grammar*
  only — never that cells are non-empty. The prototype retired 90 Success-Criteria findings by
  emitting `| SC1 | <text> |  |  |`. `Verification` and `Discharged-by` data does not exist in the
  source bullets and cannot be invented. **Normalization converts a visible gap into an invisible
  one** unless a non-empty-cell check lands first.
- **A frontmatter normalizer can detonate the corpus.** Measured: a prototype wrote
  `status: PLACEHOLDER`; `bundle_status` reads frontmatter-first, so `STATUS_SEVERITY` lookup
  missed, promotion vanished, and the repo went `PASS 0 errors` → `FAIL 58 errors` in one pass.
  Any frontmatter writer must carry the existing `**Status:**` value forward exactly.
- **Instantiating more document types will not move this number** — `reference` already
  contributes 0/610.

## Recommendations

1. **Split the normalizer by hash-neutrality, not by document type.** Preamble-only pass first
   (frontmatter + phase-log, 62 findings, 47/47 hash-neutral, zero re-review churn). Treat table
   canonicalization (309 findings, breaks 26 stored fingerprints) as a separate, explicitly
   authorized decision.
2. **Scope no normalizer work against the `finding` type** — best achievable mechanical yield is
   1 file of 123. The 239 residue is authorial work or a waiver, nothing in between.
3. **Waive `finding/measured-marker`** for the historical corpus, or re-scope it to bundles
   created after the investigator template landed.
4. **Add a non-empty-required-cell check to `plan.toml` BEFORE the table normalizer runs.**
5. `plan/required-sections` fires twice and **never for a missing section** — any plan text
   implying the corpus lacks plan sections is wrong.
6. Implementation hazard (not a measurement error): the prototype's list→table converter took
   only the first physical line of a wrapped bullet. Production needs continuation-line handling.

## Caveats

Prototype normalizer and analysis scripts live in the session scratchpad; nothing in the repo
worktree was modified. Counts above are all header/id-shape checks and unaffected by the
truncation hazard in (6).
