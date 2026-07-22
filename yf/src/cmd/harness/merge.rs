//! The kind-aware, idempotent settings merge engine (REQ-YF-TUNE-004/005).
//!
//! Pure over `serde_json::Value` (preserve-order): [`merge`] takes the existing
//! settings object and a [`Profile`] and returns the merged object plus a
//! structured [`MergeReport`]. No I/O — the caller ([`super::settings`]) reads/
//! writes files and enforces the fail-safe on unparseable input.
//!
//! - **Scalar** entries are **add-missing**: absent → written; present-and-equal →
//!   no-op (idempotent); present-and-different → a reported **conflict**, left
//!   untouched unless `force` (then overwritten).
//! - **Set-valued** entries are a **non-destructive union**: the profile's missing
//!   elements are appended; nothing existing is ever removed. Union needs no
//!   `force`.
//! - **Agent is never denied** — the `agent_tool` is filtered out of any set
//!   addition even under `force`, so tune can never disable the tool every yf
//!   agent fans out through.

use serde_json::{Map, Value};

use super::profile::{Entry, Kind, Profile};

/// What the merge did to one entry.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Change {
    /// A scalar key was absent and got written.
    ScalarAdded { path: String, value: Value },
    /// A scalar key was overwritten (present, different, `--force`).
    ScalarForced {
        path: String,
        from: Value,
        to: Value,
    },
    /// A scalar key is present with a different value; left untouched (no `--force`).
    ScalarConflict {
        path: String,
        existing: Value,
        recommended: Value,
    },
    /// A set-valued key gained these missing elements (union).
    SetUnioned { path: String, added: Vec<Value> },
    /// The existing value at a set path is not an array; left untouched (a conflict).
    SetTypeConflict { path: String, existing: Value },
}

impl Change {
    /// Whether this change modified the settings object (added/forced/unioned).
    pub fn is_mutation(&self) -> bool {
        matches!(
            self,
            Change::ScalarAdded { .. } | Change::ScalarForced { .. } | Change::SetUnioned { .. }
        )
    }

    /// Whether this change is a reported-but-unresolved conflict (needs `--force`
    /// or operator attention).
    pub fn is_conflict(&self) -> bool {
        matches!(
            self,
            Change::ScalarConflict { .. } | Change::SetTypeConflict { .. }
        )
    }
}

/// The structured outcome of a merge.
#[derive(Debug, Clone, Default)]
pub struct MergeReport {
    /// Every non-idempotent change (mutations and conflicts). Entries that were
    /// already aligned produce nothing.
    pub changes: Vec<Change>,
}

impl MergeReport {
    /// Whether any change mutated the object (drives "wrote N keys" vs "no-op").
    pub fn mutated(&self) -> bool {
        self.changes.iter().any(Change::is_mutation)
    }

    /// The unresolved conflicts (scalar value mismatch, set type mismatch).
    pub fn conflicts(&self) -> Vec<&Change> {
        self.changes.iter().filter(|c| c.is_conflict()).collect()
    }
}

/// Merge the profile into `existing` (a settings object), returning the new object
/// and a report. `force` overwrites scalar conflicts; set unions ignore `force`.
///
/// Preserves key order and structure (`serde_json` preserve-order): additions
/// append, existing keys keep their positions.
pub fn merge(existing: &Value, profile: &Profile, force: bool) -> (Value, MergeReport) {
    // Work on an object clone; a non-object existing (e.g. an empty file parsed as
    // null) starts from an empty object.
    let mut root: Map<String, Value> = existing.as_object().cloned().unwrap_or_default();
    let mut report = MergeReport::default();

    for entry in &profile.entries {
        match entry.kind {
            Kind::Scalar => merge_scalar(&mut root, entry, force, &mut report),
            Kind::Set => merge_set(&mut root, entry, profile.agent_tool.as_str(), &mut report),
        }
    }

    (Value::Object(root), report)
}

