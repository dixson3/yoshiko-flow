//! SKILL.md frontmatter parsing, install-group computation, and transitive
//! `depends-on-skill` closure (REQ-YF-INSTALL-003 / REQ-YF-INSTALL-004).
//!
//! This mirrors the retired `install.py` (`parse_frontmatter`, `load_skills`,
//! `computed_groups`, `resolve_install_set`) but reads each skill's `SKILL.md`
//! from the embedded tree ([`crate::embed`]) instead of the filesystem.
//!
//! ## Frontmatter parser
//!
//! Only the leading `--- … ---` YAML block at the top of a `SKILL.md` is parsed,
//! and only five keys are extracted: `name`, `skill-group`, `depends-on-tool`,
//! `depends-on-skill`, `user-invocable`. Unknown keys are ignored so later beads
//! can add frontmatter without touching this parser.
//!
//! Per GR-011 (small, dependency-light binary) the parser is hand-rolled rather
//! than pulling in a full YAML crate. The real `skills/*/SKILL.md` frontmatter is
//! flat key/value with inline arrays (`depends-on-skill: [a, b]`) and quoted or
//! unquoted scalars — exactly what this parser handles. It deliberately does NOT
//! support block (`-` item) sequences, nested maps, or multi-line scalars: none
//! appear in the keys we extract, and a frontmatter author adding them would be
//! diverging from the established convention.

// The group/closure API is consumed by the real `skills install`/`status`
// commands in later beads (1.5/1.6); only some entry points are wired so far.
// Mirror embed.rs and silence dead-code for the not-yet-wired public surface.
#![allow(dead_code)]

use std::collections::{BTreeMap, BTreeSet};

use crate::embed;

/// The `preflight:` nested descriptor (bead 2.2), surfaced for the preflight
/// kernel (bead 2.3, REQ-YF-PRE-004). All fields optional — a skill without a
/// `preflight:` block yields `None` for the whole [`Preflight`].
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Preflight {
    /// `companion-rule:` — the hash-checked rule filename (e.g. `PLANS.md`).
    pub companion_rule: Option<String>,
    /// `min-bd-version:` — minimum bd semver the skill requires (e.g. `1.0.5`).
    /// Absent for skills that do not need beads (e.g. optimal-instructions).
    pub min_bd_version: Option<String>,
    /// `config-basename:` — the legacy per-skill operator config file basename
    /// at repo root (e.g. `.yf-plan.local.json`).
    pub config_basename: Option<String>,
}

/// Parsed frontmatter for one skill. Mirrors the `meta` dict in `install.py`'s
/// `load_skills`, plus `name` / `user_invocable` which the SPEC also requires.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct Frontmatter {
    /// `name:` — the skill's declared name (usually equal to its dir name).
    pub name: String,
    /// `skill-group:` — install group (`beads`, `utility`, `markdown`, …). `None`
    /// if absent (such a skill is grouped under no group).
    pub group: Option<String>,
    /// `depends-on-tool:` — PATH tools the skill needs (e.g. `bd`, `uv`).
    pub tools: Vec<String>,
    /// `depends-on-skill:` — bare in-repo skill names this skill requires.
    pub skills: Vec<String>,
    /// `user-invocable:` — whether the skill is a slash-command entry point.
    pub user_invocable: Option<bool>,
    /// `preflight:` — the nested preflight descriptor (REQ-YF-PRE-004). `None`
    /// when the skill ships no `preflight:` block.
    pub preflight: Option<Preflight>,
}

