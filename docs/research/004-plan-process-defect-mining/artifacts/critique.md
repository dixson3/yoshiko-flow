---
type: Research Artifact
phase: critique
research: 004-plan-process-defect-mining
produced: '2026-08-16'
okf_spec: OKF-RESEARCH
---

# Red-team critique of `Summary.md`

Adversarial review of the draft report. `plan.yaml` was not read (deliberate exclusion).
Inputs: `Summary.md`, `sources.md`, `sources.json`, and all five cluster artifacts plus
`triangulation.md`.

**Overall verdict: the report overclaims in four specific, fixable places — a repo-count rule it
states and then violates, a "ranked by cost" claim with almost no cost evidence, a review-quality
reversal built on one bundle in the self-studying repo, and an un-triangulated fifth cluster whose
deltas are flagged 900 lines away from where they are used.** It does *not* overclaim in the ways
one would expect: prevalence discipline, the emacs.d qualification, the M8a "not a defect" verdict,
the git-subject quarantine, and the honest `[insufficient evidence]` on Q3 are all intact and should
be left alone. Quote fidelity was machine-checked against `sources.md` + artifacts and is good; only
two alterations were found.

Severity legend: `high` = misstates the evidence or contradicts the report's own stated rule;
`medium` = weakens a load-bearing claim or hides a limitation; `low` = accuracy/consistency polish.

---

## MUST-FIX BEFORE PUBLICATION

### MF-1 — The stated rule "repo counts exclude emacs.d" is violated by four of the report's own counts

- **Location:** L168 (ranking preamble), L121–122 (Bound 2), ranking table rows 1, 2, 3, 5, 11
  (L172, L174, L176, L182), L36 exec summary, L799–803 (Q2).
- **Problem:** The corpus has exactly five repos. The ranking preamble says **"Repo counts exclude
  emacs.d, which is a coverage floor"** and Bound 2 says *"Every repo count below excludes it unless
  stated."* Yet the table gives M5 = 5, M9 = 5, M10 = 5, M14 = 5 and M6b = "5 of 5 eligible", and Q2
  says "**M5** and **M9** — all five repos", "**M10** — five repos". A count of 5 is only reachable
  by *including* emacs.d. Worse, M10's own mandatory caveat (L369) says *"Weight the pybridge, d3-pxe
  and emacs.d instances"* — counting emacs.d explicitly, two lines after the section that excludes
  it. The exec summary (L34–36) likewise says the headline class "appears in all five repositories."
- **Severity:** `high`. This is the exact overstatement triangulation §4.3 / §6.4 prohibits, and the
  report states the prohibition itself.
- **Required change:** Pick one convention and apply it mechanically. Recommended: report counts as
  `N of 4 measurable repos (+emacs.d: <present as absence | unmeasurable>)`, and drop the blanket
  "repo counts exclude emacs.d" sentence in favour of a per-row note. Every "five repos" phrasing
  must be re-derived or re-worded.

### MF-2 — M6b's "5 of 5 eligible repos" appears to be an arithmetic error

