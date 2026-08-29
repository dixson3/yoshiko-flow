---
type: Review
okf_spec: OKF-PLAN
id: pass-8
description: "Red-team pass 8 — REVISE, narrow. Eighth shape: SC11c claims two files and verifies one, in the artifact pass 7 created to close that family. Plus five derived counts invalidated by adding one issue."
---

# Red-team pass 8: plan-056-james-dixson-473dba

## Verdict: REVISE

> **All 6 concerns resolved.** Counts were re-derived by script rather than transcribed, which surfaced
> an error in this pass's own figures (7 of 22, not 6 of 21). Sibling congruence now verified
> mechanically: 15 plan rows = 15 triage sections = 15 reference files, zero disposition mismatches.

Narrow and mechanical. **Pass 7's prediction is 80% correct**: the criteria/gate/harness *design*
verified sound, C54's arithmetic is exact, and no seventh-shape reformulation appeared. But pass 7's own
N2 fix introduced an eighth shape and invalidated four derived counts pass 7 had verified as "Exact"
earlier in the same pass. One C53 sub-fix did not land at all.

## Strengths

**C54's arithmetic is exact and tight, re-derived by script.** The set of `scripts/checks/*` instruments
invoked by any criterion is **exactly 10**, and SC0's conjunction names exactly those ten — no more, no
fewer. 8 (Issue 1.9) + 1 (1.8) + 1 (3.1) = 10; self-exclusion → **9**, so `--require 9` is the maximum
attainable and cannot be satisfied by a partial sweep. `--require` appears in five places, all 9. Gate
reachability re-confirmed: all three producers outside `Blocks: [3.2, 3.3, 3.4]`; extracted
`instructions` 1767 chars with both directives verbatim; `unparsed: []`; `gate_consistency` PASS.

**C52 holds** — the destructive-backfill block is gone and every issue ref in `context.md` resolves.
**C53 is 3-of-4** — #170 fixed, #265 appended, 15 rows / 15 sections / 15 reference files with every
disposition matching pairwise.

## Concerns

### C55 — `context.md:87` cites D-5, the exact misreference `plan.md` was amended to remove. [MEDIUM]

*"Per D-5, re-measure before citing rather than inheriting."* D-5 is *"Nested `log.md` stays permanently
dropped"*, and is marked CARRIED TO THE SUCCESSOR PLAN. The re-measurement doctrine is D-1/D-10.
`plan.md` Issue 0.8 already carries *"an earlier draft cited D-5, which is … not the relevant decision"* —
so the identical error was fixed in `plan.md` and left standing in `context.md`. C52 fixed issue-id refs
in that file but not decision-id refs.

### C56 — C53's #189 sub-fix is marked `resolved` and did not land. [MEDIUM]

`upstream-triage.md:93` still reads *"the new **yf-okf-hygiene** script ships WITH tests"* — pre-split
text, since that skill is D-2/D-9, both carried to the successor. `plan.md`'s #189 row says the opposite.
**This is the same defect C53 was raised to fix, in the same file, surviving the fix — and a false
`resolved` in the review record.**

### C57 — EIGHTH SHAPE: SC11c claims two files and verifies one. [MEDIUM]

SC11c reads *"The **two** test files this plan creates are wired into the validation recipe"* and runs
`check-recipe-row.sh test_recheck_criteria`. **`test_index_members.py` (Issue 2.4, discharging SC28) is
named in the criterion and in Issue 3.2a, and verified by nothing.** SC11c is green with that row absent
— which is exactly the state SC11c exists to detect.

A new instance of the plan's own governing failure family — a criterion whose verification is narrower
than its claim — **introduced in the artifact pass 7 created to close that family.**

### C58 — N2's structural addition invalidated five derived counts. [MEDIUM]

Adding Issue 3.2a changed the denominators:

| Location | States | Actual |
| :-- | --: | --: |
| SC1 — direct Epic-0 dependency | 13 of **23** | 13 of **24** |
| SC1 — transitive | 22 of **23** | **23 of 24** |
| D-17 | **34** issues | **35** |
| R12 | **34** issues | **35** |
| SC35 | 6 of **21** criteria | 6 of **22** |

The *rule* still holds — the sole non-transitive issue is still 2.4, the declared carve-out. Only the
numbers are stale. But SC1's cell states the figures are recorded *"so `check-req-coverage.py` implements
a criterion rather than defining one"* — they are the implementer's spec, and an executor encoding 23
produces a permanently-red SC1. Note the shape: pass 7 verified `13 of 23 / 22 of 23` as **"Exact"**, and
pass 7's own fix then falsified it — the C49/C54 family recurring one layer out.

### C59 — `index.md` says "Six red-team passes"; there are seven. [LOW]