/// Parse the leading `--- … ---` YAML frontmatter block of a `SKILL.md`.
///
/// Returns a [`Frontmatter`] with the five recognized keys; unknown keys are
/// ignored. If `text` does not start with a `---` fence (or the closing fence is
/// missing) an all-default [`Frontmatter`] is returned, matching `install.py`
/// returning `{}` in that case.
pub fn parse_frontmatter(text: &str) -> Frontmatter {
    let mut fm = Frontmatter::default();
    let Some(block) = frontmatter_block(text) else {
        return fm;
    };
    // We need to detect nested maps (`preflight:` followed by indented children),
    // so iterate over raw lines (indentation preserved) with peeking.
    let raw_lines: Vec<&str> = block.lines().collect();
    let mut i = 0;
    while i < raw_lines.len() {
        let raw = raw_lines[i];
        i += 1;
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') || line.starts_with('-') {
            continue;
        }
        let Some((key, value)) = line.split_once(':') else {
            continue;
        };
        let key = key.trim();
        let value = value.trim();
        match key {
            "name" => fm.name = scalar(value),
            "skill-group" => {
                let v = scalar(value);
                fm.group = if v.is_empty() { None } else { Some(v) };
            }
            "depends-on-tool" => fm.tools = parse_list(value),
            "depends-on-skill" => fm.skills = parse_list(value),
            "user-invocable" => fm.user_invocable = parse_bool(value),
            "preflight" if value.is_empty() => {
                // A nested map: consume the following indented child lines.
                let mut children: Vec<&str> = Vec::new();
                while i < raw_lines.len() {
                    let child = raw_lines[i];
                    // Indented (and non-blank) → belongs to the preflight map.
                    if child.trim().is_empty() {
                        i += 1;
                        continue;
                    }
                    let indent = child.len() - child.trim_start().len();
                    if indent == 0 {
                        break; // back to top level
                    }
                    children.push(child);
                    i += 1;
                }
                fm.preflight = Some(parse_preflight(&children));
            }
            _ => {} // ignore unknown keys (forward-compatible)
        }
    }
    fm
}

/// Parse the indented child lines of a `preflight:` block into a [`Preflight`].
fn parse_preflight(children: &[&str]) -> Preflight {
    let mut pf = Preflight::default();
    for raw in children {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let Some((key, value)) = line.split_once(':') else {
            continue;
        };
        let value = scalar(value.trim());
        let value = if value.is_empty() { None } else { Some(value) };
        match key.trim() {
            "companion-rule" => pf.companion_rule = value,
            "min-bd-version" => pf.min_bd_version = value,
            "config-basename" => pf.config_basename = value,
            _ => {}
        }
    }
    pf
}

/// Extract the text between the opening `---` and the next `---` fence line.
///
/// The opening fence must be the very first line (`text` starts with `---`),
/// mirroring `install.py`'s `text.startswith("---")` guard.
fn frontmatter_block(text: &str) -> Option<&str> {
    // Normalize a possible BOM/leading newline is not needed: real files start
    // directly with `---`. Require the first line to be exactly the fence.
    let mut lines = text.lines();
    let first = lines.next()?;
    if first.trim() != "---" {
        return None;
    }
    let after_open = &text[first.len()..];
    let after_open = after_open.strip_prefix('\n').unwrap_or(after_open);
    // Find the closing fence: a line that is exactly `---`. Track the byte offset
    // as we go so we can slice the block up to (but not including) that line.
    let mut offset = 0usize;
    for line in after_open.lines() {
        if line.trim() == "---" {
            return Some(&after_open[..offset]);
        }
        offset += line.len() + 1; // + newline
    }
    None
}

/// Strip surrounding single/double quotes from a scalar value.
fn scalar(value: &str) -> String {
    let v = value.trim();
    if (v.starts_with('"') && v.ends_with('"') && v.len() >= 2)
        || (v.starts_with('\'') && v.ends_with('\'') && v.len() >= 2)
    {
        v[1..v.len() - 1].to_string()
    } else {
        v.to_string()
    }
}

/// Parse a YAML value into a list of strings, matching `install.py`'s `_as_list`:
/// an inline array `[a, b]`, a single bare scalar, or empty/`[]` → `[]`.
fn parse_list(value: &str) -> Vec<String> {
    let v = value.trim();
    if v.is_empty() || v == "[]" || v == "~" || v == "null" {
        return Vec::new();
    }
    if let Some(inner) = v.strip_prefix('[').and_then(|s| s.strip_suffix(']')) {
        return inner
            .split(',')
            .map(scalar)
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect();
    }
    // Bare scalar → single-element list.
    vec![scalar(v)]
}

/// Parse a YAML boolean scalar (`true`/`false`, case-insensitive). Unknown → None.
fn parse_bool(value: &str) -> Option<bool> {
    match scalar(value).to_ascii_lowercase().as_str() {
        "true" | "yes" => Some(true),
        "false" | "no" => Some(false),
        _ => None,
    }
}

