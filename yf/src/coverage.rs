//! SPEC coverage check (plan-010 bead 6.5).
//!
//! Asserts that every macro requirement in the root `SPEC.md` marked
//! `*(testable)*` (format: `**REQ-YF-CLI-001** *(testable)*`) maps to at least
//! one in-crate test that **names** its REQ id via a `// REQ-YF-...` comment —
//! or is explicitly listed in [`ALLOWLIST`] with a documented reason. The check
//! runs under `cargo test`, so CI enforces forward REQ→test coverage: an
//! unmapped testable requirement FAILS the build.
//!
//! ## Honest scope (names, not asserts)
//!
//! This proves a test *names* a REQ id, not that its assertions actually verify
//! the requirement's intent. A `// REQ-YF-X-001` comment anywhere in a test
//! source satisfies the mapping; whether the test body truly exercises X-001 is
//! a human-review concern this check does NOT and cannot decide. It is a
//! tripwire against requirements that no test even claims to cover — not a proof
//! of correctness.
//!
//! ## Allowlist
//!
//! Some testable requirements are verified only by an external mechanism (a CI
//! release workflow, the drift-check gate, integration-only surfaces) and have
//! no in-crate unit test to tag. Rather than let those silently pass, each is
//! enumerated in [`ALLOWLIST`] with the mechanism that covers it. The check
//! passes only if every testable REQ is either (a) tagged in a `.rs` source or
//! (b) present in the allowlist — making coverage gaps explicit and reviewable.

#![cfg(test)]

use std::path::{Path, PathBuf};

/// Requirements that are testable per SPEC but have no in-crate unit test to
/// tag, because they are verified by an external mechanism. Each entry is
/// `(REQ id, reason)`. Keep this list small and reviewed: adding an entry is an
/// explicit acknowledgement that the requirement is NOT unit-covered in-crate.
const ALLOWLIST: &[(&str, &str)] = &[
    // CLI surface *shape* (subcommands / global flags) is declared by the clap
    // derive structs in `cli.rs`; there is no standalone unit test asserting the
    // command tree. Exercised indirectly by every command's tests + the
    // integration/help surface.
    ("REQ-YF-CLI-001", "covered by clap command-tree (cli.rs) + per-command tests; no dedicated structural unit test"),
    ("REQ-YF-CLI-002", "covered by clap arg definitions (cli.rs SkillsCommon: --scope/--surface/--target/--dry-run); no dedicated structural unit test"),
    ("REQ-YF-CLI-003", "covered by the --json flags on every clap subcommand (cli.rs) and the non-zero exit path (REQ-YF-DOCTOR-002 / preflight exit semantics); no dedicated structural unit test"),
    // Distribution is a release-pipeline concern, not in-crate behavior.
    ("REQ-YF-DIST-001", "covered by CI: cargo-dist release workflow (.github/workflows/release.yml) builds the {darwin,linux}x{amd64,arm64} matrix; not unit-testable in-crate"),
    ("REQ-YF-DIST-002", "covered by CI: the release workflow publishes/updates the dixson3/homebrew-tap formula (no runtime depends_on since v0.3.1); not unit-testable in-crate"),
    // doctor --json + non-zero exit is the same exit-code mechanism as CLI-003;
    // doctor's unit tests tag DOCTOR-001 (axis logic), not the exit/json wiring.
    ("REQ-YF-DOCTOR-002", "covered by the doctor exit-code/--json wiring (cmd/doctor/mod.rs run) shared with REQ-YF-CLI-003; doctor unit tests tag the axis logic (DOCTOR-001), not the exit path"),
    // Flag behaviors layered on the install closure; the parity golden tags
    // INSTALL-003/004 (groups + closure), not the --strict/--force/--group flags.
    ("REQ-YF-INSTALL-005", "covered by the install front-door flag wiring (cmd/install.rs: --group/--strict/--force) atop the parity-tested closure (INSTALL-003/004); no dedicated flag-behavior unit test"),
    // bd min-version detection: the comparison logic is exercised by the
    // DOCTOR-001-tagged version tests; the PRE-002 kernel surface is not
    // separately tagged.
    ("REQ-YF-PRE-002", "covered indirectly by the bd min-version comparison tested under DOCTOR-001 (cmd/doctor/checks.rs) which shares the >=1.0.5 threshold; the preflight kernel surface is not separately tagged"),
    // Rename cleanliness is a repo-wide drift concern verified by the
    // drift-check gate, not by an in-crate test.
    ("REQ-YF-RENAME-003", "covered by the drift-check gate (no stale bdplan/bdresearch reference post-rename); repo-wide drift, not unit-testable in-crate"),
];

