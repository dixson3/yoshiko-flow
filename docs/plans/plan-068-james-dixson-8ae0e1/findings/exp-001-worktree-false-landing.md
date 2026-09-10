---
type: Finding
okf_spec: OKF-PLAN
description: >-
  [finding] In-place landing halts at _land_manifest:8063 on bare branch existence; design (b) measured passing with zero REQ-LAND-* cost, design (c) refuted as a vacuously-green no-op merge; the bead's three-plan residue table is wrong (plan-061 ran in worktree mode)
id: exp-001-worktree-false-landing
plan: plan-068-james-dixson-8ae0e1
created: '2026-09-09'
---
# EXP-001: Where `land` halts under `execute.worktree: false`, and the candidate designs

**Question.** Under in-place mode, exactly where does `land` halt, and what are the candidate
designs for making the landing route reachable? (#331 / bead `yf-f7lq`, P0)

**Method.** Source read across every `_land_*` / `_worktree_*` site; five throwaway git repos in
`/tmp` driving `worktree ensure` and `land --dry-run` under `{"execute.worktree": false}`
(spikes A, A2, B1, B2, D, E); repo-wide grep for in-place landing tests; a delegated read of the
plan-061/062/063 bundles. All sandboxes removed; repo untouched.

## The halt

`plan_manager.py:8063-8067`, inside `_land_manifest`:

```python
br = _run_git(["rev-parse", "--verify", execute_branch], cwd=root)
if br.returncode != 0:
    halts.append({"code": "execute-branch-missing",
                  "detail": f"{execute_branch} does not exist — nothing to land",
                  "resolvable_by_agent": False})
```

The condition is *purely* branch existence. **`_land_manifest` never calls
`_worktree_opted_out()`** — the manifest has no concept of in-place mode at all. The halt is a
branch-existence check that in-place mode happens to fail. Because `--validate-decision` and
`--apply` re-derive the same manifest, `land` is unreachable end-to-end in every mode.

`_worktree_ensure` (`:4270-4273`) short-circuits on `opted-out` **before** `_worktree_viability`,
`_resolve_execute_base`, and any `git worktree add -b`. The branch *name* is well-defined
(`worktree path` still reports it); only the ref is absent.

## Which steps assume a branch — four of twenty

| Step | Status with no execute branch |
| :-- | :-- |
| L1 down-merge | **Harmful.** Never checks out the execute branch; `wt = ctx.worktree if ctx.worktree.is_dir() else ctx.root`. In-place it merges the target into whatever HEAD is. Measured: `Already up to date.`, **exit 0**, verdict `pass`, journals `L_DOWNMERGED`. A silent no-op. |
| L2 merge | **Meaningless-or-harmful.** Same silent-`pass` shape. |
| L4 commit-merge | **The only step that catches the hazard.** Asserts `HEAD^{tree} == <execute_branch>^{tree}`. Measured (B2): fails correctly, but *after* the merge is committed and the lock released, with a diagnostic about `pull --rebase` that describes something that did not happen. Fails closed, pre-push. |
| L18 prune | **Already a correct no-op.** `_worktree_teardown` returns `ok` with no worktree *and* with no branch. Needs no work under any design. |
| L19 redeploy | **Degraded.** `_land_changed_set` is `HEAD^1..HEAD`; with a no-op merge HEAD is not a merge commit, so `touches skills/` can read false on a landing that did change `skills/`. |

Digest facts need no change: `execute_worktree_present: false` and `execute_worktree_dirty: null`
are already three-valued and already in `LAND_DIGEST_EXCLUDED`.

## Two adjacent defects surfaced (in scope, not #331)

1. **L1 never checks out the execute branch**, so in-place it can self-merge and report `pass`
   (measured B2; caught only by L4, with a misleading diagnostic).
2. **`_land_merge_preview.changed_paths` uses a SYMMETRIC `git diff`** (`git diff --name-only
   <target> <execute_branch>`), so it cannot distinguish "branch ahead" from "branch behind".
   Measured (E): reported `changed_paths: ["work.txt"]` and `merge_preview.available: true` for a
   merge guaranteed to be a no-op. `touches_skills` is computed off that same list, so L19's
   precondition is predicted from a set that never merges.

## Candidate designs

| # | Design | Measured evidence | SPEC surface |
| :-- | :-- | :-- | :-- |
| **(a)** | Explicit in-place route skipping L1/L2 | `SKILL.md:1479-1481` **already specifies this for the manual path**; `land` never implemented it | **REQ-LAND-002/004/006** — the step table, the non-skippable set, the closed journal-state set. L1/L2 are in `LAND_NON_SKIPPABLE` and `_land_validate_decision` rejects skipping them, so it needs a *fourth* per-step state. Also: L3 would validate a tree nobody merged and L4's assertion loses its referent |
| **(b)** | `worktree ensure` cuts + checks out the branch even when opted out | **Spike A2: `land --dry-run` → `verdict pass`, `halts []`, exit 0.** Nothing else in the manifest needed to change | **REQ-BRANCH-001/002/004** and **zero `REQ-LAND-*`** |
| **(c)** | `land` synthesizes the branch at dry-run time | **Spike B1: turns a loud halt into a vacuously-green landing that merges nothing** — branch at target tip ⇒ L1/L2 no-op, L4 passes vacuously, full green `L_DONE` | Violates **REQ-LAND-026** (dry-run mutates nothing) outright |
| **(d)** | Keep the halt, flip `resolvable_by_agent` + attach remediation | Consumer already exists (`:8425-8432`) | REQ-LAND-034 only. But cuts the branch at *land* time = the B1 no-op case again |

**Design (b)'s two measured risks, both must be in SPEC text not just code:**
- **Create-without-checkout is silently wrong** (spike E). The `checkout -b` half is not optional.
- **`checkout -b` can refuse**: dirty tree on a divergent branch → `error: Your local changes
  would be overwritten by checkout / Aborting`, exit 1, HEAD unmoved. `_worktree_ensure` has no
  dirty-tree precondition on the in-place path today.

**REQ-BRANCH-004 is the one requirement (b) contradicts** — "the primary checkout is restored to
a known branch (never left on a plan branch)". (b) deliberately leaves the primary *on* a plan
branch for the duration of execution. That needs an explicit in-place carve-out in the same
change-set, not a silent exception.

## What the three plans actually did — the bead's table is WRONG

| Plan | Reality (measured) |
| :-- | :-- |
| **plan-061** | **Does NOT apply.** Ran in **worktree mode** (`context.md:72`), has no Issue 0.7, never mentions #331. Corroborated by git: `7dd863c Merge branch 'main' into plan-061-…-execute` exists; no Issue 0.7 commit |
| plan-062 | Issue 0.7, `plan.md:129` — `git checkout -b <plan-id>-execute main`, "**Placed SECOND, before every SPEC edit**". Criterion SC0b asserts `git rev-parse --verify --quiet` exit 0 |
| plan-063 | Issue 0.7, `plan.md:123` — same form, same ordering rationale. Commit `9e6c8a8` |

`plan-063-…/assets/residual-issues/r4-331-residue.md` (duplicated at
`assets/upstream-drafts/331.md`) claims a three-plan table including plan-061 and asserts "all
three plans edit `plan_manager.py` itself". **That is false for plan-061.** The residue is
**two** consecutive plans, not three.

**Do the workarounds pick a design? Yes — (b), in the `checkout -b` form, cut before the first
commit.** Three signals: both plans use `checkout -b` never bare `git branch`; both explicitly
justify the *ordering* ("a commit made before this branch exists lands on `main` and escapes the
merge L3 validates") — i.e. the operators had already diagnosed the B1/E failure mode; and #331's
own body ranks this fix first ("it removes the failure instead of documenting it").

## Absence findings

**There is no test anywhere exercising `_land_manifest`, `_land_execute`, or any L-step under
`execute.worktree: false`.**

| Search | Result |
| :-- | :-- |
| `grep -rn "execute-branch-missing" skills/ scripts/ docs/` (ex. `docs/plans`) | **one hit** — the emitting site. No test, no spec, no SKILL.md text |
| `grep -rn "opted-out\|execute.worktree\|in-place" skills/yf-plan/scripts/test_*.py` | 8 hits, **none about landing**. `test_worktree.py:264` stops at `_worktree_ensure`'s verdict |
| `grep -rn "in-place\|opted-out" skills/yf-plan/spec/*.md SPEC.md` | **zero hits.** The spec has no in-place landing concept at all |

`test_land_apply.py`'s injected-runner harness builds `LandingContext` from a manifest fixture —
a natural home for the missing test; the seam already exists.

## Implications for the plan

1. **L1-L4 are already on the `ctx.run` seam** (`LandingContext._dispatch:9162`). An in-place
   landing test can be written today without waiting for the L8-L15 work. The steps *not* on the
   seam are L8-L15 plus **L5** (raw `subprocess.run` of `recheck-criteria` at `:9354`) and L18
   (deliberately off-seam per REQ-LAND-031).
2. **SPEC cost differs sharply:** (b) = REQ-BRANCH-001/002/004, zero REQ-LAND-*. (a) = three of
   the most test-pinned requirements in `spec/landing.md`. (c) = retire REQ-LAND-026.
3. **(a) is complementary, not alternative.** Even under (b), stating what L1/L2 mean with no
   worktree removes the ambiguity L1's `wt = ... else ctx.root` currently papers over.
4. **(c) should be recorded as considered-and-rejected with the measurement attached**, not
   silently dropped.
5. **L18 needs no work.**
