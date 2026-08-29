---
type: Finding
okf_spec: OKF-PLAN
---

# The command-vs-obligation law

## Finding: Why are some yf instructions reliably followed and others reliably skipped?

### Approach Tested

See the Result section; this finding is a synthesis of measurements reported inline with their commands.

### Result

**measured:** every figure below is reproduced from the commands named inline; **inferred:** claims are marked as such where no command establishes them.

**Status.** A side-finding of EXP-001, elevated to its own artifact at the parent's flag. It is
promoted because **it is not about `yf-judgement`** — it explains #264, #270 and #145's finding 4
from one measurement, and it predicts which of `yf-judgement`'s own instructions would fire.
Proposed for its own upstream issue so it is citable outside this plan's readership.

#### The measurement

Three recorders, **one event, with author, session and task held constant** — `review-loop-check`
escalating at its bound, which is recorded twice by two different mechanisms:

**Population, stated first because getting it wrong is how this table went wrong three times.** The
**five POST-PLAN-045 plans** whose `reviews/pass-*.md` count exceeds the default bound of 5, measured
in the main checkout at `~/workspace/dixson3/yoshiko-flow`: `plan-048` (7 passes), `050` (13), `052` (6), `054`
(6), `055` (7). `plan-056` is excluded from **every** row — its bundle in `main` contains no `log.md`
at all. **The `post-plan-045` qualifier is load-bearing**: by the bare pass-count criterion the set
is **seven**, adding `plan-026` (7 passes) and `plan-029` (6), both of which **predate
`review-loop-check` and could not have run it**. A fourth draft dropped that clause and red-team
pass 4 measured the resulting sentence false. **All three rows below use this one population.**

| Recorder | Rate | Unit | How it was measured |
| :-- | --: | :-- | :-- |
| **A script writes it itself** | **12 / 12 (100%)** | per event | `grep -h "autonomy: max-review-cycles raised" docs/plans/*/log.md` -> 12: plan-050 (7), 052 (1), 054 (2), 055 (2); plan-048 contributes 0, having never run the verb |
| **Prose instructs an agent to RUN A COMMAND** | **4 / 5 (80%)** | per plan | four of the five ran `review-loop-check`; `plan-048` did not, one day after the verb landed |
| **Prose instructs an agent to HONOUR AN OBLIGATION** | **2 / 5 (40%)** | per plan | two of the five wrote a `stop_class: 4` retrospective entry (050 and 052) |

**The comparison is 4/5 vs 2/5 over one stated population. This table has been wrong THREE TIMES and both
corrections are recorded here rather than quietly applied.**

- **Draft 1** reported **2/12 (17%)** against **5/6 (83%)** and called the gap *a factor of five*.
  **Red-team pass 1** established those are different **units of analysis** — 83% is *per-plan,
  at-least-once*; 17% was *per-event*.
- **Draft 2** corrected to 2/4 but drew its rows from **different populations**: row 1 counted
  `plan-056` while row 3 excluded it. **Red-team pass 2** caught that this is *the same class of
  error one revision later* — and that the new Limits section warned only against the **unit**
  version of it.
- **Draft 3** stated "one population — the four plans complete at measurement time" while **row 2's
  denominator was still 6**. **Red-team pass 3** measured that only five post-plan-045 plans exceed
  the bound in `main` and that the claim was therefore false on the row it was meant to fix.
- **Draft 4** adopted those five but **dropped the `post-plan-045` qualifier** from the sentence
  naming them. **Red-team pass 4** re-derived by the criterion as literally written and got
  **seven** — `plan-026` and `plan-029` also exceed the bound. The numbers were right; **the sentence
  describing them was false**, which is the finding's own Limit violated by the finding itself.

Both corrections are recorded because **the wrong number was reported upward before either was
caught**, and because a limits list that omits the error you are about to make is decorative.

**The direction survives; the magnitude does not.** And one confound the earlier draft claimed to
have removed is only partly removed: both prose instructions do attach to the same event in the same
run, but `plan-050`'s 7 raises collapsing to 1 entry is **at least as plausibly a correct per-plan
granularity judgement as a compliance failure** — research 005 itself found 6 of those 7 raises were
ceremonial rounds carrying zero findings.

#### Why it is a law and not a tautology

The obvious objection is that the three rows differ in effort. They do not differ in the direction
that would explain the gap: `retrospective-append` **is itself a command**, one line, with the
arguments already in hand at the moment of the stop. The obligation row is not "prose asks for something
expensive". It is **"prose asks for a record rather than an action"** — and a record has no failure
mode the agent will notice.

The corpus's own formulation, from two directions:

> **"Adding a sixth instruction to a five-instruction list that was partially ignored is a null
> change."** — `plan-043/findings/exp-001-reconcile-skip-cause.md:105-117`

> *"Each is a paragraph. **None is a thing that must be CLOSED.** … a verification bead is a thing
> that must be closed; **a prose instruction is a thing that can be believed to have been
> followed.**"* — `plan-052/references/upstream-197.md:25-35`

