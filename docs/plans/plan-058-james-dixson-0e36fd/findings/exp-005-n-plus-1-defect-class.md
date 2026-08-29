---
type: Finding
okf_spec: OKF-PLAN
id: EXP-005
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# EXP-005: The universe-scale N+1 is a RECURRING defect class, already remediated once

**Question.** Is `collect_parent_edges`' per-bead `bd show` fan-out a one-off bug, or an
instance of a class this codebase has already hit and fixed elsewhere?

## Approach Tested

1. Read every docstring and requirement in `upstream.py` / `SPEC.md` mentioning `bd show`, bulk
   reads, or per-bead loops.
2. Traced whether the previously-shipped remediation swept for siblings or removed only the
   instance it was filed against.
3. Counted, on the live corpus, how much the surviving lesser instance actually costs — to judge
   whether it is worth fixing or merely worth noting.

## Result

It is an instance of a class **already diagnosed, already fixed once, and already documented with
an explicit prohibition — which the defective call site violates.** The remediation this plan
needs has a working precedent in the same file.

### The precedent: REQ-BUP-052 / `external_from_row`

`upstream.py:479-491` carries a function whose docstring is a near-verbatim description of #268,
written about a *different* call site:

> ```python
> def external_from_row(row: dict) -> str | None:
>     """Read external_ref off a `bd list --json` row — no subprocess (REQ-BUP-052).
>
>     `bd list --all --json` already carries `external_ref`, so resolving it per bead with
>     `bd show` is a removable N+1. Measured on this repo (991 beads): `closable` produced
>     zero output in 4 minutes and was killed; only 20 beads had a mapping at all, so 991
>     subprocesses were spent to find 20 values the bulk query had already returned.
>     """
> ```

Three structural identities with #268:

| | `closable` (fixed, REQ-BUP-052) | `push`/`enumerate` (#268, open) |
| :-- | :-- | :-- |
| Shape | one `bd show` per bead over the universe | one `bd show` per bead over the universe |
| Presentation | "zero output in 4 minutes and was killed" | "no stdout, no stderr, no progress"; killed at 120s |
| Data already present in bulk | `external_ref` on the `bd list` row | `dependencies[]` on the `bd list` row |
| Remedy | read the field off the row | read the field off the row |

The `closable` fix was **not generalised**. It removed the N+1 from one verb and left the
identical shape in `collect_parent_edges` (`upstream.py:524`), which `cmd_enumerate`
(`:603`) and `owner_claim_warning_lines` (`:1178`) both call.

### The prohibition is already written, and is already violated

`external_for`'s own docstring (`upstream.py:468-476`) states the rule:

> "Fine for the handful of ids `mappings`/`plan_hoist` resolve; **NEVER call this in a loop
> over the whole universe** — see external_from_row (REQ-BUP-052)."

`cmd_enumerate:615` calls `external_for(bid)` inside `for r in nonactive_rows:`. That loop is
over *candidates*, not the whole universe, so it is a **lesser** instance — but it is the same
prohibited shape, and the data it fetches is on the row already.

**measured, this repo:** 84 of 1801 rows carry a non-empty `external_ref`. With 37 open beads
the `cmd_enumerate` loop is ~37 subprocesses (~7 s) rather than 1801 — an order of magnitude
below the headline defect, and invisible next to the 335 s walk that precedes it, which is
precisely why it survived.

## Implications for Plan

1. **The one-call rewrite is not a novel design.** It is the application of an existing,
   reviewed, shipped pattern (`external_from_row`) to the call site the original fix missed.
   That materially lowers the design risk of the primary fix.
2. **A point fix will not hold.** The same class has now been found twice in one file, and the
   first remediation removed the instance it was filed against without sweeping for siblings.
   That is the signature of a defect that recurs because nothing mechanically forbids it. The prose
   prohibition exists (`external_for`'s docstring) and did not prevent `cmd_enumerate:615`.
3. **A mechanical check is the durable remedy, and the repo has the convention for it.**
   `check_gh_direct.py` and `check_prescriptive_push.py` are existing, FAST-tier-enforced
   contract checks over this exact file, with an established CODE-vs-COMMENT tokenizer
   boundary. A `check_no_universe_fanout.py` in the same shape is a well-precedented artifact,
   not an invention.

## Recommendations

1. Fix the lesser instance (`cmd_enumerate:615`) in the same change as the headline one. It is two
   lines, the helper already exists, and leaving a known violation of a documented prohibition in
   place is how the class recurred in the first place.
2. **Add a mechanical check**, in the established `check_gh_direct.py` shape, and wire it into the
   FAST tier. **inferred:** a prose prohibition is demonstrably insufficient here — the one that
   exists is well-written, correctly placed on the function being misused, and was violated anyway.
3. Frame the SPEC edit as **generalizing REQ-BUP-052's existing invariant** to the enumerate/push
   path, not as a new unrelated requirement. The invariant is already written and already agreed;
   what failed was its scope.

## Evidence

- `skills/yf-beads-upstream/scripts/upstream.py:468-476` (`external_for`, the prohibition)
- `skills/yf-beads-upstream/scripts/upstream.py:479-491` (`external_from_row`, the precedent)
- `skills/yf-beads-upstream/scripts/upstream.py:524-549` (`collect_parent_edges`, the defect)
- `skills/yf-beads-upstream/scripts/upstream.py:603`, `:615`, `:1178` (call sites)
- `skills/yf-beads-upstream/SPEC.md` REQ-BUP-052
- `CHANGE-VALIDATION.md` §1 fast tier rows `bup-prescriptive-push`, `bup-gh-direct`
- Measured: `bd list --all --json` → 1801 rows, 84 with non-empty `external_ref`
