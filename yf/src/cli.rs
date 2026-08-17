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
    /// Deprecated alias for `yf harness skills` (install / upgrade / remove /
    /// status). Each verb delegates verb-for-verb to `yf harness skills <verb>`;
    /// kept until the next major release (REQ-YF-CLI-001/002).
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
    /// Provision harnesses: install skills (`harness skills`) and align config +
    /// deploy always-loaded rules (`harness tune`) for claude-code, codex,
    /// opencode, and pi (REQ-YF-TUNE / REQ-YF-CLI-001/002).
    Harness {
        #[command(subcommand)]
        command: HarnessCommand,
    },
    /// Print the `yf` version and build metadata.
    Version(VersionArgs),
}

/// `yf harness …` subcommands (plan-032/033).
#[derive(Debug, Subcommand)]
pub enum HarnessCommand {
    /// Align a harness's config AND deploy its always-loaded rules (two
    /// sub-operations per `--harness`). Config alignment covers claude-code +
    /// opencode (JSON) and codex (TOML delta-replay), honoring the kind-aware,
    /// idempotent, `Agent`-never-denied merge; rule deployment writes the
    /// minimized irreducible-core managed block into each harness's global-rule
    /// surface (claude-code `~/.claude/rules/`, codex/opencode/pi `AGENTS.md`).
    /// Pi config is deferred (rules still deploy). `--revert` reverses a prior
    /// tune via the sidecar `.yf/` manifest (REQ-YF-TUNE-012..025).
    Tune(HarnessTuneArgs),
    /// Manage embedded skills (install / upgrade / remove / status). This is the
    /// **canonical** home; the top-level `yf skills` group is a deprecated alias
    /// that delegates verb-for-verb here (REQ-YF-CLI-001/002).
    Skills {
        #[command(subcommand)]
        command: SkillsCommand,
    },
}

/// `yf harness tune` arguments (REQ-YF-TUNE-002/003/007).
#[derive(Debug, Args)]
pub struct HarnessTuneArgs {
    /// Target harness(es), repeatable (REQ-YF-TUNE-012). Each value drives both tune
    /// sub-operations: config alignment where a profile ships (claude-code / codex /
    /// opencode) and rule deployment for every harness with a rule target (incl. pi,
    /// which is config-deferred). An empty list defaults to `claude-code` (Issue 7.2
    /// replaces that default with harness auto-detection).
    #[arg(long)]
    pub harness: Vec<String>,

    /// Target project scope (`<git-root>/.claude/…`) instead of the user scope.
    /// The project default is the personal, gitignored `settings.local.json`.
    #[arg(long)]
    pub project: bool,

    /// With `--project`, target the shared, committed `settings.json` instead of
    /// the gitignored `settings.local.json`.
    #[arg(long, requires = "project")]
    pub committed: bool,

    /// Overwrite an existing scalar whose value differs from the recommendation
    /// (set-valued keys always union and never need `--force`). Never denies `Agent`.
    #[arg(long)]
    pub force: bool,

    /// Show the diff without writing anything.
    #[arg(long)]
    pub dry_run: bool,

    /// Run **only** the rule sub-operation, skipping config alignment entirely
    /// (`REQ-YF-TUNE-028`) — a named exception to `REQ-YF-TUNE-012`'s
    /// both-sub-operations rule.
    ///
    /// A rules-only run writes the rules aggregate to the correct per-harness
    /// target and **touches no config file** — neither creating one nor modifying
    /// an existing one — reporting config as `skipped` (distinct from pi's
    /// `deferred`, which reflects an absent profile rather than an operator
    /// request).
    ///
    /// This is what lets the `REQ-YF-SELF-005` install-time sync deploy its
    /// **safe half** (skills + rules, no security semantics) independently of its
    /// consent-bearing half, and is also how `CI` suppression is implemented.
    #[arg(long)]
    pub rules_only: bool,

    /// Authorize applying a profile entry declared `consent_required: true`, and
    /// creating a config file where none exists (`REQ-YF-SELF-008`, D-N).
    ///
    /// **Distinct from `--yes` on purpose.** `--yes` means "bypass the
    /// `REQ-YF-TUNE-023` multi-harness fan-out prompt" and keeps that meaning
    /// unchanged; it does **not** authorize a consent-bearing write. Two gates that
    /// authorize materially different things must not share one token — an operator
    /// passing `--yes` to silence a fan-out prompt would otherwise silently
    /// authorize a `bypassPermissions` write.
    #[arg(long)]
    pub allow_permissions_write: bool,

