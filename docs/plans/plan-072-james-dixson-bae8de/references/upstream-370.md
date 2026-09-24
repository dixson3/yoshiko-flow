---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #370 - yf-okf-hygiene: `backfill --apply` generates a
  NON-CONFORMANT `index.md` with no member listing — every transformed bundle immediately
  fails index-drift'
---
# Upstream #370: yf-okf-hygiene: `backfill --apply` generates a NON-CONFORMANT `index.md` with no member listing — every transformed bundle immediately fails index-drift

- **Number:** 370
- **Title:** yf-okf-hygiene: `backfill --apply` generates a NON-CONFORMANT `index.md` with no member listing — every transformed bundle immediately fails index-drift
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

**Found during plan-065's own corpus apply — by running the plan, not by reading the code.**

`backfill --apply` renames `README.md` -> `index.md` and then strips the README's prose (step `delete-renamed-README.md-prose`), including its `## File map`. What it emits is a header, an objective blockquote, and a portability sentence — with **no member listing**.

So every bundle it transforms immediately **fails** `scripts/checks/check_okf_index_drift.py`.

## Measured

All 8 bundles of plan-065's corpus apply, with missing-member counts of **9, 13, 9, 11, 12, 12, 18 and 6** — 90 missing entries in total.

| | `no_index` | `drifting` |
| :-- | --: | --: |
| before the apply | 8 | 1 |
| immediately after | 0 | 9 |

The plan traded one non-conformance for another.

## The generated artifact refutes itself on its face

`plan-010/index.md` was 368 bytes reading:

> This bundle is **portable** — a cold reader understands its purpose, environment and history from the files below alone, without the drafting conversation.

...followed by **no files**. An index that promises a listing and omits it is worse than an absent one, because it passes a presence check while carrying a false claim.

## Scope

Repaired post-hoc in plan-065 by running `reindex --apply` on each of the 8 — which derives real descriptions from each member's frontmatter, not bare bullets (verified: 0 bare bullets across all 8). But that repairs the **symptom in one corpus**. The engine will reproduce this for every future backfill in every repo that installs the skill, and the next operator has no reason to expect it.

## Proposed fix

Call the reindex path as the final step of `backfill_one`'s apply branch, so a transformed bundle is conformant when the transform returns. `render_index` / `reindex_write` already exist and already do the right thing — the transform simply does not call them.

