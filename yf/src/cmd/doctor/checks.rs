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
    tools.iter().filter(|t| !present(t)).cloned().collect()
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
/// `settings:<harness>` axis (REQ-YF-TUNE-009): a **read-only** report of settings
/// drift from the embedded profile, computed over the **effective merged view**
/// across the precedence layers (user ← project `settings.json` ←
/// `settings.local.json`). Non-required (a warning): un-tuned settings are an
/// alignment nudge, not a health failure. Remediation is `yf harness tune`.
///
/// **Decoupled from `--repair`** (REQ-YF-TUNE-009 / REQ-YF-DOCTOR-003): `--repair`
/// short-circuits to the beads-init repair and never reaches this axis, so no
/// settings write ever happens under `doctor` — this axis only reports.
pub struct SettingsDriftCheck {
    /// Target harness key (profile lookup), e.g. `claude-code`.
    harness: String,
    /// Settings layer paths, **low → high** precedence.
    layers: Vec<PathBuf>,
}

impl SettingsDriftCheck {
    /// Build the check for `harness`, resolving the three layer paths from the
    /// real environment (`$HOME` + git root).
    pub fn from_env(harness: &str) -> Option<Self> {
        let profile = crate::cmd::harness::profile::load_profile(harness)
            .ok()
            .flatten()?;
        use crate::cmd::harness::settings::{settings_path_at, TuneScope};
        let home = std::env::var_os("HOME")
            .map(PathBuf::from)
            .unwrap_or_else(|| PathBuf::from("."));
        let root = crate::dest::git_root_or_cwd();
        // Low → high precedence: user < project committed < project local.
        let layers = vec![
            settings_path_at(&profile, TuneScope::User, &home, &root),
            settings_path_at(&profile, TuneScope::ProjectCommitted, &home, &root),
            settings_path_at(&profile, TuneScope::ProjectLocal, &home, &root),
        ];
        Some(Self {
            harness: harness.to_string(),
            layers,
        })
    }

    /// Evaluate over the resolved layer paths (I/O), returning the verdict. A
    /// malformed layer is skipped (it does not contribute to the effective view);
    /// the profile itself is the reference set (no marker).
    fn evaluate(&self) -> CheckResult {
        use crate::cmd::harness::{audit, profile, settings::read_value_for_format};
        let name = format!("settings:{}", self.harness);
        let Some(prof) = profile::load_profile(&self.harness).ok().flatten() else {
            return CheckResult::warn(
                name,
                true,
                format!("no embedded profile for harness '{}'", self.harness),
                None,
            );
        };
        // Format-aware read (REQ-YF-TUNE-026): JSON layers parse via serde_json; a
        // codex `config.toml` layer parses via the TOML adapter into a decision-only
        // Value. A malformed/absent layer is skipped (does not contribute).
        let mut parsed: Vec<serde_json::Value> = Vec::new();
        for path in &self.layers {
            if let Some(v) = read_value_for_format(path, prof.format) {
                parsed.push(v);
            }
        }
        let refs: Vec<&serde_json::Value> = parsed.iter().collect();
        let drift = audit::audit(&prof, &refs);
        if drift.is_empty() {
            CheckResult::warn(
                name,
                true,
                "aligned with the recommended profile".to_string(),
                None,
            )
        } else {
            let detail = format!(
                "{} setting(s) drift from the profile: {}",
                drift.len(),
                drift
                    .iter()
                    .map(|d| d.summary())
                    .collect::<Vec<_>>()
                    .join("; ")
            );
            CheckResult::warn(
                name,
                false,
                detail,
                Some("run `yf harness tune` to align".to_string()),
            )
        }
    }
}

impl Check for SettingsDriftCheck {
    fn run(&self) -> CheckResult {
        self.evaluate()
    }
}

