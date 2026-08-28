//! `yf harness` — align a harness's settings to the yf skill contracts
//! (REQ-YF-TUNE). The `profile` submodule owns the embedded machine-readable
//! settings profile; `merge` owns the kind-aware merge engine; `settings` owns
//! scope/path resolution and file read/write; `drift` owns the doc-agreement test.
//!
//! `yf harness tune --harness <name>` idempotently aligns a settings file to the
//! embedded profile: scalars are add-missing (conflict-reported unless `--force`),
//! set-valued keys are unioned (never removing user entries), `Agent` is never
//! denied, and a malformed file is refused rather than overwritten. `--dry-run`
//! prints the diff without writing; `--json` emits a machine-readable result.

use std::path::{Path, PathBuf};
use std::process::ExitCode;

use anyhow::Result;
use serde_json::{json, Value};

pub mod audit;
pub mod consent;
pub mod doc_agreement;
pub mod drift;
pub mod managed_block;
pub mod manifest;
pub mod merge;
pub mod minimize;
pub mod profile;
pub mod prune_private;
pub mod revert;
pub mod settings;
pub mod toml_adapter;

use crate::cli::HarnessTuneArgs;
use managed_block::RuleTargetKind;
use merge::Change;
use settings::{SettingsFormat, SettingsRead, TomlRead, TuneScope};

/// Run `yf harness tune` (Issue 7.1 — two-sub-operation orchestration,
/// REQ-YF-TUNE-012). For each requested harness `tune` runs **both** sub-operations
/// and reports a unified per-harness verdict:
///
/// - **(a) config alignment** — the kind-aware merge engine, where a config profile
///   ships (claude-code / codex / opencode). A harness with **no** config profile but
///   a rule target (pi) records a clean **config-deferred** result; a genuinely
///   unknown harness (no profile *and* no rule target) records a config **refusal**.
/// - **(b) rule deployment** — for **every** harness with a rule target: claude-code
///   aggregates the full `YOSHIKO_FLOW.md` into its `rules/` dir; codex/opencode/pi
///   place the minimized irreducible-core bundle as a managed block in their
///   `AGENTS.md` (pi honors `--pi-rule-target`).
///
/// Rule deployment is **not** gated on config success — a config-deferred pi (or a
/// malformed-config harness) still deploys rules; the two sub-operations are
/// independent. The command's exit code is `FAILURE` iff any harness's verdict is a
/// failure (a config or rule refusal), else `SUCCESS`.
///
/// `--harness` is repeatable (deduped, order-preserving); an empty list defaults to
/// `claude-code` (Issue 7.2 replaces that default with auto-detection).
pub fn run(args: &HarnessTuneArgs) -> Result<ExitCode> {
    // `--revert` reverses a prior tune (Issue 8.2, REQ-YF-TUNE-022) rather than
    // aligning — a fully separate flow driven off the sidecar `.yf/` ownership
    // manifest, not the profile/merge engine.
    if args.revert {
        return revert::run(args);
    }

    let scope = TuneScope::resolve(args.project, args.committed);
    let home = home_dir();
    let root = crate::dest::git_root_or_cwd();

    let mut verdicts = Vec::new();
    for harness in resolve_harness_list(args) {
        verdicts.push(tune_one_harness_at(args, &harness, scope, &home, &root)?);
    }

    let any_failure = verdicts.iter().any(HarnessVerdict::is_failure);
    report_verdicts(args, &verdicts);
    Ok(if any_failure {
        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    })
}

/// The harnesses `tune` acts on: the deduped, order-preserving `--harness` list, or
/// `claude-code` when none is given. (Issue 7.2 replaces the empty-list default with
/// harness auto-detection + a blast-radius confirmation.)
fn resolve_harness_list(args: &HarnessTuneArgs) -> Vec<String> {
    if args.harness.is_empty() {
        return vec!["claude-code".to_string()];
    }
    let mut seen = std::collections::BTreeSet::new();
    args.harness
        .iter()
        .filter(|h| seen.insert((*h).clone()))
        .cloned()
        .collect()
}

/// `$HOME`, falling back to cwd — total resolution (mirrors [`settings`]/[`dest`]).
fn home_dir() -> PathBuf {
    std::env::var_os("HOME")
        .map(PathBuf::from)
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
}

/// The config sub-operation's outcome for one harness (REQ-YF-TUNE-012).
#[derive(Debug)]
enum ConfigOutcome {
    /// A config profile exists and the align ran: `status` is `dry_run` / `written` /
    /// `already_aligned`; `report` carries the change set for the verdict.
    Aligned {
        status: &'static str,
        path: PathBuf,
        wrote: bool,
        report: merge::MergeReport,
    },
    /// No config profile ships for this harness (pi, REQ-YF-TUNE-017), but it has a
    /// rule target — config is **deferred**, cleanly, NOT a failure.
    Deferred { reason: String },
    /// The consent gate (`REQ-YF-SELF-008`, plan-042) blocked an automatic config
    /// write: the file would be CREATED, and/or the change set touches an entry
    /// declared `consent_required: true`. The delta is reported and NOTHING is
    /// written. Not a refusal of the harness — a request for authorization.
    ConsentRequired {
        path: PathBuf,
        reasons: Vec<consent::ConsentReason>,
        report: merge::MergeReport,
    },
    /// The operator asked for a **rules-only** run (`--rules-only`,
    /// REQ-YF-TUNE-028), so config alignment did not run at all. Distinct from
    /// [`ConfigOutcome::Deferred`]: deferred means *no profile ships*, skipped means
    /// *a profile may well ship but was not consulted*. Never a failure, and the
    /// config file is guaranteed untouched.
    Skipped,
    /// A refusal for this harness's config sub-op — a malformed/unparseable config
    /// (fail-safe, never overwritten) or a genuinely unknown harness.
    Refused { reason: String, message: String },
}

/// The rule sub-operation's outcome for one harness (REQ-YF-TUNE-012).
#[derive(Debug)]
enum RuleOutcome {
    /// claude-code (rules-dir harness): the full `YOSHIKO_FLOW.md` aggregate.
    Aggregate {
        path: PathBuf,
        upserted: usize,
        pruned: usize,
        migrated: usize,
        dry_run: bool,
    },
    /// codex/opencode/pi (AGENTS.md harness): the minimized managed block.
    Block {
        path: PathBuf,
        action: &'static str,
        wrote: bool,
        /// Codex block-size-budget warning (REQ-YF-TUNE-027): `Some(msg)` when the
        /// projected `~/.codex/AGENTS.md` approaches `project_doc_max_bytes`. Only
        /// codex carries a cap; opencode/pi are always `None`.
        budget_warning: Option<String>,
    },
    /// No rule target maps to this harness (a genuinely unknown harness).
    NotApplicable,
    /// A managed-block refusal — the target file carries partial/duplicate/out-of-order
    /// markers, so the deploy fail-safed rather than corrupt operator prose.
    Refused { message: String },
}

/// The unified per-harness verdict: both sub-operations plus the harness id.
#[derive(Debug)]
struct HarnessVerdict {
    harness: String,
    config: ConfigOutcome,
    rules: RuleOutcome,
}

impl HarnessVerdict {
    /// A harness verdict is a failure iff either sub-op refused. A config-**deferred**
    /// (pi) is NOT a failure — that is the whole point of Issue 7.1.
    fn is_failure(&self) -> bool {
        matches!(self.config, ConfigOutcome::Refused { .. })
            || matches!(self.rules, RuleOutcome::Refused { .. })
    }
}

/// Run both sub-operations for one harness over explicit `home`/`root` anchors
/// (env-free — the unit-test seam). REQ-YF-TUNE-012.
fn tune_one_harness_at(
    args: &HarnessTuneArgs,
    harness: &str,
    scope: TuneScope,
    home: &Path,
    root: &Path,
) -> Result<HarnessVerdict> {
    // REQ-YF-TUNE-028 (a named exception to REQ-YF-TUNE-012's both-sub-operations
    // rule): `--rules-only` skips config alignment ENTIRELY. The short-circuit is
    // here — before `compute_config_subop` — precisely so no config code path runs
    // at all: nothing reads the settings file, nothing computes a merge, and
    // nothing can write. That is what makes "touches no config file" a structural
    // property rather than a promise about the write step.
    let config = if args.rules_only {
        ConfigOutcome::Skipped
    } else {
        compute_config_subop(args, harness, scope, home, root)?
    };
    let rules = compute_rules_subop(args, harness, scope, home, root)?;
    // Epic 8 seam (Issue 8.1): record what this tune wrote into the sidecar `.yf/`
    // ownership manifest so Issue 8.2's `--revert` can reverse it precisely. A
    // dry-run records nothing (the guard lives in `manifest::record_tune`).
    record_manifest(harness, scope, home, root, &config, &rules, args.dry_run)?;
    Ok(HarnessVerdict {
        harness: harness.to_string(),
        config,
        rules,
    })
}

/// Record the tune's ownership into the sidecar `.yf/` manifest (REQ-YF-TUNE-021).
/// Derives the per-sub-op ownership records from the config/rule verdicts:
///
/// - **config** — an `Aligned` outcome contributes the [`merge::MergeReport`]'s
///   added scalars (prior + written) and set-union deltas; `Deferred`/`Refused`
///   contribute nothing.
/// - **rules** — a `Block` outcome contributes the file + BEGIN/END markers; an
///   `Aggregate` outcome contributes the file as a whole-file aggregate;
///   `NotApplicable`/`Refused` contribute nothing.
///
/// A dry-run writes no manifest (the guard is inside [`manifest::record_tune`]).
fn record_manifest(
    harness: &str,
    scope: TuneScope,
    home: &Path,
    root: &Path,
    config: &ConfigOutcome,
    rules: &RuleOutcome,
    dry_run: bool,
) -> Result<()> {
    let config_rec = match config {
        ConfigOutcome::Aligned { path, report, .. } => {
            Some(manifest::config_record_from_report(path, report))
        }
        ConfigOutcome::Deferred { .. }
        | ConfigOutcome::Refused { .. }
        | ConfigOutcome::Skipped
        | ConfigOutcome::ConsentRequired { .. } => None,
    };
    // REQ-YF-TUNE-029 (plan-044 #154): record the sha256 of the rule file AS YF
    // WROTE IT, on EVERY rules write. This is what revert's touched-since-tune
    // guard compares against; without it revert cannot distinguish "yf's own
    // output" from "the operator's edits" and deletes either one.
    //
    // Read back from disk rather than hashing the intended body: for a `block`
    // kind the file also holds operator prose, so the intended body is not the
    // file. Under --dry-run nothing was written, so there is nothing to record.
    let rule_sha = |path: &std::path::Path| -> Option<String> {
        if dry_run {
            return None;
        }
        std::fs::read(path)
            .ok()
            .map(|b| crate::cmd::self_cmd::update::sha256_hex(&b))
    };
    let rule_rec = match rules {
        RuleOutcome::Block { path, .. } => Some(manifest::RuleRecord {
            path: path.display().to_string(),
            kind: "block".to_string(),
            begin_marker: Some(managed_block::BEGIN_MARKER.to_string()),
            end_marker: Some(managed_block::END_MARKER.to_string()),
            sha256: rule_sha(path),
        }),
        RuleOutcome::Aggregate { path, .. } => Some(manifest::RuleRecord {
            path: path.display().to_string(),
            kind: "aggregate".to_string(),
            begin_marker: None,
            end_marker: None,
            sha256: rule_sha(path),
        }),
        RuleOutcome::NotApplicable | RuleOutcome::Refused { .. } => None,
    };
    manifest::record_tune(harness, scope, home, root, config_rec, rule_rec, dry_run)
}

