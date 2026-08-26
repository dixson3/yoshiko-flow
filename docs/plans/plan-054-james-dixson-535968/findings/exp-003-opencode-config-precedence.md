---
type: Reference
okf_spec: OKF-PLAN
id: exp-003-opencode-config-precedence
description: EXP-003 — does opencode read the opencode.json yf writes, or the operator's opencode.jsonc?
---

# EXP-003: opencode `.json` vs `.jsonc` precedence

**Verdict: the hypothesis is REFUTED. A real, adjacent defect is CONFIRMED.**

## Approach Tested

Read `yf/profiles/opencode.json` and both real config files (read-only). Extracted the shipped config loader from the compiled binary (`strings ~/.opencode/bin/opencode`, a 137 MB bun single-file build) and located the global-config load sequence. **Empirical spike:** a `mktemp -d` sandbox with `HOME` and all four `XDG_*` variables overridden, both config files copied in, driving `opencode debug config` across six ablations. Sandbox deleted; `~/.config/opencode` and `~/_dotfiles` untouched. Then read `yf/src/cmd/harness/{drift,audit,settings,profile}.rs`, `yf/src/cmd/doctor/checks.rs`, and `SPEC.md` REQ-YF-TUNE-013/015/016.

## Result

## What was asked

Scoping suspected that `yf`'s opencode config tune was a **silent no-op on this machine**:
`yf` writes `~/.config/opencode/opencode.json`, while the operator also maintains a
hand-authored `opencode.jsonc`. If opencode preferred `.jsonc`, `yf` would be writing a file
nothing reads — and `yf`'s own audit would still report *aligned*, because it reads back the
file `yf` wrote.

## What was measured

**opencode MERGES all candidates; it does not pick one.** Extracted from the shipped binary
(`strings ~/.opencode/bin/opencode`, a 137 MB bun single-file build):

```js
j=F$(j, .../config.json);  j=F$(j, .../opencode.json);  j=F$(j, .../opencode.jsonc)
```

`F$` is a recursive deep merge. Load order is low → high, so **`.jsonc` has the HIGHEST
precedence** and `config.json` the lowest.

Confirmed empirically with `opencode debug config` in a `mktemp -d` sandbox (`HOME` + all four
`XDG_*` overridden), across six ablations:

| Scenario | `permission` | `share` |
| :-- | :-- | :-- |
| both files present (today's real state) | `{"*":"allow"}` | `"disabled"` |
| only `opencode.json` (yf's file) | `{"*":"allow"}` | `"disabled"` |
| only `opencode.jsonc` (operator's) | `{"*":"allow"}` | `null` |
| `.jsonc` sets `{"*":"deny"}`, `share:"manual"` | **`{"*":"deny"}`** | **`"manual"`** |
| `.jsonc` sets `permission:{"bash":"ask"}` | `{"*":"allow","bash":"ask"}` | `"disabled"` |
| `config.json` sets conflicting values | *(both yf values survive)* | `"disabled"` |

**Both of yf's entries are in force right now.** The tune is NOT a no-op.

## The defect that IS real

Row 1 looks like yf "won", but it merely **coincided**: the operator's `.jsonc` sets
`"permission": "allow"`, which normalizes to `{"*":"allow"}` — the same value yf writes.
`share` is set only by yf. The agreement is luck, not mechanism.

Rows 4 and 5 are the hazard. An operator adding `"permission": {"*": "deny"}` to
`opencode.jsonc` would have opencode **running denied** while `yf doctor` reports the settings
drift check **aligned** — because the audit reads only the file yf wrote.

**This is `#203`'s family** (an instrument reporting success while the fact is otherwise), on a
new axis: not an exit code, but a *read set* narrower than the harness's own.

## The hypothesis named the WRONG MODULE — record this

Scoping pointed at `yf/src/cmd/harness/drift.rs`. That module is **not a read-back at all**: its
own header says it asserts agreement between the embedded profile and the reference-baseline
block in `docs/recommended-settings.md`. It never opens a harness config file.

The actual read-back is `audit.rs` (REQ-YF-TUNE-009), driven by `SettingsDriftCheck::from_env`
at `yf/src/cmd/doctor/checks.rs:404-423`, which builds its layers **solely** from
`profile.settings_filename` / `settings_local_filename`. For opencode both are `"opencode.json"`.

**A plan written against the scoping hypothesis would have edited the wrong module.**

## An option must be STRUCK from the list

*"yf writes `.jsonc` when present"* is **actively destructive**. `REQ-YF-TUNE-016` pins opencode
to `format: json` — the `serde_json` pretty-write path — and the real `opencode.jsonc` carries
operator `//` rationale comments that a JSON round-trip **deletes**. Only codex
(`format: toml`, REQ-YF-TUNE-015) has a trivia-preserving writer.

Also rejected: *detect-and-write-whichever-exists* (same comment destruction);
*refuse when both exist* (too blunt — today's overlap is benign and refusing would break a
working setup over a coincidence).

## Implications for Plan

- The **"silent no-op" framing must be dropped** — yf's opencode tune works today. Retarget at **precedence shadowing** and **audit blindness**: a latent correctness bug, not a live outage.
- **The scoping hypothesis named the wrong module.** A plan written against `drift.rs` would edit code that never opens a harness config file. The work is in `audit.rs`, `doctor/checks.rs` and `profile.rs`.
- Any fix touches the embedded profile schema, so it ships **only in a binary** — the same "guess committed to a release" risk REQ-YF-TUNE-017 cites for pi.
- The directory-axis defect warrants its own bead rather than being folded in here.

## Recommendations

**Split the READ SET from the WRITE TARGET.** 
One profile-schema change, no writer change:

1. Add optional `settings_read_layers: ["config.json", "opencode.json", "opencode.jsonc"]`
   (low→high, mirroring the harness's own order), `#[serde(default)]` so codex and claude-code
   deserialize unchanged. `SettingsDriftCheck::from_env` expands each scope into these
   candidates instead of the single `settings_filename`. **This alone kills the false "aligned".**
2. Keep `settings_filename: "opencode.json"` as the **sole write target** — yf-owned,
   comment-free, safely round-trippable.
3. Add a **shadow warning** at tune time: if a higher-precedence candidate defines a path the
   profile also sets, print the shadowed key(s). Warn, do not refuse.

## A second defect, same class, different axis

`yf` hardcodes `~/.codex` and `$HOME/.config/opencode`, ignoring `CODEX_HOME`,
`XDG_CONFIG_HOME`, `OPENCODE_CONFIG` and `OPENCODE_CONFIG_DIR` — **all four of which appear in
opencode's own loader**. `grep XDG_CONFIG_HOME yf/src/cmd/harness yf/profiles` returns no
matches, though `yf/src/dirs.rs:106` already has an XDG helper used elsewhere.

Same class — *yf writing where the harness may not read* — on the **directory** axis rather than
the filename axis. Warrants its own bead.

## Corrections to the scoping premises

- **"silent no-op" must be dropped** from the plan's framing. The tune works today.
- `~/_dotfiles` is **not** a git repo; **`~/_dotfiles/rc-files` is** (verified independently —
  the investigator checked the parent). The symlinks point into `rc-files`, so EXP-006's
  git-tracked premise **holds**.

## Confidence

**measured:** merge order (two independent signals: shipped source plus six live ablations), both files' contents, the module misattribution, and REQ-YF-TUNE-015/016.

**inferred:** that `yf doctor` would report `aligned` under a shadowing `.jsonc` — read from the code path; no live `yf doctor` run was made against a shadowed fixture.
