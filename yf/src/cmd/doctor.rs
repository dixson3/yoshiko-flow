//! `yf doctor` (bead 1.7) — environment + skill-install diagnostics.
//!
//! Checks, per axis (REQ-YF-DOCTOR-001): `version` (yf itself), `bd` present and
//! ≥ 1.0.5, `uv`, `git`, each `skills:<name>` via the §3.4 marker comparison, and
//! each installed skill's companion-rule presence/hash. Exits non-zero if any
//! axis fails (REQ-YF-DOCTOR-002 / REQ-YF-CLI-003).

use std::path::Path;
use std::process::Command;

use anyhow::Result;

use super::common;
use crate::cli::{DoctorArgs, Scope, Surface};
use crate::frontmatter;

/// Minimum acceptable `bd` version (SPEC §3.6 / REQ-YF-PRE-002).
const BD_MIN: (u64, u64, u64) = (1, 0, 5);

struct Axis {
    name: String,
    ok: bool,
    detail: String,
}

/// Run `yf doctor`. Returns `Ok(())` even when axes fail; the caller maps the
/// returned exit decision. We signal failure by returning an error so `main`'s
/// top-level handler produces a non-zero code.
pub fn run(args: &DoctorArgs) -> Result<()> {
    // --repair short-circuits the read-only doctor axes and runs the beads-init
    // repair sequence (REQ-YF-PRE-007) against the cwd repo.
    if args.repair {
        return run_repair(args);
    }

    // Doctor inspects the default user/claude install surface (matches the
    // install defaults). --target is not a doctor flag by design.
    let (skills_dir, rules_dir) = common::dirs_from(Scope::User, Surface::Claude);
    let mut axes: Vec<Axis> = Vec::new();

    // version (yf itself) — always ok; reports the build line.
    axes.push(Axis {
        name: "version".to_string(),
        ok: true,
        detail: crate::VERSION_LINE.to_string(),
    });

    // bd present + version ≥ 1.0.5.
    axes.push(check_bd());

    // uv / git present on PATH.
    for tool in ["uv", "git"] {
        let present = common::tool_on_path(tool);
        axes.push(Axis {
            name: tool.to_string(),
            ok: present,
            detail: if present {
                "present".to_string()
            } else {
                "missing on PATH".to_string()
            },
        });
    }

    // Per-skill marker health + companion-rule axis.
    let skills = frontmatter::load_skills();
    for name in skills.keys() {
        let h = common::skill_health(name, &skills_dir)?;
        axes.push(Axis {
            name: format!("skills:{name}"),
            ok: h.is_ok(),
            detail: h.doctor_state().to_string(),
        });
        // Companion-rule axis: only meaningful for skills that ship rules.
        if let Some(axis) = check_rules(name, &rules_dir) {
            axes.push(axis);
        }
    }

    let any_fail = axes.iter().any(|a| !a.ok);

    if args.json {
        let arr: Vec<_> = axes
            .iter()
            .map(|a| serde_json::json!({ "axis": a.name, "ok": a.ok, "detail": a.detail }))
            .collect();
        let out = serde_json::json!({
            "command": "doctor",
            "ok": !any_fail,
            "skills_dir": skills_dir,
            "rules_dir": rules_dir,
            "axes": arr,
        });
        println!("{}", serde_json::to_string(&out)?);
    } else {
        println!("yf doctor");
        for a in &axes {
            let mark = if a.ok { "ok  " } else { "FAIL" };
            println!("  [{mark}] {:<28} {}", a.name, a.detail);
        }
        println!();
        println!(
            "{}",
            if any_fail {
                "FAIL: one or more axes failed"
            } else {
                "ok: all axes healthy"
            }
        );
    }

    if any_fail {
        anyhow::bail!("doctor: one or more axes failed");
    }
    Ok(())
}

