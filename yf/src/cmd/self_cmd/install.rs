//! `yf self install --from-build` (plan-018 Issue 3.5).
//!
//! Dev workflow: promote the workspace's local `cargo build` output
//! (`target/<profile>/yf`) to `~/.local/bin/yf` and write the from-build marker so
//! the upgrade nag (4.1) and `self update` (3.4) treat it as a developer build
//! (no-nag; `self update --force` round-trips back to a vendor release by removing
//! the marker).

use std::path::{Path, PathBuf};
use std::process::ExitCode;

use anyhow::{Context, Result};

use super::{fsutil, receipt};
use crate::cli::SelfInstallArgs;
use crate::dirs::Dirs;

/// Build profile selected for promotion.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Profile {
    Release,
    Debug,
}

impl Profile {
    /// `target/<dir>/` segment.
    fn target_subdir(self) -> &'static str {
        match self {
            Profile::Release => "release",
            Profile::Debug => "debug",
        }
    }

    /// `cargo build` flag (release adds `--release`; debug is the default).
    fn cargo_flag(self) -> Option<&'static str> {
        match self {
            Profile::Release => Some("--release"),
            Profile::Debug => None,
        }
    }
}

/// Pick the profile from flags. `--debug` wins only when set; default is release
/// (clap already rejects `--release --debug` together).
pub fn select_profile(args: &SelfInstallArgs) -> Profile {
    if args.debug {
        Profile::Debug
    } else {
        Profile::Release
    }
}

/// The expected build-output path: `<workspace_root>/target/<profile>/yf`.
pub fn build_output_path(workspace_root: &Path, profile: Profile) -> PathBuf {
    workspace_root
        .join("target")
        .join(profile.target_subdir())
        .join("yf")
}

/// Find the cargo **workspace root** by walking up from `start` for a `Cargo.toml`
/// that declares `[workspace]`. Falls back to the nearest dir with any `Cargo.toml`,
/// then `None`.
pub fn find_workspace_root(start: &Path) -> Option<PathBuf> {
    let mut nearest_manifest: Option<PathBuf> = None;
    let mut cur: Option<&Path> = Some(start);
    while let Some(dir) = cur {
        let manifest = dir.join("Cargo.toml");
        if manifest.is_file() {
            if nearest_manifest.is_none() {
                nearest_manifest = Some(dir.to_path_buf());
            }
            if let Ok(s) = std::fs::read_to_string(&manifest) {
                if s.contains("[workspace]") {
                    return Some(dir.to_path_buf());
                }
            }
        }
        cur = dir.parent();
    }
    nearest_manifest
}

/// Run `yf self install`.
pub fn run(args: &SelfInstallArgs) -> Result<ExitCode> {
    let dirs = Dirs::from_env();
    run_with(args, &dirs)
}

