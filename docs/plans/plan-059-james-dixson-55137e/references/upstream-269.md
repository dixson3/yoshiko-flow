---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #269: New skill: yf-judgement — detect when a plan needs OPERATOR JUDGEMENT and escalate a question, rather than attempting another fix

- **Number:** 269
- **Title:** New skill: yf-judgement — detect when a plan needs OPERATOR JUDGEMENT and escalate a question, rather than attempting another fix
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/269
- **State:** OPEN
- **Labels:** 

## Body

> **Written to be read cold.** The empirical basis is `yf-research` 005 (PR #267,
> `docs/research/005-thrash-detection-and-operator-judgement/`), a deep-mode study over **114 plan
> bundles and 301 review passes across 7 repos**. Nothing here requires the originating conversation.

## Proposal

A **`yf-judgement`** skill that detects when plan development or execution has stopped converging
and — instead of attempting another fix — escalates a structured question to the **upstream
controller** (the human operator, or the session that spawned this one).

Originating hypothesis: thrash signals an **under-specified objective** — the operator stated a
goal too generally, or assumed the agent would "figure it out", when what was needed was operator
judgement to constrain the choice space.

## What the research established — read this before designing

**The originating hypothesis was NOT confirmed, and the honest scope of that result matters.**

| Prediction | Result |
| :-- | :-- |
| Under-specified objective → churn | **r = −0.002** (objective word length vs direction changes) |
| Vague objectives churn more | Churned plans' objectives were **longer** (57 vs 53 median words) |
| Pre-eliciting the missing specification reduces churn | **Null** — pre-elicited group took *more* passes (3.05 vs 2.42), confounded by size |
| bd execution telemetry surfaces thrash | **Null** — nominated **zero** bundles; content-level reopens = 0 |
| git churn surfaces thrash | **Null** — 0 of 20 hand-audited re-touches were genuine thrash |

**This is not a refutation of the construct.** Every specification measure computed was
*length-derived*, so the corpus could not test "under-specification" as such. An earlier "refuted"
framing was **withdrawn at refine** after the red-team pass established it strengthened a claim no
new measurement supported. A construct-valid test needs a specification measure that is not a
function of length.

### The four constraints any design must satisfy

1. **Plan size is the dominant confounder** (ρ = 0.739 with review-pass count). Only **3 of 14**
   candidate signals survive controlling for it. **The obvious similarity-based "the agent is
   repeating itself" detector is a length sensor** — it correlates with `plan.md` size, not with
   stuckness.
2. **There is no pre-burn signal.** Nothing is detectable at pass 1. A front-loaded
   clarifying-question interview has neither a trigger to fire on nor a measured benefit.
3. **The best surviving signal is weak and late.** Severity-decay (a HIGH-severity finding
   surviving into pass ≥ 3): LR+ **3.7** on the evaluable population / **3.0** in the stratum the
   study is actually about; **first computable at pass 3**, so it cannot prevent a 3-pass burn;
   **silent on 68% of the corpus** (72 of 114 bundles never reach pass 3).
4. **It is shippable only under an exact-match severity predicate** — lowercased, stripped, equal
   to the literal `high`. Not a substring, not a regex, and **not** any normaliser folding
   `blocking` into HIGH: that variant fires on `plan-026`, a bundle whose 7-pass APPROVE/REVISE
   oscillation is *deliberate re-scoping* with zero recurrence. Severity is unusable on **204 of
   1,509 findings (13.5%)** and the recorded vocabulary includes `medium-high`, `med/high`,
   `high, blocking`. **Pinning the vocabulary is the prerequisite deliverable; the detector is
   downstream of it.**

### Two constraints that hold regardless of trigger

- **Read second-party residue, never a controller's self-report** (certified consensus C3). An
  agent asked "are you stuck?" is the least reliable available witness.
- **Batch escalations to a boundary; never interrupt per question.** The one design shape two
  independent surfaces *and* the interruption literature converged on.

## The recommendation

**Build the escalation path; treat the detector as optional and second.**

