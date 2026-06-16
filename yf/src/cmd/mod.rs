//! Command bodies for `yf skills …` and `yf doctor` (beads 1.5/1.6/1.7).
//!
//! Each subcommand has its own module; [`common`] holds the shared selection,
//! deploy/prune, companion-rule, and per-skill health logic that `install`,
//! `status`/`upgrade`/`remove`, and `doctor` all build on.

pub mod common;
pub mod doctor;
pub mod install;
pub mod status;