- **Location:** L174 (table row 3), L258, L801.
- **Problem:** "Eligible" (a repo with a multi-pass review surface) excludes emacs.d, leaving four.
  `cluster-cross-repo-corpus.md` (recurrence table, DC-4) says **"3 of 3 eligible"** — d3-pxe,
  pybridge, evri_py. `triangulation.md` §1 and C5 put M6b at **4 repos, already including
  yoshiko-flow** (via `history-and-upstream:24` / #135). The fifth cluster then re-confirms
  yoshiko-flow and writes "**M6b is now confirmed in 5 of 5 eligible repos**"
  (`cluster-yf-corpus-reviews.md` L238, L555) — which double-counts yoshiko-flow, or silently
  promotes emacs.d to "eligible". Either way there is no fifth eligible repo, and the report inherits
  the figure verbatim into its #3-ranked class.
- **Severity:** `high`. It is the only place the report claims a class is universal across its
  eligible population.
- **Required change:** Re-derive to **4 of 4 eligible** (d3-pxe, pybridge, evri_py, yoshiko-flow),
  or name the fifth repo and cite an instance. Also define "eligible" inline the first time it is
  used — the term is load-bearing and currently undefined in `Summary.md`.

### MF-3 — M5's "5 repos" rests on a single source whose own `Repo` field is `yoshiko-flow`

- **Location:** L34–38 (exec summary), L172 (row 1), L195, L212–217, L799.
- **Problem:** M5 is the report's headline class. Every *named instance* quoted in §1 is
  yoshiko-flow (YF7, HU24, YF20, YFR8/9/10) or d3-pxe (XR4) — two repos. The jump to five rests
  entirely on ET13, the stuck-bead grep. But `sources.md` ET13 records `Repo: yoshiko-flow`; the
  mechanism is *designed in yoshiko-flow plan-004* and shipped in yoshiko-flow's `plan_manager.py`
  (`cluster-execution-telemetry.md` §9.2), and the five-repo grep merely returned "only
  design/spec/reference text" — which is consistent with that text existing *only in yoshiko-flow*.
  Nothing in the corpus shows the sweep is **specified** in pybridge, evri_py or emacs.d. The exec
  summary's "a stuck-bead sweep **specified in every repo** and observed firing in none" (L36–37) is
  therefore unsupported by its own source, and it is the sole basis for three of M5's five repos.
- **Severity:** `high`. It inflates the top-ranked class from a demonstrated 2 repos to a claimed 5.
- **Required change:** Either (a) cite a per-repo specification of the sweep in each of the five
  repos, or (b) restate M5 as "2 repos with named instances, plus a corpus-wide mechanical absence
  over a yoshiko-flow-specified mechanism," and re-rank accordingly. Delete "specified in every
  repo" unless (a) is done.

### MF-4 — "Ranked by recurrence and cost": cost is asserted, not evidenced, and it is what moves the ranking

- **Location:** L20, L164–190 (heading, preamble, table), L310.
- **Problem:** The preamble promises ranking on recurrence *and* "cost (what the instance actually
  broke, and what it consumed to find)". The table has **no cost column**. Cost is stated for only
  3 of 16 classes: M6b (a red-team pass in three repos — the only genuinely evidenced cost, DC-4),
  M9 ("its cost is this research project"), and M1 ("its per-instance cost is **the highest in the
  report**" — a comparative superlative with no measurement and no comparator anywhere). Thirteen
  classes carry no cost statement at all. And cost is exactly what the ranking turns on: M1 is
  ranked **4th on 2 repos**, above M10 (5 repos, 4 clusters, high) and M11 (4 repos, 4 clusters,
  high). Remove the unevidenced cost assertion and M1's placement has no stated basis.
- **Severity:** `high`. A reader taking "ranked by recurrence and cost" at face value is being sold
  an ordering the evidence does not produce.
- **Required change:** Say so plainly. Either add a `Cost evidence` column that is empty for the
  13 classes that have none, or re-title the section "ranked by recurrence, with cost noted where
  the corpus states it" and add one sentence: *the ordering is recurrence-primary; where a class is
  ranked above its recurrence (M1), the displacement is an editorial judgment about severity, not a
  measured cost.* Delete or evidence "the highest in the report".

### MF-5 — The un-triangulated fifth cluster is flagged once, 900 lines from where it is used

- **Location:** L137–160 ("Method corrections applied after triangulation"), L58–62 and L32–41
  (exec summary), L170–190 (ranking table), L760–776 ("Clears the bar"), L1134–1137 (the
  single-source list).
- **Problem:** The report acknowledges the structural issue only in "Reconciliation with research
  003 → A methodological tension worth naming" (L1058–1064), where it correctly says readers
  "should weight the five deltas in 'Method corrections' as single-cluster claims." That flag does
  not appear where the deltas are actually used:
  - The "Method corrections" section itself (L143–155) presents all five as settled, with no
    single-cluster marker.
  - The ranking table gives M2b `high` and M6b `high` — both upgraded by YFR — with no marker.
  - The exec summary (L58–62) states the review reversal as fact.
  - **Six of the seven "Clears the bar" bullets** (L760–776) rest wholly or partly on YFR sources
    (YFR30, YFR31, YFR2/3, YFR5, YFR24, YFR20) with no marker.
  - The report's own end-of-document "Single-source or single-cluster claims flagged in-text" list
    (L1134–1137) names M14b, M6c, M8b and plan-042 — but **omits** the calibration reversal, the
    M2b-in-yoshiko-flow confirmation, and the M6a-in-yoshiko-flow confirmation, all of which are
    YFR-only and un-cross-checked.
- **Severity:** `high`. This is the report's most likely place to overclaim and it is the one the
  report half-defends against.
- **Required change:** Add a one-line marker at the head of "Method corrections" (*"These five
  deltas come from a cluster commissioned after triangulation; none has been cross-checked against
  another cluster"*), add a footnote marker to the affected ranking rows and the affected
  "Clears the bar" bullets, and extend the L1134 list to include the calibration reversal and the
  M2b/M6a yoshiko-flow confirmations.

### MF-6 — The review-quality reversal is generalised from one bundle in the self-studying repo

- **Location:** L55–64 (exec summary), L155, L876–911, L946–949.
- **Problem:** The section is titled "Weak on executable commands — **refuted as a property of
  review**" and the exec summary calls it "the single most useful calibration the corpus yields."
  Check the sources: YFR2, YFR3 and YFR29 are **all three from `plan-039`**; YFR28 is one stated
  reviewer instruction in `plan-040` pass 3. So "reviewers there run the criterion, report its exit
  code, and demand a negative control" (L59) is generalised from **one bundle plus one instruction
  line**, in the repo the report itself designates as self-selected — and, per
  `cluster-yf-corpus-reviews.md` §5, in the recency band where this repo had already started
  looking for exactly this. The same self-selection warning the report applies rigorously to M6c
  (L553–557) is not applied here, and the conclusion here is *flattering* to the self-studying repo
  rather than incriminating. Two further problems: (a) the counter-evidence survives in the text
  (XR5 quoted at L882, XR6 at L325) but the report never says the other three repos were *not*
  assessed on the run-vs-read axis, so "a property of a review practice that reads" is asserted
  about repos nobody measured on it; (b) triangulation §6.10 never claimed a universal, so
  "refuted" overstates what was reversed — a single counterexample refutes a universal, but the
  calibration was a tendency.
- **Severity:** `high`.
- **Required change:** Retitle to "**Not universal** — one yoshiko-flow bundle demonstrates review
  that runs" (or similar). State the source concentration explicitly: *the reversal rests on three
  concerns in `plan-039` plus one reviewer instruction in `plan-040`, all yoshiko-flow, all in the
  repo's most recent multi-pass band*. Add: *no cross-repo source was assessed on the run-vs-read
  axis, so the "practice that reads" attribution is a hypothesis, not a measurement.* Demote from
  "the single most useful calibration the corpus yields" in the exec summary.

### MF-7 — "d3-pxe already persists the equivalent as a real `pass-0-conformance.md` file" is uncited

- **Location:** L586–587 (M14b), L770–771 (Q1 "Clears the bar"), L844–845 (Q3).
- **Problem:** This claim is load-bearing for M14b's remedy ("the contract already exists; another
  repo already does it") and appears three times. It is cited to **YFR24** (locator:
  `plan-041/reviews/pass-1.md` — yoshiko-flow) and to **YFR34** (locator:
  `docs/plans/*/reviews/` — yoshiko-flow). Neither source can support a fact about d3-pxe. A grep
  for `pass-0-conformance` across `cluster-cross-repo-corpus.md`,
  `cluster-history-and-upstream.md` and `cluster-execution-telemetry.md` returns **nothing** — the
  string exists only as an unsourced aside inside the yoshiko-flow-only cluster.
  `[uncited — possible model knowledge]`.
- **Severity:** `high` (it is the entire "trivially preventable" argument for M14b).
- **Required change:** Either produce a d3-pxe locator (`docs/plans/*/reviews/pass-0-conformance.md`)
  and add it as a source, or delete the d3-pxe clause from all three locations and rest M14b's
  remedy solely on "the conformance reviewer already emits a `PASS|INCOMPLETE` contract; it is not
  persisted."

### MF-8 — The "held blind to 003" claim is not verifiable for the cluster that most needs it

- **Location:** L979–984, L1012–1031 ("004 found what 003 did not"), L1058–1064.
- **Problem:** The report asserts *"**Every** retriever in this project was held blind to
  [003]"* and "004's findings were therefore derived without seeing 003." Three clusters record
  explicit blind-mining compliance (`cluster-execution-telemetry.md` L16;
  `cluster-yf-corpus.md` L418 withholds candidate 43 by name). **`cluster-yf-corpus-reviews.md`
  records no blind-mining statement at all** — it contains no mention of 003 — and it is the
  cluster commissioned *after* triangulation, i.e. the one whose retriever operated closest in time
  to a synthesizer that had 003 in scope. Two of the four "004 found what 003 did not" items
  (item 6, the `close_cascade` deadlock via YFR5; item 6's second half, M14b via YFR24) come from
  exactly that cluster. The report's independence claim is therefore weakest precisely where it is
  used most aggressively.
- **Severity:** `high`.
- **Required change:** Soften the universal: *"Three of the five clusters record explicit
  blind-mining compliance; the fifth (`yf-corpus-reviews`) does not, and its contributions to this
  section should be read as un-attested on that axis."* Do **not** delete the section — the
  corroboration items sourced from the four pre-triangulation clusters (items 1, 3, 4, 5, 7) are
  unaffected.

### MF-9 — A withheld remediation candidate was never resolved at reconciliation

- **Location:** the "Reconciliation with research 003" section (L977–1074).
- **Problem:** `cluster-yf-corpus.md` L418 explicitly parks candidate 43 — *"plan-039 → research
  003 | **WITHHELD — blind-mining rule** … Flagged so the synthesizer knows a candidate exists here
  and can resolve it at reconciliation."* The reconciliation section never mentions it. A
  deliberately deferred item that silently disappears is a process defect of exactly the class this
  report ranks fifth (M10).
- **Severity:** `medium-high`.
- **Required change:** Resolve it in the reconciliation section (confirm or reject
  plan-039 → research-003 as a remediation pair), or state that it remains unresolved and add it to
  the "What this research could not establish" table.

---

## SHOULD-FIX

### SF-1 — Absence claims: two of three are well-described, one is not falsifiable as stated

- **Location:** L215–217 (ET13), L565–569 (M14), L75–83 (M9), L926–929 (YFR35).
- **Assessment, claim by claim:**
  - **"Zero cross-plan-epic `discovered-from` edges"** (ET6, XR29) — search fully described
    (53/53 edges checked, 423 beads / 72 epics in d3-pxe). **Sound. Leave alone.**
  - **"No review pass names a defect in a different bundle"** (YFR35) — the search *is* described
    in `sources.md` (`grep 'plan-0[0-9][0-9]'` over every bundle's `reviews/`, excluding self, 63
    hits, each classified). **Sound**, but the description lives only in `sources.md`; the Summary
    states the conclusion. Pull the grep into the Summary text.
  - **"The stuck-bead sweep has never fired"** (ET13) — **not falsifiable as stated.** The search
    is a grep over *plan bundles*. A sweep that fires resets a bead's state and prints to a live
    coordinator session; by design it writes nothing into a plan bundle. So the grep's null result
    is close to guaranteed regardless of whether the sweep ever ran, and the report's phrasing "no
    log line, **no close reason**, no finding" implies a surface (bd close reasons, coordinator
    session output) the search did not cover.
  - **"No artifact anywhere records 'this review missed X'"** (M14) — **no search described
    anywhere**, in the Summary or in `cluster-yf-corpus.md`'s Absences. This is the report's
    11th-ranked class and it is an absence with no stated method.
- **Severity:** `medium`.
- **Required change:** For ET13, add the scope limit in one clause (*"over plan bundles; a sweep's
  runtime output is not an artifact any method here reads, so this is an absence of record, not a
  demonstrated absence of firing"*). For M14, state the search that produced it or downgrade its
  confidence from "high as an absence".

### SF-2 — Per-class repo counts are asserted without naming the repos

- **Location:** ranking table (L170–190), Q2 (L795–803).
- **Problem:** Several counts cannot be reconstructed from the report's own quotes. M10 = "5 repos"
  but the section quotes yoshiko-flow (HU13, YF3), d3-pxe (HU21), pybridge (ET6) and emacs.d
  (HU19) — **evri_py is never shown**. M5 = "5 repos" shows two (MF-3). A reader cannot audit the
  generality claims that carry the report's whole argument.
- **Severity:** `medium`.
- **Required change:** Replace the bare `Repos` integer with the repo initials (e.g. `yf, dp, pb,
  ep`) or add a per-class repo list line under each section.

### SF-3 — Two limitations from the source clusters never reach the report

- **Location:** "What this research could not establish" (L1078–1098).
- **Problem:** Missing from the table:
  1. **`cluster-execution-telemetry.md` L414: "Denominator is 55, not 83. 28 bundles have no
     attributable bead graph. All rates are over the 66% that do, and are therefore optimistic
     about coverage."** Every telemetry-sourced figure in the report (M9's 0-of-53, M8b's
     post-pour finding, the Q3 shared-substrate answer) inherits this and the report never says so.
  2. **The 24 unlinkable bundles' molecule↔bundle attribution** (ET4, retriever-flagged
     `[uncertain]` in triangulation §5) — dropped entirely.
  3. **"31 of 45 yf candidates neither confirmed nor rejected"** (triangulation §5) — the report
     says "unconfirmed extractor candidates carry no finding here" (L737) but never states how
     large the unadjudicated remainder is.
