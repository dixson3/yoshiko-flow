---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #185: doc_lint: upstream-cells-filled cannot distinguish a skipped triage from a measured-empty one

- **Number:** 185
- **Title:** doc_lint: upstream-cells-filled cannot distinguish a skipped triage from a measured-empty one
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`doc_lint`'s `upstream-cells-filled` check (`skills/yf-plan/scripts/document_types/plan.toml`)
fires on a `## Upstream Issues` table with zero rows, with the rationale:

> a table with no rows satisfies every column and id check while asserting nothing

At `review` / `ready-for-approval` status it promotes `W -> E`, so `_audit_plan` fails and
`ready-check` blocks approval (exit 3).

**The check cannot distinguish two opposite situations that produce the identical artifact:**

| Situation | Table | Should the check fire? |
| :-- | :-- | :-- |
| Author skipped upstream triage entirely | zero rows | **yes** — this is the defect the check exists for |
| Author ran triage and upstream genuinely has no issues | zero rows | **no** — the emptiness IS the finding |

The second case is not exotic: it is **every plan authored in a freshly created repository**,
which is a normal way to start a project.

## Encountered in

`dixson3/astrospike`, `plan-001-james-dixson-9153de`. The repo was created empty on 2026-08-20;
Phase 1.4 ran `gh issue list` and got `[]`. The plan records that measurement in prose directly
beneath the table:

> _No upstream issues: `dixson3/astrospike` was created empty on 2026-08-20 and
> `gh issue list` returns `[]`. The coarse plan tracking issue filed at intake is this plan's
> only upstream artifact._

The check cannot read prose, so it fails the plan anyway. Every other audit finding on that
bundle was resolvable by fixing the bundle; this one is only resolvable by fabricating a row —
which would be strictly worse than the finding it silences — or by `--force`, which is what was
used.

## Why `--force` is an unsatisfying resolution here

`--force` is documented as an operator bypass of the audit *as a whole*. Using it to clear a
single known false positive also suppresses any genuine finding that lands in the same run, and
it records a bypass in `log.md` for a plan that had nothing wrong with it. The override
mechanism is doing the job of a missing distinction.

## Suggested directions (not a prescription)

1. **Make the absence declarable.** Accept an explicit sentinel beneath (or inside) the section
   — e.g. a `no-upstream-issues:` line carrying the command and date that produced the result —
   and treat its presence as satisfying the check. This keeps the check's teeth for the skipped
   case while letting a measured absence be *asserted* rather than merely *empty*, which is
   exactly what the rationale asks for.
2. **Key on triage evidence.** `plan_manager.py triage` already runs in Phase 1.4; if it wrote a
   marker (even an empty `upstream-triage.md` with the query and result), the check could
   distinguish "triage ran, found nothing" from "triage never ran" mechanically.
3. **Scope the promotion.** Leave the check `W` rather than promoting to `E` at review, on the
   grounds that a zero-row table is under-determined rather than wrong. Weakest option — it
   trades the false positive for a lost signal.

Option 1 or 2 seems preferable to 3: both preserve the check's purpose instead of dulling it.

## Related

The check's own comment block already measures this shape in the corpus:

> `cell-non-empty / Upstream Issues  :  5 findings, all the ZERO-ROW shape`

All five were in `complete` bundles and therefore report-only, which is why the enforcement gap
had not surfaced before. Filed from `dixson3/astrospike` plan-001.
