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
#   * the plan bundle is born OKF: reserved index.md (not README.md) + reserved
#     newest-first log.md (not an in-plan.md **Phase log:** block), and plan.md
#     dual-writes a typed YAML frontmatter block (type: Plan / okf_spec: OKF-PLAN)
#     alongside the legacy **Field:** header lines

set -euo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRATCH_DIR="${HARNESS_DIR}/.scratch"       # harness-local bookkeeping (gitignore'd)
ENV_FILE="${SCRATCH_DIR}/sandbox.env"
REAL_HOME="${HOME}"                         # operator's real HOME (captured before sandboxing)

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

  # 4. Optional: make an interactive /yf-plan walk in the sandbox painless.
  #    Auth on macOS lives in the login Keychain (per-USER, not per-HOME), so a
  #    sandbox HOME already shares it — no token to copy, no re-login. We only link
  #    the real ~/.claude.json config so `claude` in the sandbox isn't treated as a
  #    first run. We deliberately do NOT link the whole ~/.claude (that would shadow
  #    the MODIFIED skill with the operator's installed copy). Best-effort.
  if [ -f "${REAL_HOME}/.claude.json" ] && [ ! -e "${YF_SANDBOX_HOME}/.claude.json" ]; then
    ln -s "${REAL_HOME}/.claude.json" "${YF_SANDBOX_HOME}/.claude.json" 2>/dev/null \
      && echo ">> linked ${REAL_HOME}/.claude.json into the sandbox (Keychain auth is shared)" || true
  fi

  # 5. Persist the sandbox facts for `drive` / `verify`.
  {
    echo "YF_SANDBOX_HOME=${YF_SANDBOX_HOME}"
    echo "YF_SANDBOX_BIN=${YF_SANDBOX_BIN}"
    echo "YF_SANDBOX_SKILL=${YF_SANDBOX_SKILL}"
    echo "REPO_ROOT=${REPO_ROOT}"
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

  # --- OKF bundle layout + Fingerprint header in plan.md --------------------
  local plan_md="" _search_roots=()
  [ -d "${project}/docs/plans" ] && _search_roots+=("${project}/docs/plans")
  [ -d "${project}/Incubator" ] && _search_roots+=("${project}/Incubator")
  if [ "${#_search_roots[@]}" -gt 0 ]; then
    plan_md="$(find "${_search_roots[@]}" -name plan.md -path "*${plan_id:-}*" 2>/dev/null | head -1 || true)"
  fi
  if [ -n "${plan_md}" ] && [ -f "${plan_md}" ]; then
    local plan_dir; plan_dir="$(dirname "${plan_md}")"

    # OKF layout: orientation is the reserved index.md listing, NOT a README.md.
    if [ -f "${plan_dir}/index.md" ]; then
      _ok "plan bundle carries OKF index.md (not README.md)"
    else
      _bad "plan bundle missing OKF index.md (${plan_dir})"
    fi
    if [ -f "${plan_dir}/README.md" ]; then
      _bad "plan bundle still carries a legacy README.md (${plan_dir}/README.md)"
    else
      _ok "plan bundle has no legacy README.md"
    fi

    # OKF layout: the phase log is the reserved, newest-first log.md — NOT an
    # in-plan.md **Phase log:** block.
    if [ -f "${plan_dir}/log.md" ]; then
      _ok "plan bundle carries reserved log.md"
    else
      _bad "plan bundle missing reserved log.md (${plan_dir})"
    fi
    if grep -q '^\*\*Phase log:\*\*' "${plan_md}"; then
      _bad "plan.md still carries a legacy **Phase log:** block (should live in log.md)"
    else
      _ok "plan.md carries no legacy **Phase log:** block"
    fi

    # OKF dual-write: plan.md leads with a typed YAML frontmatter block
    # (type: Plan / okf_spec: OKF-PLAN) alongside the legacy **Field:** lines.
    if [ "$(head -1 "${plan_md}")" = "---" ] \
       && grep -q '^type: Plan$' "${plan_md}" \
       && grep -q '^okf_spec: OKF-PLAN$' "${plan_md}"; then
      _ok "plan.md carries OKF frontmatter (type: Plan / okf_spec: OKF-PLAN)"
    else
      _bad "plan.md missing OKF frontmatter (type: Plan / okf_spec: OKF-PLAN)"
    fi

    if grep -q '^\*\*Fingerprint:\*\*' "${plan_md}"; then
      _ok "plan.md carries **Fingerprint:** header ($(basename "${plan_dir}"))"
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

# ------------------------------------------------------------------ drive ------
# Mechanically drive the NEW lifecycle over the sandbox project using the MODIFIED
# skill's plan_manager.py verbs — the deterministic, non-interactive equivalent of
# the operator's /yf-plan walk. Feature-branch strategy: planning on
# <id>-development, land on feature <id>, execute cuts <id>-execute from the pinned
# feature base. This exercises exactly the topology the capability gate checks.
_env_get() { [ -f "${ENV_FILE}" ] && ( . "${ENV_FILE}"; eval "echo \${$1:-}" ); }

cmd_drive() {
  local project="${1:-$(_env_get SMOKE_PROJECT)}"
  local skill; skill="$(_env_get YF_SANDBOX_SKILL)"
  [ -d "${project}/.git" ] || { echo "ERROR: no sandbox project — run 'setup' first" >&2; exit 1; }
  [ -d "${skill}/scripts" ] || { echo "ERROR: sandbox skill missing (${skill})" >&2; exit 1; }

  local PM=(env -u VIRTUAL_ENV uv run "${skill}/scripts/plan_manager.py")
  local jget=(env -u VIRTUAL_ENV uv run "${skill}/scripts/plan_manager.py" json-get)

  pushd "${project}" >/dev/null
  echo '{"landing-strategy":"feature-branch"}' > .yf-plan.local.json

  echo ">> [drive] init plan"
  local pj plan_dir plan_id
  pj="$("${PM[@]}" init "smoke: trivial no-op plan")"
  plan_dir="$(printf '%s' "${pj}" | "${jget[@]}" plan_dir)"
  plan_id="$(printf '%s' "${pj}" | "${jget[@]}" plan_id)"
  echo "   plan_id=${plan_id}"

  echo ">> [drive] planning branch ${plan_id}-development"
  git checkout -q -b "${plan_id}-development"

  echo ">> [drive] approve -> fingerprint -> auto-commit"
  "${PM[@]}" update-status "${plan_dir}" approved -m "smoke approve" >/dev/null
  "${PM[@]}" fingerprint write "${plan_dir}" --json >/dev/null
  "${PM[@]}" commit-plan "${plan_dir}" --json

  echo ">> [drive] land on feature ${plan_id} (feature-branch strategy)"
  git branch "${plan_id}"          # feature branch at the planning tip = the landing
  git checkout -q "${plan_id}"     # primary on feature: the plan folder is present here

  echo ">> [drive] execute: worktree ensure (cut ${plan_id}-execute from pinned feature base)"
  local wt viable
  wt="$("${PM[@]}" worktree ensure "${plan_dir}" --json)"
  printf '%s\n' "${wt}"
  viable="$(printf '%s' "${wt}" | "${jget[@]}" viable)"
  case "${viable}" in
    True|true) echo ">> [drive] worktree viable; execute branch created." ;;
    *) echo ">> [drive] WARNING: worktree not viable (reason: $(printf '%s' "${wt}" | "${jget[@]}" reason))." >&2
       echo ">> [drive] The execute-branch topology check will fail — inspect the reason above." >&2 ;;
  esac
  popd >/dev/null
  echo ">> [drive] done"
}

