# Markdown Lint-on-Edit Trigger Protocol

Always-loaded firing surface for the `yf-markdown-lint` skill. The linter procedure,
the rule list (ML001–ML007), and the table conventions live in the skill's
`SKILL.md`; this rule binds only the on-edit trigger a `description` cannot
reliably fire. It is the **portable, cross-harness** equivalent of the optional
Claude-Code `FileChanged` hook documented in `SKILL.md` — use one, not both.

## On-edit trigger

After any create or modify of a `**/*.md` file, **if the repo has opted in** (a
`.markdown-lint-on-edit` marker file exists at the repo root), run the linter's
**authoring-time rule subset** over the changed file and resolve any violation in
the same pass:

```bash
uv run <skill-dir>/scripts/markdown_lint.py "<changed.md>" --rules ML001,ML002,ML005,ML006,ML007
```

The subset is the fast authoring rules — wiki-links (ML001), embeds (ML002),
malformed tables (ML005), empty links (ML006), bad delimiters (ML007). It
deliberately skips link/anchor resolution (ML003/ML004): those are a full link
audit (`/yf-markdown-lint` with no `--rules`), not an every-edit check. A non-empty
marker file may override the rule set (`--rules …` on its own line) or list
exclude globs; an empty marker means "use this default subset".

## Silent no-op

**Unless the repo has a `.markdown-lint-on-edit` marker at its root**, this
trigger is a **silent no-op** — do not lint, prompt, nag, or offer to create the
marker. Opt-in is explicit and per-repo, because "lint every markdown" is broad
reach; an always-on rule would fire on every `.md` edit in every repo where the
skill is installed.

## Scope boundary

yf-markdown-lint checks that a markdown file is valid GFM (links, embeds, tables).
It never authors, reformats, or rewrites prose, and never touches non-markdown
files. Cross-edge content agreement (docs ↔ spec ↔ implementation) is
`yf-drift-check`'s axis, not this one — the two may both fire on a `.md` edit on
orthogonal axes (GFM validity vs. cross-edge agreement).

For the rule list, table conventions, the migration helper, and the Claude-Code
`FileChanged` hook alternative, see the `yf-markdown-lint` `SKILL.md`.
