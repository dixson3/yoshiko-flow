//! The TOML delta-replay write adapter (REQ-YF-TUNE-013).
//!
//! `config.toml` (codex) cannot round-trip through a `serde_json::Value`: the
//! `Value` carries no comments / key order / trivia, and it flattens TOML's
//! datetime and int-vs-float distinctions. Serializing a merged `Value` back to
//! TOML would silently destroy an operator's comments and formatting (Risk R1).
//!
//! So this adapter **keeps two representations** of the same file:
//!
//! 1. a [`toml_edit::DocumentMut`] — the real file, parsed with all trivia
//!    (comments, blank lines, key order) retained; the **write source**; and
//! 2. a [`serde_json::Value`] derived from it — fed to the **unchanged**
//!    [`super::merge`] engine for the merge **decision only** (never written).
//!
//! The merge yields a [`MergeReport`]; we then **replay only the report's
//! mutating deltas** (`ScalarAdded` / `ScalarForced` / `SetUnioned`, keyed by
//! dot-path) onto the `DocumentMut` and serialize *that document*. The `Value` is
//! never the write source, so datetimes / int-vs-float / comments survive.
//!
//! `merge.rs` is untouched — this is a pure adapter around it.
//!
//! This module is landed by Issue 4.1; Issue 4.2 (`REQ-YF-TUNE-014`) wires the
//! non-test call site — profile-driven format dispatch from `run_core` selects
//! [`merge_toml_text`] for a [`SettingsFormat::Toml`](super::settings::SettingsFormat)
//! profile, and [`super::settings::read_toml`] uses [`parse_document`] for the
//! fail-safe TOML read.

use serde_json::Value;
use toml_edit::{Array, DocumentMut, Item, Table};

use super::merge::{self, Change, MergeReport};
use super::profile::Profile;

/// Parse `text` (the contents of a `config.toml`) into a trivia-preserving
/// document. `Err(msg)` on unparseable input — the fail-safe refusal signal that
/// mirrors the JSON path's [`super::settings::SettingsRead::Malformed`]
/// (REQ-YF-TUNE-006). Empty/whitespace text parses to an empty document.
pub fn parse_document(text: &str) -> Result<DocumentMut, String> {
    text.parse::<DocumentMut>().map_err(|e| e.to_string())
}

/// Run the config merge over a TOML `config.toml` via delta-replay.
///
/// Parses `text` into a [`DocumentMut`], derives a `serde_json::Value` for the
/// merge decision, runs the **unchanged** [`merge::merge`], replays the report's
/// mutating deltas onto the document, and returns the reserialized TOML plus the
/// report. `Err(msg)` on a malformed `config.toml` (fail-safe, REQ-YF-TUNE-006).
pub fn merge_toml_text(
    text: &str,
    profile: &Profile,
    force: bool,
) -> Result<(String, MergeReport), String> {
    let mut doc = parse_document(text)?;
    // (2) derive the decision-only Value — never the write source.
    let existing = table_to_json(doc.as_table());
    // Run the unchanged engine; discard the merged Value, keep the report.
    let (_merged_value, report) = merge::merge(&existing, profile, force);
    // (1) replay the deltas onto the real document and serialize *that*.
    replay(&mut doc, &report);
    Ok((doc.to_string(), report))
}

/// Replay a [`MergeReport`]'s **mutating** deltas onto `doc`. Conflicts
/// (`ScalarConflict` / `SetTypeConflict`) and idempotent no-ops carry no delta,
/// so nothing is written for them — matching the JSON path, where an unforced
/// conflict leaves the existing value in place.
pub fn replay(doc: &mut DocumentMut, report: &MergeReport) {
    let root = doc.as_table_mut();
    for change in &report.changes {
        match change {
            Change::ScalarAdded { path, value } => set_scalar(root, path, value),
            Change::ScalarForced { path, to, .. } => set_scalar(root, path, to),
            Change::SetUnioned { path, added } => union_set(root, path, added),
            // Non-mutating: conflicts + type conflicts leave the file untouched.
            Change::ScalarConflict { .. } | Change::SetTypeConflict { .. } => {}
        }
    }
}

