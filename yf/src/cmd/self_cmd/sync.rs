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

/// Is the **config half** suppressed for this run (`REQ-YF-SELF-008`, D-H)?
///
/// Pure: `present(key)` reports whether an env var is set, mirroring the
/// `REQ-YF-SELF-006` nag-suppression precedent (`nag::suppressed`) rather than
/// inventing a second convention.
///
/// Under `CI` the config half MUST be suppressed while skills and the rules
/// aggregate still deploy. Without this the sync would either hang or hard-fail in
/// CI, because the consent gate can never be satisfied non-interactively — an
/// unattended runner has nobody to pass `--allow-permissions-write`.
///
/// `YF_NO_CONFIG_SYNC` is the explicit per-run opt-out for the same behavior
/// outside CI.
pub fn config_half_suppressed(present: impl Fn(&str) -> bool) -> bool {
    present("CI") || present("YF_NO_CONFIG_SYNC")
}

/// The `yf harness skills install` args for one harness (user scope), running the
/// `--tune` bridge.
///
/// `rules_only` selects the safe half — skills + the rules aggregate, and **no
/// config file touched** (`REQ-YF-TUNE-028`).
///
/// **`CI` suppression is implemented BY EMITTING `--rules-only`** (D-H via D-Q),
/// not by a second suppression mechanism: there is exactly one way to say "deploy
/// the safe half only", so the two callers cannot drift apart (pass-2 M3).
///
/// Issue 3.8 flipped the sync off passing `rules_only` unconditionally: it is now
/// `false` by default, i.e. the consent-gated FULL tune. That flip is the single
/// thing in this plan that can ship a config write, and it is safe because the
/// write is gated on the far side — without `--allow-permissions-write` the bridge
/// returns `consent_required`, writes nothing, and (not being `"ok"`) is counted a
/// failure by [`classify_tune_status`].
/// The install argv, plus the Issue 2.5 skills-dedupe flag.
///
/// `skills_already_written` is set for a harness whose **resolved skills root** was already
/// written earlier in this same sync. Its run still happens — the surface half is
/// harness-specific — but the redundant skills write is dropped.
pub fn install_args_full(
    harness: &str,
    rules_only: bool,
    skills_already_written: bool,
) -> Vec<String> {
    let mut v: Vec<String> = [
        "harness",
        "skills",
        "install",
        "--scope",
        "user",
        "--harness",
        harness,
        "--tune",
    ]
    .iter()
    .map(|s| s.to_string())
    .collect();
    if rules_only {
        v.push("--rules-only".to_string());
    }
    if skills_already_written {
        v.push("--no-skills".to_string());
    }
    v.push("--json".to_string());
    v
}

/// Which of the selected harnesses may skip the skills write, by resolved skills root.
///
/// **The dedupe is by RESOLVED PATH, not by harness id** — the same key
/// `REQ-YF-INSTALL-002` already uses, because it is the path that collides. Order-preserving:
/// the first harness to claim a root writes it, and later claimants of that same root are
/// marked. Returns one entry per input harness, aligned by index.
///
/// Note what this deliberately does NOT do: it never removes a harness from the fan-out. Four
/// harnesses sharing `.agents/skills` still each need their own tune, because a surface dir is
/// harness-specific even where a skills root is shared. Dropping the repeats would silently
/// stop deploying three harnesses' rules and config.
pub fn dedupe_skills_writes(home: &Path, harnesses: &[&str]) -> Vec<bool> {
    let mut seen: std::collections::BTreeSet<std::path::PathBuf> =
        std::collections::BTreeSet::new();
    harnesses
        .iter()
        .map(|h| {
            let root = crate::dest::skills_dir_for_anchor(home, h, crate::cli::Scope::User);
            // `insert` returns false when the root was already claimed → skip this write.
            !seen.insert(root)
        })
        .collect()
}

