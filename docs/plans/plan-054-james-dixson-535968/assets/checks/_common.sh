#!/usr/bin/env bash
# _common.sh — shared preamble for plan-054's criterion instruments.
#
# NOT a check itself: `verify-red-checks` globs `check-*.sh`, so this file is invisible to it
# by construction rather than by an exclusion anyone has to remember.
#
# THE EXIT CONTRACT EVERY CHECK HONOURS
#   0  the criterion holds
#   1  it does not
#   2  the check could NOT RUN (a missing tool, an unresolvable tree) — INCONCLUSIVE, a
#      statement about the instrument rather than about the tree. `record-red-check` refuses
#      to bank a 2, exactly as `record-red` refuses one from a fixture.
#
# `grep -qv` IS BANNED AS A CRITERION PRIMITIVE (#224, and 0.8 states it outright). Measured:
# `grep -qv PAT file` exits 0 whenever ANY line lacks the pattern, so on a multi-line file it
# is nearly a constant — it cannot fail, and a criterion that cannot fail is not a check. The
# correct spelling of "no line matches" is `! grep -q PAT file`.

set -uo pipefail

ck_inconclusive() { echo "${CHECK_NAME:-check}: INCONCLUSIVE — $*" >&2; exit 2; }
ck_fail()         { echo "${CHECK_NAME:-check}: FAIL — $*" >&2; CK_RC=1; }
ck_pass()         { echo "${CHECK_NAME:-check}: $*"; }

# ck_tree — resolve the tree under test. YF_TREE when the harness set it, else the repo root
# derived from this file's location. A check must be runnable BOTH under redcheck.sh and by
# hand from a criterion command, and those two callers set up differently.
ck_tree() {
  if [ -n "${YF_TREE:-}" ]; then printf '%s' "${YF_TREE}"; return 0; fi
  local here plan_dir root
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  plan_dir="$(cd "${here}/../.." && pwd)"
  root="$(git -C "${plan_dir}" rev-parse --show-toplevel 2>/dev/null)" || return 1
  # Prefer this plan's execution worktree — but ONLY WHILE IT IS STILL THE TREE UNDER TEST.
  #
  # Before the merge-back, fixes land on the execute branch and the worktree is where they are.
  # AFTER the merge-back (§6.5a) the primary carries the merged tree and the worktree is a
  # MERGED MIRROR: its source is identical, but its `target/` still holds a build from whenever
  # it was last compiled there. Measured: `check-stamp-agrees` read the worktree's stale binary
  # and reported the version stamp as `4172196-dirty` against a HEAD of `d793465` — a failure
  # that was purely an artefact of which address space it looked in.
  #
  # So the predicate is "is the worktree's branch still UNMERGED?", not "does the worktree
  # exist?". Once merged, the primary is the tree under test.
  local plan_id; plan_id="$(basename "${plan_dir}")"
  local wt="${root}/.worktrees/${plan_id}"
  if [ -d "${wt}" ] \
     && ! git -C "${root}" merge-base --is-ancestor "${plan_id}-execute" main 2>/dev/null; then
    printf '%s' "${wt}"
  else
    printf '%s' "${root}"
  fi
}

ck_plan_dir() { cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd; }

ck_need() { command -v "$1" >/dev/null 2>&1 || ck_inconclusive "$1 is not on PATH"; }

ck_done() { [ "${CK_RC:-0}" -eq 0 ] && ck_pass "${1:-criterion holds}"; exit "${CK_RC:-0}"; }
