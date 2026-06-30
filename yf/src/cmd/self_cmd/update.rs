//! `yf self update` (plan-018 Issue 3.4).
//!
//! Vendor-only in-place self-update:
//! 1. Fetch the latest release's `dist-manifest.json` (GitHub
//!    `releases/latest/download/...`) and read its `announcement_tag` + artifacts.
//! 2. Compare the latest version to the running one; stop early if already current
//!    (unless `--force`).
//! 3. Select the host triple's `executable-zip` (`yf-<triple>.tar.gz`) and its
//!    `checksum` artifact from the manifest (format-driven, not a hardcoded ext).
//! 4. Download the archive + its `.sha256`, **verify sha256** against the manifest
//!    checksum, **extract** (pure-Rust, 3.4a), and **atomically `self-replace`** the
//!    running binary.
//! 5. Warn if another `yf` earlier on `PATH` shadows the updated one (Concern F).
//!
//! Refuses on a Homebrew copy (→ `brew upgrade`) and on a from-build/unknown copy
//! unless `--force` (install-source classification, 3.3). The post-update
//! skills/rules refresh is layered on in Issue 3.7.
//!
//! **Testability:** all network IO is behind the [`Fetcher`] trait and the binary
//! swap behind a closure, so [`run_inner`] drives the full
//! manifest→select→download→verify→extract→swap pipeline against a local fixture
//! (no network, no clobbering the real binary) — the acceptance path the plan
//! requires exercised against a `.tar.gz` fixture.

use std::path::Path;
use std::process::ExitCode;

use anyhow::{Context, Result};
use serde::Deserialize;

use super::{archive, source};
use crate::cli::SelfUpdateArgs;
use crate::dirs::Dirs;

/// The host's Rust target triple — matches cargo-dist's asset naming.
#[cfg(all(target_arch = "aarch64", target_os = "macos"))]
pub const HOST_TRIPLE: &str = "aarch64-apple-darwin";
#[cfg(all(target_arch = "x86_64", target_os = "macos"))]
pub const HOST_TRIPLE: &str = "x86_64-apple-darwin";
#[cfg(all(target_arch = "aarch64", target_os = "linux"))]
pub const HOST_TRIPLE: &str = "aarch64-unknown-linux-gnu";
#[cfg(all(target_arch = "x86_64", target_os = "linux"))]
pub const HOST_TRIPLE: &str = "x86_64-unknown-linux-gnu";
#[cfg(not(any(
    all(target_arch = "aarch64", target_os = "macos"),
    all(target_arch = "x86_64", target_os = "macos"),
    all(target_arch = "aarch64", target_os = "linux"),
    all(target_arch = "x86_64", target_os = "linux"),
)))]
pub const HOST_TRIPLE: &str = "";

/// Crate repository URL (e.g. `https://github.com/dixson3/yoshiko-flow`).
const REPO_URL: &str = env!("CARGO_PKG_REPOSITORY");

/// Fetches bytes for a URL. Real impl is [`HttpFetcher`] (ureq); tests inject a
/// local-directory fetcher so the whole pipeline runs offline.
pub trait Fetcher {
    fn get(&self, url: &str) -> Result<Vec<u8>>;
}

/// ureq-backed fetcher with a short timeout (fail-fast offline behavior).
pub struct HttpFetcher {
    agent: ureq::Agent,
}

impl Default for HttpFetcher {
    fn default() -> Self {
        let agent = ureq::AgentBuilder::new()
            .timeout(std::time::Duration::from_secs(30))
            .build();
        Self { agent }
    }
}

impl Fetcher for HttpFetcher {
    fn get(&self, url: &str) -> Result<Vec<u8>> {
        let resp = self
            .agent
            .get(url)
            .call()
            .with_context(|| format!("GET {url}"))?;
        let mut buf = Vec::new();
        std::io::copy(&mut resp.into_reader(), &mut buf).with_context(|| format!("reading {url}"))?;
        Ok(buf)
    }
}

// ---- Manifest model (only the fields yf reads) ------------------------------

#[derive(Debug, Deserialize)]
pub struct DistManifest {
    /// e.g. `v0.4.0` — the release tag the manifest describes.
    #[serde(default)]
    pub announcement_tag: String,
    #[serde(default)]
    pub artifacts: std::collections::BTreeMap<String, Artifact>,
}

#[derive(Debug, Deserialize)]
pub struct Artifact {
    #[serde(default)]
    pub name: String,
    #[serde(default)]
    pub kind: String,
    #[serde(default)]
    pub target_triples: Vec<String>,
    /// Name of the checksum artifact for this one (e.g. `<name>.sha256`).
    #[serde(default)]
    pub checksum: Option<String>,
}