/// Evaluate the `REQ-YF-SELF-008` consent gate for one harness, returning
/// `Some(ConfigOutcome::ConsentRequired)` when the automatic write is blocked.
///
/// Returns `None` — i.e. proceed — when the gate is inactive (a direct, interactive
/// `yf harness tune`), when the operator passed the explicit D-N flag, or when the
/// change set is genuinely benign.
///
/// **`--yes` is deliberately not consulted.** It authorizes bypassing the
/// `REQ-YF-TUNE-023` multi-harness fan-out prompt and nothing else; letting it
/// satisfy this gate would mean an operator silencing a fan-out prompt had
/// unknowingly authorized a `bypassPermissions` write (D-N).
fn gate_config(
    args: &HarnessTuneArgs,
    profile: &profile::Profile,
    path: &Path,
) -> Option<ConfigOutcome> {
    if !args.consent_gated || args.allow_permissions_write {
        return None;
    }
    // The dry-run pass before the real one (Issue 3.4). Pure: this computes the
    // change set via `merge` and writes nothing — `record_manifest` is separately
    // dry-run-guarded, so no ownership record is produced either.
    let read = match profile.format {
        settings::SettingsFormat::Json => settings::read_settings(path),
        settings::SettingsFormat::Toml => {
            match settings::read_value_for_format(path, settings::SettingsFormat::Toml) {
                Some(v) => SettingsRead::Parsed(v),
                None => SettingsRead::Absent,
            }
        }
    };
    let report = consent::compute_change_set(profile, &read);
    match consent::evaluate(profile, &read, &report, &path.display().to_string()) {
        consent::ConsentVerdict::AutoApply => None,
        consent::ConsentVerdict::Required(reasons) => Some(ConfigOutcome::ConsentRequired {
            path: path.to_path_buf(),
            reasons,
            report,
        }),
    }
}

/// The config sub-op: align the config where a profile ships; else defer (pi — a rule
/// target but no config profile) or refuse (a genuinely unknown harness).
fn compute_config_subop(
    args: &HarnessTuneArgs,
    harness: &str,
    scope: TuneScope,
    home: &Path,
    root: &Path,
) -> Result<ConfigOutcome> {
    match profile::load_profile(harness)? {
        Some(profile) => {
            let path = settings::settings_path_at(&profile, scope, home, root);

            // REQ-YF-TUNE-030 (plan-054 / EXP-003): warn when a HIGHER-PRECEDENCE layer that
            // the harness itself reads exists on disk and will SHADOW what we are about to
            // write. Measured: opencode reads `opencode.jsonc` ahead of `opencode.json`, so a
            // tune of `opencode.json` can complete successfully and change nothing the harness
            // obeys. The shadowed keys are named explicitly — "config may be shadowed" with no
            // path is a warning the operator cannot act on.
            //
            // It WARNS rather than refusing: the write is still correct and still what the
            // operator asked for, and a higher layer is a legitimate configuration the operator
            // may have authored deliberately. What is not acceptable is doing it silently.
            let shadows = settings::shadowing_layers_at(&profile, scope, home, root);
            if !shadows.is_empty() {
                eprintln!(
                    "warning: {} reads {} at HIGHER precedence than {}, so these keys may be \
                     overridden by a layer yf does not write:",
                    harness,
                    shadows
                        .iter()
                        .map(|p| p.display().to_string())
                        .collect::<Vec<_>>()
                        .join(", "),
                    path.display(),
                );
                for e in &profile.entries {
                    eprintln!("  {}", e.path);
                }
            }

            // REQ-YF-SELF-008: the consent gate. Active only on the `--tune` bridge
            // (the sync's entry point) and satisfiable only by the explicit D-N
            // flag — never by `--yes`, which is not consulted here at all.
            if let Some(blocked) = gate_config(args, &profile, &path) {
                return Ok(blocked);
            }
            compute_config(args, &profile, &path)
        }
        None if managed_block::rule_target(harness).is_some() => Ok(ConfigOutcome::Deferred {
            reason: "no config profile ships for this harness — config tuning deferred".to_string(),
        }),
        None => Ok(ConfigOutcome::Refused {
            reason: "unknown-harness".to_string(),
            message: format!(
                "no settings profile for harness '{harness}'. Available: {}",
                profile::available_harnesses().join(", ")
            ),
        }),
    }
}

/// The rule sub-op: deploy this harness's always-loaded rules. Branches on the
/// rule-target **kind** — a rules-dir harness (claude-code) gets the full aggregate; an
/// AGENTS.md harness (codex/opencode/pi) gets the minimized managed block. An unmapped
/// harness is [`RuleOutcome::NotApplicable`]. A managed-block marker refusal is captured
/// as [`RuleOutcome::Refused`] (fail-safe — the file is never corrupted) rather than
/// aborting the whole multi-harness loop.
fn compute_rules_subop(
    args: &HarnessTuneArgs,
    harness: &str,
    scope: TuneScope,
    home: &Path,
    root: &Path,
) -> Result<RuleOutcome> {
    let Some(target) = managed_block::effective_rule_target(harness, args.pi_rule_target) else {
        return Ok(RuleOutcome::NotApplicable);
    };
    match target.kind {
        RuleTargetKind::RulesDir => {
            let rules_dir = target.resolve_at(scope, home, root);
            let flow = deploy_rules_aggregate(args, &rules_dir)?;
            Ok(RuleOutcome::Aggregate {
                path: flow.flow_file,
                upserted: flow.upserted.len(),
                pruned: flow.pruned.len(),
                migrated: flow.migrated.len(),
                dry_run: args.dry_run,
            })
        }
        RuleTargetKind::AgentsMd | RuleTargetKind::AppendSystem => {
            let bundle = minimize::irreducible_core_bundle()?;
            let path = target.resolve_at(scope, home, root);
            // Codex block-size budget (REQ-YF-TUNE-027): warn (never block) when the
            // projected ~/.codex/AGENTS.md approaches project_doc_max_bytes. Only codex
            // has this cap; opencode/pi carry no budget warning.
            let budget_warning = if harness == "codex" {
                codex_budget_warning_for(&path, &bundle)
            } else {
                None
            };
            match managed_block::deploy_block(&path, &bundle, args.dry_run) {
                Ok(d) => Ok(RuleOutcome::Block {
                    path: d.path,
                    action: d.action,
                    wrote: d.wrote,
                    budget_warning,
                }),
                Err(e) => Ok(RuleOutcome::Refused {
                    message: e.to_string(),
                }),
            }
        }
    }
}

/// Codex block-size-budget warning for a resolved `~/.codex/AGENTS.md` path
/// (REQ-YF-TUNE-027): read the sibling `config.toml` for the **effective on-disk** cap
/// (default 32768 when absent — not the profile's 65536) and the existing AGENTS.md
/// content, project the post-deploy size through the deploy engine, and return a warning
/// iff it is at/above the ≥90% threshold. Read-only — never truncates or blocks.
fn codex_budget_warning_for(agents_path: &Path, bundle: &str) -> Option<String> {
    let existing = std::fs::read_to_string(agents_path).unwrap_or_default();
    let config_path = agents_path.with_file_name("config.toml");
    let config_text = std::fs::read_to_string(&config_path).ok();
    let cap = managed_block::codex_effective_doc_max_bytes(config_text.as_deref());
    let budget = managed_block::codex_budget(&existing, bundle, cap);
    budget
        .over_threshold
        .then(|| managed_block::codex_budget_warning(&budget))
}

/// The tune-side **rule-deploy** sub-operation (REQ-YF-FLOW-007): deploy the
/// aggregated always-loaded ruleset (`YOSHIKO_FLOW.md`) into `rules_dir` over the
/// full embedded skill set. This is the **relocation** of the aggregation that
/// formerly ran at `yf harness skills install` time (Issue 3.1). The aggregation
/// engine ([`crate::cmd::common::install_rules_aggregate`]) is **unchanged** —
/// byte-stable serialization, reconcile-prune, `sha256` sections — so the aggregate
/// tune writes is byte-identical to the old install-time output for the same
/// acted-on skill set. `--dry-run` projects the change set without writing.
///
/// **Epic 6 seam (Issues 6.1/6.2).** This is the extension point for rule
/// minimization + per-harness managed-block deployment: the full aggregate written
/// here is the source the minimization classifier ([`minimize`]) reduces to the
/// irreducible-core bundle ([`minimize::irreducible_core_bundle`]) that Issue 6.2's
/// managed-block engine places per harness (claude-code `rules/`, codex/opencode
/// `AGENTS.md`). Issue 3.1 is strictly the relocation — the full aggregation now
/// runs from `tune`.
fn deploy_rules_aggregate(
    args: &HarnessTuneArgs,
    rules_dir: &Path,
) -> Result<crate::cmd::common::FlowWriteResult> {
    let acted = tune_acted_skills();
    crate::cmd::common::install_rules_aggregate(&acted, rules_dir, args.dry_run)
}

/// The skill set tune aggregates the always-loaded ruleset over: **all** embedded
/// skills (`tune` has no per-skill selection — it deploys the complete aggregate).
/// Factored out so the byte-stability test can drive the engine over the same set.
fn tune_acted_skills() -> Vec<String> {
    crate::embed::skill_names()
}

