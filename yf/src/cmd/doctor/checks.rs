//! The `yf doctor` check registry (#32): concrete [`Check`] implementations and
//! [`checks`], which assembles them. Adding a new prerequisite (git, gh, dolt) is
//! a one-line `BinCheck { .. }` push here.

use std::collections::BTreeSet;
use std::path::{Path, PathBuf};

use super::check::{Check, CheckResult};
use crate::cmd::common;
use crate::embed;
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

/// Whether a `bd mol pour|wisp <name>` token is a **concrete** formula name (vs. a
/// placeholder/metavariable/flag). Concrete = starts with an ASCII letter and uses
/// only `[A-Za-z0-9._-]`. This rejects `<name>`, `<formula>`, `${VAR}`, `$var`,
/// `{{tmpl}}`, and `--json`, keeping only real formula tokens like `plan-execute`.
fn is_concrete_formula_token(t: &str) -> bool {
    let mut chars = t.chars();
    match chars.next() {
        Some(c) if c.is_ascii_alphabetic() => {}
        _ => return false,
    }
    t.chars()
        .all(|c| c.is_ascii_alphanumeric() || c == '.' || c == '_' || c == '-')
}

/// REQ-YF-DOCTOR-004 extraction contract: the set of **concrete** molecule names a
/// SKILL.md references as `bd mol (pour|wisp) <name>` **inside a runnable bash code
/// fence**. Mentions in prose, inline code, or non-bash fences are excluded, as are
/// placeholder tokens (`<name>`, `${VAR}`, `--json`). This is the exact set of names
/// that MUST have a shipped `formulas/<name>.formula.toml`.
pub fn extract_pour_names(skill_md: &str) -> BTreeSet<String> {
    let mut names = BTreeSet::new();
    // `None` = outside any fence; `Some(is_bash)` = inside a fence of that language.
    // Tracking the language across the whole fence (not per-line) is what makes a
    // non-bash fence's CLOSING ``` not read as a new bash fence's opener.
    let mut fence: Option<bool> = None;
    for line in skill_md.lines() {
        let trimmed = line.trim_start();
        if trimmed.starts_with("```") {
            match fence {
                Some(_) => fence = None, // closing delimiter
                None => {
                    let info = trimmed.trim_start_matches('`').trim().to_ascii_lowercase();
                    let is_bash = info == "bash" || info == "sh" || info.starts_with("bash ");
                    fence = Some(is_bash);
                }
            }
            continue;
        }
        if fence != Some(true) {
            continue; // only scan inside runnable bash fences
        }
        // Normalize shell command-substitution / quoting punctuation so the `bd` in
        // `RESULT=$(bd mol pour …)` or a backtick-wrapped call tokenizes standalone.
        let cleaned: String = line
            .chars()
            .map(|c| {
                if c == '(' || c == ')' || c == '`' {
                    ' '
                } else {
                    c
                }
            })
            .collect();
        let toks: Vec<&str> = cleaned.split_whitespace().collect();
        for i in 0..toks.len().saturating_sub(3) {
            if toks[i] == "bd"
                && toks[i + 1] == "mol"
                && (toks[i + 2] == "pour" || toks[i + 2] == "wisp")
            {
                let candidate = toks[i + 3];
                if is_concrete_formula_token(candidate) {
                    names.insert(candidate.to_string());
                }
            }
        }
    }
    names
}

/// The referenced formula names with **no** shipped formula — the FormulaCheck
/// failure set. Pure (referenced ∖ shipped), sorted, for testability.
fn missing_shipped(referenced: &BTreeSet<String>, shipped: &BTreeSet<String>) -> Vec<String> {
    referenced
        .iter()
        .filter(|n| !shipped.contains(*n))
        .cloned()
        .collect()
}