/// The artifacts to download for a given host: the archive + its checksum file.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Selected {
    pub archive_name: String,
    pub checksum_name: String,
}

/// Select the host triple's `executable-zip` and its checksum artifact.
pub fn select_artifact(manifest: &DistManifest, triple: &str) -> Option<Selected> {
    if triple.is_empty() {
        return None;
    }
    let art = manifest.artifacts.values().find(|a| {
        a.kind == "executable-zip" && a.target_triples.iter().any(|t| t == triple)
    })?;
    let checksum_name = art.checksum.clone()?;
    Some(Selected {
        archive_name: art.name.clone(),
        checksum_name,
    })
}

/// Parse a `.sha256` sidecar: `"<hex>  <filename>\n"` or a bare `"<hex>"`. Returns
/// the lowercased hex digest.
pub fn parse_sha256_file(contents: &str) -> Option<String> {
    let first = contents.split_whitespace().next()?;
    let hex = first.trim().to_lowercase();
    if hex.len() == 64 && hex.bytes().all(|b| b.is_ascii_hexdigit()) {
        Some(hex)
    } else {
        None
    }
}

/// Lowercase hex sha256 of `bytes`.
pub fn sha256_hex(bytes: &[u8]) -> String {
    use sha2::{Digest, Sha256};
    let mut h = Sha256::new();
    h.update(bytes);
    h.finalize().iter().map(|b| format!("{b:02x}")).collect()
}

/// Version comparison verdict.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VersionCmp {
    /// Latest > current — an update is available.
    UpdateAvailable,
    /// Latest == current — already up to date.
    UpToDate,
    /// Latest < current (or unparseable) — running ahead / unknown.
    CurrentIsNewerOrUnknown,
}

/// Compare a `latest` tag (may be `vX.Y.Z`) against `current` semver. Falls back to
/// string inequality when either is not parseable as `MAJOR.MINOR.PATCH`.
pub fn compare_versions(current: &str, latest_tag: &str) -> VersionCmp {
    let latest = latest_tag.trim_start_matches('v');
    match (parse_semver(current), parse_semver(latest)) {
        (Some(c), Some(l)) => {
            if l > c {
                VersionCmp::UpdateAvailable
            } else if l == c {
                VersionCmp::UpToDate
            } else {
                VersionCmp::CurrentIsNewerOrUnknown
            }
        }
        _ => {
            if latest != current {
                VersionCmp::UpdateAvailable
            } else {
                VersionCmp::UpToDate
            }
        }
    }
}

/// Parse `MAJOR.MINOR.PATCH` (ignoring any `-pre`/`+build` suffix) into a tuple.
fn parse_semver(v: &str) -> Option<(u64, u64, u64)> {
    let core = v.split(['-', '+']).next()?;
    let mut it = core.split('.');
    let maj = it.next()?.parse().ok()?;
    let min = it.next()?.parse().ok()?;
    let pat = it.next().unwrap_or("0").parse().ok()?;
    Some((maj, min, pat))
}

/// The running binary's version, overridable by `YF_VERSION` (so a dev/test can
/// force the update path against a fixture without rebuilding at a lower version).
fn current_version() -> String {
    std::env::var("YF_VERSION").unwrap_or_else(|_| crate::VERSION.to_string())
}

// ---- URL construction -------------------------------------------------------

fn manifest_latest_url() -> String {
    format!(
        "{}/releases/latest/download/dist-manifest.json",
        REPO_URL.trim_end_matches('/')
    )
}

fn asset_url(tag: &str, asset: &str) -> String {
    format!(
        "{}/releases/download/{tag}/{asset}",
        REPO_URL.trim_end_matches('/')
    )
}

// ---- Orchestration ----------------------------------------------------------

/// Run `yf self update`.
pub fn run(args: &SelfUpdateArgs) -> Result<ExitCode> {
    let dirs = Dirs::from_env();
    let fetcher = HttpFetcher::default();
    // Real swap: atomically replace the running binary in place.
    let swap = |new_bin: &Path| -> Result<()> {
        self_replace::self_replace(new_bin).context("atomically replacing the running binary")
    };
    run_inner(args, &dirs, &fetcher, &swap)
}

