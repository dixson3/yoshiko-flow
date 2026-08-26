---
type: Reference
okf_spec: OKF-PLAN
id: red-prework
description: Append-only red->green observation log written by assets/redcheck.sh (Issue 0.2)
---

# Red-prework record

Append-only observation log written by `assets/redcheck.sh` (Issue 0.2). One line per
observation. The gate `verify-all` reads THIS FILE and `assets/controls.txt`; nothing else.

Record schema, comma-separated, in this order:

    verb, control, fixture, exit-code, command, utc, git-describe

`git-describe` is recorded FOR DIAGNOSIS ONLY. It makes no ordering claim: pass-7 C69
measured that check vacuous, because nothing requires the fix to be committed before
`assert-distinguishes` runs. The ordering "RED was observed before the fix landed" is carried
by the plan's `depends-on` edges, not by this file.

**`CTL_RED=1` IN THE COMMAND FIELD MARKS A *DRIVEN* RED.** Some controls grade work that,
under SPEC-first ordering, has necessarily already landed on the live tree — so the control is
green there and can never be driven red against it. Those controls carry a PINNED NEGATIVE
FIXTURE and select it with `CTL_RED=1`. This is the single convention: grep the `command` field
for `CTL_RED` to get exactly the set of REDs that were driven rather than observed in place.
(`ctl-214-id-collision` was first recorded by pointing `YF_TREE` at its pinned tree directly;
that record is still accurate, and its `CTL_RED=1` record supersedes it as the canonical form.)

## Observations

