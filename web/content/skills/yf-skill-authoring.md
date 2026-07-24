Skills accumulate divergent init, config, state, and hook patterns the moment more than one of
them ships. `yf-skill-authoring` is the conventions reference that keeps them from diverging. It
covers directory layout, the inline-vs-script threshold, modularization, the token-efficient
writing ruleset, the Skill Surface Convention, Python helper discipline, the canonical agent-role
vocabulary, and the read-only review sequence.

It is the **single source of truth for the token-efficiency ruleset** — the Cut / Keep / Extract
rules other skills reference rather than restate — and it owns skill-dir instruction files.

## When it fires

The skill is `user-invocable: false`. It is a conventions reference, applied when you author
skill-dir content:

- **Creating or editing a skill** under `.{claude,agents}/skills/*`, in the user (`~/`) or project
  (`<git-root>/`) scope.
- **Authoring a skill's `SKILL.md`** or agent prompt content, or scaffolding agents.
- **Writing a `.py` helper** under a skill dir to run via `uv run`, or adding PEP 723 inline
  metadata.

It stops at two boundaries. **Project-root** instruction files — `CLAUDE.md`, `AGENTS.md`,
`AGENTS/*` not inside a skill dir — route to
[`yf-optimal-instructions`](/skills/yf-optimal-instructions/). And it does not cover application
code outside skills, end-user docs, or a skill's design-level planning. The distinguishing axis is
one line: this skill owns skill-dir instruction files; `yf-optimal-instructions` owns project-root
ones.

## Layout and thresholds

A skill roots at `.{claude,agents}/skills/<skill>/` with `SKILL.md` as the entry point and helpers
adjacent to it. The script threshold decides what stays inline and what becomes a file:

- Inline glue and one-off snippets stay inline.
- A script over ~25 lines, or reused, moves to a file under the skill dir.
- Logic over ~200 lines factors into modules adjacent to `SKILL.md`.
- CLI entrypoints use a real argument parser — `click`, `typer`, or stdlib `argparse` — never
  ad-hoc `sys.argv` slicing.

## Token efficiency

Always-loaded context — `SKILL.md`, `CLAUDE.md`, `AGENTS.md`, `.{claude,agents}/rules/*` — must
stay tight, because it is paid on every turn. The ruleset is Cut / Keep / Extract:

| Rule | What it governs |
| :-- | :-- |
| **Cut** | narrative intros and "Purpose" sections, soft guidance ("be thorough", "consider"), bash comments that restate the command, decorative ASCII, repeated cross-references, and legacy code fenced as "reference" — trust git history |
| **Keep** | literal templates the skill writes verbatim, commands the model executes verbatim, behavioral constraints that prevent wrong actions, edge-case rules, state-transition conditions, and agent output structures |
| **Extract** | JSON-parsing bash to a `scripts/` script, one-phase behavior over ~15 lines to an `agents/<name>.md`, and shared prerequisites or phase models to one referenced file |

This ruleset is single-sourced here; [`yf-optimal-instructions`](/skills/yf-optimal-instructions/)
cites it for its K1 pass. The *structural* project-root convention — AGENTS.md primary, CLAUDE.md a
thin `@-include` index — is owned there, not here.

## The Skill Surface Convention

Skills that install companion rules, store config and state, or register hooks adopt one shape.
The convention is a seven-point contract, adopted whole or not at all — implementing only some
points produces drift the preflight audit can't recover from:

1. **Companion rules** sourced from `protocols/<NAME>.md`, installed by the repo installer to the
   scope-and-surface rules dir. Never written to `AGENTS/`; never editing `CLAUDE.md`.
2. **A hash manifest** (`protocols/manifest.json`) preflight checks the installed rule against,
   with six defined outcomes. An unknown `schema_version` makes preflight FAIL.
3. **Config files** at canonical `.yf/<short>/config.local.json`, with the legacy root dotfile read
   only as a fallback. Config is operator decisions; state is not config.
4. **Runtime state** under `.yf/<short>/` only — never under the skill source dir, never under
   `.{claude,agents}/`.
5. **Hook installation** declared in `hooks/manifest.json` and merged idempotently by `<skill> init`.
6. **Gitignore stewardship** — a single anchored `/.yf/` entry, ensured by preflight, not just init.
7. **The preflight contract** — it both checks (deps, rule hash, config, hooks) and ensures the
   idempotent scaffold, additively and reported; `yf migrate`, not preflight, moves legacy paths.

## Python helpers

Skill helpers in Python follow the toolchain rules on top of the structure and token rules:

- Run scripts via `uv run`. Never call `python` / `python3` directly, and never activate a
  virtualenv by hand.
- Single-file helpers declare dependencies inline with PEP 723 (`# /// script ... ///`). Escape to
  an explicit `uv venv` plus `requirements.txt` inside the skill dir only when the dep count passes
  ~10 or specific pins matter.
- Helpers that persist runtime state write to `.yf/<short>/`, resolved from a caller-supplied
  `project_root` — never a hardcoded cwd, never the read-only skill source tree.

## Agent roles and review

Every agent in a multi-agent skill maps to exactly one of six canonical roles — **GATHER, PRODUCE,
EVALUATE, REVISE, ORCHESTRATE, CLOSEOUT** — and carries a front-matter block declaring it. EVALUATE
agents also carry a `stance`: `reviewer` for conformance, `red-team` for adversarial. The bead-DAG
driver is always `coordinator`.

The review sequence is three read-only agents, all dispatched via the Agent tool, with the caller
applying every fix:

1. **`reviewer`** — general skill review: structure, token efficiency, trigger quality, scope,
   design, portability.
2. **`reviewer-tokens`** — token-efficiency review of skill-dir instruction files, returning ranked
   findings and suggested edits.
3. **`red-team`** — an adversarial check: what the skill misses, where it overcommits, which
   assumptions break.

For Python helpers, also run `reviewer-python` for a toolchain and design critique.

## Markdown and diagrams

Every markdown file a skill ships — `SKILL.md`, `agents/*.md`, `README.md`, `spec/*.md`,
`reference/*.md` — is plain **GFM**: no Obsidian `[[wikilinks]]` or `![[embeds]]`, GFM links and
tables with explicit alignment markers only. Every authored or edited `.md` is linted with the
[`yf-markdown-lint`](/skills/yf-markdown-lint/) authoring subset (`ML001,ML002,ML005,ML006,ML007,ML008`)
and every violation resolved before the skill is done. That lint gate is part of the review
sequence, not optional.

When a diagram aids a skill's spec — a non-trivial architecture, pipeline, state machine, or edge
graph — author it with [`yf-diagram-authoring`](/skills/yf-diagram-authoring/), co-resident at
`skills/<name>/spec/<slug>.{d2,png}`, referenced from the README by relative path. This is
conditional, not always-attempt: there is no `depends-on-skill` edge, and it degrades to prose if
`d2` is absent.
