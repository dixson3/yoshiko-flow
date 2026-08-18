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
use crate::flow::{self, FlowSection};
use crate::{dest, embed, frontmatter, harness_desc, harness_detect, marker};

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
    crate::tool::tool_on_path(tool)
}

/// Deploy one embedded skill into `skills_dir/<dir-name>`, injecting the
/// integrity marker into the written `SKILL.md` (REQ-YF-INSTALL-001,
/// REQ-YF-MARK-002).
///
/// The on-disk directory name is the skill `name` run through the target
/// `harness`'s `name_transform` (REQ-YF-INSTALL-007): identity for every harness
/// except `pi`, which imposes `lowercase-hyphen,max64`. Embedded-source lookups
/// always key on the untransformed `name`. An unknown harness id is identity.
///
/// When `prune` is set (upgrade), deployed files absent from the embedded tree
/// are removed first (REQ-YF-MARK-004). The embedded tree hash is computed from
/// the marker-stripped source so the deployed (marked) copy hashes identically
/// later (REQ-YF-MARK-001).
///
/// Returns the list of skill-relative file paths written.
pub fn deploy_skill(
    name: &str,
    skills_dir: &Path,
    prune: bool,
    harness: &str,
) -> Result<Vec<String>> {
    let dir_name = harness_desc::lookup(harness)
        .map(|d| d.transform_skill_name(name))
        .unwrap_or_else(|| name.to_string());
    let skill_root = skills_dir.join(&dir_name);
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
        // REQ-YF-MARK-005: never DELETE generated residue. Symmetric with the
        // tree-hash walk and `extra_deployed_files` — if the three disagreed, prune
        // would remove a file the hash still expected (or vice versa) and doctor
        // would oscillate between `modified` and clean.
        if crate::marker::is_ignored_relpath(&rel) {
            continue;
        }
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
///
/// plan-044 Issue 2.8 (#155): takes `harness` and applies the SAME
/// `transform_skill_name` that [`deploy_skill`] uses to resolve `skill_root`.
/// Without it this joined the RAW skill name, so on a transforming harness (pi,
/// `lowercase-hyphen,max64`) it looked in a directory that does not exist, found
/// nothing, and reported an EMPTY prune set — a `--dry-run --prune` preview
/// silently claiming nothing would be removed while the real run removed files.
/// A preview that lies is worse than no preview: it is the evidence the operator
/// consents on.
pub fn extra_deployed_files(name: &str, skills_dir: &Path, harness: &str) -> Result<Vec<String>> {
    let dir_name = harness_desc::lookup(harness)
        .map(|d| d.transform_skill_name(name))
        .unwrap_or_else(|| name.to_string());
    let skill_root = skills_dir.join(&dir_name);
    if !skill_root.exists() {
        return Ok(Vec::new());
    }
    let embedded: BTreeSet<String> = embed::skill_files(name).into_iter().collect();
    let deployed = walk_relpaths(&skill_root, &skill_root)?;
    Ok(deployed
        .into_iter()
        // REQ-YF-MARK-005: residue is not an "extra deployed file" — it is
        // generated, unembedded by design, and must not be proposed for prune.
        .filter(|r| !embedded.contains(r) && !crate::marker::is_ignored_relpath(r))
        .collect())
}

/// Outcome of an aggregate `YOSHIKO_FLOW.md` write (REQ-YF-FLOW-*). Fields feed
/// the `install`/`upgrade`/`remove` `--json` reporting (Issue 2.4).
#[derive(Debug, Default)]
pub struct FlowWriteResult {
    /// The single aggregate target path (`<rules_dir>/YOSHIKO_FLOW.md`).
    pub flow_file: PathBuf,
    /// Protocols whose section was (re)written from the embedded source.
    pub upserted: Vec<String>,
    /// Protocols whose section reconcile pruned (no longer embedded / deprecated).
    pub pruned: Vec<String>,
    /// Protocols folded in from a now-deleted standalone rule file (migration).
    pub migrated: Vec<String>,
}

/// Path of the aggregate ruleset file within `rules_dir`.
pub fn flow_path(rules_dir: &Path) -> PathBuf {
    rules_dir.join(flow::FLOW_FILENAME)
}

/// Parse the on-disk `YOSHIKO_FLOW.md` in `rules_dir` into its sections (empty if
/// the file is absent or unreadable).
pub fn read_flow_sections(rules_dir: &Path) -> Vec<FlowSection> {
    std::fs::read_to_string(flow_path(rules_dir))
        .ok()
        .map(|t| flow::parse(&t))
        .unwrap_or_default()
}

/// Write `sections` to `rules_dir/YOSHIKO_FLOW.md`, or delete the file when
/// `sections` is empty (S6: the last section removed deletes the file). Returns
/// `true` when the file was deleted. The serialized form carries the banner and
/// the deterministic `yf`-version generated-on note.
pub fn write_flow(rules_dir: &Path, sections: &[FlowSection]) -> Result<bool> {
    let path = flow_path(rules_dir);
    if sections.is_empty() {
        if path.exists() {
            std::fs::remove_file(&path).with_context(|| format!("removing {}", path.display()))?;
            return Ok(true);
        }
        return Ok(false);
    }
    std::fs::create_dir_all(rules_dir)
        .with_context(|| format!("creating {}", rules_dir.display()))?;
    let text = flow::serialize(sections, crate::VERSION);
    std::fs::write(&path, text).with_context(|| format!("writing {}", path.display()))?;
    Ok(false)
}

/// Install/refresh the acted-on skills' protocol sections into the aggregate,
/// reconcile-prune invalid sections, then write (REQ-YF-FLOW-*, S3).
///
/// S3 — no hand-edit tolerance: acted-on sections are **always** rewritten to the
/// embedded version (there is no `force`/`kept` gate). Reconcile prunes any
/// section whose protocol is no longer embedded or is `deprecated:true`; a
/// section for a skill merely not named this run is retained. Migration of
/// standalone files (Issue 2.2) is folded in by [`fold_standalone_rules`] before
/// the upsert.
/// When `dry_run` is set, the projection is computed (upserts, prunes,
/// migrations) but nothing is written or deleted — so `--dry-run --json` reports
/// exactly what a real run would do (Issue 2.4, C3).
pub fn install_rules_aggregate(
    acted_skills: &[String],
    rules_dir: &Path,
    dry_run: bool,
) -> Result<FlowWriteResult> {
    let mut sections = read_flow_sections(rules_dir);
    let migrated = fold_standalone_rules(&mut sections, rules_dir, dry_run)?;

    let mut upserted = Vec::new();
    for skill in acted_skills {
        for section in embedded_rule_sections(skill) {
            upserted.push(section.protocol.clone());
            flow::upsert_section(&mut sections, section);
        }
    }
    upserted.sort();
    upserted.dedup();

    let valid = embedded_valid_set();
    let (kept, pruned_sections) = flow::reconcile(sections, &valid);
    let mut pruned: Vec<String> = pruned_sections.into_iter().map(|s| s.protocol).collect();
    pruned.sort();

    if !dry_run {
        write_flow(rules_dir, &kept)?;
    }
    Ok(FlowWriteResult {
        flow_file: flow_path(rules_dir),
        upserted,
        pruned,
        migrated,
    })
}

/// Fold every `yf`-owned standalone rule file present in `rules_dir` into
/// `sections` and delete the standalone (Issue 2.2 migration, C4 option (a)).
///
/// On **any** install/upgrade write, every standalone whose basename matches a
/// `yf`-owned protocol — including protocols for skills **not** named in this run
/// — is folded into the aggregate and its standalone file deleted, so
/// `YOSHIKO_FLOW.md` becomes the sole `yf` ruleset. The folded section preserves
/// the **standalone's** bytes (not the embedded source), so a not-yet-upgraded
/// skill keeps its installed content and `preflight`/`doctor` verdicts are
/// identical before and after migration (M3). When the aggregate already carries
/// the section (authoritative, R4), the redundant standalone is simply deleted.
/// Non-`yf` files (e.g. `BEADS.md` from `bd init`) never match and are untouched.
/// Idempotent: a second run finds no standalones and is a no-op.
fn fold_standalone_rules(
    sections: &mut Vec<FlowSection>,
    rules_dir: &Path,
    dry_run: bool,
) -> Result<Vec<String>> {
    let owned = owned_protocol_index();
    let mut migrated = Vec::new();
    for (protocol, (skill, version)) in &owned {
        let standalone = rules_dir.join(protocol);
        if !standalone.is_file() {
            continue;
        }
        let bytes = std::fs::read(&standalone)
            .with_context(|| format!("reading {}", standalone.display()))?;
        // Only fold when the aggregate does not already own this section (R4).
        if !sections.iter().any(|s| &s.protocol == protocol) {
            let body = String::from_utf8_lossy(&bytes).into_owned();
            flow::upsert_section(
                sections,
                FlowSection::new(skill, protocol, version.clone(), body),
            );
        }
        if !dry_run {
            std::fs::remove_file(&standalone)
                .with_context(|| format!("removing standalone {}", standalone.display()))?;
        }
        migrated.push(protocol.clone());
    }
    migrated.sort();
    migrated.dedup();
    Ok(migrated)
}

/// Map every `yf`-owned protocol basename to its `(skill, version)` across the
/// embedded tree. The key set is exactly the standalone basenames migration may
/// fold; a file whose name is not a key is never `yf`-owned.
fn owned_protocol_index() -> BTreeMap<String, (String, Option<String>)> {
    let mut index = BTreeMap::new();
    for skill in embed::skill_names() {
        let manifest = embedded_manifest(&skill);
        for (protocol, _bytes) in embedded_rules(&skill) {
            let version = manifest_version(manifest.as_ref(), &protocol);
            index.insert(protocol, (skill.clone(), version));
        }
    }
    index
}

/// The [`FlowSection`]s a skill contributes — one per `protocols/*.md`, with
/// `version` taken from the skill's `protocols/manifest.json` entry when present
/// (the two manifest-less protocols carry `None`).
pub fn embedded_rule_sections(skill: &str) -> Vec<FlowSection> {
    let manifest = embedded_manifest(skill);
    embedded_rules(skill)
        .into_iter()
        .map(|(protocol, bytes)| {
            let body = String::from_utf8_lossy(&bytes).into_owned();
            let version = manifest_version(manifest.as_ref(), &protocol);
            FlowSection::new(skill, &protocol, version, body)
        })
        .collect()
}

/// The set of `(skill, protocol)` pairs that are embedded AND not
/// `deprecated:true` — reconcile's authoritative valid set (S1+). Manifest-less
/// protocols are valid (not deprecated, just version-less).
pub fn embedded_valid_set() -> BTreeSet<(String, String)> {
    let mut set = BTreeSet::new();
    for skill in embed::skill_names() {
        let manifest = embedded_manifest(&skill);
        for (protocol, _bytes) in embedded_rules(&skill) {
            if !manifest_deprecated(manifest.as_ref(), &protocol) {
                set.insert((skill.clone(), protocol));
            }
        }
    }
    set
}

/// The installed bytes of a protocol's rule content in `dir`: the aggregate
/// section body when `YOSHIKO_FLOW.md` is present (authoritative), else the
/// legacy standalone `dir/<protocol>` file (transition-release fallback, S5).
/// Returns the bytes and the source path. `None` when neither is present, or the
/// aggregate exists but lacks the section (pruned → treated as missing).
pub fn installed_rule_source(dir: &Path, protocol: &str) -> Option<(Vec<u8>, PathBuf)> {
    let flow_file = flow_path(dir);
    if flow_file.is_file() {
        let text = std::fs::read_to_string(&flow_file).ok()?;
        let body = flow::parse(&text)
            .into_iter()
            .find(|s| s.protocol == protocol)?
            .body;
        return Some((body.into_bytes(), flow_file));
    }
    let legacy = dir.join(protocol);
    let bytes = std::fs::read(&legacy).ok()?;
    Some((bytes, legacy))
}

/// Read an embedded skill's `protocols/manifest.json` as JSON (if present/valid).
fn embedded_manifest(skill: &str) -> Option<serde_json::Value> {
    embed::read_file(&format!("{skill}/protocols/manifest.json"))
        .and_then(|b| serde_json::from_slice(&b).ok())
}

/// The manifest `version` for a protocol basename, if the entry exists.
fn manifest_version(manifest: Option<&serde_json::Value>, protocol: &str) -> Option<String> {
    manifest?
        .get("files")?
        .get(protocol)?
        .get("version")
        .and_then(serde_json::Value::as_str)
        .map(str::to_string)
}

/// Whether the manifest marks a protocol `deprecated:true`.
fn manifest_deprecated(manifest: Option<&serde_json::Value>, protocol: &str) -> bool {
    manifest
        .and_then(|m| m.get("files"))
        .and_then(|f| f.get(protocol))
        .and_then(|e| e.get("deprecated"))
        .and_then(serde_json::Value::as_bool)
        .unwrap_or(false)
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

/// One unique install destination after per-path dedupe (REQ-YF-INSTALL-002).
pub struct ResolvedDest {
    /// The harness id whose descriptor produced this destination. Drives the
    /// skill-name transform applied by [`deploy_skill`].
    pub harness: String,
    /// The resolved skills directory.
    pub skills_dir: PathBuf,
}

/// The harness ids a `skills` invocation acts on, resolving the no-`--harness`
/// case by **auto-detection** (REQ-YF-INSTALL-009).
///
/// Precedence: an explicit `--harness` (or the deprecated `--surface`) **always
/// overrides** detection and is returned verbatim via
/// [`SkillsArgs::resolved_harnesses`]. A `--target` also skips detection — the
/// destination is a single fixed dir there, so only the name-transform-governing
/// primary id matters (the historical `claude-code` default). Otherwise, with no
/// explicit selection and no target, `yf` detects installed harnesses from the
/// real environment ([`harness_detect::detect_from_env`]) and acts on all
/// detected; when nothing is detected it falls back to the historical
/// `claude-code` default so a bare install still targets something.
pub fn effective_harnesses(args: &SkillsArgs) -> Vec<String> {
    if !args.harness.is_empty() || args.surface.is_some() || args.target.is_some() {
        return args.resolved_harnesses();
    }
    let detected = harness_detect::detect_from_env(args.scope);
    if detected.is_empty() {
        vec!["claude-code".to_string()]
    } else {
        detected
    }
}

/// Resolve every requested `--harness` (plus a deprecated `--surface`) to its
/// skills destination and **dedupe by resolved absolute path**
/// (REQ-YF-INSTALL-002): two harnesses that resolve to the same directory — e.g.
/// `codex` and `agents`, both `.agents/skills` — collapse to a **single**
/// destination, so a skill is written there exactly once. Order follows first
/// appearance. When `--target` is set, every harness resolves to that one dir, so
/// the result is a single destination carrying the first harness's id (which
/// governs the name transform). A deprecated `--surface` is warned to stderr
/// (never to `--json` stdout).
pub fn resolved_dests(args: &SkillsArgs) -> Vec<ResolvedDest> {
    if args.surface.is_some() {
        eprintln!(
            "warning: `--surface` is a deprecated alias for `--harness` and will be removed \
             in the next major release; use `--harness`."
        );
    }
    let target = args.target.as_deref();
    let mut seen: BTreeSet<PathBuf> = BTreeSet::new();
    let mut out: Vec<ResolvedDest> = Vec::new();
    for harness in effective_harnesses(args) {
        let skills_dir = dest::resolve_skills_dir(args.scope, &harness, target);
        if seen.insert(skills_dir.clone()) {
            out.push(ResolvedDest {
                harness,
                skills_dir,
            });
        }
    }
    out
}

/// Resolve `(skills_dir, rules_dir)` from a `skills` subcommand's args.
///
/// Issue 2.1 resolves the **primary** harness only (first `--harness`, else the
/// deprecated `--surface` alias, else `claude-code`); repeatable-harness dedupe /
/// multi-write is Issue 2.2. A deprecated `--surface` is warned to stderr (never
/// to `--json` stdout).
pub fn dirs_for(args: &SkillsArgs) -> (PathBuf, PathBuf) {
    if args.surface.is_some() {
        eprintln!(
            "warning: `--surface` is a deprecated alias for `--harness` and will be removed \
             in the next major release; use `--harness`."
        );
    }
    let target = args.target.as_deref();
    // Single-destination verbs (status/upgrade/remove): the primary of the
    // effective set, which auto-detects in the no-`--harness` case
    // (REQ-YF-INSTALL-009) and otherwise honors the explicit selection.
    let harness = effective_harnesses(args)
        .into_iter()
        .next()
        .unwrap_or_else(|| "claude-code".to_string());
    (
        dest::resolve_skills_dir(args.scope, &harness, target),
        dest::resolve_rules_dir(args.scope, &harness, target),
    )
}

/// Same, but spelled out for callers that already have the pieces (doctor).
pub fn dirs_from(scope: Scope, harness: &str) -> (PathBuf, PathBuf) {
    (
        dest::resolve_skills_dir(scope, harness, None),
        dest::resolve_rules_dir(scope, harness, None),
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

#[cfg(test)]
mod flow_tests {
    use super::*;

    // REQ-YF-FLOW (S3/2.1): installing rule-bearing skills writes ONE aggregate
    // YOSHIKO_FLOW.md with their sections — no standalone rule files — and each
    // section body equals the embedded protocol verbatim.
    #[test]
    fn aggregate_install_writes_single_flow_file() {
        let tmp = tempfile::tempdir().unwrap();
        let rules = tmp.path().join("rules");
        let res = install_rules_aggregate(
            &["yf-beads-init".to_string(), "yf-plan".to_string()],
            &rules,
            false,
        )
        .unwrap();

        let flow_file = rules.join(flow::FLOW_FILENAME);
        assert!(flow_file.is_file(), "aggregate file must be written");
        assert!(
            !rules.join("BEADS_INIT.md").exists(),
            "no standalone rule file"
        );
        assert!(!rules.join("PLANS.md").exists(), "no standalone rule file");

        let text = std::fs::read_to_string(&flow_file).unwrap();
        let sections = flow::parse(&text);
        let protos: Vec<&str> = sections.iter().map(|s| s.protocol.as_str()).collect();
        assert!(protos.contains(&"BEADS_INIT.md"));
        assert!(protos.contains(&"PLANS.md"));
        assert!(res.upserted.contains(&"BEADS_INIT.md".to_string()));

        let section = sections
            .iter()
            .find(|s| s.protocol == "BEADS_INIT.md")
            .unwrap();
        let embedded = embedded_rules("yf-beads-init")
            .into_iter()
            .find(|(p, _)| p == "BEADS_INIT.md")
            .unwrap()
            .1;
        assert_eq!(section.body.as_bytes(), embedded.as_slice());
    }

    // REQ-YF-FLOW (R3/2.1): re-installing the same skill is byte-stable.
    #[test]
    fn aggregate_reinstall_is_byte_stable() {
        let tmp = tempfile::tempdir().unwrap();
        let rules = tmp.path().join("rules");
        install_rules_aggregate(&["yf-plan".to_string()], &rules, false).unwrap();
        let first = std::fs::read_to_string(rules.join(flow::FLOW_FILENAME)).unwrap();
        install_rules_aggregate(&["yf-plan".to_string()], &rules, false).unwrap();
        let second = std::fs::read_to_string(rules.join(flow::FLOW_FILENAME)).unwrap();
        assert_eq!(first, second, "re-install must be byte-stable");
    }

    // REQ-YF-FLOW-003 (2.2/C4a): migration folds EVERY yf-owned standalone present —
    // including one for a skill NOT named this run — into the aggregate, deletes
    // each standalone, preserves the standalone's bytes, and leaves non-yf files
    // (BEADS.md) untouched.
    #[test]
    fn migration_folds_all_standalones_keeps_foreign() {
        let tmp = tempfile::tempdir().unwrap();
        let rules = tmp.path().join("rules");
        std::fs::create_dir_all(&rules).unwrap();

        // Pre-seed standalones: PLANS.md (will be acted on) + RESEARCH.md (NOT
        // acted on this run) with custom bytes, plus a foreign BEADS.md.
        std::fs::write(rules.join("PLANS.md"), b"OLD PLANS BYTES\n").unwrap();
        std::fs::write(rules.join("RESEARCH.md"), b"OLD RESEARCH BYTES\n").unwrap();
        std::fs::write(rules.join("BEADS.md"), b"from bd init\n").unwrap();

        // Install only yf-plan.
        let res = install_rules_aggregate(&["yf-plan".to_string()], &rules, false).unwrap();

        // All yf-owned standalones gone; the aggregate exists; foreign file kept.
        assert!(!rules.join("PLANS.md").exists());
        assert!(!rules.join("RESEARCH.md").exists());
        assert!(rules.join("BEADS.md").exists(), "foreign rule untouched");
        assert!(res.migrated.contains(&"RESEARCH.md".to_string()));

        let text = std::fs::read_to_string(rules.join(flow::FLOW_FILENAME)).unwrap();
        let sections = flow::parse(&text);
        // RESEARCH.md (not acted on) folded with its OLD standalone bytes preserved.
        let research = sections
            .iter()
            .find(|s| s.protocol == "RESEARCH.md")
            .unwrap();
        assert_eq!(research.body, "OLD RESEARCH BYTES\n");
        // PLANS.md (acted on) rewritten to the embedded source.
        let plans = sections.iter().find(|s| s.protocol == "PLANS.md").unwrap();
        let embedded = embedded_rules("yf-plan")
            .into_iter()
            .find(|(p, _)| p == "PLANS.md")
            .unwrap()
            .1;
        assert_eq!(plans.body.as_bytes(), embedded.as_slice());
    }

    // REQ-YF-FLOW (2.4/C3): a dry-run projects the change set (upserts/migrations)
    // but writes nothing and deletes no standalone.
    #[test]
    fn dry_run_projects_without_writing() {
        let tmp = tempfile::tempdir().unwrap();
        let rules = tmp.path().join("rules");
        std::fs::create_dir_all(&rules).unwrap();
        std::fs::write(rules.join("RESEARCH.md"), b"OLD\n").unwrap();

        let res =
            install_rules_aggregate(&["yf-plan".to_string()], &rules, /*dry_run=*/ true).unwrap();

        // Projection populated...
        assert!(res.upserted.contains(&"PLANS.md".to_string()));
        assert!(res.migrated.contains(&"RESEARCH.md".to_string()));
        // ...but nothing on disk changed.
        assert!(
            !rules.join(flow::FLOW_FILENAME).exists(),
            "no aggregate written"
        );
        assert!(rules.join("RESEARCH.md").exists(), "standalone not deleted");
    }

    // REQ-YF-FLOW (2.2): migration is idempotent — a second run finds no
    // standalones and the aggregate is unchanged.
    #[test]
    fn migration_is_idempotent() {
        let tmp = tempfile::tempdir().unwrap();
        let rules = tmp.path().join("rules");
        std::fs::create_dir_all(&rules).unwrap();
        std::fs::write(rules.join("RESEARCH.md"), b"OLD\n").unwrap();
        install_rules_aggregate(&["yf-plan".to_string()], &rules, false).unwrap();
        let first = std::fs::read_to_string(rules.join(flow::FLOW_FILENAME)).unwrap();
        let res2 = install_rules_aggregate(&["yf-plan".to_string()], &rules, false).unwrap();
        let second = std::fs::read_to_string(rules.join(flow::FLOW_FILENAME)).unwrap();
        assert_eq!(first, second, "second run is a no-op on the file");
        assert!(res2.migrated.is_empty(), "no standalones left to migrate");
    }
}

#[cfg(test)]
mod dest_dedupe_tests {
    use super::*;
    use crate::cli::{Scope, SkillsArgs};

    fn args_with_harnesses(harness: Vec<String>) -> SkillsArgs {
        SkillsArgs {
            names: Vec::new(),
            scope: Scope::User,
            harness,
            surface: None,
            target: None,
            group: None,
            strict: false,
            force: false,
            dry_run: false,
            prune: false,
            tune: false,
            rules_only: false,
            allow_permissions_write: false,
            yes: false,
            json: false,
        }
    }

    // REQ-YF-INSTALL-002: `--harness codex --harness agents` both resolve to
    // `.agents/skills`, so dedupe-by-resolved-path yields exactly ONE destination
    // (a single write), not two.
    #[test]
    fn codex_and_agents_dedupe_to_one_destination() {
        let args = args_with_harnesses(vec!["codex".to_string(), "agents".to_string()]);
        let dests = resolved_dests(&args);
        assert_eq!(
            dests.len(),
            1,
            "codex and agents resolve to the same dir → one deduped destination"
        );
        assert!(
            dests[0].skills_dir.ends_with(".agents/skills"),
            "the single destination is the shared .agents/skills dir: {:?}",
            dests[0].skills_dir
        );
    }

    // REQ-YF-INSTALL-009: an explicit `--harness` BYPASSES auto-detection — the
    // effective set is exactly the requested ids, regardless of what the ambient
    // environment has installed. (Detection only runs in the no-`--harness` case.)
    #[test]
    fn explicit_harness_bypasses_detection() {
        let args = args_with_harnesses(vec!["pi".to_string()]);
        assert_eq!(
            effective_harnesses(&args),
            vec!["pi".to_string()],
            "explicit --harness must be returned verbatim, never detection"
        );
        // The resolved destination is pi's, not a detected harness's.
        let dests = resolved_dests(&args);
        assert_eq!(dests.len(), 1);
        assert_eq!(dests[0].harness, "pi");
    }

    // REQ-YF-INSTALL-009: a `--target` also bypasses detection — the primary id
    // stays the historical `claude-code` default, so the name transform is stable
    // and the (single) destination is env-independent.
    #[test]
    fn target_bypasses_detection() {
        let mut args = args_with_harnesses(Vec::new());
        args.target = Some(PathBuf::from("/tmp/fixed/skills"));
        assert_eq!(effective_harnesses(&args), vec!["claude-code".to_string()]);
    }

    // REQ-YF-INSTALL-002: distinct harnesses keep distinct destinations, in
    // first-appearance order.
    #[test]
    fn distinct_harnesses_keep_distinct_destinations() {
        let args = args_with_harnesses(vec![
            "claude-code".to_string(),
            "codex".to_string(),
            "agents".to_string(),
        ]);
        let dests = resolved_dests(&args);
        // claude-code → .claude/skills; codex & agents collapse to .agents/skills.
        assert_eq!(dests.len(), 2, "two unique resolved paths");
        assert!(dests[0].skills_dir.ends_with(".claude/skills"));
        assert!(dests[1].skills_dir.ends_with(".agents/skills"));
    }
}
