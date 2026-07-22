//! Assert-agreement between the embedded profile and the **reference-baseline**
//! block in `docs/recommended-settings.md` (REQ-YF-TUNE-008).
//!
//! The doc block is a `jsonc` fence carrying hand-authored `//` rationale comments.
//! Those comments are the authored prose and stay authored — this module does NOT
//! regenerate the block. It only proves the block's **data** (keys, scalar values,
//! array membership) still agrees with the embedded profile, so the two never
//! silently drift. The parse is JSONC-tolerant (strip `//` line comments) and the
//! comparison flattens both sides to leaf dot-paths (arrays compared as sets).

#![allow(dead_code)]

use std::collections::{BTreeMap, BTreeSet};

use anyhow::{anyhow, Context, Result};

use super::profile::{Kind, Profile};

/// Strip `//` line comments from a JSONC string, preserving `//` sequences that
/// appear **inside** a JSON string literal (none in the reference baseline, but
/// handled for correctness). Block `/* */` comments are not used and not stripped.
pub fn strip_line_comments(src: &str) -> String {
    let mut out = String::with_capacity(src.len());
    for line in src.lines() {
        let mut in_str = false;
        let mut escaped = false;
        let bytes = line.as_bytes();
        let mut cut = None;
        let mut i = 0;
        while i < bytes.len() {
            let c = bytes[i] as char;
            if in_str {
                if escaped {
                    escaped = false;
                } else if c == '\\' {
                    escaped = true;
                } else if c == '"' {
                    in_str = false;
                }
            } else if c == '"' {
                in_str = true;
            } else if c == '/' && i + 1 < bytes.len() && bytes[i + 1] as char == '/' {
                cut = Some(i);
                break;
            }
            i += 1;
        }
        match cut {
            Some(idx) => out.push_str(&line[..idx]),
            None => out.push_str(line),
        }
        out.push('\n');
    }
    out
}

/// Extract the single ```` ```jsonc ```` fenced block that follows the
/// `## Reference baseline` heading in `doc`.
pub fn extract_reference_baseline(doc: &str) -> Result<String> {
    let anchor = doc
        .find("## Reference baseline")
        .ok_or_else(|| anyhow!("no `## Reference baseline` heading in doc"))?;
    let after = &doc[anchor..];
    let fence = after
        .find("```jsonc")
        .ok_or_else(|| anyhow!("no ```jsonc fence after `## Reference baseline`"))?;
    let body_start = after[fence..]
        .find('\n')
        .map(|nl| fence + nl + 1)
        .ok_or_else(|| anyhow!("malformed jsonc fence (no newline)"))?;
    let close = after[body_start..]
        .find("```")
        .ok_or_else(|| anyhow!("unterminated ```jsonc fence"))?;
    Ok(after[body_start..body_start + close].to_string())
}

/// Parse the reference-baseline block into JSON (JSONC-tolerant).
pub fn parse_reference_baseline(doc: &str) -> Result<serde_json::Value> {
    let block = extract_reference_baseline(doc)?;
    let stripped = strip_line_comments(&block);
    serde_json::from_str(&stripped)
        .context("reference-baseline block is not valid JSON after comment strip")
}

