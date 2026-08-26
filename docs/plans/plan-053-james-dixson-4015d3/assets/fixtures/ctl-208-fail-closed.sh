#!/usr/bin/env bash
# ctl-208-fail-closed — the NARROW fail-closed STATUS_SEVERITY (REQ-DATA-072 / #208).
#
# A THIN WRAPPER (pass-4 C53: redcheck runs `bash "$fx"`, so a bare pytest/script arm is not
# harness-runnable). The assertions live in `_shared/test_doc_lint.py` §20.
#
# TWO ARMS, ONLY ARM 1 CARRIES THE RED (pass-1 C12):
#   ARM 1  a PRESENT but UNRECOGNISED status flips PASS -> FAIL.
#   ARM 2  a NULL-`bundle_status` document is UNCHANGED. INVARIANT across the fix, so
#          redcheck classifies it a NEGATIVE control and this RED record does not certify it.
#          Its value is regression protection at 7.1, not evidence here. Without it the naive
#          one-liner ships and reddens 31 documents plus this repo's own FAST tier.
#
# IT GRADES ONLY ITS OWN ARMS, NOT THE WHOLE FILE'S EXIT CODE. R8 records two pre-existing
# `test_doc_lint.py` failures on `main`, identical on base and fixed. Keying this control on
# the suite's exit code would let an unrelated pre-existing failure hold it red forever, and
# would let 7.1 claim to have fixed something it did not touch. So the arms are matched by
# name in the output.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
SUITE="${YF_TREE}/_shared/test_doc_lint.py"

[ -f "${SUITE}" ] || { echo "ctl-208-fc: HARNESS — no suite at ${SUITE}" >&2; exit 2; }

out="$(cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${SUITE}" 2>&1)"; rc=$?
if printf '%s' "${out}" | grep -qE 'ModuleNotFoundError|Traceback \(most recent|error: Failed to spawn'; then
  echo "ctl-208-fc: HARNESS — the suite could not run:" >&2
  printf '%s\n' "${out}" | tail -20 | sed 's/^/ctl-208-fc:   /' >&2
  exit 2
fi

# The four §20 assertion names, matched verbatim.
ARMS=(
  "ARM 0 (baseline): a \`drafting\` plan with placeholders has W findings and 0 errors"
  "ARM 1: a PRESENT but UNRECOGNISED status fails CLOSED (W promoted to E)"
  "ARM 2 (invariant): bundle_status is genuinely None for the null fixture"
  "ARM 2 (invariant): the null fixture really carries a \`W\` finding"
  "ARM 2 (invariant): a NULL-\`bundle_status\` document is UNCHANGED (0 errors)"
  "the None and present-but-unrecognised branches are DISTINGUISHABLE"
)

bad=()
for arm in "${ARMS[@]}"; do
  if printf '%s\n' "${out}" | grep -qF "FAIL ${arm}"; then
    bad+=("${arm}")
  elif ! printf '%s\n' "${out}" | grep -qF "ok   ${arm}"; then
    # Neither ok nor FAIL: the assertion is GONE. A control whose assertions can silently
    # vanish is a control that certifies nothing — which is this plan's whole subject.
    echo "ctl-208-fc: HARNESS — assertion not found in the suite output: ${arm}" >&2
    exit 2
  fi
done

if [ "${#bad[@]}" -gt 0 ]; then
  echo "ctl-208-fc: ${#bad[@]} of ${#ARMS[@]} assertion(s) failing:" >&2
  for b in "${bad[@]}"; do echo "ctl-208-fc:   FAIL ${b}" >&2; done
  exit 1
fi
echo "ctl-208-fc: fail-closed is NARROW — unrecognised flips PASS->FAIL, null is unchanged, and the two branches are distinguishable"
