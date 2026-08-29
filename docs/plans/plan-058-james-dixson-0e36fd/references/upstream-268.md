---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #268: CRITICAL: yf-beads-upstream push is unusable — owner-claim warning fans out one `bd show` per bead over the ENTIRE closed universe (~360s, presents as a silent hang)

- **Number:** 268
- **Title:** CRITICAL: yf-beads-upstream push is unusable — owner-claim warning fans out one `bd show` per bead over the ENTIRE closed universe (~360s, presents as a silent hang)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Severity: CRITICAL — the routed upstream write path does not complete

`upstream.py push` **never returns** on a repo of ordinary size. It is the path
`UPSTREAM_TRACKING.md` mandates for every upstream write ("route every upstream write through
`/yf-beads-upstream` — do not hand-run the underlying commands"), so while it is broken there is
**no compliant way to push a bead upstream at all**. Hand-running `gh issue create` is explicitly
non-compliant because it records no `external_ref`.

Measured in `dixson3/yoshiko-flow` at `4fcf97b`.

## Reproduction

```bash
uv run "$(yf skill-dir yf-beads-upstream)/scripts/upstream.py" push --issues yf-djfx
```

Never completes. No stdout, no stderr, no progress. Observed at 30s, 60s, 90s and 120s timeouts,
with stdin closed (`</dev/null`) to rule out a prompt. `bd` itself is healthy and responsive
throughout (`bd show <id> --json` exits 0 in 0.18–0.31s).

## Root cause — confirmed by traceback and arithmetic, not inferred

`SIGINT` at the hang point:

```
File "upstream.py", line 1231, in cmd_push
  for line in owner_claim_warning_lines():
File "upstream.py", line 1178, in owner_claim_warning_lines
  edges = collect_parent_edges(beads)
File "upstream.py", line 533, in collect_parent_edges
  for dep in deps_for_show(bid):
File "upstream.py", line 552, in deps_for_show
  rows = parse_json_array(run(["bd", "show", bead_id, "--json"]))
File "upstream.py", line 88, in run
  proc = subprocess.run(cmd, capture_output=True, text=True)
```

Three defects compound:

**1. The universe is every bead ever created, including closed.** `load_universe_rows()` is
`bd list --all --json` — deliberately, per its own docstring, because `cmd_closable` needs closed
rows. In this repo that is **1,801 beads**.

**2. `collect_parent_edges` spawns one `bd show` subprocess per bead, serially.**

| quantity | measured |
| :-- | --: |
| beads in universe (`bd list --all --json`) | **1,801** |
| cost of one `bd show <id> --json` | **~0.2 s** |
| projected serial cost | **~360 s** |

That matches the observed behaviour exactly: not a deadlock, a **six-minute serial subprocess
fan-out** with no output until it finishes.

**3. `run()` passes no `timeout` to `subprocess.run`**, so nothing bounds any individual call and
the failure presents as an indefinite hang rather than an error.

## Why this is worse than a slow path

The fan-out is on the **owner-claim warning** path (`owner_claim_warning_lines`, REQ-BUP-051) —
a *diagnostic* — and it runs **before** the push work, **unconditionally**, and **regardless of
`--issues` scope**. Pushing a single named bead pays a full-universe walk to compute a warning
about beads that are not being pushed.

It also scales with repo *history*, not with repo *activity*: the universe only ever grows, so
every repo crosses the unusable threshold eventually and never recovers. `yoshiko-flow` has 37
open beads and 1,801 total — the work is **49×** the live working set.

## Suggested directions (for the investigating plan to evaluate, not prescriptive)

1. **Scope the warning to the beads actually being pushed** when `--issues` is given. A warning
   about unrelated beads is not worth a full-universe walk.
2. **Stop shelling out per bead.** The dependency edges needed here are almost certainly
   obtainable in one call; `bd list --all --json` already returns the universe in one shot.
3. **Give `run()` a default `timeout=`** and raise a diagnosable error. This is the defect that
   turned a slow path into a silent hang, and it is independent of the other two — a bounded call
   would have surfaced this on the first run rather than after a research pipeline needed it.
4. Consider whether the warning should be **lazy or opt-in** at all, given it is advisory.

## Impact

- Blocks the hoist of `yf-djfx` (operator-approved, amended, pending)
- Blocks any close-time / land-the-plane push, which `UPSTREAM_TRACKING.md` makes a standing
  obligation
- `cmd_enumerate` calls the same warning helper and is likely affected identically — unverified

## Evidence

- Repo `dixson3/yoshiko-flow` @ `4fcf97b`; skill at `~/.claude/skills/yf-beads-upstream`
- `upstream.py` lines 88, 506–520, 525–556, 1168–1186, 1231
- Discovered 2026-08-28 while hoisting a follow-on bead from `yf-research` 005 (PR #267)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

