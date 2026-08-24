---
type: Review
okf_spec: OKF-PLAN
id: pass-2
description: Red-team pass 2 (second independent) — REVISE, 4 high / 5 medium / 3 low; 9 of 12 concerns live inside a pass-1 fix
---

# Red-team pass 2

## Verdict: REVISE

4 high, 5 medium, 3 low. **ALL 12 RESOLVED** (see Resolutions). **9 of the 12 concerns originate inside a pass-1 resolution**, and one is
an outright **regression** — H3's fix left the plan measurably worse on the exact axis H3 named.
That is consistent with `exp-002`'s measured 75% base rate, and is further corroboration for it.

**Reproduction tally: 16 genuinely fixed · 5 partially fixed · 1 REGRESSED · 1 fixed-with-a-cost.**

## Strengths (all verified by execution)

- **H5 is completely fixed.** `grant … --check /dev/null --json` → exit **1**, `"verdict": "fail"`;
  absent file → exit 1. Single physical line, real `verdict` key. The gate that could not fail now can.
- **M1 is clean.** All **33/33** criteria parse; **`→ exit non-zero` is used ZERO times**, so the
  1-vs-2 hazard is absent rather than merely mitigated. SC3 correctly reads `→ exit 1`.
- **The DAG is sound** — 30 issues, 46 edges, `unparsed: []`, acyclic, every `Discharged-by` names a
  real issue, every one of the 30 issues discharges ≥1 criterion.
- **The Reconcile Gate survived the rewrite**; `red-prework-ext` is genuinely reachable; H1 fixed
  (`audit` exit 0); H7's 30/30 `touches:` are honest (42 paths; all 16 non-existent are new files).
- **M9 measured resolved** — the pass-1 worry that 3.4 might promote a rule the plan's own table
  trips is disproved: `doc_lint` PASS, and `verify-reconcile` parses 17 rows without tripping on
  `Resolved By: EXP-002`.

## The unifying root cause

**Three separate pass-1 fixes each introduced or relied on ONE LEVEL OF INDIRECTION, and every
guard this plan ships is STRING-MATCHING OVER NAMES.** L2 routed all controls through
`gate-run.sh run <id>`; H3 added controls; M6 specified a name-matching predicate. **C1, C3 and C8
are the same defect seen from three angles.** Piecemeal fixes will re-inject. The durable fix is to
make `controls.txt` **generated**, so the asserted set, the built set and the gate's evidence set
are one object rather than three hand-maintained lists.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | **high** | **H3's fix REGRESSED its own axis.** 25 `ctl-*` ids asserted in criteria, **14 built**, **11 orphaned**. Pass 1 found 8 unbuilt; the fix added builders but simultaneously added six new criteria naming six new controls and never re-derived the total. **8 → 11.** SC2's literal "13" matches neither 25 nor 14 |
| C2 | **high** | **`red-prework-core` is cyclic in substance.** Its Condition requires RED for *every* Epic 0-4 control, but six (`ctl-class-a-fraction`, `ctl-touches-coverage`, `ctl-199b-fields`, `ctl-199b-recursion`, `ctl-199b-halt`, `ctl-ownership-inconclusive`) are discharged **only by issues it blocks** (1.2, 1.4, 2.2, 2.3, 1.5). Either unsatisfiable, or `controls.txt` silently omits them and the gate is green while six controls have no RED. **This is H3's defect relocated into the gate the H3/L1 fix created** |
| C3 | **high** | **H4's "recursion is structurally impossible" is FALSE.** The literal `recheck-criteria` appears in **zero** of the 33 clauses — L2's `gate-run.sh` indirection means a name-based guard sees only an opaque control id. Only `YF_RECHECK_DEPTH` actually bounds it. **L2's fix broke H4's fix**; the two were never checked against each other |
| C4 | **high** | **`upstream.py closable` has no `--fixture` flag** — `closable --help` shows `[-h] [--json]` only — and **no issue commissions it**. SC11b and SC12 would die at argparse, which exits **2**, reading as INCONCLUSIVE under this plan's own new grammar rather than the failure it is. A pass-1 fix invented an interface and forgot to build it |
| C5 | med | **`pass-1.md`'s own verdict line was unparseable, so `ready-check` was exit 3.** `**Verdict: REVISE**` matches neither accepted form (colon inside the bold). Exactly REQ-PLAN-071 / #116 — and a plan about review-loop mechanization was blocked by a malformed review file |
| C6 | med | **R9's "9 escaped-pipe clauses" is measured FALSE — it is 4** (SC11b, SC12, SC18b, SC20). The 9 was pass-1's count over the *old* 26-row table, carried through a rewrite to 33 unrecalculated. Identical class to H6's corrected 8-vs-7 |
| C7 | med | **The plan's own DAG is the corpus's worst single-writer violation.** Now that `touches:` exists, D-20's lever runs against plan-052: `assets/gate-run.sh` has **9 writers** (28 of 36 pairs topologically independent); `plan_manager.py` has **7**. EXP-007 measured shared declared paths at 2.86× defect density, p=3.4e-11 — the plan designs in the two highest-risk artifacts it could, and no risk row names it |
| C8 | med | **4.2's predicate is too weak to catch its own plan's gate.** Applied to `red-prework-core` it PASSES, because the evidence dependency is mediated by `controls.txt` and `Discharged-by`, neither of which a name-matching predicate reads. Same root cause as C3 |
| C9 | med | **SC21a derives its count from `assets/deferred-defects.md`, which no issue produces** — 7.2's `touches:` names only the grant proposal. Same "no producer for the artifact the criterion rests on" shape as pass-1's H3/H5. (The count 7 itself is correctly derived) |
| C10 | low | **`verify-all` vs `verify-set core\|ext` partition is undefined** — nothing asserts `core ∪ ext == all`, and per C1 they demonstrably differ |
| C11 | low | **SC5c and SC18 thresholds are unfalsifiable as written.** SC5c budgets 20% slack on a metric currently at 100%, so it cannot detect the degradation it exists to prevent. SC18's "floor" is **never given a number anywhere** |
| C12 | low | **3.3 half-owns its criterion** — the "and the criteria they discharge" half is asserted by nothing |

