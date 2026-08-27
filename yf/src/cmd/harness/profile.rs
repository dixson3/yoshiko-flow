//! The embedded, machine-readable harness settings profile (REQ-YF-TUNE-001).
//!
//! A profile is the **single source of truth** for a harness's recommended yf
//! baseline: each [`Entry`] pins a JSON `path`, its recommended `value`, its
//! `kind` (scalar vs set-valued merge semantics), and a one-line `rationale`.
//! Boolean **polarity** lives in the value itself (mixed: `disable*` keys are
//! `true`, `*Enabled` off-switches are `false`), so it can never be hand-fumbled.
//!
//! ## Separate embed root (deliberate)
//!
//! Profiles are embedded from `yf/profiles/`, a **distinct** rust-embed root — NOT
//! under `../skills`. The skills embed ([`crate::embed`]) treats every top-level
//! directory as a skill and feeds per-skill tree hashing / integrity markers; a
//! profile dir there would surface as a bogus skill and pollute that logic. The
//! two roots are intentionally independent.

use std::collections::BTreeSet;

use anyhow::{Context, Result};
use rust_embed::RustEmbed;
use serde::Deserialize;

/// The embedded `profiles/` tree (paths relative to `profiles/`). A **separate**
/// embed root from [`crate::embed`] (`../skills`) — see the module docs.
#[derive(RustEmbed)]
#[folder = "profiles"]
struct Profiles;

/// Merge semantics for a profile entry.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Kind {
    /// A scalar value (bool / string / number): **add-missing**, and an existing
    /// different value is a reported conflict (overwritten only with `--force`).
    Scalar,
    /// An array treated as a **set**: **non-destructive union** — add the profile's
    /// missing elements, never remove an existing one.
    Set,
}

/// One recommended settings entry.
#[derive(Debug, Clone, Deserialize)]
pub struct Entry {
    /// Dot-delimited JSON path, e.g. `permissions.deny`, `todoFeatureEnabled`.
    pub path: String,
    /// Scalar vs set-valued merge semantics.
    pub kind: Kind,
    /// The recommended value (polarity encoded here — `true`/`false`/string/array).
    pub value: serde_json::Value,
    /// One-line human rationale (mirrors the doc reference-baseline comment).
    /// Surfaced by the `yf doctor` drift axis (Epic 4).
    #[allow(dead_code)]
    pub rationale: String,
    /// Does applying this entry **materially escalate the operator's security
    /// posture**? (`REQ-YF-TUNE-001`, plan-042 D-R.)
    ///
    /// Optional, defaulting to `false`, so every pre-existing entry and profile
    /// file stays valid unchanged. When `true`, the `REQ-YF-SELF-008` consent gate
    /// requires an explicit consent flag before the install-time sync may apply it.
    ///
    /// **Profile-declared, not key-path-matched.** A syntactic `permissions.*`
    /// prefix test is claude-code-specific: the same class of lever is
    /// `approval_policy = "never"` on codex and `permission.* = "allow"` on
    /// opencode, neither of which matches that prefix — so a prefix test would
    /// auto-apply a blanket-allow on two of the three config-bearing harnesses
    /// with no consent. Declaring it per entry is self-maintaining: a new lever
    /// declares its own requirement instead of relying on a prefix that only ever
    /// matched one harness.
    #[serde(default)]
    pub consent_required: bool,
}

impl Entry {
    /// The dot-path split into segments (`permissions.deny` → `["permissions",
    /// "deny"]`). Segments are always non-empty for a well-formed profile.
    pub fn segments(&self) -> Vec<&str> {
        self.path.split('.').collect()
    }
}

