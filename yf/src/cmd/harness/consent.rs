//! The **consent gate** for the install-time sync's config half
//! (`REQ-YF-SELF-008`, plan-042 Issue 3.1 — the D-C1 split with the D-R predicate).
//!
//! Config alignment may apply **automatically** only when both hold:
//!
//! 1. the target config file **already exists**, and
//! 2. the **computed change set** contains no entry declaring
//!    `consent_required: true` (`REQ-YF-TUNE-001`).
//!
//! Otherwise the sync prints the delta and requires the explicit consent flag.
//!
//! ## Why the predicate is profile-declared, not key-path-matched
//!
//! An earlier design keyed on a `permissions.*` key-path prefix. That predicate is
//! **claude-code-specific**: the same class of autonomy lever is
//! `approval_policy = "never"` on codex and `permission.* = "allow"` (singular) on
//! opencode, and **neither matches `permissions.*`**. On a machine with an existing
//! codex or opencode config, the "file exists AND no `permissions.*` key" branch
//! was therefore satisfied, and yf would auto-apply a blanket-allow /
//! never-approve lever **with no consent** — on two of the three config-bearing
//! harnesses. Keying on the profile's own `consent_required` flag is
//! self-maintaining: a new lever declares its own requirement.
//!
//! ## Why existence keys on the READ CLASSIFICATION, not `path.exists()`
//!
//! [`settings::read_settings`] classifies an empty or whitespace-only file as
//! [`SettingsRead::Absent`] — `path.exists()` would call it present. Applying to a
//! whitespace-only file is *materially* creating the config, so it must take the
//! consent-required branch. A malformed file is likewise not a usable "already
//! configured" signal.
//!
//! ## Only mutations count
//!
//! A [`merge::Change::ScalarConflict`] leaves the existing value **untouched** — no
//! write happens, so it cannot escalate anything and does not demand consent. The
//! gate inspects the mutating changes only.

use super::merge::{self, Change, MergeReport};
use super::profile::Profile;
use super::settings::SettingsRead;

/// The CLI flag that authorizes a consent-bearing config write
/// (`REQ-YF-SELF-008`, D-N).
///
/// **Deliberately distinct from `--yes`**, whose existing meaning is "bypass the
/// `REQ-YF-TUNE-023` multi-harness fan-out prompt". Two gates that authorize
/// materially different things must not share one token: an operator passing
/// `--yes` to silence a fan-out prompt would otherwise silently authorize a
/// `bypassPermissions` write.
pub const CONSENT_FLAG: &str = "--allow-permissions-write";

/// Why the automatic path is not available.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ConsentReason {
    /// The config file does not already exist (absent, empty, whitespace-only, or
    /// malformed): applying would **create** it. On claude-code that creation
    /// carries `bypassPermissions`.
    WouldCreateFile(String),
    /// A profile entry declaring `consent_required: true` is in the computed
    /// change set — the D-R predicate.
    DeclaredEntry(String),
}

impl ConsentReason {
    /// A one-line operator-facing explanation.
    pub fn describe(&self) -> String {
        match self {
            ConsentReason::WouldCreateFile(p) => {
                format!("would CREATE the config file {p} (none exists yet)")
            }
            ConsentReason::DeclaredEntry(p) => {
                format!("`{p}` is declared consent_required in the harness profile")
            }
        }
    }
}

/// The gate's verdict for one harness.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ConsentVerdict {
    /// Nothing consent-bearing: the config alignment may apply automatically.
    AutoApply,
    /// Requires the explicit consent flag. Carries every reason, so the operator
    /// sees the full picture rather than the first tripwire.
    Required(Vec<ConsentReason>),
}

impl ConsentVerdict {
    /// Is the automatic path blocked? Used by the `consent_gate` evidence module.
    #[cfg(test)]
    pub fn is_required(&self) -> bool {
        matches!(self, ConsentVerdict::Required(_))
    }
}

/// Does this change actually **write** something?
///
/// Conflicts are reported-but-untouched, so they are not escalations.
fn mutating_path(change: &Change) -> Option<&str> {
    if !change.is_mutation() {
        return None;
    }
    Some(match change {
        Change::ScalarAdded { path, .. }
        | Change::ScalarForced { path, .. }
        | Change::SetUnioned { path, .. } => path,
        Change::ScalarConflict { path, .. } | Change::SetTypeConflict { path, .. } => path,
    })
}