    /// Internal (not a CLI flag): is the `REQ-YF-SELF-008` consent gate ACTIVE for
    /// this invocation?
    ///
    /// Set by the `--tune` bridge (`tune_bridge_at`) — the programmatic entry point
    /// the install-time sync execs. A direct, interactive `yf harness tune` is a
    /// deliberate operator action and keeps its existing, tested contract
    /// unchanged; the gate exists to stop an *automatic* write reaching a machine
    /// that never asked for one.
    #[arg(skip)]
    pub consent_gated: bool,

    /// Reverse a prior `yf harness tune` (REQ-YF-TUNE-022): read the sidecar `.yf/`
    /// ownership manifest and undo **only** yf's own additions — restore each recorded
    /// prior scalar (or remove a key that had none), remove only the set elements yf
    /// unioned in, and remove the rule managed blocks (leaving operator prose). A
    /// **touched-since-tune guard** conservative-keeps (and reports) any key an operator
    /// hand-edited since the tune. Fail-safe on a malformed target; idempotent.
    #[arg(long)]
    pub revert: bool,

    /// Pi's always-loaded rule-file target (REQ-YF-TUNE-020). The verified default
    /// is `agents-md` (`~/.pi/agent/AGENTS.md`, resolved by Issue 1.5 against
    /// earendil-works/pi first-party docs). `append-system` is the documented
    /// override, retargeting to `~/.pi/agent/APPEND_SYSTEM.md` for an operator who
    /// wants it. Ignored for non-pi harnesses.
    #[arg(long, value_enum, default_value = "agents-md")]
    pub pi_rule_target: PiRuleTarget,

    /// Emit machine-readable JSON (REQ-YF-CLI-003).
    #[arg(long)]
    pub json: bool,
}

/// Pi's always-loaded global-rule file (REQ-YF-TUNE-020). The `agents-md` default
/// is the Issue 1.5-verified target (`~/.pi/agent/AGENTS.md`); `append-system` is
/// the explicit operator override (`~/.pi/agent/APPEND_SYSTEM.md`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, ValueEnum)]
pub enum PiRuleTarget {
    /// The verified default: `~/.pi/agent/AGENTS.md`.
    #[default]
    AgentsMd,
    /// The explicit override: `~/.pi/agent/APPEND_SYSTEM.md`.
    AppendSystem,
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

    /// Skip the install-time sync entirely (`REQ-YF-SELF-008`); swap the binary
    /// only, deploying no skills, no rules aggregate and no harness config.
    ///
    /// `--binary-only` is a **retained documented alias**: the flag predates the
    /// sync, when "skip the refresh" and "binary only" meant the same thing. It
    /// keeps working unchanged so existing usage and scripts do not break, but
    /// `--no-sync` is the name that describes what the flag now does, since the
    /// sync covers skills + rules + config rather than just the binary (D-J).
    #[arg(long = "no-sync", visible_alias = "binary-only")]
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

    /// Skip the install-time sync (`REQ-YF-SELF-008`); promote the binary only,
    /// deploying no skills, no rules aggregate and no harness config.
    ///
    /// The developer path has no `--binary-only` history to preserve, so it
    /// carries only the `--no-sync` spelling.
    #[arg(long = "no-sync")]
    pub no_sync: bool,

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

#[derive(Debug, PartialEq, Eq, Subcommand)]
pub enum SkillsCommand {
    /// Install skills into a scope/harness.
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

/// Deprecated harness surface (REQ-YF-CLI-002). Retained only as a **deprecated
/// alias** for `--harness`: `claude`→`claude-code`, `agents`→`agents`. New code
/// resolves destinations through the [`crate::harness_desc`] descriptor table.
#[derive(Debug, Clone, Copy, PartialEq, Eq, ValueEnum)]
#[value(rename_all = "lower")]
pub enum Surface {
    Claude,
    Agents,
}

impl Surface {
    /// The `--harness` id this deprecated surface maps to.
    pub fn harness_id(self) -> &'static str {
        match self {
            Surface::Claude => "claude-code",
            Surface::Agents => "agents",
        }
    }
}

/// Flags shared by every `skills` subcommand (REQ-YF-CLI-002/003).
#[derive(Debug, PartialEq, Eq, Args)]
pub struct SkillsArgs {
    /// Explicit skill names to act on (default: resolved set).
    pub names: Vec<String>,

