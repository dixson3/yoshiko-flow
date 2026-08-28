#!/usr/bin/env bash
# _common.sh — shared preamble for this repo's criterion instruments.
#
# PROVENANCE: COPIED (never moved) from plan-054's bundle by plan-055 Issue 0.8, then RE-BASED
# for its new home at `scripts/checks/`. plan-054's `assets/checks/` copies are FROZEN AS A
# RECORD — 34 lines of that completed plan reference them — and are deliberately not the live
# instruments. Divergence between the two is expected and is not a drift defect: nothing
# executes the frozen copy.
#
# WHAT THE RE-BASING CHANGED, and why it was mandatory. plan-054's `ck_tree` derived the tree
# from `${BASH_SOURCE[0]}/../..` — correct when the file lived at `<plan-dir>/assets/checks/`,
# and WRONG here, where that probe resolves to the repo root's parent-of-scripts and the
# `.worktrees/<plan_id>` preference can never match. Every guarded criterion would then grep
# the PRIMARY tree, where an in-flight plan's new test functions do not exist — failing closed
# but unrunnably. So the tree is now derived from `git rev-parse --show-toplevel` and the plan
# id comes from an explicit `YF_PLAN_ID`, never from a path shape.
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
  local here root
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  root="$(git -C "${here}" rev-parse --show-toplevel 2>/dev/null)" || return 1

  # Prefer a plan's execution worktree — but ONLY when the caller NAMES the plan (YF_PLAN_ID)
  # and ONLY WHILE THAT WORKTREE IS STILL THE TREE UNDER TEST.
  #
  # Before the merge-back, fixes land on the execute branch and the worktree is where they are.
  # AFTER the merge-back the primary carries the merged tree and the worktree is a MERGED
  # MIRROR: its source is identical, but its `target/` still holds a build from whenever it was
  # last compiled there. Measured on plan-054: `check-stamp-agrees` read the worktree's stale
  # binary and reported the version stamp as `4172196-dirty` against a HEAD of `d793465` — a
  # failure that was purely an artefact of which address space it looked in.
  #
  # So the predicate is "is the worktree's branch still UNMERGED?", not "does it exist?".
  #
  # WITH NO `YF_PLAN_ID` THE PRIMARY ROOT IS THE ANSWER. That is the honest default at this
  # path: `scripts/checks/` belongs to the repo, not to any one plan, so guessing a plan id
  # from the file's location — which is what the pre-re-basing version did — would silently
  # pick a tree the caller never named.
  local plan_id="${YF_PLAN_ID:-}"
  if [ -n "${plan_id}" ]; then
    local wt="${root}/.worktrees/${plan_id}"
    if [ -d "${wt}" ] \
       && ! git -C "${root}" merge-base --is-ancestor "${plan_id}-execute" main 2>/dev/null; then
      printf '%s' "${wt}"
      return 0
    fi
  fi
  printf '%s' "${root}"
}

# ck_plan_dir — the plan bundle a check reports against. EXPLICIT, never inferred from this
# file's location: at `scripts/checks/` there is no plan above us to infer. `--plan-dir` (passed
# by a caller) wins; else `YF_PLAN_DIR`; else `<tree>/docs/plans/${YF_PLAN_ID}` when the plan is
# named. With nothing named it is INCONCLUSIVE — a check that needs a plan dir and was given no
# plan must say so rather than resolve to an arbitrary directory.
ck_plan_dir() {
  if [ -n "${1:-}" ]; then (cd "$1" && pwd); return 0; fi
  if [ -n "${YF_PLAN_DIR:-}" ]; then (cd "${YF_PLAN_DIR}" && pwd); return 0; fi
  if [ -n "${YF_PLAN_ID:-}" ]; then
    local d; d="$(ck_tree)/docs/plans/${YF_PLAN_ID}"
    [ -d "${d}" ] && { (cd "${d}" && pwd); return 0; }
  fi
  ck_inconclusive "no plan dir: pass one as \$1, or set YF_PLAN_DIR / YF_PLAN_ID"
}

ck_need() { command -v "$1" >/dev/null 2>&1 || ck_inconclusive "$1 is not on PATH"; }

ck_done() { [ "${CK_RC:-0}" -eq 0 ] && ck_pass "${1:-criterion holds}"; exit "${CK_RC:-0}"; }
