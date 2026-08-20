---
type: Reference
okf_spec: OKF-PLAN
id: upstream-grant-requested
description: The upstream write grant, GENERATED FROM the Upstream Issues table rather than from the draft list (Issue 6.3, gate precondition for 6.4/6.5)
---

# Upstream write grant — requested

**Gate:** `Capability Gate: Upstream write` (`Type: human`) · **Blocks:** Issues 6.4, 6.5

## Generated FROM the Upstream Issues table, not from the draft list

The gate's own `Instructions:` require this, and the reason is specific:

> **Generate the grant FROM the Upstream Issues table, not from the draft list** — plan-048's
> grant omitted an `include` row's required close and halted its own reconcile.

A draft list only shows what someone *wrote a comment for*. The table is what `_verify_row`
actually checks at §6.4, and a row can require an action no draft covers — precisely the
`include`-must-be-CLOSED case that halted plan-048. The table below is produced by running
`plan_manager.parse_upstream_rows` over the live `plan.md`.

## The grant

| Issue | Disposition | Required upstream end state | Draft |
| :-- | :-- | :-- | :-- |
| [#135](https://github.com/dixson3/yoshiko-flow/issues/135) | `include` | **COMMENT + CLOSE** | `upstream-drafts/135.md` |
| [#140](https://github.com/dixson3/yoshiko-flow/issues/140) | `partial` | COMMENT | `upstream-drafts/140.md` |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | `partial` | COMMENT | `upstream-drafts/149.md` |
| [#113](https://github.com/dixson3/yoshiko-flow/issues/113) | `partial` | COMMENT | `upstream-drafts/113.md` |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | `partial` | COMMENT | `upstream-drafts/174.md` |
| [#171](https://github.com/dixson3/yoshiko-flow/issues/171) | `deferred` | *no action* | — |
| [#102](https://github.com/dixson3/yoshiko-flow/issues/102) | `exclude` | *no action* | — |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | `exclude` | *no action* | — |

**Plus one create:** the coarse tracking issue, titled
`plan-049-james-dixson-725bc0 execution tracking`, body at `upstream-drafts/tracker.md`.
(The title template is the plan id **verbatim** — a plan id already begins with `plan-`, and the
old `plan-<plan-id>` template produced a doubled prefix on every plan.)

**#135 is the row that must not be missed.** Its `include` disposition means `_verify_row`
requires the issue **CLOSED**, not merely commented. Commenting alone would pass a casual review
and then halt §6.4's `verify-reconcile` — the exact failure this record exists to prevent.

## Every draft is verified against the REAL matcher

SC28 requires the full plan id and that the short form fails. Driven against
`plan_manager._mentions_plan_id` itself, not a re-implementation:

| Draft | Full id `plan-049-james-dixson-725bc0` matches |
| :-- | :-- |
| `113.md`, `135.md`, `140.md`, `149.md`, `174.md` | ✅ all five |
| *negative control:* a body saying only `plan-049` | ❌ does **not** match — as required |

## To authorize

```bash
echo "authorized: <name>, <date> — 5 comments, close #135, create the coarse tracker" \
  > docs/plans/plan-049-james-dixson-725bc0/assets/upstream-authorization.txt
```

Outward-facing writes require explicit authorization. Drafts land first; posting is a **separate
decision**, and the gate is never resolved on the operator's behalf.
