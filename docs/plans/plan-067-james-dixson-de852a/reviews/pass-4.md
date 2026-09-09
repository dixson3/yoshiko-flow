---
type: Review
okf_spec: OKF-PLAN
description: "Red-team pass 4 (amendment re-approval): REVISE, 11 concerns. The restyle silently lapses the membership guarantee through group DETECTION, and the no-edges style reverses one of #373's named asks."
id: pass-4
plan: plan-067-james-dixson-de852a
created: 2026-09-07
verdict: REVISE
---
# Red-team pass 4 — plan-067-james-dixson-de852a (amendment re-approval)

## Verdict: REVISE

11 concerns (2 high, 3 medium-high, 4 medium, 2 low). Scoped to the Epic 7 amendment; Epics 0-6
were approved at pass 3 and are not re-litigated.

## Mechanical gates

`audit` all checks passed · `ready-check` READY · `plan_extract --strict` exit 0, `unparsed: []`,
52 issues / 38 criteria · `doc_lint` PASS, 0 E · `gate_consistency` PASS, 6 gates · REQ-PORT-006
**3 ≡ 3** · DAG 0 self-edges / 0 dangling / 0 cycles · uncovered list matches the extractor
exactly, and all eight 7.x issues are covered by SC28-SC33 in a **clean bijection**.

**28 criterion verbs executed: 25 PASS**, 3 FALSE (`verbs-match` — C4; `index-complete` — C10;
`plan066-still-green` — the declared handoff). **No criterion passes vacuously.**

## Strengths

- **The amendment is honest about its own cost.** D9 states that folding into an `executing` plan
  invalidates the fingerprint; `fingerprint check` confirms `STALE-APPROVED`, so re-review is being
  **sought rather than skipped**.
- **SC33 is well-formed** and classifies as `manual`, not as a broken clause.
- **D8's diagnosis of `red-team-chain.png` is exactly right**, and correctly separates the two
  defects — crammed metadata vs. a hoistable state machine.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **The membership guarantee lapses — through a door Issue 7.2 is not watching.** 7.2 targets `group_members()`. The real gate is `GROUP_RE` at `:58`, which detects a group **only by its parenthetical count** — which D8/SC28 forbid. **Spike:** baseline `PASS, claims 19, nc 0`; restyling the four group labels → `PASS, claims 11, nc 0` — **8 of 19 claims silently vanish**. Then deleting two member boxes → **still PASS**. That is Issue 1.1's exact two-member-deletion defect, reintroduced. **SC29 cannot catch it**: `not_checked == 0` is trivially true once the claim is gone. The existing control is blind too — it mutates the census, which the `.md` totals catch regardless of the `.d2`. | Fix **detection** (count-free container id), add a d2-scoped claim floor, rewrite SC29 to assert a **positive** number, and make 7.3's control mutate the **restyled `.d2`**. |
| C2 | high | **SC28 and SC19 contradict outright.** SC19 requires every `depends-on-skill` edge literally drawn and currently PASSes; `architecture.d2` holds **41-42** edges; SC28 asserts none. After 7.1, SC19 can never pass, while SC32 asserts "all checkers exit 0". No issue amends SC19. Substantively, 7.1 reverts Issue 4.1's central deliverable — **#373 names the workflows→utility relation by hand** — and the plan nowhere records dropping a named upstream ask. | Amend SC19 in the same change-set, and either record the reversal in #373's close body or **relocate the relations to a sibling diagram** so they survive. |
| C3 | medium-high | **Epic 7 has ZERO incoming edges and 6.4 has no edge to it.** 6.4's prose says "Presents the RESTYLED set (Epic 7)" — **prose, not an edge**. The only thing stopping 6.4 handing plan-066 the rejected set is the operator personally holding a gate, which is the class of guarantee this plan refuses everywhere else. | `6.4 depends-on 7.8`; `7.1 depends-on` the artifacts it restyles. |
| C4 | medium | **Five criteria name subcommands that do not exist and no issue authors them.** `verbs-match` is FALSE **now**: 33 verbs vs 28 subcommands. The amendment broke a landed, green criterion. | Add an issue authoring the five and restoring `verbs-match`. |
| C5 | medium-high | **"Where they disagree the images win" is an abdication, and the disagreements are real.** The reference uses **wildcards** (`yf-markdown-*`, `yf-okf-*`) making 6 skills unextractable; shows **13 boxes for 20 skills**; includes `bash`; **omits `d2` and `git`**, two of SC19's eight tool tokens; and misspells `yf-beads-hygeine`. A literal transcription is itself an omission — the defect Epic 1 exists to catch. | Invert: images normative for **layout**, census normative for **content**, with an explicit divergence list. |
| C6 | medium | **The coverage loss is not confined to one checker.** `check_web_harness_paths` (44 claims) and `check_web_backend_claim` also read `images/*.d2` with only corpus-wide floors, so 7.4's sublabel-stripping can silently reduce their coverage while `.md` totals stay non-zero. | Add a per-checker **claim-count non-regression** assertion to 7.7/SC32. |
| C7 | medium | **Already-closed Epic 6 work is invalidated with nothing to repair it.** 6.0/SC26b, 6.1 and SC24 `build-and-render` all ran pre-restyle; 7.6 regenerates all 11 through a changed `to_d2()` — exactly what 5.6 tuned. 7.7 says "all checkers exit 0", but those are **criterion verbs**, not checkers. | Make 7.7/SC32 re-run the full `recheck-criteria`, naming both explicitly. |
| C8 | low-medium | **SC30 is the one new criterion below this plan's own standard** — no stated predicate, no vacuity floor, no control. A naive `\|`-detector is both over- and under-inclusive. | State the predicate, add a floor, register a control. |
| C9 | low | **The plan's highest-value process finding is unrecorded** — `plan-retrospective.md` has zero occurrences of "Epic 7", "restyle" or "rejected". SC26 was discharged before the amendment existed. | Append the rejection and fold-in as part of 7.8. |
| C10 | low | Staleness: the criteria lead-in still says "the **two** marked `manual:`" (there are three), and `index-complete` is FALSE because `index.md` omits the amendment's own new assets. | Fix both. |
| C11 | low | 7.8 and 6.4 are two presentation acts with near-identical criteria and no stated distinction — 7.8 satisfies **plan-067's** gate, 6.4 presents to **plan-066's**. | State it inline in both. |

