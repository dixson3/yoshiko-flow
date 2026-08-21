---
type: Reference
okf_spec: OKF-PLAN
id: handoff-051
description: What plan-050 carries forward to plan-051 — generated from plan-050's own tables by scripts/gen_handoff.py (SC18)
---

# Handoff: plan-050 → plan-051

**This file is GENERATED.** `scripts/gen_handoff.py --check` regenerates it from `plan.md`'s
tables and `diff`s the result; a non-empty diff exits **1**. That is SC18's whole point —
*"generated, not hand-listed"* is a provenance claim with no exit code, so the assertion is
the equivalent content check instead. Edit `plan.md` or the generator, never this file.

## 1. Carried-forward upstream rows

Every `partial` and `deferred` row in plan-050's Upstream Issues table — 8 of them.
Each stays **OPEN** upstream by design; `partial` rows additionally carry a plan-050 comment
recording what was done and what was not.

| Issue | Disposition | Title | Why it is carried |
| :-- | :-- | :-- | :-- |
| [#177](https://github.com/dixson3/yoshiko-flow/issues/177) | `partial` | red-team: no check that a numeric target is derivable from the plan's own scope rules | **D-6 — DROPPED from this plan after EXP-001 refuted it.** **IN:** a comment recording the refutation, so the next attempt does not rebuild the same inadequate scanner. **OUT:** any check. Derivability is not decidable from `plan.md` — `81` is textually identical whether measured or guessed, and the naive scanner missed **both** plan-049 criteria it was built for |
| [#184](https://github.com/dixson3/yoshiko-flow/issues/184) | `deferred` | §3: the red-team is never dispatched as a sub-agent — the drafter reviews its own draft | **D-9 — SPLIT OUT to plan-051**, with #182 (same epic, same deadlock). The evidence for it is unaffected and strong: this plan's own passes 1-2 were main-session self-review and advanced it to `ready-for-approval`; three independent passes then returned REVISE with 11, 17 and 14 concerns |
| [#182](https://github.com/dixson3/yoshiko-flow/issues/182) | `deferred` | red-team: the read-only rule forbids the sandbox spike that catches specification defects | **D-9 — SPLIT OUT to plan-051.** Pass-5 C39: Epic 5's gate membership was an unconditional deadlock — the control-builders sat inside the gate's own `Blocks` set, so neither the RED nor the GREEN observation was producible. The fix is structural, not a patch |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | `deferred` | M5/M9: process rules that nothing executes, and remediation edges that exist only in prose | **D-9 — SPLIT OUT to plan-051.** M9's detector was designed and its premise measured (EXP-004; pass-5 independently reproduced the 26 edges, both `created_at` fields and the 7-hour skew), but pass-5 C40 measured that the host it was wired into cannot express the INCONCLUSIVE contract the design depends on. Goes to plan-051 with that finding as its starting evidence |
| [#150](https://github.com/dixson3/yoshiko-flow/issues/150) | `partial` | research 004: process-defect mining across 83 plan bundles | **D-9.** **IN:** the six mechanical fixes (#178-#181, #186, #187) as worked instances of the ranked classes. **OUT:** M9, the M11 probe mechanism, and the remaining 14 classes — M9 goes to plan-051, the rest stay unscheduled |
| [#173](https://github.com/dixson3/yoshiko-flow/issues/173) | `partial` | success criteria and upstream dispositions are never checked against the engine that enforces them | Adjacent to #177 and #178 — both are instances of it. The general cross-check stays open |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | `partial` | a review-phase validation pass — falsify every criterion, cross-check every claim against the code that scores it | #177 and #182 close named sub-cases; the general falsification pass stays open |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | `deferred` | New skill: yf-retrospective — measure escape rate and enforce a fix+prevention contract | **D-3.** Own plan. The emit side already exists and is accumulating; a consumer built now reads a thin corpus |

## 2. Unmet `Discharged-by` references

**None.** Every `Discharged-by` reference in plan-050's Success Criteria table names an
issue that plan-050 declared and closed. This section is generated, so an empty result is
a *measurement* rather than an omission: had a criterion named an issue the plan never
declared — the dangling-reference defect that recurred in three review rounds — it would
appear here.

## 3. Descoped SPEC amendments

**EXEMPT from the tables-only rule, deliberately** (pass-6 C60). These ids appear in **no**
table, so a tables-only generator would silently drop exactly what plan-051 needs. They are
sourced from **D-9** and carried as a literal in the generator, where the exemption is
visible rather than implicit.

| Amendment | Where it was scoped | Why it left |
| :-- | :-- | :-- |
| The **M9 stamping** `REQ-*` — stamp `metadata.plan` on `discovered-from` beads at creation (D-7, forward-only) | plan-050 Epic 4, Issue 4.1 | **D-9.** EXP-004's premise held (26 edges, 0 attributed — a stamping gap, not a missing relationship), but pass-5 C40 measured that the host it was wired into **cannot express the INCONCLUSIVE contract** the design depends on. Structural, not patchable |
| Epic 5's **two `REQ-*` amendments** for the red-team read-only rule (#182) and sub-agent dispatch (#184) | plan-050 Epic 5, Issues 5.1/5.2 | **D-9.** Pass-5 C39 measured Epic 5's gate membership as an **unconditional deadlock**: the control-builders sat inside the gate's own `Blocks` set, so neither the RED nor the GREEN observation was producible. D-8's honesty clause about #182 travels with it |

## 4. The session's headline finding

Stated as a **measurement**, because it is evidence about the *process* and the successor
plan will want it.

**Three defects were caught by RUNNING a control during plan-050's execution. None was found
by the thirteen review cycles or the eleven independent red-team passes that preceded them.**

| Entry | What was believed | What running it showed |
| :-- | :-- | :-- |
| `RE-005` | the driven-red harness works | a **missing fixture** reported `RED observed` and exited **0**, writing a record with an empty exit-code field — a silent green in the instrument built to grade silent greens |
| `RE-007` | #180 is a violable ordering constraint | it is **not violable** — `bd` itself refuses. The defect is that violating it returned `inconclusive` + exit 0 and `SKILL.md` §6.4 never read `$?` |
| `RE-009` | the new grant generator is correct | it was wrong **twice**, in the direction that looks conservative: `supersede` demanded a comment its own `requires_mention: False` denies, and `file-tracker` coverage was scoped to an issue number that cannot exist before the tracker is filed |

Two of the three were caught by an arm that exists **only because a criterion demanded a
*contrast*** — an assertion that something must still **pass**, not merely fail.

The reviews that missed all three were reading artifacts for **structure**; every one of the
three was a defect in **payload** — what the thing does when run. That is the blind spot
[#188](https://github.com/dixson3/yoshiko-flow/issues/188) names (*test suites assert output
STRUCTURE and never payload FIDELITY*), stated from a second direction, and it is direct
evidence for [#190](https://github.com/dixson3/yoshiko-flow/issues/190) (*require plans to ship
tests for code they write*). **plan-051 should inherit that link rather than re-derive it.**

The counter-observation, recorded as `RE-008` so the corpus is not only failures: two
judgements execution **vindicated** — #186's both-call-sites correction (caught by a pass-11
**spike**, not by reading) and #181's preflight design holding its central claim after three
earlier scopes were each refuted by the same mechanism.

## 5. Where the descoped work's evidence lives

plan-051 starts from measurements, not from scratch:

- [`findings/exp-004-m9-remediation-edge.md`](../findings/exp-004-m9-remediation-edge.md) — M9's premise, **revised by measurement**: 26 `discovered-from` edges, **0** with plan attribution on either endpoint. The edges are intact and resolvable; only attribution is missing. Independently reproduced at pass 5, including the 7-hour bead-vs-edge skew.
- [`findings/exp-006-red-team-rule.md`](../findings/exp-006-red-team-rule.md) — #182's rule is **one line** (`red-team.md:63`) and says *"never writes files"*. It never forbade a spike at all. The defect is **under-specification**, silence read as prohibition — which matters, because a spike is what caught #186's second call site.
- `reviews/pass-5.md` — C39 (Epic 5's unconditional gate deadlock) and C40 (Epic 4's host cannot express INCONCLUSIVE). Both are **structural**, so plan-051 needs a different shape, not a patch.

