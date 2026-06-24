//! The `yf doctor` check registry (#32): concrete [`Check`] implementations and
//! [`checks`], which assembles them. Adding a new prerequisite (git, gh, dolt) is
//! a one-line `BinCheck { .. }` push here.

use std::path::{Path, PathBuf};

use super::check::{Check, CheckResult};
use crate::cmd::common;
use crate::frontmatter;
use crate::tool;

/// Minimum acceptable `bd` version (SPEC §3.6 / REQ-YF-PRE-002).
const BD_MIN: (u32, u32, u32) = (1, 0, 5);

/// `version` axis: `yf` itself. Always ok; reports the build line.
pub struct VersionCheck;

impl Check for VersionCheck {
    fn run(&self) -> CheckResult {
        CheckResult::ok("version", crate::VERSION_LINE.to_string())
    }
}

/// A required external-binary prerequisite: present on PATH, resolvable, and
/// (optionally) at or above `min_version`. Reports the resolved path and version.
///
/// Future prereqs (git, gh, dolt) are a one-line registry add:
/// `Box::new(BinCheck::new("git", None, "Install git via your package manager"))`.
pub struct BinCheck {
    /// Binary name to resolve on PATH.
    bin: &'static str,
    /// Argument that prints the version (`version` for bd, `--version` for uv/git).
    version_arg: &'static str,
    /// Minimum acceptable version, if the binary is version-gated.
    min_version: Option<(u32, u32, u32)>,
    /// Remediation shown when the binary is missing or too old.
    remediation: &'static str,
}

impl BinCheck {
    pub fn new(
        bin: &'static str,
        version_arg: &'static str,
        min_version: Option<(u32, u32, u32)>,
        remediation: &'static str,
    ) -> Self {
        Self {
            bin,
            version_arg,
            min_version,
            remediation,
        }
    }
}

impl Check for BinCheck {
    fn run(&self) -> CheckResult {
        let Some(path) = tool::resolve_tool(self.bin) else {
            return CheckResult::fail(self.bin, "missing on PATH", self.remediation.to_string());
        };
        let path_str = path.display().to_string();
        match self.min_version {
            None => CheckResult::ok(self.bin, format!("present ({path_str})")),
            Some(min) => match tool::tool_version(None, self.bin, self.version_arg) {
                None => CheckResult::fail(
                    self.bin,
                    format!("present ({path_str}) but version unparseable"),
                    self.remediation.to_string(),
                ),
                Some(v) => {
                    let (a, b, c) = v;
                    let (ma, mb, mc) = min;
                    if v >= min {
                        CheckResult::ok(
                            self.bin,
                            format!("{a}.{b}.{c} (>= {ma}.{mb}.{mc}) at {path_str}"),
                        )
                    } else {
                        CheckResult::fail(
                            self.bin,
                            format!("{a}.{b}.{c} (< {ma}.{mb}.{mc}) at {path_str}"),
                            self.remediation.to_string(),
                        )
                    }
                }
            },
        }
    }
}

/// Warning-severity check for a Homebrew-shadowed `uv` (#32): a brew-managed `uv`
/// on PATH shadows the vendored copy and breaks `uv self update`. Non-fatal — it
/// reports a warning, never failing the command.
pub struct HomebrewShadowCheck {
    /// Binary to inspect (here, `uv`).
    bin: &'static str,
}

impl HomebrewShadowCheck {
    pub fn new(bin: &'static str) -> Self {
        Self { bin }
    }

    /// Whether `path` looks like a Homebrew-managed install.
    fn is_homebrew(path: &Path) -> bool {
        let s = path.to_string_lossy();
        s.starts_with("/opt/homebrew") || s.contains("/Cellar/") || s.contains("linuxbrew")
    }
}

impl Check for HomebrewShadowCheck {
    fn run(&self) -> CheckResult {
        let name = format!("{}:homebrew-shadow", self.bin);
        match tool::resolve_tool(self.bin) {
            // Absent: nothing to shadow. Report ok (the BinCheck handles missing).
            None => CheckResult::warn(name, true, "uv not on PATH (skipped)", None),
            Some(path) if Self::is_homebrew(&path) => CheckResult::warn(
                name,
                false,
                format!("Homebrew-shadowed uv at {}", path.display()),
                Some(
                    "A Homebrew uv shadows the vendored copy and breaks `uv self update`; \
                     prefer the standalone installer (https://docs.astral.sh/uv/) or \
                     `brew unlink uv`"
                        .to_string(),
                ),
            ),
            Some(path) => CheckResult::warn(
                name,
                true,
                format!("not Homebrew-shadowed ({})", path.display()),
                None,
            ),
        }
    }
}

/// Per-skill marker-health axis, delegating to [`common::skill_health`].
pub struct SkillCheck {
    name: String,
    skills_dir: PathBuf,
}

