//! Install-receipt contract for `yf self …` (plan-018 Issue 3.1).
//!
//! Two receipts live under `~/.config/yf` (the [`crate::dirs`] config dir):
//!
//! 1. **cargo-dist's own receipt** `yf-receipt.json` — written by the generated
//!    `curl|sh` installer (verified intact in Issue 1.3). Its schema is **fixed**
//!    by cargo-dist (we do not control it). The load-bearing field is
//!    **`install_prefix`** — the canonicalized form of this path is what the source
//!    classifier (3.3) keys vendor-detection on. NOTE: the receipt's `source` field
//!    is a **repo descriptor** (`app_name`/`owner`/…), NOT an install classifier —
//!    never branch on it (the pass-1 correction).
//!
//! 2. **yf's own from-build marker** `yf-from-build.json` — the one receipt yf
//!    authors, written ONLY by `yf self install --from-build` (3.5). Its presence
//!    marks a developer build so the upgrade nag (4.1) and `self update` (3.4)
//!    treat the binary as from-build (no-nag / `--force` required).
//!
//! Path-derived classification (3.3) is authoritative; these receipts **corroborate**
//! but are never required — detection must survive a missing or `INSTALL_UPDATER=0`
//! receipt.

use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};

use crate::dirs::Dirs;

/// Basename of cargo-dist's install receipt under the config dir.
const RECEIPT_BASENAME: &str = "yf-receipt.json";
/// Basename of yf's own from-build marker under the config dir.
const FROM_BUILD_BASENAME: &str = "yf-from-build.json";

/// Path to cargo-dist's install receipt (`~/.config/yf/yf-receipt.json`).
pub fn receipt_path(dirs: &Dirs) -> PathBuf {
    dirs.config_dir().join(RECEIPT_BASENAME)
}

/// Path to yf's from-build marker (`~/.config/yf/yf-from-build.json`).
pub fn from_build_marker_path(dirs: &Dirs) -> PathBuf {
    dirs.config_dir().join(FROM_BUILD_BASENAME)
}

/// cargo-dist's install receipt — **only the fields yf reads**.
///
/// `#[serde(default)]` + tolerating unknown keys: the real receipt also carries
/// `binary_aliases`, `cdylibs`, `cstaticlibs`, `modify_path`, etc. (see Issue 1.3
/// finding). We deliberately model only `install_prefix` + `version` (+ the inert
/// `provider`/`source` for diagnostics) so an upstream cargo-dist schema addition
/// never breaks parsing.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct CargoDistReceipt {
    /// The install prefix the binary was written to (e.g. `~/.local/bin`,
    /// pre-canonicalization). The authoritative vendor signal once canonicalized.
    #[serde(default)]
    pub install_prefix: String,
    /// Layout descriptor (cargo-dist emits `"unspecified"` for the flat layout).
    #[serde(default)]
    pub install_layout: String,
    /// Semver recorded at install time.
    #[serde(default)]
    pub version: String,
}

impl CargoDistReceipt {
    /// The receipt's `install_prefix` as a path, **canonicalized** so a symlinked
    /// install dir (e.g. `~/.local/bin` → a real store path) compares equal to a
    /// canonicalized `current_exe()` in 3.3. Returns `None` when the field is empty
    /// or the path cannot be canonicalized (e.g. the dir no longer exists).
    pub fn canonical_install_prefix(&self) -> Option<PathBuf> {
        if self.install_prefix.is_empty() {
            return None;
        }
        let raw = expand_tilde(&self.install_prefix);
        std::fs::canonicalize(&raw).ok()
    }
}

/// yf's from-build marker — authored by `--from-build` (3.5), read here.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FromBuildMarker {
    /// Always `"from-build"` — the install-source discriminator yf controls.
    pub source: String,
    /// The crate version that was promoted (the dev build's `CARGO_PKG_VERSION`).
    pub version: String,
    /// `"release"` or `"debug"` — which profile was promoted.
    pub profile: String,
}

