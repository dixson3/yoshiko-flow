---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-normalizability
---
# EXP-002 — How much of the historical corpus can be mechanically normalized?

**Status:** complete · **Date:** 2026-08-18 · **Verdict:** the **syntactic** half is 83–100%
mechanical. The **semantic** half — `discharged-by`, the one deliverable #174 actually consumes —
is **~10%** mechanical and requires authorship. Do not size these as one epic.

## Corpus-size reconciliation (two investigators disagreed; it resolves cleanly)

EXP-002 measured **46** plan dirs and reported the brief's "47" as wrong. EXP-001 measured **47**.
Both are right: EXP-002's worktree predates this plan's creation, so it saw only the **46
completed historical plans**; EXP-001's included **plan-047 itself**, which is `investigating`.

> **46 = the normalizable corpus. 47 = all plan dirs.** Use 46 for every migration count.
> All 46 parse `status: complete`, so **D-2's refusal gate rejects zero of them** — it is still
> correct to build (it protects future in-flight plans) but **it can never fire during the
> migration, so the migration cannot validate it.** It needs a synthetic non-complete fixture.

## Result — auto-normalizable fraction, per construct

| Transform | Instances | Auto | Residue | % |
| :-- | --: | --: | --: | --: |
| T1 bold-wrapped issue lines | 85 | 84 | 1 | **98.8%** |
| T2 letter epics → numeric | 27 epics / 288 refs | 27 / 288 | **14 orphans** | see below |
| T3 inline `(#N)` → `resolves-upstream:` | 5 | 4 | 1 | 80% |
| T4 gate `- Test (paren):` | 3 | 2 | 1 (unbalanced parens) | 67% |
| T5 `- Blocks:` referents | 75 | 62 | 13 | **82.7%** |
| T6 Risks bullet → table | 18 plans / 106 bullets | 11 plans / 70 rows | 7 plans / 12 bullets | 61% |
| T6b Risk table schema unification | 28 plans | 20 | 8 | 71% |
| T7 Success Criteria → ids | 46 plans / 367 criteria | 44 plans / 336 ids | **0 structural** | ~100% |

Issue-line population overall: **681 plain / 85 bold / 38 bare-letter-id** — bold is a minority
legacy form (11%) concentrated in plans 037–040.

`resolves-upstream:` is **already the corpus convention** (75 instances across 20 plans), so T3
converts a rare alternate spelling into the majority form rather than inventing one.

## The residue — 48 items, and it is heavily concentrated

The normalizer reports 34; a separate detector found 14 more it is structurally blind to.

**A. Requires authorship (20).** 12 risk bullets with no mitigation delimiter (plan-017 carries
6); 8 prose `- Blocks:` referents where the referent is an English predicate, e.g.
`Blocks: cutting the first real \`v*\` tag (Issue 4.2 completion)` and
`Blocks: **enabling** the deploy workflow`.

**B. Information-losing (8).** Risk tables carrying columns the 3-column canonical schema has no
slot for — `Severity` ×6, plus plan-005's `Likelihood`/`Impact`. **Six distinct risk-table
schemas exist.** These 8 are **one template-design decision, not eight edits**: does the canonical
risk table admit an optional `Severity` column?

**C. Ambiguous (6).** `Blocks: flipping \`execute.worktree\` default to on (D2).` (referent is a
*decision* id); `Depends on: Epic 6.1, 6.2` ("Epic" + an *issue*-shaped id);
`Blocks: Epic 1 and Epic 2 completion` ("completion" ≠ the epic).

**D. T2 orphan letter references (14) — the dangerous class, invisible to the normalizer.**
After the letter→numeric rename, 14 references still spell epics as letters because they use
forms the rewrite does not reach: `B/D`, `Epics A–F`, `E and F`, `B.1–B.3`, `E/F`. **13 of 14 are
in plan-012 alone.** The document ends up **self-contradictory** — `### Epic 2:` exists while the
Approach section says "parallel to B/D".

**Concentration is the good news:** of 48 residue items, plan-012 carries 15, plan-017 carries 6,
plan-010 carries 4 — and **32 of 46 plans have zero residue.**

## The criterion-id question — LOAD-BEARING

### The "6 of 47" figure was wrong twice over. The number is 2.

**Exactly 2 plans declare criterion ids** — plan-039 (`SC1`…`SC12`, incl. `SC1b`/`SC5b`) and
plan-040 (`SC1`…`SC16`), both via a `| # | Criterion | Verification |` table.

**6 *further* plans reference ids that are never declared** — plan-004 (`SC1`), plan-009
(`SC 1–6`), plan-022 (`SC-3`), plan-043 (`SC2/4/7/8/10/11`), plan-045 (`SC11`), plan-046
(`SC7/SC8`) — relying on **implicit positional numbering**. That second set is what this plan's
earlier grep counted.