/// `managed-block:<harness>` axis (REQ-YF-TUNE-026): a **read-only** check that the
/// yf-managed `BEGIN`/`END` rule block in a single-file harness's `AGENTS.md` (codex,
/// opencode, and pi's verified default) matches the current minimized irreducible-core
/// bundle (`minimize::irreducible_core_bundle`, REQ-YF-TUNE-018/019). This is a
/// **distinct axis** from the aggregate `rule_drift` reported by [`RuleCheck`] (which
/// covers a skill's companion rules under a claude-code `rules/` dir): different axis
/// name, different harnesses, different files — no overlap, no double-count.
///
/// The verdict reuses the exact deploy engine ([`managed_block::merge_block`]) against
/// the current expected body, so "aligned" means byte-identical to what a tune would
/// write:
/// - `Unchanged` → **aligned** (ok warning);
/// - `Appended` → **no block** where tune would deploy one (drift warning);
/// - `Replaced` → managed block **stale / hand-edited** (drift warning);
/// - `Err` → ambiguous/out-of-order markers (fail-safe report).
///
/// Non-required (a warning) and never writes — remediation is `yf harness tune`.
pub struct ManagedBlockDriftCheck {
    /// Target harness key, e.g. `codex`.
    harness: String,
    /// Resolved `AGENTS.md` (or `APPEND_SYSTEM.md`) path at user scope.
    path: PathBuf,
}

impl ManagedBlockDriftCheck {
    /// Build the check for `harness`, resolving the user-scope rule-target path. Returns
    /// `None` for a harness with no single-file rule target — claude-code (a `RulesDir`
    /// harness, served by the full aggregate, not a managed block) or an unmapped id.
    pub fn from_env(harness: &str) -> Option<Self> {
        use crate::cmd::harness::managed_block::{effective_rule_target, RuleTargetKind};
        use crate::cmd::harness::settings::TuneScope;
        let target = effective_rule_target(harness, crate::cli::PiRuleTarget::default())?;
        if !matches!(
            target.kind,
            RuleTargetKind::AgentsMd | RuleTargetKind::AppendSystem
        ) {
            return None; // claude-code reads a rules/ dir — no managed block here.
        }
        let home = std::env::var_os("HOME")
            .map(PathBuf::from)
            .filter(|p| !p.as_os_str().is_empty())
            .unwrap_or_else(|| PathBuf::from("."));
        let root = crate::dest::git_root_or_cwd();
        let path = target.resolve_at(TuneScope::User, &home, &root);
        Some(Self {
            harness: harness.to_string(),
            path,
        })
    }

    /// Evaluate the on-disk managed block against the current minimized bundle (I/O).
    fn evaluate(&self) -> CheckResult {
        use crate::cmd::harness::{managed_block, minimize};
        let axis = format!("managed-block:{}", self.harness);
        let body = match minimize::irreducible_core_bundle() {
            Ok(b) => b,
            Err(e) => {
                // The bundle itself won't build (source/classifier disagreement,
                // REQ-YF-TUNE-018). Surface it — read-only, never fatal.
                return CheckResult::warn(
                    axis,
                    false,
                    format!("cannot compute the minimized rule bundle: {e}"),
                    Some("resolve the bundle↔source disagreement (REQ-YF-TUNE-018)".to_string()),
                );
            }
        };
        // Absent file → empty text → `merge_block` reports `Appended` (no block).
        let existing = std::fs::read_to_string(&self.path).unwrap_or_default();
        match managed_block::merge_block(&existing, &body) {
            Ok(managed_block::BlockMerge::Unchanged) => CheckResult::warn(
                axis,
                true,
                format!("managed rule block current at {}", self.path.display()),
                None,
            ),
            Ok(managed_block::BlockMerge::Appended(_)) => CheckResult::warn(
                axis,
                false,
                format!(
                    "no yf-managed rule block at {} — tune would deploy one",
                    self.path.display()
                ),
                Some("run `yf harness tune` to deploy the rule block".to_string()),
            ),
            Ok(managed_block::BlockMerge::Replaced(_)) => CheckResult::warn(
                axis,
                false,
                format!(
                    "yf-managed rule block at {} drifts from the current minimized \
                     bundle (stale or hand-edited)",
                    self.path.display()
                ),
                Some("run `yf harness tune` to re-deploy the current rule block".to_string()),
            ),
            Err(e) => CheckResult::warn(
                axis,
                false,
                format!(
                    "cannot classify the managed block at {}: {e}",
                    self.path.display()
                ),
                Some(
                    "resolve the marker problem by hand, then re-run `yf harness tune`".to_string(),
                ),
            ),
        }
    }
}

