//! Shared external-tool resolution: the single `which`-style PATH lookup and
//! version parser used by `preflight`, `beads_init`, and the `doctor`/`skills`
//! commands.
//!
//! Before this module the codebase carried **three** duplicate `which` impls
//! (`preflight::which_in`, `beads_init::which`, `cmd::common::tool_on_path`) and
//! **two** version parsers. They are consolidated here (GR-011: std only, no
//! extra dep). Resolution semantics are preserved 1:1: a tool resolves when a
//! `PATH` entry holds an executable regular file of that name (symlinks followed
//! by `std::fs::metadata`; on non-unix, any file counts).

use std::path::{Path, PathBuf};
use std::process::Command;

/// `which`-style lookup against an explicit PATH (`path_override`), or the live
/// process PATH when `None`. The `Some` arm is the test-only seam used by
/// preflight's `Env::path_override`; the `None` arm is the plain `which`.
///
/// Returns the first `PATH` entry that holds an executable file named `bin`.
pub fn resolve_tool_in(path_override: Option<&std::ffi::OsStr>, bin: &str) -> Option<PathBuf> {
    let path = match path_override {
        Some(p) => p.to_os_string(),
        None => std::env::var_os("PATH")?,
    };
    for dir in std::env::split_paths(&path) {
        let candidate = dir.join(bin);
        if is_executable(&candidate) {
            return Some(candidate);
        }
    }
    None
}

/// `which`-style lookup against the live process PATH. Convenience wrapper over
/// [`resolve_tool_in`] for callers with no PATH-override seam.
pub fn resolve_tool(bin: &str) -> Option<PathBuf> {
    resolve_tool_in(None, bin)
}

/// Whether `bin` resolves to an executable on the current `PATH`.
pub fn tool_on_path(bin: &str) -> bool {
    resolve_tool(bin).is_some()
}

/// Whether `path` is an executable regular file (symlinks followed).
#[cfg(unix)]
pub fn is_executable(path: &Path) -> bool {
    use std::os::unix::fs::PermissionsExt;
    std::fs::metadata(path)
        .map(|m| m.is_file() && (m.permissions().mode() & 0o111 != 0))
        .unwrap_or(false)
}

/// Whether `path` is a regular file (no exec-bit concept on non-unix).
#[cfg(not(unix))]
pub fn is_executable(path: &Path) -> bool {
    path.is_file()
}

/// Find the first `\d+.\d+(.\d+)?` in `text` and return it as a 3-tuple (patch
/// defaults to 0). The canonical, most-robust version parser — handles `M.N`,
/// pre-release suffixes (`1.0.5-rc1`), and embedded version strings.
pub fn extract_version_tuple(text: &str) -> Option<(u32, u32, u32)> {
    let bytes = text.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i].is_ascii_digit() {
            // Read up to three dot-separated number groups.
            let mut nums: Vec<u32> = Vec::new();
            let mut j = i;
            loop {
                let start = j;
                while j < bytes.len() && bytes[j].is_ascii_digit() {
                    j += 1;
                }
                if start == j {
                    break;
                }
                let n: u32 = text[start..j].parse().ok()?;
                nums.push(n);
                if nums.len() == 3 {
                    break;
                }
                // Continue only if a '.' immediately follows another digit group.
                if j < bytes.len()
                    && bytes[j] == b'.'
                    && j + 1 < bytes.len()
                    && bytes[j + 1].is_ascii_digit()
                {
                    j += 1;
                } else {
                    break;
                }
            }
            if nums.len() >= 2 {
                let major = nums[0];
                let minor = nums[1];
                let patch = nums.get(2).copied().unwrap_or(0);
                return Some((major, minor, patch));
            }
        }
        i += 1;
    }
    None
}

/// Resolve `bin` on PATH and parse its version by running `bin <version_arg>`
/// and scanning stdout with [`extract_version_tuple`]. Returns `None` when `bin`
/// is absent, the command fails, or no version triple is found.
///
/// `path_override` is the same test seam as [`resolve_tool_in`]: when `Some` and
/// `bin` is not on that PATH, the tool is treated as absent without spawning the
/// host's real binary.
pub fn tool_version(
    path_override: Option<&std::ffi::OsStr>,
    bin: &str,
    version_arg: &str,
) -> Option<(u32, u32, u32)> {
    resolve_tool_in(path_override, bin)?;
    let out = Command::new(bin).arg(version_arg).output().ok()?;
    if !out.status.success() {
        return None;
    }
    let text = String::from_utf8_lossy(&out.stdout);
    extract_version_tuple(&text)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::OsString;

    #[test]
    fn extract_version_tuple_variants() {
        assert_eq!(extract_version_tuple("bd version 1.0.5"), Some((1, 0, 5)));
        assert_eq!(extract_version_tuple("1.2.10\n"), Some((1, 2, 10)));
        assert_eq!(extract_version_tuple("v1.2"), Some((1, 2, 0)));
        assert_eq!(extract_version_tuple("1.0.5-rc1"), Some((1, 0, 5)));
        assert_eq!(extract_version_tuple("beads v1.0.5 (abc)"), Some((1, 0, 5)));
        assert_eq!(extract_version_tuple("no version here"), None);
    }

    #[test]
    fn resolve_tool_in_honors_path_override() {
        // An empty PATH override resolves nothing.
        let empty = OsString::new();
        assert!(resolve_tool_in(Some(empty.as_os_str()), "definitely-not-a-real-bin").is_none());

        // A dir containing an executable file resolves it.
        let tmp = tempfile::tempdir().unwrap();
        let bin = tmp.path().join("mybin");
        std::fs::write(&bin, b"#!/bin/sh\n").unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            std::fs::set_permissions(&bin, std::fs::Permissions::from_mode(0o755)).unwrap();
        }
        let path = OsString::from(tmp.path());
        assert_eq!(
            resolve_tool_in(Some(path.as_os_str()), "mybin"),
            Some(bin),
            "executable in override PATH must resolve"
        );
        // A non-existent name in the same dir does not resolve.
        assert!(resolve_tool_in(Some(path.as_os_str()), "nope").is_none());
    }

    #[test]
    fn tool_version_absent_with_override_is_none() {
        let empty = OsString::new();
        assert_eq!(
            tool_version(Some(empty.as_os_str()), "bd", "version"),
            None,
            "absent tool under override must be None without spawning host bd"
        );
    }
}
