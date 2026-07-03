#!/usr/bin/env bash
# smoke.sh — end-to-end Tier-2 smoke DRIVER for the yf-plan lifecycle rework
#            (plan-021 Epic 0, Issue 0.2)
#
# Two-phase driver, because the plan → execute → land walk itself needs the
# interactive `/yf-plan` skill (an agent), which is not scriptable:
#
#   smoke.sh setup  [<scratch-home>]   — build+install the MODIFIED skill into a
#                                        sandbox HOME (via bootstrap.sh), create a
#                                        throwaway git project with `bd`
#                                        initialized, and print the operator
#                                        checklist (the manual /yf-plan steps).
#
#   smoke.sh verify [<project-dir>]    — assert the observable post-conditions of
#                                        the NEW lifecycle over the driven project
#                                        and write the `topology.txt` acceptance
#                                        artifact the capability gate consumes.
#
#   smoke.sh all    [<scratch-home>]   — setup, then (after the operator has run
#                                        the checklist under the printed HOME) is
#                                        NOT auto-run; `all` runs setup and prints
#                                        the exact verify command to run next.
#
# The manual checklist lives in README.md (§ "Operator checklist"). smoke.sh
# owns setup + machine assertions; the human owns the agent-driven walk.
#
# NEW lifecycle asserted (target of the rework):
#   * planning branch      <plan-id>-development
#   * landed feature branch <plan-id>            (landing-strategy=feature-branch)
#   * execution branch     <plan-id>-execute     cut from a PINNED base
#                                                (main, or feature <plan-id>),
#                                                NEVER from -development (no
#                                                branch-of-a-branch)
#   * .yf-plan.local.json carries "landing-strategy"
#   * plan.md carries a "**Fingerprint:**" header field (written at APPROVE)

set -euo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRATCH_DIR="${HARNESS_DIR}/.scratch"       # harness-local bookkeeping (gitignore'd)
ENV_FILE="${SCRATCH_DIR}/sandbox.env"

# ------------------------------------------------------------------ setup ------
cmd_setup() {
  local scratch_home="${1:-}"
  mkdir -p "${SCRATCH_DIR}"

  # 1. Build + install the MODIFIED skill into an isolated sandbox HOME.
  #    (bootstrap.sh exports YF_SANDBOX_HOME / _BIN / _SKILL and REPO_ROOT.)
  # shellcheck source=bootstrap.sh
  source "${HARNESS_DIR}/bootstrap.sh" ${scratch_home:+"${scratch_home}"}

  # 2. Throwaway git project INSIDE the sandbox HOME (so any user-scope config the
  #    walk writes stays inside the sandbox).
  local project="${YF_SANDBOX_HOME}/project"
  rm -rf "${project}"
  mkdir -p "${project}"
  git -C "${project}" init -q
  git -C "${project}" config user.email "smoke@yoshiko.test"
  git -C "${project}" config user.name  "yf-plan smoke"
  git -C "${project}" symbolic-ref HEAD refs/heads/main
  printf '# smoke scratch project\n' > "${project}/README.md"
  git -C "${project}" add -A
  git -C "${project}" commit -q -m "initial commit"

  # 3. Initialize beads (the plan intake/execute path depends on a healthy bd).
  if command -v bd >/dev/null 2>&1; then
    ( cd "${project}" && bd init >/dev/null 2>&1 || true )
    echo ">> bd initialized in ${project}"
  else
    echo ">> WARNING: bd not on PATH — initialize beads before the /yf-plan walk." >&2
  fi

  # 4. Persist the sandbox facts for `verify`.
  {
    echo "YF_SANDBOX_HOME=${YF_SANDBOX_HOME}"
    echo "YF_SANDBOX_BIN=${YF_SANDBOX_BIN}"
    echo "YF_SANDBOX_SKILL=${YF_SANDBOX_SKILL}"
    echo "SMOKE_PROJECT=${project}"
  } > "${ENV_FILE}"

  cat <<EOF

=========================================================================
 SANDBOX READY.  Now run the OPERATOR CHECKLIST (README § Operator checklist)
 in a Claude Code session whose HOME is the sandbox, so the MODIFIED skill
 (not your real ~/.claude install) is the one that fires:

     export HOME="${YF_SANDBOX_HOME}"
     cd "${project}"
     # then, in that session:
     #   /yf-plan  smoke: trivial no-op plan
     #   ... approve ...            (writes **Fingerprint:** + auto-commit)
     #   /yf-plan execute           (pours epic, cuts <id>-execute from pinned base)
     #   ... drive the trivial epic to done, land ...

 When the walk is complete, verify + capture topology with:

     "${HARNESS_DIR}/smoke.sh" verify "${project}"
=========================================================================
EOF
}

