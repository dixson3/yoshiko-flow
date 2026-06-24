# Upstream Issue Triage: yf doctor, suppress bd-init cruft, yf-beads-hygiene skill, recommended settings.json baseline docs

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #31 — yf-beads-init: suppress bd-init instruction/hook cruft (AGENTS.md/CLAUDE.md beads boilerplate, .agents/.codex, git hooks)

> ## Problem

When standing up a fresh repo, `bd init` (beads) injects a pile of artifacts that conflict with our conventions, requiring manual cleanup every time. Observed on a fresh `dixson3/gws-skill...

**Disposition:**
**Notes:**

## #32 — Add `yf doctor` subcommand to validate presence of `beads` and `uv`

> ## Context

The `dixson3/tap/yf` Homebrew formula previously declared hard `depends_on "beads"` and `depends_on "uv"`. These were removed so the formula no longer forces a brew-managed install of eith...

**Disposition:**
**Notes:**

## #29 — Add yf-beads-hygiene skill: safe orphan/dangling-edge cleanup for beads
Labels: enhancement
> ## Summary

Add a new skill **`yf-beads-hygiene`** that safely audits and cleans up a beads
DB — orphaned beads, dangling dependency edges, and stale/wedged state — and is
the canonical trigger for an...

**Disposition:**
**Notes:**

## #30 — Document recommended Claude settings.json baseline for yoshiko-flow skills
Labels: documentation, enhancement
> ## Summary

Document a recommended Claude Code `settings.json` baseline that materially
improves how the yoshiko-flow (`yf-*`) skills behave. Several skill contracts
assume the operator has *turned of...

**Disposition:**
**Notes:**