- **Severity:** `medium`.
- **Required change:** Add all three rows.

### SF-4 — The fifth cluster's 35 sources are 100% `high_trust`, unscored, and self-graded on a circular basis

- **Location:** L1107–1121 (Credibility model + table).
- **Problem:** `sources.json` confirms all 35 `yf-corpus-reviews` entries carry
  `credibility_score: null`, `credibility_category: null`, `credibility_rubric: null` — only a
  free-text `credibility` string written by the retriever. The report discloses this, which is
  good. But three things do not survive the four-axis rubric in `triangulation.md` §0:
  1. **35 of 35 `high_trust`, zero `verify`** is anomalous against every scored cluster
     (cross-repo 25/30, yf-corpus 10/27, telemetry 12/15, history 20/28). No cluster in this corpus
     is that uniform.
  2. **The grading is circular in at least one case.** YFR2's `credibility` reason reads *"Directly
     refutes the cross-repo claim that review reads rather than runs"* — the source is graded
     high-trust in part *because* it supports the retriever's own reversal. Under the
     self-interest axis that is a downgrade signal, not an upgrade one.
  3. **The self-interest axis is inverted for the review-quality sources.** The cluster's own
     preamble notes *"several passes below are about review quality because the plan under review
     is about review quality."* A review pass reporting favourably on review practice, inside the
     self-selected repo, in a bundle whose subject is review practice, is **self-serving**, not
     against-interest. YFR2, YFR3, YFR28, YFR29 should be `verify`, not `high_trust`. (By contrast
     YFR12, YFR13, YFR14 — first-person self-attributed regressions — genuinely clear the
     against-interest bar and should stay `high_trust`.)
