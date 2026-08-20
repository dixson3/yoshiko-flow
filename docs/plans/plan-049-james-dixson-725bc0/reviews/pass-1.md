---
type: Review
okf_spec: OKF-PLAN
pass: 1
---
# Red-team pass 1 — plan-049-james-dixson-725bc0

## Verdict: REVISE

## Strengths

- **The investigation holds up under independent re-measurement.** Reproduced from scratch: EXP-001's
  89 declarations across exactly 5 plans (010=33, 012=21, 009=15, 007=12, 006=8); plan-006 and
  plan-007 at `issues 9 edges 0 unparsed 0` and `issues 13 edges 0 unparsed 0` — "invisible AND
  uncounted" is literally true; `find skills -name doc_lint.py` empty; `doc_lint.py:565` applying the
  promotion map unconditionally; D-5's closure.
- **Two findings refuted the plan's own scope decisions and the plan changed** — real re-scopes, not
  defensive prose.
- **Structural DAG integrity is clean** — zero cycles, zero dangling, zero forward references across
  all 34 issues; `okf.py check` OK; `audit` all-pass.
- **Principle 1 is correctly applied where applied** — gating Epic 1 on "the guard FAILED on mutants
  A and B" with mutant D as the false-positive control is the part most plans omit.
- **D-7 earned its keep again** — seven corrections that would each have propagated.

## Concerns

| # | Sev | Concern |
| :-- | :-- | :-- |
| C1 | **high** | **`#140` = `include` is not supportable.** It delivers none of nested `index.md`/`log.md`, `reindex`/`--fix`, or the drift model. **This plan's own `references/upstream-171.md` calls #171 "the deferred half of #140" and the earlier `include` "dishonest"** — and #171 is `deferred` two rows down. Also: the table **truncates #140's title**, dropping exactly the undelivered half |
| C2 | **high** | **`#149` = `include` over-claims.** M9 (remediation edges in prose — the issue's rank-1 defect, 0 of 53 `discovered-from` edges connecting plan epics) is untouched: one grep hit, the table row itself. **Title truncated the same way.** Two of eight rows, both the contested ones |
| C3 | **high** | **The two most important gates cannot fail.** No `scripts/` dir exists and **no issue authors `gate-run.sh`, `gate-dagguard.sh` or `gate-cellcheck.sh`.** Under plan-048's own wrapper contract a missing script yields **exit 2 = INCONCLUSIVE = permanently green** — a vacuous control guarding the corpus write and the grammar widening |
| C4 | **high** | **The corpus-write gate still self-references, and the disclaimer saying it doesn't is false.** It credits Issue 3.2 with a dry-run diff; 3.2 produces a *linter check kind* and touches neither target document. The only producer is 3.3 — the Blocks set. Sixth consecutive pass with a gate self-reference, this one wearing a denial |
| C5 | **high** | **"The declared target" is declared nowhere.** Issue 2.4, SC5 and SC23 all consume it; no numeric target appears anywhere. **SC5 and SC23 cannot fail** — violating the plan's own Principle 3, the exact defect it diagnoses in plan-048 one paragraph earlier. No criterion covers post-work `unparsed[]` either |
| C6 | **high** | **SC11 is satisfied by a no-op, and the corrected D-4 has a gate-shaped blind spot.** L1/L2/L3 never observe gates; EXP-002's mutant C (the plan-008 relocation) passes with **zero delta**. EXP-006 Rec 5's content postcondition is built by no issue. SC11 advertises a guarantee the guard does not provide |
| C7 | med | **No `reviews/pass-N.md`** — the conformance pass and its 7 gaps are unrecorded; `ready-check` reports NOT READY for exactly this. A portability failure against `index.md`'s own promise |
| C8 | med | **`upstream-triage.md` is a blank template** — all 8 dispositions and notes empty. The only recent bundle with any blank. It is the second independent record that would have caught C1 and C2 |
| C9 | med | **D-9's and R5's present-tense "R1b fires 4 errors" is measurably false today** — SC26–29 name those four issues and R1b fires zero. Issue 0.2 is still right, but its justification is the corpus, not this plan |
| C10 | med | **SC29 cannot fail** — a disjunction whose second branch is "write a sentence saying there was nothing". The fake criterion R1b's carve-out warns about, produced by R1b |
| C11 | med | **Epic 0's `bookkeeping` declaration is false and exempts the SPEC-first work.** Contradicted by SC13/SC14 in the same document, and it removes 0.4/0.5 — the two `REQ-DATA-*` issues — from the coverage gate. **EXP-006 named this exact lever as an exploit; the plan cites EXP-006 elsewhere and uses it here** |
| C12 | med | The DAG-guard gate imports mutant D from Issue 1.4, which is **not an ancestor of 2.1** — an undeclared cross-branch precondition |
| C13 | low | `log.md` carries a stale count (25 criteria; measured 29) — in the plan that includes #135, and in scope under D-3's own rule |
| C14 | low | SC7, SC12, SC21, SC27 verify **existence, not content** — an empty file with the right name passes SC7 |
| C15 | low | `index.md` and `log.md` return `files_checked: 0` — the same silent-green vacuity the Motivation cites as a defect |
| C16 | low | SC13's "m2 fixture" names no path and is not committed |

## Missing

Gate-script issues; the dry-run diff producer; a declared numeric target and a post-work `unparsed[]`
criterion; a gate layer in the guard; `reviews/pass-N.md`; M9 of #149; **EXP-006 Rec 6 (retire
`disposition-alphabet-offered`, measured 30/30 — a constant) neither scheduled nor declined — the one
item silently deferred**; and no criterion asserting the guard reports the *recomputed* fingerprint
rather than the stored field.

