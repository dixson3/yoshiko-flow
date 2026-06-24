# exp-002 — bd-init cruft surface (feeds #31)

**Verdict:** `bd init --skip-hooks --skip-agents` suppresses **all four cruft classes** at
init time. The yf-beads-init Python engine is **retired** (a shim → `yf preflight` / `yf
doctor --repair`); the live engine is compiled into the `yf` kernel. The existing repair
step 3 (`bd hooks install --force`) **directly contradicts #31** and must be made
conditional.

## What yf-beads-init verifies/repairs today
`scripts/beads_init.py:4-21` is a shim redirecting to `yf preflight yf-beads-init --json` /
`yf doctor --repair`. Documented contract (SKILL.md/SPEC.md):
- **Verify** (`SKILL.md:74-78`): classifies `ok|deps_missing|not_initialized|corrupted` from
  parsed `bd status --json` `error` key (not exit code). Read-only.
- **Repair** (`SKILL.md:79-92`): (1) wedged migration `bd dolt stop → migrate schema → migrate`;
  (2) `chmod 700 .beads`; (3) **`bd hooks install --force`** ← contradicts #31; (4) gitignore
  `bd doctor --fix` + top-ups; (5) JSONL export; (6) `bd config set dolt.local-only true`.
- **Touches no cruft class** except actively force-installing hooks (the inverse of #31).

## Init-time suppression knobs (`bd init --help`)
- `--skip-hooks` → suppresses class (c) git hooks.
- `--skip-agents` → suppresses classes (a) **and** (b) in one flag (AGENTS.md block, CLAUDE.md
  block, `.codex/`, `.claude/settings.json` hook — all "agents setup").
- `--agents-profile minimal|full` (default minimal = pointer to `bd prime`), `--agents-file`,
  `--agents-template`.
- **No standalone `hooks.install false` key.** Related: `bd config set doctor.suppress.git-hooks
  true` (silences the doctor "Git Hooks" warning once hooks are absent); `dolt.local-only true`
  (skip wiring a Dolt remote).

## Repair-time removers (idempotent, bd-native)
| Class | Detect | Remove |
|:--|:--|:--|
| (a) CLAUDE.md managed block | grep `<!-- BEGIN BEADS INTEGRATION -->`…`END` | strip fenced span only; prefer `bd setup claude --remove` (marker-owned) |
| (a) AGENTS.md block | grep markers | marker-scoped strip |
| (b) `.agents/skills/beads/` | dir exists | `rm -rf` (no bd remover) |
| (b) `.codex/` | `bd setup codex --check` | `bd setup codex --remove` |
| (b) beads `.claude/settings.json` hook | `bd setup claude --check` | `bd setup claude --remove` |
| (c) git hooks | `git config core.hooksPath` ≠ default / `bd hooks list` | `bd hooks uninstall`; reset `core.hooksPath`; `doctor.suppress.git-hooks true` |

Init-time suppression is strictly cleaner (nothing to detect/strip). Repair path needed for
already-dirtied repos (the gws-skills case in #31) **and must neutralize repair step 3** so
cleanup isn't re-dirtied.

## This repo = the reference "correct" target
`core.hooksPath` = git default `.git/hooks`; no `.codex/`, no `.agents/skills/beads/`, no
`.claude/settings.json`; AGENTS.md hand-authored (no beads block); CLAUDE.md = `# beads-skills\n\n@AGENTS.md`
shim. (No `.beads/` here — this repo tracks upstream via `gh issue`.)

## #30 interaction (sequencing concern)
#31 strips bd-init's **project-scope** `.claude/settings.json` `SessionStart` hook; #30
documents a recommended **user-scope** `~/.claude/settings.json` baseline (feature-toggle keys).
Different file scope, different keys — no key conflict, but **both target settings.json**.
Hazard: a wholesale "delete settings.json" cleanup in #31 could wipe a #30 baseline if one ever
sits at project scope. **#31 must scope its cleanup to bd's injected entry** (prefer `bd setup
claude --remove`), delete the file only if empty afterward.

## Correction (post red-team, C1)
The original draft of this finding claimed the live engine was "compiled into `yf` and not
readable in this repo." **That is wrong.** The engine source is **`yf/src/beads_init.rs`,
present and editable in this working directory** — `repair()` at line 309, the contradictory
`bd hooks install --force` step at line 349. So #31's Epic B is direct Rust edits to that
file (not skill-doc-only and with no need to "confirm engine location first"). `beads_init.py`
is the retired shim; the Rust file is the implementation.

## Caveat (absence-as-finding)
The paired CLAUDE.md END marker was not directly observed (`bd setup --print` emits section
body without fences) — confirm against a real `bd init` in a throwaway dir during implementation.
