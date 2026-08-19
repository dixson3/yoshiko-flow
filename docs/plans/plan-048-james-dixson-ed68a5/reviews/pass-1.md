---
type: Review
okf_spec: OKF-PLAN
pass: 1
---
# Red-team pass 1 — plan-048-james-dixson-ed68a5

## Verdict: REVISE

## Strengths

- **D-5 is the real deliverable and it works.** Re-measuring rather than citing caught six inherited
  errors including a ~2× oversized headline. The reviewer independently reproduced 150 unparsed
  constructs across 33 plans with the per-class breakdown matching EXP-001 exactly.
- **The conformance claim holds** — all six findings PASS `finding.toml` with `files_checked: 1`
  (not a zero-selection silent green); `plan.md` PASSes; `okf.py check` returns `findings: []`.
- **D-11 is real and the mechanism was confirmed:** `--path` on a real-but-unselected file and on a
  nonexistent file return byte-identical objects.
- **D-8's provenance is strong** — a postcondition derived from an observed silent failure.
- **SC10c is the best criterion in the plan** — it asserts the gate scripts exit 1 *rather than 127*.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | high | Two capability gates are formal cycles: "relational checks can fail" blocks 3.5 but its evidence *is* 3.5; "intake binding does not wedge" blocks 5.3 but its condition presumes 5.3's binding |
| C2 | medium | "grammar widening is non-vacuous" gates 1.5 (the falsification issue) and duplicates SC1/SC2, while nothing downstream is gated on the widening being *correct* — Epic 3 depends on 1.2, not 1.5 |
| C3 | high | **Nothing asserts a recovered edge is CORRECT.** SC1 has no target (a drop of 1 passes); SC2 is **true by construction** and cannot fail; D-8 is trivially satisfied by a transform whose purpose is to increase edges. `Blocks: Epic 3` → `epic:3` fans out to every issue; a half-materialized blocking list is possible |
| C4 | high | **7 of 24 criteria fail the plan's own anti-vacuity standard** — SC1, SC2, SC5, SC7, SC15, SC20, SC21 |
| C5 | high | Issue 2.4 declares `E` on `skills/**` in violation of D-10. Measured: `depends-on-skill` is missing from `skills/yf-herdr/SKILL.md`. SC7's verification is a declaration audit and structurally cannot see it |
| C6 | high | Two ordering inversions: 2.1a adds §3 trigger rows before 5.1's vacuity fix (manufacturing a fresh D-11 defect), and has no edge to 2.4 so the row selects zero files; SC4 is discharged by 1.2 but no relational check exists until 3.1 |
| C7 | high | Nothing orders 0.6 before the gates whose scripts it authors. `plan_manager.py` has **no auto-gate runner**, so a missing script yields bash 127 read by an agent as a red gate |
| C8 | medium | **Nobody posts the upstream comments.** 6.4 drafts only; 6.5 files the tracker. SC21 is undischargeable |
| C9 | medium | Scope claim is dishonest: 46 issues to do work plan-047 sized at **32** (~44% expansion), and it **ties plan-045's all-time record**. No split gate or mechanical trip condition is declared |
| C10 | high | **Epic 4's honest yield is one directory rename `okf.py migrate` already performs.** 4.1–4.4 build a bespoke engine to rename 31 files; the fingerprint and DAG predicates are **inert** on that payload |
| C11 | medium | D-7's justification is false — every disposition is already a recognised literal, so R2c would not fire on this plan. SC9 cannot fail |
| C12 | low | The plan's own literals are stale (`log.md` says 43 issues/22 criteria; corpus is now 48 dirs, not 47) — #135's exact class, inside the plan that excludes #135 |

## Missing

- A split gate / mechanical trip condition — the single most effective control in plan-047's execution
- Any criterion asserting semantic correctness of a recovered DAG edge
- A named owner for `depends-on-skill` on `skills/yf-herdr/SKILL.md`
- A post step for the four `partial` upstream comments
- A stated position on `pour_fidelity.py` under the widened grammar — a measurable regression surface with no criterion

## Gate Assessment

| Gate | Blocks | Reachable? | Verdict |
| :-- | :-- | :-- | :-- |
| Start Gate | — | n/a | fine |
| grammar widening non-vacuous | 1.5 | yes | placement miss; duplicates SC1/SC2 |
| relational checks can fail | 3.5 | **no — cycle** | evidence produced by its only Blocks member |
| normalizer aggregate diff | 4.7 | yes | **sound — the one well-formed gate** |
| intake binding does not wedge | 5.3 | **no — cycle** as worded | condition presumes the deliverable |
| Upstream write | 6.5 | yes | sound shape; nothing posts what it authorizes |
| Reconcile Gate | reconcile step | yes | fine |

**The 0/1/2 discipline does not hold** — no edge orders 0.6 first, and there is no auto-gate runner.

## Upstream Assessment

Broadly sound. D-6's #173 boundary is the best-argued decision in the plan; D-2's supersede of #175
is correctly reasoned. Three defects: the four `partial` dispositions have no posting step; #165/#62/
#135 are `exclude` with notes saying "deferred" while D-7 argues that conflation is a defect worth a
SPEC amendment; and #135 is excluded while the plan ships three stale literals of #135's own class.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | Re-worded both gate conditions to be satisfiable from a predecessor's output; gate-relations now blocks 3.2/3.3 and generates its own mutants; gate-nowedge reworded to a pre-binding `doc_lint.py` drive | `main-session` | resolved |
| C2 | medium | Gate moved to block 3.1, the first consumer of the widened DAG; SC2 deleted per C4 | `main-session` | resolved |
| C3 | high | Added SC1b (hand-audited sample of >=20 recovered constructs across >=10 plans, adjudicated and recorded) and Issue 1.4a (a negative mutant a naive widening would recover WRONGLY, asserting refusal); 1.2's gate extended to all `plan_extract` consumers | `main-session` | resolved |
| C4 | high | SC2 deleted; SC1, SC5, SC7, SC15, SC20, SC21 restated with falsifying drives | `main-session` | resolved |
| C5 | high | Issue 2.4 now names `depends-on-skill` and the `yf-herdr` outlier explicitly, declaring that key at `W`; SC7 rewritten to run the linter over the corpus and assert `errors == 0` with `files_checked > 0` | `main-session` | resolved |
| C6 | high | `2.1a depends-on 5.1, 2.4`; SC4 re-assigned to 3.2 | `main-session` | resolved |
| C7 | high | `depends-on: 0.6` added to 1.3, 3.2 and 5.1 so the scripts exist well before any gate; added SC10d asserting a deliberately deleted script yields an operator-visible INCONCLUSIVE, not a red gate | `main-session` | resolved |
| C8 | medium | Added Issue 6.5a (post the drafted comments, behind the existing Upstream-write gate); SC21 re-assigned to it | `main-session` | resolved |
| C9 | medium | R7 restated with the honest 46-vs-32 comparison; **D-12 declares a mechanical split gate** (`reviews/pass-*.md >= 4`, evaluated at end of Epic 3) | `main-session` | resolved |
| C10 | high | **Epic 4 collapsed from 7 issues to 2** — postconditions attach to `okf.py migrate` rather than a bespoke engine; SC11/SC13 deleted as unmotivated | `main-session` | resolved |
| C11 | medium | #165/#62/#135 re-dispositioned to `deferred`, making D-7 load-bearing and SC9 falsifiable | `main-session` | resolved |
| C12 | low | Corpus counts restated as run-time-derived in verification columns; `log.md` refreshed | `main-session` | resolved |
