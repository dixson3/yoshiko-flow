//! `yf` — Yoshiko Flow CLI entrypoint.
//!
//! This bead (1.1) lands the CLI skeleton (REQ-YF-CLI-001/002/003) and a fully
//! implemented `version` command (REQ-YF-CLI-004). Other subcommand bodies are
//! stubs for later beads; the process exits non-zero on any error.

mod cli;
mod cmd;
mod dest;
mod embed;
mod frontmatter;
mod marker;

use anyhow::Result;
use clap::Parser;

use cli::{Cli, Command, SkillsCommand, VersionArgs};

/// Short git hash captured at build time by `build.rs` ("unknown" if absent).
const GIT_HASH: &str = env!("YF_GIT_HASH");
/// Semver from Cargo (REQ-YF-CLI-004).
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// Human-readable version line, e.g. `0.1.0 (abc1234)`. clap prepends `yf `, so
/// `yf --version` / `-V` print `yf 0.1.0 (abc1234)`, matching `yf version`.
pub const VERSION_LINE: &str = concat!(env!("CARGO_PKG_VERSION"), " (", env!("YF_GIT_HASH"), ")");

fn main() -> std::process::ExitCode {
    match run() {
        Ok(()) => std::process::ExitCode::SUCCESS,
        Err(err) => {
            eprintln!("error: {err:#}");
            std::process::ExitCode::FAILURE
        }
    }
}

fn run() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Command::Version(args) => cmd_version(&args),
        Command::Skills { command } => cmd_skills(&command),
        Command::Doctor(args) => cmd::doctor::run(&args),
        Command::Preflight(args) => stub("preflight", args.json),
    }
}

/// REQ-YF-CLI-004: print the semver version plus git build metadata.
fn cmd_version(args: &VersionArgs) -> Result<()> {
    if args.json {
        let out = serde_json::json!({
            "version": VERSION,
            "git": GIT_HASH,
        });
        println!("{}", serde_json::to_string(&out)?);
    } else {
        println!("yf {VERSION_LINE}");
    }
    Ok(())
}

fn cmd_skills(command: &SkillsCommand) -> Result<()> {
    match command {
        SkillsCommand::Install(a) => cmd::install::run(a),
        SkillsCommand::Upgrade(a) => cmd::status::upgrade(a),
        SkillsCommand::Remove(a) => cmd::status::remove(a),
        SkillsCommand::Status(a) => cmd::status::status(a),
    }
}

/// Placeholder for subcommands implemented by later beads. Parses correctly and
/// returns Ok so the CLI shape is exercisable; real bodies arrive per-bead.
fn stub(command: &str, json: bool) -> Result<()> {
    if json {
        let out = serde_json::json!({
            "command": command,
            "status": "not_implemented",
            "message": format!("`yf {command}` is not yet implemented"),
        });
        println!("{}", serde_json::to_string(&out)?);
    } else {
        println!("`yf {command}` is not yet implemented");
    }
    Ok(())
}
