---
okf_version: 0.2
---

# plan-067-james-dixson-de852a

> Diagram set redesign (#373): restack architecture as a layered marketecture with per-skill and per-formula diagrams, combine phase-model+lifecycle and install+tune, evaluate archify vs d2->png as the rendering toolchain, and amend DRIFT-CHECK so omissions FAIL

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table.
- [assets/spikes/README-plan.md](assets/spikes/README-plan.md) - Surviving executable artifacts from the plan-067 investigations. EXP-004's generator prototype was NOT recovered; this file records that honestly.
- [assets/spikes/exp001-architecture-stack.d2](assets/spikes/exp001-architecture-stack.d2)
- [assets/spikes/exp001-dagre-sample.png](assets/spikes/exp001-dagre-sample.png)
- [assets/spikes/exp001-elk-sample.png](assets/spikes/exp001-elk-sample.png)
- [findings/exp-001-archify-vs-d2.md](findings/exp-001-archify-vs-d2.md) - Keep d2. archify has no headless raster export, a non-self-contained artifact, an unvendorable dev-channel dependency, and a quality gate that penalises the very member ids the repo checks.
- [findings/exp-002-required-set-derivability.md](findings/exp-002-required-set-derivability.md) - D4 refuted as scoped. A declared required set over derivable classes newly FAILs 17-18 of 20 pages and EVERY failure is an artifact. Exactly one class has a clean signal.
- [findings/exp-003-omission-inventory.md](findings/exp-003-omission-inventory.md) - 73 real omissions (band 57-114; rejected upper bound 193). Ratio 53% real / 17% curation / 30% artifact. The required set must be corpus-wide, not per-page.
- [findings/exp-004-per-skill-diagram-model.md](findings/exp-004-per-skill-diagram-model.md) - 20 per-skill diagrams are sound only if GENERATED. Hand-authored they are 20 new drift surfaces. 8 of 20 are trivial; the wrappers relation derives at 85%.
- [references/upstream-247.md](references/upstream-247.md) - Upstream issue #247 - Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist
- [references/upstream-263.md](references/upstream-263.md) - Upstream issue #263 - META: 'two facts, one signal' is one architectural gap with 11+ instances — investigate the class before fixing another instance
- [references/upstream-317.md](references/upstream-317.md) - Upstream issue #317 - Plan 3/3: regenerate user-facing docs (the site does not currently BUILD) and separate content defects from harvest/generation-process defects
- [references/upstream-373.md](references/upstream-373.md) - Upstream issue #373 - Diagram set redesign + make DRIFT-CHECK omissions FAIL
- [references/upstream-374.md](references/upstream-374.md) - Upstream issue #374 - web/plugins/skill_pages.py: the authored-page guard is EXISTENCE-ONLY — a zero-byte page passes it and builds green
- [references/upstream-375.md](references/upstream-375.md) - Upstream issue #375 - web/content/images/lifecycle.d2: labels a preflight status `deps-missing` where the literal is `system_deps_missing`
- [references/upstream-376.md](references/upstream-376.md) - Upstream issue #376 - check_web_counts: group membership is NOT CHECKED where a bullet enumerates no member ids (declared limit)
- [reviews/pass-1.md](reviews/pass-1.md) - Red-team pass 1: REVISE, 17 concerns (7 high). D6 refuted by a six-diagram measurement; three of D1's four archify grounds refuted.
- [reviews/pass-2.md](reviews/pass-2.md) - Red-team pass 2: REVISE, 15 concerns. Two phantom resolutions, and pass-1's --min-checkers 8 floor measured UNREACHABLE — an always-passing criterion replaced by a never-passing one.
- [reviews/pass-3.md](reviews/pass-3.md) - Red-team pass 3: APPROVE. No phantoms — all 15 pass-2 resolutions verified in the file bytes. Seven concerns, none high, none blocking.

## Findings

| File | What it answers |
| :-- | :-- |
| [exp-001-archify-vs-d2.md](findings/exp-001-archify-vs-d2.md) | Keep d2 — on **two** grounds, not the four first claimed. Its dagre recommendation came from one sample and was refuted across six. |
| [exp-002-required-set-derivability.md](findings/exp-002-required-set-derivability.md) | A required set over derivable classes newly FAILs 17-18 of 20 pages, **every failure an artifact**. Only slash sub-verbs give a clean signal. |
| [exp-003-omission-inventory.md](findings/exp-003-omission-inventory.md) | **73** real omissions (band 57-114; 193 rejected). Carries an amendment retracting its own false green, itself corrected once more. |
| [exp-004-per-skill-diagram-model.md](findings/exp-004-per-skill-diagram-model.md) | Generate, do not hand-author: 20 authored diagrams would be 20 new drift surfaces. Found a live false claim on the published site. |

## Reviews

| File | Verdict |
| :-- | :-- |
| [pass-1.md](reviews/pass-1.md) | REVISE — 17 concerns. Refuted D6 by measurement and three of D1's four archify grounds. |
| [pass-2.md](reviews/pass-2.md) | REVISE — 15 concerns, including two phantom resolutions and an unreachable vacuity floor. |

## Upstream references

`references/upstream-{373,376,375,374,317,247,263}.md` — full issue bodies as fetched at triage.
Dispositions live in [upstream-triage.md](upstream-triage.md) and are restated in `plan.md`'s
Upstream Issues table.

## Spikes

[assets/spikes/](assets/spikes/) — the surviving executable artifacts, and an explicit record of
**what was lost**: EXP-004's generator prototype, EXP-001's archify spec, and EXP-003's slash-verb
extractor did not survive their sub-agent scratch. The dagre render is kept deliberately as a
**negative artifact** — it is the single sample that produced a refuted decision.
