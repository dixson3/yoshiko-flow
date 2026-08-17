//! `yf harness tune --revert` — reverse a prior tune (Issue 8.2, REQ-YF-TUNE-022).
//!
//! Revert is driven **entirely** off the sidecar `.yf/` ownership manifest
//! ([`super::manifest`]) that a tune recorded — never the profile/merge engine. It
//! undoes **only** yf's own additions:
//!
//! - **Config keys** (`keys_added`): each recorded key is reverted under a
//!   **touched-since-tune guard**. Read the key's *current* on-disk value and compare
//!   it to the manifest's recorded `written` value:
//!   - **match** (untouched since tune) → restore the recorded `prior` when
//!     `prior_present`, else remove the key entirely;
//!   - **differ** (operator hand-edited it since the tune) → **conservative-keep and
//!     report**; never clobber the operator's value.
//! - **Set unions** (`sets_unioned`): remove **only** the elements yf recorded as
//!   `added` (one occurrence each), leaving every operator entry — including a copy an
//!   operator independently re-added (the conservative choice on the ambiguous case).
//! - **Rule blocks** (`RuleRecord`): a `block` kind removes exactly the
//!   `BEGIN`..`END` managed span via [`super::managed_block::remove_block`], preserving
//!   surrounding prose; an `aggregate` kind (claude-code whole-file) removes the
//!   yf-authored aggregate file (a fully yf-managed artifact).
//!
//! **Format dispatch.** Config read/write branches on the recorded file's extension:
//! a `config.toml` is edited through a trivia-preserving [`toml_edit::DocumentMut`]
//! (operator comments / key order survive), everything else through the JSON path.
//!
//! **Fail-safe + idempotent.** A malformed target file (unparseable JSON/TOML, or
//! ambiguous rule markers) is refused for that surface — reported, never corrupted.
//! After a surface's revert completes, its consumed manifest entries are cleared so a
//! **second `--revert` is a no-op**. Revert only ever *removes* what yf added — it
//! never adds a deny — so the `Agent`-never-denied invariant holds structurally.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use anyhow::{bail, Result};
use serde_json::{json, Value};
use toml_edit::{DocumentMut, Item, Table};

use super::managed_block::{self, BlockRemoval};
use super::manifest::{self, ConfigKeyRecord, Manifest, SetUnionRecord, SurfaceRecord};
use super::settings::{self, SettingsRead, TomlRead, TuneScope};
use crate::cli::HarnessTuneArgs;

/// Env-based entry: reverse a prior tune for the requested harness(es).
pub fn run(args: &HarnessTuneArgs) -> Result<ExitCode> {
    let scope = TuneScope::resolve(args.project, args.committed);
    let home = super::home_dir();
    let root = crate::dest::git_root_or_cwd();
    let harnesses = super::resolve_harness_list(args);
    let reverts = revert_all_at(&harnesses, scope, &home, &root, args.dry_run)?;
    let any_failure = reverts.iter().any(SurfaceRevert::is_failure);
    report(args, &reverts);
    Ok(if any_failure {
        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    })
}

/// The config sub-op's revert outcome for one surface.
#[derive(Debug)]
enum ConfigRevert {
    /// No config record for this surface — nothing to revert.
    None,
    /// A malformed/unparseable target — fail-safe refusal; the file is untouched and
    /// the manifest record is NOT consumed.
    Refused { message: String },
    /// The revert ran to completion (some keys may be conservative-kept).
    Done {
        path: PathBuf,
        restored: Vec<String>,
        removed: Vec<String>,
        kept: Vec<String>,
        sets_removed: Vec<(String, usize)>,
        wrote: bool,
    },
}

/// The rule sub-op's revert outcome for one surface.
#[derive(Debug)]
enum RuleRevert {
    /// No rule record for this surface.
    None,
    /// A malformed target (ambiguous markers) — fail-safe refusal, file untouched.
    Refused { message: String },
    /// A managed block was removed (or was already absent).
    Block {
        path: PathBuf,
        removed: bool,
        wrote: bool,
    },
    /// A whole-file aggregate was removed (or was already absent).
    Aggregate {
        path: PathBuf,
        removed: bool,
        wrote: bool,
    },
}

/// One surface's unified revert verdict.
#[derive(Debug)]
struct SurfaceRevert {
    harness: String,
    scope: String,
    /// True when this surface had no manifest record at all (nothing to revert).
    absent: bool,
    config: ConfigRevert,
    rules: RuleRevert,
}

impl SurfaceRevert {
    /// A surface revert fails iff either sub-op refused (fail-safe on a malformed
    /// target). A conservative-keep is NOT a failure — it is the guard doing its job.
    fn is_failure(&self) -> bool {
        matches!(self.config, ConfigRevert::Refused { .. })
            || matches!(self.rules, RuleRevert::Refused { .. })
    }
}

