# exp-004 — Fold map: `~/.claude/rules/BEADS.md` → `BEADS_INIT.md` (Epic E.1, DEC-2 artifact)

Section-by-section audit of the orphan, unowned user-scoped rule
`~/.claude/rules/BEADS.md`. Each section is classified against **every** existing
always-loaded surface (not just `BEADS_INIT.md`), per E.1. Dispositions:

- **keep-in-rule** — genuinely always-needed mandate with no other skill-owned home → fold into `BEADS_INIT.md`.
- **route-to-extra** — CLI/issue-type/workflow detail already owned (or better owned) by `yf-beads-extra` / the canonical `beads` skill.
- **cross-ref-upstream** — already owned by `UPSTREAM_TRACKING.md` (close-time / land-the-plane push); reference, never restate.
- **drop-as-dup** — narrative/onboarding already covered elsewhere; no always-loaded value.

## Fold map

| BEADS.md section | Content | Disposition | Where it lands / why |
|:--|:--|:--|:--|
| Frontmatter + title (`# Agent Instructions`) | Obsidian metadata, "run `bd onboard`" | drop-as-dup | Onboarding narrative; `beads` skill owns `bd onboard`. No always-loaded value. |
| "For direct-CLI gotchas … invoke the `bd-cli` skill" | Pointer to a stale skill name (`bd-cli`) | route-to-extra | The real skill is `yf-beads-extra`. Replace with a one-line cross-ref, don't restate. |
| Quick Reference (`bd ready/list/show/update/close/dep/dolt push`) | CLI cheat-sheet | route-to-extra | Routine loop is the canonical `beads` skill; edge/dep mechanics are `yf-beads-extra`. Restating a cheat-sheet in an always-loaded rule is pure bloat. |
| **Non-Interactive Shell Commands** | `cp -f`/`mv -f`/`rm -rf`, `ssh -o BatchMode`, `apt-get -y`, etc. — avoid hanging on `-i` aliases | **keep-in-rule** | No other skill-owned always-loaded home. Behavioral constraint that prevents a wrong action (hang). Folded, condensed to the load-bearing forms. |
| Issue Tracking / Why bd / Quick Start / Issue Types / Priorities / Workflow / Auto-Sync | Long operational reference (create flags, type enum, priority scale, agent workflow, JSONL auto-sync) | route-to-extra | Issue-type semantics + create/dep mechanics → `yf-beads-extra`; routine workflow → `beads`. Verbose; violates token-efficiency Cut rule for an always-loaded surface. |
| "Use bd for ALL task tracking … do NOT use markdown TODOs" mandate | The one behavioral invariant in that block | **keep-in-rule** | Behavioral constraint with no other always-loaded home (the rules-surface `BEADS.md` was the only carrier). Folded as a one-liner. |
| Landing the Plane (Session Completion) | `git pull --rebase` → `bd dolt push` → `git push`; "work not complete until pushed" | cross-ref-upstream | The close-time / land-the-plane **push trigger is already owned** by `UPSTREAM_TRACKING.md`. Restating it here would recreate the duplicate always-loaded surface Epic E exists to remove. Cross-reference only. |

## Charter note (E.2, R5)

`BEADS_INIT.md`'s stated charter is the init/health **trigger contract**. The two
**keep-in-rule** items (use-bd-for-all-tracking; non-interactive shell-flag safety)
are general bd-usage mandates that sit slightly outside that charter — but
`BEADS_INIT.md` is their only skill-owned always-loaded home. E.2 adds a one-line
scope-note widening the charter so the fold is on-charter, rather than smuggling
off-charter content in silently.

## Net effect

Two short folded items (one mandate line + a condensed non-interactive-shell block),
everything else dropped or routed. The orphan rule is then retired by the operator
(manual `rm ~/.claude/rules/BEADS.md` post-install) — documented in `SKILL.md`/`README.md`,
losing only content already covered by `yf-beads-extra`, `beads`, or `UPSTREAM_TRACKING.md`.
