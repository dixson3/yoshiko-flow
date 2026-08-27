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

The `command` field records the FIXTURE-SELECTING ENVIRONMENT verbatim — `YF_TREE`, and
`CTL_RED` when set. A control whose RED was driven against a PINNED NEGATIVE FIXTURE rather
than against the live tree must say so ON ITS FACE, or the record silently overstates what
was observed.

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

record-red, ctl-154-symlink-revert, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-154-symlink-revert.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-154-symlink-revert.sh`, 2026-08-27T00:32:57Z, v0.4.0-415-g4380c74
record-red, ctl-185-empty-triage, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-185-empty-triage.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-185-empty-triage.sh`, 2026-08-27T00:32:58Z, v0.4.0-415-g4380c74
record-red, ctl-201-changed-append, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-201-changed-append.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-201-changed-append.sh`, 2026-08-27T00:32:58Z, v0.4.0-415-g4380c74
record-red, ctl-203-exit-discipline, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-203-exit-discipline.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-203-exit-discipline.sh`, 2026-08-27T00:32:59Z, v0.4.0-415-g4380c74
record-red, ctl-225-columnzero-paragraph, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-225-columnzero-paragraph.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-225-columnzero-paragraph.sh`, 2026-08-27T00:32:59Z, v0.4.0-415-g4380c74
record-red, ctl-226-leading-code-span, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-226-leading-code-span.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-226-leading-code-span.sh`, 2026-08-27T00:33:00Z, v0.4.0-415-g4380c74
record-red, ctl-901-opencode-read-layers, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-901-opencode-read-layers.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-901-opencode-read-layers.sh`, 2026-08-27T00:33:00Z, v0.4.0-415-g4380c74
record-red, ctl-902-resolver-isolated, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-902-resolver-isolated.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-902-resolver-isolated.sh`, 2026-08-27T00:33:00Z, v0.4.0-415-g4380c74
record-red-check, check-allowed-tools.sh, assets/checks/check-allowed-tools.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-allowed-tools.sh`, 2026-08-27T00:33:13Z, v0.4.0-415-g4380c74
record-red-check, check-bd-dep-types.sh, assets/checks/check-bd-dep-types.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-bd-dep-types.sh`, 2026-08-27T00:33:14Z, v0.4.0-415-g4380c74
record-red-check, check-criteria-scripts-exist.sh, assets/checks/check-criteria-scripts-exist.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-criteria-scripts-exist.sh`, 2026-08-27T00:33:14Z, v0.4.0-415-g4380c74
record-red-check, check-deferred-filed.sh, assets/checks/check-deferred-filed.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-deferred-filed.sh`, 2026-08-27T00:33:14Z, v0.4.0-415-g4380c74
record-red-check, check-deployed-tree.sh, assets/checks/check-deployed-tree.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-deployed-tree.sh`, 2026-08-27T00:33:14Z, v0.4.0-415-g4380c74
record-red-check, check-deprecations.sh, assets/checks/check-deprecations.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-deprecations.sh`, 2026-08-27T00:33:14Z, v0.4.0-415-g4380c74
record-red-check, check-drift-edges.sh, assets/checks/check-drift-edges.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-drift-edges.sh`, 2026-08-27T00:33:14Z, v0.4.0-415-g4380c74
record-red-check, check-env-var-wins.sh, assets/checks/check-env-var-wins.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-env-var-wins.sh`, 2026-08-27T00:33:14Z, v0.4.0-415-g4380c74
record-red-check, check-exit-discipline.sh, assets/checks/check-exit-discipline.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-exit-discipline.sh`, 2026-08-27T00:33:15Z, v0.4.0-415-g4380c74
record-red-check, check-fallback-superset.sh, assets/checks/check-fallback-superset.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-fallback-superset.sh`, 2026-08-27T00:33:15Z, v0.4.0-415-g4380c74
record-red-check, check-formula-count.sh, assets/checks/check-formula-count.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-formula-count.sh`, 2026-08-27T00:33:16Z, v0.4.0-415-g4380c74
record-red-check, check-glossary-terms.sh, assets/checks/check-glossary-terms.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-glossary-terms.sh`, 2026-08-27T00:33:16Z, v0.4.0-415-g4380c74
record-red-check, check-harness-matrix.sh, assets/checks/check-harness-matrix.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-harness-matrix.sh`, 2026-08-27T00:33:16Z, v0.4.0-415-g4380c74
record-red-check, check-intree-docs.sh, assets/checks/check-intree-docs.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-intree-docs.sh`, 2026-08-27T00:33:16Z, v0.4.0-415-g4380c74
record-red-check, check-merged.sh, assets/checks/check-merged.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-merged.sh`, 2026-08-27T00:33:16Z, v0.4.0-415-g4380c74
record-red-check, check-no-hardcoded-skillpath.sh, assets/checks/check-no-hardcoded-skillpath.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-no-hardcoded-skillpath.sh`, 2026-08-27T00:33:16Z, v0.4.0-415-g4380c74
record-red-check, check-no-legacy-find.sh, assets/checks/check-no-legacy-find.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-no-legacy-find.sh`, 2026-08-27T00:33:16Z, v0.4.0-415-g4380c74
record-red-check, check-readme-harness.sh, assets/checks/check-readme-harness.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-readme-harness.sh`, 2026-08-27T00:33:16Z, v0.4.0-415-g4380c74
record-red-check, check-release-notes.sh, assets/checks/check-release-notes.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-release-notes.sh`, 2026-08-27T00:33:17Z, v0.4.0-415-g4380c74
record-red-check, check-resolver-isolated.sh, assets/checks/check-resolver-isolated.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-resolver-isolated.sh`, 2026-08-27T00:33:17Z, v0.4.0-415-g4380c74
record-red-check, check-stamp-agrees.sh, assets/checks/check-stamp-agrees.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-stamp-agrees.sh`, 2026-08-27T00:33:18Z, v0.4.0-415-g4380c74
record-red-check, check-sync-emits-all.sh, assets/checks/check-sync-emits-all.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-sync-emits-all.sh`, 2026-08-27T00:33:19Z, v0.4.0-415-g4380c74
record-red-check, check-tag-exists.sh, assets/checks/check-tag-exists.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-tag-exists.sh`, 2026-08-27T00:33:19Z, v0.4.0-415-g4380c74
record-red-check, check-themes-present.sh, assets/checks/check-themes-present.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-themes-present.sh`, 2026-08-27T00:33:19Z, v0.4.0-415-g4380c74
record-red-check, check-version-agrees.sh, assets/checks/check-version-agrees.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-version-agrees.sh`, 2026-08-27T00:33:19Z, v0.4.0-415-g4380c74
record-red-check, check-web-accuracy.sh, assets/checks/check-web-accuracy.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-web-accuracy.sh`, 2026-08-27T00:33:19Z, v0.4.0-415-g4380c74
record-red-check, check-cargo-test-ran.sh, assets/checks/check-cargo-test-ran.sh, 1, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash assets/checks/check-cargo-test-ran.sh revert_through_symlink_preserves_link_and_clears_block`, 2026-08-27T00:33:42Z, v0.4.0-415-g4380c74
assert-distinguishes, ctl-902-resolver-isolated, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-902-resolver-isolated.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-902-resolver-isolated.sh`, 2026-08-27T00:36:14Z, v0.4.0-415-g4380c74-dirty
assert-distinguishes, ctl-154-symlink-revert, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-154-symlink-revert.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-154-symlink-revert.sh`, 2026-08-27T00:48:37Z, v0.4.0-418-g7d656b2-dirty
assert-distinguishes, ctl-901-opencode-read-layers, docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-901-opencode-read-layers.sh, 0, `YF_TREE=/Users/james/workspace/dixson3/yoshiko-flow/.worktrees/plan-054-james-dixson-535968 bash docs/plans/plan-054-james-dixson-535968/assets/fixtures/ctl-901-opencode-read-layers.sh`, 2026-08-27T00:51:47Z, v0.4.0-418-g7d656b2-dirty
