---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #315 - Plan 1/3: standardize the README + code-adjacent
  documentation layout contract and backfill all 20 skills'
---
# Upstream #315: Plan 1/3: standardize the README + code-adjacent documentation layout contract and backfill all 20 skills

- **Number:** 315
- **Title:** Plan 1/3: standardize the README + code-adjacent documentation layout contract and backfill all 20 skills
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::high

## Body

> **Plan 1 of 3.** Split from a website/docs realignment audit that proved too large for one
> plan. Siblings: OKF corpus backfill, and user-facing documentation regeneration. This is the
> first to execute — the other two depend on a stable README/layout contract.

## Objective

Standardize the layout/structure contract across `README.md` and code-adjacent documentation
files, then backfill every impacted file so the contract is actually met.

## Why now — the contract is stronger than anything enforcing it

`DRIFT-CHECK.md` declares four README edges (`:99-102`, `:158-161`):

| Edge | Check kind | Requires |
| :-- | :-- | :-- |
| `e-readme-layout` | `field-set-equal` | the layout fence lists exactly what `find skills/<skill> -type f` reports |
| `e-readme-prereqs` | `field-set-subset` | Prerequisites match `SKILL.md` frontmatter `depends-on-tool` |
| `e-readme-usage` | `section-present` | every `SKILL.md` invocation appears in README Usage |
| `e-readme-desc` | `value-equal` | the README one-liner matches the `SKILL.md` `description` intent |

**Nothing runs them.** `CHANGE-VALIDATION.md:6` excludes `yf-drift-check` as *"prose/LLM trigger,
not a runnable command"*, so the only firing surface is an on-edit obligation.

## Measured state (re-derived at HEAD, 2026-08-30)

#244 reported "16/19 skills". **Every number in it is stale-low** — which is itself the argument
for this plan:

| Metric | #244 as filed | Measured today |
| :-- | --: | --: |
| `e-readme-layout` failing | 16 / 19 | **18 FAIL / 1 PASS / 1 N-A of 20** |
| `SPEC.md` omitted from fences | 10 | **12** |
| Stale unprefixed fence roots | 5 | **10** |
| `yf-plan` `document_types/` schemas | 20 | **19** |
| `e-readme-prereqs` failing | 1 | 1 (unchanged) |
| `e-readme-usage` failing | 2 (+1 missing) | 3 (unchanged) |

Only `yf-beads-hygiene` passes `e-readme-layout` cleanly.

**`yf-okf-hygiene` has no `README.md` at all** — the sole such skill, and structurally invisible
to #244 (filed before it shipped). It is `N/A` on all four edges: **a fifth failure mode the
manifest's vocabulary does not name.** There is no README to fail a contract against; it is an
*absence*, not a mismatch. The project-root `README.md` also has no row for it, so
`e-index-table` is implicated.

### Sub-claim adjudication

- **CONFIRMED** — `yf-plan` omits `doc_lint.py`, `plan_extract.py`, `pour_fidelity.py`,
  `document_types/`; plus newly accrued `land_rehearsal.py`, `fixtures/severity-vocabulary/`,
  ~15 `test_*.py`.
- **CONFIRMED** — `yf-research` omits `OKF-EXTENSION.md`, `scripts/okf.py`, 4 test files
  (byte-for-byte unchanged).
- **CONFIRMED** — `yf-skill-authoring` has no Prerequisites section *and* no Usage section.
- **PARTIALLY CONFIRMED** — the `SPEC.md` omission set is **12**, not 10
  (`yf-change-validation` does list it; its failure is `test_change_validation.py` +
  `protocols/manifest.json`).
- **REFUTED AS A COUNT** — stale unprefixed roots number **at least 10**, not 5. The original
  five persist; add `yf-markdown-{lint,pdf,format,html}` (`markdown-*/` not `yf-markdown-*/`)
  and `yf-skill-authoring` (`.{claude,agents}/skills/skill-authoring/`).
- **`yf-okf` overclaims** — its fence lists `LICENSE` and `agents/`, which **do not exist**. An
  overclaim, not an omission; a `find`-diff catches both directions.

## The blocking design decision

There are **four distinct fence formats** in the repo today:

1. flat fenced list, `path<TAB>description` — `yf-plan`
2. bullet list, `` - `path` — desc `` — `yf-research`, `yf-incubator`, `yf-beads-authoring`, `yf-beads-extra`
3. `├──` ASCII tree — 10 skills
4. indented plain text inside a ` ```text ` fence — the four `yf-markdown-*`

**Standardize on one, or the regenerator needs four code paths.** This must be decided in
scoping, not mid-implementation.

## Also in scope: `install.sh` does not exist

`install.sh` and `install.py` are **absent from the repo root**. `yf/src/parity.rs:2,5` calls
`install.py` "retired" (deleted at plan-010). `README.md:39` documents a *hosted vendor*
installer at `yoshikoflow.sh/install.sh` — a different artifact.

Yet **17 skill READMEs** still direct readers to "the repo-level `install.sh`/`install.py`", and
**`DRIFT-CHECK.md` itself does so twice** (`:219`, `:225`, §5 Required-Section Contracts),
naming it as the required Install-section source. The manifest names a nonexistent authority for
its own contract — the error class its §7 conflict policy exists to catch, committed in itself.

`e-install-url` does not help: it checks byte-identity of a URL duplicated between `SKILL.md` and
README, **not that the mechanism named is real.**

The real path today is `yf self install --from-build --build` (rebuild+promote+sync) or
`yf skills install`.

## Remediation shape — favorable

| Group | Scope | Size |
| :-- | :-- | :-- |
| **Mechanically regeneratable** | layout fences for 17 of 19 README-bearing skills; one `find`-diff pass also fixes all 10 stale roots and the `yf-okf` overclaim | **17 edits, one script** |
| **Authored prose** | `yf-beads-upstream` + `yf-incubator` Usage rewrites (`/beads-upstream` → `/yf-beads-upstream`, `/incubator` → `/yf-incubator`); `yf-skill-authoring` Prerequisites + Usage; `yf-okf-hygiene` README from zero + root-index row | **4 skills, ~4-6 edits** |

So this is **not** 18 hand-authored rewrites.

Checker wrinkles: exclude `__pycache__` / `.pytest_cache`; `field-set-equal` so ordering is free;
needs a parser per fence format (or standardization first, per the decision above).

## Acceptance

- All four README edges pass for all 20 skills, **proven by a runnable check**, not asserted.
- The `find`-diff check is wired so the counts cannot go stale silently again — #244's numbers
  drifted within a single plan-cycle.
- No file in the repo directs a reader to `install.sh` / `install.py`.

## Related

- **#244** — the original README-contract drift report (superseded by the numbers above).
- **#247** — `install.sh`/`install.py` do not exist (shares this plan's second half).
- **#273** — the command-vs-obligation law: why the fix must be a command, not better prose.
- **#312** — process-audit stage; the enforcement half is noted there.