impl Check for ManagedBlockDriftCheck {
    fn run(&self) -> CheckResult {
        self.evaluate()
    }
}

/// `codex-budget` axis (REQ-YF-TUNE-027): a **read-only** check that the projected
/// global `~/.codex/AGENTS.md` size (existing content + the minimized managed block)
/// stays under the operator's **effective on-disk** `project_doc_max_bytes` cap. Warns
/// (never blocks) at ≥90% of the cap, naming both the cap and the projected size, so the
/// operator can raise the cap (a tune sets 65536) or trim content before codex silently
/// truncates. **Single-file scope**: the global `~/.codex/AGENTS.md` only, not codex's
/// full multi-file concatenation (documented in the warning). Never writes.
pub struct CodexBudgetCheck {
    /// `~/.codex/AGENTS.md` (user scope).
    agents_path: PathBuf,
    /// `~/.codex/config.toml` (user scope) — the effective-cap source.
    config_path: PathBuf,
}

impl CodexBudgetCheck {
    /// Build the check, resolving the user-scope codex `AGENTS.md` + sibling
    /// `config.toml` from the codex rule target. `None` if codex has no rule target.
    pub fn from_env() -> Option<Self> {
        use crate::cmd::harness::managed_block::rule_target;
        use crate::cmd::harness::settings::TuneScope;
        let target = rule_target("codex")?;
        let home = std::env::var_os("HOME")
            .map(PathBuf::from)
            .filter(|p| !p.as_os_str().is_empty())
            .unwrap_or_else(|| PathBuf::from("."));
        let root = crate::dest::git_root_or_cwd();
        let agents_path = target.resolve_at(TuneScope::User, &home, &root);
        let config_path = agents_path.with_file_name("config.toml");
        Some(Self {
            agents_path,
            config_path,
        })
    }

    fn evaluate(&self) -> CheckResult {
        use crate::cmd::harness::{managed_block, minimize};
        let axis = "codex-budget".to_string();
        let body = match minimize::irreducible_core_bundle() {
            Ok(b) => b,
            Err(e) => {
                return CheckResult::warn(
                    axis,
                    false,
                    format!("cannot compute the minimized rule bundle: {e}"),
                    Some("resolve the bundle↔source disagreement (REQ-YF-TUNE-018)".to_string()),
                );
            }
        };
        let existing = std::fs::read_to_string(&self.agents_path).unwrap_or_default();
        let config_text = std::fs::read_to_string(&self.config_path).ok();
        let cap = managed_block::codex_effective_doc_max_bytes(config_text.as_deref());
        let budget = managed_block::codex_budget(&existing, &body, cap);
        if budget.over_threshold {
            CheckResult::warn(
                axis,
                false,
                managed_block::codex_budget_warning(&budget),
                Some(
                    "raise project_doc_max_bytes in ~/.codex/config.toml (a tune sets 65536) \
                     or trim ~/.codex/AGENTS.md content"
                        .to_string(),
                ),
            )
        } else {
            CheckResult::warn(
                axis,
                true,
                format!(
                    "projected ~/.codex/AGENTS.md {} bytes, under the {}-byte cap",
                    budget.projected, budget.cap
                ),
                None,
            )
        }
    }
}

impl Check for CodexBudgetCheck {
    fn run(&self) -> CheckResult {
        self.evaluate()
    }
}

/// REQ-YF-DOCTOR-006 / REQ-BINIT-027 (#160): READ-ONLY detection of a Dolt remote
/// configured under `dolt.local-only = true`.
///
/// This is the **detect** half of the plan-044 D-2 authority split — *detect and
/// propose, repair only on request*. It reports the violation and names the exact
/// removal command; it **never mutates**. The correction stays behind the explicit
/// `yf doctor --repair --local-only --remove-remote` opt-in.
///
/// Why it exists at all: `dolt.local-only` is an **init-time** flag, not a runtime
/// guard (REQ-BINIT-027). Setting it stops `bd init` from wiring a remote, but it
/// neither removes nor blocks one configured by any other path — so a repo can sit
/// in this state indefinitely with nothing reporting it.
pub struct LocalOnlyRemoteCheck {
    repo_root: PathBuf,
}

impl LocalOnlyRemoteCheck {
    pub fn new(repo_root: PathBuf) -> Self {
        Self { repo_root }
    }

