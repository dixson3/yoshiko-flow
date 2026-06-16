//! Shared selection, deploy, companion-rule, and health logic for the `skills`
//! and `doctor` commands (REQ-YF-INSTALL-*, REQ-YF-MARK-*).
//!
//! These helpers are the single home for the filesystem-touching parts of the
//! lifecycle so `install`, `upgrade`, `remove`, `status`, and `doctor` agree on
//! exactly where files land and how health is judged. Every write goes through
//! the caller-supplied `skills_dir` / `rules_dir` (which a test always points at
//! a temp dir via `--target`), honoring GR-008 (touch only own surfaces).

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use anyhow::{Context, Result};

use crate::cli::{Scope, SkillsArgs};
use crate::{dest, embed, frontmatter, marker};

/// Resolved selection plus the closure diagnostics to surface to the operator.
pub struct Selection {
    /// Skills to act on, after the `depends-on-skill` transitive closure.
    pub install: BTreeSet<String>,
    /// Non-fatal closure notes (unknown deps, cross-group pulls).
    pub log: Vec<String>,
}

/// Resolve the set of skills a `skills` subcommand operates on.
///
/// Precedence mirrors `install.py`: explicit positional names > `--group` >
/// default (all embedded skills). The base set is then transitively closed over
/// `depends-on-skill` (REQ-YF-INSTALL-004). `group` is an optional group filter
/// (only `install` exposes `--group`; other verbs pass `None`).
pub fn resolve_selection(
    skills: &BTreeMap<String, frontmatter::Frontmatter>,
    names: &[String],
    group: Option<&str>,
) -> Result<Selection> {
    let mut log: Vec<String> = Vec::new();
    let base: BTreeSet<String> = if !names.is_empty() {
        let known: BTreeSet<&String> = skills.keys().collect();
        let unknown: Vec<&String> = names.iter().filter(|n| !known.contains(n)).collect();
        if !unknown.is_empty() {
            let unknown = unknown
                .iter()
                .map(|s| s.as_str())
                .collect::<Vec<_>>()
                .join(", ");
            let available = skills.keys().cloned().collect::<Vec<_>>().join(", ");
            anyhow::bail!("unknown skill(s): {unknown}\navailable: {available}");
        }
        if group.is_some() {
            log.push("  note: explicit skill names given — ignoring --group".to_string());
        }
        names.iter().cloned().collect()
    } else if let Some(g) = group {
        let groups = frontmatter::computed_groups(skills);
        if !groups.iter().any(|x| x == g) {
            anyhow::bail!("unknown group '{g}'. valid groups: {}", groups.join(", "));
        }
        frontmatter::skills_in_group(skills, g)
            .into_iter()
            .collect()
    } else {
        skills.keys().cloned().collect()
    };

    let (install, closure_log) = frontmatter::resolve_install_set(skills, &base);
    log.extend(closure_log);
    Ok(Selection { install, log })
}

/// Required `depends-on-tool` entries (across the install set) missing from PATH.
pub fn missing_tools(
    skills: &BTreeMap<String, frontmatter::Frontmatter>,
    install: &BTreeSet<String>,
) -> Vec<String> {
    let mut required: BTreeSet<String> = BTreeSet::new();
    for name in install {
        if let Some(meta) = skills.get(name) {
            required.extend(meta.tools.iter().cloned());
        }
    }
    required.into_iter().filter(|t| !tool_on_path(t)).collect()
}

/// Whether `tool` resolves on the current `PATH` (a `which`-equivalent).
pub fn tool_on_path(tool: &str) -> bool {
    let Some(path) = std::env::var_os("PATH") else {
        return false;
    };
    std::env::split_paths(&path).any(|dir| {
        let cand = dir.join(tool);
        cand.is_file() && is_executable(&cand)
    })
}

#[cfg(unix)]
fn is_executable(path: &Path) -> bool {
    use std::os::unix::fs::PermissionsExt;
    std::fs::metadata(path)
        .map(|m| m.permissions().mode() & 0o111 != 0)
        .unwrap_or(false)
}

#[cfg(not(unix))]
fn is_executable(_path: &Path) -> bool {
    true
}

