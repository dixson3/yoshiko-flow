# Upstream #15: Consolidate duplicated Python helpers across skills (PEP 723 shared package route)

- **Number:** 15
- **Title:** Consolidate duplicated Python helpers across skills (PEP 723 shared package route)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Context

The `shutil.which`-based tool-presence check is duplicated across at least three places:
`install.py`, `skills/bdplan/scripts/plan_manager.py` (`_SYSTEM_DEPS`), and
`skills/bdresearch/scripts/research_manager.py`. More broadly, each skill ships its own
`scripts/*.py` helpers (manifest updaters, JSON parsers, etc.) with overlapping logic. This
issue tracks if/how to consolidate.

## The real obstacle

Dependency *declaration* is already solved (plan-006 added `depends-on-skill` + transitive
install, so co-presence is guaranteed). The hard part is **runtime import resolution**: a
script at `~/.claude/skills/bdplan/scripts/...` has no stable path to a shared module, because
the install layout varies by surface (`.claude`/`.agents`), scope (`~/`/git-root), and
`--target`. Sibling-path `sys.path` hacks are brittle against all three. A "noop skill that
everything depends on" fixes co-location but **not** the import path — and it re-introduces the
cross-skill coupling that self-contained, independently-installable skills are designed to avoid.

## Options considered

1. **PEP 723 dependency on a micro-package (preferred long-term).** Extract shared helpers into
   a small package; each script declares it inline:
   ```python
   # /// script
   # dependencies = ["beads-skill-helpers @ git+https://github.com/dixson3/beads-skill-helpers"]
   # ///
   from beads_skill_helpers import missing_tools
   ```
   `uv run` resolves it per-script into an ephemeral venv — no sibling-path math, no
   install-topology coupling, works because it's fetched from git/PyPI not a neighbor dir.
   Cost: publish + version a package; first resolve hits the network (uv caches after).
   **This is the route to explore for consolidating the per-skill Python helpers generally**,
   not just the tool-check.

2. **Install-time vendoring from one in-repo source.** Canonical copy at `_shared/`, fanned out
   into each skill's `scripts/` by `install.py`/a build step. Single source of truth; per-skill
   copies are generated artifacts. Adds a sync step.

3. **Status quo (do nothing).** For the ~10-line tool-check specifically, duplication is cheaper
   than any sharing mechanism, and the logic is stable. Recommended until a *substantive* shared
   library actually emerges.

## Proposed direction

- Short term: leave the tool-check duplicated (below the threshold where sharing pays off).
- Long term: when consolidation is worth it, pursue **option 1 (PEP 723 git/PyPI package)** as
  the mechanism for sharing Python helpers across skills without coupling them to each other's
  on-disk location. Avoid the noop-skill / sibling-path approach.

Surfaced during plan-006 (#14).
