---
type: Review
okf_spec: OKF-PLAN
id: pass-11
status: complete
---

# Red-team pass 11

## Verdict: REVISE

Ninth independent pass (cycle 11 of 12), against `c32ab1b`. All ten pass-10 resolutions were
verified **by execution** in a sandbox clone; **eight of ten hold exactly as claimed and were
reproduced**. Two blocking defects remained, both instances of the mechanism pass-10 itself named:
the fix edited the leaf (Issue 2.2 / 2.2a) without walking up to the artifacts that enumerate over
it (SC6, Issue 2.3). Three satellite files were likewise not walked. All twelve concerns resolved
below; no concern was deferred.

## Strengths

- **C92's prescribed fix was BUILT and verified, not reasoned about.** The reviewer rewrote
  `DOC-LINT.md` per 2.2a and measured: before the SC17 assertion edit, `test_doc_lint.py` → exactly
  `1 failure(s)` naming SC17; after, `all passed` and the FAST tier green
  (`doclint-tests: ok`). **2.2a is precise enough to execute without guessing.**
- **C96's measurement reproduces exactly** — an empty selected `plan.md` gives `verdict FAIL`,
  **6 `E`-severity findings**, rc 1. Putting `empty` on the lintable side is correct.
- **SC24's figures are live and exact**: 34 titles, **27** carrying code spans; **35** continuation
  bullets, **0** carrying prose. C99's correction is right and the detail arm is honestly stated as
  an expected-zero negative observation.
- **Structure mechanically clean**: 28 issues, 41 edges, `unparsed: []`, 0 dangling, no cycles;
  `Discharged-by` sound in **both** directions; portability audit **zero findings**; FAST tier green.
- **Every line citation in `plan.md` is live** — all eight re-resolved to the symbol or line claimed.
  The 757 baseline reproduces exactly while the unfiltered figure drifted again (828 → 829), which is
  precisely why 0.2a records only the excluded number.
- C93 verified: the six control ids appear verbatim, no variant spellings, `neg-179-open-wrapper`
  correctly excluded from `controls.txt`.
- The upstream table was walked against `_verify_row`'s **live branches** rather than the plan's
  description of them: 6 `include` / 4 `partial` / 4 `deferred` / 2 `exclude` / 1 `tracker`, all
  reachable, `exclude` correctly pre-filtered, `deferred`'s no-mention rule correctly relied upon.

## Concerns

