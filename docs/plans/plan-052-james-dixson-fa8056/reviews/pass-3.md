---
type: Review
okf_spec: OKF-PLAN
id: pass-3
description: Red-team pass 3 (third independent) — REVISE, 4 high / 5 medium / 3 low; the closure architecture is vacuously green on empty input
---

# Red-team pass 3

## Verdict: REVISE

4 high, 5 medium, 3 low. **ALL 12 RESOLVED** (see Resolutions). **9 of 12 live inside a pass-2 resolution** — the third consecutive
reproduction of `exp-002`'s measured 75% base rate. Two concerns were confirmed by a **sandbox
spike** that built `gen-controls.py` and `gate-run.sh` to the plan's own words and ran them.

**Reproduction tally: 5 genuinely fixed · 4 partially fixed · 2 fixed-with-a-new-defect · 1 NOT fixed.**

## The unifying root cause

Pass 2 removed hand-maintenance by **deriving** everything — controls, counts, partitions. But
**derivation with no floor is vacuously green on empty input.** The plan applied exactly that lesson
to `ownership-report` (SC18's numeric floor, from EXP-007's recorded false-comfort risk) and
**exempted its own harness**.

Second thread: **the single-writer metric was satisfied by OMITTING the integration writes**, not by
eliminating them.

## Strengths (verified by execution)

- **The DAG survived a third rewrite** — 31 issues, 49 edges, acyclic, 0 unknown nodes, 35 criteria,
  every `Discharged-by` resolves, every issue discharges ≥1 criterion, **31/31 declare `touches:`**.
- **C2's fix is real and could not be broken** — `core builders ∩ core Blocks = ∅`, **and
  transitively-behind = ∅ too**. Same for `ext`.
- **H5 still sound**; `→ exit non-zero` used **0** times in the criteria table; `audit` exit 0;
  `doc_lint` PASS; `gate-run.sh`'s 9→1 writer split is **real** — only `plan_manager.py` has >1.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| P3-C1 | **high** | **The whole closure trio goes GREEN over ZERO controls.** Spiked: from a root with no `plan.md`, `∅ == ∅ == ∅` satisfies `ctl-controls-closure`; `verify-all` over an empty file exits 0; `∅∪∅∪∅ == ∅` satisfies the partition. **All three flagship criteria green while nothing was checked** — verbatim the plan's own motivating defect. And SC2 forbids the obvious anchor (*"no literal count appears anywhere"*): pass 2 deleted every count without adding a floor |
| P3-C2 | **high** | **SC0 is discharged by the one issue at which it is necessarily FALSE.** At Issue 0.2 only `ctl-controls-closure.sh` exists, so closure is red (measured: asserted=27, built=1, exit 1). SC0's `Discharged-by` is `0.2` alone; it can only be green after 7.0. The SC4b rot class, inside the flagship criterion |
| P3-C3 | **high** | **Both gate Conditions still accept "a non-zero exit" as RED.** M1 banned the two-valued form from the criteria table but left it in the gates — and it is not hypothetical: 3.1's three controls need `--fixture`, which does not exist until 3.2, so all three exit **2** at argparse. **Three of seven core builders produce fake REDs** |
| P3-C4 | **high** | **The four new modules have NO declared call site, and adding one restores the writer count.** `cmd_closable` prints its report inline in `upstream.py`, so 3.3 must edit it; `prevention` is already a `plan_manager.py` option, so 5.3 must touch it; no issue adds a click verb for `gate_consistency.py` or `verify_beads.py`. **The 1-multi-writer measurement is an artifact of omitted work** — and 2.3 proves the plan knows wiring is a separate touch |
| P3-C5 | med | **C2's fix made 4.1's "third negative fixture" unsatisfiable.** `red-prework-core` is now clean under both of SC13's arms, so it is a **positive** case; a negative fixture reproducing it cannot exist |
| P3-C6 | med | **SC12's `jq` does not assert what SC12's prose says.** Executed: `discharges: []` → `true`, exit 0. `close_reasons` gets a length check; `discharges` gets only `has()`. C12 was a half-fix |
| P3-C7 | med | **2.2 invented a `heavy` clause tag that nothing commissions** — one occurrence in the whole plan, absent from the grammar, the extractor, and every SC row including the two it exists for |
| P3-C8 | med | **"Bounds recursion at depth 1" makes four controls depth-dependent** and the plan does not say which verdict is asserted standalone versus under the close chain |
| P3-C9 | med | **`uv run <bash script>` is a category error repeated 32 times.** A lost exec bit turns ALL 32 mechanical criteria into exit 2 — which R4/SC8 map to `warn`, never a hard fail. **The entire suite would silently downgrade to warnings** |
| P3-C10 | low | **The `set` column's derivation is unspecified** — a hand-maintained mapping inside a generated file reintroduces what C1 removed |
| P3-C11 | low | **Pass-2's re-measurement is off by one: 27, not 28.** The substance (perfect closure) is confirmed; the count is not. **Fourth hand-count error** — and R8 cites that history as SC0's rationale, so the record should be right |
| P3-C12 | low | **SC1c waives a check that is mechanizable BEFORE the merge.** SPEC-first ordering is decidable on the branch, and 7.1 already runs pre-merge |