/// Load every embedded skill's parsed frontmatter, keyed by skill dir name.
///
/// Mirrors `install.py`'s `load_skills`: a directory counts as a skill only if it
/// has a `SKILL.md` (the embed API's `skill_names` already excludes top-level
/// files). The map key is the directory name, NOT the frontmatter `name` field —
/// `depends-on-skill` references the dir name in this repo's convention.
pub fn load_skills() -> BTreeMap<String, Frontmatter> {
    let mut skills = BTreeMap::new();
    for name in embed::skill_names() {
        let relpath = format!("{name}/SKILL.md");
        let Some(bytes) = embed::read_file(&relpath) else {
            continue; // directory without a SKILL.md is not a skill
        };
        let text = String::from_utf8_lossy(&bytes);
        skills.insert(name, parse_frontmatter(&text));
    }
    skills
}

/// Sorted set of distinct non-empty `skill-group` values, like `computed_groups`.
pub fn computed_groups(skills: &BTreeMap<String, Frontmatter>) -> Vec<String> {
    let groups: BTreeSet<String> = skills.values().filter_map(|m| m.group.clone()).collect();
    groups.into_iter().collect()
}

/// Sorted skill dir names whose `skill-group` equals `group`.
pub fn skills_in_group(skills: &BTreeMap<String, Frontmatter>, group: &str) -> Vec<String> {
    skills
        .iter()
        .filter(|(_, m)| m.group.as_deref() == Some(group))
        .map(|(n, _)| n.clone())
        .collect()
}

/// Transitively close a base set of skills over `depends-on-skill`.
///
/// Mirrors `install.py`'s `resolve_install_set`:
/// - a dep not present in the embedded tree is logged as external/assumed-provided
///   and skipped (NOT fatal);
/// - pulling a dep from a different `skill-group` is logged as crossing a group
///   boundary;
/// - base names not present in the tree are likewise reported (the Python CLI
///   rejected unknown explicit names earlier; here we keep closure robust and
///   surface them as warnings instead of panicking).
///
/// Returns the full install set plus a list of human-readable diagnostics.
pub fn resolve_install_set(
    skills: &BTreeMap<String, Frontmatter>,
    base: &BTreeSet<String>,
) -> (BTreeSet<String>, Vec<String>) {
    let mut install: BTreeSet<String> = BTreeSet::new();
    let mut log: Vec<String> = Vec::new();
    let mut queue: Vec<String> = base.iter().cloned().collect();

    while let Some(name) = queue.pop() {
        if install.contains(&name) {
            continue;
        }
        let Some(meta) = skills.get(&name) else {
            // Unknown requested skill: warn, do not add, do not panic.
            log.push(format!(
                "  note: requested skill '{name}' — not found in-repo; skipped"
            ));
            continue;
        };
        install.insert(name.clone());
        for dep in &meta.skills {
            match skills.get(dep) {
                None => log.push(format!(
                    "  note: {name} depends-on-skill '{dep}' — not found in-repo; \
                     external / assumed-provided, skipped"
                )),
                Some(dep_meta) => {
                    if !install.contains(dep) {
                        if let (Some(ng), Some(dg)) = (&meta.group, &dep_meta.group) {
                            if ng != dg {
                                log.push(format!(
                                    "  note: pulling '{dep}' (group {dg}) as a dependency of \
                                     '{name}' (group {ng}) — crosses group boundary"
                                ));
                            }
                        }
                        queue.push(dep.clone());
                    }
                }
            }
        }
    }
    (install, log)
}

/// Convenience: resolve the full install set for an entire group.
pub fn resolve_group(
    skills: &BTreeMap<String, Frontmatter>,
    group: &str,
) -> (BTreeSet<String>, Vec<String>) {
    let base: BTreeSet<String> = skills_in_group(skills, group).into_iter().collect();
    resolve_install_set(skills, &base)
}

#[cfg(test)]
mod tests {
    use super::*;

    // --- Parser unit tests (REQ-YF-INSTALL-003) ---

