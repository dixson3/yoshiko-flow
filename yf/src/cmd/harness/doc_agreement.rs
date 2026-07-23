//! Assert-agreement between the published web install/tune matrices and the
//! **code oracle** (REQ-YF-TUNE-025).
//!
//! Mirrors the [`super::drift`] `REQ-YF-TUNE-008` doc-agreement pattern: the docs
//! (`web/content/pages/install.md`, `web/content/pages/harness-tune.md`) are read
//! via an `env!("CARGO_MANIFEST_DIR")`-relative path and diffed against a code
//! oracle. Here the oracle is the **install descriptor table**
//! ([`crate::harness_desc::DESCRIPTORS`]), the **config profiles**
//! ([`super::profile`] — `surface_dir` / `settings_filename` /
//! `settings_local_filename` / `format`), and the **rule-target map**
//! ([`super::managed_block::RULE_TARGETS`]).
//!
//! **Code is the oracle; the doc is the checked artifact.** The check asserts the
//! plan's **structural invariants** (descriptor subpaths; profile filename fields;
//! rule-target subpaths) rather than env-resolved absolute paths, scoped to the
//! no-`--target` matrix: every shipped subpath / filename / rule-target the code
//! derives must appear as a substring in the corresponding published matrix. A
//! missing row / wrong path / wrong file fails the test, and the `Divergence` names
//! exactly what diverged. The comparison matches on the meaningful path/filename
//! substring (not exact table whitespace), so markdown reflow does not false-fail
//! while a genuinely wrong or missing path still does.

#![allow(dead_code)]

use crate::harness_desc::DESCRIPTORS;

use super::managed_block::{RuleTargetKind, RULE_TARGETS};
use super::profile::load_profile;
use super::settings::SettingsFormat;

/// A doc↔code divergence: something the code oracle derives that the published
/// matrix fails to state. Each variant names exactly what diverged.
#[derive(Debug, PartialEq, Eq)]
// Every variant names a matrix entry that is *missing*; the `Missing` postfix is
// the load-bearing semantics of a doc↔code divergence, not redundant noise.
#[allow(clippy::enum_variant_names)]
pub enum Divergence {
    /// An install-descriptor skills subpath absent from the install matrix.
    InstallSubpathMissing {
        harness: &'static str,
        scope: &'static str,
        subpath: &'static str,
    },
    /// A harness's skill-name transform label absent from the install matrix.
    InstallTransformMissing {
        harness: &'static str,
        label: &'static str,
    },
    /// A config profile's settings filename field absent from the tune matrix.
    ConfigFilenameMissing {
        harness: String,
        field: &'static str,
        filename: String,
    },
    /// A config profile's `surface_dir` absent from the tune matrix.
    ConfigSurfaceMissing { harness: String, surface: String },
    /// A config profile's format label absent from the tune matrix.
    ConfigFormatMissing {
        harness: String,
        format: &'static str,
    },
    /// A rule-target subpath absent from the tune matrix.
    RuleTargetMissing {
        harness: &'static str,
        scope: &'static str,
        path: String,
    },
    /// The tune matrix fails to document Pi config as deferred.
    PiConfigDeferralMissing,
    /// The tune matrix fails to state Pi's verified rule target.
    PiVerifiedTargetMissing { path: &'static str },
}

/// The format label the tune doc prints for a [`SettingsFormat`].
fn format_label(f: SettingsFormat) -> &'static str {
    match f {
        SettingsFormat::Json => "JSON",
        SettingsFormat::Toml => "TOML",
    }
}

/// The `<surface>/<leaf>` relative rule-target subpath for a target kind — the
/// structural invariant the tune matrix must state (not an env-resolved absolute).
fn rule_target_subpath(surface: &str, kind: RuleTargetKind) -> String {
    let leaf = match kind {
        RuleTargetKind::RulesDir => "rules",
        RuleTargetKind::AgentsMd => "AGENTS.md",
        RuleTargetKind::AppendSystem => "APPEND_SYSTEM.md",
    };
    format!("{surface}/{leaf}")
}