/// Deploy one embedded skill into `skills_dir/<name>`, injecting the integrity
/// marker into the written `SKILL.md` (REQ-YF-INSTALL-001, REQ-YF-MARK-002).
///
/// When `prune` is set (upgrade), deployed files absent from the embedded tree
/// are removed first (REQ-YF-MARK-004). The embedded tree hash is computed from
/// the marker-stripped source so the deployed (marked) copy hashes identically
/// later (REQ-YF-MARK-001).
///
/// Returns the list of skill-relative file paths written.
pub fn deploy_skill(name: &str, skills_dir: &Path, prune: bool) -> Result<Vec<String>> {
    let skill_root = skills_dir.join(name);
    let embedded_files = embed::skill_files(name);
    let embedded_set: BTreeSet<&str> = embedded_files.iter().map(String::as_str).collect();

    if prune {
        prune_extra_files(&skill_root, &embedded_set)?;
    }

    let tree = marker::embedded_tree_hash(name);
    let version = crate::VERSION;
    let mut written = Vec::new();

    for relpath in &embedded_files {
        let full = format!("{name}/{relpath}");
        let Some(bytes) = embed::read_file(&full) else {
            continue;
        };
        let dest = skill_root.join(relpath);
        if let Some(parent) = dest.parent() {
            std::fs::create_dir_all(parent)
                .with_context(|| format!("creating {}", parent.display()))?;
        }
        if relpath == "SKILL.md" {
            let text = String::from_utf8_lossy(&bytes).into_owned();
            let marked = marker::inject_marker(&text, version, &tree);
            std::fs::write(&dest, marked).with_context(|| format!("writing {}", dest.display()))?;
        } else {
            std::fs::write(&dest, bytes.as_ref())
                .with_context(|| format!("writing {}", dest.display()))?;
        }
        written.push(relpath.clone());
    }
    Ok(written)
}

/// Remove deployed files (and now-empty dirs) under `skill_root` that are not in
/// the embedded file set. Used by `upgrade` to keep the deployed tree a subset of
/// the embedded one (REQ-YF-MARK-004).
fn prune_extra_files(skill_root: &Path, embedded: &BTreeSet<&str>) -> Result<Vec<String>> {
    let mut pruned = Vec::new();
    if !skill_root.exists() {
        return Ok(pruned);
    }
    let deployed = walk_relpaths(skill_root, skill_root)?;
    for rel in deployed {
        if !embedded.contains(rel.as_str()) {
            let p = skill_root.join(&rel);
            std::fs::remove_file(&p).with_context(|| format!("pruning {}", p.display()))?;
            pruned.push(rel);
        }
    }
    remove_empty_dirs(skill_root)?;
    Ok(pruned)
}

/// The list of files that `deploy_skill(.., prune=true)` would remove (for
/// `--dry-run` reporting). Does not mutate the filesystem.
pub fn extra_deployed_files(name: &str, skills_dir: &Path) -> Result<Vec<String>> {
    let skill_root = skills_dir.join(name);
    if !skill_root.exists() {
        return Ok(Vec::new());
    }
    let embedded: BTreeSet<String> = embed::skill_files(name).into_iter().collect();
    let deployed = walk_relpaths(&skill_root, &skill_root)?;
    Ok(deployed
        .into_iter()
        .filter(|r| !embedded.contains(r))
        .collect())
}

/// Install a skill's companion rules (`protocols/*.md`) into `rules_dir`.
///
/// Mirrors `install.py`'s `install_rules`: each `protocols/*.md` lands at
/// `rules_dir/<basename>`. Without `force`, an existing rule is preserved
/// (REQ-YF-INSTALL-006); with `force`, it is overwritten. Returns the basenames
/// of rules written and the basenames kept (skipped because present).
pub fn install_rules(
    name: &str,
    rules_dir: &Path,
    force: bool,
) -> Result<(Vec<String>, Vec<String>)> {
    let mut written = Vec::new();
    let mut kept = Vec::new();
    for (basename, bytes) in embedded_rules(name) {
        let target = rules_dir.join(&basename);
        if target.exists() && !force {
            kept.push(basename);
            continue;
        }
        std::fs::create_dir_all(rules_dir)
            .with_context(|| format!("creating {}", rules_dir.display()))?;
        std::fs::write(&target, &bytes).with_context(|| format!("writing {}", target.display()))?;
        written.push(basename);
    }
    Ok((written, kept))
}

/// `(basename, bytes)` for every `protocols/*.md` companion rule of `skill`.
pub fn embedded_rules(skill: &str) -> Vec<(String, Vec<u8>)> {
    let mut out = Vec::new();
    for relpath in embed::skill_files(skill) {
        let Some(base) = relpath.strip_prefix("protocols/") else {
            continue;
        };
        if !base.ends_with(".md") || base.contains('/') {
            continue; // top-level protocols/*.md only (matches install.py glob)
        }
        if let Some(bytes) = embed::read_file(&format!("{skill}/{relpath}")) {
            out.push((base.to_string(), bytes.into_owned()));
        }
    }
    out
}