## Gate Assessment

No cycles among issues. **One true gate self-reference** (corpus write), **one undeclared
cross-branch precondition** (DAG guard ← 1.4), and **two auto gates whose tests are
unwritable-as-specified**, degrading to permanently-green INCONCLUSIVE. *"The gate design is the
strongest part of the plan; the gate harness is absent."*

## Upstream Assessment

Eight rows, two wrong in the same direction. **#135 is the best-handled row** — evidence-driven
scoping, declared blind spot, falsifiable criteria. #113 and #174 are sound and specific. **Both
mis-dispositioned rows carry truncated titles that omit exactly the undelivered half** — the
mechanism by which a reader checking the table would not notice. Combined with a blank
`upstream-triage.md`, the upstream half has **no independently-recorded reasoning**.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | `#140` → **`partial`** with an explicit in/out naming nested-index generation and the drift model as OUT and pointing at #171; **full title restored** | `main-session` | resolved |
| C2 | high | `#149` → **`partial`**, M5 IN / M9 OUT stated; **full title restored**; Issue 4.6 records M9 as explicitly out of scope with its measurement | `main-session` | resolved |
| C3 | high | Added Issues **0.7** (`gate-run.sh` wrapper, 127→2) and **0.8** (the two gate scripts, each recorded RED pre-work), both declared ancestors of 1.1/3.1; **SC30** asserts each is observed RED before its capability lands | `main-session` | resolved |
| C4 | high | Added Issue **3.2a** producing the dry-run diff to `assets/`; 3.3 depends on it; the gate Condition now names 3.2a, making the disclaimer true | `main-session` | resolved |
| C5 | high | Target **declared and derived** in Issue 2.4 and D-2: ≥60 of 89 declarations recovered, `unparsed[]` **81 → ≤81** (the widening adds no residue), plans-with-edges 5 → 5. SC5/SC23 rewritten against literals; **SC31** added on post-work `unparsed[]` | `main-session` | resolved |
| C6 | high | Added **L4 (gate content)** to the guard per EXP-006 Rec 5 — gate name → `{type, condition, test, blocks}` under containment — and SC11's clause rewritten to name L4 explicitly | `main-session` | resolved |
| C7 | med | This file; `reviews/` added to `index.md` | `main-session` | resolved |
| C8 | med | All 8 dispositions and notes filled in `upstream-triage.md` | `main-session` | resolved |
| C9 | med | D-9 and R5 restated in past tense with the current measurement; Issue 0.2 re-justified on the corpus | `main-session` | resolved |
| C10 | med | SC29 made mechanical — the handoff enumeration must be **generated** from unmet `Discharged-by` and `deferred`/`partial` rows, not typed | `main-session` | resolved |
| C11 | med | The false sentence corrected; **0.4/0.5/0.6 given criteria** (SC32/SC33/SC34) so the SPEC-first work is inside the coverage gate; only 0.1 remains bookkeeping | `main-session` | resolved |
| C12 | med | `1.4` added to Issue 2.1's `depends-on` | `main-session` | resolved |
| C13 | low | `log.md` count corrected and derived | `main-session` | resolved |
| C14 | low | SC7/SC12/SC21/SC27 given checkable content predicates | `main-session` | resolved |
| C15 | low | Recorded in the plan as a known instance of the class SC17 addresses | `main-session` | resolved |
| C16 | low | SC13 now names the committed fixture path Issue 0.2 creates | `main-session` | resolved |
| Missing-7 | med | **EXP-006 Rec 6 scheduled** as Issue 4.7 (retire or re-scope `disposition-alphabet-offered`) rather than silently deferred | `main-session` | resolved |
