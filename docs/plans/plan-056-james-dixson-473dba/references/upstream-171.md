---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #171: yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9)

- **Number:** 171
- **Title:** yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Filed by plan-046 Issue 5.5(iv). This is the **deferred half of #140**, filed upstream so the deferral is visible to the issue tracker and not only to `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` §9a.

Recording it in the extensions doc alone would leave it invisible here — the same asymmetry that made #140's original `include` disposition dishonest.

**What was deferred.** Generating a reserved `index.md` at every level of a bundle, not just the root. #140 originally asked for exactly this; plan-046 **retargeted to the root tier** and shipped `reindex --check` / `--write` there (SPEC `REQ-OKF-011`).

**Why — measured, not argued:**

| measurement | value | consequence |
| :-- | --: | :-- |
| nested files carrying `description:` | **0 of 423** | every generated nested entry would be bare |
| subdirectories that would get a listing of no value | **74 of 142 (52%)** | over half the output is noise |
| bundles whose **root** index already carries described subdirectory entries | **16 of 19** | the information is already available one level up |

OKF v0.2 §8 says index entries *"SHOULD include the description from the linked concept's frontmatter"* — the upstream model **presumes** a `description:` this corpus does not have. Generating nested indexes now would satisfy the letter of §8 while producing 423 entries that assert nothing.

**The precondition, and why the expensive half dissolves.** Once producers stamp `description:`, nested indexes become worth generating **forward-only**: new bundles get real descriptions, old bundles keep their hand-written root index, and the **backfill question — the risky, expensive half — never has to be answered**. That is the whole reason this is a deferral with a named trigger rather than a dropped idea.

**Not to be confused with nested `log.md`, which plan-046 dropped PERMANENTLY** (D-4): every `okf.append_log` call site targets the bundle root, so no producer event is scoped below it and nothing would populate a nested log; measured 1–2 distinct commit dates per subdirectory. That one is closed, not deferred.

**Revisit when** a producer stamps `description:` on nested artifacts. Until then, generating nested indexes makes the corpus worse, not better.

Source: plan-046 (`docs/plans/plan-046-james-dixson-aabefa/`), `findings/exp-003-reindex-and-corpus-backfill.md`. Tracker: #167. Partial of #140.

