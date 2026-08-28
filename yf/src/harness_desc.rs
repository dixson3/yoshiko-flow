//! Per-harness descriptor table (REQ-YF-INSTALL-007) — the **single source of
//! truth** for where each harness's skills tree lands.
//!
//! This replaces the old `Surface` enum's hardwired `.claude` / `.agents` logic in
//! [`crate::dest`].
//!
//! ## TWO COLUMNS, NOT ONE (plan-055, REQ-YF-INSTALL-007)
//!
//! Each [`HarnessDescriptor`] row carries **two independent destination concerns**, and
//! conflating them is what this split fixes:
//!
//! - the **skills root** (`user_skills_subpath` / `project_skills_subpath`) — where skill
//!   *bodies* are deployed. **Shared wherever a harness reads the shared root.**
//! - the **surface dir** (`user_surface_dir` / `project_surface_dir`) — where that harness's
//!   *config, hooks, extensions and rules aggregate* live. **Always harness-specific.**
//!
//! Before the split there was one column, and the rules directory was derived as the skills
//! dir's **parent**. That was only ever *incidentally* correct: it held because every harness
//! had a private skills root, so the parent of the skills dir happened to be the surface dir.
//! The moment a root is shared it becomes wrong — a shared `.agents/skills` would put pi's
//! rules in `.agents/rules` and collapse four harnesses' rules onto one directory. So the
//! surface dir is now carried explicitly and the rules destination is derived from it.
//!
//! Each row also carries an optional [`NameTransform`] applied to a skill's on-disk directory
//! name, and the two **env-override** columns (`REQ-YF-INSTALL-007`).
//!
//! Adding a harness is one row here plus one row in the SPEC's REQ-YF-INSTALL-007
//! table; a parity test (`spec_table_matches_shipped_descriptor`) asserts the two
//! never drift.

// Forward-API: `name_transform` application + `surface_alias` are consumed by the
// multi-harness install path (Issue 2.2); tests exercise them now.
#![allow(dead_code)]

use crate::cli::Scope;

/// A name-normalization rule a harness could impose on the on-disk skill directory name.
///
/// **NO SHIPPED ROW CARRIES ONE** (plan-055 Issue 2.3). pi was the only row that ever did, and
/// EXP-002 measured pi 0.84.3 loading directories named `Zz_Probe_Name` and
/// `Zz_Probe_Shared_NoName`: pi's name validation is **warn-only**, and only a missing
/// frontmatter `description` is fatal. So the transform was belt-and-braces, not a requirement.
///
/// **Dropping it was a PRECONDITION of the shared-root collapse, not a tidy-up.**
/// `resolved_dests` dedupes by resolved path and keeps the **first** matching harness's row;
/// `deploy_skill` then derives every skill's on-disk `dir_name` from *that one row's*
/// `transform_skill_name`. With pi merged onto the shared root while it alone carried a
/// transform, the shared root's on-disk names would have been **order-dependent on descriptor
/// row order** — benign only incidentally, because yf's own names are already lowercase-hyphen
/// and under 64 characters.
///
/// The type is retained so a future harness that genuinely constrains names can declare one.
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

/// How an env override interacts with the `$HOME`-derived default root.
///
/// **THREE-VALUED, NEVER A BOOLEAN.** Measured (plan-055 EXP-003): `OPENCODE_CONFIG_DIR`
/// **adds** a root while `XDG_CONFIG_HOME`, `CODEX_HOME`, `PI_CODING_AGENT_DIR` and
/// `CLAUDE_CONFIG_DIR` **replace** one. Any logic shaped "if `$VAR` is set, install there
/// *instead*" would under-install for opencode and over-install for the other three.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OverridePrecedence {
    /// The var replaces the `$HOME`-derived default root.
    Replace,
    /// The var adds a root; the default is retained.
    Additive,
}

