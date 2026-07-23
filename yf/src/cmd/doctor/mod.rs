//! `yf doctor` (bead 1.7, #32) — environment + skill-install diagnostics.
//!
//! Read-only by default (DEC-1): reports each prerequisite's presence, version,
//! and resolved path, plus per-skill marker + companion-rule health. Checks are a
//! [`Check`]-trait registry ([`checks`]) so a new prerequisite (git, gh, dolt) is
//! a one-line registry edit. A failing **required** check exits non-zero with a
//! remediation; a failing non-required check (e.g. a Homebrew-shadowed `uv`) is a
//! non-fatal **warning** (REQ-YF-DOCTOR-001/002).
//!
//! `--repair` (explicit opt-in) short-circuits the read-only axes and runs the
//! `yf-beads-init` repair sequence instead (REQ-YF-PRE-007).

mod check;
mod checks;

use std::collections::BTreeSet;
use std::path::Path;
use std::process::ExitCode;

use anyhow::Result;

use self::check::CheckResult;
use self::checks::checks;
use super::common;
use crate::cli::{DoctorArgs, Scope};
use crate::embed;

/// Run `yf doctor`. The read-only check path owns its exit code
/// (`Result<ExitCode>`, like `preflight`): a failing **required** check returns
/// `ExitCode::FAILURE` as a verdict, not as an `Err`. `--repair` delegates to
/// [`run_repair`], which keeps the `anyhow::bail!` error idiom (a repair
/// *failure* is a genuine error, not a verdict — C4 exit-idiom split).
pub fn run(args: &DoctorArgs) -> Result<ExitCode> {
    // --repair short-circuits the read-only doctor axes and runs the beads-init
    // repair sequence (REQ-YF-PRE-007) against the cwd repo. It deliberately
    // stays on the `anyhow::bail!` idiom.
    if args.repair {
        run_repair(args)?;
        return Ok(ExitCode::SUCCESS);
    }

    // --prune-formulas is its OWN affordance (REQ-YF-DOCTOR-004), deliberately
    // decoupled from --repair so a wedged-DB repair never triggers formula deletion.
    if args.prune_formulas {
        run_prune_formulas(args)?;
        return Ok(ExitCode::SUCCESS);
    }

    // Doctor inspects the default user/claude-code install surface (matches the
    // install defaults). --target is not a doctor flag by design.
    let (skills_dir, rules_dir) = common::dirs_from(Scope::User, "claude-code");

    let results: Vec<CheckResult> = checks(&skills_dir, &rules_dir)
        .iter()
        .map(|c| c.run())
        .collect();

    // Only required failures fail the command; warnings (non-required) do not.
    let any_fail = results.iter().any(CheckResult::is_failure);
    let any_warn = results.iter().any(|r| !r.ok && !r.required);

    if args.json {
        let arr: Vec<_> = results
            .iter()
            .map(|r| {
                serde_json::json!({
                    "axis": r.name,
                    "ok": r.ok,
                    "required": r.required,
                    "severity": severity(r),
                    "detail": r.detail,
                    "remediation": r.remediation,
                })
            })
            .collect();
        let out = serde_json::json!({
            "command": "doctor",
            "ok": !any_fail,
            "warnings": any_warn,
            "skills_dir": skills_dir,
            "rules_dir": rules_dir,
            "axes": arr,
        });
        println!("{}", serde_json::to_string(&out)?);
    } else {
        println!("yf doctor");
        for r in &results {
            let mark = match (r.ok, r.required) {
                (true, _) => "ok  ",
                (false, true) => "FAIL",
                (false, false) => "warn",
            };
            println!("  [{mark}] {:<28} {}", r.name, r.detail);
            if !r.ok {
                if let Some(rem) = &r.remediation {
                    println!("         ↳ {rem}");
                }
            }
        }
        println!();
        let summary = if any_fail {
            "FAIL: one or more required axes failed"
        } else if any_warn {
            "ok (with warnings): all required axes healthy"
        } else {
            "ok: all axes healthy"
        };
        println!("{summary}");
    }

    Ok(if any_fail {
        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    })
}

/// The severity label for `--json` rendering: `ok` / `warning` / `error`.
fn severity(r: &CheckResult) -> &'static str {
    if r.ok {
        "ok"
    } else if r.required {
        "error"
    } else {
        "warning"
    }
}

