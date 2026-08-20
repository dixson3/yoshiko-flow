---
type: Finding
okf_spec: OKF-PLAN
id: exp-003
status: complete
---

# Finding: Is `doc_lint`'s silent green fixable without breaking path-keyed selection? (#181)

## Approach Tested

Ran `doc_lint.py --path` against three inputs whose verdicts must differ if the engine is honest:
a selected file, a nonexistent file, and a real file outside any schema's path key.

## Result

**measured**, verbatim:

| Input | `files_checked` | `verdict` |
| :-- | --: | :-- |
| `docs/plans/plan-049-.../plan.md` (selected) | 2 | PASS |
| `docs/plans/NO-SUCH-PLAN/plan.md` (nonexistent) | **0** | **PASS** |
| `AGENTS.md` (real, unselected) | **0** | **PASS** |

The last two rows are **byte-identical**. A caller cannot distinguish "this file is clean",
"this file is not covered by any schema", and "this file does not exist".

**inferred:** `files_checked: 0` is the *correct* answer for an unselected path — every
`document_types/*.toml` keys on a directory prefix, and non-selection is by design. The defect is
not the count; it is that **three distinct states share one verdict**, and the one a caller most
needs to detect (my file was silently not checked) is the one that looks like success.

## Implications for Plan

The approach hypothesis **holds** for #181: the correct behaviour is already computed, it simply
has no distinguishing exit code. The engine already knows which of the three states it is in —
it knows whether the path exists on disk, and it knows whether any schema selected it.

The fix is a **verdict**, not a redesign: emit a distinct value (e.g. `NOT_SELECTED` /
`NO_SUCH_PATH`) and a non-zero-but-not-FAIL exit for the unselected case. This preserves
path-keying exactly — selection semantics do not change, only their reportability.

## Recommendations

- Add the third and fourth verdicts rather than changing selection. Any change to which files are
  selected is out of scope and would perturb the corpus figures plan-048/049 established.
- The `INCONCLUSIVE = 2` convention already exists in this repo's gate discipline (exit 0 present,
  1 absent, 2 harness could not run) — reuse it rather than inventing a fourth vocabulary.
- **Driven-red fixture:** a bundle copied outside `docs/plans/` must produce a non-PASS verdict.
  That is exactly the scenario in #181's title, and it is the fixture.
