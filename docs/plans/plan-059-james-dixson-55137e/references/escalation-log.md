---
type: Reference
okf_spec: OKF-PLAN
---

# Escalation log — plan-059 dogfooding record

**Why this file exists.** Decision D-3: this session was instructed to use the one-hop
escalation mechanism deliberately and record how it feels to use. That is not ceremony.
Research 005 §9.4 records, as an absence finding, that *"whether asking a question earlier
would have helped is untested — there is no counterfactual arm anywhere in the corpus"*, and
§8.4 records that *"the corpus records answers, and almost never questions."* **Every row below
is one datum in an arm that otherwise does not exist**, including the rows where the answer was
"did not escalate".

**Read the DECLINED rows as carefully as the RAISED ones.** A design that only records the
questions actually asked measures its own trigger's precision and nothing else. The rows where
escalation was considered and rejected are what bound its *recall* — the quantity research 005
never measured for anything.

## Schema

| Field | Meaning |
| :-- | :-- |
| `#` | sequential id within this plan |
| `phase` | the yf-plan phase the session was in |
| `question` | the one-line question, as it would have been sent |
| `disposition` | `raised` \| `declined-settled` \| `declined-deferred` |
| `predicate` | which arm of REQ-HERDR-024 decided it |
| `residue` | the second-party evidence that prompted it (C3: never a self-report) |
| `outcome` | what actually happened, filled in after the fact |

## Entries

### E-1 — "push a milestone": `git push`, or a herdr pane report?

| Field | Value |
| :-- | :-- |
| **phase** | SCOPE |
| **question** | "Does PUSH MILESTONES mean `git push`, or `herdr agent prompt "$YF_PARENT_PANE"`?" |
| **disposition** | `declined-settled` |
| **predicate** | *Settled by existing approved content* — the parent-answers arm. Two independent lines in the launch contract decide it: the stop list names "an outward-facing or irreversible write (commit/push/PR…)" as a **stop class**, so a git push cannot also be an autonomy-preserving action; and "Never pass `--wait`" matches a flag that exists on exactly one command, `herdr agent prompt`. |
| **residue** | The launch contract text itself — a second-party artifact, not this session's belief about it. |
| **outcome** | Resolved locally in one tool call (`herdr agent prompt --help`). No escalation sent. |

**What this row teaches the design.** The ambiguity was *real* and a wrong reading would have
violated a stop class — the worst available outcome. It was nonetheless **correctly not
escalated**, because the answer was recoverable from content already in hand.

This is the REQ-HERDR-024 predicate working exactly as written, and it exposes something the
one-line predicate does not say: **the cheap move is not "ask" and not "guess", it is "look".**
`grilling`'s G5, as quoted in research 005 §8.3, is the same move at a different hop — *"don't
ask the user for anything you could look up yourself."* A `yf-judgement` that escalates every
ambiguity would have burned an operator turn here. **The predicate needs a LOOKUP arm, not just
an answer/forward fork.** Provisionally: *look → answer → forward*, three arms, not two.

### E-2 — the worktree instruction (inbound, not outbound)

| Field | Value |
| :-- | :-- |
| **phase** | SCOPE |
| **question** | *(none — this was a downward correction, not an upward ask)* |
| **disposition** | n/a |
| **predicate** | n/a |
| **residue** | The operator measured that the shared checkout was on `research/005-thrash-detection` and that two unrelated commits from a third session had already landed on it. |
| **outcome** | Bundle moved to `.worktrees/yf-judgement-design` before any commit existed; nothing lost. |

**What this row teaches the design, and it is the sharpest datum so far.** This session could
not have raised E-2 as a question, because **it did not know the fact that made it
necessary** — that three sessions shared one checkout. The operator held that fact; the
subordinate held only its own view.

Two consequences for `yf-judgement`:

1. **The escalation channel is bidirectional, and the downward direction carries the
   information the upward direction cannot ask for.** A design that models escalation as
   "child asks, parent answers" misses the case where the parent must *volunteer* — and this
   case was, measurably, the higher-stakes one of the two so far.
