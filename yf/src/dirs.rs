//! Cross-platform, XDG-style directory resolver for `yf`'s own state.
//!
//! plan-018 decision 3: `yf` stores its config / cache / data under an **XDG**
//! layout on **both** Unix and macOS (deliberately NOT macOS's
//! `~/Library/Application Support`), honoring the `XDG_*` overrides, and installs
//! its binary to `~/.local/bin`. Every `yf`-owned directory lookup routes through
//! this one module — the foundation for the install receipt (`~/.config/yf`), the
//! update-check cache (`~/.cache/yf`), and the future on-disk materialization
//! target (`~/.local/share/yf`, the follow-on seam).
//!
//! This is a **thin, dependency-free** resolver (not the `etcetera` crate). Issue
//! 2.1 permits "etcetera or a thin resolver"; a hand resolver keeps the binary
//! small (GR-011), matches the existing `dest.rs` `$HOME`-from-env pattern, and is
//! trivially pure/testable — the core takes an explicit env lookup closure, so no
//! test ever touches the real `$HOME`. etcetera's chief value is its Windows arm,
//! which decision 4 stubs regardless.
//!
//! **Resolution is total** (matches `dest.rs`): a missing `$HOME` falls back to the
//! current directory rather than failing, so directory lookups never panic.
//!
//! ## Project vs home (the `~/.yf` distinction)
//! These are `yf`'s **home-scoped** dirs (per-user, `$HOME`-anchored). They are
//! distinct from **project** state, which stays git-root-anchored (see `dest.rs`
//! `git_root_or_cwd`). `yf` does NOT use a self-contained `~/.yf` home — decision 3
//! dropped it in favor of this XDG split. The `~/.local/share/yf` data dir is the
//! anchor the follow-on on-disk materialization target (decision 7) will hang off.

use std::ffi::OsString;
use std::path::{Path, PathBuf};

/// `yf`'s application sub-directory name under each XDG base dir.
const APP: &str = "yf";

/// Resolved, `yf`-scoped directories.
///
/// `config`/`cache`/`data` already include the `yf/` application leaf; `bin` is the
/// install directory itself (`~/.local/bin`) — the binary `yf` lives directly in it,
/// matching the cargo-dist receipt's `install_prefix` (plan-018 1.2/1.3).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Dirs {
    config: PathBuf,
    cache: PathBuf,
    data: PathBuf,
    bin: PathBuf,
}

impl Dirs {
    /// `~/.config/yf` (or `$XDG_CONFIG_HOME/yf`). Home of the install receipt
    /// (`yf-receipt.json`) and the yf-from-build marker.
    pub fn config_dir(&self) -> &Path {
        &self.config
    }

    /// `~/.cache/yf` (or `$XDG_CACHE_HOME/yf`). Home of the throttled update-check
    /// cache (`update-check.json`).
    pub fn cache_dir(&self) -> &Path {
        &self.cache
    }

    /// `~/.local/share/yf` (or `$XDG_DATA_HOME/yf`). The follow-on on-disk
    /// materialization seam (decision 7) hangs off this.
    ///
    /// `allow(dead_code)`: this path is the deferred on-disk-materialization seam
    /// (bead `yf-d4x3`, NOT built in plan-018). It is exposed now so the seam lands
    /// cleanly later; its first consumer arrives with the follow-on epic.
    #[allow(dead_code)]
    pub fn data_dir(&self) -> &Path {
        &self.data
    }

    /// `~/.local/bin` (or `$XDG_BIN_HOME`). The vendor install directory — the
    /// binary `yf` lives directly here; this is the canonicalized `install_prefix`
    /// the source classifier (3.3) keys vendor detection on.
    pub fn bin_dir(&self) -> &Path {
        &self.bin
    }

    /// Resolve from the real process environment.
    pub fn from_env() -> Self {
        resolve(|key| std::env::var_os(key))
    }
}

/// Pure resolver core: build [`Dirs`] from an explicit environment lookup.
///
/// `lookup` maps an env var name to its value (`None` when unset). Tests pass a
/// map-backed closure; [`Dirs::from_env`] passes [`std::env::var_os`]. The split
/// keeps resolution pure — no test reads the real `$HOME` or `XDG_*`.
pub fn resolve(lookup: impl Fn(&str) -> Option<OsString>) -> Dirs {
    #[cfg(not(windows))]
    {
        resolve_xdg(&lookup)
    }
    #[cfg(windows)]
    {
        resolve_windows(&lookup)
    }
}

