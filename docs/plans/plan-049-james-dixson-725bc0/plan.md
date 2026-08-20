---
type: Plan
okf_spec: OKF-PLAN
id: plan-049-james-dixson-725bc0
author: james-dixson
created: '2026-08-19'
status: approved
deliverable_class: standard
fingerprint: 56f8d113d0307affeba5ab2fb34df97d8ef13dc4645a0ecd370b18469624996e
---
# Plan: Rewrite the historical plan corpus so the constructs plan-048 refuses become readable, and bind the document linter at the two enforcement points that were never wired

**ID:** plan-049-james-dixson-725bc0
**Author:** james-dixson
**Created:** 2026-08-19
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** 56f8d113d0307affeba5ab2fb34df97d8ef13dc4645a0ecd370b18469624996e

## Objective
Rewrite the historical plan corpus so the constructs plan-048 refuses become readable, and bind the document linter at the two enforcement points that were never wired

## Motivation

plan-048 made the corpus *readable* and left two things deliberately undone, recorded in
`docs/plans/plan-048-james-dixson-ed68a5/references/handoff-049.md` while its execution context
was still live. This plan is that handoff executed.

- **81 unparsed constructs remain** across 24 of 49 plans. 16 are *perfectly parseable* and are
  refused for exactly one reason: recovering them means relocating a section, and plan-048's D-4
  forbade it from modifying any corpus document. **plan-049 is the plan permitted to write.**
- **The two enforcement points plan-047's Epic 9 named have still never been wired.** A
  non-conformant *new* plan is caught only by the FAST tier, not by `_audit_plan` at intake — so
  the fail-closed gate that would have blocked plan-047 at its own intake still does not exist.
- **Two `CHANGE-VALIDATION.md` §3 rows are live vacuities**: `docs/research/**` and
  `Incubator/*/research/**` map to `doclint`, which selects **zero** research files. `--path` on
  an unselected file returns the identical object to a **nonexistent** path — a silent green.

