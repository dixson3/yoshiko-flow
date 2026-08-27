//! Settings-file scope resolution and fail-safe read/write (REQ-YF-TUNE-003/006).
//!
//! Scope resolution (REQ-YF-TUNE-003):
//! - **user** (default) → `$HOME/<surface_dir>/<settings_filename>`
//!   (e.g. `~/.claude/settings.json`), disjoint from the project beads hook.
//! - **project-local** (`--project`) → `<git-root>/<surface_dir>/<settings_local>`
//!   (the personal, gitignored `settings.local.json` — the safe default).
//! - **project-committed** (`--project --committed`) → `<git-root>/<surface_dir>/
//!   <settings_filename>` (the shared `settings.json`).
//!
//! Read is **fail-safe** (REQ-YF-TUNE-006): a present-but-unparseable file yields
//! [`SettingsRead::Malformed`] so the command refuses and reports rather than
//! overwriting. Because the merge writes only the profile's own keys, any
//! `bd setup claude` hook block (under the profile's `hook_preserve_key`) is left
//! untouched.

use std::path::{Path, PathBuf};

use serde::Deserialize;
use serde_json::Value;

use super::profile::Profile;

/// The on-disk format of a harness's settings/config file (REQ-YF-TUNE-013/014).
///
/// The merge *decision* is always computed over a `serde_json::Value` (the
/// engine in [`super::merge`] is pure over `Value`); this enum selects the
/// read/write adapter that bridges the file's real format to that `Value`.
/// `Json` is the existing pretty-write path ([`read_settings`]/[`write_settings`]);
/// `Toml` is the trivia-preserving delta-replay path ([`super::toml_adapter`]).
///
/// Carried on [`Profile`] as a `#[serde(default)]` field (REQ-YF-TUNE-014): a
/// profile JSON with no `format` key (e.g. `claude-code.json`) deserializes to
/// [`SettingsFormat::Json`], so the existing JSON tune path is behavior-identical.
/// [`super::run_core`] dispatches read/merge/write on this value.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum SettingsFormat {
    /// `settings.json` / `opencode.json` — the existing `serde_json` path.
    #[default]
    Json,
    /// `config.toml` — the `toml_edit` delta-replay path.
    Toml,
}

/// The resolved write target for `yf harness tune`.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TuneScope {
    /// `$HOME/<surface>/settings.json` (default).
    User,
    /// `<git-root>/<surface>/settings.local.json` (personal, gitignored).
    ProjectLocal,
    /// `<git-root>/<surface>/settings.json` (shared, committed).
    ProjectCommitted,
}

impl TuneScope {
    /// Resolve the scope from the two CLI flags. `--committed` is only meaningful
    /// under `--project`; without `--project` it is ignored (user scope wins).
    pub fn resolve(project: bool, committed: bool) -> TuneScope {
        match (project, committed) {
            (false, _) => TuneScope::User,
            (true, false) => TuneScope::ProjectLocal,
            (true, true) => TuneScope::ProjectCommitted,
        }
    }

    /// A short human label for reporting.
    pub fn label(self) -> &'static str {
        match self {
            TuneScope::User => "user",
            TuneScope::ProjectLocal => "project (settings.local.json)",
            TuneScope::ProjectCommitted => "project (committed settings.json)",
        }
    }
}

/// `$HOME`, falling back to cwd — total resolution (mirrors `dest.rs`).
fn home_dir() -> PathBuf {
    std::env::var_os("HOME")
        .map(PathBuf::from)
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
}

/// Resolve the settings-file path for `profile` at `scope`, anchored at `home`
/// (user) or `root` (project). Pure — no env reads — so it is unit-testable.
pub fn settings_path_at(profile: &Profile, scope: TuneScope, home: &Path, root: &Path) -> PathBuf {
    let (anchor, filename) = match scope {
        TuneScope::User => (home, &profile.settings_filename),
        TuneScope::ProjectLocal => (root, &profile.settings_local_filename),
        TuneScope::ProjectCommitted => (root, &profile.settings_filename),
    };
    anchor.join(&profile.surface_dir).join(filename)
}

/// Every config path this harness ITSELF reads at `scope`, **highest precedence first**
/// (`REQ-YF-TUNE-030`, plan-054 / EXP-003).
///
/// This is the **audit-class** resolver and is deliberately distinct from
/// [`settings_path_at`], which resolves the single **write** target and is unchanged. `yf`
/// still writes exactly one file per harness; it must nevertheless *read* every layer the
/// harness obeys, because a read set narrower than the harness's own reports a green over a
/// higher-precedence layer it cannot see. Measured: opencode reads `opencode.jsonc` ahead of
/// `opencode.json`, so today's agreement is coincidence.
///
/// A profile that declares no layers yields exactly `[settings_path_at(...)]`, preserving
/// today's behaviour rather than reading nothing.
pub fn settings_read_paths_at(
    profile: &Profile,
    scope: TuneScope,
    home: &Path,
    root: &Path,
) -> Vec<PathBuf> {
    let anchor = match scope {
        TuneScope::User => home,
        TuneScope::ProjectLocal | TuneScope::ProjectCommitted => root,
    };
    profile
        .read_layers()
        .into_iter()
        .map(|f| anchor.join(&profile.surface_dir).join(f))
        .collect()
}

