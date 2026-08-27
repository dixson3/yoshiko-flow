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

actual="$(find "${TREE}/skills" -name '*.formula.toml' -type f 2>/dev/null | grep -v '/\.beads/' | grep -c . || true)"
[ "${actual:-0}" -gt 0 ] || ck_inconclusive "found no *.formula.toml under skills/ — a count check against zero certifies vacuously"

page="$(find "${TREE}/web" -name 'formulas.md' -type f 2>/dev/null | head -1)"
[ -n "${page}" ] || ck_inconclusive "could not locate the website's formulas.md under ${TREE}/web"

# ACCEPT THE NUMERAL OR THE ENGLISH WORD. Prose correctly writes "five shipped formulas", not
# "5 shipped formulas", so a numeral-only check would demand the page be written badly to
# satisfy it. The count is what matters, not its spelling.
word=""
case "${actual}" in
  1) word=one ;;   2) word=two ;;   3) word=three ;; 4) word=four ;;  5) word=five ;;
  6) word=six ;;   7) word=seven ;; 8) word=eight ;; 9) word=nine ;; 10) word=ten ;;
esac
if ! grep -qE "\\b${actual}\\b" "${page}" && ! { [ -n "${word}" ] && grep -qiE "\\b${word}\\b" "${page}"; }; then
  ck_fail "${page#${TREE}/} does not state the shipped formula count (${actual})"
  printf '%s: counts it mentions: %s\n' "${CHECK_NAME}" \
    "$(grep -oE '\b(one|two|three|four|five|six|[0-9]+)\b' "${page}" | sort -u | tr '\n' ' ')" >&2
fi
ck_done "the website's formula count matches the ${actual} shipped formulas"
