---
type: Research Artifact
description: Retrieval cluster operator-breakthrough-turns — what class of operator-supplied
  information ended a plan episode, whether it was elicitable before the burn, and
  a control group of episodes that converged with no evidenced operator turn
okf_spec: OKF-RESEARCH
---

# Cluster: operator-breakthrough-turns

Primary Q3: **When an episode DID break, what broke it — and can that class be elicited by a
question asked BEFORE the burn?**

## 0. Epistemic frame — everything below is RESIDUE

Research 004's boundary is this cluster's starting constraint, and it is load-bearing rather than
decorative. **No conversational turn is observable anywhere in this corpus.** What is observable
is a *record written by an agent* asserting that an operator did something — a `log.md` line, a
review-resolution cell, a `plan.md` decision row. Every "the operator said X" below is an
**inference from an agent's own claim**, not an observation.

That inference is demonstrably fallible in this corpus. d3-pxe plan-016's `log.md` carries a
self-correction:

> "CORRECTION: this transition was performed by the subordinate execute-session agent, not by an
> operator, and was originally logged as 'operator approved' — which was false at the time it was
> written." [501]

So one measured instance exists where the residue **asserted an operator turn that did not
happen**. Treat every count below as an upper bound on real operator turns, and read the whole
report as *what the artifacts claim*, not *what occurred*.

A second, sharper limit was found by a red-team pass rather than by me. yoshiko-flow plan-053's
pass-1 concern C13 states:

> "The three operator decisions D-5/D-6/D-7 have **no recorded question** — no `scope-answers.md`.
> Substance is independently corroborated by findings, but the framing cannot be audited" [502]

**The corpus records ANSWERS and almost never records QUESTIONS.** That is the single most
consequential fact for a project trying to derive a *question* taxonomy from it. Everything in §3
is reverse-engineered from an answer's shape.

## 1. Evidence-surface census

