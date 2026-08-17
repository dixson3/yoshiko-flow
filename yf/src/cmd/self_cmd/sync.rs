//! The **install-time sync** shared by both install paths (`REQ-YF-SELF-005`,
//! `REQ-YF-SELF-008`, plan-042).
//!
//! Both `yf self update` (vendor) and `yf self install --from-build` (developer)
//! must leave the machine's **deployed** surface — skills, the rules aggregate,
//! and harness config — matching the binary they just promoted. They start from
//! different states, which is why `REQ-YF-SELF-005` specifies them separately;
//! they converge here so there is exactly **one** implementation to keep correct.
//!
//! Extracted from `update.rs` as a pure refactor (plan-042 Issue 1.1), then moved
//! off the deprecated `--surface` alias onto explicit per-harness `--harness`
//! selection (Issue 1.2/1.3).

use std::path::Path;

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
///    row**, while the incumbent `present_user_surfaces` (now replaced by this
///    table) probed `~/.agents/{skills,rules}`. A config-home-only table would stop refreshing a
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

/// Classify one harness's `--tune` bridge result (`REQ-YF-SELF-008`).
///
/// **An exit code of 0 is not evidence of success.** Measured (E5): `yf harness
/// skills install --tune --json` with no `--harness` returns
/// `{"status":"confirmation_required"}` having written **no rules and no config**,
/// and **exits 0** — with skill *bodies* already written, which is what makes the
/// false success plausible. `tune_bridge_at`'s malformed-settings fail-safe path
/// returns `{"status":"refused"}` the same way. Both are `Ok(())` at the process
/// level.
///
/// So the caller must read the **payload**, and treat **any** `tune.status` other
/// than `"ok"` as a failure — not just the one status that happens to be named in
/// the defect report. This is the same false-success shape as #136.
///
/// Returns `Err(reason)` when the run must be counted as a failure.
fn classify_tune_status(stdout: &str) -> Result<(), String> {
    let Ok(v) = serde_json::from_str::<serde_json::Value>(stdout) else {
        return Err(format!(
            "unparseable --json output from the tune bridge (got {} bytes); \
             cannot confirm rules or config were written",
            stdout.len()
        ));
    };
    match v.get("status").and_then(|s| s.as_str()) {
        Some("ok") => Ok(()),
        // Named explicitly because both are exit-0 no-write paths.
        Some(s @ ("confirmation_required" | "refused")) => Err(format!(
            "tune reported status {s:?} — it exited 0 but wrote no rules and no \
             config (skill bodies only)"
        )),
        // Any OTHER non-ok status is a failure too. The point of D-M as widened is
        // that the allow-list is `ok`, not that the deny-list is those two.
        Some(other) => Err(format!("tune reported status {other:?}, expected \"ok\"")),
        None => Err("tune output carried no `status` field".to_string()),
    }
}

/// Re-deploy user-scope skills, the rules aggregate, and (once Issue 3.8 flips the
/// exec off `--rules-only`) harness config, by exec'ing the **promoted** binary at
/// `install_target` once per harness the presence predicate selects.
///
/// `install_target` MUST be the swap-destination path — NOT a post-swap
/// `current_exe()`, which `self-replace` leaves pointing at the moved-aside OLD
/// binary, silently deploying stale embedded content. Exec'ing the freshly
/// written binary is what makes the new embed take effect, and the running binary
/// is precisely the one that may carry a stale embed.
///
/// Each harness is passed **explicitly** via `--harness`, which bypasses the
/// `REQ-YF-TUNE-023` multi-harness fan-out gate by construction — so the
/// `confirmation_required` trap cannot be reached at all. [`classify_tune_status`]
/// is the second, independent defense against it.
///
/// Fail-soft: a per-harness failure is recorded, never fatal to the (already
/// successful) swap. Fail-soft is **not** silent — the caller reports failures and
/// exits non-zero on the sync alone (`REQ-YF-SELF-005`).
pub fn run_sync(install_target: &Path, home: &Path) -> RefreshReport {
    run_sync_with(home, |harness| {
        std::process::Command::new(install_target)
            .args(install_args(harness))
            .output()
            .map(|o| {
                (
                    o.status.success(),
                    o.status.code(),
                    String::from_utf8_lossy(&o.stdout).into_owned(),
                )
            })
            .map_err(|e| e.to_string())
    })
}

