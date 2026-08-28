---
type: Research Artifact
description: Cross-cluster triangulation for yf-research 005 — evidence-strength standard,
  the plan-size control applied to every candidate signal, the specification-density
  adjudication, severity-decay's operating characteristics, consensus findings, unresolved
  contradictions, and the questions this corpus structurally cannot answer.
okf_spec: OKF-RESEARCH
---

# Triangulation — thrash detection and operator judgement

Inputs: the six retrieval clusters plus `tooling-notes.md`, and `sources.json` (228 sources).
Every numeric claim below that is attributed to a cluster was **recomputed** by re-running
`scripts/corpus_scan.py`, `scripts/finding_recurrence.py` and `scripts/churn_signature.py`
read-only against the live corpus on 2026-08-28. All three reproduced their reported headline
figures exactly: **114 bundles / 301 review passes** [103], **1509 findings / 85 parse warnings /
40 matches at threshold 0.20 / 8 at 0.35 / 252 weak id-reuse / 51 self-reported** [105][424], and
**5 churn-signal commits / 233 repeatedly-touched files across 53 bundles** [401]. Where my
recomputation *differs* from a cluster's number, both are reported and the difference is named.

No claim below is an observation of a session. 004's boundary holds throughout: plan bundles
record **artifacts, not live session behavior** [100].

---

## 1. Evidence-strength standard

### 1.1 Why the default recipe does not apply

205 of 228 sources are **local corpus artifacts** — file paths, commit SHAs, bead records, tool
output. `credibility_scorer.py` derives its score from a URL's domain and a publish date; a
`docs/plans/plan-048-.../reviews/pass-3.md:97` has neither. Scoring them on that rubric would
produce a number with no referent. A separate standard is defined here and written into
`sources.json` as an `evidence_strength` object on every non-`prior-art` source.

### 1.2 The local rubric (0–100, four axes)

| axis | max | what earns the top of the band |
| :-- | --: | :-- |
| **Directness** | 40 | a verbatim quote from the primary artifact (40); the artifact cited but paraphrased (28–36); a tool-derived aggregate *over* primaries (20); a statement about this study's own method (12) |
| **Reproducibility** | 25 | an exact regenerating command, and I re-ran it (25); command given, not re-run (18); path+line pointer only (12); narrative locator (6) |
| **Verification** | 20 | hand-audited by the cluster author against the source file (20); tool-asserted and spot-checked (12); tool-asserted, unaudited (6) |
| **n / scope** | 15 | corpus-wide, n ≥ 79 (15); multi-repo subset, n ≥ 20 (11); one repo, n ≥ 4 (7); a single bundle or instance (4) |

Bands: **STRONG** ≥ 80 · **MODERATE** 65–79 · **WEAK** 50–64 · **INDICATIVE** < 50.

The axes are chosen because each corresponds to a failure this corpus actually produced.
*Directness* because the operator cluster measured a case where the residue **asserted an
operator turn that did not happen** — "CORRECTION: this transition was performed by the
subordinate execute-session agent, not by an operator, and was originally logged as 'operator
approved' — which was false at the time it was written" [501]. *Verification* because the
recurrence cluster's hand-audit inverted the tool's own headline (§6.1 below), and because the
extractor's author "found and fixed ~700 bogus matches during validation" [102]. *n* because the
entire comparison rests on 17 vs 20 bundles (§5).

**A tool-output source is deliberately capped at MODERATE** even though I re-ran every tool and
every count reproduced. Reproducibility is not verification: `finding_recurrence.py` reproduces
its 40 matches perfectly and 16 of those 40 are FALSE or DEEPEN on hand-read [audit tally,
§3 of the recurrence cluster]. A number that regenerates identically is not thereby true.

Resulting distribution over the 205 local sources: **25 STRONG · 169 MODERATE · 11 WEAK · 0
INDICATIVE**. The STRONG band is dominated by `git-log`/`git-show` sources (exact SHA, re-runnable
command, hand-audited body) and the hand-audited bead records.

### 1.3 The web rubric, applied to 601–623 — and corrected

`credibility_scorer.py batch` was run over the 23 `prior-art` sources. Its raw output is written
to each source's `credibility.scorer` field. **It misranks this set, and the misranking is
systematic, so an `adjudicated_tier` is written alongside it.**

| mechanical score | n | which sources |
| --: | --: | :-- |
| 63 "verify" | 5 | every `arxiv.org` / `dl.acm.org` URL |
| 41 "questionable" | 18 | everything else — including **ACL Anthology**, **IEEE RE 2021**, **CHI 2004**, and every primary GitHub skill file |

Two defects, both measured:

- **Peer review is invisible to it.** `aclanthology.org` (NAACL Findings 2025 [6-in-cluster,
  id 606]; ACL 2024 long paper, id 611) scores **41**, below an unreviewed arXiv preprint's **63**.
  Zaremba & Liaskos, IEEE RE 2021 [618], scores 41 because it is hosted on `yorku.ca` — a
  university, but not a `.edu` TLD, which is what the rubric tests. Adamczyk & Bailey, CHI 2004
  [623], scores 41 because it is hosted on `interruptions.net`.
- **Currency is uninformative here.** No source in the set carries a publish date in the record,
  so the retrieval date was substituted and **all 23 scored exactly 50** on that axis. The axis
  contributes 20% of the score and zero information.

Adjudicated tiers: **T1-peer-reviewed 7** (606, 611, 618, 619, 620, 622, 623) · **T1-primary 6**
(601–605, 621 — the skill files themselves, authoritative for claims about their own content and
for nothing else) · **T2-preprint 5** (607–610, 613) · **T4 5** (612 vendor glossary; 614
practitioner blog, n=1; 615–617 OSS projects, one with 0 stars).

**One tier assignment is load-bearing downstream.** `unloop-mcp` [616] is T4-OSS and its central
mechanism — "When similarity exceeds 55%, it flags a loop" [616] — is **contradicted by this
corpus**, which found no threshold plateau and found that similarity magnitude does not rank truth
(§6.6). The prior-art cluster called it "the closest fit in the whole cluster"; on evidence tier
it is the weakest external source making a mechanism claim.

---

## 2. The size confound (D-1)

### 2.1 The control, verified and re-measured

`cluster-review-pass-recurrence.md` reports:

> "**Spearman ρ(review-pass count, `plan.md` size) = 0.739 over 109 bundles**" [189]

**The artifact's number is 0.739 and the operator's report of it is correct.** My independent
recomputation over the same 109 bundles (those with ≥1 review pass and a readable `plan.md`)
gives **ρ = 0.792** on the current `plan.md` and **ρ = 0.601** on the **first-committed**
`plan.md` recovered from git. All three are large and same-signed. I use **current `plan.md`
bytes** as the control variable below and report the first-committed figure wherever it changes a
verdict; it does not change one.

The first-committed figure matters for interpretation, not for the control: the operator cluster
established that "the first committed `plan.md` is usually *post-review*, not the initial draft"
[545 §1], so **neither measure is a clean pre-work difficulty proxy**. ρ=0.601–0.792 bounds it.

Supporting per-band evidence [189]:

