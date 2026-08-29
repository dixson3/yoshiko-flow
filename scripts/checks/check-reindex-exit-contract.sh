#!/usr/bin/env bash
# SC2 / REQ-OKF-011 — `reindex --check` returns DIFFERENT exit codes for a nonexistent path
# and a real index-less bundle.
#
# THE CRITERION IS A PAIR OF EXITS, NOT A SINGLE NON-ZERO (REQ-CLI-029(a)). "reindex exits
# non-zero on a bad path" is satisfied by the ENGINE BEING ABSENT — `uv run <missing>.py`
# itself exits 2, which is also the shipped `no-index` code. Asserting the two DIFFER is what
# distinguishes a correct engine from an absent one.
#
# WHY THE SPLIT MATTERS. Both states reached the same `if not idx.exists()` line, so a
# mistyped or moved bundle path reported `no-index` — indistinguishable from a real
# index-less bundle. Any driver that tolerates `no-index` (as a corpus sweep over a mixed
# corpus must, since most bundles have none) therefore read a TYPO as a benign skip and
# certified a corpus it never inspected.
#
# EXIT  0 the exits differ and carry the declared verdicts  ·  1 they do not  ·  2 could not run
CHECK_NAME=check-reindex-exit-contract
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need uv
OKF="${TREE}/_shared/okf.py"
[ -f "${OKF}" ] || ck_inconclusive "no _shared/okf.py at ${OKF}"
CK_RC=0

FIX="$(mktemp -d)"
trap 'rm -rf "${FIX}"' EXIT
# A REAL index-less bundle: it exists, it is a directory, it carries no index.md.
mkdir -p "${FIX}/real-bundle"
printf -- '---\ntype: Concept\n---\n# x\n' > "${FIX}/real-bundle/x.md"
# ...and a path that simply is not there.
MISSING="${FIX}/definitely-not-here"

run_reindex() { (cd "${TREE}" && uv run --with pyyaml "${OKF}" reindex "$1" --json >/dev/null 2>&1); echo $?; }

RC_MISSING="$(run_reindex "${MISSING}")"
RC_NOINDEX="$(run_reindex "${FIX}/real-bundle")"

# THE PAIR.
if [ "${RC_MISSING}" = "${RC_NOINDEX}" ]; then
  ck_fail "a nonexistent path and an index-less bundle BOTH exit ${RC_MISSING} — the two states are indistinguishable"
fi

# The declared codes, so a merely-different pair (e.g. a crash) cannot satisfy the criterion.
[ "${RC_MISSING}" = "3" ] || ck_fail "a nonexistent path must exit 3 (no-such-path), got ${RC_MISSING}"
[ "${RC_NOINDEX}" = "2" ] || ck_fail "an index-less bundle must exit 2 (no-index), got ${RC_NOINDEX}"

# The verdict strings agree with the codes — an exit code with the wrong verdict beside it
# would pass the arithmetic above while reporting nonsense to a human reader.
V_MISSING="$( (cd "${TREE}" && uv run --with pyyaml "${OKF}" reindex "${MISSING}" --json 2>/dev/null) | tr -d ' \n' )"
case "${V_MISSING}" in *'"verdict":"no-such-path"'*) : ;; *) ck_fail "no-such-path verdict string absent from the JSON" ;; esac

ck_done "no-such-path (3) and no-index (2) are distinct verdicts with distinct exits"
