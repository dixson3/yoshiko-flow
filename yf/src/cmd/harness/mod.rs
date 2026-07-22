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

use std::process::ExitCode;

use anyhow::Result;
use serde_json::{json, Value};

pub mod audit;
pub mod drift;
pub mod merge;
pub mod profile;
pub mod settings;

use crate::cli::HarnessTuneArgs;
use merge::Change;
use settings::{SettingsRead, TuneScope};

/// Run `yf harness tune`. Owns its exit code: a refusal (unknown harness / a
/// malformed settings file) is a verdict → `ExitCode::FAILURE`; a completed tune
/// (even with reported scalar conflicts) is `SUCCESS`.
pub fn run(args: &HarnessTuneArgs) -> Result<ExitCode> {
    // 1. Resolve the profile (unknown harness → clean refusal, REQ-YF-TUNE-002).
    let Some(profile) = profile::load_profile(&args.harness)? else {
        return refuse(
            args.json,
            "unknown-harness",
            &format!(
                "no settings profile for harness '{}'. Available: {}",
                args.harness,
                profile::available_harnesses().join(", ")
            ),
        );
    };

    let scope = TuneScope::resolve(args.project, args.committed);
    let path = settings::settings_path(&profile, scope);
    run_core(args, &profile, scope, &path)
}

/// The tune core over an explicit resolved `path` (env-free — the unit-test seam).
/// [`run`] resolves the profile + path from args and delegates here.
fn run_core(
    args: &HarnessTuneArgs,
    profile: &profile::Profile,
    scope: TuneScope,
    path: &std::path::Path,
) -> Result<ExitCode> {
    // 2. Fail-safe read (REQ-YF-TUNE-006): refuse a malformed file, never overwrite.
    let existing = match settings::read_settings(path) {
        SettingsRead::Absent => Value::Object(Default::default()),
        SettingsRead::Parsed(v) if v.is_object() => v,
        SettingsRead::Parsed(_) => {
            return refuse(
                args.json,
                "malformed",
                &format!(
                    "{}: top-level JSON is not an object; refusing to overwrite",
                    path.display()
                ),
            );
        }
        SettingsRead::Malformed(msg) => {
            return refuse(
                args.json,
                "malformed",
                &format!("unparseable settings file; refusing to overwrite ({msg})"),
            );
        }
    };

    // 3. Kind-aware merge (REQ-YF-TUNE-004/005).
    let (merged, report) = merge::merge(&existing, profile, args.force);
    let mutated = report.mutated();

    // 4. Write unless --dry-run (REQ-YF-TUNE-007) and unless already aligned.
    let wrote = if args.dry_run {
        false
    } else if mutated {
        settings::write_settings(path, &merged)
            .map_err(|e| anyhow::anyhow!("failed to write {}: {e}", path.display()))?;
        true
    } else {
        false
    };

    report_success(args, &profile.harness, scope, path, &report, wrote);
    // Reported conflicts do not fail the command (tune did its job); they are
    // surfaced for the operator to resolve (re-run with --force).
    Ok(ExitCode::SUCCESS)
}

/// Run the Claude Code tune as a **library call** for `yf skills install --tune`
/// (REQ-YF-TUNE-010) — no stdout, returns a JSON summary the caller folds into its
/// own output. `project` selects the project-local scope (else user); it never
/// forces and never dry-runs. A malformed file yields a `refused` summary rather
/// than an error, so a `--tune` install never crashes on a hand-broken settings
/// file.
pub fn tune_for_install(project: bool) -> Result<Value> {
    let Some(profile) = profile::load_profile("claude-code")? else {
        return Ok(json!({ "status": "refused", "reason": "unknown-harness" }));
    };
    let scope = TuneScope::resolve(project, false);
    let path = settings::settings_path(&profile, scope);
    tune_for_install_at(&profile, scope, &path)
}

/// Env-free core of [`tune_for_install`] over an explicit `path` (the test seam):
/// read fail-safe, merge (never force), write if mutated, return a JSON summary.
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

/// A clean refusal verdict (unknown harness or malformed file). Never a panic.
fn refuse(as_json: bool, kind: &str, message: &str) -> Result<ExitCode> {
    if as_json {
        println!(
            "{}",
            serde_json::to_string(&json!({
                "command": "harness tune",
                "status": "refused",
                "reason": kind,
                "message": message,
            }))?
        );
    } else {
        eprintln!("yf harness tune: refused ({kind}): {message}");
    }
    Ok(ExitCode::FAILURE)
}

/// Emit the success report (text or `--json`), including the dry-run diff.
fn report_success(
    args: &HarnessTuneArgs,
    harness: &str,
    scope: TuneScope,
    path: &std::path::Path,
    report: &merge::MergeReport,
    wrote: bool,
) {
    if args.json {
        let changes: Vec<Value> = report.changes.iter().map(change_json).collect();
        let out = json!({
            "command": "harness tune",
            "status": if args.dry_run { "dry_run" } else if wrote { "written" } else { "already_aligned" },
            "harness": harness,
            "scope": scope.label(),
            "path": path.display().to_string(),
            "wrote": wrote,
            "mutated": report.mutated(),
            "changes": changes,
            "conflicts": report.conflicts().len(),
        });
        println!("{}", serde_json::to_string(&out).unwrap_or_default());
        return;
    }

    let verb = if args.dry_run { "would tune" } else { "tune" };
    println!(
        "yf harness {verb} [{harness}] {} → {}",
        scope.label(),
        path.display()
    );
    if report.changes.is_empty() {
        println!("  already aligned — nothing to change.");
        return;
    }
    for c in &report.changes {
        println!("  {}", describe(c));
    }
    if args.dry_run {
        println!("  (dry run — nothing written)");
    } else if wrote {
        println!("  wrote {}", path.display());
    }
    if !report.conflicts().is_empty() {
        println!(
            "  {} conflict(s) left untouched — re-run with --force to overwrite.",
            report.conflicts().len()
        );
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
            harness: harness.to_string(),
            project: false,
            committed: false,
            force,
            dry_run,
            json: false,
        }
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
    #[test]
    fn unknown_harness_refuses_cleanly() {
        let code = run(&args("codex", false, true)).expect("must not error");
        assert!(is_failure(code));
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
}
