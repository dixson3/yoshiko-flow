//! CLI argument surface for `yf` (clap-derive).
//!
//! Shapes the subcommands required by REQ-YF-CLI-001/002/003. Only `version`
//! has a real body in this bead (REQ-YF-CLI-004); the rest parse correctly and
//! are stubbed for later beads.

use clap::{Args, Parser, Subcommand, ValueEnum};

/// Yoshiko Flow: install, upgrade, verify, and preflight portable agent skills.
#[derive(Debug, Parser)]
#[command(
    name = "yf",
    version = crate::VERSION_LINE,
    about = "Yoshiko Flow CLI",
    propagate_version = true
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Command,
}

#[derive(Debug, Subcommand)]
pub enum Command {
    /// Manage embedded skills (install / upgrade / remove / status).
    Skills {
        #[command(subcommand)]
        command: SkillsCommand,
    },
    /// Diagnose the local environment and skill installs.
    Doctor(DoctorArgs),
    /// Run a skill's preflight checks.
    Preflight(PreflightArgs),
    /// Print the `yf` version and build metadata.
    Version(VersionArgs),
}

#[derive(Debug, Subcommand)]
pub enum SkillsCommand {
    /// Install skills into a scope/surface.
    Install(SkillsArgs),
    /// Upgrade installed skills to the embedded version.
    Upgrade(SkillsArgs),
    /// Remove installed skills.
    Remove(SkillsArgs),
    /// Report install / up-to-date / completeness status per skill.
    Status(SkillsArgs),
}

/// Install surface (REQ-YF-CLI-002).
#[derive(Debug, Clone, Copy, PartialEq, Eq, ValueEnum)]
#[value(rename_all = "lower")]
pub enum Scope {
    User,
    Project,
}

/// Harness surface (REQ-YF-CLI-002).
#[derive(Debug, Clone, Copy, PartialEq, Eq, ValueEnum)]
#[value(rename_all = "lower")]
pub enum Surface {
    Claude,
    Agents,
}

/// Flags shared by every `skills` subcommand (REQ-YF-CLI-002/003).
#[derive(Debug, Args)]
pub struct SkillsArgs {
    /// Explicit skill names to act on (default: resolved set).
    pub names: Vec<String>,

    /// Install scope.
    #[arg(long, value_enum, default_value_t = Scope::User)]
    pub scope: Scope,

    /// Harness surface.
    #[arg(long, value_enum, default_value_t = Surface::Claude)]
    pub surface: Surface,

    /// Explicit destination path (overrides scope/surface resolution).
    #[arg(long, value_name = "PATH")]
    pub target: Option<std::path::PathBuf>,

    /// Show what would change without writing anything.
    #[arg(long)]
    pub dry_run: bool,

    /// Emit machine-readable JSON (REQ-YF-CLI-003).
    #[arg(long)]
    pub json: bool,
}

#[derive(Debug, Args)]
pub struct DoctorArgs {
    /// Emit machine-readable JSON (REQ-YF-CLI-003).
    #[arg(long)]
    pub json: bool,
}

#[derive(Debug, Args)]
pub struct PreflightArgs {
    /// Skill to preflight.
    pub skill: String,

    /// Emit machine-readable JSON (REQ-YF-CLI-003).
    #[arg(long)]
    pub json: bool,
}

#[derive(Debug, Args)]
pub struct VersionArgs {
    /// Emit machine-readable JSON (REQ-YF-CLI-003).
    #[arg(long)]
    pub json: bool,
}
