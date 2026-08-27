Title: usage
Slug: usage
Subtitle: your first commands with yf and the skills

Once `yf` is installed and the skills are deployed ([install](/install/)), the skills run
inside your agent harness (Claude Code by default). Here are the paths you'll use most.

## Set up a project

```bash
yf harness skills install                # deploy the skills into ~/.claude/{skills,rules}
yf doctor                        # verify the toolchain + every install
```

`yf doctor` should report your `yf` version, `bd`/`uv`/`git` present, and each skill `ok`.

## yf-plan — structured, beads-tracked planning

`/yf-plan` replaces native plan mode with a scoped, reviewable, resumable pipeline whose work
is tracked in beads.

```text
/yf-plan build a rate limiter for the API      # scope -> investigate -> draft -> review
/yf-plan continue                              # resume an open plan
/yf-plan execute <plan-id>                     # (new session) run it in a git worktree
/yf-plan status                                # progress + parked plans
```

A plan is drafted and red-team reviewed, then — after you approve — **executed in an isolated
git worktree** in a fresh session, merged back, and re-validated against the merged tree before
anything is pushed. See [yf-plan](/skills/yf-plan/).

## yf-research — cited, resumable deep research

```text
/yf-research compare managed vector databases for RAG
/yf-research coordinate                        # (new session) run the pipeline to completion
/yf-research status
```

`/yf-research` decomposes a topic into a DAG of focused subtasks (retrieve → triangulate →
synthesize → critique → refine → package) and produces a structured, citation-backed report
with source-credibility scoring. See [yf-research](/skills/yf-research/).

## The beads loop

Beads-backed skills track their work in `bd`. The canonical loop, if you drive it directly:

```bash
bd ready --json                  # what's unblocked
bd update <id> --claim --json    # take a bead
# ... do the work ...
bd close <id> --reason "done"    # close it; dependents unblock
```

You rarely run these by hand during a skill run — the skill's coordinator drives the loop — but
`bd ready` / `bd show <id>` are handy for seeing where a plan or research project stands.

## Markdown + diagram tooling

The beads-free utility and markdown skills are one-shot:

```text
/yf-markdown-lint docs/report.md               # validate GFM: links, tables, no wiki-links
/yf-markdown-pdf docs/report.md                # render to PDF (pandoc + xelatex)
/yf-diagram-authoring                          # author a d2 diagram -> light-mode PNG
```

## Where to go next

- **[skills](/skills/)** — every skill, generated from its `SKILL.md`: what it does, when it
  fires, and when to skip it.
- **[lifecycle](/lifecycle/)** — the install → preflight → invoke → execute loop in detail.
- **[architecture](/architecture/)** — how the `yf` kernel, embedded skills, beads, and
  upstream tracking fit together.