Measured by `scripts/corpus_scan.py --json` on 2026-08-28 [545] (the corrected, worktree-excluded
baseline; `plan.yaml`'s `corpus:` block is superseded per `artifacts/tooling-notes.md`).

| repo | bundles | plan.md | context.md | log.md | index.md | review passes |
| :-- | --: | --: | --: | --: | --: | --: |
| yoshiko-flow | 56 | 56 | 56 | 27 | 26 | 166 |
| d3-pxe | 19 | 19 | 19 | 14 | 14 | 73 |
| evri_py | 9 | 9 | 8 | 1 | 1 | 13 |
| writing | 11 | 11 | 11 | 0 | 0 | 18 |
| pybridge | 11 | 11 | 10 | 0 | 0 | 20 |
| emacs.d | 4 | 4 | 4 | 0 | 0 | 4 |
| rc-files | 4 | 4 | 4 | 1 | 1 | 7 |
| **total** | **114** | **114** | **112** | **43** | **42** | **301** |

**The surface is thicker than the brief feared, but the thickness is in the WRONG place.**

- `context.md`: **112/114 (98%)** — near-universal.
- `log.md`: **43/114 (38%)** — only yoshiko-flow and d3-pxe adopted it; `writing`, `pybridge` and
  `emacs.d` have **zero**. This is an OKF-era artifact, so its absence is chronological, not
  meaningful.
- **The phase log, however, is 113/114 (99%)** once you look for it in *both* places: pre-OKF
  bundles carry it inline in `plan.md` as a `**Phase log:**` block; OKF bundles moved it to
  `log.md`. Any analysis that reads only `log.md` sees 38% of the corpus and will conclude the
  surface is thin. It is not.
- `plan.md` git revisions are a **weak** direction-change proxy: median 4 revisions per bundle in
  yoshiko-flow, **2 in `writing`**, **1.5 in `emacs.d`**. Plans are drafted in-session and
  committed in batches, so the first committed `plan.md` is usually *post-review*, not the initial
  draft (verified: plan-050's first commit `fb79b44` already contains decision D-6, "dropped on
  evidence" — a post-investigation outcome). **The phase log, not git, is the mid-flight record.**

### Direction-change prevalence

Scanning all 113 phase logs for direction-change markers (re-scope / descope / split / widen /
reverse / abandon / supersede / drop / amend / vN / cycle N / escalate / override):

| repo | bundles | with a direction-change marker | % |
| :-- | --: | --: | --: |
| yoshiko-flow | 56 | 32 | 57% |
| d3-pxe | 19 | 13 | 68% |
| evri_py | 9 | 6 | 67% |
| writing | 11 | 3 | 27% |
| pybridge | 11 | 6 | 55% |
| emacs.d | 4 | 2 | 50% |
| rc-files | 4 | 2 | 50% |
| **total** | **114** | **64** | **56%** |

## 2. Direction-change catalogue

From the 114 bundles I extracted every line in a `reviews/pass-N.md` or a phase log asserting an
operator **act** (chose / decided / ruled / directed / relaxed / overrode / escalated / authorized
/ rescoped / requested), excluding routine `approved: operator approved` boilerplate and excluding
*design mentions* of operator approval (a plan describing a feature that requires operator consent
is not an operator turn). That yields **178 candidate statements**, of which **119** are
substantive operator-information events after hand-coding; the rest are boilerplate approvals or
design prose.

Split by source: **97 in review passes, 81 in phase logs.**

## 3. Inductive taxonomy

Categories derived from the content of the 119 events, not from the brief's five starting words.
Where the brief's guess maps, I say so; where it does not, I replaced it.

| id | category | n | repos present | maps to brief's guess? |
| :-- | :-- | --: | :-- | :-- |
| **T1** | **Fork resolution** — the agent or reviewer had already enumerated ≥2 concrete alternatives and could not rank them; the operator picked one | **45** | **all 7** | *no* — not "constraint/priority/exclusion"; it is **selection among options the agent authored** |
| T2 | Scope subtraction — cut, defer, or split | 17 | yf 14, d3-pxe 1, evri_py 2 | ≈ "exclusion" |
| T6 | Process / loop-bound override — raise the review-cycle bound, narrow the next pass, change the resolution method | 18 | yf 17, d3-pxe 1 | *no* — absent from the brief's list entirely |
| T3 | Scope addition — fold in, widen, post-approval add | 10 | yf 6, d3-pxe 1, writing 2, rc-files 1 | *no* |
| T5 | Authority / capability grant — a permission or a real-world act only the operator can perform | 10 | d3-pxe 4, yf 2, evri_py 2, writing 1, pybridge 1 | ≈ "authority" |
| T4 | Risk-tolerance setting — accept a flagged risk, relax a constraint | 4 | yf/d3-pxe/writing/pybridge 1 each | ≈ "priority" |
| T7 | Goal / intent statement ("the operator wants X") | 10 bundles | yf 4, d3-pxe 3, pybridge/emacs.d/rc-files 1 each | ≈ "intent" |
| T8 | Environmental / authority fact (who the operator is, what they may do, what exists) | 110 bundles | all 7 | ≈ "constraint" |
| T9 | Taste — a preference with no derivable criterion | 1–3 | rc-files, emacs.d | *no* |
| **T0** | **Fork SURFACED but not resolved** — the reviewer escalates a decision and the record shows no answer yet [535][536][537] | **9** | d3-pxe 3, pybridge 3, writing 2, yf 1 | n/a — this is the *question*, not the answer |
| **—** | **RESIDUAL — fits nothing** | **5** | yf 3, d3-pxe 2 | — |

### The residual bucket, itemised (this is not a rounding error)

1. **A decision made on information that did not yet exist.** plan-039 pass-1: *"operator selected
   all four fixes — but that selection was made **before** EXP-001 existed."* [503] An operator
   turn that was later **invalidated by measurement**. It is neither a good decision nor a bad one;
   it is a decision taken at the wrong time.
2. **A review overturning an operator decision.** plan-040 pass-1: *"**Note on process.** C6 changed
   an operator decision: the original ensure-label-before-use choice"* [504] — the arrow runs
   backwards from the hypothesis's assumption.
3. **The un-auditable decision** — plan-053 C13 [502], above.
4. **The mis-attributed decision** — d3-pxe plan-016 [501], above.
5. **The content-free record**: d3-pxe plan-009 pass-1 logs a whole concern's resolution as
   *"| C7  | Operator decision — see below. | resolved |"* [505]. Something was decided; the
   artifact does not say what.

**Four of the five residuals are failures of the RECORD, not of the decision.** For a skill that
wants to ask better questions, that is a finding in itself: the corpus's weakest link is not the
operator's judgement but the capture of it.

### T1 is the headline, and it is cross-domain

45 of 119 events (38%) are fork resolutions, and **T1 is the only category present in all seven
repos**, including the two non-software, low-ceremony ones. The shape is identical across domains:

- yoshiko-flow: *"Operator confirmed **split apply mode** — K1 (token cuts) auto-applies; K2"* [506]
- d3-pxe: *"**Accepted — operator decision: raise to 90 days.** `NoncurrentDays: 90` … The property
  is restated as a **bounded window, not an unbounded claim**"* [507]
- pybridge: *"Leg C: pull floor-lowering in (R1 b) vs measurement-gate-only (R1 a) | high | Operator
  chose **option (a)** (2026-06-21)"* [508]
- emacs.d: *"| C4 (auth posture) | Operator chose per-session bearer token in v1 (D7); 127.0.0.1 +
  Origin as defense-in-depth."* [509]
- rc-files: *"Operator chose brew on both platforms. Entry moved to `Brewfile.common`; Linux vendor
  path, the symlinks.sh platform branch, the old Issue 1.3 and old SC9 all deleted"* [510]
- writing: *"Split vs bundle: **resolved** — operator chose bundle; conditionality removes
  ship-coupling."* [511]
- evri_py: *"Operator chose option C (hybrid: file upstream + proceed Epic 4 + hold chain)."* [512]

**T6, by contrast, is a ceremony artifact.** 17 of 18 loop-overrides are yoshiko-flow, and 7 of
those are one bundle (plan-050) raising `max-review-cycles` seven separate times [513]. The same bundle
also shows the operator changing the *resolution method* [538] and *narrowing a review pass's scope* [539]
— two moves that are not plan edits at all. There is no
T6 event in `writing`, `pybridge`, `evri_py` or `emacs.d` — because those repos have no review-cycle
bound to override. T6 is real, and it is the *purest* thrash-breaking turn in the corpus, but it is
a property of yf-plan's own machinery, not of operator judgement in general.

## 4. Elicitability: could a pre-flight question have got this?

**The decisive measurement.** Of the 45 T1 fork resolutions, **36 (80%) appear inside a
`reviews/pass-N.md` resolution** — i.e. they answer a fork that an **independent red-team pass
discovered in a plan that already existed**. Only **4 (9%)** are recorded as pre-elicited at
scoping [514][515][516]; the remaining 5 are approval-time answers to questions the plan itself
had drafted (see the `writing` pattern below).

| category | pre-elicitable? | drafted pre-flight question | adversarial verdict |
| :-- | :-- | :-- | :-- |
| **T1 fork resolution** | **MOSTLY NO** | "Where two designs are both defensible, which do you prefer?" | **Unaskable in advance in 80% of instances.** You cannot ask "a or b" before you know a and b exist. plan-039 [503] is the measured proof of the failure mode: the operator *was* asked early, chose all four fixes, and the choice was invalidated when EXP-001 ran. Asking early does not merely fail to help — it can inject a wrong commitment. |
| **T2 scope subtraction** | **PARTIALLY** | "What is explicitly out of scope? What would you cut first if this turns out to be twice the size?" | The second half is genuinely pre-elicitable — a *cut-order preference*, not a cut decision. But the corpus's biggest subtractions (plan-050's D-9 SPLIT at review cycle 5 [517], plan-047's D-13, plan-055's D-14 [518]) were taken *on measured non-convergence evidence that did not exist at scoping*. A pre-flight question can capture the **policy**, never the **trigger**. |
| **T3 scope addition** | **NO** | — | Additions are reactions to things discovered during the work (d3-pxe plan-011: *"re-opened: adding Epic 5 Postgres observability (operator request) — fingerprint invalidated, re-review required"* [519]; yoshiko-flow plan-019 adds scope *after approval* [541]; rc-files amends mid-execution [540]). Nothing to ask. |
| **T4 risk tolerance** | **YES — highest value per question** | "For each risk this plan surfaces, is the default 'refuse' or 'proceed and record'? Name one thing you will NOT accept." | The one category where the answer is a **standing disposition**, stable before the work. `writing` plan-002's *"operator relaxed C1 (staging-draft visibility accepted; production is the line)"* [520] is exactly a policy that could have been stated on day one. d3-pxe plan-017's *"operator relaxed the 'no public DNS, no public hostname' scoping constraint"* [521] shows the same: the constraint was recorded up front and the relaxation was a later amendment to a *known* line. |
| **T5 authority / capability** | **YES** | "Which of these do you personally hold, and will you exercise them: cloud write, secret provisioning, upstream push, merge-to-main, SPEC amendment?" | Already effectively solved: d3-pxe pre-declares its human gates and then logs *"**OPERATOR AUTHORIZATIONS RECORDED (2026-08-18).** All five remaining human gates"* [522]. Note the failure mode this prevents: pybridge plan-003's *"Tri-Platform Green gate resolved by OPERATOR OVERRIDE"* [523] — the gate was correct and the environment was broken; only the operator could say "override, it is not our defect." |
| **T6 loop override** | **STRUCTURALLY NO** | — | The information is "you have now burned N cycles and are not converging". It does not exist at t=0. **Cannot go in a pre-flight taxonomy.** It belongs in a *detector*, not a questionnaire. |
| **T7 goal / intent** | **YES** | "In one sentence, what does 'done' look like from where you sit?" | Already pre-elicited in all 10 instances — every "the operator wants X" sits in a Motivation section written at scoping [542]. This category is already solved by the existing template. |
| **T8 environmental / authority fact** | **YES — already solved by a FORM, not a question** | — | **110/114 bundles (96%)** carry it, because `context.md` has a slot for it [544]. The corpus's most successful pre-elicitation is a template field. |
| **T9 taste** | **YES, cheaply** | "Is there a look/feel/naming preference I should not guess at?" | emacs.d's sepia/parchment palette [543] and rc-files' `org.gnu.emacs` label are trivially askable and trivially unguessable. Low frequency, near-zero cost. |
| **T0 unresolved fork** | n/a | — | 9 instances where the reviewer surfaced a fork and the record shows no answer [535][536][537]. These are the *questions* the corpus generated but never captured as questions. |

### The corpus already invented the pre-flight question — in `writing`

The single best prior art is not in yoshiko-flow. `writing` plan-005 contains a section literally
titled:

> "**Operator decisions to confirm at approval** (defaults in brackets):
> - **D1 — spin-outs as new incubators vs PARTIAL. RESOLVED (2026-07-01): create both as new
>   incubators** …
> - **D2 — optional minor pieces. RESOLVED (2026-07-01): create both** …
> - **D3 — the client T6 (maturity framework). ACCEPTED:** seed the *concept* only" [524]

and its phase log resolves all three in one line: *"approved: operator approved; D1=both new,
D2=both, D3=seed-only"* [525]. `writing` plan-010 does the same, and its pass-1 marks two concerns
`resolved (pending operator choice)` [526].

This is the **question-with-a-default** pattern: the agent drafts the fork, proposes a default,
batches them, and resolves the whole set at one approval boundary. It is not a pre-flight question
— it fires *after* drafting — but it is the cheapest possible operator turn, and `writing` reached
single-pass APPROVE on both plans that used it. **It is the pattern a `yf-judgement` taxonomy should
generalise, and it argues for a mid-flight batching gate rather than a pre-flight questionnaire.**

## 5. CONTROL GROUP — episodes that converged with no evidenced operator turn

**Definition.** No direction-change marker in the phase log, at least one review pass, terminal
verdict `APPROVE`. **n = 32** (of 114). Treatment (≥1 direction-change marker) n = 64. Per repo:
yoshiko-flow T32/C23, d3-pxe T13/C6, writing T3/C8, pybridge T6/C4, evri_py T6/C2, emacs.d T2/C2,
rc-files T2/C1.

### The comparison, honestly

| measure | treatment (n=64) | control (n=49) | verdict |
| :-- | --: | --: | :-- |
| median review passes | 2.0 | 2.0 | no difference |
| mean review passes | 3.19 | 2.11 | treatment higher |
| **median objective length (words, first committed `plan.md`)** | **57** | **53** | **no difference** |
| mean objective length | 87.0 | 83.8 | no difference |
| median distinct `Issue N.M` in plan | **16** | **12** | treatment bigger |
| median epics | 5 | 4 | treatment bigger |
| median first-commit `plan.md` size (chars) | **22,687** | **18,155** | treatment bigger |
| has an explicit "Out of scope" section | **73%** | **51%** | **treatment MORE specified** |
| has a "Scoping/Operator decisions" section | **25%** | **16%** | **treatment MORE specified** |
| median specification density (bold-bullet constraints per 1k chars) | **0.51** | **0.72** | control denser |

Correlations across all 113 bundles with recoverable initial text:

| predictor | r with direction-change count | r with review-pass count |
| :-- | --: | --: |
| distinct issues in plan | **+0.433** | **+0.554** |
| initial `plan.md` size | +0.376 | +0.591 |
| epics | +0.321 | +0.393 |
| specification density | −0.278 | −0.319 |
| **initial objective length** | **−0.002** | **+0.069** |

### What the control group actually had

Not a tighter objective. Reading them, controls are **small, single-artifact, well-trodden**:

- pybridge plan-008 (1 pass, APPROVE, **9-word objective**): *"Investigate and fix #31:
  testArrayTransferMultiDim 2D ndarray transfer failure"* [527]
- d3-pxe plan-004 (2 passes): *"Add CalibreWeb ebook LXC guest fronted by a Caddy reverse proxy
  (Let's Encrypt via Route53 DNS-01) on pve"* [528] — 18 words, and it is the fourth plan in that
  repo to follow the same LXC-plus-Caddy recipe.
- rc-files plan-003 (2 passes): *"Tailscale proxy container for SSH/RDP into a client tailnet
  (EVRInet) without leaving my own tailnet"* [529] — 15 words.

But the **treatment** group contains equally short, equally concrete objectives that thrashed:

- d3-pxe plan-016 (**8 review passes**, 6 direction-change markers): *"Implement the PVE-STO-005
  backup tier (#51): Sanoid ZFS snapshots for the precious config/DB datasets plus scheduled Restic
  replication off-host to Amazon S3"* [530] — **22 words**, a named SPEC requirement, a named issue,
  named technologies. By any reading this is a *well-specified* objective. It generated six
  operator decisions and an eight-pass review chain.

**Verdict on the operator's hypothesis, item 5 of the brief:** the under-specification signal is
**NOT visible in the initial objective text**. r = −0.002. The control group's objectives are not
longer, not shorter, not more constrained. What separates the groups is **how many independent
decisions the work contains** (issues, r = +0.43), not how well the goal was stated.

### The natural experiment, and it is a null

40 of 114 bundles record a *pre-elicited* operator scoping decision (a `scoping: operator decisions
locked` phase entry or a `Scope decisions (operator-confirmed)` section). If pre-elicitation
prevented thrash, these should be quieter. They are not:

| group | n | median passes | mean passes | mean direction-change markers |
| :-- | --: | --: | --: | --: |
| pre-elicited scoping decisions | 40 | 2.0 | **3.05** | **1.43** |
| none recorded | 74 | 2.0 | **2.42** | **1.42** |

Identical on direction changes; the pre-elicited group has *more* review passes. Confounded (harder
plans get formal scoping sections), and I cannot deconfound it with this evidence. But it is not the
result the hypothesis predicts, and I am reporting it as it came out.

## 6. Rival explanations

| rival | can this evidence separate it? | what was measured |
| :-- | :-- | :-- |
| **Task difficulty / decision count** | **YES, and it wins** | Issue count is the strongest predictor of both direction changes (r=+0.43) and review passes (r=+0.55) — stronger than any specification measure. |
| **Genuine domain underdetermination** | **YES, and it is real** | 6 bundles record a fork **settled by measurement, not by argument**. d3-pxe plan-016 pass-4: *"**Accepted in part, and SETTLED BY MEASUREMENT — exp-007** … Operator decision: `--group-by host,paths`"* [531]; pass-5 re-measures and changes the answer again [532]. These forks were **not well-posed before the experiment ran** — no pre-flight question could have reached them. |
| **Missing tool / permission / capability** | **PARTIALLY** | 13/114 bundles carry gate-blocked residue; d3-pxe plan-016 logs *"HALTED at the 'SPEC amendment approved' and 'AWS + 1Password write authority' capability gates — neither resolved. 22 open tasks remain, all gate-blocked."* [533] evri_py plan-002 pivoted wholesale because *"client cannot yet provision EVRI_PY_DISPATCH_TOKEN (operator is a repo guest, not org member)"* [534]. This is a **distinct, pre-elicitable** cause (it maps to T5) and it is **not** under-specification. |
| **Context exhaustion** | **NO — total blindness** | A corpus-wide scan found **3 apparent hits, all false positives** (a SKILL.md token budget, not a session context window). The artifact surface records **nothing** about context exhaustion. This rival cannot be tested here at all, and any claim that it is not a cause would be unfounded. |
| **Under-specification (the hypothesis)** | **WEAKLY SUPPORTED, and not where predicted** | The only supporting signal is specification *density* (r=−0.28 with direction changes, −0.32 with passes) — denser plans churn less. That is a genuine effect and it is in the hypothesised direction. But it is weaker than the size effect, it is partly a `1/length` artifact, and the hypothesis's own headline prediction — visible in the initial objective — is **flatly null** (r=−0.002). |

## 7. Per-repo: does it hold outside yoshiko-flow?

| finding | yf | d3-pxe | evri_py | writing | pybridge | emacs.d | rc-files | holds cross-domain? |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| T1 fork resolution present | 22 | 8 | 2 | 4 | 4 | 3 | 2 | **YES — all 7** |
| T5 authority grant present | 2 | 4 | 2 | 1 | 1 | 0 | 0 | mostly (5/7) |
| T2 scope subtraction | 14 | 1 | 2 | 0 | 0 | 0 | 0 | **NO — yf-concentrated** |
| T6 loop-bound override | 17 | 1 | 0 | 0 | 0 | 0 | 0 | **NO — yf ceremony artifact** |
| T8 environment fact in `context.md` | 55 | 19 | 7 | 11 | 10 | 4 | 4 | **YES — 110/114** |
| question-with-default pattern | rare | rare | — | **plan-005, plan-010** | — | — | — | **best specimen is `writing`** |
| direction-change rate | 57% | 68% | 67% | **27%** | 55% | 50% | 50% | `writing` is the outlier — lowest churn |

The two non-software repos are the strongest evidence for T1's generality: emacs.d's operator turns
are design forks (session-id scheme, auth posture) [509], and rc-files' are packaging forks (brew on
both platforms) [510] — structurally identical to d3-pxe's retention-policy fork [507] and
pybridge's option-(a)/(b) fork [508]. The **selection** shape is domain-independent.

`writing` has the **lowest** direction-change rate (27%) and 8 of its 11 bundles are controls. It is
also the repo that invented the question-with-default section. I cannot prove causation from n=11.

## 8. What this says for a `yf-judgement` question taxonomy

1. **A pre-flight questionnaire cannot reach the dominant category.** T1 is 38% of all events and
   80% of it arrives after a draft exists and a reviewer has found the fork. Asking early does not
   just fail — plan-039 [503] measured it *injecting a commitment that measurement then invalidated*.
2. **Four categories are genuinely pre-elicitable and worth asking**: T4 risk tolerance (highest
   value — a standing disposition), T5 authority/capability (already partly solved by capability
   gates), T7 intent (already solved by Motivation), T9 taste (cheap, unguessable).
3. **T8 is already solved by a FORM, not a question** — 96% coverage via `context.md`'s slots.
   Where a template field works, a question is the wrong instrument.
4. **T6 is a DETECTOR, not a question** [513][538][539]. "You have burned 5 cycles and reproduction is falling" is
   not knowable at t=0. It belongs to the thrash-detection half of research 005.
5. **The corpus's own best answer is a mid-flight batching gate**, not a pre-flight interview:
   `writing`'s "Operator decisions to confirm at approval (defaults in brackets)" [524] — agent
   drafts the fork, proposes a default, batches, resolves at one boundary.
6. **Capture the question, not only the answer.** plan-053's C13 [502] is the corpus complaining
   about itself. Four of five residual events are record failures. A taxonomy is unfalsifiable if
   nothing writes down what was asked.

## 9. Limitations

- **No conversational turn was observed.** Everything is an agent's claim about an operator, and
  [501] proves that claim can be false.
- **Questions are not recorded.** The taxonomy is reverse-engineered from answers [502].
- **Hand-coding.** The 119 events were classified by me, single-coder, no second rater. T1/T2
  boundaries are genuinely fuzzy (a fork whose options are "cut it" and "keep it" is both).
- **The 178→119 filter is judgement.** I excluded routine approvals and design prose describing
  operator-consent features; a different filter yields different denominators.
- **"Initial" objective is really "first committed" objective.** Plans are committed in batches
  post-review, so the §5 objective comparison understates any true pre-work difference. This
  weakens — but does not reverse — the r=−0.002 null, since the *committed* text is the more
  developed one and still shows nothing.
- **Confounding is not controlled.** Bigger plans get both more scoping ceremony and more thrash;
  the §5 natural experiment cannot separate them.
- **Context exhaustion is invisible** (§6). One named rival is entirely untestable here.
- **n is small outside two repos.** emacs.d (4) and rc-files (4) carry the cross-domain claim on
  very few bundles.
- **Self-reference.** 56 of 114 bundles are yoshiko-flow fixing yoshiko-flow, and T2/T6 are
  yf-concentrated. Pooled counts over-represent one repo's ceremony; per-repo tables in §7 are the
  ones to read.