/// XDG resolution (Unix + macOS). macOS deliberately uses the XDG layout, NOT
/// `~/Library/...` (decision 3).
#[cfg(not(windows))]
fn resolve_xdg(lookup: &impl Fn(&str) -> Option<OsString>) -> Dirs {
    let home = home_dir(lookup);
    Dirs {
        config: xdg_base(lookup, "XDG_CONFIG_HOME", &home, &[".config"]).join(APP),
        cache: xdg_base(lookup, "XDG_CACHE_HOME", &home, &[".cache"]).join(APP),
        data: xdg_base(lookup, "XDG_DATA_HOME", &home, &[".local", "share"]).join(APP),
        // bin has no `yf/` leaf — the binary file is named `yf` and sits directly
        // in the install dir. XDG_BIN_HOME is non-standard but honored for parity.
        bin: xdg_base(lookup, "XDG_BIN_HOME", &home, &[".local", "bin"]),
    }
}

/// Resolve one XDG base dir: use `$VAR` when it is set to an **absolute** path
/// (per the XDG Base Directory spec — a relative or empty value is ignored), else
/// `$HOME` joined with `default_rel`.
#[cfg(not(windows))]
fn xdg_base(
    lookup: &impl Fn(&str) -> Option<OsString>,
    var: &str,
    home: &Path,
    default_rel: &[&str],
) -> PathBuf {
    if let Some(val) = lookup(var) {
        let p = PathBuf::from(&val);
        // XDG spec: ignore non-absolute (and implicitly empty) values.
        if p.is_absolute() {
            return p;
        }
    }
    let mut base = home.to_path_buf();
    for seg in default_rel {
        base.push(seg);
    }
    base
}

/// `$HOME`, falling back to the current directory then `.` — keeps resolution
/// total (mirrors `dest.rs::home_dir`).
#[cfg(not(windows))]
fn home_dir(lookup: &impl Fn(&str) -> Option<OsString>) -> PathBuf {
    lookup("HOME")
        .map(PathBuf::from)
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
}

/// Windows arm — **stubbed** (plan-018 decision 4; Windows is a follow-on target).
///
/// Maps to the conventional `%LOCALAPPDATA%` / `%APPDATA%` roots so the shape is
/// plausible, but this path is **unbuilt and untested** today (Windows is not in
/// the release matrix). The follow-on epic finalizes and tests it.
#[cfg(windows)]
fn resolve_windows(lookup: &impl Fn(&str) -> Option<OsString>) -> Dirs {
    let local = win_base(lookup, "LOCALAPPDATA", &["AppData", "Local"]);
    let roaming = win_base(lookup, "APPDATA", &["AppData", "Roaming"]);
    Dirs {
        config: roaming.join(APP).join("config"),
        cache: local.join(APP).join("cache"),
        data: local.join(APP).join("data"),
        bin: roaming.join(APP).join("bin"),
    }
}

#[cfg(windows)]
fn win_base(
    lookup: &impl Fn(&str) -> Option<OsString>,
    var: &str,
    default_rel: &[&str],
) -> PathBuf {
    if let Some(val) = lookup(var) {
        let p = PathBuf::from(&val);
        if p.is_absolute() {
            return p;
        }
    }
    let mut base = lookup("USERPROFILE")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    for seg in default_rel {
        base.push(seg);
    }
    base
}

#[cfg(all(test, not(windows)))]
mod tests {
    use super::*;
    use std::collections::HashMap;

    /// Build a lookup closure from a fixed map — the pure-test seam.
    fn env(pairs: &[(&str, &str)]) -> impl Fn(&str) -> Option<OsString> {
        let map: HashMap<String, OsString> = pairs
            .iter()
            .map(|(k, v)| (k.to_string(), OsString::from(v)))
            .collect();
        move |k: &str| map.get(k).cloned()
    }

    #[test]
    fn defaults_from_home() {
        let d = resolve(env(&[("HOME", "/home/alice")]));
        assert_eq!(d.config_dir(), Path::new("/home/alice/.config/yf"));
        assert_eq!(d.cache_dir(), Path::new("/home/alice/.cache/yf"));
        assert_eq!(d.data_dir(), Path::new("/home/alice/.local/share/yf"));
        assert_eq!(d.bin_dir(), Path::new("/home/alice/.local/bin"));
    }