- **Severity:** `medium`.
- **Required change:** Either score the 35 on the same four axes, or add one sentence to the
  Credibility model: *"The 35 YFR sources were self-graded by their own retriever with no
  adjudication; the four carrying the review-quality reversal (YFR2, YFR3, YFR28, YFR29) are
  self-serving on the self-interest axis and should be read as `verify`."*

### SF-5 — Two quote-fidelity defects

- **Location:** L436–437 (YFR20) and L676 (YF11).
- **Problem:** A machine diff of all 72 blockquotes against `sources.md` + artifacts found the
  quotes overwhelmingly faithful. Two exceptions:
  1. **YFR20 (L436–437)** renders as a verbatim quote: *"… the disconfirming grep over `SPEC.md`
     returns **nothing**. …"*. The source says *"`grep -n "rerun-if|build\.md" SPEC.md` returns
     **nothing**"* (locator `build\.rs`); "the disconfirming grep" is the *retriever's credibility note* wording, spliced
     into the quotation. Paraphrase presented as verbatim.
  2. **YF11 (L676)** renders *"`yf self install` reports ok"*; the source is *"`yf self install`
     reports `{"status":"ok"}`"* — an unmarked elision inside a quote.
- **Severity:** `medium` for (1), `low` for (2).
- **Required change:** Restore both to source wording, or move the paraphrase outside the quote
  marks.

