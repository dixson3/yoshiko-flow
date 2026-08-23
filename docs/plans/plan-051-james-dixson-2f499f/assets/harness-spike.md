---
type: Reference
okf_spec: OKF-PLAN
id: harness-spike
description: Re-spike record for the copied control harness (Issue 0.2), run before first use
---

# Harness re-spike — `redcheck.sh` + `gate-run.sh`

Issue 0.2 mandates re-spiking the **copied** harness into `assets/` **before first use**.
The reason is on record: plan-050's RE-005 documents `redcheck.sh` once reporting
*"RED observed"* with **exit 0** for a **missing fixture** — a harness reporting success while
running nothing. EXP-004 confirms the fix is in the shipped script, but 0.2's own portability
argument applies to the harness's trustworthiness too: a cold reader in a different repo must be
able to re-run the evidence from this bundle alone, and that includes the instrument.

Run in a throwaway `$(mktemp -d)` with synthetic fixtures, `YF_TREE` pointed at the sandbox.

| # | Arm | Expected | Observed |
| :-- | :-- | --: | --: |
| A1 | `record-red` against a **missing** fixture — the RE-005 regression | 2 | **2** |
| A2 | `record-red`, fixture exits non-zero (unfixed tree) | 0 | **0** |
| A3 | `assert-distinguishes`, fixture still non-zero | 1 | **1** |
| A4 | `assert-distinguishes`, fixture green with a RED on record | 0 | **0** |
| A5 | `verify-all`, both records present | 0 | **0** |
| A6 | `record-red` for a control absent from `controls.txt` | 2 | **2** |
| A7 | unknown verb | 2 | **2** |
| A8 | manifest count differs from the `plan.md`-derived count | 1 | **1** |
| A9 | empty manifest — vacuous certification refused | 2 | **2** |
| B1 | `gate-run.sh` naming a script that does not exist | 2 | **2** |
| B2 | `gate-run.sh` wrapping a script that exits 1 | 1 | **1** |
| B3 | `gate-run.sh` wrapping a script that exits 5 (outside the contract) | 2 | **2** |

**12 of 12 arms as specified.** A1 is the load-bearing one: it is the exact defect RE-005
recorded, and it is fixed in the copied script.

## The two edits made to the copied files

Copied byte-for-byte from `docs/plans/plan-050-james-dixson-d0414b/assets/`, then:

1. **Header comment line only** (line 2 of each file) — provenance.
2. **`verify-all`'s count derivation tightened** to `grep -oE 'ctl-(165|182|184)-[a-z-]+'`.
   The inherited generic `ctl-[0-9]{3}-[a-z-]+` is contaminated by prose naming *another*
   plan's control ids, which EXP-004 measured wedging the gate at 7-declared-vs-1-manifest.

**Measured on this bundle, both patterns derive 3 against a 3-line manifest** — so the
tightening is **insurance, not a live fix**, and R6's 7-vs-1 figure was EXP-004's synthetic
arm rather than this bundle. The opposite failure mode is stated in the script itself: a
control for an issue number outside {165, 182, 184} is **invisible** to the derivation, so
adding one requires widening the alternation.
