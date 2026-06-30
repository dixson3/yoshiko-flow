//! Shared filesystem helpers for `yf self …` (plan-018 Epic 3).
//!
//! Atomic, dependency-free file install used by `self install` (3.5) and as the
//! non-running-binary path for `self update` (3.4 uses `self-replace` for the
//! running binary itself). "Atomic" = write to a same-directory temp, then
//! `rename` over the destination, so a reader never sees a half-written file and
//! the swap stays within one filesystem.

use std::path::{Path, PathBuf};

use anyhow::{Context, Result};

/// Copy `src` to `dst` atomically and mark it executable (unix), creating `dst`'s
/// parent directory if needed. The temp file is a sibling of `dst` so the final
/// `rename` is atomic on the same filesystem.
pub fn atomic_install(src: &Path, dst: &Path) -> Result<()> {
    let bytes = std::fs::read(src).with_context(|| format!("reading {}", src.display()))?;
    atomic_install_bytes(&bytes, dst)
}

/// Like [`atomic_install`] but from an in-memory buffer (used after extraction).
pub fn atomic_install_bytes(bytes: &[u8], dst: &Path) -> Result<()> {
    if let Some(parent) = dst.parent() {
        std::fs::create_dir_all(parent)
            .with_context(|| format!("creating dir {}", parent.display()))?;
    }
    let tmp = temp_sibling(dst);
    std::fs::write(&tmp, bytes).with_context(|| format!("writing temp {}", tmp.display()))?;
    set_executable(&tmp)?;
    match std::fs::rename(&tmp, dst) {
        Ok(()) => Ok(()),
        Err(e) => {
            let _ = std::fs::remove_file(&tmp);
            Err(e).with_context(|| format!("renaming temp into {}", dst.display()))
        }
    }
}

/// A unique same-dir temp path for `dst`.
fn temp_sibling(dst: &Path) -> PathBuf {
    let dir = dst.parent().unwrap_or_else(|| Path::new("."));
    let base = dst
        .file_name()
        .map(|s| s.to_string_lossy().into_owned())
        .unwrap_or_else(|| "out".to_string());
    dir.join(format!(".{}.tmp.{}", base, std::process::id()))
}

/// Mark `path` executable (`0o755`) on unix; a no-op elsewhere.
#[cfg(unix)]
fn set_executable(path: &Path) -> Result<()> {
    use std::os::unix::fs::PermissionsExt;
    let mut perms = std::fs::metadata(path)?.permissions();
    perms.set_mode(0o755);
    std::fs::set_permissions(path, perms)
        .with_context(|| format!("setting +x on {}", path.display()))?;
    Ok(())
}

#[cfg(not(unix))]
fn set_executable(_path: &Path) -> Result<()> {
    Ok(())
}

#[cfg(all(test, unix))]
mod tests {
    use super::*;
    use std::os::unix::fs::PermissionsExt;

    #[test]
    fn installs_and_sets_exec_bit() {
        let tmp = tempfile::tempdir().unwrap();
        let src = tmp.path().join("src-bin");
        std::fs::write(&src, b"payload").unwrap();
        let dst = tmp.path().join("nested").join("yf");
        atomic_install(&src, &dst).unwrap();
        assert_eq!(std::fs::read(&dst).unwrap(), b"payload");
        assert_eq!(
            std::fs::metadata(&dst).unwrap().permissions().mode() & 0o111,
            0o111
        );
    }

    #[test]
    fn overwrites_existing_atomically() {
        let tmp = tempfile::tempdir().unwrap();
        let dst = tmp.path().join("yf");
        std::fs::write(&dst, b"old").unwrap();
        atomic_install_bytes(b"new", &dst).unwrap();
        assert_eq!(std::fs::read(&dst).unwrap(), b"new");
        // No leftover temp files.
        let leftovers: Vec<_> = std::fs::read_dir(tmp.path())
            .unwrap()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_name().to_string_lossy().contains(".tmp."))
            .collect();
        assert!(leftovers.is_empty(), "temp sibling should be renamed away");
    }
}