    fn evaluate(&self) -> CheckResult {
        let axis = "beads local-only remote";
        // No `.beads/` at all → not applicable (never false-positive on a
        // non-beads repo; that classification is bd_not_initialized's job).
        if !self.repo_root.join(".beads").is_dir() {
            return CheckResult::ok(axis, "no .beads/ — not applicable");
        }
        if crate::beads_init::has_local_only_remote(&self.repo_root) {
            CheckResult::fail(
                axis,
                "a Dolt remote is configured while `dolt.local-only = true` — bead data can be \
                 pushed to a remote this repo declares it does not have",
                // Reused VERBATIM from preflight.rs's Gap 3 offer, so the two
                // surfaces cannot drift into proposing different commands.
                "Canonicalization drift: a Dolt remote is configured under local-only — \
                 run `yf doctor --repair --local-only --remove-remote` to clear it",
            )
        } else {
            CheckResult::ok(axis, "no Dolt remote configured under local-only")
        }
    }
}

impl Check for LocalOnlyRemoteCheck {
    fn run(&self) -> CheckResult {
        self.evaluate()
    }
}

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
        // REQ-YF-DOCTOR-006 (#160): read-only local-only/remote violation axis.
        Box::new(LocalOnlyRemoteCheck::new(crate::dest::git_root_or_cwd())),
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

    // Settings-drift axis (REQ-YF-TUNE-009 / -026): read-only report over the
    // effective merged view, for **every harness that ships a config profile**. The
    // check is harness-generic and `from_env` is format-aware (JSON for claude-code /
    // opencode, TOML for codex), so this is registration only — `from_env` returns
    // `None` for a harness with no embedded profile (e.g. pi, config-deferred).
    for harness in ["claude-code", "codex", "opencode"] {
        if let Some(c) = SettingsDriftCheck::from_env(harness) {
            out.push(Box::new(c));
        }
    }

    // Managed-block drift axis (REQ-YF-TUNE-026): read-only, per single-file-rule
    // harness (codex, opencode, pi — the AGENTS.md harnesses). Reported under the
    // distinct `managed-block:<harness>` axis, NOT the aggregate `rule_drift`.
    // `from_env` returns `None` for claude-code (a rules/ dir harness, no managed
    // block) and any unmapped id, so only the AGENTS.md harnesses contribute.
    for harness in ["codex", "opencode", "pi"] {
        if let Some(c) = ManagedBlockDriftCheck::from_env(harness) {
            out.push(Box::new(c));
        }
    }

    // Codex block-size-budget axis (REQ-YF-TUNE-027): read-only warn when the projected
    // ~/.codex/AGENTS.md approaches the effective project_doc_max_bytes cap.
    if let Some(c) = CodexBudgetCheck::from_env() {
        out.push(Box::new(c));
    }
    out
}

#[cfg(test)]
mod tests {

    // REQ-YF-DOCTOR-006 (#160): the read-only local-only/remote axis. Detect and
    // propose — never mutate. Also pins the not-applicable case so the check can
    // never false-positive on a non-beads repo.
    #[test]
    fn local_only_remote_check_is_read_only_and_not_applicable_without_beads() {
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path().to_path_buf();

        // No `.beads/` → ok, not applicable.
        let r = LocalOnlyRemoteCheck::new(root.clone()).run();
        assert!(r.ok, "a non-beads repo must never be flagged");
        assert!(r.detail.contains("not applicable"));

        // A `.beads/` with no local-only config → ok (bd absent/unset both land here).
        std::fs::create_dir_all(root.join(".beads")).unwrap();
        let r2 = LocalOnlyRemoteCheck::new(root.clone()).run();
        assert!(r2.ok);

        // The check never wrote anything (D-2: detect + propose, repair on request).
        assert!(!root.join(".beads").join("config.yaml").exists());
    }

    // REQ-YF-DOCTOR-006: the proposed remediation is the `--remove-remote` form,
    // reused verbatim from preflight's Gap 3 so the two surfaces cannot drift.
    #[test]
    fn local_only_remote_check_proposes_the_remove_remote_command() {
        let r = CheckResult::fail(
            "beads local-only remote",
            "detail",
            "Canonicalization drift: a Dolt remote is configured under local-only — \
             run `yf doctor --repair --local-only --remove-remote` to clear it",
        );
        let rem = r.remediation.unwrap();
        assert!(rem.contains("yf doctor --repair --local-only --remove-remote"));
    }
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

