---
type: Research Report
description: Synthesis for yf-research 005 — the under-specification hypothesis's
  headline prediction is null on every length-derived proxy this corpus supports (the
  construct itself is unmeasured), cross-surface convergence is unobservable because
  two of three surfaces are near-blind, two signals survive the plan-size control
  weakly and only in the largest quartile, and the design recommendation for yf-judgement
  is conditional on an exact-match severity predicate. Revised after red-team critique;
  dispositions recorded in the final section.
okf_spec: OKF-RESEARCH
idx: '005'
topic: thrash-detection-and-operator-judgement
---

# Detecting agentic thrash: signals, operator judgement, and the design basis for `yf-judgement`

## Orientation — what this study is, and what it is not

**`yf-judgement` is a PROSPECTIVE skill that does not exist.** This report is its design basis, not
a description of it. The intended job: detect, from a plan's own recorded residue, that the agent
is thrashing and needs operator judgement — then construct the question that would break the loop.
Every recommendation in §7 is a recommendation *for a thing not yet built*, and §7.5 recommends not
building the detector first.

**The headline is a NULL on objective LENGTH, not a refutation of the under-specification
construct.** This distinction is load-bearing and the red-team's top finding (RT-1 / RT-2, and the
dispositions table at the end). An earlier draft framed the result as a refutation of the
operator's hypothesis; that framing is **withdrawn**. What is measured, and holds, is that
objective *word count* does not predict thrash. Specification *quality* was never measured — this
corpus cannot measure it independently of length (§9, item 13).

**Everything here reasons from residue, never from observed behavior.** The predecessor study
(yf-research **004**, `docs/research/004-*` in the yoshiko-flow repo) established the boundary this
one inherits: a plan bundle records **artifacts, not live session behavior**. Thrashing happens
inside a session and the session is not retained; what survives is indirect — recurring review
findings, bead reopens, revision oscillation, commit churn. No claim below is an observation of a
loop in progress.

**`yoshiko-flow#264` (§8) is OPERATOR INPUT ASSESSED HERE, not a conclusion of this study.** It is
a GitHub issue on the `dixson3/yoshiko-flow` repository proposing an N-hop escalation architecture.
Nothing in the corpus proposed it; §8 states it as given and then tests it.

### Vocabulary a reader outside this repo will need

| term | what it is |
| :-- | :-- |
| **plan bundle** | a versioned directory produced by the `yf-plan` skill — `plan.md` plus `context.md`, `reviews/`, `references/`. The unit of analysis; the corpus is 114 of them. |
| **review pass** | one `reviews/pass-N.md` file inside a bundle: an adversarial review of the plan, carrying a finding table with a severity column, an Operator Resolutions section, and a verdict line. 301 of them; the study's richest surface. |
| **`bd` / beads** | the issue tracker these repos use for execution tracking. Its status-change history is the "execution telemetry" surface — which this study finds blind (§4.3). |
| **direction change** | a hand-coded event where the work's direction shifted after operator input; 119 were coded (`artifacts/cluster-operator-breakthrough-turns.md`). |
| **`yf-herdr`** | an existing skill that runs a subordinate agent session in a separate terminal pane, seeding `YF_PARENT_PANE`. It supplies the *channel* §8's proposal would escalate over. |
| **thrash** | the phenomenon under study. §5 Q1 reports it is largely **misnamed**: most verified episodes are *partial landings*, not oscillation. |

The **evidence architecture** — six retrieval clusters, only three of which mine a bundle-nominating
surface, two of those three near-blind — is diagrammed here and expanded in §4:

![Evidence architecture: six clusters, three surfaces, near-zero overlap](diagrams/evidence-architecture.png)

---

## How to read the citations

Numbered citations resolve to [sources.md](sources.md) — 228 sources, of which 205 are local
corpus artifacts scored on the local evidence-strength rubric (STRONG / MODERATE / WEAK) and 23
are web sources carrying an adjudicated credibility tier. Claims resting on a `WEAK` local source
or a T4 web source are tagged `[uncertain]`.

Many quantities in this report are **recomputations performed by the triangulation pass itself**
rather than by a retrieval cluster; those have no source id and are attributed to
`artifacts/triangulation.md` by section. Nothing here is an observation of a live session: 004's
boundary holds throughout.

> "004 is the direct predecessor and its boundary is the starting constraint: it found that plan
> bundles record ARTIFACTS, not live session behavior — thrashing happens in a session and leaves
> only indirect residue." [100](sources.md#100)

`[uncertain]` — [100](sources.md#100) is WEAK-band (it is a statement of this study's own method,
not an observation of the corpus).

---

## Executive summary

**The operator's hypothesis's headline prediction is null — as this study operationalised it.**
Objective **word length** does not predict thrash: **r = −0.002** between initial-objective length
and direction-change count (`artifacts/triangulation.md` §3.3, from the operator-breakthrough
cluster). That is a real, reproducible null and it refutes *objective length as a predictor*. It
does **not** refute the hypothesis's construct, and this report does not claim that it does. Two
limits bound the claim, both at the point it bites:

