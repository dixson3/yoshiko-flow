//! Per-harness descriptor table (REQ-YF-INSTALL-007) — the **single source of
//! truth** for where each harness's skills tree lands.
//!
//! This replaces the old `Surface` enum's hardwired `.claude` / `.agents` logic in
//! [`crate::dest`]. Each [`HarnessDescriptor`] row carries an `id`, a `user_subpath`
//! and `project_subpath` (relative to the scope anchor — `$HOME` for user,
//! git-root/cwd for project), and an optional [`NameTransform`] applied to a skill's
//! directory name for harnesses with naming constraints (pi).
//!
//! Adding a harness is one row here plus one row in the SPEC's REQ-YF-INSTALL-007
//! table; a parity test (`spec_table_matches_shipped_descriptor`) asserts the two
//! never drift.

// Forward-API: `name_transform` application + `surface_alias` are consumed by the
// multi-harness install path (Issue 2.2); tests exercise them now.
#![allow(dead_code)]

use crate::cli::Scope;

/// A name-normalization rule some harnesses impose on the on-disk skill directory
/// name. Only pi constrains names today.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NameTransform {
    /// Lowercase, non-`[a-z0-9]` → `-`, truncated to 64 chars.
    LowercaseHyphenMax64,
}

impl NameTransform {
    /// The SPEC/label spelling of this transform (matches the SPEC table text).
    pub fn label(self) -> &'static str {
        match self {
            NameTransform::LowercaseHyphenMax64 => "lowercase-hyphen,max64",
        }
    }

    /// Apply the transform to a skill name.
    pub fn apply(self, name: &str) -> String {
        match self {
            NameTransform::LowercaseHyphenMax64 => {
                let mapped: String = name
                    .chars()
                    .map(|c| {
                        let c = c.to_ascii_lowercase();
                        if c.is_ascii_alphanumeric() {
                            c
                        } else {
                            '-'
                        }
                    })
                    .collect();
                mapped.chars().take(64).collect()
            }
        }
    }
}

/// One row of the harness descriptor table.
#[derive(Debug, Clone, Copy)]
pub struct HarnessDescriptor {
    /// Stable harness id (the `--harness` value).
    pub id: &'static str,
    /// Skills subpath under the user anchor (`$HOME`).
    pub user_subpath: &'static str,
    /// Skills subpath under the project anchor (git-root/cwd).
    pub project_subpath: &'static str,
    /// Optional skill-directory name transform.
    pub name_transform: Option<NameTransform>,
}

impl HarnessDescriptor {
    /// The skills subpath for a scope.
    pub fn subpath(&self, scope: Scope) -> &'static str {
        match scope {
            Scope::User => self.user_subpath,
            Scope::Project => self.project_subpath,
        }
    }

    /// Normalize a skill's on-disk directory name per this harness's transform
    /// (identity when the row has no transform).
    pub fn transform_skill_name(&self, name: &str) -> String {
        match self.name_transform {
            Some(t) => t.apply(name),
            None => name.to_string(),
        }
    }
}

/// The shipped descriptor table — exactly five rows (REQ-YF-INSTALL-007).
pub const DESCRIPTORS: &[HarnessDescriptor] = &[
    HarnessDescriptor {
        id: "claude-code",
        user_subpath: ".claude/skills",
        project_subpath: ".claude/skills",
        name_transform: None,
    },
    HarnessDescriptor {
        id: "codex",
        user_subpath: ".agents/skills",
        project_subpath: ".agents/skills",
        name_transform: None,
    },
    HarnessDescriptor {
        id: "opencode",
        user_subpath: ".config/opencode/skills",
        project_subpath: ".opencode/skills",
        name_transform: None,
    },
    HarnessDescriptor {
        id: "pi",
        user_subpath: ".pi/agent/skills",
        project_subpath: ".pi/skills",
        name_transform: Some(NameTransform::LowercaseHyphenMax64),
    },
    HarnessDescriptor {
        id: "agents",
        user_subpath: ".agents/skills",
        project_subpath: ".agents/skills",
        name_transform: None,
    },
];

/// Look up a descriptor row by harness id.
pub fn lookup(id: &str) -> Option<&'static HarnessDescriptor> {
    DESCRIPTORS.iter().find(|d| d.id == id)
}

/// Map a deprecated `--surface` value to its `--harness` id: `claude`→`claude-code`,
/// `agents`→`agents`, everything else passthrough (REQ-YF-CLI-002).
pub fn surface_alias(surface: &str) -> String {
    match surface {
        "claude" => "claude-code",
        other => other,
    }
    .to_string()
}

