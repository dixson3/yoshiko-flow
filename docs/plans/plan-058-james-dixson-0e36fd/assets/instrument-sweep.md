---
type: Asset
okf_spec: OKF-PLAN
id: ASSET-instrument-sweep
plan: plan-058-james-dixson-0e36fd
author: james-dixson
created: 2026-08-28
---
# Instrument sweep — baseline (Issue 0.1)

Every gate `Test:` and every non-manual Success Criterion `Verification`, run **once, as written**, in
this tree, before any implementation work. The point is to prove the instruments are real and legible
*before* anything depends on them.

## Classification FIRST, exit codes second

A sweep that does not separate the two kinds of criterion is misreadable:

- a **progress** criterion must be **RED before** the work and **GREEN after**;
- an **invariant** criterion must be **GREEN before AND after** — it is a regression guard.

A green invariant in a pre-work sweep is **correct**. The hazard is the reflex repair: "fixing" a green
invariant into failing today inverts a working regression guard into a broken one. A green *progress*
criterion is the opposite — a live defect (a vacuous criterion), and this plan's own review cycles
caught four of them.

plan-058 carries **25** criteria. Classified before any command was run:

| Kind | Count | Ids |
| :-- | --: | :-- |
| **invariant** | 1 | SC7 — "the existing suite passes with no modification to the three `collect_parent_edges` stubs" is by construction true before and after |
| **progress** (runnable) | 18 | SC1, SC1b, SC2, SC2b, SC3, SC3b, SC3c, SC4, SC4b, SC4c, SC5, SC5b, SC6, SC6b, SC6c, SC8, SC8b, SC8c |
| **progress** (manual — no runnable command) | 6 | SC1c, SC3d, SC9, SC9b, SC10, SC11 |

Plus the **2** gate `Test:` commands (Fan-out eliminated; Mechanical fan-out check green), both of which
gate work that has not happened.

**Expectation derived from that classification, stated before reading any exit code:**
21 runnable instruments → **20 RED, 1 GREEN (SC7)**.

## Result: 20 RED, 1 GREEN — the expectation met exactly

No green progress criterion. No vacuous criterion found.

Run: 2026-08-29T00:42:24Z · branch `plan-058-james-dixson-0e36fd-execute` · HEAD `b065196`

| Kind | Id | Class | Exit | Verdict | Last line |
| :-- | :-- | :-- | --: | :-- | :-- |
| GATE | Capability Gate: Fan-out eliminated | gate test | 1 | RED — expected | `107 passed in 0.25s` |
| GATE | Capability Gate: Mechanical fan-out check green | gate test | 2 | RED — expected | `  Caused by: No such file or directory (os error 2)` |
| CRIT | SC1 | progress | 5 | RED — expected | `107 deselected in 0.02s` |
| MANUAL | SC1c | progress | MANUAL | manual — not runnable | `n/a` |
| CRIT | SC1b | progress | 5 | RED — expected | `107 deselected in 0.02s` |
| CRIT | SC2 | progress | 5 | RED — expected | `107 deselected in 0.02s` |
| CRIT | SC2b | progress | 5 | RED — expected | `107 deselected in 0.02s` |
| CRIT | SC3 | progress | 5 | RED — expected | `107 deselected in 0.03s` |
| CRIT | SC3b | progress | 1 | RED — expected | `550:def deps_for_show(bead_id: str) -> list[dict]:` |
| MANUAL | SC3d | progress | MANUAL | manual — not runnable | `n/a` |
| CRIT | SC3c | progress | 5 | RED — expected | `107 deselected in 0.02s` |
| CRIT | SC4 | progress | 5 | RED — expected | `107 deselected in 0.02s` |
| CRIT | SC4b | progress | 2 | RED — expected | `  Caused by: No such file or directory (os error 2)` |
| CRIT | SC4c | progress | 5 | RED — expected | `107 deselected in 0.02s` |
| CRIT | SC5 | progress | 5 | RED — expected | `107 deselected in 0.02s` |
| CRIT | SC5b | progress | 5 | RED — expected | `107 deselected in 0.04s` |
| CRIT | SC6 | progress | 2 | RED — expected | `  Caused by: No such file or directory (os error 2)` |
| CRIT | SC6c | progress | 2 | RED — expected | `  Caused by: No such file or directory (os error 2)` |
| CRIT | SC6b | progress | 1 | RED — expected | `` |
| CRIT | SC7 | **invariant** | 0 | **GREEN** — expected | `107 passed in 0.20s` |
| CRIT | SC8 | progress | 1 | RED — expected | `` |
| CRIT | SC8b | progress | 1 | RED — expected | `` |
| CRIT | SC8c | progress | 1 | RED — expected | `` |
| MANUAL | SC9 | progress | MANUAL | manual — not runnable | `n/a` |
| MANUAL | SC9b | progress | MANUAL | manual — not runnable | `n/a` |
| MANUAL | SC10 | progress | MANUAL | manual — not runnable | `n/a` |
| MANUAL | SC11 | progress | MANUAL | manual — not runnable | `n/a` |

## Reading the exit codes

| Exit | Cause | Instrument is |
| --: | :-- | :-- |
| 0 | the check passed | live |
| 1 | `grep` found nothing, or the "Fan-out eliminated" gate's `test -s` half found no timing artifact (its pytest half passed: 107 passed) | live |
| 2 | the script named does not exist yet (`check_no_universe_fanout.py`, `test_check_no_universe_fanout.py`) | live |
| 5 | pytest collected **no** test matching the `-k` selector — the named test does not exist yet | live |

No instrument failed for an **unreadable** reason. Every red names a specific missing artifact that a
specific issue in this plan creates.

## Vacuity check on the `-k` selectors

Issue 3.3 records that a bare `-k zero_bd_show` is already satisfied by the pre-existing
`test_closable_issues_one_bd_list_and_zero_bd_show`, which is why the criteria name their tests
explicitly. That hazard was re-tested here directly — `--collect-only` against the pre-work suite:

| Selector | Pre-existing tests collected |
| :-- | --: |
| `timeout` | 0 |
| `existing_labels` | 0 |
| `push_zero_bd_show or enumerate_zero_bd_show` | 0 |
| `collect_parent_edges` | 0 |
| `scale_independence` | 0 |

All five are **non-vacuous**: none can be satisfied by a test this plan did not write. The two broadest
selectors (SC4's bare `timeout`, SC5b's bare `existing_labels`) were the ones at risk, and both are clean.
