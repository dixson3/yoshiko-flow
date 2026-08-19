---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #125: yf-plan: optional status-enum hardening for update-status (currently free-form, no validation)

- **Number:** 125
- **Title:** yf-plan: optional status-enum hardening for update-status (currently free-form, no validation)
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::low, follow-on

## Body

Follow-on from plan-035 (5.2 honesty fix). plan_manager.py update-status is a free-form writer with no enum guard — a typo'd status writes silently; the 9-value vocabulary (scoping..complete) is doc/spec/test-enforced only, never a runtime guard. Propose optional validation hardening: reject/warn on a status outside the documented set. See docs/plans/plan-035-james-dixson-74d7ae/findings/exp-03-phase-model-accuracy.md (rec #4). Bead only — no build here.
