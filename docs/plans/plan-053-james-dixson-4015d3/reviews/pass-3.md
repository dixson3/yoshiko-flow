---
type: Review
okf_spec: OKF-PLAN
id: pass-3
description: Red-team pass 3 (third independent, via Agent) — REVISE, 14 concerns, 4 high; 9 of 15 reproduced, and three failures were re-broken by pass-2's own remedies
---

# Red-team pass 3

## Verdict: REVISE

## Reproduction of pass-2's 15 resolutions

| Class | Count | Concerns |
| :-- | --: | :-- |
| (a) landed and correct | **9** | C16, C19, C20, C22, C24, C25, C26, C28, C29 |
| (b) recorded but absent | 0 | — |
| (c) landed at one site, defect survives elsewhere | **5** | C15, C17, C18, C21, C27 |
| (d) itself a new defect | **1** | C23 |

**9 of 15 (60%), against pass 2's 9 of 14 (64%) — this round did slightly WORSE.** And the
shape is unchanged: every (c)-class failure is RE-002. **Three of the five were re-broken by
pass-2's own remedies** — C21's new Issue 5.0 repeats C21's defect, and C27's new Issues
1.3a/1.3b re-break pass-1 C6, which pass 2 had verified clean.

> **This is the finding of the pass, and it is about the RESOLUTION PROCESS, not the plan.**
> Two consecutive rounds of site-by-site fixes have converged on ~60%. RE-002's own remedy
> applies: *stop iterating on the fix and put a check in front of the failing component.* The
> failing component is the main session's habit of repairing a scope at the site named and not
> sweeping for the same property elsewhere. See the resolution note below.

## Mechanical suite (re-run independently)

`plan_extract --strict` exit 0, `unparsed: []`, 8/46/60/4/26 · `doc_lint` PASS, 0 E, 3 W ·
`audit` exit 0 · `gate_consistency` PASS · `ready-check` correctly reports "last verdict
REVISE" · anchored control derivation returns **11**, matching the 11 controls named, no
collisions.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C30 | **high** | **`verify-all` certifies an exit-2 INCONCLUSIVE as a RED — proven by spike.** A fixture exiting 2 → `record-red` prints `RED observed`, returns 0, writes `rc=2`; `assert-distinguishes` says `DISTINGUISHED`; `verify-all` returns **0**. C15's fix was specified only for `verify-red-all`, and 1.1(b) offers two branches **as equals** — the `want=red` branch leaves `verify-all`, which is SC2's own command, still accepting rc=2. Pass 2's own C17 lesson ("one branch, chosen, not two offered as equals") was applied to 5.4 and not here |
| C31 | **high** | **7.1 is not downstream of 1.3a and 1.3b** — the two issues pass 2 *added*. 7.1's text asserts "names every epic leaf"; measured, the complement is exactly `{1.3a, 1.3b}` |
| C32 | **high** | **Issue 1.0 is unexecutable as written.** `.worktrees/` is empty, `assets/` is empty, the findings record no path. 1.0 says "**commit** the sandbox artifacts" — there is nothing to commit. C23 was renamed, not resolved |
| C33 | **high** | **The shipped-path check's scope excludes `skills/*/README.md`, where the same break lives** — `yf-diagram-authoring/README.md` carries more bare `uv run scripts/render.py` invocations, outside 3.7's `touches` and 3.6's globs. **The "8 rows" figure is an artifact of EXP-003's prototype scanning exactly four doc kinds.** The cleanest RE-002 instance in the plan: a scope set by a prototype's convenience and never widened |
| C34 | medium | **Issue 5.0's `touches` omits 7 files its own prose names** — `okf.py`'s four consumers and the three vendored `document_types/*.toml`. C21's defect inside C21's remedy |
| C35 | medium | **5.1's 11-file `touches` omits the 4th `web/content/**` site** — `images/phase-model.d2`, which carries `ready-for-approval`, `reconciling` and an explicit `⏸ parked` overlay node, the exact state `abandoned` is a sibling of. EXP-004's own table says ×4; the plan lists 3 |
| C36 | medium | **The findings were never corrected, though the plan says they were.** Pass-2's C17 resolution claims "the finding's claim is corrected in place" — it is not. `exp-004:24-26` still asserts the empty target set; `exp-007` still says "three lines in one file", refuted twice. The Motivation argues these bundles must be readable standalone |
| C37 | medium | **D-8 contradicts Issue 0.2** — D-8 says 12 sites in 5 files, 0.2 and SC15 say 14 in 6. The decision record justifying the choice is stale relative to the issue implementing it |
| C38 | medium | **SC16 is silently unevaluatable at §6.4.** `plan_manager.py:2731` turns a `TimeoutExpired` into `status: inconclusive` and `continue`s — never counted, never in `failed`. Default timeout **300 s**; the FULL tier is `cargo clippy --workspace --all-targets` + `cargo test --workspace` + ~25 more rows. **The plan's broadest criterion times out, records inconclusive, and completion proceeds at exit 0** — this plan's own thesis defect, in this plan |
| C39 | medium | **The RED gate blocks only 5 of 9 fix-chain heads.** Outside the Blocks closure sit **3.5, 3.6, 3.7 and 5.4** — including the entire D-3 class fix, the plan's most valuable content. Adding 3.5 and 5.4 is legal; no control is downstream of either |
| C40 | low | D-13 and R7 cite "0 of **41**"; measured now **0 of 46** — a moving-fact literal, the shape SC12b was rewritten to avoid |
| C41 | low | Issue 1.3 edits `test_epic_ref_audit.py`, a FAST-tier script, but declares no `touches`; no Epic-1 issue declares any |
| C42 | low | 3 orphan issues remain — `3.4`, `6.2`, `7.4`; the first two are substantive |
| C43 | low | `1.0 depends-on 0.1` is a declared-not-real edge — the class pass-1 C7 removed at 5.4 |

