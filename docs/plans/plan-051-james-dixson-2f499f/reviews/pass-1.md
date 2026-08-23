---
type: Review
okf_spec: OKF-PLAN
id: pass-1
status: complete
---

# Red-team pass 1

## Verdict: REVISE

**First pass, dispatched to an independent agent rather than performed in-session** — deliberately,
since the change this plan ships is *"the drafter must not review its own draft."* 20 concerns: 3
high, 8 medium, 9 low. All resolved below; none deferred.

The three highs are all the same shape — **a criterion or control that is satisfiable while its
substance is absent, or unsatisfiable no matter what** — which is the exact defect class this plan
exists to close, found inside the plan itself.

## Strengths

- **All four load-bearing premises reproduced independently.** EXP-002's FAST-tier claim
  (`status: pass`, `first_failure: null`, 3/3 green on the dangling state); EXP-004's half-fix arm
  (1 / 1 / 0 given an ellipsis-tolerant fixture — so **D-6's narrowing of plan-050's D-8 is
  correct**); EXP-003's census (251 occurrences, exactly 1 containing "executed"); EXP-001's RED
  (`grep -c 'Agent'` = 0 across all 7 `agents/*.md`; section-scoped exit 1; whole-file exit **0**).
- **Line and symbol citations resolve** — ~20 checked, including `change_validation.py:946`'s
  `nargs="*"` with no `action="append"`, verified at source.
- **The conformance fix is sound.** Each `assert-distinguishes` producer is a `depends-on` ancestor
  of the `.4` issue it feeds, and **no producer sits inside the gate's own `Blocks` set** — verified
  per control. No cycle; the gate sits at its earliest legal position.
- **SC9 is a real falsification criterion** — it prescribes deleting the test and rewording the line
  and asserting failure. Named as the only criterion in the table designed to fail for the right
  reason.
- Mechanicals clean: 5 / 23 / 26 / 4 / 19, 0 unparsed, 0 recovered; audit `pass`.

## Concerns

