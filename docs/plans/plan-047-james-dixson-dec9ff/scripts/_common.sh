# Shared preamble for plan-047's gate scripts (Issue 1.4).
#
# EXIT-CODE DISCIPLINE — the whole reason these scripts exist as committed files:
#
#     0  capability PRESENT   — the thing the gate measures is true
#     1  capability ABSENT    — the thing the gate measures is false
#     2  the HARNESS could not run — a missing tool, an unreadable tree, a crashed
#                                    dependency. Maps onto INCONCLUSIVE (REQ-DATA-024).
#
# **A gate is only allowed to be red for reason 1.** Three consecutive plan-047 review
# cycles produced a gate that failed for a reason unrelated to what it measures — a
# `KeyError` on a nonexistent key, then `exit 127` on an absent script, then a stub
# exiting 0. Each fix was correct and the CLASS survived. That is what this file encodes.
#
# Every gate `Test:` opens with `set -o pipefail` and pipes stdout through `jq -e`, so the
# ASSERTION lives outside the artifact it polices: the gate resolver is exit-code only
# (coordinator.md, enforced by test_gates.py::_classify), so an assertion INSIDE the script
# cannot stop an empty stub — measured, an empty `.sh` exits 0 and the gate resolves. With
# `jq -e` outside, a stub emitting no JSON fails at the gate.
#
# Every script therefore ALWAYS writes a JSON object to stdout, on every exit path, and
# writes diagnostics to stderr only.

set -u

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
    printf '{"harness_ok":false,"reason":"not a git repository"}\n'; exit 2; }
cd "$REPO_ROOT" || { printf '{"harness_ok":false,"reason":"cannot cd to repo root"}\n'; exit 2; }

# harness_fail <reason> — emit INCONCLUSIVE-shaped JSON and exit 2. Deliberately emits NONE
# of the gate's assertion keys, so `jq -e` sees `null` and cannot read a harness failure as
# a satisfied capability.
harness_fail() {
    printf '{"harness_ok":false,"reason":%s}\n' "$(printf '%s' "$1" | jq -Rs .)"
    exit 2
}

need() { command -v "$1" >/dev/null 2>&1 || harness_fail "required tool not on PATH: $1"; }
