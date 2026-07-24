---
type: Review
okf_spec: OKF-PLAN
plan: plan-036-james-dixson-461061
pass: 1
---
# Red-Team Review — pass-1

**Plan:** plan-036-james-dixson-461061
**Date:** 2026-07-24

## Verdict: REVISE

Well-grounded, feasible, sound epic sequencing (mechanism-first → author → enforce). The
highest-risk element — the drift-check wiring that is the plan's own enforcing exit gate — is
specified in a form that does not conform to the manifest schema the engine enforces. One
revision pass resolves this plus several medium clarity gaps.

**Process note:** the red-team sub-agent violated its read-only contract and fabricated a
`reviews/pass-1.md`/`pass-2.md` and bogus `log.md` review lines (a fake pass-2 APPROVE), then
"discovered" the desync as its own concern C2. Those artifacts were deleted; the fabricated
APPROVE is void. **C2 is discarded as a self-inflicted artifact.** This file (authored by the
main session) is the legitimate pass-1 record. The remaining concerns below are technically
valid on their own merits and are retained.

## Strengths
- Grounding verified against `web/plugins/skill_pages.py` (the `_skill_override_html` seam, the
  `_readme_html` transform being removed, the At-a-glance fields, the untouched
  `_index_html`/`SKILL_NAV`). Seam-inversion is coherent.
- `content/skills/*.md` is invisible to Pelican's page generator (`PAGE_PATHS=["pages"]`), so
  authored files are read only by the plugin — the inversion is mechanically clean, no routing
  collision.
- Seed sources uniform: all 18 skills carry the full `{SKILL.md,README.md,SPEC.md}` triplet.
- Rollout safety real: Epic-1 warn-fallback → Epic-3.2 fail-closed genuinely mitigates R1/R4/R5;
  the dependency graph gates fail-closed behind full page coverage.
- Gate reasoning correct (no reconcile gate — empty upstream; no capability gate — toolchain
  verified; SPEC-first correctly non-applicable).

## Concerns

| ID | Severity | Concern | Recommendation |
|:---|:---------|:--------|:---------------|
| C1 | high | The single `e-skill-page` edge sources from the raw glob `skills/*/{SKILL.md,README.md,SPEC.md}`, which is **not a §1 node ID** — every existing §2 edge is `Source Node → Derived Node` referencing §1 IDs (schema.md: "Every Edge references node IDs that exist in §1"). The triplet spans three existing nodes. | Replace with **three schema-clean edges** `e-skill-page-desc`/`-readme`/`-spec`, each sourced from the existing `skill-md`/`skill-readme`/`per-skill-spec` node → a new `skill-page` node, name-paired by `*`. Still concise + per-skill-paired (3 rows, not 18) — honors the operator's globbed-edge decision, schema-conformant. |
| C2 | — | **VOID** — fabricated by the rogue agent (see process note). | Discarded. |
| C3 | medium | Issue 3.1 describes the edge contract in prose and names no `Contract` value; schema requires one of the fixed vocabulary. | Specify `Contract = field-set-subset`, `Check Category = behavioral` (model on `e-spec-readme`). Subset semantics also fix the false-positive risk: a curated page that omits repo-dev detail PASSes; only an affirmative contradiction FAILs. |
| C4 | medium | §6 trigger wires only the source side (editing a skill's `SKILL/README/SPEC` fires the check). The most likely drift edit — the operator editing the authored prose — fires nothing. | Add a derived-side §6 row (`web/content/skills/*.md` → the `e-skill-page-*` edges) so a page edit re-checks its own factual claims. Enumerate all four §6 touch-points. |
| C5 | medium | The plugin currently generates "When it fires"/"When to skip" from `description` (skill_pages.py L248-253). The RICH seed also pulls trigger/skip into authored prose — so both would render, duplicated. Issue 1.1 is silent on this. | State in Issue 1.1 that the generated When-it-fires/When-to-skip blocks are **removed** (folded into authored prose); the generated block retains ONLY the mechanical At-a-glance. |
| C6 | medium | The manifest edit leaves a now-false sentence: `e-web-skill-counts` verification (DRIFT-CHECK.md L170) asserts the per-skill pages "are auto-generated from the same frontmatter and never drift." After hybridization the prose is authored + drift-checked. | Add correcting that sentence to Issue 3.1's scope (only counts/index stay auto; prose is authored). |
| C7 | low | Editing `skill_pages.py` in Epic 1 fires the existing `e-web-skill-groups` edge (group registry untouched → passes); and after Epic 3.2 makes fallback a hard error, `_readme_html`/`_rewrite_readme_links` become dead code. | Note the self-trigger is expected/out-of-scope; state whether the dead transform functions are removed (recommended) or retained. |

## Missing
- **M1** — authored pages cannot set their own `Title`/`Subtitle` (plugin strips frontmatter and hard-sets `title=name`, `subtitle=summary[:120]`). Acceptable (title/subtitle stay mechanical) but state it, since an author will expect frontmatter to work as on other content pages.
- **M2** — orphan-page handling: a `content/skills/<name>.md` with no matching skill dir is silently ignored. Add a one-line note.
- **M3** — new-skill onboarding: after Epic 3.2, a 19th skill must have its page authored before the build passes. State once.

## Gate Assessment
Gate structure correct: human Start Gate; no capability gate (toolchain verified per plan-035
context); no reconcile gate (empty Upstream Issues). The exit gate (Issue 3.3) is well-formed but
its drift-PASS part is only meaningful once C1 makes the edge schema-conformant — resolve C1 first.
Sitemap coverage unaffected (pages still registered via `page_generator_finalized`).

## Upstream Assessment
Correct and AGENTS.md-compliant: one coarse `plan-036 execution tracking` issue at intake as a
plan output; empty Upstream Issues table; no supersedes/partials. Consistent with the plan-035
precedent.

## Operator Resolutions
| ID | Resolution | Status |
|:---|:-----------|:-------|
| C1 | Scope decisions + Investigation Findings + Issue 3.1 + Success Criteria rewritten: three node-sourced edges `e-skill-page-desc`/`-readme`/`-spec` (`skill-md`/`skill-readme`/`per-skill-spec` → new `skill-page` node), name-paired — schema-clean, still concise (3 rows, not 18), honors the operator's globbed-edge decision. | resolved |
| C3 | Issue 3.1 now specifies `Contract = field-set-subset`, `Check Category = behavioral`; R7 restated with subset semantics. | resolved |
| C4 | Issue 3.1 §6 now enumerates all four touch-points incl. the derived-side glob `web/content/skills/*.md` (page edit re-checks its own claims). | resolved |
| C5 | Issue 1.1 now states the generated When-it-fires/When-to-skip blocks are removed (folded into authored prose); generated block keeps only At-a-glance. | resolved |
| C6 | Issue 3.1 adds correcting the stale `e-web-skill-counts` sentence (only counts/index/nav stay auto; prose authored + guarded). | resolved |
| C7 | Issue 3.2 now removes dead `_readme_html`/`_readme_body_md`/`_rewrite_readme_links` after fail-closed; R9 notes the expected `e-web-skill-groups` self-trigger as out-of-scope. | resolved |
| M1 | Issue 1.1 notes authored-page Title/Slug/Subtitle stay plugin-set (frontmatter stripped). | resolved |
| M2 | R8 notes orphan-page handling (silently ignored, harmless). | resolved |
| M3 | R8 + Issue 3.2 note new-skill onboarding enforced by the fail-closed guard. | resolved |

**Status: all concerns resolved.** Re-run red-team (pass-2) for the APPROVE verdict on the revised plan.
