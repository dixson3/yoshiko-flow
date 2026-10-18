---
title: yf beads touchpoint inventory
created: 2026-10-18
tags: [beads, yoshiko-flow, research]
---

> Produced by an isolated read-only sub-agent (2026-10-18) against yoshiko-flow `main` @ a9e03f1
> (bd 1.3.1, live DB queried read-only). Unedited agent output follows.

# yf's dependencies on beads (`bd`): inventory for a possible switch to grite

**Scope.** I read `skills/`, `agents/`, `scripts/`, formulas, the `yf/` Rust crate, tests and `SPEC.md`. I skipped `.worktrees/`, `target/` and `docs/plans/`. I also queried the live DB with read-only `bd count`, `bd list` and `bd export` to a temp dir. Counts are regex hits over `\bbd <verb>`, so they include prose; prose-only words like "bd is" were dropped. File:line references point to real invocations.

**Live corpus, for sizing a migration.** There are 2,754 beads:

- **Types:** 1,997 task, 374 epic, 243 gate, 79 molecule, 43 bug, 13 feature, 4 chore, 1 decision.
- **Edges:** 2,990 `blocks`, 2,542 `parent-child`, 30 `discovered-from`, 6 `relates-to`/`related`.
- **Fields in use:** 1,320 beads carry metadata, 134 carry `external_ref`, 2,515 carry `close_reason`, 75 carry `await_type`, 55 carry labels.

There is already a `.worktrees/grite-migration`. It sits at plan-073 intake with only an untracked `Incubator/`, so no migration work exists yet.

---

## 1. `bd` subcommands and flags

### Core work loop (used at runtime by skills and scripts)

| Subcommand | Hits | Key flags relied on | Main users (file:line) |
|:--|:--|:--|:--|
| `bd list` | 179 | `--all`, `--json`, `--parent`, `--type gate`, `--status all\|open,in_progress`, `--include-gates`, `--limit 500/5000`, `--label`, `--metadata-field k=v` | `plan_manager.py:3865,4681,4695,5860,5864,9504`; `close_cascade.py:130,168`; `verify_beads.py:61`; `upstream.py:630,1216,1281`; `beads_hygiene.py:198,214`; yf-research `SKILL.md:476` |
| `bd show` | 137 | `--json` (one call in upstream has no `--json`) | `plan_manager.py:1940,5874,9676`; `close_cascade.py:116`; `upstream.py:577`; `beads_hygiene.py:223`; both coordinators |
| `bd close` | 120 | `--reason`, `-r`, `--json` | `plan_manager.py:6038,6184`; `close_cascade.py:191`; `upstream.py:1709` (tombstone); yf-plan `coordinator.md:80`; research `packager.md:121` |
| `bd update` | 94 | `--claim`, `--status open\|blocked`, `--metadata <json>` (whole object), `--set-metadata k=v`, `--unset-metadata k`, `--external-ref <url>`, `-q`, `--json` | yf-plan `coordinator.md:29,61,83-89,114-115`; `SKILL.md:1026,1156`; yf-research `SKILL.md:364,372-377`; `plan_manager.py:2008`; `upstream.py:1114,1190` |
| `bd ready` | 79 | `--json`, `--limit 500` | yf-plan `coordinator.md:49-52`; research `coordinator.md:116-120` |
| `bd create` | 72 | `-t task\|epic\|gate`, `-p N`, `--parent`, `--deps "<id>"` and `--deps discovered-from:<id>`, `--description`, `--metadata <json>`, `--label`, `--silent`, `--json` | yf-plan `SKILL.md:1072,1092,1100,1174,1224,1229,1895`; yf-research `SKILL.md:389`; `refiner.md:33`; `verify_beads.py:124` (planned bead) |
| `bd dep add` / `remove` / `list` / `cycles` | 36 / 4 / 19 / 15 | `dep list --json` (edge key is `type` here, `dependency_type` in `show`) | `upstream.py:1220,1284`; `beads_hygiene.py:783,792,813`; `refiner.md:37` |
| `bd batch` | 40 | stdin of `dep add A B` lines, `-m msg` (one Dolt transaction) | yf-plan `SKILL.md:1215`; yf-research `SKILL.md:407`; also po-orchestration `_bd.py:91` (`close` ops) |
| `bd children` | 4 | `--json` | `close_cascade.py:164` |
| `bd epic status` / `close-eligible` | 2 | `--json` | yf-research `SKILL.md:503`; `packager.md:120` |
| `bd swarm create` / `bd graph` | 1 / 1 | | yf-research `SKILL.md:413-414` (reporting only) |

