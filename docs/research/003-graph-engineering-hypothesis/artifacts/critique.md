---
type: Research Artifact
okf_spec: OKF-RESEARCH
okf_version: '0.1'
---

# Red-team critique of `Summary.md`

Research project `003-graph-engineering-hypothesis`, bead `yf-mol-afb`. Reviewed artifacts:
`Summary.md` (draft, 764 lines), `sources.json` (89 entries), and — for citation-fidelity
verification only — `artifacts/triangulation.md` and `artifacts/cluster-*.md`. `plan.yaml` was not
read.

**Overall verdict: refinable, not rework.** The draft is unusually disciplined about its own limits
— the quarantine section, the independence audit, the `[insufficient evidence]` markers, and the
"What is NOT established" section are genuinely good epistemic practice and should survive refinement
intact. But four defects are load-bearing on the report's *strongest-stated* conclusions, and one of
them (C-2) is a verifiably false factual claim. Every citation link in the document is also broken.

## Severity index

| # | Severity | Section | Defect |
|:--|:-------|:--------|:-------|
| C-1 | Critical | All | 249 of 249 citation links point at a non-existent `sources.md` |
| C-2 | Critical | Exec summary; Rank 1 | "The defect class recurred **after** the prose corrective was written" is false — same commit |
| C-3 | High | Exec summary; Rank 1 | Rank 1 rests on n=2 solid legs, below the report's own 3-source consensus bar, yet is called "strongest" |
| C-4 | High | Exec summary; Rank 1 | `REQ-AGENT-047` does not contain a "runtime executor" decision; the "two bundled decisions" framing invents one |
| C-5 | High | Q1 | "Typed node, declared edge, conditional edge, run-scoped state across eight independent systems" is contradicted by the source table |
| C-6 | High | Rank 5; Q3 table | The measured-shape data contradicts the use made of it to depress Rank 5 |
| C-7 | High | Credibility skew | Domain-authority deflation is systemic (20+ sources), not "two visible inversions" |
| C-8 | Medium | Sources; `sources.json` | `sources.json` was never updated with the § 3.2 manual adjustments |
| C-9 | Medium | Rank 1; validator gap | "Contradicted" overstates what three peer systems can establish |
| C-10 | Medium | Q3; SQ1 non-opportunity | `questionable`-tier `CE-13` carries conclusions alone, against the rubric |
| C-11 | Medium | Q1; C1 quotes | Load-bearing block quotes drawn from the weakest comparative source |
| C-12 | Medium | Q3 | Self-measurement of the report's own epic is undisclosed |
| C-13 | Medium | Various | Uncited assertions — possible model knowledge |
| C-14 | Low | Q3; SQ2 | Undefined "Tier A/B/C" terminology |
| C-15 | Low | Credibility skew | Comparative-execution median is 68, not 67 |
| C-16 | Low | Q1 | "Independently corroborates" overstates a single source's assertion |
| C-17 | Low | Exec summary | "89 sources" inflates the external evidence base |

---

## C-1 (Critical) — Every citation in the report is a broken link

**Section:** entire document. **Offending pattern:** `[PT-8](sources.md#pt-8)` and 248 others.

`sources.md` does not exist in `docs/research/003-graph-engineering-hypothesis/`. The directory
contains `sources.json` only. `markdown_lint.py Summary.md` reports **249 violations, all ML003
broken link targets**, i.e. 100% of the report's citations. The report also asserts the file exists:

> "Full metadata, quotes, and per-source credibility notes are in `sources.json` (89 entries) and its
> rendered form `sources.md`."

A report whose citations cannot be resolved by a reader fails the citation requirement at the
mechanical level regardless of how well-sourced the underlying claims are.

**Required change:** either generate `sources.md` with anchors matching `#pt-N` / `#fw-N` / `#ce-N` /
`#yf-N`, or retarget all 249 links. Then re-run the full linter (not the authoring subset — ML003 is
excluded from the subset) and require zero ML003.

## C-2 (Critical) — A verifiably false chronology claim, load-bearing on Rank 1

**Section:** Executive summary and "Rank 1 — Separate the two decisions bundled in `REQ-AGENT-047`".

**Offending lines:**

