---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-dolt-remote-local-only
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
---

# exp-002 — The Dolt-remote / local-only two-layer model (#159, #160)

**Date:** 2026-08-17
**Question:** Why does `--repair --remove-remote` report `ok` without removing the remote, and how did a push happen under `dolt.local-only = true`?
**Method:** source trace of `yf/src/beads_init.rs` + `cmd/doctor/`, plus read-only measurement across three beads repos, `.beads/` metadata, server logs, and `git ls-remote`. Nothing mutated.

## Headline — #159's filed root cause is WRONG, and the real one is worse

The issue says the flag "touches `sync.remote` but not the Dolt-level remote." **The code already
attempts both layers.** The real cause is a **silent failure in the decisive layer**, and it means
`--remove-remote` has **never worked in server mode — the canonical profile (REQ-YF-PRE-010 invariant 1, SPEC.md:856-859).**

Chain (`yf/src/beads_init.rs`): plan step added only when `remove_remote && local_only` (`:568-573`)
→ dispatch (`:920-923`) → `remove_dolt_remote` (`:1172-1204`):

- **Layer 1 (decisive):** `if let Ok(dolt_root) = derive_dolt_repo_root(&beads_dir)` → raw
  `dolt remote remove <name>` + `dolt commit`.
- **Layer 2:** `remove_sync_remote_config(&beads_dir)` — raw YAML edit of `.beads/config.yaml`.

**The bug is `derive_dolt_repo_root` (`:709-731`) + `find_dolt_dirs` (`:674-703`):** it requires
**exactly one** dir containing a `.dolt/` child, else returns `Err("ambiguous Dolt working
directory: {n} candidates … refusing to guess")`. In `remove_dolt_remote` that `Err` is **swallowed
by the `if let Ok(...)` with no `else`** — layer 1 is skipped with no error, no message, rc = 0.

**Server mode structurally guarantees two candidates.** Measured across three unrelated repos:

```
yoshiko-flow:  .beads/dolt/.dolt      +  .beads/dolt/yoshiko_flow/.dolt
agent-skills:  .beads/dolt/.dolt      +  .beads/dolt/agent_skills/.dolt
talisman:      .beads/dolt/.dolt      +  .beads/dolt/talisman/.dolt
```

`.beads/metadata.json` → `{"dolt_mode":"server","dolt_database":"yoshiko_flow"}`: `.beads/dolt` is
the server data-dir (itself a Dolt repo), `.beads/dolt/<db>` is the database. Two `.dolt/` dirs is
the normal layout, not corruption.

**Blast radius beyond #159** — the same helper silently degrades:

- `has_local_only_remote` (`:998-1013`) — detection falls back to `sync.remote` only.
- The REQ-BINIT-016 embedded wedge fix.

**Three inconsistent stories about one flag:** `cli.rs:449-453` help says "Dolt remote /
`sync.remote`"; the step label (`beads_init.rs:570`) names only `sync.remote`; the code executes
layer 2 only in server mode.

**Residue of layer 2 having run** — `.beads/config.yaml` tail is a dangling key
(`remove_sync_remote_config` `:1211-1240` stripped the nested child):

```yaml
dolt.local-only: true
sync:
```

## Why it reports `ok` — the severe defect

**The verdict is unconditional; there is no postcondition check.** `cmd/doctor/mod.rs:160-168`:

```rust
let mark = match step.rc { Some(0) => "ok  ", Some(_) => "FAIL", None => "-   " };
```

`ok` means *"the step function returned `Ok`"*, never *"a remote is now absent"* — and
`remove_dolt_remote` returns `Ok(())` on the ambiguous-derive path. The post-repair `after` verify
(`mod.rs:169-184`) checks general beads health and **does not re-run `has_local_only_remote`**, so
it cannot catch it either.

Restated severity: **a repair step reports success without verifying its own postcondition, and
its single decisive sub-step fails open.**

## The layers, precisely

| Layer | Where | What it is | What it gates |
| :-- | :-- | :-- | :-- |
| `dolt.local-only` | `.beads/config.yaml` | **Init-time flag only.** bd's own help: *"Skip wiring a Dolt sync remote during bd init"* | **Nothing at push time** |
| `sync.remote` | `.beads/config.yaml` | bd-level *record* of a remote URL, persisted by `bd init --remote` | Secondary/cosmetic — clearing it alone leaves the repo gated (yf-beads-init SPEC.md:149-152) |
| **Dolt-DB remote** | `.dolt/repo_state.json` `remotes`; `bd dolt remote add/list/remove` | The decisive layer | **This is what permits a push** |
| git `origin` | `.git/config` | ordinary git remote | Source of the `git+https://…` URL |

**`dolt.local-only` provides ZERO runtime protection.** `bd dolt push --help` never mentions it —
it says only "Requires a Dolt remote to be configured in the database directory."

## #160 forensics

**(a) No yf/skills code path adds a Dolt remote.** `grep -rn "remote add|dolt remote" yf/src skills`
returns only *removal*/enumeration sites — consistent with GR-BINIT-003 (repair only ever clears).