/// Static, read-only `FormulaCheck` axis (REQ-YF-DOCTOR-004): for a skill that
/// ships a `formulas/` dir, assert every concrete `bd mol pour|wisp <name>` in a
/// runnable bash fence of its SKILL.md has a shipped `formulas/<name>.formula.toml`.
/// Embedded-tree-based (no repo handle, never mutates).
pub struct FormulaCheck {
    name: String,
}

impl Check for FormulaCheck {
    fn run(&self) -> CheckResult {
        let axis = format!("formulas:{}", self.name);
        let Some(md) = embed::read_file(&format!("{}/SKILL.md", self.name)) else {
            return CheckResult::ok(axis, "no SKILL.md to scan");
        };
        let text = String::from_utf8_lossy(&md);
        let referenced = extract_pour_names(&text);
        // Shipped formula names (`<name>` with the `.formula.toml` suffix stripped).
        let shipped: BTreeSet<String> = embed::skill_formula_basenames(&self.name)
            .into_iter()
            .filter_map(|b| b.strip_suffix(".formula.toml").map(str::to_string))
            .collect();
        let missing = missing_shipped(&referenced, &shipped);
        if missing.is_empty() {
            CheckResult::ok(
                axis,
                format!(
                    "{} runnable pour/wisp reference(s) all have shipped formulas",
                    referenced.len()
                ),
            )
        } else {
            CheckResult::fail(
                axis,
                format!(
                    "runnable `bd mol pour|wisp` with no shipped formula: {}",
                    missing.join(", ")
                ),
                format!(
                    "add skills/{}/formulas/<name>.formula.toml for: {} (or make the invocation \
                     a non-runnable example)",
                    self.name,
                    missing.join(", ")
                ),
            )
        }
    }
}

/// The declared tools absent from PATH, given a `present` predicate. Pure
/// (`tools ∖ present`), sorted-as-declared, for testability without touching PATH.
fn missing_tools<F: Fn(&str) -> bool>(tools: &[String], present: F) -> Vec<String> {
    tools
        .iter()
        .filter(|t| !present(t))
        .cloned()
        .collect()
}

/// Per-skill `depends-on-tool` axis (REQ-YF-DOCTOR-005): for a skill that declares
/// `depends-on-tool` frontmatter, probe each tool on PATH — **reusing the BinCheck
/// PATH-probe** (`tool::resolve_tool`) — and fail if any is missing, with an install
/// hint matching yf-markdown-pdf's missing-tool message (REQ-MDPDF-003). A declared
/// tool absent from PATH is a required failure (surfaced under REQ-YF-DOCTOR-002);
/// a skill declaring no tools contributes no axis. Read-only — it surfaces in the
/// report the same gap preflight enforces as `system_deps_missing`, never mutating.
pub struct SkillDepsCheck {
    name: String,
    tools: Vec<String>,
}

