---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #153: Wire PYTHONPYCACHEPREFIX out of skills/ to zero the build.rs churn tax

- **Number:** 153
- **Title:** Wire PYTHONPYCACHEPREFIX out of skills/ to zero the build.rs churn tax
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::low

## Body

Follow-up from plan-041 Issue 1.5 spike (finding E6). After plan-041 lands `cargo:rerun-if-changed=<parent>/skills`, one real 'uv run pytest' cycle forces a ~5.2s full recompile because cargo walks a watched directory RECURSIVELY and rerun-if-changed has no exclude mechanism. Measured mitigation: with PYTHONPYCACHEPREFIX pointed outside the repo, pytest wrote 272 .pyc files outside skills/ and the build stayed a NOOP with full addition coverage retained. Wiring it into the repo's uv/pytest invocations (CHANGE-VALIDATION.md rows and/or a repo .env) would satisfy the STRONGER arm of plan-041 SC3 instead of the documented-tax arm. NOT done in plan-041 because it changes developer-environment behavior repo-wide, outside that plan's 'no behavior changes' boundary.