/// Compute the config-align sub-operation over an explicit resolved `path` (env-free,
/// **no printing** — Issue 7.1 folds the result into the unified per-harness verdict).
/// Dispatches read/merge/write on `profile.format` (REQ-YF-TUNE-014): JSON via the
/// existing `serde_json` path, TOML via the [`toml_adapter`] delta-replay path.
fn compute_config(
    args: &HarnessTuneArgs,
    profile: &profile::Profile,
    path: &Path,
) -> Result<ConfigOutcome> {
    match profile.format {
        SettingsFormat::Json => compute_config_json(args, profile, path),
        SettingsFormat::Toml => compute_config_toml(args, profile, path),
    }
}

/// Status label for a completed align, from the dry-run flag + whether bytes changed.
fn align_status(dry_run: bool, wrote: bool) -> &'static str {
    if dry_run {
        "dry_run"
    } else if wrote {
        "written"
    } else {
        "already_aligned"
    }
}

/// The JSON config-align: fail-safe `serde_json` read, kind-aware merge over the
/// `Value`, pretty-write. Behavior-identical to the pre-7.1 `run_core_json`, minus the
/// stdout report (folded into the verdict).
fn compute_config_json(
    args: &HarnessTuneArgs,
    profile: &profile::Profile,
    path: &Path,
) -> Result<ConfigOutcome> {
    // Fail-safe read (REQ-YF-TUNE-006): refuse a malformed file, never overwrite.
    let existing = match settings::read_settings(path) {
        SettingsRead::Absent => Value::Object(Default::default()),
        SettingsRead::Parsed(v) if v.is_object() => v,
        SettingsRead::Parsed(_) => {
            return Ok(ConfigOutcome::Refused {
                reason: "malformed".to_string(),
                message: format!(
                    "{}: top-level JSON is not an object; refusing to overwrite",
                    path.display()
                ),
            });
        }
        SettingsRead::Malformed(msg) => {
            return Ok(ConfigOutcome::Refused {
                reason: "malformed".to_string(),
                message: format!("unparseable settings file; refusing to overwrite ({msg})"),
            });
        }
    };

    // Kind-aware merge (REQ-YF-TUNE-004/005).
    let (merged, report) = merge::merge(&existing, profile, args.force);
    let mutated = report.mutated();

    // Write unless --dry-run (REQ-YF-TUNE-007) and unless already aligned.
    let wrote = if !args.dry_run && mutated {
        settings::write_settings(path, &merged)
            .map_err(|e| anyhow::anyhow!("failed to write {}: {e}", path.display()))?;
        true
    } else {
        false
    };

    Ok(ConfigOutcome::Aligned {
        status: align_status(args.dry_run, wrote),
        path: path.to_path_buf(),
        wrote,
        report,
    })
}

/// The TOML config-align (REQ-YF-TUNE-014): fail-safe TOML read, then the
/// [`toml_adapter`] delta-replay merge/write. The merge **decision** still runs on a
/// `serde_json::Value` (the unchanged engine); only the write source differs — the
/// trivia-preserving `config.toml` document, so operator comments / key order survive
/// (REQ-YF-TUNE-013).
fn compute_config_toml(
    args: &HarnessTuneArgs,
    profile: &profile::Profile,
    path: &Path,
) -> Result<ConfigOutcome> {
    // Fail-safe read (REQ-YF-TUNE-006): refuse a malformed file, never overwrite.
    let text = match settings::read_toml(path) {
        TomlRead::Absent => String::new(),
        TomlRead::Parsed(t) => t,
        TomlRead::Malformed(msg) => {
            return Ok(ConfigOutcome::Refused {
                reason: "malformed".to_string(),
                message: format!("unparseable config file; refusing to overwrite ({msg})"),
            });
        }
    };

    // Kind-aware merge via delta-replay (REQ-YF-TUNE-004/005/013). Err mirrors the
    // Malformed refusal (a defensive second guard around parse).
    let (out, report) = match toml_adapter::merge_toml_text(&text, profile, args.force) {
        Ok(v) => v,
        Err(msg) => {
            return Ok(ConfigOutcome::Refused {
                reason: "malformed".to_string(),
                message: format!("unparseable config file; refusing to overwrite ({msg})"),
            });
        }
    };
    let mutated = report.mutated();

    // Write unless --dry-run (REQ-YF-TUNE-007) and unless already aligned.
    let wrote = if !args.dry_run && mutated {
        settings::write_text(path, &out)
            .map_err(|e| anyhow::anyhow!("failed to write {}: {e}", path.display()))?;
        true
    } else {
        false
    };

    Ok(ConfigOutcome::Aligned {
        status: align_status(args.dry_run, wrote),
        path: path.to_path_buf(),
        wrote,
        report,
    })
}

/// The install-time **config-only** Claude Code tune library call (REQ-YF-TUNE-010)
/// over an explicit `path`: read fail-safe, merge (never force), write if mutated,
/// return a JSON summary. A malformed file yields a `refused` summary rather than
/// an error, so a `--tune` install never crashes on a hand-broken settings file.
///
/// Issue 7.2's `--tune` **bridge** ([`tune_for_install_harnesses`]) supersedes the
/// production single-harness install-time tune (it runs BOTH sub-operations per
/// resolved harness). This env-free core is retained as the REQ-YF-TUNE-010 unit
/// seam for the fail-safe config-align contract.
#[cfg(test)]
fn tune_for_install_at(
    profile: &profile::Profile,
    scope: TuneScope,
    path: &std::path::Path,
) -> Result<Value> {
    let existing = match settings::read_settings(path) {
        SettingsRead::Absent => Value::Object(Default::default()),
        SettingsRead::Parsed(v) if v.is_object() => v,
        SettingsRead::Parsed(_) | SettingsRead::Malformed(_) => {
            return Ok(json!({
                "status": "refused",
                "reason": "malformed",
                "path": path.display().to_string(),
            }));
        }
    };
    let (merged, report) = merge::merge(&existing, profile, false);
    let wrote = if report.mutated() {
        settings::write_settings(path, &merged)
            .map_err(|e| anyhow::anyhow!("failed to write {}: {e}", path.display()))?;
        true
    } else {
        false
    };
    Ok(json!({
        "status": if wrote { "written" } else { "already_aligned" },
        "harness": profile.harness,
        "scope": scope.label(),
        "path": path.display().to_string(),
        "wrote": wrote,
        "changes": report.changes.len(),
        "conflicts": report.conflicts().len(),
    }))
}

/// The `--tune` **bridge** (`yf harness skills install --tune`, REQ-YF-TUNE-023):
/// run BOTH tune sub-operations (config alignment + rule deployment) for every
/// harness in `harnesses` and return a combined summary the install caller folds
/// into its own output. This is the multi-harness generalization of
/// [`tune_for_install`] — it runs the full per-harness verdict machinery
/// (`config` + `rules`), not config-only. Never forces; `dry_run` projects the
/// writes without touching disk. Env-based (real `$HOME` / git-root); the
/// env-free core is [`tune_bridge_at`].
pub fn tune_for_install_harnesses(
    harnesses: &[String],
    project: bool,
    dry_run: bool,
    rules_only: bool,
    allow_permissions_write: bool,
) -> Result<Value> {
    let scope = TuneScope::resolve(project, false);
    let home = home_dir();
    let root = crate::dest::git_root_or_cwd();
    tune_bridge_at(
        harnesses,
        scope,
        &home,
        &root,
        dry_run,
        rules_only,
        allow_permissions_write,
    )
}

/// Test seam for the `consent_gate` evidence module: run the bridge for one
/// harness under a sandboxed `home`, returning the summary JSON.
#[cfg(test)]
pub(crate) fn tune_bridge_at_for_test(
    harnesses: &[String],
    home: &Path,
    allow_permissions_write: bool,
) -> Value {
    tune_bridge_at(
        harnesses,
        TuneScope::User,
        home,
        home,
        /*dry_run=*/ false,
        /*rules_only=*/ false,
        allow_permissions_write,
    )
    .expect("bridge must not error")
}

/// Env-free core of [`tune_for_install_harnesses`] (the test seam): loop
/// [`tune_one_harness_at`] over `harnesses` at explicit `home`/`root` anchors and
/// build the combined `--tune`-bridge JSON summary. Runs both sub-operations per
/// harness; `dry_run` projects without writing. `rules_only` (REQ-YF-TUNE-028)
/// runs the rule sub-operation alone, so the bridge touches no config file.
fn tune_bridge_at(
    harnesses: &[String],
    scope: TuneScope,
    home: &Path,
    root: &Path,
    dry_run: bool,
    rules_only: bool,
    allow_permissions_write: bool,
) -> Result<Value> {
    let bridge_args = HarnessTuneArgs {
        harness: harnesses.to_vec(),
        project: matches!(scope, TuneScope::ProjectLocal | TuneScope::ProjectCommitted),
        committed: matches!(scope, TuneScope::ProjectCommitted),
        force: false,
        dry_run,
        rules_only,
        allow_permissions_write,
        // The bridge IS the sync's entry point, so the consent gate is active here.
        consent_gated: true,
        revert: false,
        pi_rule_target: crate::cli::PiRuleTarget::AgentsMd,
        json: true,
    };
    let mut verdicts = Vec::new();
    for harness in harnesses {
        verdicts.push(tune_one_harness_at(
            &bridge_args,
            harness,
            scope,
            home,
            root,
        )?);
    }
    let harnesses_json: Vec<Value> = verdicts
        .iter()
        .map(|v| {
            json!({
                "harness": v.harness,
                "config": config_json(&v.config),
                "rules": rules_json(&v.rules),
            })
        })
        .collect();
    // A blocked consent gate is NOT `ok`: the sync's caller-side check treats any
    // non-"ok" status as a failure (REQ-YF-SELF-008), which is exactly right here —
    // config was not deployed, and reporting "ok" would be the same exit-0
    // false-success shape this plan exists to close.
    let consent_blocked = verdicts
        .iter()
        .any(|v| matches!(v.config, ConfigOutcome::ConsentRequired { .. }));
    let status = if verdicts.iter().any(HarnessVerdict::is_failure) {
        "refused"
    } else if consent_blocked {
        "consent_required"
    } else if dry_run {
        "dry_run"
    } else {
        "ok"
    };
    Ok(json!({
        "status": status,
        "scope": scope.label(),
        "harnesses": harnesses_json,
    }))
}

/// The resolved config + rule write targets for one harness — the "blast radius"
/// the bounded-blast-radius confirmation surfaces (F6, REQ-YF-TUNE-023). `config`
/// is `None` where no config profile ships (pi); `rules` is `None` for a harness
/// with no rule target.
#[derive(Debug)]
pub struct TargetPlan {
    pub harness: String,
    pub config: Option<PathBuf>,
    pub rules: Option<PathBuf>,
}