/// Layers, other than the one `yf` writes, that EXIST on disk and therefore SHADOW it.
///
/// Returns the shadowing paths in precedence order. A non-empty result is the condition a
/// tune-time warning must name explicitly: the operator is about to have `yf` write a file
/// whose values the harness will not obey.
pub fn shadowing_layers_at(
    profile: &Profile,
    scope: TuneScope,
    home: &Path,
    root: &Path,
) -> Vec<PathBuf> {
    let write_target = settings_path_at(profile, scope, home, root);
    settings_read_paths_at(profile, scope, home, root)
        .into_iter()
        .take_while(|p| p != &write_target) // only HIGHER-precedence layers shadow
        .filter(|p| p.exists())
        .collect()
}

/// Resolve the always-loaded **rules dir** for `profile` at `scope`, anchored at
/// `home` (user) or `root` (project) — the sibling `rules/` of the harness surface
/// dir (e.g. `~/.claude/rules`). Anchored identically to [`settings_path_at`] so
/// tune's rule-deploy sub-operation tracks its config scope. Pure — no env reads.
///
/// This is the destination for the `YOSHIKO_FLOW.md` aggregation that
/// `yf harness tune` now owns (REQ-YF-FLOW-007); it matches the sibling-`rules/`
/// layout `dest::resolve_rules_dir` produces for the same harness's skills dir.
///
/// Reserved profile-driven seam. Issue 7.1's per-harness orchestration resolves the
/// claude-code rules dir directly off the rule-target map
/// ([`super::managed_block::RuleTarget::resolve_at`], `RulesDir` → `<surface>/rules`),
/// so this convenience wrapper is not on the live `tune` path today.
#[allow(dead_code)]
pub fn rules_dir_at(profile: &Profile, scope: TuneScope, home: &Path, root: &Path) -> PathBuf {
    let anchor = match scope {
        TuneScope::User => home,
        TuneScope::ProjectLocal | TuneScope::ProjectCommitted => root,
    };
    anchor.join(&profile.surface_dir).join("rules")
}

/// Resolve the rules dir from the real environment (`$HOME` + git root). Reserved
/// real-env convenience twin of [`rules_dir_at`] (see its note).
#[allow(dead_code)]
pub fn rules_dir(profile: &Profile, scope: TuneScope) -> PathBuf {
    let root = crate::dest::git_root_or_cwd();
    rules_dir_at(profile, scope, &home_dir(), &root)
}

/// The outcome of reading a settings file.
#[derive(Debug)]
pub enum SettingsRead {
    /// No file at the path — start from an empty object (a fresh tune).
    Absent,
    /// A valid JSON value (expected to be an object).
    Parsed(Value),
    /// The file exists but is not valid JSON — the fail-safe refusal signal.
    Malformed(String),
}

/// Read the settings file at `path`, classifying it fail-safe (REQ-YF-TUNE-006).
pub fn read_settings(path: &Path) -> SettingsRead {
    match std::fs::read_to_string(path) {
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => SettingsRead::Absent,
        Err(e) => SettingsRead::Malformed(format!("cannot read {}: {e}", path.display())),
        Ok(text) if text.trim().is_empty() => SettingsRead::Absent,
        Ok(text) => match serde_json::from_str::<Value>(&text) {
            Ok(v) => SettingsRead::Parsed(v),
            Err(e) => SettingsRead::Malformed(format!("{}: {e}", path.display())),
        },
    }
}

/// Read the settings/config file at `path` into a `serde_json::Value` view,
/// dispatching on `format` (REQ-YF-TUNE-026). `Json` uses [`read_settings`]; `Toml`
/// parses the `config.toml` and derives the decision-only `Value`
/// ([`super::toml_adapter::parse_toml_to_json`]). An absent or malformed file yields
/// `None` — the layer is skipped from the effective view, matching the drift axis's
/// malformed-layer-skip semantics. Read-only: the derived `Value` is never written
/// back (for TOML that would drop trivia; writes go through the delta-replay path).
pub fn read_value_for_format(path: &Path, format: SettingsFormat) -> Option<Value> {
    match format {
        SettingsFormat::Json => match read_settings(path) {
            SettingsRead::Parsed(v) => Some(v),
            SettingsRead::Absent | SettingsRead::Malformed(_) => None,
        },
        SettingsFormat::Toml => match read_toml(path) {
            TomlRead::Parsed(text) => super::toml_adapter::parse_toml_to_json(&text).ok(),
            TomlRead::Absent | TomlRead::Malformed(_) => None,
        },
    }
}

/// Write `value` to `path` as pretty JSON with a trailing newline, creating parent
/// dirs. Preserves key order (`serde_json` preserve-order).
pub fn write_settings(path: &Path, value: &Value) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut text = serde_json::to_string_pretty(value).unwrap_or_else(|_| "{}".to_string());
    text.push('\n');
    std::fs::write(path, text)
}

