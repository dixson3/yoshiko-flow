---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #273 - The command-vs-obligation law: prose naming a
  COMMAND is followed more reliably than prose naming an OBLIGATION — one mechanism
  behind #264, #270, #145''s finding 4, and retrospective_fields.py'
---
# Upstream #273: The command-vs-obligation law: prose naming a COMMAND is followed more reliably than prose naming an OBLIGATION — one mechanism behind #264, #270, #145's finding 4, and retrospective_fields.py

- **Number:** 273
- **Title:** The command-vs-obligation law: prose naming a COMMAND is followed more reliably than prose naming an OBLIGATION — one mechanism behind #264, #270, #145's finding 4, and retrospective_fields.py
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

> Measured by EXP-001 of plan-059 (`yf-judgement` design) and elevated to its own artifact because
> **it is not about `yf-judgement`**. Source:
> `docs/plans/plan-059-james-dixson-55137e/findings/finding-command-vs-obligation.md`.
> Written to be read cold.

## The finding

Why are some yf instructions reliably followed and others reliably skipped? Not because of effort,
and not because of prose-vs-mechanical. The discriminator is **what the prose names**.

Three recorders, measured on **one event with author, session and task held constant** —
`review-loop-check` escalating at its bound, which is recorded twice by two different mechanisms:

> **CORRECTED 2026-08-29 (plan-059 Issue 6.4).** The original framing of this section is
> **WITHDRAWN**. It compared a per-plan rate against a per-EVENT rate over two DIFFERENT
> populations — 6 plans on one row, 12 escalations on the other — and then divided them. Two
> incommensurable denominators do not form a ratio, so the "factor" it reported was an artifact
> of the unit change, not a measured effect. The comparison below is restated at **one unit
> (per-plan) over ONE stated population**, and the multiplier is withdrawn outright rather than
> recomputed.

**The population: the five post-plan-045 plans that exceeded the review-cycle bound.** Both rows
below are counted over that same set of five, per plan, so the two are commensurable.

| Recorder | Rate (per plan, same population) | How measured |
| :-- | --: | :-- |
| **Prose instructs an agent to RUN A COMMAND** | **4 / 5** | of the five post-plan-045 plans that crossed the default bound of 5, four ran `review-loop-check` |
| **Prose instructs an agent to HONOUR AN OBLIGATION** | **2 / 5** | of the same five plans, two recorded a `stop_class: 4` retrospective entry. plan-054 escalated and wrote 7 entries, **none** with `stop_class: 4` |

**A script that writes its own record is not on this table**, and that is deliberate. The
`15 / 15` figure previously shown alongside these rows measured **the absence of a failure mode**
— a script cannot forget — so it is an upper bound on the other two rather than a third
comparable recorder, and putting it in the same table invited exactly the arithmetic this
correction removes. It is retained under *Limits* below.

**The direction is what survives, and it is the part worth acting on.** With n = 5 the honest
claim is *"a command is followed more often than an obligation, on a small sample where the
confound is controlled"* — **not** a multiplier. The confound that normally ruins this comparison
— different authors, tasks, sessions — is genuinely absent: both instructions attach to the
**same event in the same run**.

## Why it is not a tautology about effort

The obvious objection is that the rows differ in effort. They do not differ in the direction that
would explain the gap: `retrospective-append` **is itself a command** — one line, with its
arguments already in hand at the moment of the stop.

The 17% row is not *"prose asks for something expensive"*. It is **"prose asks for a RECORD rather
than an ACTION"** — and a record has no failure mode the agent will notice.

The corpus had already reached this from three directions without connecting them:

> **"Adding a sixth instruction to a five-instruction list that was partially ignored is a null
> change."** — `plan-043/findings/exp-001-reconcile-skip-cause.md`

> *"Each is a paragraph. **None is a thing that must be CLOSED.** … a verification bead is a thing
> that must be closed; **a prose instruction is a thing that can be believed to have been
> followed.**"* — `plan-052/references/upstream-197.md`

> **"a step with no exit code is not a step"** — `research/004/Summary.md`

## Four independently-filed defects, one mechanism

| Observation | Prior explanation | Under this law |
| :-- | :-- | :-- |
| **#264** — subordinate goes `idle` at a phase boundary, twice, under a contract already tightened once | a wording ambiguity in the AUTONOMY clause | the clause is an **obligation** (*"continue without waiting"*). Nothing runs; nothing exits non-zero when it is not honoured. **The wording fix worked at n=1 — but it produced a stronger obligation, not a command, so the law predicts it will decay** |
| **#270** — `plan-review.formula.toml`'s human gate never poured in 27 review passes | unknown; filed as an open question | pouring it is an **obligation** in SKILL.md prose. Nothing fails when it is skipped, and the gate is invisible in its own absence |
| **#145 finding 4** — `closable` never run; `audit` never fired at the phase that mattered | "a manually-invoked skill will not be invoked" | the same law over *invocation* rather than *recording*. Both were obligations to run something, with no caller |
| **`retrospective_fields.py`** — CI-validated, README-documented, schema-referenced, **zero callers** | not previously identified | an obligation with **no command site at all** — the terminal case |

**The #264 row is the actionable one.** That issue's accepted fix is a wording change, validated at
n=1 by a three-boundary natural experiment. Under this law that fix is a *stronger obligation*, not
a command, and is predicted to decay. Anyone acting on #264 should read this first.

## Use it as a design test

plan-059 applies it to its own design and rejects one of its own options:

- **A `/yf-judgement` slash command is an obligation.** Predicted rate: that of a fresh invocation
  path — **0**. Rejected.
- **Extending `review-loop-check` is a command on an existing path.** Predicted at the
  command-form rate (`4 / 5` on the measured population). Adopted, and shipped in plan-059.
- **"Record the escalation in `escalations.md`" is an obligation.** Predicted at the
  obligation-form rate (`2 / 5`) — which is why the artifact must be written **by the same verb
  that detects**, not by a later instruction. plan-059 shipped it that way.
- **"Notice your trigger never fired" is an obligation with no event to attach to** — worse than
  17%, because there is no moment at which it comes due.

The general form: **does this instruction name a command, or an obligation?**

## Limits, stated

- **n is 5, and the unit is the plan.** Read `4 / 5` vs `2 / 5` as a **direction on a small
  sample**, never as a point estimate and never as a ratio. The earlier per-event/per-plan
  comparison and the multiplier derived from it are **withdrawn** (see the correction above).
- **The script-writes-it-itself figure (`15 / 15`) is not a fair comparator** — a script cannot
  forget, so it measures the absence of a failure mode rather than compliance. It bounds the other
  two from above, and is deliberately kept out of the comparison table.
- **Only one event was measurable this way.** `review-loop-check` is auditable *only* because the
  script writes its own echo — "an accident of design, not a general property". **The law is derived
  from the one event instrumented well enough to see it, which is itself an instance of the law.**
- **Causation is not established.** A plan that runs the check may differ from one that does not for
  reasons other than the instruction's form.

## Related

- #264 · #270 · #145 · #269

🤖 Generated with [Claude Code](https://claude.com/claude-code)


