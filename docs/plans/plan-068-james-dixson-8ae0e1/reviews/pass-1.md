---
type: Review
okf_spec: OKF-PLAN
id: pass-1
plan: plan-068-james-dixson-8ae0e1
created: '2026-09-09'
description: >-
  [red-team pass 1] REVISE - 14 concerns. Epic 5's journal projection cannot work as designed
  (the journal keeps only the LAST step's detail), the L2 boolean projection introduces a NEW
  silent-accept on foreign checkout dirt, SPEC-first is violated in six places, and Gate 1's
  test passes vacuously by two measured routes. Recommends splitting into two plans.
---
# Red-Team Pass 1 — plan-068-james-dixson-8ae0e1

## Verdict: REVISE

Dispatched as an independent sub-agent (REQ-AGENT-049); read-only with respect to the repository,
with a sandbox spike authorized. Sandbox removed cleanly.

## Strengths

- The investigation is genuinely adversarial and the plan is built on it rather than on the beads.
  Five of nine beads refuted or re-scoped by measurement, each correction carried into the issue
  text with its evidence, plus a "rejected designs with the measurement attached" table.
  *"This is the best-evidenced plan I have read in this corpus."*
- **Gate reachability is clean.** No gate's Condition depends on evidence produced inside its own
  `Blocks` set. All four capability gates are decidable at execute start and sit at their earliest
  legal position. No cycles, no frontloading misses.
- Seam-first is not merely asserted — the zero-stub spike is a decisive measurement, and Epic 1 is
  correctly scoped to 8 sites rather than the bead's 7.
- `depends-on` hygiene is mechanically sound: **zero dangling references, zero cycles, every
  `Discharged-by` id resolves.**
- Issue 0.1's premise independently verified: `.yf/plan/config.local.json` = `{"execute.worktree":
  false}`. The hand-cut is genuinely required and correctly placed first.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **The plan does not know its own size, and R1's mitigation is measurably false.** 37 issues, not the 33 R1 and `log.md` state. Max dependency chain is **8 nodes / 7 edges** (`0.1→0.2→0.3→1.1→5.1→5.2→5.3→5.4`), not "max depth 3". "Every epic is independently landable" is false: the DAG is a single tree rooted at 0.1 and E3/E4/E5/E6 all consume 1.1 | Split into two plans. **Plan A = {0.1, 0.2, 0.3, 0.6, E1, E2, E7}** (17 issues) — the enabling half; **Plan B = {0.4, 0.5, 0.7, E3–E6}** (20). The compounding argument: Plan A lands the in-place fix, so **Plan B never pays #331's tax**. If three, Epic 5 stands alone (C2–C4) |
| C2 | high | **Epic 5's journal projection cannot work as written — the journal keeps only the LAST step's detail.** `LandingJournal.write` builds `rec["detail"] = detail` with **no merge against `prior.get("detail")`**, while `history` accumulates. L4's `merged_tree` is destroyed by L5's write. Issue 5.1 is necessary and **not sufficient**. Corroborating: the journal's `detail` field is **written but never read anywhere**, so Epic 5 adds the first reader and inherits an untested field | Add an issue ahead of 5.1: make `detail` **accumulate per phase**, bump `yf-plan/landing-journal@1 → @2`, and state the back-compat rule for an in-flight `@1` journal. This is a schema change and belongs in SPEC |
| C3 | high | **The world the projection accepts and should reject.** The two L2 facts are **booleans**, `false → true`. Projected expectation at any resume ≥ `L_MERGED_UNCOMMITTED` is `true`. If the operator leaves **unrelated uncommitted work** during the L3 halt: re-derived `true`, projected `true` — **match, digest greens**. L4's `git commit --no-edit` then sweeps foreign dirt into the merge commit and pushes it. Today that resume is a guaranteed *loud* mismatch. A **new** failure mode the projection introduces | Do not project a boolean whose post-mutation value is absorbing. Project the **content** (dirty path set / working-tree hash), or leave those two covered and accept the L3-resume halt. Also: `merge_preview.predicted_tree` staying **covered and unprojected** is load-bearing and written down nowhere — state it as an invariant in the requirement |
| C4 | medium-high | **Issue 5.3 "fail closed" is a wish, not an executable specification.** No predicate, no exit code, no definition of "corrupt or absent". The hard case it omits: a detail is legitimately absent at resume points *before* the mutating step, so "absent → fail closed" turns every early resume into a halt. R5 leans entirely on 5.3, so R5 is mitigated by an unspecified issue | Rewrite with a predicate keyed on `history`/`phase`, a named halt class, an exit code. Build on `LandingJournal.read`'s existing `{"phase": None, "corrupt": True}` return. Add a test for "absent, phase implies not-yet-mutated → proceeds" |
| C5 | high | **SPEC-first violated in six places.** No SPEC precondition for: **2.2** (dirty-tree refusal class), **2.3** (L1 checkout — a REQ-LAND-002/004 behavior change), **2.4** (merge-preview directionality, which also redefines `touches_skills`), **3.6** (REQ-LAND-009 fall-through), **6.1** (three-valued measurement), and **Epic 5 entirely** — 0.5 adds a documentation column and a rationale fix; **neither authorizes the projection mechanism**. **2.6 inverts the ordering outright** (`depends-on: 2.3` — the code it documents). Two deps are **mis-wired to unrelated requirements**: 3.1→0.7 and 6.2→0.3 | Add the missing Epic 0 SPEC issues; re-point 3.1 at a REQ-LAND-014 amendment and 6.2 at a dry-run-completeness requirement; invert 2.6 → 2.3 |
| C6 | high | **Gate 1's Test passes vacuously by two measured routes, then self-invalidates.** (A) SPEC.md absent → `test ! -r` true → **exit 0, gate passes** with the id taken — the guard is inverted from "skip if no SPEC" into "pass if no SPEC". (B) BSD-specific: spec dir missing + id present in SPEC.md → macOS grep returns 2, `!` flips it → **exit 0 on a taken id**. (C) Keys on the wrong file — ids live in `spec/landing.md` (72 refs), SPEC.md carries only amendment-log mentions. (D) Once 0.3 lands, the test **exits 1 permanently**, and §5.2b re-runs the sweep on every resume | Replace with a form that fails loudly on a missing path: `f=skills/yf-plan/spec/landing.md; test -r "$f" && test -r SPEC.md && ! grep -qE 'REQ-LAND-(037\|038)' "$f" SPEC.md`. Add `--` before paths, make it explicitly one-shot. **0.7 never names its id** — 038 appears only inside the gate |
| C7 | medium | **Gate 2 will not be run by the default sweep.** `test_class: build`, and §5.2c/§5.2d run **"the `probe` class — and ONLY the `probe` class"**. It sits unevaluated, blocking 1.1. (Command itself sound: 66 passed, exit 0, 28s) | State `--sweep-gates=all` as an execution precondition, or move the baseline check into Issue 1.1's first step |
| C8 | medium | **Gate 3 tests strictly less than its Condition.** Proves two packages import; the Condition is provisioning "for the preamble measurement", and EXP-004's whole point is that the real-CLI drive site runs in a `uv run` subprocess invisible to ordinary coverage | Provision a throwaway subprocess and assert its lines appear in the combined report — still `probe`-class, and it actually establishes the Condition |
| C9 | medium-high | **Five of eleven criteria assert a moving or non-executable fact.** **SC2** is the plan-051 SC4b shape exactly — discharged at five separate points, so never finally true. **SC5** pins **line 8732**, a literal line number in a file this plan edits at eight sites in Epic 1 alone. **SC3** is vacuous against R9 by the plan's own admission. **SC4** is not executable: design (b) puts the cut in `_worktree_ensure`, which `land --dry-run` never calls — the Verification omits the only step that makes it true. **SC10** ("exists **before**") is a presence check, green under any ordering — it cannot detect the inversion C5 found. **SC11** contradicts Gate 4's own "or narrow the set" permission | SC2 → single discharge, or restate as FULL-tier-green-at-land. SC5 → anchor on the symbol. SC3 → require a real poured-DAG fixture, or claim only what R9 concedes. SC4 → name the `worktree ensure` step. SC10 → verify ordering via git log, or drop "before". SC11 → "each authorized correction" |
| C10 | medium | **Eight of 37 issues are discharged by no success criterion:** 0.1, 0.2, **2.3, 2.4, 2.5, 2.6, 3.6, 3.7**. Not incidental — that is exactly the two adjacent defects absorbed after EXP-001, the only in-place test coverage, and the fail-closed guard on the re-push path. **The highest-novelty, least-bead-backed work has no completion criterion** | Add criteria for at least 2.3, 2.4, 3.6 — each behaviorally testable. 3.7 may decline, but then its criterion is "the decision is recorded" |
| C11 | medium | **Every line number in Epics 4, 5 and 6 is stale by construction.** Epic 1 edits 9354–9759 and Epic 2 edits ~4270, both **before** Epic 4's cited 10075–10189 and `land_cmd:8589`. By the time 4.1 runs, its seven line numbers point at the wrong statements | Convert every citation to **symbol + quoted source fragment**; keep line numbers as "as measured at investigation time" annotations only |
| C12 | medium-high | **R2 answers the wrong question.** The three-artifacts reasoning is correct, but the unnamed hazard is the inverse: **this plan must land through the un-repaired path it is repairing** — the installed `land` still carries #353's guaranteed post-`L_VALIDATED` mismatch, #352, #350, and the unwrapped bookkeeping. Not speculative: the two most recent commits on `main` are `HALT: plan-066's close chain fails verify-reconcile on 5 of 7 rows` and `HALT 2: plan-066 completes at LAND` | Add a landing-hazard section enumerating the four known halts with recovery actions. **Also the strongest independent argument for C1's split** — Plan A lands the fix, so Plan B's landing is the first that does not pay the tax |
| C13 | low-medium | **The REQ id budget is wrong.** Gate 1 reserves `037\|038`, but C5 identifies at least four more requirements the plan needs. The gate greens on a budget under-counted before Epic 0 is halfway done | Fix the id set after resolving C5; make 0.2 the single place the allocation is recorded, with the gate testing exactly that recorded set |
| C14 | low | **`context.md` is an unfilled template.** Runtime assumptions are genuinely load-bearing here (in-place mode, one address space, `gh` auth for Epic 7, network for Gate 3) and it is a portability-audit exposure at intake | Fill "Runtime assumptions" at minimum |

