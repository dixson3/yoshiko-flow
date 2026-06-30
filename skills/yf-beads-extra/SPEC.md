# SPEC — Beads Extra (`yf-beads-extra`)

> **Status: Active.** Per-skill SPEC for the advanced/gotcha `bd`-CLI layer. The `yf-beads-extra` rename is complete and the
> skill is shipped; this SPEC tracks the live behavior. Requirements use RFC-2119 "shall"; composed
> by the root `SPEC.md` macro spec.

## 1. Purpose & scope

`yf-beads-extra` is the advanced/gotcha layer for driving the `bd` (beads) CLI **directly at
runtime**, on top of the canonical `beads` skill. It documents only the parts that bite when you
script `bd`: issue-type semantics, gate verbs, dependency-edge mutation, defensive `--json`
parsing, transactional bulk intake (`bd batch`), and the `bd mol pour` output shape. It is verified
against **bd 1.0.5** (gastownhall/beads) and **wins** over the bundled `beads` plugin's pre-1.0.5
`resources/` where they disagree.

**In scope:** the version-sensitive `bd` behaviors a script must get right (REQ-BEXTRA-CLI-*) and
the defensive JSON-parsing / scope rules (REQ-BEXTRA-JSON-*, REQ-BEXTRA-DOC-*).

**Out of scope:** the routine `bd ready`/`bd show`/`bd update --claim`/`bd close` loop (the `beads`
skill); authoring beads-backed skills — formulas, coordinator loops, the `coordinate` subcommand
(`yf-beads-authoring`); the canonical dependency-type taxonomy and issue lifecycle (the plugin's
`resources/DEPENDENCIES.md` / `WORKFLOWS.md`, cited not restated). `user-invocable: false`.

## 2. Requirements (`REQ-BEXTRA-NNN`)

### 2.1 `bd` CLI contracts, bd 1.0.5 (see `spec/cli.md`)

- **REQ-BEXTRA-CLI-001** *(testable)* `bd create -t` shall be documented as accepting the
  help-advertised normal-work enum `bug|feature|task|epic|chore|decision` **and** the built-in
  special types `gate`, `event`, `molecule`; an unknown type is rejected (`invalid issue type`).
  (`spec/cli.md` REQ-CLI-001.)
- **REQ-BEXTRA-CLI-002** `gate`, `event`, `molecule` shall be treated as non-ordinary work items —
  each with a dedicated creation path (`bd gate create`/formula; `--type=event` + `--event-*`;
  `bd mol pour`) — and a `molecule`/resolved-`gate` bead does not surface in `bd ready`.
  (REQ-CLI-002.)
- **REQ-BEXTRA-CLI-003** *(testable)* the gate verbs in 1.0.5 shall be
  `add-waiter|check|create|discover|list|resolve|show`; there is no `bd gate approve|eval|close`;
  a gate is resolved with `bd gate resolve` (or `bd close`). (REQ-CLI-003.)
- **REQ-BEXTRA-CLI-004** *(testable)* `bd dep` edge addition shall be documented as **additive**
  (`bd dep <blocker> --blocks <blocked>` ≡ `bd dep add <blocked> <blocker>`, neither drops existing
  edges); `bd update` has no `--deps` flag in 1.0.5 (the old replace-the-list gotcha does not
  apply). (REQ-CLI-004.)
- **REQ-BEXTRA-CLI-005** *(testable)* a task cannot block an epic — `bd dep add <epic> <task>`
  errors (`epics can only block other epics, not tasks`); the workaround is to block the epic's
  children or rely on transitive ordering. (REQ-CLI-005.)
- **REQ-BEXTRA-CLI-006** `bd close <id>` shall be documented as **not** refusing when dependents
  remain open (close ordering is not enforced); callers order their own closes or audit with
  `bd dep list` / `bd blocked`. (REQ-CLI-006.)
- **REQ-BEXTRA-CLI-007** *(testable)* `bd mol pour <formula> --json` shall be documented as
  returning `new_epic_id` and `id_mapping` (formula-step → bead ID), with a `gate` step yielding
  two beads (`<f>.<step>` wrapper task + `<f>.gate-<step>` gate). (REQ-CLI-007; cross-ref
  `yf-beads-authoring` REQ-BAUTH-011.)
- **REQ-BEXTRA-CLI-008** *(testable)* bulk edge intake shall use `bd batch` (one dolt transaction,
  atomic rollback on any error); creates are **not** batchable — each needs its returned ID
  captured before reference, and an empty create result is a stop-and-fix. (REQ-CLI-008.)
- **REQ-BEXTRA-CLI-009** *(testable)* `bd list`/`bd list --all` shall be documented as **hiding
  `gate`-type beads** and **truncating at 50 rows** by default — unsafe as the "which beads exist"
  source of truth; a graph audit shall build the full universe from `bd list --all` **plus**
  `bd list --all --type gate` and resolve edge targets via `bd show` (which sees gates), never by
  `bd list` membership. (REQ-CLI-009; `yf-beads-hygiene` encodes the discipline.)
- **REQ-BEXTRA-CLI-010** `bd dep cycles` shall be documented as the read-only post-mutation
  integrity check run after any `bd dep add`/`bd dep remove`. (REQ-CLI-010.)