# ------------------------------------------------------------------- gate ------
# One-shot: setup -> drive -> verify -> Tier-1, with a single combined verdict.
cmd_gate() {
  local scratch_home="${1:-}"
  echo "==================== [1/5] SETUP (build + sandbox install) ===================="
  cmd_setup "${scratch_home}"
  local project repo_root
  project="$(_env_get SMOKE_PROJECT)"
  repo_root="$(_env_get REPO_ROOT)"

  echo ""
  echo "==================== [2/5] DRIVE (mechanical lifecycle) ======================="
  cmd_drive "${project}"

  echo ""
  echo "==================== [3/5] VERIFY (topology assertions) ======================="
  local verify_rc=0
  cmd_verify "${project}" || verify_rc=$?

  echo ""
  echo "==================== [4/5] CONFIG TIERS (REQ-YF-PRE-004 / REQ-PLAN-079) ======="
  local cfg_rc=0
  cmd_config "${project}" || cfg_rc=$?

  echo ""
  echo "==================== [5/5] TIER-1 (test_worktree.py, repo tree) ==============="
  local t1_rc=0
  ( cd "${repo_root}" && env -u VIRTUAL_ENV uv run skills/yf-plan/scripts/test_worktree.py ) || t1_rc=$?

  echo ""
  echo "======================================= VERDICT ==============================="
  echo "  Tier-2 scratch smoke (topology): $([ "${verify_rc}" -eq 0 ] && echo PASS || echo FAIL)"
  echo "  Tier-2 config tiers + roots:     $([ "${cfg_rc}" -eq 0 ] && echo PASS || echo FAIL)"
  echo "  Tier-1 test_worktree.py:         $([ "${t1_rc}" -eq 0 ] && echo PASS || echo FAIL)"
  echo "  topology artifact:               ${HARNESS_DIR}/topology.txt"
  if [ "${verify_rc}" -eq 0 ] && [ "${cfg_rc}" -eq 0 ] && [ "${t1_rc}" -eq 0 ]; then
    echo ""
    echo "  ✅ CAPABILITY GATE SATISFIED. Resolve it with:"
    echo "       bd gate resolve yf-mol-al2.10"
    return 0
  fi
  echo ""
  echo "  ❌ One or more checks failed — do NOT resolve the gate. See output above." >&2
  return 1
}

