---
type: Finding
okf_spec: OKF-PLAN
id: EXP-002
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# EXP-002: Does `bd list --all --json` already carry the edges? — EXHAUSTIVE EQUIVALENCE

**Question.** #268 direction 2 speculates the dependency edges are "almost certainly obtainable in
one call". If true the fix is a one-call rewrite rather than a caching layer. Is it true, and is
the rewrite *exactly* equivalent?

## Approach Tested

1. Inspected the raw shape of `bd list --all --json`: which keys each row carries, how many rows
   carry a `dependencies` array, what edge types appear and under which field name.
2. Checked whether the 122 rows lacking the key mean "no dependencies" or "truncated" by
   cross-checking a sample against `bd show`.
3. Built **both** edge sets in a single process
   (`assets/exp001-equivalence-harness.py`) — the shipped
   `collect_parent_edges` (which reads `bd show` subprocess output) and a candidate rows-based
   derivation — and compared them as `(blocked, blocker, dep_type)` tuples plus resolved target
   identity, over the **whole** universe rather than a sample.

## Result

**CONFIRMED, and proven over the FULL universe.** The rewrite is exact, not approximate.

The data is already on the row. Measured over all 1,801 rows:

| | count |
| :-- | --: |
| rows returned | 1,801 |
| rows carrying a `dependencies` key | 1,679 |
| total dependency entries | 3,669 |
| of type `parent-child` | **1,648** |
| of type `blocks` | 1,987 |
| `discovered-from` / `relates-to` / `related` | 28 / 5 / 1 |
| rows with the top-level `parent` field set | **1,648** |

**measured:** `edge_type()` (`upstream.py:661`) already reads `dependency_type or type`, so the
`bd list` field name is accepted with no change — the divergence it was written for is exactly
this one. The 122 rows lacking the key mean **"no dependencies", not truncation**: sampled
independently, 44 such beads all returned an empty dependency list from `bd show` too. `--all`
also overrides the `--limit` default of 50 (`bd list --all --json` and `--all --limit 0` both
return 1,801, identical id sets), so there is no silent truncation.

Equivalence, over 1,801 of 1,801 beads:

```
EXP001 collect_parent_edges COMPLETED in 321.9s edges=1648
EXP002 one-call edge derivation=0.0018s edges=1648
EXP002 EQUIVALENT=True slow_only=0 fast_only=0
EXP002 targets identical=True
```

**Zero divergence in either direction, across the whole universe** — on the `EQUIVALENT` line,
which is the real result.

**The `targets identical` line is TRIVIALLY TRUE and is not independent evidence.** Both sides
resolve the target as `beads.get(target_id)` from the *same* dict with the same key, so the check
compares a dict lookup against itself. It is retained in the transcript for fidelity but must not
be cited as corroboration. It is harmless because `Edge.target` is provably unread by
`classify_active` on this path (EXP-004) — which is also why its vacuity costs nothing.

The load-bearing comparison is the set-equality of `(blocked, blocker, dep_type)` — exactly the
triple `classify_active` consumes — **plus** the matching edge counts (1,648 both sides), which
together close the multiplicity hole a bare set comparison would leave open. This retires the residual
sampling risk EXP-004 flagged (0/373 on two independent samples, ~21%); no separate landing-gate
run is needed.

| | fan-out | one-call |
| :-- | --: | --: |
| wall clock | 321.9 s | **0.0018 s** |
| subprocesses spawned | 1,801 | **0** (reuses the `bd list` already issued) |

**On circularity — the comparison is not self-confirming.** The two sides do not share a data
source: the slow side parses `bd show <id> --json` **subprocess output**, one call per bead; the
fast side reads the `dependencies` array off the `bd list` payload. Only *target resolution* uses
a common dict, and that is correct rather than circular — the shipped implementation resolves
targets as `beads.get(target_id)`, so any faithful rewrite must too.

## Implications for Plan

- The fix is a **removal**, not a redesign: it deletes work the process was already paying for and
  discarding. It adds no new `bd` call and no new failure mode.
- The equivalence evidence is strong enough to make the rewrite's risk (plan R1) a *measured*
  non-risk rather than a mitigated one.
- **withdrawn:** an earlier draft read the 1,648/1,648 agreement between the `parent-child` edge
  count and the top-level `parent` field count as "independent corroboration … two unrelated fields
  agreeing exactly". **Both halves are false.** Measured in a later sandbox on bd 1.2.2, a bead can
  carry **two** `parent-child` edges, so the equality is a property of *this corpus*, not an
  invariant; and the fields are **not independent** — `bd dep add --type parent-child` *sets*
  `parent` and `bd dep remove` *clears* it, so `parent` is **derived from** the edge. What survives
  is the weaker, structural, and still-useful claim the plan's Issue 1.8 relies on:
  `parent` set **implies** at least one parent-child edge, which makes *parent-set-with-zero-edges*
  a sound, false-alarm-free alarm — and a count-equality check an unsound one.

## Recommendations

1. Rewrite `collect_parent_edges` in place, keeping the signature, the `edge_type()` call and the
   `depends_on_id or id or target` chain **verbatim** — the latter two are precisely what make the
   function source-agnostic.
2. Write **both traps below** into the plan explicitly; each has already produced a false result
   once during this investigation.
3. Vendor the harness into the bundle so the load-bearing claim is re-runnable by a cold reader
   rather than taken on trust.

### Two traps the plan must state explicitly

1. **The two sources name the target id differently.** A `bd show` dep dict embeds the full target
   bead and carries the id as **`id`**; a `bd list` dep dict uses **`depends_on_id`**. The chain at
   `upstream.py:534` handles both. A harness comparing on `depends_on_id` alone reads a **false
   100% divergence** — EXP-004's spike hit exactly this.
2. **A latent gate bug is being PRESERVED, not fixed.** `load_universe_rows()` passes neither
   `--include-gates` nor `--include-infra`, so the universe is 1,801 rather than 1,976. All 165
   gate beads carry a parent-child edge to their molecule parent, and those 165 edges are invisible
   to `collect_parent_edges` today because it iterates the gate-free dict. A rows-based rewrite over
   the same `load_universe_rows()` output reproduces that **exactly**. **Do not "fix" it here** —
   adding `--include-gates` injects 165 parent-child edges into `classify_active`'s ancestor
   propagation, promoting molecules to ACTIVE and shrinking the push-candidate set. That is a
   spec-visible behavior change and belongs to its own issue.

## Evidence

- Harness `assets/exp001-equivalence-harness.py` and log `assets/exp001-equivalence-harness.output.txt` — vendored so the claim is re-runnable
- `skills/yf-beads-upstream/scripts/upstream.py:506` (`load_universe_rows`), `:524`, `:534`, `:661`
- Corroborated independently by the EXP-004 sandbox spike: `n beads 357 old edges 303 new edges 303 / EQUAL: True`
