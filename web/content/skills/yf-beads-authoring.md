A beads-backed skill is one that orchestrates its work through the `bd` issue
database — [`/yf-plan`](/skills/yf-plan/) and [`/yf-research`](/skills/yf-research/)
are the two in this repo. `yf-beads-authoring` is the design-rules layer you consult
while building or modifying one. It is not a runtime tool and you do not invoke it;
it fires while you author a `.formula.toml`, wire `bd mol pour` into a `SKILL.md`,
write a coordinator agent, or design crash-recovery for a re-invokable coordinator.
Routine `bd` CLI use routes to the canonical `beads` skill, and direct-CLI gotchas to
[`yf-beads-extra`](/skills/yf-beads-extra/); this skill owns only the conventions
layered on top of those.

## The two halves of a beads-backed skill

A beads-backed skill is built from two kinds of file that must not be conflated:

| File kind | Lives in | Defines |
| :-------- | :------- | :------ |
| beads formula (`.formula.toml`) | `formulas/` | *what work exists and how it connects* — the fixed DAG of steps, dependencies, and gates |
| agent file (markdown) | `agents/` | *how to execute* one step — its purpose, tools, and instructions |

The formula is poured into real beads with `bd mol pour`; agent instructions are
attached to each bead as metadata **after** the pour. A `[steps.metadata]` block in
the TOML is parsed but never propagated to the poured issues, so agent wiring always
happens post-pour via `bd update --metadata`.

**Right-size the formula.** A formula's `[[steps]]` encode only the stable, declared
shape — work that always exists at pour time and always wires the same way. Per-run
epics, fan-out, and runtime gates are injected after the pour, wiring in *beside* the
declared edges. The test is mechanical: if post-pour code has to rewrite or remove a
`needs=` edge the formula declared, the formula was wrong-sized. `/yf-plan`'s
`plan-execute` formula is minimal (just the start gate, because plans share no fixed
downstream shape); `/yf-research`'s is seven static steps that always exist, with
dynamic retrieve beads wired in at intake.

## Gate steps pour to two beads

A `type = "gate"` step does not pour to a single bead. It compiles to two, both
surfaced in the pour's `id_mapping`:

- `<formula>.<step-id>` — a **task wrapper** titled `Begin: …`. Downstream `needs`
  edges depend on this key.
- `<formula>.gate-<step-id>` — the **actual gate**. This is the key
  `bd gate resolve` targets.

Resolving the gate unblocks the wrapper, which the coordinator then closes, releasing
downstream work. Calling `bd gate resolve` on the wrapper key fails with
`… is not a gate issue (type=task)`. Validate any formula with
`bd mol pour <name> --dry-run` before wiring the full pipeline.

## The coordinator loop

The dispatch loop lives in `agents/coordinator.md` as a self-contained agent file, so
the `SKILL.md` stays focused on orchestration. Given an epic ID and a work directory,
the coordinator loops:

1. `bd ready --json` — find unblocked beads, filtered to this epic.
2. `bd update <id> --claim` — claim atomically.
3. `bd show <id> --json` — read the bead's metadata (parse defensively).
4. Read the agent file from `${SKILL_DIR}/${agent}`.
5. Read each `metadata.context` file from the work directory.
6. Spawn a subagent with the agent file as its instructions.
7. `bd close <id>` — mark complete.
8. Repeat until `bd ready` returns empty.

The loop terminates on `bd ready` being empty — **not** on the initial bead set
closing. A bead created mid-run with `--deps discovered-from:<parent>` re-enters the
loop once its predecessors close, so discovered work runs in the same session.

## The resilience envelope

A coordinator that can be re-invoked — after a crash, a session timeout, or the next
scheduled interval — needs a contract around the happy-path loop. `/yf-plan` is the
in-repo worked example.

- **Resume, never fork.** Before pouring an epic, check whether one already exists for
  this work unit. Detect via a durable pointer (the epic ID recorded in the skill's
  work artifact) with a metadata fallback (the epic stamped with its work directory at
  pour). Pouring a second epic forks progress.
- **Sweep stuck beads on resume.** A crash leaves beads `in_progress` or claimed, and
  the ready loop skips non-`open` beads, so they stall forever. Before the loop resets
  each stuck *durable* bead to `open` — never auto-close it. Resetting keeps the epic
  non-terminal, so a terminal gate cannot auto-fire on a resumed-but-incomplete run.
- **Report what you cannot classify.** A bead the sweep cannot positively classify —
  orphaned `discovered-from` work, `blocked` with no live blocker — is reported to the
  operator, never guessed. Vapor-phase (ephemeral) operational beads may be closed
  automatically; liquid-phase (durable) work beads may not.
- **Drain before reporting blocked gates.** Handle gate beads in place — resolve on
  pass, mark blocked on fail — but drain all unblocked work before reporting any
  blocked gate. Parallel work usually remains; do not halt at the first one.
- **Conservative git handoff.** The run is complete when `bd ready` is empty and no
  resettable stuck beads remain. Then resolve terminal gates, cascade-close every
  container in the tree bottom-up, and report the git handoff — proposed commit and
  push commands — rather than committing or pushing without explicit authority.

## The coordinate subcommand

A skill with multi-session handoff implements a `coordinate` subcommand so the
operator starts a fresh session and runs `/<skill> coordinate [<identifier>]`. With no
identifier, it queries `bd gate list --json` for open gates parented to this skill's
poured epics:

| Open gates | Action |
| :--------- | :----- |
| 0 | warn and exit — no pending work |
| 1 | auto-select, resolve, and begin |
| N | present options via `AskUserQuestion`, resolve the chosen gate, begin |

Each poured molecule has its own gate, so concurrent instances stay disambiguated.

## Reviewing a beads-backed skill

Every rule above is also an audit item. The skill ships `agents/reviewer.md`, a
read-only anti-patterns checklist that walks a skill's `SKILL.md`, `agents/*.md`,
`spec/*.md`, and `formulas/*.toml` and returns findings for you to apply. Run it after
authoring or modifying a beads-backed skill.
