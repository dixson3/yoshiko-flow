---
type: Reference
okf_spec: OKF-PLAN
---

# Research 005 — the passages this plan reasons from (vendored extract)

**Why this file exists.** `plan-059`'s Approach cites `yf-research` 005 throughout, but that bundle
is **not present on this branch or on `main`** — it lives on the unmerged branch
`research/005-thrash-detection` (PR **#267**). A cold reader following a bare path reference would
get nothing, and every §7/§8/§9 citation would be unresolvable. Red-team pass 1 raised this as C12.

**Provenance.** Recovered verbatim with
`git show research/005-thrash-detection:docs/research/005-thrash-detection-and-operator-judgement/Summary.md`
at plan-authoring time (2026-08-28). The full report is 1,249 lines with 228 cited sources; only the
sections this plan's reasoning depends on are reproduced.

> **The corrections this plan makes to these passages are NOT applied here.** The extract is
> verbatim, deliberately — see `findings/exp-002-severity-vocabulary-census.md` for the refutation
> of §7.1's shippability claim and the parse defect underlying §7.2's operating characteristics.
> Per operator decision at escalation E-4, the research bundle stays as landed and the corrections
> are carried by an issue rather than by a silent edit to a merged report.

---

## 7. Recommendation for `yf-judgement`

### 7.1 The detector recommendation, with its condition in the sentence

**Ship the severity-decay detector (D3) only if the severity predicate is an EXACT match on the
lowercased, stripped severity cell against the literal string `high` — not a substring or regex
search for `high`, and not any normaliser that folds `blocking` into HIGH.** The condition is not a
caveat — it decides whether the detector is shippable at all, so it is stated as an implementable
predicate rather than as a word.

**Why exact-match, and why the distinction is not pedantic.** The recorded severity vocabulary is
free text and wider than a five-item sample suggests. A **substring** reading of "a strict `high`
token" silently admits `medium-high` (5 cells in the census [104](sources.md#104), 9 by a direct
re-enumeration of the 308 `reviews/*.md` files at HEAD), plus `med-high` (4), `med/high` (1) and
`medium(→high)` (1) — the exact class of downgraded-severity cell the detector must not treat as
HIGH. Exact-match excludes all of them. It also excludes `high, blocking` (10), `high,
execution-blocking` (1) and `high (cross-plan)` (1), which is a deliberate and conservative cost:
the strict variant's whole purpose is to be the *narrow* reading.

**The verdict below survives on today's corpus, and that guarantee is corpus-dated.** Bundles
containing a `medium-high`-family cell are pybridge plan-003, writing plan-006, d3-pxe/garage
plan-007, d3-pxe plan-017 and plan-018, and yoshiko-flow plan-020, plan-054 and plan-056. **Only one
has such a cell at pass ≥ 3** — d3-pxe plan-017 pass-3 — and that bundle already fires on an exact
`high` in the same file, so no classification changes. **Rechecking this enumeration is a
prerequisite of any deployment against data collected after 2026-08-28**; the substring hazard is
latent, not extinct.

The evidence, measured on the two named bundles (`artifacts/triangulation.md` §4.4):