## Missing

- Producing nodes for **11 controls**, `assets/deferred-defects.md`, and the `closable --fixture` flag.
- A **numeric** floor for `ownership-report`'s INCONCLUSIVE threshold.
- The `core`/`ext`/`all` control-set partition invariant.
- A risk row for the 9-writer / 7-writer artifact concentration (C7).
- A cost/isolation model for a full `recheck-criteria` run — SC19 triggers the FULL tier and SC24 a
  rebuild+deploy, both from *inside* a criteria re-check. Pass-1's H4 addressed only the recursion half.

## Gate Assessment

| Gate | Reachable? | Verdict |
| :-- | :-- | :-- |
| Start Gate | n/a | fine |
| `red-prework-core` | **NO** | **Cyclic in substance (C2)**, and it PASSES 4.2's own predicate (C8) — the second finding |
| `red-prework-ext` | **Yes** — verified | **Sound.** L1's split was a real improvement |
| `upstream-write` | **Yes** — executed | **Sound. H5 genuinely fixed** |
| Reconcile Gate | **Yes** | **Still sound after the rewrite** |

Frontloading: no misses.

## Upstream Assessment

Dispositions survived the rewrite and remain well-evidenced. `verify-reconcile` parses 17
non-excluded rows with per-row remediation — correct pre-execution behaviour. The `tracker` row is
still absent, correctly handled by M8's end-state framing (though `ctl-tracker-endstate` is one of
C1's 11 orphans).

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Fixed at the root, as recommended — `controls.txt` is now GENERATED.** 0.2 ships `assets/gen-controls.py`, which derives the set by scanning `plan.md`'s Verification cells for `ctl-*` and globbing `assets/controls/`, plus **`ctl-controls-closure`** (new **SC0**) asserting asserted == built == file. **Every literal count is deleted** — SC2 now reads *"every control in the generated set"*. Builders added for all orphans (0.3, 0.4a, 1.1, 1.3, 2.1, 3.1, 4.1, 5.0, 6.0, and new **7.0** for the land set). **Re-measured: 27 asserted, 27 built, 0 orphaned, 0 built-but-unasserted.** *(Corrected at pass 3 — the original figure said 28 because my extractor matched the prose glob `ctl-199b-*` as an id. Fourth hand-count error, caused by pattern-matching over prose: the exact defect class this plan exists to eliminate.)* | `main-session` | `resolved` |
| C2 | high | **Fixed.** The six orphaned core controls now have builders outside `Blocks`: `ctl-class-a-fraction` → 1.1; `ctl-touches-coverage` and `ctl-ownership-inconclusive` → 1.3; the five `ctl-199b-*` → 2.1. The gate Condition now reads from the **generated** file's `set` column rather than the prose phrase *"every Epic 0-4 control"*. **Verified: `builders ∩ core Blocks` is EMPTY.** The Instructions now say the closure is asserted *mechanically by `ctl-controls-closure`, not by this sentence* | `main-session` | `resolved` |
| C3 | high | **Claim withdrawn and corrected.** 2.2 now states `YF_RECHECK_DEPTH` is the **LOAD-BEARING** guard bounding recursion **at depth 1**, and that the name-check is **BEST-EFFORT scanning the EXECUTED COMMAND STRING ONLY, never the criterion row** — which also settles the SC6b ambiguity you flagged. *"Structurally impossible"* is gone. SC6b now asserts on **DEPTH**, not on a name match, and says why: every clause routes through `gate-run.sh` and no clause contains the literal | `main-session` | `resolved` |
| C4 | high | **Fixed — the interface is now commissioned.** 3.2's title explicitly adds `--fixture` to `closable`, quoting the measurement (`closable --help` shows `[-h] [--json]` only). New **SC11b** asserts the flag EXISTS, built by `ctl-205-fixture-flag` (3.1). Also recorded: argparse's exit **2** aliases INCONCLUSIVE under the new grammar, which is why an uncommissioned interface read as inconclusive rather than as failure | `main-session` | `resolved` |
| C5 | med | **Fixed.** `pass-1.md` line 10 is now `## Verdict: REVISE` on its own line. Verified: `ready-check` no longer reports *malformed review* and instead gives the correct reason — *last red-team verdict is REVISE* — so the parse is genuinely fixed rather than merely different | `main-session` | `resolved` |
| C6 | med | **Fixed by derivation, not by recounting.** R9 no longer carries a literal; it states the count is DERIVED and records that the previous literal ("9") was measured false (actual 4) after the rewrite. This is the third hand-count defect in this plan (7/24, 31-for-30, 47-for-49) and R8 now names all three as the reason SC0 makes the control set generated | `main-session` | `resolved` |
| C7 | med | **Fixed STRUCTURALLY for the worst case, and surfaced honestly for the rest.** Each control now lives in its **own file** under `assets/controls/`, so `gate-run.sh` goes from **9 writers to 1** and every control-builder is a single writer. `plan_manager.py` cannot be split as cheaply, so 3.3, 4.2, 5.2 and 5.3 were moved to **new dedicated modules** (`upstream_render.py`, `gate_consistency.py`, `verify_beads.py`, `retrospective_fields.py`), leaving **1.5 and 2.2** as the only two remaining writers. New **R10** states the residue is *surfaced, not eliminated* | `main-session` | `resolved` |
| C8 | med | **Fixed — the predicate now resolves indirection.** 4.2 gains a second arm: *no control the Condition requires may have all its dischargers inside — or transitively behind — that `Blocks` set*. 4.1 gains a **third negative fixture reproducing this plan's own `red-prework-core`**, on your reasoning that a predicate which cannot catch its own plan's gate proves nothing. SC13 restated to assert both arms | `main-session` | `resolved` |
| C9 | med | **Fixed.** `assets/deferred-defects.md` is now named in 7.2's title AND its `touches:` list, and 7.2 enumerates all seven inline. `ctl-deferred-count` is built by the new 7.0 | `main-session` | `resolved` |
| C10 | low | **Fixed.** New **SC0b** asserts `core ∪ ext ∪ land == all` and that `verify-all` FAILS if any asserted control id is absent from the generated file. 0.2 ships the `set` column | `main-session` | `resolved` |
| C11 | low | **Both thresholds are now numbers.** SC5c → **100%** with the stated reason that a 20% budget cannot detect the degradation it exists to prevent. SC18 → **80% path coverage**, stated numerically in both the criterion and 1.5's issue text. SC7's floor raised 80% → **90%** to match the measured 94.3% | `main-session` | `resolved` |
| C12 | low | **Fixed.** SC12's `jq` now also requires `has("discharges")`, so the *"and the criteria they discharge"* half of 3.3 is asserted rather than assumed | `main-session` | `resolved` |
