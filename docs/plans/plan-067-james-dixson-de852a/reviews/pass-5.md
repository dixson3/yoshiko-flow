---
type: Review
okf_spec: OKF-PLAN
description: "Red-team pass 5 (final cycle): APPROVE, 6 concerns, none high. A spike empirically verified Issue 7.2's group-detection fix; three landed criteria were FALSE with no issue owning them."
id: pass-5
plan: plan-067-james-dixson-de852a
created: 2026-09-07
verdict: APPROVE
---
# Red-team pass 5 — plan-067-james-dixson-de852a (amendment re-approval, final cycle)

## Verdict: APPROVE

6 concerns (0 high, 3 medium, 2 low-medium, 1 low). **No concern requires an operator decision** —
every one is a mechanical edit.

## Mechanical gates

`audit` all passed · `ready-check` NOT READY *solely because pass-4's verdict is REVISE* — this
APPROVE clears it · `plan_extract --strict` exit 0, `unparsed: []`, **8 epics / 54 issues / 75 edges
/ 6 gates / 40 criteria** · `doc_lint` **PASS, 0 E, 5 W** · `gate_consistency` **PASS, 6 gates** ·
REQ-PORT-006 **4 ≡ 4** · DAG **0 self-edges / 0 dangling / 0 cycles** · uncovered list **matches the
extractor exactly**.

`recheck-criteria`: 40 total, 3 manual (all parse), **10 FALSE — seven expected and owned** (SC5,
SC27b, SC28-SC32 are what Issue 7.0 restores; SC26b is the declared handoff). **Three were not
owned** — C1, C2, C4 below.

## Phantom check — 10 of 11 pass-4 resolutions clean

Every claim verified against file bytes. **The self-reported first-attempt phantom is closed**:
`6.4 deps: ['6.1', '7.8']` and `7.1 deps: ['7.0b', '6.1']` are both in the extracted DAG.

The divergence list in D8 was **independently confirmed accurate** by reading
`architecture-reference.png`: wildcards, 13 boxes, `bash` present, `d2`/`git` absent, the
`yf-beads-hygeine` typo — all five hold.

## Spike — does Issue 7.2's fix actually work?

Built the restyle in a scratch copy: stripped the four group sublabels to bare names, deleted every
edge.

```
edges 42 -> 0 ;  count-bearing group labels -> []      (GROUP_RE confirmed dead)
count-free container-id + tiled-child-box extractor:
    groups_checked=4, equal_to_census=True
delete one member box (yf-okf-hygiene):
    groups_checked=4, equal_to_census=False, diffs={'utility': ['yf-okf-hygiene']}   <- CAUGHT
```

**Issue 7.2 as written is sufficient and SC29's positive assertion binds.** The favourable
structural fact: `architecture.d2` already carries `skills.{beads,markdown,utility,workflows}`
containers with one explicit child box per member, so the extraction surface survives the restyle.
**The largest open risk closes.**

## Strengths

- **The split (7.0b) is coherent and does not create a third unmaintained artifact** — the deps
  diagram relocates content that already existed, derived from the same frontmatter, so the two
  cannot disagree about the skill set without SC28/SC29/SC27c firing.
- **D8's inverted precedence is doing real work** — read literally, the reference would mandate a
  glob, a six-skill omission and a typo.
- **Epic 7 is executable by a coordinator**: 10 issues, rooted at 7.0, clean bijection to
  SC27b-SC33, zero cycles.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | medium | **SC4 regressed, and pass-4's own fix caused it.** `check_amendment_log` FAILs: `['7.0', '7.0b']` have no `depends-on` path to a REQ-naming Epic-0 issue, because 7.0 was added as a dependency-free root. SC4 was green at pass 4; its discharger (0.5) is closed and nothing restores it, so Issue 7.7's full `recheck-criteria` would hard-block close. **Pass-4 C4's exact defect class, reintroduced by C4's own remedy.** | `depends-on: 0.5` on Issue 7.0. Not 0.6 — 0.6 names no `REQ-*`. |
