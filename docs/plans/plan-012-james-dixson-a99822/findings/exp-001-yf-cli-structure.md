# exp-001 — yf CLI structure for an extensible `yf doctor` (feeds #32)

**Verdict:** #32 is a **refactor of an existing command**, not greenfield. `yf doctor`
already exists (`cli.rs:30`, dispatched `main.rs:55`, implemented in `yf/src/cmd/doctor.rs`,
~383 lines incl. tests) with **hardcoded axes** (version/bd/uv/git/skills/rules) **and a
`--repair` mode** (`doctor.rs:120-157`, delegating to `beads_init::repair`).

## CLI organization
- Single-member workspace `members = ["yf"]` (`Cargo.toml:1-3`); the rest of root Cargo.toml
  is cargo-dist release config.
- `yf` crate deps: `anyhow`, `clap` v4 **derive**, `rust-embed`, `serde`, `serde_json`
  (`preserve_order`), `sha2`. **No `which` crate, no `thiserror`** — tool resolution + errors
  are hand-rolled on `std` (deliberate "no extra dep" note `beads_init.rs:580`).
- clap **derive**: `struct Cli` (`cli.rs:10-20`), `enum Command` (`cli.rs:22-37`), per-command
  `#[derive(Args)]` structs (`DoctorArgs` `cli.rs:106-120`). Dispatch in `run()` `main.rs:47-61`.
- Subcommands: `skills install|upgrade|remove|status` (`cmd/install.rs`, `cmd/status.rs`),
  `doctor` (`cmd/doctor.rs`), `preflight` (`preflight.rs`), `migrate` (`migrate.rs`),
  `version` (inline `main.rs:64-75`). Shared lifecycle helpers in `cmd/common.rs`.

## Conventions
- **`--json`:** no shared serializer. Two patterns: ad-hoc `serde_json::json!` + `println!`
  (version, doctor `doctor.rs:82-94`) and `#[derive(Serialize)]` structs with key-order control
  (`preflight.rs` `Outcome::to_json` `:97-128`; `beads_init.rs` VerifyResult/RepairStep/RepairResult).
- **Human/json toggle:** per-command `--json` bool; `if args.json {…} else {…}`. No shared reporter.
- **Exit codes:** `anyhow::Result` throughout. Two idioms: most commands return `Result<()>`
  (`main.rs` maps Err→FAILURE with `eprintln!("error: …")`); **preflight returns
  `Result<ExitCode>`** and owns its exit code (`preflight.rs:875-905`) — the cleaner pattern for
  doctor (a failing check is a verdict, not an error).

## Existing "check" abstraction
- `preflight.rs` is a single linear `run_with_env` (`:215-331`), NOT a registry.
- **The list-of-checks pattern already lives in doctor:** `struct Axis { name, ok, detail }`
  (`doctor.rs:20-24`) + `Vec<Axis>` + `any_fail = axes.iter().any(|a| !a.ok)` (`:80`). 80% of a
  registry; checks are inlined rather than registered.
- `beads_init.rs` offers a richer shape (`VerifyResult` with status enum + diagnostics +
  remediations `:75-83`) — relevant since #32 requires per-check remediation strings.

## Proposed extensible shape
`Check` trait + registry `Vec<Box<dyn Check>>`, generalizing `Axis`:
```rust
struct CheckResult { name: String, ok: bool, required: bool, detail: String, remediation: Option<String> }
trait Check { fn run(&self) -> CheckResult; }
fn checks() -> Vec<Box<dyn Check>> { /* BinCheck{bin,min,expect_vendor}, HomebrewShadowCheck, skills/rules as Check impls */ }
```
- Most checks = one `BinCheck { bin, min_version, expect_vendor }` → future git/gh/dolt is a
  one-line registry edit.
- Place in a `cmd/doctor/` dir (`mod.rs` body+render, `check.rs` trait, `checks.rs` registry).
- Switch doctor body to `Result<ExitCode>` (like preflight) so a failing **required** check
  exits non-zero cleanly (not printed as `error: …`).

## External-binary plumbing (the consolidation win)
- **Three duplicate `which` impls:** `common.rs:87-95` `tool_on_path`→bool;
  `preflight.rs:542-554` `which_in`→`Option<PathBuf>` (has PATH-override test seam);
  `beads_init.rs:581-590` `which`→`Option<PathBuf>`.
- **Two version parsers:** `doctor.rs:191-212`; `preflight.rs:482-537`
  (`extract_version_tuple`, most robust — handles `M.N`, pre-release suffixes).
- **Gap:** no helper returns resolved `PathBuf` **and** captures `--version` in one call —
  needed for #32's "report resolved path" + homebrew-shadow warning. Promote one
  `which`-returning-PathBuf helper (use `preflight.rs:542 which_in`) + reuse
  `extract_version_tuple` as canonical. Homebrew-shadow = `resolve_tool("uv")` path starts-with
  `/opt/homebrew` | contains `/Cellar/` | `linuxbrew`.

## Implications for #32 epic
1. Refactor, not build-from-scratch — must preserve/rescope existing `--repair` + skills/rules axes.
2. **`--repair` conflicts with #32's "read-only" mandate** — decide: keep as explicit opt-in
   (default read-only) or split out. Flag to operator.
3. Consolidate 3×`which` + 2×version-parser (the concrete code-quality win bundled with #32).
4. `required` vs warning severity is **new** (homebrew-shadow must warn, not fail exit).
5. Switch exit idiom to `Result<ExitCode>`.