- **Construct.** Word count is not specification quality, and this report's own two exhibits show
  the two coming apart in both directions: pybridge `plan-008`'s **9-word** objective converged in
  one pass [527](sources.md#527) `[uncertain]` (WEAK-band, n=1), while d3-pxe `plan-016`'s
  **22-word**, SPEC-anchored objective produced 8 passes [530](sources.md#530) `[uncertain]`
  (WEAK-band, n=1). A null on a proxy that
  the exhibits show is orthogonal to the construct licenses no verdict on the construct. **This
  corpus cannot measure specification quality independently of specification length** (§9, item 13).
- **Instrument.** The "initial" objective is really the **first-committed** objective, and *"the
  first committed `plan.md` is usually post-review, not the initial draft"* [545](sources.md#545) —
  `sources.md` records this on the objective sources themselves, including
  [530](sources.md#530). The text measured is downstream of the very revision process whose cause
  is under test, and the pre-review text was never recovered. **The r = −0.002 null is therefore
  itself `[uncertain]` on instrument grounds.**

The only cluster that adjudicated the hypothesis against a rival table graded it *"**WEAKLY
SUPPORTED, and not where predicted**"* (`cluster-operator-breakthrough-turns.md` §6), on the
grounds that specification *density* correlates at r = −0.278 (direction changes) and −0.319
(passes). Triangulation restated that as *"not a basis on which to build a detector"*
(`artifacts/triangulation.md` §3.3). **No new measurement was taken at any step, so no step may
strengthen the claim** — and this report's earlier "refuted" framing did exactly that. It is
withdrawn.

The two supporting measurements are also nulls, not reversals. The natural experiment on the 40
bundles with pre-elicited scoping decisions gives **1.43 vs 1.42 direction changes**, and the
pre-elicited group took *more* review passes, **3.05 vs 2.42** — but treatment plans were longer
and more explicitly scoped than controls (`artifacts/triangulation.md` §7.6; single-cluster,
self-declared confounded and not deconfoundable, and reported with no dispersion statistic), so
the honest reading is that **pre-elicitation's benefit is not visible above the size effect**, not
that it harms.

What outperforms every specification measure computed here is **task difficulty and decision
count** — with the caveat in §3.2 that this corpus cannot separate difficulty from context
pressure, because both would be measured by the same number. Plan size accounts for a large share
of the rank variance in review-pass volume (ρ = 0.739 as reported [189](sources.md#189), ρ = 0.792
/ 0.601 on recomputation — at the lower bound ρ² = 0.36, a *minority* of rank variance, so "most
of the variance" holds only at the top of the range), and *"Issue count is the strongest predictor
of both direction changes (r=+0.43) and review passes (r=+0.55) — stronger than any specification
measure"* (`artifacts/triangulation.md` §C1).

**One qualified survivor, at one-third the confounder's size, and pointing the other way from the
hypothesis's own mechanism.** Once plan length is held fixed, partial ρ(constraint count, review
passes | length) = **−0.19** (current `plan.md`) / **−0.24** (first-committed)
(`artifacts/triangulation.md` §3.2). That residual is real and is not being zeroed out to tidy the
verdict — but **raw constraint count is the wrong sign** (ρ = +0.09 to +0.17: plans with *more*
stated constraints have *slightly more* review passes), so what survives is constraint
**concentration**, not constraint **presence**. Specification density's own negative sign is
inherited from its `1/length` denominator: length alone gives ρ = −0.60 to −0.79 against churn when
inverted, larger in magnitude than density's entire raw correlation of −0.39 to −0.42. This is not a
basis on which to build a detector.

**The study's own evidentiary strength is the second headline, and it is also negative.** Three
independent surfaces were mined — review-pass text, git churn, and `bd` execution telemetry — and
they do not nominate the same bundles. Jaccard between the text-similarity and git-churn nomination
sets is **0.091** (2 bundles); hand-audit TRUE ∩ git-churn is **1**; the three-way intersection is
**0**, because telemetry nominated nothing at all. Exactly **one** bundle
(`yoshiko-flow/plan-054`) is nominated by two independent surfaces *and* hand-confirmed — n=1
(`artifacts/triangulation.md` §6.6). But the reason matters and this report states it in
triangulation's own words rather than its earlier, stronger one: **two of the three surfaces have
near-zero sensitivity, so this design could not have produced convergent evidence** — *"whether
that is because two of them are blind or because the phenomenon is only visible in one, this
corpus cannot say"* (`artifacts/triangulation.md` §6.6). Convergent nomination by unrelated
surfaces is the strongest evidence this design could have produced, and it is **unobservable
here**, which is not the same as absent (§4.2 gives the overlap coefficient and the chance
baseline). Every signal recommendation below therefore carries, inline, the single surface it
rests on.

---

## 2. What the corpus is

**The `corpus:` block in `plan.yaml` is superseded.** Its 127 plans / 391 review passes were
measured by a scan that double-counted `.worktrees/<branch>/` mirrors of `docs/plans` in
yoshiko-flow, d3-pxe and evri_py — **86 of the 391 counted review files were worktree duplicates**.
The corrected baseline, measured by `scripts/corpus_scan.py` and reproduced exactly on
re-run, is:

| quantity | corrected value |
| :-- | :-- |
| plan bundles | **114** [103](sources.md#103) |
| review passes | **301** [103](sources.md#103) |
| repos | 7 (yoshiko-flow, d3-pxe, evri_py, writing, pybridge, emacs.d, rc-files) |
| multi-pass bundles (≥2 passes) | 79 |
| bundles reaching pass 3 | **42 of 114 = 37% [29–46%]** [103](sources.md#103) |

**The file-set definition** all downstream phases inherit (reconciled against an independent
operator recount of 305, `plan.yaml:corpus_corrected`): a review pass is any `*.md` file directly
inside a `reviews/` directory of a **real** plan bundle — glob `<bundle>/reviews/*.md`, comprising
299 `pass-N.md` files plus 2 `pass-N-conformance.md` files. Excluded: the 86 `.worktrees/**`
mirrors, and 4 synthetic OKF-migration sample fixtures under plan-029's `findings/` that were
authored *as* research data, not as review passes of a real plan. Reconciliation: 305 − 4 = 301.

The evidence-surface census confirms what the bundles carry: `context.md` in 112/114, a phase log in
113/114, `log.md` in only 43/114 [545](sources.md#545).

**The corpus is concentrated.** Certified across four clusters, evidenced in yoshiko-flow and d3-pxe
only:

> "**Every one of the 8 candidate episodes lives in exactly 3 of the 7 repos**"
> (`artifacts/cluster-herdr-repo-interrogation.md` §5)

The underlying tool output is `total_recurrence_matches: 8 (yoshiko-flow 4, d3-pxe 3, writing 1)`
[201](sources.md#201), so **7 of the 8** — not 6, as the cluster's prose stated — are in the two
highest-volume software repos. The prose figure is corrected here against the tool output it
rests on.

Per-repo 3-or-more-pass rates [213](sources.md#213): d3-pxe 13/19 = 68% [46–85%] · yoshiko-flow
23/56 = 41% [29–54%] · pybridge 2/11 = 18% [5–48%] · writing 2/11 = 18% [5–48%] · evri_py 1/9 =
11% [2–44%] · rc-files 1/4 = 25% [5–70%] · emacs.d 0/4 = 0% [0–49%]. Four of seven repos have
intervals wider than 40 percentage points. **No frequency claim in this report generalises past
yoshiko-flow and d3-pxe.**

---

## 3. The hypothesis, measured — and what the measurement can and cannot say

### 3.1 The hypothesis as stated, and each prediction it made

The hypothesis: *thrashing correlates with an under-specified objective (an over-general goal, an
assumed "figure it out") rather than with task difficulty, tooling failure, or model limitation.*

**Every row below is a verdict on a *prediction as operationalised here*, never on the construct.**
Each operationalisation is named in the measurement column so the reader can see what the verdict
is about.

| prediction (as operationalised) | measurement | verdict |
| :-- | :-- | :-- |
| under-specification is visible in the **initial objective**, proxied by objective **word count** | r = **−0.002** with direction changes; text is first-committed/post-review [545](sources.md#545) | **null on the proxy** `[uncertain]` (instrument) |
| **pre-eliciting** the missing specification reduces churn | 1.43 vs 1.42 direction changes; 3.05 vs 2.42 review passes, no dispersion statistic reported | **null (confounded, uncertified)** |
| a well-specified objective produces a short review cycle | d3-pxe `plan-016`: 22-word SPEC-anchored objective [530](sources.md#530) `[uncertain]` (WEAK-band, n=1) → **8 passes, 6 operator decisions** (the pass and decision counts are the operator cluster's tally for that bundle, not part of [530](sources.md#530), which records the objective text only) | **counter-instance — confounded, carries no discriminating weight** |
| stated **constraint count** predicts less churn | ρ = **+0.088 to +0.170** at n=109 — neither value distinguishable from zero (p ≈ 0.36 and p ≈ 0.08) | **null** |

Three qualifications belong with the table, not below the fold.

**The 40-bundle natural experiment** is single-cluster and its author declared it confounded and
not deconfoundable (`artifacts/triangulation.md` §7.6): treatment bundles were longer and more
explicitly scoped than controls, which is the size confound running through the treatment
assignment. The result is therefore *not* evidence that pre-elicitation harms — it is evidence that
**pre-elicitation's benefit is not visible above the size effect**, which is the weaker but honest
claim. The table row says `null`, not `wrong direction`, for that reason.

**The constraint-count row is a null, not a refutation.** At n = 109 a ρ of +0.088 or +0.170 is not
distinguishable from zero, and no interval or test was computed for either. Calling it "the wrong
sign" would give it an epistemic status this report explicitly denies to a residual of comparable
magnitude (the −0.19/−0.24 partial, §3.2) merely because the two point in opposite directions. Both
are reported as what they are: small coefficients at a sample size that cannot resolve them.

**The counter-instance is confounded and discriminates nothing.** `plan-016` is also this report's
exemplar for two rival explanations *on the same bundle*: the missing-capability rival — *"HALTED at
the 'SPEC amendment approved' and 'AWS + 1Password write authority' capability gates — neither
resolved. 22 open tasks remain, all gate-blocked"* [533](sources.md#533) — and genuine domain
underdetermination [531](sources.md#531), [532](sources.md#532). If its eight passes are explained
by blocked capability gates and by forks that could not be posed until a measurement ran, the bundle
is not evidence that good specification fails to prevent churn; it is evidence that other causes
dominate *there*, which is compatible with under-specification being one cause among several. It is
retained as an illustration and carries **no discriminating weight**.

### 3.2 What outperforms it: plan size and decision count — under a name this corpus cannot verify

**A naming caution, stated before the numbers.** What is measured is **`plan.md` byte count** and
**issue count**. Calling that "task difficulty" is an interpretation, and it is not the only one:
a longer plan and a longer review chain also consume more of a session's context window, so the
same number is at least as plausible a proxy for **context pressure** — which §5's rival table
correctly marks *untestable in this corpus, in every direction*. This report therefore does **not**
declare a winner among the rivals; declaring one would assert that the unmeasured rival lost. What
the data support is narrower and still decisive for the hypothesis: **plan size and decision count
account for more of the variance in review-pass volume than any specification measure computed
here. Whether that variance is difficulty, context pressure, or both, this corpus cannot say.**

Certified across **four clusters** (recurrence, operator-breakthrough, herdr, git-churn), evidenced
in all 7 repos:

> "**Spearman ρ(review-pass count, `plan.md` size) = 0.739 over 109 bundles**"
> [189](sources.md#189)

Independent recomputation gives ρ = **0.792** on the current `plan.md` and **0.601** on the
first-committed `plan.md` recovered from git — all large, all same-signed. Neither is a clean
pre-work difficulty proxy, because *"the first committed `plan.md` is usually post-review, not the
initial draft"* [545](sources.md#545); ρ = 0.601–0.792 bounds it.

The per-band evidence is a step function, not a gradient [189](sources.md#189):

| review passes | bundles | median `plan.md` bytes | % firing the recurrence detector |
| :-- | --: | --: | --: |
| 1 | 30 | 16,398 | 0% |
| 2 | 37 | 19,790 | 5% |
| 3–4 | 23 | 35,758 | 22% |
| 5+ | 19 | 62,461 | **63%** |

and by review-text volume rather than plan size: 0 findings → 0%, 1–20 → 12%, 21–50 → 44%, 51+ →
**86%** [190](sources.md#190).

The recurrence cluster states the corollary plainly:

> "**'Many passes' is not, on its own, a thrash signal.** It is a description of a large plan"
> [103](sources.md#103)

### 3.3 The stratified table — and why this is a study of 22 bundles

Firing rates by `plan.md` size quartile over the 79 multi-pass bundles
(`artifacts/triangulation.md` §2.3):

| quartile | n | `plan.md` bytes | D7 text-similarity | D1 back-reference | HIGH at pass ≥3 | hand-audit TRUE |
| :-- | --: | :-- | --: | --: | --: | --: |
| Q1 | 19 | 13,688–19,375 | 11% | 5% | **0%** | 5% |
| Q2 | 19 | 19,685–25,514 | 5% | 5% | **0%** | 0% |
| Q3 | 19 | 25,803–41,587 | 21% | 26% | 11% | 11% |
| Q4 | 22 | 42,110–184,157 | **55%** | **50%** | **55%** | **50%** |

Severity-decay fires **0%, 0%, 11%, 55%** across quartiles; the hand-audit TRUE label runs **5%, 0%,
11%, 50%**. In the bottom half — 38 of 79 multi-pass bundles — the severity signal never fires at
all and one bundle in 38 carries a TRUE label. **In substance this is a study of the 22 largest plan
bundles.**

### 3.4 The reframing this opens

The dominant residue signature is **partial landing**, not decision oscillation. Certified across
**two independent surfaces — review-pass prose and commit messages — with cross-repo replication on
the first.** (An earlier draft of this report counted the cross-repo read as a third surface. It is
not: [208](sources.md#208) and [205](sources.md#205) are both `reviews/pass-N.md` files, i.e. a
second *reader* of the same surface, in different repos. §4 makes surface independence this
study's evidentiary yardstick, so the looser count is corrected here rather than carried.)

> "**~20 [of 24 TRUE] are PARTIAL LANDINGS** — a remedy applied at the one site the reviewer named,
> while the same defect survives elsewhere … **Absence finding, stated plainly: I found essentially
> no decision oscillation in this corpus.** One instance in 40 candidates, over 301 review passes."
> (`artifacts/triangulation.md` §C5, from the recurrence cluster's 40-episode hand-audit)

Corroborated independently in a different repo — *"**Residual C7:** the Approach `pve_lxc` bullet
**still** cites `PVE-GPU-003/005/006`"* [208](sources.md#208) — and from a commit body: *"Third
drift of one REQ inside one plan: grep gave 25, the spec asserted 24, and retrospective-report was
unenumerated"* [408](sources.md#408). Audited proportions: TRUE 24/40 = 60% [45–74%], DEEPEN 7/40 =
18% [9–32%], FALSE 9/40 = 22% [12–38%].

**A detector designed against an oscillation model targets a phenomenon this corpus does not
contain.**

---

## 4. Evidentiary strength: near-zero cross-surface convergence

This is a first-class finding about the study, not a limitation footnote. The cheapest and most
decisive cross-surface test was not run by any retrieval cluster; triangulation ran it
(`artifacts/triangulation.md` §6.6).

### 4.1 What each surface nominated

| surface | what it nominates | bundles |
| :-- | :-- | --: |
| review-pass recurrence, D7 at threshold 0.20 | ≥1 text-similarity match | **19** |
| review-pass recurrence, D7 at 0.35 (shipped operating point) | ≥1 match | 8 |
| review-pass recurrence, hand-audit TRUE | ≥1 verified recurrence | 14 |
| git churn (commit-message signal) | ≥1 revert/redo commit | **5** |
| git churn (repeatedly-touched files) | ≥1 file at ≥3 touches | 53 |
| execution telemetry (`bd`) | ≥1 content-level bead reopen | **0** |

### 4.2 What they agree on

| intersection | result |
| :-- | :-- |
| D7 ∩ git churn-signal | **2** — `d3-pxe/plan-016`, `yoshiko-flow/plan-054`. **Jaccard = 0.091** |
| hand-audit TRUE ∩ git churn-signal | **1** — `yoshiko-flow/plan-054` |
| D7 ∩ git repeatedly-touched | 12 of 19 (Jaccard 0.20) — but the git cluster verdicted **0 of 20** hand-audited retouches as genuine intra-plan thrash (cluster audit tally; [416](sources.md#416) is one audited window) |
| all three surfaces | **0**, necessarily — telemetry nominated nothing |

**Jaccard is the wrong statistic here, and reporting it alone overstates the result.** The two sets
are of size 19 and 5, so the **maximum attainable Jaccard is 5/19 = 0.263** — the observed 0.091 is
35% of its own ceiling, not 9% of anything. The size-robust statistic for nested-scale sets is the
**overlap coefficient: 2/5 = 0.40**. Against chance: with 19 and 5 nominations over 114 bundles the
expected overlap is 19 × 5 / 114 ≈ **0.83** against an observed **2**; for hand-audit TRUE (14) ∩
churn (5) the expectation is **0.61** against an observed **1** — that one is literally chance.

| statistic | D7 ∩ git churn-signal | hand-audit TRUE ∩ git churn-signal |
| :-- | :-- | :-- |
| set sizes | 19 and 5 | 14 and 5 |
| observed overlap | 2 | 1 |
| Jaccard | 0.091 (ceiling 0.263) | 0.056 (ceiling 0.357) |
| overlap coefficient | **0.40** | **0.20** |
| overlap expected by chance | 0.83 | 0.61 |

So the honest reading is the one triangulation stated and this report previously dropped:

> "The three surfaces are not measuring the same thing. Whether that is because two of them are
> blind or because the phenomenon is only visible in one, **this corpus cannot say.**"
> (`artifacts/triangulation.md` §6.6)

**Reframed accordingly: two of three surfaces have near-zero sensitivity — git nominates 5 bundles
of 114 and telemetry nominates 0 — so this design could not have produced convergent evidence.**
That is a statement about the instrument, not a finding that convergence is absent. The earlier
formulation ("the strongest evidence this study could have produced does not exist in this corpus")
converted a *cannot say* into a negative result and is withdrawn.

`yoshiko-flow/plan-054` is the single best-evidenced thrash episode in the study, and **n=1**.

### 4.3 Why the other two surfaces are silent

Certified across three clusters (`artifacts/triangulation.md` §C6), and this one *does* generalise
to all 7 repos, because the absence was measured everywhere:

- **`bd` telemetry**: 3 reopens in 2,969 recorded status changes = **0.10%**, all in one repo
  [306](sources.md#306), and all three hand-audited as tooling probes or a bead-id clerical fix.
  `bd history` is *actively misleading* — 641 of 745 entries for one bead were duplicate `closed`
  snapshots from unrelated batch commits [303](sources.md#303).
- **Git**: **0 literal `git revert` commits** — the per-repo revert tally is
  [407](sources.md#407), the 2,044-commit denominator is [423](sources.md#423); 5 churn-signal
  commits across 114 bundles = 4.4% [1.9–9.9%], of which 3 are cross-plan documentation corrections
  rather than within-plan thrash [409](sources.md#409); 4 genuine hand-authored semantic reverts,
  **all outside every tracked plan window** (the cluster's aggregate, of which
  [411](sources.md#411) is one instance); and 5 of 20 hand-audited retouch windows contaminated by
  a *different plan's* commits — the cluster's audit tally, of which [416](sources.md#416) is one
  window. The top 7 basenames
  account for 120 of 233 retouch instances and all seven are mandated hot files
  [422](sources.md#422).

**Both are health-check surfaces, not thrash-detection surfaces.** The prose residue is the only
surface that produced verified episodes.

### 4.4 The label itself is circular for one signal

The ground-truth label is the recurrence cluster's hand-audit — 14 of 79 multi-pass bundles = **18%
[11–28%]**. Only bundles that **D7 nominated** were hand-audited. A bundle that thrashed without
producing a D7 candidate is labelled negative by construction. **D7 therefore cannot be scored
against this label at all**, and every other signal is scored against a D7-filtered ground truth.
This is the strongest available label in the study and it is not a good one
(`artifacts/triangulation.md` §2.2).

**A second, weaker circularity affects every scored signal, not just D7.** The hand-audit labels
*and* the discriminator definitions (D1, D3, D6, D9) were produced by the **same cluster agent**,
with no second rater and no held-out set. Triangulation independently reimplemented D1's *code*,
which removes implementation circularity but not label circularity: the reimplementation is still
scored against labels authored by the party that proposed the signal. **Every performance number in
§6.1 and §7.2 is therefore trained and evaluated in the same hands**, and should be read as an
upper bound.

---

## 5. Answers to the research questions

### Primary Q1 — What observable signals precede a thrash episode, and which are early enough to act on?

**Two survive the size control, both weakly, both only inside the top size quartile; eleven are
ruled out.** All surviving signals read the **review-pass prose surface** — the same single surface,
which is exactly the §4 problem.

| signal | surface | partial ρ vs label, given size | within-Q4 PPV (base rate 50%) | verdict |
| :-- | :-- | --: | :-- | :-- |
| **D3 — a HIGH-severity finding at pass ≥3** | review-pass prose only | **+0.482** | 75% [47–91%] | survives, weakly; conditional on the severity vocabulary (§6) |
| **D1 — cross-pass back-reference with a failure word** | review-pass prose only | **+0.414** | 73% [43–90%] | survives, weakly; fires on three clean controls (§5, Q2) |
| **D2 — cross-pass reproduction rate** | review-pass prose only | not computable | n=1 | `[insufficient evidence]`; an instrument to install, not residue to mine |

**On earliness.** D3 is first computable at **pass 3** by definition. D1 is definable at **pass 2** —
the first pass at which any cross-pass signal exists — and **39% of all D1 signals fire there** (21
of 54) [183](sources.md#183).

**Two D1 numbers come from two different implementations, on two different populations, and the
distinction is signposted here because it changes the comparison.** The earliness figure (21 of 54)
is the *recurrence cluster's* implementation [183](sources.md#183); the corrected PPV in §6.1 (TP
10, FP 8, FN 4 → 56%) is *triangulation's independent reimplementation* (53 signals across 18
bundles). Likewise the two precision comparisons are not commensurable: **within Q4** the two
detectors are indistinguishable (73% vs 75%, intervals almost fully overlapping), while
**corpus-wide** D1's corrected PPV (56%) is 13 points below D3's (69%). Read §7.3's "13 points of
PPV" as the corpus-wide comparison and this paragraph's "indistinguishable" as the within-Q4 one.

Nothing in this corpus is detectable at **pass 1**. There is no pre-burn signal.

### Primary Q2 — Is the under-specification hypothesis true, and what would refute it?

**Not as this study operationalised it — and this study could not operationalise it any other way.**
See §3. Every prediction the hypothesis made, *as measured here*, returned a null: objective word
length vs direction changes (r = −0.002, and the text measured is post-review); the natural
experiment (1.43 vs 1.42, and 3.05 vs 2.42 passes, confounded by size); and raw constraint count
(ρ = +0.09 to +0.17, not distinguishable from zero at n = 109). The one named counter-instance,
`plan-016` [530](sources.md#530) `[uncertain]`, is confounded by two rivals on the same bundle and
discriminates nothing. What survives is a partial correlation of about −0.2 on a hand-defined
constraint-count proxy — real, one-third the confounder's magnitude, pointing at concentration
rather than presence.

**What would refute it, and why this study is not that test.** Every measure of "specification"
computed here is a **length-derived** quantity: objective word count, constraint count, and a
density that carries a `1/length` denominator. A construct-valid test needs a specification measure
that is independent of length — e.g. blind human ratings of objective adequacy on a stratified
sample — and this study did not build one (§9, item 13). So the correct reading is: *the
hypothesis's headline prediction is null on every length-derived proxy available in this corpus,
and the construct itself is unmeasured here.*

The rival explanations, adjudicated. **No rival is declared the winner**, because one of them is
unmeasurable and naming a winner would assert that it lost:

| rival | verdict |
| :-- | :-- |
| **plan size and decision count** (interpretable as task difficulty, context pressure, or both) | **Outperforms every specification measure computed here.** Four clusters, all 7 repos. Plan size ρ = 0.60–0.79; issue count r = +0.43 / +0.55. But `plan.md` byte count is also a plausible context-pressure proxy, so the *label* on this rival is not established (§3.2) |
| **missing tool / permission / authority** | Real and measured: **13 of 114 bundles carry gate-blocked residue**, of which `plan-016`'s 22 tasks stalled on unresolved human gates is the exemplar [533](sources.md#533); a wholesale mid-execution pivot caused by a missing token [534](sources.md#534). Pre-elicitable as an environmental fact, not as a specification — **but that boundary is a definitional choice, not a measurement**: an unstated environmental precondition is a species of under-specification on most readings, and nothing here adjudicates the two apart |
| **genuine domain underdetermination** | Real: **6 bundles record a fork settled by measurement rather than by argument**; the exemplar is a fork that *"was not well-posed until an experiment ran"* [531](sources.md#531), re-opened one pass later and settled by re-measurement [532](sources.md#532) |
| **context exhaustion** | **Untestable in this corpus, in every direction.** Four clusters agree. No token counts, no session boundaries, no compaction markers exist anywhere; a corpus-wide scan found 3 apparent hits, all false positives |

### Primary Q3 — When an episode broke, what broke it, and could it have been asked for beforehand?

**A qualifier that attaches to every number in this subsection and to §8.2.** The T1–T9 taxonomy,
the 119-event denominator, and every proportion derived from them are one agent's
hand-classification: *"the 119 events were classified by me, single-coder, no second rater"*, and
*"the 178→119 filter is judgement … a different filter yields different denominators"*
(`artifacts/cluster-operator-breakthrough-turns.md` §9). There is no inter-rater statistic. Under
this study's own evidence standard that is a material qualifier on 45/119, 38%, 80%, 9% and the
T6 count of 18 wherever they appear.

The dominant class of operator-supplied information is **T1 fork resolution** — the agent or
reviewer had already enumerated two or more concrete alternatives and could not rank them, and the
operator picked one. **45 of 119 classified operator events (38%), and the only category present in
all seven repos**, including the two non-software, low-ceremony ones. The shape is
domain-independent:

> "Operator confirmed **split apply mode** — K1 (token cuts) auto-applies; K2"
> [506](sources.md#506) (yoshiko-flow)

> "Leg C: pull floor-lowering in (R1 b) vs measurement-gate-only (R1 a) | high | Operator chose
> **option (a)** (2026-06-21)" [508](sources.md#508) (pybridge)

> "| C4 (auth posture) | Operator chose per-session bearer token in v1 (D7); 127.0.0.1 + Origin as
> defense-in-depth." [509](sources.md#509) (emacs.d — non-software)

> "Operator chose brew on both platforms." [510](sources.md#510) (rc-files — non-software)

**Can it be elicited before the burn? The corpus bounds where answers land, not when they became
askable.** Of the 45 T1 fork resolutions, **36 (80%) appear inside a `reviews/pass-N.md`
resolution** — they answer a fork that an independent red-team pass discovered in a plan that
already existed. Only **4 (9%)** are recorded as pre-elicited at scoping [514](sources.md#514),
[515](sources.md#515); the remaining 5 are approval-time answers to questions the plan itself had
drafted.

**Read that as the location statistic it is.** It counts where the *answer* was written down. The
source cluster's own limitation says why it cannot bear more: *"**Questions are not recorded.** The
taxonomy is reverse-engineered from answers"* [502](sources.md#502). If questions are never
recorded, "80% of answers appear in review passes" is fully consistent with the fork having been
askable earlier and simply not asked. The bridging argument — *you cannot ask "a or b" before you
know that a and b exist* — is a **logical claim, not a measurement**, and it is marked as such
here because its position immediately after a percentage previously invited it to be read as one.

Worse, asking early has a measured failure mode:

> "operator selected all four fixes — but that selection was made *before* EXP-001 existed."
> [503](sources.md#503)

Early asking did not merely fail to help there; it injected a commitment that later measurement
invalidated.

**What *is* pre-elicitable**, per the operator cluster's taxonomy: T4 risk tolerance (a standing
disposition — *"production is the line"* [520](sources.md#520) `[uncertain]`, WEAK-band), T5
authority/capability [522](sources.md#522), T7 intent [542](sources.md#542) `[uncertain]`
(WEAK-band), and T9 taste [543](sources.md#543)
`[uncertain]` (WEAK-band). And **T8 environmental/authority facts are already solved by a form, not
a question** — a `context.md` template field, present in 110 of 114 bundles
[544](sources.md#544) `[uncertain]` (WEAK-band). *Where a template field works, a question is the
wrong instrument.*

### Secondary Q1 — What do the prior-art question taxonomies offer, and what transfers?

`grilling` (the engine behind `grill-me`) decomposes into seven moves, of which four transfer to a
plan/execution context and three assume a conversational one:

> "Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already
> settled … The session is done when the frontier is empty … Do not act on it until the user
> confirms you have reached a shared understanding." [602](sources.md#602)

> "Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the
> environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for
> anything you could look up yourself. Don't block on it … The _decisions_ are the user's."
> [602](sources.md#602)

Its output format ships every question with the asker's own recommended answer, annotated `➡️`
[602](sources.md#602).

| move | transfers to a plan context? |
| :-- | :-- |
| G3 batched-round asking | **Yes** — matches the corpus's own convention (below) |
| G4 recommended-default annotation (`➡️`) | **Yes** — matches `writing`'s defaults-in-brackets section |
| G5 fact/decision separation via a dispatched sub-agent | **Yes** — an escalation predicate in miniature (§7) |
| G6 non-blocking fact-finding | **Yes** |
| G1/G2 design-tree + frontier computation | Partly — assumes a pre-task design space |
| G7 empty-frontier termination + confirmation gate | Assumes pre-task, conversational framing |

`socrates-skill` does not transfer: *"**NEVER give a direct answer.** Instead, guide the user to
discover the answer"* [604](sources.md#604). That is the inverse of what the corpus needs — an
operator being interrogated toward self-discovery is the opposite of an operator picking between two
alternatives an agent has already drafted.

The RE literature supplies the strongest portable ontology this study actually read: Derr's
question-content categories via Zaremba and Liaskos [618](sources.md#618) (existence / identity /
properties / relations / number / time / location / action). The W6H interrogative ordering
[619](sources.md#619) is named as a **lead, not a source of content**: the only text retrieved for
it is its own title, so nothing about what W6H *is* or *orders* was read here. Zhang and Choi
frame the trigger problem exactly:

> "Determining when to ask for clarification is a challenging task that requires systems to consider
> the demands of the individual user … and the distribution of interpretations for a given request"
> [606](sources.md#606)

**The strongest prior-art finding is an absence — and the search that produced it was small.**
Every "ask before acting" skill this study reached — `grill-me` [601](sources.md#601),
`clarify-skill` [621](sources.md#621) — is **opt-in and pre-task**; none auto-fires mid-execution
from residue. *"It interrogates your request with structured, clickable questions until it's
unambiguous, before any work starts"* [621](sources.md#621). **The extent of that search is six web
queries in one cluster, and triangulation classifies the finding as carried but not certified**
(`artifacts/triangulation.md` §7.6). Six queries bound a universal quantifier very loosely, so the
claim is stated here as *no prior art we reached* detects clarification-need from post-hoc execution
residue — an absence over a small search, not a proof of non-existence. On that reading the gap is
`yf-judgement`'s plausible design space.

### Secondary Q2 — What are the false-positive costs, and what discriminates thrash from convergence?

**The corpus contains textbook convergence shapes that look like thrash on every naive metric**, and
each one names a metric that must not be used:

| convergence shape | which naive signal it defeats |
| :-- | :-- |
| `plan-026` — 7 passes, REVISE/APPROVE oscillating, **zero recurrence**, each REVISE following a *deliberate scope change* [181](sources.md#181) | verdict non-monotonicity (D9). *"Verdict non-monotonicity is the signature of a re-scoped plan"* |
| `plan-041` HIGH 3→0→0, `plan-042` 4→2→0, `plan-043` 4→1→0→0 [181](sources.md#181) | any pass-count metric — and D1, which fires on all three (§6) |
| rc-files pass-2 raising *"a **fresh mechanical defect introduced by fixing pass-1**"* [205](sources.md#205) | text similarity — a new defect at the same site is convergence, not recurrence |
| the corpus's single highest similarity score (0.600) is **productive deepening** | similarity magnitude as a ranking. *"Similarity magnitude does not rank truth"* |
| three `writing` bundles whose last pass reads `REVISE` but whose `plan.md` reads `Status: complete` [207](sources.md#207) | last-verdict-per-bundle metrics |

**Measured false-positive rates.** D7 at its documented operating point: 4 TRUE of 8 = **50%
[22–78%]** [170](sources.md#170), 60% over all 40 audited, and its `id_reuse` basis is **0 for 3**
[170](sources.md#170). The threshold has no operating point at all — matches fall monotonically from
40 to 3 across 0.20 → 0.70 (40, 23, 12, 8, 4, 4, 3), with **no knee and only a two-point plateau at
0.45–0.55** [105](sources.md#105). That plateau is worth naming rather than eliding: it sits in the
exact region `unloop-mcp`'s 55% threshold occupies (§6.3).

**The most instructive false positive is one an earlier artifact recommended as the best signal.**
Tooling notes reported 51 self-reported cross-pass signals and called them the highest-confidence
class. Hand-reading all 51 inverted it:

> "**Hand-read, that is wrong.** … **47 of 51 are clean all-resolved statements** — 'All eight
> concerns resolved' … These are evidence that the previous round *worked*. … As a thrash signal it
> is **inverted**." [171](sources.md#171)

The residual is the useful part: 4 of 51 (8%) carry an actual failure *rate*, all in `plan-053`'s
reproduction tables. **The presence of cross-pass verification prose is a convergence signal; the
numeric rate inside such prose, when present, is the study's best thrash signal.** The two were
being counted as the same thing.

**The one discriminator the corpus does supply** is not a pattern but a measurement: the
reproduction rate. `plan-053`, per pass — 9/14 = 64% [176](sources.md#176), 9/15 = 60%
[177](sources.md#177), 7/14 = 50%, then 9/10 = 90% after a method change [179](sources.md#179). It
is the only measurement in the corpus that *"moved in the thrash direction while the difficulty
proxy moved the other way"*. It is also n=1 of 114, with intervals that swallow the 64→60→50 trend
entirely (64% [39–84%], 60% [36–80%], 50% [27–73%]), and only 6 of 114 bundles contain any
reproduction section at all [188](sources.md#188). **Install the instrument; do not ship a detector
on it.**

### Secondary Q3 — At which yf surfaces could a detector fire, and what does each see?

| surface | what it can see | verdict |
| :-- | :-- | :-- |
| **review-pass loop** | finding tables, severity tokens, verdicts, cross-pass back-references. The only surface that produced verified episodes: 40 candidates, 24 hand-verified TRUE | **the only viable detection surface** — and the reason §4's convergence problem cannot be fixed by adding surfaces |
| **bead reopen (`bd`)** | 3 reopens in 2,969 status changes, all tooling artifacts [306](sources.md#306) | **no measured positives at all** |
| **`discovered-from` chains** | depth 2 is the mode, max 3 anywhere, 1–7% of issues [310](sources.md#310) | a `depth >= 2` detector would fire on effectively every recorded use of the field |
| **coordinator / phase log** | `log.md` in 37.7% of bundles [316](sources.md#316), 0–2 entries, written once retrospectively | the artifact does not have the incremental shape the signal requires |
| **plan revision / git** | 0 literal reverts of 2,044 [407](sources.md#407); 0 of 20 hand-audited retouches were intra-plan thrash [416](sources.md#416) | health-check surface |
| **timing / duration** | blocked by two filed, open defects: `started_at` on 86 of 225 beads and unexposed by `bd list --json` [319](sources.md#319); batch closes collapsing 84% of observed overlap | unmeasurable until fixed |

The one thing that **does** generalise across all seven repos is the **form** of the review artifact
— finding table, severity column, Operator Resolutions section, verdict line. A detector can assume
the form everywhere; it cannot assume the frequency anywhere.

For *where* to fire, the HCI literature contributes a principle, transferred by analogy only:
interruptions are least disruptive at task boundaries — *"interfaces should be designed to a)
interrupt users at low-problem state moments"* [622](sources.md#622), and *"different interruption
moments have different impacts on user emotional state"* [623](sources.md#623). Both papers model
interrupting a human's own task, not redirecting an agent, so the cost model does not transfer; the
boundary-preference does. In the yf loop that means a review-pass boundary, a bead close, or an
approval gate.

---

## 6. Signals: what survives, and what does not

### 6.1 Survives (both read the review-pass prose surface — the only surface with verified positives)

| signal | evidencing surface | ρ with plan size | partial ρ given size | earliest computable | status |
| :-- | :-- | --: | --: | :-- | :-- |
| **D3 — HIGH-severity finding at pass ≥3** | review-pass prose (single surface) | +0.522 | **+0.482** | pass 3 | survives weakly; **conditional on the severity vocabulary** |
| **D1 — cross-pass back-reference with a failure word** | review-pass prose (single surface) | +0.484 | **+0.414** | pass 2 | survives weakly; **precision worse than asserted** |
| **D2 — cross-pass reproduction rate** | review-pass prose (single surface), n=1 bundle | — | not computable | pass 2 | `[insufficient evidence]` — install as an instrument |

D2's one structural virtue is that it is **immune to the size confound by construction**: it is a
ratio, so plan length cancels algebraically. That is why it is worth installing even though it
cannot be scored.

**D1's precision, corrected — and note which implementation each number comes from.** The
recurrence cluster measured D1 but never validated it: 54 signals across 16 bundles, present in 5 of
7 repos [183](sources.md#183); the earliness figure in §5 Q1 (21 of 54 firing at pass 2) is *that*
implementation. Triangulation's **independent reimplementation** found 53 across 18 bundles — a
near-reproduction — and scored it for the first
time: **TP 10, FP 8, FN 4 → PPV 10/18 = 56% [34–75%]** corpus-wide, sensitivity 71% [45–88%]; the
within-Q4 figure quoted in §5 Q1 (73%) is from the same reimplementation but a different
population. **It fires on
`plan-041` (3 signals), `plan-042` (5) and `plan-043` (1)** [183](sources.md#183) — the three
textbook convergence controls the same artifact presents in its own control section
[181](sources.md#181). A plausible mechanism was identified but never connected to those bundles:
*"the one suspicious shape I saw is a *positive* verification written with a negation word ('C1
resolved (residual N3: …)')"* [195](sources.md#195). **D1's earliness advantage over D3 is real and
measured; its precision advantage is asserted and does not hold.**

### 6.2 Ruled out, by name

| signal | why |
| :-- | :-- |
| **D8 — raw review-pass count** | ρ = +0.811 with plan size. It *is* the confounder's closest proxy [103](sources.md#103) |
| **D6 — non-increasing finding counts** | Within Q4, PPV 17% [3–56%], sensitivity 9% — worse than a coin flip exactly where the thrash is (`artifacts/triangulation.md` §2.3; the corpus-wide contrast it stratifies is [182](sources.md#182)) |
| **D9 — approve→revise verdict reversal** | 21% [9–43%] vs 7% [3–16%], intervals overlap heavily; and `plan-026` shows it is the signature of a *re-scoped* plan [181](sources.md#181) |
| **D7 — text-similarity recurrence (the shipped detector)** | Circular against the only label; 50% precision at its operating point [170](sources.md#170); no knee anywhere in 0.20–0.70 [105](sources.md#105); id-reuse basis 0 for 3 |
| **Total finding count** | Survives numerically (+0.411) but is a second measurement of the confounder — listing it would be listing plan size twice [190](sources.md#190) |
| **Self-reported cross-pass signal count** | Partial ρ = +0.095, and the signal is *inverted*: 47 of 51 are convergence statements [171](sources.md#171) |
| **Git churn-signal commits** | ρ with the TRUE label = +0.016; 5 hits in 114 bundles, 3 of them cross-plan corrections [409](sources.md#409) |
| **Git repeatedly-touched files** | 0 of 20 hand-audited classified as genuine intra-plan thrash; 25% window contamination [416](sources.md#416); top basenames are mandated hot files [422](sources.md#422) |
| **`bd` status reopen** | 3 in 2,969, all tooling artifacts [306](sources.md#306). **No measured positives at all** |
| **`discovered-from` chain depth** | Depth 2 is the corpus mode [310](sources.md#310) — the detector would fire on every recorded use |
| **Phase-log churn** | `log.md` in 37.7% of bundles, 0–2 entries, retrospective [316](sources.md#316). Unmeasurable, not measured-and-null |
| **Timing / duration signals** | Two filed, open instrumentation defects [319](sources.md#319) |
| **Burst-then-gap-then-correction commit timing** | n=1 [418](sources.md#418), and the shape was absent around the other four churn signals |

### 6.3 One external mechanism whose only firing on this corpus would be a false positive

`unloop-mcp` ships a mechanism this study's local measurement does not support:

> "The engine normalizes each error into a fingerprint … and compares fix descriptions using Jaccard
> similarity. When similarity exceeds 55%, it flags a loop." [616](sources.md#616) `[uncertain]`
> (T4-OSS)

**Correction to an earlier statement of this finding.** A previous draft asserted that 55% is
"above every similarity value ever measured in this corpus" and named 0.600 as the highest score in
the same sentence. That is self-contradictory and false: **0.600 > 0.55**. The error originated in
`artifacts/triangulation.md` §6.5 and was carried here verbatim; both files are now corrected (see
that artifact's amendment log).

What the corpus actually supports is narrower, and still adverse to the mechanism. **Exactly one
measured text-similarity value in this corpus reaches 55%: the single highest, 0.600**
(`writing/plan-010` p1→p2 [170](sources.md#170)) — and hand-reading it shows *productive
deepening*, not a loop: severity dropped medium→low and the second pass closes a coverage gap the
first left explicitly pending [206](sources.md#206). **So on this corpus the 55% rule would fire
exactly once, and that one firing would be a false positive.** That is a weaker claim than "the
threshold is unreachable here" — the corpus does not show the knob is out of range, it shows the
one episode in range is the wrong kind. Against it stands the separate finding that the match count
is a smooth, near-monotone function of the knob with no knee across 0.20–0.70
[105](sources.md#105), so there is no evidence 55% is a principled operating point either.

The prior-art cluster called `unloop-mcp` *"the closest fit in the whole cluster"*; on this evidence
that means closest **in shape**, not validated **in mechanism**.

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

## 10. Sources

All 228 sources, with quotes, locators, and evidence-strength bands or adjudicated credibility
tiers: [sources.md](sources.md).

**Note on the credibility scoring of the 23 web sources.** The mechanical scorer misranks this set
systematically, so an adjudicated tier is written alongside its output and used throughout this
report: peer review is invisible to it (ACL Anthology, IEEE RE 2021 and CHI 2004 all score 41,
below an unreviewed arXiv preprint's 63), and currency is uninformative (no source carries a publish
date, so all 23 scored exactly 50 on an axis worth 20% of the total). Adjudicated:
**T1-peer-reviewed 7 · T1-primary 6 · T2-preprint 5 · T4 5**
(`artifacts/triangulation.md` §1.3).

---

## Red-team dispositions

`artifacts/critique.md` raised **30 findings (8 HIGH · 13 MEDIUM · 9 LOW)**. Every HIGH is resolved.
Counts: **19 FIXED · 6 FIXED-BY-RECOMPUTE · 5 ACCEPTED-AS-LIMITATION · 0 REJECTED.**

The critique also recorded eight attacks that **failed** — the Wilson intervals (~20 recomputed, all
reproduce), the corpus census, the `plan-026` exhibit, the per-pass HIGH trajectories, the
`[uncertain]` tagging discipline, the §4.4 circularity disclosure, the 2×2 algebra, and the
`medium-high` hazard's practical effect. **Nothing in those areas was weakened.** One upstream file
was corrected: `artifacts/triangulation.md` §6.5 (RT-5), with a dated amendment note appended there.

| id | sev | disposition | note |
| :-- | :-- | :-- | :-- |
| RT-1 | HIGH | FIXED | "Refuted" withdrawn throughout. The r=−0.002 null is retained with its correct scope — objective **word length** as a predictor — and the source cluster's "WEAKLY SUPPORTED, not where predicted" grade plus the no-new-measurement escalation are now stated in the executive summary. |
| RT-2 | HIGH | FIXED | The first-committed/post-review instrument limitation [545](sources.md#545) is now stated where the null is first used, and the null itself is marked `[uncertain]` on instrument grounds in the exec summary and the §3.1 table. |
| RT-3 | HIGH | FIXED-BY-RECOMPUTE | §7.2 rebuilt as three single-population tables (n=79, n=37, n=22) plus the 17/20 cross-tab kept separate. FPR corrected to 1 − specificity: **15% → 6%** (pooled). |
| RT-4 | HIGH | FIXED-BY-RECOMPUTE | Operating characteristics recomputed on the evaluable population. **LR+ 10.4 → 3.7 (n=37) and 3.0 (Q4); specificity 94% → 83% / 73%; base rate 18% → 38% / 50%.** The "not because the base rate is favourable" clause is deleted and reversed. |
| RT-5 | HIGH | FIXED-BY-RECOMPUTE | §6.3's false premise removed. 0.600 > 0.55, so the claim is rebuilt as "the 55% rule's only firing on this corpus would be a false positive" [170](sources.md#170), [206](sources.md#206). `triangulation.md` §6.5 corrected + amendment note appended. |
| RT-6 | HIGH | FIXED | Condition restated as an **exact-match** predicate on the lowercased stripped severity cell, with the `medium-high` / `med-high` / `med/high` / `medium(→high)` variants named as the reason and the survival guarantee explicitly corpus-dated to 2026-08-28. Verdict unchanged, per the critique's own partial retraction. |
| RT-7 | HIGH | FIXED | "Task difficulty is the winner" removed. §3.2 and §5's rival table now say plan size and decision count **outperform every specification measure computed here**, and name the context-pressure reading of the same proxy; no rival is declared a winner. |
| RT-8 | HIGH | FIXED | §8.2 row 1 split into its two propositions, the N-hop conjunct graded **Untested**. The 80% is restated as a location statistic with [502](sources.md#502)'s "questions are not recorded" attached, and the bridging argument is labelled a logical claim, not a measurement. |
| RT-9 | MED | FIXED | The constraint-count row is relabelled `null` with p ≈ 0.36 / 0.08 at n=109, and the asymmetric treatment against the −0.19/−0.24 residual is named and removed. |
| RT-10 | MED | FIXED | Table verdict changed to `null (confounded, uncertified)`; the missing dispersion statistic is stated in the row. Table and paragraph no longer contradict. |
| RT-11 | MED | FIXED-BY-RECOMPUTE | §4.2 adds the **overlap coefficient (0.40 and 0.20)**, the Jaccard ceilings (0.263, 0.357) and chance baselines (0.83, 0.61), and restores triangulation's blindness/absence disjunction. §4 reframed to "could not have produced convergent evidence". |
| RT-12 | MED | FIXED | §3.4 corrected to **two** independent surfaces with cross-repo replication on the first; the miscount is named rather than silently changed. |
| RT-13 | MED | FIXED | [501](sources.md#501) band corrected STRONG → **MODERATE**; [303](sources.md#303) dropped from C3 as an export artifact; the local base is now stated as **n = 1** and "the blog corroborates the reasoning, not the result" is withdrawn. |
| RT-14 | MED | FIXED | Verified against `plan-050/log.md` directly (`cycles=` 4, 9, 9, 9, 10, 11, 12). The amplification analogy is **withdrawn**; the propagation-budget requirement now stands as a pure design requirement with no corpus analogue. |
| RT-15 | MED | FIXED | The `plan-016` counter-instance is retained as illustration and explicitly marked confounded by two rivals on the same bundle, carrying **no discriminating weight**. |
| RT-16 | MED | FIXED-BY-RECOMPUTE | Blockquote re-attributed to the cluster artifact; **"6 of the 8" → "7 of the 8"** against [201](sources.md#201)'s own tally; per-repo pass rates re-cited to [213](sources.md#213) (both here and in §7.4). |
| RT-17 | MED | FIXED | Single-coder / judgement-filter qualifier added at the head of §5 Q3 and carried into §8.2. |
| RT-18 | MED | ACCEPTED-AS-LIMITATION | The corpus-wide count was never run and cannot be conjured. §8.4 item 1 and §9 item 4 now state this as the cluster's **assertion** plus an n = 1 illustration, and say the count remains undone. |
| RT-19 | MED | FIXED | Corpus-level counts restored (**13/114** gate-blocked bundles; **6** bundles with a fork settled by measurement) and the missing-permission / under-specification boundary is stated as a definitional choice this corpus does not adjudicate. |
| RT-20 | MED | ACCEPTED-AS-LIMITATION | The four strict-`high` false positives were not hand-read; §7.1 now says so and states that "passes the shippability test" means "passes on `plan-026`". Doing the read is named as outstanding work. |
| RT-21 | MED | FIXED | Search extent stated inline ("six queries, one cluster, uncertified"); the universal weakened to "no prior art we reached"; §8.2 grade downgraded to **Supported, weakly**. |
| RT-22 | LOW | FIXED-BY-RECOMPUTE | "No plateau" corrected: the sweep is 40, 23, 12, 8, 4, **4**, 3, i.e. monotone with a **two-point plateau at 0.45–0.55** — in exactly the region `unloop-mcp`'s threshold occupies. Fixed in Secondary Q2, §6.2 and §6.3. |
| RT-23 | LOW | FIXED-BY-RECOMPUTE | **62% → 63.2% [54–71%]** (72 of 114 from [103](sources.md#103)'s distribution 0:5 1:30 2:37). |
| RT-24 | LOW | FIXED | Citation scope corrected on the revert denominator ([407](sources.md#407) → [423](sources.md#423) for 2,044), the semantic-revert and retouch aggregates (exemplar labelled as such), the Q4 D6 figures (triangulation §2.3), and the `plan-016` decision count. |
| RT-25 | LOW | FIXED | `[uncertain]` added to [530](sources.md#530) at the §3.1 table row; T7 intent now cited to [542](sources.md#542) with its WEAK-band tag. [527](sources.md#527) tagged where newly introduced. |
| RT-26 | LOW | FIXED | [619](sources.md#619) demoted from "supplies an ontology" to a **lead**, with the fact that only its title was retrieved stated inline. |
| RT-27 | LOW | FIXED-BY-RECOMPUTE | Unusable-severity count **185 → 204 of 1,509 (13.5%)**, itemised as 185 none + `— 14` + `gap 3` + `missing 2` from [104](sources.md#104). |
| RT-28 | LOW | FIXED | "Explains most of the variance" qualified in place: at ρ = 0.601, ρ² = 0.36 — a minority of rank variance — so the phrase holds only at the top of the stated range. |
| RT-29 | LOW | FIXED | Which D1 implementation and which population each figure comes from is now signposted in §5 Q1, §6.1 and §7.3; the "indistinguishable (73/75)" and "13 points of PPV" comparisons are explicitly labelled within-Q4 and corpus-wide. |
| RT-30 | LOW | FIXED | §4.4 now names the **label** circularity alongside the D7 filtering circularity: labels and discriminators authored by the same agent, no second rater, no held-out set; §6.1 and §7.2 numbers flagged as upper bounds. |

**Three things the critique credited and this revision preserved deliberately:** the −0.19/−0.24
residual is still reported against the report's own narrative interest; the `plan-050`
reconciliation is still stated without choosing a side; and D1's precision loss is still reported
even though D1 has the better latency story.