> "and yf's own record shows the exact defect class such a validator catches recurring after a prose
> corrective was written ([YF-42], `skills/yf-plan/spec/agents.md:72`)."

> "Direct verification of `skills/yf-plan/spec/agents.md:72` adds that **"The same cycle was
> independently reproduced in this skill's own plan-039 draft"** — the defect class recurred *after*
> the prose corrective was written. And the corrective (`REQ-AGENT-046`) is another prose contract of
> the same kind that already failed twice"

This is false, and checkably so. `git log -L 70,74:skills/yf-plan/spec/agents.md` shows
`REQ-AGENT-046` — its requirement line, its rationale, and the plan-039 sentence itself — were all
introduced by a **single commit**, `d2b4a10` ("plan-039 Epics 1,2,4.1: SPEC amendments ..."). The
plan-039 reproduction is the event that *motivated* writing the corrective; it did not occur after
it. No prose reachability corrective existed at the time of either plan-013 or plan-039.

The knock-on error: "another prose contract of the same kind that **already failed twice**" conflates
two ordinary red-team *cycles* that contained no reachability check at all with two failures of a
reachability contract. `REQ-AGENT-046` has never been tested against a recurrence — which is a
weaker and different claim than the one made.

The report itself flags the correct residual open question one paragraph later ("does
`REQ-AGENT-046`'s prose reachability check actually fire? No test exists") — that is the supportable
form, and it should replace the recurrence claim rather than sit beside it.

**Required change:** delete the "recurred after the prose corrective" claim from both the executive
summary and Rank 1. Replace with the supportable statement: the same defect class was observed twice
before any reachability contract existed, and `REQ-AGENT-046` — the contract written in response —
carries a documentation-check Verification clause and has no behavioural test.

## C-3 (High) — The strongest-stated conclusion rests on evidence the report's own bar demotes

**Section:** Executive summary; "Pre-run structural validation — the clearest gap"; Rank 1.

The report's stated consensus bar is **3+ independent artifacts** — it applies that bar to demote C9
(references-not-payloads, n=2) and C10 (fork/time-travel, n=2) to `[insufficient evidence]`, and
lists both under "What is NOT established" item 5.

The pre-run-validator finding has the same arity. The report's own body says so:

> "The third leg — AutoGen's `Cycle detected without exit condition` — is **provisional**: the
> framework retriever surfaced the issue title only and never fetched the body ... The two solid legs
> are `verify`-tier first-party docs quoting a shipped API."

Two solid legs. Yet the executive summary states it without the hedge —

> "Three independent shipped systems ship a pre-run structural validator"

— and Rank 1 labels the evidence "**strongest in the assessment.**" The same n=2 that produces
`[insufficient evidence]` in one place produces "strongest" in another. This is the report's single
most serious *reasoning* defect: its top-ranked opportunity is carried by evidence its own rule
disqualifies for consensus.

**Required change:** apply the bar consistently. Either (a) restate Rank 1's external evidence as
"2 first-party legs + 1 provisional, below the consensus bar", and rest the ranking explicitly on the
internal yf record (which, per C-2, must itself be corrected), or (b) resolve the AutoGen leg by
fetching the issue bodies via a gap-fill retrieve. The executive summary must not say "three
independent shipped systems" while the body says two.

## C-4 (High) — The "two bundled decisions" framing is not in the source

**Section:** Executive summary; Rank 1.

> "It is that yf's rejection of a DAG walk (`REQ-AGENT-047`) bundled two separable decisions —
> rejecting a runtime *executor* and rejecting a pre-run *structural validator*"

Read at `skills/yf-plan/spec/agents.md:74-77`, `REQ-AGENT-047` is a requirement on the **red-team
review agent**: "for each issue, the artifacts, tools, and capabilities its text assumes are either
produced by a declared `depends-on` predecessor or established by a gate." Its rejected alternative
("a `requires:` key plus a walk engine") is an *authoring-time / review-time* structural check of the
plan graph. Nothing in the requirement, its rationale, or its Verification clause concerns a runtime
executor. The report invents one of its two "bundled" decisions and then reports the invented axis as
"unresolved (X3)".

A second, related gap: `FW-1`'s `.compile()` and `FW-12`'s event-graph validation validate a
**runtime graph program** before executing it. yf's analogue would validate a `plan.md`/bead DAG at
review time. The report never establishes these are the same kind of artifact or that the checks
transfer — it treats the analogy as given.

**Required change:** rewrite the framing. `REQ-AGENT-047` rejects a pre-run structural validator,
full stop; that is one decision, not two. The runtime-executor discussion (`PT-6`, `FW-8`, `FW-12`
vs. `FW-14`/`FW-18`, `FW-9`) is real and interesting but belongs in its own subsection, not as a
component of `REQ-AGENT-047`. Add an explicit sentence acknowledging that the transfer from
"validate a runtime graph before running it" to "validate a plan DAG at review time" is an argument
by analogy that no source in the corpus makes.

## C-5 (High) — The "eight systems" convergence claim is contradicted by its own source table

**Section:** Executive summary; "The implementation vocabulary *is* converged"; Verdict on Q1.

> "the shipped-framework corpus shows a small converged *implementation* vocabulary (typed node,
> declared edge, conditional edge, run-scoped state) across eight independent systems"