/// Should the sync's exec carry the consent flag?
///
/// Only when the operator asked for it AND the config half is not suppressed —
/// passing an authorization for a sub-operation that is not running would be
/// meaningless, and under `CI` there is nobody to have authorized it.
fn consent_args(allow_permissions_write: bool, rules_only: bool) -> Option<String> {
    (allow_permissions_write && !rules_only)
        .then(|| crate::cmd::harness::consent::CONSENT_FLAG.to_string())
}

/// Outcome of the sync — which surfaces re-deployed, which failed, and what the
/// config half actually changed.
#[derive(Debug, Default, Clone)]
pub struct RefreshReport {
    pub refreshed: Vec<String>,
    /// Harnesses whose redundant SKILLS write was skipped because an earlier harness in this
    /// same sync already wrote their (shared) skills root — Issue 2.5. They were still tuned.
    pub skills_write_skipped: Vec<String>,
    /// `"<surface>: <reason>"` for each surface whose refresh failed.
    pub failures: Vec<String>,
    /// The **per-key config delta**, `"<harness>: <change>"` (Issue 3.4).
    ///
    /// Extracted from each harness's `config.changes` — the change set over
    /// `merge::Change` — NOT from `plan_targets`/`target_plan_json`, which emit
    /// `{harness, config_path, rules_path}`, i.e. the blast radius rather than the
    /// change set (pass-1 C7). A list of file paths is not a delta.
    ///
    /// This is what makes it impossible for `bypassPermissions` to be applied
    /// invisibly: whatever the config half writes is named in the report. Empty
    /// while the exec runs `--rules-only` (nothing is written), and populated once
    /// Issue 3.8 flips the exec to the consent-gated full tune.
    pub config_changes: Vec<String>,
}

