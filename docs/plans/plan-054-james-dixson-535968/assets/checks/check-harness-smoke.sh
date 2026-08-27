#!/usr/bin/env bash
# check-harness-smoke.sh — SC18 / plan-054 Issue 2.5. The HEADLESS LIVE REGRESSION.
#
# WHY THIS EXISTS (D-4). Every mechanical multi-harness assertion in this repo is a
# filesystem-PATH assertion under a fake HOME, and `Command::new("pi")` appears nowhere. That
# gap is precisely what let the SKILL_DIR defect ship: `yf` installed to `~/.pi/agent/skills`
# and `~/.config/opencode/skills`, the embedded resolver searched neither, and the install
# reported success. Nothing in the mechanical tier could see it, because nothing in the
# mechanical tier ever STARTED A HARNESS.
#
# EXP-002 measured both harnesses as headless-drivable — `pi -p` and `opencode run` — so this
# is Tier-2 automation, not a manual checklist a human is asked to remember.
#
# THREE ASSERTIONS PER HARNESS, each chosen because it fails differently:
#   (1) a yf SKILL NAME is listed        — the skill bundle was found and parsed;
#   (2) a RULE-BLOCK-ONLY FACT is quoted — the always-loaded rules reached context. This must
#       be a string that appears ONLY in the rule block, or the harness could produce it from
#       general knowledge and the assertion would prove nothing;
#   (3) `plan_manager.py list --json-output` PARSES — a script resolved through SKILL_DIR and
#       ran, which is the half the resolver defect broke.
#
# EXIT  0 both harnesses pass  ·  1 an assertion failed  ·  2 could not run (harness absent)
#
# AN ABSENT HARNESS IS INCONCLUSIVE, NEVER A PASS. SC18 gates a tag push that auto-publishes
# the website, and a smoke that silently skips is a green that means nothing.
#
# USAGE: check-harness-smoke.sh [verify-all|pi|opencode]
set -uo pipefail

CHECK_NAME=check-harness-smoke
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAN_DIR="$(cd "${HERE}/../.." && pwd)"
TRANSCRIPT="${PLAN_DIR}/assets/harness-smoke-transcript.md"
MODE="${1:-verify-all}"

ck_inconclusive() { echo "${CHECK_NAME}: INCONCLUSIVE — $*" >&2; exit 2; }
RC=0
fail() { echo "${CHECK_NAME}: FAIL — $*" >&2; RC=1; }

# A fact that appears ONLY in the yf rule aggregate. Chosen deliberately: a model cannot
# produce this from general knowledge, so quoting it back is evidence the block was loaded.
RULE_FACT="yf-plan"
RULE_PROBE='Answer ONLY from your always-loaded instructions, in one line: which skill does the Planning Protocol say ALL planning uses? If your instructions do not say, answer exactly: NOT-IN-CONTEXT.'

_record() { printf '%s\n' "$*" >> "${TRANSCRIPT}"; }

_probe_pi() {
  command -v pi >/dev/null 2>&1 || { echo "pi-absent"; return 2; }
  pi -p "$1" 2>&1
}
_probe_opencode() {
  command -v opencode >/dev/null 2>&1 || { echo "opencode-absent"; return 2; }
  opencode run "$1" 2>&1
}

