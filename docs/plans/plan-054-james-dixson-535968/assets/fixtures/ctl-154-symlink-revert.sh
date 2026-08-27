#!/usr/bin/env bash
# ctl-154-symlink-revert — grades #154's SURVIVING half / plan-054 Issue 2.2.
#
# ASSERTED BEHAVIOUR (post-fix): `yf harness tune --revert` reverses its rules write THROUGH a
# symlinked rule target — the LINK SURVIVES and the TARGET's yf content is removed.
#
# THE DEFECT (EXP-006, two independent sandbox reproductions): revert's delete branches call
# `std::fs::remove_file(&path)`, which UNLINKS THE SYMLINK ITSELF, while the paired write path
# uses `std::fs::write`, which FOLLOWS the link. So a tune writes into the operator's real
# (often git-tracked) dotfiles file, and the revert deletes their *pointer* and strands the
# content — measured at 31613 bytes in one variant — WHILE REPORTING SUCCESS.
#
# NOTE PRECISELY WHAT IS AND IS NOT CLAIMED. #154 is CLOSED upstream and its revert half is
# genuinely fixed: the REQ-YF-TUNE-029 sha guard does fire. This fixture grades only the
# adjacent SYMLINK branch that survived, which is why Issue 6.4 files a SUCCESSOR rather than
# reopening a closed issue. The manifest records nothing distinguishing a symlinked target
# from a regular one, so no existing test can catch it — `harness_cross_e2e.rs` uses regular
# files only.
#
# THE FIXTURE IS A SANDBOX SPIKE. It builds nothing it does not need, runs entirely under a
# throwaway `HOME` in `$(mktemp -d)`, and touches no real surface. It is self-cleaning on both
# exit paths.
#
# EXIT  0 the link survives and the target was reverted  ·  1 the link was destroyed  ·  2 could not run
set -uo pipefail

[ -n "${YF_TREE:-}" ] || { echo "ctl-154: INCONCLUSIVE — YF_TREE is not set" >&2; exit 2; }
YF="${YF_TREE}/target/debug/yf"
[ -x "${YF}" ] || { echo "ctl-154: INCONCLUSIVE — no debug binary at ${YF} (run: cargo build)" >&2; exit 2; }

TMP="$(mktemp -d)" || { echo "ctl-154: INCONCLUSIVE — mktemp failed" >&2; exit 2; }
trap 'rm -rf "${TMP}"' EXIT

FAKE_HOME="${TMP}/home"
DOTFILES="${TMP}/dotfiles"
mkdir -p "${FAKE_HOME}/.pi/agent" "${DOTFILES}"

# The operator's REAL file, in their tracked dotfiles repo.
#
# IT IS **EMPTY**, AND THAT IS THE WHOLE POINT — this is the variant that reaches the branch
# under test. Revert's rule-block path deletes the file only when removing yf's block leaves
# it empty (`if out.trim().is_empty() { remove_file(&path) }`) and otherwise WRITES THE
# REMAINDER BACK — and `std::fs::write` follows a symlink correctly. So a fixture whose
# operator file carries prose takes the write-back branch, never calls `remove_file`, and
# passes on the UNFIXED tree. An earlier draft of this fixture did exactly that and came up
# green; EXP-006 lists the empty-operator-file case as a separate spike for this reason.
REAL="${DOTFILES}/AGENTS.md"
: > "${REAL}"
BEFORE_BYTES="$(wc -c < "${REAL}" | tr -d ' ')"

# The harness surface is a SYMLINK into it — the shape EXP-006 reproduced.
ln -s "${REAL}" "${FAKE_HOME}/.pi/agent/AGENTS.md"

# Rules-only keeps this spike to the one sub-operation under test and writes no config.
if ! HOME="${FAKE_HOME}" "${YF}" harness tune --harness pi --rules-only >/dev/null 2>&1; then
  echo "ctl-154: INCONCLUSIVE — the tune itself failed; nothing to revert" >&2
  exit 2
fi
[ -r "${REAL}" ] || { echo "ctl-154: INCONCLUSIVE — the real target is unreadable after the tune" >&2; exit 2; }
AFTER_TUNE_BYTES="$(wc -c < "${REAL}" | tr -d ' ')"
if [ "${AFTER_TUNE_BYTES}" -le "${BEFORE_BYTES}" ]; then
  echo "ctl-154: INCONCLUSIVE — the tune wrote nothing through the link, so the revert" >&2
  echo "ctl-154: branch under test is never reached." >&2
  exit 2
fi

HOME="${FAKE_HOME}" "${YF}" harness tune --harness pi --rules-only --revert >/dev/null 2>&1 || true

rc=0
if [ ! -L "${FAKE_HOME}/.pi/agent/AGENTS.md" ]; then
  echo "ctl-154: FAIL — the SYMLINK was destroyed by revert." >&2
  echo "ctl-154: remove_file() unlinked the link rather than writing through it, stranding" >&2
  echo "ctl-154: the content in the operator's tracked dotfiles file — while reporting success." >&2
  rc=1
fi
if [ ! -e "${REAL}" ]; then
  echo "ctl-154: FAIL — the operator's real dotfiles target no longer exists." >&2
  echo "ctl-154: revert must not delete a file whose pre-tune content yf never backed up." >&2
  rc=1
fi
[ "${rc}" -eq 0 ] && echo "ctl-154: revert wrote through the symlink — link intact, real target intact"
exit "${rc}"