| passes | bundles | median `plan.md` bytes | % firing the recurrence detector |
| :-- | --: | --: | --: |
| 1 | 30 | 16,398 | 0% |
| 2 | 37 | 19,790 | 5% |
| 3–4 | 23 | 35,758 | 22% |
| 5+ | 19 | 62,461 | **63%** |

and by review-text volume rather than plan size [190]: 0 findings → 0%, 1–20 → 12%, 21–50 → 44%,
51+ → **86%**.

### 2.2 How each signal was controlled

Two controls, both computed on the **79 multi-pass bundles**:

1. **Partial Spearman** ρ(signal, label | `plan.md` bytes).
2. **Stratified firing rate** by `plan.md` size quartile — which is the more honest instrument
   here, because the partial correlation assumes a monotone relation that the quartile table shows
   is closer to a step function.

The label is the **recurrence cluster's own hand-audit**: a bundle is labelled TRUE if it contains
at least one episode the cluster verdicted TRUE on reading both pass files. That is **14 of 79
multi-pass bundles = 18% [95% CI 11–28%]**.

**This label has a fatal circularity for exactly one signal and it must be stated first.** Only
bundles that the text-similarity detector (D7) nominated were hand-audited. A bundle that
thrashed without producing a D7 candidate is labelled negative by construction. **Therefore D7
cannot be scored against this label at all** — its apparent partial ρ of +0.79 is an artifact of
the label being derived from its own output. Every other signal *can* be scored, but is being
scored against a D7-filtered ground truth, which biases toward D7-correlated signals. This is the
strongest available label in the study and it is not a good one.

### 2.3 Stratified firing rates by plan.md size quartile (n=79 multi-pass)

| quartile | n | `plan.md` bytes | D7 fires | D1 fires | HIGH at pass ≥3 | hand-audit TRUE |
| :-- | --: | :-- | --: | --: | --: | --: |
| Q1 | 19 | 13,688–19,375 | 11% | 5% | **0%** | 5% |
| Q2 | 19 | 19,685–25,514 | 5% | 5% | **0%** | 0% |
| Q3 | 19 | 25,803–41,587 | 21% | 26% | 11% | 11% |
| Q4 | 22 | 42,110–184,157 | **55%** | **50%** | **55%** | **50%** |

**This table is the single most important result in the triangulation.** Every candidate signal
and the ground-truth label itself are concentrated in the largest quartile. In Q1+Q2 (38 bundles,
half the multi-pass corpus) the severity signal **never fires at all** and one bundle in 38 carries
a TRUE label. **The study is, in substance, a study of the 22 largest plan bundles.**

Within Q4 — the only band where anything varies — the signals do separate from the 50% base rate:

| signal (within Q4, n=22, base rate 50%) | TP | FP | FN | TN | PPV | sensitivity |
| :-- | --: | --: | --: | --: | :-- | :-- |
| HIGH at pass ≥3 (strict) | 9 | 3 | 2 | 8 | 75% [47–91%] | 82% [52–95%] |
| D1 back-reference (reimplemented) | 8 | 3 | 3 | 8 | 73% [43–90%] | 73% [43–90%] |
| D6 non-increasing finding counts | 1 | 5 | 10 | 6 | **17% [3–56%]** | 9% [2–38%] |
| D7 text similarity | 11 | 1 | 0 | 10 | *circular — not scoreable* | *circular* |

### 2.4 SURVIVES the size control

| signal | ρ w/ size | partial ρ(sig, TRUE \| size) | within-Q4 PPV | verdict |
| :-- | --: | --: | :-- | :-- |
| **D3 — HIGH-severity finding at pass ≥3** | +0.522 | **+0.482** | 75% [47–91%] vs 50% base | **SURVIVES, weakly.** Corpus-wide LR+ = 10.4, specificity 94% [85–98%]. Fails the shippability test in §4. |
| **D1 — explicit cross-pass back-reference with a failure word** | +0.484 | **+0.414** | 73% [43–90%] vs 50% base | **SURVIVES, weakly.** An exact string predicate with no threshold to tune, portable to 5 of 7 repos [183]. My reimplementation: **53 signals across 18 bundles**, against the cluster's 54 across 16 [183] — an independent near-reproduction. But see §7.2: it fires on three clean controls. |
| **D2 — cross-pass reproduction rate** | *not computable* | *not computable* | *n=1* | **SURVIVES BY CONSTRUCTION but `[insufficient evidence]`** — it is a *ratio*, so plan size cancels algebraically. It exists as a trend in exactly one bundle (§7.3). |
| total finding count | +0.535 | +0.411 | — | **SURVIVES NUMERICALLY, BUT IS NOT AN INDEPENDENT SIGNAL.** It is a second measurement of the confounder: D7's firing rate runs 12% → 86% across finding-volume bands [190]. Listing it as a candidate would be listing plan size twice. |

### 2.5 DOES NOT survive the size control — named, and ruled out

| signal | ρ w/ size | partial ρ(sig, TRUE \| size) | why it is ruled out |
| :-- | --: | --: | :-- |
| **D8 — raw review-pass count** | **+0.811** | +0.325 | It *is* the confounder's closest proxy. ρ=0.811 with plan size on the multi-pass set. The recurrence cluster says it plainly: "**'Many passes' is not, on its own, a thrash signal.** It is a description of a large plan" [103]. **Ruled out.** |
| **D6 — non-increasing finding counts** | −0.565 | −0.274 | Reproduces the cluster's contrast (firing 29% [13–53%] vs control 60% [39–78%]; over all 79, 37% vs 83%) — but **within Q4 it has PPV 17% and sensitivity 9%**, i.e. it is worse than a coin flip exactly where the thrash is. Outside Q4 it is measuring plan size. **Ruled out.** |
| **D9 — approve→revise verdict reversal** | — | — | Recomputed: firing 4/19 = 21% [9–43%] vs control 4/60 = 7% [3–16%] — the intervals overlap heavily. And the cluster's own control reading refutes it: `plan-026` runs "REVISE, APPROVE, APPROVE, REVISE, APPROVE, REVISE, APPROVE over 7 passes with **zero** recurrence" because "each REVISE follows a *deliberate scope change*" [181]. **Verdict non-monotonicity is the signature of a re-scoped plan.** Ruled out. |
| **D7 — text-similarity recurrence (the shipped detector)** | +0.418 | *circular* | Cannot be scored against the only label available. Independently: 50% precision at its documented operating point (4 TRUE of 8, [95% CI 22–78%]) [170], 60% over the audited 40 [24/40, 95% CI 45–74%], **no threshold plateau** (40 → 3 matches from 0.20 to 0.70 [105]), and its id-reuse basis is **0 for 3** [170]. Its firing rate is 0/5/22/63% across pass bands and 11/5/21/55% across size quartiles. **Ruled out as a standalone detector**, on its author's evidence and mine. |
| **Self-reported cross-pass signal count** | +0.385 | **+0.095** | Near-zero partial. And the signal is *inverted* — see §6.1. **Ruled out.** |
| **Git churn-signal commits** (revert/redo message pattern) | +0.324 | **−0.149** | ρ with the TRUE label = **+0.016**. Five hits in 114 bundles [401]; the git cluster's own verdict: "3 of the 5 are cross-plan documentation corrections rather than within-plan thrash" [409]. **Ruled out.** |
| **Git repeatedly-touched files** | +0.422 | **+0.061** | 233 files across 53 bundles [401], and the cluster hand-audited 20: "**zero classified as genuine intra-plan THRASH**", with 5 of 20 (25%) contaminated by a *different plan's* commits falling inside the window [416][420][421]. The top 7 basenames are 120 of 233 instances and all seven are mandated hot files [422]. **Ruled out.** |
| **`bd` status reopen** | *never fires* | — | 3 reopens in 2,969 status changes corpus-wide, all in one repo [306], and all three hand-audited as tooling probes or a bead-id clerical fix. "**Reopen-as-recorded-in-bd never once corresponded to 'the agent changed its mind and redid the work' in this corpus.**" **Ruled out — it has no measured positives at all.** |
| **`discovered-from` chain depth** | — | — | Depth 2 is the corpus **mode**, max 3 anywhere, population 1–7% of issues [310]. "A detector that fired on 'depth >= 2' would fire on effectively every recorded use of the field." **Ruled out structurally, not statistically.** |
| **Phase-log churn** | — | — | `log.md` exists in 37.7% of bundles [316] and where present is a single retrospective write with 0–2 entries [317][318]. The artifact does not have the incremental shape the signal requires. **Ruled out — unmeasurable, not measured-and-null.** |
| **Timing / duration signals** | — | — | Two filed, open, unresolved instrumentation defects: `started_at` written for 86 of 225 beads and unexposed by `bd list --json` [319], and batch closes collapsing 84% of observed overlap into an artifact. **Ruled out until those are fixed.** |
| **Burst-then-gap-then-correction commit timing** | — | — | n=1 [418]; the git cluster looked for the shape around the other four signals and did not find it. **Ruled out as underpowered** (§7.4). |