/// Per-skill health, shared by `status` and `doctor` (REQ-YF-MARK-003).
#[derive(Debug, Clone)]
pub struct Health {
    pub name: String,
    /// SKILL.md present at the destination.
    pub installed: bool,
    /// Deployed marker tree-hash == embedded tree hash.
    pub up_to_date: bool,
    /// Every embedded file present at the destination.
    pub complete: bool,
    /// Recomputed (marker-stripped) deployed hash == embedded — no tampering.
    pub unmodified: bool,
    /// Embedded tree hash (the source-of-truth value).
    pub embedded_hash: String,
    /// Hash parsed from the deployed marker, if any.
    pub marker_hash: Option<String>,
}

impl Health {
    /// One-word doctor verdict for the skill axis (REQ-YF-DOCTOR-001).
    pub fn doctor_state(&self) -> &'static str {
        if !self.installed {
            "not installed"
        } else if !self.complete {
            "incomplete"
        } else if !self.up_to_date {
            "outdated (run yf skills upgrade)"
        } else if !self.unmodified {
            "modified"
        } else {
            "ok"
        }
    }

    /// True when the skill axis is healthy (drives doctor's exit code).
    pub fn is_ok(&self) -> bool {
        self.installed && self.complete && self.up_to_date && self.unmodified
    }
}

/// Compute [`Health`] for one skill at `skills_dir`.
pub fn skill_health(name: &str, skills_dir: &Path) -> Result<Health> {
    let skill_root = skills_dir.join(name);
    let skill_md = skill_root.join("SKILL.md");
    let embedded_hash = marker::embedded_tree_hash(name);

    let installed = skill_md.is_file();
    if !installed {
        return Ok(Health {
            name: name.to_string(),
            installed: false,
            up_to_date: false,
            complete: false,
            unmodified: false,
            embedded_hash,
            marker_hash: None,
        });
    }

    let marker_hash = std::fs::read_to_string(&skill_md)
        .ok()
        .and_then(|t| marker::parse_marker(&t))
        .map(|(_v, h)| h);
    let up_to_date = marker_hash.as_deref() == Some(embedded_hash.as_str());

    let complete = embed::skill_files(name)
        .iter()
        .all(|rel| skill_root.join(rel).is_file());

    let unmodified = marker::deployed_tree_hash(&skill_root)
        .map(|h| h == embedded_hash)
        .unwrap_or(false);

    Ok(Health {
        name: name.to_string(),
        installed: true,
        up_to_date,
        complete,
        unmodified,
        embedded_hash,
        marker_hash,
    })
}

/// Resolve `(skills_dir, rules_dir)` from a `skills` subcommand's args.
pub fn dirs_for(args: &SkillsArgs) -> (PathBuf, PathBuf) {
    let target = args.target.as_deref();
    (
        dest::resolve_skills_dir(args.scope, args.surface, target),
        dest::resolve_rules_dir(args.scope, args.surface, target),
    )
}

/// Same, but spelled out for callers that already have the pieces (doctor).
pub fn dirs_from(scope: Scope, surface: crate::cli::Surface) -> (PathBuf, PathBuf) {
    (
        dest::resolve_skills_dir(scope, surface, None),
        dest::resolve_rules_dir(scope, surface, None),
    )
}

// --- small fs helpers ---------------------------------------------------------

/// Skill-relative paths of every file under `dir` (relative to `root`), `/`-joined.
fn walk_relpaths(root: &Path, dir: &Path) -> Result<Vec<String>> {
    let mut out = Vec::new();
    walk_relpaths_into(root, dir, &mut out)?;
    out.sort();
    Ok(out)
}

fn walk_relpaths_into(root: &Path, dir: &Path, out: &mut Vec<String>) -> Result<()> {
    for entry in std::fs::read_dir(dir).with_context(|| format!("reading {}", dir.display()))? {
        let path = entry?.path();
        if path.is_dir() {
            walk_relpaths_into(root, &path, out)?;
        } else if path.is_file() {
            if let Ok(rel) = path.strip_prefix(root) {
                let joined = rel
                    .components()
                    .map(|c| c.as_os_str().to_string_lossy())
                    .collect::<Vec<_>>()
                    .join("/");
                out.push(joined);
            }
        }
    }
    Ok(())
}

/// Recursively remove now-empty directories under `root` (root itself kept).
fn remove_empty_dirs(root: &Path) -> Result<()> {
    fn recurse(dir: &Path) -> Result<bool> {
        let mut empty = true;
        for entry in std::fs::read_dir(dir)? {
            let path = entry?.path();
            if path.is_dir() {
                if recurse(&path)? {
                    std::fs::remove_dir(&path).ok();
                } else {
                    empty = false;
                }
            } else {
                empty = false;
            }
        }
        Ok(empty)
    }
    if root.is_dir() {
        recurse(root)?;
    }
    Ok(())
}
