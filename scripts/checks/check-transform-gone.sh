#!/usr/bin/env bash
# SC8 — pi's NameTransform is gone from the DESCRIPTOR and the `lowercase-hyphen,max64` label
# is gone from SPEC.md's REQ-YF-INSTALL-007 stanza.
#
# WHY A SEPARATE CHECK RATHER THAN LEANING ON THE PARITY TEST. Measured:
# `spec_table_matches_shipped_descriptor` guards the label assertion behind
# `if let Some(t) = d.name_transform { … }`. With every row set to `None` that arm never
# executes — the parity test SKIPS the label check entirely, and a SPEC still carrying the label
# passes it green. So the parity test cannot see the half of SC8 that lives in SPEC.md.
#
# WHY THE SPEC GREP IS STANZA-SCOPED, NOT WHOLE-FILE. `lowercase-hyphen,max64` also occurs in
# the LIVING AMENDMENT LOG (a plan-033 entry), which is append-only by construction. A
# whole-file grep would therefore match forever and SC8 would be UNSATISFIABLE — it could never
# be made to pass, no matter what the code did.
#
# `! grep -q` is the correct spelling of "no line matches". `grep -qv` is banned as a criterion
# primitive: it exits 0 whenever ANY line lacks the pattern, so on a multi-line file it is
# nearly a constant and cannot fail.
#
# EXIT  0 gone from both  ·  1 present in either  ·  2 could not run
CHECK_NAME=check-transform-gone
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
DESC="${TREE}/yf/src/harness_desc.rs"
SPEC="${TREE}/SPEC.md"
[ -f "${DESC}" ] || ck_inconclusive "no harness_desc.rs at ${DESC}"
[ -f "${SPEC}" ] || ck_inconclusive "no SPEC.md at ${SPEC}"
CK_RC=0

# (a) NO SHIPPED ROW may declare the transform. The ENUM VARIANT itself is deliberately allowed
# to survive — the type is retained so a future harness that really does constrain names can
# declare one — so the predicate is over the ROWS, not over the identifier.
if grep -q 'name_transform: Some(' "${DESC}"; then
  ck_fail "a descriptor row still declares a name_transform:"
  grep -n 'name_transform: Some(' "${DESC}" >&2
fi

# (b) The label must be gone from REQ-YF-INSTALL-007's stanza. Extract the stanza the same way
# the parity test does — from the bold id to the next `- **REQ-` bullet — so the two agree on
# what "the stanza" means.
STANZA="$(awk '
  /\*\*REQ-YF-INSTALL-007\*\*/ { inblock=1 }
  inblock && /^- \*\*REQ-YF-/ && !/REQ-YF-INSTALL-007/ { exit }
  inblock { print }
' "${SPEC}")"
if [ -z "${STANZA}" ]; then
  ck_inconclusive "could not extract the REQ-YF-INSTALL-007 stanza from SPEC.md"
fi
if printf '%s' "${STANZA}" | grep -q 'lowercase-hyphen,max64'; then
  ck_fail "REQ-YF-INSTALL-007's stanza still carries the \`lowercase-hyphen,max64\` label"
fi

# (c) The stanza must also no longer REQUIRE the transform be validated against long names —
# the live requirement text a table-only edit would leave stranded.
if printf '%s' "${STANZA}" | grep -q 'transform shall be validated against'; then
  ck_fail "REQ-YF-INSTALL-007 still REQUIRES the transform be validated against long skill names"
fi

ck_done "no row declares a name_transform; REQ-YF-INSTALL-007 carries neither the label nor the validation clause"
