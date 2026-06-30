//! Install-source classification for `yf self update` (plan-018 Issue 3.3).
//!
//! Decides how the **running** `yf` was installed so `self update` and the upgrade
//! nag (4.1) do the right thing:
//!
//! | Source      | `self update` | nag (4.1) |
//! |:------------|:--------------|:----------|
//! | `Homebrew`  | **refuse** → `brew upgrade` | suppressed |
//! | `Vendor`    | proceed (in-place swap)     | shown     |
//! | `FromBuild` | refuse unless `--force` (round-trips to vendor) | suppressed |
//! | `Unknown`   | refuse unless `--force`     | suppressed |
//!
//! **Path-primary, not receipt-primary** (the pass-1 correction): the authoritative
//! signal is the **canonicalized `current_exe()`** path, so detection survives a
//! missing or `INSTALL_UPDATER=0` receipt. The receipt only *corroborates* by
//! supplying the vendor prefix.
//!
//! Two canonicalization pins from the red-team:
//! - **Canonicalize BOTH sides** — `current_exe()` AND the receipt `install_prefix`
//!   — before the prefix test, so a symlinked `~/.local/bin` (→ a real store path)
//!   does not false-`Unknown` (Concern E). Done here via [`canonical`].
//! - The vendor prefix is **derived from the receipt** (`install_prefix`), preferred
//!   over a hardcoded `~/.local/bin` literal, with `dirs.bin_dir()` as the fallback
//!   when no receipt exists (Concern D).

use std::path::{Component, Path, PathBuf};

use crate::dirs::Dirs;

use super::receipt;

/// How the running `yf` binary was installed.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Source {
    /// Installed by the cargo-dist `curl|sh` installer or a prior `self update`.
    Vendor,
    /// A Homebrew Cellar copy — `self update` must refuse and defer to `brew upgrade`.
    Homebrew,
    /// Promoted from a local `cargo build` via `yf self install --from-build`.
    FromBuild,
    /// Could not be positively classified — refuse `self update` unless `--force`.
    Unknown,
}

impl Source {
    /// Whether `self update` may proceed without `--force`. Only a confirmed
    /// `Vendor` install auto-proceeds; `Homebrew` never proceeds even with `--force`.
    pub fn auto_updatable(self) -> bool {
        matches!(self, Source::Vendor)
    }

    /// Whether the upgrade-check nag (4.1) should be shown. Vendor-only.
    pub fn nag_eligible(self) -> bool {
        matches!(self, Source::Vendor)
    }
}

/// Classify the running binary by detecting `current_exe()`, the receipt-derived
/// vendor prefix, and the from-build marker — then delegating to [`classify`].
///
/// All IO (canonicalize, receipt/marker reads) happens here; [`classify`] is the
/// pure decision the unit tests drive directly.
pub fn detect(dirs: &Dirs) -> Source {
    let exe = std::env::current_exe().ok();
    let exe = exe.as_deref();

    // Vendor prefix: prefer the receipt's install_prefix (canonicalized), else the
    // dirs bin_dir() (canonicalized). Either may be None (no receipt / dir absent).
    let receipt = receipt::load_receipt(dirs).ok().flatten();
    let vendor_prefix = receipt
        .as_ref()
        .and_then(|r| r.canonical_install_prefix())
        .or_else(|| canonical(dirs.bin_dir()));

    let from_build = receipt::load_from_build_marker(dirs)
        .ok()
        .flatten()
        .is_some();

    classify(exe, vendor_prefix.as_deref(), from_build)
}

