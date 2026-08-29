---
type: Research Artifact
description: Cluster findings for review-pass-recurrence — what observable residue
  in reviews/pass-N.md precedes an agentic thrash episode, and what discriminates
  thrash from convergence
okf_spec: OKF-RESEARCH
---

# Cluster: review-pass-recurrence

**Questions.** Primary Q1: what OBSERVABLE signals precede an agentic thrash episode, and
which are detectable EARLY enough to act on? Secondary: what are the false-positive costs —
what discriminates thrash from productive iteration?

## Epistemic frame — read this before any finding below

Research 004's boundary is this cluster's starting constraint: **plan bundles record
ARTIFACTS, not live session behavior** [100]. Nothing below is an observation of a loop. Every
claim is a claim about **residue** — what a reviewer wrote down, in a file, after the fact.
Where a rival explanation would leave different residue, it is named.

Three residue limits apply everywhere:

- A `reviews/pass-N.md` is written by a reviewer, not by the agent that thrashed. A concern
  re-raised at pass N+1 tells you the artifact still had the defect. It tells you **nothing**
  about how many edit attempts were spent on it inside the session.
- The corpus is dominated by one self-referential repo (yoshiko-flow, 42 of 79 multi-pass
  bundles [101]) whose subject matter *is* the review machinery. Signals that appear only there
  are weak.
- The extractor under-reports by design, and its author found and fixed ~700 bogus matches
  during validation [102]. Every candidate below was hand-read before being counted.

## 1. Base rates — the corrected census

`corpus_scan.py` over the 7-repo corpus, worktree mirrors and OKF fixtures excluded:
**114 bundles / 301 review passes**, 7/7 repos OK [103]. This supersedes `plan.yaml`'s
`corpus:` block (127/391), which double-counted `.worktrees/` mirrors [102].

Review-pass count per bundle — **this is the base rate everything else is judged against**:

| passes | bundles | share |
| --: | --: | --: |
| 0 | 5 | 4% |
| 1 | 30 | 26% |
| 2 | 37 | 32% |
| 3 | 15 | 13% |
| 4 | 8 | 7% |
| 5 | 9 | 8% |
| 6 | 3 | 3% |
| 7 | 4 | 4% |
| 8 | 2 | 2% |
| 13 | 1 | 1% |

Source: `corpus_scan.py --json`, aggregated [103]. **Two passes is the mode, and 62% of bundles
finish in ≤2.** 79 bundles have ≥2 passes (the only ones where cross-pass recurrence is even
definable); 42 have ≥3; 27 have ≥4.

Per repo [103]:

| repo | bundles | passes | max passes |
| :-- | --: | --: | --: |
| yoshiko-flow | 56 | 166 | 13 |
| d3-pxe | 19 | 73 | 8 |
| evri_py | 9 | 13 | 4 |
| writing | 11 | 18 | 3 |
| pybridge | 11 | 20 | 4 |
| emacs.d | 4 | 4 | 1 |
| rc-files | 4 | 7 | 3 |

Verdict vocabulary across the parsed passes: **186 REVISE, 83 APPROVE, 2 unparsed** [104]. No
REJECT/BLOCK observed.

**"Many passes" is not, on its own, a thrash signal.** It is a description of a large plan —
see §6.

## 2. Tool output and threshold sensitivity

`finding_recurrence.py --census <census> --id-floor 0.15` over the 79 multi-pass bundles.
1509 findings extracted, 85 parse warnings, at every threshold [105]:

| threshold | recurrence matches | weak id-reuse | self-reported signals |
| --: | --: | --: | --: |
| 0.20 | 40 | 252 | 51 |
| 0.25 | 23 | 252 | 51 |
| 0.30 | 12 | 252 | 51 |
| 0.35 | **8** | 252 | 51 |
| 0.45 | 4 | 252 | 51 |
| 0.55 | 4 | 252 | 51 |
| 0.70 | 3 | 252 | 51 |

