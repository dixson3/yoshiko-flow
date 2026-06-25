# Upstream #37: bdresearch: optional record-epic helper for idempotent plan.yaml epic: pointer

- **Number:** 37
- **Title:** bdresearch: optional record-epic helper for idempotent plan.yaml epic: pointer
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::low

## Body

Migrated from local bead `beads-skills-phd` (kept upstream until pulled via a plan).

Robustness delta vs the bdplan worked example. The REQ-ORCH-008 durable pointer (`epic:` line in `plan.yaml`) is written by prose instruction in Phase 3, not a scripted idempotent command like bdplan's `plan_manager.py record-epic`. Functional as-is (verified), but a small helper would make it idempotent.

**Note:** `research_manager.py` is deliberately narrow (spec REQ-CLI-006: check + json-get only), so a helper would touch that spec — needs operator approval.
