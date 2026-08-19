---
type: Plan
okf_spec: OKF-PLAN
id: plan-048-james-dixson-ed68a5
author: james-dixson
created: '2026-08-19'
status: approved
deliverable_class: standard
fingerprint: 557aea244e488c2b40dbd135fd1b971b7ae0592bf4369f2ad1dde3d719c05ff9
---
# Plan: Make the historical plan corpus machine-readable by widening the extractor grammar, and instantiate the plan-047 document-conformance engine across the remaining yf artifact types

**ID:** plan-048-james-dixson-ed68a5
**Author:** james-dixson
**Created:** 2026-08-19
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** 557aea244e488c2b40dbd135fd1b971b7ae0592bf4369f2ad1dde3d719c05ff9

## Objective
Make the historical plan corpus machine-readable by widening the extractor grammar, and instantiate the plan-047 document-conformance engine across the remaining yf artifact types

## Motivation

plan-047 built a document-conformance engine and then **stopped at its own split gate** with the
engine finished and almost nothing instantiated on top of it. That was the right call — D-13
tripped after four review cycles, and Epic 5 had just refuted a measurement the remaining epics
were planned against — but it leaves a real gap:

- The linter has **schemas for 3 document types** (`plan`, `finding`, `reference`) and the yf
  corpus has roughly a dozen. Everything unschematised is unchecked.