The candidate count falls by **5× between 0.20 and 0.35** and by 13× between 0.20 and 0.70.
There is no plateau, no knee, no natural operating point — the count is a smooth function of
the knob. **A "signal" whose magnitude is set entirely by a tuning parameter is not yet a
signal**; it is a similarity histogram. I audited the full 0.20 set (40 episodes, a superset
of every higher threshold) precisely so the verdicts do not depend on which knob position a
downstream phase picks.

**The self-reported and weak-id-reuse counts do not move at all** with the threshold — they
are computed on different code paths.

## 3. Hand-audit — all 40 candidate episodes at threshold 0.20

Every row was verified by opening both `reviews/pass-N.md` files and reading the finding in
context. Verdicts: **TRUE** = the same concern genuinely re-raised unresolved · **DEEPEN** =
same area, sharper or different claim (convergence, not thrash) · **FALSE** = fingerprint
fired on shape, boilerplate, or a reused id.

| # | bundle | passes | sim | basis | verdict | justification |
| :-- | :-- | :-- | --: | :-- | :-- | :-- |
| E01 | yf/plan-029 | 3→4 | 0.25 | text | DEEPEN | Same composition-gate area; pass-4's is `severity: low`, "Cosmetic; does not block approval" [106] against pass-3's `severity: medium` [107] |
| E02 | yf/plan-034 | 1→2 | 0.16 | id | FALSE | Later "finding" is a **resolution-confirmation** bullet: "**C1 (single-file scope) — RESOLVED.**" [108] parsed as a concern |
| E03 | yf/plan-034 | 1→2 | 0.24 | text | FALSE | Same resolution-confirmation block as E02 [108] |
| E04 | yf/plan-039 | 2→3 | 0.22 | text | TRUE | "`\brelease` matches inside `ci-release`; SC6 falsified" [109] → "SC6 falsified **again**" [110] |
| E05 | yf/plan-039 | 2→3 | 0.30 | text | TRUE | "EXP-001 figures drifted" [111] → "`exp-001` **still** carries superseded figures" [112] |
| E06 | yf/plan-039 | 2→4 | 0.20 | text | TRUE | Same chain, one more hop: → "`exp-001` Implications **still** stale" [113] |
| E07 | yf/plan-039 | 3→4 | 0.29 | text | TRUE | Same chain as E05/E06; **not independent evidence** |
| E08 | yf/plan-040 | 1→2 | 0.33 | text | TRUE | "Wrong guardrail (GR-BUP-002 vs 001)" [114] → "Issue 2.3 **still** names GR-BUP-002" [115] |
| E09 | yf/plan-047 | 1→4 | 0.28 | text | TRUE | Same wrong line-slice unrepaired across 3 passes [116][117] |
| E10 | yf/plan-047 | 2→3 | 0.24 | text | TRUE | "Count wrong three ways: says 10, lists 8, Epic 6 has 11" [118] → "**SC20's count wrong three ways again**" [119] |
| E11 | yf/plan-047 | 3→4 | 0.27 | text | TRUE | → "**Fourth consecutive cycle of a stale count surviving inside its own fix**" [120] |
| E12 | yf/plan-047 | 3→4 | 0.35 | text | TRUE | "SC20's count wrong three ways again" [119] → "**SC20 still said "10 Epic-6 issues"** — wrong three ways again" [121] |
| E13 | yf/plan-048 | 1→2 | 0.23 | text | TRUE | "two capability gates are formal cycles" [122] → "**still a cycle, made explicit** … Pass-1 moved it *onto* the producers of its own evidence — **strictly worse**" [123] |
| E14 | yf/plan-048 | 1→2 | 0.28 | text | DEEPEN | Shares the premise "`plan_manager.py` has **no** … gate runner" [124][125] but names a different defect (ordering vs. an unachievable criterion) |
| E15 | yf/plan-048 | 2→3 | 0.24 | text | TRUE | "**"declared target" has no producer**" [126] → "**The declared target is still declared after the measurement.**" [127] |
| E16 | yf/plan-048 | 4→6 | 0.27 | text | DEEPEN | Same criterion SC1, a **new** defect the repair created: "dirtied by plan-048's own bookkeeping" [128] → "**SC1's verification exits 128**" [129] |
| E17 | yf/plan-048 | 6→7 | 0.20 | text | TRUE | Partial landing: the number was corrected, the malformed emphasis was not [130][131] |
| E18 | yf/plan-049 | 1→2 | 0.32 | text | TRUE | Self-reported: "**C15's claimed resolution did not land**" [132] |
| E19 | yf/plan-050 | 3→4 | 0.28 | text | TRUE | The same count re-litigated, and inverted: six→five→six [133][134] |
| E20 | yf/plan-050 | 4→5 | 0.36 | text | TRUE | "Pass 4's C29 flagged #183's blank and **missed that the whole document is blank**" [135][136] |
| E21 | yf/plan-053 | 1→4 | 0.20 | text | DEEPEN | Same Issue 0.2 file-scoping area; pass-4 names a genuinely new dual-meaning collision [137][138] |
| E22 | yf/plan-053 | 3→4 | 0.29 | text | TRUE | "**C40 named D-13 *and* R7; only D-13 was fixed**" [139][140] |
| E23 | yf/plan-054 | 1→2 | 0.21 | text | TRUE | Same `verify-reconcile` failure, now **measured**: "→ `fail`, 15 of 23 rows" [141][142] |
| E24 | yf/plan-054 | 5→6 | 0.22 | text | TRUE | "has no verifying verb" [143] → "has a verifier but **no RECORDER** … **N2's class one** [layer down]" [144] |
| E25 | yf/plan-055 | 6→7 | 0.16 | id | FALSE | Later match is a **verification heading**, "### C1 recomputed independently — own parser, own regex, own closure" [145] |
| E26 | yf/plan-055 | 6→7 | 0.21 | text | TRUE | "**C3 was recorded resolved and is not fixed.**" [146] |
| E27 | d3-pxe/plan-016 | 1→2 | 0.20 | text | FALSE | Different objects — Issue **5.1** [147] vs Issue **2.3** [148]. Same defect *class*, not the same concern |
| E28 | d3-pxe/plan-016 | 2→3 | 0.25 | text | FALSE | Same as E27: Issue 2.3 [148] vs Issue **6.1** [149] |
| E29 | d3-pxe/plan-016 | 3→4 | 0.20 | text | DEEPEN | Same SC1 + same `--monitor-snapshots`, different claim (reversal-without-config vs unmeasured output shape) [150][151] |
| E30 | d3-pxe/plan-018 | 3→5 | 0.25 | id | FALSE | Both sides are **RESOLVED rows**; `C1` reused for unrelated concerns [152][153] |
| E31 | d3-pxe/plan-018 | 3→5 | 0.20 | text | FALSE | Four-word headlines sharing the token "gate": "Reload gate Test" vs "Env precondition on the gate" [154][153] |
| E32 | d3-pxe/plan-018 | 4→5 | 0.27 | text | TRUE | "Pass-4 C6 named **two** surfaces … **Only 0.5 was re-pointed.**" [155] |
| E33 | d3-pxe/plan-002 | 1→2 | 0.42 | text | TRUE | "**Residual C7:** the Approach `pve_lxc` bullet **still** cites `PVE-GPU-003/005/006`" [156][157] |
| E34 | d3-pxe/plan-010 | 2→3 | 0.20 | text | DEEPEN | The pass-2 fix supplied the missing command; the pass-3 finding is that the **new** command is wrong [158][159] — prose→command is progress |
| E35 | d3-pxe/plan-010 | 2→3 | 0.44 | text | TRUE | Near-verbatim, unresolved: "`index.md` still advertised the skills gateway and a dedicated CT 107" [160] → "`index.md` still advertised the dropped skills gateway and CT 107" [161] |
| E36 | d3-pxe/plan-015 | 2→3 | 0.27 | text | TRUE | The same R1b failure mode restated at HIGH after a fix attempt [162][163] |
| E37 | d3-pxe/plan-015 | 2→4 | 0.21 | text | FALSE | Earlier side is the stub header "### N3–N12" [164] — a parse artifact, not a finding |
| E38 | evri_py/plan-008 | 2→3 | 0.31 | text | TRUE | "**even though NC2 cut the `4.2→3.2` edge**, `4.2` still can't fire" [165] |
| E39 | writing/plan-002 | 1→2 | 0.20 | text | FALSE | "Multipart undecomposed" vs "cover/hero mechanism undecomposed" [166][167] — one shared word |
| E40 | writing/plan-010 | 1→2 | **0.60** | text | DEEPEN | The corpus's **highest-similarity match**, and it is convergence: medium→low, "resolved" [168][169] |