/// One env override: the var name plus how it composes with the default.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct EnvOverride {
    pub var: &'static str,
    pub precedence: OverridePrecedence,
}

impl EnvOverride {
    pub const fn replace(var: &'static str) -> Self {
        EnvOverride {
            var,
            precedence: OverridePrecedence::Replace,
        }
    }
    pub const fn additive(var: &'static str) -> Self {
        EnvOverride {
            var,
            precedence: OverridePrecedence::Additive,
        }
    }
}

/// One row of the harness descriptor table.
#[derive(Debug, Clone, Copy)]
pub struct HarnessDescriptor {
    /// Stable harness id (the `--harness` value).
    pub id: &'static str,

    // --- the SKILLS ROOT column: where skill bodies land. Shared where the harness reads it.
    /// Skills subpath under the user anchor (`$HOME`).
    pub user_skills_subpath: &'static str,
    /// Skills subpath under the project anchor (git-root/cwd).
    pub project_skills_subpath: &'static str,

    // --- the SURFACE DIR column: config / hooks / extensions / rules. ALWAYS harness-specific.
    /// Surface dir under the user anchor. The rules destination is `<surface_dir>/rules`.
    pub user_surface_dir: &'static str,
    /// Surface dir under the project anchor.
    pub project_surface_dir: &'static str,

    /// Optional skill-directory name transform.
    pub name_transform: Option<NameTransform>,

    /// Env vars that relocate this harness's **surface** dir. A slice because opencode has
    /// **two**, and they are orthogonal rather than competing.
    pub surface_env: &'static [EnvOverride],
    /// Env vars that relocate this harness's **skills** root. Non-empty for `claude-code`
    /// alone after the plan-055 collapse — `.agents/skills` was measured env-immune on codex,
    /// pi and opencode.
    pub skills_env: &'static [EnvOverride],
}

