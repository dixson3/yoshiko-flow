# Spec: Metadata, coordinator & coordinate

Contracts for post-pour metadata, the dispatch loop, and the coordinate subcommand.

## Requirements

- **REQ-ORCH-001:** Agent wiring is attached **post-pour** via `bd update --metadata` with a
  JSON payload carrying `agent` (skill-relative path, loaded as `${SKILL_DIR}/${agent}`) and
  `context` (work-dir files the coordinator includes in the subagent prompt). `[steps.metadata]`
  in TOML is **not** propagated; step `description` is. — *Rationale:* formula metadata is dropped
  on pour, so it must be set afterward. — *Verify:* SKILL.md "Bead metadata" §.

- **REQ-ORCH-002:** Metadata JSON is built with `jq -nc --arg`, never shell interpolation into a
  `--metadata '{...}'` string. — *Rationale:* interpolation silently corrupts the JSON on a quote/
  brace/newline in the value. — *Verify:* SKILL.md "Bead metadata" § jq example.

- **REQ-ORCH-003:** Consumer-specific metadata keys are namespaced (`<skill>_<field>`) or
  `x_`-prefixed for cross-consumer fields. — *Rationale:* distinguishes real fields from typos.
  — *Verify:* SKILL.md "Bead metadata" § required-keys note.

- **REQ-ORCH-004:** The dispatch loop lives in `agents/coordinator.md` (self-contained), driving
  `bd ready → claim → read metadata (defensive JSON) → load agent file → read context → spawn
  subagent → close`, repeating until `bd ready` is empty. — *Rationale:* keeps SKILL.md on
  orchestration; centralizes the loop. — *Verify:* SKILL.md "Coordinator agent" §; cross-ref
  beads-extra REQ-JSON-002.

- **REQ-ORCH-005:** The `coordinate` subcommand auto-detects gates via `bd gate list --json`
  scoped to this skill's poured epics: 0 → warn/exit; 1 → auto-select+resolve+begin; N → present
  via `AskUserQuestion`. — *Rationale:* supports concurrent instances, each with its own gate.
  — *Verify:* SKILL.md "Gate auto-detection" § table.

- **REQ-ORCH-006:** Gate resolution uses `bd gate resolve <gate-id>` (or `bd close`); there is no
  `bd gate approve` in 1.0.5. — *Rationale:* matches the verified gate verbs. — *Verify:* SKILL.md
  "Resolve and begin" §; cross-ref beads-extra REQ-CLI-003.

- **REQ-ORCH-007:** All in-skill task tracking uses `bd`; never TodoWrite/markdown/inline lists.
  Discovered sub-work creates beads with `--deps discovered-from:<parent-id>`. — *Rationale:* one
  tracking system, with provenance. — *Verify:* SKILL.md "Task tracking" §.
