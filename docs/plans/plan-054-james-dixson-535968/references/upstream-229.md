---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #229: redcheck.sh's YF_TREE default assumes plan-050's asset layout (#210's class, in the shared harness)

- **Number:** 229
- **Title:** redcheck.sh's YF_TREE default assumes plan-050's asset layout (#210's class, in the shared harness)
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

Found by plan-053 — and specifically by the guard plan-053 added at Issue 1.1(b), on its
**first real use**.

## The defect

The driven-red harness computes its tree-under-test as:

```bash
: "${YF_TREE:=${REPO_ROOT}/.worktrees/${PLAN_ID}}"
```

That is correct **only** when the plan's assets live in the **primary checkout**, as plan-050's
did. plan-053 keeps its assets in the **execution worktree** — deliberately, so that a fixture
and the fix it grades land on the same branch and a RED and a GREEN are observable from one
tree. In that layout `REPO_ROOT` already *is* the worktree, and the default produces the
doubled path:

```text
<worktree>/.worktrees/<plan-id>/_shared/plan_extract.py
```

which does not exist.

## Why this is #210's class

An assumption about **layout**, baked into a default that no other layout satisfies. Exactly
like `_shared/` in a `SKILL.md` invocation: correct where it was written, wrong everywhere
else. It is filed because **the harness will be copied by the next plan too** — that is how it
reached plan-053.

## How it surfaced, and why that is the interesting part

plan-053's Issue 1.1(b) made an exit-2 observation **unrecordable** rather than merely
rejected, by moving the rc check ahead of `_append`. The very first `record-red` hit this bug:

```text
ctl-206: HARNESS — no extractor at <worktree>/.worktrees/<plan-id>/_shared/plan_extract.py
redcheck: FAIL — ctl-206-dropped-continuation's fixture exited 2 (INCONCLUSIVE) ...
redcheck: NOTHING WAS RECORDED.
```

**Under the harness exactly as inherited**, `_append` ran *before* the rc check, so this would
have printed `RED observed`, returned 0, and banked a permanent `rc=2` record — certifying a
RED for a fixture that never executed a single assertion. That is R3's failure mode occurring
inside the instrument built to detect it.

## plan-053's fix, for whoever owns the canonical harness

Resolve rather than assume — probe for `.worktrees/<plan-id>/_shared` and fall back to
`REPO_ROOT`:

```bash
if [ -z "${YF_TREE:-}" ]; then
  if [ -d "${REPO_ROOT}/.worktrees/${PLAN_ID}/_shared" ]; then
    YF_TREE="${REPO_ROOT}/.worktrees/${PLAN_ID}"   # assets in the primary checkout
  else
    YF_TREE="${REPO_ROOT}"                          # assets in the execution worktree
  fi
fi
```

## Evidence

- `docs/plans/plan-053-james-dixson-4015d3/plan-retrospective.md` § RE-003 — verbatim command,
  output, exit code, and the exact `rc=2` line that would have been banked without the guard.
- `docs/plans/plan-053-james-dixson-4015d3/assets/deferred-defects.md` § D5

Filed by plan-053 Issue 7.2.

