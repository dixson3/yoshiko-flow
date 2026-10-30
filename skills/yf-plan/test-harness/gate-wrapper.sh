#!/usr/bin/env bash
# gate-wrapper.sh — Tier-2 mechanical drive of native gate-wrapper compatibility
# (plan-074 Issue 3.1; REQ-PLAN-077 as amended, REQ-PLAN-087, REQ-DATA-026 as amended, REQ-DATA-077).
#
#   bash skills/yf-plan/test-harness/gate-wrapper.sh gate      # the whole capability check
#   bash skills/yf-plan/test-harness/gate-wrapper.sh help
#
# WHAT IT PROVES, on REAL native `bd` stores it owns:
#   * the MODIFIED yf-plan, installed by the repo's own debug `yf` into an OWNED sandbox HOME
#     (asserted not shadowed, installed scripts byte-equal to the source), drives SKILL.md §5.2a
#     mechanically: pour with retained raw output, root linkage, start-only receipt, the plan's
#     DAG with retained create outputs, finalized receipt, actual-gate-only start resolution;
#   * on a GENUINE bd 1.3.1 gate-typed wrapper the OLD (pre-plan-074) fidelity checker fails
#     (3 declared vs 4 gates) and the old resolver is INCONCLUSIVE, while the modified ones pass the
#     same graph without retyping or dropping a gate. The old skill is taken from THIS checkout's
#     own history (`git archive 7a6ce3a`, the plan's pinned base) and its scripts are verified
#     against the installed-copy digests EXP-003 recorded — no dependency on the operator's HOME;
#   * on a GENUINE bd 1.1.0 task-typed wrapper (release binary fetched and verified against the
#     digests EXP-001 recorded) the modified path also passes;
#   * every refusal makes ZERO mutations, observed in a log of every `bd` argv; the human
#     capability gate is never touched; `bd gate resolve <wrapper>` really does close a 1.3.1
#     wrapper while the actual gate stays open, and the new resolver does not read that as consent.
#
# ISOLATION. The sandbox owns HOME, XDG_*, TMPDIR, uv's cache, the git repos and the bd stores.
# PATH holds only a logging `bd` shim, a `uv` link (own dir), /usr/bin and /bin — the real bd binaries are
# reachable ONLY through the shim, which refuses any cwd outside the sandbox. Nothing is installed
# outside the sandbox and nothing outside it is read except the tested checkout and the two
# native tools. No network except the optional bd 1.1.0 release fetch, verified by
# SHA-256 before use.
#
# EXIT  0 pass · 1 a check failed · 2 INCONCLUSIVE (a required control could not run) ·
#       3 a required tool is missing · 64 usage error.  Set YFGW_KEEP=1 to keep the sandbox.

set -euo pipefail

MODE="${1:-}"
case "${MODE}" in
  gate) ;;
  help|-h|--help) sed -n '2,35p' "$0"; exit 0 ;;
  "") echo "usage: gate-wrapper.sh gate|help" >&2; exit 64 ;;
  *) echo "gate-wrapper.sh: unknown mode '${MODE}' (expected: gate|help)" >&2; exit 64 ;;
esac

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${HERE}/../../.." && pwd)"
OLD_BASE="7a6ce3a32f18c8dee5bb693598e34edf93051177"   # plan-074 pinned base: pre-change yf-plan
OLD_PM_SHA="1b1cd81c86234121c32a3bcfdb2f66b315dff299881825d6ac356524aa643085"   # EXP-003 installed
OLD_PF_SHA="e65f03cf3231e97a3313746dcbdf62b384fcdd99c4d26f5f4f0af3c71375106a"   # EXP-003 installed

# --- tool provenance (missing -> exit 3, distinctly) ------------------------------------------
need() { command -v "$1" >/dev/null 2>&1 || { echo "MISSING TOOL: $1" >&2; exit 3; }; }
for t in bd uv git cargo shasum curl tar; do need "$t"; done
BD131="$(command -v bd)"
"${BD131}" --version | grep -q "1.3.1" || { echo "MISSING TOOL: bd 1.3.1 on PATH (found: $("${BD131}" --version))" >&2; exit 3; }
git -C "${REPO}" cat-file -e "${OLD_BASE}^{commit}" 2>/dev/null \
  || { echo "MISSING TOOL: base commit ${OLD_BASE} (old yf-plan) not in this checkout's history" >&2; exit 3; }
UVBIN="$(command -v uv)"
PY="$(cd / && env -u VIRTUAL_ENV uv python find 2>/dev/null || true)"
[ -x "${PY}" ] || { echo "MISSING TOOL: a uv-managed python (uv python find)" >&2; exit 3; }

