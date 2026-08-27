#!/usr/bin/env bash
# ctl-901-opencode-read-layers — grades REQ-YF-TUNE-030 / plan-054 Issue 2.4.
#
# A PLAN-LOCAL control (reserved 9xx range): #121 covers pi's config axis, not this.
#
# ASSERTED BEHAVIOUR (post-fix): every harness profile carries `settings_read_layers`, and
# opencode's lists BOTH config files it actually reads with the HIGHER-PRECEDENCE `.jsonc`
# ahead of `.json`.
#
# THE DEFECT (EXP-003, which REFUTED the scoping hypothesis): opencode reads `opencode.json`
# AND `opencode.jsonc`, and `.jsonc` wins. `yf` knows about one file — `settings_filename` —
# and every audit-class consumer reads that one alone. So an audit's read set is NARROWER
# than the harness's own, and it will report a green over a higher-precedence layer it cannot
# see. Today's agreement between what yf writes and what opencode obeys is COINCIDENCE.
#
# WHAT EXP-003 ALSO REFUTED, recorded here because the wrong module is the expensive mistake:
# the fix is NOT in `drift.rs`, which never opens a harness config file at all. It lands in
# `profile.rs` (the field), `doctor/checks.rs` and `audit.rs` (the read-back).
#
# THE PROBE IS THE PROFILE, and deliberately so. The claim is about a DECLARED read set, which
# is a property of the profile data rather than of any one consumer's behaviour; checking it
# here grades the thing every consumer is required to read. The consumers' own use of it is
# graded by Issue 2.4's `#[test] opencode_read_layers_surface_shadowed_keys`.
#
# EXIT  0 the layers are declared, ordered  ·  1 they are not (the defect)  ·  2 could not run
set -uo pipefail

[ -n "${YF_TREE:-}" ] || { echo "ctl-901: INCONCLUSIVE — YF_TREE is not set" >&2; exit 2; }

PROFILE=""
for cand in \
  "${YF_TREE}/yf/src/cmd/harness/profiles/opencode.toml" \
  "${YF_TREE}/yf/profiles/opencode.toml"; do
  [ -f "${cand}" ] && { PROFILE="${cand}"; break; }
done
if [ -z "${PROFILE}" ]; then
  PROFILE="$(find "${YF_TREE}/yf" -name 'opencode.*' -path '*profile*' -type f 2>/dev/null | head -1)"
fi
[ -n "${PROFILE}" ] && [ -f "${PROFILE}" ] || {
  echo "ctl-901: INCONCLUSIVE — could not locate the opencode profile under ${YF_TREE}/yf" >&2; exit 2; }

if ! grep -q 'settings_read_layers' "${PROFILE}"; then
  echo "ctl-901: FAIL — the opencode profile declares no \`settings_read_layers\`." >&2
  echo "ctl-901: the audit read set is still the single write target, so a higher-precedence" >&2
  echo "ctl-901: opencode.jsonc shadows every key the audit just reported green." >&2
  echo "ctl-901: (profile: ${PROFILE})" >&2
  exit 1
fi

layers="$(grep -A4 'settings_read_layers' "${PROFILE}" | tr -d ' \n')"
case "${layers}" in
  *opencode.jsonc*opencode.json*) : ;;
  *)
    echo "ctl-901: FAIL — \`settings_read_layers\` does not list opencode.jsonc AHEAD of" >&2
    echo "ctl-901: opencode.json. The ORDER is the requirement: .jsonc has the HIGHER" >&2
    echo "ctl-901: precedence, so a read set that consults .json first reports the value the" >&2
    echo "ctl-901: harness does not obey." >&2
    exit 1 ;;
esac
echo "ctl-901: opencode declares settings_read_layers with .jsonc ahead of .json"
exit 0