2. **It is a counter-example to the framing that thrash is what needs escalating.** Nothing
   was thrashing. The session was converging normally toward a state that would have silently
   corrupted another session's branch. **No residue-reading detector — severity-decay or
   otherwise — could have fired here**, because the residue that mattered was in a different
   session's working tree. This is a concrete instance of research 005 §9.2's unmeasured
   recall: an episode that needed operator judgement and that no proposed trigger sees.

### E-3 — is "make the `plan-review` wisp actually pour" in scope?

| Field | Value |
| :-- | :-- |
| **phase** | INVESTIGATE |
| **question** | "Is making `plan-review.formula.toml` actually pour in scope for plan-059, or is it a separate `yf-plan` defect to file and design around?" |
| **disposition** | `raised` |
| **predicate** | *Forward* — it changes **scope**, the REQ-HERDR-024 forward arm. Not settled by any approved content: the launch prompt scopes this plan to designing `yf-judgement`, and fixing a `yf-plan` Phase-3 mechanism is a different deliverable. |
| **residue** | EXP-001's measurement, second-party: zero matching beads across all 1,245; 33 review passes written since the formula landed 2026-08-24. Not this session's belief about its own scope. |
| **outcome** | **RESOLVED — default confirmed. Out of scope; filed as #270.** The operator independently corroborated the formula, its landing commit (`57a21e3`, plan-052 Issues 5.1/5.3) and the zero-bead match, and **corrected one number** (see below). Round trip cost the session nothing: it never stopped. |

**What this row teaches the design, and it is the most useful entry so far.**

