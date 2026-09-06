---
type: Finding
okf_spec: OKF-PLAN
description: 'Issue 0.4 / 0.5 — negative controls for all eleven plan065_checks.py subcommands,
  plus the four pre-transform tree-property FALSE reports (SC13, SC14)'
---
# Negative controls for `plan065_checks.py`

**Companion to `negative-controls.json`.** The JSON is the machine record; this file is why
each control is the *right* control.

## The contract being proven

`plan065_checks.py` distinguishes three outcomes, and the whole instrument is worthless if it
cannot tell the second from the third:

| exit | verdict | means |
| --: | :-- | :-- |
| 0 | `PASS` | the condition holds |
| 1 | `FALSE` | the condition was checked and does **not** hold |
| 2 | `INCONCLUSIVE` | the check **could not run** (input absent, tool missing, bad JSON) |

**A control is only valid at a non-zero exit, and a tree-property FALSE report is only valid at
exit 1.** An exit 2 says the instrument is absent; it says nothing about the tree. That is the
distinction Issue 0.5 exists to enforce, and it is the same conflation the repo has been bitten
by twice already (`doc_lint`'s `not-selected` vs `no-such-path`, #181; `resume-scan`'s `found`,
#207).

## No repository mutation occurred

SC12 forbids this plan from modifying any engine source. A literal reading of "mutate the
condition each claims to detect" would, for `no-engine-edits`, mean editing a `skills/**/*.py`
— which would breach the very criterion the control is proving. So:

- **the four tree-property subcommands** (`audit-strict`, `bundle-shape`, `phaselog-bullets`,
  `index-drift-strict`) need no mutation: the live pre-transform tree already exhibits their
  condition as false. That is Issue 0.5, recorded below.
- **every other control is driven by a synthesized `--input` / `--root` fixture** under
  `assets/negative-controls/`. Nothing outside this plan's own bundle was touched.

The fixture tree (`assets/negative-controls/tree/`) is structurally invisible to the corpus
engines: `okf_hygiene.discover` treats a directory carrying a member marker as a **leaf** and
never descends into one, and `docs/plans/plan-065-.../plan.md` makes this bundle exactly that.
`check_okf_index_drift.py` enumerates depth-1 roots and never `rglob`s. Verified by measurement,
not by reading: `bundles_checked` is 70 before and after the fixtures existed.

## Why each control is the right control

Four of the eleven are not merely "some failing input" — they reproduce a **measured** failure
shape this repository has actually produced.

| subcommand | the control | why it is the right one |
| :-- | :-- | :-- |
| `audit-strict` | audit JSON with `legacy: 0`, `verdict: pass`, `exit: 0`, `counts.unclassifiable: 1` | **`legacy` alone is blind to it.** `legacy` sums only `legacy-readme + legacy-underscore-index + hybrid-partial` (`okf_hygiene.py:977-978`), so a bundle *wrecked* by the transform into `unclassifiable` yields a fully green audit. This is the failure mode the plan is most exposed to, and the bare verdict cannot see it |
| `index-drift-strict` | drift JSON with `exit: 0`, `verdict: clean`, `no_index: 8` | **The exact shape measured at drafting.** `no_index` contributes nothing to the bare check's verdict — it reported `no_index: 8` and still exited 0. Without the added conjunct, SC3 was vacuously green before the plan ran (R10) |
| `restore-roundtrip` | all four hashes equal | **The silent-total-loss shape.** An earlier draft asserted only `post_reversal == pre_backfill`, which this fixture satisfies — it is precisely what a **no-op** restore produces, and it is what `restore --apply` on a committed backfill returns while leaving the bundle with no `README.md`, no `index.md` and no `log.md` (exp-003). The third conjunct (`post_reversal != post_backfill`) is what makes the check non-vacuous |
| `registered` | a manifest naming the script only in a §1 **blockquote** and in a **FAST** row | A substring grep passes on both. The check parses `## 1. Tiers` → `### full` → the GFM table structurally and reads the row's argv, so neither a comment nor a stale FAST row can satisfy SC15 |

The remaining seven:

| subcommand | the control |
| :-- | :-- |
| `bundle-shape` | fixture target carrying `README.md` and neither `index.md` nor `log.md` |
| `phaselog-bullets` | a `log.md` carrying **nine** of plan-030's ten bullets. The dropped bullet's date still appears on surviving bullets, so the engine's own date-comparing guard would **not** catch it (R2) |
| `merged-objectives` | fixture `index.md` whose `> ` line is present but is not the exp-001 text — proving the check reads content, not presence |
| `no-engine-edits` | the **base** is re-pinned to `bcd1511` (plan-064 intake, before that plan's engine repair), so 9 real engine changes fall inside the diff. No file was edited |
| `apply-result` | correct headline counts (`transformed: 8`, `halted: 0`, `bundles_checked: 70`) but only **seven** rows with `action == "backfilled"` |
| `finding-counts` | before/after fixture pair where plan-010 regresses 12 → 13 |
| `negative-controls` | a controls file with two defects at once: a row recording `exit: 0`, and a tree-property entry whose reason is `input absent` |

## Result

**Eleven controls, eleven `FALSE` (exit 1), zero exit 0 and zero exit 2.** No control was
merely unrunnable — every one was checked and reported the condition false.

## Issue 0.5 — the pre-transform tree-property FALSE reports (SC14)

Run against the **live pre-transform tree**, before Epics 1–2 mutated anything. These are
irrecoverable: once the transform lands, this tree no longer exists and a re-run measures a
different claim.

**Scope is deliberately the four tree-property subcommands only.** The other seven read
artifacts this plan creates, so pre-transform they can report only `input absent` — and an
absent input is not evidence the condition is false. Any exit-2 report is **rejected** here
rather than recorded.

See `tree_property_false` in the JSON for the verbatim reasons.
