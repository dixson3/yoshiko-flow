---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #174: yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it

- **Number:** 174
- **Title:** yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

**Proposes the mechanism for the defect family #173 diagnoses.** #173 records *what went wrong and why five red-team cycles missed it*, under an explicit "record, do not fix" instruction. This issue proposes *what to build*. Neither subsumes the other; #173 should stay open as the evidence.

Originated from an operator question during plan-046 execution: *"if the review is checking against a plan's intent vs the code that scores it, do we need a kind of 'review experiment' to fully validate plans — much like we run experiments to constrain the design?"*

## The observation that makes this cheap

**The red-team already does this, sporadically.** In plan-046's five cycles, every high-value finding after cycle 1 came from a reviewer *executing* something rather than reading:

- cycle 5 confirmed the engine gate by **running** it (`EXIT=1` pre-work)
- cycle 4 discharged SC9 by **running** the greps — and found the counts disagreed 2/1, 3/1, 1/0
- cycle 3 caught an incomplete blast list by **running** the corpus grep (16 hits across 8 files, three of them fixed-authority spec nodes)

So this is not a new phase. It is making systematic what currently depends on the reviewer thinking to try it.

---

## Part 1 — The falsification rule

At review time you generally **cannot verify** a criterion; the work is not done. But you can **falsify** it, and that is sufficient:

> **Every success criterion and every gate `Test:` must FAIL when executed against the pre-work tree.**

A criterion that already passes before the work exists is, by definition, not measuring the work.

**This rule alone catches both engine-gate defects in plan-046**, each of which survived a full review cycle:

| Attempt | Test | Pre-work result | Verdict |
| :-- | :-- | :-- | :-- |
| 1 | the `pytest` suite | **exit 0** (already green — exp-001 had measured `31 passed`) | vacuous |
| 2 | `uv run "${CV_SKILL_DIR}/…"` | **did not spawn** — `${CV_SKILL_DIR}` defined nowhere in the repo | broken |
| 3 | same command, repo-relative path, piped through a `python3 -c` exit-code predicate | **exit 1**, then 0 after Epic 1 | real |

plan-046's Issue 1.4 is a **hand-rolled instance of exactly this rule** — *"run the gate command today and confirm it exits non-zero"* — and it is what finally caught attempt 2. Generalizing it is the proposal.

## Part 2 — The cross-check matrix

The falsification rule handles **executable** claims. It does **not** handle claims about contracts you have to go and read. Those need a mechanical completeness check instead:

| Claim in the plan | Checked against |
| :-- | :-- |
| upstream disposition (`include` / `partial` / `supersede` / `exclude`) | what `verify-reconcile` **requires** for that literal value |
| each success criterion | the issue(s) that discharge it — and each issue → a criterion (bidirectional; an unmapped criterion or an unscored issue is a finding) |
| each cited `REQ-*` id | exists, is not double-allocated, is not dangling |
| each cited `file:line` | resolves to the quoted content |

That last row is nearly free and would have caught four defects in plan-046 alone: two stale line references, a cited `write_index` function that does not exist, and `DRIFT-CHECK.md:81` (off by one — the row is at `:80`).

---

## Three worked examples

**1. SC3 — caught by the matrix, not by execution.** The criterion required `grep -rniE "okf_version.*0\.1|OKF v0\.1"` to return **zero** hits, while Issues 2.1 / 2.3 / 2.4 *require* v0.1 references (the vendored-spec link, the v0.1→v0.2 section map, the §13 verification quoting v0.1 beside v0.2). The criterion forbade what the plan mandated. It survived all five cycles and was found at execution. This is a pure internal contradiction — **no code needed**, only the criterion↔issue mapping. Full write-up: plan-046 `findings/exec-003-sc3-unsatisfiable.md`.

Its predecessor **SC9** had the identical shape (it quoted the variant strings it forbade, *inside* the criterion, making it its own counter-example) and was caught only at pass 4/5 — by a reviewer who happened to run it.

**2. The vacuous engine gate — caught by the falsification rule.** See the table above. Two attempts, two distinct failure modes, both green-by-default.

**3. #140's disposition vs `plan_manager.py:2023` — HONEST NOTE: the falsification rule would NOT have caught this.** Issue 4.5 instructed *"Close #140 as `partial`"*; the engine enforces *"a `partial` row must stay OPEN (its remaining half is still real work)"*. There is no command to run at review time that surfaces this — you have to know `verify-reconcile` exists and read its contract for that disposition value. **Only the matrix's first row catches it**, and only if the matrix is populated from the engine rather than from the plan's own prose.

This is the strongest argument for building **both halves**. A harness that only executes would ship with #140's contradiction intact.

---

## Relationship to #113

**#113** (execution-rehearsal review pass — a topological DAG walk against running state) is the **ordering** half: does any issue need a tool, file, or artifact authored later? This is the **claims** half: is any assertion in the plan false, vacuous, or unenforceable *as written*?

They likely want to be **one pass with two checks**, because both need the same prerequisite: **the plan's assertions extracted into a machine-readable list.** That extraction is the real work; once it exists, both checks are cheap. Worth deciding deliberately rather than building two extractors.

---

## Honest limits

- **Post-state criteria are not falsifiable.** *"The producer emits `upstream-triage.md` on creation"* cannot be checked before the producer is fixed. You can only assert it does **not** today — weaker, but still worth having.
- **Cost.** plan-046 burned its full 5-cycle review budget. The counter-argument is that it burned it *finding these by hand* — but a review harness that adds a cycle to every plan needs to earn it.
- **The matrix is only as good as its population.** If the disposition→contract row is written from the plan's understanding rather than read from `plan_manager.py`, it reproduces the exact defect it exists to catch.
- **Prose criteria remain unreachable.** A criterion phrased as *"the baseline cites v0.2 section numbers throughout"* has no command; plan-046 handled this by emitting an explicit section map and checking row by row. That pattern generalizes but has to be authored per criterion.

## Prior art in this repo

plan-046 shipped **three** hand-rolled instances of these checks — Issue 1.4 (falsify the gate), Issue 3.8 (measure the audit contract by execution, *with a positive control* proving the harness can observe failure), and SC4 (check each reference against an emitted map). All three were written after a review cycle caught the corresponding defect. That is the signal: the pattern keeps being reinvented per-plan, after the fact.

**Cross-references:** #173 (the diagnosis this proposes a fix for) · #113 (the ordering half) · #135 (a measured literal in `plan.md` goes stale when the plan is inside its own measured corpus — same root: plan text asserting facts nothing re-checks) · #165 (SPEC `Verification:` lines are prose shaped like commands).

Source: plan-046 (`docs/plans/plan-046-james-dixson-aabefa/`), five red-team passes and a seven-entry retrospective.
