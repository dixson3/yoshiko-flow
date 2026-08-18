//! The sidecar `.yf/` ownership manifest (REQ-YF-TUNE-021).
//!
//! Records exactly what a `yf harness tune` wrote — per tuned surface (harness ×
//! scope) — so Issue 8.2's `yf harness tune --revert` (REQ-YF-TUNE-022) can reverse
//! it precisely without clobbering operator content.
//!
//! Three things are recorded per surface:
//!
//! 1. **Config keys yf added** — each dot-path yf wrote, with BOTH the **prior**
//!    on-disk value (where one existed) AND the **yf-written** value. The dual
//!    capture is what 8.2's *touched-since-tune guard* consumes: before reverting a
//!    key it compares the key's current on-disk value to the recorded `written`
//!    value, restoring `prior` (or removing the key when there was none) only if they
//!    still match. A **pure add** records `prior_present: false` (`prior: null`); a
//!    **forced scalar** records the merge report's captured `from` in `prior`.
//! 2. **Set unions** — for each set path, ONLY the elements yf actually **added**
//!    (the `MergeReport` `SetUnioned.added` list, never the whole set), so revert
//!    removes only yf's additions and leaves operator entries.
//! 3. **Rule managed-block markers** — the rule file plus the BEGIN/END marker
//!    identifiers of each managed block yf deployed, so revert removes exactly that
//!    span and leaves surrounding prose. A whole-file aggregate (claude-code's
//!    `rules/` dir) is recorded as `kind: "aggregate"` with no markers.
//!
//! ## Location convention (REQ-YF-TUNE-021)
//!
//! - **User scope:** `<surface_dir>/.yf/harness-tune-manifest.json` beside the tuned
//!   surface — one per harness surface (e.g. `~/.codex/.yf/…`, `~/.pi/agent/.yf/…`).
//! - **Project scope:** a single `<project-root>/.yf/harness-tune-manifest.json` at
//!   the repo root, and `.yf/` is idempotently added to the project `.gitignore`
//!   (matching the existing `/.yf/` anchor convention in `migrate.rs`).
//!
//! The manifest is **cumulative-ownership**: a re-tune folds fresh records into the
//! existing manifest (preserving the earliest-recorded `prior` for a key, unioning
//! set additions) rather than clobbering it — so an idempotent re-tune never loses
//! what an earlier tune recorded. A **dry-run never writes a manifest**.
//!
//! ## Schema (the contract Issue 8.2 consumes)
//!
//! ```json
//! {
//!   "version": 1,
//!   "surfaces": {
//!     "<harness>:<scope>": {
//!       "harness": "codex",
//!       "scope": "user",
//!       "config": {
//!         "path": "/home/jd/.codex/config.toml",
//!         "keys_added": [
//!           { "path": "approval_policy", "prior_present": false, "prior": null, "written": "never" },
//!           { "path": "effortLevel", "prior_present": true, "prior": "high", "written": "medium" }
//!         ],
//!         "sets_unioned": [ { "path": "permissions.deny", "added": ["TaskCreate"] } ]
//!       },
//!       "rules": {
//!         "path": "/home/jd/.codex/AGENTS.md",
//!         "kind": "block",
//!         "begin_marker": "<!-- BEGIN yf-managed-rules -->",
//!         "end_marker": "<!-- END yf-managed-rules -->"
//!       }
//!     }
//!   }
//! }
//! ```

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use serde_json::Value;

use super::managed_block;
use super::merge::{Change, MergeReport};
use super::settings::TuneScope;

/// The manifest filename living under the sidecar `.yf/` dir.
pub const MANIFEST_FILENAME: &str = "harness-tune-manifest.json";
/// The current manifest schema version — 8.2's `--revert` reads this.
pub const MANIFEST_VERSION: u32 = 1;

