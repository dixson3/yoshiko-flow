//! Defect 1b (#137): the build-metadata stamp must not go stale on a skills-only change.
//!
//! `yf/build.rs` stamps `YF_GIT_HASH` / `YF_GIT_DIRTY` at build time. Before the fix it
//! emitted no `cargo:rerun-if-changed`, so cargo re-ran it only when a file under `yf/`
//! changed — meaning a **skills-only** commit left the stamp reporting a stale hash while
//! every command still exited 0. `YF_GIT_DIRTY` is consumed by `REQ-YF-PRE-009`'s first
//! short-circuit, so a stale value there silently changes preflight behavior.
//!
//! ## Scope of the claim (deliberately narrow)
//!
//! The fix makes the stamp fresh for changes under **`yf/` and `skills/`** — the two
//! directories `build.rs` now watches. It does **not** make it fresh for repo-wide `HEAD`
//! movement: a docs-only commit, a `SPEC.md` commit, a `git checkout` or a rebase touches
//! nothing watched, so an incremental build can still carry a stale hash. That residue is
//! recorded under `REQ-YF-PRE-009` in `SPEC.md` and is why `AGENTS.md` keeps a one-line
//! `yf --version` sanity note. These tests assert only what is actually claimed.
//!
//! ## Why a scratch crate
//!
//! Asserting this against the real `yf` crate would mean mutating `skills/` and forcing
//! repeated release rebuilds of the workspace mid-test. The scratch crate reproduces the
//! *structure*: a build script that stamps a value, an embed-style folder OUTSIDE the
//! package, and a subdirectory INSIDE the package standing in for `yf/profiles/`.
//! That `yf/build.rs` really carries these watch lines is asserted by
//! `embed_watch_drift.rs`.

use std::path::{Path, PathBuf};
use std::process::Command;

const OUTER_CARGO_ENV: &[&str] = &[
    "RUSTC",
    "RUSTC_WRAPPER",
    "RUSTC_WORKSPACE_WRAPPER",
    "CARGO",
    "RUSTFLAGS",
    "CARGO_ENCODED_RUSTFLAGS",
    "CARGO_BUILD_TARGET_DIR",
    "CARGO_TARGET_DIR",
];

fn scratch_root() -> PathBuf {
    let unique = format!(
        "yf-build-stamp-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0)
    );
    std::env::temp_dir().join(unique)
}

/// Scratch crate: `build.rs` bumps a counter file each time it runs and bakes the value in.
/// A changed stamp between two builds therefore means "the build script re-ran".
fn write_scratch(root: &Path) -> std::io::Result<()> {
    let crate_dir = root.join("cratedir");
    std::fs::create_dir_all(crate_dir.join("src"))?;
    // Stands in for `yf/profiles/` — a second folder INSIDE the package (E5).
    std::fs::create_dir_all(crate_dir.join("profiles"))?;
    std::fs::write(crate_dir.join("profiles").join("a.json"), b"{}\n")?;
    // Stands in for `skills/` — OUTSIDE the package.
    std::fs::create_dir_all(root.join("assets"))?;
    std::fs::write(root.join("assets").join("original.txt"), b"original\n")?;

    std::fs::write(
        crate_dir.join("Cargo.toml"),
        b"[package]\nname = \"stampprobe\"\nversion = \"0.0.0\"\nedition = \"2021\"\n\n[workspace]\n",
    )?;
    std::fs::write(
        crate_dir.join("build.rs"),
        br#"use std::io::Write;
fn main() {
    let counter = std::path::Path::new("../counter.txt");
    let n: u64 = std::fs::read_to_string(counter)
        .ok()
        .and_then(|s| s.trim().parse().ok())
        .unwrap_or(0)
        + 1;
    let mut f = std::fs::File::create(counter).expect("counter");
    write!(f, "{n}").expect("counter write");
    println!("cargo:rustc-env=PROBE_STAMP={n}");
    println!("cargo:rerun-if-changed=../assets");
    println!("cargo:rerun-if-changed=.");
}
"#,
    )?;
    std::fs::write(
        crate_dir.join("src").join("main.rs"),
        b"fn main() { println!(\"{}\", env!(\"PROBE_STAMP\")); }\n",
    )?;
    Ok(())
}