> "The framework cluster inventoried 8 systems' shipped API surfaces and found a small converged core
> — typed node, declared edge, conditional edge, run-scoped state — implemented under 8 different
> names."

`artifacts/cluster-framework-evidence.md` § "The primitive vocabulary" does not support "8". Its own
table records:

- **Static edge (declared successor):** DSPy = `none`. LlamaIndex = "inferred from event types" (not
  declared). So the primitive is not present in 8 systems and certainly not "under 8 different names".
- **Shared state with merge rule:** AutoGen GraphFlow = `—` (no evidence found).

The cluster's own wording is carefully hedged and the Summary drops the hedge:

> "Four primitives appear, independently named, in every **graph-native** system surveyed"

"Graph-native" excludes the two systems the cluster elsewhere calls "the two that reject graphs"
(LlamaIndex, DSPy). The defensible count is 6, and the fourth primitive is absent from AutoGen. The
report also weakens this further in its own caveat paragraph (independent framework legs reduce to
four after removing LangChain) without ever propagating that back to the headline number.

**Required change:** replace "eight independent systems" with the count the table actually supports,
name the exceptions inline (DSPy has no declared edge; LlamaIndex derives rather than declares;
AutoGen shows no run-scoped state in the retrieved material), and restate the Q1 verdict's
"(strong, mechanically checkable, 8 systems)" accordingly.

## C-6 (High) — The measured-shape data contradicts the use made of it in Rank 5

**Section:** "Measured shape of the emitted graphs" and "Rank 5 — Parallel dispatch of the ready set".

> "The measured yf shapes bound the ceiling: research epics have exactly one wide layer of width 4-5,
> and plan epics are near-trees [YF-20]."

`YF-20`'s raw quote in `sources.json` is:

```
yf-mol-y7f layers= 16 widths= [13, 1, 1, 4, 4, 3, 4, 1, 1, 1, 2, 1, 1, 1, 1, 1] max_width= 13
yf-mol-e9q layers= 9  widths= [11, 2, 2, 6, 10, 1, 1, 2, 1]                    max_width= 11
```

`yf-mol-e9q` has **mid-graph layers of width 6 and 10** — layers 3 and 4, not the container-inflated
layer 0. That is the opposite of a ceiling argument: the report's own measurement shows a plan epic
with a ten-wide concurrently-available layer. Rank 5 uses the measurement to argue the ceiling is
low; the measurement argues the ceiling is high for at least one of the two plan epics sampled.

Two further problems in the same table:

1. The **Max layer width** column reports 13 and 11 for the two plan epics — both are layer 0, which
   the report itself immediately says is "inflated by *container* epics, which carry no dependency
   edges at all [YF-21]". The table therefore publishes a number the surrounding prose disclaims, and
   publishes no number that supports the "near-tree" reading.
2. `yf-mol-e9q` is labelled bundle `plans/plan-0xx`. That is not a resolvable identifier; the
   measurement cannot be re-verified against a real bundle.

**Required change:** (a) add the per-epic widths vector (or a container-excluded max) to the table so
both readings rest on the same disclosed data; (b) resolve `plan-0xx` to a real bundle path or state
why it is withheld; (c) rewrite the Rank 5 evidence sentence — the honest form is that research epics
have a low ceiling (one layer of width 4–5) while the two sampled plan epics differ sharply from each
other (max non-container widths 4 and 10), so the corpus does not bound the ceiling at all. Rank 5's
ranking may still stand on the "no source establishes parallel dispatch improves any outcome" leg,
which is sound; it must not stand on this one.

