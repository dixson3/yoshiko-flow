---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #302 - yf-plan: plan-folder location and plan NUMBER
  are both unenforced claims — ''stays primary-side'' is false in a worktree, and
  get_next_index() is count-based so numbers collide across checkouts'
---
# Upstream #302: yf-plan: plan-folder location and plan NUMBER are both unenforced claims — 'stays primary-side' is false in a worktree, and get_next_index() is count-based so numbers collide across checkouts

- **Number:** 302
- **Title:** yf-plan: plan-folder location and plan NUMBER are both unenforced claims — 'stays primary-side' is false in a worktree, and get_next_index() is count-based so numbers collide across checkouts
- **URL:** 
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

Two measured defects in the same layer — **plan-folder identity and location** — found by observation
of plan-060's own drafting worktree. Both are instances of the class
[#301](https://github.com/dixson3/yoshiko-flow/issues/301) names: **a claim that no mechanism
enforces and no check can fail.**

---

## A — "the plan folder stays primary-side" is prose no mechanism produces

`skills/yf-plan/SKILL.md` Phase 1 states:

> The plan folder itself stays **primary-side** (under `docs/plans/` or `Incubator/<slug>/plans/`),
> so the plan artifacts are readable from the primary checkout while drafting proceeds on the
> development branch.

**Measured, during plan-060's own scoping:**

```
docs/plans/plan-060-*                                  -> ABSENT in the primary checkout
.worktrees/plan-060-development/docs/plans/plan-060-*  -> present
```

**The cause is structural, not operator error.** `make_plan_dir()` resolves the plans root against
the **git root**, and inside a worktree the git root *is the worktree*. Nothing anywhere computes a
primary-side path, so there is no code that could produce the stated property and no check that
could fail when it does not hold.

**Consequence is mild but the property is false for exactly the interval it is wanted.** Merge-back
does eventually put the folder where the prose claims — but the whole point of the sentence is that
the artifacts are readable *from the primary checkout while drafting proceeds*, which is precisely
the window in which they are not there.

Two honest resolutions, and they are materially different:

1. **Make the prose true** — `init` computes the primary-side path (`git worktree list --porcelain`
   first entry, or `git rev-parse --git-common-dir`'s parent) and writes there. This conflicts with
   `commit-plan`, which **refuses on the default branch** (`REQ-PLAN-065`) — a primary checkout
   sitting on `main` could not commit its own plan folder. Any fix must resolve that.
2. **Delete the claim** — state that the plan folder lives on the drafting branch and arrives
   primary-side at merge-back. This is what every landed plan has actually done (verified:
   `plan-059`'s folder was created by commit `4760f3d` on its own branch).

Option 2 is probably correct; option 1 is what the text currently promises. Either way the current
state — a stated property with no producer — is the defect.

---

## B — plan NUMBERS collide across checkouts, and the counter is count-based rather than max-based

`skills/yf-plan/scripts/plan_manager.py:479`, `get_next_index()`, returns `total + 1` where `total`
**counts** `plan-*` directories under the roots resolved in the **current checkout**.

### B1 — Cross-checkout collision (measured, live, right now)

```
primary checkout: 59 plan-* dirs -> next index 060     <-- would reissue plan-060
plan-060 worktree: 60 plan-* dirs -> next index 061
```

A second plan started from `main` at this moment is **also `plan-060`** — a different hash suffix,
the same number. The docstring claims *"IDs stay globally unique"*. They are unique only by the hash
suffix, and **the number is what every human and cross-plan reference uses**: "plan-057", "D-13
requires plan-059 to land before plan-057", every `docs/plans/plan-NNN-*` path, every amendment-log
bullet. A collision is not cosmetic; it silently breaks the identifier the corpus is actually
indexed by.

### B2 — `count + 1` is not `max + 1` (independent, same line)

Deleting, archiving or rehousing **any** old plan directory makes the counter run **backward** and
reissue a burned number. This is currently latent only by coincidence: 59 directories with a highest
index of 059, so count and max happen to agree. Nothing has ever been deleted, which is the only
reason this has not been observed.

`max + 1` over parsed indices is the correct rule, and it is strictly safer than `count + 1` under
every condition — there is no scenario where counting is preferable.

### B3 — Why this touches LANDING specifically

**Merge-back is precisely the moment two checkouts' plan directories meet.** A `land` verb that
merges a plan folder cannot assume its number is unique on the merge target: two independently
drafted `plan-060-*` bundles merge cleanly, because their paths differ by hash suffix, and the
result is two directories claiming the same number with **no conflict, no warning and no failing
check**. This is the collapsed-signal shape of [#263](https://github.com/dixson3/yoshiko-flow/issues/263)
in the filesystem layer.

---

## Proposed split

| Item | Where |
| :-- | :-- |
| A — reconcile the primary-side claim with reality (make it true, or delete it) | **this issue** |
| B1 / B2 — `get_next_index()` becomes `max + 1` and resolves roots across **all** worktrees, not just the current checkout | **this issue** |
| B3 — landing-time detection of a plan-number collision on the merge target | **plan-060**, in scope; `land --dry-run` reports it as a halting finding |

plan-060 (the `land` verb, #301) takes **only B3**. The counter fix and the primary-side claim are
Phase-1 concerns and do not belong in a landing plan; they are filed here so they are not lost.

## Evidence

- `skills/yf-plan/scripts/plan_manager.py:479` — `get_next_index()`
- `skills/yf-plan/SKILL.md` Phase 1 — the primary-side sentence
- `git worktree list` + directory counts, measured 2026-08-29 during plan-060 scoping
- `git log --diff-filter=A -- docs/plans/plan-059-james-dixson-55137e/plan.md` -> `4760f3d`, on the plan's own branch

🤖 Generated with [Claude Code](https://claude.com/claude-code)

