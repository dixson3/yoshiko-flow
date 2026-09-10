---
type: Review
okf_spec: OKF-PLAN
id: pass-2
plan: plan-068-james-dixson-8ae0e1
created: '2026-09-09'
description: >-
  [red-team pass 2] REVISE - 14 concerns on the restructured Plan A. REQ-LAND-037 would be FALSE
  the moment it landed (three indirect launchers via _run_git, and both declared exceptions were
  the wrong ones); Issue 2.5's end-to-end test was unreachable without Epic 1; SC9 was not
  executable; and three items were dropped by BOTH plans. Gate 1's pass-1 fix verified genuine.
---
# Red-Team Pass 2 — plan-068-james-dixson-8ae0e1

## Verdict: REVISE

Fresh adversarial pass over the restructured Plan A, with pass-1 as prior context. Read-only;
three sandboxes created and all removed.

## Strengths

- **Gate 1 is genuinely fixed.** The rewritten Test run literally across **8 BSD/macOS cases**:
  id free → `0`; taken in `landing.md` → `1`; taken in `SPEC.md` only → `1`; `SPEC.md` absent →
  `1`; spec dir absent → `1`; `landing.md` absent + id in `SPEC.md` → `1`; unreadable file → `1`.
  Both pass-1 vacuity routes closed.
- **Gate 2 verified sound:** `66 passed`, exit 0, 22.4s.
- **EXP-002's scope claim independently reproduced** — an independent AST scan found exactly 8
  `subprocess.run` calls inside `_land_l\d+_*`, exactly two cwd-less. Issue 1.1's 8-site scope is
  right; the bead's 7 is wrong.
- **DAG mechanically clean**, re-measured: zero dangling, zero cycles, zero undischarged.
- **#349/#353 "partial, do not close" is sound and honest** — no criterion asserts their closure.

## Concerns

