//! Per-skill tree hash and integrity marker (REQ-YF-MARK-001/002).
//!
//! ## Tree hash (REQ-YF-MARK-001)
//!
//! A skill's tree hash is a SHA256 over its files, sorted by skill-relative
//! path. For each file we feed `relpath.as_bytes()` then the file's raw bytes
//! into one rolling digest; the final lowercase hex is the tree hash.
//!
//! The one subtlety: `SKILL.md` carries an injected integrity marker line once
//! deployed (REQ-YF-MARK-002). To make a **deployed (marked)** copy hash
//! **identically** to the **embedded source**, `SKILL.md`'s bytes are
//! marker-stripped *before* being fed to the digest. Everything else is hashed
//! byte-for-byte.
//!
//! Two builders produce the same list shape so embedded and deployed hashes are
//! comparable:
//!
//! - [`embedded_tree_hash`] — file list from the embed API ([`crate::embed`]).
//! - [`deployed_tree_hash`] — file list walked from an on-disk skill dir.
//!
//! Both use skill-relative paths and the same sort, and both marker-strip
//! `SKILL.md`, so `embedded == deployed` iff the deployed tree is unmodified.
//!
//! ## Marker (REQ-YF-MARK-002)
//!
//! The marker is a single line inserted immediately after the SKILL.md YAML
//! frontmatter's closing `---`:
//!
//! ```text
//! <!-- yf-skills: v=<version> tree=<sha256> -->
//! ```
//!
//! [`inject_marker`] inserts or replaces it, [`strip_marker`] removes it,
//! [`parse_marker`] reads back `(version, tree)`.

// Public marker/tree-hash API consumed by the (not-yet-wired) install / upgrade
// / status commands (beads 1.5/1.6).
#![allow(dead_code)]

use std::io;
use std::path::{Path, PathBuf};

use sha2::{Digest, Sha256};

use crate::embed;

/// The SKILL.md filename whose bytes are marker-stripped before hashing.
const SKILL_MD: &str = "SKILL.md";

/// Marker line prefix; the full line is `<!-- yf-skills: v=… tree=… -->`.
const MARKER_PREFIX: &str = "<!-- yf-skills:";

// --- Tree hash (REQ-YF-MARK-001) ---------------------------------------------

/// SHA256 over `files` sorted by relpath, feeding `relpath-bytes ++ file-bytes`
/// for each. `SKILL.md` is marker-stripped before its bytes are fed, so a marked
/// deployed copy hashes identically to the unmarked embedded source. Returns
/// lowercase hex.
pub fn tree_hash(files: &[(String, Vec<u8>)]) -> String {
    let mut sorted: Vec<&(String, Vec<u8>)> = files.iter().collect();
    sorted.sort_by(|a, b| a.0.cmp(&b.0));

    let mut hasher = Sha256::new();
    for (relpath, bytes) in sorted {
        hasher.update(relpath.as_bytes());
        if relpath == SKILL_MD {
            // Marker-strip before hashing (REQ-YF-MARK-001). Non-UTF8 SKILL.md
            // is implausible; fall back to raw bytes rather than panic.
            match std::str::from_utf8(bytes) {
                Ok(text) => hasher.update(strip_marker(text).as_bytes()),
                Err(_) => hasher.update(bytes),
            }
        } else {
            hasher.update(bytes);
        }
    }
    hex_lower(&hasher.finalize())
}

/// Tree hash of an embedded skill, built from [`crate::embed`]. Paths are
/// skill-relative (as [`embed::skill_files`] returns).
pub fn embedded_tree_hash(skill: &str) -> String {
    let mut files: Vec<(String, Vec<u8>)> = Vec::new();
    for relpath in embed::skill_files(skill) {
        let full = format!("{skill}/{relpath}");
        if let Some(bytes) = embed::read_file(&full) {
            files.push((relpath, bytes.into_owned()));
        }
    }
    tree_hash(&files)
}