## Is the plan too large?

**"The size is earned. Do not split."** Epic 1 is a fixed harness cost amortised across six
defects — splitting pays it twice. SC1 asserts SPEC-before-impl over a *single* merge-parent
range; a split fragments the only evidence that constraint has. The 46 issues are shallow: five
of eight epics are independent 2-5-issue chains. The only clean seam, if one is ever wanted, is
**3.5-3.7 + 0.7 + 1.6** — and notably that is also the unit whose scope was measured wrong
(C33). It should be fixed, not carved off.

## Gate Assessment

**No cycle** — verified programmatically over all 60 edges. All 11 controls and both builders
outside Blocks. Two defects: the harness certifies exit-2 as RED via `verify-all` (C30), and
four fixers sit outside Blocks (C39). `gate_consistency.py` returns PASS **correctly** — its
arms cannot see either.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C30 | high | **One branch mandated, alternative deleted** — the rc check moves ahead of `_append`. 1.1(a)'s wording aligned to the gate Condition (`non-zero, non-2`). The reviewer's own pass-2 C17 lesson, applied where pass 2 failed to apply it. | `main-session` | `resolved` |
| C31 | high | 7.1's `depends-on` now includes 1.3a and 1.3b — the two issues pass 2 added and pass 2's own fix then failed to wire. | `main-session` | `resolved` |
| C32 | high | 1.0 rewritten from **commit** to **REBUILD from the findings' stated specifications**, and its unreal `depends-on: 0.1` dropped (C43). The plan-050 mutant is re-derived, not recovered. | `main-session` | `resolved` |
| C33 | high | **Accepted as the cleanest RE-002 instance.** `skills/*/README.md` added to 3.6's globs and 3.7's `touches`. Re-measurement found the break in `README.md` **and more instances in `SKILL.md` than EXP-003 reported** — so even D-5's founding figure was a prototype artifact. **The '8 rows' literal is deleted**; the control enumerates. The `yf-markdown-*/README.md` pull-in from 7.2 is recorded as deliberate. | `main-session` | `resolved` |
| C34 | medium | 5.0's `touches` widened from 2 files to 9 — `okf.py`'s four consumers and the three vendored `document_types/*.toml`. | `main-session` | `resolved` |
| C35 | medium | `web/content/images/phase-model.d2` added to 5.1's `touches`. It carries an explicit `⏸ parked` overlay node — the exact state `abandoned` is a sibling of. | `main-session` | `resolved` |
| C36 | medium | **Accepted as a false statement in my own pass-2 resolution.** The findings are now *actually* corrected: `exp-004` carries a struck-through premise with a CORRECTED block explaining that the target set was never empty and why the mechanism matters (a control built on the empty-set premise is unsatisfiable); `exp-007` carries a ⚠ header withdrawing its live-site argument and recording that its count moved three times. Both keep their conclusions and withdraw their arithmetic. | `main-session` | `resolved` |
| C37 | medium | **D-8's count literal deleted rather than corrected** — it had moved three times in three passes (3 → 12 → 14 → 15), which is #221's moving-fact shape inside a decision record. The row now names the six files; `ctl-214-id-collision` enumerates the sites. | `main-session` | `resolved` |
| C38 | medium | SC16 rewritten to assert on a **dated run record** written by 7.1, following plan-050's `assets/sc15-full-validation.md` precedent. 7.1 now writes `assets/full-tier-record.md`. Without this the plan's broadest criterion would have timed out at the 300 s default, recorded `inconclusive`, and let completion proceed at exit 0. | `main-session` | `resolved` |
| C39 | medium | Gate `Blocks` widened to `2.1, 3.1, 3.5, 4.1, 5.1, 5.4, 6.1` — 3.5 and 5.4 are legal additions (no control is downstream of either) and 3.5 is the head of the D-3 class fix, the plan's most valuable content. | `main-session` | `resolved` |
| C40 | low | The `0 of 41` literal deleted, not updated — same reason as C37. D-13 now states the property without a count. | `main-session` | `resolved` |
| C41 | low | 1.3 declares `touches: skills/yf-plan/scripts/test_epic_ref_audit.py`. | `main-session` | `resolved` |
| C42 | low | Three new criteria — **SC5b** (the pour-fidelity suite runs outside this repo, which is #210's own defect in the suite guarding #210's fix), **SC14b** (the verbatim-identity claim is removed and no description-equality check was added), and **SC20** (deploy matches HEAD). `doc_lint` now reports **zero** findings, down from 3. | `main-session` | `resolved` |
| C43 | low | 1.0's declared-not-real `depends-on: 0.1` removed, with C32. | `main-session` | `resolved` |
