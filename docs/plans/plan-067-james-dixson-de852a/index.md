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
