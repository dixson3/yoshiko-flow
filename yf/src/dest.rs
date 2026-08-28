//! Destination resolution for `yf skills install/upgrade/status` (REQ-YF-INSTALL-002).
//!
//! Mirrors the retired `install.py` `resolve_dests` + `_git_root_or_cwd`:
//!
//! - `--target` wins: it **is** the skills dir; the rules dir is its **sibling**
//!   `<target>/../rules` (i.e. `target.parent()/rules`), matching install.py's
//!   `skills_dest.parent / "rules"`.
//! - otherwise the skills destination is `<anchor>/<harness.skills_subpath>`, drawn from the
//!   [`crate::harness_desc`] descriptor table's **skills** column (`user_skills_subpath` for
//!   scope=user, `project_skills_subpath` for scope=project); an unknown harness id falls back
//!   to the legacy `.<id>/skills`. `anchor` is `$HOME` for scope=user and the git-root (cwd
//!   fallback) for scope=project.
//! - the companion rules dir is `<anchor>/<harness.surface_dir>/rules`, drawn from the
//!   descriptor's **surface** column.
//!
//! ## Why the rules dir is NO LONGER the skills dir's parent (plan-055, REQ-YF-INSTALL-002)
//!
//! It used to be `skills_dir.parent()/rules`. That was **incidentally** correct only while
//! every harness had a private skills root. Once `codex`, `opencode`, `pi` and `agents` share
//! `.agents/skills`, the parent-derivation would send all four harnesses' rules to
//! `.agents/rules` — collapsing four surfaces onto one and sending pi's rules somewhere pi
//! does not read. Dedupe-by-resolved-path is a property of the **skills** column alone.
//!
//! The pure path-join logic is factored into [`skills_dir_for_anchor`] /
//! [`rules_dir_for_anchor`] so it can be unit-tested without depending on the
//! real `$HOME` or a git checkout.

// Public destination-resolution API consumed by the install / upgrade / status
// commands.
#![allow(dead_code)]

use std::path::{Path, PathBuf};
use std::process::Command;

use crate::cli::Scope;
use crate::harness_desc;

/// Resolve the skills destination directory (REQ-YF-INSTALL-002).
///
/// `--target` (when `Some`) wins and is returned verbatim as the skills dir.
/// Otherwise the destination is `<anchor>/<harness.subpath>` from the descriptor
/// table (REQ-YF-INSTALL-007), with a legacy `.<id>/skills` fallback.
pub fn resolve_skills_dir(scope: Scope, harness: &str, target: Option<&Path>) -> PathBuf {
    if let Some(t) = target {
        return t.to_path_buf();
    }
    // Issue 3.2: honour a declared skills-root override (claude-code alone, post-collapse).
    // Project scope is deliberately NOT overridden — the anchor there is the git root, and a
    // user-level config-dir var says nothing about where a repository lives.
    if scope == Scope::User {
        return skills_dir_for_anchor_env(&anchor_for(scope), harness, scope, |k| {
            std::env::var_os(k)
        });
    }
    skills_dir_for_anchor(&anchor_for(scope), harness, scope)
}

/// Resolve the companion-rules destination directory (REQ-YF-INSTALL-002).
///
/// With `--target`, the rules dir is the **sibling** of the target skills dir
/// (`<target>/../rules`), matching install.py. Otherwise it is the sibling
/// `rules/` of the resolved skills dir.
pub fn resolve_rules_dir(scope: Scope, harness: &str, target: Option<&Path>) -> PathBuf {
    if let Some(t) = target {
        return rules_sibling_of_target(t);
    }
    rules_dir_for_anchor(&anchor_for(scope), harness, scope)
}

/// `<anchor>/<harness.skills_subpath>` — pure path join (testable without env).
///
/// Deliberately env-free: [`skills_dir_for_anchor_env`] is the env-aware wrapper, so the pure
/// join stays unit-testable without a sandboxed process environment.
pub fn skills_dir_for_anchor(anchor: &Path, harness: &str, scope: Scope) -> PathBuf {
    anchor.join(harness_desc::skills_subpath(harness, scope))
}

