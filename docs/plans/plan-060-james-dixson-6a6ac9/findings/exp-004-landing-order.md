---
type: Finding
okf_spec: OKF-PLAN
description: 'EXP-004 — the correct execution order for `land --apply`. Measured verdict: neither SKILL.md''s Phase 6 order nor issue #301''s six-step order is correct, they fail differently, and no single-push total order can satisfy all four constraints.'
---
# EXP-004: The landing order — both documented orders are wrong, and differently

## Approach Tested

**Question.** What is the correct execution order for `plan_manager.py land --apply`, and is #301's
six-step order internally consistent with the SKILL.md Phase 6 it says to keep "unchanged"?

**Method.** Full read of `SKILL.md` §6.1–§6.4 with read/write polarity per step; implementation
reads of `verify-reconcile`, `recheck-criteria`, `validate-merged`, `complete-gate`, `_repo_root_for`;
`spec/phases.md` REQ-COMPLETE-001; `test_close_contract.py --list-steps`; git-topology
reconstruction of the plan-057 and plan-059 landings; **two sandbox git spikes** in `$(mktemp -d)`.


## Result

## F1 — MEASURED: SKILL.md's order structurally leaves `status: complete` uncommitted and unpushed

§6.4's terminal `update-status complete` writes `plan.md` + `log.md`. Under SKILL.md's documented
order that write happens **after** §6.2's push. Nothing commits it.

**Ground truth, plan-057:**

```
a667865  2026-08-29 16:19:38  Merge plan-057: OKF part 2 — ... (parents db07528 2e31cc6)
4f4bd94  2026-08-29 16:22:18  plan-057: operator-directed completion; follow-ons #294 #295
  docs/plans/plan-057-.../plan.md | 4 ++--
    -status: reconciling
    +status: complete
```

`status: complete` landed as an **extra hand-written commit directly on `main`, 2m40s after the
merge**. The merge itself carried `status: reconciling`. That extra commit *is* the manual repair
for a defect the documented order guarantees.

**Sandbox spike A** (throwaway repo + bare origin) reproduces it independently:

```
=== push done. now 6.4 update-status complete writes plan.md:
 M docs/plans/plan-999/plan.md
=== origin's copy of plan.md:
status: reconciling
=== left-right origin/main...HEAD: 0	0
```

`0 0` — the working tree is not even *ahead*. The write is a dirty file with nothing tracking it, so
no "unpushed commits" check would ever surface it.

## F2 — MEASURED: plan-059 did NOT follow SKILL.md's order, and ended clean

```
61ddbaa  parent 5c2e26b   plan-059: COMPLETE — SC5 amended and re-fingerprinted, §6.4 chain green
c04b071  parents a3add5f 61ddbaa   Merge plan-059: yf-judgement ...
git merge-base --is-ancestor 61ddbaa c04b071  ->  IS ancestor
```

plan-059 ran reconcile writes (14:12), then the close chain, committed `COMPLETE` **on the plan
branch** (14:21), and **then merged** (14:29). That is **#301's order**, not SKILL.md's — and it left
nothing uncommitted.

> **The two most recent landings used two different orders, and only the one that deviated from the
> documented order ended clean.** This is the single strongest piece of evidence that Phase 6's
> written order is not the order that works.

## F3 — `verify-reconcile` genuinely requires the comments to be posted first (#301 is right here)

`_gh_issue_view` (`plan_manager.py:2598-2637`) fetches `state,stateReason,comments,title` **live**,
and `_mentions_plan_id` scans comment bodies. `UPSTREAM_REQUIREMENTS` sets `requires_mention: True`
for `include` and `partial`. The check is network-bound against live upstream state.

**Reconcile writes must precede `verify-reconcile`. #301 is correct on this edge.**

## F4 — `recheck-criteria` IS tree-sensitive and must read the merged tree

`_repo_root_for` (`plan_manager.py:3189`) resolves via `git rev-parse --show-toplevel` **from
`plan_dir`** — i.e. whichever address space the bundle is read from. plan-057's criteria are heavily
tree-sensitive and several are **corpus-wide**, so they depend on what *other* plans landed:

