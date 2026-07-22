#!/usr/bin/env bash
#
# sync_installer.sh — stage the hosted `install.sh` for yoshikoflow.sh.
#
# The site hosts ONE convenience file, install.sh, which is a byte-for-byte mirror of
# cargo-dist's `yf-installer.sh` published on GitHub Releases. GitHub Releases stays
# canonical for every binary and for self-update; this script only mirrors the installer
# script so `curl … yoshikoflow.sh/install.sh | sh` works as a friendly first-install.
#
# Behavior:
#   1. Resolve the latest cargo-dist release's `dist-manifest.json` and read its pinned
#      `announcement_tag`.
#   2. Fetch `yf-installer.sh` for THAT PINNED TAG over HTTPS (not "latest", so the
#      staged bytes are reproducible).
#   3. If the manifest publishes a sha256 for the installer script, verify it. cargo-dist
#      emits `.sha256` sidecars for the release *tarballs*; the installer script itself may
#      have none — in that case the integrity floor is the pinned-tag HTTPS fetch. The
#      installer in turn fetches sha256-checksummed tarballs from GitHub Releases.
#   4. If no cargo-dist release exists yet, stage a FAIL-SAFE placeholder install.sh that
#      prints a "no release yet" message and exits non-zero, so a premature `curl | sh`
#      fails safely.
#
# Output: web/content/extra/install.sh (gitignored — a generated artifact). Pelican copies
# it to the site root as /install.sh; the Makefile `sync_installer` target re-uploads that
# one key with a short Cache-Control and invalidates it.
#
# Env overrides (for testing): REPO (owner/repo), OUT (output path).

set -euo pipefail

REPO="${REPO:-dixson3/yoshiko-flow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT="${OUT:-${WEB_DIR}/content/extra/install.sh}"

RELEASES_URL="https://github.com/${REPO}/releases"
MANIFEST_LATEST="https://github.com/${REPO}/releases/latest/download/dist-manifest.json"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

log() { printf '  %s\n' "$*" >&2; }

stage_placeholder() {
  local reason="$1"
  log "no cargo-dist release available (${reason}) — staging fail-safe placeholder"
  mkdir -p "$(dirname "${OUT}")"
  cat > "${OUT}" <<PLACEHOLDER
#!/bin/sh
# yf bootstrap installer — PLACEHOLDER.
#
# No cargo-dist release of yoshiko-flow has been published yet, so there is no installer to
# mirror. This placeholder fails safe rather than pretending to install anything.
echo "yf: no release is available yet." >&2
echo "yf: watch ${RELEASES_URL} for the first tagged release." >&2
echo "yf: meanwhile, install via Homebrew:  brew install ${REPO%%/*}/tap/yf" >&2
exit 1
PLACEHOLDER
  chmod +x "${OUT}"
  log "staged placeholder -> ${OUT}"
}

# --- 1. Resolve the manifest -------------------------------------------------------------
log "resolving dist-manifest.json for ${REPO} (latest release)"
if ! curl --proto '=https' --tlsv1.2 -fsSL "${MANIFEST_LATEST}" -o "${TMPDIR}/dist-manifest.json" 2>/dev/null; then
  stage_placeholder "dist-manifest.json not found at latest release"
  exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
  log "jq not found; cannot parse manifest — staging placeholder"
  stage_placeholder "jq unavailable"
  exit 0
fi

TAG="$(jq -r '.announcement_tag // empty' "${TMPDIR}/dist-manifest.json" 2>/dev/null || true)"
if [ -z "${TAG}" ]; then
  stage_placeholder "manifest has no announcement_tag"
  exit 0
fi
log "pinned release tag: ${TAG}"

# --- 2. Fetch the installer for the PINNED tag -------------------------------------------
INSTALLER_URL="https://github.com/${REPO}/releases/download/${TAG}/yf-installer.sh"
log "fetching yf-installer.sh for ${TAG}"
if ! curl --proto '=https' --tlsv1.2 -fsSL "${INSTALLER_URL}" -o "${TMPDIR}/install.sh" 2>/dev/null; then
  stage_placeholder "no yf-installer.sh artifact at ${TAG}"
  exit 0
fi

# --- 3. Verify sha256 IF the manifest publishes one for the installer script -------------
INSTALLER_SHA="$(jq -r '
  (.artifacts // {}) as $a
  | [ $a | to_entries[]
      | select(.value.kind == "checksum")
      | select((.value.name // "") | test("yf-installer\\.sh"))
      | .value.name ] | first // empty
' "${TMPDIR}/dist-manifest.json" 2>/dev/null || true)"

if [ -n "${INSTALLER_SHA}" ]; then
  SHA_URL="https://github.com/${REPO}/releases/download/${TAG}/${INSTALLER_SHA}"
  log "manifest publishes an installer checksum (${INSTALLER_SHA}) — verifying"
  if curl --proto '=https' --tlsv1.2 -fsSL "${SHA_URL}" -o "${TMPDIR}/installer.sha256" 2>/dev/null; then
    EXPECTED="$(awk '{print $1}' "${TMPDIR}/installer.sha256")"
    if command -v sha256sum >/dev/null 2>&1; then
      ACTUAL="$(sha256sum "${TMPDIR}/install.sh" | awk '{print $1}')"
    else
      ACTUAL="$(shasum -a 256 "${TMPDIR}/install.sh" | awk '{print $1}')"
    fi
    if [ "${EXPECTED}" != "${ACTUAL}" ]; then
      log "ERROR: installer sha256 mismatch (expected ${EXPECTED}, got ${ACTUAL})"
      exit 2
    fi
    log "sha256 verified: ${ACTUAL}"
  else
    log "WARNING: checksum named in manifest but not downloadable — relying on pinned-tag HTTPS fetch"
  fi
else
  log "no installer sha256 in manifest — integrity floor is the pinned-tag HTTPS fetch"
fi

# --- 4. Stage ----------------------------------------------------------------------------
mkdir -p "$(dirname "${OUT}")"
cp -f "${TMPDIR}/install.sh" "${OUT}"
chmod +x "${OUT}"
log "staged yf-installer.sh (${TAG}) -> ${OUT}"
