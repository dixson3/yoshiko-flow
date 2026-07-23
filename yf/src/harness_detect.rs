//! Harness auto-detection (REQ-YF-INSTALL-009).
//!
//! When a `skills` invocation gives **no** `--harness`, `yf` detects which
//! harnesses are installed and acts on all detected; an explicit `--harness`
//! (or the deprecated `--surface`) overrides detection entirely. Epic 7's
//! `--tune` bridge reuses this module, so the detection primitives are a clean,
//! callable API rather than inline install logic.
//!
//! ## Injected anchors (hermetic tests)
//!
//! Detection reads **no ambient process env** in its core functions: the home
//! anchor, the project root, and `PATH` are all **injected parameters**
//! ([`detect`] / [`detect_user_scope`] / [`detect_project_scope`]). That lets a
//! Tier-2 test drive both the home-dir probe (a sandboxed `HOME`) and the binary
//! probe (an injected `PATH`) with zero host dependency. [`detect_from_env`] is
//! the thin production wrapper that supplies the real `$HOME`, the git-root, and
//! the live `PATH` (`None` → [`crate::tool::resolve_tool_in`] reads the process
//! `PATH`).
//!
//! ## What is probed
//!
//! - **User scope**: for each harness, its home dir under the anchor **or** its
//!   binary on the injected `PATH` — either hit means "detected". Note the
//!   home-dir probe paths (`~/.codex`, `~/.config/opencode`, …) are the harness's
//!   **own** config dirs and deliberately differ from the skills *install*
//!   subpaths in [`crate::harness_desc`] (`.agents/skills`, …).
//! - **Project scope**: dot-dir presence in the git root. codex and the `agents`
//!   alias both install under `.agents`, so a single `.agents` dir detects that
//!   destination **once** — emitted as the canonical `codex` id (whose descriptor
//!   resolves to the same `.agents/skills` an `agents` selection would).

use std::collections::BTreeSet;
use std::ffi::OsStr;
use std::path::{Path, PathBuf};

use crate::cli::Scope;

/// One harness's detection probes. Distinct from [`crate::harness_desc`]: that
/// table drives skills *install destinations*; this one drives *presence
/// detection* off the harness's own config dir + binary name.
struct HarnessProbe {
    /// The `--harness` id emitted when this harness is detected.
    id: &'static str,
    /// User-scope home dir (relative to the `$HOME` anchor) whose presence signals
    /// the harness is configured for this user.
    user_home_subdir: &'static str,
    /// The harness's binary name on `PATH`.
    bin: &'static str,
    /// Project-scope dot-dir (relative to the git root) whose presence signals the
    /// harness's project destination exists.
    project_dotdir: &'static str,
}

/// The detection probe table — the four real harnesses (`agents` is not a
/// separately-probed row: it shares `codex`'s `.agents` destination, so a
/// `.agents` dir is detected once as `codex`).
const PROBES: &[HarnessProbe] = &[
    HarnessProbe {
        id: "claude-code",
        user_home_subdir: ".claude",
        bin: "claude",
        project_dotdir: ".claude",
    },
    HarnessProbe {
        id: "codex",
        user_home_subdir: ".codex",
        bin: "codex",
        project_dotdir: ".agents",
    },
    HarnessProbe {
        id: "opencode",
        user_home_subdir: ".config/opencode",
        bin: "opencode",
        project_dotdir: ".opencode",
    },
    HarnessProbe {
        id: "pi",
        user_home_subdir: ".pi",
        bin: "pi",
        project_dotdir: ".pi",
    },
];

/// Detect installed harnesses for `scope`, with every anchor injected
/// (REQ-YF-INSTALL-009). `home` is the user anchor, `root` the project (git-root)
/// anchor, `path` the injected `PATH` (`None` → the live process `PATH`). Order
/// follows the probe table (first-appearance).
pub fn detect(scope: Scope, home: &Path, root: &Path, path: Option<&OsStr>) -> Vec<String> {
    match scope {
        Scope::User => detect_user_scope(home, path),
        Scope::Project => detect_project_scope(root),
    }
}

/// User-scope detection: a harness is detected when **either** its home dir under
/// `home` exists **or** its binary resolves on the injected `path`
/// (REQ-YF-INSTALL-009). Both probes are checked so a `PATH`-only install with no
/// home dir (and vice-versa) is still found.
pub fn detect_user_scope(home: &Path, path: Option<&OsStr>) -> Vec<String> {
    PROBES
        .iter()
        .filter(|p| {
            home.join(p.user_home_subdir).is_dir()
                || crate::tool::resolve_tool_in(path, p.bin).is_some()
        })
        .map(|p| p.id.to_string())
        .collect()
}

/// Project-scope detection: a harness is detected by the presence of its dot-dir
/// under the git root `root` (REQ-YF-INSTALL-009). Dot-dirs are deduped, so the
/// shared `.agents` dir (codex + the `agents` alias) yields a single detection.
pub fn detect_project_scope(root: &Path) -> Vec<String> {
    let mut seen: BTreeSet<&str> = BTreeSet::new();
    let mut out: Vec<String> = Vec::new();
    for p in PROBES {
        if root.join(p.project_dotdir).is_dir() && seen.insert(p.project_dotdir) {
            out.push(p.id.to_string());
        }
    }
    out
}