/// Testable core. `swap(new_binary_path)` performs the in-place replacement (real
/// = `self_replace`; tests = copy into a temp "installed" path).
pub fn run_inner(
    args: &SelfUpdateArgs,
    dirs: &Dirs,
    fetcher: &dyn Fetcher,
    swap: &dyn Fn(&Path) -> Result<()>,
) -> Result<ExitCode> {
    // 1. Install-source gate.
    let src = source::detect(dirs);
    if src == source::Source::Homebrew {
        return refuse(args.json, src); // never overridable
    }
    if !src.auto_updatable() && !args.force {
        return refuse(args.json, src);
    }

    // 2. Fetch + parse the latest manifest.
    let manifest_bytes = fetcher
        .get(&manifest_latest_url())
        .context("fetching latest release manifest (are you online?)")?;
    let manifest: DistManifest =
        serde_json::from_slice(&manifest_bytes).context("parsing dist-manifest.json")?;
    let tag = manifest.announcement_tag.clone();
    let current = current_version();
    let cmp = compare_versions(&current, &tag);

    // 3. Already current?
    if cmp == VersionCmp::UpToDate && !args.force {
        return report_uptodate(args.json, &current);
    }

    // 4. Select the host artifact.
    let selected = select_artifact(&manifest, HOST_TRIPLE).ok_or_else(|| {
        anyhow::anyhow!(
            "no release asset for this platform ({}) in {}",
            if HOST_TRIPLE.is_empty() {
                "unsupported"
            } else {
                HOST_TRIPLE
            },
            tag
        )
    })?;

    // `--check`: report availability, do not download.
    if args.check {
        return report_check(args.json, &current, &tag, cmp, &selected);
    }

    // 5. Download archive + checksum, verify.
    let archive_bytes = fetcher
        .get(&asset_url(&tag, &selected.archive_name))
        .with_context(|| format!("downloading {}", selected.archive_name))?;
    let checksum_text = String::from_utf8(
        fetcher
            .get(&asset_url(&tag, &selected.checksum_name))
            .with_context(|| format!("downloading {}", selected.checksum_name))?,
    )
    .context("decoding checksum file")?;
    let expected = parse_sha256_file(&checksum_text)
        .ok_or_else(|| anyhow::anyhow!("malformed checksum file {}", selected.checksum_name))?;
    let actual = sha256_hex(&archive_bytes);
    if actual != expected {
        anyhow::bail!(
            "sha256 mismatch for {}: expected {expected}, got {actual} — refusing to install",
            selected.archive_name
        );
    }

    // 6. Extract the inner binary to a temp dir.
    let scratch = std::env::temp_dir().join(format!("yf-self-update-{}", std::process::id()));
    let new_bin = archive::extract_binary(&archive_bytes[..], "yf", &scratch)
        .context("extracting the updated yf binary")?;

    // 7. Atomic in-place swap.
    swap(&new_bin).context("swapping the binary into place")?;
    let _ = std::fs::remove_dir_all(&scratch);

    // 8. PATH-shadow warning (Concern F).
    let shadow = path_shadow_warning(dirs);

    report_updated(args.json, &current, &tag, shadow.as_deref());
    Ok(ExitCode::SUCCESS)
}

/// If a different `yf` appears on `PATH` *before* the vendor bin dir, the freshly
/// updated binary is shadowed. Return a warning string naming the shadower.
pub fn path_shadow_warning(dirs: &Dirs) -> Option<String> {
    let bin = dirs.bin_dir();
    let path = std::env::var_os("PATH")?;
    for dir in std::env::split_paths(&path) {
        let candidate = dir.join("yf");
        if candidate.is_file() {
            // First yf on PATH. If it is NOT in the vendor bin dir, it shadows.
            let canon_dir = std::fs::canonicalize(&dir).ok();
            let canon_bin = std::fs::canonicalize(bin).ok();
            if canon_dir != canon_bin {
                return Some(format!(
                    "another `yf` earlier on PATH shadows the updated one: {} (updated: {})",
                    candidate.display(),
                    bin.join("yf").display()
                ));
            }
            return None; // vendor copy is first — no shadow
        }
    }
    None
}

// ---- Reporting --------------------------------------------------------------

fn refuse(json: bool, src: source::Source) -> Result<ExitCode> {
    let guidance = source::refusal_guidance(src);
    if json {
        let out = serde_json::json!({
            "command": "self update", "status": "refused",
            "source": format!("{src:?}").to_lowercase(), "guidance": guidance,
        });
        println!("{}", serde_json::to_string(&out)?);
    } else {
        eprintln!("refusing to self-update: {guidance}");
    }
    Ok(ExitCode::FAILURE)
}

fn report_uptodate(json: bool, current: &str) -> Result<ExitCode> {
    if json {
        println!(
            "{}",
            serde_json::json!({"command":"self update","status":"up_to_date","version":current})
        );
    } else {
        println!("yf {current} is already the latest release");
    }
    Ok(ExitCode::SUCCESS)
}