    // REQ-YF-INSTALL-003
    #[test]
    fn parses_inline_arrays_and_scalars() {
        let text = "---\n\
            name: yf-plan\n\
            user-invocable: true\n\
            skill-group: beads\n\
            depends-on-tool: [bd, uv, git]\n\
            depends-on-skill: [yf-beads-extra, yf-beads-authoring]\n\
            ---\n\
            body text here\n";
        let fm = parse_frontmatter(text);
        assert_eq!(fm.name, "yf-plan");
        assert_eq!(fm.group.as_deref(), Some("beads"));
        assert_eq!(fm.tools, vec!["bd", "uv", "git"]);
        assert_eq!(fm.skills, vec!["yf-beads-extra", "yf-beads-authoring"]);
        assert_eq!(fm.user_invocable, Some(true));
    }

    // REQ-YF-PRE-004: the nested `preflight:` descriptor is surfaced.
    #[test]
    fn parses_preflight_descriptor() {
        let text = "---\n\
            name: yf-plan\n\
            depends-on-tool: [bd, uv, git]\n\
            preflight:\n\
            \x20\x20companion-rule: PLANS.md\n\
            \x20\x20min-bd-version: 1.0.5\n\
            \x20\x20config-basename: .yf-plan.local.json\n\
            ---\nbody\n";
        let fm = parse_frontmatter(text);
        let pf = fm.preflight.expect("preflight descriptor expected");
        assert_eq!(pf.companion_rule.as_deref(), Some("PLANS.md"));
        assert_eq!(pf.min_bd_version.as_deref(), Some("1.0.5"));
        assert_eq!(pf.config_basename.as_deref(), Some(".yf-plan.local.json"));
        // Existing flat keys still parse alongside the nested block.
        assert_eq!(fm.name, "yf-plan");
        assert_eq!(fm.tools, vec!["bd", "uv", "git"]);
    }

    // REQ-YF-PRE-004: a preflight block without min-bd-version (no-beads skill).
    #[test]
    fn preflight_without_min_bd_version() {
        let text = "---\n\
            name: yf-optimal-instructions\n\
            preflight:\n\
            \x20\x20companion-rule: INSTRUCTIONS.md\n\
            \x20\x20config-basename: .yf-optimal-instructions.local.json\n\
            ---\n";
        let pf = parse_frontmatter(text)
            .preflight
            .expect("preflight expected");
        assert_eq!(pf.companion_rule.as_deref(), Some("INSTRUCTIONS.md"));
        assert_eq!(pf.min_bd_version, None);
    }

    // REQ-YF-PRE-004: no preflight block → None (the real markdown skills).
    #[test]
    fn no_preflight_block_is_none() {
        let text = "---\nname: x\nskill-group: utility\n---\n";
        assert_eq!(parse_frontmatter(text).preflight, None);
    }

    // REQ-YF-PRE-004: the real embedded yf-plan SKILL.md exposes its descriptor.
    #[test]
    fn real_yf_plan_preflight_descriptor() {
        let skills = load_skills();
        let pf = skills
            .get("yf-plan")
            .and_then(|f| f.preflight.clone())
            .expect("yf-plan must carry a preflight descriptor");
        assert_eq!(pf.companion_rule.as_deref(), Some("PLANS.md"));
        assert_eq!(pf.min_bd_version.as_deref(), Some("1.0.5"));
        assert_eq!(pf.config_basename.as_deref(), Some(".yf-plan.local.json"));
    }

    // REQ-YF-INSTALL-003
    #[test]
    fn ignores_unknown_keys() {
        let text = "---\n\
            name: x\n\
            description: a long description that we ignore\n\
            some-future-key: [1, 2, 3]\n\
            skill-group: utility\n\
            ---\nbody\n";
        let fm = parse_frontmatter(text);
        assert_eq!(fm.name, "x");
        assert_eq!(fm.group.as_deref(), Some("utility"));
        assert!(fm.tools.is_empty());
        assert!(fm.skills.is_empty());
    }

    // REQ-YF-INSTALL-003
    #[test]
    fn empty_and_quoted_values() {
        let text = "---\n\
            name: \"quoted-name\"\n\
            depends-on-skill: []\n\
            depends-on-tool: 'bd'\n\
            ---\n";
        let fm = parse_frontmatter(text);
        assert_eq!(fm.name, "quoted-name");
        assert!(fm.skills.is_empty());
        assert_eq!(fm.tools, vec!["bd"]);
    }

