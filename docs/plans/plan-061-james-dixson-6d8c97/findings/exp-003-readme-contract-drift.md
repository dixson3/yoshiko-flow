---
type: Finding
okf_spec: OKF-PLAN
description: 'Issue 244 re-measured at HEAD: 18 of 20 skills fail e-readme-layout, 12 SPEC.md omissions, 10 stale fence roots, and yf-okf-hygiene has no README at all. Every figure in issue 244 is stale-low. The evidence base for this plan.'
---
# EXP-003 — README-contract drift (#244), re-measured at HEAD

**Question.** Is #244's reported README-contract drift still accurate, and what is the exact
remediation set?

**Verdict.** #244 **understates the drift on every axis that matters for scoping.** Its own
numbers drifted within one plan-cycle — which is itself evidence for this plan's thesis.

## The four edges (verbatim, `DRIFT-CHECK.md:99-102,158-161`)

| Edge | Check kind | Requires |
| :-- | :-- | :-- |
| `e-readme-layout` | `field-set-equal` | the README layout fence lists exactly what `find skills/<skill> -type f` reports |
| `e-readme-prereqs` | `field-set-subset` | README Prerequisites match `SKILL.md` frontmatter `depends-on-tool` + stated prereq checks |
| `e-readme-usage` | `section-present` | every invocation command in `SKILL.md` appears in the README Usage section |
| `e-readme-desc` | `value-equal` | the README one-line description matches the `SKILL.md` `description` intent |

Source of truth is `skill-md` (or its frontmatter) for all four; a mismatch FAILs on
`skill-readme`.

## Measured tallies (vs. #244 as filed)

| Metric | #244 claims | Measured at HEAD |
| :-- | :-- | :-- |
| `e-readme-layout` failing | 16 / 19 | **18 FAIL / 1 PASS / 1 N-A out of 20** |
| `SPEC.md` missing from fences | 10 | **12** |
| Stale unprefixed fence roots | 5 | **10** |
| `yf-plan` `document_types/` schemas | 20 | **19** |
| `e-readme-prereqs` failing | 1 | **1** (unchanged — `yf-skill-authoring`) |
| `e-readme-usage` failing | 2 (+1 missing) | **3** (unchanged set) |

Only `yf-beads-hygiene` passes `e-readme-layout` cleanly.

## Sub-claim adjudication

| # | #244 claim | Verdict |
| :-- | :-- | :-- |
| a | `SPEC.md` missing from 10 fences | **PARTIALLY CONFIRMED** — the real count is **12**. (`yf-change-validation` does list `SPEC.md`; its failure is `test_change_validation.py` + `protocols/manifest.json`.) |
| b | `yf-plan` omits `doc_lint.py`, `plan_extract.py`, `pour_fidelity.py`, `document_types/` | **CONFIRMED**, and worse: `land_rehearsal.py`, `fixtures/severity-vocabulary/` and ~15 newer `test_*.py` have accrued since. Schema count is **19**, not 20 |
| c | `yf-research` omits `OKF-EXTENSION.md`, `okf.py`, 4 test files | **CONFIRMED**, byte-for-byte unchanged |
| d | 5 stale unprefixed roots | **REFUTED AS A COUNT** — at least **10**. The original 5 persist; add `yf-markdown-lint/-pdf/-format/-html` (`markdown-*/` not `yf-markdown-*/`) and `yf-skill-authoring` (`.{claude,agents}/skills/skill-authoring/`) |
| e | `yf-skill-authoring` Prerequisites absent | **CONFIRMED** — and it has no Usage section either |

## Two findings #244 could not have contained

**1. `yf-okf-hygiene` has no `README.md` at all.** It ships user-invocable subcommands
(`audit | assess | backfill | reindex | restore`) and needs all four sections authored from
scratch. It is `N/A` on every edge — **a fifth failure mode the manifest's vocabulary does not
name.** There is no README to fail a contract against; it is an *absence*, not a mismatch.

**This is the same structural hole as the missing web page** (`DRIFT-CHECK.md:75`, `skill-page`
`optional`), one artifact class over. Two independent instances of #263's vacuous-check class in
one manifest is a pattern, not a coincidence — the manifest systematically cannot express
"this artifact must exist".

**2. `e-index-table` is implicated too.** The project-root `README.md` has **zero** mentions of
`yf-okf-hygiene`, so the skill is missing from the root index as well as from the web.

## Remediation shape — favorable

| Group | Scope | Size |
| :-- | :-- | :-- |
| **(i) Mechanically regeneratable** | layout fences for 17 of 19 README-bearing skills — one `find`-diff regeneration also fixes all 10 stale roots and the `yf-okf` overclaim | **17 edits, one script** |
| **(ii) Authored prose** | `yf-beads-upstream` + `yf-incubator` Usage rewrites (`/beads-upstream` → `/yf-beads-upstream`, `/incubator` → `/yf-incubator`); `yf-skill-authoring` Prerequisites + Usage from scratch; `yf-okf-hygiene` README from zero + root-index row | **4 skills, ~4-6 edits** |

So this workstream is **not** 18 hand-authored rewrites.

**Blocking sub-decision for the plan:** there are **four distinct fence formats** in the repo —
flat `path<TAB>desc`, bullet `` - `path` — desc ``, `├──` ASCII tree, and indented plain text in
a ```text fence. Either standardize on one repo-wide (reduces the generator to one code path) or
the generator must emit all four. **This belongs in scoping, not mid-implementation.**

Mechanical checkability wrinkles: must exclude `__pycache__` / `.pytest_cache`; `field-set-equal`
(not sequence-equal) so ordering is free; needs a parser per fence format or a permissive
trailing-filename-token heuristic.

## Limits of this finding

- **`e-readme-desc` was spot-checked on 3 of 20 skills**, not exhaustively verified. No violation
  found in those 3. Treat the desc column as **INCONCLUSIVE**, not PASS.
- The investigator self-corrected mid-report on the `SPEC.md` count (initially including
  `yf-change-validation`, then excluding it). The corrected figure — **12** — is recorded above.

## Implications for the plan

1. Scope as **two epics**: (A) the mechanical fence regenerator over 19 skills; (B) the four
   authored fixes plus the `yf-okf-hygiene` README and root-index row.
2. Decide the fence-format question **before** writing the generator.
3. Bake the `find`-diff into the mechanical checker (workstream (d)) as this plan's own
   acceptance gate — #244's numbers went stale inside one plan-cycle, which is precisely the
   failure this plan exists to stop.