## C-7 (High) — The domain-authority artifact is systemic, not "two visible inversions"

**Section:** "Credibility skew by cluster".

> "Domain authority is a URL-shape heuristic producing two visible inversions — [FW-13] (CrewAI) ...
> [PT-13] ... was lifted to 76 by `arxiv.org`'s Tier-1 weighting"

Checked against `sources.json`, the heuristic assigned `domain_authority: 30` to **every** source not
matching a `docs.<vendor>.com` hostname, including these first-party vendor documentation sources:

| Source | Host | Assigned DA | Rubric tier for "official docs" |
|:-------|:-----|--:|:--------------------------------|
| FW-10, FW-11 | `burr.apache.org` | 30 | Tier 2 (70–84) |
| FW-12 | `developers.llamaindex.ai` | 30 | Tier 2 |
| FW-14, FW-15, FW-18 | `google.github.io` / `raw.githubusercontent.com/google` | 30 | Tier 2 |
| FW-8 | `ai.pydantic.dev` | 30 | Tier 2 |
| FW-2, FW-3 | `reference.langchain.com` | 30 | Tier 2 |
| CE-3, CE-5, FW-9 | `langchain-ai.github.io`, `microsoft.github.io` | 30 | Tier 2 |
| FW-16, FW-17 | `dspy.ai` | 30 | Tier 2 |

Per the rubric, `0-34` is Tier 5: "Anonymous sources, content farms, social media posts,
unattributed content." Twenty-plus first-party vendor docs were scored as anonymous content farms
purely on hostname shape, a ~40-point deflation on the 35%-weighted axis (≈14 points of overall
score each). Note also that the *same publisher* scores 77 on `docs.langchain.com` (FW-1) and 30 on
`reference.langchain.com` (FW-2) — an inversion internal to a single vendor. And `PT-5`, a Medium
repost, outscores `PT-6`, a company engineering blog, on domain authority (47 vs 30).

This matters because the report **ranks its findings by evidence strength** and publishes a
per-cluster median table. Both the framework-cluster median (68) and every "verify"-tier label
attached to a first-party doc are artifacts of this deflation.

**Required change:** either re-score domain authority against the rubric's tier definitions rather
than hostname shape, or — at minimum — replace the "two visible inversions" sentence with an explicit
statement that the heuristic floors all non-`docs.*.com` hosts at 30, list the affected sources, and
state that the framework and comparative cluster medians are consequently understated. Do not leave
the disclosure describing a systemic floor as two isolated inversions.

## C-8 (Medium) — `sources.json` disagrees with the report

**Section:** "Sources" preamble.

> "Scores below are the triangulated values (machine score, with manual adjustments from
> triangulation § 3.2 applied)."

`sources.json` still carries the **unadjusted** machine scores:

| Source | `sources.json` | Report / triangulation § 3.2 |
|:-------|--:|--:|
| PT-13 | 76 (`verify`) | 52 (`questionable`) |
| FW-13 | 80 (`high_trust`) | 64 (`verify`) |
| CE-6 | 67 (`verify`) | 75 |

The machine-readable artifact — the one any downstream consumer will parse — records `PT-13` as
`verify` when the report says to cite it for framing only, and `FW-13` as `high_trust` when the
report says its claims are `[uncertain]` and the source was never fetched. That is the exact
misreading the adjustment exists to prevent.

**Required change:** write the adjusted `overall` and `category` into `sources.json` for PT-13,
FW-13, CE-6 (and record the machine score alongside, e.g. in `credibility_inputs`), so the JSON and
the prose agree.

## C-9 (Medium) — "Contradicted" overstates what peer practice can establish

**Section:** Rank 1.

> "**Rejecting a pre-run structural *validator*: contradicted**, by [FW-1], [FW-12], a provisional
> AutoGen leg, and by yf's own record."