- The extractor enumerates unparsed constructs that plan-047 reported as 300; **EXP-001 re-measured 150 across 33 of 48 plans** (D-5). They are *reported*
  and nothing consumes the report, so the historical corpus stays unreadable to every downstream
  tool (`plan_extract.py`, the pour, `pour_fidelity.py`, #113's DAG walk, #174's criterion pass).
- _(plan-049)_ The linter runs **report-only over history**: 0 errors, 610 completeness findings. Until the
  corpus is normalized, the severity tiering is doing the work an actual fix should do.
- _(plan-049)_ Two enforcement points named in 047's Epic 9 were never bound, so a non-conformant *new* plan
  is still only caught by the FAST tier, not by `_audit_plan` at intake.

**Who is affected:** every skill that reads a plan or research bundle mechanically, and every
future plan whose intake audit silently passes documents the engine could have rejected.

**What triggered it:** the operator's SPLIT decision at plan-047's D-13 gate, with the explicit
instruction that the follow-on get a real investigation phase against corrected measurements
rather than a transcription of the descoped epics.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#173](https://github.com/dixson3/yoshiko-flow/issues/173) | success criteria and upstream dispositions never checked against the engine | partial | D-3. A linter rule over `plan.md`; 047 built the substrate | 3.4, 4.5a |
| [#172](https://github.com/dixson3/yoshiko-flow/issues/172) | yf-plan README File Layout block is stale (29 omissions) | include | D-3. Content fix the doc-type work touches anyway | 4.1 |
| [#140](https://github.com/dixson3/yoshiko-flow/issues/140) | yf-okf: enforce OKF structure below the bundle root | deferred | D-13: the migration work moves to plan-049 | — |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | M5/M9: process rules nothing executes | deferred | D-13: the enforcement binding moves to plan-049 | — |
| [#113](https://github.com/dixson3/yoshiko-flow/issues/113) | execution-rehearsal review pass (topological DAG walk) | partial | The widened grammar is its precondition; the walk itself is out of scope | 4.5a |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | review-phase validation pass (falsify + cross-check) | partial | #173's checks are a subset; the full pass stays open | 4.5a |
| [#171](https://github.com/dixson3/yoshiko-flow/issues/171) | yf-okf nested index.md generation | exclude | Blocked behind a `description:` producer change; not this plan | — |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | yf-retrospective skill | exclude | Adjacent; own plan | — |
| [#164](https://github.com/dixson3/yoshiko-flow/issues/164) | CHANGE-VALIDATION SPEC.md mis-mapping | exclude | Already fixed by plan-047 Issue 3.3 | — |
| [#165](https://github.com/dixson3/yoshiko-flow/issues/165) | SPEC `Verification:` lines are prose shaped like commands | deferred | **D-1: deferred.** Different artifact axis (226 clauses, own grammar) | — |
| [#62](https://github.com/dixson3/yoshiko-flow/issues/62) | propose a yf-spec skill | deferred | **D-1: deferred** with #165 | — |
| [#135](https://github.com/dixson3/yoshiko-flow/issues/135) | a measured literal in plan.md goes stale | deferred | **D-1: deferred** — was 047 Issue 7.3, inside Epic 7 | — |
| [#175](https://github.com/dixson3/yoshiko-flow/issues/175) | plan-047 coarse tracker | supersede | **D-2:** close once plan-048's own tracker is filed and links it | 4.5 |

## Scope Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | **AMENDED by D-13.** Carry plan-047's descoped Epic **6** (document types) plus the grammar widening that replaces its normalizer. **Defer Epic 7** (#165, #62, #135) and, per D-13, the migration and enforcement-binding epics to **plan-049**. | Operator-selected, then narrowed at approval. Epic 7 is a different artifact axis (226 SPEC clauses, own grammar; #62 proposes a whole `yf-spec` skill). The further narrowing is D-13. |
| D-2 | File a **new coarse tracker** for plan-048 and **close #175** once the new tracker exists and links it. | Operator-selected. Preserves the one-tracker-per-plan convention that `stamp-tracker` (REQ-PLAN-073) assumes; two epics stamped onto one issue breaks `upstream.py closable`'s grouping. |
| D-3 | Include **#173** and **#172**. **AMENDED after EXP-005:** plan-048 ships only #173's *mechanical* half and **leaves #173 open**. | Operator-selected, then amended. EXP-005 found #173's own final comment (*"stays open as the evidence; #174 carries the design"*) conflicts with closing it, and that defect 1 needs an LLM judge. See D-6. |
| D-4 | **AMENDED after EXP-001/003/006, then narrowed by D-13.** The `plan.md` worklist is addressed by **widening the extractor grammar** rather than rewriting documents — so this plan writes **no** corpus documents at all. The migration write phase moves to plan-049. | Operator-selected amendment. As originally written D-4 was **refuted**: 7 of 7 real transforms move the hash (EXP-006), all 150 unparsed constructs sit in fingerprinted sections (EXP-001), and the prototype run wrote **0 files**. Grammar-widening recovers ~96 of 150 constructs while touching **zero documents**, so it is hash-neutral by construction and D-4 now costs nothing. |
| D-4a | **SUPERSEDED — carried to plan-049 as a finding, not a decision here.** The eligibility conjunct it splits belongs to plan-047's prototype normalizer; `okf.py` contains no such predicate, and this plan builds no normalizer. | EXP-006 measured the original conjunct rejecting **22 of 47 plans (47%)** — denominator 47 at EXP-006 time, deliberately not re-based, since it is not re-measurable without the prototype normalizer, and rejecting them *backwards*. That measurement is still valid and is plan-049's inheritance — it is recorded here so the successor does not re-derive it. |
| D-5 | Every measured figure inherited from plan-047 is **re-measured before use**, not cited. | Epic 5 refuted EXP-003's 20 invented edges as a parser artifact. A plan that inherits numbers from an investigation whose instrument was replaced is repeating the defect it exists to fix. **It paid immediately:** the "300 unparsed constructs" is measured at **150**. |
| D-6 | plan-048 fixes #173 **defect 2 only** (bolded disposition fails OPEN): R3 two-parser agreement, normalize `parse_upstream_rows`, unknown-disposition → `fail` in `_verify_row`. **#173 stays open**; defect 1 routes to #174. | Operator-selected. The boundary is **"does the referent exist and is it shape-consistent" (plan-048) vs "is the claim true" (#174)**. Defect 2 is live today — `parse_upstream_rows` (`:3908`) returns `'**partial**'`, and plan-023 already carries two bolded cells silently unverified. |
| D-7 | **`deferred` becomes a first-class disposition literal**, alongside `include\|exclude\|partial\|supersede\|tracker`. | Operator-selected. It means *"in scope later"*, genuinely distinct from `exclude`; plan-047 uses it 3×, and **plan-048's own triage needs it** — without it the R2c rule fires on this plan. |
| D-8 | **CARRIED TO plan-049.** Any corpus rewrite is gated on a **DAG-invariance postcondition** (issues and edges may only increase, never decrease), **in addition to** the hash predicate. | EXP-001 measured a mechanical repair silently **emptying 20 `depends-on` declarations**, after which the extractor reports them *clean* — manufacturing a false-clean fidelity number. The hash postcondition caught **none** of the 20; DAG-invariance catches all of them. |
| D-9 | **CARRIED TO plan-049** (its epic numbers refer to plan-047's structure, not this plan's). **Re-sequence: `9.1 → 6.1`, not `9.1 → 8.9`.** Epic 9 is sized at **5 issues, not 3** (three unbound bindings plus two pre-existing §3 vacuities). | EXP-004: the normalizer *cannot* fix the intake blast radius — the blocking errors live in `findings/*.md` written by an agent **during** execution, after any sweep. A fail-closed `_audit_plan` today **would have blocked plan-047 at its own intake** (11 error-severity findings). |
| D-10 | **No `E`-severity check may be declared on any `docs/research/**` or `skills/**` path** unless the whole corpus already passes it. | EXP-002 measured `bundle_status: null` outside plan bundles, so `STATUS_SEVERITY` returns `{}` and `E` stays `E`. **There is no status escape hatch off the plan-bundle axis** — the single largest hidden cost in the type epic, and plan-047 never mentions it. |
| D-11 | **CARRIED TO plan-049** — not a live imperative here; no issue in Epics 0–4 touches `CHANGE-VALIDATION.md` §3. Fix the two live §3 vacuities (`docs/research/**` and `Incubator/*/research/**` map to `doclint`, which selects **0** research files) in the same change-set as any new trigger row. | EXP-004: `--path` on an unselected file returns the identical object to a **nonexistent** path — a silent green, the #164 class re-created at the rule layer. Not in plan-047's descope list; found by measurement. |
| D-13 | **Split at approval.** plan-048 ships Epics 0–3 (SPEC, grammar widening, document types, relational checks) **plus its own landing**; the corpus migration and the enforcement binding become **plan-049**, scoped by Issue 4.6. | Operator-selected. D-12's mechanical counter tripped at approval — four review cycles is exactly the signal plan-047's D-13 used, and pass 4 independently confirmed the scope (46 issues doing work sized at 25, tying plan-045's record). **The gate was right.** Splitting at approval rather than at a mid-execution halt costs nothing and lets each half land; the earlier plan of record would have blocked 15 issues and 16 criteria after Epic 3. |
| D-12 | **SUPERSEDED by D-13** — the split it would have proposed was taken at approval instead, so no mid-execution evaluator ships. Retained as the record of why the split happened. | plan-047's D-13 is the reason it stopped cleanly, and it was **mechanical** — a counter, not a judgement. The counter reached its threshold at approval — four review cycles — and the split it would have proposed mid-execution was taken at approval instead (D-13). No evaluator issue ships. |

## Investigation Findings

Six experiments ran in parallel; each is written up in full under `findings/`. Every figure below
was **measured in this repo**, and per D-5 none is inherited from plan-047.

| # | Experiment | Headline result |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-unparsed-taxonomy.md) | Unparsed-construct taxonomy | **150 constructs across 33 of 48 plans — not 300.** All 150 sit in fingerprinted sections (Epics 83 / Gates 67, **0** excluded). ~96 are mechanically recoverable; 54 need judgement |
| [EXP-002](findings/exp-002-document-type-census.md) | Document-type census | ~30 types exist, 3 have schemas; **174 of 744 files are reachable (23.4%), measured 2026-08-19. As of the D-13 restructure it is 180, because this plan joined its own corpus**. `review` (112) is the highest-value target — its consumer has **already broken in production** (#116) |
| [EXP-003](findings/exp-003-report-only-distribution.md) | Report-only distribution | 610 reproduced exactly. **371 structural / 239 content**, split perfectly along the type axis. Status explains **100%** of the report-only classification |
| [EXP-004](findings/exp-004-enforcement-binding.md) | Enforcement binding surface | 3 bindings unbound **plus 2 unreported live vacuities**. A fail-closed `_audit_plan` **would have blocked plan-047 at its own intake** |
| [EXP-005](findings/exp-005-issue-173-feasibility.md) | #173 feasibility | Structurally checkable; the era mechanism **already exists** (`STATUS_SEVERITY`). Two extractor defects are hard prerequisites |
| [EXP-006](findings/exp-006-hash-neutrality-proof.md) | Hash-neutrality proof | **7 of 7** real transforms move the hash; the prototype wrote **0 files**. D-4 as written deletes the epic — but constrains only **6.7%** of the corpus |

### The four results that changed the plan

**1. D-4 was refuted, and the refutation is structural rather than incidental.** The fingerprint
hashes exactly the sections a normalizer wants to restructure. EXP-006 proved it three ways: 7/7
worklist transforms move the hash; a prototype run over the real corpus wrote **0 files**; and the
hash is *order-sensitive*, so even relocating 7 lines **verbatim** into the correct section moves it
(EXP-001's class-F test). Amended per D-4 — the plan.md worklist is now addressed by widening the
**extractor grammar**, which touches zero documents and is therefore hash-neutral by construction.

**2. plan-047's headline number was wrong, and D-5 caught it on the first experiment.** The corpus
carries **150** unparsed constructs, not 300. EXP-001 reproduced the old figure by patching
lettered-epic support out of the extractor (327, with `Blocks=68` and `depends-on=20` matching 047's
claims *exactly*), and observed 047's own components sum to **284, not 300** — an internally
inconsistent figure mixing two builds. Citing it would have oversized the worklist ~2×.

**3. The declared dependency `9.1 → 8.9` is wrong, and the real predecessor was missing.** The
normalizer cannot fix the intake blast radius: the errors that would block a new plan live in
`findings/*.md` written **by an agent, during execution, after any sweep**. EXP-004 proved the
severity by copying plan-047's own bundle and setting it to `review` — **11 error-severity
findings**. The load-bearing predecessor is findings-type conformance (Issue 2.9 here), not the migration — which is why 2.9 ships in plan-048 even though the binding it unblocks is deferred to plan-049 (D-9, carried).

**4. Two live vacuities nobody had named.** `docs/research/**` and `Incubator/*/research/**` are
mapped to `doclint` in `CHANGE-VALIDATION.md` §3, but **no schema selects any research path** — and
`--path` on an unselected file returns the identical object to a **nonexistent** path. Silent green;
the #164 class, re-created at the rule layer. Folded in per D-11.

### Absence findings, recorded

- **`Incubator/` does not exist in this repo at all** — every `Incubator/*` glob in the three shipped
  schemas is permanently inert here, and must not be counted as coverage.
- **`scope-answers.md` has zero instances** despite having a producer. No schema.
- **R2a (dangling `Resolved By`) has zero real violations** across all 48 plans. Worth shipping
  (it has a firing mutant and is free once the join exists), but it will find nothing historically.
- **The historical corpus is not a wedge risk.** `STATUS_SEVERITY` already solved it and nothing
  re-audits a `complete` plan. **The wedge is entirely in front of us, not behind.**
- **Issues 6.1, 6.3 and part of 6.4 of plan-047's descope list are already DONE** — shipped with
  Epics 0–5. This plan must not re-schedule them.

### Corrections to plan-047's recorded figures

| Figure | plan-047 | Measured here |
| :-- | :-- | :-- |
| unparsed constructs | 300 across 33 plans | **150 across 33 of 48** |
| `reviews/pass-N.md` count | 108 | **112** |
| review-verdict drift | 13.9% | **34% per-plan** (16 of 48 latest-pass files unparseable; 47 at EXP-002 time) |
| research `artifacts/` | 39 | **25** `.md` (the 39 counted 14 JSON sidecars) |
| tracker-variant references | 13 | **4** (13 is the `comment-*` count, conflated) |
| `_audit_plan` linter binding | "breaks zero existing plans" | true of history, **false of the next plan** |

## Approach

**Make the corpus machine-readable and extend the type coverage — then land.** plan-047 shipped the
engine; this plan widens what it can read and what it checks. The corpus *migration* and the
*enforcement binding* are deliberately **not** here: they are plan-049 (D-13).

The design reversal that shapes Epic 1: plan-047 framed the `plan.md` worklist as **document
repair** under a hash-neutral constraint, and EXP-006 measured that combination at **zero files
written**. This plan re-frames it as **grammar widening** — teach the extractor the unambiguous
historical forms instead of rewriting the documents that use them. That recovers ~96 of 150
constructs, touches **zero documents**, and is hash-neutral by construction rather than by
postcondition.

Four principles carried from plan-047's execution, each earned by a defect it found:

1. **A control must demonstrate it can fail before it is trusted to pass.** Six controls in
   plan-047 were vacuous, every one invisible to inspection and visible only to execution. Every
   check this plan ships carries a named mutant, committed as a fixture.
2. **A criterion of the form "the row is green" measures nothing.** Criteria are written as *"an
   injected mutant drives exit 1"*.
3. **Re-measure, never cite.** D-5. It caught the 300 on the first experiment.
4. **Sequence by dependency, not by topic.** Four review cycles found ordering inversions in this
   plan alone; every one is now an explicit edge.

**Ordering, forced by the findings:** the escaped-pipe fix and the `unparsed[]` gate must precede the
relational rules that would otherwise emit false failures; the gate-runner must precede any gate, or
a missing script reads as a red gate rather than a harness failure.

## Epics

### Epic 0: SPEC-first amendments
<!-- epic-kind: bookkeeping -->
_Declared **bookkeeping** per Issue 3.2's carve-out marker: these issues discharge no success
criterion by design._

_**Honest residual on the R1b rule this plan ships:** **4** non-bookkeeping issues (`1.1`, `2.1`, `3.1`, `4.4`) are
named by no criterion **directly**, though all are transitively covered; `0.1`, `0.3`, `0.5`, `0.7` fall under this
epic's carve-out. Recorded rather than papered over — the plan does not exempt itself from its
own rule by silence, and "transitively covered" is a weaker test than the R1b it ships._


- Issue 0.1: Publish the free `REQ-*` id list for `spec/data.md` and `spec/portability.md` by grepping the live set; no other issue may allocate an id before this lands.
- Issue 0.2: Amend `REQ-DATA-019` for the widened `depends-on` / `Blocks:` grammar and the `deferred` literal (D-7); amend **`REQ-PLAN-074`** — which enumerates end states for `include`/`supersede`/`partial` only — to add `deferred` with the **full** contract in one line: **OPEN → `pass`, with NO plan-id-mention requirement; not-OPEN → `fail`**. A deferral is a *non-action*: there is nothing to attribute upstream, and demanding a mention would make every deferring plan halt its own reconcile. (It is **not** the same as `tracker`, which lives in `spec/cli.md` REQ-CLI-018 and is `inconclusive`-by-construction, not `pass` — the two are report-only for different reasons.) Also add a `deferred` line to `reconciler.md`'s step-3 verb list reading "no upstream action", so the agent does not meet a non-exclude row with no prescribed command. Also record the `parse_upstream_rows` bold-normalization change, and add `deferred` to the three **producer** surfaces that still offer only four options — `SKILL.md:273`, `plan_manager.py:1011` (the generated `upstream-triage.md` header) and `README.md:15` — or the literal stays undiscoverable to the agent that would use it.
  - depends-on: 0.1
- Issue 0.3: Add a `REQ-DATA-*` requirement for the extractor's `unparsed[]`-gating contract: every `plan_extract` consumer MUST return INCONCLUSIVE, never FAIL, when `unparsed[] != []`.
  - depends-on: 0.1
- Issue 0.7: Amend the SPEC to declare the **`plan-relations` check kind** — its `plan_extract.extract()` dependency, its cross-section and cross-table reach, its INCONCLUSIVE path, the R-rule family's `W` severity, and R1b's bookkeeping carve-out. **State explicitly whether `STATUS_SEVERITY` promotion applies to this kind:** if `W → E` fires at `review`, every future plan hard-fails R1b unless every non-bookkeeping issue is named by a criterion — plan-048 itself has four and escapes only by being `executing` when the rule lands. Declare it rather than inherit it by accident, and name plan-049 as the first plan graded. `REQ-DATA-024` declares only two schema flavours and a per-document contract; a kind that reasons across sections is a third mechanism, and SPEC-first is non-negotiable.
  - depends-on: 0.1
- Issue 0.5: Add a `REQ-DATA-*` requirement stating that no `E`-severity check may be declared on a path outside a plan bundle unless the corpus already passes it (D-10), and record why (`bundle_status` is null there, so `STATUS_SEVERITY` cannot soften).
  - depends-on: 0.1
- Issue 0.6a: Ship `scripts/gate-run.sh`, a **wrapper script** (not a resolver change — so no SPEC amendment is required) that executes a named gate script and maps any exit outside {0,1,2} — notably bash's **127** for a missing script — to **2** with an explicit harness-failure message. Every gate `Test:` invokes it.
  - depends-on: 0.1
- Issue 0.6: Author the two auto-gate scripts under the plan dir's `scripts/` (`gate-grammar.sh`, `gate-relations.sh`) plus a shared `_common.sh`, with the 0/1/2 exit discipline, and record each RED pre-work.
  - depends-on: 0.1, 0.6a

### Epic 1: Extractor grammar widening
- Issue 1.1: Fix `_table_rows` in `plan_extract.py` to honour GFM-escaped pipes (`(?<!\\)\|`), and fix the identical latent defect in `doc_lint.first_table`.
  - depends-on: 0.2
- Issue 1.2: Implement the `unparsed[] != []` → INCONCLUSIVE (exit 2) gate for **every `plan_extract` consumer** — the relational checks, the pour, and `pour_fidelity.py`.
  - depends-on: 0.3
- Issue 1.3: Widen the grammar for the four unambiguous historical forms: `Issue N.M` prefix inside `Blocks:`, `Epic N` → `epic:N`, column-0 `depends-on`/`resolves-upstream` sub-keys, and title parentheticals before the colon.
  - depends-on: 1.1, 0.6
- Issue 1.4: Explicitly REFUSE to auto-repair classes D and E (prose-tailed `depends-on`, dangling targets); report them with line numbers instead.
  - depends-on: 1.3
- Issue 1.4a: Ship a **negative** mutant — a construct a naive widening would recover WRONGLY (a `Blocks:` value with a trailing qualifier, and a `depends-on: Epic N` fan-out) — and assert the widened grammar REFUSES it rather than materializing a half-complete edge list.
  - depends-on: 1.3
- Issue 1.4b: Hand-audit a sample of at least 20 recovered constructs across at least 10 plans, adjudicate each against the author's evident intent, and record in `assets/edge-audit.md`. 1.4b does not set the residue target; SC1 fixes it at 54.
  - depends-on: 1.3
- Issue 1.5: Falsify the widening — assert the corpus unparsed count drops from 150 to the **declared target of 54** (EXP-001 measured ~96 of 150 mechanically recoverable; the target is fixed HERE, at approval), that **zero** documents are modified, and that `pour_fidelity.py` over every previously-poured plan reports no NEW dropped edge.
  - depends-on: 1.4, 1.4a, 1.4b

### Epic 2: Document-type instantiation
- Issue 2.1: Hoist the producer constants (`_CONTEXT_REQUIRED_SECTIONS` and siblings) from `plan_manager.py` into `_shared/plan_template.py`, so `derive_from` can resolve them — it resolves only modules under `_shared/`.
  - depends-on: 0.5
- Issue 2.1b: Backfill the missing `tests/fixtures/doclint/reference/bad.md` — the shipped third type has no known-bad fixture.
  - depends-on: 0.5
- Issue 2.2: Instantiate the `review` type (112 files) — `## Verdict:` line and the five body sections at `E`, the Resolutions table at `W` (4% conformance).
  - depends-on: 2.1
- Issue 2.3: Instantiate `upstream-reference` (194 files, glob narrowed to `upstream-[0-9]*.md`) via `derive_from`.
  - depends-on: 2.1
- Issue 2.4: Instantiate the `skill` type (19 files) — the five frontmatter keys `yf/src/frontmatter.rs` parses. Declare `user-invocable` **and `depends-on-skill`** at `W`: measured, `skills/yf-herdr/SKILL.md` omits `depends-on-skill` **deliberately** (its SKILL.md records that naming a non-shipped skill would be a force-install), so an `E` there would break a design decision, not catch drift.
  - depends-on: 2.1
- Issue 2.5: Instantiate `context` (48 files) as a consolidation of the existing `_audit_plan` check; retire the hand-maintained duplicate.
  - depends-on: 2.1
- Issue 2.6: Batch-instantiate `upstream-triage` (30), `plan-retrospective` (3) and `agent` (23) — all measured at 0% drift.
  - depends-on: 2.1
- Issue 2.7: Instantiate the research types (`Summary` 4, `artifact` 25, `sources` 4) with **every check at `W`** per D-10; record the live producer gap (21 artifact files carry zero linked citations).
  - depends-on: 2.1
- Issue 2.8: Split `references/*` into `upstream-reference` / `reference-comment` / `reference-tracker` / `reference-authored`, and do NOT extend the vendored `source:`/`retrieved:` marker beyond `user-scope/**` (it would fire 11 false positives).
  - depends-on: 2.3
- Issue 2.9: Make agent-written `findings/*.md` conform **by construction** — waive or re-scope `finding/measured-marker` (99.2% violation, exactly one conforming file corpus-wide), and reconcile `investigator.md`'s mandated output with `finding.toml`. Verify by copying a real bundle, setting it to `review`, and asserting zero errors.
  - depends-on: 2.1
- Issue 2.10: Ship one `tests/fixtures/doclint/<type>/bad.md` per newly instantiated type, each asserting FAIL, plus a conforming control asserting PASS.
  - depends-on: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8

### Epic 3: Relational checks and #173 defect 2
- Issue 3.1: Add a `plan-relations` check kind to `doc_lint.py` that calls `plan_extract.extract()` — no existing kind can read across sections.
  - depends-on: 1.2, 0.6, 1.1, 1.5, 0.7
- Issue 3.2: Implement R1 (`Discharged-by` names a real issue) and R1b (every issue is named by a criterion) at `severity = "W"`, with a **declared** bookkeeping carve-out marker so the rule cannot train authors to write fake criteria.
  - depends-on: 3.1
- Issue 3.3: Implement R2a/R2b/R2c (dangling `Resolved By`; `exclude` resolves nothing and `include` resolves something; disposition is a recognised literal) at `severity = "W"`.
  - depends-on: 3.1, 0.2
- Issue 3.4a: Add explicit `deferred` and `tracker` branches to `_verify_row` and extend `test_verify_reconcile.py` to cover each disposition's pass and fail case. **Ordered before 3.4:** without it, 3.4's "unrecognised → `fail`" turns this plan's own five `deferred` rows into a halting reconcile failure. It also preserves the deliberate `tracker` branch — not for this plan, which has no `tracker` row, but because other plans do and `REQ-CLI-018` specifies it as inconclusive-by-construction.
  - depends-on: 0.2, 3.3
- Issue 3.4: Close #173 defect 2 — implement R3 two-parser agreement, normalize `parse_upstream_rows` (`:3908`) to strip bold, and make an unrecognised disposition `fail` rather than `inconclusive` in `_verify_row`.
  - depends-on: 3.3, 0.2, 3.2, 3.4a
  - resolves-upstream: #173 (partial)
- Issue 3.5: Land the seven mutants as committed fixtures, each asserting FAIL, plus the unmutated plan-047 asserting PASS — without the control, the bold-disposition mutant passes trivially.
  - depends-on: 3.4, 3.2

### Epic 4: Reconcile and land
- Issue 4.1: Fix #172 — the yf-plan README File Layout block, 29 omissions including `SPEC.md` and `OKF-EXTENSION`.
  - depends-on: 2.10
  - resolves-upstream: #172 (include)
- Issue 4.2: Run the FULL validation tier over the merged tree and record the result.
  - depends-on: 1.5, 3.5, 4.1, 2.9, 2.1b
- Issue 4.3: Re-measure the corpus and record the post-work figures against this plan's declared targets.
  - depends-on: 4.2
- Issue 4.4: Draft the upstream comments for #113, #173 and #174, plus the coarse tracker — drafted only; posting is gated. **Each draft must carry the full plan id** (`plan-048-james-dixson-ed68a5`): `_mentions_plan_id` normalizes but requires the whole string, so a comment saying only "plan-048" does not match and would fail the three `partial` rows.
  - depends-on: 4.3
- Issue 4.5: File plan-048's coarse tracker and close #175 per D-2, once the new tracker exists and links it.
  - depends-on: 4.4
  - resolves-upstream: #175 (supersede)
- Issue 4.5a: POST the drafted comments to #113, #173 and #174.
  - depends-on: 4.5
  - resolves-upstream: #113 (partial), #174 (partial)
- Issue 4.6: Author `references/handoff-049.md` and scope plan-049 from it — the migration and enforcement-binding epics this plan deferred, the carried decisions (D-4a, D-8, D-9, D-11), the deferred upstream rows (#140, #149), and every measured figure the successor inherits.
  - depends-on: 4.5a
- Issue 4.7: Deploy — `yf self install --from-build --build` at land-the-plane, never mid-execution.
  - depends-on: 4.6

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: grammar widening is non-vacuous
- Type: auto
- Condition: the widened grammar reduces the unparsed count to the declared target of 54, modifies zero documents, and the hand-audited edge sample has been adjudicated
- Test: bash docs/plans/plan-048-james-dixson-ed68a5/scripts/gate-run.sh docs/plans/plan-048-james-dixson-ed68a5/scripts/gate-grammar.sh
- Blocks: 3.1
- Instructions: exit 0 = capability present, 1 = capability absent, 2 = harness could not run. A gate may only be red for reason 1.

### Capability Gate: relational checks can fail
- Type: auto
- Condition: the relational checks exist and can fail — `gate-relations.sh` generates its own mutants against the rules produced by 3.2/3.3 (its ancestors, not its blocked set) and asserts each drives exit 1 with the unmutated control at exit 0
- Test: bash docs/plans/plan-048-james-dixson-ed68a5/scripts/gate-run.sh docs/plans/plan-048-james-dixson-ed68a5/scripts/gate-relations.sh
- Blocks: 3.4
- Instructions: exit 0 = capability present, 1 = capability absent, 2 = harness could not run.

### Capability Gate: Upstream write
- Type: human
- Condition: the operator has authorized posting the drafted comments and closing #175
- Test: test -f docs/plans/plan-048-james-dixson-ed68a5/assets/upstream-authorization.txt
- Blocks: 4.5, 4.5a
- Instructions: outward-facing writes require explicit authorization. Drafts land in `references/comment-*.md` first; posting is a separate operator decision. Never resolved on the operator's behalf.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | The grammar widening silently changes the extracted DAG — recovering an edge incorrectly is worse than not recovering it | high | Issue 1.4a's negative mutant (assert refusal), 1.4b's hand audit, and SC1d's `pour_fidelity` no-new-dropped-edge check. **Not** D-8, which attaches to a write path the widening never enters |
| R2 | A newly instantiated research or skills type hard-fails the corpus, because `STATUS_SEVERITY` cannot soften off the plan-bundle axis | high | D-10 forbids `E` on those paths unless the corpus already passes; 2.7 declares everything `W`, and SC7 drives the boundary with a mutant |
| R3 | A relational rule emits false failures because the extractor could not parse the plan | med | Issue 1.2's `unparsed[] != []` → INCONCLUSIVE gate across every consumer, landed before any relational rule |
| R4 | A check ships that cannot fail — the defect class plan-047 found six times, and that four review cycles found repeatedly in this plan | high | Every check carries a named mutant committed as a fixture (2.10, 3.5); criteria are written as mutant-drives-exit-1, never as row-is-green |
| R5 | A figure from plan-047 is cited rather than re-measured, oversizing an epic | med | D-5, enforced across all six experiments; six corrections recorded |
| R6 | plan-049's preconditions are not actually satisfied when it is scoped, so the deferred work stalls | med | Issue 4.6 scopes it from a **handoff written while the context is live**, and 2.9 — the load-bearing precondition for the deferred enforcement binding — lands here and is gated by SC6 |
| R7 | This plan repeats plan-047's size | med | **Resolved by splitting at approval (D-13).** At 39 issues over 5 epics it is below plan-045's 46 and well below plan-047's 77. The deferred half is plan-049 |

## Success Criteria

_Every count in the **Verification** column is derived at run time. Figures elsewhere in this plan
(150 unparsed, 610 report-only, 174 of 744 reachable) are **point-in-time measurements taken
2026-08-19 during EXP-001..006** — they record what was measured, not a live count._

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | The corpus unparsed residue is **<= 54** (fixed at approval, not after the measurement), with zero documents modified | `plan_extract.py docs/plans/*/ --json` residue <= 54; `git diff --stat -- docs/plans ':!docs/plans/plan-048-*'` empty (everything after `--`, or git parses the path as a revision and exits 128) | 1.3, 1.5 |
| SC1b | For a hand-audited sample of **>=20 recovered constructs across >=10 plans**, each recovered edge matches the author's evident intent, with **zero adverse findings** — or each adverse finding traced to a named class-D/E refusal | each row carries the before/after edge pair reproducible from `plan_extract` output, plus an explicit adverse count | 1.4b |
| SC1c | A construct a naive widening would recover WRONGLY is **refused**, not half-materialized | the negative mutant drives the widened grammar to report rather than recover | 1.4a |
| SC1d | The widened grammar introduces no NEW dropped edge in any previously-poured plan | `pour_fidelity.py` over every poured plan, before vs after | 1.5 |
| SC3 | Classes D and E are reported, never auto-repaired | a test that FAILS if a repair is attempted | 1.4 |
| SC4 | A relational check returns INCONCLUSIVE, not FAIL, on a plan with non-empty `unparsed[]` | mutant plan with an unparsable construct drives exit 2 | 3.2 |
| SC4b | The `unparsed[]` gate covers the pour and `pour_fidelity.py`, not only the relational checks | each consumer driven with an unparsable plan; all report INCONCLUSIVE | 1.2 |
| SC5 | Each newly instantiated type's `bad.md` fixture **drives the linter to exit 1**, and its conforming control to exit 0 | run each fixture; assert the exit codes, not the assertion count | 2.10 |
| SC6 | A copy of a real completed bundle, set to `review`, produces zero error-severity findings with `files_checked > 0` | copy a bundle, force `bundle_status: review`, run `doc_lint` | 2.9 |
| SC7 | Removing `skill-group` from one `skills/*/SKILL.md` drives the linter to **exit 1**; the unmutated corpus exits 0 with `files_checked > 0` | mutant drive, both directions — `errors == 0` alone is true by construction, since `name`/`skill-group`/`depends-on-tool` are measured 19/19 and every research check is `W` | 2.4, 2.7 |
| SC8 | `parse_upstream_rows` and `plan_extract` agree on every disposition cell in the corpus | R3 over all plans; plan-023's two bolded cells now parse identically in both | 3.4 |
| SC9 | `deferred` is a recognised disposition **and is offered by the producer** — removing it from the recognised set drives R2c red on this plan's own table | R2c with and without `deferred` declared; plus assert all three producer surfaces — the generated `upstream-triage.md` header, `SKILL.md`'s disposition options, and `README.md:15` — list `deferred` | 0.2, 3.3 |
| SC10 | Each of the **seven committed fixtures** drives `doc_lint` to exit 1, and the unmutated plan-047 exits 0 | run each fixture directly and assert the fixture count is seven — the relational gate generates its OWN mutants and never executes 3.5's deliverable | 3.5 |
| SC10b | R1/R1b ship at `W`, and a plan with a **declared** bookkeeping epic passes R1b without inventing a criterion | R1b against a fixture plan carrying the bookkeeping marker | 3.2 |
| SC10c | Each of the **two capability-gate scripts** exits 1 — **not 127** — before its capability is built | an explicit per-script loop over `grammar relations` through `gate-run.sh`, one exit code recorded each; a glob would collapse to a single invocation | 0.6 |
| SC10d | A **missing** gate script is reported INCONCLUSIVE (2), never red — the runner maps bash's 127 to 2 | delete a script, invoke it **through the 0.6a runner**, assert exit 2 and an explicit harness-failure message | 0.6a |
| SC20 | Post-work figures meet the targets fixed at approval — unparsed residue **<= 54**, and `files_checked` **>= 600** (derived from the EXP-002 census: 2.2–2.8 name ~462 files on top of today's measured 180; the old `> 23.4%` bar was already true before any work) | 4.3's table carries a pass/fail column against those literals | 4.3 |
| SC21 | #173's posted comment names defect 1 as deferred to #174 | `gh issue view 173` shows the posted comment | 4.5a |
| SC33 | `_verify_row` returns its **declared** verdict for each of the five literals, including under a state that would fail a *different* disposition — `tracker` and `deferred` are report-only and have no symmetric fail case | a **synthetic table fixture** extending `test_verify_reconcile.py`'s existing parametrized tables; a live run over the real table is not gradeable at 3.4a, since #172/#175 are OPEN and nothing is posted until 4.5a | 3.4a |
| SC22 | #175 is closed and plan-048's own coarse tracker exists and links it | `gh issue view 175`; the new tracker's body | 4.5 |
| SC5b | **Every type instantiated in 2.2–2.8 selects > 0 files** under `doc_lint --path` — the direct antidote to the D-11 silent green | per-type `--path` drive; assert `files_checked > 0` for each | 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8 |
| SC25 | The backfilled `reference/bad.md` fixture drives the linter to exit 1 | run the fixture; assert exit 1 and a non-empty finding list | 2.1b |
| SC27 | The FULL validation tier passes over the merged tree, with a non-zero command count | `change_validation.py run --tier full --json` → `status: pass` and `commands > 0` (a zero-command green is trap #164) | 4.2 |
| SC29 | The yf-plan README File Layout block lists every file the repo actually ships | diff the block against a directory listing; assert empty | 4.1 |
| SC31 | `references/handoff-049.md` names every deferred epic, the carried decisions **D-4a, D-8, D-9 and D-11**, the deferred upstream rows **#140 and #149**, the satisfied preconditions, and the measured figures (150→54, 610, 22-of-47 eligibility, 180 files) | the file exists and each named item is present | 4.6 |
| SC32 | After deploy, `yf --version` reports the git hash of the landed commit | `yf --version` vs `git rev-parse --short HEAD` — the documented detector for a stale embedded tree | 4.7 |
