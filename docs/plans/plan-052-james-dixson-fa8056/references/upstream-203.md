---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #203: Exit-code discipline: five instruments report failure in output and success in $? — promote the 0/1/2 contract repo-wide

- **Number:** 203
- **Title:** Exit-code discipline: five instruments report failure in output and success in $? — promote the 0/1/2 contract repo-wide
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Filed by operator decision from the **plan-051** session. Related: #199, #198, #202, #173.

## The class

**An instrument reports failure in its OUTPUT and success in its EXIT CODE.** A scripted caller reads `$?`, sees `0`, and proceeds. The failure is not merely missed — it is converted into a positive signal.

This has now been hit **five times, in five separate instruments**, three of them tools this repo wrote. It is no longer a set of bugs; it is a convention gap.

## The instances

| # | Instrument | What it did | Where it was caught |
| --: | :-- | :-- | :-- |
| 1 | `redcheck.sh` (plan-050 `assets/`) | A **missing fixture** printed `RED observed` and exited **0**, writing a record with an empty exit-code field | plan-050 RE-005 — only because the plan mandated self-spiking the harness *before first use* |
| 2 | `bd mol burn` | Exits **0** on `Canceled` — a scripted pruner gets a silent no-op with a success code | plan-051, **reproduced** not quoted (#202) |
| 3 | `yf skills status` | `yf/src/cmd/status.rs` returns `Ok(())` **unconditionally**. `unmodified` / `up_to_date` / `complete` are printed; none reaches the exit code | plan-050; needs a `jq -e` wrapper to be usable in a script |
| 4 | `<cmd> \| tail -60` | Without `set -o pipefail` a pipeline returns **tail's** status. A real exit **1** read as **0** | plan-051 RE-005 — in the plan's own deploy harness, while executing the plan about unbacked assertions |
| 5 | plan-050 `SKILL.md` §6.4 | The **caller never read `$?` at all** — violating an ordering constraint returned `inconclusive` + exit 0 and nothing checked | plan-050 RE-007 |

Instance 4 is the one worth dwelling on: it occurred **inside the harness of the plan whose entire thesis is "an assertion that something ran, with nothing behind it."** The class reproduces itself in its own countermeasures.

## The adjacent-but-different case, named so it is not conflated

`change_validation.py`'s `run_command` **collapses a vocabulary** rather than masking a code: `inconclusive` fires **only** when the command's first token is off `PATH`; otherwise `0 -> pass` and **everything else -> `fail`**. So a deliberate exit-2 `INCONCLUSIVE` contract is inexpressible — it reports `fail`.

That is a *different* defect (a lossy mapping, not a lost signal) and it already has a home in #149's correction. It is listed here only so a reader does not merge the two.

## Why this keeps happening

The repo **has** the right convention and does not apply it uniformly. `gate-run.sh` (plan-049 -> plan-050 -> plan-051, adopted verbatim each time) normalizes to a genuine three-value contract:

```
0 = pass    1 = fail    2 = INCONCLUSIVE (the instrument could not run)
```

`doc_lint.py` carries the same one, documented down to the `2 = the linter could not run` case and the rule that INCONCLUSIVE maps to `warn`, never `fail`, at the intake binding.

So the convention exists, is written down, and is good. What is missing is anything that **enforces it on a newly written instrument**. Every instance above is a tool authored without the convention being applied, caught later by a human noticing.

## Proposed remedy

1. **State the 0/1/2 contract as a repo-level requirement**, not a per-plan asset that gets copied forward by hand. Three plans have now copied `gate-run.sh` byte-for-byte; that is a convention asking to be promoted.
2. **`set -o pipefail` in every harness script**, and a standing rule: *never pipe a command whose exit code you need.* Instance 4 is pure pipeline semantics and costs one line to prevent.
3. **Require a failure-path arm for any instrument the repo ships.** Instance 1 was caught *only* because plan-050 mandated re-spiking the harness before first use, with an arm asserting the **missing-fixture** case exits non-zero. That mandate should not be per-plan.
4. **For third-party tools that cannot be fixed** (`bd mol burn`, and `yf skills status` until #-this changes it), record the required wrapper at the call site — `--force`, `jq -e` — rather than leaving each caller to rediscover it.

## The principle worth writing down

**An instrument that cannot report its own failure is worse than no instrument**, because it converts an unknown into a false positive. Every instance above was found by a human re-running something by hand. That is the same detection mechanism #199 identifies for success criteria, and it does not scale.