> The distinction is favourable: those 6 plans are **evidence the positional convention already
> works**. Hand-checked — plan-022's `SC-3` resolves to item 3 (the `yf doctor --repair
> --remove-remote` criterion), matching Issue 4.2's risk text. Same check passes for plan-046's
> SC7/SC8.

### Positional synthesis is safe — the three feared failure modes are essentially absent

| Feared obstacle | Measured |
| :-- | :-- |
| nested sub-items in Success Criteria | **0 across all 46 plans** |
| a criteria table with no id column | **0** |
| interleaved prose blocks | **3, in 2 plans** (one stray heading, two "explicitly declined" paragraphs) |

336 ids synthesizable across 44 plans; the 2 already-ided plans keep theirs. **The normalizer must
PRESERVE existing ids, never renumber** — plans 039/040 use `SC1b`/`SC5b`, so position ≠ id, and
renumbering would silently break the 6 plans that reference positions.

### `discharged-by` CANNOT be inferred — state this plainly

Three signals tried, strongest first. Corpus-wide over 367 criteria:

| Signal | n | % |
| :-- | --: | --: |
| S2 artifact-broad (3–13 candidates — not an answer) | 111 | 30.2% |
| S2 artifact, 1–2 candidates | 111 | 30.2% |
| S3 lexical only (no signal at all) | 96 | 26.2% |
| **S1 explicit, single** | 39 | 10.6% |
| S1 explicit, multi | 10 | 2.7% |

**Only 13.3% of criteria mention an issue id at all.** Hand-adjudicating the strongest signal:
plan-039 5 hits / 3 correct; plan-046 6 hits / 5 correct → **precision ≈ 73% on the 13% where it
fires. Combined yield ≈ 10% of criteria; ~90% require authorship.**

**The failure mode is structural, not tunable: a mention is not a discharge.** plan-039's SC1 was
inferred as `1.3` because the criterion's parenthetical said *"it also contradicted 1.3's licence
to pick the next free number"*; the actual discharger is 1.1. Plan prose cites issue ids in
review-history asides at least as often as in discharge assertions, and nothing distinguishes them.

**And the signal degenerates on exactly the plans that need it most:** plan-005 SC2 returns **13**
candidate issues; **plan-001 gets no signal whatsoever on all 9 criteria.** Inference works only
on plans 039/040/046 — precisely the ones that least need it.

> **Decisive result: mechanical normalization can produce a syntactically clean corpus, but it
> cannot produce a corpus #174's matrix can consume.** ~90% of the criterion→issue edges do not
> exist in the text in any recoverable form.

## Idempotency — achieved, but only after three real defects

Zero non-idempotent plans over 46, after fixing three failures a plausible first implementation
hits. **These are the shape of the problem, not prototype sloppiness:**

1. **T7 re-prefixed its own output** — `1. **SC1.** **SC1.** …`. Needs a recognizer for the
   already-normalized form.
2. **T5 could not re-parse its own canonical output** — `- Blocks: epic:2, epic:3` fell into the
   residue on pass 2. The grammar must accept its own output as input.
3. **Transform ordering** — `- **Issue 2.2 (#100): X.**` is invisible to T1 but visible to T3, so
   T1-first leaves a bold line only a second pass unwraps. **T3 must precede T1.**

## Three classes of meaning-changing diff

**(i) T3 splits sentences.** plan-037:199 — the inserted sub-bullet lands **mid-sentence**
("…Land the / `resolves-upstream: #100` / `SPEC.md`…"). The transform is line-aware where it must
be block-aware. And four lines later the epic **already carries** `- resolves-upstream: #100
(include)`, so it also duplicates an existing mapping.

**(ii) T2 orphans** — the 14 dangling letter refs above.

**(iii) T2 rewrites the historical phase log.** plan-012:13 becomes
`- 2026-06-23 review: operator added two scope items — Epic 5 (…) and Epic 6 (…)`. That line
records what the operator said on a specific date. **Rewriting it makes the record false.**

**Where it is clean:** T6's bullet→table conversion is faithful — zero sub-bullets under any risk
bullet, zero `|` characters in cell content, verified by reading plan-021's full 6-row conversion.

## Recommendations

**Do NOT "normalize all 46 in place" as one mechanical sweep. Split three ways:**

- **Tier 1 — fully mechanical, 32 plans, zero residue.** T1/T4/T5/T6/T6b/T7, bulk diff review.
  70% of the corpus at near-zero human cost.
- **Tier 2 — mechanical + bounded human edits, 13 plans** (007, 009, 010, 017, 019, 020, 021,
  022, 023, 024, 026, 029, 038). One operator pass each; plan-017 (6 risk bullets) and plan-010
  (4 gate referents) are the heavy ones.
- **Tier 3 — exclude plan-012 from the automated T2 sweep.** 13 of 14 orphans, 188 changed lines.
  Hand-migrate. plan-015's single orphan can ride Tier 2.

**Normalizer requirements the measurement justifies:**
1. **Ship the orphan detector as a gate, not a nicety** — without it T2 produces self-contradictory
   documents the normalizer cannot see. Patterns that fired: `X/Y`, `Epics X–Y`, `X and Y`,
   `X.n–X.m`.
2. **Exclude the phase-log / `log.md` region from doc-wide id rewriting.**
3. **T3 before T1**; insert at the *end* of the continuation block; **de-duplicate** against an
   existing epic-level `resolves-upstream:`.
4. **T7 preserves existing ids, never renumbers.**
5. **Require an `--idem-check` mode as an acceptance criterion of the normalizer itself**, not as
   a manual review step.

**On `discharged-by` — three options, in order of preference:**
- **Preferred: mandatory for NEW plans only; backfill nothing.** #174's matrix starts empty and
  fills forward, with plans 039/040 as immediate real input.
- If historical coverage is genuinely required: scope it as **~330 human decisions, not a script**.
  Seed from S1 (49 candidates, ~73% precise) as a **draft to be reviewed**, never a committed
  value; expect to correct 1 in 4.
- **Do not ship a normalizer that writes an inferred `discharged-by`.** At 73% precision on 13%
  coverage it populates the matrix with mostly-absent, partly-wrong edges — **worse than an empty
  matrix, because nothing downstream could tell the difference.** This is the failure plan-046
  already named: *"a stale index is worse than no index — it asserts something false."*
