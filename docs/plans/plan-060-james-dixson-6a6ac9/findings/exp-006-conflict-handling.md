---
type: Finding
okf_spec: OKF-PLAN
description: 'EXP-006 — apply-path conflict behaviour, measured. A clean preview does NOT guarantee a clean apply, and the manifest digest already detects the drift provided the predicted merge tree is one of the facts it covers.'
---
# EXP-006: Conflict handling on the apply path

## Approach Tested

**Question.** The plan covers conflicts on the **preview** side only. What does `land --apply` do
when the *real* merge conflicts — and does a clean preview guarantee a clean apply?

**Method.** Two sandbox git spikes in `$(mktemp -d)`, throwaway repos, no network. Spike 1
characterises preview / merge / abort mechanics. Spike 2 reproduces the staleness edge directly:
preview clean, target advances, same merge applied.

## Result

### F1 — `git merge-tree --write-tree` predicts conflicts and does not touch the working tree

```console
$ git merge-tree --write-tree main feat
merge-tree exit=1 (CONFLICT PREDICTED)
69549fb3c3ab25e619dea4e568bfea179ba9a164
100644 a29bdeb...  1  f.txt
100644 e5cdc04...  2  f.txt
100644 2eb1f39...  3  f.txt
Auto-merging f.txt
CONFLICT (content): Merge conflict in f.txt

$ git status --porcelain
                       # <- empty: the preview did NOT mutate the working tree
```

**measured:** exit 1 on a predicted conflict, exit 0 with the merged tree oid on a clean one, and the
working tree is untouched either way. This confirms Issue 1.2's design.

**Honest caveat, recorded rather than glossed:** `--write-tree` *does* create an **unreferenced tree
object** in the object database. It changes no ref, no file and no working-tree state, and it is
garbage-collectable. SC6's wording (`git status --porcelain` empty, no bead mutated) is therefore
exactly right and does not overclaim — but a criterion phrased as "the dry run writes nothing at
all" would have been **false**, and would have been the kind of unfalsifiable-by-inspection claim
this plan exists to avoid.

### F2 — What a real conflict leaves behind, and that it aborts cleanly

```console
$ git merge --no-ff feat -m m
CONFLICT (content): Merge conflict in f.txt
Automatic merge failed; fix conflicts and then commit the result.     # exit 1

$ git status --porcelain                 -> UU f.txt
$ git status --porcelain=v2              -> u UU N... 100644 100644 100644 100644 <o> <a> <b> f.txt
$ git diff --name-only --diff-filter=U   -> f.txt
$ test -f .git/MERGE_HEAD                -> MERGE_HEAD YES (merge in progress)
$ git rev-parse MERGE_HEAD               -> 6c9a5615...

$ git merge --abort                      # exit 0
$ git status --porcelain                 # <- empty: fully restored
```

**measured:** the conflicted state is fully enumerable (`--diff-filter=U` for the path list,
`--porcelain=v2` for the per-path stage detail, `MERGE_HEAD` for the incoming commit) and **fully
reversible** via `git merge --abort`. So a conflict is a *legible, recoverable* halt, not a wedge.

### F3 — THE OPERATOR'S EDGE, REPRODUCED: a clean preview does NOT guarantee a clean apply

```console
=== T0: preview BEFORE the target moves ===
preview: CLEAN (exit 0)
predicted merged tree: b41d872c986aad7b2959f369dada360df84b8a25

=== the target advances (another plan lands) ===

=== T1: the SAME merge, now applied ===
apply: CONFLICT (exit 1)      <-- the preview said clean
UU f.txt
```

**measured:** preview clean at T0, conflict at T1, with nothing changed about the plan branch — only
the target moved. **The operator's suspicion is correct and is not a theoretical edge.**

### F4 — The mechanism that already detects it

```console
=== T2: does the predicted TREE still match after the target moved? ===
re-preview:  3ba3bd423a4f20dad92c8c3fdc6c04538474aeba
T0 preview:  b41d872c986aad7b2959f369dada360df84b8a25
DIFFERENT -> a digest over the preview DETECTS the drift
```

**measured:** the predicted merged-tree oid changes when the target moves. So **the
`manifest_digest` re-derivation the plan already specifies is the answer to the staleness edge** —
*provided the predicted merge tree oid is one of the facts the digest covers*.

**inferred:** this is a schema requirement, not a new mechanism. `facts.git.merge_preview` must
carry `predicted_tree` (and the resolved target tip), so a target that moved between `--dry-run` and
`--apply` produces a digest mismatch and halts **before the merge is attempted** — rather than
being discovered as a conflicted working tree afterwards.

### F5 — Where conflicts can occur, relative to the first outward-facing write

Under this plan's L-order:

| Step | Can conflict? | Precedes the first outward write (L6)? |
| :-- | :-: | :-: |
| L1 down-merge of target into the execute branch | **yes** | yes |
| L2 `merge --no-ff` into the target | **yes** | yes |
| L5 push #1 rejected -> `pull --rebase` | **yes** | yes |
| L6 onward | no (no further merge) | — |

**measured from the plan's own order:** all three conflict sites precede L6. **Nothing
outward-facing has happened when a conflict occurs**, so the recovery is purely local: abort, report,
hand back.

**inferred, and this is the sharpest consequence:** the hazard of "conflicting *after* the
irreversible steps" is real — but it is a property of **#301's** order, not this one. #301 runs the
document close at step 1 and bead close-out at step 3, both *before* its merge at step 4. A conflict
there strands a plan marked `complete`, with its beads closed and its comments posted, and an
unmerged branch. **This is a fourth independent reason #301's ordering is wrong**, alongside the
three in EXP-004 F7, and it was found by taking the operator's question seriously rather than
answering it from the plan as drafted.

## Implications for Plan

**measured:** a clean preview is not a guarantee, so `--apply` must **re-preview** immediately before
merging, not merely trust the manifest.

**measured:** a conflict is enumerable and abortable, so the verb never needs to attempt resolution —
it can always produce a complete, legible description of the conflicted state and restore the tree.

**inferred:** the operator's leaning — pass the problem back to the agent rather than resolve it in
the verb — is the right call and is also the *only* safe one. An auto-resolution strategy
(`-X ours` / `-X theirs`, or any heuristic) silently discards one side's work, and the discarding is
invisible in the resulting commit. The verb has no basis for choosing; the agent, with the plan and
both diffs in hand, at least has one.

## Recommendations

1. Add `predicted_tree` and the resolved target tip to `facts.git.merge_preview`, so the digest
   covers the fact that actually drifts.
2. **Re-preview at apply time**, immediately before L2, and halt on any change since the decision was
   minted — reporting the digest mismatch, not just the conflict.
3. **Never auto-resolve.** No `-X ours`/`-X theirs`, no `--strategy` override, no heuristic. On
   conflict: capture `--diff-filter=U`, `--porcelain=v2` and `MERGE_HEAD`, write the journal state,
   `git merge --abort` to restore, and HALT with the full picture handed back.
4. Make the abort-vs-leave-conflicted choice **empirical**, via the operator-requested test-case
   matrix, rather than deciding it now. Leaving the tree conflicted aids inspection; aborting
   guarantees a clean restart. Both are defensible and the matrix is how to find out which is right.
5. State in the schema that `--write-tree` creates an unreferenced ODB object, so no criterion
   claims the dry run "writes nothing at all".