/// Set the scalar at dot-`path` (e.g. `permissions.defaultMode`), creating
/// intermediate tables as needed. A structural clash (an intermediate segment is
/// a non-table) is skipped, mirroring the engine's `parent_mut` `None` handling.
fn set_scalar(root: &mut Table, path: &str, value: &Value) {
    let segs: Vec<&str> = path.split('.').collect();
    let leaf = *segs.last().unwrap();
    let Some(parent) = navigate_parent(root, &segs) else {
        return;
    };
    parent.insert(leaf, Item::Value(json_to_toml_value(value)));
}

/// Append `added` members to the array at dot-`path` (union delta-replay).
/// `added` is *only the newly-added* elements from the merge report, so plain
/// append reproduces the non-destructive union — pre-existing members are left
/// as-is (with their trivia), never rewritten.
fn union_set(root: &mut Table, path: &str, added: &[Value]) {
    let segs: Vec<&str> = path.split('.').collect();
    let leaf = *segs.last().unwrap();
    let Some(parent) = navigate_parent(root, &segs) else {
        return;
    };
    match parent.get_mut(leaf) {
        // Existing array: append the new members, preserving existing entries.
        Some(Item::Value(toml_edit::Value::Array(arr))) => {
            for v in added {
                arr.push(json_to_toml_value(v));
            }
        }
        // Absent (or not an array — the engine would only emit SetUnioned when it
        // treated the slot as an array/absent): create it with the members.
        _ => {
            let mut arr = Array::new();
            for v in added {
                arr.push(json_to_toml_value(v));
            }
            parent.insert(leaf, Item::Value(toml_edit::Value::Array(arr)));
        }
    }
}

/// Navigate to the parent table of the leaf segment, creating intermediate
/// tables as needed. Returns `None` if an intermediate segment exists but is not
/// a table (a structural clash the caller skips).
fn navigate_parent<'a>(root: &'a mut Table, segs: &[&str]) -> Option<&'a mut Table> {
    let mut cur = root;
    for seg in &segs[..segs.len() - 1] {
        let item = cur.entry(seg).or_insert(Item::Table(Table::new()));
        cur = item.as_table_mut()?;
    }
    Some(cur)
}

// --- TOML → serde_json::Value (decision-only derivation) --------------------

/// Derive a `serde_json::Value` object from a TOML table. Used only to compute
/// the merge decision — TOML datetimes are stringified (they are never at a
/// profile path, and this Value is never written back).
fn table_to_json(table: &Table) -> Value {
    let mut map = serde_json::Map::new();
    for (key, item) in table.iter() {
        map.insert(key.to_string(), item_to_json(item));
    }
    Value::Object(map)
}

fn item_to_json(item: &Item) -> Value {
    match item {
        Item::None => Value::Null,
        Item::Value(v) => toml_value_to_json(v),
        Item::Table(t) => table_to_json(t),
        Item::ArrayOfTables(aot) => Value::Array(aot.iter().map(table_to_json).collect()),
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
        // Datetimes have no JSON analog; stringify for the decision only.
        toml_edit::Value::Datetime(d) => Value::String(d.value().to_string()),
        toml_edit::Value::Array(a) => Value::Array(a.iter().map(toml_value_to_json).collect()),
        toml_edit::Value::InlineTable(t) => {
            let mut map = serde_json::Map::new();
            for (key, val) in t.iter() {
                map.insert(key.to_string(), toml_value_to_json(val));
            }
            Value::Object(map)
        }
    }
}

// --- serde_json::Value → TOML value (replay of profile deltas) --------------

/// Convert a profile-delta `serde_json::Value` into a `toml_edit::Value` to write
/// back. Profile deltas are scalars (bool / string / number) or arrays of them.
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
            let mut arr = Array::new();
            for e in a {
                arr.push(json_to_toml_value(e));
            }
            arr.into()
        }
        // Null / nested object are not emitted by the profile as scalar/set
        // deltas; represent defensively as an empty string / inline table.
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

