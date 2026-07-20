# Plan Red-Team: plan-030-james-dixson-65526e — pass 2

## Verdict: APPROVE

### Strengths

- All four pass-1 concerns resolved with grounding in the actual code, not just prose: C1 out-of-tree
  bead matches `close_cascade.py`'s exit-2 fail-loud on any open child; C2 `log.md` bullet matches
  REQ-DATA-012 + `okf.append_log` prepend semantics; C3 registration matches `_rebuild_field_block`'s
  drop-unregistered behavior; C4 non-status token matches `_plan_review_line_count` /
  `_first_scoping_date` keying only on `review:`/`scoping:`.
- Risks table now carries a dedicated mitigation row per C1–C4, cross-referenced to the tests that
  assert them (3.1(c)/(d)/(e)). Each formerly-hand-waved claim is a testable precondition.
- Dependency ordering correct: Issue 2.0 (field registration) precedes 2.2 (the writer), so the
  marker is never written before it is durable.
- SPEC-first sequencing intact; self-referential carve-out (plan-030 is `standard`) correct.

### Concerns

| # | Severity | Concern | Recommendation | Status |
|:-:|:--|:--|:--|:--|
| C5 | low | `classify-deliverable` treats merged-tree changed paths as `high`-confidence, but intake wiring runs it before a merged tree exists — strongest signal unavailable at first suggestion. | Note in 2.1/2.3 that the class may be (re)confirmed at reconcile when changed paths are available. Optional; suggest+confirm already covers correctness. | resolved |
| C6 | low | `deliverable_class` position in `PLAN_FIELD_ORDER` unspecified. | Place it after `status` in Issue 2.0. | resolved |

### Missing

No remaining material gaps. Pass-1 "Missing" items addressed: REQ-DATA-012 read and cited; bead
discovery specified (label + `{plan}` metadata via `bd list --label`, not a tree walk);
`classify-deliverable` signal→`confidence` contract defined.

### Gate Assessment

Gates minimal and appropriate. The pass-1 Reconcile-Gate/option-(b) conflict is resolved by the C1
out-of-tree move (the deferred bead is not an execution bead of this plan). Completion criterion as a
fail-loud script precondition (own verb, mirroring `close_cascade.py`), not a bd gate — correct.

### Upstream Assessment

Sound: #89 sole driver (`include`, coarse tracking issue); #90 correctly excluded. Out-of-tree
deferred bead's individual upstream push framed as a sanctioned per-bead exception (UPSTREAM_TRACKING
deferred/follow-on path), so option (b)'s "upstream-tracked" guarantee is met.

### Operator Resolutions

| # | Resolution | Status |
|:-:|:--|:--|
| C5 | Added a reconfirm-at-reconcile note to Issues 2.1 and 2.4. | resolved |
| C6 | Issue 2.0 pins `deliverable_class` immediately after `status` in `PLAN_FIELD_ORDER`. | resolved |