/// Env-free core of [`run_sync`] (the unit-test seam): select harnesses via the
/// presence predicate and run `exec` for each, classifying the result.
///
/// `exec` returns `(process_succeeded, exit_code, stdout)` or a spawn error.
pub fn run_sync_with<F>(home: &Path, mut exec: F) -> RefreshReport
where
    F: FnMut(&str) -> Result<(bool, Option<i32>, String), String>,
{
    let mut report = RefreshReport::default();
    for harness in sync_harnesses(home) {
        match exec(harness) {
            Err(e) => report.failures.push(format!("{harness}: {e}")),
            Ok((false, code, _)) => report
                .failures
                .push(format!("{harness}: exited {code:?}")),
            // Exited 0 — now check the PAYLOAD, because exit 0 is not proof.
            Ok((true, _, stdout)) => match classify_tune_status(&stdout) {
                Ok(()) => report.refreshed.push(harness.to_string()),
                Err(reason) => report.failures.push(format!("{harness}: {reason}")),
            },
        }
    }
    report
}

#[cfg(test)]
mod tests {
    use super::*;

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

    // ---- Issue 1.3: exit 0 is not proof (D-M, widened per pass-1 C6) -------

    /// REQ-YF-SELF-008 / R1 — **the confirmation trap.** `install --tune --json`
    /// without `--harness` returns `confirmation_required` having written no rules
    /// and no config, and **exits 0**. The sync must count that as a FAILURE.
    #[test]
    fn confirmation_required_at_exit_zero_is_a_failure() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        std::fs::create_dir_all(home.join(".claude/skills")).unwrap();

        let report = run_sync_with(home, |_h| {
            Ok((
                /*success=*/ true,
                Some(0),
                r#"{"status":"confirmation_required","reason":"multi-harness auto-detected"}"#
                    .to_string(),
            ))
        });

        assert!(
            report.refreshed.is_empty(),
            "an exit-0 confirmation_required must NOT count as refreshed: {report:?}"
        );
        assert_eq!(report.failures.len(), 1, "{report:?}");
        assert!(
            report.failures[0].contains("confirmation_required"),
            "the failure must name the status: {}",
            report.failures[0]
        );
    }

    /// REQ-YF-SELF-008 / pass-1 C6 — **the second exit-0 false success.**
    /// `tune_bridge_at`'s malformed-settings fail-safe path sets `status: "refused"`
    /// and also returns `Ok(())`. D-M as originally written named only
    /// `confirmation_required`; widened, the allow-list is `ok`.
    #[test]
    fn refused_at_exit_zero_is_a_failure() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        std::fs::create_dir_all(home.join(".claude/skills")).unwrap();

        let report = run_sync_with(home, |_h| {
            Ok((true, Some(0), r#"{"status":"refused"}"#.to_string()))
        });

        assert!(report.refreshed.is_empty(), "{report:?}");
        assert_eq!(report.failures.len(), 1, "{report:?}");
        assert!(report.failures[0].contains("refused"));
    }

    /// REQ-YF-SELF-008: the check is an **allow-list on `ok`**, not a deny-list on
    /// the two known-bad statuses. An unrecognized future status is a failure, and
    /// so is output with no `status` field or unparseable output — none of which
    /// may be silently treated as success.
    #[test]
    fn only_status_ok_counts_as_success() {
        assert!(classify_tune_status(r#"{"status":"ok"}"#).is_ok());
        for bad in [
            r#"{"status":"dry_run"}"#,
            r#"{"status":"some_future_status"}"#,
            r#"{"harnesses":[]}"#,
            "not json at all",
            "",
        ] {
            assert!(
                classify_tune_status(bad).is_err(),
                "must not accept {bad:?} as success"
            );
        }
    }

    /// REQ-YF-SELF-005: a clean `status: "ok"` per selected harness is a success,
    /// and the sync runs **once per selected harness** with that harness's id.
    #[test]
    fn ok_status_refreshes_each_selected_harness() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        std::fs::create_dir_all(home.join(".claude/skills")).unwrap();
        std::fs::create_dir_all(home.join(".codex")).unwrap();

        let seen = std::cell::RefCell::new(Vec::<String>::new());
        let report = run_sync_with(home, |h| {
            seen.borrow_mut().push(h.to_string());
            Ok((true, Some(0), r#"{"status":"ok"}"#.to_string()))
        });

        assert_eq!(report.failures, Vec::<String>::new());
        assert_eq!(report.refreshed, vec!["claude-code", "codex"]);
        assert_eq!(*seen.borrow(), vec!["claude-code", "codex"]);
    }

    /// REQ-YF-SELF-005: a genuine non-zero exit is still a failure (the ordinary
    /// case the payload check sits on top of, not instead of).
    #[test]
    fn nonzero_exit_is_a_failure() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        std::fs::create_dir_all(home.join(".claude/skills")).unwrap();
        let report = run_sync_with(home, |_h| Ok((false, Some(2), String::new())));
        assert!(report.refreshed.is_empty());
        assert_eq!(report.failures.len(), 1);
    }
}