/// Testable core: resolve the build, optionally build, promote, write the marker.
fn run_with(args: &SelfInstallArgs, dirs: &Dirs) -> Result<ExitCode> {
    // `--from-build` is currently the only supported mode (vendor installs come
    // from the curl|sh installer / `self update`, not this command).
    if !args.from_build {
        return fail(
            args.json,
            "`yf self install` requires `--from-build` (the only supported mode); \
             vendor installs use the curl|sh installer or `yf self update`",
        );
    }

    let profile = select_profile(args);
    let cwd = std::env::current_dir().context("resolving current directory")?;
    let workspace_root = find_workspace_root(&cwd).ok_or_else(|| {
        anyhow::anyhow!(
            "no cargo workspace found from {} — run this from inside the yf repo",
            cwd.display()
        )
    })?;

    if args.build {
        cargo_build(&workspace_root, profile)?;
    }

    let src = build_output_path(&workspace_root, profile);
    if !src.is_file() {
        return fail(
            args.json,
            &format!(
                "no build at {} — run `cargo build{}` first, or pass `--build`",
                src.display(),
                if profile == Profile::Release {
                    " --release"
                } else {
                    ""
                }
            ),
        );
    }

    let dst = dirs.bin_dir().join("yf");
    if dst.exists() && !args.force {
        return fail(
            args.json,
            &format!(
                "{} already exists — pass `--force` to overwrite",
                dst.display()
            ),
        );
    }

    fsutil::atomic_install(&src, &dst)
        .with_context(|| format!("installing {} → {}", src.display(), dst.display()))?;

    // Record the promoted binary's own version (query it; fall back to this
    // binary's version). Presence of the marker is what suppresses the nag (3.3);
    // the version is informational for the report.
    let version = promoted_version(&dst).unwrap_or_else(|| crate::VERSION.to_string());
    let marker = receipt::FromBuildMarker::new(version.clone(), profile.target_subdir());
    let marker_path =
        receipt::write_from_build_marker(dirs, &marker).context("writing from-build marker")?;

    // The install-time sync (REQ-YF-SELF-005 / REQ-YF-SELF-008). Runs unless
    // --no-sync. This is the defect plan-042 exists to fix: the from-build path
    // previously deployed NONE of the three sub-operations, so a promoted binary
    // and the deployed surface could disagree indefinitely and silently.
    //
    // `dst` — the CAPTURED install path — is what we exec, never `current_exe()`:
    // the running binary is precisely the one that may carry a stale embed
    // (D-B). Exec'ing the freshly promoted binary is what makes the new embed
    // take effect.
    let sync_report = if args.no_sync {
        None
    } else {
        Some(super::sync::run_sync(&dst, &home_dir()))
    };

    report(
        args.json,
        &dst,
        &version,
        profile,
        &marker_path,
        sync_report.as_ref(),
    );

    // Fail-soft in the sense REQ-YF-SELF-005 defines it: a sync failure is
    // REPORTED and exits non-zero ON THE SYNC ALONE, but NEVER rolls back the
    // (successful) promote — the binary stays in place and the marker stands.
    //
    // FAIL-SOFT IS NOT SILENT (pass-1 C8). An earlier draft of this issue said
    // only "never invalidates a successful promote" and omitted the non-zero
    // exit; implemented literally, that would have recreated the exact
    // silent-divergence defect this plan exists to fix.
    if sync_report.is_some_and(|r| !r.failures.is_empty()) {
        return Ok(ExitCode::FAILURE);
    }
    Ok(ExitCode::SUCCESS)
}