    // REQ-YF-INSTALL-003
    #[test]
    fn no_frontmatter_returns_default() {
        let fm = parse_frontmatter("# Just a heading\n\nno frontmatter here\n");
        assert_eq!(fm, Frontmatter::default());
    }

    // --- Real embedded-tree tests (REQ-YF-INSTALL-003) ---

    // REQ-YF-INSTALL-003
    #[test]
    fn loads_real_embedded_skills() {
        let skills = load_skills();
        assert!(!skills.is_empty(), "expected embedded skills");
        let extra = skills
            .get("yf-beads-extra")
            .expect("yf-beads-extra must be embedded");
        assert_eq!(extra.name, "yf-beads-extra");
        assert_eq!(extra.group.as_deref(), Some("beads"));
        assert!(extra.skills.is_empty(), "yf-beads-extra has no skill deps");
    }

    // REQ-YF-INSTALL-003
    #[test]
    fn computed_groups_match_spec() {
        let skills = load_skills();
        let groups = computed_groups(&skills);
        // SPEC §3.3: current groups are beads, utility, markdown.
        assert_eq!(groups, vec!["beads", "markdown", "utility"]);
    }

    // REQ-YF-INSTALL-003
    #[test]
    fn beads_group_contains_beads_skills() {
        let skills = load_skills();
        let beads = skills_in_group(&skills, "beads");
        for expected in ["yf-beads-extra", "yf-beads-authoring", "yf-plan"] {
            assert!(
                beads.contains(&expected.to_string()),
                "beads group missing {expected}: {beads:?}"
            );
        }
        // A markdown skill must NOT be in the beads group.
        assert!(!beads.contains(&"yf-markdown-lint".to_string()));
    }

    // --- Transitive closure tests (REQ-YF-INSTALL-004) ---

    // REQ-YF-INSTALL-004
    #[test]
    fn closure_pulls_transitive_skill_dep() {
        let skills = load_skills();
        let base: BTreeSet<String> = ["yf-beads-upstream".to_string()].into_iter().collect();
        let (install, log) = resolve_install_set(&skills, &base);
        // yf-beads-upstream depends-on-skill: [yf-beads-extra].
        assert!(install.contains("yf-beads-upstream"));
        assert!(
            install.contains("yf-beads-extra"),
            "closure must pull yf-beads-extra: {install:?}"
        );
        // Same group → no cross-group warning expected.
        assert!(
            log.is_empty(),
            "no diagnostics expected for in-group closure: {log:?}"
        );
    }

    // REQ-YF-INSTALL-004
    #[test]
    fn closure_handles_multi_hop_base() {
        let skills = load_skills();
        // yf-plan depends on yf-beads-extra AND yf-beads-authoring; the latter
        // also depends on yf-beads-extra — exercise the de-dup path.
        let base: BTreeSet<String> = ["yf-plan".to_string()].into_iter().collect();
        let (install, _log) = resolve_install_set(&skills, &base);
        for expected in ["yf-plan", "yf-beads-extra", "yf-beads-authoring"] {
            assert!(
                install.contains(expected),
                "closure missing {expected}: {install:?}"
            );
        }
    }

    // REQ-YF-INSTALL-004
    #[test]
    fn unknown_requested_skill_warns_not_panics() {
        let skills = load_skills();
        let base: BTreeSet<String> = ["does-not-exist".to_string()].into_iter().collect();
        let (install, log) = resolve_install_set(&skills, &base);
        assert!(install.is_empty(), "unknown skill must not be installed");
        assert!(
            log.iter().any(|l| l.contains("does-not-exist")),
            "unknown skill must be logged: {log:?}"
        );
    }

    // REQ-YF-INSTALL-004
    #[test]
    fn group_resolution_is_closed() {
        let skills = load_skills();
        let (install, _log) = resolve_group(&skills, "beads");
        // Every beads-group skill is present, plus its deps (all in-group here).
        for n in skills_in_group(&skills, "beads") {
            assert!(install.contains(&n), "group closure missing {n}");
        }
    }
}
