# Installer verification (Issue 2.3)

All checks run against `install.py` via `uv run` (and the `install.sh` wrapper).

| Check | Command | Result |
|-------|---------|--------|
| Group computation | `--list-groups` | `beads` (6) + `utility` (2), computed from frontmatter ✓ |
| Utility group is beads-free (SC2/SC7) | `--group utility --dry-run` | exactly `optimal-instructions, skill-authoring`; no beads skill ✓ |
| Beads group | `--group beads --dry-run` | the 6 beads skills ✓ |
| Transitive closure | `bdplan --dry-run` | pulls `beads-authoring, beads-extra` ✓ |
| Explicit-name override | `skill-authoring --group beads --dry-run` | installs only `skill-authoring` + note "ignoring --group" ✓ |
| Warn path exit code | `--group beads --dry-run` (bd/gh off PATH) | warns, **exit 0** ✓ |
| Strict path exit code | `--group beads --strict --dry-run` (bd/gh off PATH) | aborts, no install, **exit 2** ✓ |
| Strict, all present | `--group beads --strict --dry-run` (full PATH) | **exit 0** ✓ |
| `--group` under explicit `--target` | `--group utility --target <tmp>` | filters to 2 utility skills at the chosen target; `INSTRUCTIONS.md` surfaced to sibling `rules/` ✓ |
| Companion-rule install | (same) | `optimal-instructions/protocols/INSTRUCTIONS.md` → `<target>/../rules/INSTRUCTIONS.md` ✓ |
| Post-edit load check (SC5) | default `--target <tmp>` | all 8 skills copied; every installed dir has a valid `SKILL.md` ✓ |
| Wrapper parity | `./install.sh --help` / `--list-groups` | identical output via `uv run install.py` ✓ |

Cross-group invariant (Success Criterion 7) confirmed mechanically: `--group utility` resolves
to `{optimal-instructions, skill-authoring}` with no beads skill pulled by the transitive
`depends-on-skill` closure.
