---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #362 - yf-okf-hygiene: the _index.md legacy-variant transform
  route manufactures a hybrid under the yf-plan member'
---
# Upstream #362: yf-okf-hygiene: the _index.md legacy-variant transform route manufactures a hybrid under the yf-plan member

- **Number:** 362
- **Title:** yf-okf-hygiene: the _index.md legacy-variant transform route manufactures a hybrid under the yf-plan member
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug, follow-on

## Body

Discovered by plan-064 Issue 4.1/4.5 while making the `backfill` dry run predictive (REQ-OKFH-011).

**Measured, before and after plan-064's changes:**

| legacy index | dry run | apply |
| :-- | :-- | :-- |
| `README.md` | `would-backfill` | `backfilled` |
| `_index.md` | `halt` (after 4.1) / `would-backfill` (before) | **`halt` — `manufactured-hybrid`** |

`okf.migrate` is member-driven and OKF-PLAN's `index_source` is `README.md`. For a bundle whose
legacy index is `_index.md`, migrate finds no `README.md`, **scaffolds a fresh `index.md`, and
leaves `_index.md` beside it** — manufacturing the exact `hybrid-partial` state the tool refuses to
create. The post-condition catches it and halts.

So `REQ-OKFH-010`'s two-variant-equivalence clause is satisfied for **classification** and NOT for
the **transform**. It was invisible until the dry run became predictive — a second instance of the
defect `REQ-OKFH-011` closes, found by closing it.

**Blocks nothing today:** all 8 remaining legacy bundles classify `legacy-readme`; zero are
`_index.md`. Measured population: `{conformant: 61, legacy-readme: 8}` over 69 bundles.

**Why plan-064 did not fix it:** repairing the routing means changing `okf.migrate`'s
`index_source` resolution across **six** vendored engine copies, which is outside every epic of
that plan. Recording it beat absorbing it silently.

**Guard already in place:** `test_two_variant_equivalence` asserts the measured behaviour of each
variant, so the divergence cannot be re-hidden — and that arm FAILS if the routing is ever
repaired, forcing this bead to be revisited.

Evidence: `docs/plans/plan-064-james-dixson-a0b7fa/findings/exp-004-post-repair-halt-profile.md` §2a