/// Compute the resolved write targets for `harnesses` without touching disk — the
/// read-only projection the `--tune` bridge prints for confirmation before it
/// fans out any write. Env-based; env-free core is [`plan_targets_at`].
pub fn plan_targets(harnesses: &[String], project: bool) -> Result<Vec<TargetPlan>> {
    let scope = TuneScope::resolve(project, false);
    let home = home_dir();
    let root = crate::dest::git_root_or_cwd();
    plan_targets_at(harnesses, scope, &home, &root)
}

/// Env-free core of [`plan_targets`] (the test seam): resolve each harness's config
/// path (where a profile ships) and rule-target path against explicit anchors,
/// writing nothing.
fn plan_targets_at(
    harnesses: &[String],
    scope: TuneScope,
    home: &Path,
    root: &Path,
) -> Result<Vec<TargetPlan>> {
    let mut out = Vec::new();
    for harness in harnesses {
        let config = profile::load_profile(harness)?
            .map(|p| settings::settings_path_at(&p, scope, home, root));
        let rules =
            managed_block::effective_rule_target(harness, crate::cli::PiRuleTarget::AgentsMd)
                .map(|t| t.resolve_at(scope, home, root));
        out.push(TargetPlan {
            harness: harness.clone(),
            config,
            rules,
        });
    }
    Ok(out)
}

/// The `--json`/report shape for a [`TargetPlan`] set — the surfaced blast radius.
pub fn target_plan_json(plan: &[TargetPlan]) -> Value {
    let targets: Vec<Value> = plan
        .iter()
        .map(|t| {
            json!({
                "harness": t.harness,
                "config": t.config.as_ref().map(|p| p.display().to_string()),
                "rules": t.rules.as_ref().map(|p| p.display().to_string()),
            })
        })
        .collect();
    json!(targets)
}

/// Emit the unified per-harness verdict — one object carrying **both** sub-operations
/// per harness under `--json`, or a readable per-harness block otherwise
/// (REQ-YF-TUNE-012). The overall `status` is `refused` iff any harness verdict failed.
fn report_verdicts(args: &HarnessTuneArgs, verdicts: &[HarnessVerdict]) {
    if args.json {
        let harnesses: Vec<Value> = verdicts
            .iter()
            .map(|v| {
                json!({
                    "harness": v.harness,
                    "config": config_json(&v.config),
                    "rules": rules_json(&v.rules),
                })
            })
            .collect();
        let status = if verdicts.iter().any(HarnessVerdict::is_failure) {
            "refused"
        } else {
            "ok"
        };
        let out = json!({
            "command": "harness tune",
            "status": status,
            "harnesses": harnesses,
        });
        println!("{}", serde_json::to_string(&out).unwrap_or_default());
        return;
    }

    for v in verdicts {
        println!("yf harness tune [{}]", v.harness);
        render_config_human(&v.config);
        render_rules_human(&v.rules);
    }
}

/// Human-mode rendering of the config sub-op.
fn render_config_human(config: &ConfigOutcome) {
    match config {
        ConfigOutcome::Aligned {
            status,
            path,
            report,
            ..
        } => {
            println!("  config: {status} → {}", path.display());
            for c in &report.changes {
                println!("    {}", describe(c));
            }
            let conflicts = report.conflicts().len();
            if conflicts > 0 {
                println!("    {conflicts} conflict(s) left untouched — re-run with --force.");
            }
        }
        ConfigOutcome::Deferred { reason } => println!("  config: deferred ({reason})"),
        ConfigOutcome::Skipped => {
            println!("  config: skipped (--rules-only; no config file read or written)")
        }
        ConfigOutcome::ConsentRequired {
            path,
            reasons,
            report,
        } => {
            println!(
                "  config: CONSENT REQUIRED — nothing written to {}",
                path.display()
            );
            for r in reasons {
                println!("    - {}", r.describe());
            }
            // The per-key delta, so a bypassPermissions write is never invisible.
            for line in consent::render_delta(report) {
                println!("      {line}");
            }
            println!(
                "    re-run with {} to authorize (NOT --yes, which only bypasses the \
                 multi-harness fan-out prompt)",
                consent::CONSENT_FLAG
            );
        }
        ConfigOutcome::Refused { reason, message } => {
            println!("  config: refused ({reason}): {message}")
        }
    }
}

/// Human-mode rendering of the rule sub-op.
fn render_rules_human(rules: &RuleOutcome) {
    match rules {
        RuleOutcome::Aggregate {
            path,
            upserted,
            pruned,
            migrated,
            dry_run,
        } => {
            let dr = if *dry_run { " (dry run)" } else { "" };
            println!(
                "  rules: aggregate → {}{dr} ({upserted} section(s), {pruned} pruned, {migrated} folded)",
                path.display()
            );
        }
        RuleOutcome::Block {
            path,
            action,
            wrote,
            budget_warning,
        } => {
            let dr = if *wrote { "" } else { " (no write)" };
            println!("  rules: block {action}{dr} → {}", path.display());
            if let Some(w) = budget_warning {
                println!("    warning: {w}");
            }
        }
        RuleOutcome::NotApplicable => println!("  rules: (no rule target for this harness)"),
        RuleOutcome::Refused { message } => println!("  rules: refused — {message}"),
    }
}

/// The `--json` shape for one harness's config sub-op.
fn config_json(config: &ConfigOutcome) -> Value {
    match config {
        ConfigOutcome::Aligned {
            status,
            path,
            wrote,
            report,
        } => {
            let changes: Vec<Value> = report.changes.iter().map(change_json).collect();
            json!({
                "status": status,
                "path": path.display().to_string(),
                "wrote": wrote,
                "mutated": report.mutated(),
                "changes": changes,
                "conflicts": report.conflicts().len(),
            })
        }
        ConfigOutcome::Deferred { reason } => json!({ "status": "deferred", "reason": reason }),
        ConfigOutcome::Skipped => json!({
            "status": "skipped",
            "reason": "--rules-only (REQ-YF-TUNE-028): config sub-operation not run"
        }),
        ConfigOutcome::ConsentRequired {
            path,
            reasons,
            report,
        } => consent::blocked_json(path, reasons, report),
        ConfigOutcome::Refused { reason, message } => {
            json!({ "status": "refused", "reason": reason, "message": message })
        }
    }
}

/// The `--json` shape for one harness's rule sub-op.
fn rules_json(rules: &RuleOutcome) -> Value {
    match rules {
        RuleOutcome::Aggregate {
            path,
            upserted,
            pruned,
            migrated,
            dry_run,
        } => json!({
            "kind": "aggregate",
            "path": path.display().to_string(),
            "dry_run": dry_run,
            "upserted": upserted,
            "pruned": pruned,
            "migrated": migrated,
        }),
        RuleOutcome::Block {
            path,
            action,
            wrote,
            budget_warning,
        } => json!({
            "kind": "block",
            "path": path.display().to_string(),
            "action": action,
            "wrote": wrote,
            "budget_warning": budget_warning,
        }),
        RuleOutcome::NotApplicable => json!({ "kind": "not_applicable" }),
        RuleOutcome::Refused { message } => json!({ "kind": "refused", "message": message }),
    }
}

/// One-line human description of a change (dry-run diff / report body).
fn describe(c: &Change) -> String {
    match c {
        Change::ScalarAdded { path, value } => format!("+ {path} = {value}"),
        Change::ScalarForced { path, from, to } => format!("~ {path}: {from} → {to} (forced)"),
        Change::ScalarConflict {
            path,
            existing,
            recommended,
        } => {
            format!("! {path}: {existing} (yours) ≠ {recommended} (recommended) — kept yours")
        }
        Change::SetUnioned { path, added } => {
            let names: Vec<String> = added.iter().map(|v| v.to_string()).collect();
            format!("∪ {path} += [{}]", names.join(", "))
        }
        Change::SetTypeConflict { path, existing } => {
            format!("! {path}: existing {existing} is not an array — left untouched")
        }
    }
}

