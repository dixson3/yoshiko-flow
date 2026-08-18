---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #118: yf-plan README.md stale: still lists README.md as plan-folder orientation file (pre-OKF), contradicts index.md/log.md in SPEC REQ-PLAN-010 + SKILL.md

- **Number:** 118
- **Title:** yf-plan README.md stale: still lists README.md as plan-folder orientation file (pre-OKF), contradicts index.md/log.md in SPEC REQ-PLAN-010 + SKILL.md
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium

## Body

Surfaced by plan-036 e-skill-page-readme drift check as a CONFLICT: skills/yf-plan/README.md lines ~97,144 describe 'README.md — orientation (file map, reading order)' but the OKF migration reserved index.md (bundle listing) + log.md (phase history) 'replacing the legacy README.md' per skills/yf-plan/SPEC.md:38-39 (REQ-PLAN-010) and skills/yf-plan/SKILL.md:245. The authored web page web/content/skills/yf-plan.md is correct; skills/yf-plan/README.md is the stale party. Out of scope for plan-036 (which does not edit skill READMEs). Fix: update skills/yf-plan/README.md plan-folder file-set description to index.md/log.md.
