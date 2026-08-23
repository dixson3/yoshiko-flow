---
type: Reference
okf_spec: OKF-PLAN
id: sc7-wisp
description: SC7 verification of the plan-review wisp — all four clauses, with the instrument each is read from
---

# SC7 — the Phase-3 `plan-review` wisp

Phase 3 was the **only phase with no bead representation**: Phase 2 is a wisp
(`plan-investigate`), Phase 5 is a pour (`plan-execute`), Phase 3 was a prose loop.
`skills/yf-plan/formulas/plan-review.formula.toml` closes that gap.

## The four clauses, each with its instrument

| Clause | Instrument | Result |
| :-- | :-- | :-- |
| **1 (positive)** `bd cook --dry-run` succeeds **and** its emitted step-id **set equals** `{conformance, red-team, resolve, gate}`, in a chain with the gate terminal | `bd cook --dry-run` | **PASS** — exit 0; emitted set equal; each step `needs` exactly its predecessor; `gate` is last, is gate-typed, and nothing needs it |
| **2 (negative)** no step has more than one `needs` entry — arms stay **sequential** | the `.toml` | **PASS** — 0 offenders |
| **3 (negative)** no step or var records a review-cycle count | the `.toml` | **PASS** — 0 matching vars, 0 matching step keys |
| **4** every **non-gate** step carries a non-empty description | **the `.toml` DIRECTLY** | **PASS** — lengths 294 / 511 / 395 (gate 194) |

**The positive clause is required because the two negatives are vacuously true of an empty
formula** (pass-1 C6): a zero-step file cooks, has no multi-`needs` step, and records no
counter. Clause 1 is what makes clauses 2 and 3 mean something.

**Clause 4 is read from the `.toml`, NOT from `bd cook --dry-run`** (pass-5 C45). The dry-run
emits only `step-id: Title (type)` and carries **no description field**, so the clause is not
observable from the instrument SC7 otherwise names. Reading it from the wrong instrument would
have made the clause unfalsifiable.

**Stated limit (pass-2 C28):** four *empty* steps with the right ids in the right order would
still satisfy clauses 1–3. Under **D-7** that is close to the whole deliverable — the wisp is
scoped to *sequencing*, so step identity and order **are** the substance — which is exactly why
clause 4 exists as the guard against a skeleton.

## D-7 and the non-goal, both recorded in the formula itself

- **No parallel lenses.** EXP-005 **built** the fan-out and drove it (`needs` is an array;
  multi-parent fan-in is first-class), so parallelism is *buildable*. It is declined for lack
  of evidence: **29 review passes across four plans, all sequential, one reviewer each.** The
  5 → 4 → 11 → 17 → 14 series sometimes cited for it measures **independence**, not parallelism.
- **The review-cycle counter stays in FILES.** `len(glob('reviews/pass-*.md'))` is monotonic
  (REQ-PLAN-030 / REQ-PORT-006). A wisp is ephemeral and burnable, so a counter inside one is
  **resettable by `bd mol burn`** — restoring the unbounded self-resolving loop the bound
  exists to forbid. The wisp orchestrates dispatch; the file remains the ledger.
- **Burning it:** `bd mol burn <id> --force`, **checking the output, not the exit code** —
  measured, a cancelled burn on a wisp with an open APPROVE gate exits **0** (R5). Filed
  upstream by Issue 4.6 so the fix is not private to this plan.