/// Production wrapper: detect against the **real** environment — `$HOME` for the
/// user anchor, the git-root (cwd fallback) for the project anchor, and the live
/// process `PATH` for the binary probe. The core [`detect`] stays env-free for
/// hermetic tests; this is the only detection entry point that reads ambient env.
pub fn detect_from_env(scope: Scope) -> Vec<String> {
    let home = home_dir();
    let root = crate::dest::git_root_or_cwd();
    detect(scope, &home, &root, None)
}

/// `$HOME` (env), falling back to cwd when unset — keeps resolution total
/// (mirrors `dest.rs::home_dir`).
fn home_dir() -> PathBuf {
    std::env::var_os("HOME")
        .map(PathBuf::from)
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::OsString;

    /// Create an executable file named `bin` in `dir` (a fake harness binary).
    fn write_bin(dir: &Path, bin: &str) {
        let p = dir.join(bin);
        std::fs::write(&p, b"#!/bin/sh\n").unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            std::fs::set_permissions(&p, std::fs::Permissions::from_mode(0o755)).unwrap();
        }
    }

    // REQ-YF-INSTALL-009: under a sandboxed HOME and an INJECTED PATH, user-scope
    // detection fires on BOTH the home-dir hit and the PATH-binary hit, and an
    // absent harness is not detected. Fully hermetic: no probe reads the real
    // process env, so the host's installed harnesses cannot leak into the result.
    #[test]
    fn user_scope_detects_home_dir_and_path_binary_hermetically() {
        let sandbox = tempfile::tempdir().unwrap();
        let home = sandbox.path().join("home");
        let bindir = sandbox.path().join("bin");
        std::fs::create_dir_all(&home).unwrap();
        std::fs::create_dir_all(&bindir).unwrap();

        // Home-dir hit: seed ~/.codex (its own config dir), no codex binary.
        std::fs::create_dir_all(home.join(".codex")).unwrap();
        // PATH-binary hit: a `claude` binary on the injected PATH, no ~/.claude dir.
        write_bin(&bindir, "claude");

        let path = OsString::from(&bindir);
        let detected = detect_user_scope(&home, Some(path.as_os_str()));

        // codex via the home-dir probe; claude-code via the PATH-binary probe.
        assert!(
            detected.contains(&"codex".to_string()),
            "seeded ~/.codex must be detected (home-dir probe): {detected:?}"
        );
        assert!(
            detected.contains(&"claude-code".to_string()),
            "a claude binary on the injected PATH must be detected (binary probe): {detected:?}"
        );
        // Absent harnesses (no ~/.pi, no ~/.config/opencode, no pi/opencode binary)
        // are NOT detected.
        assert!(
            !detected.contains(&"pi".to_string()),
            "absent pi must not be detected: {detected:?}"
        );
        assert!(
            !detected.contains(&"opencode".to_string()),
            "absent opencode must not be detected: {detected:?}"
        );
    }

    // REQ-YF-INSTALL-009: an EMPTY injected PATH plus an empty sandboxed HOME
    // detects nothing — proving the binary probe honors the injected PATH and does
    // not fall through to the live process PATH.
    #[test]
    fn empty_home_and_empty_path_detects_nothing() {
        let sandbox = tempfile::tempdir().unwrap();
        let home = sandbox.path().join("empty-home");
        std::fs::create_dir_all(&home).unwrap();
        let empty = OsString::new();
        let detected = detect_user_scope(&home, Some(empty.as_os_str()));
        assert!(
            detected.is_empty(),
            "empty HOME + empty PATH must detect nothing: {detected:?}"
        );
    }

    // REQ-YF-INSTALL-009: project-scope detection keys on dot-dir presence under
    // the injected git root; the shared `.agents` dir (codex + the agents alias) is
    // detected ONCE as the canonical `codex` id.
    #[test]
    fn project_scope_detects_dotdirs_and_dedupes_agents() {
        let root = tempfile::tempdir().unwrap();
        std::fs::create_dir_all(root.path().join(".claude")).unwrap();
        std::fs::create_dir_all(root.path().join(".agents")).unwrap();
        // No `.opencode` / `.pi`.

        let detected = detect_project_scope(root.path());
        assert!(
            detected.contains(&"claude-code".to_string()),
            ".claude dir → claude-code: {detected:?}"
        );
        assert!(
            detected.contains(&"codex".to_string()),
            ".agents dir → codex (agents/codex shared destination): {detected:?}"
        );
        // `.agents` maps to exactly one detection, not two.
        assert_eq!(
            detected.iter().filter(|id| *id == "codex").count(),
            1,
            "shared .agents dir detects once: {detected:?}"
        );
        assert!(!detected.contains(&"opencode".to_string()));
        assert!(!detected.contains(&"pi".to_string()));
    }

    // REQ-YF-INSTALL-009: the scope-dispatching `detect` routes to the user probe
    // (home + PATH) for Scope::User and the dot-dir probe for Scope::Project.
    #[test]
    fn detect_dispatches_by_scope() {
        let sandbox = tempfile::tempdir().unwrap();
        let home = sandbox.path().join("home");
        let root = sandbox.path().join("root");
        std::fs::create_dir_all(home.join(".pi")).unwrap();
        std::fs::create_dir_all(root.join(".opencode")).unwrap();
        let empty = OsString::new();

        let user = detect(Scope::User, &home, &root, Some(empty.as_os_str()));
        assert_eq!(user, vec!["pi".to_string()], "user scope reads HOME probe");

        let project = detect(Scope::Project, &home, &root, Some(empty.as_os_str()));
        assert_eq!(
            project,
            vec!["opencode".to_string()],
            "project scope reads the git-root dot-dir probe"
        );
    }
}
