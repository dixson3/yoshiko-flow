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

use serde_json::Value;

use super::profile::Profile;

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

/// Resolve the settings-file path from the real environment (`$HOME` + git root).
pub fn settings_path(profile: &Profile, scope: TuneScope) -> PathBuf {
    let root = crate::dest::git_root_or_cwd();
    settings_path_at(profile, scope, &home_dir(), &root)
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