/// One config scalar key yf wrote, with BOTH the prior on-disk value (where one
/// existed) AND the yf-written value — the dual capture 8.2's touched-since-tune
/// guard needs (REQ-YF-TUNE-021).
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ConfigKeyRecord {
    /// The dot-path yf wrote (e.g. `permissions.defaultMode`).
    pub path: String,
    /// Whether a prior value existed on disk before yf wrote — `false` = pure add.
    pub prior_present: bool,
    /// The captured prior value (a forced scalar's `from`); `null` for a pure add.
    #[serde(default)]
    pub prior: Option<Value>,
    /// The value yf wrote (a scalar's `value` / forced `to`).
    pub written: Value,
}

/// One set-valued key yf unioned into — records ONLY the elements yf actually added
/// (never the whole set), so revert removes yf's additions and leaves operator
/// entries (REQ-YF-TUNE-021).
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct SetUnionRecord {
    /// The set's dot-path (e.g. `permissions.deny`).
    pub path: String,
    /// The elements yf appended (the `MergeReport` `SetUnioned.added` list).
    pub added: Vec<Value>,
}

/// The config sub-op's ownership record for one surface.
#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
pub struct ConfigRecord {
    /// The tuned config file.
    pub path: String,
    /// Scalar keys yf added/forced, each with prior + written.
    pub keys_added: Vec<ConfigKeyRecord>,
    /// Set-valued keys yf unioned into, each with only yf's added elements.
    pub sets_unioned: Vec<SetUnionRecord>,
}

impl ConfigRecord {
    /// Whether this record carries any yf write (else there is nothing to record).
    fn is_empty(&self) -> bool {
        self.keys_added.is_empty() && self.sets_unioned.is_empty()
    }
}

/// The rule sub-op's ownership record for one surface.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct RuleRecord {
    /// The rule file yf deployed into.
    pub path: String,
    /// `block` — a managed BEGIN/END span sharing a file with operator prose; or
    /// `aggregate` — a whole-file aggregate (claude-code's `rules/` dir).
    pub kind: String,
    /// The BEGIN marker identifier of the deployed managed block (`block` kind only).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub begin_marker: Option<String>,
    /// The END marker identifier of the deployed managed block (`block` kind only).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub end_marker: Option<String>,
    /// SHA-256 of the rule file **as yf wrote it** (REQ-YF-TUNE-029, plan-044 #154).
    ///
    /// This is the rules-side analogue of the config half's recorded yf-written
    /// value: it is what `--revert`'s touched-since-tune guard compares the current
    /// on-disk file against. A mismatch means the operator hand-edited the file
    /// since the tune, so revert **keeps and reports** it rather than deleting.
    ///
    /// `Option` because a manifest written before this field existed carries none.
    /// An absent sha is treated as "cannot prove it is untouched", which is the
    /// conservative direction — see the revert branch.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub sha256: Option<String>,
}

/// One tuned surface (harness × scope) ownership record.
#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
pub struct SurfaceRecord {
    /// The harness id (`--harness` value).
    pub harness: String,
    /// The scope label (`user` / `project-local` / `project-committed`).
    pub scope: String,
    /// The config sub-op record, when a config profile shipped and aligned.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub config: Option<ConfigRecord>,
    /// The rule sub-op record, when a rule target deployed.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub rules: Option<RuleRecord>,
}

/// The sidecar ownership manifest document (REQ-YF-TUNE-021).
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Manifest {
    /// Schema version (see [`MANIFEST_VERSION`]).
    pub version: u32,
    /// Per-surface ownership records keyed by `<harness>:<scope>`.
    pub surfaces: BTreeMap<String, SurfaceRecord>,
}

impl Default for Manifest {
    fn default() -> Self {
        Manifest {
            version: MANIFEST_VERSION,
            surfaces: BTreeMap::new(),
        }
    }
}

/// The `<harness>:<scope>` surface key a [`SurfaceRecord`] is stored under — the key
/// `--revert` (Issue 8.2) looks a surface up by.
pub fn surface_key(harness: &str, scope: TuneScope) -> String {
    format!("{harness}:{}", scope_key(scope))
}

/// The scope's stable manifest key/label.
fn scope_key(scope: TuneScope) -> &'static str {
    match scope {
        TuneScope::User => "user",
        TuneScope::ProjectLocal => "project-local",
        TuneScope::ProjectCommitted => "project-committed",
    }
}