**Net:** of ~14 candidate signals carried into triangulation, **two survive the size control as
independent detectors (D3, D1), both weakly, both only inside the top size quartile**; one (D2)
survives by construction on n=1; and eleven are ruled out.

---

## 3. The specification-density adjudication (D-2)

### 3.1 The claim under test

`cluster-operator-breakthrough-turns.md` reports specification density (bold-bullet constraints
per 1k chars) at **r = −0.278** with direction-change count and **−0.319** with review-pass count,
and calls it:

> "The only supporting signal is specification *density* … That is a genuine effect and it is in
> the hypothesised direction. But it is weaker than the size effect, it is partly a `1/length`
> artifact, and the hypothesis's own headline prediction — visible in the initial objective — is
> **flatly null** (r = −0.002)."

**The operator's report of −0.28 / −0.32 is verified against the artifact.** Both are correct as
written.

### 3.2 The decomposition the directive asks for

Density = constraints ÷ length. I recomputed all three terms separately as Spearman correlations
with review-pass count, over the 109 bundles with ≥1 pass, on both the current and the
first-committed `plan.md`. (Note: my bold-bullet regex yields densities ~1.4/1k against the
cluster's medians of 0.51/0.72, so the *definitions differ*; the decomposition below is internally
consistent and should be read as a re-derivation, not a re-check of their exact constant.)

| term | current `plan.md` | first-committed `plan.md` |
| :-- | --: | --: |
| ρ(**length**, review passes) | **+0.791** | **+0.601** |
| ρ(**raw constraint count**, review passes) | **+0.170** | **+0.088** |
| ρ(**density** = constraints/length, review passes) | **−0.422** | **−0.392** |
| ρ(−length, review passes) — pure inverse length | −0.791 | −0.601 |
| ρ(length, constraint count) | +0.350 | +0.438 |
| **partial ρ(constraint count, passes \| length)** | **−0.186** | **−0.244** |
| **partial ρ(density, passes \| length)** | **−0.230** | **−0.294** |

### 3.3 The verdict

**The numerator does not carry the effect. The denominator does — but the numerator is not zero
either, and the honest answer is between the two positions.**

1. **Raw constraint count correlates with churn in the WRONG direction for the hypothesis.**
   ρ = **+0.088 to +0.170** — plans with *more* constraints have *slightly more* review passes,
   not fewer. If the under-specification hypothesis were carried by the number of constraints
   stated, this term would be negative. It is positive.
2. **Density's negative sign is inherited from `1/length`.** Length alone gives ρ = −0.60 to −0.79
   against churn when inverted; density gives −0.39 to −0.42. **Density's entire raw correlation
   is smaller in magnitude than the pure inverse-length term it contains.** The cluster author's
   own flag — "partly a `1/length` artifact" — is confirmed and can be stated more strongly: the
   *sign and most of the magnitude* are the length denominator.
3. **A small residual survives the control, and I will not zero it out to make the verdict
   cleaner.** Partial ρ(constraint count, passes | length) = **−0.19 (current) / −0.24
   (first-committed)**. At n=109 the first-committed figure is nominally p ≈ 0.011. So once length
   is held fixed, *within* a length band, plans with more bold-bullet constraints do show slightly
   fewer review passes. It is one-third the magnitude of the length effect and it is a single
   unadjusted test among many computed in this study.

**Plain verdict on the under-specification hypothesis.** The hypothesis's own headline prediction
— that under-specification is visible in the initial objective — is **null, r = −0.002**, and is
directly refuted by a named counter-instance: d3-pxe plan-016's objective is a 22-word,
SPEC-anchored, issue-numbered, technology-named statement that produced **8 review passes and 6
operator decisions** [530]. What remains after the size control is **a residual partial
correlation of about −0.2 on a hand-defined constraint-count proxy**. That is not "no surviving
quantitative support" — but it is **an order of magnitude weaker than the confounder it is
competing with**, it points at constraint *concentration* rather than constraint *presence*
(raw count is positively correlated with churn), and it is not a basis on which to build a
detector. The operator cluster's own alternative reading is better supported by the same data:
what separates the groups is **"how many independent decisions the work contains (issues,
r = +0.43), not how well the goal was stated."**

---

## 4. Severity-decay operating characteristics (D-3)

### 4.1 The two numbers, verified

The operator reports **59% in firing bundles vs 15% in controls**. The artifact's cross-tab [180]
reads:

| discriminator | recurrence-fired (n=17) | control (n=20) |
| :-- | :-- | :-- |
| a HIGH-severity finding at pass ≥3 | 10 (59%) | 3 (15%) |

**Both numbers are correct as reported, and both reproduce exactly** when the severity match is
the strict token `high`: firing **10/17 = 59% [95% CI 36–78%]**, control **3/20 = 15% [95% CI
5–36%]**. The three control bundles that fire are `yoshiko-flow/plan-033`, `d3-pxe/plan-017`, and
`d3-pxe/plan-011` (Incubator).

**The numbers are fragile to severity-vocabulary normalisation, which is a measured defect, not a
hypothetical.** Widening the match to `high|critical|blocking` — a reasonable normalisation given
that the recurrence cluster itself records the vocabulary as unnormalised, listing `medium`,
`med`, `medium-low`, `low-med`, `high, blocking` [104] — moves the control to **4/20 = 20%** and
**adds `plan-026` to the firing set**. See §4.4.

### 4.2 Implied false-positive rate and the base rate it acts on

- **FPR = 15% [95% CI 5–36%]** on ≥3-pass, parseable, non-recurrence bundles. The interval's upper
  bound is more than twice its point estimate; **from n=20 this rate is bounded, not known.**