**(b) A plausible yf-side mechanism: ordering in `repair()`.** `beads_init.rs:456-467` pushes
`bd init --skip-hooks --skip-agents` **then** `bd config set dolt.local-only true`. Since
local-only is an *init-time skip flag*, setting it **after** `bd init` is too late — `bd init` may
already have wired the remote from git origin, and `--remove-remote` is not implied here.
*(inferred, uncorroborated — verifying needs a sandboxed `bd init` in a repo with a git origin.)*

**(c) Timeline of the actual push.** `.beads/push-state.json` →
`{"last_push":"2026-04-05T23:09:12Z"}`; `.beads/dolt-server.log:857` at 22:19Z →
`error="fatal: remote 'origin' not found."`. So a push failed for want of a remote at ~22:19Z and
succeeded ~50 min later — a remote was added in that window. The server log records only *failing*
queries, so the `dolt_remote('add', …)` left no trace. **One push, not ongoing replication.**

**(d) Land-the-plane prose proposing `bd dolt push` — none is local-only-aware:**

| File:line | Guard |
| :-- | :-- |
| `skills/yf-plan/SKILL.md:1038` — `bd dolt push && git push` (§6.2) | **none** |
| `skills/yf-beads-hygiene/scripts/beads_hygiene.py:689, :764` — printed unconditionally after any mutation | **none** |
| `skills/yf-beads-hygiene/SKILL.md:127` | **none** |
| `skills/yf-plan/agents/coordinator.md:114-116` | authorization-gated, not local-only-gated |
| `skills/yf-research/agents/packager.md:71` — *"only if a dolt remote is configured"* | **partial, and backwards for #160** — a stray remote satisfies it |

These are the mechanism by which an operator or agent, handed a remote by (b), executes the push.

## Current state (read-only, unchanged)

```
bd config get dolt.local-only  → "true"
bd config get sync.remote      → ""            (cleared)
bd dolt remote list            → No remotes configured.
both repo_state.json           → "remotes": {}
bd version                     → 1.1.2 (Homebrew)
```

**GitHub-side dolt refs are GONE.** `git ls-remote origin` advertises only `HEAD`,
`refs/heads/main`, five `refs/pull/*/head`, and `refs/tags/v0.1.0…v0.4.0` — **no `refs/dolt/*`, no
`__dolt_remote_info__`.** They were present on 2026-08-17, so they have since been deleted
server-side. **The #160 data exposure is already remediated on the remote; only the code-path
defect remains.** `.beads/` is untracked, so no git-history forensics for `config.yaml`.

## Where the fix goes

`yf doctor`'s read-only path has **no beads-canonicalization axis today** — the drift detection
lives in preflight (`preflight.rs:772-813`, remote arm `:786-795`, already emitting the correct
`yf doctor --repair --local-only --remove-remote` string per REQ-BINIT-024). Insertion points in
dependency order:

1. **`beads_init.rs:709-731 derive_dolt_repo_root`** — the actual bug. Resolve server mode
   deterministically (prefer `beads_dir/<metadata.dolt_database>`) before declaring ambiguity.
   **Fixing this alone repairs `--remove-remote`, `has_local_only_remote`, and REQ-BINIT-016
   together.**
2. **`beads_init.rs:1178`** — replace `if let Ok(...)` with explicit `Err` propagation so an
   underivable root becomes rc != 0 → `FAIL`, never a silent `ok`.
3. **`cmd/doctor/mod.rs:169-184`** — postcondition: after an applied `remove-remote`, re-run
   `has_local_only_remote` and bail if still true. The generalizable fix.
4. **New `Check` in `cmd/doctor/checks.rs:682-704`** — `Box<dyn Check>` registry; `CheckResult::
   fail/warn` at `check.rs:27-50`. Wrapping `has_local_only_remote` is a one-line registry edit and
   delivers the "reports loudly" half. Reuse the remediation string from `preflight.rs:791-793`.
5. **Skill-prose half of #160** — local-only guard in the four land-the-plane sites in (d).

## SPEC coverage

**Exists** (`skills/yf-beads-init/SPEC.md`): REQ-BINIT-020 (`:143-159`, the two-layer contract —
*the requirement is correct; the implementation silently fails it in server mode*), REQ-BINIT-024
(`:160-170`), REQ-BINIT-023 (`:171-178`), REQ-BINIT-016 (`:73-86`), REQ-BINIT-025 /
REQ-YF-PRE-010.

**Missing:**

1. **No requirement that a repair step VERIFY its own postcondition** — nothing forbids reporting
   `ok` for a step that did nothing. The #159 gap and the most valuable new REQ.
2. **No requirement that an ambiguous/underivable Dolt root be an ERROR, not a silent skip.**
   REQ-BINIT-016 specifies a "derived (not hardcoded) path" but not the failure mode.
3. **`derive_dolt_repo_root` is specified only against the EMBEDDED layout** — REQ-BINIT-020's
   caveat names `.beads/embeddeddolt/<db>/` "(or server data dir)" and the fixture at `:272-276`
   is embedded. **No requirement or fixture covers the server-mode two-`.dolt` layout — which is
   why this shipped.**
4. **No requirement that `dolt.local-only` is init-time-only and therefore not a runtime guard**,
   and none that land-the-plane prose suppress `bd dolt push` under local-only. GR-BINIT-003 is an
   anti-drift rule for agents, not a testable requirement. The #160 gap.
5. Root `SPEC.md` carries only the doctor-flag surface (`:914-915`); no repair-verification REQ.