impl FromBuildMarker {
    /// Construct a marker for the given version/profile (`source` is fixed).
    pub fn new(version: impl Into<String>, profile: impl Into<String>) -> Self {
        Self {
            source: "from-build".to_string(),
            version: version.into(),
            profile: profile.into(),
        }
    }
}

/// Load and parse cargo-dist's receipt, if present and well-formed.
///
/// A missing file is `Ok(None)` (vendor detection must survive an absent receipt).
/// A present-but-malformed file is an `Err` the caller may downgrade to `None`.
pub fn load_receipt(dirs: &Dirs) -> Result<Option<CargoDistReceipt>> {
    load_json(&receipt_path(dirs))
}

/// Load yf's from-build marker, if present and well-formed.
pub fn load_from_build_marker(dirs: &Dirs) -> Result<Option<FromBuildMarker>> {
    load_json(&from_build_marker_path(dirs))
}

/// Write yf's from-build marker atomically (parent dir created if needed).
pub fn write_from_build_marker(dirs: &Dirs, marker: &FromBuildMarker) -> Result<PathBuf> {
    let path = from_build_marker_path(dirs);
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)
            .with_context(|| format!("creating config dir {}", parent.display()))?;
    }
    let json = serde_json::to_string_pretty(marker)?;
    write_atomic(&path, json.as_bytes())
        .with_context(|| format!("writing from-build marker {}", path.display()))?;
    Ok(path)
}

/// Remove yf's from-build marker if it exists (used by `self update`'s round-trip
/// back to a vendor release, and by `self uninstall`). Absent → `Ok(())`.
pub fn remove_from_build_marker(dirs: &Dirs) -> Result<()> {
    let path = from_build_marker_path(dirs);
    match std::fs::remove_file(&path) {
        Ok(()) => Ok(()),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(e) => Err(e).with_context(|| format!("removing {}", path.display())),
    }
}

/// Parse a JSON file into `T`; missing file → `Ok(None)`.
fn load_json<T: for<'de> Deserialize<'de>>(path: &Path) -> Result<Option<T>> {
    match std::fs::read_to_string(path) {
        Ok(s) => {
            let v = serde_json::from_str::<T>(&s)
                .with_context(|| format!("parsing {}", path.display()))?;
            Ok(Some(v))
        }
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(None),
        Err(e) => Err(e).with_context(|| format!("reading {}", path.display())),
    }
}

/// Expand a leading `~/` against `$HOME` (cargo-dist stores `install_prefix` with a
/// literal tilde in some configs). Non-tilde paths pass through unchanged.
fn expand_tilde(p: &str) -> PathBuf {
    if let Some(rest) = p.strip_prefix("~/") {
        if let Some(home) = std::env::var_os("HOME") {
            return PathBuf::from(home).join(rest);
        }
    }
    PathBuf::from(p)
}

/// Write `bytes` to `path` via a same-dir temp file + atomic rename (no runtime
/// dep on `tempfile`; the sibling temp keeps the rename within one filesystem).
fn write_atomic(path: &Path, bytes: &[u8]) -> Result<()> {
    use std::io::Write;
    let dir = path.parent().unwrap_or_else(|| Path::new("."));
    let tmp = dir.join(format!(".{}.tmp.{}", basename(path), std::process::id()));
    {
        let mut f = std::fs::File::create(&tmp)
            .with_context(|| format!("creating temp {}", tmp.display()))?;
        f.write_all(bytes)?;
        f.flush()?;
    }
    match std::fs::rename(&tmp, path) {
        Ok(()) => Ok(()),
        Err(e) => {
            let _ = std::fs::remove_file(&tmp);
            Err(e).with_context(|| format!("renaming temp into {}", path.display()))
        }
    }
}

