//! Read-only settings-drift audit over the **effective merged view**
//! (REQ-YF-TUNE-009). Pure over ordered settings layers — no I/O — so the doctor
//! wrapper ([`crate::cmd::doctor::checks`]) does the file reads and this stays
//! unit-testable.
//!
//! Precedence: layers are passed **low → high** (user `settings.json` ← project
//! `settings.json` ← project `settings.local.json`). The effective value at a leaf
//! path is the highest-precedence layer that defines it, so a recommended key set
//! in a *different* layer is **not** a false "missing" (the plan's key case).

#![allow(dead_code)]

use std::collections::BTreeMap;

use serde_json::{Map, Value};

use super::profile::{Kind, Profile};

/// One drift finding against the effective merged view.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Drift {
    /// A recommended path defined in no layer.
    Missing(String),
    /// A scalar path whose effective value differs from the recommendation.
    ScalarConflict {
        path: String,
        effective: Value,
        recommended: Value,
    },
    /// Recommended set members absent from the effective set.
    MissingSetMembers { path: String, missing: Vec<String> },
    /// The `Agent` tool is present in the effective deny set (must never be).
    AgentDenied { path: String },
}

impl Drift {
    /// A one-line human summary of this finding.
    pub fn summary(&self) -> String {
        match self {
            Drift::Missing(p) => format!("missing recommended key `{p}`"),
            Drift::ScalarConflict {
                path,
                effective,
                recommended,
            } => {
                format!("`{path}` = {effective} (effective) ≠ {recommended} (recommended)")
            }
            Drift::MissingSetMembers { path, missing } => {
                format!(
                    "`{path}` missing {} recommended member(s): {}",
                    missing.len(),
                    missing.join(", ")
                )
            }
            Drift::AgentDenied { path } => {
                format!("`{path}` DENIES Agent — every yf agent fans out through it")
            }
        }
    }
}

/// Flatten one settings object to leaf dot-paths (objects recurse; arrays/scalars
/// are leaves). Mirrors the drift-test flattening so the two views agree.
fn flatten_leaves(value: &Value, prefix: &str, out: &mut BTreeMap<String, Value>) {
    match value {
        Value::Object(map) => {
            for (k, v) in map {
                let path = if prefix.is_empty() {
                    k.clone()
                } else {
                    format!("{prefix}.{k}")
                };
                flatten_leaves(v, &path, out);
            }
        }
        other => {
            out.insert(prefix.to_string(), other.clone());
        }
    }
}

/// Compute the effective leaf map across `layers` (low → high precedence). A later
/// layer's leaf value overrides an earlier one.
pub fn effective_leaves(layers: &[&Value]) -> BTreeMap<String, Value> {
    let mut out: BTreeMap<String, Value> = BTreeMap::new();
    for layer in layers {
        let mut this: BTreeMap<String, Value> = BTreeMap::new();
        flatten_leaves(layer, "", &mut this);
        out.extend(this); // later layer overrides
    }
    out
}

/// Audit the profile against the effective merged view of `layers` (low → high).
pub fn audit(profile: &Profile, layers: &[&Value]) -> Vec<Drift> {
    let effective = effective_leaves(layers);
    let mut out = Vec::new();

    for entry in &profile.entries {
        match entry.kind {
            Kind::Scalar => match effective.get(&entry.path) {
                None => out.push(Drift::Missing(entry.path.clone())),
                Some(v) if v == &entry.value => {}
                Some(v) => out.push(Drift::ScalarConflict {
                    path: entry.path.clone(),
                    effective: v.clone(),
                    recommended: entry.value.clone(),
                }),
            },
            Kind::Set => {
                let recommended: Vec<String> = entry
                    .value
                    .as_array()
                    .map(|a| a.iter().map(|x| x.to_string()).collect())
                    .unwrap_or_default();
                match effective.get(&entry.path).and_then(|v| v.as_array()) {
                    None => out.push(Drift::Missing(entry.path.clone())),
                    Some(arr) => {
                        let present: std::collections::BTreeSet<String> =
                            arr.iter().map(|x| x.to_string()).collect();
                        let missing: Vec<String> = recommended
                            .iter()
                            .filter(|m| !present.contains(*m))
                            .cloned()
                            .collect();
                        if !missing.is_empty() {
                            out.push(Drift::MissingSetMembers {
                                path: entry.path.clone(),
                                missing,
                            });
                        }
                        // Agent-denied check on any deny-shaped set.
                        if entry.path.ends_with(".deny")
                            && arr
                                .iter()
                                .any(|x| x == &Value::String(profile.agent_tool.clone()))
                        {
                            out.push(Drift::AgentDenied {
                                path: entry.path.clone(),
                            });
                        }
                    }
                }
            }
        }
    }
    out
}