/// Env-free core: revert every requested harness at explicit `home`/`root` anchors.
/// Manifests are loaded once per distinct path (project scope shares one repo-root
/// manifest across harnesses), the reverted surfaces are consumed (cleared), and each
/// modified manifest is saved once — unless `dry_run`, which writes nothing.
fn revert_all_at(
    harnesses: &[String],
    scope: TuneScope,
    home: &Path,
    root: &Path,
    dry_run: bool,
) -> Result<Vec<SurfaceRevert>> {
    // Load each distinct manifest path at most once (project scope shares one).
    let mut manifests: BTreeMap<PathBuf, Manifest> = BTreeMap::new();
    let mut dirty: BTreeMap<PathBuf, bool> = BTreeMap::new();
    let mut out = Vec::new();

    for harness in harnesses {
        let Some(mpath) = manifest::manifest_path_at(harness, scope, home, root) else {
            // Unmapped harness — no surface to revert against.
            out.push(SurfaceRevert {
                harness: harness.clone(),
                scope: scope.label().to_string(),
                absent: true,
                config: ConfigRevert::None,
                rules: RuleRevert::None,
            });
            continue;
        };
        if !manifests.contains_key(&mpath) {
            manifests.insert(mpath.clone(), manifest::load_manifest(&mpath)?);
            dirty.insert(mpath.clone(), false);
        }
        let key = manifest::surface_key(harness, scope);
        let record = manifests
            .get(&mpath)
            .and_then(|m| m.surfaces.get(&key).cloned());

        let Some(record) = record else {
            out.push(SurfaceRevert {
                harness: harness.clone(),
                scope: scope.label().to_string(),
                absent: true,
                config: ConfigRevert::None,
                rules: RuleRevert::None,
            });
            continue;
        };

        let config = revert_config(&record, dry_run)?;
        let rules = revert_rules(&record, dry_run)?;

        // Consume (clear) the records a completed sub-op reverted, so a second revert
        // is a no-op. A refusal keeps its record. Never mutate the manifest on dry-run.
        if !dry_run {
            let clear_config = !matches!(config, ConfigRevert::Refused { .. });
            let clear_rules = !matches!(rules, RuleRevert::Refused { .. });
            let m = manifests.get_mut(&mpath).expect("manifest loaded");
            if let Some(surface) = m.surfaces.get_mut(&key) {
                if clear_config {
                    surface.config = None;
                }
                if clear_rules {
                    surface.rules = None;
                }
                if surface.config.is_none() && surface.rules.is_none() {
                    m.surfaces.remove(&key);
                }
            }
            *dirty.get_mut(&mpath).unwrap() = true;
        }

        out.push(SurfaceRevert {
            harness: harness.clone(),
            scope: scope.label().to_string(),
            absent: false,
            config,
            rules,
        });
    }

    if !dry_run {
        for (path, was_dirty) in dirty {
            if was_dirty {
                if let Some(m) = manifests.get(&path) {
                    manifest::save_manifest(&path, m)?;
                }
            }
        }
    }

    Ok(out)
}

// ---------------------------------------------------------------------------
// Config revert (touched-since-tune guard + set-union removal).
// ---------------------------------------------------------------------------

fn revert_config(record: &SurfaceRecord, dry_run: bool) -> Result<ConfigRevert> {
    let Some(config) = record.config.as_ref() else {
        return Ok(ConfigRevert::None);
    };
    let path = PathBuf::from(&config.path);
    // Format dispatch on the recorded file (a `config.toml` keeps its trivia).
    if path.extension().and_then(|e| e.to_str()) == Some("toml") {
        revert_config_toml(&path, &config.keys_added, &config.sets_unioned, dry_run)
    } else {
        revert_config_json(&path, &config.keys_added, &config.sets_unioned, dry_run)
    }
}