impl Check for SkillCheck {
    fn run(&self) -> CheckResult {
        match common::skill_health(&self.name, &self.skills_dir) {
            Ok(h) => {
                let axis = format!("skills:{}", self.name);
                if h.is_ok() {
                    CheckResult::ok(axis, h.doctor_state().to_string())
                } else {
                    CheckResult::fail(
                        axis,
                        h.doctor_state().to_string(),
                        "run `yf skills upgrade` to repair the skill install".to_string(),
                    )
                }
            }
            Err(e) => CheckResult::fail(
                format!("skills:{}", self.name),
                format!("health check error: {e}"),
                "re-run `yf skills install`".to_string(),
            ),
        }
    }
}

/// Companion-rule axis for a skill that ships `protocols/*.md` (presence +
/// content-hash against the embedded source, read from the aggregate
/// `YOSHIKO_FLOW.md` when present). Delegates to [`common`].
pub struct RuleCheck {
    name: String,
    rules_dir: PathBuf,
}

impl Check for RuleCheck {
    fn run(&self) -> CheckResult {
        let rules = common::embedded_rules(&self.name);
        let axis = format!("rules:{}", self.name);
        let mut missing = Vec::new();
        let mut drift = Vec::new();
        for (base, bytes) in &rules {
            match common::installed_rule_source(&self.rules_dir, base) {
                None => missing.push(base.clone()),
                Some((on_disk, _path)) => {
                    if &on_disk != bytes {
                        drift.push(base.clone());
                    }
                }
            }
        }
        if missing.is_empty() && drift.is_empty() {
            return CheckResult::ok(axis, "rule(s) present and current");
        }
        let mut parts = Vec::new();
        if !missing.is_empty() {
            parts.push(format!("rule_missing: {}", missing.join(", ")));
        }
        if !drift.is_empty() {
            parts.push(format!("rule_drift: {}", drift.join(", ")));
        }
        CheckResult::fail(
            axis,
            parts.join("; "),
            "run `yf skills install` to (re)write the companion rule(s)".to_string(),
        )
    }
}

