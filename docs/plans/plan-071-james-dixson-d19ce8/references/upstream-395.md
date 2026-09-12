---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #395 - `bd mol pour` drops the formula''s declared gate
  type — REQ-DATA-040 verifies a field the poured bead never carries (metadata null
  on 153 of 232 gates)'
---
# Upstream #395: `bd mol pour` drops the formula's declared gate type — REQ-DATA-040 verifies a field the poured bead never carries (metadata null on 153 of 232 gates)

- **Number:** 395
- **Title:** `bd mol pour` drops the formula's declared gate type — REQ-DATA-040 verifies a field the poured bead never carries (metadata null on 153 of 232 gates)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

`REQ-DATA-040` cites a declaration `bd mol pour` never carries. Measured while investigating #388 (plan-070 EXP-001).

The `plan-execute` formula's start-gate step declares `[steps.gate] type = "human"`. The poured start gate for plan-068 (`yf-mol-7bor`, "Gate: human") has **`metadata: null`** — the pour does not translate the formula's gate type into bead metadata.

Corpus-wide across 232 gates: `gate_type` **absent on 153**, dominated by poured start gates and reconcile gates. So any requirement whose Verification reads the formula's declared type off the poured bead is verifying a field that does not exist.

This is #392's class ("declared in prose, acted on by code") one level below #388: #388 is the SKILL.md snippet dropping the metadata; this is the **pour itself** dropping it. plan-070 fixes the reconcile gate's carry (Issue 1.1) but explicitly does not touch the pour — filing so it is not silently dropped.

Found at plan-070 pass-1 C9. File, don't fix.

