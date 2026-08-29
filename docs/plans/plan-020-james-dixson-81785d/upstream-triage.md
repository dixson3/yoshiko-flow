---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: Fix yf-beads-init embedded-mode wedged-migration repair

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #56 — yf-beads-init repair: embedded-mode wedged-migration fix can't clear a dirty Dolt working set
Labels: type::bug, priority::high
> The wedged-schema-migration repair (REQ-BINIT-011 / GR-BINIT-002 / SKILL.md 'Wedged schema migration') is hardcoded to: bd dolt stop -> bd migrate schema -> bd migrate, on the premise that 'bd dolt st...

**Disposition:**
**Notes:**