/// Pull the per-key config delta out of a tune-bridge payload (Issue 3.4).
///
/// Reads `harnesses[].config.changes`, which the bridge emits for BOTH the applied
/// (`Aligned`) and the blocked (`consent_required`) cases — so the operator sees
/// the change set whether it was written or is being asked about.
fn extract_config_changes(stdout: &str) -> Vec<String> {
    let Ok(v) = serde_json::from_str::<serde_json::Value>(stdout) else {
        return Vec::new();
    };
    let Some(harnesses) = v.get("harnesses").and_then(|h| h.as_array()) else {
        return Vec::new();
    };
    let mut out = Vec::new();
    for h in harnesses {
        let name = h.get("harness").and_then(|n| n.as_str()).unwrap_or("?");
        let Some(changes) = h.pointer("/config/changes").and_then(|c| c.as_array()) else {
            continue;
        };
        for c in changes {
            // The bridge renders a consent-blocked delta as strings and an applied
            // one as structured objects; both are surfaced verbatim.
            let rendered = match c.as_str() {
                Some(s) => s.to_string(),
                None => c.to_string(),
            };
            out.push(format!("{name}: {rendered}"));
        }
    }
    out
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
pub fn run_sync(
    install_target: &Path,
    home: &Path,
    allow_permissions_write: bool,
) -> RefreshReport {
    let rules_only = config_half_suppressed(|k| std::env::var_os(k).is_some());
    // Issue 2.5: which harnesses may skip the redundant SKILLS write, keyed by resolved path.
    // Computed ONCE, before the fan-out, so the decision does not depend on iteration state
    // inside the closure.
    let selected = sync_harnesses(home);
    let skip: std::collections::BTreeSet<&str> = dedupe_skills_writes(home, &selected)
        .into_iter()
        .zip(selected.iter().copied())
        .filter_map(|(s, h)| s.then_some(h))
        .collect();
    run_sync_with(home, |harness| {
        let mut argv = install_args_full(harness, rules_only, skip.contains(harness));
        if let Some(flag) = consent_args(allow_permissions_write, rules_only) {
            // Insert before --json so the arg order stays conventional.
            let at = argv.len() - 1;
            argv.insert(at, flag);
        }
        std::process::Command::new(install_target)
            .args(argv)
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
    let selected = sync_harnesses(home);
    // Issue 2.5: after the collapse four of the five rows share one skills root, so an
    // undeduped fan-out writes it once per harness. Computed here and consumed by the caller's
    // `exec`, which is what actually builds the argv.
    report.skills_write_skipped = dedupe_skills_writes(home, &selected)
        .iter()
        .zip(selected.iter())
        .filter(|(skip, _)| **skip)
        .map(|(_, h)| h.to_string())
        .collect();
    for harness in selected {
        match exec(harness) {
            Err(e) => report.failures.push(format!("{harness}: {e}")),
            Ok((false, code, _)) => report.failures.push(format!("{harness}: exited {code:?}")),
            // Exited 0 — now check the PAYLOAD, because exit 0 is not proof.
            Ok((true, _, stdout)) => {
                // Surface the config delta either way (Issue 3.4): on success so a
                // write is never invisible, and on a consent refusal so the
                // operator can see what they are being asked to authorize.
                report
                    .config_changes
                    .extend(extract_config_changes(&stdout));
                match classify_tune_status(&stdout) {
                    Ok(()) => report.refreshed.push(harness.to_string()),
                    Err(reason) => report.failures.push(format!("{harness}: {reason}")),
                }
            }
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
        let detected = crate::harness_detect::detect_user_scope(&home, Some(path.as_os_str()));
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

    /// REQ-YF-SELF-008 / REQ-YF-TUNE-023: the exec always passes an **explicit
    /// `--harness`**, which bypasses the multi-harness fan-out gate by
    /// construction — so the `confirmation_required` exit-0 no-write trap cannot be
    /// reached at all.
    #[test]
    fn install_args_are_explicit_per_harness() {
        for rules_only in [true, false] {
            let args = install_args_full("codex", rules_only, false);
            let i = args.iter().position(|a| a == "--harness").expect(
                "the exec must always name the harness explicitly (bypasses the fan-out gate)",
            );
            assert_eq!(args[i + 1], "codex");
            assert!(args.iter().any(|a| a == "--tune"));
            assert!(args.iter().any(|a| a == "--json"));
        }
    }

    /// REQ-YF-TUNE-028 / REQ-YF-SELF-008 (Issues 3.3 + 3.8): `--rules-only` is
    /// emitted **iff** the config half is suppressed.
    ///
    /// Issue 3.8 flipped the exec off an unconditional `--rules-only`; Issue 3.3
    /// implements `CI` suppression **by emitting that same flag**, not by a second
    /// mechanism — so there is exactly one way to say "safe half only" and the two
    /// callers cannot drift apart (pass-2 M3).
    #[test]
    fn rules_only_is_emitted_iff_the_config_half_is_suppressed() {
        assert!(
            install_args_full("codex", true, false)
                .iter()
                .any(|a| a == "--rules-only"),
            "suppressed → --rules-only"
        );
        assert!(
            !install_args_full("codex", false, false)
                .iter()
                .any(|a| a == "--rules-only"),
            "not suppressed → the consent-gated FULL tune (Issue 3.8's flip)"
        );
    }

    /// REQ-YF-SELF-008 (D-H): the config half is suppressed under `CI` and under
    /// the explicit `YF_NO_CONFIG_SYNC` opt-out, and NOT otherwise.
    ///
    /// Pure over an injected env probe (mirroring the `REQ-YF-SELF-006`
    /// `nag::suppressed` precedent), so the test never reads ambient env.
    #[test]
    fn config_half_is_suppressed_under_ci() {
        assert!(config_half_suppressed(|k| k == "CI"));
        assert!(config_half_suppressed(|k| k == "YF_NO_CONFIG_SYNC"));
        assert!(!config_half_suppressed(|_| false));
        // An unrelated variable must not suppress it.
        assert!(!config_half_suppressed(|k| k == "SOME_OTHER_VAR"));
    }

    /// REQ-YF-SELF-008 (D-H): under `CI`, **skills and rules still deploy** — the
    /// suppression removes the config half only, never the whole sync.
    #[test]
    fn ci_suppression_still_deploys_skills_and_rules() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        std::fs::create_dir_all(home.join(".claude/skills")).unwrap();

        let seen = std::cell::RefCell::new(Vec::<Vec<String>>::new());
        let report = run_sync_with(home, |h| {
            let args = install_args_full(h, /*suppressed=*/ true, false);
            seen.borrow_mut().push(args);
            Ok((true, Some(0), r#"{"status":"ok"}"#.to_string()))
        });

        // The sync RAN (skills + rules deployed) rather than being skipped.
        assert_eq!(report.refreshed, vec!["claude-code"]);
        assert!(report.failures.is_empty());
        // ...via the rules-only form, so no config was written.
        assert!(seen.borrow()[0].iter().any(|a| a == "--rules-only"));
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

    // ---- Issue 3.4: the config delta is surfaced, never invisible ---------

    /// REQ-YF-SELF-008 (Issue 3.4): the sync report carries the **per-key config
    /// delta**, so a `bypassPermissions` write can never be applied invisibly.
    ///
    /// Sourced from `harnesses[].config.changes` — the change set over
    /// `merge::Change` — NOT `plan_targets`/`target_plan_json`, which emit
    /// `{harness, config_path, rules_path}`: the blast radius, not the delta
    /// (pass-1 C7).
    #[test]
    fn config_delta_is_surfaced_in_the_sync_report() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        std::fs::create_dir_all(home.join(".claude/skills")).unwrap();

        let payload = r#"{
          "status":"ok",
          "harnesses":[{
            "harness":"claude-code",
            "config":{"status":"written","changes":[
              "+ permissions.defaultMode = \"bypassPermissions\""
            ]}
          }]
        }"#;
        let report = run_sync_with(home, |_h| Ok((true, Some(0), payload.to_string())));

        assert_eq!(report.failures, Vec::<String>::new());
        assert!(
            report
                .config_changes
                .iter()
                .any(|c| c.contains("permissions.defaultMode") && c.contains("bypassPermissions")),
            "the delta must NAME the bypassPermissions write: {:?}",
            report.config_changes
        );
        // Attributed to its harness, since the sync runs several.
        assert!(report.config_changes[0].starts_with("claude-code: "));
    }

    /// The delta is surfaced on a consent REFUSAL too — the operator has to see
    /// what they are being asked to authorize, not just that something was refused.
    #[test]
    fn config_delta_is_surfaced_on_a_consent_refusal() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        std::fs::create_dir_all(home.join(".codex")).unwrap();

        let payload = r#"{
          "status":"consent_required",
          "harnesses":[{
            "harness":"codex",
            "config":{"status":"consent_required","changes":[
              "+ approval_policy = \"never\""
            ]}
          }]
        }"#;
        let report = run_sync_with(home, |_h| Ok((true, Some(0), payload.to_string())));

        // consent_required is not "ok", so it counts as a failure (Issue 1.3)...
        assert_eq!(report.failures.len(), 1, "{report:?}");
        // ...and the delta is still reported.
        assert!(
            report
                .config_changes
                .iter()
                .any(|c| c.contains("approval_policy")),
            "the refusal must still name the change set: {:?}",
            report.config_changes
        );
    }

    /// Under `--rules-only` nothing is written, so the delta is empty — the
    /// report must not imply a config change that did not happen.
    #[test]
    fn rules_only_sync_reports_an_empty_config_delta() {
        let td = tempfile::tempdir().unwrap();
        let home = td.path();
        std::fs::create_dir_all(home.join(".claude/skills")).unwrap();

        let payload = r#"{"status":"ok","harnesses":[{"harness":"claude-code",
          "config":{"status":"skipped"}}]}"#;
        let report = run_sync_with(home, |_h| Ok((true, Some(0), payload.to_string())));

        assert_eq!(report.refreshed, vec!["claude-code"]);
        assert!(
            report.config_changes.is_empty(),
            "a rules-only run changes no config: {:?}",
            report.config_changes
        );
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
