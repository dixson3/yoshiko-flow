#!/usr/bin/env bash
# ctl-208-vocabulary-sites — `abandoned` reaches EVERY site, and NONE of the schema lists (#208).
#
# A FIXTURE per redcheck.sh's definition: exits 0 iff the asserted behaviour holds.
#
# THE FIXTURE ENUMERATES AND THE PROSE DOES NOT (pass-4 C52). The old count literal moved
# twice and survived three deletion attempts, so no count is recorded anywhere — here or in
# plan.md. This file IS the enumeration. Adding a site means adding an assertion.
#
# WHY THIS CONTROL EXISTS AT ALL. Issue 5.1 previously had NO criterion (pass-2 C27), which is
# how a twelve-file vocabulary edit could have landed PARTIAL and still reported green.
#
# ═══ THE PHASE MODEL LINE IS ITS OWN ASSERTION, NOT A FILE-LEVEL ONE ═══════════════════════
# `SKILL.md`'s `Status values:` line is the DECLARED SOURCE OF TRUTH for the `e-status-values`
# drift edge — SKILL.md says so in as many words. A file-level check ("`abandoned` appears
# somewhere in SKILL.md") PASSES while that line is still nine-valued, because the word will
# certainly appear in the parked-nudge prose nearby. That is the scope-too-narrow failure this
# plan's review hit five times, and it is why assertion 1 greps THE LINE and counts what is ON
# it rather than searching the file.
#
# It is also, right now, a live instance of #165's class inside this plan: REQ-STATUS-001
# already reads "Exactly 10" and names that grep as its Verification, so until Issue 5.1 lands
# a shipped requirement's own stated verification is FALSE. That is the expected SPEC-first
# window — nothing gates on it today — and this control is what closes it.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
cd "${YF_TREE}" || { echo "ctl-208-vocab: HARNESS — cannot cd to ${YF_TREE}" >&2; exit 2; }

bad=()

_need_file() {  # _need_file <path> -> 0 if present, else record a HARNESS failure
  [ -f "$1" ] || { echo "ctl-208-vocab: HARNESS — missing $1" >&2; exit 2; }
}

_present() {  # _present <label> <path> <grep-args...>
  local label="$1" path="$2"; shift 2
  _need_file "${path}"
  if ! grep -qE "$@" "${path}"; then
    bad+=("${label}: \`abandoned\` has not reached ${path}")
  fi
}

