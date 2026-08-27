#!/usr/bin/env bash
# SC14 — the website's formula count equals the number of *.formula.toml under skills/.
#
# The staged copies under .beads/formulas/ are EXCLUDED: preflight writes them on every run
# (REQ-YF-PRE-011), so counting them double-counts every formula and makes the number depend
# on whether a preflight has happened. The site currently asserts 3; five ship.
CHECK_NAME=check-formula-count
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
[ -d "${TREE}/skills" ] || ck_inconclusive "no skills/ under ${TREE}"
CK_RC=0

actual="$(find "${TREE}/skills" -name '*.formula.toml' -type f 2>/dev/null | grep -vc '/\.beads/' || true)"
actual="$(find "${TREE}/skills" -name '*.formula.toml' -type f 2>/dev/null | grep -v '/\.beads/' | grep -c . || true)"
[ "${actual:-0}" -gt 0 ] || ck_inconclusive "found no *.formula.toml under skills/ — a count check against zero certifies vacuously"

page="$(find "${TREE}/web" -name 'formulas.md' -type f 2>/dev/null | head -1)"
[ -n "${page}" ] || ck_inconclusive "could not locate the website's formulas.md under ${TREE}/web"

if ! grep -qE "\\b${actual}\\b" "${page}"; then
  ck_fail "${page#${TREE}/} does not state the shipped formula count (${actual})"
  printf '%s: counts it mentions: %s\n' "${CHECK_NAME}" \
    "$(grep -oE '\b(one|two|three|four|five|six|[0-9]+)\b' "${page}" | sort -u | tr '\n' ' ')" >&2
fi
ck_done "the website's formula count matches the ${actual} shipped formulas"
