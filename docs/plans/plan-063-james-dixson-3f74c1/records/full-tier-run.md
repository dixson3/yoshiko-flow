# FULL-tier validation run (Issue 6.3 / SC12)

**Verdict: PASS — 68/68 commands, 0 failing.** Raw envelope: [full-tier-run.json](full-tier-run.json).

| field | value |
| :-- | :-- |
| command | `uv run skills/yf-change-validation/scripts/change_validation.py run --tier full --json` |
| date | 2026-09-04 |
| branch | `plan-063-james-dixson-3f74c1-execute` |
| HEAD | `fb33e102c8d9f8dac79512d49b9152783084e353` |
| `main` tip | `eb0d859df0615b3c357ef31e7cb0012ca070a340` |
| merge-base | `eb0d859df0615b3c357ef31e7cb0012ca070a340` |

## Why this IS the merged tree

`main` has not moved since this plan's execute branch was cut: `main`, the merge-base and the
plan's base are all `eb0d859`. The merge is therefore a **fast-forward-equivalent**
`--no-ff` of the execute branch onto an unchanged target, so the tree `land`'s L2 produces is
byte-identical to the tree this run validated. `land --dry-run` independently confirms it:
`merge_preview.available: true`, `conflicts: []`.

Stated as the limitation it is: this equivalence holds **only while `main` stays at that tip**.
If another plan lands first, the manifest digest changes, `land --apply` halts as a staleness
report (`REQ-LAND-011`), and L3 re-runs this tier against the real merged tree — which is the
control that makes recording this run safe rather than a substitute for it.

## First run, and why it failed

The first FULL run failed on exactly one command — `okf-index-drift`, reporting that
`assets/` was present in **this bundle** and absent from its `index.md`. That is Issue 6.6's
work, which the DAG places after this issue. The index was brought current, `okf.py reindex
--check` went clean, and the tier was re-run from scratch. Recorded rather than quietly
re-run: a green that followed a red is a different fact from a green on the first attempt.

## Scope note (SC12)

SC12 is deliberately **manual**, not a clause. `recheck-criteria` would re-run this
multi-minute tier at L5 and again at L11, and its 300 s cap would record a timeout as FAIL
**past the irreversible boundary**.
