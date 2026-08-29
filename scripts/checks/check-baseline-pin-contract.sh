#!/usr/bin/env bash
# SC21 — the baseline-pin drift detector EXISTS, is READ-ONLY, and a SIMULATED NETWORK FAILURE
# yields a DIFFERENT EXIT from a clean check.
#
# --- WHY A PAIR OF EXITS, NOT A SINGLE ASSERTION (REQ-CLI-029(a)) -------------------------
# "the detector returns non-zero on a network failure" is satisfied by the detector being
# ABSENT: `bash <missing>` exits 127 and `uv run <missing>.py` exits 2. Asserting that the
# clean exit and the offline exit DIFFER is what distinguishes a detector that WORKS from one
# that is merely not there, because an absent detector returns the same code on both arms.
#
# --- WHY AN OFFLINE ARM IS INCONCLUSIVE, NOT A FAILURE ------------------------------------
# If the real network is down, the "clean" arm ALSO reports a network condition and the two
# arms agree for a reason that has nothing to do with the detector. That is a statement about
# the environment, so it exits 2. The detector's INCONCLUSIVE path existing at all is the
# point: an offline land must not be blocked by it.
#
# --- READ-ONLY IS ASSERTED, NOT ASSUMED ---------------------------------------------------
# The detector reports and proposes a human diff; it never rewrites the baseline. This check
# hashes `OKF-BASELINE.md` before and after both arms and requires it unchanged.
#
# THE OFFLINE ARM IS SIMULATED VIA `YF_OKF_BASELINE_URL`, an unreachable override. That is the
# detector's contract with this check: it fetches whatever that variable names when set.
#
# EXIT  0 the pin key is present, the detector exists, the two arms differ, nothing was written
#       1 the pin key is absent, the detector is absent, or the arms do not differ
#       2 could not run (no curl, the network is genuinely down)
CHECK_NAME=check-baseline-pin-contract
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need shasum

BASELINE="${TREE}/skills/yf-okf/spec/OKF-BASELINE.md"
DETECTOR="${TREE}/scripts/baseline-pin-drift.sh"
CK_RC=0

# (1) The pin key itself. A detector with nothing to compare against is not a pin.
if [ ! -f "${BASELINE}" ]; then
  ck_fail "no OKF-BASELINE.md at skills/yf-okf/spec/OKF-BASELINE.md"
  exit 1
fi
if grep -q '^okf_baseline_sha256:' "${BASELINE}"; then
  ck_pass "OKF-BASELINE.md carries an \`okf_baseline_sha256:\` pin"
else
  ck_fail "OKF-BASELINE.md carries no \`okf_baseline_sha256:\` key — a version label is not a pin (REQ-OKF-033)"
fi

# (2) The detector must EXIST. A missing detector reads FALSE here, never INCONCLUSIVE — that
# is R11's third rule, and 126/127 would make the absence invisible to the verdict arithmetic.
if [ ! -x "${DETECTOR}" ]; then
  ck_fail "no executable detector at scripts/baseline-pin-drift.sh — the criterion cannot hold without one"
  exit 1
fi

BEFORE="$(shasum -a 256 "${BASELINE}" | awk '{print $1}')"

# (3) ARM A — a clean check against the real upstream.
( cd "${TREE}" && bash "${DETECTOR}" >/dev/null 2>&1 )
CLEAN_RC=$?

# (4) ARM B — a SIMULATED network failure.
( cd "${TREE}" && YF_OKF_BASELINE_URL="https://127.0.0.1:1/definitely-not-there" \
    bash "${DETECTOR}" >/dev/null 2>&1 )
OFFLINE_RC=$?

AFTER="$(shasum -a 256 "${BASELINE}" | awk '{print $1}')"

echo "${CHECK_NAME}: clean arm -> ${CLEAN_RC} · simulated-offline arm -> ${OFFLINE_RC}"

# (5) READ-ONLY.
if [ "${BEFORE}" != "${AFTER}" ]; then
  ck_fail "the detector MUTATED OKF-BASELINE.md (${BEFORE} -> ${AFTER}) — it is specified read-only (REQ-OKF-033)"
fi

# (6) The environment guard, before the pair assertion. A genuinely offline machine makes both
# arms report the same network condition, which says nothing about the detector.
if [ "${CLEAN_RC}" -eq 2 ]; then
  ck_inconclusive "the clean arm returned 2 (INCONCLUSIVE) — the real network is unreachable, so the two arms cannot be distinguished for a reason that has nothing to do with the detector"
fi

# (7) THE PAIR. This is the assertion an absent detector cannot satisfy.
if [ "${CLEAN_RC}" -eq "${OFFLINE_RC}" ]; then
  ck_fail "both arms returned ${CLEAN_RC} — a simulated network failure must yield a DIFFERENT exit from a clean check, or the detector's absence would satisfy this criterion"
fi
if [ "${OFFLINE_RC}" -ne 2 ]; then
  ck_fail "the simulated-offline arm returned ${OFFLINE_RC}, expected 2 (INCONCLUSIVE) — a network failure is a statement about the instrument, never drift"
fi

ck_done "the pin is present, the detector is read-only, and clean(${CLEAN_RC}) differs from simulated-offline(${OFFLINE_RC})"
