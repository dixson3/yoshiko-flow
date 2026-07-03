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

    // Deliberately emit NO `rerun-if-changed` narrowing (REQ-YF-PRE-009, red-team
    // C7): the previous `.git/HEAD` / `.git/refs` pins did not move on a tracked
    // source edit, so `build.rs` would not re-run and the dirty flag would go
    // stale. With no rerun-if instructions, cargo re-runs this script whenever any
    // file in the `yf/` package changes — the best dev-loop accuracy achievable.
    // Known limit (documented, not over-promised): it still cannot observe
    // repo-wide changes outside the `yf/` package on an incremental rebuild. The
    // clean CI/release build (a fresh full build) is unaffected and authoritative.
}
