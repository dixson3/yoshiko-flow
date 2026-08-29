---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #56: yf-beads-init repair: embedded-mode wedged-migration fix can't clear a dirty Dolt working set

- **Number:** 56
- **Title:** yf-beads-init repair: embedded-mode wedged-migration fix can't clear a dirty Dolt working set
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/56
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

The wedged-schema-migration repair (REQ-BINIT-011 / GR-BINIT-002 / SKILL.md 'Wedged schema migration') is hardcoded to: bd dolt stop -> bd migrate schema -> bd migrate, on the premise that 'bd dolt stop flushes and clears the in-memory Dolt working set'. That premise only holds in dolt SERVER mode. For EMBEDDED-mode repos (.beads/embeddeddolt/ — the cruft-suppressed default this skill itself creates), all three steps fail and the repo cannot self-heal.

REPRO (observed in dixson3/yoshiko-flow on 2026-06-30, after a beads 1.0.0 -> 1.0.5 upgrade):
- bd status/ready/list return error JSON: 'pending schema migrations alter pre-existing dirty tables: config, events, issues' (bd ready/list also error, so the corrupted classifier is correct).
- yf doctor --repair: [FAIL] stop dolt server (flush working set); [FAIL] apply schema migrations; [FAIL] update db metadata version. 'bd dolt stop' errors: 'not supported in embedded mode (no Dolt server)'.
- Root cause: the upgrade carried a schema migration (adds wisp_* tables: wisps/wisp_events/wisp_comments/wisp_dependencies/wisp_labels) that must alter config/events/issues, but those tables had an uncommitted on-disk Dolt working set from a prior session. Dolt refuses to alter dirty tables.

FIX THAT WORKED (manual): commit the embedded working set directly via the dolt CLI, which CAN open the repo even though bd's migration gate has wedged bd:
  cd .beads/embeddeddolt/<dbname> && dolt add -A && dolt commit -m '...'
then bd migrate schema (Schema already at v49) -> bd migrate (Updating Dolt schema version 1.0.0 -> 1.0.5). Healthy after.

PROPOSED ENGINE CHANGE (yf doctor --repair + REQ-BINIT-011 + SKILL.md + protocols/BEADS_INIT.md):
1. Detect embedded vs server mode; 'bd dolt stop' is server-only and must not be the working-set-clearing mechanism in embedded mode.
2. Add a DATA-PRESERVING working-set-commit step for the embedded case BEFORE bd migrate schema: in .beads/embeddeddolt/<db>, dolt add -A && dolt commit. Commit, never dolt reset --hard — the working set can hold real issue data.
3. Update the spec/skill/rule wedged-migration sequence: the current text hardcodes the server-only order and forbids 'bd vc commit' without noting that a direct 'dolt commit' (bypassing bd's gate) is the embedded-mode escape hatch.

This is an UPGRADE ARTIFACT and will recur on the next beads schema-bump for any embedded repo whose prior session left an unflushed working set.