/// Evaluate the consent gate for one harness (`REQ-YF-SELF-008`).
///
/// `read` is the **classification** of the target file (never `path.exists()`);
/// `report` is the change set a dry-run merge computed; `path` is shown to the
/// operator.
pub fn evaluate(
    profile: &Profile,
    read: &SettingsRead,
    report: &MergeReport,
    path: &str,
) -> ConsentVerdict {
    let mut reasons = Vec::new();

    // (1) Does the file already exist, as READ CLASSIFICATION defines it?
    if !matches!(read, SettingsRead::Parsed(_)) {
        reasons.push(ConsentReason::WouldCreateFile(path.to_string()));
    }

    // (2) Does the computed change set touch a consent-declaring entry?
    for change in &report.changes {
        let Some(cpath) = mutating_path(change) else {
            continue;
        };
        if profile
            .entries
            .iter()
            .any(|e| e.path == cpath && e.consent_required)
        {
            reasons.push(ConsentReason::DeclaredEntry(cpath.to_string()));
        }
    }

    if reasons.is_empty() {
        ConsentVerdict::AutoApply
    } else {
        ConsentVerdict::Required(reasons)
    }
}

/// Render the **per-key change set** for the operator (`REQ-YF-SELF-008`, Issue
/// 3.4).
///
/// Built from `MergeReport`'s `changes` over [`merge::Change`] — deliberately NOT
/// from `plan_targets`/`target_plan_json`, which emit `{harness, config_path,
/// rules_path}`, i.e. the **blast radius** rather than the **change set**. A list
/// of file paths is not a delta, and would let `bypassPermissions` be applied
/// without ever being named.
pub fn render_delta(report: &MergeReport) -> Vec<String> {
    report
        .changes
        .iter()
        .filter(|c| c.is_mutation())
        .map(|c| match c {
            Change::ScalarAdded { path, value } => format!("+ {path} = {value}"),
            Change::ScalarForced { path, from, to } => format!("~ {path}: {from} -> {to}"),
            Change::SetUnioned { path, added } => format!(
                "+ {path} += [{}]",
                added
                    .iter()
                    .map(|v| v.to_string())
                    .collect::<Vec<_>>()
                    .join(", ")
            ),
            // Non-mutations are filtered above.
            _ => String::new(),
        })
        .collect()
}

/// The machine-readable consent-blocked verdict for `--json` — the SINGLE source
/// of this shape, so the human and JSON reports cannot drift apart.
pub fn blocked_json(
    path: &std::path::Path,
    reasons: &[ConsentReason],
    report: &MergeReport,
) -> serde_json::Value {
    serde_json::json!({
        "status": "consent_required",
        "path": path.display().to_string(),
        "reasons": reasons.iter().map(ConsentReason::describe).collect::<Vec<_>>(),
        // The per-key delta, so bypassPermissions is never applied invisibly.
        "changes": render_delta(report),
        "flag": CONSENT_FLAG,
    })
}

/// Compute the change set for `profile` against `read` without writing anything —
/// the **dry-run pass before the real one** the gate needs in order to show a
/// delta (Issue 3.4). Safe: `record_manifest` is dry-run-guarded, and this calls
/// only the pure merge.
pub fn compute_change_set(profile: &Profile, read: &SettingsRead) -> MergeReport {
    let existing = match read {
        SettingsRead::Parsed(v) => v.clone(),
        // Absent / malformed both merge against an empty object: the change set is
        // then "everything the profile would write", which is exactly what the
        // operator must see before consenting to file creation.
        _ => serde_json::Value::Object(Default::default()),
    };
    let (_new, report) = merge::merge(&existing, profile, /*force=*/ false);
    report
}

/// The Capability Gate's evidence module (plan-042 Issue 3.6).
///
/// **The module name is load-bearing.** The plan's Capability Gate runs
/// `cargo test -p yf consent_gate`, and a name filter that matches nothing is an
/// exit-0 PASS — measured: `running 0 tests … 0 passed; 4 filtered out`, exit 0.
/// That is the exact exit-0-means-nothing shape R1 defends against, reproduced
/// inside the gate guarding this plan's most dangerous edge. The gate therefore
/// proves the filter NON-EMPTY (`--list | grep -c ': test$' >= 6`) before trusting
/// the run, and this module must keep the name `consent_gate` for that filter to
/// select it.
///
/// The count is a FLOOR against the empty-filter trap, not a coverage measure.
/// Coverage is the four scenario classes below, each exercised across **all three**
/// config-bearing profiles (claude-code, codex, opencode — pi and `agents` ship no
/// config profile, SC5a):
///
/// 1. a fresh machine with no config file **requires** the flag;
/// 2. an existing file whose change set declares **no** consent entry does **not**;
/// 3. a change set that **does** declare one requires the flag **on every profile**;
/// 4. `--yes` alone **never** authorizes it.
#[cfg(test)]
mod consent_gate {
    use super::*;
    use crate::cmd::harness::profile::load_profile;

