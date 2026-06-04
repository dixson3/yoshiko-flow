#!/usr/bin/env bash
# Thin wrapper around install.py — the dependency-aware skills installer.
#
# All logic (frontmatter parsing, group computation, dependency closure, tool
# checks, copy + companion-rule install) lives in install.py and runs via `uv`.
# This wrapper preserves the documented `./install.sh ...` entrypoint and forwards
# every argument unchanged. Run `./install.sh --help` for usage.
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: 'uv' is required to run the installer but was not found on PATH." >&2
  echo "Install uv: https://docs.astral.sh/uv/" >&2
  exit 1
fi

exec uv run "$(dirname "$0")/install.py" "$@"