/// Navigate to the parent object of the entry's leaf key, creating intermediate
/// objects as needed. Returns `None` if an intermediate segment exists but is not
/// an object (a structural conflict the caller reports).
fn parent_mut<'a>(
    root: &'a mut Map<String, Value>,
    segments: &[&str],
) -> Option<&'a mut Map<String, Value>> {
    let mut cur = root;
    for seg in &segments[..segments.len() - 1] {
        let next = cur
            .entry(seg.to_string())
            .or_insert_with(|| Value::Object(Map::new()));
        if !next.is_object() {
            return None;
        }
        cur = next.as_object_mut().unwrap();
    }
    Some(cur)
}

fn merge_scalar(
    root: &mut Map<String, Value>,
    entry: &Entry,
    force: bool,
    report: &mut MergeReport,
) {
    let segs = entry.segments();
    let leaf = *segs.last().unwrap();
    let Some(parent) = parent_mut(root, &segs) else {
        // An intermediate path segment is a non-object; report as a conflict.
        report.changes.push(Change::ScalarConflict {
            path: entry.path.clone(),
            existing: Value::Null,
            recommended: entry.value.clone(),
        });
        return;
    };
    match parent.get(leaf) {
        None => {
            parent.insert(leaf.to_string(), entry.value.clone());
            report.changes.push(Change::ScalarAdded {
                path: entry.path.clone(),
                value: entry.value.clone(),
            });
        }
        Some(cur) if cur == &entry.value => { /* idempotent: already aligned */ }
        Some(cur) => {
            let existing = cur.clone();
            if force {
                parent.insert(leaf.to_string(), entry.value.clone());
                report.changes.push(Change::ScalarForced {
                    path: entry.path.clone(),
                    from: existing,
                    to: entry.value.clone(),
                });
            } else {
                report.changes.push(Change::ScalarConflict {
                    path: entry.path.clone(),
                    existing,
                    recommended: entry.value.clone(),
                });
            }
        }
    }
}