/// JSON config revert: fail-safe read, apply the guard per key, remove yf's set
/// additions, pretty-write if changed.
fn revert_config_json(
    path: &Path,
    keys: &[ConfigKeyRecord],
    sets: &[SetUnionRecord],
    dry_run: bool,
) -> Result<ConfigRevert> {
    let mut value = match settings::read_settings(path) {
        SettingsRead::Absent => Value::Object(Default::default()),
        SettingsRead::Parsed(v) if v.is_object() => v,
        SettingsRead::Parsed(_) => {
            return Ok(ConfigRevert::Refused {
                message: format!("{}: top-level JSON is not an object", path.display()),
            });
        }
        SettingsRead::Malformed(msg) => {
            return Ok(ConfigRevert::Refused {
                message: format!("unparseable settings file; refusing to edit ({msg})"),
            });
        }
    };

    let mut restored = Vec::new();
    let mut removed = Vec::new();
    let mut kept = Vec::new();
    let mut mutated = false;

    for k in keys {
        let segs: Vec<&str> = k.path.split('.').collect();
        match json_get(&value, &segs) {
            // Already gone — nothing to do (idempotent).
            None => {}
            Some(current) if *current == k.written => {
                // Untouched since tune → restore prior or remove.
                if k.prior_present {
                    let prior = k.prior.clone().unwrap_or(Value::Null);
                    json_set(&mut value, &segs, prior);
                    restored.push(k.path.clone());
                } else {
                    json_remove(&mut value, &segs);
                    removed.push(k.path.clone());
                }
                mutated = true;
            }
            // Touched since tune → conservative-keep and report.
            Some(_) => kept.push(k.path.clone()),
        }
    }

    let mut sets_removed = Vec::new();
    for s in sets {
        let segs: Vec<&str> = s.path.split('.').collect();
        let n = json_remove_set_elements(&mut value, &segs, &s.added);
        if n > 0 {
            mutated = true;
            sets_removed.push((s.path.clone(), n));
        }
    }

    let wrote = if mutated && !dry_run {
        settings::write_settings(path, &value)
            .map_err(|e| anyhow::anyhow!("failed to write {}: {e}", path.display()))?;
        true
    } else {
        false
    };

    Ok(ConfigRevert::Done {
        path: path.to_path_buf(),
        restored,
        removed,
        kept,
        sets_removed,
        wrote,
    })
}

/// TOML config revert: fail-safe read into a trivia-preserving document, apply the
/// guard per key, remove yf's set additions, serialize if changed. Operator comments
/// / key order survive (REQ-YF-TUNE-013 delta-preserving write).
fn revert_config_toml(
    path: &Path,
    keys: &[ConfigKeyRecord],
    sets: &[SetUnionRecord],
    dry_run: bool,
) -> Result<ConfigRevert> {
    let text = match settings::read_toml(path) {
        TomlRead::Absent => String::new(),
        TomlRead::Parsed(t) => t,
        TomlRead::Malformed(msg) => {
            return Ok(ConfigRevert::Refused {
                message: format!("unparseable config file; refusing to edit ({msg})"),
            });
        }
    };
    let mut doc: DocumentMut = match text.parse() {
        Ok(d) => d,
        Err(e) => {
            return Ok(ConfigRevert::Refused {
                message: format!("unparseable config file; refusing to edit ({e})"),
            });
        }
    };

    let mut restored = Vec::new();
    let mut removed = Vec::new();
    let mut kept = Vec::new();
    let mut mutated = false;

    for k in keys {
        let segs: Vec<&str> = k.path.split('.').collect();
        match toml_get_json(doc.as_table(), &segs) {
            None => {}
            Some(current) if current == k.written => {
                if k.prior_present {
                    let prior = k.prior.clone().unwrap_or(Value::Null);
                    toml_set(doc.as_table_mut(), &segs, &prior);
                    restored.push(k.path.clone());
                } else {
                    toml_remove(doc.as_table_mut(), &segs);
                    removed.push(k.path.clone());
                }
                mutated = true;
            }
            Some(_) => kept.push(k.path.clone()),
        }
    }

    let mut sets_removed = Vec::new();
    for s in sets {
        let segs: Vec<&str> = s.path.split('.').collect();
        let n = toml_remove_set_elements(doc.as_table_mut(), &segs, &s.added);
        if n > 0 {
            mutated = true;
            sets_removed.push((s.path.clone(), n));
        }
    }

    let wrote = if mutated && !dry_run {
        settings::write_text(path, &doc.to_string())
            .map_err(|e| anyhow::anyhow!("failed to write {}: {e}", path.display()))?;
        true
    } else {
        false
    };

    Ok(ConfigRevert::Done {
        path: path.to_path_buf(),
        restored,
        removed,
        kept,
        sets_removed,
        wrote,
    })
}

// ---------------------------------------------------------------------------
// Rule revert (managed block or whole-file aggregate).
// ---------------------------------------------------------------------------

