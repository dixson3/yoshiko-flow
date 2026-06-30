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
    /// Diagnose the local environment and skill installs (read-only; pass
    /// `--repair` to apply the beads-init repair sequence).
    Doctor(DoctorArgs),
    /// Run a skill's preflight checks.
    Preflight(PreflightArgs),
    /// Migrate legacy `.state/<old>/` + `.<old>.local.json` to the `.yf/` layout.
    Migrate(MigrateArgs),
    /// Manage the `yf` binary itself: self-update, dev install, uninstall.
    ///
    /// This is the **binary** lifecycle — distinct from `yf skills upgrade`, which
    /// re-deploys the embedded **skills/rules**. `yf self update` swaps the binary
    /// in place from a GitHub release; `yf skills upgrade` does not touch the binary.
    #[command(name = "self")]
    SelfCmd {
        #[command(subcommand)]
        command: SelfCommand,
    },
    /// Print the `yf` version and build metadata.
    Version(VersionArgs),
}

/// `yf self …` subcommands (plan-018 Epic 3).
#[derive(Debug, Subcommand)]
pub enum SelfCommand {
    /// Update the `yf` binary in place from the latest GitHub release.
    ///
    /// Vendor installs only: refuses on a Homebrew copy (use `brew upgrade`) and
    /// no-nags a `--from-build` dev copy. Verifies the downloaded archive's sha256
    /// against the release manifest before an atomic swap.
    Update(SelfUpdateArgs),
    /// Install a locally-built `yf` to `~/.local/bin` (dev workflow).
    Install(SelfInstallArgs),
    /// Remove the `yf` binary and yf-owned XDG dirs (never touches installed skills).
    Uninstall(SelfUninstallArgs),
}

#[derive(Debug, Args)]
pub struct SelfUpdateArgs {
    /// Check for a newer release and report, but do not download or swap.
    #[arg(long)]
    pub check: bool,

    /// Proceed even when the source can't be confirmed as a vendor install
    /// (e.g. an `unknown`/from-build copy). Never overrides a Homebrew refusal.
    #[arg(long)]
    pub force: bool,

    /// Skip the post-update skills/rules refresh (3.7); swap the binary only.
    #[arg(long)]
    pub binary_only: bool,

    /// Emit machine-readable JSON (REQ-YF-CLI-003).
    #[arg(long)]
    pub json: bool,
}

#[derive(Debug, Args)]
pub struct SelfInstallArgs {
    /// Promote the local build to `~/.local/bin` (the only supported mode today).
    #[arg(long)]
    pub from_build: bool,

    /// Promote the `release` profile build (default).
    #[arg(long, conflicts_with = "debug")]
    pub release: bool,

    /// Promote the `debug` profile build instead of `release`.
    #[arg(long)]
    pub debug: bool,

    /// Run `cargo build` (for the chosen profile) before promoting.
    #[arg(long)]
    pub build: bool,

    /// Overwrite an existing `~/.local/bin/yf`.
    #[arg(long)]
    pub force: bool,

    /// Emit machine-readable JSON (REQ-YF-CLI-003).
    #[arg(long)]
    pub json: bool,
}

#[derive(Debug, Args)]
pub struct SelfUninstallArgs {
    /// Proceed without the interactive confirmation.
    #[arg(long)]
    pub force: bool,

    /// Emit machine-readable JSON (REQ-YF-CLI-003).
    #[arg(long)]
    pub json: bool,
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

    /// Act only on skills in this group (computed from `skill-group` frontmatter).
    #[arg(long, value_name = "NAME")]
    pub group: Option<String>,

    /// Treat a missing `depends-on-tool` as a hard failure (install only).
    #[arg(long)]
    pub strict: bool,

    /// Overwrite an existing companion rule (default preserves hand-edits).
    #[arg(long)]
    pub force: bool,

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

    /// Opt in to mutation: apply the `yf-beads-init` repair sequence to a broken
    /// beads config (REQ-YF-PRE-007). Default (no `--repair`) is read-only —
    /// doctor only reports, never modifies the repo (DEC-1).
    #[arg(long)]
    pub repair: bool,

    /// With `--repair`, also assert local-only Dolt (no remote).
    #[arg(long)]
    pub local_only: bool,

    /// With `--repair` under local-only context, also CLEAR any configured Dolt
    /// remote / `sync.remote` (#39, Epic B). Off by default; this is the one
    /// repair step that touches remote config, so it is an explicit opt-in.
    #[arg(long)]
    pub remove_remote: bool,
}

#[derive(Debug, Args)]
pub struct MigrateArgs {
    /// Repo to migrate (default: git-root of cwd).
    #[arg(long, value_name = "PATH")]
    pub path: Option<std::path::PathBuf>,

    /// Show what would change without writing anything.
    #[arg(long)]
    pub dry_run: bool,

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

#[cfg(test)]
mod tests {
    use super::*;
    use clap::CommandFactory;

    #[test]
    fn cli_is_well_formed() {
        // clap's own internal consistency check (catches conflicting args, bad
        // defaults, duplicate flags).
        Cli::command().debug_assert();
    }

    #[test]
    fn self_command_is_named_self_not_self_cmd() {
        // The variant is `SelfCmd` (Self is reserved) but the subcommand the user
        // types must be `self`.
        let cli = Cli::try_parse_from(["yf", "self", "update"]).unwrap();
        assert!(matches!(
            cli.command,
            Command::SelfCmd {
                command: SelfCommand::Update(_)
            }
        ));
        // `self-cmd` must NOT be accepted.
        assert!(Cli::try_parse_from(["yf", "self-cmd", "update"]).is_err());
    }

    #[test]
    fn self_update_flags_parse() {
        let cli =
            Cli::try_parse_from(["yf", "self", "update", "--check", "--json", "--binary-only"])
                .unwrap();
        let Command::SelfCmd {
            command: SelfCommand::Update(a),
        } = cli.command
        else {
            panic!("expected self update");
        };
        assert!(a.check && a.json && a.binary_only && !a.force);
    }

    #[test]
    fn self_install_from_build_flags_parse() {
        let cli = Cli::try_parse_from([
            "yf",
            "self",
            "install",
            "--from-build",
            "--debug",
            "--build",
            "--json",
        ])
        .unwrap();
        let Command::SelfCmd {
            command: SelfCommand::Install(a),
        } = cli.command
        else {
            panic!("expected self install");
        };
        assert!(a.from_build && a.debug && a.build && a.json && !a.release);
    }

    #[test]
    fn self_install_release_and_debug_conflict() {
        // --release and --debug are mutually exclusive.
        assert!(Cli::try_parse_from(["yf", "self", "install", "--release", "--debug"]).is_err());
    }

    #[test]
    fn self_uninstall_json_parses() {
        let cli = Cli::try_parse_from(["yf", "self", "uninstall", "--json", "--force"]).unwrap();
        let Command::SelfCmd {
            command: SelfCommand::Uninstall(a),
        } = cli.command
        else {
            panic!("expected self uninstall");
        };
        assert!(a.json && a.force);
    }
}