SB="$(mktemp -d "${TMPDIR:-/tmp}/yf-gatewrapper.XXXXXX")"
SB="$(cd "${SB}" && pwd -P)"
cleanup() {
  if [ "${YFGW_KEEP:-}" = "1" ]; then echo ">> kept sandbox: ${SB}"; return; fi
  chmod -R u+w "${SB}" 2>/dev/null || true
  rm -rf "${SB}"
  [ ! -e "${SB}" ] && echo ">> sandbox removed" || echo "WARNING: sandbox not removed: ${SB}" >&2
}
trap cleanup EXIT
mkdir -p "${SB}/home" "${SB}/bin" "${SB}/tmp" "${SB}/work" "${SB}/xdg/config" "${SB}/xdg/data" \
         "${SB}/xdg/state" "${SB}/xdg/cache" "${SB}/uvcache" "${SB}/bd110"
# The OLD control: pre-plan-074 yf-plan from this checkout's own history, digest-verified.
OLD_SKILL="${SB}/old/skills/yf-plan"
mkdir -p "${SB}/old" && git -C "${REPO}" archive "${OLD_BASE}" skills/yf-plan | tar -x -C "${SB}/old"
[ "$(shasum -a 256 "${OLD_SKILL}/scripts/plan_manager.py" | cut -c1-64)" = "${OLD_PM_SHA}" ] \
  && [ "$(shasum -a 256 "${OLD_SKILL}/scripts/pour_fidelity.py" | cut -c1-64)" = "${OLD_PF_SHA}" ] \
  || { echo "FAIL: old yf-plan from ${OLD_BASE} does not match the recorded installed digests" >&2; exit 1; }
echo ">> old control: yf-plan @ ${OLD_BASE:0:12} (scripts match the recorded installed digests)"
mkdir -p "${SB}/uvbin"
ln -s "${UVBIN}" "${SB}/uvbin/uv"   # separate dir: the bd-absent control drops only bin/

# --- the bd shim: log every argv + cwd, refuse outside the sandbox, exec the REAL binary -------
cat > "${SB}/bin/bd" <<'SHIM'
#!/usr/bin/env python3
import json, os, sys
root, log, real = os.environ["YFGW_ROOT"], os.environ["YFGW_LOG"], os.environ.get("YFGW_REAL_BD", "")
cwd = os.path.realpath(os.getcwd())
with open(log, "a") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "cwd": cwd, "bd": real}) + "\n")
if not cwd.startswith(root + os.sep) and cwd != root:
    print(f"bd shim: REFUSED — cwd {cwd} is outside the sandbox {root}", file=sys.stderr)
    sys.exit(97)
if not real or not os.access(real, os.X_OK):
    print("bd shim: no real bd configured", file=sys.stderr); sys.exit(98)
os.execv(real, [real] + sys.argv[1:])
SHIM
# Pin the shim interpreter to the recorded uv python (never whatever /usr/bin/env finds).
sed -i.bak "1s|.*|#!${PY}|" "${SB}/bin/bd" && rm -f "${SB}/bin/bd.bak"
chmod +x "${SB}/bin/bd"

# --- bd 1.1.0: the authentic historical task-wrapper tool, verified before use ----------------
BD110=""
BD110_ARCHIVE_SHA="c42e24d83b258f7ba9f52a6d2d5f6b055869dfe7807165055988b12e7ea8c564"
BD110_BIN_SHA="efa02cc59bbb50cd1ecf2a9af242033eb66b2676d64cd50a7414730e67cfa5b1"
if [ "$(uname -s)-$(uname -m)" = "Darwin-arm64" ]; then
  if curl -s -L -o "${SB}/bd110/a.tgz" \
       "https://github.com/gastownhall/beads/releases/download/v1.1.0/beads_1.1.0_darwin_arm64.tar.gz"; then
    if [ "$(shasum -a 256 "${SB}/bd110/a.tgz" | cut -c1-64)" = "${BD110_ARCHIVE_SHA}" ]; then
      tar xzf "${SB}/bd110/a.tgz" -C "${SB}/bd110" bd
      if [ "$(shasum -a 256 "${SB}/bd110/bd" | cut -c1-64)" = "${BD110_BIN_SHA}" ]; then
        BD110="${SB}/bd110/bd"
      else echo "bd 1.1.0 binary digest MISMATCH — not used" >&2; fi
    else echo "bd 1.1.0 archive digest MISMATCH — not used" >&2; fi
  else echo "bd 1.1.0 release fetch failed — that control will be INCONCLUSIVE" >&2; fi
else
  echo "bd 1.1.0 control: no recorded digest for $(uname -s)-$(uname -m) — INCONCLUSIVE" >&2
fi

# --- build + install the MODIFIED skill into the owned HOME ------------------------------------
echo ">> cargo build (debug; reads ${REPO}/skills from disk at runtime)"
CARGO_HOME="${CARGO_HOME:-${HOME}/.cargo}" RUSTUP_HOME="${RUSTUP_HOME:-${HOME}/.rustup}" \
  cargo build --quiet --manifest-path "${REPO}/yf/Cargo.toml"