/// `yf doctor --repair` (REQ-YF-PRE-007): run the `yf-beads-init` repair sequence
/// against the cwd repo. Exits non-zero if the post-repair verify is not `ok`.
fn run_repair(args: &DoctorArgs) -> Result<()> {
    let repo = crate::dest::git_root_or_cwd();
    let result = crate::beads_init::repair(&repo, /* apply */ true, args.local_only)?;

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

/// `bd` axis: present and version ≥ [`BD_MIN`].
fn check_bd() -> Axis {
    if !common::tool_on_path("bd") {
        return Axis {
            name: "bd".to_string(),
            ok: false,
            detail: "missing on PATH".to_string(),
        };
    }
    match bd_version() {
        Some(v) => {
            let ok = v >= BD_MIN;
            let (a, b, c) = v;
            Axis {
                name: "bd".to_string(),
                ok,
                detail: if ok {
                    format!("{a}.{b}.{c} (>= 1.0.5)")
                } else {
                    format!("{a}.{b}.{c} (< 1.0.5 — upgrade bd)")
                },
            }
        }
        None => Axis {
            name: "bd".to_string(),
            ok: false,
            detail: "present but version unparseable".to_string(),
        },
    }
}

/// Parse `bd version` output into a (major, minor, patch) tuple.
fn bd_version() -> Option<(u64, u64, u64)> {
    let out = Command::new("bd").arg("version").output().ok()?;
    let text = String::from_utf8_lossy(&out.stdout);
    parse_semver(&text)
}

/// Extract the first `MAJOR.MINOR.PATCH` triple from arbitrary text.
fn parse_semver(text: &str) -> Option<(u64, u64, u64)> {
    for token in text.split(|c: char| !(c.is_ascii_digit() || c == '.')) {
        let parts: Vec<&str> = token.split('.').collect();
        if parts.len() >= 3 {
            if let (Ok(a), Ok(b), Ok(c)) = (
                parts[0].parse::<u64>(),
                parts[1].parse::<u64>(),
                parts[2].parse::<u64>(),
            ) {
                return Some((a, b, c));
            }
        }
    }
    None
}

/// Companion-rule axis for a skill that ships `protocols/*.md`. `None` if the
/// skill ships no rules.
///
/// Verdict precedence: missing rule → FAIL `rule_missing`; present but bytes
/// differ from the embedded source → FAIL `rule_drift`; otherwise ok. (The
/// per-rule manifest semver axis is REQ-YF-PRE-003's domain; doctor's rule axis
/// is presence + content-hash against the embedded source, which is the
/// authoritative bytes the manifest's sha256 also pins.)
fn check_rules(name: &str, rules_dir: &Path) -> Option<Axis> {
    let rules = common::embedded_rules(name);
    if rules.is_empty() {
        return None;
    }
    let mut missing = Vec::new();
    let mut drift = Vec::new();
    for (base, bytes) in &rules {
        let target = rules_dir.join(base);
        match std::fs::read(&target) {
            Err(_) => missing.push(base.clone()),
            Ok(on_disk) => {
                if &on_disk != bytes {
                    drift.push(base.clone());
                }
            }
        }
    }
    let ok = missing.is_empty() && drift.is_empty();
    let detail = if ok {
        "rule(s) present and current".to_string()
    } else {
        let mut parts = Vec::new();
        if !missing.is_empty() {
            parts.push(format!("rule_missing: {}", missing.join(", ")));
        }
        if !drift.is_empty() {
            parts.push(format!("rule_drift: {}", drift.join(", ")));
        }
        parts.join("; ")
    };
    Some(Axis {
        name: format!("rules:{name}"),
        ok,
        detail,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    // REQ-YF-DOCTOR-001: semver parsing tolerates bd's varied version output.
    #[test]
    fn parses_bd_version_strings() {
        assert_eq!(parse_semver("bd version 1.0.5"), Some((1, 0, 5)));
        assert_eq!(parse_semver("1.2.10\n"), Some((1, 2, 10)));
        assert_eq!(parse_semver("beads v1.0.5 (abc)"), Some((1, 0, 5)));
        assert_eq!(parse_semver("no version here"), None);
    }

    // REQ-YF-DOCTOR-001: the min-version comparison is tuple-ordered, not lexical.
    #[test]
    fn version_gate_is_numeric() {
        assert!((1, 0, 5) >= BD_MIN);
        assert!((1, 0, 10) >= BD_MIN);
        assert!((1, 1, 0) >= BD_MIN);
        assert!((1, 0, 4) < BD_MIN);
        assert!((0, 9, 9) < BD_MIN);
    }

    // REQ-YF-DOCTOR-001: rule axis is None for a skill that ships no rules.
    #[test]
    fn no_rule_axis_for_ruleless_skill() {
        let tmp = tempfile::tempdir().unwrap();
        // yf-beads-extra ships no protocols/*.md.
        assert!(check_rules("yf-beads-extra", tmp.path()).is_none());
    }

    // REQ-YF-DOCTOR-001: rule axis flags a missing companion rule.
    #[test]
    fn rule_axis_flags_missing() {
        let tmp = tempfile::tempdir().unwrap();
        let axis = check_rules("yf-beads-init", tmp.path()).expect("ships a rule");
        assert!(!axis.ok);
        assert!(axis.detail.contains("rule_missing"));
    }

    // REQ-YF-DOCTOR-001: rule axis passes once the embedded rule is written out.
    #[test]
    fn rule_axis_ok_when_present_and_current() {
        let tmp = tempfile::tempdir().unwrap();
        for (base, bytes) in common::embedded_rules("yf-beads-init") {
            std::fs::write(tmp.path().join(base), bytes).unwrap();
        }
        let axis = check_rules("yf-beads-init", tmp.path()).expect("ships a rule");
        assert!(axis.ok, "rule present + current must pass: {}", axis.detail);
    }

    // sanity: embedded skill list is what doctor iterates.
    #[test]
    fn doctor_iterates_embedded_skills() {
        assert!(!crate::embed::skill_names().is_empty());
    }
}