#[cfg(test)]
mod tests {
    use super::super::profile::load_profile;
    use super::*;

    fn profile() -> Profile {
        load_profile("claude-code").unwrap().unwrap()
    }

    // REQ-YF-TUNE-013: a merge decision computed over a TOML `Value` is replayed
    // onto the `DocumentMut` and serialized to a valid `config.toml` that
    // PRESERVES a pre-existing operator comment — the property only delta-replay
    // provides (a from-scratch `Value` reserialization would drop the comment).
    // Also asserts a scalar-add and a nested set-union land in the TOML output.
    #[test]
    fn delta_replay_preserves_comment_scalar_add_and_set_union() {
        let existing = "\
# operator comment — must survive the tune
effortLevel = \"high\"

[permissions]
deny = [\"MyCustomTool\"]
";
        let (out, report) = merge_toml_text(existing, &profile(), false).expect("must parse");

        // (1) The operator's comment survived — the delta-replay guarantee.
        assert!(
            out.contains("# operator comment — must survive the tune"),
            "comment must be preserved, got:\n{out}"
        );

        // The written document is valid TOML and re-parses.
        let doc = parse_document(&out).expect("output must be valid TOML");

        // (2) Scalar-add landed: a profile scalar absent from the file was added.
        assert_eq!(
            doc["todoFeatureEnabled"].as_bool(),
            Some(false),
            "scalar add must land in TOML output"
        );
        // The pre-existing conflicting scalar is KEPT (no --force) — not clobbered.
        assert_eq!(doc["effortLevel"].as_str(), Some("high"), "conflict kept");

        // (3) Nested set-union landed: existing member preserved, profile members
        // appended, Agent never present.
        let deny: Vec<String> = doc["permissions"]["deny"]
            .as_array()
            .expect("permissions.deny is a TOML array")
            .iter()
            .map(|v| v.as_str().unwrap_or_default().to_string())
            .collect();
        assert!(
            deny.contains(&"MyCustomTool".to_string()),
            "existing member preserved"
        );
        assert!(
            deny.contains(&"TaskCreate".to_string()),
            "profile member unioned in"
        );
        assert!(!deny.contains(&"Agent".to_string()), "Agent never denied");

        // The report reflects the same mutations (adapter shares the engine).
        assert!(report.mutated());
        assert!(report.changes.iter().any(|c| matches!(
            c, Change::SetUnioned { path, .. } if path == "permissions.deny"
        )));
    }

    // REQ-YF-TUNE-013: a fresh (empty) config.toml gains the full profile via
    // delta-replay and round-trips to valid TOML.
    #[test]
    fn fresh_toml_gets_full_profile() {
        let (out, report) = merge_toml_text("", &profile(), false).expect("empty parses");
        assert!(report.mutated());
        let doc = parse_document(&out).expect("valid TOML");
        assert_eq!(doc["todoFeatureEnabled"].as_bool(), Some(false));
        assert_eq!(
            doc["permissions"]["defaultMode"].as_str(),
            Some("bypassPermissions")
        );
    }

    // REQ-YF-TUNE-013: replaying twice is idempotent — a second tune over the
    // written document mutates nothing (the engine's idempotence carries through
    // the adapter).
    #[test]
    fn second_toml_tune_is_noop() {
        let (out1, _) = merge_toml_text("", &profile(), false).unwrap();
        let (out2, report2) = merge_toml_text(&out1, &profile(), false).unwrap();
        assert!(
            !report2.mutated(),
            "second tune must be a no-op: {:?}",
            report2.changes
        );
        // A no-op leaves the document byte-identical.
        assert_eq!(out1, out2);
    }

    // REQ-YF-TUNE-013 / REQ-YF-TUNE-006: a malformed config.toml is refused
    // cleanly (Err), mirroring the JSON path's Malformed fail-safe — the caller
    // must NOT overwrite it.
    #[test]
    fn malformed_toml_refused() {
        let bad = "this is [ not valid = toml";
        assert!(
            merge_toml_text(bad, &profile(), false).is_err(),
            "malformed TOML must refuse cleanly"
        );
    }
}
