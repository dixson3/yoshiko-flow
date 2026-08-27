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