fn revert_rules(record: &SurfaceRecord, dry_run: bool) -> Result<RuleRevert> {
    let Some(rule) = record.rules.as_ref() else {
        return Ok(RuleRevert::None);
    };
    let path = PathBuf::from(&rule.path);
    match rule.kind.as_str() {
        // A managed BEGIN..END span sharing a file with operator prose.
        "block" => {
            let existing = match std::fs::read_to_string(&path) {
                Ok(t) => t,
                Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
                    // File already gone → nothing to remove (idempotent).
                    return Ok(RuleRevert::Block {
                        path,
                        removed: false,
                        wrote: false,
                    });
                }
                Err(e) => bail!("cannot read rule target {}: {e}", path.display()),
            };
            match managed_block::remove_block(&existing) {
                Ok(BlockRemoval::Absent) => Ok(RuleRevert::Block {
                    path,
                    removed: false,
                    wrote: false,
                }),
                Ok(BlockRemoval::Removed(out)) => {
                    let wrote = if !dry_run {
                        // If removing the block empties the file, delete it; else write
                        // the prose-only remainder back.
                        if out.trim().is_empty() {
                            std::fs::remove_file(&path)?;
                        } else {
                            std::fs::write(&path, &out)?;
                        }
                        true
                    } else {
                        false
                    };
                    Ok(RuleRevert::Block {
                        path,
                        removed: true,
                        wrote,
                    })
                }
                Err(e) => Ok(RuleRevert::Refused {
                    message: e.to_string(),
                }),
            }
        }
        // A whole-file aggregate (claude-code `rules/YOSHIKO_FLOW.md`) — a fully
        // yf-managed artifact; remove the file.
        _ => {
            let existed = path.exists();
            let wrote = if existed && !dry_run {
                std::fs::remove_file(&path)?;
                true
            } else {
                false
            };
            Ok(RuleRevert::Aggregate {
                path,
                removed: existed,
                wrote,
            })
        }
    }
}

// ---------------------------------------------------------------------------
// serde_json::Value dot-path helpers.
// ---------------------------------------------------------------------------

/// Get the value at a dot-path, or `None` if any segment is missing / not an object.
fn json_get<'a>(v: &'a Value, segs: &[&str]) -> Option<&'a Value> {
    let mut cur = v;
    for seg in segs {
        cur = cur.as_object()?.get(*seg)?;
    }
    Some(cur)
}

/// Set the scalar at a dot-path, creating intermediate objects as needed.
fn json_set(v: &mut Value, segs: &[&str], new: Value) {
    let mut cur = v;
    for seg in &segs[..segs.len() - 1] {
        if !cur.is_object() {
            *cur = Value::Object(Default::default());
        }
        cur = cur
            .as_object_mut()
            .unwrap()
            .entry(seg.to_string())
            .or_insert_with(|| Value::Object(Default::default()));
    }
    if let Some(obj) = cur.as_object_mut() {
        obj.insert(segs[segs.len() - 1].to_string(), new);
    }
}

/// Remove the leaf at a dot-path, then prune any ancestor objects the removal left
/// empty (so a round-trip revert leaves no orphaned `{}` container).
fn json_remove(v: &mut Value, segs: &[&str]) {
    json_remove_inner(v, segs);
}

/// Returns true if `v` itself became an empty object the caller should prune.
fn json_remove_inner(v: &mut Value, segs: &[&str]) -> bool {
    let Some(obj) = v.as_object_mut() else {
        return false;
    };
    if segs.len() == 1 {
        obj.shift_remove(segs[0]);
    } else if let Some(child) = obj.get_mut(segs[0]) {
        if json_remove_inner(child, &segs[1..]) {
            obj.shift_remove(segs[0]);
        }
    }
    obj.is_empty()
}

/// Remove yf's `added` elements from the array at a dot-path (one occurrence each —
/// the conservative choice when an operator independently re-added a copy). Returns
/// the count removed.
fn json_remove_set_elements(v: &mut Value, segs: &[&str], added: &[Value]) -> usize {
    let mut cur = v;
    for seg in segs {
        let Some(next) = cur.as_object_mut().and_then(|o| o.get_mut(*seg)) else {
            return 0;
        };
        cur = next;
    }
    let Some(arr) = cur.as_array_mut() else {
        return 0;
    };
    let mut removed = 0;
    for want in added {
        if let Some(idx) = arr.iter().position(|e| e == want) {
            arr.remove(idx);
            removed += 1;
        }
    }
    removed
}

// ---------------------------------------------------------------------------
// toml_edit dot-path helpers (trivia-preserving).
// ---------------------------------------------------------------------------

/// Convert a TOML leaf at a dot-path to a `serde_json::Value` for the guard's
/// value comparison, or `None` if the path is absent.
fn toml_get_json(table: &Table, segs: &[&str]) -> Option<Value> {
    let mut item = table.get(segs[0])?;
    for seg in &segs[1..] {
        item = item.as_table()?.get(seg)?;
    }
    match item {
        Item::Value(v) => Some(toml_value_to_json(v)),
        _ => None,
    }
}

fn toml_value_to_json(v: &toml_edit::Value) -> Value {
    match v {
        toml_edit::Value::String(s) => Value::String(s.value().clone()),
        toml_edit::Value::Integer(i) => Value::from(*i.value()),
        toml_edit::Value::Float(f) => serde_json::Number::from_f64(*f.value())
            .map(Value::Number)
            .unwrap_or(Value::Null),
        toml_edit::Value::Boolean(b) => Value::Bool(*b.value()),
        toml_edit::Value::Datetime(d) => Value::String(d.value().to_string()),
        toml_edit::Value::Array(a) => Value::Array(a.iter().map(toml_value_to_json).collect()),
        toml_edit::Value::InlineTable(t) => {
            let mut map = serde_json::Map::new();
            for (k, val) in t.iter() {
                map.insert(k.to_string(), toml_value_to_json(val));
            }
            Value::Object(map)
        }
    }
}