/// Root of the `yf` crate (the dir holding `Cargo.toml`).
fn manifest_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

/// Parse every testable macro requirement id out of the root `SPEC.md`.
///
/// Matches lines of the form `**REQ-YF-<AREA>-<NNN>** *(testable)*` and returns
/// the bare ids (e.g. `REQ-YF-CLI-001`), sorted and de-duplicated.
fn testable_reqs(spec: &str) -> Vec<String> {
    let mut ids: Vec<String> = spec
        .lines()
        .filter_map(|line| {
            // Look for the marker first; cheap reject for most lines.
            if !line.contains("*(testable)*") {
                return None;
            }
            let start = line.find("**REQ-YF-")? + 2; // skip leading `**`
            let rest = &line[start..];
            let end = rest.find("**")?;
            let id = &rest[..end];
            if is_req_id(id) {
                Some(id.to_string())
            } else {
                None
            }
        })
        .collect();
    ids.sort();
    ids.dedup();
    ids
}

/// Shape check: `REQ-YF-<UPPER>-<digits>`.
fn is_req_id(id: &str) -> bool {
    let Some(tail) = id.strip_prefix("REQ-YF-") else {
        return false;
    };
    let Some((area, num)) = tail.rsplit_once('-') else {
        return false;
    };
    !area.is_empty()
        && area.bytes().all(|b| b.is_ascii_uppercase())
        && !num.is_empty()
        && num.bytes().all(|b| b.is_ascii_digit())
}

/// Collect every `// REQ-YF-...` tag present in the crate's `.rs` sources by
/// walking `<manifest>/src` recursively at test time.
///
/// This module's own file (`coverage.rs`) is excluded: it is the *checker*, and
/// its parser fixtures contain literal REQ ids that are not real test tags.
fn tagged_reqs(src_root: &Path) -> std::collections::BTreeSet<String> {
    let mut tags = std::collections::BTreeSet::new();
    let mut stack = vec![src_root.to_path_buf()];
    while let Some(dir) = stack.pop() {
        let Ok(entries) = std::fs::read_dir(&dir) else {
            continue;
        };
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                stack.push(path);
            } else if path.extension().is_some_and(|e| e == "rs") {
                if path.file_name().is_some_and(|n| n == "coverage.rs") {
                    continue;
                }
                if let Ok(text) = std::fs::read_to_string(&path) {
                    collect_tags(&text, &mut tags);
                }
            }
        }
    }
    tags
}

/// Extract `// REQ-YF-<AREA>-<NNN>` ids from a source string.
fn collect_tags(text: &str, out: &mut std::collections::BTreeSet<String>) {
    for (idx, _) in text.match_indices("// REQ-YF-") {
        let rest = &text[idx + "// ".len()..];
        // The id runs while chars are id-legal (REQ-YF-<UPPER>-<digit>).
        let end = rest
            .find(|c: char| !(c.is_ascii_uppercase() || c.is_ascii_digit() || c == '-'))
            .unwrap_or(rest.len());
        let id = &rest[..end];
        if is_req_id(id) {
            out.insert(id.to_string());
        }
    }
}