## Missing

- **A non-emptiness / INCONCLUSIVE floor for the harness itself** — applied to `ownership-report` and
  nothing else. P3-C1 and P3-C6 are both that omission.
- **Declared call sites for the four new modules.**
- **Tests and recipe ids for the four new modules** — every existing script family pairs with a
  `test_*.py`, and no issue's `touches:` names one.
- A statement of what the `heavy` cost model protects, or its deletion.

## Gate Assessment

| Gate | Reachable? | Verdict |
| :-- | :-- | :-- |
| `red-prework-core` | **Yes — measured** | C2's fix genuinely holds, both arms. But the Condition accepts an **exit-2 as RED** (P3-C3) |
| `red-prework-ext` | **Yes — measured** | Sound |
| `upstream-write` | **Yes — executed** | Sound |
| Reconcile Gate | **Yes** | Still sound after the third rewrite |

## Upstream Assessment

Unchanged and sound. `verify-reconcile` parses 17 rows, exits 1 pre-execution — correct. The
`tracker` row's absence is correctly handled by the end-state framing, and `ctl-tracker-endstate`
now has a builder.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| P3-C1 | high | **Fixed with a FLOOR, which is what was missing.** 0.2 now specifies that `gate-run.sh` exits **2 (INCONCLUSIVE), never 0**, on an empty or unreadable control set, and `ctl-controls-closure` asserts a **DERIVED lower bound** — every issue whose `touches:` names `assets/controls/*.sh` must contribute ≥1 id. A derived floor is not a literal count, so SC2's no-literals rule is intact. New **SC0c** asserts the empty case is INCONCLUSIVE, built by `ctl-empty-set-floor`. This is EXP-007's own recorded lesson, now applied to the harness instead of only to `ownership-report` | `main-session` | `resolved` |
| P3-C2 | high | **Fixed.** SC0 and SC0b now carry the same 11-builder `Discharged-by` list SC2 has (0.2, 0.3, 0.4a, 1.1, 1.3, 2.1, 3.1, 4.1, 5.0, 6.0, 7.0), so neither is discharged at a point where it is necessarily false | `main-session` | `resolved` |
| P3-C3 | high | **Fixed in both gates.** Each Condition now reads *"a recorded RED observation with **EXIT 1** — an exit 2 is INCONCLUSIVE and does NOT satisfy this gate"*. 3.1 additionally requires its REDs be **real negatives against the pinned fixture, never an argparse exit 2** from the not-yet-existing `--fixture` flag. The two-valued form is now banned from the gates as well as the criteria table | `main-session` | `resolved` |
| P3-C4 | high | **Fixed by declaring the call sites, and R10 restated at its TRUE value.** 3.3 now touches `upstream.py` (where `cmd_closable` prints inline) and `test_upstream.py`; 4.2, 5.2 and 5.3 each now touch `plan_manager.py` for their click verb, plus a test file; 5.3 also touches `_shared/document_types/plan-retrospective.toml`. **R10 now states 5 writers, not 2**, and says explicitly that the 2 was *"an artifact of OMITTING the call sites… stated at its real value rather than at the value that flattered the metric"*. Your diagnosis of metric-gaming was correct and is recorded as such | `main-session` | `resolved` |
| P3-C5 | med | **Fixed.** 4.1's third negative now reproduces the **PRE-FIX** `red-prework-core` (pass-2 C2's state: the six core controls' dischargers inside the Blocks set), and a **positive** fixture asserting the CURRENT gate passes was added — regression protection in both directions. The text notes the current gate is clean under both arms, so a negative reproducing it cannot exist | `main-session` | `resolved` |
| P3-C6 | med | **Fixed and VERIFIED BY EXECUTION against your counterexample.** SC12's `jq` is now `(.issues\|length) > 0 and all(.issues[]; (.beads\|length)==0 or (((.close_reasons\|length) > 0) and ((.discharges\|length) > 0)))`. Measured: `discharges: []` → exit 1; `issues: []` → exit 1; a good payload → exit 0. Both vacuous paths you named are closed | `main-session` | `resolved` |
| P3-C7 | med | **The `heavy` tag is DELETED.** It was an interface invented by a fix and never commissioned — your C4 shape, re-injected. The depth rule replaces it (see P3-C8) and the cost limit is an operator-facing statement, not a fabricated grammar form | `main-session` | `resolved` |
| P3-C8 | med | **Fixed by stating the rule as what each depth MAY DO**, not as a bound: **depth 0 and depth 1 evaluate; depth 2 returns exit 2 (INCONCLUSIVE) without executing.** That makes SC6/SC8/SC9/SC10 valid standalone AND under the close chain, where they run at depth 1 — the ambiguity you identified is removed rather than papered over | `main-session` | `resolved` |
| P3-C9 | med | **Fixed at all 32 sites.** Every `uv run …/gate-run.sh` is now `bash …/gate-run.sh`. Verified: **0 remaining**. This removes the silent whole-suite downgrade — a lost exec bit would have turned all 32 mechanical criteria into exit 2, which R4/SC8 map to `warn` | `main-session` | `resolved` |
| P3-C10 | low | **Fixed.** 0.2 now specifies the `set` column is **DERIVED FROM THE BUILDER'S EPIC** (0-4 core, 5-6 ext, 7 land), never hand-assigned, and that every id must carry a non-empty `set` — asserted by `ctl-controls-closure`. A hand-maintained mapping inside a generated file would have reintroduced exactly what C1 removed | `main-session` | `resolved` |
| P3-C11 | low | **Confirmed — you are right and I was wrong.** Re-measured: my extractor matched the prose glob `ctl-199b-*` as though it were an id. The true figure was **27/27/0**. pass-2's C1 row is corrected, with the cause recorded: this is the **fourth** hand-count error in this plan and it was caused by pattern-matching over prose — the exact defect class the plan exists to eliminate. 0.2 now requires `gen-controls.py` to ignore prose globs | `main-session` | `resolved` |
| P3-C12 | low | **Fixed — the waiver is withdrawn.** SC1c is now a class-(a) criterion run **PRE-MERGE at 7.1**, where the branch history still exists, via `ctl-spec-first-order` asserting the `REQ-*` commit precedes the first `skills/**` commit. The post-merge undecidability is retained as the *reason it runs at 7.1*, not as an excuse to waive it. **This leaves exactly ONE `manual:` criterion (SC21b), and class-(a) rises to 97.2%** | `main-session` | `resolved` |