# ── 1. THE PHASE MODEL LINE ITSELF ────────────────────────────────────────────────────────
_need_file skills/yf-plan/SKILL.md
LINE="$(grep -m1 '^Status values:' skills/yf-plan/SKILL.md || true)"
if [ -z "${LINE}" ]; then
  bad+=("SITE 1 (Phase Model line): no \`Status values:\` line in skills/yf-plan/SKILL.md at \
all. REQ-STATUS-001's Verification greps for exactly this line.")
else
  # Count the pipe-separated values ON THE LINE.
  N="$(printf '%s' "${LINE}" | sed 's/^Status values: *//' | tr '|' '\n' | grep -c '[a-z]')"
  if [ "${N}" -ne 10 ]; then
    bad+=("SITE 1 (Phase Model line, THE DECLARED SOURCE OF TRUTH for e-status-values): the \
\`Status values:\` line enumerates ${N} values, expected 10. REQ-STATUS-001 reads 'Exactly 10' \
and names a grep of THIS LINE as its Verification, so a shipped requirement's stated \
verification is false while this holds. Line:
      ${LINE}")
  fi
  if ! printf '%s' "${LINE}" | grep -q 'abandoned'; then
    bad+=("SITE 1 (Phase Model line): the line does not carry \`abandoned\`. A file-level \
check would pass here — the word appears elsewhere in SKILL.md — which is exactly why this \
assertion greps THE LINE.")
  fi
fi

# ── 2. SKILL.md's parked nudge distinguishes abandoned from parked ────────────────────────
# `_is_parked` stays `approved`-only, because the nudge's text is literally "run /yf-plan
# execute" — exactly wrong for a plan that was deliberately stopped.
if ! grep -qE 'abandoned' skills/yf-plan/SKILL.md; then
  bad+=("SITE 2 (parked nudge / SKILL.md body): SKILL.md never mentions \`abandoned\` outside \
the status line.")
fi

# ── 3. plan_manager.py ────────────────────────────────────────────────────────────────────
_present "SITE 3 (plan_manager.py)" skills/yf-plan/scripts/plan_manager.py 'abandoned'
if ! grep -qE 'ABANDONED' skills/yf-plan/scripts/plan_manager.py; then
  bad+=("SITE 3 (plan_manager.py): \`list\` does not render an ⏹ ABANDONED tag.")
fi
# `_is_parked` MUST stay approved-only — an abandoned plan must never be nudged to execute.
if sed -n "/^def _is_parked/,/^@/p" skills/yf-plan/scripts/plan_manager.py \
   | grep -qE 'abandoned'; then
  bad+=("SITE 3 (plan_manager.py): \`_is_parked\` now references \`abandoned\`. It must stay \
\`approved\`-only — the parked nudge's text is literally 'run /yf-plan execute', which is \
precisely wrong for a plan that was deliberately stopped.")
fi

# ── 4. doc_lint.py — the STATUS_SEVERITY profile ──────────────────────────────────────────
_present "SITE 4 (_shared/doc_lint.py)" _shared/doc_lint.py '^ *"abandoned":'
if ! sed -n '/^STATUS_SEVERITY = {/,/^}/p' _shared/doc_lint.py \
   | grep -qE '"abandoned": *\{ *WARN: *REPORT, *ERROR: *REPORT *\}'; then
  bad+=("SITE 4 (_shared/doc_lint.py): \`abandoned\` is not mapped to {WARN: REPORT, ERROR: \
REPORT} inside STATUS_SEVERITY. It is terminal, so a finding on it is a report about a \
record, never an actionable defect — and it must be listed EXPLICITLY rather than falling \
through a default, because an unmapped status is exactly what REQ-DATA-072's fail-closed \
treatment reddens.")
fi

# ── 5. THE THREE SCHEMA `statuses` LISTS — abandoned must be ABSENT ───────────────────────
# The exclusion is ASSERTED, not inherited by accident. A frozen bundle whose status is
# `abandoned` must not be re-linted into an error.
for t in _shared/document_types/plan.toml \
         _shared/document_types/upstream-triage.toml \
         _shared/document_types/plan-relations.toml; do
  _need_file "${t}"
  if grep -E '^statuses *=' "${t}" | grep -q 'abandoned'; then
    bad+=("SITE 5 (${t}): \`abandoned\` LEAKED into a schema \`statuses\` list. The exclusion \
is deliberate and is asserted here rather than inherited.")
  fi
done

# ── 6. yf-herdr — readiness must exclude abandoned ────────────────────────────────────────
_present "SITE 6 (skills/yf-herdr/SKILL.md)" skills/yf-herdr/SKILL.md 'abandoned'
_present "SITE 6 (skills/yf-herdr/SPEC.md)"  skills/yf-herdr/SPEC.md  'abandoned'

# ── 7. web/content — the four lifecycle surfaces ──────────────────────────────────────────
_present "SITE 7 (web workflows)"  web/content/pages/workflows.md      'abandoned'
_present "SITE 7 (web glossary)"   web/content/pages/glossary.md       'abandoned'
_present "SITE 7 (web yf-herdr)"   web/content/skills/yf-herdr.md      'abandoned'
_present "SITE 7 (phase-model.d2)" web/content/images/phase-model.d2   'abandoned'

if [ "${#bad[@]}" -gt 0 ]; then
  echo "ctl-208-vocab: ${#bad[@]} failure(s):" >&2
  for b in "${bad[@]}"; do echo "ctl-208-vocab:   ${b}" >&2; done
  exit 1
fi
echo "ctl-208-vocab: \`abandoned\` present at every enumerated site (Status values: line = 10) and absent from all three schema statuses lists"