/// Build the ordered registry of doctor checks for the given install surface.
///
/// Order mirrors the previous hardcoded axes: `version`, `bd`, `uv` (+ its
/// homebrew-shadow warning), `git`, then per-skill marker + companion-rule axes.
/// Adding a prerequisite is a one-line `Box::new(BinCheck::new(..))` here.
pub fn checks(skills_dir: &Path, rules_dir: &Path) -> Vec<Box<dyn Check>> {
    let mut out: Vec<Box<dyn Check>> = vec![
        Box::new(VersionCheck),
        Box::new(BinCheck::new(
            "bd",
            "version",
            Some(BD_MIN),
            "Install/upgrade beads: https://github.com/gastownhall/beads",
        )),
        Box::new(BinCheck::new(
            "uv",
            "--version",
            None,
            "Install uv: https://docs.astral.sh/uv/",
        )),
        Box::new(HomebrewShadowCheck::new("uv")),
        Box::new(BinCheck::new(
            "git",
            "--version",
            None,
            "Install git via your system package manager",
        )),
    ];

    let skills = frontmatter::load_skills();
    for name in skills.keys() {
        out.push(Box::new(SkillCheck {
            name: name.clone(),
            skills_dir: skills_dir.to_path_buf(),
        }));
        // Companion-rule axis only for skills that ship rules.
        if !common::embedded_rules(name).is_empty() {
            out.push(Box::new(RuleCheck {
                name: name.clone(),
                rules_dir: rules_dir.to_path_buf(),
            }));
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    // #32: BinCheck reports a missing binary as a required failure with remediation.
    #[test]
    fn bincheck_missing_is_required_failure() {
        let c = BinCheck::new(
            "definitely-not-a-real-binary-xyz",
            "--version",
            None,
            "install it",
        );
        let r = c.run();
        assert!(!r.ok && r.required && r.is_failure());
        assert_eq!(r.remediation.as_deref(), Some("install it"));
    }

    // #32: the homebrew-shadow check is always non-required (a warning), never a
    // command failure, regardless of verdict.
    #[test]
    fn homebrew_shadow_is_never_required() {
        let r = HomebrewShadowCheck::new("uv").run();
        assert!(
            !r.required,
            "homebrew-shadow must be a warning, not required"
        );
        assert!(!r.is_failure(), "a warning never fails the command");
    }

    // #32: the homebrew path classifier matches brew install locations only.
    #[test]
    fn homebrew_path_classifier() {
        assert!(HomebrewShadowCheck::is_homebrew(Path::new(
            "/opt/homebrew/bin/uv"
        )));
        assert!(HomebrewShadowCheck::is_homebrew(Path::new(
            "/usr/local/Cellar/uv/0.1/bin/uv"
        )));
        assert!(HomebrewShadowCheck::is_homebrew(Path::new(
            "/home/linuxbrew/.linuxbrew/bin/uv"
        )));
        assert!(!HomebrewShadowCheck::is_homebrew(Path::new(
            "/usr/local/bin/uv"
        )));
        assert!(!HomebrewShadowCheck::is_homebrew(Path::new(
            "/Users/me/.local/bin/uv"
        )));
    }

    // #32: the registry includes the core prereq axes and is non-empty.
    #[test]
    fn registry_contains_core_axes() {
        let tmp = tempfile::tempdir().unwrap();
        let names: Vec<String> = checks(tmp.path(), tmp.path())
            .iter()
            .map(|c| c.run().name)
            .collect();
        assert!(names.iter().any(|n| n == "version"));
        assert!(names.iter().any(|n| n == "bd"));
        assert!(names.iter().any(|n| n == "uv"));
        assert!(names.iter().any(|n| n == "git"));
        assert!(names.iter().any(|n| n == "uv:homebrew-shadow"));
        assert!(names.iter().any(|n| n.starts_with("skills:")));
    }

    // #32: RuleCheck flags a missing companion rule as a required failure, and
    // there is no rule axis for a ruleless skill (it is simply not pushed).
    #[test]
    fn rulecheck_flags_missing() {
        let tmp = tempfile::tempdir().unwrap();
        let c = RuleCheck {
            name: "yf-beads-init".to_string(),
            rules_dir: tmp.path().to_path_buf(),
        };
        let r = c.run();
        assert!(!r.ok && r.is_failure());
        assert!(r.detail.contains("rule_missing"));
    }

    // #32: a ruleless skill contributes no rule axis to the registry.
    #[test]
    fn no_rule_axis_for_ruleless_skill() {
        let tmp = tempfile::tempdir().unwrap();
        let has_extra_rule = checks(tmp.path(), tmp.path())
            .iter()
            .any(|c| c.run().name == "rules:yf-beads-extra");
        assert!(!has_extra_rule, "yf-beads-extra ships no protocols/*.md");
    }

    fn rule_check(name: &str, rules_dir: &Path) -> RuleCheck {
        RuleCheck {
            name: name.to_string(),
            rules_dir: rules_dir.to_path_buf(),
        }
    }

    // REQ-YF-DOCTOR-001 (ported): rule axis passes once the embedded rule is
    // written out as a legacy standalone.
    #[test]
    fn rule_axis_ok_when_present_and_current() {
        let tmp = tempfile::tempdir().unwrap();
        for (base, bytes) in common::embedded_rules("yf-beads-init") {
            std::fs::write(tmp.path().join(base), bytes).unwrap();
        }
        let r = rule_check("yf-beads-init", tmp.path()).run();
        assert!(r.ok, "rule present + current must pass: {}", r.detail);
    }

    // REQ-YF-FLOW-005 (3.1/C2): doctor reads the rule body from the aggregate
    // YOSHIKO_FLOW.md and reports ok when the section matches embedded.
    #[test]
    fn rule_axis_ok_from_aggregate() {
        let tmp = tempfile::tempdir().unwrap();
        common::install_rules_aggregate(&["yf-beads-init".to_string()], tmp.path(), false).unwrap();
        // No standalone file — only the aggregate is present.
        assert!(!tmp.path().join("BEADS_INIT.md").exists());
        let r = rule_check("yf-beads-init", tmp.path()).run();
        assert!(r.ok, "aggregate section must read ok: {}", r.detail);
    }

    // REQ-YF-FLOW (3.1/C2): a drifted aggregate section is flagged rule_drift.
    #[test]
    fn rule_axis_drift_from_aggregate() {
        let tmp = tempfile::tempdir().unwrap();
        common::install_rules_aggregate(&["yf-beads-init".to_string()], tmp.path(), false).unwrap();
        let flow_file = tmp.path().join(crate::flow::FLOW_FILENAME);
        let mangled = std::fs::read_to_string(&flow_file)
            .unwrap()
            .replace("Protocol", "DRIFT");
        std::fs::write(&flow_file, mangled).unwrap();
        let r = rule_check("yf-beads-init", tmp.path()).run();
        assert!(!r.ok);
        assert!(r.detail.contains("rule_drift"), "{}", r.detail);
    }

    // #32: the bd BinCheck is version-gated; the gate is numeric (tuple-ordered).
    #[test]
    fn bd_version_gate_is_numeric() {
        assert!((1, 0, 5) >= BD_MIN);
        assert!((1, 0, 10) >= BD_MIN);
        assert!((1, 1, 0) >= BD_MIN);
        assert!((1, 0, 4) < BD_MIN);
        assert!((0, 9, 9) < BD_MIN);
    }
}
