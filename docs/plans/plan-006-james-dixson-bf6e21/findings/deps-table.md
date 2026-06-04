# Finalized per-skill frontmatter dependency table

Derived (Issue 1.2) by reading each `skills/<skill>/SKILL.md`, its `scripts/` (presence of
`*.py` → needs `uv`), and any `_SYSTEM_DEPS` map in its manager script. `depends-on-skill`
captures **genuine** in-repo dependencies (skills whose content/patterns the skill relies on),
not routing mentions ("use X instead for Y") in `SKILL.md` descriptions.

| Skill | skill-group | depends-on-tool | depends-on-skill | Evidence |
|-------|-------------|-----------------|------------------|----------|
| bdplan | beads | bd, uv, git | beads-extra, beads-authoring | `_SYSTEM_DEPS` hard set = git/uv/bd; "Reference skills" names beads-extra + beads-authoring as relied-upon (beads is external) |
| bdresearch | beads | bd, uv, git | beads-extra, beads-authoring | 6 py scripts → uv; bd-tracked; relies on beads-extra (CLI) + beads-authoring (coordinator) |
| beads-authoring | beads | bd | beads-extra | no scripts; conventions skill about `bd`; relies on beads-extra gotchas |
| beads-extra | beads | bd | _(none)_ | no scripts; base `bd` CLI layer; `beads` is external; other refs are routing |
| beads-upstream | beads | bd, uv, gh | beads-extra | py scripts → uv; default GitHub backend needs `gh`; relies on beads-extra |
| incubator | beads | uv | beads-extra | ships `incubator-index.py` → uv; files beads at promotion (soft, hence beads group); beads-extra for CLI patterns |
| optimal-instructions | utility | uv | skill-authoring | ships `manifest_update.py` → uv; token-efficiency ruleset single-source is skill-authoring |
| skill-authoring | utility | uv | _(none)_ | ships `manifest_update.py` → uv; base authoring skill; optimal-instructions refs are inbound routing, not a dep |

## Notes vs the plan's proposed table

- **incubator** `depends-on-tool` corrected from `_(none hard)_` → `[uv]`: it ships
  `incubator-index.py`, which runs via `uv`. Its `bd` need is soft (promotion only) and is
  expressed by group membership + the tie-break rule, not `depends-on-tool`.
- **beads-upstream** `depends-on-tool` finalized to `[bd, uv, gh]` (was `[bd]`): py scripts need
  `uv`; the default GitHub backend needs `gh`.
- **bdresearch** / **bdplan** `depends-on-skill` includes `beads-authoring` (coordinator
  conventions), not just `beads-extra`.
- The external `beads` marketplace skill is intentionally **never** listed under
  `depends-on-skill` (bare-names resolution would warn every run); the hard `bd` binary need is
  captured by `depends-on-tool`.

## Cross-group invariant (Success Criterion 7) — ASSERTED

Transitive `depends-on-skill` closure of the `utility` group:

```
optimal-instructions → {skill-authoring}
skill-authoring      → {}
closure(utility)     = {optimal-instructions, skill-authoring}
```

No `utility` skill (transitively) reaches a `beads` skill. **Invariant holds** → `--group
utility` is provably beads-free. (Installer Issue 2.3 re-checks this mechanically.)