Three peer systems shipping a validator does not *contradict* a fourth system's decision not to ship
one — it shows the decision is not universal practice. The report elsewhere argues, correctly and at
length, that yf occupies a different substrate tier (SQ1 reason 2) and that the tier boundary is
itself unestablished. It cannot simultaneously use substrate difference to explain away yf's
linearity and ignore substrate difference when calling the validator rejection "contradicted".

**Required change:** downgrade to "runs against the field's practice" or "not supported by peer
practice", and add one sentence on why the substrate argument does or does not apply here.

## C-10 (Medium) — A `questionable`-tier source carries conclusions alone

**Section:** "The acyclicity fracture resolves into a substrate distinction"; SQ1 reason 3;
"Explicitly *not* an opportunity → Adding cycles to the yf graph".

`CE-13` (clu README) scores **55, `questionable`**. The rubric's action for that band is: "Use only
if corroborated by 2+ independent sources." `CE-13` is the sole source for the
generation/instantiation split, and it carries three separate report conclusions. The corroboration
offered is `YF-12`/`YF-18` — but yf is the *subject* of the analysis, not an independent corroborator
of clu's claim, and the report says so itself in Rank 2 ("yf is a third *instance*, not a third
source") without applying the same reasoning here.

Credit where due: Q1's substrate paragraph does carry an `[uncertain]` tag and names the small-sample
and shared-ancestry risks. The problem is that the tag is not propagated. The
"Explicitly *not* an opportunity" bullet states it flatly —

> "**Adding cycles to the yf graph.** The acyclicity evidence settles the *in-process runtime* case
> only; yf's substrate is the one where staying acyclic is the attested norm ([CE-13])."

— with no hedge, on a single `questionable` source, in the section a reader will treat as settled.

**Required change:** carry the Q1 `[uncertain]` tag into SQ1 reason 3 and into the "not an
opportunity" bullet, and note in each that the substrate distinction rests on one `questionable`-tier
README.

## C-11 (Medium) — The strongest execution-layer finding is illustrated only by the weakest source

**Section:** "Fan-in / join — where yf is ahead, not behind".

Both block quotes under "The corpus's strongest execution-layer finding" are `[CE-4]` — scored 54,
`questionable`, and described by the report itself as "LLM-authored blog with a human editor" whose
"*framing* should be read as hypothesis, not fact". The report does disclose this, which is good
practice and should be preserved. But the presentation puts a **Strong** label in the heading and
then supplies only `questionable`-tier prose beneath it; the framework cluster's absence census
(`FW-15`, `FW-12`) is mentioned but never quoted.

A parallel case: the C4 convergence quotes in Q1 include `[CE-7]` (58, `questionable`, DeepWiki —
machine-generated documentation) as a load-bearing leg of a **Strong** finding.

**Required change:** promote a first-party quote (`FW-15` `AddFanIn`, `FW-12` `ctx.collect_events`)
to sit above the `CE-4` quotes so the Strong label is carried by `verify`-tier or better evidence,
and demote `CE-4` explicitly to illustrating the failure *framing*. Same treatment for `CE-7` in Q1.

## C-12 (Medium) — Undisclosed self-measurement

**Section:** "Measured shape of the emitted graphs".

Row 1 of the table is `yf-mol-62k` = `research/003` — **this research project's own epic**. `YF-22`'s
quote confirms it, and the quoted graph even contains the orphan `Swarm: yf-research` node the report
criticises as defect d8. The sample is therefore n=4 epics of which one is the report's own artifact
and two are research epics produced by the same formula (so not independent shapes).

This is not disqualifying — the measurement is reproducible and the shapes are what they are — but a
report this careful about independence elsewhere should say it.

**Required change:** add one sentence to the table's surrounding prose: n=4, two research epics from
the same formula (hence one shape, not two), one of which is this project's own epic; the two plan
epics are the only independent shapes.

## C-13 (Medium) — Uncited assertions, possible model knowledge

Each of these reads as background narration; none carries a source id.

