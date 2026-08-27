#!/usr/bin/env bash
# ctl-203-exit-discipline — grades #203 / plan-054 Issue 3.6.
#
# ASSERTED BEHAVIOUR (post-fix): `yf skills status` reports failure IN ITS EXIT CODE, not only
# in its output.
#
# THE DEFECT: `cmd/status.rs`'s `status()` ends in a bare `Ok(())` on every path. It prints a
# per-skill INSTALLED / UP-TO-DATE / COMPLETE / UNMODIFIED table that can be uniformly "no"
# and still exits 0 — so any caller that branches on `$?` (a CI step, a `set -e` script, a
# preflight) reads "everything is fine" from an instrument that just reported everything is
# broken. `REQ-YF-CLI-003` already requires every subcommand to exit non-zero on failure.
#
# THE PROBE IS AN EMPTY SKILLS DIRECTORY, which is the least ambiguous unhealthy state
# available: nothing is installed, so every skill is `installed: false`. If THAT exits 0, the
# exit code is carrying no information at all.
#
# NOTE ON SCOPE: #203 names five instruments; this fixture grades the one that lives in the
# BINARY, which is the one a release ships. The others are swept by Issue 3.6 alongside it.
#
# EXIT  0 a failing status exits non-zero  ·  1 it exits 0 (the defect)  ·  2 could not run
set -uo pipefail

[ -n "${YF_TREE:-}" ] || { echo "ctl-203: INCONCLUSIVE — YF_TREE is not set" >&2; exit 2; }
YF="${YF_TREE}/target/debug/yf"
[ -x "${YF}" ] || { echo "ctl-203: INCONCLUSIVE — no debug binary at ${YF} (run: cargo build)" >&2; exit 2; }

TMP="$(mktemp -d)" || { echo "ctl-203: INCONCLUSIVE — mktemp failed" >&2; exit 2; }
trap 'rm -rf "${TMP}"' EXIT

EMPTY="${TMP}/skills"
mkdir -p "${EMPTY}"

out="$("${YF}" skills status --target "${EMPTY}" --json 2>&1)"; rc=$?

# Confirm the run actually MEASURED an unhealthy state. Without this the fixture could pass on
# a non-zero exit that meant "bad flags" rather than "unhealthy skills" — a right answer for
# the wrong reason, which is not evidence.
if ! printf '%s' "${out}" | grep -q '"installed"'; then
  echo "ctl-203: INCONCLUSIVE — status produced no per-skill health report; the probe did not" >&2
  echo "ctl-203: reach the state under test. Output was: ${out}" >&2
  exit 2
fi
if ! printf '%s' "${out}" | grep -q '"installed"[[:space:]]*:[[:space:]]*false'; then
  echo "ctl-203: INCONCLUSIVE — no skill reported installed:false against an EMPTY dir, so" >&2
  echo "ctl-203: there is no unhealthy state for the exit code to report." >&2
  exit 2
fi

if [ "${rc}" -eq 0 ]; then
  echo "ctl-203: FAIL — \`yf skills status\` reported an unhealthy tree and exited 0." >&2
  echo "ctl-203: failure appeared in the output and success in \$? — REQ-YF-CLI-003 requires" >&2
  echo "ctl-203: a non-zero exit on failure. An exit code nothing can trust is not a step." >&2
  exit 1
fi
echo "ctl-203: unhealthy \`skills status\` exited ${rc} (non-zero)"
exit 0
