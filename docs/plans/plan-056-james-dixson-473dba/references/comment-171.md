---
type: Reference
okf_spec: OKF-PLAN
description: "Draft upstream comment for #171 — description: is now a producer contract; nested index.md generation stays out, on a re-measured premise."
---
**Partial, as re-scoped. The `description:` producer change shipped; nested index generation did not.**

**IN — `REQ-DATA-075`, the `description:` producer contract.** It is a *producer* obligation, not a
lint, and it names its stamping sites explicitly:

| producer site | type | derived from |
| :-- | :-- | :-- |
| `_write_upstream_reference` | `Reference` | `"Upstream issue #N - <title>"` |
| `seed_plan_md` | `Plan` | the plan's objective |
| the `upstream-triage.md` writer | `Triage` | a fixed statement of what the file records |

**`context.md` and `plan-retrospective.md` are DECLARED EXEMPT**, and the exemption is part of the
contract rather than an omission: one file per bundle with one shape means a derived description
there is the *same string in every bundle* — measured, 67 identical copies. A key whose value is
constant across the corpus carries zero information and dilutes the ones that do not.

The paired linter check ships at **`W`** on exactly the types that HAVE a producer or a declared
authoring contract (`upstream-reference`, `finding`, `review`), with `regex-present`
`^description:\s*\S` so an empty value cannot satisfy it. `research-*` is scoped out — its
`bundle_status` is `None`, so a `W` there is permanent and never demoted, and a permanent warning is
noise rather than enforcement.

**OUT — nested `index.md` generation, and the premise for deferring it has been corrected.** The
shipped specs asserted `description:` was present on **0 of 423** nested files. Re-measured
2026-08-28: **165 of 983**. That figure was stale on *both* terms, and all eight occurrences across
four files now carry the re-measurement and its date. The correction **weakens** the original
rationale — coverage is no longer zero — and the specs now say so explicitly rather than continuing
to assert absence. It does not reverse the decision: 818 of 983 generated entries would still be
bare, and the 165 are concentrated entirely in the twelve newest bundles, so this is a
producer-version artifact that the contract above will grow forward without touching frozen history.

Plan: `docs/plans/plan-056-james-dixson-473dba/`