### Molecules and formulas

| Subcommand | Hits | Users |
|:--|:--|:--|
| `bd mol pour <f> --var k=v --json` | 71 | yf-plan `SKILL.md:1006`; yf-research `SKILL.md:342`; `yf/src/cmd/doctor/checks.rs:267` (static scan) |
| `bd mol wisp` / `bd mol burn --force` | 8 / 8 | yf-plan `SKILL.md:404,1241` |
| `bd mol distill` | 2 | research `coordinator.md:172` (optional) |
| `bd formula list --json` / `bd formula show --json` | 5 / 3 | `retrospective_fields.py:35`; `verify_beads.py:80` |

### Gates

| Subcommand | Hits | Users |
|:--|:--|:--|
| `bd gate resolve <id>` | 38 | `plan_manager.py:6018`; yf-plan `coordinator.md:182`; yf-research `SKILL.md:425,456` |
| `bd gate list [--all] [--limit] --json` | 16 | yf-research `SKILL.md:439`; yf-plan `coordinator.md:150-166` (documented as unsuitable because it carries no metadata) |
| `bd gate create` / `approve` | 4 / 9 | documentation only; `approve` is noted as nonexistent in `yf-beads-extra` |

### Infrastructure and configuration

| Subcommand | Hits | Users |
|:--|:--|:--|
| `bd status --json` | 50 | `beads_init.rs:224`; `preflight.rs:830`; `beads_hygiene.py:190` |
| `bd init --skip-hooks --skip-agents` | 42 | `beads_init.rs:466` |
| `bd doctor [--fix]` | 13 | `beads_init.rs:303,533` |
| `bd migrate [schema]` | 22 / 28 | `beads_init.rs:373-375,535` |
| `bd dolt stop` / `commit` / `push` / `remote` | 29 / 23 / 47 / 8 | `beads_init.rs:365,868`. `dolt push` appears only as a proposed command in land-the-plane handoffs (yf-plan `SKILL.md:1636`, `coordinator.md:283-298`, `packager.md:125-142`, `beads_hygiene.py:172-177`) |
| `bd vc commit` | 18 | documented as unusable on a wedged DB |
| `bd config get` / `set` / `unset` | 21 / 28 / 3 | `upstream.py:263` (`custom.upstream.*`); `beads_hygiene.py:166`; `beads_init.rs:486,504,1059`; coordinator `dolt.local-only` guard |
| `bd export -o .beads/issues.jsonl` | 4 | `beads_init.rs:544` |
| `bd hooks uninstall` / `run` | 5 / 10 | `beads_init.rs:558`; `preflight.rs` (shim signature detection) |
| `bd setup claude\|codex --remove` | 30 | `beads_init.rs:565,571` |
| `bd version` / `--version` | 17 | `preflight.rs:663`; `tool.rs:172`; `plan_manager.py:621` |

### Memory

`bd remember`, `bd memories`, `bd recall` and `bd prime` appear only in `AGENTS.md:9` as the clone-local memory convention. `yf/src/cmd/harness/settings.rs:346` and `mod.rs:1577` preserve a `bd prime` SessionStart hook in harness settings. No skill or script calls them.

### `--json` parsing

Every script has its own defensive parser for multi-document output, warning prefixes and object-or-array shapes:

- `plan_manager.py:4639` (`_parse_bd_json`) plus the `json-get` verb
- `close_cascade.py:34`
- `beads_hygiene.py:83`
- `upstream.py:494` (`parse_json_array`)
- `research_manager.py:29-77`

### po-* skills

These are not in this repo; they are installed from the `panopticon` package. `po-orchestration/scripts/orch/_bd.py` wraps:

