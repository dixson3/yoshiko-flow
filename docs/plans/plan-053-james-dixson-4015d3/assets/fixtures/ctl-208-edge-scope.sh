#!/usr/bin/env bash
# ctl-208-edge-scope — `e-status-values` is NON-VACUOUS (#208 / D-6).
#
# A FIXTURE per redcheck.sh's definition: exits 0 iff the asserted behaviour holds.
#
# ══ WHY THIS IS A MANIFEST ASSERTION AND NOT A VERIFIER RUN ═══════════════════════════════
#
# There is NO RUNNABLE DRIFT VERIFIER to invoke (pass-1 C3). `skills/yf-drift-check/` ships no
# `scripts/` directory at all, and `CHANGE-VALIDATION.md`'s own header excludes yf-drift-check
# as a prose/LLM trigger rather than an executable recipe row. So the strongest MECHANICAL
# claim available is about the manifest's declared SCOPE, and this control says so rather than
# faking a verifier.
#
# ══ EXP-004'S PREMISE IS REFUTED. THE NAIVE FORM IS UNSATISFIABLE. ════════════════════════
#
# EXP-004 reported the edge vacuous because "no yf-plan agent file carries a status literal",
# making the target set EMPTY. Pass-2 C17 measured that FALSE: `agents/coordinator.md:238` and
# `agents/reconciler.md:64` both carry `complete`. The target set was never empty.
#
# The edge is weak for a DIFFERENT reason: the check is `field-set-subset`, and `complete` IS
# in the declared vocabulary — so the subset holds and the check passes. It cannot fail on
# anything the agent files actually contain.
#
# And the obvious repair — "every selected target contains a status literal" — is measurably
# UNSATISFIABLE: 2 of 23 agent files and 3 of 19 SKILL.md carry one, getting WORSE after the
# widening (6 of 33). It could never reach exit 0. So it is not the assertion.
#
# ══ WHAT THIS CONTROL ACTUALLY ASSERTS ════════════════════════════════════════════════════
#
# The property the edge is FOR: a status literal planted in a file that RESTATES the
# vocabulary must be somewhere the edge can SEE. Concretely — every real restatement site is
# inside the edge's declared TARGET-node glob set, and the §6 Trigger Scope routes that path
# to `e-status-values`.
#
# Today the target node is `agent` (`skills/*/agents/*.md`), which covers none of
# `plan_manager.py`, `_shared/doc_lint.py`, `skills/yf-herdr/**` or `web/content/**` — every
# one of which restates the vocabulary. Issue 5.4 REPLACES the target node with the real
# restatement set. That is one branch, chosen: widening §6 ALONE cannot fix the edge, because
# it makes the targets-carrying-a-status-literal ratio worse, not better.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
DC="${YF_TREE}/DRIFT-CHECK.md"

[ -f "${DC}" ] || { echo "ctl-208-edge: HARNESS — no DRIFT-CHECK.md at ${DC}" >&2; exit 2; }

# THE REAL RESTATEMENT SET: files that carry the status vocabulary and would silently drift.
# Enumerated, because no glob can decide "restates the vocabulary".
RESTATERS="skills/yf-plan/scripts/plan_manager.py
_shared/doc_lint.py
skills/yf-herdr/SKILL.md
web/content/pages/workflows.md"

bad=()

# ---- the edge must still exist, and its declared TARGET node must be recoverable ----------
ROW="$(grep -m1 '^| `e-status-values` |' "${DC}" || true)"
if [ -z "${ROW}" ]; then
  echo "ctl-208-edge: HARNESS — no \`e-status-values\` row in DRIFT-CHECK.md §2" >&2
  exit 2
fi
TARGETS="$(printf '%s' "${ROW}" | awk -F'|' '{gsub(/[` ]/,"",$4); print $4}')"
[ -n "${TARGETS}" ] || { echo "ctl-208-edge: HARNESS — could not parse the edge's target node" >&2; exit 2; }

# Resolve each declared target node id to its glob(s) from the §1 node table.
GLOBS=""
for node in $(printf '%s' "${TARGETS}" | tr ',+' '  '); do
  g="$(grep -m1 "^| \`${node}\` |" "${DC}" | awk -F'|' '{print $3}' \
       | sed 's/`//g; s/([^)]*)//g; s/^ *//; s/ *$//')"
  if [ -z "${g}" ]; then
    bad+=("the edge names target node \`${node}\`, which has NO row in the §1 Artifact Nodes \
table — a target that resolves to no glob cannot see anything.")
  fi
  GLOBS="${GLOBS}${g}
"
done

# ---- ASSERTION 1: every restatement site is inside the edge's declared target set ---------
while IFS= read -r f; do
  [ -n "${f}" ] || continue
  covered=0
  while IFS= read -r g; do
    [ -n "${g}" ] || continue
    # shellcheck disable=SC2254
    case "${f}" in ${g}) covered=1 ;; esac
  done <<< "${GLOBS}"
  if [ "${covered}" -eq 0 ]; then
    bad+=("ASSERTION 1: \`${f}\` RESTATES the status vocabulary but is NOT inside \
\`e-status-values\`' declared target set (nodes: ${TARGETS}; globs: $(printf '%s' "${GLOBS}" | tr '\n' ' ')). \
A status literal planted there is invisible to the edge — which is what makes the edge unable \
to fail on the sites that matter.")
  fi
done <<< "${RESTATERS}"

# ---- ASSERTION 2: §6 Trigger Scope routes each restatement path to the edge ---------------
# Coverage by the target GLOB is necessary but not sufficient: if no §6 row maps the changed
# path to `e-status-values`, editing it never fires the edge at all.
S6="$(sed -n '/^## 6\. Trigger Scope/,/^## 7\./p' "${DC}")"
while IFS= read -r f; do
  [ -n "${f}" ] || continue
  if ! printf '%s' "${S6}" | grep -F "e-status-values" | grep -qF "$(dirname "${f}")"; then
    if ! printf '%s' "${S6}" | grep -F "e-status-values" | grep -qF "${f}"; then
      bad+=("ASSERTION 2: no §6 Trigger Scope row maps \`${f}\` to \`e-status-values\`, so \
editing it never fires the edge. Coverage by the target glob is necessary but NOT sufficient.")
    fi
  fi
done <<< "${RESTATERS}"

# ---- ASSERTION 3: the target node is no longer ONLY `agent` -------------------------------
# The one-branch repair D-6 mandates. Stated separately so the RED names the decision, not
# just its symptom.
if [ "${TARGETS}" = "agent" ]; then
  bad+=("ASSERTION 3: \`e-status-values\`' target node is still ONLY \`agent\` \
(\`skills/*/agents/*.md\`). Issue 5.4 REPLACES it with the real restatement set. Widening §6 \
alone is NOT the fix — measured, it makes the targets-carrying-a-status-literal ratio worse \
(2/23 agent files and 3/19 SKILL.md, going to 6/33 after widening), so it can never reach \
exit 0.")
fi

if [ "${#bad[@]}" -gt 0 ]; then
  echo "ctl-208-edge: ${#bad[@]} failure(s):" >&2
  for b in "${bad[@]}"; do echo "ctl-208-edge:   ${b}" >&2; done
  exit 1
fi
echo "ctl-208-edge: every status-vocabulary restatement site is inside e-status-values' declared target set AND is routed to it by §6"