    fn profile(h: &str) -> Profile {
        load_profile(h).unwrap().unwrap()
    }

    /// The three harnesses that ship a config profile. pi and `agents` ship none,
    /// so the config half is a documented no-op for them (SC5a) — the matrix is
    /// three profiles, not five.
    const CONFIG_BEARING: &[&str] = &["claude-code", "codex", "opencode"];

    // ---- REQ-YF-SELF-008: the gate, on ALL THREE config-bearing profiles ----

    /// A fresh machine with **no config file** requires consent — on every
    /// config-bearing profile. This is the case where applying would CREATE the
    /// file, which on claude-code means creating it with `bypassPermissions`.
    #[test]
    fn consent_gate_fresh_machine_requires_consent_on_every_profile() {
        for h in CONFIG_BEARING {
            let p = profile(h);
            let read = SettingsRead::Absent;
            let report = compute_change_set(&p, &read);
            let v = evaluate(&p, &read, &report, "/sandbox/config");
            assert!(
                v.is_required(),
                "{h}: a fresh machine with no config file must require consent"
            );
            let ConsentVerdict::Required(reasons) = &v else {
                unreachable!()
            };
            assert!(
                reasons
                    .iter()
                    .any(|r| matches!(r, ConsentReason::WouldCreateFile(_))),
                "{h}: the would-create reason must be named: {reasons:?}"
            );
        }
    }

    /// **The C4 regression test.** A change set that DOES declare a
    /// `consent_required` entry requires the flag on **every one of the three**
    /// config-bearing profiles — not just claude-code.
    ///
    /// Each harness's file already exists (so the would-create reason cannot be
    /// what trips the gate) and is seeded with a *different* value at the lever's
    /// path, forcing a real mutation of exactly that key. Under the superseded
    /// `permissions.*` predicate, codex and opencode both slipped through here.
    #[test]
    fn consent_gate_declared_entry_requires_flag_on_every_profile() {
        for h in CONFIG_BEARING {
            let p = profile(h);
            let lever = p
                .entries
                .iter()
                .find(|e| e.consent_required)
                .unwrap_or_else(|| panic!("{h} must ship a consent_required entry"));

            // An EXISTING config whose lever key is absent → applying it is a
            // ScalarAdded mutation of a consent-declaring path.
            let existing = serde_json::json!({ "unrelatedOperatorKey": 1 });
            let read = SettingsRead::Parsed(existing);
            let report = compute_change_set(&p, &read);
            let v = evaluate(&p, &read, &report, "/sandbox/config");

            assert!(
                v.is_required(),
                "{h}: a change set touching {} must require consent",
                lever.path
            );
            let ConsentVerdict::Required(reasons) = &v else {
                unreachable!()
            };
            assert!(
                reasons.iter().any(|r| matches!(
                    r,
                    ConsentReason::DeclaredEntry(path) if path == &lever.path
                )),
                "{h}: the reason must name the declared entry {}: {reasons:?}",
                lever.path
            );
            // And it must NOT be the would-create reason — the file exists.
            assert!(
                !reasons
                    .iter()
                    .any(|r| matches!(r, ConsentReason::WouldCreateFile(_))),
                "{h}: the file exists; the gate must trip on the DECLARED ENTRY"
            );
        }
    }