fn report_check(
    json: bool,
    current: &str,
    tag: &str,
    cmp: VersionCmp,
    selected: &Selected,
) -> Result<ExitCode> {
    let available = cmp == VersionCmp::UpdateAvailable;
    if json {
        println!(
            "{}",
            serde_json::json!({
                "command": "self update", "status": "checked",
                "current": current, "latest": tag, "update_available": available,
                "asset": selected.archive_name,
            })
        );
    } else if available {
        println!("update available: {current} → {tag} (run `yf self update`)");
    } else {
        println!("yf {current} is up to date (latest: {tag})");
    }
    Ok(ExitCode::SUCCESS)
}

fn report_updated(json: bool, from: &str, tag: &str, shadow: Option<&str>) {
    if json {
        let out = serde_json::json!({
            "command": "self update", "status": "updated",
            "from": from, "to": tag, "shadow_warning": shadow,
        });
        if let Ok(s) = serde_json::to_string(&out) {
            println!("{s}");
        }
    } else {
        println!("updated yf {from} → {tag}");
        if let Some(w) = shadow {
            eprintln!("warning: {w}");
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;
    use std::io::Write;

    #[test]
    fn semver_compare() {
        assert_eq!(
            compare_versions("0.3.2", "v0.4.0"),
            VersionCmp::UpdateAvailable
        );
        assert_eq!(compare_versions("0.3.2", "v0.3.2"), VersionCmp::UpToDate);
        assert_eq!(
            compare_versions("0.4.0", "v0.3.9"),
            VersionCmp::CurrentIsNewerOrUnknown
        );
        // patch default + prerelease suffix tolerated.
        assert_eq!(compare_versions("1.2", "v1.2.0"), VersionCmp::UpToDate);
    }

    #[test]
    fn parse_checksum_forms() {
        let hex = "a".repeat(64);
        assert_eq!(parse_sha256_file(&hex).unwrap(), hex);
        assert_eq!(
            parse_sha256_file(&format!("{hex}  yf-x86_64-unknown-linux-gnu.tar.gz\n")).unwrap(),
            hex
        );
        assert!(parse_sha256_file("not-a-hash").is_none());
        assert!(parse_sha256_file("").is_none());
    }

    fn manifest_json(tag: &str, triple: &str) -> String {
        format!(
            r#"{{
              "announcement_tag": "{tag}",
              "artifacts": {{
                "yf-{triple}.tar.gz": {{
                  "name": "yf-{triple}.tar.gz", "kind": "executable-zip",
                  "target_triples": ["{triple}"],
                  "checksum": "yf-{triple}.tar.gz.sha256"
                }},
                "yf-{triple}.tar.gz.sha256": {{
                  "name": "yf-{triple}.tar.gz.sha256", "kind": "checksum",
                  "target_triples": ["{triple}"]
                }}
              }}
            }}"#
        )
    }

    #[test]
    fn select_artifact_finds_host_zip_and_checksum() {
        let m: DistManifest =
            serde_json::from_str(&manifest_json("v0.4.0", "x86_64-unknown-linux-gnu")).unwrap();
        let s = select_artifact(&m, "x86_64-unknown-linux-gnu").unwrap();
        assert_eq!(s.archive_name, "yf-x86_64-unknown-linux-gnu.tar.gz");
        assert_eq!(s.checksum_name, "yf-x86_64-unknown-linux-gnu.tar.gz.sha256");
        // Wrong triple → None.
        assert!(select_artifact(&m, "mips-unknown-linux-gnu").is_none());
        assert!(select_artifact(&m, "").is_none());
    }

    /// A fetcher that maps a URL's trailing filename to in-memory bytes.
    struct MapFetcher(HashMap<String, Vec<u8>>);
    impl Fetcher for MapFetcher {
        fn get(&self, url: &str) -> Result<Vec<u8>> {
            let file = url.rsplit('/').next().unwrap_or(url);
            self.0
                .get(file)
                .cloned()
                .ok_or_else(|| anyhow::anyhow!("no fixture for {file}"))
        }
    }

    fn make_targz_with_yf(contents: &[u8]) -> Vec<u8> {
        let mut tar_buf = Vec::new();
        {
            let mut b = tar::Builder::new(&mut tar_buf);
            let mut h = tar::Header::new_gnu();
            h.set_size(contents.len() as u64);
            h.set_mode(0o755);
            h.set_cksum();
            b.append_data(&mut h, "yf", contents).unwrap();
            b.finish().unwrap();
        }
        let mut gz = flate2::write::GzEncoder::new(Vec::new(), flate2::Compression::fast());
        gz.write_all(&tar_buf).unwrap();
        gz.finish().unwrap()
    }

    /// Full pipeline against a local fixture (the acceptance path): a bumped
    /// manifest + a real `.tar.gz` + a correct `.sha256` drive
    /// select→download→verify→extract→swap with no network and no clobbering.
    #[test]
    fn full_update_pipeline_against_fixture() {
        // Only meaningful on the supported host triples (HOST_TRIPLE non-empty).
        if HOST_TRIPLE.is_empty() {
            return;
        }
        let archive = make_targz_with_yf(b"NEW-BINARY-BYTES");
        let checksum = format!("{}  yf-{}.tar.gz\n", sha256_hex(&archive), HOST_TRIPLE);
        let manifest = manifest_json("v9.9.9", HOST_TRIPLE);

        let mut map = HashMap::new();
        map.insert("dist-manifest.json".to_string(), manifest.into_bytes());
        map.insert(format!("yf-{HOST_TRIPLE}.tar.gz"), archive);
        map.insert(format!("yf-{HOST_TRIPLE}.tar.gz.sha256"), checksum.into_bytes());
        let fetcher = MapFetcher(map);

        // Swap target: a temp "installed binary" we can assert on.
        let tmp = tempfile::tempdir().unwrap();
        let installed = tmp.path().join("installed-yf");
        std::fs::write(&installed, b"OLD").unwrap();
        let installed2 = installed.clone();
        let swap = move |new_bin: &Path| -> Result<()> {
            std::fs::copy(new_bin, &installed2)?;
            Ok(())
        };

        // dirs with a temp HOME; force=true so source-classification (Unknown here)
        // doesn't block the test.
        let home = tmp.path().to_path_buf();
        let dirs =
            crate::dirs::resolve(move |k| (k == "HOME").then(|| home.clone().into_os_string()));
        let args = SelfUpdateArgs {
            check: false,
            force: true,
            binary_only: true,
            json: true,
        };

        let code = run_inner(&args, &dirs, &fetcher, &swap).unwrap();
        assert_eq!(format!("{code:?}"), format!("{:?}", ExitCode::SUCCESS));
        // The swapped-in binary carries the new bytes — proves extract+verify+swap.
        assert_eq!(std::fs::read(&installed).unwrap(), b"NEW-BINARY-BYTES");
    }

    #[test]
    fn sha256_mismatch_aborts_before_swap() {
        if HOST_TRIPLE.is_empty() {
            return;
        }
        let archive = make_targz_with_yf(b"NEW");
        // Wrong checksum.
        let checksum = format!("{}  x\n", "0".repeat(64));
        let manifest = manifest_json("v9.9.9", HOST_TRIPLE);
        let mut map = HashMap::new();
        map.insert("dist-manifest.json".to_string(), manifest.into_bytes());
        map.insert(format!("yf-{HOST_TRIPLE}.tar.gz"), archive);
        map.insert(format!("yf-{HOST_TRIPLE}.tar.gz.sha256"), checksum.into_bytes());
        let fetcher = MapFetcher(map);

        let swapped = std::cell::Cell::new(false);
        let swap = |_: &Path| -> Result<()> {
            swapped.set(true);
            Ok(())
        };
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().to_path_buf();
        let dirs =
            crate::dirs::resolve(move |k| (k == "HOME").then(|| home.clone().into_os_string()));
        let args = SelfUpdateArgs {
            check: false,
            force: true,
            binary_only: true,
            json: true,
        };
        let err = run_inner(&args, &dirs, &fetcher, &swap).unwrap_err();
        assert!(err.to_string().contains("sha256 mismatch"));
        assert!(!swapped.get(), "must not swap on checksum mismatch");
    }

    #[test]
    fn check_mode_reports_without_swapping() {
        if HOST_TRIPLE.is_empty() {
            return;
        }
        let manifest = manifest_json("v9.9.9", HOST_TRIPLE);
        let mut map = HashMap::new();
        map.insert("dist-manifest.json".to_string(), manifest.into_bytes());
        let fetcher = MapFetcher(map);
        let swapped = std::cell::Cell::new(false);
        let swap = |_: &Path| -> Result<()> {
            swapped.set(true);
            Ok(())
        };
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().to_path_buf();
        let dirs =
            crate::dirs::resolve(move |k| (k == "HOME").then(|| home.clone().into_os_string()));
        let args = SelfUpdateArgs {
            check: true,
            force: true,
            binary_only: true,
            json: true,
        };
        let code = run_inner(&args, &dirs, &fetcher, &swap).unwrap();
        assert_eq!(format!("{code:?}"), format!("{:?}", ExitCode::SUCCESS));
        assert!(!swapped.get(), "--check must not download or swap");
    }
}