_smoke_one() {
  # _smoke_one <harness>
  local h="$1" out rc tree
  command -v "${h}" >/dev/null 2>&1 || { fail "${h} is not on PATH — cannot run the live regression"; return 2; }

  # WHICH TREE DID IT READ? SC35 requires the transcript to record this, because EXP-002
  # measured BOTH harnesses resolving to the claude-code copy while reporting success — a pass
  # that does not name the tree cannot be distinguished from that exact failure.
  # RESOLVE WITH THE TREE-UNDER-TEST'S BINARY, not whatever `yf` happens to be on PATH.
  # Measured: the PATH copy is the PRE-RELEASE binary with no `skill-dir` subcommand, so this
  # recorded `<unresolved>` for every harness — turning SC35's whole point (name the tree) into
  # a placeholder. A transcript that records `<unresolved>` satisfies nothing.
  local yf_bin="${YF_TREE:-.}/target/debug/yf"
  [ -x "${yf_bin}" ] || yf_bin="yf"
  tree="$("${yf_bin}" skill-dir yf-plan 2>/dev/null || true)"
  [ -n "${tree}" ] || tree="<unresolved>"
  _record ""
  _record "### ${h}"
  _record ""
  _record "- resolved tree: \`${tree}\`"
  _record "- \`$(command -v "${h}")\`"

  # (1) a yf skill name is listed.
  out="$("_probe_${h}" 'List the names of the skills available to you, comma separated. Output only the list.')"
  _record ""
  _record '```'
  _record "\$ ${h} <list-skills>"
  _record "${out}"
  _record '```'
  printf '%s' "${out}" | grep -qiE 'yf-(plan|research|okf|beads)' \
    || fail "${h}: no yf skill name was listed — the skill bundle was not found or not parsed"

  # (2) a rule-block-only fact is quoted back.
  out="$("_probe_${h}" "${RULE_PROBE}")"
  _record ""
  _record '```'
  _record "\$ ${h} <rule-block probe>"
  _record "${out}"
  _record '```'
  if printf '%s' "${out}" | grep -q 'NOT-IN-CONTEXT'; then
    fail "${h}: the always-loaded rule block did NOT reach context (harness answered NOT-IN-CONTEXT)"
  elif ! printf '%s' "${out}" | grep -qF "${RULE_FACT}"; then
    fail "${h}: the rule-block-only fact '${RULE_FACT}' was not quoted back"
  fi

  # (3) a SKILL_DIR-resolved script actually runs and its JSON parses.
  out="$("_probe_${h}" 'Resolve SKILL_DIR for yf-plan exactly as your instructions say, then run `uv run ${SKILL_DIR}/scripts/plan_manager.py list --json-output` and paste its raw output only.')"
  _record ""
  _record '```'
  _record "\$ ${h} <plan_manager list>"
  _record "${out}"
  _record '```'
  # FIND A CANDIDATE THAT ACTUALLY PARSES, rather than one greedy span.
  #
  # A single `re.search(r"[\[{].*[\]}]", …, re.S)` starts at the FIRST `{` in the output — and
  # the harness echoes the resolver block, which contains `${SKILL_DIR:-}`. So the span began
  # inside a shell parameter expansion and could never parse, and the check reported "a script
  # resolved through SKILL_DIR did not run" while the JSON sat complete further down. That is a
  # false FAIL on the single assertion SC18 gates an auto-publishing tag with.
  if ! printf '%s' "${out}" | python3 -c '
import json, sys
t = sys.stdin.read()
for i, ch in enumerate(t):
    if ch not in "[{":
        continue
    for j in range(len(t), i, -1):
        if t[j-1] not in "]}":
            continue
        try:
            json.loads(t[i:j])
        except Exception:
            continue
        print("PARSES"); raise SystemExit(0)
raise SystemExit(1)
' 2>/dev/null | grep -q PARSES; then
    fail "${h}: plan_manager.py list --json-output did not produce parseable JSON — a script resolved through SKILL_DIR did not run"
  fi
  return 0
}

case "${MODE}" in
  pi|opencode) targets="${MODE}" ;;
  verify-all)  targets="pi opencode" ;;
  *) ck_inconclusive "unknown mode '${MODE}' (expected verify-all | pi | opencode)" ;;
esac

missing=""
for h in ${targets}; do
  command -v "${h}" >/dev/null 2>&1 || missing="${missing} ${h}"
done
[ -z "${missing}" ] || ck_inconclusive "harness(es) not installed:${missing} — an absent harness is INCONCLUSIVE, never a pass; SC18 gates an irreversible, auto-publishing tag"

{
  echo "---"
  echo "type: Reference"
  echo "okf_spec: OKF-PLAN"
  echo "id: harness-smoke-transcript"
  echo "description: Live headless regression transcript (plan-054 Issue 2.5 / SC18, SC35)"
  echo "---"
  echo
  echo "# Harness smoke transcript"
  echo
  echo "Generated by \`assets/checks/check-harness-smoke.sh\` on $(date -u +%Y-%m-%dT%H:%M:%SZ)."
  echo
  echo "Each harness section records **which tree it read**, because EXP-002 measured both"
  echo "resolving to the claude-code copy while reporting success — a pass that does not name"
  echo "the tree is indistinguishable from that failure (SC35)."
} > "${TRANSCRIPT}"

for h in ${targets}; do _smoke_one "${h}"; done

if [ "${RC}" -eq 0 ]; then
  echo "${CHECK_NAME}: live regression passed for: ${targets}"
  _record ""
  _record "**Verdict: PASS** for ${targets}."
else
  _record ""
  _record "**Verdict: FAIL.**"
fi
exit "${RC}"
