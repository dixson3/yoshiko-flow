# Upstream Issue Triage: shared helpers audit json canonicalize

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #15 — Consolidate duplicated Python helpers across skills (PEP 723 shared package route)

> ## Context

The `shutil.which`-based tool-presence check is duplicated across at least three places:
`install.py`, `skills/bdplan/scripts/plan_manager.py` (`_SYSTEM_DEPS`), and
`skills/bdresearch/scri...

**Disposition:**
**Notes:**

## #36 — bdplan audit --json-output emits invalid JSON on control chars in findings
Labels: bug, priority::medium
> Migrated from local bead `beads-skills-3ma` (kept upstream until pulled via a plan).

`plan_manager.py audit --json-output` produced JSON with a raw control character (tab/newline) inside a finding st...

**Disposition:**
**Notes:**

## #39 — beads: auto-canonicalize yf projects on preflight/init (strip stray hooks, untrack runtime jsonl) — upstream sink is the only knob
Labels: enhancement, type::feature
> ## Summary

When a beads preflight runs — or `/yf-beads-init`, `/yf-beads-extra`,
`/yf-beads-upstream`, or `/yf-beads-hygiene` is invoked — yf-enabled repos should
be **canonicalized automatically** t...

**Disposition:**
**Notes:**