- `SC19`: `okf_hygiene.py audit --root docs/plans --root docs/research --require-legacy 0 --min-roots 64`
- `SC7`: `check_okf_index_drift.py --min-roots 60`
- `SC3`: index-boilerplate ratio over a frozen 25-bundle set
- `SC5b`: `_shared/sync.py --check`
- `SC24`: `verify-reconcile … -> exit 0` — so `recheck-criteria` **transitively depends on the
  reconcile writes too**

plan-057's D-13 required plan-059 to land first for `index.md` contention — cross-plan tree coupling
is measured, not theoretical.

## F5 — Spike B: a down-merge makes the branch tree byte-identical to the merged tree

```
--- CASE A: no down-merge
branch tree=58b5198  merged tree=bfb758c   equal=NO
files on merged main: a.txt b.txt c.txt    files on branch: a.txt b.txt
--- CASE B: down-merge target into branch first, then land
branch tree=bfb758c  merged tree=bfb758c   equal=YES
```

**Measured:** after a down-merge of the target into the plan branch, `git merge --no-ff branch` from
the target produces a byte-identical tree. In-repo precedent: `173f8e2 Merge main (plan-059) into
plan-057 review branch — D-13 sequencing`.

So "measure on the branch" and "measure the tree that will be on `main`" are **reconcilable** —
conditional on a down-merge held under the landing lock, and only for the window in which nothing
else lands.

## F6 — NEW DEFECT (independent of #301): `CHANGED` is structurally empty

`SKILL.md:1662` computes the merged-tree changed paths as:

```bash
CHANGED=$(git diff --name-only "${MERGE_TARGET}"...HEAD)
```

But at §6.4's own documented position — after `git checkout ${MERGE_TARGET}` and the merge —
`HEAD == ${MERGE_TARGET}`. **Measured** (spike A):

```
=== after merge, MERGE_TARGET=main, HEAD=main
CHANGED (main...HEAD) = []
CHANGED (main..HEAD)  = []
CHANGED (HEAD^1..HEAD)= [impl.txt]
```

So SKILL.md's own claim at `:1672` — *"Here the merged tree exists, so a `.github/workflows/**` path
can actually match — and `evidence: path-backed` … is the only combination that carries real
weight"* — **is false as written**. `classify-deliverable` can only ever return `prose-only` at the
one binding documented as producing `path-backed`. The correct expression is `HEAD^1..HEAD` (or
`ORIG_HEAD..HEAD`).

*(Line numbers corrected from 1707/1712 after red-team pass 1 re-measured.)* This is #263's class again: a criterion documented as the strong-evidence path that **cannot fire**.
Filed separately as **#303**.

## F7 — #301's internal contradiction, confirmed by execution

`test_close_contract.py --list-steps`, run:

```
audit-close, retrospective-report, judgement-never-fired-report, classify-deliverable,
set-deliverable-class, close-reconcile-step, verify-reconcile, recheck-criteria,
close_cascade.py, complete-gate, pour_fidelity.py, update-status
```

The chain #301 calls step 1 "unchanged" **contains** `verify-reconcile` (its step 2's terminator)
and `close_cascade.py` (its step 3). **Steps 1–3 are not sequential; 2 and 3 sit inside 1.**

Worse: **`close-reconcile-step` is a bead close that runs BEFORE `verify-reconcile`**, and that
ordering is *mandated* by REQ-COMPLETE-001 constraint 2 (`spec/phases.md:94`): *"Any step verifying
the outcome of RECONCILE runs **after the reconcile bead is closed** and before the first destructive
step."*

> **So #301's blanket rule — *"A `land` verb that closes beads before running `verify-reconcile`
> automates exactly that error"* — is contradicted by the SPEC it says to leave unchanged.**
> The real hazard is narrower and must be restated: **`close_cascade.py` and `complete-gate` must not
> run before `verify-reconcile` returns 0.** It is a *gate-condition* hazard, not a
> bead-close-ordering one.

## F8 — The constraint matrix: both orders fail, differently