- **The base rate it is applied against is the reachability of pass 3 at all: 42 of 114 bundles =
  37% [95% CI 29–46%]** [103]. Only 37 of those 42 extract any parseable finding, so the
  detector's actual denominator is **37 of 114 = 32%** of the corpus.
- Prevalence of the hand-audit TRUE label among multi-pass bundles: **14/79 = 18% [95% CI 11–28%]**.
  Among the 37-bundle ≥3-pass set it is **38%**.

### 4.3 Positive predictive value

Scored against the hand-audit TRUE label over all 79 multi-pass bundles (strict `high`):

| | TRUE | not TRUE |
| :-- | --: | --: |
| HIGH at pass ≥3 | **9** | **4** |
| no HIGH at pass ≥3 | 5 | 61 |

- **Sensitivity 9/14 = 64% [95% CI 39–84%]**
- **Specificity 61/65 = 94% [95% CI 85–98%]**
- **PPV 9/13 = 69% [95% CI 42–87%]** at the corpus base rate of 18%
- **Likelihood ratio+ ≈ 10.4**

**This is the answer to the "good LR, bad PPV" question: it is the other case.** The likelihood
ratio is good *and* the PPV is tolerable (69%) — because the specificity is 94%, not because the
base rate is favourable. **But the PPV's confidence interval runs from 42% to 87%**, and 42% is
below a coin flip. **At this n the detector cannot be distinguished from one that is wrong more
often than it is right.** Report it as a candidate, never as a characterised instrument.

Three further caveats attach to that PPV and each is capable of reversing it:

1. **The label is D7-derived.** Four of the five FN and all four FP are bundles D7 never
   nominated, so they were never hand-read. The FP count is a floor and the FN count is unknown.
2. **8 multi-pass bundles extract zero findings** and are invisible to the detector by
   construction [105][180]; the letter-paragraph parse shape is a documented, unfixed gap [102].
3. **Severity is not recorded on 185 of 1509 findings** and its vocabulary is unnormalised [104].
   §4.1 shows the headline contrast moving with the normaliser.

### 4.4 The shippability test — `plan-026` and `plan-050`, by name

**`plan-026-james-dixson-6e0e2f` — 7 passes, verdict oscillation from deliberate re-scoping, zero
recurrence** [181]. Measured per-pass, in correct numeric order:

| pass | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| :-- | --: | --: | --: | --: | --: | --: | --: |
| findings | 6 | 2 | 3 | 5 | 1 | 5 | 1 |
| verdict | REVISE | APPROVE | APPROVE | REVISE | APPROVE | REVISE | APPROVE |
| HIGH (strict `high`) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| HIGH (incl. `blocking`) | 0 | 0 | 0 | 0 | 0 | **1** | 0 |

**The answer is conditional, and the condition is the severity normaliser.**

- Under a **strict** `high` match, severity-decay **does not fire** on plan-026. It passes the test.
- Under a normaliser that folds `blocking` into HIGH, it **does** fire. The single triggering
  finding, read directly, is `pass-6.md`'s: "**C1 — the de-list list misses ≥3 in-repo references
  — severity: medium (blocking).**" That is a *medium* finding the reviewer marked
  merge-blocking, in a **delta review of one refactor since a pass-5 APPROVE** — the purest
  possible instance of the re-scoping shape the test exists to protect.

**Stated outright, as the directive requires:** a severity-decay detector that treats
"medium (blocking)" as HIGH **fires on plan-026 and is not shippable.** The strict-`high` variant
survives this test, but it survives it *by a single token in an unnormalised free-text field*
[104]. Any implementation must pin the severity vocabulary before it is deployed, and the pinning
decision — not the detector — is what determines whether it passes.

**`plan-050-james-dixson-d0414b` — 13 passes, 8 of them empty.** The empty-pass count is verified:
**8 of 13 passes extract zero findings** [180]. Measured in correct numeric order:

| pass | 1 | 2 | 3 | 4 | 5 | 6–13 |
| :-- | --: | --: | --: | --: | --: | --: |
| findings | 5 | 4 | 11 | 17 | 14 | 0 (all eight) |
| HIGH | 1 | 1 | 2 | 4 | 3 | 0 (all eight) |
| verdict | REVISE | APPROVE | REVISE | REVISE | REVISE | REVISE ×7, APPROVE |

**Severity-decay fires on plan-050, under both normalisers** (HIGH at passes 3, 4 and 5).

**But plan-050 is not a clean non-thrash shape, and the artifact contradicts itself about it.**
`cluster-review-pass-recurrence.md` §5 lists it under "Two control shapes that look like thrash
and are not" — while §3 of the *same artifact* audits two of its episodes, E19 and E20, as
**TRUE**: "The same count re-litigated, and inverted: six→five→six" [133][134] and "Pass 4's C29
flagged #183's blank and **missed that the whole document is blank**" [135][136]. It is also, on
the tool's own output, a **firing** bundle (2 matches at 0.20, 1 at 0.35), not a control.

**Adjudication.** The measurement reconciles them and I do not have to choose: plan-050 is
**both**, sequentially. Passes 1–5 carry every finding and every HIGH finding in the bundle and
contain two hand-verified TRUE recurrences; passes 6–13 are the eight empty bookkeeping rounds.
So the *pass count* (13) is inflated by cosmetic rounds — which is what §5 is really saying — while
the *content* is a genuine 5-pass recurrence episode. **Severity-decay firing on plan-050 is
therefore a true positive, not a false one**, and it fires at pass 3, before the eight cosmetic
rounds were ever written. The artifact's §5 framing is misleading as written and should not be
carried forward as "plan-050 is a control."

### 4.5 Latency — what it can and cannot buy

**First computable at pass 3, by definition.** The predicate is "a HIGH-severity finding survives
into pass 3 or later"; it cannot be evaluated before a third pass file exists.

- **It cannot prevent a 3-pass burn.** By the time it can speak, three adversarial review passes
  have been written. In the corpus's firing group those first three passes are where most of the
  work is: `plan-054` carries 22, 14, 8 findings in passes 1–3; `plan-053` carries 14, 15, 14.
- **It can prevent passes 4 through N**, and N reaches 6, 7, 8 and 13 in this corpus. In the firing
  group, HIGH counts reach zero only at passes 6–7: `plan-048` runs HIGH 7,6,4,1,2,0,0;
  `plan-054` 8,6,4,2,2,0; `plan-055` 5,8,2,1,1,1,0 [180]. Against controls that reach zero by
  pass 2–3: `plan-042` HIGH 4→2→0; `plan-041` 3→0→0; `plan-043` 4→1→0→0 [181].
- **It is silent on 68% of the corpus.** 72 of 114 bundles never reach pass 3, and 62% of bundles
  finish in ≤2 passes [103]. A detector that only speaks about the third of the corpus that is
  already in trouble is a *triage* instrument, not an early-warning one.
- **D1 is available one pass earlier** — at pass 2, the first pass at which any cross-pass signal
  is definable — and **39% of all D1 signals fire there** (21 of 54) [183]. On latency alone, D1
  dominates D3. On measured precision within Q4 they are indistinguishable (73% vs 75%, intervals
  almost fully overlapping).