/// The `--json` shape for one change.
fn change_json(c: &Change) -> Value {
    match c {
        Change::ScalarAdded { path, value } => {
            json!({ "kind": "scalar_added", "path": path, "value": value })
        }
        Change::ScalarForced { path, from, to } => {
            json!({ "kind": "scalar_forced", "path": path, "from": from, "to": to })
        }
        Change::ScalarConflict {
            path,
            existing,
            recommended,
        } => {
            json!({ "kind": "scalar_conflict", "path": path, "existing": existing, "recommended": recommended })
        }
        Change::SetUnioned { path, added } => {
            json!({ "kind": "set_unioned", "path": path, "added": added })
        }
        Change::SetTypeConflict { path, existing } => {
            json!({ "kind": "set_type_conflict", "path": path, "existing": existing })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cli::HarnessTuneArgs;

    fn args(harness: &str, force: bool, dry_run: bool) -> HarnessTuneArgs {
        HarnessTuneArgs {
            harness: vec![harness.to_string()],
            project: false,
            committed: false,
            force,
            dry_run,
            rules_only: false,
            allow_permissions_write: false,
            consent_gated: false,
            revert: false,
            pi_rule_target: crate::cli::PiRuleTarget::AgentsMd,
            json: false,
        }
    }

    /// A `--rules-only` variant of [`args`] (REQ-YF-TUNE-028).
    fn rules_only_args(harness: &str) -> HarnessTuneArgs {
        HarnessTuneArgs {
            rules_only: true,
            ..args(harness, false, false)
        }
    }

    // REQ-YF-TUNE-023 (Issue 7.2): the `--tune`-bridge core. A seeded SINGLE
    // harness runs BOTH tune sub-operations (config alignment + rule deployment);
    // the resolved-target-set projection (`plan_targets_at`) that the multi-harness
    // auto path surfaces for confirmation is READ-ONLY — it writes nothing. Both
    // seams are env-free (hermetic HOME/root), matching the crate's REQ-tagging
    // convention.
    //
    // plan-042 (REQ-YF-SELF-008): the bridge is now consent-gated, and codex's
    // `approval_policy` is a declared consent-bearing entry on a machine with no
    // config.toml — so BOTH sub-operations running is now conditional on the
    // explicit D-N flag. Passing it here preserves what this test is about (the
    // bridge runs both sub-ops); the gated case is covered by the consent_gate
    // module.
    #[test]
    fn tune_bridge_runs_both_subops_and_plan_writes_nothing() {
        let dir = tempfile::tempdir().unwrap();
        let home = dir.path();
        let root = dir.path();

        // Seeded single harness (codex): the bridge runs config AND rules.
        let summary = tune_bridge_at(
            &["codex".to_string()],
            TuneScope::User,
            home,
            root,
            false,
            false,
            /*allow_permissions_write=*/ true,
        )
        .unwrap();
        assert_eq!(
            summary["status"],
            json!("ok"),
            "single-harness bridge succeeds"
        );
        assert_eq!(
            summary["harnesses"].as_array().map(Vec::len),
            Some(1),
            "one harness in the bridge summary"
        );
        assert!(
            home.join(".codex/config.toml").exists(),
            "config sub-op wrote config.toml"
        );
        let agents = std::fs::read_to_string(home.join(".codex/AGENTS.md")).unwrap();
        assert!(
            agents.contains(managed_block::BEGIN_MARKER),
            "rule sub-op wrote the managed block"
        );

        // The multi-harness target projection surfaces every harness's config +
        // rule target but writes NOTHING (a fresh sandbox stays empty) — the
        // "surface before any write" bound (F6).
        let dir2 = tempfile::tempdir().unwrap();
        let h2 = dir2.path();
        let plan = plan_targets_at(
            &["codex".to_string(), "opencode".to_string()],
            TuneScope::User,
            h2,
            h2,
        )
        .unwrap();
        assert_eq!(plan.len(), 2, "both harnesses in the resolved target set");
        assert!(plan[0]
            .config
            .as_ref()
            .unwrap()
            .ends_with(".codex/config.toml"));
        assert!(plan[1]
            .config
            .as_ref()
            .unwrap()
            .ends_with(".config/opencode/opencode.json"));
        assert!(
            plan.iter().all(|t| t.rules.is_some()),
            "each harness has a rule target"
        );
        assert!(
            !h2.join(".codex").exists() && !h2.join(".config").exists(),
            "plan_targets must write nothing"
        );
    }

    /// Legacy single-harness config-align seam: run the config sub-op over an explicit
    /// `path` and map its outcome to an `ExitCode`, exactly as the pre-7.1 `run_core`
    /// did. The existing config-alignment tests drive this env-free seam; production
    /// `run` now folds `compute_config` into the unified per-harness verdict instead.
    fn run_core(
        args: &HarnessTuneArgs,
        profile: &profile::Profile,
        _scope: TuneScope,
        path: &std::path::Path,
    ) -> Result<ExitCode> {
        Ok(match compute_config(args, profile, path)? {
            ConfigOutcome::Refused { .. } => ExitCode::FAILURE,
            _ => ExitCode::SUCCESS,
        })
    }

    fn claude() -> profile::Profile {
        profile::load_profile("claude-code").unwrap().unwrap()
    }

    fn is_failure(code: ExitCode) -> bool {
        format!("{code:?}") == format!("{:?}", ExitCode::FAILURE)
    }

    fn read_json(path: &std::path::Path) -> Value {
        serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap()
    }

    fn deny(v: &Value) -> Vec<String> {
        v["permissions"]["deny"]
            .as_array()
            .map(|a| {
                a.iter()
                    .map(|x| x.as_str().unwrap_or_default().to_string())
                    .collect()
            })
            .unwrap_or_default()
    }

    // REQ-YF-TUNE-002: an unknown harness is a clean refusal (non-zero exit, no
    // panic). It refuses before any path resolution, so it never touches the FS.
    // (codex/opencode now ship config profiles, so `nonesuch` is the unknown one.)
    #[test]
    fn unknown_harness_refuses_cleanly() {
        let code = run(&args("nonesuch", false, true)).expect("must not error");
        assert!(is_failure(code));
    }

    /// Load a shipped config profile by harness key (test convenience).
    fn load(harness: &str) -> profile::Profile {
        profile::load_profile(harness).unwrap().unwrap()
    }

    // REQ-YF-TUNE-015: the codex profile loads, its format is Toml, and a fresh tune
    // writes a VALID `config.toml` (delta-replay path, NOT JSON) honoring the
    // kind-aware / idempotent / Agent-never-denied contract — a second tune is a
    // byte-for-byte no-op.
    #[test]
    fn codex_tune_writes_valid_toml_idempotently() {
        let p = load("codex");
        assert_eq!(p.format, SettingsFormat::Toml);

        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join(".codex").join("config.toml");
        let code = run_core(&args("codex", false, false), &p, TuneScope::User, &path).unwrap();
        assert!(!is_failure(code));
        assert!(path.exists());

        let text = std::fs::read_to_string(&path).unwrap();
        // Output is valid TOML (not JSON) — the delta-replay adapter produced it.
        let doc = text.parse::<toml_edit::DocumentMut>().expect("valid TOML");
        assert!(
            serde_json::from_str::<Value>(&text).is_err(),
            "codex output must be TOML, not JSON"
        );
        // The evidence-backed codex keys landed with the profile values.
        assert_eq!(doc["approval_policy"].as_str(), Some("never"));
        assert_eq!(doc["tui"]["notifications"].as_bool(), Some(false));
        assert_eq!(doc["project_doc_max_bytes"].as_integer(), Some(65536));
        // Agent-never-denied holds structurally (codex ships no deny surface).
        assert!(
            !text.contains("Agent"),
            "Agent must never appear in a codex tune"
        );

        // Idempotent: a second tune mutates nothing (byte-identical file).
        let before = std::fs::read(&path).unwrap();
        run_core(&args("codex", false, false), &p, TuneScope::User, &path).unwrap();
        assert_eq!(
            std::fs::read(&path).unwrap(),
            before,
            "second codex tune must be a byte-identical no-op"
        );
    }

    // REQ-YF-TUNE-016: the opencode profile loads, reuses the JSON write path, and a
    // fresh tune is idempotent. The written file is a JSON object carrying the
    // profile's opencode.json keys.
    #[test]
    fn opencode_tune_reuses_json_path_idempotently() {
        let p = load("opencode");
        assert_eq!(p.format, SettingsFormat::Json);

        let dir = tempfile::tempdir().unwrap();
        let path = dir
            .path()
            .join(".config")
            .join("opencode")
            .join("opencode.json");
        run_core(&args("opencode", false, false), &p, TuneScope::User, &path).unwrap();
        assert!(path.exists());

        let v = read_json(&path);
        assert!(v.is_object(), "opencode tune writes a JSON object");
        assert_eq!(v["permission"]["*"], json!("allow"));
        assert_eq!(v["share"], json!("disabled"));

        // Idempotent: a second tune reports no mutation and leaves the file as-is.
        let before = std::fs::read(&path).unwrap();
        run_core(&args("opencode", false, false), &p, TuneScope::User, &path).unwrap();
        assert_eq!(
            std::fs::read(&path).unwrap(),
            before,
            "second opencode tune must be a byte-identical no-op"
        );
    }

    // REQ-YF-TUNE-017 / REQ-YF-TUNE-012 (Issue 7.1): a Pi tune no longer refuses the
    // whole command. Pi ships no config profile, so its config sub-op is a clean
    // config-DEFERRED (not a failure) while rule deployment still runs — the
    // config-independent rule-deploy Issue 7.1 owns. Driven env-free so it never
    // touches the real `$HOME`. The available CONFIG harnesses still exclude pi.
    #[test]
    fn pi_config_deferred_not_refused() {
        assert!(profile::load_profile("pi").unwrap().is_none());
        let dir = tempfile::tempdir().unwrap();
        let v = tune_one_harness_at(
            &args("pi", false, false),
            "pi",
            TuneScope::User,
            dir.path(),
            dir.path(),
        )
        .unwrap();
        assert!(!v.is_failure(), "a pi tune must NOT fail the command");
        assert!(
            matches!(v.config, ConfigOutcome::Deferred { .. }),
            "pi config must be deferred, not refused"
        );
        // available_harnesses (the config harnesses) names the three and never pi.
        let available = profile::available_harnesses();
        assert_eq!(
            available,
            vec![
                "claude-code".to_string(),
                "codex".to_string(),
                "opencode".to_string()
            ]
        );
        assert!(!available.contains(&"pi".to_string()));
    }

    // REQ-YF-TUNE-012 (Issue 7.1): `yf harness tune` runs BOTH sub-operations per
    // harness and reports a unified per-harness verdict.
    //   * A **codex** tune writes BOTH `~/.codex/config.toml` (config alignment) AND
    //     the `~/.codex/AGENTS.md` managed block (rule deployment).
    //   * A **pi** tune writes ONLY the rule block (against the verified
    //     `~/.pi/agent/AGENTS.md`) and reports config as **deferred** — it does NOT
    //     fail — with no config file written.
    // Both sub-op results appear in the per-harness verdict. Driven env-free.
    #[test]
    fn tune_runs_both_subops_per_harness_verdict() {
        let dir = tempfile::tempdir().unwrap();
        let home = dir.path();
        let root = dir.path();

        // --- codex: config alignment AND rule deployment both fire. ----------------
        let codex = tune_one_harness_at(
            &args("codex", false, false),
            "codex",
            TuneScope::User,
            home,
            root,
        )
        .unwrap();
        assert!(!codex.is_failure(), "a codex tune must succeed");
        match &codex.config {
            ConfigOutcome::Aligned {
                status,
                path,
                wrote,
                ..
            } => {
                assert_eq!(*status, "written", "fresh codex config is written");
                assert!(*wrote);
                assert!(path.ends_with(".codex/config.toml"));
            }
            other => panic!("codex config must be Aligned, got {other:?}"),
        }
        match &codex.rules {
            RuleOutcome::Block {
                path,
                wrote,
                action,
                budget_warning,
            } => {
                assert!(
                    path.ends_with(".codex/AGENTS.md"),
                    "codex rules land in AGENTS.md"
                );
                assert!(*wrote && *action == "appended");
                // A small managed block into an empty AGENTS.md with the tuned/default
                // cap is well under budget — no warning (REQ-YF-TUNE-027).
                assert!(
                    budget_warning.is_none(),
                    "a small codex block must not trip the budget warning: {budget_warning:?}"
                );
            }
            other => panic!("codex rules must be a Block, got {other:?}"),
        }
        // Both files exist on disk — config.toml AND the AGENTS.md block.
        assert!(
            home.join(".codex/config.toml").exists(),
            "codex config.toml written"
        );
        let codex_agents = std::fs::read_to_string(home.join(".codex/AGENTS.md")).unwrap();
        assert!(
            codex_agents.contains(managed_block::BEGIN_MARKER),
            "codex AGENTS.md carries the managed rule block"
        );

        // --- pi: rule deployment ONLY; config DEFERRED (not a failure). ------------
        let pi = tune_one_harness_at(&args("pi", false, false), "pi", TuneScope::User, home, root)
            .unwrap();
        assert!(
            !pi.is_failure(),
            "a pi tune must NOT fail (config-deferred)"
        );
        assert!(
            matches!(pi.config, ConfigOutcome::Deferred { .. }),
            "pi config must be deferred, got {:?}",
            pi.config
        );
        match &pi.rules {
            RuleOutcome::Block { path, wrote, .. } => {
                assert!(
                    path.ends_with(".pi/agent/AGENTS.md"),
                    "pi rules land in the verified target"
                );
                assert!(*wrote, "pi rule block is written");
            }
            other => panic!("pi rules must be a Block, got {other:?}"),
        }
        // Pi wrote its rule block but NO config file of any kind under .pi.
        assert!(
            home.join(".pi/agent/AGENTS.md").exists(),
            "pi rule block written"
        );
        assert!(
            !home.join(".pi/agent/config.toml").exists(),
            "pi writes no config"
        );
        assert!(
            !home.join(".pi/config.toml").exists(),
            "pi writes no config"
        );
    }

    // REQ-YF-TUNE-007: dry-run over a fresh (absent) file reports changes but never
    // writes. Uses run_core with an explicit temp path (no global-env mutation).
    #[test]
    fn dry_run_reports_without_writing() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join(".claude").join("settings.json");
        let code = run_core(
            &args("claude-code", false, true),
            &claude(),
            TuneScope::User,
            &path,
        )
        .unwrap();
        assert!(!is_failure(code));
        assert!(!path.exists(), "dry-run must not create {}", path.display());
    }

    // REQ-YF-TUNE-004: a fresh file is fully written; a second run is idempotent
    // (no write). REQ-YF-TUNE-005: Agent is never denied in the written file.
    #[test]
    fn fresh_write_then_idempotent_rerun() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join(".claude").join("settings.json");
        run_core(
            &args("claude-code", false, false),
            &claude(),
            TuneScope::User,
            &path,
        )
        .unwrap();
        assert!(path.exists());
        let first = read_json(&path);
        assert_eq!(first["todoFeatureEnabled"], json!(false));
        assert_eq!(
            first["permissions"]["defaultMode"],
            json!("bypassPermissions")
        );
        assert!(
            !deny(&first).contains(&"Agent".to_string()),
            "Agent must never be denied"
        );

        let before = std::fs::metadata(&path).unwrap().modified().unwrap();
        // Second run: already aligned → nothing changes.
        run_core(
            &args("claude-code", false, false),
            &claude(),
            TuneScope::User,
            &path,
        )
        .unwrap();
        let second = read_json(&path);
        assert_eq!(first, second, "idempotent re-run must not change the file");
        let _ = before;
    }

    // REQ-YF-TUNE-004: a pre-existing scalar conflict is reported and preserved
    // without --force; overwritten with --force.
    #[test]
    fn scalar_conflict_preserved_then_forced() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("settings.json");
        settings::write_settings(&path, &json!({ "effortLevel": "high" })).unwrap();

        run_core(
            &args("claude-code", false, false),
            &claude(),
            TuneScope::User,
            &path,
        )
        .unwrap();
        assert_eq!(
            read_json(&path)["effortLevel"],
            json!("high"),
            "conflict preserved w/o --force"
        );

        run_core(
            &args("claude-code", true, false),
            &claude(),
            TuneScope::User,
            &path,
        )
        .unwrap();
        assert_eq!(
            read_json(&path)["effortLevel"],
            json!("medium"),
            "--force overwrites"
        );
    }

    // REQ-YF-TUNE-006: a malformed settings file is refused without data loss —
    // the original bytes survive untouched.
    #[test]
    fn malformed_file_refused_without_data_loss() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("settings.json");
        let original = "{ not json ,,, ";
        std::fs::write(&path, original).unwrap();
        let code = run_core(
            &args("claude-code", false, false),
            &claude(),
            TuneScope::User,
            &path,
        )
        .unwrap();
        assert!(is_failure(code), "malformed input must refuse");
        assert_eq!(
            std::fs::read_to_string(&path).unwrap(),
            original,
            "file must be untouched"
        );
    }

    // REQ-YF-TUNE-006: a bd setup claude hook block survives a tune untouched.
    #[test]
    fn hook_block_preserved_through_tune() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("settings.json");
        settings::write_settings(
            &path,
            &json!({ "hooks": { "SessionStart": [{ "command": "bd prime" }] } }),
        )
        .unwrap();
        run_core(
            &args("claude-code", false, false),
            &claude(),
            TuneScope::User,
            &path,
        )
        .unwrap();
        let out = read_json(&path);
        assert_eq!(
            out["hooks"]["SessionStart"][0]["command"],
            json!("bd prime"),
            "hook preserved"
        );
        // And the tune keys landed alongside it.
        assert_eq!(out["todoFeatureEnabled"], json!(false));
    }

    // REQ-YF-TUNE-004 (Issue 3.5): a pre-existing deny with the operator's custom
    // denies + rm -rf safety globs is UNIONED end-to-end — user entries preserved,
    // profile denies added, nothing removed.
    #[test]
    fn set_valued_union_end_to_end() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("settings.json");
        settings::write_settings(
            &path,
            &json!({
                "permissions": {
                    "defaultMode": "bypassPermissions",
                    "deny": ["Bash(rm -rf /opt/mine)", "MyOrgTool", "TaskCreate"]
                }
            }),
        )
        .unwrap();
        run_core(
            &args("claude-code", false, false),
            &claude(),
            TuneScope::User,
            &path,
        )
        .unwrap();
        let d = deny(&read_json(&path));
        // User entries + safety glob preserved.
        assert!(d.contains(&"Bash(rm -rf /opt/mine)".to_string()));
        assert!(d.contains(&"MyOrgTool".to_string()));
        // Existing profile member not duplicated.
        assert_eq!(d.iter().filter(|x| *x == "TaskCreate").count(), 1);
        // Profile members unioned in.
        assert!(d.contains(&"EnterPlanMode".to_string()));
        assert!(d.contains(&"CronCreate".to_string()));
        // Nothing removed, and Agent never present.
        assert!(!d.contains(&"Agent".to_string()));
    }

    // REQ-YF-TUNE-003: both project scopes resolve to the correct file and write it.
    #[test]
    fn project_scopes_write_correct_file() {
        let dir = tempfile::tempdir().unwrap();
        let root = dir.path();
        let p = claude();
        let local = settings::settings_path_at(&p, TuneScope::ProjectLocal, root, root);
        let committed = settings::settings_path_at(&p, TuneScope::ProjectCommitted, root, root);
        run_core(
            &args("claude-code", false, false),
            &p,
            TuneScope::ProjectLocal,
            &local,
        )
        .unwrap();
        run_core(
            &args("claude-code", false, false),
            &p,
            TuneScope::ProjectCommitted,
            &committed,
        )
        .unwrap();
        assert!(local.ends_with(".claude/settings.local.json") && local.exists());
        assert!(committed.ends_with(".claude/settings.json") && committed.exists());
    }

    // REQ-YF-TUNE-010: the install-time tune core writes on a fresh file and is
    // idempotent on re-run — the same engine `yf skills install --tune` invokes.
    #[test]
    fn install_tune_core_writes_then_idempotent() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join(".claude").join("settings.json");
        let p = claude();
        let first = tune_for_install_at(&p, TuneScope::User, &path).unwrap();
        assert_eq!(first["status"], json!("written"));
        assert_eq!(first["wrote"], json!(true));
        assert!(path.exists());
        // A bd setup claude hook and Agent invariant hold through the install tune.
        assert!(!deny(&read_json(&path)).contains(&"Agent".to_string()));
        let second = tune_for_install_at(&p, TuneScope::User, &path).unwrap();
        assert_eq!(second["status"], json!("already_aligned"));
        assert_eq!(second["wrote"], json!(false));
    }

    // REQ-YF-TUNE-010: the install-time tune refuses (not crashes) on a malformed
    // settings file, leaving it untouched — a --tune install never data-loses.
    #[test]
    fn install_tune_core_refuses_malformed() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("settings.json");
        std::fs::write(&path, "{ broken ,,,").unwrap();
        let r = tune_for_install_at(&claude(), TuneScope::User, &path).unwrap();
        assert_eq!(r["status"], json!("refused"));
        assert_eq!(std::fs::read_to_string(&path).unwrap(), "{ broken ,,,");
    }

    /// A test-only in-memory TOML-format profile (codex/opencode profiles ship in
    /// Epic 5). Reuses the claude entries but flips surface + format so 4.2's
    /// dispatch is exercised without shipping a new `yf/profiles/*.json`.
    fn toml_profile() -> profile::Profile {
        let mut p = claude();
        p.harness = "test-toml".to_string();
        p.surface_dir = ".codex".to_string();
        p.settings_filename = "config.toml".to_string();
        p.settings_local_filename = "config.toml".to_string();
        p.format = settings::SettingsFormat::Toml;
        p
    }

    // REQ-YF-TUNE-014: scope/path resolution is profile-driven (surface dir +
    // filename) and read/write dispatch branches on `profile.format`. A TOML
    // profile resolves to its `config.toml` surface and dispatches to the
    // delta-replay adapter (output preserves a comment, is valid TOML, NOT JSON); a
    // JSON profile resolves to its own surface and still writes JSON.
    #[test]
    fn format_dispatch_selects_adapter_by_profile() {
        use std::path::Path;

        // --- TOML profile: profile-driven path resolution + TOML dispatch. -----
        let tp = toml_profile();
        // Path resolution reads surface_dir + filename off the profile (~/.codex/config.toml).
        assert_eq!(
            settings::settings_path_at(
                &tp,
                TuneScope::User,
                Path::new("/home/jd"),
                Path::new("/r")
            ),
            std::path::PathBuf::from("/home/jd/.codex/config.toml"),
        );

        let dir = tempfile::tempdir().unwrap();
        let toml_path = dir.path().join(".codex").join("config.toml");
        std::fs::create_dir_all(toml_path.parent().unwrap()).unwrap();
        std::fs::write(
            &toml_path,
            "# operator comment — must survive\neffortLevel = \"high\"\n",
        )
        .unwrap();

        let code = run_core(
            &args("test-toml", false, false),
            &tp,
            TuneScope::User,
            &toml_path,
        )
        .unwrap();
        assert!(!is_failure(code));
        let toml_out = std::fs::read_to_string(&toml_path).unwrap();
        // Delta-replay adapter chosen: the comment survived (JSON path could not).
        assert!(
            toml_out.contains("# operator comment — must survive"),
            "TOML dispatch must preserve the comment:\n{toml_out}"
        );
        // Output is valid TOML with the profile scalar merged in, and is NOT JSON —
        // proving the TOML adapter, not the JSON writer, produced it.
        let doc = toml_out
            .parse::<toml_edit::DocumentMut>()
            .expect("valid TOML");
        assert_eq!(doc["todoFeatureEnabled"].as_bool(), Some(false));
        assert_eq!(doc["effortLevel"].as_str(), Some("high"), "conflict kept");
        assert!(
            serde_json::from_str::<Value>(&toml_out).is_err(),
            "TOML output must not parse as JSON"
        );

        // --- JSON profile: resolves to its own surface + still writes JSON. -----
        let jp = claude();
        assert_eq!(
            settings::settings_path_at(
                &jp,
                TuneScope::User,
                Path::new("/home/jd"),
                Path::new("/r")
            ),
            std::path::PathBuf::from("/home/jd/.claude/settings.json"),
        );
        let json_path = dir.path().join(".claude").join("settings.json");
        run_core(
            &args("claude-code", false, false),
            &jp,
            TuneScope::User,
            &json_path,
        )
        .unwrap();
        // JSON dispatch: output parses as a JSON object with the profile scalar.
        let parsed = read_json(&json_path);
        assert!(parsed.is_object(), "JSON dispatch must write a JSON object");
        assert_eq!(parsed["todoFeatureEnabled"], json!(false));
    }

    // REQ-YF-TUNE-014: a malformed TOML config is refused fail-safe (non-zero exit)
    // and the original bytes survive — the TOML parallel of the JSON Malformed guard.
    #[test]
    fn toml_malformed_refused_without_data_loss() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("config.toml");
        let original = "this is [ not valid = toml";
        std::fs::write(&path, original).unwrap();
        let code = run_core(
            &args("test-toml", false, false),
            &toml_profile(),
            TuneScope::User,
            &path,
        )
        .unwrap();
        assert!(is_failure(code), "malformed TOML must refuse");
        assert_eq!(std::fs::read_to_string(&path).unwrap(), original);
    }

    // REQ-YF-TUNE-007: --json emits a machine-readable result with a status field.
    #[test]
    fn json_output_shape() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join("settings.json");
        let mut a = args("claude-code", false, true);
        a.json = true;
        // Just assert it runs and produces the dry-run verdict without writing.
        let code = run_core(&a, &claude(), TuneScope::User, &path).unwrap();
        assert!(!is_failure(code));
        assert!(!path.exists());
    }

    // REQ-YF-FLOW-007: the `YOSHIKO_FLOW.md` aggregation relocated install→tune.
    // A skills-only install writes NO aggregate; the tune-side rule-deploy seam
    // then produces the aggregate that is **byte-identical** to what the old
    // install-time path produced — the same unchanged engine over the same
    // acted-on skill set. Proves the relocation is byte-stable (Issue 3.1).
    #[test]
    fn tune_deploys_byte_identical_aggregate_install_writes_none() {
        use crate::cli::{Scope, SkillsArgs};

        let tmp = tempfile::tempdir().unwrap();

        // --- skills-only install writes no aggregate (REQ-YF-FLOW-007). ---------
        let skills_dir = tmp.path().join("skills");
        let install_args = SkillsArgs {
            names: vec!["yf-beads-init".to_string(), "yf-plan".to_string()],
            scope: Scope::User,
            harness: Vec::new(),
            surface: None,
            target: Some(skills_dir.clone()),
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            prune: false,
            tune: false,
            rules_only: false,
            allow_permissions_write: false,
            yes: false,
            json: true,
        };
        crate::cmd::install::run(&install_args).unwrap();
        let install_rules = skills_dir.parent().unwrap().join("rules");
        assert!(
            !install_rules.join(crate::flow::FLOW_FILENAME).exists(),
            "skills-only install must not write the aggregate"
        );

        // --- tune's rule-deploy seam writes the full aggregate. ----------------
        let tune_rules = tmp.path().join("tune-rules");
        deploy_rules_aggregate(&args("claude-code", false, false), &tune_rules).unwrap();
        let tune_flow = tune_rules.join(crate::flow::FLOW_FILENAME);
        assert!(tune_flow.is_file(), "tune must write the aggregate");

        // --- byte-identical to the old install-time engine output (same set). ---
        let engine_rules = tmp.path().join("engine-rules");
        crate::cmd::common::install_rules_aggregate(&tune_acted_skills(), &engine_rules, false)
            .unwrap();
        let engine_flow = engine_rules.join(crate::flow::FLOW_FILENAME);
        assert_eq!(
            std::fs::read(&tune_flow).unwrap(),
            std::fs::read(&engine_flow).unwrap(),
            "tune's aggregate must be byte-identical to the install-time engine output"
        );
    }

    // REQ-YF-TUNE-028 (plan-042 Issue 2.1): a **rules-only** tune writes the rules
    // and touches NO config file. This is the seam that makes the sync's safe half
    // shippable without its consent-bearing half — before this mode existed,
    // `tune_one_harness_at` ran both sub-operations unconditionally, so "deploy
    // rules without config" was unreachable by any verb.
    //
    // Both halves are asserted on claude-code, the harness whose profile applies
    // `permissions.defaultMode: "bypassPermissions"` and CREATES settings.json where
    // none exists — i.e. exactly the write this mode must not perform.
    #[test]
    fn rules_only_tune_writes_rules_and_touches_no_config() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().join("home");
        let root = tmp.path().join("root");
        std::fs::create_dir_all(&home).unwrap();
        std::fs::create_dir_all(&root).unwrap();

        let settings = settings::settings_path_at(
            &profile::load_profile("claude-code").unwrap().unwrap(),
            TuneScope::User,
            &home,
            &root,
        );
        assert!(!settings.exists(), "precondition: no settings file yet");

        let verdict = tune_one_harness_at(
            &rules_only_args("claude-code"),
            "claude-code",
            TuneScope::User,
            &home,
            &root,
        )
        .unwrap();

        // (a) config was SKIPPED — not deferred (no profile) and not refused.
        assert!(
            matches!(verdict.config, ConfigOutcome::Skipped),
            "rules-only must report config skipped, got {:?}",
            verdict.config
        );
        assert!(
            !verdict.is_failure(),
            "a rules-only run is not a failure verdict"
        );

        // (b) NO config file was created — the whole point. claude-code's profile
        // would otherwise CREATE this file carrying bypassPermissions.
        assert!(
            !settings.exists(),
            "rules-only must not create {} — that is the unconsented \
             bypassPermissions write this mode exists to prevent",
            settings.display()
        );

        // (c) the rules DID deploy.
        assert!(
            !matches!(
                verdict.rules,
                RuleOutcome::NotApplicable | RuleOutcome::Refused { .. }
            ),
            "rules-only must still deploy rules, got {:?}",
            verdict.rules
        );
        let flow = home.join(".claude/rules").join(crate::flow::FLOW_FILENAME);
        assert!(
            flow.is_file(),
            "rules-only must write the aggregate at {}",
            flow.display()
        );

        // (d) an EXISTING config file is not modified either — skipping must mean
        // "not consulted", not merely "not created".
        std::fs::create_dir_all(settings.parent().unwrap()).unwrap();
        let sentinel = br#"{"operatorKey": "untouched"}"#;
        std::fs::write(&settings, sentinel).unwrap();
        tune_one_harness_at(
            &rules_only_args("claude-code"),
            "claude-code",
            TuneScope::User,
            &home,
            &root,
        )
        .unwrap();
        assert_eq!(
            std::fs::read(&settings).unwrap(),
            sentinel,
            "rules-only must leave an EXISTING config file byte-identical"
        );
    }

    // REQ-YF-TUNE-028: the `--rules-only` JSON verdict is `skipped`, distinct from
    // pi's `deferred`. A caller (the sync) must be able to tell "you asked me not to"
    // apart from "this harness ships no profile".
    #[test]
    fn rules_only_config_json_is_skipped_not_deferred() {
        let v = config_json(&ConfigOutcome::Skipped);
        assert_eq!(v["status"], "skipped");
        let d = config_json(&ConfigOutcome::Deferred {
            reason: "no profile".to_string(),
        });
        assert_eq!(d["status"], "deferred");
        assert_ne!(v["status"], d["status"]);
    }

    // REQ-YF-TUNE-028: the bridge threads `rules_only` through, so
    // `harness skills install --tune --rules-only` (the sync's exec) reports
    // status "ok" while writing no config.
    #[test]
    fn bridge_rules_only_reports_ok_and_writes_no_config() {
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().join("home");
        let root = tmp.path().join("root");
        std::fs::create_dir_all(&home).unwrap();
        std::fs::create_dir_all(&root).unwrap();

        let out = tune_bridge_at(
            &["claude-code".to_string()],
            TuneScope::User,
            &home,
            &root,
            /*dry_run=*/ false,
            /*rules_only=*/ true,
            /*allow_permissions_write=*/ false,
        )
        .unwrap();

        assert_eq!(
            out["status"], "ok",
            "a rules-only bridge run is a success, not a refusal: {out}"
        );
        assert_eq!(out["harnesses"][0]["config"]["status"], "skipped");
        assert!(
            !home.join(".claude/settings.json").exists(),
            "the bridge's rules-only path must write no config file"
        );
    }

    // REQ-YF-FLOW-007 (backward-compat, Issue 3.2): a pre-existing `YOSHIKO_FLOW.md`
    // — as a pre-plan-033 install would have written (here an OLDER install that only
    // carried the yf-plan section) — is **adopted/reconciled** on the first `tune`,
    // NOT duplicated and NOT orphaned. After the first tune the pre-existing section
    // is folded into the current full aggregate exactly once (no double-append), a
    // single aggregate file remains, and the result is byte-identical to a fresh
    // full deploy into an empty dir. This is distinct from the 3.1 byte-stability
    // test: it covers the *pre-existing file* / *adopt-on-first-tune* axis.
    #[test]
    fn pre_existing_aggregate_adopted_not_duplicated_on_first_tune() {
        let tmp = tempfile::tempdir().unwrap();

        // --- pre-seed: a pre-plan-033 install artifact (older, partial set). ------
        // The old install-time path wrote the aggregate via the same engine. Seed an
        // OLDER install that only carried yf-plan's section, so first tune must fold
        // it into the full acted-on set.
        let rules = tmp.path().join("rules");
        crate::cmd::common::install_rules_aggregate(&["yf-plan".to_string()], &rules, false)
            .unwrap();
        let flow_file = rules.join(crate::flow::FLOW_FILENAME);
        assert!(flow_file.is_file(), "pre-existing aggregate seeded");
        let pre_sections = crate::flow::parse(&std::fs::read_to_string(&flow_file).unwrap());
        assert!(
            pre_sections.iter().any(|s| s.protocol == "PLANS.md"),
            "pre-seed carries the yf-plan section"
        );

        // --- first tune over the pre-existing aggregate. --------------------------
        deploy_rules_aggregate(&args("claude-code", false, false), &rules).unwrap();

        // Still exactly ONE aggregate file in the rules dir (not orphaned/split).
        let aggregates: Vec<_> = std::fs::read_dir(&rules)
            .unwrap()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_name() == crate::flow::FLOW_FILENAME)
            .collect();
        assert_eq!(aggregates.len(), 1, "one aggregate file after adopt");

        // The pre-existing section is folded in, and NO protocol is duplicated
        // (reconcile-prune adopted it — it was not appended a second time).
        let text = std::fs::read_to_string(&flow_file).unwrap();
        let sections = crate::flow::parse(&text);
        let mut protocols: Vec<&str> = sections.iter().map(|s| s.protocol.as_str()).collect();
        let count = protocols.len();
        protocols.sort_unstable();
        protocols.dedup();
        assert_eq!(
            protocols.len(),
            count,
            "no protocol section is duplicated after adopt-on-first-tune"
        );
        assert!(
            sections.iter().any(|s| s.protocol == "PLANS.md"),
            "the pre-existing yf-plan section survives adoption (not orphaned)"
        );

        // Adoption reconciles to canonical form: byte-identical to a fresh full
        // deploy into an empty dir over the same acted-on skill set.
        let fresh = tmp.path().join("fresh-rules");
        crate::cmd::common::install_rules_aggregate(&tune_acted_skills(), &fresh, false).unwrap();
        assert_eq!(
            std::fs::read(&flow_file).unwrap(),
            std::fs::read(fresh.join(crate::flow::FLOW_FILENAME)).unwrap(),
            "adopted aggregate is byte-identical to a fresh full deploy (reconciled, not duplicated)"
        );
    }

    // REQ-YF-FLOW-007 (backward-compat, Issue 3.2): a skills-only re-install over an
    // existing `YOSHIKO_FLOW.md` leaves it **byte-identical** — install does not read,
    // rewrite, or delete the aggregate (it touches no rules surface at all). Locks
    // that an existing install's aggregate is left untouched by the now-skills-only
    // install, so `tune` remains the sole author of the rules surface.
    #[test]
    fn skills_only_reinstall_leaves_existing_aggregate_byte_identical() {
        use crate::cli::{Scope, SkillsArgs};

        let tmp = tempfile::tempdir().unwrap();
        let skills_dir = tmp.path().join("skills");

        // Pre-seed an existing aggregate at the conventional sibling rules dir, as a
        // prior install/tune would have left it.
        let rules_dir = skills_dir.parent().unwrap().join("rules");
        crate::cmd::common::install_rules_aggregate(&tune_acted_skills(), &rules_dir, false)
            .unwrap();
        let flow_file = rules_dir.join(crate::flow::FLOW_FILENAME);
        let before = std::fs::read(&flow_file).unwrap();

        // Skills-only re-install (writes skill bodies only, never the rules surface).
        let install_args = SkillsArgs {
            names: vec!["yf-beads-init".to_string(), "yf-plan".to_string()],
            scope: Scope::User,
            harness: Vec::new(),
            surface: None,
            target: Some(skills_dir.clone()),
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            prune: false,
            tune: false,
            rules_only: false,
            allow_permissions_write: false,
            yes: false,
            json: true,
        };
        crate::cmd::install::run(&install_args).unwrap();

        // The pre-existing aggregate is byte-identical — install left it untouched.
        assert_eq!(
            std::fs::read(&flow_file).unwrap(),
            before,
            "skills-only install must leave an existing aggregate byte-identical"
        );
    }

    // REQ-YF-FLOW-007: `--dry-run tune` projects the aggregate without writing —
    // the rule-deploy seam honors the engine's dry-run (no rules dir created).
    #[test]
    fn tune_rule_deploy_dry_run_writes_nothing() {
        let tmp = tempfile::tempdir().unwrap();
        let rules = tmp.path().join("rules");
        deploy_rules_aggregate(&args("claude-code", false, /*dry_run=*/ true), &rules).unwrap();
        assert!(
            !rules.join(crate::flow::FLOW_FILENAME).exists(),
            "dry-run tune must not write the aggregate"
        );
    }

    // REQ-YF-TUNE-021 (Issue 8.1): after a tune, the sidecar `.yf/` ownership
    // manifest records EXACTLY what yf wrote — the added config keys (each with its
    // prior + yf-written value), the set-union deltas (ONLY yf's added elements, not
    // operator entries), and the rule managed-block markers. A **pure add** records
    // `prior_present: false`; a **forced scalar** records the captured prior. In
    // project scope `.yf/` is gitignored. A dry-run writes NO manifest. Driven
    // env-free (hermetic HOME/root).
    #[test]
    fn tune_records_ownership_manifest_with_priors_unions_and_block_markers() {
        use manifest::MANIFEST_FILENAME;

        fn read_manifest(path: &std::path::Path) -> manifest::Manifest {
            serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap()
        }

        // --- claude-code user tune: config priors + set-union delta + aggregate. ----
        // Seed a settings.json with a CONFLICTING scalar (effortLevel) so `--force`
        // yields a forced scalar whose captured prior must be recorded, plus an
        // operator deny entry so the union delta records only yf's additions.
        let dir = tempfile::tempdir().unwrap();
        let home = dir.path();
        let root = dir.path();
        let settings = home.join(".claude").join("settings.json");
        settings::write_settings(
            &settings,
            &json!({
                "effortLevel": "high",
                "permissions": { "deny": ["MyOrgTool"] }
            }),
        )
        .unwrap();

        tune_one_harness_at(
            &args("claude-code", /*force=*/ true, /*dry_run=*/ false),
            "claude-code",
            TuneScope::User,
            home,
            root,
        )
        .unwrap();

        let mpath = home.join(".claude").join(".yf").join(MANIFEST_FILENAME);
        assert!(
            mpath.exists(),
            "user-scope manifest lands beside the surface at {}",
            mpath.display()
        );
        let m = read_manifest(&mpath);
        let surface = m
            .surfaces
            .get("claude-code:user")
            .expect("claude-code:user surface recorded");
        let cfg = surface.config.as_ref().expect("config record present");

        // A PURE ADD records prior absent (prior_present:false, prior:null).
        let todo = cfg
            .keys_added
            .iter()
            .find(|k| k.path == "todoFeatureEnabled")
            .expect("pure-add key recorded");
        assert!(!todo.prior_present, "pure add records prior absent");
        assert_eq!(todo.prior, None);
        assert_eq!(todo.written, json!(false), "yf-written value recorded");

        // A FORCED SCALAR records the captured prior AND the yf-written value.
        let effort = cfg
            .keys_added
            .iter()
            .find(|k| k.path == "effortLevel")
            .expect("forced scalar recorded");
        assert!(effort.prior_present, "forced scalar records a prior");
        assert_eq!(effort.prior, Some(json!("high")), "captured prior");
        assert_eq!(effort.written, json!("medium"), "yf-written value");

        // The SET-UNION delta records ONLY yf's added elements — the operator's
        // pre-existing `MyOrgTool` is NOT in the added list.
        let deny = cfg
            .sets_unioned
            .iter()
            .find(|s| s.path == "permissions.deny")
            .expect("set-union delta recorded");
        assert!(
            deny.added.iter().any(|v| v == &json!("TaskCreate")),
            "yf's added deny element recorded"
        );
        assert!(
            !deny.added.iter().any(|v| v == &json!("MyOrgTool")),
            "operator's pre-existing entry is NOT recorded as a yf addition"
        );

        // claude-code deploys a whole-file aggregate (rules dir), not a managed block.
        let rules = surface.rules.as_ref().expect("rule record present");
        assert_eq!(rules.kind, "aggregate");
        assert!(rules.begin_marker.is_none() && rules.end_marker.is_none());

        // --- codex project-committed tune: rule BLOCK markers + gitignore. ----------
        let pdir = tempfile::tempdir().unwrap();
        let proot = pdir.path();
        tune_one_harness_at(
            &args("codex", false, false),
            "codex",
            TuneScope::ProjectCommitted,
            proot,
            proot,
        )
        .unwrap();

        // Project-scope manifest is the single repo-root `.yf/` file.
        let pmpath = proot.join(".yf").join(MANIFEST_FILENAME);
        assert!(pmpath.exists(), "project-scope manifest at repo-root .yf/");
        let pm = read_manifest(&pmpath);
        let ps = pm
            .surfaces
            .get("codex:project-committed")
            .expect("codex project surface recorded");
        let prules = ps.rules.as_ref().expect("codex rule record present");
        assert_eq!(prules.kind, "block", "codex rules are a managed block");
        assert_eq!(
            prules.begin_marker.as_deref(),
            Some(managed_block::BEGIN_MARKER),
            "BEGIN marker recorded"
        );
        assert_eq!(
            prules.end_marker.as_deref(),
            Some(managed_block::END_MARKER),
            "END marker recorded"
        );

        // Project scope gitignores `.yf/` (idempotently — the `/.yf/` anchor).
        let gitignore = std::fs::read_to_string(proot.join(".gitignore")).unwrap();
        assert!(
            gitignore.lines().any(|l| l.trim() == "/.yf/"),
            "project-scope `.yf/` is gitignored:\n{gitignore}"
        );

        // --- dry-run writes NO manifest. --------------------------------------------
        let ddir = tempfile::tempdir().unwrap();
        let dhome = ddir.path();
        tune_one_harness_at(
            &args("codex", false, /*dry_run=*/ true),
            "codex",
            TuneScope::User,
            dhome,
            dhome,
        )
        .unwrap();
        assert!(
            !dhome
                .join(".codex")
                .join(".yf")
                .join(MANIFEST_FILENAME)
                .exists(),
            "a dry-run tune must not write a manifest"
        );
    }
}
