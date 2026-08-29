---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #273: The command-vs-obligation law: prose naming a COMMAND is followed more reliably than prose naming an OBLIGATION — one mechanism behind #264, #270, #145's finding 4, and retrospective_fields.py

- **Number:** 273
- **Title:** The command-vs-obligation law: prose naming a COMMAND is followed more reliably than prose naming an OBLIGATION — one mechanism behind #264, #270, #145's finding 4, and retrospective_fields.py
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/273
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

| Recorder | Rate | How measured |
| :-- | --: | :-- |
| **A script writes it itself** | **15 / 15 (100%)** | `okf.append_log` inside `plan_manager.py:6172`; `grep -h "autonomy: max-review-cycles raised" docs/plans/*/log.md` → 15 across plan-050 (7), 052 (1), 054 (2), 055 (2), 056 (3) |
| **Prose instructs an agent to RUN A COMMAND** | **5 / 6 (83%)** | of 6 post-plan-045 plans that crossed the default bound of 5, five ran `review-loop-check`. plan-048 did not — it ran 7 cycles one day after the verb landed |
| **Prose instructs an agent to HONOUR AN OBLIGATION** | **2 / 12 (17%)** | 12 escalations in completed plans → 2 `stop_class: 4` retrospective entries. plan-054 had 2 escalations and wrote 7 entries, **none** with `stop_class: 4` |

**A factor of five between the two prose forms.** The confound that normally ruins this comparison —
different authors, tasks, sessions — is absent by construction: both instructions attach to the
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
- **Extending `review-loop-check` is a command on an existing path.** Predicted **83%**. Adopted.
- **"Record the escalation in `escalations.md`" is an obligation.** Predicted **17%** — which is why
  the artifact must be written **by the same verb that detects**, not by a later instruction.
- **"Notice your trigger never fired" is an obligation with no event to attach to** — worse than
  17%, because there is no moment at which it comes due.

The general form: **does this instruction name a command, or an obligation?**

## Limits, stated

- **n is small on the decisive row.** 6 plans crossed the bound, one skipped. Read the 83% as
  *"materially better than 17%"*, **not** as a point estimate.
- **The 15/15 row is not a fair comparator** — a script cannot forget, so it measures the absence of
  a failure mode rather than compliance. It bounds the other two from above.
- **Only one event was measurable this way.** `review-loop-check` is auditable *only* because the
  script writes its own echo — "an accident of design, not a general property". **The law is derived
  from the one event instrumented well enough to see it, which is itself an instance of the law.**
- **Causation is not established.** A plan that runs the check may differ from one that does not for
  reasons other than the instruction's form.

## Related

- #264 · #270 · #145 · #269

🤖 Generated with [Claude Code](https://claude.com/claude-code)