### Audit tally

**TRUE 24 · DEEPEN 7 · FALSE 9** (of 40).

Precision by similarity band [own audit, cross-tabbed against tool output]:

| similarity band | n | TRUE | DEEPEN | FALSE | TRUE-precision |
| :-- | --: | --: | --: | --: | --: |
| 0.20–0.25 | 17 | 9 | 3 | 5 | 53% |
| 0.25–0.30 | 12 | 7 | 3 | 2 | 58% |
| 0.30–0.35 | 4 | 4 | 0 | 0 | 100% |
| ≥ 0.35 | 5 | 4 | 1 | 0 | 80% |

**Similarity magnitude does not rank truth.** The single highest score in the corpus (0.600,
E40) is a *productive-deepening* case, and the 0.30–0.35 band outperforms the ≥0.35 band. The
signal is weakly monotone at best.

**The `id_reuse` basis is worthless as shipped: 3 of 3 id-reuse-basis episodes are FALSE
MATCHES** (E02, E25, E30). This matters because at the tool's documented operating point
(threshold 0.35) the reported 8 episodes are E02, E12, E20, E25, E30, E33, E35, E40 [170] —
**3 of the 8 are id-reuse false matches and 1 is productive deepening, so the headline
operating point is 4 TRUE / 8 = 50% precision.** Auditing only the 0.35 set would have both
overstated the noise floor and hidden the 20 TRUE episodes that sit below it.