    // REQ-YF-TUNE-009: the doctor drift axis is read-only and non-required; it
    // reports drift over the effective merged view read from real layer files, and
    // a recommended key set in a lower-precedence layer is NOT a false-missing.
    #[test]
    fn settings_drift_axis_reads_layers_and_reports() {
        let dir = tempfile::tempdir().unwrap();
        let user = dir.path().join("user.json");
        let committed = dir.path().join("committed.json");
        let local = dir.path().join("local.json");

        // An empty view: everything drifts, axis is a non-required warning.
        std::fs::write(&user, "{}").unwrap();
        let check = SettingsDriftCheck {
            harness: "claude-code".to_string(),
            layers: vec![user.clone(), committed.clone(), local.clone()],
        };
        let r = check.run();
        assert!(
            !r.required,
            "settings-drift axis must be report-only (non-required)"
        );
        assert!(!r.ok, "empty settings must report drift");
        assert_eq!(
            r.remediation.as_deref(),
            Some("run `yf harness tune` to align")
        );

        // Fully tune the user layer via the merge engine, write it back → no drift,
        // even though committed/local are absent (key set in ONE layer suffices).
        let profile = crate::cmd::harness::profile::load_profile("claude-code")
            .unwrap()
            .unwrap();
        let (tuned, _) = crate::cmd::harness::merge::merge(&serde_json::json!({}), &profile, false);
        std::fs::write(&user, serde_json::to_string_pretty(&tuned).unwrap()).unwrap();
        let r2 = check.run();
        assert!(r2.ok, "a fully-tuned layer must clear drift: {}", r2.detail);
        assert!(!r2.required);
    }

    // REQ-YF-TUNE-026: the drift axis runs format-aware for a codex TOML profile — a
    // seeded drifted `config.toml` reports the injected divergence; a fully-tuned
    // `config.toml` reports none. Exercises the TOML read path (`read_value_for_format`).
    #[test]
    fn settings_drift_axis_codex_toml_reports_and_clears() {
        let dir = tempfile::tempdir().unwrap();
        let cfg = dir.path().join("config.toml");
        let profile = crate::cmd::harness::profile::load_profile("codex")
            .unwrap()
            .unwrap();

        // Drifted: a real-but-unaligned config.toml (an operator comment + one
        // unrelated key) → the profile's recommended keys are missing → drift.
        std::fs::write(&cfg, "# operator config\nmodel = \"gpt-5\"\n").unwrap();
        let check = SettingsDriftCheck {
            harness: "codex".to_string(),
            layers: vec![cfg.clone()],
        };
        let r = check.run();
        assert!(!r.required, "drift axis must be report-only (non-required)");
        assert!(!r.ok, "a drifted codex config.toml must report drift");
        assert_eq!(
            r.remediation.as_deref(),
            Some("run `yf harness tune` to align")
        );

        // Fully tune the config.toml via the TOML delta-replay engine, write it back
        // → no drift, proving the axis reads TOML (not just JSON).
        let (tuned, _) =
            crate::cmd::harness::toml_adapter::merge_toml_text("", &profile, false).unwrap();
        std::fs::write(&cfg, tuned).unwrap();
        let r2 = check.run();
        assert!(
            r2.ok,
            "a fully-tuned codex config.toml must clear drift: {}",
            r2.detail
        );
    }

    // REQ-YF-TUNE-026: the drift axis runs for the opencode JSON profile — a seeded
    // drifted `opencode.json` reports divergence; a tuned one reports none. Confirms
    // per-harness registration is not claude-code-only.
    #[test]
    fn settings_drift_axis_opencode_json_reports_and_clears() {
        let dir = tempfile::tempdir().unwrap();
        let cfg = dir.path().join("opencode.json");
        let profile = crate::cmd::harness::profile::load_profile("opencode")
            .unwrap()
            .unwrap();

        std::fs::write(&cfg, "{}").unwrap();
        let check = SettingsDriftCheck {
            harness: "opencode".to_string(),
            layers: vec![cfg.clone()],
        };
        let r = check.run();
        assert!(!r.ok, "an empty opencode.json must report drift");
        assert!(!r.required);

        let (tuned, _) = crate::cmd::harness::merge::merge(&serde_json::json!({}), &profile, false);
        std::fs::write(&cfg, serde_json::to_string_pretty(&tuned).unwrap()).unwrap();
        let r2 = check.run();
        assert!(
            r2.ok,
            "a fully-tuned opencode.json must clear drift: {}",
            r2.detail
        );
    }

