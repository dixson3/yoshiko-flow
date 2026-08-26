#!/usr/bin/env bash
# check-suite-portable — SC5b. `test_pour_fidelity.py` runs in a repo that is NOT this one.
#
# A `check-`, NOT a `ctl-`. It lives OUTSIDE the `ctl-` namespace and outside `controls.txt`
# deliberately (pass-4 C44): it is a plain criterion check with no RED/GREEN pair, and naming
# it `ctl-NNN-` made `verify-red-all`'s manifest derivation count 13 against 11 builders,
# rendering the capability gate unsatisfiable while it blocked every fix head.
#
# WHAT IT PROVES. The suite's TIER A arms pass with:
#   * a sandboxed `HOME` (no user config, no `~/.claude`, no `~/.beads`),
#   * `bd` forced OFF `PATH`, so there is NO live bead state to lean on,
#   * `cwd` OUTSIDE this repository.
#
# WHY IT EXISTS. Before Issue 3.4 the suite exited **2** the moment `bd` was unavailable, so
# it could not run in any repository but this one — which is *the same portability defect
# #210 is about*, occurring in the suite that guards #210's fix. A guard that only works
# where the bug does not is not a guard.
#
# It also asserts the SKIP IS REPORTED. A suite that silently drops its corpus arms and prints
# "all passed" is claiming coverage it does not have; the skip must be visible in the output.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
SUITE="${YF_TREE}/_shared/test_pour_fidelity.py"

[ -f "${SUITE}" ] || { echo "check-suite-portable: HARNESS — no suite at ${SUITE}" >&2; exit 2; }
command -v uv >/dev/null 2>&1 || { echo "check-suite-portable: HARNESS — no uv on PATH" >&2; exit 2; }

work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT
mkdir -p "${work}/home" "${work}/elsewhere" "${work}/bin"

# A PATH with `uv` and the system utilities but WITHOUT `bd`. Built by symlinking only what is
# needed, so the exclusion is by construction rather than by hope.
for tool in uv python3 env bash sh sed grep awk git; do
  src="$(command -v "${tool}" 2>/dev/null || true)"
  [ -n "${src}" ] && ln -sf "${src}" "${work}/bin/${tool}"
done
if [ -e "${work}/bin/bd" ]; then
  echo "check-suite-portable: HARNESS — bd leaked onto the sandbox PATH" >&2; exit 2
fi

out="$(cd "${work}/elsewhere" && env -i \
        HOME="${work}/home" \
        PATH="${work}/bin" \
        TERM=dumb \
        "${work}/bin/uv" run "${SUITE}" 2>&1)"
rc=$?

bad=()

# The sandbox must really have had no `bd` — otherwise the run proves nothing about portability.
if ! printf '%s' "${out}" | grep -q 'SKIP TIER B'; then
  bad+=("the corpus tier did not report a SKIP. Either \`bd\` leaked into the sandbox (so this \
run proves nothing about portability), or the suite dropped its corpus arms SILENTLY — and a \
suite that prints 'all passed' while quietly shedding coverage is the silent-green class this \
plan exists to close.")
fi

if [ "${rc}" -ne 0 ]; then
  bad+=("the suite exited ${rc} under a sandboxed HOME with no \`bd\` and cwd outside the \
repo. Before Issue 3.4 this was exit 2 — the suite could not run in any repository but this \
one, which is the SAME portability defect #210 is about, in the suite that guards #210's fix.")
fi

# The Tier A arms must actually have RUN — a green earned by executing nothing is the defect.
for arm in "TIER A baseline" "A1:" "A2:" "A3:" "A4:" "A5 (NARROWNESS)"; do
  if ! printf '%s' "${out}" | grep -qF "ok   ${arm}"; then
    bad+=("Tier A arm '${arm}' did not report ok in the sandboxed run.")
  fi
done

if [ "${#bad[@]}" -gt 0 ]; then
  echo "check-suite-portable: ${#bad[@]} failure(s):" >&2
  for b in "${bad[@]}"; do echo "check-suite-portable:   ${b}" >&2; done
  echo "check-suite-portable: --- sandboxed run output ---" >&2
  printf '%s\n' "${out}" | tail -25 | sed 's/^/check-suite-portable:   /' >&2
  exit 1
fi
echo "check-suite-portable: the suite's Tier A arms pass under a sandboxed HOME with no bd and cwd outside the repo; Tier B skips visibly"