fn json_to_toml_value(v: &Value) -> toml_edit::Value {
    match v {
        Value::Bool(b) => (*b).into(),
        Value::String(s) => s.as_str().into(),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                i.into()
            } else if let Some(f) = n.as_f64() {
                f.into()
            } else {
                n.to_string().into()
            }
        }
        Value::Array(a) => {
            let mut arr = toml_edit::Array::new();
            for e in a {
                arr.push(json_to_toml_value(e));
            }
            arr.into()
        }
        Value::Null => "".into(),
        Value::Object(o) => {
            let mut t = toml_edit::InlineTable::new();
            for (k, val) in o {
                t.insert(k, json_to_toml_value(val));
            }
            t.into()
        }
    }
}

/// Navigate to the parent table of the leaf segment (no creation). `None` if a
/// segment is missing or not a table.
fn toml_parent<'a>(root: &'a mut Table, segs: &[&str]) -> Option<&'a mut Table> {
    let mut cur = root;
    for seg in &segs[..segs.len() - 1] {
        cur = cur.get_mut(seg)?.as_table_mut()?;
    }
    Some(cur)
}

/// Set the scalar at a dot-path, creating intermediate tables as needed.
fn toml_set(root: &mut Table, segs: &[&str], value: &Value) {
    let mut cur = root;
    for seg in &segs[..segs.len() - 1] {
        let item = cur.entry(seg).or_insert(Item::Table(Table::new()));
        match item.as_table_mut() {
            Some(t) => cur = t,
            None => return,
        }
    }
    cur.insert(segs[segs.len() - 1], Item::Value(json_to_toml_value(value)));
}

/// Remove the leaf at a dot-path; then prune any now-empty ancestor tables.
fn toml_remove(root: &mut Table, segs: &[&str]) {
    if let Some(parent) = toml_parent(root, segs) {
        parent.remove(segs[segs.len() - 1]);
    }
    // Prune empty ancestor tables from the deepest up.
    for depth in (1..segs.len()).rev() {
        let ancestor = &segs[..depth];
        let empty = toml_parent(root, &[ancestor, &[""]].concat())
            .map(|t| t.is_empty())
            .unwrap_or(false);
        if empty {
            if let Some(gp) = toml_parent(root, ancestor) {
                gp.remove(ancestor[ancestor.len() - 1]);
            }
        }
    }
}

/// Remove yf's `added` elements from the array at a dot-path (one occurrence each).
fn toml_remove_set_elements(root: &mut Table, segs: &[&str], added: &[Value]) -> usize {
    let Some(parent) = toml_parent(root, segs) else {
        return 0;
    };
    let Some(arr) = parent
        .get_mut(segs[segs.len() - 1])
        .and_then(Item::as_array_mut)
    else {
        return 0;
    };
    let mut removed = 0;
    for want in added {
        let pos = (0..arr.len()).find(|&i| {
            arr.get(i)
                .map(|v| toml_value_to_json(v) == *want)
                .unwrap_or(false)
        });
        if let Some(i) = pos {
            arr.remove(i);
            removed += 1;
        }
    }
    removed
}

// ---------------------------------------------------------------------------
// Reporting.
// ---------------------------------------------------------------------------

fn report(args: &HarnessTuneArgs, reverts: &[SurfaceRevert]) {
    if args.json {
        let surfaces: Vec<Value> = reverts.iter().map(surface_json).collect();
        let status = if reverts.iter().any(SurfaceRevert::is_failure) {
            "refused"
        } else {
            "ok"
        };
        let out = json!({
            "command": "harness tune --revert",
            "status": status,
            "surfaces": surfaces,
        });
        println!("{}", serde_json::to_string(&out).unwrap_or_default());
        return;
    }
    for r in reverts {
        println!("yf harness tune --revert [{}] ({})", r.harness, r.scope);
        if r.absent {
            println!("  nothing recorded for this surface — nothing to revert");
            continue;
        }
        render_config_human(&r.config);
        render_rules_human(&r.rules);
    }
}

fn render_config_human(config: &ConfigRevert) {
    match config {
        ConfigRevert::None => {}
        ConfigRevert::Refused { message } => println!("  config: refused — {message}"),
        ConfigRevert::Done {
            path,
            restored,
            removed,
            kept,
            sets_removed,
            wrote,
        } => {
            let verb = if *wrote { "reverted" } else { "no change" };
            println!("  config: {verb} → {}", path.display());
            for k in restored {
                println!("    restored prior: {k}");
            }
            for k in removed {
                println!("    removed yf key: {k}");
            }
            for (p, n) in sets_removed {
                println!("    removed {n} yf set element(s) from {p}");
            }
            for k in kept {
                println!("    kept (hand-edited since tune, not clobbered): {k}");
            }
        }
    }
}