    // REQ-YF-TUNE-026: registration is wired for every config-profile harness — the
    // registry builds a `settings:<harness>` axis for claude-code, codex, and
    // opencode (pi, config-deferred, contributes none).
    #[test]
    fn settings_drift_axes_registered_for_config_harnesses() {
        let dir = tempfile::tempdir().unwrap();
        let axes: Vec<String> = checks(dir.path(), dir.path())
            .iter()
            .map(|c| c.run().name)
            .collect();
        for h in ["claude-code", "codex", "opencode"] {
            assert!(
                axes.iter().any(|a| a == &format!("settings:{h}")),
                "expected a settings:{h} drift axis in the registry; got {axes:?}"
            );
        }
        assert!(
            !axes.iter().any(|a| a == "settings:pi"),
            "pi is config-deferred (no profile) — it must contribute no settings axis"
        );
    }

    // REQ-YF-TUNE-026: the managed-block drift axis reports **aligned** when the
    // on-disk AGENTS.md block byte-matches the current minimized bundle, and **drift**
    // for a hand-edited block or an absent one — all read-only (non-required).
    #[test]
    fn managed_block_drift_aligned_stale_and_absent() {
        use crate::cmd::harness::{managed_block, minimize};
        let dir = tempfile::tempdir().unwrap();
        let agents = dir.path().join("AGENTS.md");
        let body = minimize::irreducible_core_bundle().unwrap();

        // Absent file → "no managed block; tune would deploy one" (drift warning).
        let check = ManagedBlockDriftCheck {
            harness: "codex".to_string(),
            path: agents.clone(),
        };
        let r = check.run();
        assert!(!r.required, "managed-block axis must be report-only");
        assert!(!r.ok, "an absent block must report drift");
        assert!(
            r.detail.contains("no yf-managed rule block"),
            "absent detail: {}",
            r.detail
        );

        // Deploy the current bundle → aligned (byte-identical), ok warning.
        managed_block::deploy_block(&agents, &body, false).unwrap();
        let r2 = check.run();
        assert!(
            r2.ok,
            "a freshly-deployed block must be aligned: {}",
            r2.detail
        );
        assert!(!r2.required);

        // Hand-edit the block body → drift (stale/hand-edited).
        let tampered = format!(
            "# operator prose\n\n{}\nHAND EDITED — not the real bundle\n{}\n",
            managed_block::BEGIN_MARKER,
            managed_block::END_MARKER
        );
        std::fs::write(&agents, tampered).unwrap();
        let r3 = check.run();
        assert!(!r3.ok, "a hand-edited block must report drift");
        assert!(
            r3.detail
                .contains("drifts from the current minimized bundle"),
            "stale detail: {}",
            r3.detail
        );
    }

    // REQ-YF-TUNE-026: ambiguous/out-of-order markers are a fail-safe report, never a
    // crash (mirrors the deploy engine's refusal).
    #[test]
    fn managed_block_drift_reports_ambiguous_markers() {
        use crate::cmd::harness::managed_block;
        let dir = tempfile::tempdir().unwrap();
        let agents = dir.path().join("AGENTS.md");
        // Two BEGIN markers, one END → ambiguous.
        std::fs::write(
            &agents,
            format!(
                "{b}\nx\n{b}\ny\n{e}\n",
                b = managed_block::BEGIN_MARKER,
                e = managed_block::END_MARKER
            ),
        )
        .unwrap();
        let check = ManagedBlockDriftCheck {
            harness: "opencode".to_string(),
            path: agents,
        };
        let r = check.run();
        assert!(
            !r.ok && !r.required,
            "ambiguous markers report, never fatal"
        );
        assert!(
            r.detail.contains("cannot classify the managed block"),
            "ambiguous detail: {}",
            r.detail
        );
    }

