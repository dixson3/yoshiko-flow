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

## Exit codes

```
RC gate-severity-vocabulary 1
RC gate-escalation-schema 1
RC gate-upstream-writes INCONCLUSIVE
RC SC0b 0
RC SC1 1
RC SC1b 1
RC SC1c MANUAL
RC SC2b 1
RC SC2c 0
RC SC2d 4
RC SC3 4
RC SC4 1
RC SC4b 1
RC SC5 4
RC SC5b MANUAL
RC SC6 4
RC SC6d 4
RC SC6b 5
RC SC6c 1
RC SC7 MANUAL
RC SC8 MANUAL
RC SC8b 2
RC SC9 MANUAL
RC SC9b 1
RC SC9c 4
RC SC10 4
RC recheck-criteria 1
RC gate-consistency 0
RC okf-check 0
RC pour-fidelity 0
RC audit-close 0
RC SC0a 0
RC SC0 1
```

## Notes per row

| Label | Code | Note |
| :-- | :-- | :-- |
| `gate-severity-vocabulary` | `1` | — |
| `gate-escalation-schema` | `1` | false |
| `gate-upstream-writes` | `INCONCLUSIVE` | no Test: declared — a green command cannot establish authorization |
| `SC0b` | `0` | true |
| `SC1` | `1` | false |
| `SC1b` | `1` | false |
| `SC1c` | `MANUAL` | manual verification — not a command |
| `SC2b` | `1` | false |
| `SC2c` | `0` | Installed 2 packages in 4ms |
| `SC2d` | `4` | invalid issue format: "" |
| `SC3` | `4` | Error: No such command 'escalation-resolve'. Did you mean 'config-resolve'? |
| `SC4` | `1` | false |
| `SC4b` | `1` | Installed 5 packages in 14ms |
| `SC5` | `4` | Error: No such command 'escalation-report'. Did you mean 'retrospective-report'? |
| `SC5b` | `MANUAL` | manual verification — not a command |
| `SC6` | `4` | Error: No such command 'judgement-echo-check'. |
| `SC6d` | `4` | Error: No such command 'judgement-echo-check'. |
| `SC6b` | `5` | BrokenPipeError: [Errno 32] Broken pipe |
| `SC6c` | `1` | false |
| `SC7` | `MANUAL` | manual verification — not a command |
| `SC8` | `MANUAL` | manual verification — not a command |
| `SC8b` | `2` |   Caused by: No such file or directory (os error 2) |
| `SC9` | `MANUAL` | manual verification — not a command |
| `SC9b` | `1` | false |
| `SC9c` | `4` | invalid issue format: "" |
| `SC10` | `4` | Error: No such command 'escalation-report'. Did you mean 'retrospective-report'? |
| `recheck-criteria` | `1` | — |
| `gate-consistency` | `0` | — |
| `okf-check` | `0` | Installed 1 package in 2ms |
| `pour-fidelity` | `0` | — |
| `audit-close` | `0` | — |
| `SC0a` | `0` | — |
| `SC0` | `1` | — |

## Mutation assertion

No verification mutated the bundle it verifies. Every criterion that needs a
writable target copies the bundle to `$(mktemp -d)` first, so `recheck-criteria`'s
in-table-order execution cannot have one row change the state a later row reads.

