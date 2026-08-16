use std::process::Command;

/// Capture git build metadata at build time and expose it as compile-time env
/// vars: the short commit hash (`YF_GIT_HASH`), a working-tree dirty flag
/// (`YF_GIT_DIRTY`, `"1"`/`"0"`), and a display suffix (`YF_GIT_DIRTY_SUFFIX`,
/// `"-dirty"`/`""`) appended to the human-readable version line. Degrades
/// gracefully to "unknown" / not-dirty when git is unavailable or the build
/// happens outside a git checkout — never fails the build (GR-011: small,
/// self-contained binary; REQ-YF-CLI-004: build metadata "when available";
/// REQ-YF-PRE-009: dirty capture is best-effort).
fn main() {
    let hash = Command::new("git")
        .args(["rev-parse", "--short", "HEAD"])
        .output()
        .ok()
        .filter(|out| out.status.success())
        .and_then(|out| String::from_utf8(out.stdout).ok())
        .map(|s| s.trim().to_string())
        .filter(|s| !s.is_empty())
        .unwrap_or_else(|| "unknown".to_string());

    // Dirty capture (REQ-YF-PRE-008/009): the NORMATIVE probe is `git status
    // --porcelain` — whole-repo, INCLUDES untracked files (chosen over `git
    // describe --dirty`, which is tracked-only and needs a tag). Best-effort:
    // absent git / non-checkout / a failed command all degrade to **not-dirty**
    // (the same graceful-degradation stance as the hash above), so the only
    // shipped artifact — a clean CI/release build — is reliably not-dirty and
    // stays nag-eligible. `YF_GIT_DIRTY` is authoritative for that clean build
    // but stale-prone on the incremental local dev loop (see the rerun note
    // below); it feeds `is_dirty_build()` in main.rs.
    let dirty = Command::new("git")
        .args(["status", "--porcelain"])
        .output()
        .ok()
        .filter(|out| out.status.success())
        .map(|out| !out.stdout.iter().all(u8::is_ascii_whitespace))
        .unwrap_or(false);

    println!("cargo:rustc-env=YF_GIT_HASH={hash}");
    println!(
        "cargo:rustc-env=YF_GIT_DIRTY={}",
        if dirty { "1" } else { "0" }
    );
    // `-dirty` is appended to VERSION_LINE only (visibility); VERSION — the
    // compare/stamp key (REQ-YF-PRE-008) — stays pure CARGO_PKG_VERSION.
    println!(
        "cargo:rustc-env=YF_GIT_DIRTY_SUFFIX={}",
        if dirty { "-dirty" } else { "" }
    );

    // Watch declarations (REQ-YF-EMBED-004; REQ-YF-PRE-009 constraint; #137).
    //
    // WHY THIS IS NEEDED (measured, plan-041 E2/E5): `skills/` lives OUTSIDE the
    // `yf/` package, and `rust-embed` is a PROC MACRO — it cannot emit build
    // directives, and `grep -rn "rerun" rust-embed-impl-*/src/` returns nothing.
    // Its only staleness signal is the `include_bytes!` dep-info the macro expands
    // to, which tracks each embedded file's CONTENT but never THE DIRECTORY
    // LISTING. So cargo had no reason to re-expand the macro when a *new* path
    // appeared: a file ADDED under `skills/` was invisible to an incremental
    // release rebuild (0.17 s no-op, the new file absent from the binary), while
    // content edits, deletes and renames all propagated correctly. The defect is
    // ADDITION-SCOPED, not universal. A second, distinct defect shared the root
    // cause: this script never re-ran on a skills-only change, so YF_GIT_HASH /
    // YF_GIT_DIRTY went stale even when the embed was fresh.
    //
    // BOTH LINES ARE LOAD-BEARING. Emitting ANY `rerun-if-changed` disables cargo's
    // implicit whole-package watch, so `../skills` ALONE would stop this script
    // re-running on changes under `yf/` itself — measured: `touch yf/src/main.rs`
    // left it un-re-run, staling YF_GIT_DIRTY, which REQ-YF-PRE-009's first
    // short-circuit consumes. The `.` line re-declares the package directory and
    // restores that coverage. It also PRESERVES (not adds) addition coverage for
    // `yf/profiles/`, the second `rust-embed` root: that folder is INSIDE the
    // package, so the implicit watch already covered it (measured — additions there
    // never had the blind spot), and `../skills` alone would have silently REMOVED
    // that coverage. This is a regression guard, not a bonus.
    //
    // FORM: a DIRECTORY watch, not per-file emission. Per-file lines mirroring
    // `embed.rs`'s `#[exclude]` set were spiked (plan-041 E6) and REFUTED: a
    // per-file watch list can only name files that existed when this script last
    // ran, so a NEWLY ADDED file is never watched and the addition case fails
    // exactly as before (0.13 s no-op, marker absent). A listing snapshot cannot
    // observe a change to the listing — the same reason the `include_bytes!`
    // dep-info fails above.
    //
    // KNOWN COSTS, documented rather than over-promised:
    //  - `rerun-if-changed` has no exclude mechanism and cargo walks a watched
    //    directory RECURSIVELY, so gitignored churn under `skills/` (the ~40
    //    `__pycache__`/`*.pyc` entries this repo's `uv`/pytest rules generate)
    //    forces a full recompile: measured 5.23 s where a 0.20 s no-op is expected.
    //    Fully eliminable from the other side by keeping bytecode out of the tree
    //    (`PYTHONPYCACHEPREFIX` outside the repo measured the tax back to zero).
    //  - Repo-wide `HEAD` movement is still NOT observed: a docs-only commit, a
    //    `SPEC.md` commit, a `git checkout` or a rebase touches nothing watched, so
    //    the stamp can still go stale on an incremental build. `yf --version` vs
    //    `HEAD` remains the only detector for that residue. Watching `.git/` was
    //    tried before and rejected (the pins did not move on a tracked source
    //    edit). The clean CI/release build is unaffected and authoritative.
    //  - `../skills` does not exist under `cargo package`/`publish`, where cargo
    //    treats a missing path as permanently dirty. Harmless today:
    //    `#[folder = "../skills"]` already precludes publishing this crate.
    println!("cargo:rerun-if-changed=../skills");
    println!("cargo:rerun-if-changed=.");
}