    /// An existing config file whose change set declares **no** `consent_required`
    /// entry does **not** require the flag — the auto-apply branch is reachable, so
    /// the gate is not vacuously "always require".
    #[test]
    fn consent_gate_existing_file_without_declared_entry_auto_applies() {
        for h in CONFIG_BEARING {
            let p = profile(h);
            // Seed the file with the profile's OWN fully-merged output, so every
            // entry — including each consent-declaring one — is already aligned and
            // produces no change. Uses only the public merge API.
            let (aligned, _) = merge::merge(
                &serde_json::Value::Object(Default::default()),
                &p,
                /*force=*/ false,
            );
            let read = SettingsRead::Parsed(aligned);
            let report = compute_change_set(&p, &read);

            // Sanity: no consent-declaring path is in the mutating change set.
            let touched: Vec<&str> = report
                .changes
                .iter()
                .filter_map(mutating_path)
                .filter(|cp| {
                    p.entries
                        .iter()
                        .any(|e| e.path == *cp && e.consent_required)
                })
                .collect();
            assert!(
                touched.is_empty(),
                "{h}: precondition — no declared entry should be mutated, got {touched:?}"
            );

            let v = evaluate(&p, &read, &report, "/sandbox/config");
            assert_eq!(
                v,
                ConsentVerdict::AutoApply,
                "{h}: an existing file with no declared entry in the change set must auto-apply"
            );
        }
    }

    /// **pass-1 C12**: existence keys on the READ CLASSIFICATION, not
    /// `path.exists()`. A whitespace-only file classifies `Absent`, so it takes the
    /// consent-required branch even though the path exists on disk.
    #[test]
    fn whitespace_only_file_classifies_absent_and_requires_consent() {
        let td = tempfile::tempdir().unwrap();
        let f = td.path().join("settings.json");
        std::fs::write(&f, "   \n\t\n").unwrap();
        assert!(f.exists(), "the file DOES exist on disk");

        let read = super::super::settings::read_settings(&f);
        assert!(
            matches!(read, SettingsRead::Absent),
            "a whitespace-only file must classify Absent, got {read:?}"
        );

        let p = profile("claude-code");
        let report = compute_change_set(&p, &read);
        let v = evaluate(&p, &read, &report, &f.display().to_string());
        assert!(
            v.is_required(),
            "path.exists() is true but the classification is Absent — must require consent"
        );
    }

    /// A reported-but-untouched conflict is **not** an escalation: nothing is
    /// written, so it cannot demand consent on its own.
    #[test]
    fn untouched_conflict_alone_does_not_require_consent() {
        let p = profile("claude-code");
        let lever = p.entries.iter().find(|e| e.consent_required).unwrap();
        assert_eq!(lever.path, "permissions.defaultMode");

        // Operator set a DIFFERENT value: without --force this is a ScalarConflict,
        // left untouched.
        let existing = serde_json::json!({
            "permissions": { "defaultMode": "default" }
        });
        let read = SettingsRead::Parsed(existing);
        let (_v, report) = merge::merge(
            &match &read {
                SettingsRead::Parsed(v) => v.clone(),
                _ => unreachable!(),
            },
            &p,
            false,
        );
        let conflicts = report.conflicts();
        assert!(
            conflicts
                .iter()
                .any(|c| matches!(c, Change::ScalarConflict { path, .. }
                                  if path == "permissions.defaultMode")),
            "precondition: defaultMode must be a conflict, got {report:?}"
        );

        // The conflict on the lever contributes no DeclaredEntry reason.
        let reasons_for_lever = {
            let v = evaluate(&p, &read, &report, "/sandbox/config");
            match v {
                ConsentVerdict::AutoApply => Vec::new(),
                ConsentVerdict::Required(r) => r,
            }
        };
        assert!(
            !reasons_for_lever.iter().any(|r| matches!(
                r,
                ConsentReason::DeclaredEntry(p) if p == "permissions.defaultMode"
            )),
            "an untouched conflict must not count as a consent-bearing write: {reasons_for_lever:?}"
        );
    }

    /// Issue 3.4: the delta is the **per-key change set**, not a list of file
    /// paths — so `bypassPermissions` is named before it is applied.
    #[test]
    fn delta_names_the_keys_not_just_the_file() {
        let p = profile("claude-code");
        let read = SettingsRead::Absent;
        let report = compute_change_set(&p, &read);
        let delta = render_delta(&report);

        assert!(!delta.is_empty(), "a fresh machine has a non-empty delta");
        assert!(
            delta
                .iter()
                .any(|l| l.contains("permissions.defaultMode") && l.contains("bypassPermissions")),
            "the delta must NAME the bypassPermissions write: {delta:?}"
        );
        // Not a blast-radius listing.
        assert!(
            !delta.iter().any(|l| l.contains("config_path")),
            "the delta must be a change set, not {{harness, config_path, rules_path}}"
        );
    }

