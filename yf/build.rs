use std::process::Command;

/// Capture the short git commit hash at build time and expose it as the
/// `YF_GIT_HASH` compile-time env var. Degrades gracefully to "unknown" when
/// git is unavailable or the build happens outside a git checkout — never fails
/// the build (GR-011: small, self-contained binary; REQ-YF-CLI-004: build
/// metadata "when available").
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

    println!("cargo:rustc-env=YF_GIT_HASH={hash}");
    // Re-run if HEAD moves so the embedded hash stays current.
    println!("cargo:rerun-if-changed=.git/HEAD");
    println!("cargo:rerun-if-changed=.git/refs");
}
