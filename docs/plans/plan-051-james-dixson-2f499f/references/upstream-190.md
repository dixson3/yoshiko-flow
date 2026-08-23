---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #190: Require plans to ship tests for code they write, at >= 80% coverage of that code — with a recipe row that enforces it

- **Number:** 190
- **Title:** Require plans to ship tests for code they write, at >= 80% coverage of that code — with a recipe row that enforces it
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/190
- **State:** OPEN
- **Labels:** 

## Body

## Proposed policy

**Code written as part of a plan ships with tests, at >= 80% coverage of the code that plan wrote.**

Today this is convention, unevenly applied, and enforced by nothing. #189 measures the result: six shipped scripts with no tests at all, two of which are themselves `CHANGE-VALIDATION.md` checks.

## Scope: the code the plan wrote, not the repo

The threshold must be **per-change**, not global. A repo-wide 80% gate would either block every plan until a historical backlog is paid down, or be waived immediately and become another rule nothing executes. Per-change is the form that can actually hold, and it ratchets: every plan leaves the repo better covered than it found it.

## The blocker to state up front: there is no coverage tooling

```
$ grep -rn "coverage\|pytest-cov\|--cov" CHANGE-VALIDATION.md pyproject.toml
(no output)
```

No `pytest-cov`, no coverage row in either tier, no baseline. **This issue cannot be closed by writing the policy into a document** — that would reproduce the exact defect this repo keeps rediscovering, and which research 004 ranks as its headline: *a written rule that nothing executes is unreliably obeyed, and no exit code records the skip.*

So the work is, in order:

1. **Add coverage tooling** and record a baseline per script directory. Nothing is enforced at this step; the number is just measured and written down.
2. **Add a `CHANGE-VALIDATION.md` recipe row** that computes coverage over the diff's touched Python files and exits non-zero below the threshold. FULL tier — coverage over a change-set is not a per-edit cost.
3. **Then** state the policy, pointing at the row that enforces it.

Doing 3 before 1 and 2 is the null change the corpus warns about.

## Design questions worth settling before implementation

- **What counts as "the code this plan wrote"?** Cleanest mechanical definition: lines added or modified by the plan's merge commit, i.e. diff-scoped coverage rather than file-scoped. File-scoped punishes a one-line fix to a large untested file — which would discourage exactly the small corrective changes we want.
- **What is the escape hatch, and is it recorded?** Some code is genuinely hard to cover (network-facing, live-DB repair paths). An exemption should be a declared list with a stated reason per entry, not an ambient waiver — the same treatment D-8 gives unenforceable prose in `plan-050`.
- **Does 80% assert anything about test quality?** No, and the policy should say so plainly. #188 documents a 62-assertion suite that would score high coverage while asserting nothing about payload fidelity — the exact blind spot #186 and #187 lived in. **Coverage is a floor on what was executed, never evidence that the assertions are meaningful.** These two issues are complements: #189 closes gaps, #188 makes the assertions worth having, and this one keeps new code from adding to either problem.

## Suggested home

`AGENTS.md` (a repo-wide engineering rule, beside the SPEC-first mandate) with the mechanism in `TESTING.md` and the enforcement in `CHANGE-VALIDATION.md`. `yf-plan`'s review step could additionally check that a plan touching `*.py` names its test issues — but the recipe row is the load-bearing part.

## Provenance

Requested by the operator while resolving #186/#187 into `plan-050-james-dixson-d0414b`, alongside #188 (the blind-spot class) and #189 (the coverage gaps). Filed for a future plan; deliberately not folded into plan-050.