- `bd list -l <label>` (12 calls)
- `bd list --metadata-field epic|job=...` (15)
- `bd show`, `bd close`, `bd update`, `bd create --metadata`
- `bd batch --json` carrying `close` ops

It follows the same patterns as yf, and adds label-based and metadata-field queries.

---

## 2. Formulas

The shipped formulas are under `skills/*/formulas/`. Preflight stages them into `.beads/formulas/` and records ownership in `.beads/formulas/.yf-staged.json` (`preflight.rs:65-74,399-434`, REQ-YF-PRE-011). `plan-review` and `verify-artifact` still exist in the local `.beads/formulas/` but were deleted from source in plan-071 (commit `52da43e`). They are stale and have no callers.

| Formula | Definition | Poured by | Consumption |
|:--|:--|:--|:--|
| `plan-investigate` (`yf-plan/formulas/…:1-23`) | `phase="vapor"`; vars `objective`, `plan_dir`; **no static steps**. Experiment beads are injected as children. | yf-plan §2 `bd mol wisp plan-investigate` (`SKILL.md:404`) | Investigator subagents run in disposable worktrees. Burned at §5.2a with `bd mol burn --force` (`SKILL.md:1241`); without `--force` the prompt defaults to No and orphans the wisp. |
| `plan-execute` (`…/plan-execute.formula.toml`, 33 lines) | `phase="liquid"`; vars `objective`, `plan_dir`. One step: `start-gate`, `type="gate"`, `[steps.gate] type="human" approvers=["operator"]`. Everything else is injected at intake. | yf-plan §5.2a `bd mol pour plan-execute --var … --json` (`SKILL.md:1006`) | `new_epic_id` gives the epic. `id_mapping["plan-execute.start-gate"]` is the task wrapper used in `--deps`; `id_mapping["plan-execute.gate-start-gate"]` is the real gate. Child epics, task issues, capability gates and the optional reconcile gate/step are created by hand from `plan_extract.py` JSON, and edges are wired with one `bd batch`. The coordinator loop in `agents/coordinator.md` drains `bd ready` under `${EPIC}`. |
| `yf-research` (72 lines) | `phase="liquid"`; vars `topic`, `mode` (enum quick/standard/deep/ultradeep), `research_dir`. Steps: `gate` (human) → `tooling` → `triangulate` → `synthesize` → `critique` → `refine` → `package`, chained with `needs`. | yf-research Phase 3 (`SKILL.md:342`) | Each step id is read from `id_mapping["yf-research.<step>"]`. Agent metadata is attached per step (`SKILL.md:372-377`). Retrieve beads fan out, one per source cluster, with `--deps tooling`; triangulate is then wired to every retrieve bead in one `bd batch` (fan-in). `bd gate resolve` runs in a new session via `coordinate`. |

**Pour behaviour yf depends on:**

- A `type="gate"` step produces **two beads**: a task wrapper titled `Begin: …` and a gate titled `Gate: …`.
- The wrapper→gate dependency is visible in `bd show`'s `dependencies[].issue_type`.
- `plan_manager.py:5896-5936` (`_find_start_gate_pair`) finds the pair by **title prefix and issue_type**.
- `resolve-start-gate` (`plan_manager.py:5958-6067`) runs `bd gate resolve` on the gate, then closes the wrapper. That two-step close was added after all 49 historical wrappers had been closed by hand.
- `yf doctor`'s FormulaCheck (`checks.rs:250-290`, REQ-YF-DOCTOR-004) scans bash fences for `bd mol pour|wisp <name>` and requires a shipped formula for each name.

---

## 3. Gates

**Kinds of gate in use:**

1. **Session-boundary human start gate.** Created by the formula. Released only in a **new session**: `/yf-plan execute` through `resolve-start-gate` (REQ-SESSION-001, REQ-PHASE-002), or `/yf-research coordinate` (`SKILL.md:425-456`), except in quick mode. The research `coordinate` command finds pending work by listing open gates with `bd gate list --json` and filtering to yf-research epics. With 0 open gates it falls back to resume detection (`SKILL.md:441-480`).
2. **Capability gates.** Created with `bd create -t gate --parent ${EPIC} --metadata '{gate_type,test,test_class,cwd}'` (`SKILL.md:1174`), and wired to dependent issues through `bd batch`.
   - The semantics are implemented by yf, not bd: an absent `gate_type` means `human`, and `human` gates are never auto-resolved; `auto` gates run `test` in the address space named by `cwd`, and exit 0 leads to `bd gate resolve` (`coordinator.md:171-185`).
   - The execute-start sweep (§5.2c, `SKILL.md:1290+`) auto-runs only `test_class=probe`.