fn render_rules_human(rules: &RuleRevert) {
    match rules {
        RuleRevert::None => {}
        RuleRevert::Refused { message } => println!("  rules: refused — {message}"),
        RuleRevert::Block { path, removed, .. } => {
            if *removed {
                println!("  rules: removed managed block → {}", path.display());
            } else {
                println!("  rules: no managed block to remove → {}", path.display());
            }
        }
        RuleRevert::Aggregate { path, removed, .. } => {
            if *removed {
                println!("  rules: removed aggregate → {}", path.display());
            } else {
                println!("  rules: no aggregate to remove → {}", path.display());
            }
        }
    }
}

fn surface_json(r: &SurfaceRevert) -> Value {
    json!({
        "harness": r.harness,
        "scope": r.scope,
        "absent": r.absent,
        "config": config_json(&r.config),
        "rules": rules_json(&r.rules),
    })
}

fn config_json(config: &ConfigRevert) -> Value {
    match config {
        ConfigRevert::None => json!({ "status": "none" }),
        ConfigRevert::Refused { message } => json!({ "status": "refused", "message": message }),
        ConfigRevert::Done {
            path,
            restored,
            removed,
            kept,
            sets_removed,
            wrote,
        } => json!({
            "status": "reverted",
            "path": path.display().to_string(),
            "wrote": wrote,
            "restored": restored,
            "removed": removed,
            "kept": kept,
            "sets_removed": sets_removed
                .iter()
                .map(|(p, n)| json!({ "path": p, "count": n }))
                .collect::<Vec<_>>(),
        }),
    }
}

