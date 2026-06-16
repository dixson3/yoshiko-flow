//! Consolidated tree-hash + marker + prune test suite (bead 6.2,
//! REQ-YF-MARK-001/002/003/004).
//!
//! marker.rs and cmd/status.rs already carry focused unit tests on these axes;
//! this module adds the cross-cutting, end-to-end assertions the per-file tests
//! don't (multi-file ordering independence WITH a marked SKILL.md, the
//! deploy→prune lifecycle through the real cmd helpers asserting an embedded file
//! is never pruned, and the status 4-axis flip via `skill_health`). It does NOT
//! duplicate the in-`marker.rs` strip/inject/parse unit tests — those stay where
//! the private helpers live.

use crate::cmd::common;
use crate::{embed, marker};

/// A skill that ships a SKILL.md plus other files (so ordering/marker-strip
/// interaction is exercised over a real multi-file tree).
const SKILL: &str = "yf-beads-extra";

// REQ-YF-MARK-001: `embedded_tree_hash` is stable across repeated calls AND the
// canonical sort makes it independent of the input file ORDER — proven over a
// real multi-file embedded skill (not a 2-file synthetic).
#[test]
fn req_yf_mark_001_tree_hash_deterministic_and_order_independent() {
    // Repeated calls are stable.
    let a = marker::embedded_tree_hash(SKILL);
    let b = marker::embedded_tree_hash(SKILL);
    assert_eq!(a, b, "embedded_tree_hash must be deterministic");
    assert_eq!(a.len(), 64);

    // Build the file list two ways (forward and reversed) and confirm tree_hash
    // collapses both to the same value — the sort is canonical.
    let mut files: Vec<(String, Vec<u8>)> = Vec::new();
    for rel in embed::skill_files(SKILL) {
        let bytes = embed::read_file(&format!("{SKILL}/{rel}"))
            .unwrap()
            .into_owned();
        files.push((rel, bytes));
    }
    assert!(files.len() >= 2, "need a multi-file skill to test ordering");
    let forward = marker::tree_hash(&files);
    let mut reversed = files.clone();
    reversed.reverse();
    let backward = marker::tree_hash(&reversed);
    assert_eq!(
        forward, backward,
        "tree_hash must be input-order-independent"
    );
    // And it equals the embed-API path's hash.
    assert_eq!(forward, a);
}

// REQ-YF-MARK-001/002: marker-strip invariance over a multi-file tree — a
// deployed copy whose SKILL.md carries an injected marker hashes IDENTICALLY to
// the embedded source (deployed == embedded), and the marker is the only change.
#[test]
fn req_yf_mark_001_marker_strip_invariance_deployed_equals_embedded() {
    let tmp = tempfile::tempdir().unwrap();
    let skills_dir = tmp.path().join("skills");
    let embedded = marker::embedded_tree_hash(SKILL);

    // deploy_skill injects the marker into the written SKILL.md exactly as install.
    common::deploy_skill(SKILL, &skills_dir, /*prune=*/ false).unwrap();
    let skill_root = skills_dir.join(SKILL);

    // The deployed SKILL.md differs from the embedded bytes (marker present)...
    let deployed_md = std::fs::read_to_string(skill_root.join("SKILL.md")).unwrap();
    let embedded_md = String::from_utf8(
        embed::read_file(&format!("{SKILL}/SKILL.md"))
            .unwrap()
            .into_owned(),
    )
    .unwrap();
    assert_ne!(
        deployed_md, embedded_md,
        "deployed SKILL.md must carry a marker"
    );
    assert!(marker::parse_marker(&deployed_md).is_some());

    // ...yet the marker-stripped deployed tree hashes equal to embedded.
    let (ok, actual) = marker::verify(&skill_root, &embedded).unwrap();
    assert!(
        ok,
        "deployed (marked) tree {actual} must equal embedded {embedded}"
    );
}