    /// Install scope.
    #[arg(long, value_enum, default_value_t = Scope::User)]
    pub scope: Scope,

    /// Target harness(es) (repeatable): `claude-code`, `codex`, `opencode`, `pi`,
    /// `agents`. An unknown id falls back to the legacy `.<id>/skills` layout.
    /// When omitted, resolution defaults to `claude-code` (Issue 2.1); harness
    /// auto-detection lands in Issue 2.3.
    #[arg(long, value_name = "NAME")]
    pub harness: Vec<String>,

    /// Deprecated alias for `--harness` (`claude`→`claude-code`, `agents`→`agents`).
    /// Kept until the next major release; prefer `--harness`.
    #[arg(long, value_enum)]
    pub surface: Option<Surface>,

    /// Explicit destination path (overrides scope/harness resolution).
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

    /// After a successful install, run `yf harness tune` to align the harness
    /// settings to the yf skill contracts (install only). Off by default — without
    /// it, install reports that tuning is available and changes no settings.
    #[arg(long)]
    pub tune: bool,

    /// With `--tune`, run **only** the rule sub-operation and skip config
    /// alignment entirely (`REQ-YF-TUNE-028`). The bridge deploys skills and the
    /// rules aggregate and **touches no config file**.
    ///
    /// This is the form the `REQ-YF-SELF-005` install-time sync uses, so promoting
    /// a binary can never write a consent-bearing config key as a side effect.
    #[arg(long, requires = "tune")]
    pub rules_only: bool,

    /// With `--tune`, authorize a consent-bearing config write (`REQ-YF-SELF-008`,
    /// D-N) — applying an entry declared `consent_required: true`, or creating a
    /// config file where none exists. Distinct from `--yes`, which only bypasses
    /// the multi-harness fan-out prompt and never authorizes this.
    #[arg(long, requires = "tune")]
    pub allow_permissions_write: bool,

    /// Assume-yes: bypass the bounded-blast-radius confirmation that the
    /// no-`--harness --tune` multi-harness auto path prints before writing config
    /// and rules to every auto-detected harness (F6, REQ-YF-TUNE-023). Ignored
    /// unless the confirmation would otherwise fire.
    #[arg(long)]
    pub yes: bool,

    /// Emit machine-readable JSON (REQ-YF-CLI-003).
    #[arg(long)]
    pub json: bool,
}

impl SkillsArgs {
    /// The ordered, resolved set of harness ids this invocation targets. Explicit
    /// `--harness` values come first, then a deprecated `--surface` (mapped to its
    /// id); an empty selection defaults to `claude-code` (Issue 2.1). Per-path
    /// dedupe and multi-write are Issue 2.2; auto-detection is Issue 2.3.
    pub fn resolved_harnesses(&self) -> Vec<String> {
        let mut ids: Vec<String> = self.harness.clone();
        if let Some(s) = self.surface {
            ids.push(s.harness_id().to_string());
        }
        if ids.is_empty() {
            ids.push("claude-code".to_string());
        }
        ids
    }

    /// The single harness id used for destination resolution in Issue 2.1 (the
    /// first of [`Self::resolved_harnesses`]).
    pub fn primary_harness(&self) -> String {
        self.resolved_harnesses()
            .into_iter()
            .next()
            .unwrap_or_else(|| "claude-code".to_string())
    }
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

    /// Provenance-tracked formula GC (REQ-YF-DOCTOR-004). Its OWN affordance,
    /// distinct from `--repair` (a wedged-DB repair must never trigger deletion).
    /// Removes only `.beads/formulas/` entries the yf-owned staged-manifest marker
    /// attributes to yf that NO currently-embedded skill still declares; never a
    /// foreign/unmarked proto, and nothing at all when the marker is absent.
    #[arg(long)]
    pub prune_formulas: bool,
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