| Line | Claim | Verdict |
|:-----|:------|:--------|
| "The practitioner cluster's chronology shows a formal treatment in April 2026, an unnoticed naming in early July, virality around 18 July, then a two-week burst..." | Four dated events | Traceable to `cluster-practitioner-trend.md:29,98` but **no per-event source id in the report**. Attach PT-ids per event. |
| "'Graph engineering' is a label roughly four weeks old at retrieval" (exec summary) | Age of label | `[uncited — possible model knowledge]` in the report itself; the cluster supports it. Add the id. |
| "Systems that recompute readiness from edges per query — `tk ready`, `clu ready`, `bd ready` —" | Behaviour of three tools | `tk` and `clu` are uncited inline. Add `CE-12`/`CE-13`. |
| "which the comparative cluster calls 'the most expensive gap' for Tier C" | Direct quotation | Quoted string with **no source id**. It is `cluster-comparative-execution.md` obs 5; give it an id or attribute it to the artifact by name. |
| "conference talks on 'graph engineering' were searched for and **none were found**" | Absence claim | The epistemic standard requires showing where you looked. The report names no provider and no query. **Add the search surface** (providers, query strings) or downgrade to "no talk surfaced in the practitioner retrieval". |

## C-14 (Low) — Undefined terminology

"Tier A / Tier B / Tier C" appear in the SQ2 evidence-strength column and the credibility-skew table
(> "Tier C claims are self-descriptions; Tier A is first-party docs") but are never defined in the
report. A cold reader cannot map them. Also note that column mixes kinds: "Tier C claims are
self-descriptions; Tier A is first-party docs" is a provenance note, not an evidence strength, and
sits in a column whose other cells read "C4 **Strong**" and "`[insufficient evidence]`".

**Required change:** define the tiers once on first use, and make the SQ2 column uniformly a strength
verdict.

## C-15 (Low) — Arithmetic

"Credibility skew by cluster" and the Sources heading give comparative-execution a median of **67**.
The 15 CE scores in `sources.json` are `[80,80,68,54,68,67,58,80,80,80,80,55,55,55,55]`; the median
is **68** — and still 68 after the `CE-6` 67→75 adjustment. Practitioner (55) and framework (68) both
check out.

## C-16 (Low) — "Independently corroborates" overstates

> "conference talks on 'graph engineering' were searched for and **none were found**, which [PT-7]
> independently corroborates ('Nobody held a keynote for it')."

One practitioner asserting nobody held a keynote is a second *assertion*, not independent
corroboration of a retrieval. Soften to "is consistent with".

## C-17 (Low) — "89 sources" inflates the external evidence base

The executive summary opens with "Evidence base: 89 sources across four clusters." 43 of those are
single-observer reads of the repository under audit — a fact the report discloses only at line 648.
Recommend the opening read "46 external sources plus 43 single-observer repo reads".

---

## What is sound and should survive refinement

Not everything here is a defect; several sections are better than the field norm and the refiner
should not weaken them:

- **The independence audit and its propagation.** Identifying `CE-1`=`FW-1`, `CE-2`=`FW-4`,
  `CE-5`=`FW-9` and the `CE-3`/`FW-5` vendor mirror, then *applying* the consequence ("every claim
  resting on LangGraph super-step, checkpointer, or interrupt evidence is single-sourced across two
  clusters") is exactly right and is done consistently.
- **The LangChain over-representation caveat** in Q1 is the correct treatment of manufactured
  agreement: it names the vendor, counts the surviving independent legs on both sides, and states
  that the finding survives "but not at the apparent strength."
- **The quarantine section.** Six claims removed, including both Anthropic-attributed statistics —
  and, critically, the report follows through: "After quarantine the corpus contains no verified
  outcome number of any kind." The strongest sentence in the document is the executive summary's "The
  single most important property of the corpus is what it does **not** contain."
- **The scope-hole disclosure.** Naming the excluded Airflow/Dagster/Pegasus lineage as "the most
  mature prior art on its central question", then listing exactly which findings it limits (C3, C1,
  the validation gap, Rank 5), and instructing the reader to read every "no system does X" as "no
  system *in this corpus* does X" — this is a model absence-of-evidence disclosure.
- **C8's strength cap.** "The *prescription* has four supporting artifacts, but the *failure mode*
  that motivates it has exactly one, so triangulation rates C8 **Moderate**, not Strong" — correct
  asymmetric reasoning, correctly reported.
- **The `[uncited]` d10 firewall.** Refusing to let the retriever's own dispatch-prompt claim
  propagate as a repo fact, and saying so in the report, is precisely right.