fn merge_set(
    root: &mut Map<String, Value>,
    entry: &Entry,
    agent_tool: &str,
    report: &mut MergeReport,
) {
    let segs = entry.segments();
    let leaf = *segs.last().unwrap();
    let Some(parent) = parent_mut(root, &segs) else {
        report.changes.push(Change::SetTypeConflict {
            path: entry.path.clone(),
            existing: Value::Null,
        });
        return;
    };
    // The profile's recommended members, with the Agent-never-denied guard: the
    // agent tool is NEVER added to a deny/set even if a future profile listed it.
    let agent_val = Value::String(agent_tool.to_string());
    let recommended: Vec<Value> = entry
        .value
        .as_array()
        .cloned()
        .unwrap_or_default()
        .into_iter()
        .filter(|v| v != &agent_val)
        .collect();

    match parent.get_mut(leaf) {
        None => {
            // Absent → create the array with the recommended members.
            if !recommended.is_empty() {
                parent.insert(leaf.to_string(), Value::Array(recommended.clone()));
                report.changes.push(Change::SetUnioned {
                    path: entry.path.clone(),
                    added: recommended,
                });
            }
        }
        Some(Value::Array(existing)) => {
            // Union: append only members not already present; never remove.
            let mut added = Vec::new();
            for member in &recommended {
                if !existing.iter().any(|e| e == member) {
                    existing.push(member.clone());
                    added.push(member.clone());
                }
            }
            if !added.is_empty() {
                report.changes.push(Change::SetUnioned {
                    path: entry.path.clone(),
                    added,
                });
            }
        }
        Some(other) => {
            // Present but not an array — a type conflict; leave untouched.
            report.changes.push(Change::SetTypeConflict {
                path: entry.path.clone(),
                existing: other.clone(),
            });
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

    fn deny_of(v: &Value) -> Vec<String> {
        v["permissions"]["deny"]
            .as_array()
            .map(|a| {
                a.iter()
                    .map(|x| x.as_str().unwrap_or_default().to_string())
                    .collect()
            })
            .unwrap_or_default()
    }

    // REQ-YF-TUNE-004: a fresh (empty) settings object gains every recommended key.
    #[test]
    fn fresh_file_gets_full_profile() {
        let (out, rep) = merge(&Value::Object(Map::new()), &profile(), false);
        assert!(rep.mutated());
        assert_eq!(out["todoFeatureEnabled"], serde_json::json!(false));
        assert_eq!(out["disableWorkflows"], serde_json::json!(true));
        assert_eq!(
            out["permissions"]["defaultMode"],
            serde_json::json!("bypassPermissions")
        );
        assert!(deny_of(&out).contains(&"TaskCreate".to_string()));
        assert!(rep.conflicts().is_empty());
    }

    // REQ-YF-TUNE-005: merging twice is idempotent — the second run mutates nothing.
    #[test]
    fn second_run_is_noop() {
        let (out1, _) = merge(&Value::Object(Map::new()), &profile(), false);
        let (out2, rep2) = merge(&out1, &profile(), false);
        assert!(
            !rep2.mutated(),
            "second merge must be a no-op: {:?}",
            rep2.changes
        );
        assert_eq!(out1, out2);
    }

    // REQ-YF-TUNE-004: a scalar conflict is reported, not clobbered, without --force.
    #[test]
    fn scalar_conflict_preserved_without_force() {
        let existing = serde_json::json!({ "effortLevel": "high" });
        let (out, rep) = merge(&existing, &profile(), false);
        assert_eq!(
            out["effortLevel"],
            serde_json::json!("high"),
            "must not clobber"
        );
        assert!(rep.conflicts().iter().any(|c| matches!(
            c, Change::ScalarConflict { path, .. } if path == "effortLevel"
        )));
    }

    // REQ-YF-TUNE-004: with --force, a scalar conflict is overwritten to the profile.
    #[test]
    fn scalar_conflict_forced() {
        let existing = serde_json::json!({ "effortLevel": "high" });
        let (out, rep) = merge(&existing, &profile(), true);
        assert_eq!(
            out["effortLevel"],
            serde_json::json!("medium"),
            "force overwrites"
        );
        assert!(rep.changes.iter().any(|c| matches!(
            c, Change::ScalarForced { path, .. } if path == "effortLevel"
        )));
    }

    // REQ-YF-TUNE-004: a pre-existing deny array is UNIONED — user entries and rm
    // -rf safety globs preserved, profile denies added, nothing removed.
    #[test]
    fn set_valued_union_preserves_user_entries() {
        let existing = serde_json::json!({
            "permissions": {
                "deny": ["Bash(rm -rf /custom)", "MyCustomTool", "TaskCreate"]
            }
        });
        let (out, rep) = merge(&existing, &profile(), false);
        let deny = deny_of(&out);
        // User entries preserved.
        assert!(deny.contains(&"Bash(rm -rf /custom)".to_string()));
        assert!(deny.contains(&"MyCustomTool".to_string()));
        // Pre-existing profile member not duplicated.
        assert_eq!(deny.iter().filter(|d| *d == "TaskCreate").count(), 1);
        // Profile members added.
        assert!(deny.contains(&"EnterPlanMode".to_string()));
        assert!(deny.contains(&"NotebookEdit".to_string()));
        // Union needs no --force and is not a conflict.
        assert!(rep.conflicts().is_empty());
        assert!(rep.changes.iter().any(|c| matches!(
            c, Change::SetUnioned { path, .. } if path == "permissions.deny"
        )));
    }

    // REQ-YF-TUNE-005: Agent is never added to the deny set, even under --force.
    #[test]
    fn agent_never_denied() {
        let (out, _) = merge(&Value::Object(Map::new()), &profile(), true);
        assert!(
            !deny_of(&out).contains(&"Agent".to_string()),
            "Agent must never be denied"
        );
    }

    // REQ-YF-TUNE-005: preserve-order — existing keys keep their positions, new
    // keys append after.
    #[test]
    fn preserves_key_order() {
        let existing = serde_json::json!({ "zzzCustom": 1, "todoFeatureEnabled": false });
        let (out, _) = merge(&existing, &profile(), false);
        let keys: Vec<&String> = out.as_object().unwrap().keys().collect();
        assert_eq!(
            keys[0], "zzzCustom",
            "existing first key keeps its position"
        );
        assert_eq!(
            keys[1], "todoFeatureEnabled",
            "existing second key keeps its position"
        );
    }
}
