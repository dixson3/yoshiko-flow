---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #40: PEP-723 micro-package route for shared Python helpers (longer-term alternative to _shared/ vendoring)

- **Number:** 40
- **Title:** PEP-723 micro-package route for shared Python helpers (longer-term alternative to _shared/ vendoring)
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement

## Body

## Summary

Longer-term alternative to the in-repo `_shared/` vendoring pattern (plan-014, extended by the #15 broader sweep) for consolidating duplicated Python helpers across yf skills: publish shared helpers as a versioned **PEP-723 micro-package** that each script declares inline, so `uv run` resolves it per-script into an ephemeral venv.

```python
# /// script
# dependencies = ["beads-skill-helpers @ git+https://github.com/dixson3/beads-skill-helpers"]
# ///
from beads_skill_helpers import missing_tools
```

## Why this is filed separately

#15 (PEP-723 shared package route) is being addressed in a near-term plan via the **established `_shared/` in-repo vendoring** pattern (option 2: canonical source + `sync.py` regeneration + DRIFT-CHECK edge) — chosen for consistency with plan-014, offline operation, and no publish/versioning overhead. This issue captures the **PEP-723 micro-package route (option 1)** as a deliberate, deferred enhancement so the decision is recorded rather than lost.

## The obstacle it solves

The hard part of cross-skill sharing is **runtime import resolution**: a script installed at `~/.claude/skills/<skill>/scripts/...` has no stable path to a sibling shared module (install layout varies by surface `.claude`/`.agents`, scope `~/`/git-root, and `--target`). Vendoring sidesteps this by copying canonical text into each consumer. PEP-723 sidesteps it differently — the helper is fetched from git/PyPI, not a neighbor dir — at the cost of publishing + versioning a package and a first-resolve network hit (uv caches after).

## Relationship to the operator's yf-owned-asset direction

The operator's stated long-term preference is to keep shared content in a **yf-owned asset directory** rather than the harness-native skills folders. PEP-723 is one way to get shared content *out* of skill dirs (it lives in an external package); a `yf`-embedded/served asset path is another. Both are alternatives to vendoring-into-skills and should be weighed together when this is picked up.

## Acceptance (when revisited)

- Decide package home (git repo vs PyPI), naming, and versioning policy.
- Prototype one helper (e.g. the `missing_tools` tool-presence check) as the package + inline PEP-723 dep; measure cold-resolve cost.
- Compare against the `_shared/` vendoring end-state shipped for #15.

Spun out of #15 during plan-016 scoping.