| Concern | Severity | Resolution |
| :-- | :-- | :-- |
| C111 — SC6 still said `empty` → **exit 1**, which C96's fix made false; and the dangerous branch was the *passing* one, since 2.1's fixture asserted classes only, so a classifier exiting 1 on `empty` passed both and silently reinstated the removed skip semantics | high | **Fixed.** SC6's empty arm now reads **exit 0**; the headline restated to "four states, **two of which** the lint reports identically". 2.1's `empty` arm now asserts the exit code too, so the fixture — not only the prose — pins it |
| C112 — "zero edits to `_shared/test_doc_lint.py`" survived in Issue 2.3 and SC6, which 2.2a made false; 2.3 runs strictly after 2.2a, so its stated expectation was unsatisfiable at the point it is checked | high | **Fixed.** Both scoped to "zero edits **beyond 2.2a's SC17 rule-text assertion**". SC6 additionally notes 2.4 depends only on 2.2, so the pre-2.2a reading is legal too — the qualification makes the criterion satisfiable either way |
| C113 — `context.md`'s surface list was stale in **two** directions: it asserted `test_doc_lint.py` is "deliberately NOT on this list", and omitted Epic 7's two `plan_extract.py` surfaces entirely | med | **Fixed.** Rewritten to put the file on the list **for 2.2a only** (SC42 stays true unedited; SC17's rule-text assertion must be repointed), and both Epic 7 surfaces added |
| C114 — `upstream-triage.md` carried the #187 relevance claim pass-10 C99 measured false, and still said "the **four** mechanical fixes (#178-#181)" against `plan.md`'s six | med | **Fixed.** Both rows mirrored from `plan.md`'s authoritative table; the #187 note now states the re-measured **0 of 35** and explains why the defect is real but does not bite this bundle |
| C115 — `findings/exp-003-silent-green.md` still recorded the SUPERSEDED `--require-selection` design as what ships, contradicting 2.2 in its own words | med | **Fixed.** Second banner added — **SUPERSEDED at pass-10 (operator redirect), recorded at pass-11** — naming the classifier redesign and the correct issues (2.2 + 2.2a) |
| C116 — Issue 7.2's central factual claim was **false**: there are **two** title-capture call sites (`EPIC` `m.group(2)` and `ISSUE` `m.group("rest")`), not one, and SC21/SC24 both cover epic names | med | **Fixed.** 7.2 now names **both** sites and requires both to change, recording that the reviewer refuted the single-site claim by spike. 7.1's fixture would catch a half-fix, which is why this was recoverable |
| C117 — C94 dropped the `REQ-DATA-024` amendment on verdict grounds, but REQ-DATA-024 also fixes the **exit contract** as "binary at every binding point"; after 2.2 the same executable exits 0 on a document with 6 `E` findings | med | **Fixed.** One amendment restored in 0.1, **scoped to the exit-contract sentence and not to verdicts** — C94/C95's verdict reasoning stands unchanged. An amendment adds no id, so SC1's six still holds |
| C118 — SC6b said "branches on **its exit**", the wording C97 replaced; as written it was *satisfied* by the exit-only branch 2.2 forbids | low | **Fixed.** Now "branches on **the `class` it returns**", with the note that the old wording would have passed the forbidden design |
| C119 — 0.2's manifest-count assertion named no source of truth; a hard-coded `6` would be a **third** enumerating literal, the artifact class C93 was filed about | low | **Fixed.** The count is now specified as **derived by grepping `plan.md` for `ctl-*` ids** |
| C120 — `not-selected` = "not lintable" is not universally true; `plan_manager.py` deliberately re-lints a bundle's `plan.md` with the type **forced**, so such a path *is* lintable by that route | low | **Fixed.** One clause added to 2.2: `not-selected` means *not selected by path routing*; a `--type`-forced lint is unaffected |
| C121 — the Objective and `index.md` described only the D-9 narrowing, in a plan whose scope is now six, with no mention of D-10 | low | **Fixed.** Both now read "…then **widened back to six** by D-10 (#186, #187)" |
| C122 — five pass-10 deferrals still open: C103 (`--root` documentation half unscheduled), C105 (#181 `Resolved By` vs Notes), C106 (SC11-SC14 gap unannotated), C108 (§5.2a's `_shared/` path does not resolve in an installed skill), C109 (D-5's re-measure range) | low | **All five resolved, none re-deferred.** C103 → 2.2a documents the `--root` form; C105 → `Resolved By: 2.2, 2.2a`; C106 → gap annotated, **and the first annotation written was wrong** (it said "Epic 5's") — corrected against `d40e1a3^` to SC11/SC12 = Epic 4, SC13/SC14 = Epic 5; C108 → 7.3 repoints §5.2a at the installed `scripts/` path; C109 → D-5 extended to #186/#187 |

## Missing

- Nothing structurally absent. Every issue has a producer, every criterion a discharger, every gate a
  reachable Condition, and the portability audit is clean.
- The one enumeration gap found — C117's dropped `REQ-DATA-024` amendment — was an **amendment**, not
  a missing id, so SC1 remained sound at six throughout.

## Gate Assessment

Clean and mechanically verified. `Blocks: {1.4, 2.4, 3.4, 7.4}`; every named producer is an ancestor
of a blocked issue, none sits inside `Blocks`, no cycle across 41 edges, and the gate is correctly
frontloaded to the earliest legal position. C93's fix closed the gap pass 10 found — `controls.txt`
enumerates all six ids, so the executable and the Condition prose now agree. C119 named the
manifest-count assertion's source of truth, which was the one thing still unstated. The 0/1/2 contract
and its "no engine executes this `Test`" disclosure remain honest.

## Upstream Assessment

Still the strongest part of the bundle, and this pass walked every row against the **live**
`_verify_row` source rather than the plan's description of it. The two factual errors were in the
**satellite**, not the table (C114). Because 6.2 drafts comment content and 6.4 performs closes from
the generated grant rather than from the triage note, neither could corrupt reconciliation — they
could corrupt what gets posted upstream, which is why they were medium rather than low. Both fixed.

## The mechanism worth naming

**Eighth consecutive round of the self-injected-remedy class**, and this time both injections landed
in the *same two artifacts* — SC6 twice over (C96's exit code, C92's "zero edits") and Issue 2.3.

Pass-10's proposed countermeasure — "does the new issue appear in the gate's manifest, 0.1's REQ list,
an SC, and the Objective's count?" — **held for what it covers**: Epic 7 is now enumerated everywhere.
It covers **added issues** and does not cover **changed contracts**.

The generalisation this round adds: **when a fix changes what an issue CLAIMS, grep the bundle for the
claim's own words** — `exit 1`, `zero edits`, `four`, `--require-selection`. The claim is restated
verbatim in the criterion that scores it, in `context.md`'s surface list, and in the finding it came
from. Four of this pass's twelve concerns (C112-C115) were found by exactly that grep, and one more
(C106's mis-annotation) was caught in the *resolution* pass by checking a claim against `git` instead
of writing it from memory.