    #[test]
    fn macos_uses_xdg_not_library() {
        // Decision 3: on macOS we deliberately use the XDG layout, never
        // ~/Library/Application Support. Resolution is platform-uniform on unix.
        let d = resolve(env(&[("HOME", "/Users/alice")]));
        assert_eq!(d.config_dir(), Path::new("/Users/alice/.config/yf"));
        assert!(!d.config_dir().starts_with("/Users/alice/Library"));
    }

    #[test]
    fn xdg_overrides_are_honored() {
        let d = resolve(env(&[
            ("HOME", "/home/bob"),
            ("XDG_CONFIG_HOME", "/cfg"),
            ("XDG_CACHE_HOME", "/cache"),
            ("XDG_DATA_HOME", "/data"),
            ("XDG_BIN_HOME", "/bin"),
        ]));
        assert_eq!(d.config_dir(), Path::new("/cfg/yf"));
        assert_eq!(d.cache_dir(), Path::new("/cache/yf"));
        assert_eq!(d.data_dir(), Path::new("/data/yf"));
        // bin has no `yf/` leaf — the binary file is named `yf`.
        assert_eq!(d.bin_dir(), Path::new("/bin"));
    }

    #[test]
    fn partial_xdg_override_only_affects_named_dir() {
        let d = resolve(env(&[("HOME", "/home/carol"), ("XDG_CACHE_HOME", "/fast/cache")]));
        assert_eq!(d.cache_dir(), Path::new("/fast/cache/yf"));
        // The others still derive from HOME.
        assert_eq!(d.config_dir(), Path::new("/home/carol/.config/yf"));
        assert_eq!(d.data_dir(), Path::new("/home/carol/.local/share/yf"));
    }

    #[test]
    fn relative_xdg_value_is_ignored() {
        // XDG Base Dir spec: a non-absolute $XDG_* value must be ignored, falling
        // back to the $HOME default.
        let d = resolve(env(&[("HOME", "/home/dave"), ("XDG_CONFIG_HOME", "relative/cfg")]));
        assert_eq!(d.config_dir(), Path::new("/home/dave/.config/yf"));
    }

    #[test]
    fn empty_xdg_value_is_ignored() {
        // An empty value is not absolute → ignored → HOME default.
        let d = resolve(env(&[("HOME", "/home/erin"), ("XDG_DATA_HOME", "")]));
        assert_eq!(d.data_dir(), Path::new("/home/erin/.local/share/yf"));
    }

    #[test]
    fn empty_home_falls_back_to_cwd_total_resolution() {
        // Resolution is total: an empty HOME never panics — it falls back to the
        // current dir (mirrors dest.rs). We can't assert the exact cwd, but the
        // relative leaf must still be appended.
        let d = resolve(env(&[("HOME", "")]));
        assert!(d.config_dir().ends_with(".config/yf"));
        assert!(d.bin_dir().ends_with(".local/bin"));
    }

    #[test]
    fn from_env_does_not_panic() {
        // Smoke: the real-env entry point resolves to absolute-ish paths.
        let _ = Dirs::from_env();
    }
}

// ## Home-vs-project `~/.yf` distinction (Issue 2.2)
//
// The dirs above are **home-scoped** (per-user, `$HOME`-anchored XDG paths for
// `yf`'s own config/cache/data + the `~/.local/bin` install target). They are
// distinct from **project state**, which is **git-root-anchored** and resolved by
// `dest.rs` (`git_root_or_cwd` / `Scope::Project`): per-repo skill installs land in
// `<git-root>/.claude/{skills,rules}` etc., and per-repo config like
// `.yf-plan.local.json` sits at the repo root. plan-018 decision 3 deliberately
// **dropped** a self-contained `~/.yf` home: `yf` does NOT keep a single `~/.yf`
// tree. There is therefore no `~/.yf` directory to confuse with project state —
// home state is the XDG split here; project state stays at the git root. The one
// home path that anchors future on-disk content is `data_dir()` →
// `~/.local/share/yf` (the deferred materialization seam, decision 7).