3. **Reconcile gate.** Created with `-t gate`, no metadata (`SKILL.md:1224`). `coordinator.md:247-250` says it "auto-resolves" once the execution beads close, but nothing in the repo calls bd await or timer machinery for it. In practice it is resolved by the coordinator. **This needs checking.**
4. **Deferral gates.** A gate's `Instructions:` may tell the coordinator to tombstone the beads it blocks with `bd close -r` (`coordinator.md:253`).

**Measured bd behaviours yf relies on** (asserted in `test_gates.py`):

- `bd ready` never returns gate beads.
- `bd list` without `--type gate` or `--include-gates` hides gates.
- `bd gate list` returns rows **without metadata**; `bd list --type gate` returns them with metadata.
- Default pages silently truncate at 50 with exit 0, so an explicit `--limit` is mandatory.
- `bd ready --include-gates` is rejected.

**Terminal-state check.** `close_cascade.py::_bead_is_terminal` is the single predicate, shared by `plan_manager.py:5882`. Gates are terminal when `status == closed`. The 75 `await_type` values in the DB come from pour, not from yf.

**Hygiene.** `beads_hygiene.py:205-218` merges `list --all` with `list --all --type gate` so that live gates are never reported as dangling.

---

## 4. Bead fields and metadata conventions

- **Issue types:** `epic`, `task`, `gate` and `molecule` (from pour) are structural. `bug`, `feature`, `chore` and `decision` are informational. `upstream.py:937-953` maps `type::<issue_type>` and priorities 0–4 to `priority::critical…backlog` labels.
- **Priorities:** `-p 1` for reconcile and deferred-validation beads, `-p 2` for normal issues.
- **Metadata keys** (live counts, with writers):
  - `plan` (980), `plan_issue` (911), `plan_dir` (748): yf-plan intake (`SKILL.md:1092-1104`). Read by `pour_fidelity.py:82-85`, `verify_beads.py:101-124`, and resume-scan's fallback (`plan_manager.py:2106-2163`).
  - `upstream` (220), `disposition` (209): `SKILL.md:1156`, read by the reconciler.
  - `agent` (108), `context` (108): agent dispatch in both coordinators (`research coordinator.md:133`).
  - `gate_type`, `test`, `test_class`, `cwd` (≈85): capability gates.
  - `cluster`: research retrieve beads. `research_dir`: research epic, queried with `bd list --metadata-field`.
  - `yf_attempts`: failure counter, written only with `--set-metadata` / `--unset-metadata` because whole-object `--metadata` would clobber sibling keys (`coordinator.md:107-120`).
  - `verifies`: `verify_beads.py:124`.
- **`external_ref`:** the GitHub issue URL. It is the **only** bead↔issue mapping. Written by `upstream.py:1114` and `plan_manager.py:2008` (`stamp-tracker`). `closable` groups beads by it.
- **`close_reason`:**
  - Must state what was verified (`coordinator.md:80`).
  - The hoist tombstone prefix `"hoisted upstream to "` is parsed by `upstream.py:1488-1497` (REQ-BUP-070).
  - The start-gate wrapper gets a generated reason (`plan_manager.py:6030`).