record-red, ctl-206-dropped-continuation, fixtures/ctl-206-dropped-continuation.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-206-dropped-continuation.sh`, 2026-08-26T01:13:23Z, v0.4.0-395-g7edca7e
record-red, ctl-210-empty-scope, fixtures/ctl-210-empty-scope.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-210-empty-scope.sh`, 2026-08-26T01:15:07Z, v0.4.0-395-g7edca7e
record-red, ctl-210-script-refs, fixtures/ctl-210-script-refs.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-210-script-refs.sh`, 2026-08-26T01:15:58Z, v0.4.0-395-g7edca7e
record-red, ctl-214-id-collision, fixtures/ctl-214-id-collision.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3/docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/corpus/ctl-214-pre-fix bash fixtures/ctl-214-id-collision.sh`, 2026-08-26T01:18:55Z, v0.4.0-395-g7edca7e
record-red, ctl-053-spec-order, fixtures/ctl-053-spec-order.sh, 1, `CTL_RED=1 YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-053-spec-order.sh`, 2026-08-26T01:20:08Z, v0.4.0-395-g7edca7e
record-red, ctl-207-epic-state, fixtures/ctl-207-epic-state.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-207-epic-state.sh`, 2026-08-26T01:22:27Z, v0.4.0-395-g7edca7e-dirty
record-red, ctl-207-human-output, fixtures/ctl-207-human-output.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-207-human-output.sh`, 2026-08-26T01:23:42Z, v0.4.0-395-g7edca7e-dirty
record-red, ctl-214-id-collision, fixtures/ctl-214-id-collision.sh, 1, `CTL_RED=1 YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-214-id-collision.sh`, 2026-08-26T01:25:15Z, v0.4.0-395-g7edca7e-dirty
record-red, ctl-208-vocabulary-sites, fixtures/ctl-208-vocabulary-sites.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-208-vocabulary-sites.sh`, 2026-08-26T01:25:48Z, v0.4.0-395-g7edca7e-dirty
record-red, ctl-208-fail-closed, fixtures/ctl-208-fail-closed.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-208-fail-closed.sh`, 2026-08-26T01:30:16Z, v0.4.0-395-g7edca7e-dirty
record-red, ctl-209-provenance, fixtures/ctl-209-provenance.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-209-provenance.sh`, 2026-08-26T01:31:29Z, v0.4.0-395-g7edca7e-dirty
record-red, ctl-209-provenance, fixtures/ctl-209-provenance.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-209-provenance.sh`, 2026-08-26T01:31:42Z, v0.4.0-395-g7edca7e-dirty
record-red, ctl-208-edge-scope, fixtures/ctl-208-edge-scope.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-208-edge-scope.sh`, 2026-08-26T01:33:42Z, v0.4.0-395-g7edca7e-dirty
assert-distinguishes, ctl-206-dropped-continuation, fixtures/ctl-206-dropped-continuation.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-206-dropped-continuation.sh`, 2026-08-26T01:37:00Z, v0.4.0-396-g2506845-dirty
assert-distinguishes, ctl-210-empty-scope, fixtures/ctl-210-empty-scope.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-210-empty-scope.sh`, 2026-08-26T01:40:06Z, v0.4.0-397-g866fbb8-dirty
assert-distinguishes, ctl-210-script-refs, fixtures/ctl-210-script-refs.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-210-script-refs.sh`, 2026-08-26T01:46:14Z, v0.4.0-397-g866fbb8-dirty
assert-distinguishes, ctl-207-human-output, fixtures/ctl-207-human-output.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-207-human-output.sh`, 2026-08-26T01:49:53Z, v0.4.0-398-gefd2be8-dirty
assert-distinguishes, ctl-207-epic-state, fixtures/ctl-207-epic-state.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-207-epic-state.sh`, 2026-08-26T01:53:59Z, v0.4.0-398-gefd2be8-dirty
record-red, ctl-208-edge-scope, fixtures/ctl-208-edge-scope.sh, 1, `CTL_RED=1 YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-208-edge-scope.sh`, 2026-08-26T01:56:27Z, v0.4.0-399-gfc274cf-dirty
assert-distinguishes, ctl-208-edge-scope, fixtures/ctl-208-edge-scope.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-208-edge-scope.sh`, 2026-08-26T01:56:27Z, v0.4.0-399-gfc274cf-dirty
record-red, ctl-208-vocabulary-sites, fixtures/ctl-208-vocabulary-sites.sh, 1, `CTL_RED=1 YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-208-vocabulary-sites.sh`, 2026-08-26T01:58:38Z, v0.4.0-399-gfc274cf-dirty
record-red, ctl-208-vocabulary-sites, fixtures/ctl-208-vocabulary-sites.sh, 1, `CTL_RED=1 YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-208-vocabulary-sites.sh`, 2026-08-26T01:58:38Z, v0.4.0-399-gfc274cf-dirty
assert-distinguishes, ctl-208-vocabulary-sites, fixtures/ctl-208-vocabulary-sites.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-208-vocabulary-sites.sh`, 2026-08-26T01:58:38Z, v0.4.0-399-gfc274cf-dirty
assert-distinguishes, ctl-208-fail-closed, fixtures/ctl-208-fail-closed.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-208-fail-closed.sh`, 2026-08-26T02:01:40Z, v0.4.0-399-gfc274cf-dirty
record-red, ctl-209-provenance, fixtures/ctl-209-provenance.sh, 1, `CTL_RED=1 YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-209-provenance.sh`, 2026-08-26T02:03:29Z, v0.4.0-400-gd5b21da-dirty
assert-distinguishes, ctl-209-provenance, fixtures/ctl-209-provenance.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-209-provenance.sh`, 2026-08-26T02:03:29Z, v0.4.0-400-gd5b21da-dirty
assert-distinguishes, ctl-053-spec-order, fixtures/ctl-053-spec-order.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-053-spec-order.sh`, 2026-08-26T02:04:49Z, v0.4.0-401-g16ffbc7
assert-distinguishes, ctl-214-id-collision, fixtures/ctl-214-id-collision.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-053-james-dixson-4015d3 bash fixtures/ctl-214-id-collision.sh`, 2026-08-26T02:04:49Z, v0.4.0-401-g16ffbc7-dirty