### What the TRUE episodes actually are — and are not

The research question anticipated "re-litigated decisions, oscillating fixes". **The residue
does not show that.** Of 24 TRUE recurrences:

- **~20 are PARTIAL LANDINGS** — a remedy applied at the one site the reviewer named, while
  the same defect survives elsewhere. The reviewers name this themselves: "C40 named D-13
  *and* R7; only D-13 was fixed" [140]; "Pass-4 C6 named **two** surfaces … Only 0.5 was
  re-pointed" [155]; "C15's claimed resolution did not land" [132]; "C3 was recorded resolved
  and is not fixed" [146].
- **3 are fix-induced new defects** — the repair introduced a fresh instance of the class it
  repaired: "**Fourth consecutive cycle of a stale count surviving inside its own fix**" [120];
  "Pass-1 moved it *onto* the producers of its own evidence — **strictly worse**" [123].
- **1 is a genuine oscillation** — plan-050's count going six → five → six [133][134].

**Absence finding, stated plainly: I found essentially no decision oscillation in this
corpus.** One instance in 40 candidates, over 301 review passes. The dominant residue
signature is not "the agent kept changing its mind"; it is **"the agent fixed exactly what it
was pointed at."** That is a different failure, it implies a different intervention, and any
detector designed against the oscillation model would be designed against a phenomenon this
corpus does not contain.

## 4. The self-reported cross-pass signal is a CONVERGENCE signal, not a recurrence one

The tooling notes call the 51 self-reported cross-pass signals "the highest-confidence
recurrence signal in the corpus" [102]. **Hand-read, that is wrong.** All 51 were inspected [171]:

- **47 of 51 are clean all-resolved statements** — "All eight concerns resolved" [172],
  "All four pass-1 concerns verified genuinely and correctly resolved against the real repo"
  [173], "All 16 concerns resolved" [174], "All 10 pass-1 concerns verified addressed in revised
  plan with quoted text" [175]. These are evidence that the previous round *worked*.