/// Flatten a JSON object to leaf dot-paths. Objects recurse; arrays and scalars
/// are leaves (an array leaf keeps its `Value::Array`). Matches the profile's
/// path model (`permissions.deny` is one set-valued leaf, not per-element paths).
fn flatten_leaves(
    value: &serde_json::Value,
    prefix: &str,
    out: &mut BTreeMap<String, serde_json::Value>,
) {
    match value {
        serde_json::Value::Object(map) => {
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

/// A drift finding: a leaf path that disagrees between the doc block and profile.
#[derive(Debug, PartialEq, Eq)]
pub enum Divergence {
    /// A leaf path in the doc block that the profile does not declare.
    ExtraInDoc(String),
    /// A profile path missing from the doc block.
    MissingInDoc(String),
    /// A scalar path whose doc value differs from the profile value.
    ScalarMismatch {
        path: String,
        doc: String,
        profile: String,
    },
    /// A set path whose doc membership differs from the profile membership.
    SetMismatch {
        path: String,
        only_in_doc: Vec<String>,
        only_in_profile: Vec<String>,
    },
}

/// Compare the doc reference-baseline block against the profile; return every
/// divergence (empty = agreement).
pub fn diff(doc_json: &serde_json::Value, profile: &Profile) -> Vec<Divergence> {
    let mut doc_leaves: BTreeMap<String, serde_json::Value> = BTreeMap::new();
    flatten_leaves(doc_json, "", &mut doc_leaves);

    let mut out = Vec::new();
    let profile_paths: BTreeSet<&str> = profile.entries.iter().map(|e| e.path.as_str()).collect();

    // Extra keys in the doc block (present in doc, absent from profile).
    for path in doc_leaves.keys() {
        if !profile_paths.contains(path.as_str()) {
            out.push(Divergence::ExtraInDoc(path.clone()));
        }
    }

    for entry in &profile.entries {
        let Some(doc_val) = doc_leaves.get(&entry.path) else {
            out.push(Divergence::MissingInDoc(entry.path.clone()));
            continue;
        };
        match entry.kind {
            Kind::Scalar => {
                if doc_val != &entry.value {
                    out.push(Divergence::ScalarMismatch {
                        path: entry.path.clone(),
                        doc: doc_val.to_string(),
                        profile: entry.value.to_string(),
                    });
                }
            }
            Kind::Set => {
                let to_set = |v: &serde_json::Value| -> BTreeSet<String> {
                    v.as_array()
                        .map(|a| a.iter().map(|x| x.to_string()).collect())
                        .unwrap_or_default()
                };
                let doc_set = to_set(doc_val);
                let prof_set = to_set(&entry.value);
                if doc_set != prof_set {
                    out.push(Divergence::SetMismatch {
                        path: entry.path.clone(),
                        only_in_doc: doc_set.difference(&prof_set).cloned().collect(),
                        only_in_profile: prof_set.difference(&doc_set).cloned().collect(),
                    });
                }
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::super::profile::load_profile;
    use super::*;

    fn read_doc() -> String {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("../docs/recommended-settings.md");
        std::fs::read_to_string(&path)
            .unwrap_or_else(|e| panic!("cannot read {}: {e}", path.display()))
    }

    // REQ-YF-TUNE-008: the fenced reference-baseline block in
    // docs/recommended-settings.md agrees with the embedded profile — same keys,
    // same scalar values, same array (set) membership. Fails CI on divergence.
    #[test]
    fn doc_reference_baseline_agrees_with_profile() {
        let doc = read_doc();
        let doc_json = parse_reference_baseline(&doc).expect("parse reference baseline");
        let profile = load_profile("claude-code").unwrap().unwrap();
        let divergences = diff(&doc_json, &profile);
        assert!(
            divergences.is_empty(),
            "reference-baseline block drifted from the profile:\n{divergences:#?}\n\n\
             Fix docs/recommended-settings.md (or the profile) so they agree. The `//` \
             comments are hand-authored prose — only the key/value DATA is checked."
        );
    }

    // REQ-YF-TUNE-008: comment-strip keeps string content intact and drops trailing
    // `//` comments.
    #[test]
    fn strip_line_comments_preserves_strings() {
        let src = "{\n  \"a\": \"http://x\", // trailing\n  \"b\": 1\n}\n";
        let out = strip_line_comments(src);
        assert!(
            out.contains("http://x"),
            "must not strip // inside a string: {out}"
        );
        assert!(
            !out.contains("trailing"),
            "must strip the trailing comment: {out}"
        );
        let v: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(v["a"], serde_json::json!("http://x"));
        assert_eq!(v["b"], serde_json::json!(1));
    }

    // REQ-YF-TUNE-008: the diff detects an injected scalar mismatch (guards the
    // guard — an all-green diff on a doctored input would be a false negative).
    #[test]
    fn diff_flags_injected_mismatch() {
        let doc = read_doc();
        let mut doc_json = parse_reference_baseline(&doc).unwrap();
        doc_json["todoFeatureEnabled"] = serde_json::json!(true); // wrong polarity
        let profile = load_profile("claude-code").unwrap().unwrap();
        let divergences = diff(&doc_json, &profile);
        assert!(
            divergences.iter().any(|d| matches!(d, Divergence::ScalarMismatch { path, .. } if path == "todoFeatureEnabled")),
            "expected a ScalarMismatch on todoFeatureEnabled, got {divergences:#?}"
        );
    }
}