The detector cannot prevent the burn where the damage happens. The escalation path has the one
result with corpus support behind it: the dominant category of operator input (T1, 45/119, the only
category present in **all 7 repos**) has **80% arriving after a draft exists** — exactly where a
mid-execution ask can reach and a pre-flight cannot. Mid-execution escalation is also a genuine gap
in prior art: every "ask before acting" skill the study reached is opt-in and pre-task.

**Ship one-hop; label N-hop as a bet.** See #264 — `yf-herdr` already seeds `YF_PARENT_PANE`,
establishing an upstream-controller chain, and `REQ-HERDR-024` is already the escalation predicate
at one hop (*the parent answers only when settled by existing approved plan content; anything
changing scope, risk or a success criterion goes to the operator*). The **N-hop** generalisation is
**untested** — the corpus's own mechanism is one-hop, and the propagation-budget/dedup requirement
follows from topology rather than measurement (its one supporting analogy was withdrawn).

## Synergies with #145 (`yf-retrospective`) — the reason this issue cites it

These two skills share more than a namespace, and at least one shared constraint is decisive.

**1. #145's finding 4 is `yf-judgement`'s hardest constraint too: "a manually-invoked skill will
not be invoked."** #145 proves it twice — `closable` shipped and was *never once run to
completion*; `plan_manager.py audit` existed but never fired at the phase where it mattered, and
four plans shipped non-conformant files. A `/yf-judgement` slash command would rot identically.
**The trigger points are the design, not an implementation detail.**

**2. Independent convergence on the self-report problem.** plan-045 added `detected_by` and
`evidence` to `plan-retrospective.md` because *"a retrospective built from an actor's own account
would faithfully transcribe a false claim rather than detect one — an entry's trust level is a
property of who found it, and the recorder is usually the subject."* That is research 005's
consensus C3, reached from a different direction. **Two independent efforts converged on the same
principle**, which is the strongest form of support either has.

**3. `plan-retrospective.md` is a ready-made capture surface.** plan-045 landed the **emit** side
(`## RE-NNN` schema, `retrospective-append` / `retrospective-report`, 7 backfilled entries).
#145 notes *"a consumer built now would read an empty corpus; the corpus has to accumulate first."*
**`yf-judgement` may be that consumer** — and building on it avoids inventing a second capture
surface for the same events.

**4. The §6.4 step contract already permits `yf-judgement`'s exact shape.** Per #145's first
comment, the axes are orthogonal and **`halting` + `prose` remediation is explicitly permitted** —
a step may *enforce* that a record exists while remediation is *authoring* it. More precisely,
`remediation-kind: adjudication` is defined as *"the operator must decide between valid readings;
no mechanical fix exists"* — which is `yf-judgement`'s payload, named. **Inherit this contract; do
not re-derive it.**

**5. Complementary in time, on the same axis.** `yf-judgement` fires **during** review cycles;
`yf-retrospective` measures **after**. #145's review-escape / process-escape split (the check
existed and missed, vs no check existed) is the same distinction `yf-judgement` needs to decide
whether to ask a question or file a gap.

**6. Both are data-starved by the same shortfall, and #145's risks transfer wholesale.** #145 has
n=3 after ~40 plans; 005 has 17 firing / 20 control and exactly **one** bundle nominated by two
independent surfaces. Both flag **Goodhart** (once measured, pressure to reclassify), and #145's
**origin-vs-culpability split with a default of "no review at fault"** is directly applicable —
`yf-judgement` asking "why are you stuck" risks manufacturing an under-specification story where
none exists, which is precisely the hindsight failure #145 guards against.

## What nobody has measured — check before trusting the above

- **Recall was never measured.** Only precision. No statement in the research bounds how many
  thrash episodes were missed.
- **"The agent thrashed" and "the reviewer was slow" leave identical residue.** Nothing in a plan
  bundle separates them, and `yf-judgement` would treat them the same.
- **Whether asking a question earlier would have helped is untested** — there is no counterfactual
  arm anywhere in the corpus.

## Related

- #145 — `yf-retrospective` (synergies above)
- #264 — `yf-herdr` AUTONOMY defect; carries the escalation-architecture proposal and its assessment
- PR #267 — the research bundle

🤖 Generated with [Claude Code](https://claude.com/claude-code)

