---
type: Finding
okf_spec: OKF-PLAN
---
# Finding: current `yf harness` architecture and its multi-harness extension seam

**Source:** inline investigation of `yf/src/cmd/harness/*` and `SPEC.md §3.10` (main session, 2026-07-22).

## Current state (plan-032, REQ-YF-TUNE-001..011)

`yf harness tune --harness <name> [--project [--committed]] [--force] [--dry-run] [--json]` is
implemented and wired (`yf/src/main.rs`, `yf/src/cli.rs`), but ships **only** the `claude-code`
profile with a **JSON-only** engine. Module layout:

| Module | Owns | Multi-harness impact |
|:--|:--|:--|
| `profile.rs` | Embedded machine-readable `Profile` (harness key, `surface_dir`, settings filenames, `hook_preserve_key`, `agent_tool`, `entries[]`). Loads from a **separate** rust-embed root `yf/profiles/`. | `Entry.path` is a **JSON dot-path**; `value` is `serde_json::Value`. A new profile is data-only for a JSON harness; a non-JSON harness (codex TOML) needs more. |
| `settings.rs` | `TuneScope` (user / project-local / project-committed) → path resolution; **fail-safe** read (`SettingsRead::{Absent,Parsed,Malformed}`) refusing to overwrite a malformed file; JSON pretty-write preserving key order. | Read/write is `serde_json`-hardwired. TOML needs a format-aware read/write adapter. Scope paths differ per harness (codex `~/.codex/`, opencode `~/.config/opencode/`, pi `~/.pi/agent/`). |
| `merge.rs` | Kind-aware, idempotent merge **pure over `serde_json::Value`**: scalar add-missing (conflict unless `--force`), set union (non-destructive), `Agent`-never-denied. | Reusable as-is if TOML is bridged to `serde_json::Value` (parse TOML→Value, merge, serialize Value→TOML). The engine itself need not change. |
| `drift.rs` | Doc-agreement (`docs/recommended-settings.md` reference block ↔ profile). | Per-harness reference blocks. |
| `audit.rs` | `yf doctor` read-only settings-drift axis over the effective merged view. | Per-harness axis. |

## SPEC pre-declared extension point

`REQ-YF-TUNE-011` already states the multi-harness dimension exists but "the merge engine, scope
resolution, and JSON model are Claude-Code-specific in this plan — a future harness (e.g. codex →
`.codex/config.toml` TOML) needs a *new engine*, not merely a new profile. Concrete non-Claude
profiles are a follow-on gated on the `yf-2gyv` per-harness research." An unknown `--harness`
already refuses cleanly (REQ-YF-TUNE-002). So this plan **extends** an anticipated seam; it does
not retrofit.

## Design implications (carried into Approach)

1. **Format engine abstraction.** Introduce a `SettingsFormat` (Json | Toml) per profile. The
   merge stays `serde_json::Value`-based; each format supplies parse→Value and Value→serialize
   (TOML via the `toml` crate ↔ `serde_json::Value`). opencode (`opencode.json`) and pi
   (`settings.json`) reuse the JSON path; codex (`config.toml`) is the first TOML consumer.
2. **AGENTS.md rule deployment is a distinct capability, not a settings profile.** Per research-002,
   non-Claude config surfaces are enforcement/visibility-only; the load-bearing cross-harness
   surface is always-loaded **AGENTS.md** prose. Deploying a **minimized irreducible-core** rule
   bundle to each harness's global-rule path is a new sub-command/mode, delimited by a managed
   marker block so update/revert never clobbers user prose.
3. **Ownership tracking for `--revert`.** JSON/TOML key-value formats carry no yf-ownership signal;
   a **sidecar managed-key manifest** records which keys/blocks yf wrote so revert removes only
   those. AGENTS.md uses self-describing begin/end markers (revert deletes the block); the sidecar
   unifies the record across formats.
