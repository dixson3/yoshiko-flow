---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #303 - yf-plan §6.4: CHANGED is structurally EMPTY post-merge
  — classify-deliverable''s ''path-backed'' evidence is unreachable at the one binding
  documented to produce it'
---
# Upstream #303: yf-plan §6.4: CHANGED is structurally EMPTY post-merge — classify-deliverable's 'path-backed' evidence is unreachable at the one binding documented to produce it

- **Number:** 303
- **Title:** yf-plan §6.4: CHANGED is structurally EMPTY post-merge — classify-deliverable's 'path-backed' evidence is unreachable at the one binding documented to produce it
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

## The defect

`skills/yf-plan/SKILL.md:1662` computes the merged-tree changed paths for the §6.4 reconcile-time
deliverable-class re-confirm as:

```bash
CHANGED=$(git diff --name-only "${MERGE_TARGET}"...HEAD)   # merged-tree paths
```

At §6.4's own documented position this runs **after** §6.1's `git checkout "${MERGE_TARGET}"` and
`git merge --no-ff`. So `HEAD` **is** `${MERGE_TARGET}`, and the diff is between a ref and itself.

**Measured** in a throwaway git repo reproducing the documented sequence:

```
=== after merge, MERGE_TARGET=main, HEAD=main
CHANGED (main...HEAD)  = []
CHANGED (main..HEAD)   = []
CHANGED (HEAD^1..HEAD) = [impl.txt]
```

`CHANGED` is empty **by construction**, on every landing, forever.

## Why it matters: the strong-evidence path cannot fire

`SKILL.md:1672` states, of this exact binding:

> **This is the one place `evidence` can be `path-backed`.** At intake `--changed` is empty, so a
> suggestion there is always `prose-only` (§4.1.5). Here the merged tree exists, so a
> `.github/workflows/**` path can actually match — and `evidence: path-backed` with
> `confidence: high` is the only combination that carries real weight.

That is **false as written**. `classify-deliverable` is handed an empty `--changed` list here, so it
can only ever return `prose-only` — the same value §4.1.5 already documents as **weak** and
explicitly tells the operator not to act on alone.

The net effect: the `ci-release` completion gate's only strong signal is unreachable at both of its
bindings. §4.1.5 says the intake suggestion is uninformative and defers to §6.4; §6.4 believes it is
informative and is not.

This is the [#263](https://github.com/dixson3/yoshiko-flow/issues/263) collapsed-signal class in its
"criterion that cannot fail" form ([#224](https://github.com/dixson3/yoshiko-flow/issues/224)): a
check documented as the authoritative path, which structurally produces one constant answer.

## The fix

The merge commit's first parent is the pre-merge target; its second is the plan branch. The changed
set the step wants is:

```bash
CHANGED=$(git diff --name-only HEAD^1..HEAD)     # or ORIG_HEAD..HEAD
```

Both are correct at the documented position. `HEAD^1..HEAD` is preferable because it does not depend
on `ORIG_HEAD` surviving intervening git operations.

**Caveat worth stating in the fix:** this is only correct while §6.4 runs *after* the merge and *on
the merge commit*. If the close chain's position relative to the merge ever changes, the expression
must change with it — which argues for computing it in `plan_manager.py` from the resolved landing
strategy rather than leaving it as prose an editor can silently invalidate.

## Provenance

Found by plan-060 (the `land` verb, #301) while establishing the correct landing order — a sandbox
git spike run specifically to test whether `recheck-criteria` and `classify-deliverable` observe the
merged tree. The empty `CHANGED` was not what the spike was looking for.

Filed separately from #301 because it is independent of the landing verb: the expression is wrong
today, under the order documented today, and stays wrong under either proposed reordering.

## Evidence

- `skills/yf-plan/SKILL.md:1662` — the expression
- `skills/yf-plan/SKILL.md:1672` — the claim it falsifies
- `skills/yf-plan/SKILL.md:1485-1487` — the `git checkout` + `git merge` that make `HEAD == MERGE_TARGET`
- Sandbox reproduction, output quoted above

🤖 Generated with [Claude Code](https://claude.com/claude-code)

> **Line numbers corrected in place (2026-08-29):** originally filed as 1707/1712; re-measured at
> **1662**/**1672**. See the correction comment below for the measurement and for a second finding
> about verifying this defect's fix.

