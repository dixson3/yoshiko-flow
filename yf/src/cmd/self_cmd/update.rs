//! `yf self update` (plan-018 Issue 3.4) + post-update skills refresh (3.7).
//!
//! Body implemented in Issue 3.4 (download/verify/extract/self-replace) and 3.7
//! (post-swap skills/rules refresh). Issue 3.2 wires the command surface; this
//! stub is replaced when 3.4 lands.

use std::process::ExitCode;

use anyhow::Result;

use crate::cli::SelfUpdateArgs;

/// Run `yf self update` (stub — implemented in 3.4).
pub fn run(_args: &SelfUpdateArgs) -> Result<ExitCode> {
    anyhow::bail!("`yf self update` is not yet implemented (plan-018 Issue 3.4)")
}
