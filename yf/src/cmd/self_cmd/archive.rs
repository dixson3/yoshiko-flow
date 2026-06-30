//! Pure-Rust `.tar.gz` extraction for `yf self update` (plan-018 Issue 3.4a).
//!
//! The `unix-archive = ".tar.gz"` flip (1.2) lets the updater decode release assets
//! with **`flate2`** (gzip, pure-Rust `miniz_oxide` backend) + **`tar`** — no C
//! codec and **no system `tar`/`xz`** dependency, so extraction works on minimal
//! Linux / Alpine / container hosts that lack an `xz` userland (the landmine a
//! `.tar.xz` asset would hit).
//!
//! [`extract_binary`] streams a `.tar.gz` reader, finds the inner binary entry
//! (tolerating an enclosing top-level directory, e.g. `yf-<triple>/yf`), unpacks it
//! to a destination directory, and returns the extracted path with the executable
//! bit set (unix). Issue 3.4 hands that path to its sha256-verify + atomic
//! `self-replace` step.

use std::io::Read;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use flate2::read::GzDecoder;

/// Extract the binary named `binary_name` from a `.tar.gz` stream into `dest_dir`.
///
/// Returns the path to the extracted binary (`dest_dir/<binary_name>`). The match
/// is on the entry's **final path component**, so a tarball that wraps the binary
/// in a top-level directory (`yf-aarch64-apple-darwin/yf`) is handled the same as a
/// flat one (`yf`). The first matching regular-file entry wins.
///
/// On unix the extracted file is marked `0o755` so it is immediately executable.
pub fn extract_binary<R: Read>(reader: R, binary_name: &str, dest_dir: &Path) -> Result<PathBuf> {
    std::fs::create_dir_all(dest_dir)
        .with_context(|| format!("creating extract dir {}", dest_dir.display()))?;

    let gz = GzDecoder::new(reader);
    let mut archive = tar::Archive::new(gz);
    let dest = dest_dir.join(binary_name);

    for entry in archive.entries().context("reading tar entries")? {
        let mut entry = entry.context("reading tar entry")?;
        let is_file = entry.header().entry_type().is_file();
        let path = entry.path().context("decoding tar entry path")?.into_owned();
        let matches = path
            .file_name()
            .map(|n| n == std::ffi::OsStr::new(binary_name))
            .unwrap_or(false);

        if is_file && matches {
            // Unpack just this entry to the fixed dest path (do NOT trust the
            // archive's directory structure — avoids path-traversal and keeps the
            // output predictable for the caller's verify+swap).
            let mut out = std::fs::File::create(&dest)
                .with_context(|| format!("creating {}", dest.display()))?;
            std::io::copy(&mut entry, &mut out)
                .with_context(|| format!("writing {}", dest.display()))?;
            drop(out);
            set_executable(&dest)?;
            return Ok(dest);
        }
    }

    anyhow::bail!("binary `{binary_name}` not found in archive")
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

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;

    /// Build an in-memory `.tar.gz` from `(path, contents)` entries.
    fn make_targz(entries: &[(&str, &[u8])]) -> Vec<u8> {
        let mut tar_buf = Vec::new();
        {
            let mut builder = tar::Builder::new(&mut tar_buf);
            for (name, data) in entries {
                let mut header = tar::Header::new_gnu();
                header.set_size(data.len() as u64);
                header.set_mode(0o644);
                header.set_cksum();
                builder.append_data(&mut header, name, *data).unwrap();
            }
            builder.finish().unwrap();
        }
        let mut gz = flate2::write::GzEncoder::new(Vec::new(), flate2::Compression::fast());
        gz.write_all(&tar_buf).unwrap();
        gz.finish().unwrap()
    }

    #[test]
    fn extracts_flat_binary() {
        let bytes = make_targz(&[("yf", b"#!binary-contents")]);
        let tmp = tempfile::tempdir().unwrap();
        let out = extract_binary(&bytes[..], "yf", tmp.path()).unwrap();
        assert_eq!(out, tmp.path().join("yf"));
        assert_eq!(std::fs::read(&out).unwrap(), b"#!binary-contents");
    }

    #[test]
    fn extracts_binary_nested_under_top_dir() {
        // cargo-dist may wrap the binary in a per-triple directory.
        let bytes = make_targz(&[
            ("yf-aarch64-apple-darwin/README.md", b"docs"),
            ("yf-aarch64-apple-darwin/yf", b"real-binary"),
        ]);
        let tmp = tempfile::tempdir().unwrap();
        let out = extract_binary(&bytes[..], "yf", tmp.path()).unwrap();
        assert_eq!(std::fs::read(&out).unwrap(), b"real-binary");
    }

    #[cfg(unix)]
    #[test]
    fn extracted_binary_is_executable() {
        use std::os::unix::fs::PermissionsExt;
        let bytes = make_targz(&[("yf", b"x")]);
        let tmp = tempfile::tempdir().unwrap();
        let out = extract_binary(&bytes[..], "yf", tmp.path()).unwrap();
        let mode = std::fs::metadata(&out).unwrap().permissions().mode();
        assert_eq!(mode & 0o111, 0o111, "owner/group/other exec bits set");
    }

    #[test]
    fn missing_binary_is_error() {
        let bytes = make_targz(&[("not-yf", b"data")]);
        let tmp = tempfile::tempdir().unwrap();
        let err = extract_binary(&bytes[..], "yf", tmp.path()).unwrap_err();
        assert!(err.to_string().contains("not found"));
    }
}
