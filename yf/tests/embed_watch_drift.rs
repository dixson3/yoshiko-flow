//! Drift guard for the `build.rs` ↔ `embed.rs` couplings introduced by the #137 fix.
//!
//! The fix works only if `build.rs` watches the SAME directory `embed.rs` embeds. Nothing
//! in the compiler enforces that: they are two independent string literals in two files.
//! A future folder move that updates one and not the other silently restores #137 — with
//! every test still green, because `embed_addition.rs` builds its own scratch crate and
//! therefore proves the MECHANISM, not this repo's wiring.
//!
//! These two tests are the other half. Together with `embed_addition.rs` they close the
//! loop: the mechanism works (there) AND this crate is actually wired to use it (here).
//!
//! Second coupling: `embed.rs` excludes `*.pyc` / `__pycache__` from the embed. Those
//! excludes are recorded here so that a change to them is a deliberate, test-updating act.
//! The watch itself is a plain directory watch and CANNOT mirror them — cargo's
//! `rerun-if-changed` has no exclude mechanism and walks directories recursively. That
//! asymmetry is intentional and measured (plan-041 E6: per-file emission mirroring the
//! excludes was refuted — it cannot observe additions at all), so this test pins the
//! asymmetry rather than asserting a parity that must not exist.

const BUILD_RS: &str = include_str!("../build.rs");
const EMBED_RS: &str = include_str!("../src/embed.rs");

/// Extract the `#[folder = "..."]` literal from `embed.rs`.
fn embed_folder() -> String {
    let marker = "#[folder = \"";
    let start = EMBED_RS
        .find(marker)
        .expect("embed.rs no longer contains a `#[folder = \"...\"]` attribute")
        + marker.len();
    let rest = &EMBED_RS[start..];
    let end = rest.find('"').expect("unterminated #[folder] literal");
    rest[..end].to_string()
}

/// The folder `build.rs` watches must be exactly the folder `embed.rs` embeds.
///
/// Guards the #137 regression a folder move would otherwise reintroduce silently.
#[test]
fn build_rs_watches_the_folder_embed_rs_embeds() {
    let folder = embed_folder();
    let expected = format!("cargo:rerun-if-changed={folder}");

    assert!(
        BUILD_RS.contains(&expected),
        "DRIFT: embed.rs embeds `{folder}` but build.rs does not emit `{expected}`.\n\
         The embed root and the build watch have diverged — additions under `{folder}` \
         will silently stop reaching the binary (#137). Update build.rs to watch the new \
         folder."
    );

    // The companion `.` line is what keeps the implicit whole-package watch alive after
    // the line above disables it. Without it, `yf/`-local changes stop re-running the
    // build script, staling YF_GIT_DIRTY (the REQ-YF-PRE-009 constraint) and silently
    // removing the addition coverage `yf/profiles/` gets from the implicit watch.
    assert!(
        BUILD_RS.contains("cargo:rerun-if-changed=."),
        "DRIFT: build.rs emits a narrowing `rerun-if-changed` without the companion \
         `cargo:rerun-if-changed=.` line. Emitting ANY rerun-if-changed disables cargo's \
         implicit whole-package watch, so this staleness the `.` line exists to prevent: \
         YF_GIT_DIRTY goes stale (REQ-YF-PRE-009) and additions under yf/profiles/ stop \
         propagating. Both lines are load-bearing."
    );
}

/// Pin `embed.rs`'s exclude set, and pin the deliberate fact that the watch does not
/// mirror it.
///
/// Rationale (plan-041 C4 / E6): the natural reading of "the watch should match the
/// embed" is that `build.rs` ought to exclude what `embed.rs` excludes. That was spiked
/// and REFUTED — per-file emission mirroring the excludes cannot observe additions, which
/// is the entire defect being fixed. So the correct invariant is the opposite of parity:
/// the watch is deliberately BROADER than the embed, and the cost is a rebuild on
/// gitignored churn. This test exists so that a future reader who "fixes" the asymmetry
/// has to delete an assertion that tells them why not to.
#[test]
fn embed_excludes_are_pinned_and_the_watch_deliberately_does_not_mirror_them() {
    for exclude in ["*.pyc", "__pycache__/*", "**/__pycache__/*"] {
        assert!(
            EMBED_RS.contains(&format!("#[exclude = \"{exclude}\"]")),
            "embed.rs no longer excludes `{exclude}`. If the exclude set changed \
             deliberately, update this test — and re-read the note below before assuming \
             build.rs should mirror the change."
        );
    }

    // The watch must NOT try to mirror the excludes. `rerun-if-changed` has no exclude
    // mechanism; the only way to approximate one is per-file emission, which is blind to
    // additions (plan-041 E6, measured). If someone adds such a walk, this fails.
    //
    // Checked against CODE only: build.rs's comment block deliberately discusses
    // `__pycache__` (it records why the watch does not filter it), and that prose must
    // survive. Same code-vs-comment boundary the repo's other acceptance checks use.
    let build_rs_code: String = BUILD_RS
        .lines()
        .filter(|line| !line.trim_start().starts_with("//"))
        .collect::<Vec<_>>()
        .join("\n");
    assert!(
        !build_rs_code.contains("__pycache__"),
        "build.rs appears to filter `__pycache__` from its watch. Per-file emission \
         mirroring embed.rs's excludes was measured (plan-041 E6) and REFUTED: a per-file \
         watch list only names files that existed when build.rs last ran, so a NEWLY \
         ADDED file is never watched and #137 returns. The directory watch is broader on \
         purpose; the gitignored-churn rebuild is the documented price (mitigate with \
         PYTHONPYCACHEPREFIX outside the repo, not by narrowing the watch)."
    );
}