**Who is affected:** every consumer of the plan DAG (`plan_extract`, the pour, `pour_fidelity`,
#113's proposed walk) still gets INCONCLUSIVE on 24 of 49 plans; and every future plan's intake
audit still passes documents the engine could reject.

**What triggered it:** plan-048's D-13 split at approval, and its Issue 4.6 handoff.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#140](https://github.com/dixson3/yoshiko-flow/issues/140) | yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model | partial | **IN:** the readability half — grammar widening plus a 2-document structural relocation. **OUT:** nested `index.md`/`log.md` generation, the `reindex`/`--fix` verb, and the drift model — all of which route to [#171](https://github.com/dixson3/yoshiko-flow/issues/171), which this bundle's own `references/upstream-171.md` calls "the deferred half of #140". `include` would repeat the dishonesty #171 was filed to prevent | 6.5 |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | M5/M9: process rules that nothing executes, and remediation edges that exist only in prose | partial | **IN:** M5 — the enforcement binding gives the linter an executing home. **OUT:** M9 — remediation edges in prose; measured 0 of 53 `discovered-from` bead edges connect two plan epics, and no issue here touches it. Issue 4.6 records it out of scope | 6.5 |
| [#135](https://github.com/dixson3/yoshiko-flow/issues/135) | yf-plan: a measured literal in plan.md goes stale when the plan is inside its own measured corpus | include | **D-3.** Deferred twice; plan-048 produced **three live instances** (47→48 dirs, 112→119 review files, 174→180 files_checked) | 5.2 |
| [#113](https://github.com/dixson3/yoshiko-flow/issues/113) | yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state) | partial | Residue drops further here; the walk itself still out of scope | 6.5 |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it | partial | The binding closes more of the class; the falsification pass stays open | 6.5 |
| [#171](https://github.com/dixson3/yoshiko-flow/issues/171) | yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9) | deferred | Blocked behind a `description:` producer change; a separate skill's axis |  |
| [#102](https://github.com/dixson3/yoshiko-flow/issues/102) | .markdown-lint-on-edit -> .yf/markdown-lint-on-edit: gitignore semantics + migrate.rs rename | exclude | Unrelated axis |  |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract | exclude | Adjacent; own plan |  |

## Scope Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | Carry **both** deferred halves: the corpus migration write-phase (#140) and the enforcement binding (#149). | Operator-selected. They are **independent** — neither's preconditions depend on the other — so a split can cleanly shed one. The handoff's precondition analysis is already done for both. |
| D-2 | **REPLACED after EXP-001/006.** The migration is **redirected at the 89 inline `depends-on:` declarations** — a grammar widening that touches **zero documents**. Only plan-008's **7** genuinely-free relocations and the plan-015 de-bold remain as the write-phase proof. The 65 adjudications are **descoped**. | Operator-selected. EXP-001 measured **89 trailing-inline declarations across 5 plans that are invisible AND uncounted** — plan-006 and plan-007 report `0 unparsed, 0 edges` while 20 declarations go unread. Larger than the 65, entirely unambiguous, no writes. Meanwhile the 65 yield **+35 archival edges** in plans that are all `complete`, and EXP-006 measured the relocations making the report-only count **worse (+41)**. |
| D-2a | The "16 free" is **7**. Nine are not gate blocks — **and one of those nine, plan-015's de-bold, subsequently moved IN scope** (Issue 3.3 performs it), leaving **eight** out of scope; relocating them produces **content-empty gates the extractor certifies clean** — and **plan-045, the only plan D-2 fully unblocked, is entirely in that category**. | EXP-006's relocation experiment, measured on all five distinct shapes. plan-047's visible→invisible conversion, reproduced inside the migration meant to avoid it. |
| D-3 | Include **#135**, scoped: **self-exclusion primary** (`--exclude <glob>` so a plan's corpus measurements exclude itself) plus **one narrow in-flight rule** at `W`, gated on `status != complete` and skipping `findings/` and `reviews/`. Ships with its denominator-only blind spot stated. | Operator-selected. EXP-005 measured a naive check firing **41/41 with 39 correct-behaviour false positives** — the `measured-marker` failure mode. The scoped form measures **2 fires, 2 true positives, 0 false positives**. Prior art: plan-048's SC1 already self-excludes. |
| D-4 | **REPLACED after EXP-002.** The postcondition is the **four-layer form** — L1 issues, L2 materialised edges, **L3 the multiset of raw referent tokens literally written, whether or not the extractor can parse them**, and **L4 gate content** — all under **set/multiset containment, never counts**. **L3 is primary** (it is the only layer that fires on mutant A); **L4 is what observes the corpus write**, since EXP-002 measured L1–L3 at zero delta on the plan-008 relocation. Epic 1 is gated on **"the guard FAILED on mutants A and B"**, not on the corpus. Writes are bracketed by a clean git worktree so FAIL means `git checkout -- docs/plans`. | Operator-selected. **EXP-002 built the postcondition exactly as D-8 words it and drove it with the 23-emptied-declaration replay: `PASS`, exit 0** — edges *up* 2, residue *down* 22, the harm reading as an improvement. Blind for the same structural reason the hash was: a refused declaration contributes no edge. **Count-only also passes the substitution mutant** with totals exactly unchanged. And gating on the 16 is satisfiable by a no-op — measured zero edge delta, the same as a 468-diff real migration. |
| D-5 | **DEMOTED to documentation after EXP-004.** The research *selection* vacuity is **closed** — plan-048's Issue 2.7 instantiated the research types, and `files_checked` now reads 1 for a real file vs 0 for a nonexistent one. The residual "cannot fail" is **REQ-DATA-045 policy, not a defect**. The `Incubator/*` §3 rows are a **permanent no-op to document**, not work. | EXP-004, measured. Schedule at most a re-measurement of whether one research check can be promoted to `E` with the corpus pass recorded, which REQ-DATA-045 explicitly permits. |
| D-9 | **`plan-relations` promotion-off is declared in two places and implemented in neither** — fix it FIRST. | EXP-004 measured the m2 fixture at `executing` → `R` exit 0, and the **same file at `review` → `E` exit 1**. `plan-relations.toml:11` names **plan-049 as the first plan graded by this kind**, so without the fix this plan trips its own gate at its own INTAKE — the exact shape of plan-048's finding about plan-047. |
| D-10 | **Vendor `doc_lint.py` + `document_types/` under `skills/yf-plan/scripts/` before any deployed rule invokes them.** | EXP-004: `find skills -name doc_lint.py` → **empty**, and `embed.rs:47` embeds only `../skills`. An always-loaded rule would reference a file that **exists in no deployed vault**. A hard blocker on the on-edit rule, named by neither plan-047 nor plan-048. |
| D-11 | Land a **`cell-non-empty` check kind and a gate-completeness check BEFORE any corpus write.** | EXP-006 measured the empty-cell hole intact and **wider** than plan-047 recorded — a zero-row table also passes. Without these, plan-047's 90-finding exploit is available to this plan's own writes with no instrument to detect its use. |
| D-12 | **Strike "findings conform by construction" from this plan's premises.** | EXP-003: `investigator.md`'s rewrite **postdates every finding cited as evidence** (`git merge-base --is-ancestor` → YES), and the live corpus is 12/129 conforming. It is an unfalsified prediction with **n=0**. plan-047 passes today because plan-048 **demoted two checks E→R**, not because any file changed. |
| D-6 | Bind `_audit_plan` **after** re-verifying findings-type conformance, not after the migration. | Carried from plan-048's D-9. The normalizer cannot fix the intake blast radius — the blocking errors live in `findings/*.md` written by an agent **during** execution, after any sweep. |
| D-7 | Every measured figure inherited from plan-048 is **re-measured before use**. The handoff explicitly flags `610 report-only` as **not re-measured** by plan-048 (it is 1340 today). | plan-048's D-5, carried. It caught the "300" on the first experiment and the "54" at execution. |
| D-8 | **The two halves are independently landable.** If either stalls, the other ships on its own. | plan-048's split gate tripped *at approval* because its counter was constant from approval onward — a lesson worth not repeating. A structural independence guarantee is a control that can actually fire mid-execution, unlike a static count. |

## Investigation Findings

Six experiments ran in parallel; each is written up in full under `findings/`. Every figure was
**measured in this repo** at `HEAD = 7a45e97`; per D-7 nothing is inherited.

| # | Experiment | Headline |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-adjudication-taxonomy.md) | Adjudication taxonomy | Residue reproduces exactly, but the 65 are **51 adjudications** yielding **~35 archival edges**. **89 inline `depends-on:` declarations are invisible AND uncounted** |
| [EXP-002](findings/exp-002-dag-invariance-design.md) | DAG-invariance design | **D-4 as worded PASSES the replay it was written for** — exit 0 on 23 emptied declarations. The three-layer form with L3 primary is what fires *(the plan adopts a **fourth** layer, L4 gate content — see D-4)* |
| [EXP-003](findings/exp-003-intake-binding-blast-radius.md) | Intake-binding blast radius | The findings blocker is gone — **by demotion, not conformance**. "Conform by construction" is **n=0** |
| [EXP-004](findings/exp-004-unbound-enforcement-surface.md) | Unbound surface | D-5 is a no-op; **the engine is not vendored into any skill**; `plan-relations` promotion-off is declared twice and implemented never |
| [EXP-005](findings/exp-005-stale-literal-detectability.md) | #135 detectability | A naive check fires **41/41 with 39 correct-behaviour false positives**. Scoped: 2 fires, 2 true positives, 0 false |
| [EXP-006](findings/exp-006-linter-distribution.md) | Linter distribution | 610 is wrong by **2.2×** (1340). The populations overlap at **144 of 1340**, and the migration moves the count **+41** |

### The five results that re-shaped the plan

**1. The primary safety control passed the harm it was created for.** EXP-002 implemented D-4
literally, replayed the 23-emptied-`depends-on` mutation, and measured **`PASS`, exit 0** — with
edges *up* two and residue *down* 22, so the destruction read as an improvement on both instruments.
Blind for the same structural reason the hash predicate was: **a refused declaration contributes no
edge, so emptying it destroys nothing the extractor ever saw.** plan-048's all-or-nothing refusal
*widened* the blind spot. Replaced per D-4.

**2. The migration's target was the wrong population.** The 65 yield ~35 edges in plans that are
**all `complete`** — archival. Meanwhile **89 trailing-inline declarations across 5 plans are read by
nothing and counted by nothing**: plan-006 and plan-007 report `0 unparsed, 0 edges` while 20
declarations go unread. Redirected per D-2.

**3. Nine of the "16 free recoveries" are not gate blocks**, and relocating them produces
**content-empty gates the extractor certifies clean**. **plan-045 — the only plan the original scope
fully unblocked — is entirely in that category.** plan-047's visible→invisible conversion,
reproduced inside the migration written to avoid it.

**4. The intake binding is safe now, but not for the stated reason.** plan-047's bundle is clean at
`review` **because plan-048 demoted two checks `E→R`**, not because any file was fixed. And
"findings conform by construction" is unfalsified with **n=0** — the prompt rewrite postdates every
finding cited as evidence.

**Known instance of SC17's class, recorded rather than left implicit:** this bundle's own `index.md`
and `log.md` return `files_checked: 0` from `doc_lint` — indistinguishable from a nonexistent path.
That is the same silent-green vacuity the Motivation cites for `docs/research/**`, present inside the
plan that closes it. No type claims those two reserved files; SC17 is the criterion that makes the
condition reportable.

**5. This plan *would have* tripped its own gate at its own intake, and no longer does.** As drafted
it measured **4 R1b errors** at `review` (issues 1.1, 4.5, 6.3, 6.6 named by no criterion) and **3
R2b errors** from `_tbd_` cells. Both were fixed at drafting — criteria added, cells filled — and the
current measurement is **PASS, 0 errors**. Issues 0.2 and 0.3 assert it so neither can silently
regress. **Issue 0.2's justification is the corpus, not this plan:** `doc_lint.py:565` applies the
promotion map unconditionally against two declarations that say it must not, which affects every
future plan.

### Absence findings, recorded

- **D-5's research vacuity is already closed** by plan-048's Issue 2.7. Do not schedule it.
- **The `Incubator/*` schema globs are correct and load-bearing for other vaults** — only the
  per-repo `CHANGE-VALIDATION.md` rows are inert here, and those are a documentation line.
- **plan-048's "load-bearing predecessor" (findings conformance) is gone.** Do not re-schedule it.
- A real 48-bundle `okf.py migrate` (468 diffs) **legitimately passes** the corrected guard — the
  false-positive control that shows it is not FAIL-happy.

### Corrections to inherited figures

| Figure | Inherited | Measured here |
| :-- | :-- | :-- |
| report-only findings | 610 (flagged stale) | **1340** (2.2×) |
| `files_checked` | 726 | **731** (5 of plan-048's own close-out artifacts) |
| plan dirs | 48 | **49** |
| "16 free recoveries" | 16 | **7** genuinely free |
| residue after the relocations | 65 | **67** (plan-008's relocation *creates* two new refusals) |
| free-recovery distribution | plan-008 + 2 singletons | **five plans** (008=7, 010=3, 015=1, 018=2, 045=3) |
| `bundle_status` explains the residue | 100% | **57%** — 43% is declared `R` at schema level |

## Approach

**Read better before writing at all.** The investigation redirected this plan twice, and both
redirections point the same way: plan-048 recovered 39 constructs by widening the *reading* grammar
and touching zero documents, and EXP-001 found **89 more declarations** that the same technique
reaches — larger than the write-phase target, entirely unambiguous, and currently invisible to both
the parser and the residue metric. So the migration half becomes a second grammar widening, and the
write phase shrinks to the 8 lines that genuinely need a document edit.

**The corrected guard is the deliverable, not a formality.** EXP-002 proved the inherited
postcondition passes the harm it was written for. Its replacement is gated on **failing mutants A
and B** — a claim about the instrument, not the corpus — with a real 48-bundle `okf.py migrate` as
the false-positive control, and writes bracketed by a clean git worktree so FAIL means
`git checkout`.

**The self-inflicted trips were fixed at drafting, and Epic 0 asserts they stay fixed.** Both were
measured firing (4 R1b, 3 R2b) and both now measure zero. `plan-relations` promotion-off is still
unimplemented in the engine (D-9) and Issue 0.2 fixes it **for the corpus** — every future plan is
graded by a map that two declarations say must not apply.

Principles carried, each earned by a defect it caught:

1. **A control must demonstrate it can FAIL before it is trusted to pass** — and "fail" means on the
   specific harm, not on a synthetic. D-4's replacement is gated on exactly that.
2. **Re-measure, never cite.** D-7. It caught 610→1340, 48→49, 16→7, 65→67.
3. **A number is not a target unless it is derivable from what the plan permits.** plan-048's residue
   target was misderived because nobody checked it against the plan's own refusals.
4. **Unblocking is unmasking.** Every plan the extractor stops refusing trades quiet inconclusive
   rows for loud real ones. Success criteria are written on the extractor-side figure, never the
   report-only count.

## Epics

### Epic 0: SPEC-first and the two self-inflicted trips
<!-- epic-kind: bookkeeping -->
_Only **Issue 0.1** is bookkeeping — it publishes the free `REQ-*` id list and discharges no
criterion by design. **Every other issue in this epic carries one** (0.2→SC13, 0.3→SC14, 0.4→SC32,
0.5→SC33, 0.6→SC34, 0.7/0.8→SC30). The SPEC-first work is deliberately **inside** the coverage gate:
EXP-006 named a blanket `bookkeeping` declaration as an exploit that retires 834 R1b findings at zero
authoring cost, and this plan cites that finding elsewhere — it will not use the lever._

- Issue 0.1: Publish the free `REQ-*` id list to `assets/free-req-ids.md`, by grepping the live set; no issue may allocate an id before this lands.
- Issue 0.2: Fix `plan-relations` promotion — add a `promote = false` schema key (or a kind guard at `doc_lint.py:590`) that **bypasses `STATUS_SEVERITY` in both directions**, so a `W` check stays `W` at every status rather than being promoted at `review` or demoted at `complete`, plus a test asserting the fixture stays `W`. **D-9: without this, plan-049 hard-fails R1b at its own intake.**
  - depends-on: 0.1
- Issue 0.3: **Verify** this plan's own `## Upstream Issues` table produces zero R2b errors at `review`. The `_tbd_` cells EXP-003 measured were filled at drafting; this issue asserts it, so the fix cannot silently regress.
  - depends-on: 0.1
- Issue 0.4: Add a `REQ-DATA-*` for the **four-layer DAG postcondition** — L1 issues, L2 edges, **L3 raw referent tokens (primary — the only layer that fires on mutant A)**, and **L4 gate content** (gate name → `{type, condition, test, blocks}`, the only layer that observes the corpus write) — stating set/multiset containment explicitly — a reader who implements it as counts gets a control that passes the substitution mutant.
  - depends-on: 0.1
- Issue 0.5: Add a `REQ-DATA-*` for the widened trailing-inline `depends-on:` grammar.
  - depends-on: 0.1
- Issue 0.9: Once 0.2 lands, **strip the `epic-kind: bookkeeping` marker from Epic 0**. Measured: `doc_lint.py:353` exempts *every* issue in a marked epic, so the marker is a machine-level blanket exemption whatever the prose says. Stripping it leaves exactly one `W` finding (`0.1`), which is the honest state. **Expected side effect, declared:** the marker sits inside `## Epics`, which is **inside** the fingerprint span, so stripping it flips `_plan_content_fingerprint` and every later `status`/`resume` prints `STALE-APPROVED`. That warning is **advisory and expected here** — not a blocker and not a reason to halt; re-stamp with `fingerprint write` if the noise matters.
  - depends-on: 0.2
- Issue 0.7: Ship `docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh` — the wrapper mapping any exit outside {0,1,2}, notably bash's **127** for a missing script, to **2** with an explicit harness-failure message. Without it a never-authored gate script returns INCONCLUSIVE, which leaves the gate **unresolved** rather than red — so the blocked work never runs and the failure reads as a stall rather than a missing capability.
  - depends-on: 0.1
- Issue 0.8: Author `docs/plans/plan-049-james-dixson-725bc0/scripts/gate-dagguard.sh` and `…/scripts/gate-cellcheck.sh` with the 0/1/2 discipline, and **record each RED pre-work** before its capability exists. Add the `scripts/` entry to `index.md` in the same change-set — it is listed only once the directory exists, since an entry for an absent directory is an OKF ghost.
  - depends-on: 0.7
- Issue 0.6: Add a `DRIFT-CHECK.md` edge for `_shared/doc_lint.py` ↔ `skills/yf-plan/spec/data.md` — the promotion defect is exactly the class that edge exists to catch, and its absence is why two declarations disagreed with the code for a whole plan cycle.
  - depends-on: 0.2

### Epic 1: The corrected DAG guard
- Issue 1.1: Land `_shared/dag_guard.py` with `snapshot`/`verify` and the 0/1/2 exit contract, implementing the **four**-layer form — L1 issues, L2 edges, L3 raw referent tokens, **L4 gate content** (gate name → `{type, condition, test, blocks}` under containment, so a gate losing fields is a loss). Wire the recomputed fingerprint in directly — the prototype reported the *stored* field, which would read as never moving. **Do not import the skill-layer symbol into `_shared/`** (a layering inversion); hoist or reimplement it, and note that Issue 1.5 demotes the hash to a note regardless.
  - depends-on: 0.4, 0.8
- Issue 1.2: Pin **mutant A** (the 23-emptied-declaration replay) as a test asserting exit 1 on L3. This is the specific test the inherited D-4 implementation fails.
  - depends-on: 1.1
- Issue 1.3: Pin **mutant B** (edge-target substitution) as a test asserting exit 1 on L2+L3, and assert a count-only implementation would pass it — the guard against a future simplification.
  - depends-on: 1.1
- Issue 1.4: Pin **mutant D** — a real `okf.py migrate` over all 48 bundles (468 diffs) — as the false-positive control asserting exit 0.
  - depends-on: 1.1
- Issue 1.6: Add the **paired upper-bound postcondition** — no plan's edge count may grow by more than the number of declarations recovered in it — and drive it with the fan-out mutant EXP-001 measured at **+141 invented edges from 11 lines**, which loss-only containment passes cleanly. EXP-001 Rec 1, scheduled rather than deferred.
  - depends-on: 1.1
- Issue 1.5: Demote the fingerprint to a reported note that never changes the verdict; a hash-moving, DAG-preserving write is what a legal relocation *is*.
  - depends-on: 1.1

### Epic 2: Widen the grammar at the dark matter
- Issue 2.1: Widen `plan_extract` to read the trailing-inline `depends-on:` form, **including lettered referents** (21 of the 89 use them — `plan-012` carries `A.1`, `B.4`). **Zero documents modified.**
  - depends-on: 0.5, 1.2, 1.3, 1.4
- Issue 2.2: Ship a negative mutant — a trailing-inline form a naive widening would mis-attribute — and assert the grammar REFUSES rather than guessing.
  - depends-on: 2.1
- Issue 2.3: Hand-audit a sample of at least 20 recovered declarations across at least 4 of the 5 affected plans, recording the before/after edge pair per row in `assets/edge-audit-049.md`.
  - depends-on: 2.1
- Issue 2.4: Falsify — assert **at least 60 of the 89** inline declarations are recovered as edges (the target, fixed HERE at approval; 89 is the measured population and 60 is the floor after allowing for declarations naming non-issues), that corpus `unparsed[]` **does not rise above 81** (a reading widening must add no residue), that **zero** documents are modified, and that the DAG guard reports no L1–L4 loss.
  - depends-on: 2.2, 2.3

### Epic 3: The write-phase proof, and the checks that must precede it
- Issue 3.1: Add a `cell-non-empty` check kind — minimum `Verification` and `Discharged-by` in `## Success Criteria`, and a zero-row table is a finding. **Measure its blast radius over the corpus before binding it**; plan-047's "90-finding exploit" is a cited figure, and D-7 says re-measure, never cite.
  - depends-on: 0.1, 0.8
- Issue 3.2: Add a gate-completeness check whose predicate is **all three of `Type`, `Condition` and `Test` absent** — the form SC10 already states. **Measured: the `Type` + one-of predicate fires on 80 of 137 corpus gates, including all 49 Start Gates and the canonical template** (`plan_template.py:134`, `SKILL.md:451`), so binding it fail-closed at intake (Issue 4.2) would make plan-050 unable to pass its own intake. The all-absent form fires on **two** corpus gates: plan-008's `Capability Gate: d2 present (see above)` stub, and **plan-006 L194** — `### Reconcile Gate` / `- Not needed — no upstream issues incorporated`. That "declare it not needed" idiom is a live authoring form; decide explicitly whether it is exempt or should fire, and record the decision. A `Type: human` + `Approvers: operator` gate must NOT fire.
  - depends-on: 3.1
- Issue 3.2b: Ship the **false-positive control** for both new document checks — assert neither `cell-non-empty` nor gate-completeness fires on a conformant document, including the canonical Start Gate template. Epic 1 has mutant D as its false-positive control; Epic 3 had none, and that omission is what let the gate predicate above through.
  - depends-on: 3.2
- Issue 3.2a: Produce the **proposed** write diff as a dry run over the two target documents and write it to `assets/proposed-write-diff.md`, so the corpus-write gate's evidence comes from an ancestor rather than from the issue it blocks.
  - depends-on: 3.2, 2.4
- Issue 3.3: Relocate plan-008's gate block — the **only** genuine gate-block relocation — and the plan-015 de-bold, on a clean git worktree with the guard bracketing the write. Record that plan-008 does **not** clear: the relocation creates two new refusals.
  - depends-on: 1.4, 1.5, 3.2, 2.4, 3.2a, 3.2b
- Issue 3.4: Record the **eight** out-of-scope non-gate-block constructs, with the measured reason each is not a relocation. **plan-015's construct is the ninth of D-2a's split and is IN scope** — Issue 3.3 performs its de-bold — so eight, not nine.
  - depends-on: 3.3

### Epic 4: Enforcement binding
- Issue 4.1: Vendor the **full transitive set** — `doc_lint.py`, `plan_extract.py`, `plan_template.py` and `document_types/` — under `skills/yf-plan/scripts/` via `_shared/sync.py` whole-file mode, **and make root resolution explicit**: `doc_lint.py:47` computes `REPO_ROOT` from `__file__.parent.parent`, so a byte-identical vendored copy resolves the root to the *skill directory* and returns `files_checked: 0` on every real document. Resolve by git discovery or an explicit `--root`. **A byte-identical vendor of a root-relative script is not a vendor.** **D-10: hard blocker on the on-edit rule — the engine currently exists in no deployed vault.**
  - depends-on: 0.1
- Issue 4.2: Bind `_audit_plan` to the linter at `plan_manager.py:3999` **only** — sites 1 and 3 inherit (exit 1 / exit 3) and `audit_close` stays advisory for free. Map `Inconclusive` → `warn`, never `fail`.
  - depends-on: 0.2, 0.3, 3.1
- Issue 4.3: Add the always-on on-edit rule at `skills/yf-plan/protocols/DOC-LINT.md`, with **no marker** — inertness is structural via path-keying. The rule text must mandate parsing `files_checked` from `--json` and reporting `not-a-typed-document` when it is 0; an exit code cannot carry that.
  - depends-on: 4.1
- Issue 4.4: Promote **this plan's own** gate scripts (`gate-dagguard.sh`, `gate-cellcheck.sh`) into committed `CHANGE-VALIDATION.md` §1 rows. **The coupling is accepted knowingly:** these scripts become a completed bundle's at land-the-plane too, but they are authored *by this plan for this purpose* and land with it, where a historical bundle's were authored for a different plan's gates and would drift out from under the row. If a second plan needs them, move them to a non-bundle home (`_shared/` or `tests/`) rather than adding a second bundle coupling — today plan-047's and plan-048's best positive controls are executed by nothing.
  - depends-on: 4.2
- Issue 4.6: Record **M9 of #149 as explicitly out of scope** with its measurement — 0 of 53 `discovered-from` bead edges connect two plan epics — so the deferral is visible rather than implied by a truncated title.
  - depends-on: 0.1
- Issue 4.7: Retire or re-scope `upstream-triage/disposition-alphabet-offered`, measured at **30 findings over 31 files** — a rule that always fires is a constant carrying zero information, and it is live in the linter this plan binds at intake. Declined-with-reason is an acceptable outcome; silence is not.
  - depends-on: 3.1
- Issue 4.8: Schedule EXP-003's two remaining recommendations — a one-shot `R1b` sweep before enforcement, and the two `finding.toml` repairs (the stale `## Output` cross-reference, and the `sections()` fenced-template trap). Declining either is acceptable **with a recorded reason**; silence is not.
  - depends-on: 3.1
- Issue 4.5: Document the `Incubator/*` §3 rows as a permanent no-op in the manifest preamble, and record D-5's research vacuity as already closed by plan-048.
  - depends-on: 0.1

### Epic 5: #135, scoped
- Issue 5.1: Add `--exclude <glob>` to `plan_extract.py` and `doc_lint.py`, and default intake corpus measurements to exclude the plan being written. Prior art: plan-048's SC1.
  - depends-on: 0.1
- Issue 5.2: Add one in-flight lint rule at `W`, gated on `status != complete`, skipping `findings/` and `reviews/`, reading **both** status formats (`plan-026` uses `**Status:**`, not YAML).
  - depends-on: 5.1
  - resolves-upstream: #135 (include)
- Issue 5.3: Record the denominator-only blind spot in the rule's own docstring and in the closing comment — the mutant shows a numerator-drift instance passes green.
  - depends-on: 5.2

### Epic 6: Reconcile and land
- Issue 6.1: Run the FULL validation tier over the merged tree and record the result.
  - depends-on: 2.4, 3.4, 4.4, 4.5, 5.3
- Issue 6.2: Re-measure the corpus against this plan's declared targets, on the extractor-side figures. **Two drafting literals have already drifted** (`files_checked` 731→752, report-only 1340→1341) — anticipated by SC23's delta framing and D-3's self-exclusion, and itself a live instance of the #135 pattern this plan scopes.
  - depends-on: 6.1
- Issue 6.3: Draft the upstream comments for #140, #149, #135, #113, #174 and the coarse tracker. Each draft carries the **full** plan id.
  - depends-on: 6.2
- Issue 6.4: File plan-049's coarse tracker.
  - depends-on: 6.3
- Issue 6.5: POST the drafted comments **and close #135** — its `include` disposition requires CLOSED under `_verify_row`, and plan-048 halted its own reconcile on exactly that omission.
  - depends-on: 6.4
  - resolves-upstream: #140 (partial), #149 (partial), #113 (partial), #174 (partial)
- Issue 6.6: Author `references/handoff-050.md`. It is not optional — five `deferred`/`partial` rows and every unmet `Discharged-by` must appear in it, generated from the plan's own tables.
  - depends-on: 6.5
- Issue 6.7: Deploy — `yf self install --from-build --build` at land-the-plane. **It will hit AGENTS.md's consent gate on the config half and exit non-zero without `--allow-permissions-write`**; that flag is a separate operator authorization from the Upstream-write gate and must be requested, not assumed. `--force` may also be needed if `~/.local/bin/yf` exists.
  - depends-on: 6.6

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: the DAG guard can fail
- Type: auto
- Condition: the guard exits 1 on mutant A and on mutant B, and exits 0 on mutant D — a claim about the instrument, not the corpus
- Test: bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh docs/plans/plan-049-james-dixson-725bc0/scripts/gate-dagguard.sh
- Blocks: 2.1, 3.3
- Instructions: exit 0 = capability present, 1 = capability absent, 2 = harness could not run. A gate may only be RED for reason 1; a **2 leaves the gate UNRESOLVED** — it neither opens nor reds — so repair the harness rather than reading it either way.

### Capability Gate: the empty-cell and gate-completeness checks can fail
- Type: auto
- Condition: a criteria table with empty required cells drives exit 1, a zero-row table drives exit 1, and a gate with no Type/Condition/Test drives exit 1
- Test: bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh docs/plans/plan-049-james-dixson-725bc0/scripts/gate-cellcheck.sh
- Blocks: 3.3
- Instructions: exit 0/1/2 as above; a 2 leaves the gate UNRESOLVED. These checks must exist and be falsifiable before any document is written.

### Capability Gate: corpus write authorization
- Type: human
- Approvers: operator
- Condition: the operator has reviewed the **proposed** write diff at `assets/proposed-write-diff.md`, produced by **Issue 3.2a** — an ancestor of 3.3 and outside this gate's Blocks set — and authorized it
- Test: test -f docs/plans/plan-049-james-dixson-725bc0/assets/write-authorization.txt
- Blocks: 3.3
- Instructions: this plan writes to 2 documents. Review the diff, then record authorization in the named file. Never resolved on the operator's behalf.

### Capability Gate: Upstream write
- Type: human
- Approvers: operator
- Condition: the operator has authorized filing the tracker and posting the comments
- Test: test -f docs/plans/plan-049-james-dixson-725bc0/assets/upstream-authorization.txt
- Blocks: 6.4, 6.5
- Instructions: outward-facing writes require explicit authorization. Drafts land first; posting is a separate decision. **Generate the grant FROM the Upstream Issues table, not from the draft list** — plan-048's grant omitted an `include` row's required close and halted its own reconcile.

### Reconcile Gate
- Type: auto
- Condition: every execution bead under the plan epic is closed
- Test: bd list --all --include-gates --limit 5000 --json | jq -e '[.[] | select(.metadata.plan == "plan-049-james-dixson-725bc0")] as $p | ($p | length > 0) and ([$p[] | select(.status != "closed")] | length == 0)'
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | The DAG guard ships as a count-based implementation and silently passes substitution | high | Issue 1.3 pins mutant B **and** asserts a count-only implementation would pass it; D-4 states containment explicitly in the requirement text |
| R2 | The grammar widening mis-attributes a trailing-inline declaration, inventing an edge | high | Issue 2.2's negative mutant asserts refusal; Issue 2.3 hand-audits ≥20 with reproducible before/after pairs; the guard's L3 layer catches token loss |
| R3 | The write phase damages a document irrecoverably | high | Writes run on a clean git worktree so FAIL means `git checkout -- docs/plans`; scope is **2 documents**; `okf.py:1174` — the one `plan.md` rewrite, a regex-bounded slice deletion — is bracketed by the guard |
| R4 | A relocation produces a vacuous gate the extractor certifies clean | high | Issue 3.2's gate-completeness check lands **before** 3.3, and 3.4 records the **eight** remaining non-relocations as explicitly out of scope (plan-015's moved in-scope) |
| R5 | This plan trips its own gate at its own intake | high | Issues 0.2 and 0.3 are the first work after the id list; both were measured firing |
| R6 | The on-edit rule ships referencing an engine that exists in no deployed vault | med | Issue 4.1 vendors it, and is a hard dependency of 4.3 |
| R7 | #135's rule fires on correct historical behaviour | med | Scoped to `status != complete`, skipping `findings/`/`reviews/`, at `W`; measured 2 fires / 0 false positives |
| R8 | A success criterion is written against the report-only count, which the work moves upward | med | Every criterion below uses extractor-side figures; the +41 direction is stated in the plan so no reviewer reads it as regression |
| R9 | An inherited figure is cited rather than re-measured | med | D-7; seven corrections already recorded |

## Success Criteria

_Counts in the **Verification** column are derived at run time. Figures elsewhere are point-in-time
measurements taken 2026-08-19, and this plan **self-excludes** from its own corpus counts per D-3._

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | The DAG guard **exits 1 on mutant A** — the replay the inherited postcondition passed | run mutant A; assert exit 1 and `failing_layers` contains `L3` | 1.2 |
| SC2 | The guard **exits 1 on mutant B**, and a count-only implementation is shown to pass it | run both forms against B; assert 1 and 0 respectively | 1.3 |
| SC3 | The guard **exits 0** on a real 48-bundle `okf.py migrate` | run mutant D; assert exit 0 | 1.4 |
| SC4 | The fingerprint is reported, never a blocker | a hash-moving DAG-preserving write exits 0 with a `hash_note` | 1.5 |
| SC5 | **At least 60 of the 89** inline declarations are recovered as edges, with **zero documents modified** | edge count before/after against the literal 60; `git diff --stat -- docs/plans ':!docs/plans/plan-049-*'` empty | 2.1, 2.4 |
| SC6 | A trailing-inline form a naive widening would mis-attribute is **refused**, not guessed | the negative mutant reports rather than recovers | 2.2 |
| SC7 | ≥20 recovered declarations across ≥4 plans are adjudicated with reproducible before/after edge pairs | `assets/edge-audit-049.md` has ≥20 rows, each with a `before`/`after` edge pair reproducible from `plan_extract` output, plus an explicit adverse-finding count; an empty file with the right name does NOT discharge it | 2.3 |
| SC8 | plan-006 and plan-007 no longer report `0 edges` while carrying declarations | `plan_extract` on both; assert edges > 0 | 2.1 |
| SC9 | An empty required cell drives exit 1; a zero-row table drives exit 1 | the cell-check gate | 3.1 |
| SC10 | A gate with **all three** of `Type`/`Condition`/`Test` absent drives exit 1, **and the canonical `Type` + `Approvers` Start Gate template does NOT** | the cell-check gate, driven in **both** directions — measured, the one-of predicate would fire on 80 of 137 corpus gates | 3.2 |
| SC11 | The write phase modifies exactly 2 documents, and the guard reports no loss on **L4 (gate content)** — the layer that can actually observe a relocation; L1–L3 are known to show zero delta on this write (EXP-002 mutant C), so asserting them alone would be a no-op | `git diff --stat`; guard exit 0 with a non-empty L4 population | 3.3 |
| SC12 | Each of the **eight** out-of-scope non-relocations is named with its plan, line, and the measured reason it is not a gate block | the record lists eight entries. **plan-015's construct is the ninth of D-2a's split and is IN scope** — Issue 3.3 performs it — so nine would be wrong | 3.4 |
| SC13 | `plan-relations` findings stay at their **declared `W`** at `review` — the mapping is bypassed in both directions | the fixture must be a **bundle**: `tests/fixtures/doclint/plan-relations/<bundle>/plan.md` with `status: review`, driven `--type plan-relations --path`. A flat file has no sibling `plan.md`, so `bundle_status()` returns null, promotion never applies, and it **exits 0 before any fix**. Assert **exit 1 pre-fix and exit 0 post-fix from the same invocation** | 0.2 |
| SC14 | This plan's own Upstream Issues table produces zero R2b errors at `review` | `doc_lint` on a `review`-forced copy | 0.3 |
| SC15 | `doc_lint.py` and `document_types/` resolve from a deployed skill dir | `find skills -name doc_lint.py` non-empty; `sync.py --check` fails on drift | 4.1 |
| SC16 | An in-flight bundle with an injected malformed heading drives `ready-check` to **exit 3** | inject and run — **exits 0 today** | 4.2 |
| SC17 | The on-edit rule reports `not-a-typed-document` rather than PASS on an unselected path | drive it with a real unselected file | 4.3 |
| SC18 | **Two-sided:** with the `docs/plans/**` §3 row present, a DAG-breaking change under it selects and **reddens** the promoted control; with the row deleted, the same change selects it **not at all** | run both ways. Measured: the deletion yields `{"commands": [], "status": "pass"}` — a **vacuous green, never red** — and `change_validation.py` has no verb flagging a §1 id that no §3 glob references, so "deleting the row reddens it" is unsatisfiable as a one-sided assertion | 4.4 |
| SC19 | A plan's corpus measurements exclude itself — **derived, not an era literal** | run the measurement twice over the live tree: `--exclude '<plan>/**'` must equal the unexcluded count **minus that plan's own contribution**, for at least two different plans. No fixed number appears in the assertion | 5.1 |
| SC20 | The #135 rule fires on the 2 in-flight literals and on **zero** of the 39 historical ones | run over the whole corpus | 5.2 |
| SC21 | The rule's denominator-only blind spot is stated where a reader meets it | `grep -q 'denominator-only'` in both the rule's docstring and the posted comment | 5.3 |
| SC22 | FULL passes over the merged tree with a non-zero command count | `status: pass` and `commands > 0` | 6.1 |
| SC23 | Post-work figures meet the targets fixed at approval — **≥60 declarations recovered**, and corpus `unparsed[]` **≤ 73** (derived: 81 − 7 for plan-008's gate block + 2 for the refusals its relocation creates − 3 for plan-015's cascade). `files_checked` is reported as a **delta**, not a floor: a floor of 731 was already true at drafting | 6.2's table carries a pass/fail column against those literals | 6.2 |
| SC24 | The upstream grant is generated **from the Upstream Issues table**, and every non-exclude row reaches its required end state | `verify-reconcile` exits 0 | 6.4, 6.5 |
| SC25 | After deploy, `yf --version` reports the landed commit's hash | vs `git rev-parse --short HEAD`. **Documented caveat:** a docs-only commit moves `HEAD` without touching a watched file, so a legitimate no-op rebuild shows the pre-commit hash — re-stamp before asserting | 6.7 |
| SC26 | `_shared/dag_guard.py` exposes `snapshot` and `verify` with the 0/1/2 exit contract, and exits 2 when a plan vanishes from the population | drive all three exit paths, including the address-space case | 1.1 |
| SC27 | The `Incubator/*` §3 rows and D-5's closed research vacuity are recorded in the manifest itself | a preamble-scoped grep (`sed -n '1,/^## 0. Status/p'` piped to `grep -q`) for both `Incubator` and `research` — scoped, because an unscoped grep passes against the §3 rows themselves | 4.5 |
| SC28 | Every drafted upstream comment carries the **full** plan id and is verified against the real `_mentions_plan_id` matcher | run the matcher over each draft; short-form must fail | 6.3 |
| SC35 | The proposed write diff is produced **before** the corpus-write gate is evaluated, and covers exactly the two target documents | `assets/proposed-write-diff.md` exists and names plan-008 and plan-015 only | 3.2a |
| SC36 | M9 of #149 is recorded out of scope with its measurement, visible to a reader of the plan rather than implied by a title | the record states `0 of 53 discovered-from edges` | 4.6 |
| SC37 | `disposition-alphabet-offered` is retired or re-scoped so its violation rate **strictly decreases from the measured 30 of 31 baseline** (it is already not 100%, because this plan's own triage is the one non-firing file) — or a decline that **names the replacement signal** that will carry the producer-version check | the measured rate, or the named replacement; a bare "declined" does NOT discharge it | 4.7 |
| SC38 | The upper-bound postcondition **fails** the fan-out mutant EXP-001 measured at +141 invented edges, which loss-only containment passes | run the mutant against both forms; assert exit 1 and exit 0 respectively | 1.6 |
| SC39 | Epic 0's `epic-kind: bookkeeping` marker is **absent** at completion, and R1b then reports exactly one finding (`0.1`) at its declared `W` | grep the marker; run `doc_lint` and assert the single finding | 0.9 |
| SC40 | EXP-003's two remaining recommendations are each scheduled or declined **with a named reason** | both appear in the record with a disposition | 4.8 |
| SC41 | Neither new document check fires on a conformant document, and **both** checks' blast radii are **measured, not cited** — including 3.2's, whose "and nothing else" was measurably wrong at two | the false-positive control runs green on a conformant fixture and on the canonical Start Gate template; both measured counts are recorded | 3.1, 3.2, 3.2b |
| SC42 | The **vendored** engine, run from a deployed vault against a real typed document, reports `files_checked >= 1` **and reproduces the `_shared/` copy's verdict** | run both copies over the same file and diff the JSON; `files_checked: 0` does NOT discharge it, and neither does `not-a-typed-document` | 4.1 |
| SC30 | Each of the two capability-gate scripts is observed **RED at exit 1 — not 2, not 127** — before its capability lands | a per-script loop through `gate-run.sh`, exit codes recorded pre-work; a 2 means the harness, not the capability | 0.7, 0.8 |
| SC31 | Corpus `unparsed[]` after the grammar widening is **≤ 81** and after the write phase is **≤ 73** — the first is the no-added-residue floor for a reading change, the second the derived post-write target. A single ceiling of 81 would be satisfied by a whitespace-only write | `plan_extract` over `docs/plans/*/`, excluding this plan per D-3, at both points | 2.4, 3.3 |
| SC32 | The `REQ-DATA-*` for the postcondition states **set/multiset containment** explicitly, and names all four layers | `grep -q 'containment'` and each of L1–L4 in the requirement text | 0.4 |
| SC33 | The `REQ-DATA-*` for the widened grammar states the trailing-inline form and its refusal cases | the requirement text names both | 0.5 |
| SC34 | The `DRIFT-CHECK.md` edge for `doc_lint.py` ↔ `spec/data.md` exists and fires on an injected divergence | inject a contradiction; assert the edge reports it | 0.6 |
| SC29 | Every unmet `Discharged-by` and every `deferred`/`partial` upstream row appears in `references/handoff-050.md` | the enumeration is **generated** from the plan's own tables and diffed against a hand list; a typed list does NOT discharge it | 6.6 |