| Constraint | SKILL.md order | #301 order |
| :-- | :-: | :-: |
| reconcile writes before `verify-reconcile` | yes | yes |
| no cascade/gate close before `verify-reconcile` | yes | yes |
| merged-tree FULL validation before push | yes | yes |
| **FULL validation before irreversible doc/bead close** | yes | **NO** — steps 1+3 precede step 4 |
| `recheck-criteria` measures the merged tree | yes | **NO** unless a down-merge (unstated) |
| **no plan-folder write left uncommitted/unpushed** | **NO — measured red** | yes |
| artifacts incl. `status: complete` on origin before prune (#204) | **NO** | yes |
| push before reconcile (cited SHAs survive a rebase) | yes (`:1579`) | **NO** |

## F9 — PROOF: no single-push total order satisfies all four constraints

- (iii) *no write left unpushed* requires `update-status complete`'s write to be pushed
  ⇒ **a push after the close chain**.
- (iv) *completion-time measurement reads the merged tree* requires the merge to precede the close
  chain.
- `SKILL.md:1579` requires reconcile comments to cite **pushed** commits (a rebase after posting
  invalidates the cited SHAs) ⇒ **a push before reconcile**.
- F3 establishes reconcile precedes the close chain.

⇒ push-before-reconcile and push-after-close-chain are **two different pushes**. The single-push
assumption is what both documents share, and it is what breaks.

**If one push is insisted on, the constraint that must give is push-before-reconcile** — accept
comment bodies citing locally-created merge SHAs, and accept that a push rejection plus rebase
orphans them. That is #301's implicit choice, **made without stating it**. It is defensible (the
landing lock makes rejection rare; the rejection path already mandates re-validation) but it is a
real, unacknowledged trade.

## CORRECTION (red-team pass 2/3): the step labels below are PRE-RENUMBER

> **Recorded rather than silently edited**, per this bundle's convention — the table below is the
> *measured derivation*, and rewriting measured text to match a later decision would destroy the
> evidence it exists to carry.
>
> Red-team pass 2 found the step count stated three ways once an advisory pre-push criteria run was
> inserted between L4 and L5 (as `L4.5`). The plan retired the fractional label and renumbered to a
> contiguous **L0-L19**. This finding's table still uses the **original L0-L18** labels.
>
> **The map, from L5 onward — everything below L5 is unchanged:**
>
> | This finding (old) | `plan.md` (current) | Step |
> | :-- | :-- | :-- |
> | *(did not exist)* | **L5** | advisory `recheck-criteria` on the merged tree |
> | L5 | **L6** | push #1 |
> | L6 | **L7** | reconcile writes |
> | L7-L14 | **L8-L15** | the close chain |
> | L15 | **L16** | commit plan-folder writes; push #2 |
> | L16 | **L17** | residual mirroring |
> | L17 | **L18** | prune |
> | L18 | **L19** | redeploy |
>
> The **justifying edge per step** is what Issue 0.2 must carry into `spec/landing.md`, and those
> edges live in the table below — read them through this map. The Recommendations section's
> "eighteen-step order" should be read as **twenty steps, L0-L19**.

## Recommended total order for `land --apply` (two pushes, fail-closed at every edge)

