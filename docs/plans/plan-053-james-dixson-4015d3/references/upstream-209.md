---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #209: Issue beads carry no plan_dir, so poured descriptions cite EXP-NNN / SC-N evidence an executor cannot locate (21 of 35 in one plan)

- **Number:** 209
- **Title:** Issue beads carry no plan_dir, so poured descriptions cite EXP-NNN / SC-N evidence an executor cannot locate (21 of 35 in one plan)
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/209
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

## Summary

Since #187, an issue bead's description is the plan's per-issue `detail` **verbatim**. That text routinely cites evidence by identifier — `EXP-001`, `SC8`, `R11`, a bundle-relative filename — but the issue bead carries no pointer back to the bundle those identifiers live in. Only the **epic** bead gets `metadata.plan_dir`.

So a bead-level executor is told to rely on a measurement it has no way to locate.

## Measured

In `dixson3/astrospike` `plan-001` (35 issues): **21 of 35 details cite `EXP-0NN`, 36 occurrences in total.** Also present: `SC8` / `SC10`, `(R11)` / `(R12)` / `(R13)`, and bundle-relative filenames such as `decisions.md`.

Per SKILL.md §5.2 the pour passes `detail` straight through as `--description`, and issue beads carry only `plan_issue` and `plan` in metadata. `metadata.plan_dir` is set on the epic bead alone.

## Why it matters more after #187 than before

Before #187 this was invisible: descriptions were empty, so nothing was cited anywhere. The fix is what turned per-issue prose from commentary into the executor's actual reading matter — and with it, every unresolved reference inside that prose became operational.

This is not a "the plan should write better prose" issue. Restating each finding in full inside every citing issue would duplicate substantial text across 21 beads and is precisely the churn that plan authoring guidance warns against. The missing piece is *provenance*, and provenance is naturally the pour's job — it is the only step that knows the bundle path.

## Suggested fix

Either of:

1. **Stamp `plan_dir` into issue metadata**, not just the epic's. Smallest change; makes the bundle findable from any bead programmatically.
2. **Prepend a one-line provenance header** to each issue description at pour time, e.g. `Plan: <plan_id> · Bundle: <plan_dir>`. Slightly larger diff, but readable by a human executor who is looking at the bead text rather than its metadata — which is the case that actually bites.

(2) is probably the more useful of the two, since the failure mode is a person or agent reading the description and not knowing where `EXP-004` is.

## Severity

Low-to-medium, and deliberately filed as such. In the plan where this was found, every operative instruction restated the fact it depended on, so no bead was *unexecutable* — the citations were corroboration rather than load-bearing. But that is a property of one carefully-reviewed plan, not a guarantee of the format, and the cost of relying on it grows with plan size.

## Context

Found during a red-team pass over `plan-001` scoped specifically to "is the plan's prose sound *as bead content*" — a question that only became askable once #187 shipped. Related: #206, #207, #208.

