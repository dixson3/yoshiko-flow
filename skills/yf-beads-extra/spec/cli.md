# Spec: bd CLI contracts (1.0.5)

The version-sensitive `bd` behaviors this skill asserts. Each is verified against the
installed binary; re-verify on a `bd version` bump.

## Requirements

- **REQ-CLI-001:** `bd create -t` accepts the help-advertised normal-work enum
  `bug|feature|task|epic|chore|decision`, and additionally the built-in special types
  `gate`, `event`, `molecule`; an unknown type is rejected (`invalid issue type`).
  — *Rationale:* the help text under-reports the accepted set; documenting only the help
  enum (or wrongly dropping `molecule`) misleads. — *Verify:* `bd create --help`; isolated-DB
  probe `bd --db /tmp/x create -t {decision,gate,event,molecule}` succeeds, `-t bananafone` fails.

- **REQ-CLI-002:** `gate`, `event`, `molecule` are not ordinary work items: each has a
  dedicated creation path (`bd gate create`/formula; `--type=event` + `--event-*`;
  `bd mol pour`) and a `molecule`/resolved-`gate` bead does not surface in `bd ready`.
  — *Rationale:* listing them as plain `-t` types without their special paths invites misuse.
  — *Verify:* SKILL.md "Issue types" §; `bd gate create --help`, `bd create --help` event flags.

- **REQ-CLI-003:** Gate verbs in 1.0.5 are `add-waiter|check|create|discover|list|resolve|show`.
  There is no `bd gate approve|eval|close`. Resolve a gate with `bd gate resolve` (or `bd close`).
  — *Rationale:* the bundled plugin docs use the removed verbs. — *Verify:* `bd gate --help`.

- **REQ-CLI-004:** `bd dep` edge addition is additive (`bd dep <blocker> --blocks <blocked>` ≡
  `bd dep add <blocked> <blocker>`); `bd update` has no `--deps` flag. — *Rationale:* the old
  "`bd update --deps` replaces the list" gotcha does not apply because the flag is absent.
  — *Verify:* `bd dep --help`, `bd update --help` (no `--deps`).

- **REQ-CLI-005:** A task cannot block an epic — `bd dep add <epic> <task>` errors
  (`epics can only block other epics, not tasks`). — *Rationale:* drives the "gate entry leaves,
  not child epics" wiring pattern. — *Verify:* SKILL.md "Epic blocking rule" §.

- **REQ-CLI-006:** `bd close <id>` does not refuse when dependents remain open; close ordering
  is not enforced. — *Rationale:* callers must order closes (or audit) themselves. — *Verify:*
  SKILL.md "Closing a bead with open dependents" §.

- **REQ-CLI-007:** `bd mol pour <formula> --json` returns `new_epic_id` and `id_mapping`
  (formula-step → bead ID); a `gate` step yields two beads (`<f>.<step>` wrapper task +
  `<f>.gate-<step>` gate). — *Rationale:* downstream wiring and gate resolution target different
  keys. — *Verify:* SKILL.md "`bd mol pour` output shape" §; cross-ref beads-authoring formula gate steps.

- **REQ-CLI-008:** Bulk edge intake uses `bd batch` (one dolt transaction, atomic rollback);
  creates are not batchable (each needs its returned ID). — *Rationale:* avoids write
  amplification and partial-failure graphs. — *Verify:* `bd batch --help`; SKILL.md "Bulk intake" §.

- **REQ-CLI-009:** `bd list` (and `bd list --all`) **hides `gate`-type beads** and **truncates
  at 50 rows** by default; it is unsafe as the "which beads exist" source of truth. A graph
  audit must build the full universe from `bd list --all` **plus** `bd list --all --type gate`
  (or `bd gate list`) and resolve individual edge targets with `bd show <id>` (which sees
  gates), never by membership in a `bd list` dump. — *Rationale:* both traps caused a
  destructive false positive (11 valid live-gate edges flagged "dangling"); `yf-beads-hygiene`
  encodes the safe discipline. — *Verify:* SKILL.md "`bd list` hides gate beads AND truncates
  at 50 rows" §; isolated-DB probe: a `-t gate` bead is absent from `bd list --all`, present in
  `bd list --all --type gate` and `bd show <gate-id>`.

- **REQ-CLI-010:** `bd dep cycles` reports circular `blocks` chains; it is read-only and is the
  mandated post-mutation integrity check after any `bd dep add`/`bd dep remove`. — *Rationale:*
  a cycle silently wedges readiness (no bead in the loop ever becomes `ready`). — *Verify:*
  `bd dep cycles --help`; SKILL.md "Detecting dependency cycles" §.