---

## 5. Consensus findings

Certified only where **three or more clusters independently support the finding**. Each carries
the repos it is actually evidenced in, per the cross-domain limit (§5.6 of the herdr cluster).
Every rate carries a Wilson interval.

### C1 — Task difficulty, proxied by plan size and decision count, is the dominant explanation of review-pass volume, and it beats every specification measure

**Clusters: 4** — recurrence, operator-breakthrough, herdr, git-churn. **Confidence: HIGH.**
**Evidenced in: all 7 repos.**

- recurrence: "**Spearman ρ(review-pass count, `plan.md` size) = 0.739 over 109 bundles**" [189];
  "**This is the central negative result of the cluster.** The recurrence detector's output is
  very nearly a monotone function of how much review text a bundle contains."
- operator: "Issue count is the strongest predictor of both direction changes (r=+0.43) and review
  passes (r=+0.55) — stronger than any specification measure." Initial-objective length: **r =
  −0.002**.
- herdr: "**Volume, not domain, predicts multi-pass rate.**"
- git-churn: "**File re-touch count is confounded with commit granularity by construction.**"

My recomputation: ρ = 0.792 (current `plan.md`) / 0.601 (first-committed), n=109; and the quartile
table in §2.3.

### C2 — Context exhaustion is untestable in this corpus, in every direction

**Clusters: 4** — recurrence, operator-breakthrough, execution-telemetry, git-churn.
**Confidence: HIGH (as an absence).** **Evidenced in: all 7 repos.**

- recurrence: "**Not testable from this residue at all** … Plan bundles carry no token counts, no
  session boundaries, no compaction markers … **Every discriminator above fails this rival.**"
- operator: "**NO — total blindness.** A corpus-wide scan found **3 apparent hits, all false
  positives** (a SKILL.md token budget, not a session context window)."
- telemetry: no token or session field exists in the `bd` schema; `interactions.jsonl` records
  only status transitions [302].
- git-churn: "none of the signals in this cluster distinguish these from thrash."

**Absence is the finding.** Any downstream claim that context exhaustion is or is not a cause of
thrash is unfounded on this corpus.

### C3 — The agent's own progress self-report is not admissible evidence, and the residue can be wrong about the operator too

**Clusters: 4** — operator-breakthrough, prior-art, recurrence, telemetry. **Confidence: HIGH.**
**Evidenced in: yoshiko-flow, d3-pxe (residue mis-attribution); external literature.**

- prior-art [614, T4-practitioner]: "Asking a stuck agent whether it's stuck is asking the
  unreliable narrator to review their own reliability."
- operator [501]: a `log.md` entry recording "operator approved" that was **false when written**.
- recurrence: "A `reviews/pass-N.md` is written by a reviewer, not by the agent that thrashed."
- telemetry: `bd history` "is **actively misleading** — 641/745 entries for one bead were duplicate
  'closed' snapshots from unrelated batch commits" [303].

**Note the tier asymmetry**: the external support [614] is a T4 single-incident blog. The *local*
support (501, 303) is STRONG-band and directly measured. The finding rests on the local evidence;
the blog corroborates the reasoning, not the result.

### C4 — The corpus is concentrated in two repos, and no frequency or rate claim generalises beyond them

**Clusters: 4** — herdr, recurrence, telemetry, git-churn. **Confidence: HIGH.**
**Evidenced in: yoshiko-flow + d3-pxe only; explicitly NOT in the other five.**

- herdr: "**Every one of the 8 candidate episodes lives in exactly 3 of the 7 repos** … and **6 of
  the 8 are in the two highest-volume software repos**" [201]. "absence of detected recurrence in
  the low-ceremony repos is NOT evidence of absence of thrash."
- recurrence: "yoshiko-flow supplies 42 of 79 multi-pass bundles and 26 of 40 D7 episodes" [182];
  the "defect inside its own fix" phrasing is "effectively a single-repo artifact" [194].
- telemetry: all 3 corpus reopens are in yoshiko-flow [306]; the bd↔bundle join covers 69.3%.
- git-churn: all 5 churn-signal commits are in yoshiko-flow (2) and d3-pxe (3).

Per-repo 3+-pass rates with intervals, showing why: **d3-pxe 13/19 = 68% [46–85%]** ·
**yoshiko-flow 23/56 = 41% [29–54%]** · pybridge 2/11 = 18% [5–48%] · writing 2/11 = 18% [5–48%] ·
evri_py 1/9 = 11% [2–44%] · rc-files 1/4 = 25% [5–70%] · **emacs.d 0/4 = 0% [0–49%]**. Four of
seven repos have intervals wider than 40 percentage points. **Only yoshiko-flow's and d3-pxe's
rates are estimated at all.**

### C5 — The dominant residue signature is PARTIAL LANDING, not decision oscillation

**Clusters: 3** — recurrence, herdr, git-churn. **Confidence: MODERATE-HIGH.**
**Evidenced in: yoshiko-flow, d3-pxe, rc-files, evri_py.**

- recurrence, from the 40-episode hand-audit: "**~20 [of 24 TRUE] are PARTIAL LANDINGS** — a
  remedy applied at the one site the reviewer named, while the same defect survives elsewhere …
  **Absence finding, stated plainly: I found essentially no decision oscillation in this corpus.**
  One instance in 40 candidates, over 301 review passes."
- herdr, independently, in a different repo: "**Residual C7:** the Approach `pve_lxc` bullet
  **still** cites `PVE-GPU-003/005/006`" [208]; and rc-files' pass-2 raising "a **fresh mechanical
  defect introduced by fixing pass-1**" [205].
- git-churn, from a commit body: "Third drift of one REQ inside one plan: grep gave 25, the spec
  asserted 24, and retrospective-report was unenumerated" [408].

**This is the study's most consequential reframing, and it is convergent across three independent
surfaces (review text, cross-repo read, commit messages).** Audited proportions: TRUE 24/40 = 60%
[45–74%], of which ~20 are partial landings; DEEPEN 7/40 = 18% [9–32%]; FALSE 9/40 = 22% [12–38%].
A detector designed against an oscillation model targets a phenomenon this corpus does not contain.

### C6 — Execution telemetry (`bd`) and git history are health-check surfaces, not thrash-detection surfaces

**Clusters: 3** — telemetry, git-churn, recurrence. **Confidence: HIGH.**
**Evidenced in: all 7 repos** (this one does generalise, because the *absence* was measured
everywhere).

- telemetry: "**The prose artifacts … are, on this corpus, the load-bearing evidence; bd telemetry
  as currently instrumented is a health-check surface, not a thrash-detection surface.**"
- git-churn: "**Git carries a real but sparse and mostly-precision-limited thrash signal, and it is
  not earlier or more reliable than the review-pass residue** … **zero of 20** hand-audited samples
  were genuine intra-plan thrash."
- recurrence supplies the comparator: the prose surface produced 40 candidates and 24 hand-verified
  TRUE episodes from the same corpus.

Rates: bd reopens **3/2969 = 0.10%**, all tooling artifacts [306]. Git churn-signal commits
**5/114 bundles = 4.4% [95% CI 1.9–9.9%]**, of which 3 are cross-plan corrections. Literal
`git revert` commits: **0 of 2044** [407]. Semantic hand-authored reverts: **4, all outside every
tracked plan window** [411].