/// A harness settings profile: the recommended baseline plus the harness's file
/// layout (surface dir, settings filenames) and the two never-touch anchors
/// (`agent_tool`, `hook_preserve_key`).
#[derive(Debug, Clone, Deserialize)]
pub struct Profile {
    /// Harness key, e.g. `claude-code`.
    pub harness: String,
    /// Dotted surface directory, e.g. `.claude`.
    pub surface_dir: String,
    /// Committed/user settings filename, e.g. `settings.json`.
    pub settings_filename: String,
    /// Personal, gitignored project settings filename, e.g. `settings.local.json`.
    pub settings_local_filename: String,
    /// On-disk format of the settings/config file (REQ-YF-TUNE-014). Deserialized
    /// from the embedded profile JSON's `format` key (`"json"` | `"toml"`);
    /// **defaults to [`SettingsFormat::Json`]** when the key is absent, so the
    /// existing `claude-code.json` (no `format` key) stays JSON. Selects the
    /// read/merge/write adapter in [`super::run_core`].
    #[serde(default)]
    pub format: super::settings::SettingsFormat,
    /// Top-level key whose value tune must preserve untouched (the `bd setup
    /// claude` `SessionStart` hook block lives under this key). Preservation is
    /// automatic (tune writes only its own profile keys); this documents the
    /// contract and is read by the doctor drift axis (Epic 4).
    #[allow(dead_code)]
    pub hook_preserve_key: String,
    /// The tool that must NEVER be denied/disabled (every yf agent fans out
    /// through it) — the `Agent`-never-denied invariant (REQ-YF-TUNE-005).
    pub agent_tool: String,
    /// Every config file this harness ITSELF reads, **highest precedence first**
    /// (`REQ-YF-TUNE-030`, added plan-054 / EXP-003).
    ///
    /// # The read set is DECOUPLED from the write target
    ///
    /// `yf` writes exactly one config file per harness — [`Self::settings_filename`] — and that
    /// is unchanged. But every **audit-class** consumer (`yf doctor`, the settings-drift axis,
    /// tune's pre-write inspection) must read *every* layer the harness obeys, not the write
    /// target alone.
    ///
    /// Measured (EXP-003): **opencode reads both `opencode.json` and `opencode.jsonc`, and
    /// `.jsonc` has the HIGHER precedence.** Today's agreement between what yf writes and what
    /// opencode actually obeys is therefore **coincidence**. An audit whose read set is
    /// narrower than the harness's own reports a confident green over a higher-precedence
    /// layer it cannot see.
    ///
    /// EXP-003 also **refuted** the scoping hypothesis that named `drift.rs`: that module never
    /// opens a harness config file at all.
    ///
    /// Defaults to empty, which every consumer must treat as "fall back to
    /// [`Self::settings_filename`] alone" — so a profile that has not declared its layers keeps
    /// today's behaviour rather than silently reading nothing.
    #[serde(default)]
    pub settings_read_layers: Vec<String>,
    /// The recommended entries.
    pub entries: Vec<Entry>,
}

impl Profile {
    /// The ordered read set for audit-class consumers (`REQ-YF-TUNE-030`).
    ///
    /// Falls back to `[settings_filename]` when the profile declares no layers, so an
    /// undeclared profile keeps today's single-file behaviour instead of reading nothing.
    pub fn read_layers(&self) -> Vec<String> {
        if self.settings_read_layers.is_empty() {
            vec![self.settings_filename.clone()]
        } else {
            self.settings_read_layers.clone()
        }
    }

    /// The set-valued `permissions.deny` entry, if the profile has one. Used by
    /// the profile tests and the `yf doctor` Agent-denied check (Epic 4).
    #[allow(dead_code)]
    pub fn deny_entry(&self) -> Option<&Entry> {
        self.entries
            .iter()
            .find(|e| e.kind == Kind::Set && e.path.ends_with(".deny"))
    }
}

/// Load the embedded profile for `harness` (e.g. `claude-code`).
///
/// Returns `Ok(None)` for an **unknown** harness (no embedded `<harness>.json`) —
/// the clean-refusal path (REQ-YF-TUNE-002). `Err` is reserved for a *present but
/// malformed* embedded profile (a build-time authoring bug, not operator input).
pub fn load_profile(harness: &str) -> Result<Option<Profile>> {
    let relpath = format!("{harness}.json");
    let Some(file) = Profiles::get(&relpath) else {
        return Ok(None);
    };
    let profile: Profile = serde_json::from_slice(&file.data)
        .with_context(|| format!("embedded profile {relpath} is malformed"))?;
    Ok(Some(profile))
}

