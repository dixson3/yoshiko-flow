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

# --- ARM 4: GITIGNORE AWARENESS, BOTH SIDES (REQ-OKF-CHK-004 as corrected, #294) -----
# The contract check had NO gitignore arm until plan-064 Issue 1.6, which is why #294 could
# sit open against a requirement that already mandated the behaviour: nothing here looked.
#
# THE ARM IS TWO-SIDED, and that is the whole of its value. A one-sided arm ("residue does
# not cause drift") is satisfied by a driver that ignores every UNTRACKED path — which is the
# fix #294 proposed, and which would blind the FAST tier at exactly the moment it fires (on
# edit, when a newly authored member is untracked BY DEFINITION). So:
#
#   4a  IGNORED residue dropped into a conformant bundle must NOT turn the corpus red.
#   4b  An UNTRACKED-but-NOT-IGNORED member must STILL turn it red — it is a real member,
#       missing from the index, and that is a genuine drift finding.
#
# Passing 4a while failing 4b is precisely the wrong fix passing a weak test.
printf '__pycache__/\n*.pyc\n' > "${FIX}/.gitignore"
mkdir -p "${FIX}/corpus/bundle-a/__pycache__"
: > "${FIX}/corpus/bundle-a/__pycache__/okf.cpython-314.pyc"
: > "${FIX}/corpus/bundle-a/stale.pyc"

RC_IGNORED="$( (cd "${FIX}" && uv run "${DRIVER}" --root 'corpus/*' --min-roots 1 >/dev/null 2>&1); echo $? )"
if [ "${RC_IGNORED}" != "0" ]; then
  ck_fail "arm 4a: IGNORED build residue turned the corpus red (exit ${RC_IGNORED}) — the walk is not gitignore-aware (#294)"
fi

# 4b — the other side. A real, untracked, NOT-ignored member is absent from the index, so the
# driver MUST report drift. NON-VACUITY for 4a: without this, 4a is satisfied by a driver that
# suppresses everything untracked.
: > "${FIX}/corpus/bundle-a/scratch-notes.md"
RC_UNTRACKED="$( (cd "${FIX}" && uv run "${DRIVER}" --root 'corpus/*' --min-roots 1 >/dev/null 2>&1); echo $? )"
if [ "${RC_UNTRACKED}" = "0" ]; then
  ck_fail "arm 4b: an UNTRACKED-but-NOT-IGNORED member did not register as drift — the predicate is tracked-ness, not ignored-ness, which blinds the on-edit FAST tier"
fi
rm -f "${FIX}/corpus/bundle-a/scratch-notes.md"

ck_done "synthetic-clean-corpus=${RC_CORPUS}, nonexistent-root=${RC_BADROOT}, impossible-floor=${RC_FLOOR}, ignored-residue=${RC_IGNORED}, untracked-member=${RC_UNTRACKED} — all distinguishable, and arm 4 is two-sided"