- **4 carry an actual failure rate**, and all four are plan-053's `Reproduction of pass-N`
  tables [176]–[179].

The detector fires on the presence of *cross-pass verification prose*, and such prose is
written by careful reviewers on converging plans. As a thrash signal it is **inverted**.

**But those 4 rows are the most valuable artifact in the cluster.** plan-053 measured, per
pass, what fraction of the previous pass's resolutions actually landed:

| pass | reproduction rate | verbatim |
| --: | :-- | :-- |
| 2 | 9/14 = 64% | "**9 of 14.** All four (c)-class failures are **RE-002's shape** — a global property repaired at the one site the reviewer named." [176] |
| 3 | 9/15 = 60% | "**9 of 15 (60%), against pass 2's 9 of 14 (64%) — this round did slightly WORSE.**" [177] |
| 4 | 7/14 = 50% | "**64% → 60% → 50%. The rate did not improve; it fell by the largest margin yet.**" [178] |
| 5 | 9/10 = 90% | "**64% → 60% → 50% → 90%. The method change is real and it worked.**" [179] |

This is a **direct, numeric, per-pass measurement of the partial-landing rate**, computed by
the reviewer from the artifacts alone — and it moved when the *method* changed, not when the
task got easier. plan-053's own diagnosis of the fall names the mechanism precisely:
"**pass-3's structural remedy was ITSELF applied site-by-site**" [178].

## 5. Control group — what convergence looks like structurally

I characterised **all 37 bundles with ≥3 passes and any parseable findings** — 20 of which had
zero recurrence matches, and are the control [180]. Twelve were read in full detail
(plan-004-f0bcc5 in rc-files, plan-006-204159 in writing, plan-010-06eefa in pybridge,
plan-009-4f56e2 and plan-017-feb918 in d3-pxe, plan-008-382e8a / plan-026-6e0e2f /
plan-033-46aca2 / plan-041-a9d837 / plan-042-98631b / plan-043-a8afe8 in yoshiko-flow,
plan-011-150357 in d3-pxe/Incubator) [181].

Cross-tab of candidate structural discriminators over those 37 [180]:

| discriminator | recurrence-fired (n=17) | control (n=20) |
| :-- | :-- | :-- |
| a HIGH-severity finding at pass ≥3 | 10 (59%) | 3 (15%) |
| a HIGH-severity finding at pass ≥2 | 12 (71%) | 8 (40%) |
| finding counts non-increasing across all passes | 5 (29%) | 12 (60%) |
| pass-2 findings ≥ pass-1 findings | 6 (35%) | 8 (40%) |

Over the full 79 multi-pass set [182]: approve-then-revise **verdict reversal** occurs in 21%
of recurrence bundles vs 7% of controls; non-increasing finding counts in 37% vs 83%.

### What convergence actually looks like

Reading the controls, the recurring shape is a **severity collapse, not a volume collapse**:

- `plan-042-98631b`: findings **12 → 12 → 4**; HIGH **4 → 2 → 0**; REVISE, REVISE, APPROVE
  [181]. The count is flat between passes 1 and 2 and the plan still converges — because
  pass-2's HIGH findings dropped by half and pass 3 carries only low/medium.
- `plan-041-a9d837`: 14 → 9 → 4, HIGH 3 → 0 → 0 [181].
- `plan-043-a8afe8`: 15 → 6 → 4 → 0, HIGH 4 → 1 → 0 → 0 [181].
- `plan-017-feb918` (d3-pxe): 19 → 19 → 11 → 10, HIGH 4 → 2 → 1 → 0 [180]. Volume barely
  moves across four passes; **HIGH count is the thing that decays**, and it approves.
- `plan-004-f0bcc5` (rc-files, non-software): 16 → 16 → 11, HIGH 4 → **6** → 0 [180]. Volume
  flat, HIGH *rises* at pass 2, and it still approves at pass 3.

