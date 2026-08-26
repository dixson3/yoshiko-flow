#!/usr/bin/env bash
# check-full-tier-record — SC16. The FULL tier passed over the MERGED tree.
#
# A `check-`, NOT a `ctl-`. Outside the `ctl-` namespace and outside `controls.txt`
# deliberately (pass-4 C44): a plain criterion check with no RED/GREEN pair. Naming it
# `ctl-NNN-` made `verify-red-all`'s derivation count 13 against 11 builders and rendered the
# capability gate unsatisfiable while it blocked every fix head.
#
# ══ WHY IT READS A RECORD INSTEAD OF RE-RUNNING THE TIER ══════════════════════════════════
#
# Two measured defects (pass-2 C19, pass-3 C38):
#
#   1. the criterion's earlier command path was wrong, and measured exit 2 `Failed to spawn`;
#   2. `recheck-criteria` converts a `TimeoutExpired` into `status: inconclusive` and
#      **continues** — never counted, never in `failed` — while the FULL tier far exceeds its
#      300 s default.
#
# Together those mean the plan's BROADEST criterion would have timed out, recorded
# inconclusive, and let completion proceed at exit 0. That is this plan's own thesis defect —
# a check that reports success while measuring nothing — occurring inside the plan that exists
# to close it. So the tier is run ONCE, at Issue 7.1, against the merged tree, and its verdict
# is written down; this check reads what was written.
#
# THE RECORD IS THEREFORE HELD TO A HIGHER STANDARD THAN ITS OWN HEADLINE. A file that merely
# says "PASS" would be a claim, not evidence — so this check also requires the per-row table,
# a non-trivial row count, a date, and INTERNAL CONSISTENCY between the headline and the rows.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REC="${HERE}/../full-tier-record.md"

if [ ! -f "${REC}" ]; then
  echo "check-full-tier-record: no record at ${REC}." >&2
  echo "check-full-tier-record: Issue 7.1 must run the FULL tier over the MERGED tree and" >&2
  echo "check-full-tier-record: write its verdict, command and date here." >&2
  exit 1
fi

bad=()

grep -qE '^\| \*\*Verdict\*\* \| \*\*PASS\*\* \|' "${REC}" \
  || bad+=("the record does not carry a **PASS** verdict.")
grep -qE '^\| \*\*Engine\*\* \| `change-validation` \(tier `full`\) \|' "${REC}" \
  || bad+=("the record does not name the change-validation engine at tier FULL. A FAST-tier \
run is not what SC16 asserts.")
grep -qE '^\| \*\*Date \(UTC\)\*\* \| [0-9]{4}-[0-9]{2}-[0-9]{2}T' "${REC}" \
  || bad+=("the record carries no ISO-8601 UTC date. An undated verdict cannot be tied to a \
tree state.")
grep -qE '^\| \*\*Command\*\* \| `.*validate-merged' "${REC}" \
  || bad+=("the record does not name the command that produced it.")
grep -qi 'MERGED' "${REC}" \
  || bad+=("the record does not state that the tree was the MERGED one. Validating pre-merge \
cannot catch class-(b) integration regressions (plan-009 INV-4).")

# ---- the per-row table must be present, non-trivial, and CONSISTENT with the headline -----
rows="$(grep -cE '^\| `[^`]+` \| (pass|fail|skip) \| [0-9-]+ \|$' "${REC}" || true)"
if [ "${rows}" -lt 20 ]; then
  bad+=("the record lists only ${rows} command row(s). The FULL tier is the CI-union \
superset; a handful of rows means a partial run was recorded, not the tier.")
fi
nonpass="$(grep -cE '^\| `[^`]+` \| (fail|skip) \| ' "${REC}" || true)"
if [ "${nonpass}" -ne 0 ]; then
  bad+=("${nonpass} row(s) in the record are not \`pass\`, but the headline claims PASS. The \
headline and the rows disagree — which is exactly the kind of unexamined green this check \
exists to refuse.")
fi
# The headline's own row count must match the table it summarises.
claimed="$(sed -n 's/^| \*\*Rows\*\* | \([0-9]*\) --.*/\1/p' "${REC}")"
if [ -n "${claimed}" ] && [ "${claimed}" != "${rows}" ]; then
  bad+=("the record's headline claims ${claimed} rows but the table lists ${rows}.")
fi

if [ "${#bad[@]}" -gt 0 ]; then
  echo "check-full-tier-record: ${#bad[@]} failure(s):" >&2
  for b in "${bad[@]}"; do echo "check-full-tier-record:   ${b}" >&2; done
  exit 1
fi
echo "check-full-tier-record: FULL tier recorded PASS over the merged tree, ${rows} rows, 0 non-pass"
