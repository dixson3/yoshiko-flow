//! `yf self uninstall` (plan-018 Issue 3.6).
//!
//! Body implemented in Issue 3.6 (remove the binary + yf-owned XDG dirs; strip the
//! installer PATH block). Issue 3.2 wires the command surface; this stub is
//! replaced when 3.6 lands.

use std::process::ExitCode;

use anyhow::Result;

use crate::cli::SelfUninstallArgs;

/// Run `yf self uninstall` (stub — implemented in 3.6).
pub fn run(_args: &SelfUninstallArgs) -> Result<ExitCode> {
    anyhow::bail!("`yf self uninstall` is not yet implemented (plan-018 Issue 3.6)")
}