/// `yf doctor --repair` (REQ-YF-PRE-007): run the `yf-beads-init` repair sequence
/// against the cwd repo. Stays on `anyhow::bail!` (C4): a repair that does not
/// reach a healthy state is a genuine error, not a read-only verdict.
fn run_repair(args: &DoctorArgs) -> Result<()> {
    let repo = crate::dest::git_root_or_cwd();
    let result = crate::beads_init::repair(
        &repo,
        /* apply */ true,
        args.local_only,
        args.remove_remote,
    )?;

    // REQ-YF-PRE-010 / REQ-BINIT-025 (#58): repair corrects only the SAFE profile
    // axes (local-only / no-remote). An embedded engine mode is DETECT/WARN-ONLY —
    // reported here, NEVER migrated. Emitted to stderr so `--json` stdout stays a
    // clean flat RepairResult for programmatic consumers.
    if crate::beads_init::has_embedded_engine_drift(&repo) {
        eprintln!(
            "profile (warn-only): beads uses embedded Dolt storage; the canonical minimal-local \
             profile is a per-repo local-server. Engine-mode migration is out of scope — repair \
             did NOT convert it. Re-initialize in server mode only if you deliberately want to switch."
        );
    }

    if args.json {
        println!("{}", serde_json::to_string_pretty(&result)?);
    } else {
        println!(
            "yf doctor --repair (before: {})",
            result.before.status.as_str()
        );
        for step in &result.plan {
            let mark = match step.rc {
                Some(0) => "ok  ",
                Some(_) => "FAIL",
                None => "-   ",
            };
            let kind = if step.native { "native" } else { "bd" };
            println!("  [{mark}] ({kind}) {}", step.why);
        }
        if let Some(after) = &result.after {
            println!("\nbeads status after repair: {}", after.status.as_str());
            for d in &after.diagnostics {
                println!("  - {d}");
            }
        }
    }

    if let Some(after) = &result.after {
        if after.status != crate::beads_init::VerifyStatus::Ok {
            anyhow::bail!(
                "repair did not reach a healthy state: {}",
                after.status.as_str()
            );
        }
    }
    Ok(())
}

/// The union of formula basenames declared by the currently-embedded skill fleet.
/// A staged basename NOT in this set is an orphan (deprecated/removed formula).
fn declared_formula_basenames() -> BTreeSet<String> {
    let mut set = BTreeSet::new();
    for name in embed::skill_names() {
        for base in embed::skill_formula_basenames(&name) {
            set.insert(base);
        }
    }
    set
}

/// Provenance-tracked formula GC report.
#[derive(Debug, serde::Serialize)]
struct PruneReport {
    /// Whether a yf-owned staged-manifest marker was found. `false` ⇒ deletes
    /// nothing (fail-safe): with no marker, yf owns no files here.
    marker_present: bool,
    /// Basenames removed: yf-staged AND no longer declared by any embedded skill.
    pruned: Vec<String>,
    /// yf-staged basenames still declared by an embedded skill (kept).
    kept: Vec<String>,
}

/// REQ-YF-DOCTOR-004 GC: remove `.beads/formulas/` entries the staged-manifest
/// marker attributes to yf that NO currently-embedded skill still declares. Only
/// marker-recorded (yf-staged) basenames are ever considered — a foreign/unmarked
/// proto is never touched — and with no marker present, nothing is deleted.
fn prune_orphan_formulas(repo: &Path) -> Result<PruneReport> {
    let formulas_dir = repo.join(".beads").join("formulas");
    let marker_path = formulas_dir.join(".yf-staged.json");
    let Ok(text) = std::fs::read_to_string(&marker_path) else {
        // Fail-safe: no marker → yf owns nothing here → delete nothing.
        return Ok(PruneReport {
            marker_present: false,
            pruned: vec![],
            kept: vec![],
        });
    };
    let mut map: serde_json::Map<String, serde_json::Value> =
        serde_json::from_str(&text).unwrap_or_default();
    let declared = declared_formula_basenames();

    let mut pruned = vec![];
    let mut kept = vec![];
    let recorded: Vec<String> = map.keys().cloned().collect();
    for basename in recorded {
        if declared.contains(&basename) {
            kept.push(basename);
        } else {
            // Orphan yf-staged file: delete the proto (if present) and drop it from
            // the marker. A foreign/unmarked file is never in `recorded`, so never here.
            let path = formulas_dir.join(&basename);
            if path.exists() {
                std::fs::remove_file(&path)?;
            }
            map.remove(&basename);
            pruned.push(basename);
        }
    }
    // Rewrite the marker to reflect the removals.
    let out = serde_json::to_string_pretty(&serde_json::Value::Object(map))?;
    std::fs::write(&marker_path, out + "\n")?;
    Ok(PruneReport {
        marker_present: true,
        pruned,
        kept,
    })
}