YF="${REPO}/target/debug/yf"
[ -x "${YF}" ] || { echo "built yf not found at ${YF}" >&2; exit 2; }

SBENV=(env -i "HOME=${SB}/home" "PATH=${SB}/bin:${SB}/uvbin:/usr/bin:/bin:/usr/sbin:/sbin" "TMPDIR=${SB}/tmp"
       "USER=gw" "LANG=C.UTF-8" "BD_NON_INTERACTIVE=1" "XDG_CONFIG_HOME=${SB}/xdg/config"
       "XDG_DATA_HOME=${SB}/xdg/data" "XDG_STATE_HOME=${SB}/xdg/state" "XDG_CACHE_HOME=${SB}/xdg/cache"
       "UV_CACHE_DIR=${SB}/uvcache" "UV_PYTHON=${PY}" "UV_NO_PROGRESS=1" "CI=1" "YF_NO_CONFIG_SYNC=1"
       "YFGW_ROOT=${SB}" "YFGW_LOG=${SB}/bd-calls.jsonl" "YFGW_REAL_BD=${BD131}")

echo ">> yf skills install into the sandbox HOME"
(cd "${SB}/work" && "${SBENV[@]}" "${YF}" skills install yf-plan --json > "${SB}/install.json")
SKILL=""
for c in "${SB}/home/.claude/skills/yf-plan" "${SB}/home/.agents/skills/yf-plan"; do
  [ -d "${c}" ] && { SKILL="${c}"; break; }
done
case "${SKILL}" in "${SB}/home/"*) ;; *) echo "FAIL: installed skill not under the sandbox HOME" >&2; exit 1 ;; esac
for f in plan_manager.py gate_roles.py pour_fidelity.py plan_extract.py; do
  cmp -s "${SKILL}/scripts/${f}" "${REPO}/skills/yf-plan/scripts/${f}" \
    || { echo "FAIL: installed ${f} differs from the source tree" >&2; exit 1; }
done
grep -q "record-execution-roles" "${SKILL}/SKILL.md" \
  || { echo "FAIL: installed SKILL.md lacks the §5.2a record-execution-roles step" >&2; exit 1; }
echo ">> sandbox skill: ${SKILL} (byte-equal to source for the four scripts)"

# --- the guard must actually refuse (a guard that cannot fire proves nothing) -------------------
set +e
(cd / && "${SBENV[@]}" "${SB}/bin/bd" --version >/dev/null 2>&1); GUARD=$?
set -e
[ "${GUARD}" -eq 97 ] || { echo "FAIL: bd shim did not refuse an out-of-sandbox cwd (exit ${GUARD})" >&2; exit 1; }
: > "${SB}/bd-calls.jsonl"   # the probe's own refused entry is not part of the drive
echo ">> bd shim guard refuses out-of-sandbox cwd (exit 97)"

# --- drive --------------------------------------------------------------------------------------
REPORT="${YFGW_REPORT:-${SB}/report.json}"
set +e
"${SBENV[@]}" "YFGW_SKILL=${SKILL}" "YFGW_REPO=${REPO}" "YFGW_OLD_SKILL=${OLD_SKILL}" \
  "YFGW_BD131=${BD131}" "YFGW_BD110=${BD110}" "YFGW_PY=${PY}" \
  "${PY}" "${HERE}/gate_wrapper_drive.py" "${REPORT}"
RC=$?
set -e
python3 - "${REPORT}" "${BD131}" "${BD110}" "${YF}" "${PY}" "${SKILL}" <<'EOF' || true
import hashlib, json, subprocess, sys
rep, bd131, bd110, yf, py, skill = sys.argv[1:7]
d = json.load(open(rep))
def h(p): return hashlib.sha256(open(p, "rb").read()).hexdigest() if p else None
d["provenance"] = {"bd131": {"path": bd131, "sha256": h(bd131)}, "bd110": {"path": bd110 or None,
                   "sha256": h(bd110)}, "yf": {"path": yf, "sha256": h(yf)},
                   "python": py, "sandbox_skill": skill}
json.dump(d, open(rep, "w"), indent=2)
print(f">> {d['passed']}/{d['selected']} checks passed, {d['failed']} failed, "
      f"inconclusive={d['inconclusive']}, bd calls logged={d['bd_calls']}")
EOF
if [ "${RC}" -eq 0 ] && [ -z "${BD110}" ]; then RC=2; fi
[ -n "${YFGW_REPORT:-}" ] || echo ">> report was sandbox-local (set YFGW_REPORT=<path> to keep it)"
echo ">> gate-wrapper.sh exit ${RC}"
exit "${RC}"