/// The outcome of reading a TOML config file (`config.toml`) — the format-parallel
/// of [`SettingsRead`] for the [`SettingsFormat::Toml`] dispatch (REQ-YF-TUNE-014).
///
/// Carries the **raw file text** (not a parsed value): the TOML write path is
/// delta-replay ([`super::toml_adapter::merge_toml_text`]), which parses the text
/// itself into a trivia-preserving document. Classification is fail-safe
/// (REQ-YF-TUNE-006): a present-but-unparseable file yields [`TomlRead::Malformed`]
/// so the command refuses rather than overwriting.
#[derive(Debug)]
pub enum TomlRead {
    /// No file (or an empty one) — start from an empty document (a fresh tune).
    Absent,
    /// A parseable `config.toml`; the tuple is its verbatim text (the write source).
    Parsed(String),
    /// The file exists but is not valid TOML — the fail-safe refusal signal.
    Malformed(String),
}

/// Read the TOML config file at `path`, classifying it fail-safe (REQ-YF-TUNE-006).
/// Parses with [`super::toml_adapter::parse_document`] to validate; on success the
/// original text is returned untouched (the delta-replay write source).
pub fn read_toml(path: &Path) -> TomlRead {
    match std::fs::read_to_string(path) {
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => TomlRead::Absent,
        Err(e) => TomlRead::Malformed(format!("cannot read {}: {e}", path.display())),
        Ok(text) if text.trim().is_empty() => TomlRead::Absent,
        Ok(text) => match super::toml_adapter::parse_document(&text) {
            Ok(_) => TomlRead::Parsed(text),
            Err(e) => TomlRead::Malformed(format!("{}: {e}", path.display())),
        },
    }
}

/// Write raw `text` to `path`, creating parent dirs. The verbatim-string write used
/// by the TOML delta-replay path (the document already carries its own trailing
/// trivia, so no newline is appended here).
pub fn write_text(path: &Path, text: &str) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(path, text)
}

#[cfg(test)]
mod tests {
    use super::super::profile::load_profile;
    use super::*;

    fn profile() -> Profile {
        load_profile("claude-code").unwrap().unwrap()
    }

    // REQ-YF-TUNE-003: scope resolution from the flag pair.
    #[test]
    fn scope_resolution() {
        assert_eq!(TuneScope::resolve(false, false), TuneScope::User);
        assert_eq!(
            TuneScope::resolve(false, true),
            TuneScope::User,
            "committed ignored w/o project"
        );
        assert_eq!(TuneScope::resolve(true, false), TuneScope::ProjectLocal);
        assert_eq!(TuneScope::resolve(true, true), TuneScope::ProjectCommitted);
    }

    // REQ-YF-TUNE-003: each scope resolves to the correct file under the surface dir.
    #[test]
    fn scope_paths() {
        let p = profile();
        let home = Path::new("/home/jd");
        let root = Path::new("/repo");
        assert_eq!(
            settings_path_at(&p, TuneScope::User, home, root),
            PathBuf::from("/home/jd/.claude/settings.json")
        );
        assert_eq!(
            settings_path_at(&p, TuneScope::ProjectLocal, home, root),
            PathBuf::from("/repo/.claude/settings.local.json")
        );
        assert_eq!(
            settings_path_at(&p, TuneScope::ProjectCommitted, home, root),
            PathBuf::from("/repo/.claude/settings.json")
        );
    }

    // REQ-YF-TUNE-006: an absent file reads as Absent (fresh), an empty file too.
    #[test]
    fn absent_and_empty_read_as_absent() {
        let dir = tempfile::tempdir().unwrap();
        let missing = dir.path().join("nope.json");
        assert!(matches!(read_settings(&missing), SettingsRead::Absent));
        let empty = dir.path().join("empty.json");
        std::fs::write(&empty, "   \n").unwrap();
        assert!(matches!(read_settings(&empty), SettingsRead::Absent));
    }

    // REQ-YF-TUNE-006: a malformed file reads as Malformed (the fail-safe refusal
    // signal) — the caller must NOT overwrite it.
    #[test]
    fn malformed_read_is_flagged() {
        let dir = tempfile::tempdir().unwrap();
        let bad = dir.path().join("settings.json");
        std::fs::write(&bad, "{ this is not json ,,, ").unwrap();
        match read_settings(&bad) {
            SettingsRead::Malformed(_) => {}
            other => panic!("expected Malformed, got {other:?}"),
        }
    }

    // REQ-YF-TUNE-006: write round-trips and preserves a bd setup claude hook block
    // (under the profile's hook_preserve_key) untouched.
    #[test]
    fn write_preserves_hook_block() {
        let dir = tempfile::tempdir().unwrap();
        let path = dir.path().join(".claude").join("settings.json");
        let with_hook = serde_json::json!({
            "hooks": { "SessionStart": [{ "command": "bd prime" }] },
            "todoFeatureEnabled": false
        });
        write_settings(&path, &with_hook).unwrap();
        let SettingsRead::Parsed(back) = read_settings(&path) else {
            panic!("round-trip must parse");
        };
        assert_eq!(
            back["hooks"]["SessionStart"][0]["command"],
            serde_json::json!("bd prime")
        );
    }
}