Against the firing group, which take 4–7 passes to drive HIGH to zero: `plan-048` HIGH
7,6,4,1,2,0,0; `plan-054` 8,6,4,2,2,0; `plan-055` 5,8,2,1,1,1,0 [180].

### Two control shapes that look like thrash and are not

- **Verdict oscillation from re-scoping.** `plan-026-6e0e2f` runs REVISE, APPROVE, APPROVE,
  REVISE, APPROVE, REVISE, APPROVE over 7 passes with **zero** recurrence [181]. Reading it,
  each REVISE follows a *deliberate scope change* to the plan, and the concerns are entirely
  different objects each time — pass-1 `C1` is "Epic 4 premise factually wrong for md2pdf";
  pass-4 `C1` is "#85 reverses GR-MDLINT-001". `plan-033-46aca2` (5,2,2,7,0) and
  `plan-029-75fd34` (4,1,5,1,5,1) are the same shape [181]. **Verdict non-monotonicity is not
  a thrash signal in this corpus** — it is the signature of a plan being re-opened and grown.
- **Bulk cosmetic rounds.** `plan-050-d0414b` has **13** passes, but passes 6–13 extract zero
  findings [180] — the volume comes from bookkeeping rounds, not from unresolved concerns.

## 6. Candidate discriminators, with earliness

Each is stated as: thrash form / convergence form / computable from artifacts alone? / **first
pass at which it is available**.

| # | discriminator | under thrash | under convergence | computable | earliest |
| :-- | :-- | :-- | :-- | :-- | :-- |
| D1 | **Explicit back-reference with a failure word** — a pass-N finding naming a prior pass's finding id together with "still / again / did not land / residual / survives" | present, and repeats | absent, or appears once and clears | **yes**, exactly (no similarity threshold) | **pass 2** |
| D2 | **Reproduction rate** — fraction of pass N−1's resolutions that verifiably landed | falls or stalls below ~65% | ≥90%, rising | **only if the reviewer computes it**; not recoverable from an ordinary pass file | pass 2 (rate), **pass 3** (trend) |
| D3 | **HIGH-severity count trajectory** | HIGH > 0 still at pass ≥3 | HIGH reaches 0 by pass 2–3 | yes, where severity is recorded (1324/1509 findings [104]) | pass 3 |
| D4 | **Partial-landing shape** — the remedy names one site, the defect is a global property | reviewer writes "landed at one site, defect survives elsewhere" | remedy is class-scoped | yes, as prose | pass 2 |
| D5 | **Fix-induced defect** — the new defect is an instance of the class just repaired | "surviving inside its own fix", "re-broken by pass-2's own remedies" | absent | yes, as prose | pass 2 |
| D6 | Total finding count non-increasing | violated | holds | yes | pass 2 |
| D7 | Text-similarity recurrence (the shipped tool) | fires | — | yes | pass 2 |
| D8 | Raw review-pass count | high | low | yes | continuously |
| D9 | Approve→revise verdict reversal | — | — | yes | pass 3 |

**D1 is the strongest early signal I found, and it is not the one the tool ships.** Measured
corpus-wide as "a finding whose text names a finding id first introduced in an earlier pass,
together with a failure/persistence word": **54 signals across 16 of the 79 multi-pass
bundles** [183]. Its earliness distribution is the point:

| pass at which the back-reference appears | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --: | --: | --: | --: | --: | --: | --: | --: |
| signals | **21** | 12 | 11 | 5 | 2 | 2 | 1 |

**39% of all D1 signals fire at pass 2** — the first pass at which any cross-pass signal is
even definable. It is also more *portable* than D7: it fires in d3-pxe (5 bundles), evri_py,
pybridge, **and rc-files** — a non-software, low-ceremony repo — as well as yoshiko-flow [183].
Per method_notes, that cross-domain reach is what makes it materially stronger than a
yoshiko-flow-only pattern [100]. It overlaps D7 only partially: 9 bundles fire both, **7 fire D1
alone, 10 fire D7 alone** [183].

