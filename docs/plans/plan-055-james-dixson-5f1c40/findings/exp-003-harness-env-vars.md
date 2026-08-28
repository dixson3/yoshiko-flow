---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-harness-env-vars
description: What CODEX_HOME / OPENCODE_CONFIG_DIR / XDG_CONFIG_HOME do to each installed harness's skills and config lookup (#238)
---

# EXP-003 — harness directory env vars (#238)

## Approach Tested

Versions measured (installed binaries, 2026-08-27): codex **0.150.1**, opencode **1.18.23**,
pi **0.84.3**, claude-code **2.1.247**.

Two independent methods, both against installed artifacts, never docs:

1. **Static** — `strings`/`grep` over each binary or bundle for the var names and the directory
   literals they combine with.
2. **Dynamic sandbox spikes** under scratch dirs with a fake `$HOME` and `GIT_CONFIG_GLOBAL=/dev/null`,
   planting a uniquely named `SKILL.md` in every candidate root and observing which the harness loaded.
   codex and opencode expose direct read-outs (`codex debug prompt-input` emits a `(file: …)` locator;
   `opencode debug skill` emits `"location"`). pi and claude-code have no listing command, so an
   **atime probe** was used, validated by an explicit atime sanity check and by in-run negative
   controls — in every sweep some candidates stayed untouched while others flipped, so the instrument
   discriminates.

> **A first probe was discarded as invalid and is recorded rather than hidden.** FIFOs were used as
> candidates; a FIFO fails `isFile()` and is skipped by the loaders, producing a uniform false
> negative. Replaced with real files. Separately, pi had to get past auth before skill discovery runs,
> and `claude doctor` loads no skills at all — both needed a real started session.

Every override result was reproduced (opencode ×2; claude-code ×2 for each of two vars).

## Result

"config" = the harness-private surface (config file, auth, state); "skills" = the user-scope skills root.

| harness | var | moves CONFIG | moves SKILLS root | precedence vs default | `XDG_CONFIG_HOME` honoured |
| :-- | :-- | :-- | :-- | :-- | :-- |
| codex | `CODEX_HOME` | yes | yes (`$CODEX_HOME/skills`) | **replace** — default silently dropped | **no** |
| opencode | `OPENCODE_CONFIG_DIR` | adds a config dir | **adds** `$VAR/skills` | **additive** — default retained | **yes**, and it **replaces** `~/.config/opencode` |
| pi | `PI_CODING_AGENT_DIR` | yes | yes (`$VAR/skills`) | **replace** — default silently dropped | **no** (zero occurrences) |
| claude-code | `CLAUDE_CONFIG_DIR` | yes | yes (`$VAR/skills`) | **replace** — default silently dropped | **no** |

### The decisive result for this plan: `.agents/skills` is ENV-IMMUNE on three of four harnesses

- **measured — codex.** `$HOME/.agents/skills` is a first-class user-scope root and **`CODEX_HOME`
  does not move it**: the probe loaded in both the baseline and the `CODEX_HOME`-set sweep. codex's
  full measured root set is `$CODEX_HOME/skills` (or `~/.codex/skills`), `$HOME/.agents/skills`,
  `<cwd>/.codex/skills`, `<cwd>/.agents/skills`. `<cwd>/.claude/skills` was **not** picked up.
- **measured — pi.** `~/.agents/skills` is `$HOME`-derived and **unaffected by
  `PI_CODING_AGENT_DIR`** — READ in both sweeps — while `~/.pi/agent/skills` flips from READ to
  untouched when the var is set. Verbatim: `userAgentsSkillsDir = join(homeDir, ".agents", "skills")`.
- **measured — opencode.** `~/.agents/skills` loaded under **all four** override combinations.

### opencode is the odd one out, in two ways

**measured.** `XDG_CONFIG_HOME` **replaces**; `OPENCODE_CONFIG_DIR` **adds**. Verbatim:
`Y=R.XDG_CONFIG_HOME||(X?Z.join(X,".config"):void 0)` and `config: e.OPENCODE_CONFIG_DIR ?? G.config`,
with the roots assembled by a **list append**. Measured: `XDG_CONFIG_HOME` swapped the default skills
root out; `OPENCODE_CONFIG_DIR` **gained** a root while **keeping** the default (8 roots vs 7). With
both set, both new roots loaded and the default was gone — the two vars are orthogonal, not competing.

### `XDG_CONFIG_HOME` is honoured by opencode ONLY

**measured.** codex's only `XDG_CONFIG_HOME` strings sit inside vendored `gix` git-config code;
claude-code's 25 occurrences are git discovery, fish completions, vendored ripgrep docs, an
env-scrubbing deny-list and one unused vendored helper; **pi references it zero times anywhere**.
Each was confirmed dynamically: setting it produced a byte-identical loaded-skill set.

### claude-code, cross-checked against EXP-001