### SF-6 — The exec summary states M5 absolutely, against the report's own mandatory counter-evidence

- **Location:** L33–34.
- **Problem:** "**a written rule that nothing executes is reliably skipped**". The class section
  carries the mandatory counter-quote (L226–231: *"the same prose reconciled correctly for plan-040
  and plan-041 … the variable is agent diligence, not a deterministic bug"*) and correctly says
  "The supported claim is *unreliable*, not *broken*". The exec summary — the part most readers
  stop at — states the strong form.
- **Severity:** `medium`.
- **Required change:** Add "unreliably" / "often" to the exec summary sentence, or append the
  one-clause counter-evidence there.

### SF-7 — "The four `questionable` sources, none of which carries a finding" is inaccurate

- **Location:** L1129–1132, cross-check L96–99.
- **Problem:** HU27 is cited in **Bound 1** to support *"Precision and recall both fail on the one
  pair that git can prove"* — which is a finding (class M13, and it is the load-bearing evidence
  for "83 candidates is not a denominator"). The intended meaning is presumably "none supports a
  defect-class or prevalence claim."
- **Severity:** `low-medium`.
- **Required change:** Reword to *"none of which supports a defect-class or prevalence claim; HU25–27
  are cited only as evidence about the extractor itself (M13)."*

---