# ----------------------------------------------------------------- verify ------
_fail=0
_ok()   { echo "  PASS: $*"; }
_bad()  { echo "  FAIL: $*" >&2; _fail=$((_fail + 1)); }

cmd_verify() {
  local project="${1:-}"
  if [ -z "${project}" ] && [ -f "${ENV_FILE}" ]; then
    # shellcheck disable=SC1090
    project="$(. "${ENV_FILE}"; echo "${SMOKE_PROJECT}")"
  fi
  if [ -z "${project}" ] || [ ! -d "${project}/.git" ]; then
    echo "ERROR: no scratch project (pass <project-dir> or run 'setup' first)" >&2
    exit 1
  fi
  project="$(cd "${project}" && pwd)"
  echo ">> verifying lifecycle over ${project}"

  # Discover the plan id from the -development branch (the planning branch).
  local plan_id
  plan_id="$(git -C "${project}" for-each-ref --format='%(refname:short)' refs/heads \
             | sed -n 's/-development$//p' | head -1 || true)"
  if [ -z "${plan_id}" ]; then
    _bad "no <plan-id>-development branch found — planning branch missing"
  else
    _ok  "planning branch present: ${plan_id}-development"
  fi

  # --- branch topology assertions -------------------------------------------
  has() { git -C "${project}" show-ref --verify --quiet "refs/heads/$1"; }

  if [ -n "${plan_id}" ]; then
    # execution branch must exist
    if has "${plan_id}-execute"; then
      _ok "execution branch present: ${plan_id}-execute"
    else
      _bad "execution branch ${plan_id}-execute missing"
    fi

    # landing target: EITHER feature branch <plan-id> (feature-branch strategy)
    # OR main advanced (main strategy). Detect strategy from config.
    local strategy=""
    if [ -f "${project}/.yf-plan.local.json" ]; then
      strategy="$(sed -n 's/.*"landing-strategy"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
                  "${project}/.yf-plan.local.json" | head -1 || true)"
    fi
    if [ -n "${strategy}" ]; then
      _ok "landing-strategy config present: ${strategy}"
    else
      _bad "landing-strategy key absent from .yf-plan.local.json"
    fi

    # pinned-base / no-branch-of-a-branch, STRATEGY-AWARE:
    #   -execute must be cut from the PINNED BASE, never off the -development tip
    #   (ambient HEAD). The pinned base differs by landing-strategy:
    #     * main           → base is `main`. -development is a SEPARATE branch
    #                        (not landed into main), so it must NOT be an ancestor
    #                        of -execute; if it is, execute was cut off the
    #                        planning branch — the regression this rework removes.
    #     * feature-branch → base is feature `<plan-id>`. -development is LANDED
    #                        into that feature, so -development being an ancestor
    #                        of -execute is EXPECTED; the meaningful property is
    #                        that -execute descends from feature `<plan-id>`.
    is_anc() { git -C "${project}" merge-base --is-ancestor "$1" "$2" 2>/dev/null; }

    case "${strategy}" in
      feature-branch)
        if has "${plan_id}"; then
          _ok "feature branch present: ${plan_id}"
          if has "${plan_id}-execute" && is_anc "${plan_id}" "${plan_id}-execute"; then
            _ok "${plan_id}-execute descends from feature ${plan_id} (pinned base)"
          else
            _bad "${plan_id}-execute does not descend from feature ${plan_id} (base not pinned)"
          fi
        else
          _bad "feature-branch strategy but feature branch ${plan_id} missing"
        fi
        ;;
      main)
        if has "${plan_id}-execute" && is_anc "main" "${plan_id}-execute"; then
          _ok "${plan_id}-execute descends from main (pinned base)"
        else
          _bad "${plan_id}-execute does not descend from main (base not pinned)"
        fi
        if has "${plan_id}-execute" && has "${plan_id}-development" \
           && is_anc "${plan_id}-development" "${plan_id}-execute"; then
          _bad "branch-of-a-branch: ${plan_id}-execute descends from ${plan_id}-development (cut off planning branch, not main)"
        elif has "${plan_id}-execute" && has "${plan_id}-development"; then
          _ok "${plan_id}-execute does NOT descend from -development (base pinned to main)"
        fi
        ;;
      *)
        # Unknown/absent strategy — best-effort: at minimum -execute must not be a
        # child of the -development tip.
        if has "${plan_id}-execute" && has "${plan_id}-development" \
           && is_anc "${plan_id}-development" "${plan_id}-execute"; then
          _bad "branch-of-a-branch: ${plan_id}-execute descends from ${plan_id}-development (strategy unknown; cannot confirm pinned base)"
        fi
        ;;
    esac
  fi

  # --- Fingerprint header in plan.md ----------------------------------------
  local plan_md="" _search_roots=()
  [ -d "${project}/docs/plans" ] && _search_roots+=("${project}/docs/plans")
  [ -d "${project}/Incubator" ] && _search_roots+=("${project}/Incubator")
  if [ "${#_search_roots[@]}" -gt 0 ]; then
    plan_md="$(find "${_search_roots[@]}" -name plan.md -path "*${plan_id:-}*" 2>/dev/null | head -1 || true)"
  fi
  if [ -n "${plan_md}" ] && [ -f "${plan_md}" ]; then
    if grep -q '^\*\*Fingerprint:\*\*' "${plan_md}"; then
      _ok "plan.md carries **Fingerprint:** header ($(basename "$(dirname "${plan_md}")"))"
    else
      _bad "plan.md missing **Fingerprint:** header (${plan_md})"
    fi
  else
    _bad "no plan.md found under docs/plans or Incubator for ${plan_id:-<unknown>}"
  fi

  # --- record topology acceptance artifact ----------------------------------
  local topo="${HARNESS_DIR}/topology.txt"
  {
    echo "# yf-plan lifecycle smoke — observed branch topology"
    echo "# generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "# project:   ${project}"
    echo "# plan-id:   ${plan_id:-<none>}"
    echo
    echo "## git branch -vv"
    git -C "${project}" branch -vv || true
    echo
    echo "## git worktree list"
    git -C "${project}" worktree list || true
    echo
    echo "## verdict"
    if [ "${_fail}" -eq 0 ]; then echo "PASS (0 failures)"; else echo "FAIL (${_fail} failure(s))"; fi
  } > "${topo}"
  echo ">> wrote topology artifact: ${topo}"

  if [ "${_fail}" -eq 0 ]; then
    echo ">> SMOKE PASS"
  else
    echo ">> SMOKE FAIL: ${_fail} assertion(s) failed" >&2
    exit 1
  fi
}

# ------------------------------------------------------------------- main ------
case "${1:-all}" in
  setup)  shift; cmd_setup "${1:-}" ;;
  verify) shift; cmd_verify "${1:-}" ;;
  all)    shift; cmd_setup "${1:-}"
          echo ">> 'all' completed setup only; run 'smoke.sh verify' after the walk." ;;
  *)      echo "usage: smoke.sh {setup|verify|all} [arg]" >&2; exit 2 ;;
esac
