---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #397 - plan-071-james-dixson-d19ce8 execution tracking'
---
# Upstream #397: plan-071-james-dixson-d19ce8 execution tracking

- **Number:** 397
- **Title:** plan-071-james-dixson-d19ce8 execution tracking
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/397
- **State:** OPEN
- **Labels:** (none)
- **Disposition:** tracker (the coarse tracking issue this plan filed at intake)

## Body

Coarse tracking issue for **plan-071-james-dixson-d19ce8** (AGENTS.md convention: one issue per plan-scale effort).

**Plan:** `docs/plans/plan-071-james-dixson-d19ce8/` on `main` (intake merge `80a109c`; fingerprint `d623f106…`).

**Objective.** Freeze yf-plan mechanism growth and convert the review loop from reading to executing, with an approval-to-landing fidelity metric and subtraction of declared-but-unenforced layers.

**Why.** A retrospective over plans 050–070 found one defect class ("vacuous / silent green / declared-not-enforced") renamed at least six times, near-zero recall by reading passes and near-total recall by execution, and `plan_manager.py` growing 3.4x in 30 days while the defect rate stayed flat. Every landing since plan-062 halted or crashed while landing itself.

**Shape.**
- Epic 0 — SPEC-first: `REQ-AGENT-066` (execution-pass contract), `REQ-PLAN-084` (fidelity metric), `REQ-PLAN-085` (ready-check smoke-run; INCONCLUSIVE halts), `REQ-PLAN-086` (freeze + retention standard); `spec/landing.md` 39 → 22 ids.
- Epic 1 — the metric: `retrospective-append --kind fidelity`, `retrospective-report --fidelity`, baseline over 060–070.
- Epic 2 — review executes: red-team passes 1–2 read, pass ≥3 runs checkers + criteria; `ready-check` smoke-runs every criterion and runs `gate_consistency.py`; unpoured `plan-review` / `verify-artifact` formulas deleted.
- Epic 3 — REQ-LAND prune, code side (after plan-070 lands; gated).
- Epic 4 — manager prune: 6 dead verbs, `audit-close`, `_land_l5_advisory_recheck`, unwired `scripts/checks/*`, one source for the close chain, and `scripts/checks/check-provably-necessary.py` (the freeze's teeth, five negative controls).
- Epic 5 — lands under its own rule.

**Upstream dispositions.** include: #323 #338 #384 #286 #364 #325 #390 · partial: #392 #356 #358 #306 · exclude: #289 #328 #312 #395.

**Ordering constraint.** A `probe` gate requires plan-070 (#386's successor) to be `complete` on `main` before the `spec/landing.md` rewrite (Issues 0.4, 3.2).

**Review record.** 2 reading passes (19 concerns) + 2 execution passes (5 measured concerns, then APPROVE). The first execution pass found a criterion that could never go green (ugrep binary-match lines from `__pycache__`) that both reading passes had accepted.

Execute with `/yf-plan execute plan-071-james-dixson-d19ce8` in a new session.