- **`owner` / `assignee`:** `--claim` sets ownership. An open bead with an owner counts as active and is excluded from hoist (`upstream.py:849-858`).
- **`status`:** `open`, `in_progress`, `blocked` and `closed`, plus `deferred` (in `NONACTIVE_STATUSES`). `blocked` has a deliberate meaning: it drops the bead out of `bd ready`, and is used for escalation (`coordinator.md:89-100`).
- **`created_at`:** the broad follow-on signal (`upstream.py:897`).
- **Labels:** `deferred-validation` (`SKILL.md:1895`; queried at `plan_manager.py:2389`). `follow-on` and ad-hoc labels are passed through to GitHub.
- **Dependency types:** `blocks`, `parent-child` (`--parent`), and `discovered-from` (`--deps discovered-from:<id>`). `discovered-from` is the narrow auto-hoist signal (`upstream.py:860-904`).
- **Unused:** `design`, `notes` and `acceptance_criteria` are never written by yf (3 and 18 live occurrences, all incidental).
- **Bead description:** carries a provenance header `Plan: … | Bundle: …` (`SKILL.md:1078-1090`, REQ-DATA-073).

---

## 5. Infrastructure coupling

**Rust kernel.**

- `yf/src/beads_init.rs` (2,614 lines) is entirely beads/Dolt-specific:
  - `verify()` parses `bd status --json` for an `error` key (`:160-232`).
  - Wedged-migration repair is mode-aware: `bd dolt stop` in server mode, or a native raw `dolt add -A && commit` in the embedded Dolt dir (`:354-377,814-880`), followed by `bd migrate schema` and `bd migrate`.
  - The init path asserts `dolt.local-only` and removes the Dolt remote that `bd init` wires from git origin (`:466-512`).
  - Hardening runs `doctor --fix`, `migrate`, `export -o .beads/issues.jsonl`, `hooks uninstall` and `setup claude|codex --remove`. Native steps strip managed blocks, untrack runtime `.beads/` files, remove hook shims, `chmod 700`, and top up `.beads/.gitignore` and the root `.gitignore` (`:524-631`).
  - Embedded-vs-server detection comes from `metadata.json` `dolt_mode` plus `dolt-server.{pid,port}` (`:679-700`).
- `preflight.rs`:
  - min-bd-version gate: default 1.0.5 (`:39,616-663`); the yf-plan, yf-research, yf-beads-init and yf-beads-upstream skills declare 1.1.0.
  - `bd_not_initialized` status (`:830`).
  - Formula staging and gitignore anchor (`:65-74,397-434`).
  - Canonicalization drift (REQ-YF-PRE-010).
- `cmd/doctor/checks.rs`: `BinCheck("bd")` (`:749`), FormulaCheck (`:250-290`), and LocalOnlyRemoteCheck.
- `frontmatter.rs` parses `depends-on-tool: [bd,…]`.
- `cmd/harness/settings.rs` preserves the `bd setup claude` SessionStart hook block (REQ-YF-TUNE-003/006).
- `skills/yf-beads-init/scripts/beads_init.py` is a retired shim that forwards to `yf`.

**This repo's state.** Server mode (`dolt_mode: server`). The whole `.beads/` directory is excluded via `.git/info/exclude`, so the JSONL export is **not** committed here. Even so, the coordinator's handoff still proposes `git add .beads/` (`coordinator.md:287`).

**Worktree DB sharing (INV-2).**

- `bd` finds the primary `.beads/` through git-common-dir.
- `plan_manager.py:3862-3869` (`_bd_resolves_from`) probes this by running `bd list --json` with `cwd=` the worktree. A non-zero exit gives the `bd-db-unresolved` verdict, which falls back to an in-place run.
- `_worktree_viability` also requires `.beads/` in the primary (`:3895-3899`).
- All `bd` calls run primary-side (`coordinator.md:196-198`).

**Upstream hoist path** (`upstream.py`, gh-direct):

1. Read: `bd list --all --json` (`:630`), `bd list --parent --all` plus `bd dep list` for the subtree and follow-ons (`:1213-1290`), `bd show` (`:577`).
2. Write: `gh issue create/edit`, then `bd update --external-ref <url> -q` (`:1114`).
3. Only after a structurally verified write: the local `bd close <id> -r "hoisted upstream to …"` tombstone (`:1164-1173`). `bd delete` is never used.
4. Un-hoist: `bd update --status open` (`:1185`).
5. Config keys: `custom.upstream.{enabled,backend,granularity,auto_hoist_followons,owner_on_create}` via `bd config get` (`:250-340`). Upstream configuration therefore lives in the **bd config store**.
6. `reconcile` closes beads whose upstream issue is closed (`:1709`).

