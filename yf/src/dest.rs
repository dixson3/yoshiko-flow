//! Destination resolution for `yf skills install/upgrade/status` (REQ-YF-INSTALL-002).
//!
//! Mirrors the retired `install.py` `resolve_dests` + `_git_root_or_cwd`:
//!
//! - `--target` wins: it **is** the skills dir; the rules dir is its **sibling**
//!   `<target>/../rules` (i.e. `target.parent()/rules`), matching install.py's
//!   `skills_dest.parent / "rules"`.
//! - otherwise the destination is `<anchor>/.<surface>/skills` (skills) and
//!   `<anchor>/.<surface>/rules` (rules), where `anchor` is `$HOME` for
//!   scope=user and the git-root (cwd fallback) for scope=project, and
//!   `<surface>` is `claude` or `agents`.
//!
//! The pure path-join logic is factored into [`skills_dir_for_anchor`] /
//! [`rules_dir_for_anchor`] so it can be unit-tested without depending on the
//! real `$HOME` or a git checkout.

// Public destination-resolution API consumed by the (not-yet-wired) install /
// upgrade / status commands (beads 1.5/1.6).
#![allow(dead_code)]

use std::path::{Path, PathBuf};
use std::process::Command;

use crate::cli::{Scope, Surface};

impl Surface {
    /// The dotted surface directory component, e.g. `.claude` / `.agents`.
    fn dot_dir(self) -> &'static str {
        match self {
            Surface::Claude => ".claude",
            Surface::Agents => ".agents",
        }
    }
}

/// Resolve the skills destination directory (REQ-YF-INSTALL-002).
///
/// `--target` (when `Some`) wins and is returned verbatim as the skills dir.
pub fn resolve_skills_dir(scope: Scope, surface: Surface, target: Option<&Path>) -> PathBuf {
    if let Some(t) = target {
        return t.to_path_buf();
    }
    skills_dir_for_anchor(&anchor_for(scope), surface)
}

/// Resolve the companion-rules destination directory (REQ-YF-INSTALL-002).
///
/// With `--target`, the rules dir is the **sibling** of the target skills dir
/// (`<target>/../rules`), matching install.py. Otherwise it is
/// `<anchor>/.<surface>/rules`.
pub fn resolve_rules_dir(scope: Scope, surface: Surface, target: Option<&Path>) -> PathBuf {
    if let Some(t) = target {
        return rules_sibling_of_target(t);
    }
    rules_dir_for_anchor(&anchor_for(scope), surface)
}

/// `<anchor>/.<surface>/skills` — pure path join (testable without env).
pub fn skills_dir_for_anchor(anchor: &Path, surface: Surface) -> PathBuf {
    anchor.join(surface.dot_dir()).join("skills")
}

/// `<anchor>/.<surface>/rules` — pure path join (testable without env).
pub fn rules_dir_for_anchor(anchor: &Path, surface: Surface) -> PathBuf {
    anchor.join(surface.dot_dir()).join("rules")
}

/// The sibling `rules` dir of a `--target` skills dir: `<target>/../rules`.
///
/// Equivalent to install.py's `Path(target).parent / "rules"`. A target with no
/// parent (e.g. a bare relative name) yields `rules` in the implicit cwd.
pub fn rules_sibling_of_target(target: &Path) -> PathBuf {
    match target.parent() {
        Some(parent) => parent.join("rules"),
        None => PathBuf::from("rules"),
    }
}

/// The anchor directory for a scope: `$HOME` for user, git-root (cwd fallback)
/// for project.
fn anchor_for(scope: Scope) -> PathBuf {
    match scope {
        Scope::User => home_dir(),
        Scope::Project => git_root_or_cwd(),
    }
}

