Title: lifecycle
Slug: lifecycle
Subtitle: install → preflight → invoke → coordinate/execute

A yoshiko-flow skill moves through the same five stages every time, whether it is a one-shot
markdown linter or a multi-session planning run. The shared `yf` kernel gates each skill
before it does any work.

![yoshiko-flow skill lifecycle](/images/lifecycle.png)

## 1. Install

```bash
yf skills install                # all skills + companion rules -> ~/.claude/skills (+ rules/)
yf skills install --group utility # just one group
yf skills install yf-plan        # a named skill (pulls its depends-on-skill closure)
```

`yf` copies the skill's tree to the resolved destination and its companion rules
(`protocols/*.md`) to the sibling `rules/` surface, then injects an integrity marker into the
deployed `SKILL.md`. See [install](/install/) for scope / surface / group options.

## 2. Preflight

Before a beads-backed skill runs, it routes through the shared kernel:

```bash
yf preflight yf-plan --json
```

The `status` field is authoritative:

- **`ok`** — proceed. Preflight also ensures any idempotent scaffold (gitignore anchors, state
  dirs) the skill needs.
- **`ignored`** — the operator opted this repo out (`ignore-skill` in the skill's
  `.yf-<skill>.local.json`).
- **`system_deps_missing` / `bd_not_initialized`** — a required tool (`git`, `uv`, `bd ≥ 1.1`)
  is absent, or beads is not initialized. Remediation is in the `instructions`.
- **`rule_missing` / `rule_drift` / `rule_deprecated`** — the skill's always-loaded companion
  rule is absent or has drifted from the version the skill expects; re-run the installer to
  restore it.

A red preflight is a **repair-and-re-run** loop, not a dead end: fix the reported cause, then
preflight again.

## 3. Invoke

Skills fire two ways:

- **User-invocable** skills are triggered explicitly: `/yf-plan build the auth service`,
  `/yf-research compare vector databases`, `/yf-markdown-lint report.md`.
- **Auto** skills fire from their `description` conditions when relevant work appears — e.g.
  `yf-drift-check` on an edit to a file its manifest tracks, or `yf-skill-authoring` when you
  edit a skill's `SKILL.md`.

## 4. Coordinate / execute

Beads-backed skills don't do their work inline — they build a **DAG of beads** and drive it to
completion:

- `/yf-plan` scopes → investigates → drafts → (after approval, in a fresh session) **executes**
  the plan in an isolated git **worktree**, then merges back and re-validates the merged state.
- `/yf-research` decomposes a topic into a retrieve → triangulate → synthesize → critique →
  refine → package pipeline, each phase a bead.

Because the state lives in beads, a crashed session **resumes**: the coordinator sweeps stuck
beads, re-attaches the worktree, and continues where it left off.

## 5. Land the plane

When the DAG drains, the skill lands its changes and pushes **open + deferred** beads upstream
to the issue tracker, so nothing tracked is lost when the local clone goes away. Plan
execution reconciles any incorporated upstream issues (closing or updating them per the plan's
dispositions).

## The whole loop, once

```bash
yf skills install                # 1. install
yf preflight yf-plan --json      # 2. preflight (status: ok)
# 3. invoke — in your agent:  /yf-plan <objective>
# 4. coordinate/execute — /yf-plan execute <plan-id> in a fresh session
# 5. land — push upstream + reconcile at completion
```
