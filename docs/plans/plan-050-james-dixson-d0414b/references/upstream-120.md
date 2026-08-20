---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #120: Codex project_doc_max_bytes (32 KiB) block-size-budget check for yf managed rule block (plan-033 R8/F7)

- **Number:** 120
- **Title:** Codex project_doc_max_bytes (32 KiB) block-size-budget check for yf managed rule block (plan-033 R8/F7)
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium, deferred, plan-033-followon

## Body

Codex concatenates AGENTS.md sources capped at project_doc_max_bytes (32 KiB default; plan-033 codex.json raises it to 65536). A yf managed rule block in ~/.codex/AGENTS.md competes with operator content; a large block could push docs past the cap and silently truncate. Add a block-size-budget check that warns when the deployed managed block + existing content approaches the cap.