/// Skills-root resolution that **follows a declared skills-root env override** (Issue 3.2,
/// `REQ-YF-INSTALL-007`).
///
/// ## Exactly one harness is affected, and that is a MEASURED result
///
/// After the plan-055 collapse, `claude-code` is the **only** row with a non-empty `skills_env`.
/// `.agents/skills` was measured **env-immune** on the other three (EXP-003): `CODEX_HOME` does
/// not move codex's `~/.agents/skills`, pi's survives `PI_CODING_AGENT_DIR`, and opencode loaded
/// it under all four override combinations. So the collapse did not merely make this cheap to
/// implement — it **deleted three quarters of the problem**, and the narrow scope is the finding
/// rather than a shortcut.
///
/// ## Only `replace` precedence is honoured here, and it cannot be otherwise
///
/// An `additive` override adds a root the harness *also* reads; it does not move the one `yf`
/// writes. There is exactly one skills directory to return, so "additive" has no meaning on this
/// path — treating it as a replace would send the write somewhere the harness merely *also*
/// looks, and every one of the shipped `additive` entries is on the SURFACE column anyway.
///
/// `env(var)` is injected rather than read from the ambient process environment, matching the
/// `REQ-YF-INSTALL-009` detection convention, so tests drive it hermetically.
pub fn skills_dir_for_anchor_env(
    anchor: &Path,
    harness: &str,
    scope: Scope,
    env: impl Fn(&str) -> Option<std::ffi::OsString>,
) -> PathBuf {
    if let Some(d) = harness_desc::lookup(harness) {
        for ov in d.skills_env {
            if ov.precedence != harness_desc::OverridePrecedence::Replace {
                continue;
            }
            if let Some(v) = env(ov.var) {
                let root = PathBuf::from(v);
                if !root.as_os_str().is_empty() {
                    // The override names the harness's CONFIG ROOT, so the skills subpath is
                    // re-anchored onto it: `CLAUDE_CONFIG_DIR=/x` → `/x/skills`, not
                    // `/x/.claude/skills`. The `.claude` segment IS the config root.
                    return root.join(skills_leaf(d.skills_subpath(scope)));
                }
            }
        }
    }
    skills_dir_for_anchor(anchor, harness, scope)
}

/// The portion of a skills subpath BELOW the harness's config root — i.e. the subpath with its
/// leading surface segment(s) dropped. `.claude/skills` → `skills`.
fn skills_leaf(subpath: &str) -> PathBuf {
    let p = Path::new(subpath);
    match p.file_name() {
        Some(leaf) => PathBuf::from(leaf),
        None => PathBuf::from(subpath),
    }
}

