# SPEC — Incubator (`yf-incubator`)

> **Status: DRAFT (primed).** Per-skill SPEC for the incubator skill (currently `incubator`,
> renamed to `yf-incubator` per root `SPEC.md` §3.8). Operator to review/edit. Composed by the
> root macro `SPEC.md` §4 under spec key **INCUB**. The output contracts (frontmatter, body
> sections) live verbatim in `SKILL.md`; this layer references them rather than restating them.

## 1. Purpose & scope

`yf-incubator` manages long-lived research topics ("incubators") under `Incubator/`: it creates,
forks, bookmarks, resumes, and triages them so a topic can be parked mid-conversation and a cold
reader can pick it back up from the folder alone. Each incubator is a portable, frontmatter-keyed
markdown state file; the skill never stores state in session-only or Claude-only stores. It is a
`user-invocable: true` utility skill with no companion rule.

**In scope:** the `new`/`fork`/`bookmark`/`resume`/`list`/`touch` subcommands, the incubator
state schema (frontmatter + ordered body sections), proactive sidequest detection, and the
indexer that triages `Incubator/` by status/priority/staleness.

**Out of scope:** beads-tracked multi-step build planning (that is `yf-plan`); filing the actual
beads from `## Beads to file` (that hands off to `yf-beads` / `yf-beads-extra`); routine note
edits with no park/resume intent.

## 2. Requirements (`REQ-INCUB-NNN`)

### 2.1 State schema (output contract; see `SKILL.md` "State schema")

- **REQ-INCUB-001** *(testable)* an incubator state file shall be either directory form
  (`Incubator/<kebab>/README.md`, with `research/`/`references/`/`plans/` alongside) or
  single-file form (`Incubator/<kebab>.md`); single-file is promoted to directory form when it
  gains `research/` or a `## Resume`.
- **REQ-INCUB-002** *(testable)* the state file frontmatter shall carry `title`, `created`,
  `tags`, `status`, `last_reviewed`, `priority`, and `aliases`; `status` is one of
  `incubating | scoping | exploring | converging | concluded | parked | abandoned` and
  `priority` is one of `high | normal | low`.
- **REQ-INCUB-003** the body shall contain, in order, the verbatim sections `## Resume`,
  `## Status`, `## Premise`, `## Open questions`, `## Decision log`, `## Files`, and
  `## Beads to file`; `## Decision log` and `## Beads to file` are never dropped (they may be
  empty).
- **REQ-INCUB-004** `## Resume` shall let a cold reader resume with no session history — concrete
  next action plus the exact files to re-read under "Context to reload".

### 2.2 Subcommands (see `SKILL.md` "Subcommands")

- **REQ-INCUB-010** *(testable)* `new` and `fork` shall resolve `<name>` → kebab, write all
  standard body sections, set `created = last_reviewed = today` and `status: incubating`, and
  report the path; `fork` additionally records in `## Status` the originating main topic, why it
  was forked, and context produced so far.
- **REQ-INCUB-011** *(testable)* `bookmark` shall rewrite the active incubator's `## Resume` and
  set `last_reviewed: today`, firing only on departure signals or a phase boundary — never every
  turn and never via a hook.
- **REQ-INCUB-012** *(testable)* `resume` shall read `## Resume` + frontmatter, re-read the files
  named under "Context to reload", set `last_reviewed: today`, and restore a working status
  (default `exploring`) when the incubator was `parked`.
- **REQ-INCUB-013** *(testable)* `touch` shall set `last_reviewed: today` on the named state file
  and change nothing else.
- **REQ-INCUB-014** *(testable)* `list` shall index `Incubator/` via the indexer script,
  tolerate unmanaged incubators (list, never mutate), and optionally regenerate
  `Incubator/INDEX.md` (`--write`) or emit machine output (`--json`).

### 2.3 Indexer (see `scripts/incubator-index.py`)

