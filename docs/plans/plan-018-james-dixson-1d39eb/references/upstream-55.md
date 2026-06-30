# Upstream #55 — Upgrade detection and self-update (vendor install model)

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/55
- **State:** OPEN
- **Labels:** type::feature, priority::medium
- **Disposition in this plan:** include (core objective)

## Body (verbatim)

> Transition yf away from a Homebrew-based install to a vendor install model like `uv`
> (self-contained, vendored distribution). Add native upgrade detection (notify when a newer
> version is available) and self-update capability (`yf` can update itself in place), rather than
> relying on `brew upgrade`.

## How this plan resolves it

cargo-dist (kept as the build engine) already produces prebuilt binaries; this plan adds the
consumer side: a `curl|sh` vendor install retargeted to an XDG layout (`~/.local/bin` + `~/.config`
/`~/.cache`/`~/.local/share/yf`), a native `yf self update` (hand-rolled `ureq`+`self-replace`,
GitHub-Releases-API check + verified atomic in-place swap) with install-source detection that
**refuses on a Homebrew copy** (Homebrew kept as secondary), a throttled/fail-open upgrade
notification on `yf version`/`yf doctor`, `yf self install --from-build` for dev, and a post-update
hook that refreshes user-scope skills/rules. Closes #55.