> **"a step with no exit code is not a step"** — `research/004/Summary.md:41-52`

#### What it explains that was previously explained separately

| Observation | Prior explanation | Under this law |
| :-- | :-- | :-- |
| **#264** — subordinate goes `idle` at a phase boundary, twice, under a contract that had already been tightened once | a wording ambiguity in the AUTONOMY clause | the clause is an **obligation** (*"continue without waiting"*). Nothing runs; nothing exits non-zero when it is not honoured. The wording fix worked at n=1 — but it produced a **stronger obligation**, not a command, so the law predicts it will decay |
| **#270** — `plan-review.formula.toml`'s human gate has never been poured in 27 review passes | unknown; recorded as an open question | pouring it is an **obligation** in SKILL.md prose. Nothing fails when it is skipped, and the gate is invisible in its own absence |
| **#145 finding 4** — `closable` never run; `audit` never fired at the phase that mattered | "a manually-invoked skill will not be invoked" | the same law, stated over invocation rather than over recording. Both were **obligations to run something**, with no caller |
| **`retrospective_fields.py`** — CI-validated, README-documented, schema-referenced, **zero callers** | not previously identified | an obligation with no command site at all — the terminal case |

**Four independently-filed defects, one mechanism.**

#### What it predicts about `yf-judgement` itself

The law is usable as a design test, and this plan applies it to itself:

**These predictions survive the correction above**, because each turns on the *direction* of the
gap and on the four independently-filed defects the law explains — not on its magnitude. A 1.7x gap
is a weaker argument than a 5x gap and a sufficient one for every choice below.

- **A `/yf-judgement` slash command is an obligation.** Predicted rate: the measured rate of a fresh
  invocation path, which is **0**. Rejected.
- **Extending `review-loop-check` is a command on an existing path.** Predicted rate: **4/5**, the
  measured rate of that path. Adopted.
- **"Record the escalation in `escalations.md`" is an obligation.** Predicted rate: **the obligation row, ~50% at best**. This is
  why the artifact must be written **by the same verb that detects**, not by a subsequent
  instruction — and it is the specific reason Epic 2's `escalation-raise` is a script rather than a
  documented convention.
- **"Notice your trigger never fired" is an obligation with no event to attach to** — worse than
  the obligation row, because there is no moment at which it comes due. Hence Epic 5, and hence SC6.

#### The limits, stated

- **THE UNIT MISMATCH — draft 1's error.** The two prose rows must be compared at the same unit or
  the gap is manufactured. At the per-plan unit the comparison is **4/5 vs 2/5**.
- **THE POPULATION MISMATCH — draft 2's error, a different failure with the same shape.** Every row
  must be drawn from the **same set of plans**, and that set must be **stated**. Mixing an incomplete
  or unmerged bundle into one row and not another manufactures a gap just as effectively as mixing
  units. **Any restatement must name its population in the same sentence as its numbers.**
- **REPRODUCIBILITY IS PART OF THE MEASUREMENT.** Row 1's command returns 12 or 15 depending on which
  worktree it runs in. State the tree.
- **n is small on both decisive rows.** Five plans crossed the bound; the two prose rows are 4/5 and 2/5. Read the
  gap as *"materially better, direction only"* — not as a point estimate and not as a ratio.
- **The single miss is dated, and it cuts both ways.** plan-048 crossed the bound **one day after
  the verb landed**. Excluding it as "mechanism not yet known" gives 5/5 = 100% and destroys the
  contrast with the script row; including it makes *"the miss rate is a design input"* rest on n=1. Neither reading is obviously right, and the plan does not depend on choosing.
- **The 12/12 row is not a fair comparator** — a script cannot forget, so it measures the absence of
  a failure mode rather than compliance. It is included because it bounds the other two from above.
- **Only one event was measurable this way.** `review-loop-check` is auditable **only because the
  script writes its own echo — "an accident of design, not a general property"** (EXP-001). The law
  is derived from the one event in the corpus instrumented well enough to see it, which is itself
  an instance of the law.
- **The direction of causation is not established.** A plan that runs the check may differ from one
  that does not for reasons other than the instruction's form.

### Implications for Plan

**This is the law the whole plan keys on**, and it is not specific to `yf-judgement`: it explains
#264, #270 and #145's finding 4 from one measurement, and it is applied to this plan's own design
choices as a test.

**It predicts that a `/yf-judgement` slash command fires at 0%**, that extending `review-loop-check`
fires at 4/5, and that "record the escalation" as an instruction fires at the obligation row's rate — which is why
`escalation-raise` must be a script invoked by the detecting verb, not a documented convention.

### Recommendations

1. **File it as its own upstream issue** so it is citable outside this plan's readership.
2. **Use it as a design test on every new instruction**: does this name a command, or an obligation?
3. **Treat the gap as directional, not as a point estimate or a ratio** — n=6 and n=4 on the two
   decisive rows, and the table has already been restated twice.
4. **Do not read the 12/12 row as compliance** — a script cannot forget; it bounds the others from
   above.
