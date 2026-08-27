#!/usr/bin/env bash
# SC1 — every new REQ this plan lands is in SPEC.md, marked (testable), and named by a tagged test.
#
# THE IDS ARE NAMED EXPLICITLY, and that is deliberate: a check that merely counted REQs, or
# asserted "coverage.rs passes", would be green on today's tree. Neither the portability audit
# nor bare `coverage.rs` measures this — `coverage.rs` proves a test NAMES a REQ id and has no
# temporal dimension at all, so it cannot tell this plan's ids from any other plan's.
CHECK_NAME=check-req-coverage
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
SPEC="${TREE}/SPEC.md"
[ -f "${SPEC}" ] || ck_inconclusive "no SPEC.md at ${SPEC}"
CK_RC=0

# The testable ids from Issues 0.2/0.3. REQ-YF-EMBED-006 is a decision-of-record with no
# (testable) marker by design, so it is asserted PRESENT but not asserted tagged.
for id in REQ-YF-CLI-005 REQ-YF-TUNE-030; do
  grep -q "\*\*${id}\*\* \*(testable)\*" "${SPEC}" \
    || ck_fail "${id} is absent from SPEC.md or not marked bare *(testable)* (an annotated marker escapes coverage.rs's enforced set entirely)"
done
grep -q '\*\*REQ-YF-EMBED-006\*\*' "${SPEC}" || ck_fail "REQ-YF-EMBED-006 is absent from SPEC.md"
grep -q 'Symlink-aware delete' "${SPEC}"     || ck_fail "REQ-YF-TUNE-022 carries no symlink-aware delete amendment"
grep -q 'plan-054 (2026-08-26' "${SPEC}"     || ck_fail "SPEC.md has no plan-054 living-amendment-log entry"

# Each testable id must be TAGGED by a test, or bridged by an ALLOWLIST row. The bridge is
# legitimate DURING the plan and must be GONE by its end, which Issue 4.3 asserts separately.
COV="${TREE}/yf/src/coverage.rs"
[ -f "${COV}" ] || ck_inconclusive "no coverage.rs at ${COV}"
for id in REQ-YF-CLI-005 REQ-YF-TUNE-030; do
  # coverage.rs IS EXCLUDED, mirroring its own `tagged_reqs`, which skips itself with the
  # note that "its parser fixtures contain literal REQ ids that are not real test tags". The
  # same trap caught this check: an ALLOWLIST reason reading "…the `// REQ-YF-CLI-005` tag
  # that supersedes it" matches a bare `// REQ-…` search, so the check read a BRIDGE ROW as
  # a TAG and reported a stale-row failure that did not exist.
  if grep -rq "// ${id}" "${TREE}/yf/src" --include='*.rs' --exclude=coverage.rs 2>/dev/null; then
    grep -q "(\"${id}\"" "${COV}" \
      && ck_fail "${id} is BOTH tagged and still on the ALLOWLIST — a stale row turns the tree red for every other branch (plan-044 D-7: add the tag and delete the row in one commit)"
  else
    grep -q "(\"${id}\"" "${COV}" \
      || ck_fail "${id} is neither tagged by a test nor bridged by an ALLOWLIST row"
  fi
done
ck_done "the new REQ ids are present, testable-marked and tagged-or-bridged"
