---
type: Finding
okf_spec: OKF-PLAN
---
# Finding: `closable` never completes at this repo's scale, and the cause is a removable N+1

**Experiment:** EXP-002 · **Date:** 2026-08-16 · **Issues:** [#117](https://github.com/dixson3/yoshiko-flow/issues/117), [#131](https://github.com/dixson3/yoshiko-flow/issues/131)

Marked **[measured]** / **[inferred]** per REQ-AGENT-021.

## Approach Tested

#131 proposes stamping the coarse tracker URL onto the plan epic so `closable` can see it. Before
scoping that, the prerequisite question: **does `closable` work today?** Run it, then read the
implementation if it does not.

## Result

### `closable` does not complete **[measured]**

```
$ uv run skills/yf-beads-upstream/scripts/upstream.py closable --json
(no output after 120s — moved to background)
(still running after 4 minutes; killed)
```

Zero output, no partial progress, no error. From an operator's seat it is indistinguishable from
a hang.

### Cause: one subprocess per bead **[measured]**

`cmd_closable` (`upstream.py:969`):

```python
rows = load_universe_rows()                      # bd list --all --json   → ONE call
beads = [
    {"id": r["id"], "status": r.get("status", ""), "external": external_for(r["id"])}
    for r in rows                                 # ← per row…
    if r.get("id")
]
```

and `external_for` (`upstream.py:340`):

```python
def external_for(bead_id: str) -> str | None:
    out = run(["bd", "show", bead_id])            # ← …a fresh `bd show` subprocess
    m = EXTERNAL_RE.search(out)
    return m.group(1) if m else None
```

Measured universe: **991 beads**. So the verb spawns **991 sequential `bd show` subprocesses**,
each parsed with a regex over human-readable output.

### The data is already in hand — the N+1 is entirely removable **[measured]**

`bd list --all --json` returns all 991 beads in one call **and already carries the field**:

```
beads in list --all: 991
beads with external_ref in LIST output: 20
sample: yf-1656  https://github.com/dixson3/yoshiko-flow/issues/132
```

**[inferred]** Reading `external_ref` from the rows `load_universe_rows()` already returned makes
all 991 subprocess calls unnecessary — 991 → 0. It also replaces regex-scraping of display output
with a structured field read, which is the same robustness argument #133 makes for `gh --json`
over parsing `Pushed N issues`.

### The scan is ~50× wider than the population it reports **[measured]**

Only **20 of 991** beads carry an `external_ref`. The verb iterates the entire history —
`bd list --all` includes closed beads — to find 20 mapped issues. `load_universe_rows()`'s
docstring says *"All non-closed beads"*, but it calls `bd list --all --json`, which does not
filter by status. **[inferred]** The docstring and the call disagree; whichever is intended, the
mapped population can be found by filtering on `external_ref` presence rather than by walking
everything.

## Implications for Plan

1. **#131 as filed would deliver a fix nobody can run.** Stamping the epic makes coarse trackers
   *visible* to a verb that does not return. The performance defect must be fixed in the same
   plan, or #131's value is theoretical.
2. **It is a small fix with a large effect** — read a field that is already present instead of
   shelling out per bead. Not a rewrite, and it is on the same `external_ref` mechanism #133's
   Measurement 1 establishes as the whole mapping, so it survives the gh-direct swap unchanged.
3. **This strengthens the decision to fold #131 into this plan.** The three pieces —
   gh-direct writes `external_ref`, `closable` reads `external_ref`, `yf-plan` stamps
   `external_ref` — are one mechanism viewed from three sides. Splitting them across plans would
   mean touching the same field three times with three separate reviews.
4. **It is also a second instance of a familiar shape**: a documented, shipped verb whose
   behavior nobody had exercised at real scale. `closable` shipped in plan-038 and was cited by
   #131 as the thing to make useful; it had apparently never been run to completion on this repo.

## Recommendations

- Fold a `closable` performance fix into this plan as a prerequisite of the #131 stamp: source
  `external_ref` from `load_universe_rows()` output; drop `external_for`'s per-bead `bd show`.
- Reconcile `load_universe_rows()`'s docstring with its call, or filter to mapped beads directly.
- Add a regression test asserting `closable` issues **one** `bd` invocation regardless of universe
  size — the invariant, not a wall-clock threshold.
- Re-run `closable` after the fix and record the completion time as the evidence #131 needs.
