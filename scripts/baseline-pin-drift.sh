#!/usr/bin/env bash
# baseline-pin-drift.sh — REQ-OKF-033. Read-only upstream-drift detector for the OKF baseline.
#
# Fetches the live upstream `SPEC.md`, hashes it, and compares against the
# `okf_baseline_sha256:` pin in `skills/yf-okf/spec/OKF-BASELINE.md`.
#
# WHY A CONTENT HASH AND NOT A VERSION LABEL. Upstream relocated, announced the old snapshot
# frozen, and then CHANGED v0.2 IN PLACE with no version bump — measured 2026-08-29, the live
# document adds a normative "explicit UTC offset" clause the vendored v0.2 snapshot does not
# carry, while still reading `Version 0.2`. A label-only pin would have detected NOTHING.
#
# READ-ONLY, DELIBERATELY. It reports and proposes a human diff; it never rewrites the
# baseline. Deciding what an upstream change MEANS for the yf layer is a judgement, not a
# transform — and D-9 keeps this project read-only upstream, so it files nothing either.
#
# EXIT  0 the live upstream matches the pin
#       1 DRIFT — the live upstream differs from the pin (reported, never auto-applied)
#       2 INCONCLUSIVE — could not fetch, no pin, no hasher. A NETWORK FAILURE IS 2, NEVER 1:
#         an unreachable upstream is a statement about the instrument, not about the baseline,
#         and an offline land must not be blocked by it.
#
# `YF_OKF_BASELINE_URL` overrides the fetch target. That override is this script's contract
# with `scripts/checks/check-baseline-pin-contract.sh`, which uses it to SIMULATE a network
# failure and assert the offline exit DIFFERS from the clean one — the pair of exits that an
# absent detector could not produce.
set -uo pipefail

NAME=baseline-pin-drift
TREE="${YF_TREE:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
BASELINE="${TREE}/skills/yf-okf/spec/OKF-BASELINE.md"
DEFAULT_URL="https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md"
URL="${YF_OKF_BASELINE_URL:-${DEFAULT_URL}}"

inconclusive() { echo "${NAME}: INCONCLUSIVE — $*" >&2; exit 2; }

command -v curl    >/dev/null 2>&1 || inconclusive "curl is not on PATH"
command -v shasum  >/dev/null 2>&1 || inconclusive "shasum is not on PATH"
[ -f "${BASELINE}" ] || inconclusive "no OKF-BASELINE.md at ${BASELINE}"

PIN="$(sed -n 's/^okf_baseline_sha256:[ \t]*//p' "${BASELINE}" | head -1)"
[ -n "${PIN}" ] || inconclusive "OKF-BASELINE.md carries no \`okf_baseline_sha256:\` pin — a version label is not a pin (REQ-OKF-033)"

TMP="$(mktemp)"
trap 'rm -f "${TMP}"' EXIT
if ! curl -sfL --max-time 30 "${URL}" -o "${TMP}" 2>/dev/null; then
  inconclusive "could not fetch ${URL} — the network is a property of the RUN, not of the baseline"
fi
[ -s "${TMP}" ] || inconclusive "fetched ${URL} but it was empty"

LIVE="$(shasum -a 256 "${TMP}" | awk '{print $1}')"
if [ "${LIVE}" = "${PIN}" ]; then
  echo "${NAME}: live upstream matches the pin (${PIN})"
  exit 0
fi

# REPORT AND PROPOSE. Never rewrite, never file.
cat >&2 <<EOF
${NAME}: DRIFT — the live upstream no longer matches the pinned baseline.
  url    ${URL}
  pinned ${PIN}
  live   ${LIVE}

This is REPORTED, not repaired. Upstream has already changed v0.2 in place once without a
version bump, so a differing hash says the document moved — it does not say what the change
MEANS for the yf layer, which is a judgement. Propose to a human:

  curl -sfL "${URL}" -o /tmp/okf-live.md
  diff -u docs/plans/plan-046-james-dixson-aabefa/references/okf-spec-v0.2.md /tmp/okf-live.md

Then, if the change is accepted, update \`okf_baseline_sha256:\` in
skills/yf-okf/spec/OKF-BASELINE.md and record what changed. Nothing is filed upstream (D-9).
EOF
exit 1