## Missing

- **No issue pours the Epic 7 beads** into an already-poured graph. Possibly the yf-plan amendment
  flow owns this, but it is unstated and is the first thing execution hits.
- **No statement of what the restyle costs in information** — 42 edges and 13 sublabel-bearing
  nodes deleted from `architecture.d2` alone.
- **D8 says nothing about visual style beyond content** — the reference is monochrome, rounded,
  hand-drawn. If any of the objection was aesthetic, 7.1 will guess.

## Gate Assessment

`gate_consistency` **PASS, 6 gates**; reachability holds for all six. The one problem is
**placement, not reachability**: the Diagram-human-read gate blocks `6.4` only, yet Epic 7 exists
*because* that gate fired and the gate has no relationship to 7.8. Adding `6.4 depends-on 7.8`
converts operator vigilance into a DAG invariant.

## Upstream Assessment

Unchanged and sound. Two amendment-touched observations: **#373's named ask is being partially
reversed** while 6.5 still carries `resolves-upstream: #373 (include)` — the pass-1 C8 defect one
epic later; and **#376's closure is at risk**, since per C1 the restyle reopens its failure mode by
a route 1.1b's fix does not cover. Closing #376 on the restyled tree would be a false close.

## Resolutions

All 11 resolved. C2 and C5 were **operator decisions** — both were put to the operator with the
measurements, and both were re-decided on the corrected information.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Fixed, and I verified the mechanism myself.** `GROUP_RE` does require `\(\d+\)`. Issue 7.2 now fixes **detection** — count-free container id, plus a d2-scoped claim floor returning INCONCLUSIVE if a census group is not locatable. SC29 rewritten to a **positive** assertion (`groups_checked == len(census.groups)`, each set equal to the census) because `not_checked == 0` was satisfied BY the failure mode. Issue 7.3's control now mutates the **restyled `.d2`**, not the census. | `main-session` | `resolved` |
| C2 | high | **Fixed by SPLIT, on the operator's decision.** New Issue 7.0b creates `architecture-deps.d2` carrying the tool layer, the `yf` paths and all twelve `depends-on-skill` edges **including workflows→utility**; `architecture.d2` becomes the edge-free stack. SC19 retargeted to the deps diagram; new SC27c asserts the relations survive. **#373's named ask is preserved rather than silently reversed.** | `operator` | `resolved` |
| C3 | medium-high | **Fixed — and the first attempt was a phantom.** `6.4 depends-on: 6.1, 7.8` and `7.1 depends-on: 7.0b, 6.1`, both verified in the extracted DAG. The first attempt anchored on `depends-on: 6.1\n  - resolves-upstream:` — but that `resolves-upstream` belongs to **6.5** — and sat inside a conditional bare `.replace()` rather than an asserted `sub()`, so it skipped silently. Same root cause as every other phantom in this plan pair: an unasserted edit. | `main-session` | `resolved` |
| C4 | medium | **Fixed.** New Issue 7.0 authors the five subcommands and restores `verbs-match`; new SC27b asserts it. 7.0b and 7.1 depend on it, so the restyle cannot land ahead of its own instruments. | `main-session` | `resolved` |
| C5 | medium-high | **Fixed by INVERTING the precedence, on the operator's decision.** Images are normative for **layout**; the skill census is normative for **content**. D8 now carries the explicit divergence list — the wildcards, 13-vs-20, `bash`, the missing `d2`/`git`, the typo — so a cold executor cannot transcribe the sketch's gaps. Issue 7.1 states all 20 skills appear, named from frontmatter. | `operator` | `resolved` |
| C6 | medium | **Fixed.** SC29 now carries a per-checker **claim-count non-regression** across `check_web_counts`, `check_web_harness_paths` and `check_web_backend_claim`, none of which may lose `.d2` coverage to the restyle. | `main-session` | `resolved` |
| C7 | medium | **Fixed.** Issue 7.7 now re-runs the **full `recheck-criteria`** over the post-restyle tree, naming `plan066-still-green` and `build-and-render` explicitly — the reviewer was right that "all checkers exit 0" does not reach a criterion verb. | `main-session` | `resolved` |
| C8 | low-medium | **Fixed.** Issue 7.5 states the predicate (≥2 all-caps tokens joined by `\|`, `/` or `·` in one node label), carries a vacuity floor, and 7.3 registers its control. | `main-session` | `resolved` |
| C9 | low | **Fixed.** Issue 7.8 now appends the gate rejection and the Epic 7 fold-in to `plan-retrospective.md`. A second fully-green artifact set failing a human read is the plan's highest-value finding and was going unrecorded. | `main-session` | `resolved` |
| C10 | low | **Fixed.** "two" → "three" marked `manual:`; `index.md` gains a Style reference section naming both images and stating the layout-only precedence. | `main-session` | `resolved` |
| C11 | low | **Fixed.** Issue 7.8 states inline that it satisfies **plan-067's** gate while 6.4 presents to **plan-066's**, so a cold reader cannot merge them and silently drop the C3 ordering. | `main-session` | `resolved` |