| # | Severity | Concern | Resolution |
| :-- | :-- | :-- | :-- |
| C1 | high | **REQ-LAND-037 would be FALSE the moment Issue 0.3 landed it.** `_run_git` is a bare `subprocess.run(["git", ...], cwd=cwd)` with no root default, and three helpers called from inside L-steps route through it: `_land_capture_conflict` (L1, L2), `_land_abort_merge` (L1, L2), `_land_changed_set` (close chain, L19). **Both exceptions 0.3 declared were the wrong ones** — `_land_epic_from_bd` / `_land_route_record_findings` are called from no L-step at all. Issue 1.3's check keys on the *token* `subprocess.*`, so it is blind to indirect launchers: SC1 and SC2 would pass while the requirement was violated at five sites | **Verified independently in the source.** 0.3 rewritten: REQ-LAND-037 now says "launches **directly**", enumerates the three ctx-less helpers as declared, and corrects the wrong exception pair. 1.3's AST check extended to the indirect-launcher set, resolved from 0.3's declared list rather than a second hand-written one |
| C2 | high | **Issue 2.5's end-to-end `--apply` test was unreachable at its dependency set** — it depended on 2.1–2.4 with no Epic 1 edge, but EXP-002 measured that unpatched the run halts at `l14_pour_fidelity` at 18 rows and never reaches `L_DONE`. It also named no mechanism for suppressing L6/L7/L12/L16/L17/L19's outward writes | `depends-on` now includes **1.1, 1.5**; the harness is named (`_build_sandbox` + injected runner), and the runner is identified as what keeps push / `gh` / cascade / redeploy inside the sandbox |
| C3 | high | **SC9 was not executable** — no command; unscoped it would FAIL a compliant plan (this repo's `plan_manager.py` predates `spec/landing.md` by months); AGENTS.md permits same-commit staging, which was undecidable; and it carried 6 of 23 issues on one criterion | **Command written and verified in a sandbox across five cases** (spec→code 0, code→spec 1, same-commit 0, code-with-no-spec 1, spec-only 0), scoped to `main..HEAD`. Split into SC9 / SC9b / SC9c |
| C4 | medium-high | **Gate 1 tested strictly less than its Condition** — greped `037` alone while the Condition said "every id 0.2 records", and **Issue 0.5's requirement had no id anywhere in the plan**. Blocked 0.3 only; omitted `spec/phases.md` where the REQ-BRANCH ids live | 0.5's requirement is now **`REQ-LAND-038`**, named in the issue; the Test covers `037\|038`, blocks 0.3 **and** 0.5, and adds `spec/phases.md`. Re-run on the live repo: exit 0, both ids free |
| C5 | medium-high | **Issue 2.1 had no idempotent re-attach path.** `_worktree_ensure` runs on every `execute` and promises "idempotent create-or-reattach", but `git checkout -b` on an existing branch exits 128. The `opted-out` short-circuit also sits above `_resolve_execute_base`, so design (b) must reach the pinned-base resolver | 2.1 now states the **three-way branch** (absent → `checkout -b <base>`; exists → plain `checkout`; already on it → no-op), notes the short-circuit's position, and asks explicitly whether the bd-resolution probe applies in-place |
| C6 | medium-high | **Three items were dropped by BOTH plans:** the `recover()` fall-through fail-closed fix (*"the single line standing between an unhandled action and a re-push"*, named twice by pass-1), the "no write occurred" helper, and `_land_assert_primary_checkout`'s behavioral test. plan-069's text never mentioned any of them | **The genuine escape of this split.** All three written into plan-069's text under a "do not drop these again" heading, plus EXP-003's post-L4 digest absence finding and EXP-001's L4 misleading diagnostic. New **Issue 3.3** verifies plan-069 carries them *before* 3.2 publishes the cross-reference; **SC12** discharges it |
| C7 | medium | **R1 still said "20 issues"; measured 22** — the exact defect C1 named, surviving inside the row C1's resolution rewrote. SC8 attributed "the landing test suite passes" partly to the landing-hazard-playbook issue, evidence that "zero undischarged" was reached partly by padding `Discharged-by` cells | Counts corrected to **23** in both places and re-measured from `plan_extract.py`; a note now records that every count is taken from tooling rather than written by hand. SC8 re-pointed at 1.1/1.3; new **SC8b** gives 1.2 a criterion that actually asserts the `{"uv"} → {"uv","bd"}` change |
| C8 | medium | **SC2's second clause asserted a property no requirement stated** — 0.3 declared the two helpers *outside* REQ-LAND-037 while 1.4 fixed them, a behavior change with no REQ ahead of it under a SPEC-first mandate | 0.3 now carries the clause: the ctx-less landing helpers resolve their working directory from an explicit root argument. 1.4's serializing `depends-on: 1.1` dropped for `0.3` |
| C9 | medium | **Cross-plan coupling neither plan recorded:** Issue 2.5's `--apply` test could only clear the consent gate *because* of `#334`'s unconditional bypass — which plan-069 fixes | 2.5 now passes an **explicit tty allow-list** rather than relying on the bypass, and the coupling is recorded in plan-069 |
| C10 | low-medium | **plan-069's Upstream Issues table was empty**, so Issue 3.2 would publish a cross-reference pointing at a bundle recording no disposition for #349/#353 | Table seeded with #334/#349/#350/#352/#353, marking #349 and #353 as closed **by that plan** |
| C11 | low-medium | **Gate 2 was not ONE-SHOT** although its Condition is "green **before any seam routing**" and §5.2b re-sweeps on resume | Marked ONE-SHOT with the reason stated |
| C12 | low | **Issue 2.3's necessity was not established** — once 2.1 lands, `ctx.root`'s HEAD *is* the execute branch, so the measured self-merge disappears with 2.1 alone, and SC5 was satisfiable without 2.3 | 2.3 restated as **defence-in-depth against ambient HEAD**; SC5 now requires a test that **moves HEAD off the execute branch before L1**, so it fails under 2.1-only |
| C13 | low | Three smaller drops: EXP-001's design **(d)** absent from the rejected table; L4's misleading `pull --rebase` diagnostic unfixed and unmentioned; the `.yf-plan.local.json` vs `.yf/plan/config.local.json` drift in code and `SKILL.md` | (d) added to the rejected-designs table with its measurement; the L4 diagnostic recorded in plan-069 as legibility-not-safety; the filename drift folded into 2.1 as an opportunistic one-line fix in code it already edits |
| C14 | low | **Gate 1 exited `1` indistinguishably** for "id taken" and "path missing" while its Instructions claimed it "fails loudly on a missing path" | Test now echoes `MISSING: <path>` to stderr before exiting |

## Missing (all closed)

Every item pass-2 listed as missing is now carried: SC9's command (verified), Issue 0.5's id
(`REQ-LAND-038`), Issue 2.5's outward-write suppression mechanism, the three dropped EXP-004
items, and EXP-003's post-L4 digest absence finding.

## Gate Assessment

| Gate | Test run literally | Verdict |
| :-- | :-- | :-- |
| Start (human) | n/a | correct |
| REQ ids are free | 8 cases on BSD/macOS, all correct; live repo exit 0 | **pass-1's C6 genuinely fixed**; scope widened at C4/C14 |
| Baseline suite green | `66 passed`, exit 0, 22.4s | Sound; ONE-SHOT added at C11 |
| Publish upstream corrections | empty Test + `human` + `consent` | Correctly modeled |
| Reconcile | auto | standard |

*"No gate passes vacuously and no gate depends on evidence its `Blocks` set produces."*

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 REQ-LAND-037 false on arrival | high | 0.3 narrowed to "directly" + three declared helpers; wrong exception pair corrected; 1.3 extended to indirect launchers | `main-session` | `resolved` |
| C2 2.5 unreachable | high | `depends-on: 1.1, 1.5`; harness and write-suppression named | `main-session` | `resolved` |
| C3 SC9 not executable | high | Command written and sandbox-verified across 5 cases; split into SC9/9b/9c | `main-session` | `resolved` |
| C4 Gate 1 < Condition | medium-high | `REQ-LAND-038` named; alternation, `Blocks: 0.5`, `phases.md` added | `main-session` | `resolved` |
| C5 no idempotent re-attach | medium-high | Three-way branch stated in 2.1 | `main-session` | `resolved` |
| C6 three items dropped by both plans | medium-high | Written into plan-069; Issue 3.3 + SC12 verify before 3.2 publishes | `main-session` | `resolved` |
| C7 R1 count wrong again | medium | 23 everywhere, measured from tooling; SC8 re-pointed; SC8b added | `main-session` | `resolved` |
| C8 SC2 clause unspecified | medium | Clause added to 0.3; 1.4 edge re-pointed | `main-session` | `resolved` |
| C9 cross-plan coupling | medium | 2.5 uses an explicit allow-list; recorded in plan-069 | `main-session` | `resolved` |
| C10 plan-069 upstream table empty | low-medium | Seeded with five rows | `main-session` | `resolved` |
| C11 Gate 2 not ONE-SHOT | low-medium | Marked, with reason | `main-session` | `resolved` |
| C12 2.3 necessity unestablished | low | Restated as defence-in-depth; SC5 strengthened to fail under 2.1-only | `main-session` | `resolved` |
| C13 three smaller drops | low | (d) in rejected table; L4 diagnostic to plan-069; filename drift into 2.1 | `main-session` | `resolved` |
| C14 Gate 1 silent on missing path | low | `MISSING:` echoed to stderr | `main-session` | `resolved` |

**Final status: all concerns resolved.** Re-verified after the rewrite — 5 epics, **23 issues**,
5 gates, **16 criteria**, 9 risks, zero `unparsed`, zero dangling edges, zero cycles, zero
undischarged issues, longest chain 6 nodes.
