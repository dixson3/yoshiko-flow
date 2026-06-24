# beads-hygiene

Safe, read-only-first **audit** and gated **repair** of a beads (`bd`) dependency graph: finds
orphaned beads and dangling dependency edges, and classifies gate-typed edges by status so live
gates are never mistaken for dangling. Implements upstream #29.

It encodes the discipline learned from a real incident: an ad-hoc cleanup flagged **11 valid
live-gate edges as "dangling"** because `bd list` hides gate beads and truncates at 50 rows;
removing them would have un-gated 7 live beads. The fix is to resolve every edge target with
`bd show` (which sees gates) over the full universe, and classify gates by status.

## Prerequisites

| Tool | Version | Purpose |
| :--- | :--- | :--- |
| `bd` | >= 1.0.5 | the beads CLI being audited/repaired |
| `uv` | any | runs the `beads_hygiene.py` engine (PEP 723) |
| `git` | any | repo-root resolution |

Mirrors SKILL.md frontmatter `depends-on-tool: [bd, uv, git]`. Depends on `yf-beads-extra`
(direct-CLI gotchas) and `yf-beads-init` (DB-health routing).

## Usage

```
/yf-beads-hygiene
```

Or invoke the engine directly:

```bash
uv run scripts/beads_hygiene.py audit                 # read-only four-class report
uv run scripts/beads_hygiene.py audit --json          # machine-readable
uv run scripts/beads_hygiene.py repair                # dry run: list truly-dangling proposals
uv run scripts/beads_hygiene.py repair --apply --record removed.json   # mutate (prompts)
uv run scripts/beads_hygiene.py restore --record removed.json --apply  # round-trip undo
```

`audit` classifies every dependency edge into `true-orphan` / `truly-dangling` /
`satisfied-gate` / `live-gate`. Only `truly-dangling` is ever proposed for removal; `live-gate`
edges are always preserved. On a wedged/corrupted DB the engine exits with status `db_wedged`
and routes you to `yf-beads-init` (do not clean a broken store).

## Tests

```bash
cd scripts && uv run --with pytest python3 -m pytest test_beads_hygiene.py -q
```

The classifier core is pure, so the tests reproduce the #29 11-live-gate false positive without
a live DB.

## Layout

```
skills/yf-beads-hygiene/
├── SKILL.md                    # trigger contract, audit/repair/restore procedure
├── SPEC.md                     # REQ-HYG-* requirements
├── README.md                   # this file
└── scripts/
    ├── beads_hygiene.py        # PEP 723 engine: audit / repair / restore
    └── test_beads_hygiene.py   # four-class + #29 regression tests
```

## Install

Deployed by `yf skills install`, which auto-discovers every `skills/*/` by its `SKILL.md`
frontmatter.
