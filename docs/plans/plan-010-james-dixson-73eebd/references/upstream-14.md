# Upstream issue #14: Install groups: split beads vs utility skills via frontmatter contract + dependency-aware installer

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/14
- **State:** OPEN
- **Labels:** (none)
- **Disposition (plan-010):** supersede

## Body

Adds a per-skill `SKILL.md` frontmatter contract (`skill-group`, `depends-on-tool`, `depends-on-skill`) and a new `install.py` (wrapped by `install.sh` via `uv`) that computes install groups from frontmatter.

Users can now install the beads-free `utility` skills (`optimal-instructions`, `skill-authoring`) independently of the `bd`-dependent `beads` skills:

```bash
./install.sh --group utility   # only the beads-free skills
./install.sh --group beads     # only the bd-dependent skills
./install.sh --list-groups     # show computed groups + members
```

The installer resolves transitive in-repo skill deps, checks `depends-on-tool` (warn by default, `--strict` to block), and adds `--group`/`--list-groups`/`--dry-run`/`--strict` while preserving all existing flags. The group set is **computed** from frontmatter, so adding or regrouping a skill needs no installer edit.

Invariant enforced: no `utility` skill transitively depends on a `beads` skill, keeping `--group utility` provably beads-free.

Implemented via plan-006 (docs/plans/plan-006-james-dixson-bf6e21/).
