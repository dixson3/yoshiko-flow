//! Embedded `skills/` tree and its enumeration API (REQ-YF-EMBED-001/002).
//!
//! The repo's `skills/` directory is compiled into the binary at build time via
//! [`rust_embed`], so installation needs no network access or repo clone.
//!
//! ## Path scheme
//!
//! `rust-embed` strips the `folder = "../skills"` prefix, so every embedded path
//! is **relative to `skills/`** — e.g. `yf-beads-extra/SKILL.md`,
//! `yf-beads-extra/spec/cli.md`. A "skill" is a top-level directory under
//! `skills/`; the first path segment of any embedded relpath is its skill name.
//! Top-level files (e.g. `SPEC-TEMPLATE.md`) have no `/` and are not skills.
//!
//! - [`skill_names`] — distinct top-level skill directory names.
//! - [`skill_files`] — file relpaths **relative to a skill's own dir** (the
//!   `<skill>/` prefix stripped), directly usable for per-skill tree hashing.
//! - [`read_file`] — read any embedded file by its `skills/`-relative path.

// `all_relpaths`, `skill_files`, and `read_file` are the embed enumeration API
// (REQ-YF-EMBED-002) consumed by later beads (tree-hash / install); only
// `skill_names` is wired into a command so far, so silence dead-code here.
#![allow(dead_code)]

use std::borrow::Cow;
use std::collections::BTreeSet;

use rust_embed::RustEmbed;

/// The embedded `skills/` tree. Paths are relative to `skills/` (see module docs).
#[derive(RustEmbed)]
#[folder = "../skills"]
#[exclude = "*.pyc"]
#[exclude = "__pycache__/*"]
#[exclude = "**/__pycache__/*"]
struct Skills;

/// Every embedded file path, relative to the `skills/` root.
pub fn all_relpaths() -> Vec<String> {
    Skills::iter().map(|p| p.into_owned()).collect()
}

/// Distinct top-level skill directory names under the embedded `skills/` tree.
///
/// Derived from embedded paths; top-level files (no `/`, e.g. `SPEC-TEMPLATE.md`)
/// are excluded since they are not skill directories.
pub fn skill_names() -> Vec<String> {
    let mut names: BTreeSet<String> = BTreeSet::new();
    for path in Skills::iter() {
        if let Some((head, _rest)) = path.split_once('/') {
            names.insert(head.to_string());
        }
    }
    names.into_iter().collect()
}

/// File relpaths under `skill`, relative to that skill's own directory
/// (the leading `<skill>/` is stripped). Empty if the skill is unknown.
pub fn skill_files(skill: &str) -> Vec<String> {
    let prefix = format!("{skill}/");
    let mut files: Vec<String> = Skills::iter()
        .filter_map(|p| p.strip_prefix(&prefix).map(str::to_string))
        .collect();
    files.sort();
    files
}

/// Read an embedded file by its `skills/`-relative path (e.g.
/// `yf-beads-extra/SKILL.md`). `None` if no such file is embedded.
pub fn read_file(relpath: &str) -> Option<Cow<'static, [u8]>> {
    Skills::get(relpath).map(|f| f.data)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn skill_names_nonempty_and_known() {
        let names = skill_names();
        assert!(!names.is_empty(), "expected embedded skills, found none");
        assert!(
            names.iter().any(|n| n == "yf-beads-extra"),
            "skill_names() missing yf-beads-extra: {names:?}"
        );
    }

    #[test]
    fn top_level_files_are_not_skills() {
        // SPEC-TEMPLATE.md is a top-level file under skills/, not a skill dir.
        assert!(!skill_names().iter().any(|n| n == "SPEC-TEMPLATE.md"));
    }

    #[test]
    fn skill_files_relative_to_skill_dir() {
        let files = skill_files("yf-beads-extra");
        assert!(
            files.iter().any(|f| f == "SKILL.md"),
            "skill_files(yf-beads-extra) missing SKILL.md: {files:?}"
        );
        // Paths are stripped of the `<skill>/` prefix.
        assert!(!files.iter().any(|f| f.starts_with("yf-beads-extra/")));
    }

    #[test]
    fn read_embedded_file() {
        let data = read_file("yf-beads-extra/SKILL.md").expect("SKILL.md must be embedded");
        let text = String::from_utf8_lossy(&data);
        assert!(
            text.contains("name: yf-beads-extra"),
            "embedded SKILL.md missing expected front matter"
        );
    }

    #[test]
    fn read_missing_file_is_none() {
        assert!(read_file("does-not-exist/nope.md").is_none());
    }
}