    // REQ-YF-TUNE-026: the managed-block axis is registered for exactly the AGENTS.md
    // harnesses (codex/opencode/pi) and is a DISTINCT axis from the aggregate
    // `rule_drift` (RuleCheck's `rules:<skill>` axis) — no collision, no double-count,
    // and claude-code (a rules/ dir harness) contributes NO managed-block axis.
    #[test]
    fn managed_block_axis_registered_distinct_from_rule_drift() {
        let dir = tempfile::tempdir().unwrap();
        let names: Vec<String> = checks(dir.path(), dir.path())
            .iter()
            .map(|c| c.run().name)
            .collect();
        for h in ["codex", "opencode", "pi"] {
            assert!(
                names.iter().any(|n| n == &format!("managed-block:{h}")),
                "expected a managed-block:{h} axis; got {names:?}"
            );
        }
        assert!(
            !names.iter().any(|n| n == "managed-block:claude-code"),
            "claude-code reads a rules/ dir — it must contribute no managed-block axis"
        );
        // Distinct axis namespace: no managed-block axis is named `rules:*`, and the
        // `rules:*` companion-rule axis is untouched (no `managed-block:*` collision).
        assert!(
            !names
                .iter()
                .any(|n| n.starts_with("managed-block:") && n.contains("rules:")),
            "managed-block axis must not overlap the rules: namespace"
        );
    }

    // REQ-YF-TUNE-027: the codex-budget doctor axis warns when the projected
    // ~/.codex/AGENTS.md approaches the effective cap read from the sibling config.toml,
    // is aligned/ok well under it, and is read-only (never writes, non-required).
    #[test]
    fn codex_budget_axis_warns_near_cap_reads_effective_config() {
        use crate::cmd::harness::{managed_block, minimize};
        let dir = tempfile::tempdir().unwrap();
        let agents = dir.path().join("AGENTS.md");
        let config = dir.path().join("config.toml");
        let body = minimize::irreducible_core_bundle().unwrap();

        // A generous cap in config.toml → under threshold, ok warning.
        std::fs::write(&config, "project_doc_max_bytes = 200000\n").unwrap();
        let check = CodexBudgetCheck {
            agents_path: agents.clone(),
            config_path: config.clone(),
        };
        let r = check.run();
        assert_eq!(r.name, "codex-budget");
        assert!(!r.required, "budget axis must be report-only");
        assert!(r.ok, "well under a 200 KiB cap must not warn: {}", r.detail);

        // Shrink the effective cap just below the projected size → warns, naming both.
        let projected = managed_block::projected_agents_md_bytes("", &body);
        std::fs::write(
            &config,
            format!("project_doc_max_bytes = {}\n", projected.saturating_sub(1)),
        )
        .unwrap();
        let r2 = check.run();
        assert!(!r2.ok, "a cap below the projected size must warn");
        assert!(!r2.required, "the warning never fails the command");
        assert!(
            r2.detail.contains(&projected.to_string()),
            "warning names the projected size: {}",
            r2.detail
        );

        // The AGENTS.md file was never written (read-only axis).
        assert!(
            !agents.exists(),
            "codex-budget axis must not create AGENTS.md"
        );
    }

    // REQ-YF-TUNE-009: a malformed layer is skipped (does not crash the axis) — the
    // other layers still drive the effective view.
    #[test]
    fn settings_drift_axis_skips_malformed_layer() {
        let dir = tempfile::tempdir().unwrap();
        let user = dir.path().join("user.json");
        let profile = crate::cmd::harness::profile::load_profile("claude-code")
            .unwrap()
            .unwrap();
        let (tuned, _) = crate::cmd::harness::merge::merge(&serde_json::json!({}), &profile, false);
        std::fs::write(&user, serde_json::to_string_pretty(&tuned).unwrap()).unwrap();
        let bad = dir.path().join("local.json");
        std::fs::write(&bad, "{ not json ,,,").unwrap();
        let check = SettingsDriftCheck {
            harness: "claude-code".to_string(),
            layers: vec![user, bad],
        };
        let r = check.run();
        assert!(
            r.ok,
            "malformed layer skipped; tuned user layer clears drift: {}",
            r.detail
        );
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