/// `$HOME` (env), falling back to cwd if unset — keeps resolution total.
fn home_dir() -> PathBuf {
    std::env::var_os("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
}

/// The git repository root, walking up for a `.git` entry, falling back to the
/// current working directory.
///
/// Prefers `git rev-parse --show-toplevel` (matches install.py); if `git` is
/// absent or fails, walks ancestors for a `.git` dir/file; finally returns cwd.
pub fn git_root_or_cwd() -> PathBuf {
    if let Some(root) = git_root_via_cli() {
        return root;
    }
    let cwd = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
    git_root_walk_up(&cwd).unwrap_or(cwd)
}

fn git_root_via_cli() -> Option<PathBuf> {
    let out = Command::new("git")
        .args(["rev-parse", "--show-toplevel"])
        .output()
        .ok()?;
    if !out.status.success() {
        return None;
    }
    let path = String::from_utf8(out.stdout).ok()?;
    let trimmed = path.trim();
    if trimmed.is_empty() {
        return None;
    }
    Some(PathBuf::from(trimmed))
}

/// Walk `start` and its ancestors looking for a `.git` entry (dir or file, the
/// latter covering worktrees/submodules). Returns the first directory that
/// contains one.
pub fn git_root_walk_up(start: &Path) -> Option<PathBuf> {
    let mut cur: Option<&Path> = Some(start);
    while let Some(dir) = cur {
        if dir.join(".git").exists() {
            return Some(dir.to_path_buf());
        }
        cur = dir.parent();
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    // REQ-YF-INSTALL-002: --target wins; skills dir is the target verbatim.
    #[test]
    fn target_wins_for_skills_dir() {
        let target = PathBuf::from("/tmp/custom/skills");
        let got = resolve_skills_dir(Scope::User, Surface::Claude, Some(&target));
        assert_eq!(got, target);
        // Scope/surface are ignored when target is present.
        let got2 = resolve_skills_dir(Scope::Project, Surface::Agents, Some(&target));
        assert_eq!(got2, target);
    }

    // REQ-YF-INSTALL-002: with --target, rules dir is the sibling <target>/../rules.
    #[test]
    fn target_rules_is_sibling() {
        let target = PathBuf::from("/tmp/custom/skills");
        let got = resolve_rules_dir(Scope::User, Surface::Claude, Some(&target));
        assert_eq!(got, PathBuf::from("/tmp/custom/rules"));
    }

    // REQ-YF-INSTALL-002: a target whose parent differs still sibling-joins rules.
    #[test]
    fn target_rules_sibling_uses_parent() {
        let target = PathBuf::from("/a/b/c/myskills");
        assert_eq!(
            rules_sibling_of_target(&target),
            PathBuf::from("/a/b/c/rules")
        );
    }

    // REQ-YF-INSTALL-002: bare target with no parent → "rules" relative.
    #[test]
    fn target_rules_sibling_no_parent() {
        let target = PathBuf::from("skills");
        // Path::parent() of "skills" is Some(""), so join gives "rules".
        let got = rules_sibling_of_target(&target);
        assert_eq!(got, PathBuf::from("rules"));
    }

    // REQ-YF-INSTALL-002: surface maps to .claude / .agents (pure join).
    #[test]
    fn surface_dot_dir_mapping() {
        let anchor = Path::new("/home/jd");
        assert_eq!(
            skills_dir_for_anchor(anchor, Surface::Claude),
            PathBuf::from("/home/jd/.claude/skills")
        );
        assert_eq!(
            skills_dir_for_anchor(anchor, Surface::Agents),
            PathBuf::from("/home/jd/.agents/skills")
        );
        assert_eq!(
            rules_dir_for_anchor(anchor, Surface::Claude),
            PathBuf::from("/home/jd/.claude/rules")
        );
        assert_eq!(
            rules_dir_for_anchor(anchor, Surface::Agents),
            PathBuf::from("/home/jd/.agents/rules")
        );
    }

    // REQ-YF-INSTALL-002: user-scope resolution joins under the HOME anchor.
    // Tested via the pure path-join helper so we never depend on the real $HOME.
    #[test]
    fn user_scope_path_layout() {
        let fake_home = Path::new("/fake/home");
        assert_eq!(
            skills_dir_for_anchor(fake_home, Surface::Claude),
            PathBuf::from("/fake/home/.claude/skills")
        );
        assert_eq!(
            rules_dir_for_anchor(fake_home, Surface::Claude),
            PathBuf::from("/fake/home/.claude/rules")
        );
    }

    // REQ-YF-INSTALL-002: project-scope resolution joins under a git-root anchor.
    #[test]
    fn project_scope_path_layout() {
        let fake_root = Path::new("/repo/root");
        assert_eq!(
            skills_dir_for_anchor(fake_root, Surface::Agents),
            PathBuf::from("/repo/root/.agents/skills")
        );
    }

    // REQ-YF-INSTALL-002: git-root walk-up finds the dir containing .git.
    #[test]
    fn git_root_walk_up_finds_marker() {
        let tmp = std::env::temp_dir().join(format!("yf-dest-test-{}", std::process::id()));
        let nested = tmp.join("a").join("b");
        std::fs::create_dir_all(&nested).unwrap();
        std::fs::create_dir_all(tmp.join(".git")).unwrap();

        let found = git_root_walk_up(&nested);
        assert_eq!(found.as_deref(), Some(tmp.as_path()));

        std::fs::remove_dir_all(&tmp).ok();
    }

    // REQ-YF-INSTALL-002: walk-up returns None when no .git ancestor exists.
    #[test]
    fn git_root_walk_up_none_without_marker() {
        let tmp = std::env::temp_dir().join(format!("yf-dest-nogit-{}", std::process::id()));
        let nested = tmp.join("x").join("y");
        std::fs::create_dir_all(&nested).unwrap();

        // No .git anywhere under tmp; walk stops at filesystem root without a hit
        // *within our tree* — but ancestors above tmp could theoretically have a
        // .git. Restrict the assertion to the portion we control by checking the
        // result is not inside our tmp tree.
        let found = git_root_walk_up(&nested);
        if let Some(p) = found {
            assert!(
                !p.starts_with(&tmp),
                "unexpected .git found inside test tree: {p:?}"
            );
        }

        std::fs::remove_dir_all(&tmp).ok();
    }
}
