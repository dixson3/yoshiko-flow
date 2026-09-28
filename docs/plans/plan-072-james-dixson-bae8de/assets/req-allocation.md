---
type: Asset
okf_spec: OKF-PLAN
description: "Issue 0.2 REQ id allocation: the four plan-072 ids verified free and where each is homed"
---
# REQ allocation — plan-072

Issue 0.2. Verified free on 2026-09-25 by `grep -rln` for each id across `*.md`/`*.py`
(excluding this plan folder): zero hits. Highest existing ids at allocation time:
`REQ-YF-EMBED-006` (SPEC.md), `REQ-SKAUTH-060` (skills/yf-skill-authoring/SPEC.md),
`REQ-ENGINE-010` (skills/yf-change-validation/spec/engine.md).

| Id | Home | Subject |
| :-- | :-- | :-- |
| `REQ-YF-EMBED-007` | `SPEC.md` §3.2 | Agent Skills `name`/`description` field rules, enforced by `scripts/check_frontmatter.py` |
| `REQ-SKAUTH-061` | `skills/yf-skill-authoring/SPEC.md` | Four-state description rating (crisp / satisfactory / unrouted / loose) |
| `REQ-SKAUTH-062` | `skills/yf-skill-authoring/SPEC.md` | Trigger-eval contract (`scripts/checks/skill_trigger_eval.py`) |
| `REQ-ENGINE-011` | `skills/yf-change-validation/spec/engine.md` | Per-row opt-in `flags` column (`inconclusive-exit=4`, `stream`) |

Also amended: `REQ-SCHEMA-002` (`skills/yf-change-validation/spec/schema.md`), for the fifth §1 column.
