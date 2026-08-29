---
type: Finding
okf_spec: OKF-PLAN
---

# EXP-002 — Pin the severity vocabulary, and finish the control read that was left undone

## Finding: Does the strict `high` predicate survive a wider control read, and what does pinning the vocabulary cost?

### Approach Tested

All work in `$(mktemp -d)`, since deleted; read-only against 7 repos at HEAD. Re-ran the
study's own `corpus_scan.py`; **imported `finding_recurrence.py` as a module** (not reimplemented)
and re-ran its `parse_pass_file` over every review pass; built a **parser-free grep tokenizer** as
an independent second instrument and compared; hand-read the four §7.2 false positives; and read
`review.toml`, `doc_lint.py`, `red-team.md`, `spec/agents.md` for the cost estimate.

### Result

**measured:** every figure below is reproduced from the commands named inline; **inferred:** claims are marked as such where no command establishes them.

#### Headline verdicts

**(a) The strict predicate does NOT survive the wider control read.** It fires on **two further
bundles that are deliberate re-scoping by their own phase logs** — `yoshiko-flow/plan-029` and
`yoshiko-flow/plan-033`. **`plan-026` was not the exception; it was the one instance whose reviewer
happened to write `medium (blocking)` rather than `high`.**

**(b) Pinning the vocabulary costs ONE new `doc_lint` check kind, not a migration.**
`reviews/pass-N.md` **is** already a typed, linted document; a vocabulary **is** already declared in
prose (REQ-AGENT-041); nothing enforces it.

**(c) The corpus-dated guarantee's CONCLUSION holds; its ENUMERATION is false at HEAD — and was
already false when written.**

**(d) An unrequested fourth verdict that cannot be omitted: the study's measurement instrument
systematically DELETES HIGH severities, biased toward HIGH.** Under a parser-free reading D3 fires
on **22 of 43** ≥3-pass bundles, not 13. **Every D3 operating characteristic in §4.1–§4.3 — the
10/17-vs-3/20 cross-tab, the 2×2, PPV 69%, specificity 94%, FPR 15% — is computed on that
instrument.**

#### (a) The control read — the strict predicate fails its own shippability standard

