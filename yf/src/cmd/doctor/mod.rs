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

use std::process::ExitCode;

use anyhow::Result;

use self::check::CheckResult;
use self::checks::checks;
use super::common;
use crate::cli::{DoctorArgs, Scope, Surface};

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

    // Doctor inspects the default user/claude install surface (matches the
    // install defaults). --target is not a doctor flag by design.
    let (skills_dir, rules_dir) = common::dirs_from(Scope::User, Surface::Claude);

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
}
