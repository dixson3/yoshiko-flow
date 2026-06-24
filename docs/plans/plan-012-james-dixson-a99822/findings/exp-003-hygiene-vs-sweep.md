# exp-003 — yf-beads-hygiene: reuse vs standalone (feeds #29)

**VERDICT: STANDALONE skill.** No reusable classifier exists in yf-plan's coordinator sweep;
the only shared asset is gotcha *knowledge*, which already lives in yf-beads-extra.

## What resume-scan actually does
- **Vocabulary is "stuck", not "orphan."** Despite the "Resume orphan sweep" title
  (`coordinator.md:17`), the only computed category is **stuck = `status == in_progress`**
  (`plan_manager.py:1421` `_STUCK_STATUSES`; collected `:1550-1559`). "Orphan" is prose only.
- **Detection:** builds the full universe (`_all_plan_beads` `:1473`), walks the **parent tree**
  from the epic (`children_of` adjacency `:1531-1545`), buckets descendants by status.
- **Gate handling = exclusion-by-count, not classification:** `if st != "closed" and
  issue_type != "gate"` (`:1560-1561`) only excludes gates from the "work remaining" tally.
  No open/closed/satisfied/live gate classification.
- Coordinator explicitly **refuses** to classify orphaned `discovered-from` work — "Report,
  never guess… No bead is ever auto-closed" (`coordinator.md:33-36`).

## Overlap with #29's audit — small
- **Edge-target resolution via `bd show`: ABSENT.** resume-scan never resolves a dependency
  edge; it walks only `parent` pointers. #29's core operation has no counterpart.
- **Gate-hidden-in-`bd list`: HANDLED for a different reason.** `_all_plan_beads:1473-1484`
  merges `bd list --all` + `--all --type gate` to complete the parent-walk universe — the one
  genuine technical overlap, but used for universe-building not edge classification.
- **50-row truncation:** addressed via `--all` (`:1480`).
- **#29's four classifications (true-orphan, dangling-edge, satisfied-gate-edge,
  live-gate-edge): ALL ABSENT.**

## Reusable helper?
The reusable units are bd-plumbing primitives, **not a classifier (none exists)**:
`_parse_bd_json` (`:1424-1460`), `_bd_list` (`:1463-1470`), `_all_plan_beads` (`:1473-1484`,
the gate/closed-inclusive universe builder — most relevant). But they're **private
underscore functions in a yf-plan-internal module**; scopes differ fundamentally
(plan-epic-subtree vs whole-DB graph audit). Sharing = forced coupling.

## yf-beads-extra gotchas (#29 "reference, don't restate") — CONFIRMED citable
- Gate semantics: `SKILL.md:49,:62-77`. Edge mutation: `:79-108`. `bd show` vs `bd list` +
  defensive JSON ("`--json` not always one document", `bd show` returns 1-elem array): `:110-165`.
- **Gaps to file under #29:** (1) the "`bd list` hides gate beads + truncates at 50" fact lives
  only as a code comment (`plan_manager.py:1476-1477`) — add it to yf-beads-extra so both skills
  cite one source. (2) `bd dep cycles` (#29's post-repair validation) is **not** documented in
  yf-beads-extra.

## Recommendation
Build **yf-beads-hygiene standalone**. Do not extract/share a classifier. Cross-reference
yf-beads-extra for gate/edge/JSON gotchas. Optionally **re-implement** (copy, don't import)
the ~12-line universe-builder pattern. File the two yf-beads-extra additions above as part of
the #29 epic.