/// `$HOME`, falling back to cwd when unset — keeps resolution total.
fn home_dir() -> PathBuf {
    std::env::var_os("HOME")
        .map(PathBuf::from)
        .filter(|p| !p.as_os_str().is_empty())
        .unwrap_or_else(|| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
}

/// Run `cargo build [--release]` for the `yf` package in the workspace root.
fn cargo_build(workspace_root: &Path, profile: Profile) -> Result<()> {
    let mut cmd = std::process::Command::new("cargo");
    cmd.current_dir(workspace_root)
        .arg("build")
        .args(["-p", "yf"]);
    if let Some(flag) = profile.cargo_flag() {
        cmd.arg(flag);
    }
    let status = cmd
        .status()
        .context("running `cargo build` (is cargo on PATH?)")?;
    if !status.success() {
        anyhow::bail!("`cargo build` failed");
    }
    Ok(())
}

/// Ask the just-promoted binary for its version (`yf version --json`).
fn promoted_version(dst: &Path) -> Option<String> {
    let out = std::process::Command::new(dst)
        .args(["version", "--json"])
        .output()
        .ok()?;
    if !out.status.success() {
        return None;
    }
    let v: serde_json::Value = serde_json::from_slice(&out.stdout).ok()?;
    v.get("version")?.as_str().map(|s| s.to_string())
}

/// Emit a structured failure (json or human) and return a FAILURE exit code.
fn fail(json: bool, msg: &str) -> Result<ExitCode> {
    if json {
        let out = serde_json::json!({"command": "self install", "status": "error", "error": msg});
        println!("{}", serde_json::to_string(&out)?);
    } else {
        eprintln!("error: {msg}");
    }
    Ok(ExitCode::FAILURE)
}

fn report(
    json: bool,
    dst: &Path,
    version: &str,
    profile: Profile,
    marker: &Path,
    sync: Option<&super::sync::RefreshReport>,
) {
    // The sync's own verdict, kept distinct from the promote's. A promote that
    // succeeded while its sync failed reports `status: "ok"` (the binary IS
    // installed) with `sync.status: "failed"` — the caller learns both facts.
    let sync_json = match sync {
        None => serde_json::json!({ "status": "skipped", "reason": "--no-sync" }),
        Some(r) if r.failures.is_empty() => serde_json::json!({
            "status": "ok",
            "refreshed": r.refreshed,
        }),
        Some(r) => serde_json::json!({
            "status": "failed",
            "refreshed": r.refreshed,
            "failures": r.failures,
            "rerun": "yf harness skills install --scope user --tune",
        }),
    };

    if json {
        let out = serde_json::json!({
            "command": "self install",
            "status": "ok",
            "installed": dst.display().to_string(),
            "version": version,
            "profile": profile.target_subdir(),
            "from_build_marker": marker.display().to_string(),
            "sync": sync_json,
        });
        if let Ok(s) = serde_json::to_string(&out) {
            println!("{s}");
        }
        return;
    }

    println!(
        "installed {} ({} build, v{}) — from-build marker at {} (nag suppressed; \
         `yf self update --force` switches to a vendor release)",
        dst.display(),
        profile.target_subdir(),
        version,
        marker.display()
    );
    match sync {
        None => println!("sync: skipped (--no-sync) — skills, rules and config unchanged"),
        Some(r) if r.failures.is_empty() && r.refreshed.is_empty() => {
            println!("sync: no harnesses selected (nothing deployed here yet)")
        }
        Some(r) if r.failures.is_empty() => {
            println!("sync: deployed to {}", r.refreshed.join(", "))
        }
        Some(r) => {
            // Reported, not swallowed — and the caller exits non-zero.
            eprintln!(
                "error: the binary was promoted, but the sync FAILED — the deployed \
                 skills/rules may not match it."
            );
            for f in &r.failures {
                eprintln!("  {f}");
            }
            if !r.refreshed.is_empty() {
                eprintln!("  (succeeded for: {})", r.refreshed.join(", "));
            }
            eprintln!("  re-run manually: yf harness skills install --scope user --tune");
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // REQ-YF-SELF-004: yf self install --from-build promotes local build + from-build marker.
    #[test]
    fn profile_paths() {
        let root = Path::new("/ws");
        assert_eq!(
            build_output_path(root, Profile::Release),
            Path::new("/ws/target/release/yf")
        );
        assert_eq!(
            build_output_path(root, Profile::Debug),
            Path::new("/ws/target/debug/yf")
        );
    }

    #[test]
    fn workspace_root_detection_prefers_workspace_manifest() {
        let tmp = tempfile::tempdir().unwrap();
        let root = tmp.path();
        std::fs::write(root.join("Cargo.toml"), "[workspace]\nmembers=[\"yf\"]\n").unwrap();
        let member = root.join("yf");
        std::fs::create_dir_all(&member).unwrap();
        std::fs::write(member.join("Cargo.toml"), "[package]\nname=\"yf\"\n").unwrap();
        let nested = member.join("src");
        std::fs::create_dir_all(&nested).unwrap();
        let found = find_workspace_root(&nested).unwrap();
        assert_eq!(
            std::fs::canonicalize(found).unwrap(),
            std::fs::canonicalize(root).unwrap()
        );
    }

    #[test]
    fn workspace_root_none_when_no_manifest() {
        let tmp = tempfile::tempdir().unwrap();
        assert!(find_workspace_root(tmp.path()).is_none());
    }

    #[test]
    fn from_build_required() {
        // Without --from-build the command refuses (FAILURE), no IO performed.
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().to_path_buf();
        let dirs =
            crate::dirs::resolve(move |k| (k == "HOME").then(|| home.clone().into_os_string()));
        let args = SelfInstallArgs {
            from_build: false,
            release: false,
            debug: false,
            build: false,
            force: false,
            no_sync: true,
            json: true,
        };
        let code = run_with(&args, &dirs).unwrap();
        assert_eq!(format!("{code:?}"), format!("{:?}", ExitCode::FAILURE));
    }
}
