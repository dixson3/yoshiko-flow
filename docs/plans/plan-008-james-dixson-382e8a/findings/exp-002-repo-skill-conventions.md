# EXP-002 — repo conventions for a new standalone utility skill

**Question:** What conventions must a new `diagram-authoring` skill follow to conform to
this repo (frontmatter, install groups, helper scripts, layout, drift-check)?

## Findings

### Frontmatter contract (utility skills)
Required keys (per `skills/optimal-instructions`, `skills/drift-check`):
`name`, `description` (TRIGGER/SKIP narrative), `user-invocable` (bool),
`skill-group` (`utility`), `depends-on-tool` (list of CLI tools),
`depends-on-skill` (list of in-repo skills), `allowed-tools`, `title`, `created`, `tags`.

→ diagram-authoring: `skill-group: utility`, `depends-on-tool: [d2, ...rasterizer]`,
`user-invocable: true` (operator should be able to call it directly to render a diagram),
`depends-on-skill: []`.

### Install / dependency contract (`install.py`)
Reads `skill-group`, `depends-on-tool`, `depends-on-skill`. `depends-on-skill` forms a
directed graph; transitive closure pulls dependencies in. **No "soft dependency" concept
exists** — all `depends-on-skill` edges are hard. → A Phase-2 "soft" dependency from
bdplan/bdresearch on diagram-authoring should therefore be expressed as **instruction-level
guidance** (planner/agent prose pointing at the skill with when-to-diagram heuristics),
NOT as a `depends-on-skill` edge (which would force-install diagram-authoring whenever
bdplan installs). Optionally diagram-authoring is co-installed by being in the same group.

### Helper script convention
`skills/<name>/scripts/*.py`, PEP 723 inline deps, shebang `#!/usr/bin/env -S uv run --script`,
invoked `uv run ${SKILL_DIR}/scripts/<x>.py <subcommand> --json`, real argparse/click.
Threshold ~25 lines of logic. → A small `render.py` (preflight + path-selection +
white-bg flag assembly + .d2/.png naming + regenerate) is justified.

### Layout
`SKILL.md` + `README.md` required. Optional `scripts/`, `agents/`, `spec/`, `reference/`,
`protocols/` (+ `manifest.json` for always-loaded companion rules with hash tracking).

### Drift-check
`DRIFT-CHECK.md` covers new skills automatically via `skills/*/SKILL.md`, `skills/*/README.md`,
`skills/*/scripts/*.{sh,py}` globs — no manifest edit needed for basic coverage. README must
mirror SKILL.md frontmatter `depends-on-tool` (e-readme-prereqs) and file layout
(e-readme-layout); the repo README index table lists each skill (e-index-table).
