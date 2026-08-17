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

// ---- The sync's presence predicate (REQ-YF-SELF-008, plan-042 Issue 1.2) ----

/// Which signal selects a harness for the sync.
///
/// The predicate is **per-harness by necessity**, not by preference — a single
/// uniform rule fails one of the two hazards below whichever way it is written.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PresenceSignal {
    /// **yf already deployed here** — a `skills` or `rules` dir under yf's own
    /// surface dir. Used for the two harnesses yf has always been able to reach.
    YfSurface,
    /// **The harness's own config home exists** — the harness has actually been
    /// configured by its user. Used for the three harnesses the vendor path could
    /// never reach at all.
    ConfigHome,
}

/// One harness's sync-presence probe.
pub struct SyncPresence {
    /// The `--harness` id passed to the exec.
    pub id: &'static str,
    /// Home-relative directory the signal probes.
    pub subdir: &'static str,
    /// Which signal this row uses.
    pub signal: PresenceSignal,
}

/// The sync's presence table — **all five** supported harness ids, each stating
/// which signal it uses (`REQ-YF-SELF-008`).
///
/// This deliberately does **not** reuse [`crate::harness_detect`]'s
/// `detect_user_scope` / `effective_harnesses`, whose user-scope probe is
/// `home_dir_exists || binary_on_PATH`. A binary on `PATH` is not evidence a
/// harness was ever *configured*: a machine carrying the `codex` binary but no
/// `~/.codex` has never been set up, and creating one as a side effect of
/// promoting a binary is exactly the surprise the consent gate exists to prevent.
///
/// Two hazards a naive predicate hits, both pinned by tests below:
///
/// 1. **Regression.** `harness_detect::PROBES` has four rows and **no `agents`
///    row**, while the incumbent [`present_user_surfaces`] probes
///    `~/.agents/{skills,rules}`. A config-home-only table would stop refreshing a
///    machine with `~/.agents/skills` and no `~/.codex`. The `agents` row below
///    keeps that machine selected.
/// 2. **Over-broadening.** `~/.claude` exists on **every** Claude Code machine,
///    whether or not yf was ever installed at user scope. Probing it as a config
///    home would make the sync start writing into a surface the operator never
///    yf-installed. `claude-code` therefore keeps the incumbent
///    *yf-already-deployed-here* signal rather than a bare `~/.claude` check.
///
/// `codex`, `opencode` and `pi` use the config-home signal because they have
/// **never** been reachable from the vendor path (its `--surface` alias spanned
/// only `claude` and `agents`), so there is no incumbent yf-deployment signal to
/// preserve, and their config homes are a genuine "configured this harness" mark.
pub const SYNC_PRESENCE: &[SyncPresence] = &[
    SyncPresence {
        id: "claude-code",
        subdir: ".claude",
        signal: PresenceSignal::YfSurface,
    },
    SyncPresence {
        id: "agents",
        subdir: ".agents",
        signal: PresenceSignal::YfSurface,
    },
    SyncPresence {
        id: "codex",
        subdir: ".codex",
        signal: PresenceSignal::ConfigHome,
    },
    SyncPresence {
        id: "opencode",
        subdir: ".config/opencode",
        signal: PresenceSignal::ConfigHome,
    },
    SyncPresence {
        id: "pi",
        subdir: ".pi",
        signal: PresenceSignal::ConfigHome,
    },
];

/// Does this row's signal fire under `home`?
fn signal_fires(row: &SyncPresence, home: &Path) -> bool {
    let base = home.join(row.subdir);
    match row.signal {
        // yf already deployed here — a skills or rules dir it wrote.
        PresenceSignal::YfSurface => base.join("skills").is_dir() || base.join("rules").is_dir(),
        // The harness's own config home exists.
        PresenceSignal::ConfigHome => base.is_dir(),
    }
}