// REQ-YF-MARK-002: inject→parse round-trips; inject→strip restores the marker-free
// original; injecting over an existing marker REPLACES (never duplicates). Driven
// against a real embedded SKILL.md.
#[test]
fn req_yf_mark_002_inject_strip_parse_round_trip_and_replace() {
    let original = String::from_utf8(
        embed::read_file(&format!("{SKILL}/SKILL.md"))
            .unwrap()
            .into_owned(),
    )
    .unwrap();

    // inject → parse recovers (version, tree).
    let once = marker::inject_marker(&original, "1.2.3", "feedface");
    let (v, t) = marker::parse_marker(&once).expect("marker parses");
    assert_eq!((v.as_str(), t.as_str()), ("1.2.3", "feedface"));

    // inject → strip restores the byte-identical original.
    assert_eq!(
        marker::strip_marker(&once),
        original,
        "strip must restore original"
    );

    // Re-inject over an existing marker REPLACES it (exactly one marker remains).
    let twice = marker::inject_marker(&once, "2.0.0", "beadcafe");
    assert_eq!(
        twice.matches("<!-- yf-skills:").count(),
        1,
        "re-inject must replace, not duplicate"
    );
    let (v2, t2) = marker::parse_marker(&twice).unwrap();
    assert_eq!((v2.as_str(), t2.as_str()), ("2.0.0", "beadcafe"));
    // Stripping the twice-injected text still returns the same original.
    assert_eq!(marker::strip_marker(&twice), original);
}

// REQ-YF-MARK-004: prune correctness through the real cmd helpers — a stray
// deployed file is removed on upgrade, while every EMBEDDED file survives (an
// embedded file is never pruned). After prune the tree is unmodified again.
#[test]
fn req_yf_mark_004_prune_removes_stray_keeps_embedded() {
    let tmp = tempfile::tempdir().unwrap();
    let skills_dir = tmp.path().join("skills");
    common::deploy_skill(SKILL, &skills_dir, false).unwrap();
    let skill_root = skills_dir.join(SKILL);

    // Add a stray file in a nested dir absent from the embedded tree.
    let stray_dir = skill_root.join("scratch");
    std::fs::create_dir_all(&stray_dir).unwrap();
    let stray = stray_dir.join("ORPHAN.md");
    std::fs::write(&stray, b"orphan\n").unwrap();

    // The dry-run extras list names exactly the stray (no embedded file).
    let extras = common::extra_deployed_files(SKILL, &skills_dir).unwrap();
    assert_eq!(
        extras,
        vec!["scratch/ORPHAN.md".to_string()],
        "only the stray is extra"
    );

    // Re-deploy with prune: the stray (and its now-empty dir) go; embedded stays.
    common::deploy_skill(SKILL, &skills_dir, /*prune=*/ true).unwrap();
    assert!(!stray.exists(), "stray file must be pruned");
    assert!(!stray_dir.exists(), "now-empty stray dir must be removed");
    for rel in embed::skill_files(SKILL) {
        assert!(
            skill_root.join(&rel).is_file(),
            "embedded file must NEVER be pruned: {rel}"
        );
    }

    // After prune the deployed tree hashes equal to embedded again.
    let h = common::skill_health(SKILL, &skills_dir).unwrap();
    assert!(
        h.unmodified && h.complete && h.up_to_date,
        "post-prune health: {h:?}"
    );
}

// REQ-YF-MARK-003: the status 4-axis through `skill_health` — a fresh install is
// installed/up-to-date/complete/unmodified; tampering a deployed embedded file
// flips ONLY `unmodified` to false (the marker, untouched, still reads
// up-to-date). Consolidated here over the same helper status.rs uses.
#[test]
fn req_yf_mark_003_status_four_axis_and_tamper_flips_unmodified() {
    let tmp = tempfile::tempdir().unwrap();
    let skills_dir = tmp.path().join("skills");
    common::deploy_skill(SKILL, &skills_dir, false).unwrap();
    let skill_root = skills_dir.join(SKILL);

    let h = common::skill_health(SKILL, &skills_dir).unwrap();
    assert!(h.installed, "installed");
    assert!(h.up_to_date, "up_to_date (marker == embedded)");
    assert!(h.complete, "complete (all embedded files present)");
    assert!(h.unmodified, "unmodified (deployed tree hashes equal)");
    assert_eq!(h.marker_hash.as_deref(), Some(h.embedded_hash.as_str()));
    assert_eq!(h.doctor_state(), "ok");

    // Tamper a NON-SKILL.md embedded file (so the marker stays valid).
    let victim = embed::skill_files(SKILL)
        .into_iter()
        .find(|f| f != "SKILL.md")
        .expect("a non-SKILL.md embedded file");
    let path = skill_root.join(&victim);
    let mut bytes = std::fs::read(&path).unwrap();
    bytes.extend_from_slice(b"\n# tampered\n");
    std::fs::write(&path, bytes).unwrap();

    let h2 = common::skill_health(SKILL, &skills_dir).unwrap();
    assert!(h2.installed && h2.complete, "still installed + complete");
    assert!(h2.up_to_date, "marker untouched → still up_to_date");
    assert!(!h2.unmodified, "tampering flips unmodified to false");
    assert_eq!(h2.doctor_state(), "modified");
}