impl HarnessDescriptor {
    /// The **skills** subpath for a scope.
    pub fn skills_subpath(&self, scope: Scope) -> &'static str {
        match scope {
            Scope::User => self.user_skills_subpath,
            Scope::Project => self.project_skills_subpath,
        }
    }

    /// The **surface** dir for a scope — the parent of `rules/`, never derived from the
    /// skills dir.
    pub fn surface_dir(&self, scope: Scope) -> &'static str {
        match scope {
            Scope::User => self.user_surface_dir,
            Scope::Project => self.project_surface_dir,
        }
    }

    /// Deprecated spelling of [`Self::skills_subpath`], kept so the split is a pure refactor
    /// at every call site rather than a rename sweep bundled into a behaviour change.
    pub fn subpath(&self, scope: Scope) -> &'static str {
        self.skills_subpath(scope)
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
///
/// **FOUR of the five rows share one skills root** (`.agents/skills`, both scopes) and each
/// keeps its **own** surface dir. That asymmetry is the plan-055 result in one place: a skills
/// root is shared where the harness agrees to read it; a surface dir never is.
///
/// `claude-code` is the sole private-skills-root row, and it is not an omission. EXP-001
/// measured claude-code 2.1.247: the string `.agents/` occurs **zero times** in the 222 MB
/// binary, the auto-load constant is a hardcoded `[".claude/skills", ".claude/commands"]`, and
/// a headless probe with a skill in `.agents/skills` and a control in `.claude/skills` returned
/// **only the control**, twice. No env var can add a root — all ten `CLAUDE_*SKILL*` vars are
/// disable/telemetry switches, none a path.
pub const DESCRIPTORS: &[HarnessDescriptor] = &[
    HarnessDescriptor {
        id: "claude-code",
        user_skills_subpath: ".claude/skills",
        project_skills_subpath: ".claude/skills",
        user_surface_dir: ".claude",
        project_surface_dir: ".claude",
        name_transform: None,
        surface_env: &[EnvOverride::replace("CLAUDE_CONFIG_DIR")],
        skills_env: &[EnvOverride::replace("CLAUDE_CONFIG_DIR")],
    },
    HarnessDescriptor {
        id: "codex",
        user_skills_subpath: ".agents/skills",
        project_skills_subpath: ".agents/skills",
        user_surface_dir: ".agents",
        project_surface_dir: ".agents",
        name_transform: None,
        surface_env: &[EnvOverride::replace("CODEX_HOME")],
        skills_env: &[],
    },
    HarnessDescriptor {
        id: "opencode",
        // COLLAPSED to the shared root (plan-055 Issue 2.2, #257). opencode reads
        // `~/.agents/skills` with no configuration, and its private `.config/opencode/skills`
        // was measured to be SHADOWED: with one skill planted in three roots, opencode's winner
        // across five identical runs was `.config/opencode` four times and `.agents` once. The
        // loader processes matches with unbounded concurrency and OVERWRITES ON COLLISION, so
        // the winner is whichever async read finishes last — a coin flip per process start,
        // not a preference. Today that is harmless only because every tree comes from one
        // install and is byte-identical; the moment two copies diverge it is a silent,
        // nondeterministic choice between two versions of one skill.
        user_skills_subpath: ".agents/skills",
        project_skills_subpath: ".agents/skills",
        user_surface_dir: ".config/opencode",
        project_surface_dir: ".opencode",
        name_transform: None,
        // TWO vars, orthogonal rather than competing (EXP-003): XDG replaces the config root,
        // OPENCODE_CONFIG_DIR adds one and the default is retained.
        surface_env: &[
            EnvOverride::replace("XDG_CONFIG_HOME"),
            EnvOverride::additive("OPENCODE_CONFIG_DIR"),
        ],
        skills_env: &[],
    },
    HarnessDescriptor {
        id: "pi",
        // COLLAPSED to the shared root (plan-055 Issue 2.2, #257). EXP-002 measured pi 0.84.3
        // loading `~/.agents/skills` in BOTH scopes with no configuration. Unlike opencode, pi
        // is deterministic first-wins — so before the collapse it reliably preferred its own
        // private tree, which is a stale-copy hazard rather than a race.
        user_skills_subpath: ".agents/skills",
        project_skills_subpath: ".agents/skills",
        user_surface_dir: ".pi/agent",
        project_surface_dir: ".pi",
        name_transform: None,
        surface_env: &[EnvOverride::replace("PI_CODING_AGENT_DIR")],
        skills_env: &[],
    },
    HarnessDescriptor {
        id: "agents",
        user_skills_subpath: ".agents/skills",
        project_skills_subpath: ".agents/skills",
        user_surface_dir: ".agents",
        project_surface_dir: ".agents",
        name_transform: None,
        surface_env: &[],
        skills_env: &[],
    },
];

