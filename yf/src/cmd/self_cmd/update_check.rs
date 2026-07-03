//! Shared, **network-free** update-check cache helpers (plan-019 Issue 3.1).
//!
//! The version/doctor upgrade nudge (`nag.rs`, REQ-YF-SELF-006) and the preflight
//! self-update offer (`preflight.rs`, REQ-YF-PRE-009) both read the same cached
//! "latest known tag" (`~/.cache/yf/update-check.json`) and both gate on the same
//! "is a newer version available" comparison. That shared, **cache-only** surface
//! lives here so neither consumer duplicates it.
//!
//! The **network** fetch (`fetch_latest_tag`) stays in `nag.rs` — it is the *sole*
//! writer of this cache. Preflight is a pure reader (REQ-YF-PRE-009: no network),
//! so a preflight-surfaced offer is *eventually consistent* — it appears only once
//! the throttled `yf version`/`yf doctor` path has refreshed the cache.

use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

use super::update;
use crate::dirs::Dirs;

/// Cache file basename under the XDG cache dir (`~/.cache/yf/`).
pub const CACHE_BASENAME: &str = "update-check.json";

/// Persisted throttle state: when we last checked and the latest tag we saw.
/// Shared by the nag writer and the preflight reader.
#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct CheckCache {
    #[serde(default)]
    pub last_check_epoch: u64,
    #[serde(default)]
    pub latest_tag: String,
}

/// The cache path: `<cache_dir>/update-check.json`.
pub fn cache_path(dirs: &Dirs) -> PathBuf {
    dirs.cache_dir().join(CACHE_BASENAME)
}

/// Read the cache, `None` on any error (missing / malformed). Never writes.
pub fn read_cache(path: &Path) -> Option<CheckCache> {
    let s = std::fs::read_to_string(path).ok()?;
    serde_json::from_str(&s).ok()
}

/// Persist the cache (creating the parent dir). Called only by the nag writer.
pub fn write_cache(path: &Path, cache: &CheckCache) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let json = serde_json::to_string_pretty(cache).unwrap_or_default();
    std::fs::write(path, json)
}

/// The newer tag (trimmed of a leading `v`) iff `latest_tag` is strictly newer
/// than `current`, else `None`. Pure — the shared availability gate both the
/// nudge and the offer build on. An empty cached tag is never "available".
pub fn newer_tag(current: &str, latest_tag: &str) -> Option<String> {
    if latest_tag.is_empty() {
        return None;
    }
    match update::compare_versions(current, latest_tag) {
        update::VersionCmp::UpdateAvailable => Some(latest_tag.trim_start_matches('v').to_string()),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // REQ-YF-SELF-006 / REQ-YF-PRE-009: the shared cache-only availability gate.
    #[test]
    fn newer_tag_only_when_strictly_newer() {
        assert_eq!(newer_tag("0.3.2", "v0.4.0").as_deref(), Some("0.4.0"));
        assert_eq!(newer_tag("0.3.2", "0.4.0").as_deref(), Some("0.4.0")); // no leading v
        assert!(newer_tag("0.3.2", "v0.3.2").is_none()); // same
        assert!(newer_tag("0.4.0", "v0.3.9").is_none()); // older
        assert!(newer_tag("0.3.2", "").is_none()); // empty cache
    }

    #[test]
    fn cache_round_trips() {
        let tmp = tempfile::tempdir().unwrap();
        let path = tmp.path().join("sub").join(CACHE_BASENAME);
        let c = CheckCache {
            last_check_epoch: 12345,
            latest_tag: "v0.4.0".to_string(),
        };
        write_cache(&path, &c).unwrap();
        let back = read_cache(&path).unwrap();
        assert_eq!(back.last_check_epoch, 12345);
        assert_eq!(back.latest_tag, "v0.4.0");
    }

    #[test]
    fn read_missing_is_none() {
        let tmp = tempfile::tempdir().unwrap();
        assert!(read_cache(&tmp.path().join("nope.json")).is_none());
    }
}
