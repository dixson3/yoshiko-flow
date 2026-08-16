#!/usr/bin/env bash
# bootstrap.sh — Tier-2 sandboxed-HOME harness for yf-plan (plan-021 Epic 0, Issue 0.1)
#
# Builds the yf binary with the MODIFIED repo `skills/` re-embedded, installs it
# into an ISOLATED sandbox HOME, and asserts the yf-plan resolver's first hit is
# the sandbox copy (not the operator's `~/.claude/...` install).
#
# WHY a sandboxed HOME (RT2-1 resolver-shadowing hazard):
#   The yf-plan SKILL_DIR resolver searches `~/.claude/skills` FIRST with
#   `head -1`. If the operator already has `~/.claude/skills/yf-plan` installed,
#   ANY scratch `<scratch>/.claude/skills/yf-plan` is SHADOWED — the resolver
#   returns the OLD installed copy and a smoke would silently test the wrong
#   skill. Setting `HOME=<scratch-home>` makes `~` expand to the sandbox, so the
#   re-embedded/re-installed MODIFIED skill IS the resolver's first hit.
#
# Usage:
#   ./bootstrap.sh [<scratch-home>]
#     <scratch-home>  Sandbox HOME dir. Default: a fresh mktemp -d.
#
# On success prints (and, when sourced, exports) the sandbox facts:
#   YF_SANDBOX_HOME   the isolated HOME
#   YF_SANDBOX_BIN    the freshly built yf binary
#   YF_SANDBOX_SKILL  the resolved yf-plan skill dir (asserted == sandbox copy)
#
# Sourceable: `source bootstrap.sh <home>` leaves the three vars in your shell
# so smoke.sh can consume them. Executed standalone it just prints them.

set -euo pipefail

# --- locate repo root (harness lives at <repo>/skills/yf-plan/test-harness) ----
_HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${_HARNESS_DIR}/../../.." && pwd)"
MANIFEST="${REPO_ROOT}/yf/Cargo.toml"

if [ ! -f "${MANIFEST}" ]; then
  echo "ERROR: cannot find yf/Cargo.toml at ${MANIFEST}" >&2
  echo "       (expected harness at <repo>/skills/yf-plan/test-harness)" >&2
  exit 1
fi

# --- sandbox HOME --------------------------------------------------------------
YF_SANDBOX_HOME="${1:-$(mktemp -d "${TMPDIR:-/tmp}/yf-plan-sandbox.XXXXXX")}"
mkdir -p "${YF_SANDBOX_HOME}"
YF_SANDBOX_HOME="$(cd "${YF_SANDBOX_HOME}" && pwd)"   # absolutize

echo ">> repo root:     ${REPO_ROOT}"
echo ">> sandbox HOME:  ${YF_SANDBOX_HOME}"

# --- build: make sure the yf binary is current ---------------------------------
# NOTE: this is a DEBUG build, and `rust-embed` is declared WITHOUT `debug-embed`,
# so the debug `yf` reads `../skills` FROM DISK AT RUNTIME (yf/src/embed.rs
# `#[folder]` bakes the tree only in release). Repo edits under `skills/` therefore
# reach the installed skill with NO rebuild; this build is needed only when `yf`'s
# own Rust code changed. Build under the sandbox HOME so nothing touches the
# operator's cargo/home state beyond the shared target dir.
echo ">> cargo build (debug; reads ${REPO_ROOT}/skills at runtime) ..."
HOME="${YF_SANDBOX_HOME}" cargo build --manifest-path "${MANIFEST}"

# Resolve the built binary. This is a cargo WORKSPACE (root Cargo.toml has
# [workspace]), so the binary lands in the workspace-root target dir
# (${REPO_ROOT}/target/debug/yf), NOT the crate-local yf/target/debug/yf. Ask cargo
# for the target dir rather than hardcoding, then fall back to the known candidates.
TARGET_DIR="$(HOME="${YF_SANDBOX_HOME}" cargo metadata --no-deps --format-version 1 \
  --manifest-path "${MANIFEST}" 2>/dev/null \
  | sed -n 's/.*"target_directory":"\([^"]*\)".*/\1/p')"
YF_SANDBOX_BIN=""
for cand in "${TARGET_DIR:+${TARGET_DIR}/debug/yf}" \
            "${REPO_ROOT}/target/debug/yf" \
            "${REPO_ROOT}/yf/target/debug/yf"; do
  [ -n "${cand}" ] && [ -x "${cand}" ] && { YF_SANDBOX_BIN="${cand}"; break; }
done
if [ -z "${YF_SANDBOX_BIN}" ]; then
  echo "ERROR: built yf binary not found/executable (looked in workspace target dir" >&2
  echo "       '${TARGET_DIR:-?}', ${REPO_ROOT}/target/debug, ${REPO_ROOT}/yf/target/debug)" >&2
  exit 1
fi
echo ">> built yf:      ${YF_SANDBOX_BIN}"

# --- install the modified skill into the sandbox HOME --------------------------
# Default scope=user, surface=claude → anchor is $HOME → lands at
# <sandbox-home>/.claude/skills/yf-plan.
echo ">> yf skills install (into sandbox HOME) ..."
INSTALL_JSON="$(HOME="${YF_SANDBOX_HOME}" "${YF_SANDBOX_BIN}" skills install --json)"
echo "${INSTALL_JSON}"

# --- assert the resolver's first hit is the sandbox copy -----------------------
# Mirror the SKILL.md SKILL_DIR resolver exactly, under the sandbox HOME.
GIT_ROOT="$(git -C "${REPO_ROOT}" rev-parse --show-toplevel 2>/dev/null || echo "${REPO_ROOT}")"
YF_SANDBOX_SKILL="$(
  HOME="${YF_SANDBOX_HOME}" find \
    "${YF_SANDBOX_HOME}/.claude/skills" \
    "${YF_SANDBOX_HOME}/.agents/skills" \
    "${GIT_ROOT}/.claude/skills" \
    "${GIT_ROOT}/.agents/skills" \
    .claude/skills .agents/skills \
    -maxdepth 1 -name yf-plan -type d 2>/dev/null | head -1 || true
)"

if [ -z "${YF_SANDBOX_SKILL}" ]; then
  echo "ERROR: resolver found no yf-plan skill dir under the sandbox HOME" >&2
  exit 1
fi
echo ">> resolved skill: ${YF_SANDBOX_SKILL}"

case "${YF_SANDBOX_SKILL}" in
  "${YF_SANDBOX_HOME}/.claude/skills/yf-plan"|"${YF_SANDBOX_HOME}/.agents/skills/yf-plan")
    echo ">> OK: resolver's first hit is the SANDBOX copy (not shadowed)."
    ;;
  *)
    echo "ERROR: resolver returned a NON-sandbox path: ${YF_SANDBOX_SKILL}" >&2
    echo "       The operator's real ~/.claude install is shadowing the sandbox." >&2
    echo "       Ensure HOME is set to ${YF_SANDBOX_HOME} for every step." >&2
    exit 1
    ;;
esac

export YF_SANDBOX_HOME YF_SANDBOX_BIN YF_SANDBOX_SKILL REPO_ROOT

# When executed (not sourced), emit the facts for the caller to capture.
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  echo "YF_SANDBOX_HOME=${YF_SANDBOX_HOME}"
  echo "YF_SANDBOX_BIN=${YF_SANDBOX_BIN}"
  echo "YF_SANDBOX_SKILL=${YF_SANDBOX_SKILL}"
fi
