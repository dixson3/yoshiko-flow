---
type: Finding
okf_spec: OKF-PLAN
---
# Verification sweep — every landed instrument that reads this bundle

Issue 0.1 (intake) / Issue 0.3 (reconcile). Every gate `Test:`, every non-`manual:`
Success Criterion, and the five landed instruments, run **as written** from the repo
root, each as a single `bash -c` string so the recorded code is the **composite** exit.

Row grammar is fixed: `RC <label> <exit-code>` at line start (SC0 and SC0a grep it).
`INCONCLUSIVE` and `MANUAL` are recorded for instruments that declare no runnable
command — neither is a failure, and neither matches SC0's `[1-9]` pattern.

**Three rows are SELF-REFERENTIAL and are resolved as a verified fixed point.**
`SC0` and `SC0a` read this file directly; `recheck-criteria` reads it transitively,
because it evaluates the criteria table that contains `SC0`. Running any of them
before this block is rewritten evaluates it against the PREVIOUS block — which is
how the first attempt wrote its own failure into the new file. So the block is
written with those three ASSERTED zero, then each is RUN against what was written;
if any disagrees, the true non-zero value replaces it and the disagreement stands
recorded. An assertion that is checked is not an assumption.

## Exit codes

```
RC gate-severity-vocabulary 0
RC gate-escalation-schema 0
RC gate-upstream-writes INCONCLUSIVE
RC SC0b 0
RC SC1 0
RC SC1b 0
RC SC1c MANUAL
RC SC2b 0
RC SC2c 0
RC SC2d 0
RC SC3 0
RC SC4 0
RC SC4b 0
RC SC5 0
RC SC5b MANUAL
RC SC6 0
RC SC6d 0
RC SC6b 0
RC SC6c 0
RC SC7 MANUAL
RC SC8 MANUAL
RC SC8b 0
RC SC9 MANUAL
RC SC9b 0
RC SC9c 0
RC SC10 0
RC gate-consistency 0
RC okf-check 0
RC pour-fidelity 0
RC audit-close 0
RC recheck-criteria 0
RC SC0a 0
RC SC0 0
```

## Notes per row

| Label | Code | Note |
| :-- | :-- | :-- |
| `gate-severity-vocabulary` | `0` | — |
| `gate-escalation-schema` | `0` | true |
| `gate-upstream-writes` | `INCONCLUSIVE` | no Test: declared — a green command cannot establish authorization |
| `SC0b` | `0` | true |
| `SC1` | `0` | true |
| `SC1b` | `0` | true |
| `SC1c` | `MANUAL` | manual verification — not a command |
| `SC2b` | `0` | true |
| `SC2c` | `0` | true |
| `SC2d` | `0` | true |
| `SC3` | `0` | true |
| `SC4` | `0` | true |
| `SC4b` | `0` | } |
| `SC5` | `0` | true |
| `SC5b` | `MANUAL` | manual verification — not a command |
| `SC6` | `0` | true |
| `SC6d` | `0` | true |
| `SC6b` | `0` | true |
| `SC6c` | `0` | true |
| `SC7` | `MANUAL` | manual verification — not a command |
| `SC8` | `MANUAL` | manual verification — not a command |
| `SC8b` | `0` | all passed |
| `SC9` | `MANUAL` | manual verification — not a command |
| `SC9b` | `0` | true |
| `SC9c` | `0` | true |
| `SC10` | `0` | true |
| `gate-consistency` | `0` | — |
| `okf-check` | `0` | — |
| `pour-fidelity` | `0` | — |
| `audit-close` | `0` | — |
| `recheck-criteria` | `0` | — |
| `SC0a` | `0` | — |
| `SC0` | `0` | — |

## Mutation assertion

No verification mutated the bundle it verifies. Every criterion that needs a
writable target copies the bundle to `$(mktemp -d)` first, so `recheck-criteria`'s
in-table-order execution cannot have one row change the state a later row reads.

