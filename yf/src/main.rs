//! `yf` — Yoshiko Flow CLI entrypoint.
//!
//! This bead (1.1) lands the CLI skeleton (REQ-YF-CLI-001/002/003) and a fully
//! implemented `version` command (REQ-YF-CLI-004). Other subcommand bodies are
//! stubs for later beads; the process exits non-zero on any error.

mod beads_init;
mod cli;
mod cmd;
#[cfg(test)]
mod coverage;
mod dest;
mod dirs;
mod embed;
mod flow;
mod frontmatter;
mod marker;
#[cfg(test)]
mod marker_tests;
mod migrate;
#[cfg(test)]
mod parity;
mod preflight;
mod tool;

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
        Ok(code) => code,
        Err(err) => {
            eprintln!("error: {err:#}");
            std::process::ExitCode::FAILURE
        }
    }
}

fn run() -> Result<std::process::ExitCode> {
    let cli = Cli::parse();
    match cli.command {
        // Most subcommands either succeed or return an Err; map Ok(()) → SUCCESS.
        Command::Version(args) => {
            let r = cmd_version(&args);
            // Throttled, fail-open, vendor-only upgrade nudge — AFTER the real
            // output (stderr; never pollutes `--json` stdout). REQ 4.1.
            cmd::self_cmd::nag::maybe_notify(&dirs::Dirs::from_env());
            r.map(|()| std::process::ExitCode::SUCCESS)
        }
        Command::Skills { command } => {
            cmd_skills(&command).map(|()| std::process::ExitCode::SUCCESS)
        }
        // Doctor owns its exit code (like preflight): a failing required check is
        // a verdict, not an error.
        Command::Doctor(args) => {
            let code = cmd::doctor::run(&args)?;
            cmd::self_cmd::nag::maybe_notify(&dirs::Dirs::from_env());
            Ok(code)
        }
        // Preflight owns its exit code (REQ-YF-CLI-003: non-zero on a failing status).
        Command::Preflight(args) => preflight::run(&args.skill, args.json),
        Command::Migrate(args) => migrate::run(args.path, args.dry_run, args.json)
            .map(|()| std::process::ExitCode::SUCCESS),
        // `self` owns its exit code: a refusal (e.g. a Homebrew copy) is a verdict,
        // and a failed post-update refresh exits non-zero without rolling back.
        Command::SelfCmd { command } => cmd::self_cmd::run(&command),
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
