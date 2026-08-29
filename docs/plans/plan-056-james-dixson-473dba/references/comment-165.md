---
type: Reference
okf_spec: OKF-PLAN
description: "Draft upstream comment for #165 — plan-056's Verification lines are executable; the general class stays open, plus an adjacent id-collision defect found."
disposition: partial
target: "#165"
---
**Partial. plan-056's own `Verification:` lines execute; the corpus-wide class stays open.**

Every requirement plan-056 added or amended carries a `Verification:` line that is a **runnable
command with an exit code**, not prose shaped like one:

| requirement | Verification |
| :-- | :-- |
| `REQ-OKF-CHK-003` | `_shared/test_okf.py::exclude_globs_declared` + `::overlap_invariant`, and `scripts/checks/check-fixture-carveout.sh` |
| `REQ-OKF-CHK-004` | `scripts/checks/check-drift-driver-contract.sh` and `check-recipe-row.sh okf-index-drift` |
| `REQ-DATA-074` | `scripts/checks/check-closeout-can-fail.sh` |
| `REQ-DATA-075` | `scripts/checks/check-description-coverage.py <plan-dir>` |
| `REQ-PLAN-080` (amended) | `check-pytest-ran.sh …/test_recheck_criteria.py unjudged_class_a_blocks` |
| `REQ-PLAN-081` | `check-pytest-ran.sh …/test_cli_enumeration.py index_add_verb` + the corpus driver |
| `REQ-CLI-028` | `scripts/checks/check-pytest-ran.sh <file> <name>` |
| `REQ-CLI-029` | `scripts/checks/harness-selftest.sh --require 9` |

**Each asserts a PAIR of exits, not a single non-zero** — `REQ-CLI-029(a)`. That rule exists because
a criterion expecting non-zero from a script that does not exist is satisfied by the script's
*absence*: `uv run <missing>.py` itself exits 2, which silently satisfied two criteria in an earlier
draft of this plan.

**The general class is NOT discharged.** Measured, 1 of 251 corpus `Verification:` clauses executes.
This plan fixed its own and did not sweep the corpus.

**Adjacent defect found while working this, filed separately** (bead `yf-ne3e`): `REQ-PORT-010`
resolves to **two unrelated requirements in two specs**, so a citation of it is ambiguous. That is a
different failure from a non-executable verification line, and it would have been hidden by fixing
only the surface this issue names.

Plan: `docs/plans/plan-056-james-dixson-473dba/`
