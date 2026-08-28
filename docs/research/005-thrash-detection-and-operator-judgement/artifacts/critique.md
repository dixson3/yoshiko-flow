---
type: Research Artifact
description: Red-team critique of Summary.md for yf-research 005 — 30 findings (8
  HIGH, 13 MEDIUM, 9 LOW), a verdict that the headline refutation is overclaimed,
  and an explicit record of the attacks that failed.
okf_spec: OKF-RESEARCH
---

# Red-team critique — 005 `Summary.md`

Read-only adversarial pass. Scope: `Summary.md` (843 lines), checked against `sources.md`,
`artifacts/triangulation.md`, the six cluster artifacts, and — where a number was cheap to
re-measure — the corpus repos themselves. `plan.yaml` was not read.

Counts: **8 HIGH · 13 MEDIUM · 9 LOW.** The attacks that *failed* are recorded in §"Attacks that
did not land" and are as much a part of this report as the ones that landed.

---

## HIGH

### RT-1 — "Refuted" reverses the only cluster that tested the hypothesis, and rests on a proxy the report's own examples show is not a measure of specification

- **Location:** Executive summary, L37–L52; §3.1 table L125; §5 Q2 L291–L298 ("**No.**").
- **Claim as written:** *"**The operator's hypothesis is refuted.** Thrash does not correlate with
  an under-specified objective. The headline prediction — that under-specification is visible in
  the initial objective — is **null: r = −0.002** between initial-objective length and
  direction-change count"*.