/// The **surface** subpath for a harness id + scope, with a legacy `.<id>` fallback.
pub fn surface_subpath(harness: &str, scope: Scope) -> String {
    match lookup(harness) {
        Some(d) => d.surface_dir(scope).to_string(),
        None => format!(".{harness}"),
    }
}

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

        // Every shipped row's id, BOTH skills subpaths and BOTH surface dirs must be quoted
        // in the SPEC block. Covering only the skills column would leave the surface column —
        // which now determines where every harness's RULES land — governed by nothing.
        for d in DESCRIPTORS {
            assert!(
                block.contains(&format!("`{}`", d.id)),
                "SPEC block missing id `{}`",
                d.id
            );
            for (label, value) in [
                ("user_skills_subpath", d.user_skills_subpath),
                ("project_skills_subpath", d.project_skills_subpath),
                ("user_surface_dir", d.user_surface_dir),
                ("project_surface_dir", d.project_surface_dir),
            ] {
                assert!(
                    block.contains(&format!("`{value}`")),
                    "SPEC block missing {label} `{value}` for {}",
                    d.id
                );
            }
            if let Some(t) = d.name_transform {
                assert!(
                    block.contains(t.label()),
                    "SPEC block missing name_transform `{}` for {}",
                    t.label(),
                    d.id
                );
            }
        }

        // NO shipped row carries a transform (plan-055 Issue 2.3), and the SPEC says so.
        //
        // THIS ASSERTION IS LOAD-BEARING PRECISELY BECAUSE THE LOOP ABOVE CANNOT MAKE IT. That
        // loop guards the label check behind `if let Some(t) = d.name_transform`, so with every
        // row at `None` it checks NOTHING — a stale SPEC still carrying the label would sail
        // through. The emptiness has to be asserted directly, from this side.
        assert!(
            DESCRIPTORS.iter().all(|d| d.name_transform.is_none()),
            "no shipped row may carry a name_transform (plan-055 Issue 2.3)"
        );
    }

    // REQ-YF-INSTALL-007 (plan-055 Issue 2.3): NO row carries a transform, so
    // `transform_skill_name` is the IDENTITY on every row — including on a >64-character name,
    // the one arm EXP-002 never exercised and the arm that would have truncated silently.
    #[test]
    fn no_row_transforms_skill_names() {
        // A synthetic name longer than the retired transform's 64-char cap. Under the old pi
        // row this came back truncated to exactly 64; under every shipped row it must now come
        // back verbatim, because a truncating rename on a SHARED root would collide two skills
        // onto one directory.
        let long = "yf-".to_string() + &"x".repeat(80);
        assert_eq!(long.chars().count(), 83);

        for d in DESCRIPTORS {
            assert_eq!(d.name_transform, None, "{} must carry no transform", d.id);
            assert_eq!(
                d.transform_skill_name("yf-change-validation"),
                "yf-change-validation",
                "{} must not rewrite a long yf skill name",
                d.id
            );
            assert_eq!(
                d.transform_skill_name(&long),
                long,
                "{} must not TRUNCATE a >64-char name — the unexercised arm",
                d.id
            );
            // Case and separators are preserved too: opencode reads the name from frontmatter
            // and ignores the directory name entirely, so nothing needs normalizing.
            assert_eq!(d.transform_skill_name("YF_Mixed_Case"), "YF_Mixed_Case");
        }
    }

    // The retired transform's LOGIC is still correct where it is defined — kept so a future
    // harness adopting it inherits a tested implementation rather than an untested one.
    #[test]
    fn name_transform_type_still_works_when_declared() {
        let t = NameTransform::LowercaseHyphenMax64;
        assert_eq!(t.apply("YF_Change_Validation"), "yf-change-validation");
        let long = "yf-".to_string() + &"x".repeat(80);
        assert_eq!(t.apply(&long).chars().count(), 64);
    }

    // REQ-YF-CLI-002: `--surface` deprecated-alias mapping + legacy fallback.
    #[test]
    fn surface_alias_and_legacy_fallback() {
        assert_eq!(surface_alias("claude"), "claude-code");
        assert_eq!(surface_alias("agents"), "agents");
        assert_eq!(surface_alias("unknown"), "unknown");
        // Known ids resolve via the table; an unknown id falls back to `.<id>/skills`.
        assert_eq!(skills_subpath("claude-code", Scope::User), ".claude/skills");
        // COLLAPSED (Issue 2.2): pi's SKILLS resolve to the shared root in both scopes...
        assert_eq!(skills_subpath("pi", Scope::Project), ".agents/skills");
        assert_eq!(skills_subpath("pi", Scope::User), ".agents/skills");
        // ...while its SURFACE dir stays private, which is what the split buys.
        assert_eq!(surface_subpath("pi", Scope::User), ".pi/agent");
        assert_eq!(surface_subpath("pi", Scope::Project), ".pi");
        assert_eq!(surface_subpath("opencode", Scope::User), ".config/opencode");
        assert_eq!(
            skills_subpath("frobnicator", Scope::User),
            ".frobnicator/skills"
        );
    }
}