**measured, by a second and independent method.** `~/.agents/skills` and `<proj>/.agents/skills` were
**untouched in all five sweeps** while sibling `.claude` candidates flipped to READ in the same runs.
The string `".agents"` as a directory literal occurs **zero** times in the binary; all 135 `.agents`
hits are JS property access. `ANTHROPIC_CONFIG_DIR` exists in the binary but **does not** move the
skills root.

## Implications for Plan

1. **A single "env override" column on the descriptor would be wrong.** The right shape is a per-row
   *surface-dir* override var plus a separate, mostly-empty *skills-root* override var:

   | harness | surface-dir override | skills-root override (post-055) |
   | :-- | :-- | :-- |
   | claude-code | `CLAUDE_CONFIG_DIR` | `CLAUDE_CONFIG_DIR` (skills stay under it) |
   | codex | `CODEX_HOME` | **none** |
   | pi | `PI_CODING_AGENT_DIR` | **none** |
   | opencode | `XDG_CONFIG_HOME` (replace) + `OPENCODE_CONFIG_DIR` (additive) | **none** |
   | agents | — | — |

2. **#238's surface shrinks by three-quarters, not entirely.** Moving skills to `.agents/skills`
   removes skills-root env sensitivity for codex, pi and opencode outright. It does **not** help
   claude-code, whose only skills root is `.claude/skills` and *is* moved by `CLAUDE_CONFIG_DIR`.
   #238 reduces from "four harnesses × two concerns" to "one harness × one var (skills) + four
   harnesses × one var (surface)".
3. **Two current descriptor rows are already sub-optimal, in opposite directions.**
   `codex → .agents/skills` is already the env-immune choice and is measurably correct.
   **`opencode → .config/opencode/skills` is the WORST available choice** — the one opencode path
   `XDG_CONFIG_HOME` relocates — when opencode also reads `~/.agents/skills` and `~/.opencode/skills`.
   `pi → .pi/agent/skills` is relocated by `PI_CODING_AGENT_DIR`; `~/.agents/skills` is not.
4. **The precedence column must be three-valued** — `replace` / `additive` / `none`. Any yf logic of
   the form "if `$VAR` set, install there *instead*" would **under-install for opencode and
   over-install for the other three**.
5. **The `--from-build` sync is exposed to the replace-semantics vars, and fails silently.** With
   `CODEX_HOME` / `PI_CODING_AGENT_DIR` / `CLAUDE_CONFIG_DIR` exported, yf's `$HOME`-relative install
   writes to a directory the harness no longer reads — a silent no-op, because the default dir still
   exists and looks correct on disk. Measured for all three. This is #238's concrete user-visible
   failure.

## Recommendations

1. **Split the descriptor into `skills_root` and `surface_dir`, attaching the env override to the
   SURFACE column by default.** Only claude-code needs it propagated to the skills column.
2. **Switch opencode's user-scope skills subpath off `.config/opencode/skills`** — prefer
   `.agents/skills`, which is both the plan-055 shared root and measured-read.
3. **Switch pi's user-scope skills subpath to `.agents/skills`** for the same reason.
4. **Make the precedence column three-valued**, encoding opencode as *two* vars.
5. **Add a one-line preflight warning rather than a resolver rewrite.** For each harness, if its
   replace-semantics var is set and disagrees with the `$HOME`-derived default, warn at install time.
   After recs 2–3 only `CLAUDE_CONFIG_DIR` would still need the resolver to actually follow it — a
   fraction of the cost of teaching `dest.rs` full env resolution.
6. **Record `XDG_CONFIG_HOME` as honoured by opencode ONLY.**
7. **Note the claude-code `.agents/skills` gap explicitly.** "One shared root all harnesses read" is
   false today; the split must keep a per-harness skills root, with `.agents/skills` as the shared
   *value* for three rows rather than a single global path.

## Confidence

- **measured:** every cell of the four-harness table, each by a direct read-out (codex, opencode) or a
  validated atime probe with in-run negative controls (pi, claude-code); the additive-vs-replace
  distinction for opencode, by both source form and a 7-vs-8-root listing; `XDG_CONFIG_HOME` ignored
  by codex/pi/claude-code, dynamically confirmed; `.agents/skills` surviving `CODEX_HOME` and
  `PI_CODING_AGENT_DIR`; claude-code never reading `.agents` at any scope, across five sweeps;
  `ANTHROPIC_CONFIG_DIR` not moving the skills root; the silent-no-op sync exposure for all three
  replace-semantics vars.
- **inferred:** that three of four vars stop mattering for skills under plan-055 (measured directly
  for codex, pi and opencode; claude-code is a *different* problem, not a confirmation).
- **not tested, flagged by the investigator:** whether pi's name transform collides with
  codex/opencode entries in a shared directory. **EXP-002 answers this** — pi's transform is not
  required at 0.84.3, and D-7 drops it, so no normalization asymmetry remains to collide.
- **discarded as invalid:** the FIFO-based first probe (see Approach).

## Residue

Repo clean. A sandbox tree remains under the session scratchpad; the investigator's `rm -rf` was
denied by the permission layer and it awaits an operator-side delete.
