//! REQ-YF-EMBED-004 — a build shall observe **additions** under the embed root.
//!
//! ## What this guards (#137)
//!
//! `skills/` lives OUTSIDE the `yf/` package and `rust-embed` is a proc macro, so it
//! emits no `cargo:rerun-if-changed`; its only staleness signal is the `include_bytes!`
//! dep-info it expands to, which tracks each embedded file's CONTENT but never THE
//! DIRECTORY LISTING. A file *added* under `skills/` was therefore invisible to an
//! incremental release rebuild. `yf/build.rs` closes this by declaring a directory watch.
//!
//! ## Why the test builds a scratch crate rather than `yf` itself
//!
//! Reproducing the defect requires ADDING a file under the embed root and rebuilding.
//! Doing that to the real `skills/` tree would mutate the repo mid-test and race any
//! concurrent build. The scratch crate reproduces the *structure* that causes the defect —
//! an embed folder OUTSIDE the package — in an isolated temp dir with its own target dir.
//!
//! ## Why BOTH arms are asserted on every run (pass-2 C13)
//!
//! A test that only ever observes green cannot distinguish "green because the fix works"
//! from "green because it never exercised the addition path". So this test builds the
//! scratch crate TWICE: once WITHOUT the watch lines (asserting the addition is ABSENT —
//! the defect reproduced) and once WITH them (asserting it is PRESENT). The RED arm is a
//! permanent assertion, not a one-time manual demonstration.
//!
//! ## Why `--release` is mandatory
//!
//! `rust-embed` is declared without `debug-embed`, so a DEBUG binary resolves embedded
//! paths from disk at runtime and can never miss an addition. A debug version of this test
//! passes even against the pre-fix `build.rs` — measured during the plan-041 Issue 1.2a
//! spike. Release is the profile the defect lives in, and the one that ships.
//!
//! ## Scope note
//!
//! This proves the MECHANISM. That `yf/build.rs` actually emits the watch for the real
//! `../skills` root is asserted separately by the drift guard in `embed_watch_drift.rs`.
//! Either test alone leaves a hole; together they close it.

use std::path::{Path, PathBuf};
use std::process::Command;

/// Env vars the OUTER `cargo test` sets that would otherwise leak into the nested build.
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

/// A unique-enough scratch root under the system temp dir.
fn scratch_root() -> PathBuf {
    let unique = format!(
        "yf-embed-addition-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0)
    );
    std::env::temp_dir().join(unique)
}

/// Write the scratch crate. `watch` selects the pre-fix (false) or fixed (true) `build.rs`.
///
/// Layout mirrors `skills/` vs `yf/`: the embed root is a SIBLING of the crate dir, so it
/// sits outside the package exactly as `../skills` does.
fn write_scratch(root: &Path, watch: bool) -> std::io::Result<()> {
    let crate_dir = root.join("cratedir");
    std::fs::create_dir_all(crate_dir.join("src"))?;
    std::fs::create_dir_all(root.join("assets"))?;
    std::fs::write(root.join("assets").join("original.txt"), b"original\n")?;

    // `[workspace]` detaches the scratch crate from any parent workspace it may land in.
    std::fs::write(
        crate_dir.join("Cargo.toml"),
        b"[package]\nname = \"embedprobe\"\nversion = \"0.0.0\"\nedition = \"2021\"\n\n\
          [workspace]\n\n[dependencies]\nrust-embed = \"8\"\n",
    )?;

    // The pre-fix arm still emits a `rustc-env` line, mirroring the real pre-fix
    // `build.rs`, which emitted build metadata but no `rerun-if-changed`.
    let build_rs = if watch {
        "fn main() {\n    \
             println!(\"cargo:rustc-env=PROBE_STAMP=x\");\n    \
             println!(\"cargo:rerun-if-changed=../assets\");\n    \
             println!(\"cargo:rerun-if-changed=.\");\n\
         }\n"
    } else {
        "fn main() {\n    println!(\"cargo:rustc-env=PROBE_STAMP=x\");\n}\n"
    };
    std::fs::write(crate_dir.join("build.rs"), build_rs)?;

    std::fs::write(
        crate_dir.join("src").join("main.rs"),
        b"use rust_embed::RustEmbed;\n\
          #[derive(RustEmbed)]\n\
          #[folder = \"../assets\"]\n\
          struct Assets;\n\
          fn main() { for p in Assets::iter() { println!(\"{p}\"); } }\n",
    )?;
    Ok(())
}