The four §7.2 false positives were recovered by set arithmetic and verified: firing-under-strict =
13 bundles (reproducing the study's "13 firing"); intersecting the 14 hand-audited TRUE bundles
gives 9 (matching TP=9); the complement is exactly `d3-pxe/plan-011`, `d3-pxe/plan-017`,
`yoshiko-flow/plan-029`, `yoshiko-flow/plan-033`.

##### `yoshiko-flow/plan-033` — **RE-SCOPING. The detector fires. High confidence.**

Fires on pass-4 `F1` (`high`). Verdicts run REVISE, APPROVE, APPROVE, **REVISE**, APPROVE. **The
concern does not recur**, and `log.md` records the scope change between passes 3 and 4 verbatim:

> `- drafting: material re-scope: --harness install (4 harnesses), tune=config+rule-opt, --tune
> opt-in, auto-detect; back to drafting for re-investigation`

`reviews/pass-4.md:12` says it itself: *"**First adversarial pass on the heavily re-scoped 10-epic
multi-harness provisioning plan**."* **Pass-4 is structurally pass 1 of a different plan.** That is
the `plan-026` signature exactly.

##### `yoshiko-flow/plan-029` — **RE-SCOPING. The detector fires. High confidence.**

Fires on pass-5, two `high` findings. Verdicts run REVISE, APPROVE, REVISE, APPROVE, **REVISE**,
APPROVE — textbook oscillation. **The concern does not recur.** The phase log dates both REVISEs to
a scope change (*"add OKF-* impact-assessment epic + ratification human gate"*), `pass-5.md:3` names
itself *"cycle 5 (**post impact-assessment-epic addition**)"*, and pass-3 explicitly certifies
non-recurrence: *"All five pass-1 concerns survived the reframe/renumber … **None regressed.**"*

**The study's own recurrence cluster already said these two are the same shape:** *"`plan-033` … and
`plan-029` … are the same shape."*

##### `d3-pxe/plan-017` — **GENUINE. A LABEL error, not a detector error.**

Fires on pass-3 `M1` (`high`), whose earlier form **is in pass 1** as `C7` (medium) — same object
(the 55/45 split at the decision surface), and **pass-1's own remedy created pass-3's defect.**
`log.md` records **no re-scoping event at all.** The file states the recurrence twice, e.g.
`pass-4.md` `C2` — *"**M8 was recorded resolved and was not.**"*

**Inference: D3's "false positive" here is D7's false negative.** The bundle carries explicit
self-reported cross-pass recurrence that the text-similarity detector never nominated, so it was
never hand-read and defaulted to not-TRUE. The study anticipated this mode: *"Four of the five FN
and all four FP are bundles D7 never nominated, so they were never hand-read."*

##### `d3-pxe/plan-011` — **MIXED.** Pass-6 firing is cleanly re-scoping (`log.md`: *"re-opened:
adding Epic 5 … fingerprint invalidated"*). The pass-3/4 firing is not: no scope change precedes
it, and the same *object* is fatally wrong three passes running — the D5 shape rather than the
`plan-026` shape. **Verdict: inconclusive, leaning genuine.** Caveat: `pass-2.md` extracts **zero**
findings, so one link of the chain is unread by any instrument.

##### The consequence, and the constructive alternative

Under the study's own standard — *"a detector that fires on `plan-026` is not shippable"* — **the
strict variant fails**, because `plan-029` and `plan-033` are the same shape. **The severity
normaliser was never the discriminator.**

**A HIGH at pass ≥ 3 is a thrash signal only if pass ≥ 3 is not the first review of a re-scoped
plan — and that fact is already mechanically available in `log.md`, as a `drafting:` bullet
appearing between two `review-pass:` bullets.** Three of the four FPs are excludable by that one
guard; the fourth is arguably a true positive.

#### (d) The instrument deletes HIGH — three reproduced causes

| predicate | fires — `finding_recurrence.py` | fires — direct grep |
| :-- | --: | --: |
| strict `high` | **13 / 43** | **22 / 43** |
| substring `high` | 13 / 43 | 22 / 43 |
| `high`-or-`blocking` | 14 / 43 | 23 / 43 |

1. **Prose shadowing.** `dedupe_findings` ranks `prose_subsection > table` (`:262`), and
   `extract_prose_subsection_findings` **always** returns `severity=None` (`:236`). **The loss is
   biased toward HIGH:** 35 of 309 `high` table rows shadowed (**11%**) vs 31/441 `medium` (7%) and
   13/472 `low` (**3%**). *Reviewers write prose elaborations for their most serious findings.*
2. **No-id-column header skip.** `extract_table_findings` requires a header cell in
   `{#, id, no, num}` and skips the whole table otherwise (`:196-203`). **That rejects
   `| Concern | Severity | Resolution | Actor | Status |` — the shape `SKILL.md:623` currently
   MANDATES, and the corpus's single most common severity table (62 occurrences).**
3. **Id folded into the concern cell** — same skip.

`plan-056` hits (2) and (3) together and extracts **zero** severities from **59** findings across
**9** passes, despite carrying exact `high` cells at passes 3, 4, 6 and 7 — **a complete false
negative on the corpus's newest multi-pass bundle.**

**Not recomputed, deliberately:** the hand-audit TRUE label does not exist for the 9 newly-firing
bundles, so a revised PPV/sensitivity/specificity **would be fabricated.** Only the firing-rate
change is reported.

#### (b) The pinning cost — one check kind, at `R`, no migration

**`reviews/pass-N.md` IS typed and `doc_lint` DOES reach it** (`review.toml`, paths
`docs/plans/*/reviews/*.md` and `Incubator/*/plans/*/reviews/*.md`). The crux resolves in favour of
the cheap answer.

**A vocabulary already exists in prose, in three places, all agreeing on `high|medium|low`** —
REQ-AGENT-041 (`spec/agents.md:63`), `red-team.md:46`, `SKILL.md:616`. **`review.toml` declares four
checks and none inspects a severity value.** Measured against that: **45 distinct literal severity
tokens across 1,701 findings.**

**No migration is required, and one is not even possible at `E`.** `review.toml`'s own header states
the governing rule: *"a document type whose files are AUTHORED DURING the plan phase at which the
linter BINDS cannot carry a promotable severity for content shape."* A vocabulary check inherits
that constraint and ships at **`R` (report-only)** — historical findings reported, never failed.

**Forward-looking cost:** a `REQ-DATA-*` requirement (SPEC-first); **one new `cell-vocabulary` check
kind in `doc_lint.py`** — locate a column **by header name**, assert each cell's
lowercased/stripped/de-emphasised value ∈ a declared set — roughly 20 lines, in the same shape as
`row-id-grammar`; one `[[checks]]` block at `R`; and an amendment to REQ-AGENT-041 + `red-team.md`.

**The existing `table-columns` kind cannot express this**: it is an exact **ordered header equality**
check (`doc_lint.py:574-576`), and the severity column sits at index **1, 2 or 3** depending on the
bundle across **~26 distinct table headers**.

**The pinning decision is substantive, not clerical.** `high|medium|low` alone would reject **42 of
45** observed tokens, and the corpus uses `medium-high` and `medium (blocking)` **deliberately**.

**The residual cost the check cannot buy:** severity appears in **7 structural shapes**; **17 files
carry severity only in prose** and **42 carry none**. Pinning the *table* leaves the prose forms
(used by 22 bundles each) unconstrained unless `red-team.md`'s template is narrowed to one emission
shape.

#### (c) The corpus-dated enumeration, re-run at HEAD

30 `medium-high`-family occurrences in **9** bundles. Two errors in the study's sentence, both
verifiable:

- **`rc-files/plan-001` is omitted** from the study's bundle list (its `MEDIUM-HIGH` *is* counted in
  census [104]).
