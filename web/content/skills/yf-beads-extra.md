The routine `bd` loop — `bd ready`, `bd show`, `bd update --claim`, `bd close` — lives
in the canonical `beads` skill. `yf-beads-extra` is the layer on top of it: the parts
of the `bd` CLI that bite when you script it directly. It is not invoked; it fires when
you write or debug a script that calls `bd create`, `bd dep`, or `bd update`, when you
parse `bd … --json`, when you wire gates or dependency graphs, or when you recover a
malformed graph. If you are only running the routine loop, you do not need it.

Every gotcha here is verified against `bd` 1.0.5 and re-certified against `bd` 1.1.0.
The behaviors are structurally unchanged across those versions; where a fact is
version-sensitive it says so. Re-verify against your installed `bd version` if it is
newer.

## `bd list` is not the universe of beads

Two independent traps make `bd list` unsafe as the source of truth for which beads
exist, and both have caused a destructive false positive:

- **It hides `gate`-type beads.** Gate beads never appear in `bd list` or
  `bd list --all`. An audit that resolves edge targets by membership in a `bd list`
  dump flags every edge pointing at a gate as dangling — even though the gate exists
  and the edge is valid.
- **It truncates at 50 rows.** Molecule roots and children past the 50th row look
  missing when they are present.

The rule for any graph audit: build the full universe from `bd list --all` **plus**
`bd list --all --type gate` (or `bd gate list`), then resolve every individual edge
target with `bd show <id>`, which *does* see gates — never by presence in a list dump.
[`yf-beads-hygiene`](/skills/yf-beads-hygiene/) encodes exactly this discipline.

## `--json` is not always one JSON document

Before reaching for `--json` at all: for a status report or eyeballing state, use the
human-readable output. `bd show`, `bd list --status`, and `bd ready` already print
id, title, status, and close-reason in plain form. Going to `--json` plus an ad-hoc
`json.loads` for a report is the common self-inflicted failure.

When a script genuinely consumes specific fields, parse defensively. `bd`'s `--json`
output may carry a warning prefix on stdout, and `bd show --json` returns a **JSON
array even for a single id**. So `json.loads(stdin).get("status")` raises
`AttributeError` on the list and, if that exception is swallowed, produces a bogus
report. Never call `json.loads(stdin)` directly on `bd` output — extract the first
balanced object, or parse the top-level array once and iterate. Inside `/yf-plan`,
prefer its hardened `plan_manager.py json-get` extractor over hand-rolled `jq`.

## Dependency edges and their gotchas

- **Adding an edge is additive.** `bd dep <blocker> --blocks <blocked>` and
  `bd dep add <blocked> <blocker>` are equivalent, and neither drops existing edges.
  Set the initial set at create time with `bd create … --deps <csv>` (for example
  `--deps discovered-from:<parent>`).
- **There is no `--deps` flag on `bd update` in 1.0.5.** The old "`bd update --deps`
  silently replaces the whole list" gotcha does not apply because the flag is not
  there. Mutate edges after creation with `bd dep add`.
- **A task cannot block an epic** — only epics block epics.
  `bd dep add <epic> <task>` errors. Block the epic's children individually instead.
- **`bd close` does not refuse a bead with open dependents** in 1.0.5 — it closes
  freely. Close in dependency order if downstream beads must not be stranded.
- **Run `bd dep cycles` after any edge mutation.** A cycle silently wedges readiness —
  every bead in the loop blocks itself, so none is ever `ready`. The check is
  read-only and cheap; make it the last step of any script that mutates edges.

## Bulk intake with `bd batch`

When wiring many edges — typical at plan intake — do not call `bd dep add` once per
shell invocation. `bd batch` runs every write op in a single Dolt transaction: one
commit, rolled back on any error. That avoids write amplification and gives you
atomicity. One command per line, piped in via `printf '%b'` so the newlines are
interpreted.

Creates still need individual calls, because you must capture each new bead's ID from
its `--json` result before you can reference it in a later `--deps`. Batch the edge
wiring, not the ID-producing creates. If a create returns an empty ID, stop and
fix — silent failures cascade into broken dependency graphs.

## Issue types and gates

`bd create -t` advertises the normal-work enum (`bug | feature | task | epic | chore |
decision`) but also accepts three types that are not ordinary work items: `gate`,
`event`, and `molecule`. A `gate` or a resolved gate does not surface in `bd ready`.
Create a gate from a formula step or directly with
`bd create "Gate: <name>" -t gate --parent <epic>`, and resolve it with
`bd gate resolve <gate-id>` (or `bd close`). There is no `bd gate approve` subcommand
in 1.0.5 — the gate verbs are `add-waiter`, `check`, `create`, `discover`, `list`,
`resolve`, and `show`.

## `bd mol pour` output shape

`bd mol pour <formula> --json` returns one object with `new_epic_id` (the top-level
epic the formula created) and `id_mapping` (a dict from formula step names to bead
IDs). Capture both — without `id_mapping` you cannot wire downstream beads to
formula-created gates without re-discovering them. This is the shape
[`yf-beads-authoring`](/skills/yf-beads-authoring/) relies on when it pours and wires a
skill's DAG.
