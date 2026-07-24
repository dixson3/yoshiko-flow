Project instruction files load on every turn, so waste in them is paid repeatedly.
`yf-optimal-instructions` is an on-write optimizer for those files. When a project-root
`CLAUDE.md`, `AGENTS.md`, `AGENTS/*`, or repo-root `.{claude,agents}/rules/*` file changes, it
reads the file, auto-applies token-efficiency cuts, proposes a structural relocation, and reports
what it changed.

It splits its work by risk. Token cuts are low-risk and reversible, so they apply automatically.
Structural moves relocate operator-authored governance between files, so they are proposed and wait
for your confirmation. Nothing is ever deleted — structure only moves.

## When it fires

The skill is `user-invocable: false`. It fires on create or modify of a **project-root**
instruction file: `CLAUDE.md`, `AGENTS.md`, an `AGENTS/*` rule, or a repo-root
`.{claude,agents}/rules/*` file, in either the `.claude` or `.agents` surface.

It stops at the skill-directory boundary. Instruction files inside a skill directory under
`.{claude,agents}/skills/<skill>/` — a skill's `SKILL.md`, its `agents/*.md`, its own rules — route
to [`yf-skill-authoring`](/skills/yf-skill-authoring/). If the changed path is inside a skill dir,
this skill stops and defers. It also ignores application code, end-user docs, and notes.

Triggering is best-effort: a description-only skill registers no hook and cannot guarantee it runs
on every write. That is why it ships an always-loaded companion rule, `INSTRUCTIONS.md`, as the
backstop — a thin, pointer-only rule stating the on-write token-efficiency obligation, not a second
trigger mechanism.

## Two bodies of knowledge

The skill applies two distinct rulesets, and it owns exactly one of them:

- **K1 — token efficiency.** Cut narrative, keep templates and constraints and command blocks,
  extract scripts. The single source of truth is [`yf-skill-authoring`](/skills/yf-skill-authoring/)'s
  "Token efficiency" section. This skill **cites** that anchor and never restates the ruleset —
  duplicating it is the exact anti-pattern the skill exists to prevent.
- **K2 — instruction-file structure.** `AGENTS.md` is the primary, cross-harness surface.
  `CLAUDE.md` is a thin `@-include` index pointing at `AGENTS.md` and the rules subdir, plus only
  Claude-specific essentials with no portable home. Behavioral rules live in the project's rules
  subdir, one concern per file. This structural convention is owned here.

## The split-apply contract

The optimizer dispatches an apply agent and acts on what it returns:

1. **K1 edits — auto-apply.** Token-efficiency cuts are written without confirmation. They are
   low-risk and reversible.
2. **K2 proposal — propose and confirm.** The structural relocation is presented to you. It is
   written only after you explicitly confirm.
3. **Relocate, never delete.** K2 content moves between files and never disappears. Every
   relocation appears in the operator-visible change report — content the agent might misread as
   narrative can encode a behavioral constraint, so demoting or dropping it silently is off the
   table.
4. **Change report.** The skill surfaces what it did: K1 applied, and K2 proposed, applied, or
   declined.

Running on an already-optimized file is a **no-op** — an empty K1 edit set and no K2 proposal.
Idempotency is required, not incidental: an on-write skill re-processes its own output on the next
write, so a second pass must find nothing to do.

## Surface detection

A project's behavioral-rules subdir takes one of three forms — `AGENTS/*`, `.agents/rules/*`, or
`.claude/rules/*`. The skill detects which the project uses and normalizes relocations to **that**
surface; it never imposes one. If the changed file is itself under a rules surface, that surface
wins. A project may carry both a `.claude` and a `.agents` surface, one often symlinked into the
other, so the skill picks the changed file's own surface — relocations stay where the operator is
editing.

## Scope versus yf-skill-authoring

The two skills partition the instruction-file space cleanly on a single axis: this skill owns
**project-root** instruction files; `yf-skill-authoring` owns **skill-dir** ones. Their
`description` triggers are mutually exclusive on exactly that split. The K1 token-efficiency ruleset
is single-sourced in `yf-skill-authoring`; the K2 structural convention is single-sourced here; each
references the other, and neither restates the other's body.
