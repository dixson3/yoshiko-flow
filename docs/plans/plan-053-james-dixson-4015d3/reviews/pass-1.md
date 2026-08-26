---
type: Review
okf_spec: OKF-PLAN
id: pass-1
description: Red-team pass 1 (independent, via Agent) — REVISE, 14 concerns, 6 high
---

# Red-team pass 1

## Verdict: REVISE

**All 14 concerns resolved.** Pass 2 reproduced 9 of the 14 by execution; the other 5 are
re-opened as C15, C16, C17, C18 and C23 in `pass-2.md`.

**First independent pass.** 14 concerns: 6 high, 6 medium, 2 low. Four concerns are
**measured refutations of plan content**, including one that refutes this plan's own
`findings/exp-007`.

## Strengths

- The investigation is adversarial to its own scoping: 5 of 6 premises revised, 2 refuted
  outright, one guardrail found inoperative.
- D-12 and R4 are earned by measurement — the naive fence fix demonstrably swallows a
  plan-body fence into a bead description.
- D-7 (fix `pour_fidelity`'s exit-0 hole **before** shipping) is right and non-obvious.
- SC6b's honesty clause is the correct model and should be applied to three more criteria.
- `plan_extract` reads the plan cleanly: 8/41/47/4/24, `unparsed: []`.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | **high** | **The capability gate's Test is an unconditional deadlock.** Two defects: `--verify-all` is not a verb (`redcheck.sh` has `record-red`, `assert-distinguishes`, `verify-all`) → exit 2; and `verify-all` demands a **GREEN** `assert-distinguishes` record per control, which cannot exist before the fixes the gate blocks. plan-050's own gate blocks the **verification** issues for exactly this reason; plan-053 blocks the **fixers**. This is plan-050 pass-5 C39's class, reintroduced |
| C2 | **high** | **`verify-all`'s manifest derivation fails permanently on this plan's control names.** The pattern is anchored `ctl-[0-9]{3}-[a-z-]+` and the anchoring is documented load-bearing. `ctl-skill-script-refs`, `ctl-spec-first-order`, `ctl-status-edge-mutation` do not match. Measured: declared=5, manifest=8 → FAIL, exit 1, permanently |
| C3 | **high** | **`ctl-status-edge-mutation` has no executable to invoke.** `skills/yf-drift-check/` has **no `scripts/` directory**, and `CHANGE-VALIDATION.md`'s header states yf-drift-check is excluded as a prose/LLM trigger. The plan's *only* control proving 5.4 fixed the edge cannot be built as specified |
| C4 | **high** | **`ctl-spec-first-order` cannot be legitimately observed RED.** `1.1 depends-on 0.1`, so Epic 0 has landed by Epic-1 time and no non-spec `skills/**` commit exists. Worse, `record-red` treats **any** non-zero as RED — including **exit 2**, which `M^1..M^2` returns with no merge commit. That is R3's failure mode occurring inside the instrument built to prevent it. plan-052 solved this with a pinned negative fixture; 1.6a never mentions one |
| C5 | **high** | **D-8's live-site argument is REFUTED, and Issue 0.2 is scoped to one file.** Measured: roots = **12 live sites in 5 files**; stamp = **5 in 4**. Live cost points the OPPOSITE way from the claim. Four cited sites do not exist — `skills/yf-plan/SPEC.md` has exactly ONE `REQ-PLAN-073` line. 0.2 `touches` only `SPEC.md`, leaving 11 roots-meaning citations pointing at a retired id, and SC15 greps only `SPEC.md` so it passes anyway |
| C6 | **high** | **Issue 7.1 is not downstream of 6 issues** — `3.1, 3.2, 3.3, 3.4, 4.2, 5.2`. SC16 and the GREEN re-observation can discharge while the entire tail of the #210 fix is open. A validation issue that does not depend on the work it validates is the shape this plan exists to close |
| C7 | medium | **R2's "accepted ordering" rests on a false premise.** Every site 5.4 would add exists today; nothing in its scope-widening depends on `abandoned`. The `depends-on: 5.1` is a declared edge, not a real one. Inverting is free |
| C8 | medium | **R7's mitigation describes plan text that does not exist.** `14.2` appears only at lines 51, 87, 300 — the Upstream table, the Findings table, and R7 itself. The Motivation cites the unrevised peak; Issue 6.1 carries no figure |
| C9 | medium | **`ctl-209-provenance` cannot assert what SC14 claims** — §5.2a is agent-executed prose. Compounding: measured on THIS plan, `plan_extract` returns **0 of 41 issues with non-empty `detail`**. plan-053's own pour produces 41 empty descriptions, and its citations live in titles — the class D-13 scopes out |
| C10 | medium | **`ctl-skill-script-refs`'s RED is an absent-instrument red** — before 3.5 the tool does not exist, so it fails because the file is missing, not because the tree is broken. R3's named pattern |
| C11 | medium | **SC12b asserts a moving whole-corpus figure** (917 files) — the #221/SC24 shape. Measured without the bundle: **913**. This plan adds findings, reviews and assets; it will be neither |
| C12 | low | `ctl-208-fail-closed` arm 2 is invariant across the fix — a **negative control**, which `redcheck.sh` defines as never appearing in `controls.txt`. The composite still goes red→green, but the record does not certify arm 2 |
| C13 | low | The three operator decisions D-5/D-6/D-7 have **no recorded question** — no `scope-answers.md`. Substance is independently corroborated by findings, but the framing cannot be audited |
| C14 | low | SC17's verification is prose, flagged `W` by `doc_lint` |

## Missing

- No control and no criterion covers **Issue 4.2** (human `resume-scan` output) — a leaf with no successor and no SC, on the surface EXP-005 called *"worse than the JSON"*.
- **Issue 5.1 has no control ancestor**; its RED-before-fix ordering rests entirely on the gate C1 shows inoperative.
- **Issue 7.4's deploy** omits `--allow-permissions-write`; the consent gate can make the command as written fail.
- **No issue owns the harness extension** C1/C2 require — 1.1 says "adopt", measurably insufficient.

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| Start Gate | fine |
| **RED observed before any fix** | **DAG-reachable, Test-unsatisfiable.** No cycle — every control sits outside the Blocks set. But the Test verb does not exist, the real verb demands post-fix GREEN, and two controls cannot produce a legitimate RED at all |
| Deploy consent | correct; human, blocks only the last issue |
| Reconcile Gate | fine, but carries no `Test` (plan-050's carried a `bd list … jq -e` probe) |

## Upstream Assessment

Dispositions reasonable; each `include` traces to concrete issues; both `partial`s specific
about in/out and cite the measurement that narrowed them. #214's `include` is **under-scoped**
— see C5.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | Issue 1.1 rewritten from *adopt* to **adopt and EXTEND**: adds a red-only `verify-red-all` verb that asserts nothing about green. Gate Test → `verify-red-all`; Condition tightened to *non-zero, **non-2***. SC2 keeps `verify-all`, discharged at 7.1. | `main-session` | `resolved` |
| C2 | high | **Controls renamed to fit the anchored pattern rather than loosening it** — `ctl-210-script-refs`, `ctl-053-spec-order`, `ctl-208-edge-scope`. Loosening would reintroduce the `ctl-187` false positive the anchoring was built against. 1.1(c) makes the confirmation explicit. | `main-session` | `resolved` |
| C3 | high | Control replaced with a **non-vacuity** assertion over `DRIFT-CHECK.md`: the §6 globs select a non-empty set AND every selected target contains a status literal — the exact property EXP-004 measured false, so the RED is behavioural. Planted-mutation dispatch kept as an honest **manual** artifact, run on a `mktemp -d` copy so an abort cannot leave a modified `skills/` file. R2 rewritten to name this limit instead of the ordering risk. | `main-session` | `resolved` |
| C4 | high | 1.6a now specifies a **pinned negative fixture** (a throwaway history with an impl commit before the SPEC commit). 1.1(b) makes `record-red` **reject exit 2 as evidence** — the deeper half of the concern, which would have let an INCONCLUSIVE masquerade as a RED for every control. | `main-session` | `resolved` |
| C5 | high | **Accepted as a refutation of this plan's own finding.** exp-007 conflated the repo-root `SPEC.md` with `skills/yf-plan/SPEC.md`. D-8 rewritten with the re-measured counts (roots 12/5 files, stamp 5/4) and now rests on the **frozen-record argument alone**, stated as a trade-off rather than one-sided. Issue 0.2's `touches` widened from 1 file to 5. SC15 rewritten to a new control `ctl-214-id-collision` (Issue 1.6c) scoped to the whole skill, since a `SPEC.md`-only grep passed while 11 stale citations survived. | `main-session` | `resolved` |
| C6 | high | 7.1's `depends-on` widened to **every epic leaf** — `1.6a, 1.6b, 1.6c, 2.3, 3.3, 3.4, 3.6, 3.7, 4.2, 4.5, 5.2, 5.3, 6.2`. The issue text now states the rule and why. | `main-session` | `resolved` |
| C7 | medium | **Premise conceded and the ordering INVERTED**: 5.4 now runs before 5.1 (`5.4 depends-on 1.6b`, `5.1 depends-on 5.4`). Every site 5.4 widens to exists today, so the old edge was declared, not real. R2 rewritten — the ordering risk is gone and the row now names the real residual limit (no runnable drift verifier). | `main-session` | `resolved` |
| C8 | medium | Motivation's #209 row now cites **14.2% across 53 bundles** alongside the 21/35 peak, and adds that plan-053's own bundle is zero-`detail`. R7 restated so its mitigation describes text that exists. | `main-session` | `resolved` |
| C9 | medium | SC14 rewritten in SC6b's honest form — asserted on the **`SKILL.md` text**, with the behavioural claim explicitly attributed to a sandbox pour that tests the fixture's own copy. **D-13 now records the self-referential measurement**: plan-053 is itself a 0-of-41 `detail` bundle, so it will hit #209 during its own execution and Epic 6 will not reach it. | `main-session` | `resolved` |
| C10 | medium | 1.6 now drives the RED against **EXP-003's existing prototype** on the plan-050 mutant — a behavioural distinction — rather than against the absence of `check_skill_script_refs.py`. | `main-session` | `resolved` |
| C11 | medium | SC12b's file-count literal **removed**. Restated as the stable invariant: errors remain 0 and no pre-existing document gains a finding. The row now names #221/SC24 as the shape it was avoiding. | `main-session` | `resolved` |
| C12 | low | Issue 1.4 now states that **only arm 1 carries the RED**; arm 2 is a negative control whose value is regression protection at 7.1, not evidence at Epic 1. | `main-session` | `resolved` |
| C13 | low | **`scope-answers.md` added**, recording all six questions with their option sets verbatim. It also records two things the reviewer could not have known: Q1's option-2 description asserted the `e-status-values` cost that EXP-004 later measured **false**, and in five of six questions the drafter's recommended option was placed first and chosen — so these are drafter proposals ratified, not independent judgements. | `main-session` | `resolved` |
| C14 | low | SC17 rewritten to the `manual:` disposition with its reason: filing is an outward-facing write whose content quality no exit code reaches. | `main-session` | `resolved` |