/// REQ (coverage): every `*(testable)*` macro REQ in SPEC.md must be tagged by
/// at least one in-crate test source OR be on the documented allowlist.
#[test]
fn every_testable_req_is_tagged_or_allowlisted() {
    let spec_path = manifest_dir().join("../SPEC.md");
    let spec = std::fs::read_to_string(&spec_path)
        .unwrap_or_else(|e| panic!("cannot read SPEC.md at {}: {e}", spec_path.display()));

    let testable = testable_reqs(&spec);
    assert!(
        !testable.is_empty(),
        "no `*(testable)*` REQ-YF requirements found in {} — parser or SPEC drift?",
        spec_path.display()
    );

    let tagged = tagged_reqs(&manifest_dir().join("src"));
    let allow: std::collections::BTreeSet<&str> = ALLOWLIST.iter().map(|(id, _)| *id).collect();

    let unmapped: Vec<&String> = testable
        .iter()
        .filter(|id| !tagged.contains(id.as_str()) && !allow.contains(id.as_str()))
        .collect();

    assert!(
        unmapped.is_empty(),
        "SPEC coverage gap: {} testable REQ-YF requirement(s) have no `// {{id}}` test \
         tag and no allowlist entry:\n  {}\n\nFix each by either tagging a test that exercises \
         it (`// {{id}}`) or adding a reviewed ALLOWLIST entry in yf/src/coverage.rs.",
        unmapped.len(),
        unmapped
            .iter()
            .map(|id| id.as_str())
            .collect::<Vec<_>>()
            .join("\n  ")
    );
}

/// Allowlist hygiene: an allowlist entry must name a real testable REQ, and must
/// NOT shadow a requirement that is in fact tagged (which would be stale). This
/// keeps the allowlist honest as tags are added over time.
#[test]
fn allowlist_entries_are_relevant_and_not_stale() {
    let spec_path = manifest_dir().join("../SPEC.md");
    let spec = std::fs::read_to_string(&spec_path)
        .unwrap_or_else(|e| panic!("cannot read SPEC.md at {}: {e}", spec_path.display()));
    let testable: std::collections::BTreeSet<String> = testable_reqs(&spec).into_iter().collect();
    let tagged = tagged_reqs(&manifest_dir().join("src"));

    for (id, reason) in ALLOWLIST {
        assert!(
            testable.contains(*id),
            "allowlist entry {id} is not a `*(testable)*` REQ in SPEC.md \
             (typo, or the requirement is no longer testable)"
        );
        assert!(
            !tagged.contains(*id),
            "allowlist entry {id} is now tagged by a test — remove it from the ALLOWLIST \
             (reason was: {reason:?})"
        );
    }
}

#[cfg(test)]
mod parser_tests {
    use super::*;

    #[test]
    fn parses_testable_ids_only() {
        let spec = "\
**REQ-YF-CLI-001** *(testable)* shape.\n\
- **REQ-YF-INSTALL-006** companion-rule install (NOT testable).\n\
**REQ-YF-MARK-002** *(testable)* marker.\n";
        let ids = testable_reqs(spec);
        assert_eq!(ids, vec!["REQ-YF-CLI-001", "REQ-YF-MARK-002"]);
    }

    #[test]
    fn collects_line_tags() {
        let mut out = std::collections::BTreeSet::new();
        collect_tags(
            "// REQ-YF-PRE-002: detect tools.\n/// REQ-YF-CLI-004 doc tag.",
            &mut out,
        );
        assert!(out.contains("REQ-YF-PRE-002"));
        // `/// REQ-YF-...` contains `// REQ-YF-...`, so it is collected too.
        assert!(out.contains("REQ-YF-CLI-004"));
    }

    #[test]
    fn req_id_shape() {
        assert!(is_req_id("REQ-YF-CLI-001"));
        assert!(!is_req_id("REQ-YF-cli-001"));
        assert!(!is_req_id("REQ-YF-CLI-"));
        assert!(!is_req_id("REQ-YF-CLI"));
    }
}
