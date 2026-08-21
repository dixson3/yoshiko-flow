---
type: Reference
okf_spec: OKF-PLAN
id: tracker-050-draft
description: Draft of plan-050's coarse upstream tracking issue (Issue 6.3)
---

# Draft: plan-050's coarse tracker

**Title** (verbatim — the id already begins with `plan-`, so no `plan-` prefix is added;
plan-048 shipped `plan-plan-048-…` from the old template):

```
plan-050-james-dixson-d0414b execution tracking
```

**Body:**

> Coarse tracking issue for `plan-050-james-dixson-d0414b` — one issue per plan-scale effort,
> per this repo's Upstream Tracking convention.
>
> **Plan folder:** [`docs/plans/plan-050-james-dixson-d0414b/`](../../../docs/plans/plan-050-james-dixson-d0414b/)
> **Epic:** `yf-mol-m3e`
> **Landed on `main`:** `cacb834` (bundle) · `849003e` (the six fixes)
>
> ## Objective
>
> Fix the six mechanical process defects that plans 047, 048 and 049 each hit and each worked
> around by hand. Every fix ships with a control that was **observed RED before the fix
> landed**.
>
> | Issue | Requirement | What shipped |
> | :-- | :-- | :-- |
> | #178 | `REQ-CLI-025` | `plan_manager.py grant` — one shared requirement table read by both the generator and `_verify_row` |
> | #179 | `REQ-PLAN-077` | `resolve-start-gate` — the gate resolve and the wrapper close are one step, with a generated reason |
> | #180 | `REQ-COMPLETE-004` | gate-before-close asserted with an exit code, **and** `SKILL.md` §6.4 reads it |
> | #181 | `REQ-DATA-061` | a preflight `classify` mode, and the `DOC-LINT.md` on-edit rule rewritten to call it |
> | #186 | `REQ-DATA-062` | titles captured verbatim by offset-slicing the unmasked line |
> | #187 | `REQ-DATA-063` | the issue `detail` field, sub-key bullets excluded |
>
> Plus one amendment to `REQ-DATA-024`, scoped to its exit-contract sentence, carried to its
> three restatements outside the spec.
>
> ## Scope moves, both recorded rather than absorbed
>
> - **D-9** — Epics 4 and 5 (M9/#149, #182, #184) were **split out to plan-051** at review
>   cycle 5, on measured evidence: concerns per pass ran 5 → 4 → 11 → 17 → 14, and every high
>   concern for three consecutive rounds landed on those two epics.
> - **D-10** — #186 and #187 were **pulled in** after review cycle 9 as Epic 7. The epic
>   numbering is gapped and out of order (0–3, 7, then 6) **deliberately**: renumbering is this
>   corpus's top recurring defect class.
> - **D-6** — #177 was scoped in and then **dropped on evidence**; the refutation is commented
>   upstream instead.
>
> ## Result
>
> 28 issues, 41 edges, 3 gates, 22 success criteria. `validate-merged` over the merged tree:
> engine `change-validation`, FULL tier, **45 commands, 45 pass, 0 failures**.
>
> **Three defects were caught by RUNNING the controls, none by the thirteen review cycles and
> eleven independent red-team passes that preceded them** (`RE-005`, `RE-007`, `RE-009` in the
> bundle's `plan-retrospective.md`). Direct evidence for #188 and #190.
>
> Handoff to plan-051: `references/handoff-051.md` in the plan folder.