/// The harness keys with an embedded profile (basenames minus `.json`), sorted.
/// The clean-refusal message lists these as the available harnesses.
pub fn available_harnesses() -> Vec<String> {
    let mut names: BTreeSet<String> = BTreeSet::new();
    for p in Profiles::iter() {
        if let Some(stem) = p.strip_suffix(".json") {
            names.insert(stem.to_string());
        }
    }
    names.into_iter().collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    /// REQ-YF-TUNE-001 (plan-042 D-R / Issue 3.0): exactly the four
    /// consent-bearing entries declare `consent_required: true`, one per
    /// config-bearing harness path the plan names — and every other entry defaults
    /// to `false`.
    ///
    /// Pinned as an exact set in both directions. Dropping a flag would silently
    /// re-open the unconsented-write hole; adding one elsewhere would start
    /// demanding consent for a benign key.
    #[test]
    fn consent_required_is_set_on_exactly_the_four_autonomy_levers() {
        let expected: &[(&str, &[&str])] = &[
            (
                "claude-code",
                &[
                    "permissions.defaultMode",
                    "skipDangerousModePermissionPrompt",
                ],
            ),
            ("codex", &["approval_policy"]),
            ("opencode", &["permission.*"]),
        ];

        let mut total = 0;
        for (harness, paths) in expected {
            let p = load_profile(harness)
                .expect("load must not error")
                .unwrap_or_else(|| panic!("{harness} profile must be embedded"));

            let flagged: Vec<&str> = p
                .entries
                .iter()
                .filter(|e| e.consent_required)
                .map(|e| e.path.as_str())
                .collect();
            assert_eq!(
                flagged, *paths,
                "{harness}: consent_required set on the wrong entries"
            );
            total += flagged.len();

            // Every OTHER entry defaults to false — the field is opt-in, so an
            // absent key must never read as "requires consent".
            for e in &p.entries {
                if !paths.contains(&e.path.as_str()) {
                    assert!(
                        !e.consent_required,
                        "{harness}: {} must not require consent",
                        e.path
                    );
                }
            }
        }
        assert_eq!(total, 4, "exactly four consent-bearing entries ship");
    }

    /// REQ-YF-TUNE-001: `consent_required` is **optional** with a `false` default,
    /// so a profile entry written before the field existed still deserializes.
    /// This is what makes the schema change backward-compatible.
    #[test]
    fn consent_required_defaults_to_false_when_absent() {
        let e: Entry = serde_json::from_str(
            r#"{"path":"someKey","kind":"scalar","value":true,"rationale":"x"}"#,
        )
        .expect("an entry without consent_required must still parse");
        assert!(!e.consent_required);
    }

    // REQ-YF-TUNE-001: the machine-readable profile loads from the embedded
    // separate root, and every entry carries path / value / kind / rationale with
    // polarity encoded in the value.
    #[test]
    fn claude_code_profile_loads_and_is_well_formed() {
        let p = load_profile("claude-code")
            .expect("load must not error")
            .expect("claude-code profile must be embedded");
        assert_eq!(p.harness, "claude-code");
        assert_eq!(p.surface_dir, ".claude");
        assert_eq!(p.settings_filename, "settings.json");
        assert_eq!(p.settings_local_filename, "settings.local.json");
        assert_eq!(p.agent_tool, "Agent");
        assert!(!p.entries.is_empty(), "profile must have entries");

        for e in &p.entries {
            assert!(!e.path.is_empty(), "entry path must be non-empty");
            assert!(
                !e.rationale.is_empty(),
                "entry {} needs a rationale",
                e.path
            );
            assert!(
                e.segments().iter().all(|s| !s.is_empty()),
                "entry {} has an empty path segment",
                e.path
            );
        }
    }

    // REQ-YF-TUNE-001: polarity is encoded in the value — the mixed disable*=true
    // vs *Enabled=false convention holds in the data, not in open code.
    #[test]
    fn polarity_is_encoded_in_values() {
        let p = load_profile("claude-code").unwrap().unwrap();
        let by_path = |path: &str| {
            p.entries
                .iter()
                .find(|e| e.path == path)
                .unwrap_or_else(|| panic!("missing entry {path}"))
                .value
                .clone()
        };
        // disable* switches are `true` to disable.
        assert_eq!(by_path("disableWorkflows"), serde_json::json!(true));
        assert_eq!(by_path("disableBundledSkills"), serde_json::json!(true));
        // *Enabled off-switches are `false`.
        assert_eq!(by_path("todoFeatureEnabled"), serde_json::json!(false));
        assert_eq!(by_path("autoMemoryEnabled"), serde_json::json!(false));
        // A string scalar.
        assert_eq!(
            by_path("askUserQuestionTimeout"),
            serde_json::json!("never")
        );
    }

    // REQ-YF-TUNE-001: kinds are correctly assigned — permissions.deny is a set,
    // and Agent is deliberately absent from it (the never-denied invariant source).
    #[test]
    fn deny_is_set_valued_and_omits_agent() {
        let p = load_profile("claude-code").unwrap().unwrap();
        let deny = p
            .deny_entry()
            .expect("profile must have a permissions.deny set");
        assert_eq!(deny.kind, Kind::Set);
        let arr = deny.value.as_array().expect("deny value is an array");
        assert!(!arr.is_empty());
        assert!(
            !arr.iter().any(|v| v == &serde_json::json!("Agent")),
            "Agent must NEVER be in the profile deny set"
        );
        // Representative competing-tool denies are present.
        for tool in ["TaskCreate", "EnterPlanMode", "NotebookEdit"] {
            assert!(
                arr.iter().any(|v| v == &serde_json::json!(tool)),
                "deny set missing {tool}"
            );
        }
    }

    // REQ-YF-TUNE-001: an unknown harness resolves to None (no embedded profile) —
    // the loader signal the command turns into a clean refusal, distinct from a
    // malformed-profile Err. The command-level refusal is tagged in mod.rs.
    #[test]
    fn unknown_harness_is_none() {
        // pi ships NO config profile (REQ-YF-TUNE-017 — Pi config deferral).
        assert!(load_profile("pi").unwrap().is_none());
        assert!(load_profile("nonesuch").unwrap().is_none());
        // The three harnesses with an embedded CONFIG profile, sorted.
        assert_eq!(
            available_harnesses(),
            vec![
                "claude-code".to_string(),
                "codex".to_string(),
                "opencode".to_string(),
            ]
        );
    }

    // REQ-YF-TUNE-015: the codex TOML config profile loads, is well-formed, and its
    // format is Toml so `run_core` dispatches to the delta-replay adapter. Codex has
    // no native-tool deny surface, so it ships no set entry — the Agent-never-denied
    // invariant holds structurally (no deny set can carry Agent).
    #[test]
    fn codex_profile_loads_toml_and_is_well_formed() {
        let p = load_profile("codex")
            .expect("load must not error")
            .expect("codex profile must be embedded");
        assert_eq!(p.harness, "codex");
        assert_eq!(p.surface_dir, ".codex");
        assert_eq!(p.settings_filename, "config.toml");
        assert_eq!(p.settings_local_filename, "config.toml");
        assert_eq!(p.format, super::super::settings::SettingsFormat::Toml);
        assert_eq!(p.agent_tool, "Agent");
        assert!(!p.entries.is_empty());
        for e in &p.entries {
            assert!(!e.path.is_empty());
            assert!(
                !e.rationale.is_empty(),
                "entry {} needs a rationale",
                e.path
            );
            assert!(e.segments().iter().all(|s| !s.is_empty()));
        }
        // Honest set: all scalar codex keys; no fabricated deny/set surface.
        assert!(
            p.deny_entry().is_none(),
            "codex has no native-tool deny surface — must ship no deny set"
        );
        assert!(
            p.entries.iter().all(|e| e.kind == Kind::Scalar),
            "codex profile is scalar-only"
        );
        // The evidence-backed key set (real codex config.toml keys).
        for key in [
            "approval_policy",
            "tui.notifications",
            "project_doc_max_bytes",
        ] {
            assert!(
                p.entries.iter().any(|e| e.path == key),
                "codex profile missing {key}"
            );
        }
    }

    // REQ-YF-TUNE-016: the opencode JSON config profile loads and its format is Json
    // so tune reuses the existing serde_json merge/write path unchanged.
    #[test]
    fn opencode_profile_loads_json() {
        let p = load_profile("opencode")
            .expect("load must not error")
            .expect("opencode profile must be embedded");
        assert_eq!(p.harness, "opencode");
        assert_eq!(p.surface_dir, ".config/opencode");
        assert_eq!(p.settings_filename, "opencode.json");
        assert_eq!(p.format, super::super::settings::SettingsFormat::Json);
        assert!(!p.entries.is_empty());
        for e in &p.entries {
            assert!(
                !e.rationale.is_empty(),
                "entry {} needs a rationale",
                e.path
            );
        }
        for key in ["permission.*", "share"] {
            assert!(
                p.entries.iter().any(|e| e.path == key),
                "opencode profile missing {key}"
            );
        }
    }

    // REQ-YF-TUNE-017: Pi config tuning is deferred — NO `pi` config profile ships,
    // so the loader returns None (the clean-refusal signal) while pi's skills+rules
    // remain supported elsewhere. available_harnesses (the list a refusal surfaces)
    // names the three config harnesses and never pi.
    #[test]
    fn pi_has_no_config_profile() {
        assert!(
            load_profile("pi").unwrap().is_none(),
            "no pi CONFIG profile may ship (research-002 Q6: pi config surface [uncertain])"
        );
        let available = available_harnesses();
        assert!(!available.contains(&"pi".to_string()));
        assert!(available.contains(&"claude-code".to_string()));
        assert!(available.contains(&"codex".to_string()));
        assert!(available.contains(&"opencode".to_string()));
    }

    // REQ-YF-TUNE-030 (plan-054 / EXP-003). Named by SC10, so the criterion and the test
    // cannot drift apart — a criterion naming a test that does not exist is satisfied by a
    // zero-match `cargo test` filter, which exits 0.
    #[test]
    fn opencode_read_layers_surface_shadowed_keys() {
        let p = load_profile("opencode")
            .expect("opencode profile must load")
            .expect("opencode profile must be embedded");

        // The DECLARED read set: both files opencode reads, `.jsonc` FIRST.
        assert_eq!(
            p.read_layers(),
            vec!["opencode.jsonc".to_string(), "opencode.json".to_string()],
            "opencode reads BOTH files and .jsonc has the HIGHER precedence; an audit that \
             consults .json first reports the value the harness does not obey"
        );
        // The WRITE target is unchanged — the read set is decoupled from it, not a rename.
        assert_eq!(p.settings_filename, "opencode.json");

        // A profile that declares nothing keeps today's single-file behaviour rather than
        // reading nothing — the fallback that makes this change safe to land incrementally.
        let cc = load_profile("claude-code").unwrap().unwrap();
        assert_eq!(cc.read_layers(), vec![cc.settings_filename.clone()]);

        // The SHADOW is surfaced: with a higher-precedence layer present on disk, the
        // shadowing set is non-empty and names that layer. This is what the tune-time warning
        // and the doctor axis both key on.
        use super::super::settings::{shadowing_layers_at, TuneScope};
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path();
        let surface = home.join(&p.surface_dir);
        std::fs::create_dir_all(&surface).unwrap();
        std::fs::write(surface.join("opencode.json"), "{}").unwrap();

        assert!(
            shadowing_layers_at(&p, TuneScope::User, home, home).is_empty(),
            "with no .jsonc present nothing shadows the write target"
        );

        std::fs::write(surface.join("opencode.jsonc"), "{}").unwrap();
        let shadows = shadowing_layers_at(&p, TuneScope::User, home, home);
        assert_eq!(
            shadows.len(),
            1,
            "the .jsonc layer must be reported as shadowing"
        );
        assert!(
            shadows[0].ends_with("opencode.jsonc"),
            "the shadowing layer must be NAMED, not merely counted: {shadows:?}"
        );
    }
}