- **`plan-026`** — 7 passes, APPROVE/REVISE oscillation driven by deliberate re-scoping, **zero
  recurrence**. Under strict `high` it does **not** fire. Under a normaliser folding `blocking` into
  HIGH it **does** — on `pass-6.md`'s finding *"C1 — the de-list list misses ≥3 in-repo references —
  severity: medium (blocking)"*, a **medium** finding a reviewer marked merge-blocking, in a
  **delta review of one refactor since a pass-5 APPROVE** [181](sources.md#181). That is the purest
  possible instance of the re-scoping shape the test exists to protect. **A detector that fires on
  `plan-026` is not shippable.**
- **`plan-050`** — 13 passes, fires under **both** normalisers, and is a **true positive**.
  Triangulation resolved a self-contradiction inside the recurrence cluster to establish this: the
  same artifact listed `plan-050` as a control shape in §5 while auditing two of its episodes as
  TRUE in §3 [133](sources.md#133). The measurement reconciles them without choosing — passes 1–5
  carry all 51 findings and all 11 HIGH findings and two hand-verified TRUE recurrences; **passes
  6–13 are eight empty cosmetic rounds** [180](sources.md#180). The pass count is inflated; the
  content is a genuine 5-pass recurrence episode, and D3 fires at pass 3, before the cosmetic rounds
  were written. **The "plan-050 is a control" framing must not be carried forward.**

**The shippability test is one hand-picked negative control, and its scope should be stated.**
`plan-026` was chosen precisely because it exhibits the re-scoping shape, so passing it establishes
that the detector does not fire on the one control it was tuned against — not that it is free of
that shape generally. Three *other* control bundles do fire under strict `high` —
`yoshiko-flow/plan-033`, `d3-pxe/plan-017`, `d3-pxe/plan-011` (`artifacts/triangulation.md` §4.1) —
and the 2×2 in §7.2 carries four false positives. **None of them was hand-read against the
re-scoping criterion.** Doing so is roughly an hour of work and is the difference between a test and
an anecdote; until it is done, "passes the shippability test" means "passes on `plan-026`".

The strict variant survives — but it survives *by a single token in an unnormalised free-text
field*, in a corpus where the recorded severity vocabulary includes `medium`, `med`, `medium-low`,
`low-med`, `medium-high` and `high, blocking`, and where **severity is unusable on 204 of 1,509
findings (13.5%)** — 185 recorded as none, plus `— 14`, `gap 3` and `missing 2`
[104](sources.md#104). (An earlier draft gave 185; the three residual unusable tokens were
omitted.) **Pinning the vocabulary is the prerequisite deliverable; the detector is downstream of
it.**

### 7.2 Operating characteristics — on the population that can actually fire the detector

An earlier draft of this section presented six statistics under a single stated n of "17 firing /
20 control". **That was wrong in two ways and both are corrected here.** Four of the six came from a
2×2 over all 79 multi-pass bundles with **13** firing, not 17; the 17/20 figures are a separate
cross-tab [180](sources.md#180). The consequence was a table in which specificity 94% and a
false-positive rate of 15% appeared as properties of the same detector, when FPR must equal
1 − specificity. Each table below now comes from exactly one population, with its own denominator.

**Table A — pooled over all 79 multi-pass bundles** (`artifacts/triangulation.md` §4.3; TP 9 / FP 4
/ FN 5 / TN 61). **This is the flattering table and it should not be used for a shipping
decision**, for the reason stated beneath it.

| statistic | value (n=79) |
| :-- | :-- |
| Sensitivity | 64% [39–84%] |
| Specificity | 94% [85–98%] |
| PPV | 69% [42–87%] |
| False-positive rate (= 1 − specificity) | 6% [2–15%] |
| Likelihood ratio+ | ≈ 10.4 |
| Base rate (TRUE among multi-pass) | 18% [11–28%] |

**Why Table A overstates the detector.** The predicate is "a HIGH finding at pass ≥ 3". **37 of the
79 bundles have exactly two passes and cannot fire it by construction** — and every one of them is
credited as a true negative. This report states elsewhere that the detector "is silent on 68% of the
corpus" (§7.3); Table A counts that silence as success. The pooled specificity and the pooled LR+
are therefore stratification artifacts.

**Table B — the evaluable population: ≥3 passes with ≥1 parsed finding, n=37.** The same 2×2 cells,
with the 37 non-evaluable two-pass bundles removed from the TN cell (all 14 TRUE-labelled bundles
lie inside this stratum, which is why triangulation §4.2 records its prevalence as 38%): TP 9 / FP 4
/ FN 5 / TN 19.

| statistic | value (n=37) |
| :-- | :-- |
| Sensitivity | 64% [39–84%] |
| Specificity | **83% [63–93%]** |
| PPV | 69% [42–87%] |
| False-positive rate | 17% [7–37%] |
| Likelihood ratio+ | **≈ 3.7** |
| Base rate (TRUE among the evaluable set) | **38% [24–54%]** |

**Table C — within Q4, the stratum this study is in substance about** (n=22;
`artifacts/triangulation.md` §2.3: TP 9 / FP 3 / FN 2 / TN 8).

| statistic | value (n=22) |
| :-- | :-- |
| Sensitivity | 82% [52–95%] |
| Specificity | **73% [43–90%]** |
| PPV | 75% [47–91%] |
| False-positive rate | 27% [10–57%] |
| Likelihood ratio+ | **≈ 3.0** |
| Base rate (TRUE within Q4) | 50% [31–69%] |

**The separate 17/20 cross-tab, kept apart.** The recurrence cluster's own contrast — a HIGH finding
at pass ≥3 in **10 of 17 (59% [36–78%])** recurrence-fired bundles vs **3 of 20 (15% [5–36%])**
controls [180](sources.md#180) — is a *different* sample from Tables A–C (its denominators are the
cluster's firing/control split, not the hand-audit label over the multi-pass set). It is reported
here on its own and is **not** combined with any row above; the 15% is that cross-tab's control
firing rate, not this detector's false-positive rate.

**Tables B and C are the honest ones for a shipping decision**, because a detector is only ever
consulted where it can speak. On those populations the likelihood ratio is **≈ 3.0–3.7, not 10.4** —
the pooled figure is inflated roughly threefold by strata where nothing fires and almost nothing is
true.

**The base-rate sentence is corrected.** An earlier draft said the PPV is tolerable "because
specificity is 94%, not because the base rate is favourable". That is false as written: in the
population the detector acts on, the base rate is **38%** (and 50% inside Q4), more than twice the
18% corpus figure previously quoted. **A favourable base rate is doing much of the work.** With
specificity at 83% (Table B) rather than 94%, the PPV of 69% is largely a consequence of testing on
a stratum where more than a third of bundles are positive.

**And the PPV interval still runs to 42%, below a coin flip. At this n the detector cannot be
distinguished from one that is wrong more often than it is right.** Four further caveats can each
reverse it: the label is D7-derived so the FP count is a floor and the FN count is unknown; the
label and the discriminator were authored by the same agent with no held-out set (§4.4); **8
multi-pass bundles extract zero findings** and are invisible to the detector by construction
[105](sources.md#105); and the severity vocabulary is unnormalised [104](sources.md#104).

Report it as a candidate. Never as a characterised instrument.

### 7.3 The operational envelope — state these three numbers next to the proposal

1. **First computable at pass 3.** The predicate is "a HIGH-severity finding survives into pass 3 or
   later"; it cannot be evaluated before a third pass file exists.
2. **It cannot prevent a 3-pass burn.** By the time it can speak, three adversarial review passes
   have been written — and in the firing group those are where most of the work is: `plan-054`
   carries 22, 14, 8 findings in passes 1–3; `plan-053` carries 14, 15, 14
   [180](sources.md#180). What it *can* prevent is passes 4 through N, and N reaches 6, 7, 8 and 13
   here: `plan-048` runs HIGH 7,6,4,1,2,0,0; `plan-054` 8,6,4,2,2,0; `plan-055` 5,8,2,1,1,1,0
   [180](sources.md#180), against controls reaching zero by pass 2–3 [181](sources.md#181).
3. **It is silent on 68% of the corpus.** Only **42 of 114 bundles reach pass 3 at all — 37%
   [29–46%]** [103](sources.md#103); 72 never do, and **63% finish in ≤2 passes** (5 + 30 + 37 =
   72 of 114 = 63.2% [54–71%] on the pass-count distribution [103](sources.md#103); an earlier
   draft rounded this to 62%). Only 37 of the 42
   extract any parseable finding, so the true denominator is **32% of the corpus**. A detector that
   speaks only about the third of the corpus already in trouble is a **triage** instrument, not an
   early-warning one.

**The alternative on latency, reported honestly.** D1 is available at **pass 2**, one pass earlier,
with 39% of its signals firing there [183](sources.md#183). But its corrected precision is **PPV 56%
[34–75%]**, and it fires on `plan-041`, `plan-042` and `plan-043` — the three textbook convergence
controls in the recurrence cluster's own control section [181](sources.md#181),
[183](sources.md#183). **Buying one pass of earliness costs 13 points of PPV — corpus-wide, 56% vs
69% — and three known false alarms on clean plans.** Within Q4 the two are indistinguishable (73%
vs 75%); the trade-off above is the corpus-wide comparison, not the Q4 one.

### 7.4 The scope limit

Stratified by plan size, D3 fires **0%, 0%, 11%, 55%** across quartiles and the hand-audit TRUE
label runs **5%, 0%, 11%, 50%**. **In substance this is a study of the 22 largest bundles**, which
is why §7.2's Table C is reported alongside the pooled figures. The
detectors are untested below roughly 42 KB of `plan.md` because there is nothing there to test them
on, and **no frequency claim generalises past yoshiko-flow and d3-pxe** — four of seven repos have
3-or-more-pass-rate intervals wider than 40 percentage points [213](sources.md#213).

### 7.5 What to do instead of, or before, shipping a detector

- **Pin the severity vocabulary.** It is a prerequisite for D3 and independently valuable.
- **Install the D2 reproduction-rate instrument** in the review template. It is the only
  size-immune measurement in the corpus, and it currently exists in 6 bundles of 114
  [188](sources.md#188) because one reviewer chose to compute it.
- **Fix the two open telemetry defects** [319](sources.md#319) — every duration, latency and
  concurrency question is blocked on them.
- **Prefer forms over questions where a form works.** `context.md`'s environmental slots already
  capture the T8 class in 110 of 114 bundles [544](sources.md#544) `[uncertain]` (WEAK-band).

---

## 8. Assessment of the escalation-architecture proposal

**This section assesses OPERATOR-SUPPLIED INPUT, filed as `yoshiko-flow#264` with a follow-up
comment. It is not a triangulated finding and nothing in the corpus proposed it.** It is stated here
as given, then tested against the evidence above.

### 8.1 The proposal, as supplied

`yf-herdr` already seeds `YF_PARENT_PANE`, establishing an **upstream controller chain terminating
at the human**. `REQ-HERDR-024` is already the escalation predicate at one hop: *the parent shall
answer only when the question is settled by existing approved plan content; anything changing scope,
risk or a success criterion shall go to the operator.* Generalised to N hops this becomes an
**intent-resolution protocol** — each controller answers if its own content settles the question,
else forwards upward. The carve: **`yf-herdr` owns the CHANNEL; `yf-judgement` owns the DECISION to
ask and what to ask.**

### 8.2 Verdict

**Supported in shape; unsupported in magnitude; and its central cost claim is untestable from this
corpus.** More precisely:

| proposition | verdict on this evidence |
| :-- | :-- |
| The dominant thing an operator supplies is a **selection among alternatives the agent already drafted** | **Supported, strongly** — with the single-coder qualifier (§5 Q3). T1 = 45 of 119 events, the only category in all 7 repos [506](sources.md#506)–[512](sources.md#512) |
| …and an **N-hop upward-forwarding escalation channel** is the right shape for supplying it | **Untested.** T1's prevalence says nothing about channel topology, and the corpus's own mechanism is one-hop: a reviewer drafts the fork and the operator resolves it at a review boundary that already exists. The corpus neither tests nor contradicts the N-hop generalisation |
| That selection is **recorded after a draft exists** | **Supported as a location statistic.** 80% of *recorded* T1 resolutions sit inside a `reviews/pass-N.md` [514](sources.md#514); only 9% are recorded as pre-elicited. **Questions are not recorded anywhere in this corpus** [502](sources.md#502), so this bounds where answers land, not when they became askable |
| A mid-execution escalation is a **genuine gap in prior art**, not a solved problem | **Supported, weakly — an absence over six queries, one cluster, uncertified** (`artifacts/triangulation.md` §7.6). Every "ask before acting" skill this study reached is opt-in and pre-task [601](sources.md#601), [621](sources.md#621) |
| The **trigger** must not be the agent's self-report of stuckness | **Supported, and it constrains who may escalate.** See §8.3 |
| A cheap ask **dominates** an automatic trigger because a wrong ask costs one question and a wrong autonomous fix costs a review cycle | **Untestable from this corpus.** See §8.4 |
| An N-hop chain needs a propagation budget and dedup | **A design requirement the evidence implies, but the corpus contains no N-hop data.** See §8.5 |

### 8.3 Where the evidence actively supports it

**The detector it would replace is weak on exactly the axes the proposal names.** D3 is
pass-3-limited, silent on 68% of the corpus, vocabulary-fragile to the point where one token decides
shippability, and carries PPV 69% [42–87%]. An architecture that makes "ask upstream" cheap and
legitimate does not need a high-precision autonomous trigger, and that is a real advantage over the
instrument this study actually characterised.

**Who may trigger an escalation is constrained by a certified finding.** Consensus C3, four
clusters: the agent's own progress self-report is not admissible evidence.

> "We trusted the model's self-assessment. This is the deep one. … A drifting agent's self-report
> drifts with it. Asking a stuck agent whether it's stuck is asking the unreliable narrator to
> review their own reliability." [614](sources.md#614) `[uncertain]` (T4-practitioner, n=1)

The tier asymmetry matters and triangulation names it: [614](sources.md#614) is a T4 single-incident
blog. **The local evidence base is thinner than an earlier draft of this section stated, and the
correction cuts against the finding.** That draft described the local support as "STRONG-band" and
cited two items; both attributions were wrong.

- [501](sources.md#501) — a `log.md` entry recording "operator approved" that was **false when
  written** — is **MODERATE** (total 68) in this study's own register, not STRONG. It is directly on
  point and it is **n = 1**.
- [303](sources.md#303) — `bd history` returning 641 duplicate `closed` snapshots — is STRONG (82)
  but is a **Dolt export artifact**: duplicate commit snapshots emitted by unrelated batch commits.
  It shows a *tool's history view* is unreliable, which is a claim about instrumentation, not about
  an **agent's self-assessment of progress**. It is dropped from C3 here; it belongs to C6, where it
  already appears (§4.3).

**So the local base for "the agent's own progress self-report is not admissible evidence" is
[501](sources.md#501) alone: n = 1, MODERATE.** The earlier sentence "the blog corroborates the
reasoning, not the result" is withdrawn — on this evidence the T4 blog is carrying more of the
result than a corroborating source should, and C3 should be read as a **certified-by-agreement
finding with a one-instance local anchor**. Its consequence for the proposal is unchanged in
direction, and stated as a design constraint rather than a measured law: an escalation should be
triggered by
*residue a second party can read* — a reviewer's finding table, a verdict, a reproduction rate — and
never by a controller asserting that it is stuck.

**The convergence on batching is genuine, and triangulation was asked precisely this question.** Its
verdict:

> "**Tension 4 asked whether this is genuine convergence or coincidence of framing. It is genuine
> convergence of MECHANISM, on two independent artifacts, discovered by two clusters that did not
> share sources.**" (`artifacts/triangulation.md` §7.5)

The two artifacts are the corpus's own `writing` convention —

> "**Operator decisions to confirm at approval** (defaults in brackets): - **D1 — spin-outs as new
> incubators vs PARTIAL. RESOLVED (2026-07-01): create both as new incubators** … **D2 — optional
> minor pieces. RESOLVED (2026-07-01): create both** … **D3 — the client T6 (maturity framework).
> ACCEPTED:** seed the *concept* only" [524](sources.md#524)

resolved in a single phase-log line, *"operator approved; D1=both new, D2=both, D3=seed-only"*
[525](sources.md#525) — the cheapest operator turn in the corpus; and `grilling`'s G3 batched-round
asking plus G4 recommended-default annotation [602](sources.md#602). They are structurally identical
on the two moves that matter: **batch the open decisions to one boundary, and ship each with a
proposed default the operator can accept rather than derive.**

**But it is reported below the certification bar**, on two limits triangulation states: (a)
[602](sources.md#602) is T1-primary for its own content and nothing else — one author's skill file,
carrying no evidence that the technique works; (b) the local evidence is n=2 bundles in one repo,
with causation explicitly disclaimed (`writing` has the lowest direction-change rate in the corpus,
3/11 = 27% [10–57%], and *"I cannot prove causation from n=11"*). **And the two artifacts disagree
on timing**: `grilling` is pre-task (*"Do not act on it until the user confirms"*
[602](sources.md#602)) while `writing`'s gate fires *after* a draft exists. **On that disagreement
the corpus is decisive and it favours the proposal's mid-flight framing** — 80% of T1 arrives after a
draft exists.

`grilling`'s G5 is worth naming as the proposal's own predicate in miniature: *"When a frontier
question needs a fact from the environment … dispatch a sub-agent to find it; don't ask the user for
anything you could look up yourself … The _decisions_ are the user's"* [602](sources.md#602). That
is REQ-HERDR-024's shape at a different hop — answer it here if it is answerable here, otherwise
route it. The N-hop generalisation is a coherent extension of a move prior art already makes at one
hop.

### 8.4 Where the evidence does not reach — the cost ratio

**The asymmetry the proposal rests on — a wrong ask costs one operator question, a wrong autonomous
fix costs a review cycle — is an assumption this corpus cannot test.** Four reasons, each measured
or certified:

1. **The corpus records answers, and almost never questions — asserted by the operator cluster, not
   counted.** The operator cluster states it in its limitations (*"Questions are not recorded. The
   taxonomy is reverse-engineered from answers"*), and the only citable instance is a single `low`
   severity self-observation about three decisions in one plan: *"The three operator decisions
   D-5/D-6/D-7 have **no recorded question** — no `scope-answers.md`"* [502](sources.md#502). **No
   corpus-wide count of recorded-versus-unrecorded questions was ever run**, so this is the
   cluster's assertion plus an n = 1 illustration, not a 114-bundle measurement. Counting it is
   cheap and remains undone. On that basis the cost of an ask is not observable, because asks are
   not recorded — but note that the premise itself is uncounted.
2. **There is no counterfactual arm.** Whether asking earlier would have helped is on the list of
   things this corpus structurally cannot answer.
3. **The one measured instance of early asking is a failure, not a cheap one.** The operator was
   asked, selected all four fixes, and *"that selection was made before EXP-001 existed"*
   [503](sources.md#503) — the ask injected a commitment that later measurement invalidated. **A
   wrong ask is not always merely one question; it can be a wrong answer that then has to be
   unwound.** A second instance runs the arrow backwards: a review pass *overturned* an operator
   decision [504](sources.md#504).
4. **Interruption cost is not constant.** The HCI literature is explicit that *"different
   interruption moments have different impacts"* [623](sources.md#623) and that systems should
   *"interrupt users at low-problem state moments"* [622](sources.md#622). Both transfer by analogy
   only — they model interrupting a human's own task, not redirecting an agent — but they are enough
   to say the cost of an ask is a function of *when*, which the flat "one question" model omits.

**The honest formulation.** The corpus supports *"escalation reaches the dominant category of
operator input, and a pre-flight interview does not"*. It does **not** support *"escalation dominates
an automatic trigger"* — that comparison requires a cost measurement no artifact in this corpus
contains. The practical consequence: **the cost ratio should be treated as a design assumption to be
instrumented, not as a finding.** The cheapest instrumentation is to record the ask, since the corpus
currently records only the answer [502](sources.md#502).

### 8.5 The amplification risk — a design requirement the evidence implies

The operator's concern is correct and should be taken seriously: N nested levels each forwarding
upward can flood the human with duplicates of one question. **Any such protocol needs a propagation
budget and dedup-on-the-way-up.** State that as a requirement of the protocol, not as an
implementation detail.

**The corpus cannot measure it.** There is no N-hop data anywhere: `discovered-from` chains reach a
maximum depth of 3 in the whole corpus, with depth 2 the mode and the field used on 1–7% of issues
[310](sources.md#310). The bd graph never nested deeply enough for amplification to be observable.

**The closest local analogue does not survive a direct read, and is withdrawn as support.** T6
loop-bound overrides — the purest thrash-breaking turn in the corpus — run 17 of 18 in one repo,
and **7 of those are one bundle (`plan-050`) raising `max-review-cycles` seven separate times**
[513](sources.md#513). An earlier draft read that as one unresolved question re-escalated seven
times through an unbudgeted channel. **Reading `plan-050`'s `log.md` directly refutes that
reading:** the seven raises occur at `cycles=` 4, 9, 9, 9, 10, 11, 12, so **six of the seven fall
at cycle ≥ 9 — inside the eight rounds this report itself measures as carrying zero findings**
(§7.1: passes 6–13 are eight empty cosmetic rounds [180](sources.md#180)). What was re-escalated
was a *ceremonial loop bound* permitting more empty bookkeeping rounds, not a substantive question
re-asked. The log lines also read `raised to N for this invocation` — an autonomy setting — and per
[501](sources.md#501) "operator" attributions in `log.md` are measurably fallible.

**So the propagation-budget requirement is stated here as a pure design requirement, with no
supporting analogue from this corpus.** It follows from the topology (N levels each forwarding
upward can duplicate one question) and not from a measurement; the corpus contains no N-hop data
and no verified instance of one substantive question being re-escalated.

Two further requirements follow from findings above rather than from the proposal:

- **The escalation trigger must read second-party residue, never a controller's self-report** (§8.3,
  consensus C3).
- **Escalations should batch to a boundary rather than interrupt per question** — the one design
  shape two independent surfaces converged on [524](sources.md#524), [602](sources.md#602), and the
  one the interruption literature's boundary-preference supports [622](sources.md#622).

### 8.6 On the carve

**`yf-herdr` owns the channel; `yf-judgement` owns the decision to ask and what to ask.** The corpus
neither tests nor contradicts this split, but it is consistent with the one certified structural
finding about surfaces: the only surface carrying verified thrash episodes is the **review-pass
prose residue** (§C6), which is a content read, not a transport property. A channel that does not
inspect content cannot decide when to escalate; a judgement layer that has no channel cannot act on
its decision. The carve puts each capability where the evidence locates it. **This is an
architectural judgement consistent with the evidence, not a finding the evidence produced.**

---

## 9. What this corpus cannot answer — absence findings

1. **Whether context exhaustion causes thrash, in either direction.** No token counts, no session
   boundaries, no compaction markers exist anywhere. Four clusters agree; a corpus-wide scan found 3
   apparent hits, all false positives.
2. **The RECALL of any detector.** Only precision was ever measured. 8 multi-pass bundles extract
   zero findings [105](sources.md#105); the letter-paragraph parse shape is a documented unfixed gap;
   85 parse warnings stand. **No statement in this report bounds how many episodes were missed.**
3. **Whether the agent thrashed or the reviewer was slow.** Under that rival the residue is
   identical — same passes, same re-raised concerns. Nothing in a plan bundle separates them.
4. **Whether asking a question earlier would have helped.** No counterfactual arm; the corpus is
   asserted to record answers and not questions (the operator cluster's limitation, illustrated by
   a single `low`-severity finding [502](sources.md#502) — never counted corpus-wide); the one
   measured early ask failed [503](sources.md#503).
5. **Whether low-ceremony repos thrash less.** The fork is stated and cannot be closed: genuinely
   less thrash, or too few bundles to expect even one episode at this base rate, or both.
6. **Any duration, latency or concurrency question.** Blocked by two filed, open defects
   [319](sources.md#319).
7. **Whether phase-log churn is a signal.** The artifact does not exist in the required shape
   [316](sources.md#316). Neither supported nor refuted.
8. **What happens to plans that are abandoned or end after one pass.** 30 of 114 bundles are
   single-pass and excluded by construction; emacs.d `plan-001` was reframed and parked mid-review
   with `Status: drafting` and no pass-2 — a third category the extractor cannot see at all.
9. **Whether any of this survives a different git workflow.** No squash-merging anywhere in the
   corpus [423](sources.md#423); a squash-merging team would destroy essentially all the intra-branch
   churn this study measured.
10. **Cross-repo frequency, for anything.** Only yoshiko-flow and d3-pxe are estimated at all
    [201](sources.md#201).
11. **Whether the two surviving detectors work outside the largest plans.** They are untested below
    roughly 42 KB of `plan.md` because there is nothing there to test them on.
12. **Whether the residue is even the right instrument.** No cluster observed a session, and two
    clusters measured the residue being *wrong* — about who acted [501](sources.md#501) and about
    what happened [303](sources.md#303). **The method has a measured, nonzero error rate against
    ground truth it cannot otherwise see.**
13. **Whether under-specification, construed as anything other than objective word length, relates
    to thrash.** This is the hypothesis's own construct and **it was not measured.** Every
    "specification" quantity computed here is length-derived — objective word count, constraint
    count, and a density carrying a `1/length` denominator — and the report's own exhibits show
    length and specification quality coming apart in both directions (a 9-word objective that
    converged [527](sources.md#527), a 22-word one that thrashed [530](sources.md#530), both
    `[uncertain]`, WEAK-band). Compounding it, the objective text available is **first-committed,
    i.e. post-review in most bundles** [545](sources.md#545), so even the length proxy is measured
    downstream of the process under test. **This corpus cannot measure specification quality
    independently of specification length.** Closing it needs an instrument this study did not
    build — e.g. blind human ratings of objective adequacy on a stratified sample, or recovery of
    genuinely pre-review objective text.

### Contradictions left open

Two contradictions are reported **unresolved**, per their own authors, and must not be synthesised
as settled:

- **Ceremony vs trouble.** *"the corpus supports both readings at different grain"* — at repo
  aggregate, ceremony and multi-pass rate move together; at bundle level, at least one clear
  counter-example (rc-files `plan-004` [204](sources.md#204)) shows depth tracking task stakes, not
  repo habit. n=1 on the bundle-level side.
- **What `writing`'s final-verdict field means.** A direct read of three bundles beats a regex over
  the verdict line [207](sources.md#207) — but **the blast radius was never measured**. Nobody
  checked how many of the other 111 bundles resolve inline. **Every corpus-wide verdict statistic in
  this study is therefore an upper bound on non-convergence by an unknown margin.**

---
