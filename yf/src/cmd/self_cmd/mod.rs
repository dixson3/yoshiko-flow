//! `yf self …` — the binary's own install/update lifecycle (plan-018 Epic 3).
//!
//! Distinct from `yf skills …` (which manages the embedded *skills/rules*): `yf
//! self` manages the **`yf` binary itself** — vendor self-update, dev from-build
//! install, and uninstall. Submodules:
//!
//! - [`receipt`] — install-receipt contract (3.1): cargo-dist's `yf-receipt.json`
//!   and yf's own `yf-from-build.json` marker.
//! - [`update`] — `yf self update` (3.4) + post-update skills refresh (3.7).
//! - [`install`] — `yf self install --from-build` (3.5).
//! - [`uninstall`] — `yf self uninstall` (3.6).
//!
//! Later beads add `source` (3.3 install-source classification) and `archive`
//! (3.4a pure-Rust extraction).

use std::process::ExitCode;

use anyhow::Result;

use crate::cli::SelfCommand;

pub mod install;
pub mod receipt;
pub mod uninstall;
pub mod update;

/// Dispatch `yf self <sub>`. Each body owns its exit code (a refusal is a verdict,
/// not an error), so this returns [`ExitCode`] directly.
pub fn run(command: &SelfCommand) -> Result<ExitCode> {
    match command {
        SelfCommand::Update(args) => update::run(args),
        SelfCommand::Install(args) => install::run(args),
        SelfCommand::Uninstall(args) => uninstall::run(args),
    }
}