fn rules_json(rules: &RuleRevert) -> Value {
    match rules {
        RuleRevert::None => json!({ "status": "none" }),
        RuleRevert::Refused { message } => json!({ "status": "refused", "message": message }),
        RuleRevert::Block {
            path,
            removed,
            wrote,
        } => json!({
            "kind": "block",
            "status": "reverted",
            "path": path.display().to_string(),
            "removed": removed,
            "wrote": wrote,
        }),
        RuleRevert::Aggregate {
            path,
            removed,
            wrote,
        } => json!({
            "kind": "aggregate",
            "status": "reverted",
            "path": path.display().to_string(),
            "removed": removed,
            "wrote": wrote,
        }),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cli::PiRuleTarget;
    use serde_json::json;

    fn revert_args(harness: &str, project: bool, committed: bool) -> HarnessTuneArgs {
        HarnessTuneArgs {
            harness: vec![harness.to_string()],
            project,
            committed,
            force: false,
            dry_run: false,
            rules_only: false,
            allow_permissions_write: false,
            consent_gated: false,
            revert: true,
            pi_rule_target: PiRuleTarget::AgentsMd,
            json: false,
        }
    }

    fn tune_args(harness: &str, force: bool) -> HarnessTuneArgs {
        HarnessTuneArgs {
            harness: vec![harness.to_string()],
            project: false,
            committed: false,
            force,
            dry_run: false,
            rules_only: false,
            allow_permissions_write: false,
            consent_gated: false,
            revert: false,
            pi_rule_target: PiRuleTarget::AgentsMd,
            json: false,
        }
    }

    fn read_json(path: &Path) -> Value {
        serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap()
    }

    // REQ-YF-TUNE-022: a tune→revert round-trip restores prior state (modulo
    // reserialization). Exercises, in one claude-code surface:
    //  * a PURE-ADD key (`todoFeatureEnabled`) → removed on revert;
    //  * a FORCED scalar (`effortLevel`, seeded "high", forced to "medium") → restored
    //    to its prior "high";
    //  * a key HAND-EDITED since the tune (`permissions.defaultMode`) → conservative-
    //    kept and reported, NOT clobbered;
    //  * a SET-UNION revert (`permissions.deny`) → only yf's added elements removed,
    //    the operator's `MyOrgTool` entry survives;
    //  * a second revert is a no-op (manifest consumed);
    //  * `Agent`-never-denied holds (revert only removes).
    #[test]
    fn tune_then_revert_round_trip_with_guard_and_set_and_idempotency() {
        let dir = tempfile::tempdir().unwrap();
        let home = dir.path();
        let root = dir.path();
        let settings = home.join(".claude").join("settings.json");

        // Seed operator state: a conflicting scalar (forces a captured prior) and an
        // operator deny entry (so the union delta records only yf's additions).
        settings::write_settings(
            &settings,
            &json!({
                "effortLevel": "high",
                "permissions": { "deny": ["MyOrgTool"] }
            }),
        )
        .unwrap();

        // Tune with --force so effortLevel becomes a forced scalar.
        super::super::tune_one_harness_at(
            &tune_args("claude-code", true),
            "claude-code",
            TuneScope::User,
            home,
            root,
        )
        .unwrap();

        // The tune wrote yf's keys + unioned the deny set + wrote the aggregate.
        let tuned = read_json(&settings);
        assert_eq!(
            tuned["todoFeatureEnabled"],
            json!(false),
            "pure add present"
        );
        assert_eq!(tuned["effortLevel"], json!("medium"), "forced to medium");
        let deny_after_tune: Vec<String> = tuned["permissions"]["deny"]
            .as_array()
            .unwrap()
            .iter()
            .map(|v| v.as_str().unwrap().to_string())
            .collect();
        assert!(deny_after_tune.contains(&"TaskCreate".to_string()));
        assert!(deny_after_tune.contains(&"MyOrgTool".to_string()));

        // Operator HAND-EDITS a yf-written key AFTER the tune. Revert must NOT clobber.
        let mut edited = read_json(&settings);
        edited["permissions"]["defaultMode"] = json!("acceptEdits");
        settings::write_settings(&settings, &edited).unwrap();

        // Aggregate exists before revert.
        let flow = home
            .join(".claude")
            .join("rules")
            .join(crate::flow::FLOW_FILENAME);
        assert!(flow.is_file(), "tune wrote the aggregate");

        // --- REVERT --------------------------------------------------------------
        let reverts = revert_all_at(
            &["claude-code".to_string()],
            TuneScope::User,
            home,
            root,
            false,
        )
        .unwrap();
        assert_eq!(reverts.len(), 1);
        assert!(!reverts[0].is_failure(), "revert must not fail");

        let after = read_json(&settings);

        // Pure-add key removed.
        assert!(
            after.get("todoFeatureEnabled").is_none(),
            "pure-add key removed on revert: {after}"
        );
        // Forced scalar restored to its captured prior.
        assert_eq!(
            after["effortLevel"],
            json!("high"),
            "forced scalar restored to prior"
        );
        // Hand-edited key conservative-kept (NOT restored to yf's value, NOT removed).
        assert_eq!(
            after["permissions"]["defaultMode"],
            json!("acceptEdits"),
            "operator's since-tune edit preserved"
        );
        match &reverts[0].config {
            ConfigRevert::Done { kept, .. } => assert!(
                kept.iter().any(|k| k == "permissions.defaultMode"),
                "the hand-edited key is reported as kept: {kept:?}"
            ),
            other => panic!("expected Done, got {other:?}"),
        }
        // Set-union revert: yf's TaskCreate removed, operator's MyOrgTool survives.
        let deny_after: Vec<String> = after["permissions"]["deny"]
            .as_array()
            .map(|a| {
                a.iter()
                    .map(|v| v.as_str().unwrap_or_default().to_string())
                    .collect()
            })
            .unwrap_or_default();
        assert!(
            deny_after.contains(&"MyOrgTool".to_string()),
            "operator set entry survives: {deny_after:?}"
        );
        assert!(
            !deny_after.contains(&"TaskCreate".to_string()),
            "yf's unioned set element removed: {deny_after:?}"
        );
        // Agent-never-denied holds (revert only ever removes).
        assert!(!deny_after.contains(&"Agent".to_string()));
        // Aggregate removed.
        assert!(!flow.exists(), "aggregate removed on revert");

        // --- SECOND REVERT is a no-op (manifest consumed). -----------------------
        let before_bytes = std::fs::read(&settings).unwrap();
        let reverts2 = revert_all_at(
            &["claude-code".to_string()],
            TuneScope::User,
            home,
            root,
            false,
        )
        .unwrap();
        assert!(
            reverts2[0].absent,
            "second revert finds no recorded surface (idempotent)"
        );
        assert_eq!(
            std::fs::read(&settings).unwrap(),
            before_bytes,
            "second revert changes nothing"
        );
    }

    // REQ-YF-TUNE-022: a rule managed-block revert removes ONLY the managed span,
    // preserving operator prose; and a TOML config revert removes yf's key while
    // preserving operator trivia (comments). Driven on codex (config.toml + AGENTS.md
    // managed block).
    #[test]
    fn revert_preserves_prose_and_toml_trivia() {
        let dir = tempfile::tempdir().unwrap();
        let home = dir.path();
        let root = dir.path();

        // Seed a config.toml with an operator comment so trivia survival is testable.
        let cfg = home.join(".codex").join("config.toml");
        std::fs::create_dir_all(cfg.parent().unwrap()).unwrap();
        std::fs::write(&cfg, "# operator note — keep me\n").unwrap();

        // Seed AGENTS.md with operator prose so the block deploy appends after it.
        let agents = home.join(".codex").join("AGENTS.md");
        let prose = "# My codex rules\n\nBe careful.\n";
        std::fs::write(&agents, prose).unwrap();

        super::super::tune_one_harness_at(
            &tune_args("codex", false),
            "codex",
            TuneScope::User,
            home,
            root,
        )
        .unwrap();

        // Tune added yf's config keys + the managed block.
        let tuned = std::fs::read_to_string(&cfg).unwrap();
        assert!(tuned.contains("approval_policy"), "yf key written");
        assert!(tuned.contains("# operator note — keep me"), "comment kept");
        let tuned_agents = std::fs::read_to_string(&agents).unwrap();
        assert!(tuned_agents.contains(managed_block::BEGIN_MARKER));

        // --- REVERT --------------------------------------------------------------
        let reverts =
            revert_all_at(&["codex".to_string()], TuneScope::User, home, root, false).unwrap();
        assert!(!reverts[0].is_failure());

        // TOML: yf's key gone, operator comment preserved, still valid TOML.
        let reverted = std::fs::read_to_string(&cfg).unwrap();
        assert!(
            reverted.contains("# operator note — keep me"),
            "operator TOML comment preserved through revert:\n{reverted}"
        );
        assert!(
            !reverted.contains("approval_policy"),
            "yf config key removed on revert:\n{reverted}"
        );
        reverted
            .parse::<DocumentMut>()
            .expect("reverted config.toml is valid TOML");

        // Managed block: gone; operator prose preserved verbatim.
        let reverted_agents = std::fs::read_to_string(&agents).unwrap();
        assert!(
            !reverted_agents.contains(managed_block::BEGIN_MARKER),
            "managed block removed"
        );
        assert!(
            reverted_agents.contains("Be careful."),
            "operator prose preserved after block removal:\n{reverted_agents}"
        );
    }

    // REQ-YF-TUNE-022: revert is fail-safe on a malformed target — a hand-broken
    // settings.json is refused (surface fails) and left byte-for-byte untouched, and
    // the manifest record is NOT consumed (so a later, repaired revert can still run).
    #[test]
    fn revert_fail_safe_on_malformed_target() {
        let dir = tempfile::tempdir().unwrap();
        let home = dir.path();
        let root = dir.path();
        let settings = home.join(".claude").join("settings.json");

        super::super::tune_one_harness_at(
            &tune_args("claude-code", false),
            "claude-code",
            TuneScope::User,
            home,
            root,
        )
        .unwrap();

        // Corrupt the settings file after the tune.
        let broken = "{ not json ,,,";
        std::fs::write(&settings, broken).unwrap();

        let reverts = revert_all_at(
            &["claude-code".to_string()],
            TuneScope::User,
            home,
            root,
            false,
        )
        .unwrap();
        assert!(reverts[0].is_failure(), "malformed target must refuse");
        assert_eq!(
            std::fs::read_to_string(&settings).unwrap(),
            broken,
            "malformed file left untouched"
        );

        // The config record was NOT consumed (a repaired file could still revert).
        let mpath = manifest::manifest_path_at("claude-code", TuneScope::User, home, root).unwrap();
        let m = manifest::load_manifest(&mpath).unwrap();
        let surface = m.surfaces.get("claude-code:user").expect("surface kept");
        assert!(
            surface.config.is_some(),
            "a refused config revert keeps its manifest record"
        );
    }

    // REQ-YF-TUNE-022: a dry-run revert writes nothing and does not consume the
    // manifest — the surface is still revertible afterward.
    #[test]
    fn dry_run_revert_writes_nothing_and_keeps_manifest() {
        let dir = tempfile::tempdir().unwrap();
        let home = dir.path();
        let root = dir.path();
        let settings = home.join(".claude").join("settings.json");

        super::super::tune_one_harness_at(
            &tune_args("claude-code", false),
            "claude-code",
            TuneScope::User,
            home,
            root,
        )
        .unwrap();
        let before = std::fs::read(&settings).unwrap();

        let reverts = revert_all_at(
            &["claude-code".to_string()],
            TuneScope::User,
            home,
            root,
            true, // dry_run
        )
        .unwrap();
        assert!(!reverts[0].is_failure());
        assert_eq!(
            std::fs::read(&settings).unwrap(),
            before,
            "dry-run revert must not write"
        );

        // Manifest still carries the surface — a real revert can still run.
        let mpath = manifest::manifest_path_at("claude-code", TuneScope::User, home, root).unwrap();
        let m = manifest::load_manifest(&mpath).unwrap();
        assert!(m.surfaces.contains_key("claude-code:user"));
    }

    // The `run` env entry dispatches revert for an unmapped harness cleanly (no
    // panic, success — nothing recorded to revert). Guards the CLI wiring.
    #[test]
    fn revert_run_unmapped_harness_is_clean() {
        let code = run(&revert_args("nonesuch", false, false)).unwrap();
        assert_eq!(format!("{code:?}"), format!("{:?}", ExitCode::SUCCESS));
    }
}