| Step | Operation | Justifying edge |
| --: | :-- | :-- |
| L0 | `landing-lock acquire` | serializes merge-back (§6.1) |
| L1 | `git fetch` + **down-merge** target into `<plan>-execute` **in the worktree** | F5: makes branch tree ≡ merged tree, so any branch-side measurement is honest |
| L2 | `git checkout <target>`; `git pull --rebase`; `git merge --no-ff` (uncommitted) | §6.1 |
| L3 | `validate-merged` (FULL tier) — **halt with the lock still held on fail** | §6.1.5; must follow L2 and precede every irreversible step — **this is what #301 loses** |
| L4 | commit the merge; `landing-lock release` | §6.1.5 |
| L5 | **push #1** (`git push`; `bd dolt push` unless `dolt.local-only`) | reconcile comments cite these SHAs (`:1579`); #204 needs artifacts on origin |
| L6 | **Reconcile writes** — `gh issue comment` / `close`, each verified by **read-back** | F3 |
| L7 | close chain 1–5 (`audit-close`, `retrospective-report`, `judgement-never-fired-report`, `classify-deliverable` with **`CHANGED=$(git diff --name-only HEAD^1..HEAD)`**, `set-deliverable-class`) | REQ-COMPLETE-001 c1; fixes F6 |
| L8 | `close-reconcile-step` | REQ-COMPLETE-001 c2 — mandated **before** `verify-reconcile` |
| L9 | `verify-reconcile` (halting) | requires L6 |
| L10 | `recheck-criteria` (halting), from the primary checkout on the merged tree | F4; SC24 depends on L9's subject |
| L11 | `close_cascade.py` — first destructive step; **refuse any gate whose condition does not hold** | REQ-COMPLETE-001 c2/c3; #301's *real* constraint |
| L12 | `complete-gate` | c3 |
| L13 | `pour_fidelity.py` | bd-only |
| L14 | `update-status complete` | c4; sole status writer; terminal **in the chain** |
| L15 | **commit the L7/L14 plan-folder writes; push #2** | **the step neither document has** — closes the F1 gap |
| L16 | mirror residual open beads upstream (`external_ref` set, grouped per the decision) | outward-facing; after the tree is settled |
| L17 | **prune** — `worktree teardown`, delete branch local + remote, close the herdr tab only under #204's mechanical preconditions | harvest-before-prune |
| L18 | redeploy `yf self install --from-build --build` iff the landing touched `skills/` | AGENTS.md; must be last |

Every edge is forced by a measured dependency; none is stylistic.

## Verdict on #301's ordering: SUBTLY WRONG, in three separate ways

1. **Steps 1–3 are not sequential** — 2 and 3 are *contained* in 1 (F7). As written the order is
   unimplementable without decomposing step 1, which the issue does not do.
2. **The load-bearing constraint is stated too broadly and contradicts REQ-COMPLETE-001** (F7). The
   correct statement is about `close_cascade` / `complete-gate`, not "any bead close".
3. **The load-bearing error: merge + FULL validation at step 4, after the document close (step 1) and
   bead close-out (step 3).** #301 says *"Fail closed at any step; never proceed past a red FULL
   tier"* — but under its own order the FULL tier runs **after** `update-status complete` has been
   written and the whole execution tree has been closed. A red tier at step 4 leaves a plan marked
   complete with its beads closed and **nothing to fail closed onto**. This inverts the one thing
   `SKILL.md:1462` gets demonstrably right (*"merge-back FIRST, then validate the MERGED state, then
   push … the old order validated pre-merge, which cannot catch class-(b) integration regressions"*
   — plan-009 INV-4), and #301 discards it without citing it.

**#301 is nonetheless RIGHT about what SKILL.md gets wrong**, and F1 is the proof. The fix, though,
is **not** to move the close chain before the merge (#301's answer) but to **add push #2 after it**
(L15).

## Absence findings

- **No step anywhere** for deleting the remote branch, closing the herdr tab, or redeploying. #301's
  steps 5 and 6 are correct and uncontested; only their position relative to push #2 is at issue.
- **No check exists that could have caught F1.** An unpushed *commit* is detectable
  (`git rev-list --count origin/main..main`); an uncommitted *working-tree write* after the last push
  is not, because the branch is not ahead at all.

## Implications for Plan

**measured:** the two most recent landings used two different orders, and only the one that deviated
from the documented order ended clean. The documented Phase-6 order is not the order that works.

**measured:** no single-push total order satisfies all four constraints — the proof is in F9. Both
source documents share the single-push assumption, and that is what breaks.

**inferred:** #301 is right about the defect and wrong about the remedy. The fix is not to move the
close chain before the merge, which sacrifices the FULL-tier-before-irreversible-step property; it is
to add a second push after the close chain.

## Recommendations

1. Adopt the eighteen-step order in this finding; every edge is forced by a measurement.
2. Restate #301's ordering constraint correctly in the SPEC: it binds `close_cascade` and
   `complete-gate`, not "any bead close".
3. Down-merge the target into the execute branch under the landing lock, so completion-time
   measurement reads the tree that will be on `main`.
4. File the empty-`CHANGED` defect separately — it is wrong today, under today's order.
