#!/usr/bin/env bash
# ctl-201-changed-append — grades #201 / plan-054 Issue 3.4.
#
# ASSERTED BEHAVIOUR (post-fix): repeating `--changed` ACCUMULATES the paths.
#
# THE DEFECT: `--changed` is declared `nargs="*"`, which argparse treats as a SINGLE
# optional taking zero-or-more values. A second `--changed` therefore OVERWRITES the first
# rather than appending — so `run --tier fast --changed a.py --changed b.py` validates
# `b.py` ALONE and reports a green covering half the change-set, with nothing in the output
# to say so.
#
# WHY THE PROBE IS THE PARSER AND NOT A FULL `run`. The claim under test is entirely about
# argument BINDING; a full `run` would additionally need a git repo and an approved
# CHANGE-VALIDATION.md, so a failure there could mean six things. `build_parser()` is
# factored out precisely so the binding can be asked directly.
#
# EXIT  0 both paths bound  ·  1 they are not (the defect)  ·  2 could not run
set -uo pipefail

# An UNSET YF_TREE is INCONCLUSIVE (2), never RED (1): the fixture could not run, which is a
# statement about the harness rather than about the tree. `${VAR:?}` would exit 1 and
# manufacture a RED — the exact failure redcheck.sh's own exit-2 guard exists to refuse.
# YF_TREE SELF-RESOLUTION (added at close). A fixture is invoked TWO ways: by `redcheck.sh`,
# which exports YF_TREE, and DIRECTLY by its Success Criterion's Verification command, which does
# not. Exiting 2 on an unset YF_TREE made every criterion that invokes a fixture directly
# UNSATISFIABLE — SC7, SC7b, SC8, SC23 and SC24 could never pass, in either direction. That is a
# criterion that cannot be met, which is worse than one that cannot fail: it halts the close
# chain over nothing.
#
# So resolve it the way redcheck.sh does: the plan's execution worktree while its branch is still
# UNMERGED, else the repo root. A genuinely unresolvable tree is still INCONCLUSIVE.
if [ -z "${YF_TREE:-}" ]; then
  _fx_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  _fx_plan="$(cd "${_fx_here}/../.." && pwd)"
  _fx_root="$(git -C "${_fx_plan}" rev-parse --show-toplevel 2>/dev/null)" || _fx_root=""
  _fx_id="$(basename "${_fx_plan}")"
  if [ -n "${_fx_root}" ] && [ -d "${_fx_root}/.worktrees/${_fx_id}" ] \
     && ! git -C "${_fx_root}" merge-base --is-ancestor "${_fx_id}-execute" main 2>/dev/null; then
    YF_TREE="${_fx_root}/.worktrees/${_fx_id}"
  else
    YF_TREE="${_fx_root}"
  fi
  export YF_TREE
  unset _fx_here _fx_plan _fx_root _fx_id
fi
[ -n "${YF_TREE:-}" ] || { echo "ctl-201: INCONCLUSIVE — YF_TREE is not set" >&2; exit 2; }
TREE="${YF_TREE}"
SCRIPT="${TREE}/skills/yf-change-validation/scripts/change_validation.py"

[ -f "${SCRIPT}" ] || { echo "ctl-201: INCONCLUSIVE — no change_validation.py at ${SCRIPT}" >&2; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "ctl-201: INCONCLUSIVE — python3 not on PATH" >&2; exit 2; }

out="$(python3 - "${SCRIPT}" <<'PY' 2>&1
import importlib.util, sys
spec = importlib.util.spec_from_file_location("cv", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    p = mod.build_parser()
except Exception as e:                      # noqa: BLE001 — any import/parser error is INCONCLUSIVE
    print("INCONCLUSIVE: %s" % e); raise SystemExit(0)
try:
    ns = p.parse_args(["run", "--tier", "fast", "--changed", "AAA.py", "--changed", "BBB.py"])
except SystemExit:
    print("INCONCLUSIVE: parser rejected the repeated-flag form"); raise SystemExit(0)
got = ns.changed
flat = []
for v in (got or []):
    flat.extend(v) if isinstance(v, list) else flat.append(v)
print("ACCUMULATES" if ("AAA.py" in flat and "BBB.py" in flat) else "DROPS:%r" % (got,))
PY
)"

case "${out}" in
  ACCUMULATES*)  echo "ctl-201: both --changed paths bound"; exit 0 ;;
  INCONCLUSIVE*) echo "ctl-201: ${out}" >&2; exit 2 ;;
  DROPS*)        echo "ctl-201: repeated --changed dropped all but the last — ${out}" >&2; exit 1 ;;
  *)             echo "ctl-201: INCONCLUSIVE — unrecognised probe output: ${out}" >&2; exit 2 ;;
esac
