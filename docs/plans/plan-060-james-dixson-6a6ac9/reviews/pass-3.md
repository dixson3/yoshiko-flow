---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 3 — VERDICT REVISE, narrowly, with ZERO high concerns. Seven concerns, all text-level: one pass-2 resolution did not land, and two sentences contradicted the plan''s own irreversibility boundary. All seven resolved.'
---
# Review pass 3 — adversarial (red-team)

## Verdict: REVISE

Narrowly, with **zero high concerns**. **All 7 concerns resolved** by the main session; re-dispatched
as pass 4.

**Date:** 2026-08-29
**Dispatched as:** sub-agent (REQ-AGENT-049), read-only with respect to the repository under review.
**Subject:** plan.md after the pass-2 revision (7 epics, 48 issues, 84 edges, 40 criteria).

The reviewer's own framing: *"Narrowly, and with less than passes 1 and 2 found. Zero high concerns.
Three medium-high, all text-level, none structural. … One resolution (C3) did **not** land — the
thing I was asked to verify one-to-one is not one-to-one — and two long-standing sentences contradict
the plan's own irreversibility boundary. If C1–C3 are corrected I would approve."*

## Strengths

- **SC2b's new form is satisfiable in both directions — verified independently, not trusted.** In a
  `$(mktemp -d)` sandbox under `bash -c`: all-good -> **exit 0**, one-file-broken -> **exit 1**;
  against the live tree (files absent) -> exit 1. The `\|` escaping is correctly handled by
  `_recheck_unescape` (`plan_manager.py:3209`).
- **All 40 criteria parse as clauses under the real `_RECHECK_CLAUSE` grammar** — zero prose, zero
  `manual:`, **31 distinct** guard-routed test names with **no duplicates**. Nothing was silently
  reduced to an unparsed row.
- **The vacuity sweep is clean on the third pass.** Every criterion whose command exists today was
  executed under `bash -c`: SC1->2, SC2->0, SC2b->1, SC4->0, SC13->1, SC32->2, SC33->0, SC34->1,
  SC37->2 — each *not-yet-true*, none *unsatisfiable*. **SC34's negative half is live.** *"The
  round-3 defect the brief predicted is not there."*
- **Bidirectional integrity is perfect.** Zero dangling `depends-on` or `Discharged-by`; every issue
  discharges >=1 criterion; all 18 upstream rows exist and are OPEN on GitHub; `references/` matches
  the table exactly; the 14 inline `resolves-upstream:` annotations match the table **exactly in both
  directions, disposition included**.
- **Every cited figure re-measured true** — 7461 lines, 20 `_run_git` call sites with no
  merge/push/pull/checkout among them, `:2676`, `SKILL.md:1662`, 12 close-chain steps, FAST 59 /
  FULL 57. *"`:2679` and `:1707` are gone from the entire bundle."*
- **The renumber is contiguous and complete inside `plan.md`**; every count reads "twenty / L0-L19".
- **Mechanically green:** `gate_consistency` PASS (5 gates, zero findings), `doc_lint` PASS,
  and `ready-check`'s only blocker is the standing REVISE — *"which proves the `## Verdict:` heading
  fix landed and is parsed."*

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | medium-high | **Pass-2 C3's resolution did not land. The `steps` key set is still the coarse nine-key set it refuted, and the one-to-one L0-L19 set exists nowhere in the bundle.** The prose added below the example *declares* the rule, but the example directly above it is a live counter-example, and an implementer of Issue 2.3 copies the example. Also: L0 and **L16 (push #2)** are currently skippable, and skipping L16 reproduces D-2's exact residue — the defect this plan exists to remove. | Replace the example with the actual twenty keys so `--validate-decision` has a set to enforce, and state the non-skippable set with a reason per member. |
| C2 | medium-high | **`plan.md` states the reversibility boundary one step too late, in the sentence that governs journal design.** *"Steps L0-L6 are reversible or idempotent; L7 is the first outward-facing write"* — but five other statements say L6's push is the first irreversible step. Issues 0.2 and 3.1 build the journal state set *around this sentence*, so the error propagates into the state set. | State L0-L5 reversible, L6 first irreversible, L7 first outward-facing; make the state set straddle **L6**. |
| C3 | medium | **The Conflicts section's central safety claim is false for one of the sites it names.** *"all three precede L7 … nothing posted and nothing closed"* — but an **L16** push rejection is post-L7 (comments posted), post-L12 (beads closed) and post-L15 (`status: complete` written). This is the paragraph used as *"a fourth independent reason #301's ordering is wrong."* Issue 4.10 also carries a single undifferentiated `push rejection` matrix case. | Split the claim: L1/L2/L6-rejection are locally recoverable; an **L16 rejection is post-outward-write** and its contract is retry-after-rebase, never revert. Give it its own journal state and its own matrix row. |
| C4 | low-medium | **`findings/exp-004` carries the pre-renumber labels and `plan.md` points at it as the derivation.** Its table is L0-L18 with L5 = push #1, off by one from L5 onward; Issue 0.2 requires *"one justifying edge per step"* and those edges live only in that table, under the wrong labels. Unlike EXP-005 and EXP-006 it carries no correction block. | Add a CORRECTION block with the old->new map, per the bundle's convention, rather than silently editing measured text. |
| C5 | low-medium | **`decision-schema.md` §1 omits the two fields R6's whole staleness mechanism depends on** — no `predicted_tree`, no resolved target tip. Issue 1.1 binds the implementation to *"the `facts` object of §1"*, i.e. to a schema missing them, while Issue 1.5 says the digest MUST cover both and SC8 tests it. | Add both to §1's `facts.git`. |
| C6 | low-medium | **SC36 and SC36b bind to an artifact no issue commissions.** Issue 6.1 says only "Tier-2 mechanical drive"; nothing requires a machine-readable record. Without a commissioned artifact the tests assert something they invent. | One clause in 6.1: the rehearsal emits a record naming origin URL, terminal journal state and executed step list. |
| C7 | low | **The criteria-validation record is not exhaustive and miscounts.** It omits **SC32**, whose command runs today (measured exit 2, *"'land' is not a registered plan_manager.py verb"*), and says *"33 criteria routed through `check-pytest-ran.sh`"* when the count is **31**. It is the evidence for the standing rule Issue 0.9 adopts, so its bookkeeping should balance. | Add an SC32 row and correct 33 -> 31. |