### C7 — Every consensus finding above is a claim about ARTIFACTS

**Clusters: 6 of 6.** **Confidence: HIGH.** Every cluster opens by restating 004's boundary [100],
and two clusters supply measured instances of the residue being wrong about what happened
([501], [303]). Under the rival "the agent converged fast and the *reviewer* was slow," the
residue would look identical. Nothing in this corpus separates them.

### Findings with exactly TWO clusters — reported, not certified

- **Batching operator decisions with proposed defaults at a boundary is the best-supported
  intervention shape.** operator-breakthrough + prior-art. See §7.5.
- **The review artifact FORM is shared across all seven repos** (finding table, severity, Operator
  Resolutions, verdict line). herdr §6 + tooling-notes. This is about form, not frequency, and it
  is the one thing herdr says *does* generalise.

---

## 6. Contradictions

### 6.1 The 51 self-reported cross-pass signals — ADJUDICATED, with the downstream damage named

**Side A**, `tooling-notes.md` [102][424]:

> "**51 self-reported cross-pass signals** … This is the highest-confidence recurrence signal in
> the corpus because a human reviewer already did the cross-pass comparison; it should be weighted
> above the text-similarity matches in any downstream synthesis."

**Side B**, `cluster-review-pass-recurrence.md` §4, having read all 51 [171]:

> "**Hand-read, that is wrong.** … **47 of 51 are clean all-resolved statements** — 'All eight
> concerns resolved', 'All four pass-1 concerns verified genuinely and correctly resolved against
> the real repo', 'All 16 concerns resolved' … These are evidence that the previous round *worked*.
> … As a thrash signal it is **inverted**."

**Adjudication: Side B, and the reasoning is not a preference.** Side A is a *design assertion*
about what a code path was built to capture; Side B is an *audit of the 51 objects it actually
captured*, each read in its source file. Under this triangulation's own rubric (§1.2) a
hand-audited primary read (verification 20) dominates a tool docstring's stated intent
(`tool-doc`, verification 12, directness 12). Side B's enumeration is reproduced verbatim in
source [171] and I re-ran the extractor: the count is exactly 51, unchanged at every threshold
[105] because it runs on a different code path.

**Residual that survives the adjudication:** the class is not worthless. **4 of 51 (8%) do carry a
failure rate**, and all four are plan-053's reproduction tables [176]–[179]. So the correct
statement is: *the presence of cross-pass verification prose is a convergence signal; the numeric
rate inside such prose, when present, is the study's best thrash signal.* One is a proxy for
reviewer diligence; the other is a measurement. They were being counted as the same thing.

**Downstream conclusions this invalidates:**

1. **The `tooling-notes.md` weighting instruction is reversed.** "Weight above the text-similarity
   matches" must not be carried into synthesis for thrash detection.
2. **`cluster-herdr-repo-interrogation.md` §3's confound table is partly mis-read.** It uses
   "self-reported signals" as one of three columns arguing that ceremony tracks review VOLUME:
   yoshiko-flow 29, d3-pxe 15, pybridge 4, rc-files 2, writing 1, evri_py 0, emacs.d 0 [215]. The
   column is **valid as a volume/diligence proxy** — which is what §3 actually concludes with it —
   but **invalid as a per-repo comparator of trouble**, which is how the table's framing invites
   it to be read. herdr's own §3 conclusion ("Volume, not domain, predicts multi-pass rate")
   survives; any reading of that column as "d3-pxe is in more trouble than pybridge" does not.
3. **`cluster-git-churn-signatures.md` §7's closing comparison loses one of its two supports.** It
   argues git is the weaker surface because review-pass text "already found 8 candidate episodes
   **and 51 higher-confidence self-reported recurrence signals**" [424] — an order of magnitude
   more usable signal than git's 5. The "51" half of that argument is void. **The conclusion
   survives on its other support** (git produced 0 of 20 hand-audited thrash samples, and its one
   genuine signal is "a residue that already happened") — but the specific 51-vs-5 comparison
   should not be repeated.

### 6.2 `plan-050`: a control shape or a firing bundle? — RECONCILED BY MEASUREMENT

Both sides are in the **same** artifact. §5 lists it under "Two control shapes that look like
thrash and are not"; §3 audits E19 and E20 in it as **TRUE**; the tool places it in the firing
group. Reconciled in §4.4: passes 1–5 carry all 51 findings and all 11 HIGH findings and two
verified TRUE recurrences; passes 6–13 are eight empty rounds. **The pass count is cosmetic; the
content is real.** The §5 wording should not be carried forward.

### 6.3 The ceremony-vs-trouble confound — DECLARED UNRESOLVED BY ITS OWN AUTHOR, and I leave it unresolved

`cluster-herdr-repo-interrogation.md` §3 states both readings and refuses to pick:

> "**the corpus supports both readings at different grain.** At the repo-aggregate level, ceremony
> (volume, scaffolding presence) and multi-pass rate move together — a real confound for cross-repo
> comparison. At the individual-bundle level, at least one clear counter-example (rc-files
> plan-004) shows depth tracking task stakes, not repo habit."

I have nothing that separates them either, and the bundle-level counter-evidence is n=1 [204].
**Unresolved.** Do not synthesise this as settled in either direction.

### 6.4 What `writing`'s final-verdict field means — one side is measurably wrong, the blast radius is not measured

