---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-pi-opencode-agents-root
description: Do pi and opencode load skills from .agents/skills in both scopes, and does pi require its name transform?
---

# EXP-002 — pi and opencode against the shared `.agents/skills` root

## Approach Tested

Sandboxed spike under an isolated `HOME` plus a `git init`'d repo. Probe `SKILL.md` files were
planted at exactly one root each and the harnesses' **own** skill listings were read — no model
calls, no API keys:

- **opencode** — `opencode debug skill` (JSON listing) under `env -i` with `HOME`/`XDG_*` pointed at
  the sandbox; isolation confirmed first with `opencode debug paths`.
- **pi** — `pi --mode rpc --no-session` fed `{"id":"1","type":"get_commands"}`; the RPC handler
  enumerates loaded skills as `skill:<name>` with full `sourceInfo` (path + scope).

Both were cross-checked against the installed artifacts: the opencode Mach-O binary via `strings`,
and pi's real entrypoint bundle. Probes covered user scope, project scope, pi-native controls,
non-normalized directory names, and a same-named skill planted in three roots at once.

**Versions measured:** pi **0.84.3**, opencode **1.18.23**.

## Result

### 1. opencode — both scopes: YES

**measured.** Both probes loaded with no flag, no config and no trust prompt:

```
"name": "zz-probe-user",    "location": ".../home/.agents/skills/zz-probe-user/SKILL.md"
"name": "zz-probe-project", "location": ".../repo/.agents/skills/zz-probe-project/SKILL.md"
```

Corroborated by the binary's own discovery function, recovered verbatim: a global scan of
`$home/.agents/skills/**/SKILL.md` followed by an ancestor walk from cwd up to the worktree root for
the same pattern. Documented kill switches exist: `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` (both roots)
and `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` (`.claude` only).

### 2. pi — both scopes: YES, but project scope is TRUST-GATED

**measured.** With the project trusted, both probes loaded:

```
{"name":"skill:zz-probe-user",   "sourceInfo":{"scope":"user",   "baseDir":".../home/.agents"}}
{"name":"skill:zz-probe-project","sourceInfo":{"scope":"project","baseDir":".../repo/.agents"}}
```

Re-run with **no** trust flag — the default for an untrusted project — returned only the user-scope
entries. Both project probes vanished, **including pi's own `.pi/skills`**, so the gate is not a
regression introduced by moving to `.agents`. User scope is ungated.

Corroborated by pi's live code: `userAgentsSkillsDir = join(getHomeDir(), ".agents", "skills")`, and
`projectAgentsSkillDirs = projectTrusted ? collectAncestorAgentsSkillDirs(cwd)… : []`.

> **Method trap, recorded because it would have produced a false refutation.** `bin/pi` symlinks to
> `dist/bundle/cli.js`, **not** `dist/main.js`. The readable `dist/core/skills.js` is stale, unused,
> and mentions only `.pi` — a source-only read of it refutes the premise incorrectly. Verify pi
> against `dist/bundle/chunks/*`.

### 3. pi's name transform is NOT required

**measured.** Directories `Zz_Probe_Name` and `Zz_Probe_Shared_NoName` — neither
`lowercase-hyphen,max64` — both loaded, registering under their raw folder names. pi's name
validation is warn-only; only a missing or empty `description` is fatal.

**Asymmetry found: opencode is the stricter of the two.** It silently skipped
`Zz_Probe_Shared_NoName` (no frontmatter `name`) while loading `Zz_Probe_Shared_WithName`. opencode
takes the name **only** from frontmatter and ignores the folder name; pi falls back to the folder
name.

### 4. The plan-054 shadowing was a RACE, not a precedence rule

**measured.** One `zz-dup` skill planted simultaneously in `~/.config/opencode/skills`,
`~/.agents/skills` and `~/.pi/agent/skills`:

| harness | runs | outcome |
| :-- | --: | :-- |
| **opencode** | 5 | `.config/opencode` won **4**, `.agents` won **1** — **nondeterministic** |
| **pi** | 3 | `.pi/agent/skills` won **3/3** — deterministic first-wins in scan order |

Corroborated by the opencode binary: matches are processed with `concurrency:"unbounded"` and the
loader **overwrites** on collision after merely logging `"duplicate skill name"`. The winner is
whichever async read finishes last.

## Implications for Plan

- **The load-bearing premise holds, and is stronger than assumed.** pi *does* read `.agents/skills`,
  in both scopes. D-3's project-scope decision is **confirmed by measurement**, not merely unrefuted.
- **#257's own framing needs correcting.** The issue reasons from "opencode PREFERS `.agents`" and
  asks whether that preference is stable. It is not a preference at all — it is a **coin flip**, and
  the one run where `.agents` won is the same race landing the other way. This is *worse* than the
  issue claims and argues harder for deploy-once.
- **Migration must be a MOVE, not an ADD.** Because collision resolution is racy, leaving the old
  `~/.config/opencode/skills` copy in place is not a safe fallback — it is a per-process coin flip
  between two possibly-divergent copies. Removal must happen in the same operation that writes the
  new root. This independently corroborates D-2's removal decision from a second direction.
- **pi's `name_transform` is dead weight** and is the only thing that would force pi a separate tree
  from codex/agents. Measurably not a pi requirement at 0.84.3.
- **New constraint, pi-only:** project-scope `.agents/skills` under pi requires the project to be
  trusted. A fresh clone loads nothing from project scope until the operator trusts it. User scope is
  the reliable path. This is EXP-005's (#239) territory and confirms the two experiments meet.
- opencode's frontmatter-`name` requirement means a shared tree must keep `name:` in every
  `SKILL.md` — yf already does — but the *folder* name is free.

## Recommendations

1. **Proceed with D-3**, deploying once to `.agents/skills` for opencode and pi in both scopes.
2. **Make the migration a MOVE**, removing the old destination in the same operation.
3. **Drop pi's `name_transform`** from `harness_desc.rs` and its `REQ-YF-INSTALL-007` tests, or
   explicitly re-scope it as belt-and-braces.
4. **Record the pi project-trust gate as a plan risk**; prefer user scope for pi as the primary path.
5. **Add a method note:** verify pi against `dist/bundle/chunks/*`, never `dist/core/*.js`.
6. Consider documenting `OPENCODE_DISABLE_EXTERNAL_SKILLS` as an operator escape hatch.

## Confidence

- **measured:** both opencode probes loading in both scopes; both pi probes loading when trusted and
  project probes vanishing when untrusted; pi loading non-normalized directory names; opencode
  skipping a frontmatter-`name`-less skill; the 5-run and 3-run duplicate-collision tallies; both
  harness versions. Each behavioural measurement is independently corroborated by the shipped
  artifact's own discovery code.
- **inferred:** that opencode's nondeterminism is caused by unbounded-concurrency overwrite-on-collision
  (read from the binary's strings and consistent with the 4:1 split, but the scheduler was not
  instrumented directly); that dropping `name_transform` is safe for *all* future skill names — measured
  only for the probes tested and for the `yf-*` set, which is already lowercase-hyphen.

## Residue

None. The sandbox under the session scratchpad was removed by the main session after the finding
returned, and the operator's real `~/.agents`, `~/.config/opencode` and `~/.pi` trees were verified
free of probe directories.
