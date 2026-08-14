---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #98: plan-034 execution tracking: post-plan-033 follow-ups (drift axis + codex budget + web docs)

- **Number:** 98
- **Title:** plan-034 execution tracking: post-plan-033 follow-ups (drift axis + codex budget + web docs)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Coarse tracking issue for **plan-034-james-dixson-ac6633** (one issue per plan, per the project convention).

Post-plan-033 follow-ups, four epics:
1. **Per-harness settings-drift axis** (`yf-252c`) — register `yf doctor` `SettingsDriftCheck` for codex/opencode (config drift) + new per-harness managed-block drift vs the minimized bundle (codex/opencode/pi), read-only. REQ-YF-TUNE-026.
2. **Codex block-size-budget check** (`yf-297v`, plan-033 R8/F7) — warn (never truncate) when the global `~/.codex/AGENTS.md` + managed block nears the effective on-disk `project_doc_max_bytes` (32768 default). REQ-YF-TUNE-027.
3. **web/ docs buildout** — workflow glossary (`yf-3d13`), beads & `yf-beads-*` concepts (`yf-rd33`), yf-plan/yf-research subagent+workflow docs (`yf-7ntv`), managed-files reference reconciled with `harness-tune.md` (`yf-pxet`).

SPEC-first (Epic 1 lands REQ-YF-TUNE-026/027). No capability/reconcile gate. Human start gate only.

Plan folder: `docs/plans/plan-034-james-dixson-ac6633/`. Predecessor: plan-033 (#96). Related deferral hoisted separately: #97 (multi-environment reconciliation).

_Filed at intake; awaiting `/yf-plan execute` in a new session._