/// A convenience for a single-object layer (`effective_leaves(&[&obj])`).
pub fn single_layer(obj: Map<String, Value>) -> Value {
    Value::Object(obj)
}

#[cfg(test)]
mod tests {
    use super::super::profile::load_profile;
    use super::*;

    fn profile() -> Profile {
        load_profile("claude-code").unwrap().unwrap()
    }

    // REQ-YF-TUNE-009: an empty effective view flags every recommended entry as
    // drift (all scalars Missing, the deny set Missing).
    #[test]
    fn empty_view_is_all_drift() {
        let empty = serde_json::json!({});
        let drift = audit(&profile(), &[&empty]);
        assert!(drift
            .iter()
            .any(|d| matches!(d, Drift::Missing(p) if p == "todoFeatureEnabled")));
        assert!(drift
            .iter()
            .any(|d| matches!(d, Drift::Missing(p) if p == "permissions.deny")));
    }

    // REQ-YF-TUNE-009: a fully-tuned single layer has zero drift.
    #[test]
    fn tuned_view_has_no_drift() {
        // Build the effective view by merging the profile into an empty object via
        // the merge engine, then audit — should be clean.
        let (tuned, _) = super::super::merge::merge(&serde_json::json!({}), &profile(), false);
        let drift = audit(&profile(), &[&tuned]);
        assert!(
            drift.is_empty(),
            "tuned view must have no drift: {drift:#?}"
        );
    }

    // REQ-YF-TUNE-009: a recommended key set in a DIFFERENT (lower-precedence) layer
    // is NOT a false-missing — the effective view sees it.
    #[test]
    fn key_in_other_layer_is_not_false_missing() {
        let user = serde_json::json!({ "todoFeatureEnabled": false });
        let project = serde_json::json!({ "disableWorkflows": true });
        let local = serde_json::json!({});
        let drift = audit(&profile(), &[&user, &project, &local]);
        // Neither todoFeatureEnabled (in user) nor disableWorkflows (in project) is
        // reported missing.
        assert!(!drift
            .iter()
            .any(|d| matches!(d, Drift::Missing(p) if p == "todoFeatureEnabled")));
        assert!(!drift
            .iter()
            .any(|d| matches!(d, Drift::Missing(p) if p == "disableWorkflows")));
    }

    // REQ-YF-TUNE-009: a higher-precedence layer overriding a good value to a bad
    // one is a scalar conflict.
    #[test]
    fn higher_layer_override_is_conflict() {
        let user = serde_json::json!({ "todoFeatureEnabled": false });
        // local layer (highest precedence) flips it wrong.
        let local = serde_json::json!({ "todoFeatureEnabled": true });
        let drift = audit(&profile(), &[&user, &local]);
        assert!(drift.iter().any(|d| matches!(
            d, Drift::ScalarConflict { path, .. } if path == "todoFeatureEnabled"
        )));
    }

    // REQ-YF-TUNE-009: an Agent deny in the effective view is flagged.
    #[test]
    fn agent_denied_is_flagged() {
        let layer = serde_json::json!({ "permissions": { "deny": ["Agent", "TaskCreate"] } });
        let drift = audit(&profile(), &[&layer]);
        assert!(drift.iter().any(|d| matches!(d, Drift::AgentDenied { .. })));
    }
}
