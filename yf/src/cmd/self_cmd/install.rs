//! `yf self install --from-build` (plan-018 Issue 3.5).
//!
//! Body implemented in Issue 3.5 (promote the local cargo build to ~/.local/bin +
//! write the from-build marker). Issue 3.2 wires the command surface; this stub is
//! replaced when 3.5 lands.

use std::process::ExitCode;

use anyhow::Result;

use crate::cli::SelfInstallArgs;

/// Run `yf self install` (stub — implemented in 3.5).
pub fn run(_args: &SelfInstallArgs) -> Result<ExitCode> {
    anyhow::bail!("`yf self install` is not yet implemented (plan-018 Issue 3.5)")
}