## Missing

Nothing new of substance. Pass 2's Missing items were addressed — SC36b binds the rehearsal outcome,
Issue 0.2 seeds the journal state set from `okf_hygiene.py backfill`'s five states, Issue 4.10 names
its file, Issue 4.4 requires #301 be closed *"as amended"*. The residual gaps were **C1** (the
`steps` set is the journal-state-set problem repeated, without 0.2's safeguard) and **C6**.

Still true and accepted, not re-raised: no issue body names a single test function, so the 31 test
names in the criteria table are the only contract binding implementation to criteria.

## Gate Assessment

**Clean — no change from pass 2, re-verified mechanically.** `gate_consistency.py` returns `PASS`
over 5 gates with zero findings. The first capability gate's Condition figure ("20 existing call
sites of the `_run_git` helper") re-measured **true**, and no merge/push/pull/checkout appears among
them, so D-1's premise holds. Its evidence sits entirely outside its `Blocks: 4.1` set — reachable,
at the earliest legal anchor. Both `Blocks: reconcile step` gates are correctly deferred to the last
anchor their evidence permits; the redeploy gate's dependence on Epic 6's rehearsal is a real
evidence dependency, not a frontloading miss. **No frontloading misses. No cycles.**

## Upstream Assessment

**Mechanically clean, in both directions, verified against live GitHub.** Eighteen rows; all exist
and are OPEN; `references/` is exactly the same set; `upstream-triage.md` carries all eighteen with
matching dispositions; fourteen inline annotations match the table exactly, disposition included;
zero dangling ids. **#305's `exclude` with provenance recorded is the right disposition.** The
partials remain honest and specific about in/out. **#301 -> `include` -> CLOSED "as amended" is now
stated in Issue 4.4** — pass 1's and pass 2's outstanding item, closed. *"Given D-11 refutes #301's
central structural claim, 'as amended' is the only honest close, and #304 correctly carries the
residue."*

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 — pass-2 C3's resolution did not land | medium-high | **Accepted, and the criticism is exactly right: I declared the rule in prose and left the counter-example above it.** `decision-schema.md`'s `steps` object is replaced with the **twenty** L-keyed entries (`l0_lock_acquire` … `l19_redeploy`). The non-skippable set is stated as **L0-L6 plus L16**, with a per-member reason table rather than a blanket rule — including the one pass 3 found: **skipping L16 reproduces D-2's residue exactly**, the defect this plan exists to remove. | `main-session` | `resolved` |
| C2 — reversibility boundary off by one | medium-high | **Accepted; verified before fixing** (six statements, five saying L6 and one saying L0-L6 reversible — an artifact of the L0-L19 renumber). Now: *"Steps L0-L5 are reversible or idempotent; L6's push is the first IRREVERSIBLE step and L7 the first OUTWARD-FACING write. The journal's state set straddles L6, not L7 — the two boundaries are one step apart and only the earlier one bounds recoverability."* | `main-session` | `resolved` |
| C3 — the conflict claim is false for an L16 rejection | medium | **Accepted; this was a real logic error in the plan's own argument.** The Conflicts section now enumerates **four** sites in a table with each one's position relative to L6/L7 and its recovery, states plainly that an earlier draft's claim was false, and gives the L16 rejection its own contract: **retry-after-`pull --rebase`, never revert**, because reverting would contradict outward statements already made. Issue 4.10's matrix splits the L6 and L16 rejections into separate rows. **The "fourth reason #301's ordering is wrong" argument survives** and the plan says why: it turns on the *merge*, which this plan puts at L2 and #301 puts after its irreversible steps. | `main-session` | `resolved` |
| C4 — exp-004 carries pre-renumber labels | low-medium | **Accepted.** A CORRECTION block is added at the head of the recommended-order section, per the bundle's established convention (EXP-005, EXP-006), carrying the full old->new map from L5 onward and noting that the *justifying edges* Issue 0.2 must lift into `spec/landing.md` are to be read through it. The measured table is left unedited. | `main-session` | `resolved` |
| C5 — schema omits the fields R6 depends on | low-medium | **Accepted.** `facts.git` gains `resolved_target_tip`, and `merge_preview` gains `predicted_tree`, with an inline note that these are the two digest-covered fields making the staleness edge detectable — measured in EXP-006 F4, the predicted tree oid changes when the target moves. | `main-session` | `resolved` |
| C6 — SC36/SC36b bind to an uncommissioned artifact | low-medium | **Accepted.** Issue 6.1 now requires the rehearsal to emit a machine-readable record naming its origin URL, terminal journal state and executed step list — *"without a commissioned artifact those tests would assert something they invented."* | `main-session` | `resolved` |
| C7 — validation record incomplete and miscounted | low | **Accepted.** SC32 and SC37 rows added (both *not-yet-true*, exit 2, with the reason each returns 2 distinguished from an argument error); 33 -> **31**, verified by counting guard-routed SC rows and distinct test names, both **31**. The correction and its cause are recorded in the file rather than silently applied. | `main-session` | `resolved` |
