# exp-002: bd mechanisms for reconcile (active-set, follow-on detection, granularity, removal)

bd 1.0.5.

## Detecting follow-on / discovered-during beads

- **`discovered-from` is a first-class dependency edge type.** Full set: `blocks|tracks|related|parent-child|discovered-from|until|caused-by|validates|relates-to|supersedes`. Set via `bd create --deps "discovered-from:<id>"` or `bd dep add <id> <target> -t discovered-from`. Verified live: `dqo` has a `discovered-from` dep to `mol-2bi.2`. Agents already file follow-ons this way.
- **Identification (best → fallback):**
  1. `discovered-from` edges — query candidate bead deps for `dependency_type == "discovered-from"`; the target is whatever discovery happened during (epic/task), so walk up to confirm it's under the plan molecule.
  2. `created_at` (RFC3339 UTC) + parent scoping: `bd list --parent <mol-id> --created-after <date> --all --json` (`--parent` matches descendants).
  3. Molecule `created_at` is the intake timestamp; later-created beads under the tree are candidates.

## "Actively worked" mechanically

- **Status:** `open|in_progress|blocked|deferred|closed`. Filter `bd list --status in_progress,open --json`.
- **Ownership:** `owner` (identity URI/email) and `assignee` (display name) are distinct; claimed bead has `owner` set; `started_at` set when work begins. `bd ready --unassigned` / `--assignee`.
- **Chosen active set** = `status==in_progress` ∪ (`status∈{open}` AND `owner` non-empty) ∪ their **open** parent-chain ancestors.
- **Ancestors:** parent is a `parent-child` **edge**, not a scalar. From child: `bd dep list <id> --direction=down -t parent-child --json` → parent is `depends_on_id`. Walk down until no parent; keep `status != closed`.
- **Edge-type field name differs:** `dependency_type` in `bd show --json`; `type` in `bd dep list --json`. Handle both.

## Granularity config (folds in #17)

- Custom keys in `custom.*` namespace, per-project in the DB. `bd config get/set/unset/list/show/set-many`. **Unset key returns `(not set)` on stdout with exit 0** — detect unset by inspection, not exit code.
- **Recommendation:** add `custom.upstream.granularity` = `coarse|granular` (default `coarse`) alongside `custom.upstream.enabled`/`backend`. AGENTS.md already documents coarse as the operative default (precedent #13/#14/#16/#24) — the key formalizes existing behavior (REQ-BUP-043).

## Removal: close vs delete

- **`bd close [id] -r "<reason>"`** — sets `status=closed` + `closed_at` + `close_reason`; non-destructive, edges/history/JSONL retained, reversible. **Established reconcile pattern** (e.g. `mol-yvv` close_reason records "...Epic 7 hoisted to #28").
- **`bd delete <id> --force`** — permanent, strips edges, rewrites references to `[deleted:ID]`, `--cascade` recurses. Not reversible.
- **"Remove locally" = `bd close` with a destination-recording reason** (reversible tombstone, survives export). Reserve `delete` for truly-gone beads.

## Drop-in reference

- Follow-ons: `bd dep add <id> <target> -t discovered-from`; scope: `bd list --parent <mol-id> --created-after <date> --all --json`.
- Active: `bd list --status in_progress --json` ∪ (`bd list --status open --json` with non-empty `owner`); `bd ready --json`.
- Ancestors: `bd dep list <id> --direction=down -t parent-child --json`.
- Config: `bd config get/set custom.upstream.granularity` (unset → `(not set)` exit 0).
- Removal: `bd close [id] -r "<reason>"` (preferred) vs `bd delete <id> --force` (destructive).
