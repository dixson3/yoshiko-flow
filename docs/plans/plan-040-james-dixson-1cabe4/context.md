---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` is the source repository for a family of beads-backed Claude Code skills. This plan touches **three** of them: **`yf-beads-upstream`** (the upstream issue-tracker mirror) and
**`yf-plan`** (structured planning), and **`yf-beads-hygiene`**, which delegates its hoist step to `upstream.py` and so sits in the blast radius (Issue 3.3). Each lives under `skills/<name>/` as a `SKILL.md`, a
per-skill `SPEC.md` + `spec/*.md` requirement set, `agents/*.md` prompts, and `scripts/*.py`
helpers run via `uv run` with PEP 723 inline metadata.

Non-obvious properties a cold reader needs:

- **`yf-beads-upstream` mirrors beads to GitHub issues.** A bead's `external_ref` field holds the
  URL of its upstream issue and **is the entire mapping** — there is no sync table. That single
  fact is what makes this plan possible; see `findings/` and #133's Measurement 1.
- **`protocols/UPSTREAM_TRACKING.md` is hash-pinned** in `protocols/manifest.json`. Revising it
  without re-stamping the manifest is a preflight `rule_drift` failure in every consuming repo —
  see R3.
- **This repo is both source and consumer.** The installed skills at `~/.claude/skills/` are a
  separate artifact from `skills/` in the repo; see AGENTS.md "Syncing local `yf` to the repo".
- **SPEC-first is mandatory** (AGENTS.md): a behavior change lands as a `REQ-*` amendment plus an
  amendment-log entry *before* the implementation.
- **Upstream tracking is coarse**: one GitHub tracking issue per plan, not one per bead. That
  convention is precisely what makes coarse trackers invisible to `closable` (#131).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-16 -->

- `bd`: bd version 1.1.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.3 (507230998 2026-08-07 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.97.0 (2026-07-31)
- `glab`: glab 1.113.0 (d62881304)
- `claude`: 2.1.228 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-040-james-dixson-1cabe4`

## Operator identity

- Git user: `james-dixson` (james@yoshikostudios.com)
- Role: sole maintainer of the `yoshiko-flow` skill family; owns the `dixson3` GitHub org.
- Authority scope: full — may amend `SPEC.md`, edit skills, and open/close/comment on issues in
  `dixson3/yoshiko-flow`. The plan still gates outward-facing writes behind explicit confirmation
  by convention, not by permission limit.

## Runtime assumptions

- **OS / shell:** macOS (Darwin 25.5.0), `zsh`. `$HOME` is `/Users/james`.
- **Network:** required throughout — this plan's subject *is* the GitHub API. `gh` must be
  authenticated against `dixson3/yoshiko-flow`.
- **Credentials and scope:** an authenticated `gh` CLI with issue read/write. **No label-write
  scope is needed** — decision 5 was revised at review to **restrict-and-drop** (emit only labels
  that already exist), so the plan never creates a label. The earlier ensure-label-before-use
  option, which would have needed that scope, was dropped once EXP-001's affected population was
  corrected from ~45 beads to 3.
- **Outward-facing writes:** three classes, all gated — a scratch issue for the 1.1 label test;
  comments on #51/#52/#53/#111 and a close on #132 (5.2b); and operator-run `gh issue close`
  commands that 4.4 only *proposes*.
- **`bd`:** a healthy local beads DB, local-only (no Dolt remote). The live DB carries **991**
  beads, which is what makes EXP-002's N+1 observable — a small DB would hide it.
- **Scale dependency:** SC8's `closable` timing is measured against this 991-bead DB. On a
  substantially smaller DB the before/after difference will be less dramatic; the one-invocation
  invariant (4.2) is the scale-independent check and is the one that matters.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