| C2 | medium | **SC27c passes RIGHT NOW, satisfied by the artifact it exists to replace.** SC19 and SC27c share the verb `architecture-complete`, whose implementation hardcodes `architecture.d2`. SC19's *prose* was retargeted; the *instrument* was not. So SC27c is green with `architecture-deps.d2` nonexistent, and would stay green if it were never created — flipping FALSE only at 7.1, by accident, three issues late. | Retarget `sc_architecture_complete` in 7.0b's change-set and **assert the file exists** — absent must be INCONCLUSIVE, not a silent empty-string pass. |
| C3 | medium | **Issue 7.1's band list contradicts SC29's container requirement.** The reference has **no group containers at all** and merges markdown with utility; 7.1's bands merge them too and give `yf-incubator` its own band — but it is `skill-group: workflows`. SC29 requires four locatable containers equal to the census. An executor obeying "images normative for LAYOUT" could satisfy SC28 and D8 and make SC29 **unsatisfiable**. | State that the four `skill-group` containers are preserved with their ids and full membership: bands are *visual*, containers are *structural*. |
| C4 | low-medium | **Pass-4 C10 is half-resolved; `index-complete` still FALSE** — `index.md` omits `reviews/pass-4.md`, and this pass adds a fifth. The Style reference section landed; the thing the criterion was failing on did not. | Add the missing reviews and give Issue 7.8 an explicit clause to refresh the list — it is the last issue to write bundle artifacts. |
| C5 | low-medium | **The style-reference README still carries the precedence D8 inverted** — "where the two disagree **the images win**", the clause pass-4 struck. D8 and `index.md` say layout-only; the asset README, which is what an executor is pointed at as "the spec", says the opposite. A cold executor reading in file order hits the wrong authority first. | Mirror D8's split and carry the same divergence list. Three files state this rule; they must state it identically. |
| C6 | low | Stale counts: "the **eight** 7.x issues … SC28-SC33" (there are **ten**, covered by SC27b-SC33); the checker docstring still says two `manual:` criteria; Issue 1.1b declares `depends-on: 0.5` twice. | Fix the counts; fold the docstring into 7.0, which already edits that file. |

## Missing

Nothing new. Pass-4's three items are addressed or correctly out of scope: the Epic 7 bead pour is
the amendment flow's job; the restyle's information cost is now *answered* by 7.0b (the 42 edges
relocate rather than vanish); and the aesthetic axis is covered by D8's layout-normative clause.

## Gate Assessment

`gate_consistency` **PASS, 6 gates**. **Pass-4's placement objection is closed** — `6.4 depends-on
7.8` is in the extracted DAG, so the Diagram-human-read gate can no longer be handed the rejected
set by an ordering slip; operator vigilance became a DAG invariant. No frontloading miss: both open
human gates sit at the latest point their evidence permits, correct for gates whose evidence is the
deliverable itself.

## Upstream Assessment

Sound on the point pass-4 flagged. **#373's hand-named workflows→utility relation is preserved by
the 7.0b split**, so 6.5's `resolves-upstream: #373 (include)` is earned again. **#376's closure is
no longer at risk** — the evasion route is the `GROUP_RE` count dependency, 7.2 closes it at the
detection layer, and the spike confirms the closed form catches a deleted member box, so closing
#376 on the restyled tree would be a **true** close.

## Why APPROVE on the final cycle

Five cycles, 50 prior concerns, and the design questions are settled: the split is coherent, the
group-detection fix is **empirically verified**, the precedence inversion is correct and its
divergence list accurate, and the gate ordering is a DAG invariant. The six concerns are three
one-line plan edits, one README paragraph, one `index.md` list and two stale numbers. Escalating
them would spend an operator decision on edits that need none.

## Resolutions

All 6 resolved by the main session. **None required an operator decision** — the reviewer's judgement
on that was correct.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | medium | **Fixed, and verified by reading the check back rather than trusting the edit.** `depends-on: 0.5` added to Issue 7.0; `check_amendment_log` now reports *"all 44 non-exempt implementation issues reach a REQ-naming Epic-0 issue"*, exit 0. The reviewer is right that this was pass-4 C4's own remedy creating pass-4 C4's defect — the third time in this plan pair a fix has broken a landed green criterion. | `main-session` | `resolved` |
| C2 | medium | **Fixed.** Issue 7.0b now requires retargeting `sc_architecture_complete` to `architecture-deps.d2` **in the same change-set**, and asserting the file exists so an absent file is INCONCLUSIVE rather than a silent empty-string pass. A criterion that passes because its subject does not exist is the vacuity class this plan spent three cycles closing elsewhere. | `main-session` | `resolved` |
| C3 | medium | **Fixed.** Issue 7.1 now states that the four `skill-group` d2 containers are preserved with their existing ids and full census membership — bands *visual*, containers *structural*, `yf-incubator` inside `workflows` wherever it is drawn. This is the one place an executing agent could have built an artifact satisfying D8 while making SC29 unsatisfiable. | `main-session` | `resolved` |
| C4 | low-medium | **Fixed and verified.** `index.md` gained pass-3, pass-4 and pass-5 with one-line verdicts; `index-complete` now reports *"lists all 36 bundle artifact(s)"*, exit 0. Issue 7.8 owns keeping it green, being the last issue to write bundle artifacts. | `main-session` | `resolved` |
| C5 | low-medium | **Fixed.** The asset README now carries the layout/content split and the full divergence table, and states explicitly that three files hold this rule and must state it identically. The reviewer's point is the sharp one: an executor is pointed at that file as "the spec", so it was the *worst* place for the struck clause to survive. | `main-session` | `resolved` |
| C6 | low | **Fixed.** "eight … SC28-SC33" → "ten … SC27b-SC33"; the checker docstring now says three `manual:` criteria; Issue 1.1b's duplicated `depends-on: 0.5` bullet removed. | `main-session` | `resolved` |