## NICE-TO-HAVE

- **NH-1 — Two different "83"s collide.** The title says "across **83 plan bundles**"; the body says
  "**83 candidates** is not a denominator" (L94) and triangulation says "43 of the 83 bundles". If
  the bundle count and the extractor candidate count are genuinely both 83, say so explicitly,
  because as written a reader will assume the report is asserting a rate over its own bundle
  population — the exact error Bound 1 forbids. `low`.
- **NH-2 — Denominator drift.** "9 of 40 bundles fail" (L626), "one bundle" from XR27's "one bundle
  in 40" (L90), and "43 bundles" (L142) are three different populations (yoshiko-flow at YF9's
  retrieval date, cross-repo's non-yf 40, yoshiko-flow on 2026-08-16). Disambiguate inline. `low`.
- **NH-3 — M11 is ranked as a defect class but presented as "the corpus's positive finding"**
  (L177, L380). Consider a visual marker in the table (as done for M8a's `—` row) so the ranking
  does not read as "the sixth-worst defect is the thing that worked". `low`.
- **NH-4 — M14b's "Across the other 92 passes the conformance layer appears as a one-word banner"**
  (L580–581) is supported by `cluster-yf-corpus-reviews.md` L471–472 but is not attached to a
  citation in the Summary. Add the YFR34/cluster anchor. `low`.

---

## Where the report is RIGHT — do not "fix" these

A refiner working through the list above should be told plainly which criticisms would be unfair, so
that defensive over-hedging does not damage genuinely sound work:

1. **The two structural bounds are stated before any finding, not buried.** Putting M9 (the recall
   bound) and self-selection at L68–133, ahead of the ranking, is the correct structure. Do not move
   or shorten them.
2. **Prevalence discipline holds throughout.** No percentage, no "N% of plans", no rate derived from
   83. Triangulation §6.1/§6.2 are obeyed everywhere I checked.
3. **The emacs.d "coverage floor, not clean" framing is correct and correctly evidenced** (HU19,
   HU20, XR28). The *only* problem is that the exclusion rule is then not applied (MF-1) — the
   framing itself is right.
4. **M8a is correctly refused as a defect** (L710–731), matching triangulation §4.2 and §6.7, with
   both clusters' independent negative results quoted. Do not soften this into a defect.
5. **The git-subject instruments are correctly quarantined** (L124–133), including the 100%
   false-negative revert finding. Do not reintroduce any fix-density or revert signal.
6. **The self-flagged non-corroboration of #147** (L1066–1074) is exemplary — the report identifies
   a corroboration that is likely 003's own downstream artifact and refuses to bank it. This is the
   single best passage in the report. I looked for other cases of the same shape and found the
   `close_cascade`/YFR5 item (item 6) to be the main additional risk, which MF-8 covers; items 1, 3,
   4, 5 and 7 are genuinely independent.
7. **Q3 is answered `[insufficient evidence]`** (L855–859) rather than confabulated from adjacent
   material, and it names the retrieval leg that would settle it. Leave as is.
8. **Counter-evidence travels with the classes that need it** — M5 (L226–231) and M6a (L506–508)
   both carry their mandatory counter-quotes inline. This is exactly right; the only gap is the exec
   summary (SF-6).
9. **M2a and M2b are kept unpooled**, with the opposite-remedy rationale stated twice (L476, L633).
   Correct per triangulation §2.1.
10. **Quote fidelity is high.** 72 blockquotes were diffed against the source ledger; only the two
    defects in SF-5 surfaced. Do not re-verify the rest.
11. **`[uncertain]` usage is disciplined.** Both live tags (M6c generality, plan-042) are escalated
    into the "could not establish" table rather than left dangling. No `[uncertain]` needs resolving
    or escalating beyond what SF-3 adds.
