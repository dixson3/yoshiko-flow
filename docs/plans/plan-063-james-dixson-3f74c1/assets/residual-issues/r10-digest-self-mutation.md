**Found by plan-063's own landing (RE-005). Every resume at or after `L_VALIDATED` is a guaranteed
digest mismatch — the landing halts on a change it made itself.**

`REQ-LAND-036` (plan-063) introduced a coverage set so the staleness digest ignores facts the
landing mutates as it runs:

```python
LAND_DIGEST_EXCLUDED: tuple[tuple[str, ...], ...] = (
    ("git", "execute_worktree_present"),
    ("git", "execute_worktree_dirty"),
)
```

Both members are there because **L18's teardown flips them mid-landing**. But `resolved_target_tip`
is flipped by **L4's merge commit and L6's push, in the same chain**, and it is not excluded.
Neither are `merge_preview.predicted_tree` and `merge_preview.changed_paths`, which the merge
likewise invalidates.

**Measured.** Plan-063's landing halted at L10, and the resume halted again immediately:

```
manifest_digest MISMATCH — decision carries 'sha256:4d8976f4...',
re-derived reality is 'sha256:dd3dd31a...'.  halt_class 5
```

A fact-level diff of the two manifests showed **exactly one changed field**:
`resolved_target_tip: eb0d859... -> 567f342...` — the merge commit the landing had just created —
with `merge_preview.changed_paths` collapsing 13 -> 0 for the same reason. The operator was routed
back to `--dry-run` for a mutation the landing performed on purpose, and recovery cost a full
re-adjudication cycle.

**The exclusion set is the WRONG place to fix this.** The source comment already says so, and it is
right about the constraint while being incomplete about the cause:

> `NOTHING ELSE BELONGS HERE. resolved_target_tip and merge_preview drift when ANOTHER plan lands,`
> `which is exactly the staleness the digest exists to detect — excluding them would make the check`
> `vacuous.`

That is an **incomplete disjunction**. The tip drifts from two causes, not one:

| cause | correct behaviour |
| :-- | :-- |
| a foreign landing moved the target | **halt** — this is the digest's entire purpose |
| this landing's own L4/L6 moved it | **proceed** — the decision is still valid |

The exclusion predicate is keyed on the **field**; the correct discriminator is the **cause**.
`execute_worktree_*` could be excluded safely only because L18 is their sole writer, so field and
cause coincide there. For the tip they do not, and adding it to the set would trade a nuisance halt
for a silent one — reopening on a new axis exactly what `REQ-LAND-036` closed.

**Proposed fix — rebase the expectation, do not drop the field.** The landing already knows the SHA
it created; it simply does not record it.

1. At L4/L6, record the resulting tip (and the post-merge preview shape) into the journal entry's
   `detail`, alongside the phase already written there.
2. On resume, compare the re-derived tip against **the journal's recorded self-mutation first**.
   Equal means self-inflicted: proceed with the decision's original digest intact. Not equal means
   foreign drift: halt exactly as today.

Equivalently: project the re-derived facts back through the journal-recorded self-mutations before
digesting, so the comparison is against *the world as this landing left it* rather than *the world
as the dry run found it*. Foreign-drift detection is preserved in full, which is the property the
current comment is defending.

**Note on severity.** This does not corrupt anything and it fails closed — but it makes the resume
path, which `REQ-LAND-011` exists to provide, unreachable past L6 without re-minting a decision. A
resumable landing that cannot be resumed after its own merge is the halt-recovery contract not
holding in the one case it was written for.