/// Check the **install matrix** doc against the descriptor-table oracle. Every
/// shipped descriptor's user + project skills subpath (and pi's name-transform
/// label) must appear as a substring in `doc`.
pub fn check_install(doc: &str) -> Vec<Divergence> {
    let mut out = Vec::new();
    for d in DESCRIPTORS {
        if !doc.contains(d.user_subpath) {
            out.push(Divergence::InstallSubpathMissing {
                harness: d.id,
                scope: "user",
                subpath: d.user_subpath,
            });
        }
        if !doc.contains(d.project_subpath) {
            out.push(Divergence::InstallSubpathMissing {
                harness: d.id,
                scope: "project",
                subpath: d.project_subpath,
            });
        }
        if let Some(t) = d.name_transform {
            if !doc.contains(t.label()) {
                out.push(Divergence::InstallTransformMissing {
                    harness: d.id,
                    label: t.label(),
                });
            }
        }
    }
    out
}

/// Check the **tune matrix** doc against the profile + rule-target oracle:
///
/// - every config profile's `settings_filename` AND `settings_local_filename` AND
///   `surface_dir` AND format label must appear;
/// - every rule-target's `<surface>/<leaf>` subpath (user, and pi's distinct
///   project surface) must appear;
/// - Pi config must be documented as deferred, and Pi's verified `.pi/agent/AGENTS.md`
///   rule target must appear.
pub fn check_tune(doc: &str) -> Vec<Divergence> {
    let mut out = Vec::new();

    // Config profiles: derive filename/surface/format from every shipped profile.
    for d in DESCRIPTORS {
        let Some(p) = load_profile(d.id).expect("profile load must not error") else {
            continue; // pi / agents ship no config profile.
        };
        for (field, filename) in [
            ("settings_filename", &p.settings_filename),
            ("settings_local_filename", &p.settings_local_filename),
        ] {
            if !doc.contains(filename.as_str()) {
                out.push(Divergence::ConfigFilenameMissing {
                    harness: p.harness.clone(),
                    field,
                    filename: filename.clone(),
                });
            }
        }
        if !doc.contains(p.surface_dir.as_str()) {
            out.push(Divergence::ConfigSurfaceMissing {
                harness: p.harness.clone(),
                surface: p.surface_dir.clone(),
            });
        }
        let fmt = format_label(p.format);
        if !doc.contains(fmt) {
            out.push(Divergence::ConfigFormatMissing {
                harness: p.harness.clone(),
                format: fmt,
            });
        }
    }

    // Rule targets: derive the structural subpath per harness × scope.
    for t in RULE_TARGETS {
        let user = rule_target_subpath(t.surface_dir, t.kind);
        if !doc.contains(&user) {
            out.push(Divergence::RuleTargetMissing {
                harness: t.harness,
                scope: "user",
                path: user,
            });
        }
        if let Some(proj_surface) = t.project_surface_dir {
            let proj = rule_target_subpath(proj_surface, t.kind);
            if !doc.contains(&proj) {
                out.push(Divergence::RuleTargetMissing {
                    harness: t.harness,
                    scope: "project",
                    path: proj,
                });
            }
        }
    }

    // Pi config deferral must be documented.
    if !doc.to_lowercase().contains("deferred") {
        out.push(Divergence::PiConfigDeferralMissing);
    }

    // Pi's verified rule target must be stated explicitly.
    const PI_VERIFIED: &str = ".pi/agent/AGENTS.md";
    if !doc.contains(PI_VERIFIED) {
        out.push(Divergence::PiVerifiedTargetMissing { path: PI_VERIFIED });
    }

    out
}

#[cfg(test)]
mod tests {
    use super::*;

    fn read_doc(relpath: &str) -> String {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join(relpath);
        std::fs::read_to_string(&path)
            .unwrap_or_else(|e| panic!("cannot read {}: {e}", path.display()))
    }

    fn install_doc() -> String {
        read_doc("web/content/pages/install.md")
    }

    fn tune_doc() -> String {
        read_doc("web/content/pages/harness-tune.md")
    }

    // REQ-YF-TUNE-025: the published install matrix in web/content/pages/install.md
    // agrees with the shipped descriptor table — every harness's user + project
    // skills subpath and pi's name-transform label appear. Fails on any divergence
    // (missing row / wrong path).
    #[test]
    fn install_matrix_agrees_with_descriptor_table() {
        let doc = install_doc();
        let divergences = check_install(&doc);
        assert!(
            divergences.is_empty(),
            "install matrix drifted from the descriptor table (harness_desc.rs):\n{divergences:#?}\n\n\
             Fix web/content/pages/install.md (the CODE is the oracle) so every shipped \
             subpath appears."
        );
    }

