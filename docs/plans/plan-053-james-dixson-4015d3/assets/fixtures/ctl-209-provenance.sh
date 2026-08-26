#!/usr/bin/env bash
# ctl-209-provenance — issue-bead provenance at pour time (REQ-DATA-073 / #209).
#
# A FIXTURE per redcheck.sh's definition: exits 0 iff the asserted behaviour holds.
#
# ══ WHAT THIS CONTROL CAN AND CANNOT PROVE — READ THIS BEFORE TRUSTING IT ═════════════════
#
# `SKILL.md` §5.2a is AGENT-EXECUTED PROSE. No exit code can reach what an agent actually
# transcribes at pour time, so there is no honest way to assert the real end state mechanically
# from here. The control is therefore split, and each half says what it is:
#
#   ARM A (TEXT).  The two `bd create` sites in §5.2a carry `plan_dir` in their `jq` metadata
#                  and prepend the provenance header with a blank line. This is SC14's form,
#                  and it is the strongest claim available about prose.
#   ARM B (SHAPE). The header and metadata CONSTRUCTION is executed here, against THE
#                  FIXTURE'S OWN COPY of the commands — not against a live pour. It proves the
#                  recipe produces the required shape; it does NOT prove an agent ran it.
#
# ARM B DELIBERATELY DOES NOT POUR. A real `bd create` writes to the repository's live beads
# database, and `bd` has no delete — the fixture would leave permanent residue in the operator's
# DB every time it ran, and `redcheck.sh` runs it at least twice (RED and GREEN). A control
# that damages the thing it measures is not a control. So arm B runs the same `jq` and `printf`
# the SKILL.md block runs and asserts the resulting strings.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
SKILL="${YF_TREE}/skills/yf-plan/SKILL.md"

[ -f "${SKILL}" ] || { echo "ctl-209: HARNESS — no SKILL.md at ${SKILL}" >&2; exit 2; }
command -v jq >/dev/null 2>&1 || { echo "ctl-209: HARNESS — jq is not on PATH" >&2; exit 2; }

bad=()

# ── ARM A: THE TEXT ───────────────────────────────────────────────────────────────────────
# §5.2a carries exactly TWO `bd create` issue sites (the entry issue and the downstream
# issue). Both must be fixed — fixing one leaves half of every pour unprovenanced.
# Scoped to the ISSUE sites by matching the FULL three-key metadata form. A bare
# `plan_dir:$d` grep also matches §5.2a step (a)'s `bd update ${EPIC} --metadata` epic stamp,
# which is a different line for a different purpose — measured: it returned 1 against a tree
# where NEITHER issue site had been touched, i.e. the control's own false positive.
n_meta="$(grep -c "{plan_issue:\$i, plan:\$p, plan_dir:\$d}" "${SKILL}" || true)"
if [ "${n_meta}" -lt 2 ]; then
  bad+=("ARM A: only ${n_meta} of the two §5.2a \`bd create\` sites carry \`plan_dir:\$d\` in \
their \`jq -nc\` metadata. Both the ENTRY-issue and the DOWNSTREAM-issue site must carry it; \
fixing one leaves half of every pour without a route back to its bundle.")
fi

n_hdr="$(grep -c 'Plan: \${plan_id} | Bundle: \${plan_dir}' "${SKILL}" || true)"
if [ "${n_hdr}" -lt 2 ]; then
  bad+=("ARM A: only ${n_hdr} of the two §5.2a \`bd create\` sites prepend the provenance \
header \`Plan: \${plan_id} | Bundle: \${plan_dir} (repo-relative)\`.")
fi

# The ASCII pipe, not `·`. Both round-trip through `bd` byte-exact, but a bead description
# also becomes a GitHub issue body, and only one of the two is unambiguous in every renderer.
if grep -q 'Plan: \${plan_id} · Bundle:' "${SKILL}"; then
  bad+=("ARM A: the header uses \`·\` rather than the ASCII \`|\`. A bead description is \
rendered as a GitHub issue body, where the ASCII separator is the unambiguous one.")
fi

# The BLANK LINE is load-bearing, not cosmetic: without it a renderer joins the header to any
# `detail` that opens with a list, a heading or a fence.
if [ "$(grep -c 'Bundle: \${plan_dir} (repo-relative)\\n\\n' "${SKILL}" || true)" -lt 2 ]; then
  bad+=("ARM A: the header is not followed by a BLANK LINE (\\n\\n) at both sites. Without it \
a markdown renderer joins the header to any \`detail\` opening with a list, heading or fence, \
corrupting the first construct.")
fi

# ── ARM B: THE SHAPE, executed against THE FIXTURE'S OWN COPY ─────────────────────────────
plan_id="plan-209-fixture-ffffff"
plan_dir="docs/plans/${plan_id}"
issue_id="1.1"
issue_detail="- a detail opening with a LIST, which is what the blank line protects"

# THE FIXTURE'S OWN COPY of §5.2a's metadata construction.
meta="$(jq -nc --arg i "${issue_id}" --arg p "${plan_id}" --arg d "${plan_dir}" \
        '{plan_issue:$i, plan:$p, plan_dir:$d}')"
for k in plan_issue plan plan_dir; do
  if [ "$(printf '%s' "${meta}" | jq -r --arg k "${k}" 'has($k)')" != "true" ]; then
    bad+=("ARM B: constructed metadata is missing the \`${k}\` key: ${meta}")
  fi
done

# THE FIXTURE'S OWN COPY of §5.2a's description construction.
desc="$(printf 'Plan: %s | Bundle: %s (repo-relative)\n\n%s' \
        "${plan_id}" "${plan_dir}" "${issue_detail}")"

first="$(printf '%s' "${desc}" | sed -n '1p')"
if ! printf '%s' "${first}" | grep -qE '^Plan: [^[:space:]]+ \| Bundle: [^[:space:]]+'; then
  bad+=("ARM B: the description's FIRST LINE does not match \`^Plan: \\S+ \\| Bundle: \\S+\`; \
got: ${first}")
fi
second="$(printf '%s' "${desc}" | sed -n '2p')"
if [ -n "${second}" ]; then
  bad+=("ARM B: line 2 of the description is not BLANK (got: ${second}). The blank line is \
what stops a renderer joining the header to a detail that opens with a list.")
fi
if ! printf '%s' "${desc}" | sed -n '3p' | grep -q 'a detail opening with a LIST'; then
  bad+=("ARM B: the detail did not survive after the header and blank line.")
fi

# NO description-equality check may exist ANYWHERE (REQ-DATA-073). The ABSENCE of one is what
# makes prepending the header safe; adding one would re-create the coupling #209 needs broken.
if (cd "${YF_TREE}" && grep -rqE 'description.*==.*detail' _shared skills 2>/dev/null); then
  bad+=("A description-equality check exists. Nothing in the repo compares a bead description \
to plan text, and that ABSENCE is exactly what makes the header safe — REQ-DATA-073 forbids \
adding one.")
fi

if [ "${#bad[@]}" -gt 0 ]; then
  echo "ctl-209: ${#bad[@]} failure(s):" >&2
  for b in "${bad[@]}"; do echo "ctl-209:   ${b}" >&2; done
  exit 1
fi
echo "ctl-209: both §5.2a sites carry plan_dir + the provenance header (ARM A, text); the construction yields the required shape (ARM B, the fixture's own copy — not a live pour)"