# ------------------------------------------------------------- config-tiers ----
# Mechanically drive the THREE-TIER config reader (REQ-YF-PRE-004 / -004a) and the
# configurable roots (REQ-PLAN-079) with the MODIFIED skill, under the sandbox HOME.
#
# Tier-1 (test_config_tiers.py) covers this by importing the module; this phase is
# the Tier-2 counterpart — a real `plan_manager.py init` subprocess resolving real
# config files on disk, which is what an operator actually hits. The distinction
# matters because the roots bind at IMPORT time: an in-process test can be fooled by
# module caching in a way a fresh subprocess cannot.
cmd_config() {
  local project="${1:-$(_env_get SMOKE_PROJECT)}"
  local skill; skill="$(_env_get YF_SANDBOX_SKILL)"
  [ -d "${project}/.git" ] || { echo "ERROR: no sandbox project — run 'setup' first" >&2; exit 1; }
  [ -d "${skill}/scripts" ] || { echo "ERROR: sandbox skill missing (${skill})" >&2; exit 1; }

  # Isolated sub-project so this phase cannot perturb the topology walk's repo.
  local proj="${project}-config"
  rm -rf "${proj}"; mkdir -p "${proj}/.yf/plan"
  git -C "${proj}" init -q .
  git -C "${proj}" config user.email "smoke@yoshiko.test"
  git -C "${proj}" config user.name  "yf-plan smoke"

  local PM=(env -u VIRTUAL_ENV uv run "${skill}/scripts/plan_manager.py")
  local jget=(env -u VIRTUAL_ENV uv run "${skill}/scripts/plan_manager.py" json-get)
  local rc=0

  pushd "${proj}" >/dev/null

  # Committed tier carries the LAYOUT; local tier overrides ONE unrelated key.
  # Under the old whole-file first-match this masked plans-root entirely.
  printf '%s' '{"plans-root":"Notes/plans","incubator-root":"Notes/Inc","landing-strategy":"main"}' \
    > .yf/plan/config.json
  printf '%s' '{"landing-strategy":"feature-branch"}' > .yf/plan/config.local.json
  printf '%s' '{"validate-cmd":"legacy-only-cmd"}'   > .yf-plan.local.json

  echo ">> [config] init under a committed non-default plans-root"
  local pj plan_dir
  pj="$("${PM[@]}" init "smoke: configurable roots")" || rc=1
  plan_dir="$(printf '%s' "${pj}" | "${jget[@]}" plan_dir)"

  case "${plan_dir}" in
    Notes/plans/*) _ok "committed tier drove plans-root: ${plan_dir}" ;;
    *)             _bad "plans-root ignored — plan landed at ${plan_dir}"; rc=1 ;;
  esac
  if [ -d "${plan_dir}" ]; then _ok "bundle created under the configured root"
  else _bad "bundle missing at ${plan_dir}"; rc=1; fi
  if [ -d docs/plans ]; then _bad "default docs/plans was created despite config"; rc=1
  else _ok "default docs/plans NOT created"; fi

  # The assertions above ARE the merge proof, and this is the whole point of the
  # phase: a `.yf/plan/config.local.json` exists and sets only `landing-strategy`.
  # Under the OLD whole-file first-match-wins reader that local file would have won
  # outright, `plans-root` would never have been seen, and the plan would have landed
  # in the default `docs/plans`. It landed in `Notes/plans`, so the committed tier
  # was merged rather than masked. `landing-strategy` / `validate-cmd` have no CLI
  # verbs of their own (they are internal resolvers), so per-key precedence for those
  # keys is asserted in Tier-1 (`test_config_tiers.py`) rather than re-probed here.

  # State dir is the short name, and a pre-#100 full-name dir migrates.
  mkdir -p .yf/yf-plan && printf '%s' '{"plan":"legacy"}' > .yf/yf-plan/landing.lock
  "${PM[@]}" list >/dev/null 2>&1 || true
  if [ -f .yf/plan/landing.lock ] && [ ! -d .yf/yf-plan ]; then
    _ok "pre-#100 .yf/yf-plan state migrated to short-name .yf/plan"
  else
    _bad "state migration did not run (.yf/plan/landing.lock or leftover .yf/yf-plan)"; rc=1
  fi

  popd >/dev/null
  [ "${rc}" -eq 0 ] && echo ">> CONFIG-TIER PASS" || echo ">> CONFIG-TIER FAIL" >&2
  return "${rc}"
}

# ------------------------------------------------------------------- main ------
case "${1:-gate}" in
  setup)  shift; cmd_setup  "${1:-}" ;;
  drive)  shift; cmd_drive  "${1:-}" ;;
  verify) shift; cmd_verify "${1:-}" ;;
  config) shift; cmd_config "${1:-}" ;;
  gate)   shift; cmd_gate   "${1:-}" ;;
  all)    shift; cmd_setup "${1:-}"
          echo ">> 'all' completed setup only; run 'smoke.sh verify' after the walk." ;;
  *)      echo "usage: smoke.sh {gate|setup|drive|verify|config|all} [arg]" >&2; exit 2 ;;
esac