**Side A** (any corpus-wide verdict count, including the recurrence cluster's "186 REVISE, 83
APPROVE" census [104] and herdr's own §5 table): a bundle's last pass says `REVISE`.
**Side B**, herdr §2, on direct read of the same bundles [207]:

> "pass-2 body: `'Final status: resolved — plan revised to v4.'` / `plan.md`: `'**Status:**
> complete'` … **This is a distinct low-ceremony convention** … A naive 'last verdict field per
> bundle' metric would misclassify this bundle as unresolved thrash; it is not."

**Adjudication: Side B for the three named `writing` bundles** — a direct read of `plan.md`
frontmatter beats a regex over a verdict line. **But the blast radius was never measured.** Nobody
checked how many of the other 111 bundles resolve inline. Every corpus-wide verdict statistic in
this study is therefore an **upper bound on non-convergence by an unknown margin**. Flagged, not
resolved.

### 6.5 D7's threshold has no operating point — but an external tool ships one anyway

**Side A**, recurrence §2 [105]: "The candidate count falls by **5× between 0.20 and 0.35** …
There is no plateau, no knee, no natural operating point — the count is a smooth function of the
knob. **A 'signal' whose magnitude is set entirely by a tuning parameter is not yet a signal.**"
And: "**Similarity magnitude does not rank truth.** The single highest score in the corpus (0.600)
is a *productive-deepening* case."

**Side B**, prior-art [616], `unloop-mcp`: "compares fix descriptions using Jaccard similarity.
When similarity exceeds 55%, it flags a loop."

Not a contradiction about a fact — a contradiction about a **method**. **Exactly one measured
text-similarity value in this corpus reaches or exceeds 55%: the single highest score, 0.600**
(`writing/plan-010` p1→p2 [170]) — and it is hand-read as *productive deepening*, not a loop
[206]. So on this corpus `unloop-mcp`'s 55% rule would fire exactly once, and that one firing
would be a false positive. That is the defensible claim, and it is weaker than "the threshold is
unreachable here": the corpus does not show the knob is out of range, it shows the one episode in
range is the wrong kind. Combined with the absence of any plateau or knee across 0.20–0.70 [105]
— the count falls 40 → 23 → 12 → 8 → 4 → 4 → 3, monotone with only a two-point plateau at
0.45–0.55 — there is still no evidence that 55% is a principled operating point. Given [616]'s
tier (T4-OSS, 0 external validation), **the local measurement should be preferred** and the
prior-art cluster's assessment of `unloop-mcp` as "the closest fit in the whole cluster" should be
read as *closest in shape*, not *validated in mechanism*.

### 6.6 Do the three surfaces nominate the SAME bundles? — measured, and the answer is NO

This is the study's cheapest and most decisive cross-surface test, and it was not run by any
cluster. Bundle-level nomination sets, computed:

| surface | what it nominates | n |
| :-- | :-- | --: |
| review-pass recurrence (D7 @ 0.20) | bundles with ≥1 text-similarity match | **19** |
| review-pass recurrence (D7 @ 0.35) | the shipped operating point | 8 |
| review-pass recurrence (hand-audit TRUE) | bundles with ≥1 verified recurrence | 14 |
| git-churn (commit-message signal) | bundles with a revert/redo commit | **5** |
| git-churn (repeatedly-touched files) | bundles with ≥1 file at ≥3 touches | 53 |
| execution telemetry | bundles with a content-level bead reopen | **0** |

| intersection | result |
| :-- | :-- |
| D7 ∩ git churn-signal | **2** — `d3-pxe/plan-016`, `yoshiko-flow/plan-054`. Jaccard = **0.091** |
| hand-audit TRUE ∩ git churn-signal | **1** — `yoshiko-flow/plan-054` |
| D7 ∩ git repeatedly-touched | 12 of 19; Jaccard = 0.20 (and the git cluster verdicted **0 of 20** hand-audited retouches as thrash) |
| recurrence ∩ git ∩ telemetry (all three) | **0**, necessarily — telemetry nominated nothing |

**Read this as the directive frames it: near-zero overlap is equally informative, and this is
near-zero.** The strongest evidence this study could have produced — the same episode independently
nominated by three unrelated surfaces — **does not exist in this corpus.** Exactly **one** bundle
(`yoshiko-flow/plan-054`) is nominated by two independent surfaces and confirmed by hand-audit.
`plan-054` is therefore the single best-evidenced thrash episode in the study, and n=1.

The three surfaces are not measuring the same thing. Whether that is because two of them are blind
or because the phenomenon is only visible in one, this corpus cannot say.

---

## 7. `[insufficient evidence]` findings

### 7.1 `[insufficient evidence — 1 cluster, n=1 bundle]` D2, the reproduction rate

The strongest signal any cluster identified, and the thinnest. plan-053's per-pass rates
[176]–[179]:

| pass | rate | verbatim |
| --: | :-- | :-- |
| 2 | 9/14 = 64% | "**9 of 14.** All four (c)-class failures are **RE-002's shape** — a global property repaired at the one site the reviewer named." [176] |
| 3 | 9/15 = 60% | "**9 of 15 (60%), against pass 2's 9 of 14 (64%) — this round did slightly WORSE.**" [177] |
| 4 | 7/14 = 50% | "**64% → 60% → 50%. The rate did not improve; it fell by the largest margin yet.**" [178] |
| 5 | 9/10 = 90% | "**64% → 60% → 50% → 90%. The method change is real and it worked.**" [179] |

**How much weight can one bundle carry? Very little as evidence, and quite a lot as a
specification.** Bounding it honestly:

- **Every point estimate is from n=10–15 and the intervals swallow the trend.** 9/14 = 64% [95% CI
  39–84%] · 9/15 = 60% [36–80%] · 7/14 = 50% [27–73%] · 9/10 = 90% [60–98%]. **The first three
  intervals overlap almost entirely.** The 64→60→50 "fall" — the sequence the directive correctly
  identifies as load-bearing — **is not distinguishable from noise at this n.** Only the 90% is
  separated from the 50%, and barely (intervals touch at 60%).
- **It is one bundle of 114.** The recurrence cluster measured that only **6 bundles in 114 contain
  any reproduction/verification section at all** (17 files, 6 bundles) [188], and only plan-053
  produced a trend. My own exact-heading scan found **2 bundles** carrying `## Reproduction of
  pass-N`; the difference is a definition width, and it makes the point sharper, not softer.
- **It is not residue.** "It is an **instrument to install**, not residue to mine." Its four data
  points exist because one reviewer chose to compute them.

**What it does survive.** D2 is the only candidate that is **structurally immune to the size
confound** — it is a ratio, so plan length cancels algebraically — and it is the only measurement
in the corpus that "move[d] in the thrash direction while the difficulty proxy move[d] the other
way" (open findings ran 14→15→14→10 while the rate fell). **That argues for installing the
instrument and re-measuring, not for shipping a detector built on n=1.** Carry it as a
recommendation, never as a validated signal.

### 7.2 `[insufficient evidence — 1 cluster; precision never audited]` D1's false-positive rate

D1 is one of only two signals that survived the size control (§2.4), and its precision is
unmeasured. The recurrence cluster is explicit: "**D1 was measured, not validated the way D7
was.** I hand-read the ~20 instances quoted above and they are all genuine, but I did not audit
all 54. Its false-positive rate is `[uncertain]`."

**My reimplementation supplies the first evidence on this, and it is not reassuring.** 53 signals
across 18 bundles (against the cluster's 54 across 16 [183] — an independent near-reproduction).
Scored against the hand-audit label over 79 multi-pass bundles: **TP 10, FP 8, FN 4 → PPV 10/18 =
56% [95% CI 34–75%]**, sensitivity 71% [45–88%]. **Materially worse than D3's 69% PPV**, though
the intervals overlap.

**The specific problem: the cluster's own bundle list shows D1 firing on three clean controls.**
[183] enumerates `plan-041` (3 signals), `plan-042` (5), `plan-043` (1) — and §5 of the same
artifact presents exactly those three as the textbook convergence cases, with HIGH counts running
3→0→0, 4→2→0 and 4→1→0→0 [181]. The cluster identified a plausible mechanism without connecting it
to these bundles: "the one suspicious shape I saw is a *positive* verification written with a
negation word ('C1 resolved (residual N3: …)')" [195]. **D1's earliness advantage over D3 is real
and measured; its precision advantage is asserted and, on this evidence, does not hold.**

### 7.3 `[insufficient evidence — 1 cluster, n=1]` burst-then-gap-then-correction commit timing

git-churn §5, self-flagged: "**This is n=1.** I looked for the same shape around the other 4
tool-detected churn signals and did not find a comparably clean burst-gap-correction pattern in
any of them" [418]. Compounded by an unverified rebase risk that would invalidate the timestamps
the shape rests on.

### 7.4 `[insufficient evidence — 1 cluster, n=11 bundles, causation disclaimed]` `writing`'s question-with-default pattern causing low churn

`writing` has the corpus's **lowest** direction-change rate (3/11 = 27% [10–57%]) and is also the
repo that invented the "Operator decisions to confirm at approval (defaults in brackets)" section
[524]. The operator cluster states the limit itself: "I cannot prove causation from n=11." The
interval on 27% spans nearly 50 points.

### 7.5 `[2 clusters — reported, below the certification bar]` the mid-flight batching gate

The single most actionable design proposal in the study, supported by **two** clusters, so not
certified:

- operator-breakthrough: "**The corpus's own best answer is a mid-flight batching gate**, not a
  pre-flight interview" [524], resolved in one phase-log line ("D1=both new, D2=both,
  D3=seed-only") [525].
- prior-art, independently: `grilling`'s **G3 batched-round asking** and **G4 recommended-default
  annotation** [602], graded "**Yes** … Directly portable" and "Strong fit" in its transfer table.

**Tension 4 asked whether this is genuine convergence or coincidence of framing. It is genuine
convergence of MECHANISM, on two independent artifacts, discovered by two clusters that did not
share sources.** The two artifacts are structurally identical on the two moves that matter — batch
the open decisions into one boundary, and ship each with a proposed default the operator can
accept rather than derive. `writing` plan-005's D1/D2/D3-with-defaults [524] *is* a frontier round
with recommended answers.

**Two limits keep it below certification.** (a) The prior-art source [602] is **T1-primary for its
own content and nothing else** — it is one author's skill file, carrying no evidence that the
technique works. (b) The local evidence is n=2 bundles in one repo, with causation explicitly
disclaimed (§7.4). And the two artifacts **disagree on timing**: `grilling` is pre-task ("Do not
act on it until the user confirms"), while `writing`'s gate fires *after* a draft exists — which is
the operator cluster's own conclusion, since "**T1 is 38% of all events and 80% of it arrives after
a draft exists**."

### 7.6 Other 1-cluster findings, carried but not certified

| finding | cluster | support |
| :-- | :-- | :-- |
| No prior art detects clarification-need from post-hoc execution residue | prior-art | 1 cluster, an absence over 6 queries; T1/T2 sources |
| Interruption-breakpoint principle applies to operator attention | prior-art [622][623] | 1 cluster; T1-peer-reviewed, but transferred **by analogy** — both papers model interrupting a human's own task |
| T9 "taste" as an operator-information category | operator | n = 1–3 instances |
| rc-files plan-004 proves review depth tracks task stakes | herdr [204] | n=1; the counter-evidence in §6.3 |
| T6 loop-bound override is "the purest thrash-breaking turn" | operator [513] | 17 of 18 in yoshiko-flow, 7 in one bundle; a yf-ceremony artifact |
| Pre-elicited scoping decisions do not reduce churn (mean passes 3.05 vs 2.42) | operator | 1 cluster; self-declared confounded, not deconfoundable |

---

## 8. What this corpus cannot answer

1. **Whether context exhaustion causes thrash — in either direction.** No token counts, no session
   boundaries, no compaction markers exist anywhere in the corpus (C2). Already known; confirmed by
   four clusters.
2. **The RECALL of any detector.** Only precision was ever measured. 8 multi-pass bundles extract
   **zero** findings and are invisible to every finding-based signal [105][180]; the
   letter-paragraph shape is a documented unfixed parser gap [102]; 85 parse warnings stand. **No
   statement in this study bounds how many thrash episodes were missed.**
3. **Whether the agent thrashed or the reviewer was slow.** "Under the rival 'the agent converged
   fast and the *reviewer* was slow', the residue would look identical: same passes, same re-raised
   concerns. Nothing in a plan bundle can separate them."
4. **Whether asking a question earlier would have helped.** The corpus records **answers and almost
   never questions** [502], there is no counterfactual arm, and the one measured instance of early
   asking is a *failure*: "operator selected all four fixes — but that selection was made **before**
   EXP-001 existed" [503].
5. **Whether low-ceremony repos thrash less.** herdr states the exact fork and cannot close it:
   "(a) low-volume repos genuinely thrash less, (b) 14 bundles is too few to expect even one
   recurrence episode at this corpus's base rate (~8/79 ≈ 10%), or (c) some interaction of both.
   The data cannot distinguish (a) from (b)."
6. **Any duration, latency or concurrency question.** Blocked by two filed, open defects — `started_at`
   present on 86 of 225 beads and unexposed by `bd list --json` [319], and batch closes collapsing
   84% of observed overlap [304]. These are bugs to fix, not corpus properties to work around.
7. **Whether phase-log churn is a signal.** The artifact does not exist in the required shape:
   `log.md` in 37.7% of bundles [316], 0–2 entries each, written once retrospectively [317][318].
   Neither supported nor refuted.
8. **What happens to plans that are abandoned, or that end after one pass.** 30 of 114 bundles are
   single-pass and excluded by construction; emacs.d `plan-001` was **reframed and parked**
   mid-review with `Status: drafting` and no pass-2 — "a third category the recurrence extractor
   cannot see at all." If thrash ever ends in abandonment, this study is blind to it.
9. **Whether any of this survives a different git workflow.** No squash-merging anywhere in the
   corpus — 89 merge commits of 697 in yoshiko-flow, every Issue-level commit preserved [423]. "a
   squash-merging team would destroy essentially all of the intra-branch churn this retrieval
   measured."
10. **Cross-repo frequency, for anything.** Four of seven repos have 3+-pass-rate intervals wider
    than 40 percentage points (C4). Only yoshiko-flow and d3-pxe are estimated at all.
11. **Whether the two surviving detectors work outside the largest plans.** §2.3: in the bottom
    half of the size distribution (38 of 79 multi-pass bundles) severity-decay **never fires**, D1
    fires twice, and one bundle carries a TRUE label. **The detectors are untested below ~42 KB of
    `plan.md`, because there is nothing there to test them on.**
12. **Whether the residue is even the right instrument.** No cluster observed a session. Two
    clusters measured the residue being *wrong* — about who acted [501] and about what happened
    [303]. The study's method has a measured, nonzero error rate against ground truth it cannot
    otherwise see.

---

## Amendment log

### 2026-08-28 — §6.5 corrected (red-team finding RT-5)

**What changed.** §6.5 asserted that `unloop-mcp`'s 55% Jaccard threshold sits "at a threshold
above every value ever measured here". That is **false**, and it was contradicted two sentences
earlier by the same subsection, which names 0.600 as the corpus's single highest similarity score.
0.600 > 0.55.

**Why.** The red-team critique (`artifacts/critique.md`, RT-5, HIGH) identified the contradiction;
it was carried verbatim into `Summary.md` §6.3, where it was the entire premise of the "one
external mechanism this corpus falsifies" claim. Re-derived from [170] (the complete list of
matches at threshold 0.35, which necessarily contains every value ≥ 0.55): exactly one measured
text-similarity value, 0.600, reaches the threshold, and [206] hand-reads that episode as
productive deepening rather than a loop.

**The corrected claim** is narrower: on this corpus the 55% rule's *only* firing would be a false
positive — not that the threshold is unreachable. `Summary.md` §6.3 was rewritten to match.

**Nothing else in this artifact was altered.** The §6.5 verdict (prefer the local measurement;
`unloop-mcp` is closest in shape, not validated in mechanism) is unchanged, because the corrected
premise still supports it.