    /// **Scenario class (d): `--yes` alone NEVER authorizes a consent-bearing
    /// write** (D-N / E5 defect B).
    ///
    /// Asserted two ways, because the behavioral half alone could be satisfied by
    /// an implementation that merely happens not to read `--yes` today:
    ///
    /// 1. **Structurally** — `--yes` lives on `SkillsArgs` and is consumed by the
    ///    fan-out gate in `install.rs`; it is not a field of `HarnessTuneArgs` at
    ///    all, so the consent gate *cannot* see it. That is a stronger guarantee
    ///    than "does not currently consult it".
    /// 2. **Behaviorally** — driving the bridge with the fan-out concern fully
    ///    satisfied (a single explicit harness, which bypasses the fan-out gate the
    ///    way `--yes` would) still yields `consent_required`, on every profile.
    #[test]
    fn yes_alone_never_authorizes_a_consent_bearing_write() {
        // (1) Structural: the gate's argument type has no `yes` field. If someone
        // ever adds one, this fails and forces the D-N decision to be re-made
        // deliberately rather than by autocomplete.
        let cli_src = include_str!("../../cli.rs");
        let tune_args = cli_src
            .split("pub struct HarnessTuneArgs {")
            .nth(1)
            .and_then(|s| s.split("\n}").next())
            .expect("HarnessTuneArgs must be findable in cli.rs");
        assert!(
            !tune_args.contains("pub yes:"),
            "HarnessTuneArgs must NOT carry `yes` — the consent gate must be unable \
             to be satisfied by the fan-out bypass token (D-N)"
        );
        assert!(
            tune_args.contains("pub allow_permissions_write:"),
            "the consent gate's own distinct flag must be present"
        );

        // (2) Behavioral: on every config-bearing profile, a single explicit
        // harness (fan-out concern satisfied, exactly what --yes buys) still trips
        // the consent gate, because that is a different authorization.
        for h in CONFIG_BEARING {
            let td = tempfile::tempdir().unwrap();
            let home = td.path();
            let summary = crate::cmd::harness::tune_bridge_at_for_test(
                &[h.to_string()],
                home,
                /*allow_permissions_write=*/ false,
            );
            assert_eq!(
                summary["status"], "consent_required",
                "{h}: a single explicit harness must still require the D-N flag: {summary}"
            );
            let cfg = &summary["harnesses"][0]["config"];
            assert_eq!(cfg["status"], "consent_required", "{h}: {summary}");
            assert!(
                !cfg["changes"].as_array().unwrap().is_empty(),
                "{h}: the per-key delta must be surfaced with the refusal"
            );
        }
    }

    /// The gate is **satisfiable**: with the explicit D-N flag the config IS
    /// written, on every config-bearing profile. Without this, "requires consent"
    /// could be indistinguishable from "never works".
    #[test]
    fn explicit_flag_authorizes_the_write_on_every_profile() {
        for h in CONFIG_BEARING {
            let td = tempfile::tempdir().unwrap();
            let home = td.path();
            let summary = crate::cmd::harness::tune_bridge_at_for_test(
                &[h.to_string()],
                home,
                /*allow_permissions_write=*/ true,
            );
            assert_eq!(
                summary["status"], "ok",
                "{h}: the explicit flag must authorize the write: {summary}"
            );
            assert_eq!(summary["harnesses"][0]["config"]["status"], "written");
        }
    }

    /// The JSON verdict carries the reasons, the per-key delta, and the flag name
    /// the operator must pass.
    #[test]
    fn verdict_json_carries_reasons_delta_and_flag() {
        let p = profile("claude-code");
        let read = SettingsRead::Absent;
        let report = compute_change_set(&p, &read);
        let ConsentVerdict::Required(reasons) =
            evaluate(&p, &read, &report, "/sandbox/settings.json")
        else {
            panic!("a fresh machine must be consent-blocked");
        };
        let j = blocked_json(
            std::path::Path::new("/sandbox/settings.json"),
            &reasons,
            &report,
        );

        assert_eq!(j["status"], "consent_required");
        assert_eq!(j["path"], "/sandbox/settings.json");
        assert!(!j["reasons"].as_array().unwrap().is_empty());
        assert!(!j["changes"].as_array().unwrap().is_empty());
        assert_eq!(j["flag"], CONSENT_FLAG);
    }
}
