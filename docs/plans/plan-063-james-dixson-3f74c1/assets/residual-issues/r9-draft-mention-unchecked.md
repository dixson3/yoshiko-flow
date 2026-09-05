**Found by plan-063's own landing (RE-004). Cost: a mid-landing halt with six issues already
written, plus six additional public comments to recover.**

`land --dry-run` enumerates every upstream row and reports whether its draft body exists:

```python
"requires_mention": bool(req.get("requires_mention")),
"draft_body_path": draft_rel,
# ENUMERATED, never assumed. An omission here is SILENT (REQ-LAND-003) ...
"draft_present": draft_rel in present,
```

L7 then posts each body and verifies the write by read-back, comparing the posted comment against
the draft it was given. **Neither check verifies the one property the draft must actually have.**

`_verify_row` requires, for any row whose `requires_mention` is true, that some comment mention the
plan — via `_mentions_plan_id` (`plan_manager.py:2621`), which **normalizes and searches for the
FULL plan id**:

```python
def _norm(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())
needle = _norm(plan_id)
```

Plan-063's six drafts named the plan as `plan-063`. That normalizes to `plan063`, which does not
contain the needle `plan063jamesdixson3f74c1`. So all six were checked for **existence**
(`draft_present`) and for **fidelity to themselves** (L7's body match), and the check that would
have failed them ran only at L10 — *after* eleven irreversible writes to five closed issues and one
open one.

**This is the vacuous-check family (#263) one level up.** Neither check is wrong; both verify a
property *adjacent to* the one that matters. A green `draft_present` reads as "the drafts are
ready" when it means only "files exist at these paths".

**Measured cost.** `land --apply` reached L10 and halted:

```
verify-reconcile exited 1. HALTING: completion stops here and `complete` is NOT set.
  #340 (include): #340 is CLOSED but no comment mentions plan-063-james-dixson-3f74c1
  ... (all six rows)
```

Recovery required operator authorization for six further public comments, then a resume — which hit
a second, unrelated halt (see the companion issue on `LAND_DIGEST_EXCLUDED`).

**Proposed fix.** At the site above, for rows where `requires_mention` is true, read the draft body
and evaluate it against the same predicate L10 will use; report the row as failing when it does not
satisfy it. The predicate already exists and the row already carries both `requires_mention` and
`draft_body_path` **on adjacent lines** — only the binding point is missing.

Consider also whether `_mentions_plan_id` should accept a documented short form. It should not: the
short form is ambiguous across plans (`plan-063` matches any `plan-063-*`), and the check exists to
prove *this* plan reconciled the issue. The fix belongs at the dry run, not in the predicate.