/// Run a nested `cargo build --release --offline` in the scratch crate.
fn nested_build(root: &Path) -> std::io::Result<std::process::Output> {
    let mut cmd = Command::new("cargo");
    cmd.args(["build", "--release", "--offline", "-q"])
        .current_dir(root.join("cratedir"));
    // Scrub FIRST, then set: `CARGO_TARGET_DIR` is itself in the scrub list (the outer
    // `cargo test` may export it), so setting it before the removals would delete it
    // again and send the nested build to a target dir this test does not look in.
    for key in OUTER_CARGO_ENV {
        cmd.env_remove(key);
    }
    cmd.env("CARGO_TARGET_DIR", root.join("target"));
    cmd.output()
}

/// Build, add a new asset, rebuild, and report whether the new asset reached the binary.
fn addition_propagates(root: &Path, watch: bool) -> Option<bool> {
    write_scratch(root, watch).ok()?;

    // Phase 1: cold build, then settle so the rebuild below starts from a no-op state.
    let first = nested_build(root).ok()?;
    if !first.status.success() {
        // Offline resolution failed, or cargo cannot build here — inconclusive, not a
        // failure. The caller skips.
        eprintln!(
            "embed_addition: nested build failed, skipping:\n{}",
            String::from_utf8_lossy(&first.stderr)
        );
        return None;
    }
    let _ = nested_build(root);

    // Phase 2: ADD a new file — the case REQ-YF-EMBED-004 is about.
    std::fs::write(root.join("assets").join("added.txt"), b"ADDEDMARKER\n").ok()?;
    let second = nested_build(root).ok()?;
    if !second.status.success() {
        return None;
    }

    // Phase 3: ask the built binary what it embedded.
    //
    // A missing binary here is NOT an environment limitation to skip over — the build
    // just reported success, so the probe is broken. Fail loudly: silently skipping is
    // how this guard would rot into a permanent no-op.
    let bin = root.join("target").join("release").join("embedprobe");
    assert!(
        bin.is_file(),
        "nested build reported success but produced no binary at {bin:?} — the probe is \
         broken (a stray CARGO_TARGET_DIR redirecting the output?). Fix the probe; do not \
         convert this into a skip."
    );
    let listing = Command::new(&bin)
        .output()
        .expect("failed to run the freshly built scratch binary");
    let listing = String::from_utf8_lossy(&listing.stdout).to_string();
    assert!(
        listing.contains("original.txt"),
        "scratch crate embedded nothing at all — the probe itself is broken, listing was: {listing:?}"
    );
    Some(listing.contains("added.txt"))
}

/// REQ-YF-EMBED-004: an addition under the embed root reaches the embedded payload.
///
/// Asserts BOTH arms so the guard can never be vacuously green (pass-2 C13).
#[test]
fn req_yf_embed_004_build_observes_additions_under_embed_root() {
    if Command::new("cargo").arg("--version").output().is_err() {
        eprintln!("embed_addition: cargo not on PATH, skipping");
        return;
    }

    let root = scratch_root();
    let _ = std::fs::create_dir_all(&root);

    // RED arm: without the watch lines the addition must NOT propagate. This is the
    // defect (#137) reproduced. If this ever starts passing, the test below has stopped
    // proving anything and must be re-examined before it is trusted.
    let red_root = root.join("red");
    let red = addition_propagates(&red_root, false);

    // GREEN arm: with the watch lines it must propagate.
    let green_root = root.join("green");
    let green = addition_propagates(&green_root, true);

    let _ = std::fs::remove_dir_all(&root);

    let (red, green) = match (red, green) {
        (Some(r), Some(g)) => (r, g),
        _ => {
            eprintln!("embed_addition: nested cargo build unavailable (offline cache?), skipping");
            return;
        }
    };

    assert!(
        !red,
        "RED arm did not reproduce #137: an addition propagated WITHOUT any \
         `rerun-if-changed`. Either cargo's behavior changed or the probe stopped \
         exercising the addition path — this test is not a valid guard until that is \
         understood. Do NOT simply delete this assertion."
    );
    assert!(
        green,
        "REQ-YF-EMBED-004 VIOLATED: a file added under the embed root did NOT reach the \
         embedded payload even with `cargo:rerun-if-changed` declared on the embed \
         directory. This is the #137 defect class."
    );
}