fn build(root: &Path) -> bool {
    let mut cmd = Command::new("cargo");
    cmd.args(["build", "--release", "--offline", "-q"])
        .current_dir(root.join("cratedir"));
    for key in OUTER_CARGO_ENV {
        cmd.env_remove(key);
    }
    cmd.env("CARGO_TARGET_DIR", root.join("target"));
    matches!(cmd.output(), Ok(out) if out.status.success())
}

/// The stamp currently baked into the built binary.
fn stamp(root: &Path) -> String {
    let bin = root.join("target").join("release").join("stampprobe");
    assert!(
        bin.is_file(),
        "nested build reported success but produced no binary at {bin:?} — the probe is \
         broken. Fix it; do not convert this into a skip."
    );
    let out = Command::new(&bin).output().expect("run stamp probe");
    String::from_utf8_lossy(&out.stdout).trim().to_string()
}

/// Defect 1b: a change OUTSIDE the package (the `skills/` case) must re-run the build
/// script, and changes INSIDE the package (the `yf/` and `yf/profiles/` cases) must keep
/// doing so.
#[test]
fn build_stamp_refreshes_for_the_watched_scopes() {
    if Command::new("cargo").arg("--version").output().is_err() {
        eprintln!("build_stamp_freshness: cargo not on PATH, skipping");
        return;
    }
    let root = scratch_root();
    if write_scratch(&root).is_err() || !build(&root) {
        eprintln!("build_stamp_freshness: nested build unavailable (offline cache?), skipping");
        let _ = std::fs::remove_dir_all(&root);
        return;
    }
    // Settle to a no-op so each probe below measures only its own change.
    build(&root);
    let mut last = stamp(&root);

    // A no-op build must NOT re-run the script — otherwise every assertion below would
    // pass trivially and this test would prove nothing.
    assert!(build(&root));
    assert_eq!(
        stamp(&root),
        last,
        "a no-op rebuild re-ran the build script; every assertion in this test would then \
         be vacuous. The watch declarations are too broad, or the tree is churning."
    );

    // (1) skills-side change — the defect-1b case. OUTSIDE the package.
    std::fs::write(root.join("assets").join("original.txt"), b"edited\n").unwrap();
    assert!(build(&root));
    let now = stamp(&root);
    assert_ne!(
        now, last,
        "DEFECT 1b: a change under the OUT-OF-PACKAGE embed root did not re-run the build \
         script, so the build stamp (YF_GIT_HASH / YF_GIT_DIRTY) would go stale on a \
         skills-only change. This is the #137 version-stamp defect."
    );
    last = now;

    // (2) package-local source change — the R2 dirty-flag preservation case. Emitting
    // `../assets` disables cargo's implicit whole-package watch; the `.` line restores it.
    std::fs::write(
        root.join("cratedir").join("src").join("main.rs"),
        b"fn main() { println!(\"{}\", env!(\"PROBE_STAMP\")); /* edit */ }\n",
    )
    .unwrap();
    assert!(build(&root));
    let now = stamp(&root);
    assert_ne!(
        now, last,
        "REGRESSION (R2 / REQ-YF-PRE-009): a package-local source edit did not re-run the \
         build script. Emitting a narrowing `rerun-if-changed` disabled cargo's implicit \
         whole-package watch and the companion `cargo:rerun-if-changed=.` line is missing \
         or ineffective. YF_GIT_DIRTY would go stale, and PRE-009's first short-circuit \
         consumes it."
    );
    last = now;

    // (3) ADDITION under a package-local subfolder — the `yf/profiles/` case (E5).
    // Measured in plan-041: `yf/profiles/` never had the addition blind spot, because the
    // implicit whole-package watch covered it. Emitting `../skills` ALONE would have
    // silently REMOVED that coverage. This asserts the `.` line preserves it.
    std::fs::write(
        root.join("cratedir").join("profiles").join("added.json"),
        b"{\"added\":true}\n",
    )
    .unwrap();
    assert!(build(&root));
    assert_ne!(
        stamp(&root),
        last,
        "REGRESSION (E5): an ADDITION under a package-local subfolder (the `yf/profiles/` \
         case, the second rust-embed root) did not re-run the build script. That coverage \
         came free from cargo's implicit whole-package watch before the #137 fix; the \
         `cargo:rerun-if-changed=.` line exists to PRESERVE it. Losing it would be a \
         silent regression that no other test covers."
    );

    let _ = std::fs::remove_dir_all(&root);
}
