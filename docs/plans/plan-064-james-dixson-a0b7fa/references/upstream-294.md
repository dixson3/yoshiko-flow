---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #294 - okf index drift enumerates gitignored build residue — a clean checkout is green, a working clone is red'
---
# Upstream #294: okf index drift enumerates gitignored build residue — a clean checkout is green, a working clone is red

- **Number:** 294
- **Title:** okf index drift enumerates gitignored build residue — a clean checkout is green, a working clone is red
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/294
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

> ## The root-index enumerator walks gitignored paths
>
> plan-057's Epic 1 made the index enumeration **recursive** (rule D: enumerate a subdirectory's files iff it holds ≤ 10). That is the intended behaviour and it worked — boilerplate ratio 0.6848 → 0.3443. But the enumerator walks the **filesystem**, not the **tracked tree**, so it now reports build residue as corpus drift.
>
> ### Measured, immediately after plan-057 merged to `main` (a667865)
>
> ```
> $ uv run scripts/checks/check_okf_index_drift.py --min-roots 60
> 1 bundle(s) have root-index drift
>   005-thrash-detection-and-operator-judgement  drift  {missing: 1}
>     missing  scripts/__pycache__/finding_recurrence.cpython-311.pyc
>              "present in the bundle but absent from index.md"
> exit 1
>
> $ git ls-files <that path> | wc -l     → 0        # not tracked
> $ git check-ignore -q <that path>      → YES      # gitignored
> $ rm -rf <that __pycache__> && re-run  → exit 0   # clean
> ```
>
> So **a clean checkout is green and a working clone is red**, purely as a function of whether anyone has run a script in that bundle. `__pycache__` appears in no exclusion list:
>
> ```
> grep -c '__pycache__'  check_okf_index_drift.py → 0
>                        _shared/okf.py           → 0
>                        yf-plan/OKF-EXTENSION.md → 0
> ```
>
> ### Why it matters
>
> `CHANGE-VALIDATION.md` binds `docs/plans/**` to `okf-index-drift` in the **FAST** tier, so this fires on *every* edit anywhere under the plans corpus, on any machine carrying ordinary build residue. It is also indistinguishable at the exit code from a genuine unindexed member — the check reports `missing`, which is the same finding a real drift produces.
>
> This was invisible before Epic 1: `scripts/` was a single directory bullet, so nothing inside it was enumerated.
>
> ### Proposed
>
> Skip paths that `git check-ignore` matches, or add a default exclusion set covering at minimum `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.DS_Store`. Prefer the former — it is self-maintaining, and the existing `exclude_globs` (`assets/fixtures/**`, `findings/okf-migration-samples/**`) is a hand-written list, which this repo has already measured drifting by six in `harness-selftest.sh`.
>
> Related: #289 (nothing compares a plan's cited figures against its commands' output) is the same family — a hand-maintained list nothing checks.
>