/// `<anchor>/<harness.surface_dir>/rules` — pure path join, derived from the descriptor's
/// **surface** column and never from the skills dir's parent (see the module docs).
pub fn rules_dir_for_anchor(anchor: &Path, harness: &str, scope: Scope) -> PathBuf {
    anchor
        .join(harness_desc::surface_subpath(harness, scope))
        .join("rules")
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
        let got = resolve_skills_dir(Scope::User, "claude-code", Some(&target));
        assert_eq!(got, target);
        // Scope/harness are ignored when target is present.
        let got2 = resolve_skills_dir(Scope::Project, "agents", Some(&target));
        assert_eq!(got2, target);
    }

    // REQ-YF-INSTALL-002: with --target, rules dir is the sibling <target>/../rules.
    #[test]
    fn target_rules_is_sibling() {
        let target = PathBuf::from("/tmp/custom/skills");
        let got = resolve_rules_dir(Scope::User, "claude-code", Some(&target));
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

    // REQ-YF-INSTALL-002: descriptor subpaths map per harness/scope (pure join).
    // claude-code/agents preserve the legacy `.claude`/`.agents` layout; the
    // multi-segment harnesses (opencode, pi) resolve their descriptor subpaths.
    #[test]
    fn descriptor_subpath_mapping() {
        let anchor = Path::new("/home/jd");
        assert_eq!(
            skills_dir_for_anchor(anchor, "claude-code", Scope::User),
            PathBuf::from("/home/jd/.claude/skills")
        );
        assert_eq!(
            skills_dir_for_anchor(anchor, "agents", Scope::User),
            PathBuf::from("/home/jd/.agents/skills")
        );
        assert_eq!(
            rules_dir_for_anchor(anchor, "claude-code", Scope::User),
            PathBuf::from("/home/jd/.claude/rules")
        );
        assert_eq!(
            rules_dir_for_anchor(anchor, "agents", Scope::User),
            PathBuf::from("/home/jd/.agents/rules")
        );
        // COLLAPSED (plan-055 Issue 2.2): opencode and pi resolve their SKILLS to the shared
        // `.agents/skills` in BOTH scopes...
        for h in ["opencode", "pi", "codex", "agents"] {
            for scope in [Scope::User, Scope::Project] {
                assert_eq!(
                    skills_dir_for_anchor(anchor, h, scope),
                    PathBuf::from("/home/jd/.agents/skills"),
                    "{h} must resolve skills to the shared root ({scope:?})"
                );
            }
        }

        // ...while each keeps its OWN surface dir, which is the entire point of the split. If
        // the rules dir were still derived from the skills dir's parent, all four of these
        // would now read `/home/jd/.agents/rules`.
        assert_eq!(
            rules_dir_for_anchor(anchor, "opencode", Scope::User),
            PathBuf::from("/home/jd/.config/opencode/rules")
        );
        assert_eq!(
            rules_dir_for_anchor(anchor, "opencode", Scope::Project),
            PathBuf::from("/home/jd/.opencode/rules")
        );
        assert_eq!(
            rules_dir_for_anchor(anchor, "pi", Scope::User),
            PathBuf::from("/home/jd/.pi/agent/rules")
        );
        assert_eq!(
            rules_dir_for_anchor(anchor, "pi", Scope::Project),
            PathBuf::from("/home/jd/.pi/rules")
        );

        // Unknown harness → legacy `.<id>/skills` fallback.
        assert_eq!(
            skills_dir_for_anchor(anchor, "frobnicator", Scope::User),
            PathBuf::from("/home/jd/.frobnicator/skills")
        );
    }

    /// SC9 — env-override precedence is THREE-VALUED, and the opencode ADDITIVE case is
    /// asserted **distinctly** from the three replace cases.
    ///
    /// The distinctness is the point. A boolean model ("is the var set?") would get opencode
    /// exactly backwards: `OPENCODE_CONFIG_DIR` was measured to ADD a root while the default is
    /// retained (7 roots vs 8, EXP-003), so treating it as a replace would under-install for
    /// opencode and over-install for the other three. An assertion that merely counted overrides
    /// would pass under that wrong model.
    #[test]
    fn env_precedence_additive_and_replace() {
        use crate::harness_desc::{lookup, OverridePrecedence};

        // The three REPLACE vars, one per harness.
        for (h, var) in [
            ("claude-code", "CLAUDE_CONFIG_DIR"),
            ("codex", "CODEX_HOME"),
            ("pi", "PI_CODING_AGENT_DIR"),
        ] {
            let d = lookup(h).unwrap();
            let ov = d
                .surface_env
                .iter()
                .find(|o| o.var == var)
                .unwrap_or_else(|| panic!("{h} must declare {var}"));
            assert_eq!(
                ov.precedence,
                OverridePrecedence::Replace,
                "{var} REPLACES the default root"
            );
        }

        // opencode carries TWO vars, and they differ in precedence. Asserted as a pair, because
        // the defect a single-var assertion misses is precisely the two being conflated.
        let oc = lookup("opencode").unwrap();
        let xdg = oc.surface_env.iter().find(|o| o.var == "XDG_CONFIG_HOME").unwrap();
        let ocd = oc
            .surface_env
            .iter()
            .find(|o| o.var == "OPENCODE_CONFIG_DIR")
            .unwrap();
        assert_eq!(xdg.precedence, OverridePrecedence::Replace);
        assert_eq!(
            ocd.precedence,
            OverridePrecedence::Additive,
            "OPENCODE_CONFIG_DIR ADDS a root; the default is retained (EXP-003)"
        );
        assert_ne!(
            xdg.precedence, ocd.precedence,
            "opencode's two vars are ORTHOGONAL, not competing — a boolean model collapses them"
        );

        // XDG_CONFIG_HOME is honoured by OPENCODE ONLY. codex's occurrences are vendored gix
        // git-config code and claude-code's are git discovery / completions / an env-scrubbing
        // deny-list; pi references it nowhere.
        for h in ["claude-code", "codex", "pi", "agents"] {
            let d = lookup(h).unwrap();
            assert!(
                !d.surface_env.iter().any(|o| o.var == "XDG_CONFIG_HOME"),
                "{h} must NOT declare XDG_CONFIG_HOME"
            );
        }
    }

    /// SC10 — `CLAUDE_CONFIG_DIR` relocates claude-code's SKILLS root, and no other harness's
    /// skills root responds to any env var.
    ///
    /// The negative half is the substantive one: after the collapse, `.agents/skills` was
    /// measured env-immune on codex, pi and opencode, and this asserts yf does not reintroduce a
    /// sensitivity the harnesses do not have.
    #[test]
    fn skills_root_env_override_claude_only() {
        let anchor = Path::new("/home/jd");
        let overridden = std::ffi::OsString::from("/elsewhere/cc");
        let env = |k: &str| (k == "CLAUDE_CONFIG_DIR").then(|| overridden.clone());

        // claude-code FOLLOWS it — and re-anchors onto the override rather than re-appending
        // `.claude`, because the override names the config root itself.
        assert_eq!(
            skills_dir_for_anchor_env(anchor, "claude-code", Scope::User, env),
            PathBuf::from("/elsewhere/cc/skills")
        );

        // Nothing else does, with the SAME var set.
        for h in ["codex", "opencode", "pi", "agents"] {
            assert_eq!(
                skills_dir_for_anchor_env(anchor, h, Scope::User, env),
                PathBuf::from("/home/jd/.agents/skills"),
                "{h}'s skills root must be env-immune"
            );
        }

        // And the other harnesses' OWN vars move nothing on the skills column either.
        for (h, var) in [
            ("codex", "CODEX_HOME"),
            ("pi", "PI_CODING_AGENT_DIR"),
            ("opencode", "XDG_CONFIG_HOME"),
            ("opencode", "OPENCODE_CONFIG_DIR"),
        ] {
            let v = std::ffi::OsString::from("/elsewhere/other");
            let e = |k: &str| (k == var).then(|| v.clone());
            assert_eq!(
                skills_dir_for_anchor_env(anchor, h, Scope::User, e),
                PathBuf::from("/home/jd/.agents/skills"),
                "{var} must not move {h}'s skills root"
            );
        }

        // Unset (or empty) falls through to the default — an empty var is not an override.
        let empty = |k: &str| (k == "CLAUDE_CONFIG_DIR").then(std::ffi::OsString::new);
        assert_eq!(
            skills_dir_for_anchor_env(anchor, "claude-code", Scope::User, empty),
            PathBuf::from("/home/jd/.claude/skills")
        );
    }

    // REQ-YF-INSTALL-002: user-scope resolution joins under the HOME anchor.
    // Tested via the pure path-join helper so we never depend on the real $HOME.
    #[test]
    fn user_scope_path_layout() {
        let fake_home = Path::new("/fake/home");
        assert_eq!(
            skills_dir_for_anchor(fake_home, "claude-code", Scope::User),
            PathBuf::from("/fake/home/.claude/skills")
        );
        assert_eq!(
            rules_dir_for_anchor(fake_home, "claude-code", Scope::User),
            PathBuf::from("/fake/home/.claude/rules")
        );
    }

    // REQ-YF-INSTALL-002: project-scope resolution joins under a git-root anchor.
    #[test]
    fn project_scope_path_layout() {
        let fake_root = Path::new("/repo/root");
        assert_eq!(
            skills_dir_for_anchor(fake_root, "agents", Scope::Project),
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