/// Tree hash of an on-disk deployed skill dir, built by walking `skill_dir`.
/// Paths are made skill-relative (the `skill_dir` prefix stripped) and sorted
/// identically to [`embedded_tree_hash`]; `SKILL.md` is marker-stripped.
pub fn deployed_tree_hash(skill_dir: &Path) -> io::Result<String> {
    let mut files: Vec<(String, Vec<u8>)> = Vec::new();
    walk_files(skill_dir, skill_dir, &mut files)?;
    Ok(tree_hash(&files))
}

/// Recursively collect `(skill-relative-path, bytes)` for every file under
/// `dir`, with paths relative to `root`. Relpaths use `/` separators to match
/// the embed API regardless of platform.
fn walk_files(root: &Path, dir: &Path, out: &mut Vec<(String, Vec<u8>)>) -> io::Result<()> {
    let mut entries: Vec<PathBuf> = std::fs::read_dir(dir)?
        .map(|e| e.map(|e| e.path()))
        .collect::<io::Result<_>>()?;
    entries.sort();
    for path in entries {
        if path.is_dir() {
            walk_files(root, &path, out)?;
        } else if path.is_file() {
            let rel = path
                .strip_prefix(root)
                .map_err(io::Error::other)?;
            let relpath = rel
                .components()
                .map(|c| c.as_os_str().to_string_lossy())
                .collect::<Vec<_>>()
                .join("/");
            let bytes = std::fs::read(&path)?;
            out.push((relpath, bytes));
        }
    }
    Ok(())
}

fn hex_lower(bytes: &[u8]) -> String {
    let mut s = String::with_capacity(bytes.len() * 2);
    for b in bytes {
        s.push_str(&format!("{b:02x}"));
    }
    s
}

// --- Marker (REQ-YF-MARK-002) ------------------------------------------------

/// Build the marker line (no trailing newline) for `version` + `tree` hash.
fn marker_line(version: &str, tree: &str) -> String {
    format!("<!-- yf-skills: v={version} tree={tree} -->")
}

/// Insert (or replace) the integrity marker immediately after the closing `---`
/// of `skill_md`'s YAML frontmatter (REQ-YF-MARK-002). Any pre-existing marker
/// is removed first so injection is idempotent (replace, never duplicate). If
/// there is no frontmatter, the marker is prepended at the top of the file.
pub fn inject_marker(skill_md: &str, version: &str, tree: &str) -> String {
    let stripped = strip_marker(skill_md);
    let line = marker_line(version, tree);

    match frontmatter_close_offset(&stripped) {
        Some(end) => {
            // `end` is the byte offset just past the closing fence line's `\n`
            // (or end-of-string). Insert the marker line there.
            let (head, tail) = stripped.split_at(end);
            // Ensure the marker sits on its own line followed by a newline.
            format!("{head}{line}\n{tail}")
        }
        None => {
            // No frontmatter: prepend.
            if stripped.is_empty() {
                format!("{line}\n")
            } else {
                format!("{line}\n{stripped}")
            }
        }
    }
}

/// Remove the integrity marker line (and its trailing newline) from `skill_md`,
/// returning the marker-free text. Idempotent: text without a marker is
/// returned unchanged.
pub fn strip_marker(skill_md: &str) -> String {
    let mut out = String::with_capacity(skill_md.len());
    for segment in skill_md.split_inclusive('\n') {
        let line = segment.strip_suffix('\n').unwrap_or(segment);
        if line.trim_start().starts_with(MARKER_PREFIX) {
            // Drop this whole line including its newline. A marker with no
            // trailing newline (file-final) is simply dropped.
            continue;
        }
        out.push_str(segment);
    }
    out
}

/// Parse `(version, tree)` from the marker line, if present.
pub fn parse_marker(skill_md: &str) -> Option<(String, String)> {
    for line in skill_md.lines() {
        let t = line.trim();
        if !t.starts_with(MARKER_PREFIX) {
            continue;
        }
        // Body between the prefix and the closing `-->`.
        let body = t.strip_prefix(MARKER_PREFIX)?;
        let body = body.strip_suffix("-->").unwrap_or(body).trim();
        let mut version: Option<String> = None;
        let mut tree: Option<String> = None;
        for tok in body.split_whitespace() {
            if let Some(v) = tok.strip_prefix("v=") {
                version = Some(v.to_string());
            } else if let Some(h) = tok.strip_prefix("tree=") {
                tree = Some(h.to_string());
            }
        }
        if let (Some(v), Some(h)) = (version, tree) {
            return Some((v, h));
        }
    }
    None
}