/// Pure classifier. `exe` is the running binary path and `vendor_prefix` the
/// vendor install dir (or `None`); **both are canonicalized inside** before the
/// containment test (the "canonicalize BOTH sides" pin — a symlinked `~/.local/bin`
/// on either side must not false-`Unknown`). `from_build` is whether yf's
/// from-build marker is present.
///
/// Precedence: **Homebrew > FromBuild > Vendor > Unknown**. Homebrew is checked
/// first and is absolute — a brew copy is never updatable, even `--force`. The
/// from-build marker outranks the vendor-prefix test because a from-build install
/// *also* lands under the vendor prefix (`~/.local/bin`), and we must not nag it.
pub fn classify(exe: Option<&Path>, vendor_prefix: Option<&Path>, from_build: bool) -> Source {
    let exe_canon = exe.and_then(canonical);

    // 1. Homebrew Cellar — highest precedence. Canonicalizing first means a
    //    `/opt/homebrew/bin/yf` symlink that resolves into `.../Cellar/...` is
    //    caught (Concern: brew bin/yf → Cellar).
    if let Some(e) = exe_canon.as_deref() {
        if is_homebrew(e) {
            return Source::Homebrew;
        }
    }

    // 2. From-build marker — yf-authored, outranks the vendor-prefix test.
    if from_build {
        return Source::FromBuild;
    }

    // 3. Vendor prefix — canonicalize BOTH sides before the containment test, so a
    //    symlinked install dir (on the exe side, the prefix side, or both) resolves
    //    to the same real path (Concern E). `detect()` already canonicalizes the
    //    prefix; re-canonicalizing here is idempotent and makes the guarantee total.
    let prefix_canon = vendor_prefix.and_then(canonical);
    if let (Some(e), Some(p)) = (exe_canon.as_deref(), prefix_canon.as_deref()) {
        if e.starts_with(p) {
            return Source::Vendor;
        }
    }

    // 4. Anything else.
    Source::Unknown
}

/// True when a canonicalized path lives inside a Homebrew Cellar (macOS
/// `/opt/homebrew/Cellar`, `/usr/local/Cellar`, or linuxbrew
/// `/home/linuxbrew/.linuxbrew/Cellar`). Keying on a `Cellar` path component
/// covers every prefix without hardcoding the brew root.
fn is_homebrew(path: &Path) -> bool {
    path.components().any(|c| match c {
        Component::Normal(s) => s == "Cellar",
        _ => false,
    }) || path.components().any(|c| match c {
        // linuxbrew may not nest under Cellar in every layout; the `.linuxbrew`
        // component is the robust secondary signal.
        Component::Normal(s) => s == ".linuxbrew",
        _ => false,
    })
}

/// Canonicalize a path, returning `None` if it cannot be resolved (does not exist).
fn canonical(p: &Path) -> Option<PathBuf> {
    std::fs::canonicalize(p).ok()
}

/// Operator-facing guidance for a refused `self update`, by source.
pub fn refusal_guidance(source: Source) -> &'static str {
    match source {
        Source::Homebrew => {
            "this `yf` was installed via Homebrew — run `brew upgrade yf` instead \
             (self-update will not touch a Cellar copy)"
        }
        Source::FromBuild => {
            "this `yf` is a local from-build install — re-run `yf self install \
             --from-build` to rebuild, or `yf self update --force` to switch to the \
             latest vendor release"
        }
        Source::Unknown => {
            "could not confirm this `yf` is a vendor install (no matching install \
             prefix) — re-run with `--force` to update anyway"
        }
        Source::Vendor => "",
    }
}

#[cfg(all(test, unix))]
mod tests {
    use super::*;

    #[test]
    fn homebrew_cellar_is_detected() {
        // A real path under a Cellar component. We build it inside a temp dir so
        // canonicalize succeeds.
        let tmp = tempfile::tempdir().unwrap();
        let cellar = tmp
            .path()
            .join("Cellar")
            .join("yf")
            .join("0.3.2")
            .join("bin");
        std::fs::create_dir_all(&cellar).unwrap();
        let exe = cellar.join("yf");
        std::fs::write(&exe, b"").unwrap();
        assert_eq!(classify(Some(&exe), None, false), Source::Homebrew);
    }