### 2.2 Defensive JSON parsing & scope (see `spec/json-and-scope.md`)

- **REQ-BEXTRA-JSON-001** for a status report or eyeballing state, `--json` shall **not** be used —
  the human-readable `bd show`/`bd list`/`bd ready` output is the direct path; `--json` is reached
  for only when a script consumes specific fields. (`spec/json-and-scope.md` REQ-JSON-001.)
- **REQ-BEXTRA-JSON-002** *(testable)* a script shall never call `json.loads(stdin)` directly on
  `bd` output: it may carry warning prefixes and may be a multi-document array (`bd show --json`
  returns a one-element array even for a single id). Parsing shall be defensive — first-balanced-
  block extraction, or array-aware iteration (`data[0]`, not `data.get(...)`). (REQ-JSON-002.)
- **REQ-BEXTRA-JSON-003** inside `yf-plan`/`yf-research`, the manager script's hardened `json-get`
  extractor shall be preferred over a hand-rolled parser (one audited parser, not many).
  (REQ-JSON-003.)
- **REQ-BEXTRA-JSON-004** *(testable)* test-pattern titles (`bd create "TEST-…"`) prepend a
  multi-line warning that breaks naive parsers; tests shall use a real title or an isolated DB
  (`bd --db /tmp/…`). (REQ-JSON-004.)

### 2.3 Documentation-authority boundary (see `spec/json-and-scope.md` → *Scope & boundary*)

- **REQ-BEXTRA-DOC-001** this skill shall be the 1.0.5-verified layer and **win** over the bundled
  `beads` plugin's pre-1.0.5 `resources/` where they disagree (named: `ASYNC_GATES.md` gate verbs;
  `CHEMISTRY_PATTERNS.md` bare `bd pour`/`bd wisp`/`bd mol catalog`). (REQ-DOC-001.)
- **REQ-BEXTRA-DOC-002** stable taxonomy the plugin documents correctly (the four dependency types
  in `DEPENDENCIES.md`; the lifecycle in `WORKFLOWS.md`) shall be **cited, not restated**; this
  skill keeps only mutation/gotcha mechanics the plugin lacks. (REQ-DOC-002.)
- **REQ-BEXTRA-DOC-003** routine `bd ready`/`bd show`/`bd update --claim`/`bd close` flows belong to
  the canonical `beads` skill, not here; authoring beads-backed skills belongs to
  `yf-beads-authoring`. (REQ-DOC-003.)

## 3. Interfaces

- **CLI / scripts:** none — this is a reference/gotcha skill. It documents `bd` CLI behavior and
  ships defensive-parse snippets inline; the hardened parser it points consumers to lives in
  `yf-plan`'s `plan_manager.py json-get`, not here.
- **Companion rule:** none — `user-invocable: false`, no always-loaded trigger rule.
- **Config / state:** none. No `.local.json`, no `.yf/` state.

## 4. Guardrails (`GR-BEXTRA-NNN`)

- **GR-BEXTRA-001** *Drift:* restating the canonical `bd` taxonomy or the routine loop. *Rule:* the
  four dependency types and the issue lifecycle are **cited** from the plugin `resources/`; the
  routine loop is the `beads` skill's; this skill keeps only the 1.0.5-verified gotcha delta.
  *Why:* one source of truth per fact.
- **GR-BEXTRA-002** *Drift:* assuming pre-1.0.5 `bd` behavior. *Rule:* every contract is verified
  against bd 1.0.5 and re-verified on a `bd version` bump; where the bundled plugin docs disagree,
  this skill wins (REQ-BEXTRA-DOC-001). *Why:* removed verbs (`bd gate approve`, bare `bd pour`)
  silently break scripts.

## 5. Verification

- The CLI contracts (REQ-BEXTRA-CLI-*) are verifiable by direct probes against an isolated DB:
  `bd --db /tmp/x create -t {decision,gate,event,molecule}` succeed and `-t bananafone` fails
  (REQ-BEXTRA-CLI-001); `bd gate --help` enumerates the verbs (REQ-BEXTRA-CLI-003);
  `bd dep add <epic> <task>` errors (REQ-BEXTRA-CLI-005); `bd mol pour … --json` shows
  `new_epic_id`/`id_mapping` and a two-bead gate (REQ-BEXTRA-CLI-007). The defensive-parse
  requirements are verifiable by feeding the documented multi-document/warning-prefixed output
  through the snippet and asserting the right record is extracted (REQ-BEXTRA-JSON-002). Each
  *(testable)* item is the anchor a later plan-010 Epic 6 integration test names.

## 6. References

- `skills/yf-beads-extra/SKILL.md`; `skills/yf-beads-extra/spec/cli.md`, `spec/json-and-scope.md`.
- `protocols/` — none (no companion rule).
- Root `SPEC.md` §4 (BEXTRA) and `GUARDRAILS.md`.
- Sibling specs: `yf-beads-authoring` (BAUTH), which **cites** these CLI contracts; the canonical
  `beads` skill (routine loop) and the plugin `resources/` (dependency/lifecycle taxonomy) this
  skill cites.