## Missing

- **A journal schema issue** — C2's overwrite defect, the `@1 → @2` bump, the in-flight back-compat rule. Nothing in Epic 5 touches it.
- **The two out-of-L-step cwd-less `bd` calls stay unfixed.** Issue 1.3 makes `_land_epic_from_bd:6504` and `_land_route_record_findings:6623` **advisory only**, so the plan closes #348's normative sentence while leaving two calls reading a database from the wrong cwd. Fix them or declare the boundary in SPEC.
- **L19's in-place degradation is named by EXP-001 and dropped.** Design (b) mostly fixes it by making HEAD a real merge commit — but that inference is never stated, and it is the *redeploy* precondition. 2.4 fixes the preview side only.
- **`--validate-decision`'s CLI branch (8457–8476) is entirely uncovered** and is the middle of three landing modes. Scoping Epic 3 to `--apply` is legitimate but should be *declared*.
- **No end-to-end criterion for the capability the plan exists to deliver.** Nothing asserts `execute` in-place → cut → commit → `--dry-run` → `--apply` → `L_DONE`.
- **The seam has no `env=` parameter.** One sentence in 1.1 deciding to add it or declaring it out of scope.
- Minor: **SKILL.md §5.2a names `.yf-plan.local.json`; the actual file is `.yf/plan/config.local.json`.** The plan is right; the skill prose is drifted.

