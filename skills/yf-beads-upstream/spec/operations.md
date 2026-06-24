# Spec: Operations

The operations beads-upstream owns (init, push, status/pull, and the land-the-plane
hoist/un-hoist reconcile path). Source of truth for the skill's behavioral contract.

## Requirements

- **REQ-OP-001:** `init` detects the git remote, proposes a backend (`github` from `github.com`,
  `gitlab` from `gitlab.*`, else `none`), confirms via `AskUserQuestion`, and writes config with
  `bd config set`. — *Rationale:* one consent-gated setup path. — *Verify:* SKILL.md "/beads-upstream init" §; `bd config set --help`.

- **REQ-OP-002:** `init` writes no rule file into the target project; the trigger contract ships
  only as the skill's installed companion rule. — *Rationale:* the rule is installer-managed, not
  init-managed (Surface Convention). — *Verify:* SKILL.md init §; absence of any rule-write in init steps.

- **REQ-OP-003:** Selecting backend `none` writes an explicit opted-out marker
  (`custom.upstream.enabled=false`, `custom.upstream.backend=none`), not merely leaving config unset;
  re-running `init` can re-enable. — *Rationale:* opted-out ≠ unconfigured; distinguishes "off on
  purpose" from "never set up." — *Verify:* SKILL.md init step 3.

- **REQ-OP-004:** The push step short-circuits to a clean exit 0 (no enumeration, prompt, or upstream
  call) when tracking is disabled. — *Rationale:* opted-out projects are never nagged. — *Verify:*
  SKILL.md push step 0; protocols/UPSTREAM_TRACKING.md no-op clause.

- **REQ-OP-005:** The push step pushes only **open + deferred** work (open, blocked, deferred);
  never closed beads; epics/molecules/gates excluded as non-work. — *Rationale:* only unfinished work
  belongs upstream. — *Verify:* `upstream.py` `CANDIDATE_STATUSES` + type filter; SKILL.md push intro.

- **REQ-OP-006:** The push step verifies the auth token resolves before any push and fails fast on
  empty/expired. — *Rationale:* fail before side effects, not during. — *Verify:* SKILL.md push step 1.

- **REQ-OP-007:** On partial push failure the step re-enumerates `External:` mappings and reports
  pushed-vs-remaining; it never swallows the error. — *Rationale:* recoverable, auditable failure.
  — *Verify:* SKILL.md push step 4; `upstream.py mappings`.

- **REQ-OP-008:** Status/pull treats the upstream tracker as the authoritative worklist when enabled,
  and falls back to local `bd ready` / `bd list` when disabled. — *Rationale:* the local bead set may
  be stale relative to upstream. — *Verify:* SKILL.md "Status / pull" §.

- **REQ-OP-009:** Updating an already-mapped bead's upstream issue body is done by folding the new
  content into the bead's **`description`** and re-pushing — bd's GitHub sync maps `description` →
  issue body only; `notes`/`design` are not synced. The re-push dry-run must read `Would update`
  (not `Would create`), and the open-issue count must stay constant. — *Rationale:* `--notes` edits
  silently never reach upstream; `bd update --description` replaces (never appends) and `bd show
  --json` is a list, so a naive read-modify-write can clobber the description. — *Verify:* SKILL.md
  push step §6; Safety invariants "Only `description` syncs upstream".

## Granularity & auto-hoist config

- **REQ-OP-010:** `custom.upstream.granularity` (`coarse` | `granular`, default `coarse`) controls
  hoist issue-count: `coarse` files one tracking issue per plan-scale effort, `granular` one per
  hoisted bead. Read inspects the config text for `(not set)` — never the exit code. `coarse` is
  the tested happy path; `granular` is implemented but not the tested-happy-path. The two coexist:
  flipping to `granular` leaves existing coarse trackers intact via the `External:` create-or-map
  dedup. — *Rationale:* hoist count must be operator-policy, not hard-coded. — *Verify:*
  `upstream.py` `granularity` / `hoist_issue_count`; SKILL.md init §; README.

- **REQ-OP-011:** `custom.upstream.auto_hoist_followons` (default-deny: enabled only on literal
  `true`) gates the unattended no-prompt land-the-plane hoist. Disabled → propose-with-confirm
  only. — *Rationale:* removing a local bead without a prompt is opt-in, mirroring
  `custom.upstream.enabled`. — *Verify:* `upstream.py` `auto_hoist_followons`; SKILL.md init §.

## Hoist / land-the-plane / un-hoist

- **REQ-OP-012:** The `hoist` operation ensures an upstream issue per granularity (create-or-map
  via `External:`), **dry-runs the push first**, then removes the bead locally with
  `bd close -r "<destination>"` — a reversible tombstone, never `bd delete`. Scoped `--issues`,
  inline auth. — *Rationale:* local DB = active work only; removal must be reversible and
  auditable. — *Verify:* `upstream.py` `plan_hoist` / `cmd_hoist`; SKILL.md push step §7.

- **REQ-OP-013:** Follow-on detection separates a **narrow** signal (`discovered-from` into the
  plan subtree **AND** non-active — auto-eligible) from a **broad** signal (created-after-intake
  under the subtree — gated-proposal-only). — *Rationale:* the broad signal can catch a bead still
  being worked, so it is never auto-hoisted. — *Verify:* `upstream.py` `detect_followons`.

- **REQ-OP-014:** Land-the-plane (`land`) defaults to propose-with-confirm (emit the whole
  detected batch, require `--apply`). The no-prompt path runs only under
  `auto_hoist_followons=true` and is restricted to the narrow set; the broad set stays gated.
  Non-follow-on reconcile is always gated. — *Rationale:* matches the confirm-required push
  contract; an in-progress bead is never auto-removed. — *Verify:* `upstream.py` `plan_land_hoist`
  / `cmd_land`; SKILL.md push step §7.

- **REQ-OP-015:** A wrongly-hoisted bead is restored via `un-hoist`: `bd update <id> --status open`
  reopens it from its `close_reason` tombstone (the upstream issue stays); a `--record` file
  supports batch round-trip. — *Rationale:* one-command rollback for a mis-hoist. — *Verify:*
  `upstream.py` `plan_unhoist` / `cmd_unhoist`; SKILL.md "un-hoist".