- **Rank 4 (INVESTIGATE parallel-vs-serial)** and **Rank 3 (dropped REFINE feedback edge)** are both
  verified sound against the repo: `skills/yf-plan/SKILL.md:308` vs `:321-324` are genuinely in
  tension in the same phase of the same file, and `skills/yf-research/agents/refiner.md:33` does wire
  `bd dep add ${PACKAGE_BEAD_ID} ${NEW_RID}` forward to package with no back-edge. Both `[uncertain]`
  tags are appropriately placed and should **not** be resolved by the refiner — neither can be
  resolved from this corpus.
- **The line counts and absence greps check out:** `plan_manager.py` is 3525 lines,
  `close_cascade.py` 241, `research_manager.py` 164; `grep -rn "swarm" skills/` returns exactly two
  lines (`yf-research/SKILL.md:336,339`).

## Bias assessment

**Source-selection bias: disclosed and adequately handled, with one residual.** LangChain's
over-representation across all three web clusters is identified, quantified, and its corroboration
value correctly voided. The residual is the *direction* of the remaining skew: the framework cluster
is 7/18 LangGraph, and the primitive-vocabulary table's "reference vocabulary" is LangGraph's, so the
"converged core" is partly a measurement of how much of LangGraph's API other systems reimplement.
The report should say this once.

**Motivated-reasoning bias: one bad argument.** The report claims (relaying triangulation § 3.3):

> "This is the yf-codebase cluster's own verdict, and it is unfavourable to the repo it audits —
> which is evidence against motivated reasoning"

"Evidence against interest" is a credibility heuristic about *human or commercial* incentives. A
subagent auditing a repository has no stake in the verdict, so an unfavourable finding is not
evidence of anything about its reliability. Drop or heavily qualify this — it is the one place the
report reaches for a credibility boost it has not earned.

**Design-proposal smuggling: minor.** The declared "no target architecture" boundary mostly holds.
Two soft breaches: Rank 1's "contradicted" verdict on the validator axis functions as a recommendation
to adopt a validator (see C-9), and Rank 2's references-not-payloads convergence points at a concrete
remedy for `sources.json`. Both are hedged; neither names an implementation. Acceptable if C-9 is
fixed.

## `[uncertain]` disposition

| Tag | Location | Refiner action |
|:----|:---------|:---------------|
| Substrate correlation, n=4 | Q1 acyclicity | **Keep**, and propagate to SQ1(3) and the "not an opportunity" bullet (C-10) |
| Which of YF-5 / YF-35 an agent honours | Q2 | **Keep** — unresolvable from this corpus; correctly scoped |
| Graph-shape interpretation | Q3 | **Keep**, but fix the underlying data presentation first (C-6) |
| REFINE feedback edge intentional? | d7 / Rank 3 | **Keep** — no rationale exists in the repo; absence correctly reported |
| `REQ-AGENT-047` measurement unverifiable | Rank 1 | **Keep and strengthen.** The report reads "found to buy nothing" as an absolute. The spec sentence is comparative — the walk engine bought nothing *over the prose cross-check*, which is a marginal-value claim. Add that distinction; it changes what "up to 3 of 5 are" licenses. |
| FW-13 claims / source never fetched | Credibility skew | **Escalate** — resolvable with one fetch, and it also fixes C-8 |
| AutoGen cycle-detection issue bodies | Validator gap | **Escalate** — this is the third leg of the report's top-ranked finding (C-3). One gap-fill retrieve resolves it or confirms the demotion. |
| `[uncited]` d10 hand-patch | d10 | **Keep as-is** — correctly firewalled |

## Recommended gap-fill retrievals

Two `[uncertain]` items are the only ones in the document that are both resolvable and load-bearing:

1. **AutoGen cycle-detection issue bodies** (issues #6628, #6551) — resolves C-3 either way.
2. **CrewAI Flows source / PR bodies for `@router`, `and_`, `or_`, `@persist`** (`FW-13`) — resolves
   the provisional status and the score discrepancy in C-8.

Note that per `refiner.md`, a gap-fill retrieve is wired forward to `package` and is **never
re-triangulated or re-critiqued** — the very defect this report identifies as d7 / Rank 3. Any
evidence these retrievals produce will therefore enter the report without passing this critique
stage. The refiner should hold itself to the standard manually.
