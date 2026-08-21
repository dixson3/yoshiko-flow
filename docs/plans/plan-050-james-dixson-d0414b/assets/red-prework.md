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

## Observations

record-red, ctl-186-masked-title, assets/fixtures/ctl-186-masked-title.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-186-masked-title.sh`, 2026-08-21T05:12:01Z, v0.4.0-285-gb030bf0
record-red, ctl-187-empty-detail, assets/fixtures/ctl-187-empty-detail.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-187-empty-detail.sh`, 2026-08-21T05:12:01Z, v0.4.0-285-gb030bf0
assert-distinguishes, ctl-186-masked-title, assets/fixtures/ctl-186-masked-title.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-186-masked-title.sh`, 2026-08-21T05:15:35Z, v0.4.0-286-g2100bdd
assert-distinguishes, ctl-187-empty-detail, assets/fixtures/ctl-187-empty-detail.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-187-empty-detail.sh`, 2026-08-21T05:15:35Z, v0.4.0-286-g2100bdd
record-red, ctl-179-wrapper-close, assets/fixtures/ctl-179-wrapper-close.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-179-wrapper-close.sh`, 2026-08-21T05:18:10Z, v0.4.0-286-g2100bdd
record-red, ctl-180-chain-order, assets/fixtures/ctl-180-chain-order.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-180-chain-order.sh`, 2026-08-21T05:18:16Z, v0.4.0-286-g2100bdd
assert-distinguishes, ctl-179-wrapper-close, assets/fixtures/ctl-179-wrapper-close.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-179-wrapper-close.sh`, 2026-08-21T05:24:02Z, v0.4.0-287-g1795cf3
assert-distinguishes, ctl-180-chain-order, assets/fixtures/ctl-180-chain-order.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-180-chain-order.sh`, 2026-08-21T05:24:08Z, v0.4.0-287-g1795cf3
record-red, ctl-181-silent-green, assets/fixtures/ctl-181-silent-green.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-181-silent-green.sh`, 2026-08-21T05:25:33Z, v0.4.0-287-g1795cf3
assert-distinguishes, ctl-181-silent-green, assets/fixtures/ctl-181-silent-green.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-181-silent-green.sh`, 2026-08-21T05:30:17Z, v0.4.0-288-g5945ed9
record-red, ctl-178-grant, assets/fixtures/ctl-178-grant.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow bash assets/fixtures/ctl-178-grant.sh`, 2026-08-21T05:36:53Z, v0.4.0-307-gfc66606
assert-distinguishes, ctl-178-grant, assets/fixtures/ctl-178-grant.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-050-james-dixson-d0414b bash assets/fixtures/ctl-178-grant.sh`, 2026-08-21T05:37:15Z, v0.4.0-288-g5945ed9-dirty