D1's verbatim instances are unambiguous in a way similarity scores are not: "**M3's resolution
did not land.**" [184]; "**C4 landed in the Decisions table only.**" [185]; "**C18's fix did not
propagate to SC2 or D10.**" [186]; "**C5 was applied to plan.md and to nothing else.**" [187].

**D2 is the strongest signal overall but is not free.** It requires the reviewer to *do* the
cross-pass reproduction check and write the rate down — only 6 bundles in 114 contain such a
section [188], and only plan-053 produced a trend. It is an **instrument to install**, not
residue to mine.

**D3, D6, D8, D9 are cheap and weak.** D8 in particular is close to worthless on its own
(§7). D9 is actively misleading — it fires on re-scoped plans (§5).

**D7, hand-audited, does not earn its place.** 50% precision at its documented operating
point, 60% over the full audited set, no threshold plateau, id-reuse basis 0/3, and its score
does not rank truth. Anything D7 catches at pass 2, D1 catches at pass 2 more precisely and
more portably.

## 7. Rival-explanation test — and where the signals fail it

The plan mandates testing task difficulty, missing tool/permission, context exhaustion, and
genuine domain underdetermination [100]. A signal that cannot distinguish these is not a signal.

### Task difficulty — the rival that survives, and largely wins

**Spearman ρ(review-pass count, `plan.md` size) = 0.739 over 109 bundles** [189]. Median
`plan.md` size by pass count [189]:

| passes | bundles | median plan.md bytes | median in-window commits | % firing D7 |
| :-- | --: | --: | --: | --: |
| 1 | 30 | 16,398 | 2 | 0% |
| 2 | 37 | 19,790 | 3 | 5% |
| 3–4 | 23 | 35,758 | 5 | 22% |
| 5+ | 19 | 62,461 | 6 | **63%** |

And D7's own firing rate tracks raw finding volume even more tightly [190]:

| total findings in bundle | bundles | % firing D7 |
| :-- | --: | --: |
| 0 | 8 | 0% |
| 1–20 | 48 | 12% |
| 21–50 | 16 | 44% |
| 51+ | 7 | **86%** |

**This is the central negative result of the cluster.** The recurrence detector's output is
very nearly a monotone function of how much review text a bundle contains, and review text
volume is very nearly a monotone function of plan size. **D7 cannot distinguish thrash from a
large plan reviewed thoroughly, and neither can D8, D6, D3 or D9** — all of them have more
opportunities to trip on a longer document, by construction.

**D1 partially survives** because it is a *pointed* predicate: it requires a specific prior id
plus a persistence word, so a bundle can be large and still emit zero D1 signals. 63 of 79
multi-pass bundles emit none [183]. But it is not immune — more passes means more chances, and
I have not normalised D1 by pass count. `[uncertain]`

**D2 survives cleanly** — it is a *ratio*, so plan size cancels. plan-053's rate fell from 64%
to 50% while the plan was, if anything, shrinking in open concerns (14→15→14→10 findings
[180]). That is the one measurement in the corpus that moves in the thrash direction while the
difficulty proxy moves the other way.

### Missing tool / permission

Reviews do record capability failures — "`op` is not installed on the pve host and `pct`
exists nowhere else" [191], "a deleted script returns 127 *from bash*" [125] — but these appear
as ordinary findings and are **indistinguishable at the signal level** from a partial landing.
D1 will fire on a re-raised tool gap exactly as it fires on a re-raised logic defect. **None
of D1, D3, D6, D7, D8, D9 can separate this rival.** D2 can in principle (a blocked tool
yields a *stable* low rate rather than a falling one) but I have no instance to demonstrate
it. `[uncertain]`

### Context exhaustion

**Not testable from this residue at all, and I want to be explicit about that.** Plan bundles
carry no token counts, no session boundaries, no compaction markers. The 004 boundary applies
in full: nothing in a `reviews/pass-N.md` distinguishes "the agent forgot" from "the agent was
pointed at one site". Where a reviewer writes "missed by all six prior passes" [192], that is a
*reviewer's* miss, not an agent's context loss. **Every discriminator above fails this rival.**
Testing it requires session telemetry the corpus does not contain.