/// The harness ids the sync should act on, in table order (`REQ-YF-SELF-008`).
///
/// Pure over the injected `home` anchor — reads no ambient env, so tests drive it
/// under a sandboxed `HOME` with zero host dependency. Notably it takes **no
/// `PATH`**: a binary on `PATH` can never select a harness here, which is the
/// difference from `harness_detect::detect_user_scope`.
pub fn sync_harnesses(home: &Path) -> Vec<&'static str> {
    SYNC_PRESENCE
        .iter()
        .filter(|row| signal_fires(row, home))
        .map(|row| row.id)
        .collect()
}

/// The `yf harness skills install` args for one harness (user scope), running the
/// `--tune` bridge in **rules-only** mode (`REQ-YF-TUNE-028`).
///
/// Rules-only is the Epic-2 form: it deploys skills and the rules aggregate and
/// **cannot write config**, so the sync carries no consent burden until the
/// consent gate ships and the exec flips off `--rules-only`.
pub fn install_args(harness: &str) -> Vec<String> {
    [
        "harness",
        "skills",
        "install",
        "--scope",
        "user",
        "--harness",
        harness,
        "--tune",
        "--rules-only",
        "--json",
    ]
    .iter()
    .map(|s| s.to_string())
    .collect()
}

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

    // ---- Issue 1.2: the sync presence predicate ----------------------------

    /// REQ-YF-SELF-008: the presence table covers **all five** supported harness
    /// ids and states a signal for each — the "define it explicitly for all five"
    /// requirement, so a future harness cannot be added without a declared signal.
    #[test]
    fn presence_table_covers_all_five_harness_ids() {
        let ids: Vec<&str> = SYNC_PRESENCE.iter().map(|r| r.id).collect();
        assert_eq!(ids, ["claude-code", "agents", "codex", "opencode", "pi"]);
        // Every descriptor-table id has a presence row (no harness left unreachable).
        for d in crate::harness_desc::DESCRIPTORS {
            assert!(
                SYNC_PRESENCE.iter().any(|r| r.id == d.id),
                "descriptor id {} has no sync presence row",
                d.id
            );
        }
    }

    /// REQ-YF-SELF-008 / SC3 — **the regression hazard.** `harness_detect::PROBES`
    /// has no `agents` row, so a config-home-only predicate would stop refreshing a
    /// machine the incumbent `present_user_surfaces` refreshed today. A machine with
    /// `~/.agents/skills` and **no** `~/.codex` must still be selected.
    #[test]
    fn agents_surface_without_codex_home_is_still_selected() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        std::fs::create_dir_all(home.join(".agents/skills")).unwrap();
        // Deliberately NO ~/.codex.
        assert!(!home.join(".codex").exists());

        let selected = sync_harnesses(home);
        assert!(
            selected.contains(&"agents"),
            "~/.agents/skills must select the `agents` id (incumbent signal preserved): {selected:?}"
        );
        assert!(
            !selected.contains(&"codex"),
            "no ~/.codex means codex is not selected: {selected:?}"
        );
    }

    /// REQ-YF-SELF-008 / SC4 (D-O) — **a binary on `PATH` is not presence.** The
    /// sync predicate takes no `PATH` at all, so a harness whose binary is installed
    /// but whose config home does not exist is **not** selected. This is the
    /// difference from `harness_detect::detect_user_scope`, whose user probe ORs the
    /// binary check.
    #[test]
    fn harness_binary_on_path_without_config_home_is_not_selected() {
        let sandbox = tempfile::tempdir().unwrap();
        let home = sandbox.path().join("home");
        let bindir = sandbox.path().join("bin");
        std::fs::create_dir_all(&home).unwrap();
        std::fs::create_dir_all(&bindir).unwrap();
        // A real-looking codex binary on PATH, but no ~/.codex.
        let bin = bindir.join("codex");
        std::fs::write(&bin, b"#!/bin/sh\n").unwrap();
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            std::fs::set_permissions(&bin, std::fs::Permissions::from_mode(0o755)).unwrap();
        }

        let selected = sync_harnesses(&home);
        assert!(
            selected.is_empty(),
            "a binary on PATH with no config home must select nothing: {selected:?}"
        );

        // Cross-check the contrast this predicate exists to draw: the INSTALL-009
        // detector *would* have selected it off the PATH probe alone.
        let path = std::ffi::OsString::from(&bindir);
        let detected =
            crate::harness_detect::detect_user_scope(&home, Some(path.as_os_str()));
        assert!(
            detected.contains(&"codex".to_string()),
            "sanity: detect_user_scope selects on the PATH probe — which is precisely \
             why the sync must not reuse it: {detected:?}"
        );
    }

    /// REQ-YF-SELF-008 / R8 — **the over-broadening hazard.** `~/.claude` exists on
    /// every Claude Code machine. A bare config-home probe would make the sync begin
    /// writing into a surface yf was never installed into, so `claude-code` keeps the
    /// incumbent *yf-already-deployed-here* signal: a bare `~/.claude` with no
    /// yf-written `skills`/`rules` dir is **not** selected.
    #[test]
    fn bare_claude_home_without_yf_deployment_is_not_selected() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        // A Claude Code machine yf has never installed into: the dir and a settings
        // file exist, but no yf-written skills/ or rules/ dir.
        std::fs::create_dir_all(home.join(".claude")).unwrap();
        std::fs::write(home.join(".claude/settings.json"), b"{}").unwrap();

        let selected = sync_harnesses(home);
        assert!(
            !selected.contains(&"claude-code"),
            "bare ~/.claude with no yf deployment must NOT be selected: {selected:?}"
        );

        // Once yf has actually deployed there, it IS selected.
        std::fs::create_dir_all(home.join(".claude/skills")).unwrap();
        assert!(
            sync_harnesses(home).contains(&"claude-code"),
            "~/.claude/skills (yf deployed here) must be selected"
        );
    }

    /// REQ-YF-SELF-008 / SC3 — codex, opencode and pi become reachable for the
    /// first time. The vendor path's `--surface` alias spanned only `claude` and
    /// `agents`, so all three were unreachable; each is now selected by its own
    /// config home.
    #[test]
    fn codex_opencode_and_pi_are_reachable_by_config_home() {
        for (subdir, id) in [
            (".codex", "codex"),
            (".config/opencode", "opencode"),
            (".pi", "pi"),
        ] {
            let td = tempfile::tempdir().unwrap();
            let home = td.path();
            std::fs::create_dir_all(home.join(subdir)).unwrap();
            let selected = sync_harnesses(home);
            assert!(
                selected.contains(&id),
                "~/{subdir} must select {id} (previously unreachable): {selected:?}"
            );
        }
    }

    /// REQ-YF-SELF-008: an empty home selects nothing — the predicate reads no
    /// ambient env, so the host's real harnesses cannot leak into a sandboxed run.
    #[test]
    fn empty_home_selects_nothing() {
        let td = tempfile::tempdir().unwrap();
        assert!(sync_harnesses(td.path()).is_empty());
    }

    /// REQ-YF-SELF-008 / REQ-YF-TUNE-028: the exec passes an **explicit
    /// `--harness`** (which bypasses the `REQ-YF-TUNE-023` fan-out gate by
    /// construction) and, until Issue 3.8 flips it, `--rules-only` — so the sync
    /// cannot write config.
    #[test]
    fn install_args_are_explicit_per_harness_and_rules_only() {
        let args = install_args("codex");
        assert_eq!(
            args,
            [
                "harness",
                "skills",
                "install",
                "--scope",
                "user",
                "--harness",
                "codex",
                "--tune",
                "--rules-only",
                "--json"
            ]
        );
        // The explicit --harness is what bypasses the no---harness confirmation
        // branch that returns `confirmation_required` while writing nothing.
        assert!(args.iter().any(|a| a == "--harness"));
        assert!(args.iter().any(|a| a == "--rules-only"));
    }
}
