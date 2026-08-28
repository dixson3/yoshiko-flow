---
type: Finding
okf_spec: OKF-PLAN
description: "Re-derived measurement of doc_lint's terminal-status demotion — 392 findings demoted, 197 of them truly E (2026-08-28)."
---
# exec-001: what the terminal-status demotion actually suppresses

**Issue:** 0.12 · **Measured:** 2026-08-28 · **Discharges:** D-1's re-derivation obligation, SC27 (with 0.8)

## Why this measurement exists

D-1 originally cited "**~423 findings**" as the size of the remediation burden that re-judging
history would create. That figure was **unsourced**, and it collided numerically with the
**separate and equally stale** "`0 of 423` nested files carrying `description:`" claim that Issue
0.8 corrects in the shipped specs. Two different quantities, one number, neither traceable to a
run. This file replaces the first with a reproducible measurement; Issue 0.8 replaces the second.

## Approach Tested

Two full-corpus `doc_lint` runs over the same tree, differing in exactly one edit:

```bash
# (a) as shipped
uv run _shared/doc_lint.py --json --show-report-only

# (b) probe: the five TERMINAL rows of STATUS_SEVERITY
#     ("approved", "executing", "reconciling", "complete", "abandoned")
#     changed from {WARN: REPORT, ERROR: REPORT} to {} — demotion disabled,
#     nothing else touched. Run as a throwaway copy inside _shared/ so that
#     TYPES_DIR still resolves to _shared/document_types/, then removed.
uv run _shared/_probe_doc_lint_nodemote.py --json --show-report-only
```

The probe is a **measurement instrument, not a change**: it left no residue and no shipped file
was modified. `STATUS_SEVERITY`'s demotion is left intact, per D-1.

## Result

**measured:** two full-corpus runs, same tree, one edit apart.

| run | files | findings | `E` | `W` | `R` | verdict | exit |
| :-- | --: | --: | --: | --: | --: | :-- | --: |
| (a) as shipped | 1116 | 1643 | **0** | 612 | 1031 | PASS | 0 |
| (b) demotion disabled | 1116 | 1643 | **197** | 807 | 639 | FAIL | 1 |

**The real number is 392** — `1031 − 639` findings that the terminal-status rule currently demotes
to `R`. Of those, **197 are truly `E`** and **195 are truly `W`**. This reproduces D-1's re-measured
392 exactly on a corpus that has since grown by 28 files (1088 → 1116), which is itself weak
evidence that the quantity is stable rather than incidental.

**"~423" was standing in for 392.** The two are 8% apart, which is why the substitution went
unnoticed for a full plan cycle.

## Implications for Plan

**measured:** all 197 suppressed errors come from **seven** checks on the `plan` type, concentrated in **46** bundles:

| check | suppressed `E` |
| :-- | --: |
| `criteria-table-columns` | 46 |
| `criterion-ids` | 44 |
| `risks-table-columns` | 41 |
| `no-retired-phase-log` | 32 |
| `identity-frontmatter` | 30 |
| `upstream-table-columns` | 2 |
| `required-sections` | 2 |

**inferred:** every one is a **schema-shape** rule written after the bundles it fires on. That is the substance
of D-1's "history is not re-judged by a rule written after it", and it is the reason this plan
leaves the demotion in place: the 392 are not latent defects in live artifacts, they are a newer
schema meeting older records.

## Recommendations

### Leave the demotion in place; do not re-judge history

### What this does NOT license

It does not show that `doc_lint` is *fit* as a gate. The motivating defect stands unchanged: 46 of
48 checks are structurally incapable of a non-zero exit at `complete`, and this measurement is
precisely the size of the blind spot. The plan's answer is forward-only enforcement (D-1) plus the
`promote = false` close-out binding (Issues 0.2 / 1.6), not a retroactive re-judging.
