---
type: Finding
okf_spec: OKF-PLAN
id: exp-005
status: complete
---
# EXP-005 — Is #135 mechanically detectable, or only avoidable by convention?

**Question:** Can a check distinguish a stale corpus-measurement literal from a deliberately
frozen one, or from a coincidental number?

## Approach Tested

Read #135 upstream; re-measured all three claimed plan-048 instances against the live tree;
surveyed the whole corpus for denominator literals and classified each *presented-live* vs
*explicitly frozen*, cross-cut by bundle `status`; measured the coincidence noise floor; read all
three candidate mechanisms in source; built a mutant harness for the recommended check.

## Result

**1. The three instances, re-measured today** — the corpus is **49** plan dirs now, not 48.

| # | As written | Live today | Drift |
| :-- | :-- | --: | :-- |
| (a) | `48` plan dirs (`47` in findings) | **49** | +1 / +2 |
| (b) | `112` review passes | **119** | +7 |
| (c) | `174 of 744` → `180` → `726` post-work | **743** | +17 |

- **measured:** the +7 on (b) is *exactly* plan-048's own seven passes. Self-join confirmed as the
  whole cause.
- **inferred:** all three are **narrative-only**. The *shipped* artifacts were re-based —
  `review.toml:3` already reads `# MEASURED over 119 files (2026-08-19 …)`, and `finding.toml`'s
  three literals re-measure as **still exactly correct**. **The defect lands on prose, not code.**

**2. Corpus survey — 41 literals, 2 actually wrong**

- **measured:** 41 denominator literals exist; **41 of 41 (100%) disagree with today's 49**.
- **measured:** **39 of 41 live in `status: complete` bundles** — historical records, correct when
  written. **Re-basing them would falsify them.**
- **measured:** only **2 of 41** live in an in-flight bundle, and both are in **plan-049's own
  plan.md** (`:25`, `:36`, "24 of 48 plans").

**3. Coincidence noise floor.** **measured:** 8,859 bare 2–4-digit integers in the corpus; **214**
equal one of today's live counts by coincidence. A "number matches a corpus count" check has
**~0.9% precision**. The `N of M plans` grammar lifts it to ~5%. Only in-flight scope reaches 100%.

**4. The three mechanisms**

| | Verdict | Evidence |
| :-- | :-- | :-- |
| **`measured:` marker convention** | **Reject** — repeats the failure it is modelled on | `finding.toml`'s epistemic marker, mandated as a "hard output contract", stands at **7 of 129 (5.4%)**. On corpus figures it would open at **83% violation, of which 39/41 are correct behaviour** |
| **`derive_from`** | **Not expressible** | `doc_lint.py:110-122` returns a list of *section names*; consumed only by heading checks. No numeric path, no in-prose substitution point, no render step in `plan.md` |
| **Self-exclusion** | **Correct by construction — but it is not a check** | Self-excluding plan-048 keeps (a) at 47 and (b) at 112 stable for the plan's whole life. **Prior art in-repo:** plan-048's SC1 already self-excludes. `plan_extract.py:522-525` has no `--exclude` flag, so there is no enforcement point yet |

**5. The distinguishability problem, exactly.** A stale literal and a deliberately-frozen one are
**byte-identical**. The only signal is authorial intent, which must be *declared* — i.e. mechanism
1, measured at 5–17% adoption. **The escape is not a better discriminator; it is a better scope.**
`status: complete` is already a declaration that a bundle's figures are history.

- **measured:** the scoped check today → `examined: 2, FIRES: 2`, both true positives, **zero false
  positives**.
- **measured, incidental defect:** `plan-026/plan.md` records `**Status:** complete`, not YAML
  `status:`. A status-scoped check must read **both** formats or it re-admits old bundles.

**6. The mutant — the check is denominator-only**

```
CONTROL (denominator stale): "…across 24 of 48 plans."  -> FAIL [(48,49)]  caught
MUTANT  (denominator fixed, numerator stale): "…24 of 49" -> PASS (green)  MISSED
```

The numerator requires *running the measuring tool*, which the check does not do. **This is not
hypothetical — it is instance (c)**, a numerator drift. **The scoped check catches (a) and (b) and
misses (c): 2 of 3.**

## Implications for Plan

- **D-3's inclusion is sound, but #135 as filed over-scopes the defect by ~20×.** The standing
  population is **2 literals in one in-flight plan**, not 41. An issue written against "#135 across
  the corpus" spends its budget re-basing 39 historically-correct numbers — a net harm.
- The issue's own second suggested direction (flag numeric literals that look like measurements) is
  **measured at 0.9% precision** and should be recorded as rejected-with-evidence.
- Its third direction (figures live in `findings/` with a stamp) is **already de-facto practice and
  is not the failure point** — the shipped artifacts are correct; `plan.md`'s narrative *copies*
  went stale. That argues for self-exclusion plus a narrow detector, not more stamping.
- **Risk carried:** the detector is denominator-only and must ship with that limit stated, or its
  green will be read as "no stale literals", which the mutant shows is false.

## Recommendations

1. **Self-exclusion primary; a narrowly-scoped lint rule secondary. Reject the corpus-wide
   convention and `derive_from` outright.**
   - *Primary:* add `--exclude <glob>` to `plan_extract.py` and `doc_lint.py`; have intake default
     corpus measurements to exclude the plan being written. It prevents the class without judging
     anything, so **it cannot fire on correct behaviour**.
   - *Secondary:* one rule **gated on `status != complete`**, skipping `findings/` and `reviews/`,
     matching `N of M plans|dirs`. Ship at **`W`, not `E`** — the bundle it judges is the one still
     being edited. Read **both** status formats.
2. **State the mutant as the check's declared blind spot** in the closing comment: denominator drift
   is caught, numerator drift is not.
3. **Verdict: closable by a mechanical check, but only narrowly scoped — catching 2 of the 3 cited
   instances.** Unscoped, a naive check fires **41/41, with 39 correct-behaviour false positives**
   — decisively worse than the defect. If the plan cannot afford the self-exclusion work, close
   #135 as won't-fix with this survey attached rather than ship the corpus-wide check.