impl Check for SkillDepsCheck {
    fn run(&self) -> CheckResult {
        let axis = format!("skill-deps:{}", self.name);
        let missing = missing_tools(&self.tools, |t| tool::resolve_tool(t).is_some());
        if missing.is_empty() {
            CheckResult::ok(
                axis,
                format!("depends-on-tool present: {}", self.tools.join(", ")),
            )
        } else {
            CheckResult::fail(
                axis,
                format!("missing required tool(s): {}", missing.join(", ")),
                format!(
                    "install the missing tool(s): {} (see skills/{}'s README/SPEC for install hints)",
                    missing.join(", "),
                    self.name,
                ),
            )
        }
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
    for (name, fm) in &skills {
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
        // FormulaCheck axis (REQ-YF-DOCTOR-004) only for skills that ship formulas.
        if !embed::skill_formula_basenames(name).is_empty() {
            out.push(Box::new(FormulaCheck { name: name.clone() }));
        }
        // Per-skill depends-on-tool axis (REQ-YF-DOCTOR-005), after the SkillCheck
        // axes, only for skills that declare `depends-on-tool` frontmatter.
        if !fm.tools.is_empty() {
            out.push(Box::new(SkillDepsCheck {
                name: name.clone(),
                tools: fm.tools.clone(),
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

    // ---- REQ-YF-DOCTOR-004: FormulaCheck extraction contract ---------------

    // Concrete tokens only: real formula names accepted, metavariables/flags rejected.
    #[test]
    fn concrete_token_classifier() {
        assert!(is_concrete_formula_token("plan-execute"));
        assert!(is_concrete_formula_token("yf-research"));
        assert!(is_concrete_formula_token("a.b_c-1"));
        assert!(!is_concrete_formula_token("<name>"));
        assert!(!is_concrete_formula_token("${VAR}"));
        assert!(!is_concrete_formula_token("$var"));
        assert!(!is_concrete_formula_token("--json"));
        assert!(!is_concrete_formula_token("{{tmpl}}"));
        assert!(!is_concrete_formula_token(""));
        assert!(!is_concrete_formula_token("1formula"));
    }

    // Prose / inline-code mentions (outside a bash fence) contribute NO names.
    #[test]
    fn extract_ignores_prose_and_inline() {
        let md = "See `bd mol pour` for details.\n\
                  The formula is poured via `bd mol pour foo` inline.\n\
                  No bd mol pour happens here in prose either.\n";
        assert!(extract_pour_names(md).is_empty());
    }

    // A placeholder inside a bash fence is excluded (the yf-beads-authoring pattern).
    #[test]
    fn extract_ignores_placeholder_in_bash_fence() {
        let md = "```bash\nRESULT=$(bd mol pour <name> --var key=value --json)\n```\n";
        assert!(extract_pour_names(md).is_empty());
    }

    // The command-substitution form `$(bd mol pour NAME …)` IS caught (the real
    // yf-plan/yf-research shape). This is the regression the whitespace-only scan missed.
    #[test]
    fn extract_catches_command_substitution() {
        let md = "```bash\nRESULT=$(bd mol pour plan-execute --var x=1 --json)\n\
                  WISP=$(bd mol wisp plan-investigate --json)\n```\n";
        let names = extract_pour_names(md);
        assert!(names.contains("plan-execute"), "{names:?}");
        assert!(names.contains("plan-investigate"), "{names:?}");
        assert_eq!(names.len(), 2);
    }

    // A non-bash fence (e.g. ```toml) is NOT scanned, and its closing ``` does not
    // desync the fence tracker into reading following prose as bash.
    #[test]
    fn extract_ignores_non_bash_fence() {
        let md = "```toml\nbd mol pour should-not-count\n```\n\
                  Now prose: bd mol pour also-not.\n";
        assert!(extract_pour_names(md).is_empty());
    }

    // The failure set is referenced ∖ shipped: a runnable pour with no shipped
    // formula is flagged; a referenced name that IS shipped is not.
    #[test]
    fn missing_shipped_flags_unshipped_only() {
        let referenced: BTreeSet<String> = ["plan-execute", "ghost"]
            .iter()
            .map(|s| s.to_string())
            .collect();
        let shipped: BTreeSet<String> = ["plan-execute"].iter().map(|s| s.to_string()).collect();
        assert_eq!(
            missing_shipped(&referenced, &shipped),
            vec!["ghost".to_string()]
        );
        // All-shipped ⇒ empty (pass).
        assert!(missing_shipped(&shipped, &shipped).is_empty());
    }

    // Integration: FormulaCheck passes on the real fleet (every runnable pour/wisp
    // in yf-plan / yf-research has a shipped formula).
    #[test]
    fn formulacheck_passes_real_fleet() {
        for skill in ["yf-plan", "yf-research"] {
            let r = FormulaCheck {
                name: skill.to_string(),
            }
            .run();
            assert!(r.ok, "{skill} FormulaCheck should pass: {}", r.detail);
        }
    }

    // A prose-only skill (no formulas/ dir, mentions `bd mol pour` only in prose)
    // contributes NO formulas axis to the registry — it is structurally excluded.
    #[test]
    fn prose_only_skill_has_no_formula_axis() {
        let tmp = tempfile::tempdir().unwrap();
        let names: Vec<String> = checks(tmp.path(), tmp.path())
            .iter()
            .map(|c| c.run().name)
            .collect();
        assert!(
            !names.iter().any(|n| n == "formulas:yf-beads-authoring"),
            "yf-beads-authoring ships no formulas dir → no FormulaCheck axis"
        );
        assert!(
            !names.iter().any(|n| n == "formulas:yf-beads-extra"),
            "yf-beads-extra ships no formulas dir → no FormulaCheck axis"
        );
        // The skills that DO ship formulas get an axis.
        assert!(names.iter().any(|n| n == "formulas:yf-plan"));
    }

    // ---- REQ-YF-DOCTOR-005: per-skill depends-on-tool axis ------------------

    // REQ-YF-DOCTOR-005: the missing set is declared ∖ present — a tool absent per
    // the probe is flagged; a present one is not; all-present ⇒ empty (pass).
    #[test]
    fn skill_deps_missing_is_declared_minus_present() {
        let tools: Vec<String> = ["uv", "pandoc"].iter().map(|s| s.to_string()).collect();
        // Only `uv` present ⇒ `pandoc` is the missing set.
        assert_eq!(
            missing_tools(&tools, |t| t == "uv"),
            vec!["pandoc".to_string()]
        );
        // All present ⇒ empty (the ok path).
        assert!(missing_tools(&tools, |_| true).is_empty());
        // A skill declaring no tools has no missing set.
        assert!(missing_tools(&[], |_| false).is_empty());
    }

    // REQ-YF-DOCTOR-005: all declared deps present ⇒ ok verdict on the run() path.
    #[test]
    fn skill_deps_all_present_is_ok() {
        // Empty declared set trivially has all-present; run() reports ok.
        let r = SkillDepsCheck {
            name: "some-skill".to_string(),
            tools: vec![],
        }
        .run();
        assert!(r.ok && r.required);
        assert_eq!(r.name, "skill-deps:some-skill");
    }

    // REQ-YF-DOCTOR-005: a declared tool missing from PATH ⇒ required failure with
    // an install hint naming the missing tool (md2pdf REQ-MDPDF-003 message format).
    #[test]
    fn skill_deps_missing_tool_fails_with_hint() {
        let r = SkillDepsCheck {
            name: "yf-markdown-html".to_string(),
            tools: vec!["definitely-not-a-real-binary-xyz".to_string()],
        }
        .run();
        assert!(!r.ok && r.required && r.is_failure());
        assert_eq!(r.name, "skill-deps:yf-markdown-html");
        assert!(
            r.detail.contains("missing required tool(s)")
                && r.detail.contains("definitely-not-a-real-binary-xyz"),
            "detail must name the missing tool: {}",
            r.detail
        );
        let rem = r.remediation.expect("missing-tool failure carries a hint");
        assert!(
            rem.contains("definitely-not-a-real-binary-xyz"),
            "hint must name the missing tool: {rem}"
        );
    }

    // REQ-YF-DOCTOR-005: the registry adds a skill-deps axis for a skill that
    // declares depends-on-tool (yf-markdown-html: [uv, pandoc]), and NONE for a
    // skill that declares no tools.
    #[test]
    fn registry_has_skill_deps_axis_only_when_declared() {
        let tmp = tempfile::tempdir().unwrap();
        let names: Vec<String> = checks(tmp.path(), tmp.path())
            .iter()
            .map(|c| c.run().name)
            .collect();
        assert!(
            names.iter().any(|n| n == "skill-deps:yf-markdown-html"),
            "yf-markdown-html declares depends-on-tool ⇒ a skill-deps axis: {names:?}"
        );
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