/// Byte offset just past the SKILL.md frontmatter's closing `---` line
/// (including its trailing newline), or `None` if `text` has no opening fence /
/// no closing fence. Mirrors `frontmatter.rs`'s fence detection: the first line
/// must be exactly `---`, and the close is the next line that is exactly `---`.
fn frontmatter_close_offset(text: &str) -> Option<usize> {
    let mut offset = 0usize;
    let mut first = true;
    let mut opened = false;
    for segment in text.split_inclusive('\n') {
        let line = segment.strip_suffix('\n').unwrap_or(segment);
        if first {
            first = false;
            if line.trim() != "---" {
                return None; // no opening fence
            }
            opened = true;
            offset += segment.len();
            continue;
        }
        if opened && line.trim() == "---" {
            return Some(offset + segment.len());
        }
        offset += segment.len();
    }
    None // never closed
}

// --- Verify helper (REQ-YF-MARK-001) -----------------------------------------

/// Whether a deployed skill dir's recomputed (marker-stripped) tree hash equals
/// `expected_embedded_hash`. Returns the recomputed hash alongside the verdict
/// so callers can report mismatches.
pub fn verify(skill_dir: &Path, expected_embedded_hash: &str) -> io::Result<(bool, String)> {
    let actual = deployed_tree_hash(skill_dir)?;
    Ok((actual == expected_embedded_hash, actual))
}

#[cfg(test)]
mod tests {
    use super::*;

    const FM_SKILL: &str = "---\nname: yf-demo\nskill-group: utility\n---\n# Heading\n\nbody text\n";

    // REQ-YF-MARK-001: embedded tree hash is stable across repeated calls.
    #[test]
    fn embedded_tree_hash_is_deterministic() {
        let a = embedded_tree_hash("yf-beads-extra");
        let b = embedded_tree_hash("yf-beads-extra");
        assert_eq!(a, b);
        assert_eq!(a.len(), 64, "sha256 hex must be 64 chars: {a}");
        assert!(a.chars().all(|c| c.is_ascii_hexdigit() && !c.is_ascii_uppercase()));
    }

    // REQ-YF-MARK-001: tree_hash is order-independent (sorts by relpath).
    #[test]
    fn tree_hash_sorts_by_relpath() {
        let files_a = vec![
            ("b.md".to_string(), b"bbb".to_vec()),
            ("a.md".to_string(), b"aaa".to_vec()),
        ];
        let files_b = vec![
            ("a.md".to_string(), b"aaa".to_vec()),
            ("b.md".to_string(), b"bbb".to_vec()),
        ];
        assert_eq!(tree_hash(&files_a), tree_hash(&files_b));
    }

    // REQ-YF-MARK-001: a SKILL.md WITH a marker hashes equal to the same file
    // WITHOUT one (marker-strip before hashing).
    #[test]
    fn marked_skill_md_hashes_equal_to_unmarked() {
        let unmarked = FM_SKILL.to_string();
        let marked = inject_marker(&unmarked, "0.1.0", "deadbeef");
        assert_ne!(unmarked, marked, "marker must change the raw text");

        let h_unmarked = tree_hash(&[("SKILL.md".to_string(), unmarked.into_bytes())]);
        let h_marked = tree_hash(&[("SKILL.md".to_string(), marked.into_bytes())]);
        assert_eq!(
            h_unmarked, h_marked,
            "marked SKILL.md must hash identically to unmarked"
        );
    }

    // REQ-YF-MARK-001: a NON-SKILL.md file is NOT marker-stripped (marker-like
    // content in other files is hashed verbatim).
    #[test]
    fn non_skill_md_is_not_stripped() {
        let body = b"<!-- yf-skills: v=1 tree=x -->\nreal content\n".to_vec();
        let with = tree_hash(&[("notes.md".to_string(), body.clone())]);
        let stripped: Vec<u8> = b"real content\n".to_vec();
        let without = tree_hash(&[("notes.md".to_string(), stripped)]);
        assert_ne!(with, without);
    }