## Gate Assessment

| Gate | Reachable | Decidable | Test verdict (run literally) |
| :-- | :-- | :-- | :-- |
| Start (human) | yes | n/a | n/a |
| REQ id allocation is free | yes | yes | **BROKEN** — vacuous exit 0 by two routes; keys on the wrong file; exits 1 permanently after 0.3 |
| Baseline suite green | yes | yes | **Sound** (66 passed, 28s) but `build` class, so the default `probe` sweep never runs it |
| Coverage tooling available | yes | yes | Exits 0 in <1s. **Weaker than its Condition** |
| Publish upstream corrections | yes | n/a | **Correctly modeled** — empty test + `consent` + `human`. Its "narrow the set" permission contradicts SC11 |

No gate depends on evidence its `Blocks` set produces; no cycles, no frontloading misses. The
failures are vacuity and class-routing, not reachability.

## Upstream Assessment

Dispositions reasonable; the three exclusions each a genuinely different axis with the operator
decision recorded. #304 in particular would have turned this into a consent-model redesign.

- **`Resolved By` is `_TBD_` on all seven includes** — expected pre-intake, but **#349 is claimed by
  four issues across three epics**. Under a C1 split it straddles both plans and its close condition
  needs stating, or it will be closed by whichever lands second on partial evidence.
- **Epic 7 publishes before the code exists.** 7.1 is defensible (pure factual corrections, true
  today). **7.2 is not** — it re-scopes `yf-jp7z` to match an implementation C2/C3/C4 say is not yet
  correctly designed. **Hold 7.2 until Epic 5's design is settled.**

## Resolutions

