# Upstream #36: bdplan audit --json-output emits invalid JSON on control chars in findings

- **Number:** 36
- **Title:** bdplan audit --json-output emits invalid JSON on control chars in findings
- **URL:** 
- **State:** OPEN
- **Labels:** bug, priority::medium

## Body

Migrated from local bead `beads-skills-3ma` (kept upstream until pulled via a plan).

`plan_manager.py audit --json-output` produced JSON with a raw control character (tab/newline) inside a finding string, breaking `json.load` (`Invalid control character at line 20`). Observed during plan-011 intake; the human-readable `audit` worked.

**Fix:** JSON-escape finding/report strings (control chars) in the `--json-output` path.

**Location:** the bdplan skill (`~/.claude/skills/bdplan/scripts/plan_manager.py`), not this repo's code.