Ironically the same line says the count is drift-prone and outside `reindex --check`'s reach. The six
*shapes* it enumerates remain accurate; only the numeral is stale, and it will be stale again after this
pass. **A count that must be edited every cycle is a drift generator** — drop the numeral.

### C60 — The gate's `Blocks:` claim is now literally false. [LOW]

*"…while still gating every act that turns enforcement on."* Issue 3.2a wires two recipe rows — an act
that turns enforcement on — and is not in `Blocks`. Practically harmless (3.2a `depends-on 1.10, 2.4`, so
its producers precede it), but the universality is wrong.

## Missing

- **Still nothing verifies `context.md` / `upstream-triage.md` against `plan.md`.** Issue 4.2 files this,
  but C55 and C56 show it recurring *within the pass that filed it*.
- **`harness-selftest.sh` has no RED control anywhere.** It is the gate's `Test` and SC35's subject, and
  it self-excludes — so a selftest that unconditionally prints `9` and exits 0 satisfies both. Issue 1.9
  states the reason, so this is acknowledged rather than overlooked, but it is **the residual floor of
  the entire defence** and belongs in R13 as such.

## Gate Assessment

| Gate | Reachable? | Frontloaded? | Verdict |
| :-- | :-- | :-- | :-- |
| Start Gate | n/a | n/a | fine |
| Verification harness ready | **Yes** — `--require 9` tight against 9 attainable | earliest legal position | **Sound**; C60 is prose overclaim, not a placement defect |
| Reconcile Gate | auto | — | fine |

## Upstream Assessment

**Congruent.** 15 rows ↔ 15 triage sections ↔ 15 reference files, dispositions matching pairwise.
`verify-reconcile` fails 7 of 11 for the correct pre-execution reason, and those 7 are **exactly** Issue
4.3's action list. The only defect is C56's prose.

## Loop termination

All six items are single-line corrections — two decision/prose refs, one unlanded sentence, one criterion
command, five numerals, one clause. **None touches the DAG, the gate, a severity, an epic boundary, or a
criterion's rule.** Pass 7 was right about *shape* and wrong about *derived counts* — the one hazard a
deletion-and-correction set still carries. Pass 9's highest-value check is re-running the count
extraction after the fixes.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C55 context.md cites carried-away D-5 | medium | Fixed — `context.md` now cites **D-1 and D-10**. Pass 8 is right that this was the identical misreference corrected in `plan.md` and left standing one file over: C52 fixed issue-id refs in that file but not decision-id refs, so the sweep was narrower than the defect. | `main-session` | `resolved` |
| C56 #189 re-aim marked resolved, did not land | medium | Fixed, and the miss is instructive. My pass-7 edit used the wrong search string — the file says *"Not this plan's cluster. Noted as a constraint instead: the new yf-okf-hygiene script…"* and I searched for a variant — so `replace()` no-opped and I recorded it `resolved` anyway. **Fifth false resolution row.** This pass every edit asserts on match, and the assertion is what caught it: the script halted on `MISS C56` rather than reporting success. | `main-session` | `resolved` |
| C57 SC11c claims two files, verifies one | medium | Fixed — SC11c now runs `check-recipe-row.sh` for **both** row ids, and its `Discharged-by` gains `1.9` (it was the only criterion invoking a `scripts/checks/` instrument without crediting its producer). Pass 8 is right that this was the plan's governing failure family reproduced inside the artifact created to close it: a criterion whose verification is narrower than its claim, green in exactly the state it exists to detect. | `main-session` | `resolved` |
| C58 five derived counts invalidated by 3.2a | medium | All five corrected, and **re-derived by script rather than transcribed** — which caught an error in pass 8's own figures: the `check-pytest-ran.sh` routing is **7 of 22**, not the 6 of 21 pass 8 reported. Final measured values: 35 issues, 22 criteria, 36 edges, 24 non-Epic-0 issues, **13 direct / 23 transitive**, sole non-transitive `2.4`. The lesson is the one pass 8 states: after a structural edit, re-run the extractor and re-derive every count rather than editing the one that prompted the change. | `main-session` | `resolved` |
| C59 index.md pass count stale and drift-prone | low | Fixed by **removing the count rather than updating it** — the line now reads "The red-team passes, newest last" and states why it carries no number: a count that must be edited every cycle is a drift generator, and `reindex --check` cannot catch it because it checks membership, not description content. The six shapes it enumerates remain accurate and do not go stale. | `main-session` | `resolved` |
| C60 gate Blocks universality claim false | low | Fixed — the gate's claim narrowed to "every act that turns **the OKF drift gate** on", with an explicit note that Issue 3.2a sits outside `Blocks:` deliberately because its producers precede it via `depends-on`, so R1's ordering hazard does not reach it. Adding 3.2a to `Blocks:` was the alternative; narrowing the claim is truthful and avoids widening a gate whose reachability was itself a defect two passes ago. | `main-session` | `resolved` |