    #[test]
    fn homebrew_wins_even_with_from_build_marker() {
        let tmp = tempfile::tempdir().unwrap();
        let cellar = tmp.path().join("Cellar").join("yf").join("bin");
        std::fs::create_dir_all(&cellar).unwrap();
        let exe = cellar.join("yf");
        std::fs::write(&exe, b"").unwrap();
        // Even if a stale from-build marker exists, a Cellar copy is Homebrew.
        assert_eq!(classify(Some(&exe), None, true), Source::Homebrew);
    }

    #[test]
    fn under_vendor_prefix_is_vendor() {
        let tmp = tempfile::tempdir().unwrap();
        let bin = tmp.path().join(".local").join("bin");
        std::fs::create_dir_all(&bin).unwrap();
        let exe = bin.join("yf");
        std::fs::write(&exe, b"").unwrap();
        let prefix = canonical(&bin).unwrap();
        assert_eq!(classify(Some(&exe), Some(&prefix), false), Source::Vendor);
    }

    #[test]
    fn symlinked_install_dir_does_not_false_refuse() {
        // Concern E: ~/.local/bin is a symlink to a real store dir. Canonicalizing
        // BOTH the exe and the prefix must still yield Vendor.
        let tmp = tempfile::tempdir().unwrap();
        let real = tmp.path().join("store").join("bin");
        std::fs::create_dir_all(&real).unwrap();
        let exe_real = real.join("yf");
        std::fs::write(&exe_real, b"").unwrap();

        let link = tmp.path().join("local-bin"); // symlink → store/bin
        std::os::unix::fs::symlink(&real, &link).unwrap();
        let exe_via_link = link.join("yf");

        // Vendor prefix supplied as the *symlinked* path (as a receipt might store
        // it); classify canonicalizes both sides.
        let prefix_via_link = link.clone();
        assert_eq!(
            classify(Some(&exe_via_link), Some(&prefix_via_link), false),
            Source::Vendor,
            "symlinked install dir must canonicalize to the same real path"
        );
    }

    #[test]
    fn from_build_marker_outranks_vendor_prefix() {
        // A from-build install lands under the vendor prefix but must classify
        // FromBuild (no nag).
        let tmp = tempfile::tempdir().unwrap();
        let bin = tmp.path().join(".local").join("bin");
        std::fs::create_dir_all(&bin).unwrap();
        let exe = bin.join("yf");
        std::fs::write(&exe, b"").unwrap();
        let prefix = canonical(&bin).unwrap();
        assert_eq!(classify(Some(&exe), Some(&prefix), true), Source::FromBuild);
    }

    #[test]
    fn outside_prefix_is_unknown() {
        let tmp = tempfile::tempdir().unwrap();
        let elsewhere = tmp.path().join("opt").join("random");
        std::fs::create_dir_all(&elsewhere).unwrap();
        let exe = elsewhere.join("yf");
        std::fs::write(&exe, b"").unwrap();
        let other = tmp.path().join(".local").join("bin");
        std::fs::create_dir_all(&other).unwrap();
        let prefix = canonical(&other).unwrap();
        assert_eq!(classify(Some(&exe), Some(&prefix), false), Source::Unknown);
    }

    #[test]
    fn no_prefix_no_marker_is_unknown() {
        let tmp = tempfile::tempdir().unwrap();
        let exe = tmp.path().join("yf");
        std::fs::write(&exe, b"").unwrap();
        assert_eq!(classify(Some(&exe), None, false), Source::Unknown);
    }

    #[test]
    fn source_predicates() {
        assert!(Source::Vendor.auto_updatable() && Source::Vendor.nag_eligible());
        assert!(!Source::Homebrew.auto_updatable() && !Source::Homebrew.nag_eligible());
        assert!(!Source::FromBuild.auto_updatable() && !Source::FromBuild.nag_eligible());
        assert!(!Source::Unknown.auto_updatable() && !Source::Unknown.nag_eligible());
    }
}
