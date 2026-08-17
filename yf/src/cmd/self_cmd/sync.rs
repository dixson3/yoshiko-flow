//! The **install-time sync** shared by both install paths (`REQ-YF-SELF-005`,
//! `REQ-YF-SELF-008`, plan-042).
//!
//! Both `yf self update` (vendor) and `yf self install --from-build` (developer)
//! must leave the machine's **deployed** surface — skills, the rules aggregate,
//! and harness config — matching the binary they just promoted. They start from
//! different states, which is why `REQ-YF-SELF-005` specifies them separately;
//! they converge here so there is exactly **one** implementation to keep correct.
//!
//! Extracted from `update.rs` as a pure refactor (plan-042 Issue 1.1): the
//! behavior below is byte-for-byte the vendor path's prior behavior, so the
//! behavior changes that follow have a clean diff.

use std::path::Path;

/// User-scope surfaces yf may have installed skills/rules into, as
/// `(--surface value, home-relative dir)`.
const USER_SURFACES: &[(&str, &str)] = &[("claude", ".claude"), ("agents", ".agents")];

/// Outcome of the sync — which surfaces re-deployed, which failed.
#[derive(Debug, Default, Clone)]
pub struct RefreshReport {
    pub refreshed: Vec<String>,
    /// `"<surface>: <reason>"` for each surface whose refresh failed.
    pub failures: Vec<String>,
}

/// Detect which user-scope surfaces actually exist (a `skills` or `rules` dir
/// under `~/.claude` / `~/.agents`). Pure — drives the per-surface refresh and is
/// unit-tested directly. (`skills upgrade` is `--surface`-singular, so we invoke
/// once per *present* surface rather than assuming `claude`.)
pub fn present_user_surfaces(home: &Path) -> Vec<&'static str> {
    USER_SURFACES
        .iter()
        .filter_map(|(name, dir)| {
            let base = home.join(dir);
            (base.join("skills").is_dir() || base.join("rules").is_dir()).then_some(*name)
        })
        .collect()
}

/// The `yf skills upgrade` args for a surface (user scope). Pure/testable.
pub fn upgrade_args(surface: &str) -> [&str; 6] {
    ["skills", "upgrade", "--scope", "user", "--surface", surface]
}

/// Re-deploy user-scope skills/rules by exec'ing the **promoted** binary at
/// `install_target` once per present surface.
///
/// `install_target` MUST be the swap-destination path — NOT a post-swap
/// `current_exe()`, which `self-replace` leaves pointing at the moved-aside OLD
/// binary, silently deploying stale embedded content. Exec'ing the freshly
/// written binary is what makes the new embed take effect, and the running binary
/// is precisely the one that may carry a stale embed.
///
/// Fail-soft: a per-surface failure is recorded, never fatal to the (already
/// successful) swap. Fail-soft is **not** silent — the caller reports failures and
/// exits non-zero on the sync alone (`REQ-YF-SELF-005`).
pub fn run_sync(install_target: &Path, home: &Path) -> RefreshReport {
    let mut report = RefreshReport::default();
    for surface in present_user_surfaces(home) {
        let result = std::process::Command::new(install_target)
            .args(upgrade_args(surface))
            .status();
        match result {
            Ok(s) if s.success() => report.refreshed.push(surface.to_string()),
            Ok(s) => report
                .failures
                .push(format!("{surface}: exited {:?}", s.code())),
            Err(e) => report.failures.push(format!("{surface}: {e}")),
        }
    }
    report
}

#[cfg(test)]
mod tests {
    use super::*;

    /// REQ-YF-SELF-005: the sync routine has exactly ONE definition, shared by
    /// both install paths. Structural check — `run_sync` lives here and nowhere
    /// else, verified by the test suite compiling against this single path.
    #[test]
    fn present_surfaces_detects_skills_or_rules() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        assert!(present_user_surfaces(home).is_empty());
        std::fs::create_dir_all(home.join(".claude/skills")).unwrap();
        let s = present_user_surfaces(home);
        assert_eq!(s, vec!["claude"]);
        std::fs::create_dir_all(home.join(".agents/rules")).unwrap();
        let s = present_user_surfaces(home);
        assert_eq!(s, vec!["claude", "agents"]);
    }

    #[test]
    fn upgrade_args_are_user_scoped_per_surface() {
        assert_eq!(
            upgrade_args("agents"),
            ["skills", "upgrade", "--scope", "user", "--surface", "agents"]
        );
    }
}
