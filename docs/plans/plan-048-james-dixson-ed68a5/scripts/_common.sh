#!/usr/bin/env bash
# _common.sh — shared helpers for plan-048's capability gate scripts.
# Sourced, never executed. Callers must already `set -u`.
#
# Exit discipline (see gate-run.sh): 0 present, 1 absent, 2 harness could not run.

# Repo root, resolved from this file's location (plan bundle -> scripts/).
GATE_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAN_DIR="$(cd "${GATE_SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${PLAN_DIR}/../../.." && pwd)"

gate_present() { echo "GATE: capability PRESENT — $*"; exit 0; }
gate_absent()  { echo "GATE: capability ABSENT — $*" >&2; exit 1; }
gate_harness() { echo "GATE: HARNESS FAILURE — $*" >&2; exit 2; }

# require_tool <name> — a missing tool is a harness failure (2), never an absent
# capability (1). This is the same distinction gate-run.sh enforces for 127.
require_tool() {
  command -v "$1" >/dev/null 2>&1 || gate_harness "required tool not on PATH: $1"
}

# require_file <path> — a missing INPUT is a harness failure; a missing
# DELIVERABLE is the caller's job to report as absent.
require_file() {
  [ -f "$1" ] || gate_harness "required input not found: $1"
}
