//! Upgrade-detection nudge (plan-018 Issue 4.1) — notify-only.
//!
//! On `yf version` / `yf doctor`, after the real output, print a one-line "a newer
//! yf is available" nudge to **stderr**. Properties:
//!
//! - **Throttled (24h):** the network check runs at most once per 24h; in between,
//!   the cached latest tag (`~/.cache/yf/update-check.json`) decides the nudge.
//! - **Fail-open:** a short (2s) timeout and every error are swallowed — a network
//!   problem never delays or breaks the command (the nudge just doesn't appear).
//! - **Vendor-only:** suppressed for Homebrew / from-build / unknown installs
//!   (`Source::nag_eligible`), so only vendor users — who *can* `yf self update` —
//!   are nudged.
//! - **Opt-out:** `YF_NO_UPDATE_CHECK=1` disables it; `CI` is auto-detected and
//!   skipped.
//!
//! Notify-ONLY: it never downloads or swaps — that is `yf self update`.

use std::path::Path;
use std::time::{SystemTime, UNIX_EPOCH};

use serde::{Deserialize, Serialize};

use super::{source, update};
use crate::dirs::Dirs;

/// Re-check the network at most this often.
const THROTTLE_SECS: u64 = 24 * 60 * 60;
/// Short timeout for the background-ish check (fail-open).
const CHECK_TIMEOUT_SECS: u64 = 2;
const CACHE_BASENAME: &str = "update-check.json";

/// Persisted throttle state: when we last checked and the latest tag we saw.
#[derive(Debug, Default, Clone, Serialize, Deserialize)]
struct CheckCache {
    #[serde(default)]
    last_check_epoch: u64,
    #[serde(default)]
    latest_tag: String,
}

/// Entry point: print an upgrade nudge if warranted. Best-effort and **fail-open**
/// — any error is swallowed so a `yf version`/`doctor` run is never affected.
pub fn maybe_notify(dirs: &Dirs) {
    let _ = try_notify(dirs);
}

fn try_notify(dirs: &Dirs) -> Option<()> {
    if suppressed(|k| std::env::var_os(k).is_some()) {
        return None;
    }
    // Vendor-only: skip the (cheap) cache/network work for non-vendor installs.
    if !source::detect(dirs).nag_eligible() {
        return None;
    }

    let now = epoch_now();
    let cache_path = dirs.cache_dir().join(CACHE_BASENAME);
    let mut cache = read_cache(&cache_path).unwrap_or_default();

    if should_query(now, cache.last_check_epoch) {
        if let Some(tag) = fetch_latest_tag() {
            cache.latest_tag = tag;
            cache.last_check_epoch = now;
            let _ = write_cache(&cache_path, &cache);
        }
        // On a failed check we deliberately do NOT bump last_check_epoch, so the
        // next invocation retries rather than waiting a full 24h.
    }

    let line = nudge_line(crate::VERSION, &cache.latest_tag)?;
    eprintln!("{line}");
    Some(())
}

/// Opt-out / CI suppression. Pure: `present(key)` reports whether an env var is set.
pub fn suppressed(present: impl Fn(&str) -> bool) -> bool {
    present("YF_NO_UPDATE_CHECK") || present("CI")
}

/// Whether a fresh network check is due (throttle elapsed). Pure.
pub fn should_query(now: u64, last_check: u64) -> bool {
    now.saturating_sub(last_check) >= THROTTLE_SECS
}

/// The nudge line if `latest` is strictly newer than `current`, else `None`. Pure.
pub fn nudge_line(current: &str, latest_tag: &str) -> Option<String> {
    if latest_tag.is_empty() {
        return None;
    }
    match update::compare_versions(current, latest_tag) {
        update::VersionCmp::UpdateAvailable => Some(format!(
            "note: yf {} is available (you have {current}) — run `yf self update` \
             (set YF_NO_UPDATE_CHECK=1 to silence)",
            latest_tag.trim_start_matches('v')
        )),
        _ => None,
    }
}

/// Fetch just the latest release tag, with a short timeout. Fail-open → `None`.
fn fetch_latest_tag() -> Option<String> {
    use std::io::Read;
    let agent = ureq::AgentBuilder::new()
        .timeout(std::time::Duration::from_secs(CHECK_TIMEOUT_SECS))
        .build();
    let resp = agent.get(&update::manifest_latest_url()).call().ok()?;
    let mut buf = String::new();
    resp.into_reader().read_to_string(&mut buf).ok()?;
    let manifest: update::DistManifest = serde_json::from_str(&buf).ok()?;
    (!manifest.announcement_tag.is_empty()).then_some(manifest.announcement_tag)
}

fn epoch_now() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

fn read_cache(path: &Path) -> Option<CheckCache> {
    let s = std::fs::read_to_string(path).ok()?;
    serde_json::from_str(&s).ok()
}

fn write_cache(path: &Path, cache: &CheckCache) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let json = serde_json::to_string_pretty(cache).unwrap_or_default();
    std::fs::write(path, json)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn suppressed_by_optout_or_ci() {
        assert!(suppressed(|k| k == "YF_NO_UPDATE_CHECK"));
        assert!(suppressed(|k| k == "CI"));
        assert!(!suppressed(|_| false));
    }

    #[test]
    fn throttle_respects_24h() {
        let day = 24 * 60 * 60;
        assert!(should_query(day, 0)); // exactly 24h elapsed → due
        assert!(should_query(day + 1, 0));
        assert!(!should_query(day - 1, 0)); // within 24h → not due
        assert!(should_query(2_000_000_000, 0)); // never checked → epoch 0 is ancient
    }

    #[test]
    fn nudge_only_when_newer() {
        assert!(nudge_line("0.3.2", "v0.4.0").unwrap().contains("0.4.0"));
        assert!(nudge_line("0.3.2", "v0.3.2").is_none()); // same
        assert!(nudge_line("0.4.0", "v0.3.9").is_none()); // older
        assert!(nudge_line("0.3.2", "").is_none()); // no cached tag
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
    fn non_vendor_source_is_not_notified() {
        // A temp HOME with no receipt → source is Unknown → nag_eligible() false →
        // try_notify returns None without any network work.
        let tmp = tempfile::tempdir().unwrap();
        let home = tmp.path().to_path_buf();
        let dirs =
            crate::dirs::resolve(move |k| (k == "HOME").then(|| home.clone().into_os_string()));
        assert!(try_notify(&dirs).is_none());
    }
}