/// The sidecar `.yf/` manifest path for `harness` at `scope`, anchored at `home`
/// (user) or `root` (project). Pure — no env reads.
///
/// - **User scope:** `<home>/<surface_dir>/.yf/harness-tune-manifest.json` — beside
///   the tuned surface (the harness's rule-target surface dir).
/// - **Project scope:** `<root>/.yf/harness-tune-manifest.json` — one manifest at the
///   repo root for all project-scope surfaces.
///
/// Returns `None` for an unmapped harness (no surface to record against).
pub fn manifest_path_at(
    harness: &str,
    scope: TuneScope,
    home: &Path,
    root: &Path,
) -> Option<PathBuf> {
    match scope {
        TuneScope::User => {
            let surface = managed_block::rule_target(harness)?.surface_dir;
            Some(home.join(surface).join(".yf").join(MANIFEST_FILENAME))
        }
        TuneScope::ProjectLocal | TuneScope::ProjectCommitted => {
            Some(root.join(".yf").join(MANIFEST_FILENAME))
        }
    }
}

/// Build a [`ConfigRecord`] from a [`MergeReport`]: every scalar yf added/forced
/// (with prior + written) and every set yf unioned into (only the added elements).
/// Conflicts and type conflicts are NOT yf writes and are skipped.
pub fn config_record_from_report(path: &Path, report: &MergeReport) -> ConfigRecord {
    let mut keys_added = Vec::new();
    let mut sets_unioned = Vec::new();
    for c in &report.changes {
        match c {
            Change::ScalarAdded { path, value } => keys_added.push(ConfigKeyRecord {
                path: path.clone(),
                prior_present: false,
                prior: None,
                written: value.clone(),
            }),
            Change::ScalarForced { path, from, to } => keys_added.push(ConfigKeyRecord {
                path: path.clone(),
                prior_present: true,
                prior: Some(from.clone()),
                written: to.clone(),
            }),
            Change::SetUnioned { path, added } => sets_unioned.push(SetUnionRecord {
                path: path.clone(),
                added: added.clone(),
            }),
            // ScalarConflict / SetTypeConflict were left untouched — yf wrote nothing.
            Change::ScalarConflict { .. } | Change::SetTypeConflict { .. } => {}
        }
    }
    ConfigRecord {
        path: path.display().to_string(),
        keys_added,
        sets_unioned,
    }
}

/// Fold a freshly-computed config record into any existing one — cumulative
/// ownership across re-tunes. Preserves the **earliest-recorded** `prior` for a
/// re-tuned key (only `written` advances to the latest value) and unions set
/// additions, so an idempotent re-tune never corrupts or drops what an earlier tune
/// recorded.
fn merge_config(existing: Option<ConfigRecord>, fresh: ConfigRecord) -> ConfigRecord {
    let Some(mut base) = existing else {
        return fresh;
    };
    base.path = fresh.path;
    for k in fresh.keys_added {
        if let Some(prev) = base.keys_added.iter_mut().find(|e| e.path == k.path) {
            // Keep the original prior (the true pre-yf value); advance written.
            prev.written = k.written;
        } else {
            base.keys_added.push(k);
        }
    }
    for s in fresh.sets_unioned {
        if let Some(prev) = base.sets_unioned.iter_mut().find(|e| e.path == s.path) {
            for v in s.added {
                if !prev.added.iter().any(|e| e == &v) {
                    prev.added.push(v);
                }
            }
        } else {
            base.sets_unioned.push(s);
        }
    }
    base
}

