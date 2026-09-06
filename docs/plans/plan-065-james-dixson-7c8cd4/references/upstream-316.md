---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #316 - Plan 2/3: run the yf-okf-hygiene corpus backfill
  — 8 legacy-readme bundles to the reserved index.md + log.md model'
---
# Upstream #316: Plan 2/3: run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles to the reserved index.md + log.md model

- **Number:** 316
- **Title:** Plan 2/3: run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles to the reserved index.md + log.md model
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::high

## Body

> **Plan 2 of 3.** Split from a website/docs realignment audit that proved too large for one
> plan. Siblings: #315 (README layout standardization, executes first) and the user-facing
> documentation regeneration.

## Objective

Run the `yf-okf-hygiene` corpus backfill to bring every historical plan bundle and OKF-based
documentation structure onto the reserved `index.md` + `log.md` + frontmatter model.

## Measured state (read-only audit, 2026-08-30)

```
$ uv run skills/yf-okf-hygiene/scripts/okf_hygiene.py audit --json
bundles_checked: 66
  conformant:               58
  legacy-readme:             8
  legacy-underscore-index:   0
  hybrid-partial:            0
  unclassifiable:            0
verdict: pass    exit: 0
```

**8 legacy bundles, all one class (`legacy-readme`), zero unclassifiable.** That is the easy
shape: a single transform, no per-bundle adjudication, nothing the engine cannot categorize.

| Bundle |
| :-- |
| `docs/plans/plan-010-james-dixson-73eebd` |
| `docs/plans/plan-012-james-dixson-a99822` |
| `docs/plans/plan-013-james-dixson-0af2f8` |
| `docs/plans/plan-014-james-dixson-916de2` |
| `docs/plans/plan-021-james-dixson-bb3558` |
| `docs/plans/plan-023-james-dixson-b618bb` |
| `docs/plans/plan-026-james-dixson-6e0e2f` |
| `docs/plans/plan-030-james-dixson-65526e` |

All are plan bundles; the 5 `docs/research/` bundles are already conformant.

## Note on the audit verdict

**`verdict: pass` with 8 legacy bundles is correct, not a bug** — `audit` is read-only
discovery and classification, so "pass" means *the classification succeeded*, not *the corpus is
clean*. Worth stating explicitly in the plan, because reading that verdict as "nothing to do" is
exactly the vacuous-check misread (#263) this family of work keeps encountering. The actionable
signal is `legacy: 8`, not `verdict`.

## Scope

1. **Backfill the 8 bundles.** `backfill` is dry-run by default and `--apply` is consent-gated
   because it rewrites bundles in place. The three-step transform carries a crash-recovery
   journal and `restore` provides record-driven, per-path reversal — verify the journal and
   rehearse `restore` on at least one bundle **before** applying to the set.
2. **Verify reversibility for real.** A reversal path that has never been exercised is an
   assumption. Rehearse it; do not take the SPEC's word.
3. **Re-audit to zero legacy**, and confirm `okf-index-drift` (already a `CHANGE-VALIDATION` row,
   FAST + FULL) stays green across the transform.
4. **Cover the other OKF-based structures**, not just plan bundles — `docs/research/` is already
   conformant, but confirm no OKF structure outside the audit's roots is missed. Per-skill
   `OKF-EXTENSION.md` files (3 exist) carry **no node in `DRIFT-CHECK.md` §1 at all** and nothing
   checks them against their skill's behavior; decide in scoping whether that belongs here or in
   the drift-manifest work.

## Sequencing

Runs **after #315**. Both touch documentation structure, and #315 establishes the layout contract
that governs what a conformant bundle's files should look like. Running the corpus transform
first would backfill 8 bundles onto a contract about to change.

## Acceptance

- `okf_hygiene.py audit` reports `legacy: 0` across all roots.
- The `restore` path has been exercised on a real bundle and shown to reverse cleanly.
- `okf-index-drift` green in the FULL tier over the merged tree.
- Any bundle the engine could not transform is reported explicitly rather than silently skipped.

## Related

- **#140** — `yf-okf`: enforce OKF structure below the bundle root; index drift/regeneration model.
- **#294** — okf index drift enumerates gitignored build residue (a clean checkout is green, a
  working clone is red). Likely to surface during this work.
- **#171** — nested `index.md` generation, deferred behind a `description:` producer change.
- **#298** — OKF/spec-family hygiene: ambiguous REQ ids, stale authority pointers, unmigrated
  `okf_version` split.

