#!/usr/bin/env bash
# SC3 / REQ-OKF-CHK-004 — the corpus driver returns a DIFFERENT exit for a nonexistent
# enumerated root than for a clean corpus, so a mistyped path can never be read as clean.
#
# THIS IS THE CONSUMER HALF OF REQ-OKF-011's NEW `no-such-path`. Splitting the engine's exit
# codes buys nothing if the driver above it folds them back together — and the fold is the
# natural thing to write, because a corpus sweep MUST tolerate `no-index` (most bundles have
# none). A driver that tolerates `no-index` and cannot distinguish `no-such-path` reads a typo
# as a benign skip and certifies a corpus it never inspected.
#
# THE CRITERION IS A PAIR OF EXITS, NEVER A SINGLE NON-ZERO (REQ-CLI-029(a)). "the driver
# exits non-zero on a bad root" is satisfied by the driver BEING ABSENT — `uv run
# <missing>.py` itself exits 2.
#
# THE `--min-roots` FLOOR IS ALSO EXERCISED, because it is the other half of the same
# property: an enumerator that found nothing must not report clean.
#
# EXIT  0 the exits differ and the floor bites  ·  1 they do not  ·  2 could not run
CHECK_NAME=check-drift-driver-contract
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need uv
DRIVER="${TREE}/scripts/checks/check_okf_index_drift.py"
[ -f "${DRIVER}" ] || ck_inconclusive "no check_okf_index_drift.py at ${DRIVER} (Issue 3.1 has not landed)"
CK_RC=0

run_driver() { (cd "${TREE}" && uv run "${DRIVER}" "$@" >/dev/null 2>&1); echo $?; }

# --- ARM 1: the corpus as it stands -------------------------------------------------
RC_CORPUS="$(run_driver --min-roots 1)"

# --- ARM 2: a root that does not exist ----------------------------------------------
# HARD ERROR, not a skip. The driver must refuse to demote a path it was explicitly told to
# enumerate and could not find.
RC_BADROOT="$(run_driver --root 'definitely/not/a/real/root/*' --min-roots 0)"

if [ "${RC_CORPUS}" = "${RC_BADROOT}" ]; then
  ck_fail "a nonexistent enumerated root and the real corpus BOTH exit ${RC_CORPUS} — a mistyped root is indistinguishable from a clean sweep"
fi
if [ "${RC_BADROOT}" = "0" ]; then
  ck_fail "a nonexistent enumerated root exits 0 — a typo reads as clean"
fi

# --- ARM 3: the empty-inspection floor (REQ-CLI-029(b)) -----------------------------
# A floor no run can trip is not a floor. Setting it above the corpus size must fail.
RC_FLOOR="$(run_driver --min-roots 100000)"
if [ "${RC_FLOOR}" = "0" ]; then
  ck_fail "--min-roots 100000 exited 0 — the floor does not bite, so 'clean' and 'not read' are the same observation"
fi

ck_done "corpus=${RC_CORPUS}, nonexistent-root=${RC_BADROOT}, impossible-floor=${RC_FLOOR} — the three are distinguishable"
