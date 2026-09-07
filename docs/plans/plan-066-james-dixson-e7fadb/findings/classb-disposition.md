---
type: Finding
okf_spec: OKF-PLAN
description: "Explicit per-item disposition for all six Class-B defects — each CLOSED with the artifact that closes it, or FILED with an owner. Never implied by a green build."
id: classb-disposition
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
---
# Class-B disposition — six items, each named

## Approach Tested

**measured:** each disposition below names the artifact that closes the item and the command
that demonstrates it, or the issue it is filed as. **A green build is not a disposition** — the
whole Class-B thesis is that coverage and detection are different things, so "everything passes"
is precisely the evidence that does not settle these.

## Result

| Item | Defect | Disposition |
| :-- | :-- | :-- |
| **item-1** | "images / cards / home have no §6 trigger row" | **CLOSED** |
| **item-2** | `e-web-cli-surface` excludes `harness_desc.rs` | **CLOSED** |
| **item-3** | `web/content/**` fans out to `e-status-values` only | **CLOSED** |
| **item-4** | No coverage of the upstream-backend claim | **CLOSED** |
| **item-5** | `e-skill-page-desc` missed real defects | **CLOSED** |
| **item-6** | `optional`/`required` reachability enforces nothing | **CLOSED** |

### item-1 — CLOSED, and #317's literal claim was FALSE

The issue says those three paths have no §6 row. They did: `web/content/**` matched all three.
The real defect was that the row **fanned out to one narrow edge**, so the remedy #317 proposed
— *add §6 rows* — was a **no-op**, because a §6 row can only name edges that exist and no node
covered `web/content/images/*.d2`.

Closed by the sequence the defect actually required, **node → edge → §6 row**: the
`web-diagram-src` node, the `e-web-diagram-*` edges, and only then the trigger row. Merged with
item-3, which is the same fact seen from the other side.

### item-2 — CLOSED, all three edits, not the one #317 named

`grep` for the path strings in the source node's files returned zero output: `cli-surface` held
`cli.rs` and `profiles/*.json`, and contained none of the facts the pages state. #317 named one
edit; three were needed:

1. `yf/src/harness_desc.rs` added to the source node;
2. a **§6 trigger row for that path**, which it had NONE of — so a widened node would still
   never have fired on its own source edit;
3. the contract rewritten from `path-resolves` to `value-equal` — an existence test structurally
   cannot compare a root **path string** or a `name_transform` **value**.

Verified: `uv run scripts/checks/check_web_harness_paths.py` → exit 0 over 47 files, having
reported 26 findings before the Epic-4 repairs.

### item-3 — CLOSED (merged with item-1)

`lifecycle.md`, `workflows.md`, `usage.md`, `glossary.md`, `managed-files.md`,
`beads-concepts.md` and `why.md` fanned out to `e-status-values` alone — a plan-status-literal
subset check — and so had **no content coverage at all**. Closed by the `web-content-prose` node
and the `e-web-prose-status` edge, mechanically realized by `check_web_counts.py` +
`check_web_harness_paths.py`, whose corpus is a parameter covering exactly that node set plus
`README.md` and `AGENTS.md`.

### item-4 — CLOSED, and it was the cleanest causal evidence in the set

Five sites stated the backend set and **the one that was correct was the one an edge covered** —
a 4-false / 1-true split falling precisely along the coverage boundary. Closed by the
`upstream-backend-truth` node, the `e-web-backend-claim` and `e-web-backend-diagram` edges (split
by artifact kind, since repairing a `.d2` additionally requires a re-render), and
`check_web_backend_claim.py`. Verified: exit 0 over all six sites, with `README.md:25`'s `gh` /
`glab` CLI mention correctly allowlisted rather than false-positived.

### item-5 — CLOSED. It was a DISPATCH gap, and #317's diagnosis was wrong

#317 asked whether the edge was report-only or INCONCLUSIVE-tolerant. Measured answer: **it was
never dispatched.** Dispatched by hand the edge returned **3 FAILs with quoted evidence**,
including one #317 never named. Root cause: `CHANGE-VALIDATION.md` excluded the engine as "not a
runnable command", so its only firing surface was an always-loaded prose trigger — **4 firing
opportunities, 0 catches**.

**A manifest edit cannot fix a dispatch gap**, which is why closing items 1-4 and 6 while leaving
this one open would have produced *more edges that also never run*. Closed by the mechanical
gate: six `CHANGE-VALIDATION.md` recipe rows in **both** tiers with source-side §3 globs
(verified: 6/6 fire), plus the `web-doc-checks` CI job, because the FULL tier binds on the
yf-plan land path only and CI ran no tier at all.

### item-6 — CLOSED, with #317's proposed remedy DROPPED as inert

The `optional`→`required` token flip is **byte-identical either side** — proven by A/B, not
argued. Edge pairing computes the **intersection** of the two globs, so the one-element
difference (a skill with no page) drops out of the pairing taking its own absence with it. The
flip was therefore removed from the remedy entirely.

Closed instead by making the check a **set difference**: `check_skill_page_contract.py`
(`A \ B` FAILs, `B \ A` advisory, `--min-skills` floor), the §4 Referencers row for `skill-page`,
and the Epic-0 spec work that gave a node-level check a firing surface at all —
`REQ-CHECK-004(a)` split out, `REQ-CHECK-005` scoped, `REQ-CHECK-008` added, and
`REQ-SCHEMA-002` widened so a node-keyed §6 row passes referential closure.

#317's "`yf-okf-hygiene` has neither a page nor a README" was also **stale**: it had a README
(`4cf61c7`, plan-061); only the page was missing.

## Filed, not fixed (D5 — a pipeline defect outside the four in-scope items is filed)

| # | Defect | Why filed rather than fixed |
| --: | :-- | :-- |
| F1 | `skill_pages.py`'s authored-page guard is **existence-only** — a zero-byte page passes it and builds green | Same class as the four Class-B items but a fifth instance; D5 bounds this plan to the four in scope |
| F2 | `lifecycle.d2` labels a preflight status `deps-missing` where the literal is `system_deps_missing` | Cosmetic today; will not survive a literal-equality checker over preflight statuses, which does not yet exist |
| F3 | `check_web_counts` declares `not_checked` for any group bullet that enumerates no member ids | An honest declared limit, not a defect — recorded so a future reader does not mistake the silence for a pass |

## Implications for Plan

All six are **CLOSED**, none by implication. Three follow-ons are **FILED** under D5 and are
carried into Issue 8.4's upstream filings.

## Recommendations

Read item-5 as the load-bearing one. Items 1-4 and 6 were manifest gaps that editing
`DRIFT-CHECK.md` fixes; item-5 was a dispatch gap, and it is the only one whose remedy required
building something that runs.