    // REQ-YF-CLI-002: the entire top-level `yf skills <verb>` group is a deprecated
    // alias that parses **identically** to the canonical `yf harness skills <verb>`
    // for every verb — so both dispatch through the same handler with identical
    // behavior. (`main::run` sends both arms through the same `cmd_skills`.)
    #[test]
    fn skills_alias_parses_identically_to_harness_skills() {
        for verb in ["install", "upgrade", "remove", "status"] {
            let alias = Cli::try_parse_from([
                "yf",
                "skills",
                verb,
                "--scope",
                "project",
                "--harness",
                "codex",
                "--dry-run",
            ])
            .unwrap();
            let canon = Cli::try_parse_from([
                "yf",
                "harness",
                "skills",
                verb,
                "--scope",
                "project",
                "--harness",
                "codex",
                "--dry-run",
            ])
            .unwrap();
            let alias_cmd = match alias.command {
                Command::Skills { command } => command,
                other => panic!("expected top-level skills, got {other:?}"),
            };
            let canon_cmd = match canon.command {
                Command::Harness {
                    command: HarnessCommand::Skills { command },
                } => command,
                other => panic!("expected harness skills, got {other:?}"),
            };
            assert_eq!(
                alias_cmd, canon_cmd,
                "`yf skills {verb}` must parse identically to `yf harness skills {verb}`"
            );
        }
    }

    // REQ-YF-CLI-002: `--surface` is retained as a deprecated alias for `--harness`.
    #[test]
    fn surface_flag_still_accepted_as_deprecated_alias() {
        let cli =
            Cli::try_parse_from(["yf", "harness", "skills", "install", "--surface", "agents"])
                .unwrap();
        let Command::Harness {
            command:
                HarnessCommand::Skills {
                    command: SkillsCommand::Install(a),
                },
        } = cli.command
        else {
            panic!("expected harness skills install");
        };
        assert_eq!(a.surface, Some(Surface::Agents));
        assert_eq!(a.primary_harness(), "agents");
    }

    /// REQ-YF-SELF-008 (D-J): `--no-sync` exists on **both** commands, and
    /// `--binary-only` is retained as a working alias on `self update` so existing
    /// usage does not break. The developer path carries only `--no-sync`.
    #[test]
    fn no_sync_on_both_commands_with_binary_only_alias() {
        let parse_update = |flag: &str| {
            let cli = Cli::try_parse_from(["yf", "self", "update", flag]).unwrap();
            let Command::SelfCmd {
                command: SelfCommand::Update(a),
            } = cli.command
            else {
                panic!("expected self update");
            };
            a.binary_only
        };
        // The new canonical name and the retained alias both set the same field.
        assert!(parse_update("--no-sync"), "--no-sync must be accepted");
        assert!(
            parse_update("--binary-only"),
            "--binary-only must keep working (documented alias)"
        );

        // The developer path takes --no-sync.
        let cli =
            Cli::try_parse_from(["yf", "self", "install", "--from-build", "--no-sync"]).unwrap();
        let Command::SelfCmd {
            command: SelfCommand::Install(a),
        } = cli.command
        else {
            panic!("expected self install");
        };
        assert!(a.no_sync);
        assert!(a.from_build);

        // ...and NOT --binary-only, which never existed there.
        assert!(
            Cli::try_parse_from(["yf", "self", "install", "--from-build", "--binary-only"])
                .is_err(),
            "--binary-only is not a self install flag"
        );

        // Absent the flag, the sync is ON by default (D-E).
        let cli = Cli::try_parse_from(["yf", "self", "install", "--from-build"]).unwrap();
        let Command::SelfCmd {
            command: SelfCommand::Install(a),
        } = cli.command
        else {
            panic!("expected self install");
        };
        assert!(!a.no_sync, "sync is on by default; --no-sync opts out");
    }

    /// REQ-YF-TUNE-028: `--rules-only` is accepted on `harness tune`, and on
    /// `harness skills install` only together with `--tune` (it modifies the
    /// bridge, so it is meaningless alone).
    #[test]
    fn rules_only_parses_on_tune_and_requires_tune_on_install() {
        let cli =
            Cli::try_parse_from(["yf", "harness", "tune", "--harness", "codex", "--rules-only"])
                .unwrap();
        let Command::Harness {
            command: HarnessCommand::Tune(a),
        } = cli.command
        else {
            panic!("expected harness tune");
        };
        assert!(a.rules_only);

        assert!(
            Cli::try_parse_from([
                "yf", "harness", "skills", "install", "--tune", "--rules-only"
            ])
            .is_ok(),
            "--rules-only is valid with --tune"
        );
        assert!(
            Cli::try_parse_from(["yf", "harness", "skills", "install", "--rules-only"]).is_err(),
            "--rules-only without --tune must be rejected"
        );
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
