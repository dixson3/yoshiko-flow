---
type: Reference
okf_spec: OKF-PLAN
id: sc7-remeasure
description: Issue 2.3's post-change re-measurement and the two regressions that pin the classifier design
---

# Issue 2.3 — the post-change measurement

## (a) SC7: the corpus figure did not move

| | Command | `files_checked` |
| :-- | :-- | --: |
| baseline (Issue 0.2a, before any Epic-2 change) | `uv run _shared/doc_lint.py --json --exclude 'docs/plans/plan-050-james-dixson-d0414b/**'` | **757** |
| after (Issue 2.3, at commit `5945ed9`) | *identical command* | **757** |

**EQUAL.** SC7 is discharged. The assertion is against **757** — the excluded figure — and
nothing else; the unfiltered count is diagnostic only and has drifted
817 → 820 → 828 → 829 → 830 → 832 across drafting, review and execution, one step per file
written into this plan's own bundle.

Any delta here would have meant selection was perturbed, which REQ-DATA-061 forbids: the
classifier is a **preflight**, and the lint path is untouched.

## (b) `test_doc_lint.py` — `all passed`, and the edit scope is exactly what 2.2a sanctioned

```
uv run _shared/test_doc_lint.py     ->  all passed   (exit 0)
```

`git diff main` over that file: **45 changed lines, 5 hunks, all inside the SC17 block**
(`:704`–`:765`). That is 2.2a's SC17 rule-text re-pin and nothing else — the qualification
Issue 2.3 carries, because 2.3 runs *after* 2.2a and an unqualified "zero edits" would be
unsatisfiable at the point it is checked.

**Issue 2.2's own claim was measured separately and held**: at 2.2, before 2.2a touched the
protocol, `git diff main` over `test_doc_lint.py` was **empty** and the suite reported
`all passed`. The engine change genuinely touched nothing the suite characterises. SC17 and
SC42 remained literally true, which is the property that made the preflight design viable
where three earlier scopes were refuted.

## (c) The FAST tier over a `doc_lint.py` change

```
change_validation.py run --tier fast --changed _shared/doc_lint.py   ->  pass
  uv · uv-yf-intake-lint · uv-_shared · doclint · doclint-tests · gate-cellcheck
```

This is the gate that refuted the two rejected scopes. `doclint-tests` runs in **both** the
FAST and FULL tiers, so a scope breaking SC42 or SC17 fails the on-edit gate for every
`doc_lint.py` edit — pass-8 C77 and pass-9 C86 each measured a candidate fix failing exactly
here. The preflight passes it.

The full FAST tier (44 commands, unscoped) is also green at `5945ed9`.