---

## 6. Tests

- **Tier-1** (54 `test_*.py` files; 23 mention bd). No Python test runs a live `bd`. They either:
  - monkeypatch the bd wrappers (`run` ×28, `_bd_healthy` ×8, `_bd_ex` ×7, `_bd_list` ×7, `_bd_resolves_from` ×2, and others; for example `test_worktree.py:66,121`), or
  - feed pinned JSON fixtures (`upstream.py --fixture`, REQ-BUP-070a), or
  - assert on SKILL.md and coordinator prose (`test_gates.py:134-230` checks that `bd list --type gate` is used and `--limit` is present).
- `land_rehearsal.py:82-123` fakes `bd`, `gh`, `uv`, `yf` and `sh` in a rehearsal harness. `check_no_universe_fanout.py` is an AST lint that forbids per-bead `bd show` / `bd dep list` fan-out over the full bead set.
- **Tier-2:** `skills/yf-plan/test-harness/smoke.sh:71-76` runs `bd init` in a throwaway git project under a sandboxed `HOME` (`bootstrap.sh`). It drives `plan_manager.py` verbs and does not pour.
- **Rust:** `beads_init.rs` live tests (`:1860,2031,2539`) use `tempfile::tempdir()`, `git init` and `bd init --skip-hooks --skip-agents`, and return early when `which("bd")` or `which("dolt")` is missing.

`bd mol pour`, `bd gate resolve`, `bd ready` and `bd batch` therefore have **no automated live coverage**. Their behaviour is pinned only by prose assertions and measurements recorded in comments.

---

## 7. Root SPEC.md requirement IDs that mention beads/bd

- **REQ-YF-INSTALL-003/004:** frontmatter `depends-on-tool` / `depends-on-skill` closure; installing workflows pulls in the beads skills.
- **REQ-YF-PRE-001:** preflight status enum includes `bd_not_initialized`.
- **REQ-YF-PRE-002:** enforce the per-skill `min-bd-version`.
- **REQ-YF-PRE-006:** classify `bd status --json` by its `error` key, not the exit code.
- **REQ-YF-PRE-007:** mode-aware wedged-migration repair (`bd dolt stop` or a raw dolt commit, then `bd migrate schema` and `bd migrate`) plus hardening.
- **REQ-YF-PRE-008:** the preflight cache re-probes bd on a version change.
- **REQ-YF-PRE-010:** minimal-local beads profile (server mode, worktree sharing, local-only/no remote); drift is detected read-only.
- **REQ-YF-PRE-011:** the kernel owns formula staging into `.beads/formulas/`, with the `.yf-staged.json` marker and a gitignore anchor.
- **REQ-YF-DOCTOR-001:** doctor checks `bd` is present and at least 1.0.5.
- **REQ-YF-DOCTOR-003:** `doctor --repair` runs the beads-init repair, with `--local-only` and `--remove-remote`.
- **REQ-YF-DOCTOR-004:** static FormulaCheck: every `bd mol pour|wisp <name>` has a shipped formula; `--prune-formulas` garbage-collects staged ones.
- **REQ-YF-DOCTOR-006:** every repair step verifies its own postcondition (local-only remote removal, among others).
- **REQ-YF-DIST-002:** the Homebrew formula declares no `bd` dependency.
- **REQ-YF-TUNE-001/003/006:** harness tune preserves the `bd setup claude` SessionStart hook.
- **Amendment log (L1341):** REQ-PLAN-030 amended; the `plan-review` and `verify-artifact` formulas were removed.

Most of the beads contract lives in the **per-skill specs**. Requirements that touch beads, per file:

| Spec | Beads-related reqs |
|:--|:--|
| yf-beads-upstream (`SPEC.md` + `spec/`) | 59 (`REQ-BUP-*`) |
| yf-beads-authoring | 44 (`REQ-BAUTH-*`, `REQ-ORCH-*`, `REQ-FORMULA-*`) |
| yf-beads-extra | 34 (`REQ-BEXTRA-CLI-*`, `REQ-CLI-*`) |
| yf-plan (all files) | ~62 (`REQ-PLAN-067/073/077`, `REQ-DATA-026/073`, `REQ-PHASE-002`, `REQ-RESUME-004`, `REQ-SESSION-001`, and others) |
| yf-beads-init | 20 (`REQ-BINIT-*`) |
| yf-research | 18 |
| yf-beads-hygiene | 13 |