All fourteen resolved. C1 and C12 were operator decisions; the remainder were resolved by the main
session. C2, C3, C4 and C8 are **carried to plan-069** rather than fixed here, because the A/B
split moved the work they concern into Plan B — they are recorded as open design questions in that
bundle's Investigation Findings, not dropped.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 split into two plans | high | **Split confirmed.** plan-068 is now Plan A (22 issues, longest chain 6 nodes — both re-measured); plan-069 created and seeded with Plan B's scope, inherited findings and open design questions. R1 rewritten; the false "independently landable" claim withdrawn | `operator` | `resolved` |
| C2 journal keeps only last detail | high | **Verified independently** — `rec["detail"] = detail`, no merge with `prior`, while `history` accumulates; and the field is written but never read. **Carried to plan-069** with the per-phase accumulation and `@1 → @2` schema bump stated as a precondition on its digest epic | `main-session` | `resolved` |
| C3 boolean projection silent-accept | high | Accepted as a real new failure mode. **Carried to plan-069**, together with C3b — that `predicted_tree` staying covered and unprojected is load-bearing and must be stated as an invariant | `main-session` | `resolved` |
| C4 5.3 fail-closed unspecified | medium-high | **Carried to plan-069** with the predicate requirement made explicit: keyed on `history`/`phase`, named halt class and exit code, and handling a legitimately-absent detail before the mutating step | `main-session` | `resolved` |
| C5 SPEC-first violated ×6 | high | **Fixed in Plan A's scope.** Added Issue 0.4 (REQ-LAND-002/-004 for L1 checkout + in-place step semantics) and Issue 0.5 (merge-preview directionality) as SPEC preconditions for 2.3 and 2.4; folded the dirty-tree refusal class into 0.6 as the precondition for 2.2. **Ordering inversion corrected** — old 2.6 documented SPEC and depended on the code implementing it; the SPEC now lands in 0.4 and 2.6 only verifies agreement. The two mis-wired deps (3.1→0.7, 6.2→0.3) went to plan-069 with their epics | `main-session` | `resolved` |
| C6 Gate 1 test vacuous | high | **Both routes reproduced in a sandbox** — exit 0 on a *taken* id with SPEC.md absent, and again on macOS with the spec dir missing. Test rewritten to fail loudly on a missing path and to key on `spec/landing.md` (63 REQ-LAND refs vs SPEC.md's 18). Marked ONE-SHOT in the Instructions. `REQ-LAND-037` re-verified free | `main-session` | `resolved` |
| C7 Gate 2 never swept | medium | Instructions now state explicitly that it is `build` class and requires `--sweep-gates=all`, or must run as Issue 1.1's first step | `main-session` | `resolved` |
| C8 Gate 3 weaker than condition | medium | Gate removed from Plan A — coverage tooling is only needed by the preamble epic. **Carried to plan-069** with the subprocess-coverage requirement recorded | `main-session` | `resolved` |
| C9 five criteria moving/non-executable | medium-high | All rewritten. SC2's five-way discharge replaced by a single FULL-tier-green-at-land criterion (now SC8); the line-number anchor (8732) is gone with its epic; SC3 reworded to claim only what R7 concedes; SC4 now names the `worktree ensure` step and is an end-to-end assertion; SC9 is a **git-log ordering** check, not a presence check; SC10 says "each **authorized** correction" and additionally asserts #349/#353 remain OPEN | `main-session` | `resolved` |
| C10 eight issues undischarged | medium | **Zero undischarged issues** — re-verified mechanically. Added SC0 (branch cut, plan-062 SC0b precedent), SC5 (L1 self-merge), SC6 (directionality + `_land_changed_set`), SC7 (dirty-tree refusal); 0.2 folded into SC9 and 1.2 into SC8 | `main-session` | `resolved` |
| C11 line numbers stale by construction | medium | Every citation converted to **symbol + quoted fragment**, with a standing note at the head of the Epics section that line figures are investigation-time annotations only | `main-session` | `resolved` |
| C12 landing-hazard playbook missing | medium-high | **Operator chose the playbook.** New Epic 4 / Issue 4.1 enumerates the four known halts on this plan's own landing path with recovery actions and the clean-`main` redeploy rule; R2 rewritten to name the inverse hazard. SC11 asserts it | `operator` | `resolved` |
| C13 REQ id budget under-counted | low-medium | Issue 0.2 rewritten to allocate and **record** the full id set in one place, and Gate 1 now tests exactly the recorded set. Plan A needs three ids plus the REQ-BRANCH amendments | `main-session` | `resolved` |
| C14 context.md unfilled | low | New Issue 4.2 fills Runtime assumptions — in-place execution and its single address space, `gh` credentials for the consent gate, and the `uv --with` network dependency | `main-session` | `resolved` |

**Final status: all concerns resolved.** Plan A re-verified mechanically after the rewrite —
5 epics, 22 issues, 5 gates, 12 criteria, 9 risks, zero `unparsed`, zero dangling edges, zero
cycles, zero undischarged issues, longest dependency chain 6 nodes.
