A diagram is worth committing only if the reader can regenerate it. `yf-diagram-authoring`
authors diagrams as **d2** source and renders light-mode, white-background PNGs from it. The
`.d2` source always sits beside its `.png` render — never temp-and-discard. When a label is
wrong, you edit the source and re-render; you never hand-edit the image.

d2 is the single diagram engine for the toolchain, chosen over mermaid for cleaner syntax,
stronger auto-layout (elk), and a fully local, offline render path. Every call goes through one
wrapper, `scripts/render.py`, run via `uv run`, with fixed defaults: `--theme 0` (light, white
opaque background) and `--layout elk`.

## When it fires

The skill fires two ways:

- **You ask for it** — author, render, or regenerate a diagram.
- **A content-producing skill calls it** — [`/yf-plan`](/skills/yf-plan/),
  [`/yf-research`](/skills/yf-research/), and [`/yf-skill-authoring`](/skills/yf-skill-authoring/)
  generate a structural diagram for a plan, a research report, or a skill spec.

It stays out of non-diagram image work, mermaid-specific workflows, and any task that does not
produce a d2 diagram.

Diagram when structure is easier shown than described: more than two interacting components, a
lifecycle or state machine, a data model, a dependency or org graph. Skip trivial one- or
two-node relationships and pure prose. `/yf-plan` and `/yf-research` always attempt at least one
diagram for a non-trivial artifact; `/yf-skill-authoring` is conditional — a diagram only if it
aids the description.

## How it works

The workflow is four steps:

1. **Preflight.** `uv run scripts/render.py preflight` confirms `d2` is on your PATH — the only
   contract, and OS-independent. If it is missing, `brew install d2`. The first PNG render fetches
   a one-time Chromium (~140MB); preflight never probes that cache, because cache paths are
   OS-specific and probing them produces false negatives.
2. **Write `<slug>.d2`** into the caller's diagrams location. The slug is kebab-case, derived from
   the section or topic.
3. **Render** with `uv run scripts/render.py render <slug>.d2`. The PNG lands at the sibling path
   — the same name with a `.png` suffix — so the source is always next to the render.
4. **Verify by Read.** Open the PNG and check: white background, legible labels, correct
   structure. Fix the `.d2` and re-render on any problem.

The wrapper covers the whole surface: `preflight`, `render <file.d2>`, `render-dir <dir>`,
`check-dir <dir>`, and the inline-source round-trip `embed` / `lift` / `inline`. Every
subcommand accepts `--json` for machine-readable output.

## Where renders go

The skill hardcodes no destination. It renders beside the `.d2` you give it, wherever that is,
and each consumer sets its own convention:

| Consumer | Location | Referenced from |
| :-- | :-- | :-- |
| `/yf-plan` (plans) | `<plan_dir>/diagrams/<slug>.{d2,png}` | `plan.md` |
| `/yf-research` (reports) | `<research_dir>/diagrams/<slug>.{d2,png}` | report body |
| `/yf-skill-authoring` (specs) | `skills/<name>/spec/<slug>.{d2,png}` | skill `README.md` |
| top-level docs | `<repo-root>/docs/diagrams/<slug>.{d2,png}` | project `README.md` |
| standalone | `./diagrams/` (override freely) | — |

Reference a render with a **relative** markdown image path so it survives a skill install:
`![<alt>](spec/<slug>.png)` from a skill README, `![<alt>](docs/diagrams/<slug>.png)` from a
top-level doc.

**Placement test.** Put a diagram in `skills/<name>/spec/` only if it documents the skill itself
— its engine or model, repo-agnostic, shipped with the skill. A diagram of a specific repo's
content or config is repo-level and belongs in `docs/diagrams/`. One trap: the
[`yf-drift-check`](/skills/yf-drift-check/) skill and a repo's `DRIFT-CHECK.md` manifest share a
name, so a diagram of a repo's `DRIFT-CHECK.md` graph reads as "drift-check" but is repo config
— `docs/diagrams/`, not `skills/yf-drift-check/spec/`.

## Inline source vs standalone render

A d2 diagram can live in a markdown doc two ways, and the pair round-trips — the source survives
the move unchanged:

| Representation | What it is | Pro | Con |
| :-- | :-- | :-- | :-- |
| Inline fence | a ` ```d2 ` block carrying the source verbatim, rendered at preview or PDF time by [`yf-markdown-pdf`](/skills/yf-markdown-pdf/) | one file, no committed binary, edit in place | needs a render step to view |
| Standalone | a committed `.d2` plus rendered `.png`, referenced by `![alt](slug.png)` | previews anywhere with no render step | a committed binary plus regeneration discipline |

Three subcommands move a diagram between them:

- **`embed <src.d2> <tgt.md>`** inserts the source as an inline ` ```d2 ` fence — appended by
  default, or after the first line matching `--anchor <text>`. Source comes from a `.d2` file or
  stdin (`-`).
- **`lift <tgt.md>`** extracts the first inline ` ```d2 ` block to a standalone `.d2`, renders its
  sibling `.png`, and replaces the fence with an image link. If `d2` is absent it still writes the
  `.d2` and replaces the fence — only the `.png` is skipped.
- **`inline <tgt.md>`** is the inverse: it replaces the first `![](*.png)` link whose sibling
  `.d2` exists with an inline fence carrying that source.

## Regeneration discipline

A `.d2` edited without a re-render leaves a stale `.png`. Before you commit, regenerate all
renders under a tree with `render-dir <dir>`, then run `check-dir <dir>`:

- **Authoritative on orphans** — exit 1 when any `.d2` has no matching `.png`.
- **Advisory on staleness** — a WARN when a `.d2` is newer than its `.png`, never a failure.
  Cross-clone freshness can't be enforced, because a git checkout normalizes mtimes and a fresh
  clone cannot tell stale from current.

## d2 authoring notes

- **Line breaks in labels** — d2 renders `\n` inside a quoted label as a newline
  (`node: "First line\nSecond line"`). Do not use mermaid's `<br/>`.
- **Rich labels** — markdown blocks (`node: |md **Bold**\n- point |`) carry multi-line or styled
  text.
- **Layout** — d2 auto-layouts; there is no fixed width or height. Prefer `elk` for dense or
  nested graphs and `--layout dagre` for simple left-to-right flows. `direction: right|down|left|up`
  sets flow direction.
- **Theme** — theme `0` is light with a guaranteed-opaque white background. Keep it.