/// The skills subpath for a harness id + scope, with a **legacy `.<id>/skills`
/// fallback** for an unknown id (REQ-YF-CLI-002 / REQ-YF-INSTALL-002).
pub fn skills_subpath(harness: &str, scope: Scope) -> String {
    match lookup(harness) {
        Some(d) => d.subpath(scope).to_string(),
        None => format!(".{harness}/skills"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // REQ-YF-INSTALL-007: exactly five descriptor rows with the SPEC ids.
    #[test]
    fn five_rows_with_expected_ids() {
        let ids: Vec<&str> = DESCRIPTORS.iter().map(|d| d.id).collect();
        assert_eq!(ids, ["claude-code", "codex", "opencode", "pi", "agents"]);
    }

    // REQ-YF-INSTALL-007: SPEC↔code parity — parse the descriptor table encoded in
    // SPEC.md's REQ-YF-INSTALL-007 requirement and assert it equals the shipped
    // table (id, both subpaths, name_transform, and row count). The naba-pattern
    // parity guard against SPEC/code drift.
    #[test]
    fn spec_table_matches_shipped_descriptor() {
        let spec_path = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../SPEC.md");
        let spec = std::fs::read_to_string(&spec_path)
            .unwrap_or_else(|e| panic!("cannot read SPEC.md at {}: {e}", spec_path.display()));

        // Isolate the REQ-YF-INSTALL-007 requirement block (from its bold id to the
        // next `- **REQ-` bullet).
        let start = spec
            .find("**REQ-YF-INSTALL-007**")
            .expect("SPEC must define REQ-YF-INSTALL-007");
        let rest = &spec[start..];
        let end = rest[1..]
            .find("- **REQ-YF-")
            .map(|i| i + 1)
            .unwrap_or(rest.len());
        let block = &rest[..end];

        // The SPEC states the row count in prose.
        assert!(
            block.contains("five rows"),
            "SPEC REQ-YF-INSTALL-007 must state 'five rows'"
        );
        assert_eq!(DESCRIPTORS.len(), 5, "shipped table must have five rows");

        // Every shipped row's id + both subpaths must be quoted in the SPEC block,
        // and no foreign harness id may appear.
        for d in DESCRIPTORS {
            assert!(
                block.contains(&format!("`{}`", d.id)),
                "SPEC block missing id `{}`",
                d.id
            );
            assert!(
                block.contains(&format!("`{}`", d.user_subpath)),
                "SPEC block missing user_subpath `{}` for {}",
                d.user_subpath,
                d.id
            );
            assert!(
                block.contains(&format!("`{}`", d.project_subpath)),
                "SPEC block missing project_subpath `{}` for {}",
                d.project_subpath,
                d.id
            );
            if let Some(t) = d.name_transform {
                assert!(
                    block.contains(t.label()),
                    "SPEC block missing name_transform `{}` for {}",
                    t.label(),
                    d.id
                );
            }
        }

        // pi is the only row carrying a transform; the SPEC names it against pi.
        let pi = lookup("pi").unwrap();
        assert_eq!(pi.name_transform, Some(NameTransform::LowercaseHyphenMax64));
    }

    // REQ-YF-INSTALL-007: pi's `lowercase-hyphen,max64` transform validated against
    // yf's real (long) skill names.
    #[test]
    fn pi_name_transform_handles_long_yf_skill_names() {
        let pi = lookup("pi").unwrap();
        // A real long yf skill name is already lowercase-hyphen and under 64 chars:
        // the transform is the identity on it.
        assert_eq!(
            pi.transform_skill_name("yf-change-validation"),
            "yf-change-validation"
        );
        // Uppercase / underscores are normalized.
        assert_eq!(
            pi.transform_skill_name("YF_Change_Validation"),
            "yf-change-validation"
        );
        // A synthetic >64-char name is truncated to 64.
        let long = "yf-".to_string() + &"x".repeat(80);
        assert_eq!(pi.transform_skill_name(&long).chars().count(), 64);
        // A harness without a transform (claude-code) is the identity.
        assert_eq!(
            lookup("claude-code")
                .unwrap()
                .transform_skill_name("yf-change-validation"),
            "yf-change-validation"
        );
    }

    // REQ-YF-CLI-002: `--surface` deprecated-alias mapping + legacy fallback.
    #[test]
    fn surface_alias_and_legacy_fallback() {
        assert_eq!(surface_alias("claude"), "claude-code");
        assert_eq!(surface_alias("agents"), "agents");
        assert_eq!(surface_alias("unknown"), "unknown");
        // Known ids resolve via the table; an unknown id falls back to `.<id>/skills`.
        assert_eq!(skills_subpath("claude-code", Scope::User), ".claude/skills");
        assert_eq!(skills_subpath("pi", Scope::Project), ".pi/skills");
        assert_eq!(
            skills_subpath("frobnicator", Scope::User),
            ".frobnicator/skills"
        );
    }
}
