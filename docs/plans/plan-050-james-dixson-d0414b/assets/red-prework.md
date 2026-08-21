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
