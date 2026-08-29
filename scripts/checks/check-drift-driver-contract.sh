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

# --- ARM 1: a SYNTHESISED CLEAN corpus ----------------------------------------------
# NOT the live corpus. SC3's claim is about the DRIVER's contract — "a nonexistent root is
# distinguishable from a CLEAN corpus" — and the live corpus is legitimately drifting for
# most of this plan's execution, which would make the two arms both exit 1 and the criterion
# false for a reason that has nothing to do with the driver. Corpus cleanliness is SC10's
# claim; conflating the two is the same two-properties-one-signal defect this plan is about.
FIX="$(mktemp -d)"
trap 'rm -rf "${FIX}"' EXIT
mkdir -p "${FIX}/corpus/bundle-a"
printf -- '---\ntype: Plan\nokf_spec: OKF-PLAN\n---\n# p\n' > "${FIX}/corpus/bundle-a/plan.md"
printf '# Log\n\n## 2026-08-28\n\n- scoping: f\n' > "${FIX}/corpus/bundle-a/log.md"
printf -- '---\nokf_version: 0.2\n---\n\n# bundle-a\n\n- [plan.md](plan.md) - The plan.\n' \
  > "${FIX}/corpus/bundle-a/index.md"
( cd "${FIX}" && git init -q . 2>/dev/null )

RC_CORPUS="$( (cd "${FIX}" && uv run "${DRIVER}" --root 'corpus/*' --min-roots 1 >/dev/null 2>&1); echo $? )"
if [ "${RC_CORPUS}" != "0" ]; then
  ck_fail "the driver reports a SYNTHESISED CLEAN corpus as ${RC_CORPUS}, not 0 — arm 2 below cannot be interpreted"
fi

# --- ARM 2: a root that does not exist ----------------------------------------------
# HARD ERROR, not a skip. The driver must refuse to demote a path it was explicitly told to
# enumerate and could not find.
RC_BADROOT="$( (cd "${FIX}" && uv run "${DRIVER}" --root 'definitely/not/a/real/root/*' --min-roots 0 >/dev/null 2>&1); echo $? )"

if [ "${RC_CORPUS}" = "${RC_BADROOT}" ]; then
  ck_fail "a nonexistent enumerated root and the real corpus BOTH exit ${RC_CORPUS} — a mistyped root is indistinguishable from a clean sweep"
fi
if [ "${RC_BADROOT}" = "0" ]; then
  ck_fail "a nonexistent enumerated root exits 0 — a typo reads as clean"
fi

# --- ARM 3: the empty-inspection floor (REQ-CLI-029(b)) -----------------------------
# A floor no run can trip is not a floor. Setting it above the corpus size must fail.
RC_FLOOR="$( (cd "${FIX}" && uv run "${DRIVER}" --root 'corpus/*' --min-roots 100000 >/dev/null 2>&1); echo $? )"
if [ "${RC_FLOOR}" = "0" ]; then
  ck_fail "--min-roots 100000 exited 0 — the floor does not bite, so 'clean' and 'not read' are the same observation"
fi

ck_done "synthetic-clean-corpus=${RC_CORPUS}, nonexistent-root=${RC_BADROOT}, impossible-floor=${RC_FLOOR} — the three are distinguishable"
