---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #96: plan-033 execution tracking: yf multi-harness provisioning (harness skills + tune + rules + revert)

- **Number:** 96
- **Title:** plan-033 execution tracking: yf multi-harness provisioning (harness skills + tune + rules + revert)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Coarse tracking issue for **plan-033-james-dixson-46aca2** (one issue per plan, per the repo Upstream Tracking convention).

**Plan folder:** \`docs/plans/plan-033-james-dixson-46aca2/\` (landed on \`main\`).

**Objective.** Turn \`yf\` into a multi-harness provisioning actor, all ops under \`yf harness\`:
- \`yf harness skills install|upgrade|remove|status\` — skill bodies only, \`--harness {claude-code,codex,opencode,pi,agents}\` (naba-style descriptor table), auto-detect, dedupe. \`--tune\` flag on \`install\` bridges to tune.
- \`yf harness tune\` — (a) config alignment (settings.json / codex TOML config.toml via a delta-replay engine; \`merge.rs\` untouched) for claude-code/codex/opencode (Pi config deferred); (b) rule optimization (\`protocols/\` → minimized irreducible-core → per-harness global rules/AGENTS.md). \`--revert\` via a \`.yf/\` ownership manifest + touched-since-tune guard.
- Top-level \`yf skills <verb>\` becomes a deprecated alias until next major.
- Code-accurate \`web/\` docs + a doc↔code agreement test.

**Grounding.** research-002 (harness global-rule minimization) + naba's \`--harness\` model.

**Scope decisions.** Pi: skills-install + rule-deploy (gated on an investigation resolving \`~/.pi/agent/AGENTS.md\` vs \`APPEND_SYSTEM.md\`; no compiled-in guess), Pi config deferred. Rules move out of install into tune (bare install warns rules not deployed).

**Predecessor:** #95 (plan-032, harness settings tune — claude-code only). This plan is the follow-on.

**Closes local beads:** yf-8agh (multi-harness profiles+engines), yf-up7s (--revert). **Reconciles:** yf-8ayq, yf-ij06. **Follow-ons filed:** Pi config re-verification, Pi-rules-target (if unresolved), per-harness doctor/drift axis, codex size-budget.

**Review trail:** conformance PASS ×5; red-team pass-1 REVISE → 2/3 APPROVE (initial codex/opencode scope) → re-scoped → pass-4 REVISE → pass-5 APPROVE. SPEC-first (10 epics, Epic 1 lands all REQ revisions/additions first).

Execution runs via \`/yf-plan execute plan-033-james-dixson-46aca2\` in a new session.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