- **"Only one has such a cell at pass ≥ 3" is wrong.** `yoshiko-flow/plan-056` carries them at
  passes **4, 6 and 7** — and had 7 passes at the time of the study's own re-enumeration.

**The conclusion nevertheless holds.** `plan-056`'s passes 4/6/7 each carry exact `| high |` cells
in the same file, so no classification changes. Over all 43 ≥3-pass bundles, `strict` and
`substring` fire on the **identical set** under both instruments. **Only `blocking`-folding moves
anything, and it moves exactly `plan-026`.**

**One new hazard token the study never saw:** `plan-056/reviews/pass-4.md` records
`[MEDIUM — high for plan-057]`. **A substring predicate reads that as HIGH; it says MEDIUM.** Inert
today only because pass-4 also carries four exact `high` cells.

#### Census reproduction

The study's figures reproduce **exactly** at study scope: **79 bundles / 1,509 findings / 185
`none`**, and unusable = 185 + `—` 14 + `gap` 3 + `missing` 2 = **204 / 1509 = 13.52%**. Corpus at
HEAD is **115 bundles / 310 passes**; the delta is exactly `plan-056` (+9 passes, +59 findings,
**all 59 with no parsed severity** — see (d)).

#### Absence findings

- **The hand-audit TRUE/FALSE label for the 9 newly-firing bundles does not exist.** No revised 2×2
  is reported, because one would be fabricated.
- **`d3-pxe/plan-011` pass-2 extracts zero findings** — one link of its HIGH chain is unread.
- **Whether `plan-011` pass-1 `C2` was ever recorded resolved** was not verified; that is what would
  settle same-concern recurrence vs same-area deepening.
- **The 42 review files with no severity token at all were not audited** for severity-less-by-
  convention vs by-omission. That distinction decides what an `R` check would report.
- **The grep-instrument per-pass magnitudes are inflated ~2×** (a concern usually appears in both a
  Concerns and a Resolutions table). **Only the firing decision is safe to read from it.**
- **The study's "9 cells by direct re-enumeration" for `medium-high` could not be reproduced
  exactly** — 12 case-insensitive occurrences at study scope, or 10 counting table cells only. The
  study does not state its convention, so this reports its own rather than reconciling to a number
  whose definition cannot be recovered.

### Implications for Plan

**The §7.1 recommendation as written should not be implemented.** Its exact-match condition is
correct and cheap, but it is **not** the condition that makes the detector shippable. The
shippability failure is `plan-029` and `plan-033`, and **no severity predicate fixes those.**

**The prerequisite deliverable is real but was mis-scoped.** Pinning the vocabulary is one
`doc_lint` check kind at `R` — cheap, no migration. But **pinning the token does not pin the shape**,
and the shape is where the measured failures are.

**No number derived from `finding_recurrence.py` may be carried forward** until its two severity-loss
defects are repaired.

### Recommendations

1. **Do not ship D3 on the strict-`high` predicate alone.**
2. **Ship the vocabulary pin anyway, on its own merits**, deciding explicitly whether `medium-high`
   and a qualifier suffix are legal — `high|medium|low` alone would reject 42 of 45 observed tokens.
3. **Repair `finding_recurrence.py` before re-running §4.1–§4.3.** The firing rate is 22/43.
4. **Correct the §7.1 enumeration** — add `rc-files/plan-001`, and replace "only one has such a cell
   at pass >= 3" with `d3-pxe/plan-017` **and** `yoshiko-flow/plan-056` passes 4, 6, 7.
5. **Treat `d3-pxe/plan-017`'s FP label as unsafe** — the FP count of 4 is an over-count on top of
   being a floor.