/// Final path component as a string (for the temp filename); `"out"` if none.
fn basename(path: &Path) -> String {
    path.file_name()
        .map(|s| s.to_string_lossy().into_owned())
        .unwrap_or_else(|| "out".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn dirs_with_config(home: &Path) -> Dirs {
        // Drive the resolver with an explicit HOME so the config dir lands in a
        // temp tree — no real $HOME touched.
        let home = home.to_path_buf();
        crate::dirs::resolve(move |k| match k {
            "HOME" => Some(home.clone().into_os_string()),
            _ => None,
        })
    }

    // REQ-YF-SELF-001: install-receipt contract (~/.config/yf/yf-receipt.json + from-build marker).
    #[test]
    fn missing_receipt_is_none() {
        let tmp = tempfile::tempdir().unwrap();
        let dirs = dirs_with_config(tmp.path());
        assert!(load_receipt(&dirs).unwrap().is_none());
        assert!(load_from_build_marker(&dirs).unwrap().is_none());
    }

    #[test]
    fn parses_real_cargo_dist_schema_ignoring_extra_keys() {
        let tmp = tempfile::tempdir().unwrap();
        let dirs = dirs_with_config(tmp.path());
        std::fs::create_dir_all(dirs.config_dir()).unwrap();
        // The actual cargo-dist receipt (Issue 1.3 finding) with extra keys.
        let body = r#"{
            "binaries": ["yf"], "binary_aliases": {}, "cdylibs": [], "cstaticlibs": [],
            "install_layout": "unspecified", "install_prefix": "/opt/x/.local/bin",
            "modify_path": true,
            "provider": {"source": "cargo-dist", "version": "0.32.0"},
            "source": {"app_name": "yf", "name": "yoshiko-flow", "owner": "dixson3", "release_type": "github"},
            "version": "0.3.2"
        }"#;
        std::fs::write(receipt_path(&dirs), body).unwrap();
        let r = load_receipt(&dirs).unwrap().unwrap();
        assert_eq!(r.install_prefix, "/opt/x/.local/bin");
        assert_eq!(r.install_layout, "unspecified");
        assert_eq!(r.version, "0.3.2");
    }

    #[test]
    fn from_build_marker_round_trips() {
        let tmp = tempfile::tempdir().unwrap();
        let dirs = dirs_with_config(tmp.path());
        let m = FromBuildMarker::new("0.4.0-dev", "release");
        let path = write_from_build_marker(&dirs, &m).unwrap();
        assert_eq!(path, from_build_marker_path(&dirs));
        let loaded = load_from_build_marker(&dirs).unwrap().unwrap();
        assert_eq!(loaded.source, "from-build");
        assert_eq!(loaded.version, "0.4.0-dev");
        assert_eq!(loaded.profile, "release");
        // Removal is idempotent.
        remove_from_build_marker(&dirs).unwrap();
        assert!(load_from_build_marker(&dirs).unwrap().is_none());
        remove_from_build_marker(&dirs).unwrap();
    }

    #[test]
    fn canonical_prefix_none_for_nonexistent() {
        let r = CargoDistReceipt {
            install_prefix: "/no/such/path/anywhere".to_string(),
            ..Default::default()
        };
        assert!(r.canonical_install_prefix().is_none());
    }

    #[test]
    fn canonical_prefix_resolves_symlink() {
        let tmp = tempfile::tempdir().unwrap();
        let real = tmp.path().join("real-bin");
        std::fs::create_dir_all(&real).unwrap();
        let link = tmp.path().join("link-bin");
        #[cfg(unix)]
        std::os::unix::fs::symlink(&real, &link).unwrap();
        #[cfg(not(unix))]
        std::fs::create_dir_all(&link).unwrap();
        let r = CargoDistReceipt {
            install_prefix: link.to_string_lossy().into_owned(),
            ..Default::default()
        };
        let canon = r.canonical_install_prefix().unwrap();
        assert_eq!(canon, std::fs::canonicalize(&real).unwrap());
    }
}
