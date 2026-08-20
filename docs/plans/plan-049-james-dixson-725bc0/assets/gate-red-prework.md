---
type: Reference
okf_spec: OKF-PLAN
id: gate-red-prework
description: Both capability-gate scripts observed RED at exit 1 before their capability existed (Issues 0.7/0.8 / SC30)
---

# SC30 evidence: both capability-gate scripts observed **RED at exit 1** before their capability existed

**Issues:** plan-049 0.7 (`gate-run.sh`) and 0.8 (the two gate scripts) · **Criterion:** SC30
**Recorded:** 2026-08-20, at `HEAD = 458092d`, before Issue 1.1 or Epic 3 had landed anything.

## Why "exit 1" and not merely "red"

SC30 asks for **1 — not 2, not 127**, and the three values are genuinely different outcomes:

| Exit | Meaning | Gate state | Reads to an operator as |
| --: | :-- | :-- | :-- |
| `0` | capability present | opens | work proceeds |
| `1` | capability **absent** | **RED** | this gate is blocking, and correctly so |
| `2` | harness could not run | **UNRESOLVED** | *nothing* — the gate neither opens nor blocks |
| `127` | bash: script not found | UNRESOLVED (via 2) | a **stall**, indistinguishable from a hung plan |

A gate script that does not yet have its deliverable must return **1**. Returning 2 — or being
absent, which bash reports as 127 — leaves the gate unresolved, the blocked work never runs, and
the failure presents as a stall rather than as the missing capability it is. That is precisely
the confusion `gate-run.sh` (Issue 0.7) exists to remove, by mapping every exit outside {0,1,2}
to an explicit **2** with a stated harness-failure message.

## The measurement

Both scripts were driven through `gate-run.sh` **before** `_shared/dag_guard.py` existed and
before any Epic 3 fixture existed:

```console
$ bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh \
       docs/plans/plan-049-james-dixson-725bc0/scripts/gate-dagguard.sh
gate-dagguard: CAPABILITY ABSENT — _shared/dag_guard.py does not exist (Issue 1.1 ships it).
$ echo $?
1

$ bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh \
       docs/plans/plan-049-james-dixson-725bc0/scripts/gate-cellcheck.sh
gate-cellcheck: CAPABILITY ABSENT — fixture tests/fixtures/doc-checks/m-empty-required-cell/plan.md is missing.
gate-cellcheck: CAPABILITY ABSENT — fixture tests/fixtures/doc-checks/m-zero-row-criteria/plan.md is missing.
gate-cellcheck: CAPABILITY ABSENT — fixture tests/fixtures/doc-checks/m-gate-all-three-absent/plan.md is missing.
gate-cellcheck: CAPABILITY ABSENT — fixture tests/fixtures/doc-checks/control-conformant/plan.md is missing.
gate-cellcheck: CAPABILITY ABSENT — fixture tests/fixtures/doc-checks/control-canonical-start-gate/plan.md is missing.
gate-cellcheck: the fixtures are part of the deliverable (Issues 3.1/3.2/3.2b).
$ echo $?
1
```

| Gate script | Pre-work exit | Required by SC30 | Verdict |
| :-- | --: | --: | :-- |
| `gate-dagguard.sh` | **1** | 1 | ✅ RED for the right reason |
| `gate-cellcheck.sh` | **1** | 1 | ✅ RED for the right reason |

Recorded **before** the work, which is the only order in which the observation means anything:
run afterwards, both scripts return 0 and the pre-work claim becomes unfalsifiable.

## The wrapper's own contract, driven on all eight paths

`gate-run.sh` is the component that makes the "1, not 127" distinction possible at all, so its
contract is driven directly rather than assumed:

| Input | Exit | Expected |
| :-- | --: | --: |
| script does not exist (bash would give 127) | 2 | 2 |
| no argument at all | 2 | 2 |
| inner script `exit 0` | 0 | 0 |
| inner script `exit 1` | 1 | 1 |
| inner script `exit 2` | 2 | 2 |
| inner script `exit 42` | 2 | 2 |
| inner script runs a missing command (127) | 2 | 2 |
| inner script killed by a signal (143) | 2 | 2 |

Eight for eight. The wrapper emits **only** 0, 1 or 2.

## The distinction the two scripts encode

`gate-run.sh` maps an inner **127** to 2, because "a command inside the script was not found" is
a missing *dependency* — a harness fault. But when the gate script itself detects that its own
**deliverable** is absent, that is the capability being absent, and it returns **1** deliberately.
The two look superficially alike and mean opposite things; conflating them is how a red gate
becomes a stall.