**1. The recommended default is what makes the ask cheap, and it is not optional.** The escalation
shipped with *"RECOMMENDED DEFAULT, which I will take if you do not answer: out of scope."* That
single clause converts the message from a **blocking question** into a **ratifiable proposal** —
the operator can ignore it entirely and the correct thing still happens. This is exactly the two
moves research 005 §8.3 found two independent surfaces converging on (*"batch the open decisions to
one boundary, and ship each with a proposed default the operator can accept rather than derive"*),
and it is the difference between the `writing` repo's single-line resolution — *"operator approved;
D1=both new, D2=both, D3=seed-only"*, described as **the cheapest operator turn in the corpus** —
and a question that stops a session.

**A `yf-judgement` escalation that does not carry a default is a stop wearing a question's
clothes.** Make the default a REQUIRED field.

**2. Escalating did not cost a stop, and that is the whole architecture in one observation.** The
session sent the question and kept working. This is the third arm #264's follow-up named — *"ask
upward, then continue or await"* — and it is the arm the current contract does not have. Note what
that implies mechanically: **the ask must be non-blocking by default**, which makes the
answer-return path (EXP-004's Q1) the load-bearing unknown rather than the sending path.

**3. The trigger was an INVESTIGATION RESULT, not a stuckness signal.** Nothing was thrashing. A
sub-agent returned a measurement whose consequence exceeded this session's authority. **No
severity-decay predicate, and no detector reading review-pass residue, would have fired here** —
the same shape as E-2, now twice in three entries.

Two of the three real escalation-worthy moments in this session were invisible to every detector
research 005 characterised. That is a small n, but it is n=2 in the direction of §9.2's unmeasured
recall, and it is direct support for constraint S2: **build the escalation path; treat the detector
as optional and second.**


#### E-3 postscript — what the resolution itself taught

**The count correction, and why it is recorded rather than quietly fixed.** EXP-001 reported *33*
review passes written since the formula landed; the operator measured **27** by
`git log --diff-filter=A`, after first getting *552* from an mtime-based count that was **measuring
their own action** — creating three worktrees that day reset every file's mtime. The two surviving
numbers use different bases: **27 = review passes ADDED TO GIT**; **33 = pass files present in the
working tree**, which includes bundles that were still untracked at the time of measurement. **The
plan states the basis with the number.** The claim — zero pours — is unaffected at either.

*The design lesson is not the arithmetic.* A measurement of a shared tree was corrupted by the
measurer's own concurrent action, and it was caught only because a second party recomputed it on a
different basis. **That is consensus C3 in a form research 005 did not state**: not merely "an
agent's self-report is inadmissible", but *"a measurement taken by a party who is also acting on
the measured surface is suspect."* An escalation carrying a metric must carry **how it was
counted**, not just the count.

**The operator's design question, adopted as a requirement.** Offered as an observation, taken here
as binding:

> The failure mode is not *"an agent forgot to run a check"*. It is *"a mechanism built to remove
> the forgetting was itself left unconnected, and nothing detected that."* If `yf-judgement` ships
> a trigger, **ask what would detect ITS trigger never firing.**

This is the sharpest constraint the plan has received, because **the plan is otherwise on track to
reproduce the exact defect it is citing.** Three instances are now on record — `closable` (never
run), `plan_manager.py audit` (never fired at the phase that mattered), `retrospective_fields.py`
(zero callers), plus #270's formula (zero pours) — and every one was discovered *by hand, late, by
someone who went looking.*

**Recorded as a hard design requirement: `yf-judgement` must be observable in its own absence.** A
trigger whose non-firing is indistinguishable from a quiet period is not shippable, and this is
now a success criterion rather than a nicety. Note it is *cheap* here in a way it was not for the
four cited cases: EXP-001 measured that `review-loop-check` is auditable **only because the script
writes its own echo to `log.md`** — *"an accident of design, not a general property."* Making that
accident deliberate is the whole of the requirement.

### E-4 — who owns correcting research 005 and repairing `finding_recurrence.py`?

| Field | Value |
| :-- | :-- |
| **phase** | INVESTIGATE |
| **question** | "Does plan-059 own correcting `Summary.md` §7.1 and repairing `finding_recurrence.py`, or do those belong to PR #267 — the parent's own branch?" |
| **disposition** | `raised` |
| **predicate** | *Forward* — it changes **scope** *and* proposes writing to **another session's branch**. Neither is settled by approved content. |
| **residue** | EXP-002's measurements, second-party throughout: two named bundles whose own `log.md` records the scope change; a parser-free second instrument disagreeing with the study's own parser 22/43 vs 13/43. |
| **outcome** | **RESOLVED — default confirmed, unchanged.** plan-059 does not edit PR #267; one issue carries both defects; the parser repair is scoped in only if the detector epic survives (it does not). The parent independently re-verified `plan-033`'s `log.md` ordering before forwarding, and posted a correction comment on #269. |

**What this row teaches the design.**

**1. The highest-value escalation in this session carried a NEGATIVE result, and the channel had to
survive that.** E-4 reports that the thing the plan was commissioned to build **does not work as
specified**. Note what makes it sendable: it ships the disconfirming evidence *and* a cheap
constructive alternative (the `log.md` re-scope guard) in the same message. **An escalation
protocol that only carries "I am stuck" will not be used to carry "the premise is wrong"** — which
is the more valuable message and the harder one to send.

**2. The `on_no_answer` field is not a formality — E-4 could not have been sent without it.** With
no answer-return path (EXP-004), the ask is fire-and-forget. E-4's default (*"do not edit your
branch; file one issue; scope the repair only if the detector epic survives"*) is what let the
session state a negative result and **keep working** rather than halt. Recorded as evidence that
`on_no_answer` should be **required**, not optional.

**3. TWO OF THE THREE raised-or-raisable moments came from a SECOND PARTY, not from introspection.**

*An earlier draft of this row said "three of four" and was corrected by red-team pass 1 (C6).* **E-2
does not belong in the numerator** — its own row above reads `disposition: n/a` and states that the
session **could not** have raised it, because it did not hold the fact that made it necessary.
Counting an unraisable event as one a trigger would catch is exactly backwards. The honest figure is
**2 of 3**: E-3 and E-4, both sub-agents returning measurements. **Not one arose from the session
noticing it was stuck.**

**And both are the same event shape, observed twice, in one session, by one author.** That is n=2 of
one kind — too thin to carry a first-class trigger on its own, which is why the plan cites an
independent corpus signal alongside it: EXP-001's `detected_by` census over 81 retrospective
entries, **47 `mechanical-check` / 22 `operator` / 12 `self-report`**, pointing the same way from a
sample this session did not author.

The design consequence stands but is downgraded to a **proposed** trigger with its n stated inline:
*"a second party returned a result whose consequence exceeds this session's authority"*, whose
richest surface in `yf-plan` is a **dispatched sub-agent's returned findings**. Neither #269 nor
#264 lists it.

**A caveat this log must state against itself.** Every *"what this row teaches the design"* block
here is a self-authored, non-blind interpretation by the author of the design it supports, and every
one resolves in favour of that design. That is the defect research 005 names against itself —
*"the label and the discriminator were authored by the same agent with no held-out set."* The
`residue` rows cite second-party artifacts and so satisfy C3 *as a trigger*; the **interpretations
do not, and should be read as hypotheses this session generated, not evidence it gathered.**


#### E-4 postscript — the verification behaviour is the finding

**The parent did not relay the claim; it re-derived it.** Before forwarding, it read `plan-033`'s
`log.md` in order — pass-3 APPROVE → `ready-for-approval` → *"drafting: material re-scope … back to
drafting"* → pass-4 REVISE → pass-5 APPROVE — and reported back a **strengthening** of the finding
this session had not stated: **pass-4 is the first review of a plan that had already been APPROVED
and then re-scoped.**

Three design consequences, and the second is uncomfortable.

**1. The middle hop adds value precisely by NOT being a relay.** REQ-HERDR-024 as written is a
*routing* rule — answer if settled, else forward. It says nothing about **verifying before
forwarding**, and verification is what happened here and what improved the result. Recorded as a
proposed fourth element of the predicate: *look → answer → **verify** → forward.* An escalation
carrying a measurement should be re-derived at the hop that can cheaply re-derive it, because a
claim that survives an independent recomputation is a different object from one that does not.

**2. Both the study and the relaying session had generalised from n=1** — the parent said so of
itself. `plan-026` was treated as *the* re-scoping control when it was **the one bundle whose
reviewer happened to write `medium (blocking)`**. Neither party noticed until a third party read
four more bundles. **The escalation channel did not catch this; a dispatched sub-agent did.** That
is consistent with E-2/E-3/E-4's pattern — **the escalation-worthy facts arrive from second
parties, not from introspection at any level of the chain.**

**3. The operator declined to amend the research bundle, deliberately, and gave a reason worth
inheriting:** *"the bundle is a dated artifact and the corrections are better carried by an issue
that can be tracked than by a silent edit to a merged report."* **A corrected report with no record
of the correction is worse than an uncorrected one with an issue against it** — the same principle
as `recommended` being stored separately from `answer`, and as `writing`'s defaults being destroyed
by their own resolutions. **The escalation schema encodes it: an answer never overwrites the
question.**

### E-5 — stop class 4: authorize a 6th review cycle, or approve without one?

| Field | Value |
| :-- | :-- |
| **phase** | PLAN (review loop) |
| **question** | "Authorize a 6th red-team cycle, or approve on the pass-5 remediation without one?" |
| **disposition** | `raised` |
| **predicate** | *Forward* — a **mechanical counter threshold**, not a judgement call. `review-loop-check` exit 3, `cycles: 5/5`, `escalates: true`, `stop_class: 4`. The only exit is a per-invocation `--max-review-cycles` raise, which is the operator's. |
| **residue** | An exit code, and two verbs the plan depends on: `recheck-criteria` -> verdict FAIL / rc=1, `gate_consistency.py` -> rc=1. Second-party throughout; no self-report anywhere in the trigger. |
| **outcome** | *(pending — session continued fixing without blocking)* |

**What this row teaches the design, and it is the cleanest datum in the log.**

**1. This is the first escalation in the session raised by a MECHANICAL COUNTER rather than by a
second party returning a judgement.** E-2, E-3 and E-4 were all "someone handed me a result whose
consequence exceeded my authority". E-5 is an **exit code**. It fired without anyone noticing
anything, which is exactly the property `yf-judgement`'s trigger design argues for: **the escalation
came from residue, not from the session's assessment of itself.**

**2. It is a live instance of the whole architecture, unrehearsed.** The trigger is a command that
already existed (`review-loop-check`), on an existing invocation path, at a boundary, reading
second-party residue, carrying a recommended default, non-blocking, with the session continuing
under `on_no_answer`. Every element of the Epic 2/3 design ran once, in anger, before any of it was
built. **The one element that did NOT run is the artifact**: this entry is prose in a log, not an
`escalations.md` row — which is precisely the gap Epic 2 exists to close.

**3. The counter fired at the right moment for the wrong-looking reason, and that is worth
recording.** Five review cycles on a *design* plan looks like thrash. It was not: each pass found
defects the previous pass's fixes introduced, and pass 5's own verdict is that the **design was
never in question** — every one of the ~74 concerns across five passes landed in the verification
layer. **Research 005's absence finding 3 — "the agent thrashed" and "the reviewer was slow" leave
identical residue — has a third member: "the reviewers were right five times running."** A
severity-decay detector would have fired on this plan at pass 3 and been **wrong**, which is a
direct, unplanned instance of the false-positive class EXP-002 measured and the strongest available
argument for shipping the escalation path rather than the detector.

### E-5 outcome, and what the whole review arc taught the design

**Outcome: the operator raised the bound to 10 and instructed "review to approval."** Five further
cycles ran; pass 10 returned **APPROVE**. Blockers per pass: **9, 6, 3, 2, 2, 1, 0.**

**1. The recommended default was NOT what happened, and that is the point.** E-5 shipped with
*"if you do not answer I will stop at `ready-for-approval` with the REVISE outstanding."* The
operator answered, and the answer **changed the outcome** — five more cycles, and an APPROVE the
default would never have reached. **A default is what makes the ask cheap; it is not a prediction of
the answer.** An escalation protocol whose defaults are always taken is one whose questions were not
worth asking.

**2. The scoped convergence standard was the single highest-leverage input, and it came from the
operator, not from the loop.** Passes 1–5 ran an open brief and produced 15, 17, 18, 10 and 14
concerns while the plan *grew*. Passes 6–10 ran the operator's five-class blocking standard and
produced 3, 2, 2, 1, 0 while the plan **shrank**. **No amount of additional review cycles would have
produced that; it required a change to the brief, which only the controller could make.** That is
the strongest evidence in this session for the whole premise — *some inputs are structurally
unavailable to the session and must be asked for.*

**3. A detector would have fired on this plan and been wrong.** Ten review cycles, seven REVISE
verdicts, the same concerns re-raised — the exact residue research 005's severity-decay predicate
reads. And **the design was never in doubt**: four passes certified it independently, and every one
of ~90 concerns landed in the verification layer. This is an unplanned, live instance of the
false-positive class EXP-002 measured on `plan-029` and `plan-033`, and it is the strongest argument
available for **shipping the escalation path and refusing the detector** — which is what the plan
does.

**4. The bookkeeping defect recurred three times and is the plan's own thesis turned on itself.**
Pass 4 marked two resolutions `resolved` with no edit made; the `exp-001` banner failed three
anchors before being verified; pass 9 claimed gate 2's Instructions were updated when only its
`Test:` was. **Recording a fix is an obligation; verifying it against the artifact is a command** —
the command-vs-obligation gap, committed by the process that discovered it. The structural answer is
in the plan: Issue 0.1's rule that a `resolved` row must name the changed file, and the widening from
"every criterion" to **"every landed instrument that reads this bundle."**