- **REQ-INCUB-020** *(testable)* the indexer shall classify an entry **managed** only when its
  state-file frontmatter carries both `status` and `last_reviewed`; everything else is
  **unmanaged** (listed with a reason, never mutated).
- **REQ-INCUB-021** *(testable)* managed incubators shall sort by priority rank
  (`high < normal < low`) then stalest-first within a band (unparseable `last_reviewed` dates
  sort last); unmanaged shall sort by file mtime, stalest first.

### 2.4 Proactive behavior & dependency

- **REQ-INCUB-030** when a conversation descends into a substantive tangent off its main topic,
  the skill shall offer **once** to fork it into an incubator and proceed only on confirmation
  (one offer per tangent).
- **REQ-INCUB-031** the incubation→build hand-off shall route `## Beads to file` stubs to the
  beads skills (`bd create`, deps via `bd dep add` per `yf-beads-extra`) or to `yf-plan` for a
  full plan/execute DAG; the stubs stay human-readable until then. This skill `depends-on-skill:
  beads-extra`.

## 3. Interfaces

- **CLI / scripts:** `scripts/incubator-index.py` — `collect` (managed vs unmanaged split),
  `sort_managed` (priority then staleness), `render_text`; flags `--root` (default `Incubator`),
  `--json`, `--write` (regenerate `Incubator/INDEX.md`). No other scripts.
- **Companion rule:** none — `yf-incubator` is `user-invocable: true` and binds no always-loaded
  trigger contract.
- **Config / state:** no `.local.json` operator config and no `.yf/` runtime state today; all
  durable state is the per-incubator markdown under `Incubator/`. If preflight/config under the
  macro kernel (`REQ-YF-PRE-*`) later applies, it would use `.yf-incubator.local.json` /
  `.yf/yf-incubator/`, with legacy paths migrated via macro `REQ-YF-MIGRATE-001`.

## 4. Guardrails (`GR-INCUB-NNN`)

- **GR-INCUB-001** *Drift:* using incubators as the task tracker for multi-step builds. *Rule:*
  incubation→build hands off to `bd`/`yf-plan` (REQ-INCUB-031); incubators hold research state,
  not the execution DAG. *Why:* one durable task system (beads), one research-parking surface.
- **GR-INCUB-002** *Drift:* bulk-migrating or rewriting unmanaged incubators on `list`. *Rule:*
  the indexer lists unmanaged entries with a reason and never mutates them; retrofit happens only
  as part of actively working an incubator (REQ-INCUB-020). *Why:* non-destructive triage.
- **GR-INCUB-003** *Drift:* per-turn or hook-driven bookmarking. *Rule:* `bookmark` fires only on
  departure signals or phase boundaries (REQ-INCUB-011). *Why:* avoid churn and surprise writes.
- **GR-INCUB-004** *Drift:* Claude-only / session-only state. *Rule:* all state lives in vault
  files under `Incubator/`; instruction changes go to `AGENTS.md`, never `CLAUDE.md`. *Why:*
  cross-harness portability.

## 5. Verification

- The schema requirements (REQ-INCUB-001..004) are checked by reading a generated incubator and
  asserting frontmatter keys, the `status`/`priority` enums, and the ordered body sections
  (`## Decision log` / `## Beads to file` present). The indexer requirements (REQ-INCUB-020/021)
  are unit-testable directly against `incubator-index.py` (`collect`/`sort_managed`) over a
  fixture `Incubator/` tree mixing managed and unmanaged entries, asserting the priority-then-
  staleness order and that unmanaged entries are reported but unmodified. Subcommand behaviors
  (REQ-INCUB-010..014) map to plan-010 Epic 6 integration tests naming the REQ id.

## 6. References

- `skills/incubator/SKILL.md` (invocation, state schema, subcommands, proactive detection).
- `skills/incubator/scripts/incubator-index.py` (managed/unmanaged classification + sort).
- Root `SPEC.md` §4 (INCUB), §3.8 (rename), §3.9 (`REQ-YF-MIGRATE-001`), and `GUARDRAILS.md`.
