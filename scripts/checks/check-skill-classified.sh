#!/usr/bin/env bash
# SC19b — a skill's `SKILL.md` is SELECTED by the document linter's classifier.
#
# ASSERT THE `class` VALUE, NEVER THE CLASSIFY EXIT CODE. The classifier's exit vocabulary is
# `0 lintable · 1 not lintable · 2 could not run`, and `lintable` covers BOTH `selected` and
# `empty` — so an EMPTY `SKILL.md` also exits 0. A check reading the exit code alone would
# certify a skill whose SKILL.md is a zero-byte file, which is precisely the thing this
# criterion exists to notice.
#
# The two non-lintable classes share exit 1 and are DIFFERENT FACTS: `not-selected` (no schema
# claims the path) and `no-such-path` (the file is not there). This check reports them
# separately for the same reason the classifier does.
#
# EXIT  0 the skill's SKILL.md classifies as `selected`
#       1 it does not (`not-selected`, `empty`, or `no-such-path`)
#       2 could not run (no linter, unparseable output)
CHECK_NAME=check-skill-classified
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

SKILL="${1:-}"
[ -n "${SKILL}" ] || ck_inconclusive "usage: ${CHECK_NAME} <skill-name>"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need uv
ck_need python3

LINTER="${TREE}/_shared/doc_lint.py"
[ -f "${LINTER}" ] || ck_inconclusive "no doc_lint.py at ${LINTER}"

REL="skills/${SKILL}/SKILL.md"
OUT="$(cd "${TREE}" && uv run "${LINTER}" --classify --path "${REL}" --json 2>/dev/null)" \
  || true
[ -n "${OUT}" ] || ck_inconclusive "the classifier produced no output for ${REL}"

CLASS="$(printf '%s' "${OUT}" | python3 -c 'import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(3)
print(d.get("class", ""))' 2>/dev/null)" || ck_inconclusive "classifier output is not JSON"
[ -n "${CLASS}" ] || ck_inconclusive "classifier output carries no `class` key"

CK_RC=0
case "${CLASS}" in
  selected)
    ck_pass "${REL} classifies as \`selected\`"
    ;;
  empty)
    ck_fail "${REL} classifies as \`empty\` — the classifier exits 0 on this, which is why this check reads the class and not the code"
    ;;
  not-selected)
    ck_fail "${REL} classifies as \`not-selected\` — no document-type schema claims it, so nothing lints it"
    ;;
  no-such-path)
    ck_fail "${REL} does not exist (class \`no-such-path\`) — a caller bug, reported separately from an ordinary skip"
    ;;
  *)
    ck_inconclusive "unrecognised class \`${CLASS}\` — the classifier's vocabulary changed under this check"
    ;;
esac

exit "${CK_RC}"