    // REQ-YF-TUNE-025: the published tune matrix in web/content/pages/harness-tune.md
    // agrees with the config profiles (surface_dir / settings_filename /
    // settings_local_filename / format) and the rule-target map — every config
    // filename/surface, every rule-target subpath, the Pi config deferral, and Pi's
    // verified target appear. Fails on any divergence.
    #[test]
    fn tune_matrix_agrees_with_profiles_and_rule_targets() {
        let doc = tune_doc();
        let divergences = check_tune(&doc);
        assert!(
            divergences.is_empty(),
            "tune matrix drifted from the profiles / rule-target map:\n{divergences:#?}\n\n\
             Fix web/content/pages/harness-tune.md (the CODE is the oracle) so every \
             derived filename / surface / rule target appears."
        );
    }

    // REQ-YF-TUNE-025 (Scope guard): both docs really exist and the code oracle is
    // non-empty — a vacuous all-green pass (e.g. an empty descriptor table) would be a
    // false negative.
    #[test]
    fn oracle_is_non_vacuous() {
        assert!(
            !DESCRIPTORS.is_empty(),
            "descriptor table must be non-empty"
        );
        assert!(
            !RULE_TARGETS.is_empty(),
            "rule-target map must be non-empty"
        );
        assert!(
            DESCRIPTORS
                .iter()
                .any(|d| load_profile(d.id).unwrap().is_some()),
            "at least one harness must ship a config profile"
        );
    }

    // REQ-YF-TUNE-025 (negative guard): feed a deliberately WRONG doc and assert the
    // checker REPORTS the divergence — proving the agreement test can actually fail,
    // not just pass vacuously (mirrors drift.rs::diff_flags_injected_mismatch).
    #[test]
    fn check_install_flags_a_wrong_subpath() {
        // Take the real doc and corrupt claude-code's user subpath. The descriptor
        // says `.claude/skills`; rewrite it to a bogus dir so the substring is gone.
        let doc = install_doc().replace(".claude/skills", ".WRONG/skills");
        let divergences = check_install(&doc);
        assert!(
            divergences.iter().any(|d| matches!(
                d,
                Divergence::InstallSubpathMissing { harness, subpath, .. }
                    if *harness == "claude-code" && *subpath == ".claude/skills"
            )),
            "expected an InstallSubpathMissing for claude-code `.claude/skills`, got {divergences:#?}"
        );
    }

    // REQ-YF-TUNE-025 (negative guard): a tune doc missing a config filename and a
    // rule target is flagged — the checker names the diverged harness/field.
    #[test]
    fn check_tune_flags_wrong_filename_and_rule_target() {
        // Drop codex's config.toml filename and pi's verified rule target.
        let doc = tune_doc()
            .replace("config.toml", "config.WRONG")
            .replace(".pi/agent/AGENTS.md", ".pi/agent/WRONG.md");
        let divergences = check_tune(&doc);
        assert!(
            divergences.iter().any(|d| matches!(
                d,
                Divergence::ConfigFilenameMissing { harness, filename, .. }
                    if harness == "codex" && filename == "config.toml"
            )),
            "expected a ConfigFilenameMissing for codex `config.toml`, got {divergences:#?}"
        );
        assert!(
            divergences
                .iter()
                .any(|d| matches!(d, Divergence::PiVerifiedTargetMissing { .. })),
            "expected a PiVerifiedTargetMissing, got {divergences:#?}"
        );
    }

    // REQ-YF-TUNE-025 (negative guard): a tune doc that omits the Pi config deferral
    // is flagged.
    #[test]
    fn check_tune_flags_missing_pi_deferral() {
        // Strip every "deferred"/"defer" token so the deferral is undocumented.
        let doc = tune_doc()
            .replace("deferred", "removed")
            .replace("DEFERRED", "REMOVED");
        let divergences = check_tune(&doc);
        assert!(
            divergences.contains(&Divergence::PiConfigDeferralMissing),
            "expected a PiConfigDeferralMissing, got {divergences:#?}"
        );
    }
}
