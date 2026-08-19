# Handoff to plan-049

Written **while the plan-048 execution context is live** (Issue 4.6), not reconstructed
afterwards. Everything here is a measured figure or a decision with a recorded reason.

> **Status:** complete. Drafted early, at the operator's instruction, so the grammar-widening
> findings were captured while fresh; finished after Epics 2–3 and Issue 4.1–4.4 landed.

## 1. The free recovery: 16 constructs plan-049 gets at no analytical cost

plan-048 leaves a residue of **81** unparsed constructs. **16 of them are perfectly
parseable** and are refused for one reason only: recovering them means **relocating a
section**, and D-4 forbids plan-048 from modifying any corpus document.

The construct is a **whole gate block written inside `## Epics`** instead of `## Gates`:

```markdown
## Epics
### Epic 2: …
- Issue 2.1: …

### Capability Gate: d2 present        <- an H3 that is not an epic heading
- Type: human                          <- 6 gate-field bullets at column 0
- Approvers: operator
- Condition: `d2` is installed and on PATH.
- Test: `command -v d2 && d2 --version`
- Blocks: Issue 1.5 (self-verify renders), Issue 2.x / 3.x verification (need rendered PNGs)
- Instructions: `brew install d2` (already done on the dev machine; v0.7.1).
```

Measured: **13** column-0 gate-field bullets + **3** non-epic H3s = **16**, concentrated in
`plan-008-james-dixson-382e8a` with singletons in plan-018 and plan-045.

**Why this is free for plan-049 and not for plan-048.** The fields already parse — the
extractor's `GATE_FIELD` regex reads them correctly the moment they are under `## Gates`.
There is no new grammar to design, no ambiguity to adjudicate, and no risk of a wrong edge.
The only operation required is **moving the block to the `## Gates` section**, which is a
document write. plan-049 is the plan permitted to write.

**Expected residue after this move alone: 81 − 16 = 65.** Note one of the 16, plan-008's
`Blocks: Issue 1.5 (self-verify renders), Issue 2.x / 3.x verification (…)`, will *still* be
refused once relocated (wildcard `2.x / 3.x` + prose), so the realized figure is 65 with one
construct changing category rather than disappearing. **Do not claim 65 without re-measuring** —
that is exactly the mistake §4 below records.

## 2. Carried decisions

| Decision | What plan-049 inherits |
| :-- | :-- |
| **D-4a** | The eligibility conjunct rejects **22 of 47 plans (47%)**, and rejects them *backwards*. Denominator is 47 at EXP-006 time, deliberately not re-based — it is not re-measurable without plan-047's prototype normalizer, which plan-048 never built. It belongs to that normalizer, not to `okf.py`, which contains no such predicate. |
| **D-8** | Any corpus rewrite is gated on a **DAG-invariance postcondition** — issues and edges may only increase, never decrease — **in addition to** the hash predicate. EXP-001 measured a mechanical repair silently **emptying 20 `depends-on` declarations**, after which the extractor reports them *clean*. The hash postcondition caught **none** of the 20. This becomes load-bearing the moment plan-049 writes, which plan-048 never did. |
| **D-9** | Re-sequence `9.1 → 6.1`, **not** `9.1 → 8.9`. Epic 9 is **5 issues, not 3** (three unbound bindings plus two pre-existing §3 vacuities). The normalizer *cannot* fix the intake blast radius: the blocking errors live in `findings/*.md` written by an agent **during** execution, after any sweep. A fail-closed `_audit_plan` today **would have blocked plan-047 at its own intake** (11 error-severity findings). |
| **D-11** | Fix the two live `CHANGE-VALIDATION.md` §3 vacuities (`docs/research/**` and `Incubator/*/research/**` map to `doclint`, which selects **0** research files) **in the same change-set as any new trigger row**. `--path` on an unselected file returns the identical object to a **nonexistent** path — a silent green, the #164 class re-created at the rule layer. |

## 3. Deferred upstream rows