### Genuine domain underdetermination

The corpus contains a clean positive instance, and it exonerates the signal: plan-039's SC6
was "asserted twice and falsified twice, because the measured document is the [one being
edited]" [193] — a self-reference problem, not agent confusion. The resolution was to
**restructure the criterion** ("SC6 rewritten to assert stable properties") rather than
re-attempt the fix. That episode (E04) is a TRUE D7/D1 firing whose *cause* is
underdetermination, and **no discriminator here distinguishes it from a partial landing.** It
looks identical in the residue.

## 8. Bottom line

**Does the residue support an early-detectable recurrence signal? Qualifiedly yes — but not
the one that was built, and not on the strength originally hypothesised.**

- The **shipped text-similarity detector (D7) does not clear the bar.** 50% precision at its
  operating point, no threshold plateau, 0/3 on its id-reuse path, and — decisively — its
  firing rate is 86% on bundles with 51+ findings vs 12% on bundles with 1–20 [190], while plan
  size alone correlates ρ=0.739 with pass count [189]. It cannot separate thrash from a big
  plan.
- A **better, cheaper, more portable signal exists in the same residue and is available at
  pass 2**: the explicit cross-pass back-reference with a failure word (D1). 54 instances in
  16 bundles, 21 at pass 2, present in five of seven repos including a non-software one [183].
  It is an exact string predicate with no threshold to tune.
- The **best signal (D2, the reproduction rate) is not extractable from ordinary residue** —
  it exists in exactly one bundle as a trend [176]–[179] because one reviewer chose to compute
  it. Making it available is a **process change**, not a detector.
- **The phenomenon is misnamed in the research question.** The residue shows almost no
  oscillation (1 instance in 40 audited). It shows **partial landing** — a remedy applied at
  the site named, while the class survives — in roughly 20 of 24 TRUE episodes. The reviewers
  named this class themselves before this study did: "a global property repaired at the one
  site the reviewer named" [176].

## 9. Limitations

1. **Residue only.** No claim here is an observation of a session. Under the rival "the agent
   converged fast and the *reviewer* was slow", the residue would look identical: same passes,
   same re-raised concerns. Nothing in a plan bundle can separate them.
2. **Corpus concentration.** yoshiko-flow supplies 42 of 79 multi-pass bundles and 26 of 40
   D7 episodes [182]. The "defect inside its own fix" phrasing appears in 14 files across 9
   bundles, **11 of them in yoshiko-flow** and the rest in one d3-pxe plan [194] — that
   sub-signal is effectively a single-repo artifact and should not be generalised.
3. **Parse blindness.** 85 parse warnings; 8 multi-pass bundles extract **zero** findings and
   are structurally invisible to every finding-based discriminator [105][180]. The
   letter-paragraph shape (`**A. [MEDIUM] …**`) is a documented, unfixed gap [102]. D7's and
   D1's recall are unknown, only their precision is measured.
4. **D1 was measured, not validated the way D7 was.** I hand-read the ~20 instances quoted
   above and they are all genuine, but I did not audit all 54. Its false-positive rate is
   `[uncertain]`; the one suspicious shape I saw is a *positive* verification written with a
   negation word ("C1 resolved (residual N3: …)" [195]).
5. **No normalisation.** None of the discriminators are rate-normalised by pass count or
   finding volume. Given §7, that is the single most important next measurement.
6. **Severity is not universally recorded** — 185 of 1509 findings carry none, and the
   vocabulary is unnormalised (`medium`, `med`, `medium-low`, `low-med`, `high, blocking`)
   [104]. D3 is only as good as that field.
7. **Single-pass bundles are excluded by construction** (30 of 114). If thrash ever ends in a
   plan being abandoned after one pass, this cluster is blind to it.
8. **Two reserved OKF files** and worktree/fixture paths were excluded by `corpus_scan.py`
   [102]; I did not independently re-verify that exclusion beyond confirming the 114/301 totals.