| Concern | Severity | Resolution |
| :-- | :-- | :-- |
| C1 — **`REQ-AGENT-052` has no subject.** It appears 6 times in the bundle and **not once with a stated requirement**. D-1 makes #182 an *amendment*, so there is no third behaviour change needing an id. Yet SC1 asserts it exists, SC8 asserts its Verification is green, and 3.1's fixture asserts a property of it — **SC1 passes either way** | **high** | **Dropped.** 0.1 is now "ONE new id plus two amendments", and SC1, SC8 and 3.1 are amended to name `049` + the two amended REQs. Recorded that the reservation came from EXP-004, written **before** D-1 narrowed #182 |
| C2 — **`ctl-182-spike` as specified is unsatisfiable and the gate can never open.** `REQ-AGENT-043`'s Verification line contains an editorial ellipsis, `"writes ... at presentation"`; `grep -cF` → **0**. Built to the letter, the fixture returns exit 1 on **all three** arms — a false RED, a half-fix arm carrying no information, and 1.4/2.4/3.4 plus all of Epic 4 blocked forever | **high** | **Fixed.** Conjunct (b) now says fragments **resolve**, with `...` matched as a regex wildcard, and the reason is stated in the issue — the fixture author copies whatever the issue prints. 1.2's retarget must leave every fragment resolvable under the same rule |
| C3 — **Issue 1.2 cites an artifact that does not exist.** "Steps 3, 9 and 10 of EXP-002's ordered list" — EXP-002 *recommends* shipping such a list and does not contain one. R1's mitigation depended on that enumeration | **high** | **Fixed.** 1.2 now **writes** the list to `assets/edit-set-182.md`, one row per site with *what catches a miss*, and names the three unmechanized sites inline instead of by index |
| C4 — **three `partial` rows have no comment producer**, and `_verify_row` maps `partial` → `requires_mention: True`. `verify-reconcile` runs at 4.4, **after** the outward writes begin | med | **Fixed.** 4.2 now names all five, with what each comment carries, plus a clause reconciling `grant`'s enumeration against the table **before** the gate is presented |
| C5 — **SC3 cannot fail.** A control that is unconditionally non-zero satisfies "assert non-zero" trivially | med | **Fixed.** SC3 is now two-armed: non-zero on the half-fix tree **and** zero on the same tree with the retarget applied. One arm is not a distinction |
| C6 — **SC7 passes on a stub.** Both clauses are negative, and negatives are vacuously true of an empty formula | med | **Fixed.** Added a positive **set** assertion on the cooked step-ids, per 3.3's own never-a-count rule |
| C7 — **R1 over-claims the drift edge.** `yf-drift-check` has no runnable command and is never a CV row, so a declared edge executes nothing — yet R1 credited it with closing the plan's only high risk | med | **Fixed.** R1 now attributes mechanical closure to 3.3's CV `fast` row and calls the edge the prose backstop it is. SC5's own wording was already honest and is unchanged |
| C8 — **SC6 asserts conduct its check cannot reach.** R2 admits a token check is satisfied by a comment or a prohibition (both measured GREEN); SC6 then claimed §3 "dispatches" | med | **Fixed.** SC6 now claims what it checks — the section *names* `Agent` — plus a second, less gameable clause requiring the imperative dispatch form used at `SKILL.md:315` |
| C9 — **a D-5 "re-measured" figure is wrong.** "3 sites" omitted `reviewer.md:43`; the real count is **4**. The stale-literal class D-5 exists to prevent, occurring inside D-5's own table | med | **Fixed** to 4 with the site list, and 0.3's baseline instruction now says re-grep rather than copy the list |
| C10 — **`ctl-184-dispatch`'s GREEN record was attached to the wisp** (2.3), the one deliverable R4 concedes the plan did not need, so a descope would silently wedge the gate | med | **Fixed.** Moved to 2.2, the issue that lands the fix the control measures. 1.2a and 3.3 are correct as-is — each is the last edit of its own edit set |
| C11 — **SC10 is self-contradictory:** one invocation with both paths shows only the union, not that each side selects independently | med | **Fixed.** Two separate single-path invocations. The one-flag rule stays with 4.1's multi-path FULL run |
| C12 — the **Reconcile Gate declares no Condition and no Test**, a regression from plan-050 | low | **Fixed** — Condition plus a real `bd list … \| jq -e` test with this plan's id |
| C13 — "Four experiments returned"; there are **five** | low | **Fixed** in both the prose and the results heading |
| C14 — **#177's note says "closed out"; the issue is OPEN.** Also "D-6" referred to plan-050's D-6 while this plan has its own | low | **Fixed** — reworded, and the cross-plan reference is now qualified as plan-050's |
| C15 — two `read-only` restatement sites were dropped from the finding's own list | low | **Fixed** — `workflows.md:180` and `:64` named with an explicit **no-edit** disposition, so the enumeration is complete rather than silently narrowed |
| C16 — the tightened grep pattern is **currently a no-op** (both patterns derive 3), and has the opposite failure mode | low | **Fixed** — recorded as insurance rather than a live fix, with the widening requirement stated |
| C17 — "Epics 1-3 are independent" is contradicted by a gate spanning all three controls | low | **Fixed** — qualified as independent *up to the shared red-prework gate* |
| C18 — `SPEC.md` is ambiguous between root and `skills/yf-plan/` | low | **Fixed** — every citation path-qualified; noted both files are edited here |
| C19 — **`ctl-165-executable`'s RED will be red for the wrong reason.** After 0.1 the backticked-command conjunct is already green, so the RED comes only from the test not existing | low | **Fixed** — recorded as a second honesty note in 3.1, to be written into `red-prework.md` alongside the observation |
| C20 — all 11 `references/upstream-*.md` had an empty `URL:` field | low | **Fixed** — all 11 populated |

## Missing

- **A re-spike record for the copied harness.** plan-050's RE-005 documents `redcheck.sh` reporting
  *"RED observed"* with **exit 0** for a missing fixture. **Resolved:** 0.2 now requires re-spiking
  into `assets/` before first use — 0.2's own portability argument applies to the harness's
  trustworthiness too.
- Comment drafts for #173/#174/#150 — resolved under C4.
- The reviewer noted the three `.4` verify issues assert a strict subset of what the gate's
  `verify-all` already asserts, and are therefore near-no-ops. **Retained deliberately:** they are
  the discharge point for SC2b and they read the record rather than re-running a verb, which is the
  separation plan-050's C38/C53 established.

## Gate Assessment

**Reachability sound, satisfiability was not** — and the distinction is the reason for the REVISE.
Per-control verification confirmed every `assert-distinguishes` producer is an ancestor of the `.4`
it feeds and that none sits inside `Blocks {1.4, 2.4, 3.4}`; no cycle; earliest legal position. But
`ctl-182-spike` as specified could **never** exit 0 (C2), so the gate was unreachable in the way that
matters, taking Epic 4 with it. Reachability is a graph property and passed; satisfiability is
semantic and did not. Both are now fixed, and C10 moved the one misplaced producer.

## Upstream Assessment

`include` (#182, #184) correct — both OPEN, both wired, both with a measured RED, and #182's note
correctly records that **D-1 narrows the issue rather than accepting its framing** (the issue body
claims a prohibition the tree does not contain; that correction must reach the closing comment, not
just the plan). `partial` #149/#165 well specified, and SC13's requirement that the #149 comment
*refute* the issue's own premise is the right call. #173/#174/#150 were under-specified — fixed under
C4. #177's disposition is right, its note was wrong (C14). The three `deferred` rows carry specific
reasons rather than boilerplate. Both out-of-scope defects are correctly identified and one was
re-verified at source.