/// Record what a tune wrote into the sidecar ownership manifest (REQ-YF-TUNE-021).
///
/// A **no-op on `dry_run`** (never writes). Merges into any existing manifest so a
/// re-tune updates ownership without corrupting prior records. In **project scope**
/// it also idempotently gitignores `.yf/`.
///
/// `config`/`rules` are the sub-op ownership records; both `None` (nothing yf owns on
/// this surface) is a no-op.
pub fn record_tune(
    harness: &str,
    scope: TuneScope,
    home: &Path,
    root: &Path,
    config: Option<ConfigRecord>,
    rules: Option<RuleRecord>,
    dry_run: bool,
) -> Result<()> {
    if dry_run {
        return Ok(());
    }
    // Drop an empty config record (an already-aligned tune wrote nothing new).
    let config = config.filter(|c| !c.is_empty());
    if config.is_none() && rules.is_none() {
        return Ok(());
    }
    let Some(path) = manifest_path_at(harness, scope, home, root) else {
        return Ok(());
    };

    let mut manifest = load(&path)?;
    let key = format!("{harness}:{}", scope_key(scope));
    let entry = manifest
        .surfaces
        .entry(key)
        .or_insert_with(|| SurfaceRecord {
            harness: harness.to_string(),
            scope: scope_key(scope).to_string(),
            config: None,
            rules: None,
        });
    if let Some(fresh) = config {
        entry.config = Some(merge_config(entry.config.take(), fresh));
    }
    if let Some(r) = rules {
        entry.rules = Some(r);
    }
    write(&path, &manifest)?;

    if matches!(scope, TuneScope::ProjectLocal | TuneScope::ProjectCommitted) {
        ensure_gitignored(root)?;
    }
    Ok(())
}

/// Load an existing ownership manifest for `yf harness tune --revert` (Issue 8.2),
/// or a fresh empty one when absent — the public entry point the revert flow reads.
/// A malformed manifest is a hard error (it is yf-owned state).
pub fn load_manifest(path: &Path) -> Result<Manifest> {
    load(path)
}

/// Persist an ownership manifest after `--revert` consumed (cleared) the surfaces it
/// reversed (Issue 8.2), so a second revert is a no-op. Writes pretty JSON, creating
/// the `.yf/` parent dir.
pub fn save_manifest(path: &Path, manifest: &Manifest) -> Result<()> {
    write(path, manifest)
}

/// Load an existing manifest, or a fresh empty one when absent. A malformed manifest
/// is a hard error (it is yf-owned state — never silently overwrite ownership).
fn load(path: &Path) -> Result<Manifest> {
    match std::fs::read_to_string(path) {
        Ok(text) => serde_json::from_str(&text)
            .with_context(|| format!("parsing ownership manifest {}", path.display())),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(Manifest::default()),
        Err(e) => Err(anyhow::anyhow!(
            "cannot read ownership manifest {}: {e}",
            path.display()
        )),
    }
}

/// Write the manifest as pretty JSON with a trailing newline, creating the `.yf/`
/// parent dir.
fn write(path: &Path, manifest: &Manifest) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut text = serde_json::to_string_pretty(manifest)?;
    text.push('\n');
    std::fs::write(path, text)?;
    Ok(())
}

/// Idempotently ensure the project `.gitignore` ignores the sidecar `.yf/` dir
/// (REQ-YF-TUNE-021, project scope). Recognizes the existing `/.yf/` anchor
/// convention (`migrate.rs`) so it never duplicates the entry.
fn ensure_gitignored(root: &Path) -> Result<()> {
    let gitignore = root.join(".gitignore");
    let existing = match std::fs::read_to_string(&gitignore) {
        Ok(t) => t,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => String::new(),
        Err(e) => return Err(anyhow::anyhow!("cannot read {}: {e}", gitignore.display())),
    };
    // Already covered by any `.yf/` anchor spelling → idempotent no-op.
    if existing.lines().any(|l| {
        let t = l.trim();
        t == "/.yf/" || t == ".yf/" || t == "/.yf" || t == ".yf"
    }) {
        return Ok(());
    }
    let mut out = existing;
    if !out.is_empty() && !out.ends_with('\n') {
        out.push('\n');
    }
    if !out.is_empty() {
        out.push('\n');
    }
    out.push_str("# yf harness-tune ownership manifest + skill runtime state (never committed)\n");
    out.push_str("/.yf/\n");
    std::fs::write(&gitignore, out)?;
    Ok(())
}