- **What is wrong.** Two separable defects.

  (a) *The source graded it the other way.* `cluster-operator-breakthrough-turns.md` §6 — the only
  cluster that adjudicated the hypothesis against a rival table — records:
  `| **Under-specification (the hypothesis)** | **WEAKLY SUPPORTED, and not where predicted** |`,
  on the grounds that specification *density* correlates at r = −0.278 (direction changes) and
  −0.319 (passes), *"a genuine effect and it is in the hypothesised direction."* Triangulation
  softened this to *"not a basis on which to build a detector"* (§3.3). `Summary.md` hardened it
  to "refuted". "Weakly supported" → "not a basis for a detector" → "refuted" is a three-step
  escalation with no new measurement at any step.

  (b) *Word count is not specification.* The measured quantity is the **word length** of the
  Objective paragraph. The report's own two exhibits demonstrate that length is orthogonal to
  specification quality: pybridge `plan-008`'s **9-word** objective converged in one pass
  [527](../sources.md#527), and d3-pxe `plan-016`'s **22-word** objective produced 8 passes
  [530](../sources.md#530). If a 9-word objective can be well-specified and a 22-word one can
  thrash, then r ≈ 0 between length and churn is the *expected* result for a null proxy and
  carries no information about the construct. The report reads a null on the proxy as a null on
  the construct. That is the difference between "the hypothesis is false" and "this measurement
  cannot see it", and §9's twelve absence findings do not contain the latter.
- **What would make it defensible.** Retitle to what was measured — "the hypothesis's headline
  *prediction*, as operationalised by objective word length, is null" — and add to §9: "whether
  under-specification, construed as anything other than objective word length, relates to thrash:
  not measured." Any stronger claim needs a construct-valid specification measure (e.g. blind
  human rating of objective adequacy on a stratified sample) that this study did not build.

### RT-2 — The "initial objective" is post-review text, and the limitation that says so is dropped from the Summary while the headline that depends on it is kept

- **Location:** Executive summary L37–L40; §3.1 L125; §3.2 L146–L148.
- **Claim as written:** L146–148 carries the caveat, but attached to the *wrong* claim:
  *"Neither is a clean pre-work difficulty proxy, because "the first committed `plan.md` is usually
  post-review, not the initial draft" [545]; ρ = 0.601–0.792 bounds it."*
- **What is wrong.** The caveat is applied only to the plan-size correlation. The source cluster
  applies it to the objective measurement, which is where it bites hardest —
  `cluster-operator-breakthrough-turns.md` §9 Limitations: *"**'Initial' objective is really 'first
  committed' objective.** Plans are committed in batches post-review, so the §5 objective
  comparison understates any true pre-work difference."* `sources.md` records the same on every
  `plan-revision`-typed source, including [530](../sources.md#530), the counter-instance:
  *"'initial' is really 'first committed' (post-review in most bundles)"*. `Summary.md` never
  states this about the objective measurement. Grep confirms: `single-coder`, `second rater`,
  `hand-cod` appear zero times in `Summary.md`; `post-review` appears once, at L147.
  The cluster's own resolution — *"This weakens — but does not reverse — the r=−0.002 null"* — is
  itself an unsupported assertion: a measurement taken downstream of the very revision process
  whose cause is under test cannot be argued to be conservative without a comparison to the
  upstream text, which was never recovered.
- **What would make it defensible.** State, at the point the r = −0.002 is first used, that the
  objective text is post-review in most bundles, and mark the null `[uncertain]` on that basis —
  or recover pre-review objectives for a sample and show the null survives.

### RT-3 — §7.2's operating-characteristics table pools three different populations under one stated n, and two of its rows are mutually inconsistent

- **Location:** §7.2, L555–L566.
- **Claim as written:** *"Scored against the hand-audit TRUE label over 79 multi-pass bundles,
  strict `high`, from **n=17 firing / n=20 control**:"* followed by a six-row table containing
  Sensitivity 64%, Specificity 94%, PPV 69%, LR+ ≈ 10.4, **False-positive rate 15% [5–36%]**, Base
  rate 18%.
- **What is wrong.** Four of the six rows do not come from `n=17 firing / n=20 control`.
  Triangulation §4.3's 2×2 over all 79 multi-pass bundles is TP 9 / FP 4 / FN 5 / TN 61 —
  **13 firing bundles, not 17** — and sensitivity, specificity, PPV and LR+ are all computed from
  it. The `n=17/n=20` figures are the recurrence cluster's separate cross-tab (10/17 vs 3/20,
  [180](../sources.md#180)), which is where the FPR row comes from: 3/20 = 15% [5–36%] reproduces
  exactly on Wilson. The consequence is a table in which **specificity 94% and false-positive rate
  15% both appear as properties of the same detector**, when FPR must equal 1 − specificity = 6%.
  Triangulation at least kept them in separate subsections (§4.1/§4.2 vs §4.3); the Summary
  collapses them into one table and one n. A reader cannot reconstruct which number describes
  which population.
- **What would make it defensible.** Split the table by population, label each with its own
  denominator (79 multi-pass / 37 hand-audited), and drop either the FPR row or the specificity
  row — they are the same quantity measured on incompatible samples.

### RT-4 — The headline LR+ of 10.4 and specificity of 94% are stratification artifacts; inside the only stratum the report says the study is about, LR+ is ≈ 3.0

- **Location:** §7.2 L563, L567–L568; against §3.3 L167–L182 and §7.4 L600–L606.
- **Claim as written:** *"The likelihood ratio is good *and* the PPV is tolerable — because
  specificity is 94%, not because the base rate is favourable."*
- **What is wrong.** The 2×2 is computed over all 79 multi-pass bundles, of which **37 have exactly
  two passes and therefore cannot fire the detector by construction** (the predicate is "a HIGH
  finding at pass ≥ 3"). Those 37 are credited as true negatives. The report itself says the
  detector "is silent on 68% of the corpus" (L587) — and then reports a specificity that counts
  that silence as success. The report also says "In substance this is a study of the 22 largest
  plan bundles" (L182, repeated L603). Inside Q4, triangulation §2.3 gives TP 9 / FP 3 / FN 2 /
  TN 8, so sensitivity = 9/11 = 0.818, specificity = 8/11 = 0.727, and **LR+ = 0.818 / 0.273 =
  3.0**, not 10.4. The pooled figure is inflated roughly 3.5× by strata where nothing fires and
  almost nothing is true.
  A second, related suppression: triangulation §4.2 records that *"Among the 37-bundle ≥3-pass set
  it [prevalence] is **38%**"*. `Summary.md` reports only the 18% corpus base rate and asserts the
  PPV is not owed to a favourable base rate. In the population the detector actually acts on, the
  base rate is 38% — more than twice the figure quoted — so the sentence quoted above is false as
  written.
- **What would make it defensible.** Report operating characteristics on the population where the
  detector is evaluable (≥3 passes, ≥1 parsed finding, n = 37) and, separately, within Q4. State
  the 38% prevalence. Delete the "not because the base rate is favourable" clause.

### RT-5 — §6.3's factual premise is false, and is contradicted inside its own sentence

- **Location:** §6.3, L514–L515.
- **Claim as written:** *"55% is **above every similarity value ever measured in this corpus**,
  where the count is a smooth function of the knob with no knee [105] and the single highest score
  (0.600) is a productive-deepening case."*
- **What is wrong.** 0.600 > 0.55. The sentence asserts a maximum and then names a larger value
  eight words later. [170](../sources.md#170) records the episode:
  `plan-010-james-dixson-e049e3 p1->p2 sim=0.600 text_similarity`. §5 of the same report states the
  0.600 figure independently (L408). The error originates in triangulation §6.5 (*"at a threshold
  above every value ever measured here"*) and was carried through verbatim. This is the entire
  premise of "One external mechanism this corpus falsifies": if the corpus contains a value above
  `unloop-mcp`'s threshold, then this corpus does not show the threshold is unreachable — it shows
  the one value that reaches it is a false positive, which is a different and weaker claim.
- **What would make it defensible.** Rewrite as: "exactly one measured value in this corpus exceeds
  55% (0.600), and hand-reading shows it is productive deepening, not a loop — so on this corpus
  the 55% rule's only firing would be a false positive." That claim is supported. The current one
  is not.

### RT-6 — The shippability condition ("strict `high` token") is underspecified in exactly the dimension it declares decisive, and neither reading of it is correct

- **Location:** §7.1, L525–L527 and L547–L551.
- **Claim as written:** *"**Ship the severity-decay detector (D3) only if the severity vocabulary
  is pinned to a strict `high` token** … The strict variant survives — but it survives *by a single
  token in an unnormalised free-text field*, in a corpus where the recorded severity vocabulary
  includes `medium`, `med`, `medium-low`, `low-med` and `high, blocking`"*.
- **What is wrong.** I enumerated every severity-shaped table cell across all 308 `reviews/*.md`
  files in the seven corpus repos. The vocabulary is wider than the report's list in both
  directions, and the two obvious implementations of "a strict `high` token" fail in opposite ways:

  | reading of "strict `high`" | what it wrongly includes | what it wrongly drops |
  | :-- | :-- | :-- |
  | substring / regex `high` | `medium-high` (9 cells), `med-high` (4), `med/high` (1), `medium(→high)` (1) | — |
  | exact string equality `high` | — | `high, blocking` (10), `high, execution-blocking` (1), `high (cross-plan)` (1) |

  The report's own cited source lists the first of these and the report's enumeration omits it:
  [104](../sources.md#104) reads `… medium-low 11 / low-medium 5 / **medium-high 5** / low-med 3 /
  high, blocki 3 …`. Since §7.1 states the condition "decides whether the detector is shippable at
  all", omitting the one variant that defeats the substring reading is not a cosmetic gap.
  Also worth stating: the report cites "severity is not recorded at all on 185 of 1,509 findings"
  [104]; the same source additionally lists `— 14`, `gap 3` and `missing 2`, so the unusable-
  severity count is **204 of 1,509 (13.5%)**, not 185.
- **Partial retraction, in the report's favour.** I checked whether the substring hazard changes
  any verdict on today's corpus. Bundles containing a `medium-high`-family cell are plan-003
  (pybridge), plan-006 (writing), plan-007 (d3-pxe/garage), plan-017 and plan-018 (d3-pxe),
  plan-020, plan-054, plan-056 (yoshiko-flow). Only one has such a cell at pass ≥ 3 —
  d3-pxe `plan-017` pass-3 — and that bundle already fires on an exact `high` in the same file, so
  its classification is unchanged. **The §7.1 verdict survives on this corpus.** The condition as
  *written* is still not sufficient, and would not survive one more repo.
- **What would make it defensible.** State the predicate as a matcher, not a word: e.g. "the
  severity cell, lowercased and stripped, must begin with `high` and must not contain `med`" —
  and show its behaviour on the full measured vocabulary rather than a five-item sample.

### RT-7 — "Task difficulty is the winner" is not compatible with "context exhaustion is untestable in every direction", because they share a proxy

- **Location:** §3.2 heading L137; §5 rival table L304 and L307; §9 item 1 L784–L786.
- **Claim as written:** L304 *"**task difficulty** | **The winner.** Four clusters, all 7 repos.
  Plan size ρ = 0.60–0.79"* alongside L307 *"**context exhaustion** | **Untestable in this corpus,
  in every direction.**"*
- **What is wrong.** Triangulation C2 states the prohibition explicitly: *"Any downstream claim
  that context exhaustion is or is not a cause of thrash is unfounded on this corpus."* Naming a
  *winner* among a set of rivals, one of which is unmeasured, is such a claim — it asserts that the
  unmeasured rival lost. The problem is sharper than a logical technicality, because the winning
  measurement is **`plan.md` byte count**, which is at least as plausible a proxy for context
  pressure (a longer plan and a longer review chain consume more of a session's window) as it is
  for task difficulty. The report never considers that its winner and its untestable rival are
  measured by the same number, and therefore never establishes that "task difficulty" beat
  anything other than "specification measures".
- **What would make it defensible.** Downgrade to what the data support: "plan size and decision
  count explain most of the variance in review-pass volume, and both beat every specification
  measure. Whether that variance is difficulty, context pressure, or both, this corpus cannot say."

### RT-8 — §8's central evidence chain measures where a record lives, not when a question was askable, and grades a compound proposition on its first conjunct alone

- **Location:** §8.2 table rows 1–2, L644–L645; §5 Q3 L328–L333.
- **Claims as written:** L644 *"The dominant thing an operator supplies is a **selection among
  alternatives the agent already drafted**, which an escalation channel is the right shape for |
  **Supported, strongly.**"* and L645 *"That selection **arrives after a draft exists**, so a
  pre-flight interview cannot reach it | **Supported.** 80% of T1 appears inside a
  `reviews/pass-N.md` resolution; only 9% pre-elicited"*.
- **What is wrong.** Three defects, compounding.

  1. *Row 1 is a conjunction graded on one conjunct.* T1 = 45/119 events across all 7 repos
     supports "operators mostly pick among drafted alternatives". It says nothing about whether an
     **N-hop upward-forwarding escalation channel** is the right shape for that. The corpus's own
     mechanism is the opposite of N-hop: a reviewer drafts the fork and the operator resolves it at
     a one-hop review boundary that already exists. §8.6 concedes "The corpus neither tests nor
     contradicts this split" for the carve — the same concession is owed here and is not made.
  2. *The 80% is a location statistic.* It counts where the *answer* is written down. The source
     cluster's limitations say why that cannot bear the weight placed on it:
     *"**Questions are not recorded.** The taxonomy is reverse-engineered from answers [502]."* If
     questions are never recorded, then "80% of answers appear in review passes" is consistent with
     the fork having been askable much earlier and simply not asked. The bridging argument — *"You
     cannot ask 'a or b' before you know that a and b exist"* (L333) — is a logical assertion, not
     a measurement, and it is presented in bold immediately after a measurement, in a position that
     invites it to be read as one.
  3. *The denominators are single-coder judgement calls and the Summary never says so.* The cluster
     records: *"The 119 events were classified by me, single-coder, no second rater"*; *"The
     178→119 filter is judgement … a different filter yields different denominators."* `Summary.md`
     uses 45/119, 38%, 80% and 9% at four separate load-bearing points and never mentions either.
- **What would make it defensible.** Split row 1 into its two propositions and grade the second
  "untested". Restate the 80% as "80% of *recorded* T1 resolutions are recorded inside a review
  pass; questions are not recorded anywhere in this corpus, so this bounds where answers land, not
  when they became askable." Carry the single-coder caveat.

---

## MEDIUM

### RT-9 — A null on constraint count is reported as a refutation, with no significance test, and treated asymmetrically against a residual of similar magnitude

- **Location:** §3.1 table L128; Executive summary L57–L59.
- **Claim as written:** *"| stated **constraint count** predicts less churn | ρ = **+0.088 to
  +0.170** — the wrong sign | **refuted** |"*
- **What is wrong.** At n = 109 neither value is distinguishable from zero (ρ = 0.088 → p ≈ 0.36;
  ρ = 0.170 → p ≈ 0.08). No interval or p-value is given for either. A correlation that cannot be
  distinguished from zero refutes nothing; it is a null, and it should be labelled one. The
  asymmetry is the sharper problem: the same report keeps a **partial** ρ of −0.19/−0.24 as the
  "one qualified survivor" that is "real and is not being zeroed out to tidy the verdict" (L57),
  while discarding a raw ρ of +0.17 — *larger in magnitude* — as evidence of a wrong sign. Two
  coefficients of comparable size are given opposite epistemic treatment because they point in
  opposite directions.
- **What would make it defensible.** Label the row `null` and attach intervals to both figures. If
  the +0.17 is retained as meaningful, retain it symmetrically.

### RT-10 — A caveat that survives in the executive summary is dropped at the two most quotable places, and the prediction table contradicts the paragraph beneath it

- **Location:** §3.1 table L126 and the paragraph at L130–L135; §5 Q2 L293–L295.
- **Claim as written:** L126 *"| **pre-eliciting** the missing specification reduces churn | 1.43
  vs 1.42 direction changes; **3.05 vs 2.42** review passes (pre-elicited group worse) | **null /
  wrong direction** |"* — followed five lines later by *"The result is therefore *not* evidence that
  pre-elicitation harms — it is evidence that **pre-elicitation's benefit is not visible above the
  size effect**, which is the weaker but honest claim."*
- **What is wrong.** "Wrong direction" and "not evidence that pre-elicitation harms" cannot both
  stand; the table verdict is the one that will be quoted. Separately, triangulation §7.6 lists
  this finding in the **uncertified, one-cluster, self-declared-confounded** bucket. The executive
  summary carries the confound note (L44–L45); the prediction table (L126) and the Q2 answer
  (L293–L295) do not. No dispersion statistic, interval or test accompanies 3.05 vs 2.42 anywhere.
- **What would make it defensible.** Change the table verdict to `null (confounded, uncertified)`
  and give the two group means an interval or a test.

### RT-11 — Jaccard is the wrong statistic for the sets compared, and the "near-zero convergence" headline is largely an arithmetic consequence of two surfaces with near-zero sensitivity

- **Location:** §4 heading and Executive summary L65–L73; §4.2 table L226–L229.
- **Claim as written:** *"Jaccard between the text-similarity and git-churn nomination sets is
  **0.091** (2 bundles) … Convergent nomination by unrelated surfaces is the strongest evidence
  this design could have produced and **it does not exist in this corpus.**"*
- **What is wrong.** The two sets are of size 19 and 5. The **maximum attainable Jaccard is
  5/19 = 0.263**, so 0.091 is 35% of the ceiling, not 9% of anything meaningful; Jaccard is
  dominated by the size mismatch. The overlap coefficient — the right statistic for nested-scale
  sets — is 2/5 = **0.40**. Against chance: with 19 and 5 nominations over 114 bundles, expected
  overlap is 19 × 5 / 114 ≈ 0.83; observed is 2. For hand-audit TRUE (14) ∩ churn (5), expected is
  0.61 and observed is 1 — literally chance. So the honest reading is "the git surface nominates
  almost nothing and the telemetry surface nominates nothing, so convergence is *unobservable*, not
  *absent*." Triangulation says exactly this and the Summary drops the sentence: *"The three
  surfaces are not measuring the same thing. Whether that is because two of them are blind or
  because the phenomenon is only visible in one, this corpus cannot say."* Dropping it converts a
  "cannot say" into the report's second headline ("it is also negative", L65).
- **What would make it defensible.** Report the overlap coefficient and a chance baseline alongside
  Jaccard; restore triangulation's blindness/absence disjunction; and reframe §4 as "two of three
  surfaces have near-zero sensitivity, so this design could not have produced convergent evidence"
  rather than "convergent evidence does not exist".

### RT-12 — §3.4 counts two reads of the same artifact type as two independent surfaces, in a report whose central axis is surface independence

- **Location:** §3.4, L186–L198.
- **Claim as written:** *"Certified across three independent surfaces (review text, cross-repo
  read, commit messages)"*.
- **What is wrong.** The "cross-repo read" evidence is [208](../sources.md#208) —
  `Incubator/ansible/plans/plan-002/reviews/pass-2.md:24` — and [205](../sources.md#205) —
  `rc-files plan-004/reviews/pass-2.md`. Both are `reviews/pass-N.md` files, i.e. the *same
  surface* the recurrence cluster reads, examined by a different agent in different repos. That is
  a second reader, not a second surface. Only [408](../sources.md#408) (a commit body) is a genuine
  second surface. The distinction matters because §4 makes surface independence the study's whole
  evidentiary yardstick and counts exactly three surfaces (review text, git, telemetry); §3.4
  silently uses a different and looser definition to reach "three".
- **What would make it defensible.** Say "two independent surfaces (review-pass prose, commit
  messages), with cross-repo replication on the first."

### RT-13 — C3's local evidence base is misdescribed: one source's band is wrong and the other is not a self-report at all

- **Location:** §8.3, L659–L673.
- **Claim as written:** *"the *local* support is STRONG-band and directly measured — a `log.md`
  entry recording "operator approved" that was **false when written** [501], and `bd history`
  returning 641 duplicate `closed` snapshots for a bead last semantically touched two days earlier
  [303]. **The finding rests on the local evidence**"*.
- **What is wrong.** Two errors. (a) `sources.md` records
  [501](../sources.md#501) as **MODERATE** (total 68), not STRONG; only [303] is STRONG (82). The
  "STRONG-band" attribution to the pair is false against the study's own register. (b) [303] is a
  Dolt/`bd history` **export artifact** — duplicate commit snapshots emitted by unrelated batch
  commits. It demonstrates that a *tool's history view* is unreliable. It does not demonstrate
  anything about an *agent's self-assessment of progress*, which is what C3 asserts. Strip it and
  the local base for "the agent's own progress self-report is not admissible evidence" is
  [501] alone — n = 1, MODERATE — with a T4 single-incident blog [614] doing the conceptual work.
  The report's own sentence "the blog corroborates the reasoning, not the result" is then backwards:
  on this evidence the blog is carrying the result.
- **What would make it defensible.** Correct the band; drop [303] from C3 (it belongs to C6, where
  it already appears); and state the local base as n = 1.

### RT-14 — The amplification analogy is contradicted by the report's own measurement of the same bundle

- **Location:** §8.5, L752–L760.
- **Claim as written:** *"**7 of those are one bundle (`plan-050`) raising `max-review-cycles` seven
  separate times** [513]. That is a single unresolved situation being re-escalated to the operator
  seven times through a channel with no budget and no dedup, in a bundle that also contains eight
  empty cosmetic review rounds [180]."*
- **What is wrong.** Those two facts are not additive — they are the same fact, and it points the
  other way. Reading `plan-050`'s `log.md` directly, the seven raises occur at `cycles=` 4, 9, 9, 9,
  10, 11, 12. Six of the seven fall at cycle ≥ 9, i.e. **inside the eight rounds the report itself
  measures as carrying zero findings** (§7.1 L542–L543: *"passes 6–13 are eight empty cosmetic
  rounds"*). What was re-escalated was therefore a *ceremonial loop bound* permitting more empty
  bookkeeping rounds — not one unresolved question re-asked seven times. The log lines also read
  `raised to N for this invocation`, an autonomy setting, and per [501] "operator" attributions in
  `log.md` are measurably fallible. The report calls this analogy *"close enough to act on"*, so it
  is load-bearing rather than decorative — and it does not survive the report's own data.
- **What would make it defensible.** Either drop the analogy and state the budget requirement as a
  pure design requirement (which §8.5's first paragraph already does adequately), or replace it
  with an instance where a *substantive* question was re-escalated.

### RT-15 — The named counter-instance is confounded by two rivals the report itself endorses on the same bundle

- **Location:** §3.1 table L127; Executive summary L46–L47; §5 Q2 L295–L296.
- **Claim as written:** *"a well-specified objective produces a short review cycle | d3-pxe
  `plan-016`: 22-word SPEC-anchored objective → **8 passes, 6 operator decisions** [530] |
  **counter-instance**"*.
- **What is wrong.** `plan-016` is also the report's exemplar for two rivals: the missing-capability
  rival — [533](../sources.md#533), *"HALTED at the 'SPEC amendment approved' and 'AWS + 1Password
  write authority' capability gates — neither resolved. 22 open tasks remain, all gate-blocked"* —
  and genuine domain underdetermination — [531](../sources.md#531)/[532](../sources.md#532), a fork
  settled by `exp-007` and re-settled a pass later. If `plan-016`'s eight passes are explained by
  blocked capability gates and by forks that could not be posed until a measurement ran, then the
  bundle is not evidence that *good specification fails to prevent churn*; it is evidence that
  *other causes dominate on this bundle*, which is compatible with the hypothesis being merely one
  cause among several. A counter-instance that three explanations fit equally does not discriminate.
- **What would make it defensible.** Use a counter-instance not already claimed by a rival, or
  state explicitly that the single named counter-instance is confounded and carries no
  discriminating weight (it is already `[uncertain]`, WEAK-band, n = 1).

### RT-16 — The §2 blockquote is misattributed, its internal arithmetic disagrees with the source it cites, and the per-repo rates beneath it cite a source that does not contain them

- **Location:** §2, L106–L112.
- **Claim as written:** *"> "**Every one of the 8 candidate episodes lives in exactly 3 of the 7
  repos** … and **6 of the 8 are in the two highest-volume software repos**" [201]"*, followed by
  seven per-repo 3-or-more-pass rates also cited to [201].
- **What is wrong.** [201](../sources.md#201)'s recorded quote is a tool output:
  `total_recurrence_matches: 8 (yoshiko-flow 4, d3-pxe 3, writing 1; …)`. The blockquoted prose is
  from `cluster-herdr-repo-interrogation.md:231`, not from [201]. Worse, the prose disagrees with
  the tool output it rests on: yoshiko-flow 4 + d3-pxe 3 = **7 of 8** in the two highest-volume
  software repos, not 6. And none of the per-repo pass-count rates (13/19, 23/56, 2/11, 2/11, 1/9,
  1/4, 0/4) appear in [201], which is about recurrence matches, not pass counts.
  *In the report's favour:* I recomputed those seven rates directly from the corpus and every one
  reproduces (see "Attacks that did not land"). The numbers are right; the citation is wrong and the
  quoted "6 of the 8" is wrong.
- **What would make it defensible.** Cite the cluster artifact for the prose and [103] (or a new
  source id) for the pass rates; fix "6 of the 8" to "7 of the 8".

### RT-17 — Every operator-taxonomy statistic in §5 Q3 and §8 is single-coder, and the Summary never says so

- **Location:** §5 Q3, L311–L333; §8.2 L644–L645; §8.5.
- **What is wrong.** See RT-8(3). Listed separately because it applies beyond §8: 45/119 (38%),
  the "only category present in all seven repos", 36/45 (80%), 4/45 (9%), the T1–T9 taxonomy
  itself, and the T6 count of 18 are all products of one agent's hand-classification of a
  judgement-selected 119-of-178 subset, with no second rater and no inter-rater statistic. Under
  the study's own evidence standard this is a material qualifier on every number derived from it.
- **What would make it defensible.** One sentence at the head of §5 Q3, carried into §8.2.

### RT-18 — A corpus-wide claim rests on a single `low`-severity finding in a single bundle, and is then used three times as a premise

- **Location:** §8.4 item 1 L718–L719; §8.4 closing L738–L739; §9 item 4 L792–L794.
- **Claim as written:** *"**The corpus records answers, and almost never questions** [502]. The cost
  of an ask is not observable because asks are not recorded."*
- **What is wrong.** [502](../sources.md#502) is one table row from one review pass:
  `| C13 | low | The three operator decisions D-5/D-6/D-7 have **no recorded question** — no
  scope-answers.md …`. It is a `low`-severity self-observation about *three decisions in one plan*.
  No corpus-wide count of recorded-vs-unrecorded questions is cited anywhere in the report. The
  claim may well be true — the operator cluster asserts it in its limitations — but as cited it is
  an n = 1 observation carrying a 114-bundle universal, and it is the load-bearing premise for
  §8.4's "untestable" verdict and for §9's absence finding 4.
- **What would make it defensible.** Either count it (a grep for question-recording artifacts across
  114 bundles is cheap) or state it as the cluster's assertion rather than a measurement.

### RT-19 — Two rivals are separated from the hypothesis by definitional fiat, and both lose their corpus-level counts in transit

- **Location:** §5 rival table L305–L306.
- **Claims as written:** *"missing tool / permission / authority | Real and measured: 22 tasks
  stalled on unresolved human gates [533] … Pre-elicitable as an environmental fact, not as a
  specification"*; *"genuine domain underdetermination | Real: a fork "was not well-posed until an
  experiment ran" [531], and the same fork re-opened one pass later [532]"*.
- **What is wrong.** (a) The separation of "missing permission" from "under-specification" is
  asserted, not measured — a missing, unstated environmental precondition is a species of
  under-specification under most readings of the hypothesis, and no measurement in the study
  distinguishes them. (b) The cluster's corpus-level counts are dropped: *"13/114 bundles carry
  gate-blocked residue"* becomes one bundle's 22 tasks, and *"6 bundles record a fork settled by
  measurement, not by argument"* becomes two quotes from the same bundle (`plan-016`, again). The
  effect is to shrink both rivals to single-bundle anecdotes while "task difficulty" retains its
  four-cluster, seven-repo framing.
- **What would make it defensible.** Restore 13/114 and n = 6, and say plainly that the
  missing-permission/under-specification boundary is a definitional choice this corpus does not
  adjudicate.

### RT-20 — The shippability test was run against one hand-picked negative control, and the four measured false positives were never examined for the same shape

- **Location:** §7.1, L529–L537.
- **Claim as written:** *"**A detector that fires on `plan-026` is not shippable.**"*
- **What is wrong.** The strict-`high` variant "passes" a test consisting of a single bundle chosen
  because it exhibits the re-scoping shape. Triangulation §4.1 names three control bundles that
  **do** fire under strict `high` — `yoshiko-flow/plan-033`, `d3-pxe/plan-017`, `d3-pxe/plan-011` —
  and §4.3's 2×2 has four false positives. None is examined for whether it is also a re-scoping
  shape, which is the only thing the plan-026 test was designed to detect. The test therefore
  establishes that the detector does not fire on the one control it was tuned against.
- **What would make it defensible.** Hand-read the four strict-`high` false positives against the
  same criterion and report the result. That is roughly an hour of work and it is the difference
  between a test and an anecdote.

### RT-21 — An absence over six web queries is stated as a universal and graded "Supported"

- **Location:** Secondary Q1 L391–L396; §8.2 row 3 L646.
- **Claim as written:** *"**The strongest prior-art finding is an absence.** Every publicly
  discoverable "ask before acting" skill … is **opt-in and pre-task**; none auto-fires mid-execution
  from residue."* and, in §8.2, *"A mid-execution escalation is a **genuine gap in prior art**, not
  a solved problem | **Supported.**"*
- **What is wrong.** Triangulation §7.6 classifies this as `1 cluster, an absence over 6 queries`
  and lists it among findings "carried but not certified". "Every publicly discoverable" is a
  universal quantifier over a search space; six queries bound it very loosely. In §8.2 it is graded
  "Supported" with no tag, in a table whose other rows carry explicit "Untestable" and "no N-hop
  data" qualifiers — so the reader is given no signal that this row is the weakest of the four
  "Supported" ones.
- **What would make it defensible.** State the search extent inline ("an absence over six queries,
  one cluster, uncertified") and downgrade the §8.2 grade to "Supported, weakly (absence over a
  small search)".

---

## LOW

### RT-22 — "No plateau" is contradicted by the cited sweep

- **Location:** Secondary Q2 L413–L414; §6.2 L495.
- **Claim:** *"matches fall from 40 to 3 with no plateau or knee between 0.20 and 0.70 [105]"*.
- **Wrong because:** [105](../sources.md#105) records 40, 23, 12, 8, 4, **4**, 3 at thresholds 0.20,
  0.25, 0.30, 0.35, 0.45, 0.55, 0.70. The count is identical at 0.45 and 0.55 — a plateau, at the
  exact region `unloop-mcp`'s 55% threshold lives in. Fix: "falls monotonically with only a
  two-point plateau at 0.45–0.55, and no knee."

### RT-23 — "62% finish in ≤2 passes" does not match the census

- **Location:** §7.3 item 3, L588.
- **Wrong because:** [103](../sources.md#103)'s distribution is `0:5 1:30 2:37 …`, so bundles
  finishing in ≤2 passes = 72/114 = **63.2%**. (Inherited from triangulation §4.5.) The companion
  figures — 42/114 = 37%, 72 never reaching pass 3, "silent on 68%" and "true denominator 32%" —
  all reproduce exactly.

### RT-24 — Citation-scope drift: five aggregate claims cite an exemplar source

- **Locations and mismatches:**

  | claim (line) | cited | what the source actually contains |
  | :-- | :-- | :-- |
  | "0 literal `git revert` commits **of 2,044**" (L247) | [407] | 407 gives the per-repo revert counts; the 2,044 denominator is [423]'s merge/total tally |
  | "4 genuine hand-authored semantic reverts, **all** outside every tracked plan window" (L249–250) | [411] | one commit (evri_py `db41594`) |
  | "0 of 20 hand-audited retouches"; "5 of 20 … contaminated" (L228, L250) | [416] | one window (7 commits touching `yf/src/coverage.rs`) |
  | "Within Q4, PPV 17% [3–56%], sensitivity 9%" (L493) | [182] | corpus-wide monotonicity tallies, no Q4 stratification |
  | "22-word … objective → **8 passes, 6 operator decisions**" (L127) | [530] | the objective text only |

  None of these numbers appears to be *wrong* — they are traceable to the cluster artifacts and to
  triangulation. The citation points at an instance where the reader needs the aggregate.

### RT-25 — One `[uncertain]` tag missing, and one uncited assertion

- **Location:** §3.1 table L127; §5 Q3 L345.
- **Wrong because:** the report's own rule (L18–L19) is that claims resting on a WEAK local source
  carry `[uncertain]`. [530] is WEAK-band and is tagged at L47 and L296 but **not** at L127, the
  prediction-table row where it does the most work. Separately, L345's *"T7 intent"* is listed among
  the pre-elicitable categories with no citation, unlike T4 [520], T5 [522] and T9 [543] beside it.
  Otherwise tagging discipline is good — I checked every citation in the report against its recorded
  band and found no other miss.

### RT-26 — A source whose entire retrieved content is its own title is cited as supplying an ontology

- **Location:** Secondary Q1 L382–L384.
- **Claim:** *"the W6H interrogative ordering [619]"*, presented alongside [618] as one of "the
  strongest portable ontologies".
- **Wrong because:** [619](../sources.md#619)'s recorded quote is the paper's title and nothing
  else (DOI link, no body retrieved). Nothing about what W6H *is* or *orders* was actually read.
  [618] by contrast carries a substantive quote and supports its claim.

### RT-27 — Unusable-severity count understated

Covered under RT-6: 185 → 204 of 1,509 once `— 14`, `gap 3` and `missing 2` are included.
(§7.1 L549–L550, §7.2 L572–L573.)

### RT-28 — "Explains most of the variance" is not supported at the stated lower bound

- **Location:** Executive summary L48–L49.
- **Wrong because:** the report gives ρ = 0.601–0.792. At ρ = 0.601, ρ² = 0.36 — a minority of
  rank-variance, and Spearman ρ² is not "variance explained" in the ordinary sense in any case.
  "Explains most of the variance" holds only at the top of the stated range.

### RT-29 — D1's statistics come from two different implementations and the two precision comparisons are on different populations, unsignposted

- **Location:** §5 Q1 L283–L287; §6.1 L477–L486; §7.3 L593–L598.
- **Wrong because:** the earliness figure ("39% of all D1 signals fire there (21 of 54)") is the
  cluster's implementation; the PPV ("TP 10, FP 8, FN 4 → 56%") is triangulation's reimplementation
  (53 signals / 18 bundles). Neither location says which. And L286 says the two detectors' precision
  is *"indistinguishable (73% vs 75%)"* while L597 says buying a pass of earliness *"costs 13 points
  of PPV"* — the first is within-Q4, the second corpus-wide, and the report never tells the reader
  they are different populations.

### RT-30 — The label's circularity is disclosed for D7 but not for the weaker circularity that affects every scored signal

- **Location:** §4.4, L258–L265.
- **Claim:** *"**D7 therefore cannot be scored against this label at all**, and every other signal
  is scored against a D7-filtered ground truth."*
- **Wrong because:** the disclosure is accurate as far as it goes and is one of the report's better
  moments — but it names only the *filtering*. The stronger fact is that the hand-audit labels and
  the discriminator definitions (D1, D3, D6, D9) were produced by the **same cluster agent**, with
  no second rater and no held-out set. Triangulation reimplemented D1's *code* independently, which
  removes implementation circularity but not label circularity: it is still scored against labels
  authored by the party that proposed the signal. Every performance number in §6.1 and §7.2 is
  therefore trained-and-evaluated in the same hands. Fix: name it in §4.4 alongside the D7 point.

---

## Attacks that did not land

Reported because a failed attack is a result.

1. **Wilson intervals.** I recomputed roughly twenty of them — 42/114, 14/79, 24/40, 7/40, 9/40,
   9/14, 61/65, 9/13, 9/12, 8/11, 1/6, 1/11, 4/19, 4/60, 5/114, 3/20, 4/8, 9/14, 9/15, 7/14, 9/10,
   and all seven per-repo rates. **Every one reproduces to the stated rounding.** The interval
   arithmetic in this report is clean.
2. **The corpus census.** I re-enumerated `reviews/*.md` across all seven repos independently of
   `corpus_scan.py`. At HEAD I count 308 review files against the report's 301 — the difference is
   entirely `plan-056` (3 new passes) and two later `plan-055` passes, all created after the scan
   date. Per-repo 3-or-more-pass counts reproduce exactly: d3-pxe 13/19, yoshiko-flow 23/56,
   pybridge 2/11, writing 2/11, evri_py 1/9, rc-files 1/4, emacs.d 0/4; multi-pass total 79; the
   quartile n's (19/19/19/22) sum to 79; the pass-band table (30/37/23/19) sums to 114 with the five
   zero-pass bundles. **The worktree-double-count correction in §2 is real and the corrected census
   is sound.**
3. **The `plan-026` shippability exhibit.** I read `plan-026/reviews/pass-6.md` directly. The
   finding is verbatim as quoted — `**C1 — the de-list list misses ≥3 in-repo references —
   severity: medium (blocking).**` — and the file's own header confirms the framing:
   *"delta review of the one change since pass-5 APPROVE"*. The exhibit is accurate.
4. **The per-pass HIGH trajectories.** `plan-048` 7,6,4,1,2,0,0 · `plan-054` 8,6,4,2,2,0 ·
   `plan-055` 5,8,2,1,1,1,0 · `plan-054` findings 22,14,8 · `plan-050` findings 5,4,11,17,14 then
   eight zeros — all match [180](../sources.md#180) verbatim.
5. **The `medium-high` hazard does not currently flip a verdict.** See RT-6's partial retraction. I
   expected this to break the §7.1 conclusion and it does not.
6. **`[uncertain]` tagging.** I checked every one of the 71 distinct citations against its recorded
   band. Exactly one WEAK-band use is untagged (RT-25). Discipline here is better than the norm.
7. **The circularity disclosure itself** (§4.4) is honest, prominent, and correctly excludes D7 from
   scoring. My complaint (RT-30) is that it stops one step short, not that it is absent.
8. **Internal consistency of the 2×2.** Given triangulation §4.3's own cell counts, sensitivity,
   specificity, PPV and LR+ are all arithmetically correct. The problem (RT-3, RT-4) is the
   population they are computed over, not the algebra.

---

## Verdict on the headline refutation

**Overclaimed — in a specific and correctable way, not fabricated.**

What is sound and survives every attack I made: the measurement is reproducible; the census it rests
on is correct; `r = −0.002` between objective word length and direction-change count is a real null;
plan size and issue count dominate every specification measure that was computed; and the study is
unusually honest about its own label circularity, its stratification, and its inability to test
context exhaustion.

What is overclaimed is the **inference layer sitting on top of that measurement**, and it is
overclaimed at three joints:

1. **Construct.** Objective *word length* is not under-specification, and the report's own two
   exhibits (a 9-word objective that converged, a 22-word one that thrashed) demonstrate the two are
   orthogonal. A null on a null proxy licenses no verdict on the construct (RT-1).
2. **Instrument.** The text measured is post-review in most bundles — a fact `sources.md` records on
   the very source used as the counter-instance, and which `Summary.md` states once, attached to a
   different claim (RT-2).
3. **Grammar.** The report moves between "the hypothesis is false" and "this corpus cannot see it"
   without marking the transition. §9 lists twelve things this corpus cannot answer; "whether
   under-specification, construed as anything but objective length, relates to thrash" is not among
   them, and it should be the thirteenth.

The correctly-scoped claim — *"the hypothesis's headline prediction, as this study operationalised
it, is null; specification density shows a weak effect that is mostly a `1/length` artifact; and
task difficulty dominates every specification measure computed here"* — is fully supported and is
already present in the report's own §3.2 and §3.3. The word "refuted" in the first line of the
executive summary is doing work the evidence beneath it does not do.

One symmetry worth stating, since this critique was commissioned partly to check for
over-refutation: the report does **not** over-refute uniformly. It preserves the −0.19/−0.24
residual against its own narrative interest, states the plan-050 reconciliation without choosing a
side, and reports D1's precision loss even though D1 is the signal with the better latency story.
The defect is concentrated in the framing sentences — the executive summary, the §3.1 verdict
column, the §5 Q2 "**No.**", and the §8.2 grades — not in the body measurements.