| Issue | Title | Why deferred |
| :-- | :-- | :-- |
| [#140](https://github.com/dixson3/yoshiko-flow/issues/140) | yf-okf: enforce OKF structure below the bundle root | D-13: the migration work moves to plan-049 |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | M5/M9: process rules nothing executes | D-13: the enforcement binding moves to plan-049 |

Both remain **OPEN and untouched** — `deferred` is a non-action (REQ-PLAN-074 as amended by
plan-048 Issue 0.2), so there is nothing to attribute upstream and no comment to write.

## 4. Findings that cost real time — carry them, do not re-derive them

### 4.1 The all-or-nothing refusal trade, and why it is safe

Issue 1.4a requires a partly-readable value be refused **whole**. That is not free, and one
plan pays visibly.

**plan-033 L511:** `- depends-on: 6.2, 1.5, gate:pi-rule-target-verified`

- **Before:** `6.2` and `1.5` materialized as edges; `gate:…` was reported unparsed.
- **After:** the whole declaration is refused; **two real edges are lost**, and
  `pour_fidelity` reports plan-033 as `divergent` with two "invented" edges — bd carries edges
  the extractor no longer reads.

**It is nonetheless the right trade, for a reason that is easy to miss.** REQ-DATA-043 gates
every consumer at the **document** level: plan-033 has `unparsed[] != []`, so `pour_fidelity`
returns **INCONCLUSIVE (exit 2)**, not FAIL, and the apparent divergence can never be consumed
as a verdict. **The value-level refusal and the document-level gate are the same conservatism
applied twice** — and the gate is what makes the refusal safe rather than merely lossy.
**Without Issue 1.2 landing first, this refusal WOULD have manufactured a false FAIL on
plan-033.** Sequencing 1.2 before 1.4a was load-bearing, not incidental.

### 4.2 A 62-edge "regression" that is an address-space artifact

The raw before/after `pour_fidelity` comparison showed plan-048 losing **62 edges**. It had
not lost any.

The "before" run executes in the **primary checkout** and the "after" run in the **execute
worktree**. `record-epic` writes plan-048's `**Epic:**` field **primary-side** by the SKILL.md
§5.3 address-space model, and `pour_fidelity` **skips** a plan with no `**Epic:**` field. So
plan-048 was simply *absent* from the "after" population, and its whole edge count read as a
loss.

**This is exactly the class of thing that gets mistaken for data.** Corrected net edge delta,
excluding plan-048: **+11 recovered across 6 plans, −2 lost in plan-033**. Any plan-049
measurement that compares across the two address spaces must exclude plans whose bookkeeping
fields differ between them, or it will manufacture the same artifact.

### 4.3 The recovery log had the half-complete hazard too

`Blocks:` values are refused whole, but the recovery *log* was initially written per-token as
each referent resolved — so it recorded recoveries inside values that were then refused. **6
of 43** logged recoveries were affected. The edge list was always correct; the **audit log**
was not, and an auditor would have signed off on six edges that do not exist. Recoveries are
now **staged** and committed only when the whole value resolves. Pinned by
`_shared/test_plan_extract.py`.

The general lesson, which plan-049 should assume applies to its own instruments: **the
half-complete hazard reappears in whatever records the work, not only in the work.**

## 5. The review-process gap plan-048 exposed

plan-048's residue target of **54** was **misderived, not missed**. It inherited EXP-001's
"~96 of 150 mechanically recoverable" — which counted a construct as recoverable if a rule
*could* produce an edge — while Issues 1.4/1.4a, written later in response to EXP-001's *own*
warning about wrong fixes, **refuse** several of those same classes. The plan adopted the
optimistic half of a finding and the pessimistic half of the same finding, and never
reconciled them.

**Seven red-team cycles all verified that the target was FIXED AT APPROVAL. None verified that
it was DERIVABLE FROM WHAT THE PLAN PERMITS.** The target was re-based to **81** at execution
by operator decision, with the corrected derivation recorded in `plan.md` and
`assets/residue-analysis.md`, and a mutant (`assets/residue-mutant.md`) proving a residue
*above* 81 still fails.

**Recommendation for plan-049's review protocol:** for every numeric target, require the
red-team to state the derivation *and* check it against the plan's own refusal/scope rules —
"is this number consistent with what this plan is allowed to do?" is a different question from
"is this number fixed?", and only the first would have caught this.

## 6. Measured figures plan-049 inherits

| Figure | Value | Provenance |
| :-- | --: | :-- |
| Corpus unparsed baseline | 150 across 33 of 48 plans | re-measured 2026-08-19 (D-5); plan-047's "300" was wrong |
| Residue after plan-048's widening | **81** across 24 of 48 plans | measured post-Epic-1 |
| Recovered by the four declared classes | 39 constructs / 15 plans | `recovered[]`, all hand-adjudicated, zero adverse |
| Free recovery available to plan-049 (§1) | 16 | gate-block-inside-`## Epics` |
| Report-only linter findings over history | 610 | plan-047 measurement, **not** re-measured by plan-048 — re-measure before use |
| Eligibility conjunct rejection rate | 22 of 47 plans (47%) | EXP-006; not re-measurable without the prototype normalizer |
| `doc_lint` files_checked before plan-048 | 180 | EXP-002 census |
| `doc_lint` `files_checked` after plan-048 | **726** | Issue 4.3, merged tree `e080d29` (was 180) |
| `doc_lint` error-severity findings, merged tree | **0** | Issue 4.3 |
| `doc_lint` report-only findings | **1340** | mostly R1b over history + the `R`-severity content checks |
| Document types declared | **17** | was 3 |
| Constructs recovered by the widening | **39** across 15 plans | all hand-adjudicated, zero adverse |
| FULL validation tier on the merged tree | **pass, 41 commands** | SC27 — not a zero-command green |

## 7. The deferred epics, and the state of their preconditions

D-13 split plan-048 at approval. Two bodies of work moved here.

### 7.1 The corpus migration write-phase (carries #140)

Rewrite the historical corpus so the constructs plan-048 *refuses* become readable, and
enforce OKF structure below the bundle root.

| Precondition | State | Evidence |
| :-- | :-- | :-- |
| A reading grammar that recovers the unambiguous forms | **satisfied** | 39 recoveries, 15 plans, zero adverse (Issue 1.4b) |
| A consumer contract for partially-readable plans | **satisfied** | `REQ-DATA-043`; every consumer exits 2, never 1 |
| A DAG-invariance postcondition for any write | **NOT satisfied — build it first** | D-8. EXP-001 measured a repair silently emptying 20 `depends-on` declarations, after which the extractor reports them *clean*. The hash postcondition caught **none** of the 20 |
| A `recovered[]` audit trail to diff against | **satisfied** | `plan_extract` emits before/after pairs |

**Start with the 16 free recoveries (§1).** They need no new grammar, no adjudication, and
no ambiguity call — only a section move. They are the cheapest possible first proof that the
write-phase machinery is sound, and D-8's DAG-invariance postcondition can be validated on
them before anything harder is attempted.

### 7.2 The enforcement binding (carries #149)

Bind the linter at the two enforcement points plan-047's Epic 9 named and never wired, so a
non-conformant *new* plan is caught by `_audit_plan` at intake rather than only by the FAST
tier.

| Precondition | State | Evidence |
| :-- | :-- | :-- |
| Agent-written `findings/*.md` conform by construction | **satisfied** | Issue 2.9: `investigator.md` now states the four sections and the epistemic marker as a hard output contract |
| The severity model survives the enforcement point | **satisfied** | Issue 2.9's rule — a type authored *during* the phase where the linter binds cannot carry a promotable severity. `finding`, `review` and `plan-retrospective` are `R` with one `E` teeth-check each |
| A completed bundle at `review` produces zero errors | **satisfied** | SC6, verified on a real bundle copy |
| The `CHANGE-VALIDATION.md` §3 vacuities are fixed | **NOT satisfied** | D-11: `docs/research/**` and `Incubator/*/research/**` map to `doclint`, which selects **0** research files. Fix in the same change-set as any new trigger row |

**Sequencing warning (D-9).** The normalizer *cannot* fix the intake blast radius. The
blocking errors live in `findings/*.md` written by an agent **during** execution, after any
sweep — so a fail-closed `_audit_plan` today would have blocked plan-047 at its *own* intake
with 11 error-severity findings. Issue 2.9's rule is what makes this bindable at all; bind
it before assuming a sweep is enough. Re-sequence `9.1 → 6.1`, **not** `9.1 → 8.9`, and size
Epic 9 at **5 issues, not 3**.

## 8. Process recommendation for plan-049's review protocol

Beyond §5's specific gap, three defect shapes recurred often enough in plan-048's execution
to be worth checking for deliberately:

1. **A check that reports clean while checking nothing.** R3 did this twice, in two different
   ways, and both looked like a passing rule. Every new check should be driven by a mutant
   *before* it is trusted, and a "not checked" state must render as UNVERIFIED, never as
   agreement.
2. **A measurement compared across two address spaces.** Under worktree execution, a bundle
   verification is meaningless unless the tree is named — this produced a phantom 62-edge
   regression and a phantom missing retrospective (§4.2, RE-006).
3. **A numeric target inherited from an estimate whose assumptions the plan later
   contradicted.** §5.

## 9. Where to start

1. Read `assets/residue-analysis.md` for the 81-construct itemization.
2. Take the 16 free recoveries (§1) as plan-049's Epic 1, gated on D-8's DAG-invariance
   postcondition built first.
3. Fix the two D-11 §3 vacuities before adding any trigger row.
4. Then the enforcement binding (§7.2), which has the most preconditions already satisfied.