---

## Summary table

| Capability | Used by (skills) | Criticality | Notes |
|:--|:--|:--|:--|
| Typed issues (task/epic/gate/molecule) + `--parent` hierarchy | yf-plan, yf-research, hygiene, upstream | core | Structural types; the "epics only block epics" rule shapes intake |
| `blocks` deps + `bd ready` (excludes blocked status, gates, molecules) | yf-plan, yf-research coordinators | core | Semantics measured by hand and encoded in prose; no live test. **Hard** |
| `--claim` (atomic owner set) | coordinators, upstream active-set | core | `owner` drives hoist exclusion |
| Formula engine: `mol pour` with vars, `id_mapping`, gate step → wrapper+gate pair | yf-plan, yf-research, yf doctor | core | Key shapes (`<f>.gate-<step>`), `Begin:`/`Gate:` title detection, staging dir. **Hardest to replace** |
| `mol wisp` / `burn` (ephemeral molecule) | yf-plan §2 | convenience | Only used as a parent for experiment beads |
| Gate beads + `gate resolve` + `list --type gate` metadata | yf-plan, yf-research, hygiene | core | Human/session semantics are yf's, but gate exclusion from `ready` is bd's. Reconcile "auto-resolve" is unverified |
| JSON metadata, per-key `--set/--unset-metadata`, `--metadata-field` query | all orchestrators, po-orchestration | core | 1,320 beads; resume and fidelity depend on it. **Hard** if grite lacks per-key merge or field query |
| `bd batch` transactional dep wiring | yf-plan, yf-research, po-orchestration | convenience→core | Atomicity was the stated reason; could fall back to sequential with rollback |
| `discovered-from` edge type | coordinators, upstream follow-on hoist | core (upstream) | Narrow auto-hoist signal |
| `external_ref` field | yf-beads-upstream, yf-plan `stamp-tracker` | core | The only bead↔GitHub mapping (134 beads) |
| `close_reason` (verified-reason, tombstone prefix) | coordinators, upstream, close_cascade | core | Parsed semantically (`hoisted upstream to `) |
| Labels / `--label` queries | yf-plan deferred-validation, upstream, po-* | convenience | Light use in yf; heavier in po-* |
| `bd config` store (`custom.upstream.*`, `dolt.local-only`) | upstream, init, coordinators | core | Upstream config would need a new home |
| Dolt infra (init/migrate/doctor/dolt stop/commit/remote, server vs embedded) | yf-beads-init, yf kernel | core today | ~2.6k lines of Rust plus the BINIT/PRE specs would be replaced, not ported |
| JSONL export / gitignore / hooks / `bd setup` cleanup | yf-beads-init, kernel | convenience | Exists to clean up bd side effects |
| Worktree DB sharing via git-common-dir | yf-plan worktree mode | core | `_bd_resolves_from` probe; grite needs equivalent cross-worktree visibility |
| `children`, `epic status/close-eligible`, `swarm`, `graph`, `dep cycles` | close_cascade, research, hygiene | convenience | All derivable from list+deps |
| `bd remember` / `prime` memory | AGENTS.md convention, harness hook preservation | convenience | Not used by skills |
| Version gating (`min-bd-version`, `bd version`) | kernel, 4 skills | core (mechanical) | Would become a grite version gate |

**Likely hard to replace:**

1. The `mol pour` gate-step expansion and `id_mapping` key names, which yf code depends on precisely.
2. The exact `bd ready` and gate-visibility semantics, which are pinned only by prose and measurements.
3. Per-key metadata merge plus metadata-field queries.
4. `external_ref` and `close_reason` as semantic carriers for the upstream mapping.
5. Worktree-shared DB resolution.
6. The fact that the whole repair/verify kernel and roughly 70 per-skill requirements are written against Dolt-specific failure modes.
