# incubator

Topic-scoped pause/resume for exploratory research in the vault's `Incubator/`
tree. The unit of pause/resume is the **topic**, not the session — sessions are
the wrong factoring for "walk away and pick up later," because resuming a
session is hard to reconstruct whereas a topic carries its own state.

An incubator is a directory (or single file) under `Incubator/` whose state file
holds frontmatter + a standard body, including a `## Resume` bookmark that lets a
cold reader (or another harness, on another machine) continue with no session
history. All state lives in vault files so it is portable across harnesses;
nothing is kept in session-only or Claude-only stores.

## Prerequisites

- `uv` — runs the `scripts/incubator-index.py` helper (PEP 723 inline deps).
- `beads-extra` skill — the incubation→build hand-off (`## Beads to file`) files beads via the
  `bd` CLI patterns that skill documents.

## Install

Installed by the repo-level `install.sh`, which auto-discovers every `skills/*/` directory and
closes over `depends-on-skill` (it pulls `beads-extra` transitively). No install changes needed.
See the project [README](../../README.md) for `install.sh` flags.

## Usage

User-invocable (`/incubator`). Subcommands:

```
/incubator new <name> [seed notes]   create, set active
/incubator fork <name>               fork current sidequest into a new incubator, set active
/incubator bookmark [notes]          rewrite active incubator's ## Resume + last_reviewed
/incubator resume <name>             load bookmark, set active
/incubator list                      index all incubators by state + staleness
/incubator touch <name>              bump last_reviewed only
```

Proactive sidequest detection (offer once to fork a tangent) also fires from natural-language
park/resume signals, driven from `AGENTS.md` (see below).

## What it does

- **new / fork** — spin up a fresh incubator mid-conversation, or fork a
  sidequest out of the current conversation so the tangent isn't lost.
- **bookmark** — write the `## Resume` block for the active topic on demand
  (explicit only: on a "walking away" signal or a phase boundary; there is no
  per-turn write and no Stop hook, by design — the trade-off is that a turn
  killed mid-write loses only that turn's delta).
- **resume** — reload a parked topic from its bookmark and named context files.
- **list** — `scripts/incubator-index.py` indexes the whole tree by state and
  staleness, tolerating pre-existing "unmanaged" incubators without mutating
  them; managed ones are retrofitted lazily when next actively worked.
- **touch** — bump `last_reviewed` for triage without a full resume.

Proactive sidequest detection (offer once to fork a tangent) is driven from
`AGENTS.md`, not this skill, so it fires even when the skill isn't pre-loaded.

## Schema rationale

The frontmatter and body contract were derived by surveying all ~36 existing
incubators and biasing toward the most active (bookpipe, gloak, yoshiko-flow):

- `status` is the maturity ladder actually used in the vault —
  `incubating → scoping → exploring → converging → concluded` — plus `parked`
  (deliberately paused) and `abandoned`. The earlier `active`/`blocked` values
  were invented and unused.
- `## Decision log` and `## Beads to file` are load-bearing in the active
  incubators: the decision log is a first-class append-only record, and "Beads
  to file" is the incubation→build hand-off (bead stubs ready for `bd create`),
  which ties into the project rule that follow-on work is filed as beads.
- `## Resume` is the one skill-owned addition. It consolidates into a single
  predictable block what the best existing resume artifact
  (`yoshiko-flow/routing-proxy-investigation.md`) scatters across "Next
  concrete steps" + "Beads to file" + "Open invitation."
- `last_reviewed` / `priority` exist only to drive the index's triage sort.

## Layout

- `SKILL.md` — instruction-only entry point (frontmatter trigger, invocation,
  schema as output contract, subcommand steps, constraints).
- `README.md` — this file.
- `scripts/incubator-index.py` — `uv` PEP-723 script; classifies managed vs
  unmanaged, sorts by priority then staleness, `--json` / `--write` options.