    // REQ-YF-MARK-002: inject → parse round-trips version + tree.
    #[test]
    fn inject_parse_round_trip() {
        let out = inject_marker(FM_SKILL, "1.2.3", "abc123");
        let (v, t) = parse_marker(&out).expect("marker must parse");
        assert_eq!(v, "1.2.3");
        assert_eq!(t, "abc123");
    }

    // REQ-YF-MARK-002: marker is placed immediately after the frontmatter close.
    #[test]
    fn marker_placed_after_frontmatter() {
        let out = inject_marker(FM_SKILL, "0.1.0", "hh");
        let expected = "---\nname: yf-demo\nskill-group: utility\n---\n\
                        <!-- yf-skills: v=0.1.0 tree=hh -->\n# Heading\n\nbody text\n";
        assert_eq!(out, expected);
    }

    // REQ-YF-MARK-002: inject → strip returns the original marker-free text.
    #[test]
    fn inject_then_strip_is_identity() {
        let out = inject_marker(FM_SKILL, "0.1.0", "hh");
        assert_eq!(strip_marker(&out), FM_SKILL);
    }

    // REQ-YF-MARK-002: injecting into already-marked text REPLACES, not duplicates.
    #[test]
    fn inject_replaces_existing_marker() {
        let once = inject_marker(FM_SKILL, "0.1.0", "old");
        let twice = inject_marker(&once, "0.2.0", "new");
        let count = twice.matches(MARKER_PREFIX).count();
        assert_eq!(count, 1, "exactly one marker after re-inject: {twice}");
        let (v, t) = parse_marker(&twice).unwrap();
        assert_eq!((v.as_str(), t.as_str()), ("0.2.0", "new"));
    }

    // REQ-YF-MARK-002: strip on marker-free text is a no-op.
    #[test]
    fn strip_no_marker_is_noop() {
        assert_eq!(strip_marker(FM_SKILL), FM_SKILL);
    }

    // REQ-YF-MARK-002: no frontmatter → marker prepended; still round-trips.
    #[test]
    fn inject_without_frontmatter_prepends() {
        let text = "# Just a heading\nbody\n";
        let out = inject_marker(text, "9.9.9", "zz");
        assert!(out.starts_with("<!-- yf-skills: v=9.9.9 tree=zz -->\n"));
        assert_eq!(strip_marker(&out), text);
        let (v, t) = parse_marker(&out).unwrap();
        assert_eq!((v.as_str(), t.as_str()), ("9.9.9", "zz"));
    }

    // REQ-YF-MARK-001: deployed_tree_hash of a written-out embedded skill equals
    // embedded_tree_hash (proves embedded vs deployed parity, incl. marker).
    #[test]
    fn deployed_matches_embedded_round_trip() {
        let skill = "yf-beads-extra";
        let embedded = embedded_tree_hash(skill);

        // Materialize the embedded skill to a temp dir, injecting a marker into
        // SKILL.md exactly as a real install would.
        let tmp = std::env::temp_dir().join(format!(
            "yf-marker-test-{}-{}",
            std::process::id(),
            skill
        ));
        std::fs::remove_dir_all(&tmp).ok();
        let skill_root = tmp.join(skill);
        for relpath in embed::skill_files(skill) {
            let bytes = embed::read_file(&format!("{skill}/{relpath}")).unwrap();
            let dest = skill_root.join(&relpath);
            std::fs::create_dir_all(dest.parent().unwrap()).unwrap();
            if relpath == "SKILL.md" {
                let text = String::from_utf8(bytes.into_owned()).unwrap();
                let marked = inject_marker(&text, "0.1.0", &embedded);
                std::fs::write(&dest, marked).unwrap();
            } else {
                std::fs::write(&dest, bytes.as_ref()).unwrap();
            }
        }

        let (ok, actual) = verify(&skill_root, &embedded).unwrap();
        assert!(
            ok,
            "deployed (marked) hash {actual} must equal embedded {embedded}"
        );

        std::fs::remove_dir_all(&tmp).ok();
    }
}