/// `yf doctor --prune-formulas` (REQ-YF-DOCTOR-004): run provenance-tracked formula
/// GC against the cwd repo. Cwd-scoped; stays on `anyhow::bail!` for genuine I/O
/// errors (a deletion failure is an error, not a read-only verdict).
fn run_prune_formulas(args: &DoctorArgs) -> Result<()> {
    let repo = crate::dest::git_root_or_cwd();
    let report = prune_orphan_formulas(&repo)?;
    if args.json {
        println!("{}", serde_json::to_string_pretty(&report)?);
    } else if !report.marker_present {
        println!("yf doctor --prune-formulas: no yf-staged marker; nothing to prune.");
    } else if report.pruned.is_empty() {
        println!(
            "yf doctor --prune-formulas: no orphaned yf-staged formulas ({} kept).",
            report.kept.len()
        );
    } else {
        println!(
            "yf doctor --prune-formulas: pruned {} orphaned formula(s):",
            report.pruned.len()
        );
        for p in &report.pruned {
            println!("  - {p}");
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    // #32: severity labels map (ok / required-fail / warning) → ok/error/warning.
    #[test]
    fn severity_labels() {
        assert_eq!(severity(&CheckResult::ok("x", "d")), "ok");
        assert_eq!(severity(&CheckResult::fail("x", "d", "r")), "error");
        assert_eq!(
            severity(&CheckResult::warn("x", false, "d", None)),
            "warning"
        );
        assert_eq!(severity(&CheckResult::warn("x", true, "d", None)), "ok");
    }

    // #32: is_failure counts only required failures — a warning never fails.
    #[test]
    fn only_required_failures_count() {
        assert!(CheckResult::fail("x", "d", "r").is_failure());
        assert!(!CheckResult::warn("x", false, "d", None).is_failure());
        assert!(!CheckResult::ok("x", "d").is_failure());
    }

    // ---- REQ-YF-DOCTOR-004: provenance-tracked formula GC ------------------

    fn write_formula(dir: &Path, name: &str, body: &str) {
        std::fs::write(dir.join(name), body).unwrap();
    }

    // GC removes a yf-staged orphan (marker-recorded, no embedded skill declares it),
    // KEEPS a still-declared yf-staged formula, and NEVER touches a foreign/unmarked file.
    #[test]
    fn prune_removes_orphan_keeps_declared_and_foreign() {
        let tmp = tempfile::tempdir().unwrap();
        let fdir = tmp.path().join(".beads").join("formulas");
        std::fs::create_dir_all(&fdir).unwrap();
        // A currently-declared formula (yf-plan ships plan-execute), an orphan
        // (deprecated, no longer declared), and a FOREIGN file absent from the marker.
        write_formula(&fdir, "plan-execute.formula.toml", "declared");
        write_formula(&fdir, "deprecated-old.formula.toml", "orphan");
        write_formula(&fdir, "foreign.formula.toml", "not ours");
        // Marker attributes only the two yf-staged files to yf; foreign is unmarked.
        std::fs::write(
            fdir.join(".yf-staged.json"),
            r#"{"plan-execute.formula.toml":["yf-plan"],"deprecated-old.formula.toml":["yf-plan"]}"#,
        )
        .unwrap();

        let report = prune_orphan_formulas(tmp.path()).unwrap();
        assert!(report.marker_present);
        assert_eq!(
            report.pruned,
            vec!["deprecated-old.formula.toml".to_string()]
        );
        assert_eq!(report.kept, vec!["plan-execute.formula.toml".to_string()]);

        // Orphan deleted; declared kept; FOREIGN untouched.
        assert!(
            !fdir.join("deprecated-old.formula.toml").exists(),
            "orphan pruned"
        );
        assert!(
            fdir.join("plan-execute.formula.toml").exists(),
            "declared kept"
        );
        assert!(
            fdir.join("foreign.formula.toml").exists(),
            "foreign/unmarked formula must NEVER be deleted"
        );
        // Marker no longer records the orphan.
        let marker: serde_json::Value =
            serde_json::from_str(&std::fs::read_to_string(fdir.join(".yf-staged.json")).unwrap())
                .unwrap();
        assert!(marker.get("deprecated-old.formula.toml").is_none());
        assert!(marker.get("plan-execute.formula.toml").is_some());
    }

    // Fail-safe: with NO marker present, GC deletes nothing (yf owns nothing here).
    #[test]
    fn prune_no_marker_is_noop() {
        let tmp = tempfile::tempdir().unwrap();
        let fdir = tmp.path().join(".beads").join("formulas");
        std::fs::create_dir_all(&fdir).unwrap();
        write_formula(&fdir, "someone-elses.formula.toml", "foreign");

        let report = prune_orphan_formulas(tmp.path()).unwrap();
        assert!(!report.marker_present);
        assert!(report.pruned.is_empty());
        assert!(
            fdir.join("someone-elses.formula.toml").exists(),
            "no marker ⇒ delete nothing"
        );
    }
}
