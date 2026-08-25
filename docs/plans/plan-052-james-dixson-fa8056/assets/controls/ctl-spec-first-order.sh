#!/usr/bin/env bash
# ctl-spec-first-order (SC1c) — the SPEC commit PRECEDES the first non-spec skills/** commit.
#
# The criterion's earlier form ("before the first `skills/**` commit") was FALSE BY
# CONSTRUCTION: Issue 0.1's own touches are all under skills/**, so it could never hold. The
# checked property is therefore: the commit touching `skills/*/spec/**` or `skills/*/SPEC.md`
# precedes the first commit touching any OTHER `skills/**` path.
#
# Checked PRE-MERGE and PRE-SQUASH (at 7.1): a squash destroys the ordering this asserts, so
# reading it off a merged trunk would always be vacuous.
#
# The live branch is already GREEN (0.1 landed spec-only first), so RED comes from a PINNED
# NEGATIVE FIXTURE: a scratch repo whose recorded history puts an impl commit BEFORE the spec
# commit.
#
#   CTL_RED=1   run the predicate against the negative fixture ALONE (real negative, exit 1)
#   (unset)     both arms: the fixture must FAIL and the live branch must PASS
#
# Exit: 0 both arms hold · 1 a real negative · 2 the instrument could not run
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"

is_spec_path() { case "$1" in skills/*/spec/*|skills/*/SPEC.md) return 0 ;; *) return 1 ;; esac; }

# predicate <repo> <range> -> 0 ordering holds · 1 violated · 2 cannot run
predicate() {
  local repo="$1" range="$2" shas c f spec_at=-1 impl_at=-1 i=0
  shas=$(git -C "$repo" rev-list --reverse "$range" 2>/dev/null) || {
    echo "INCONCLUSIVE: cannot resolve range '$range' in $repo" >&2; return 2; }
  [ -n "$shas" ] || { echo "INCONCLUSIVE: range '$range' is empty" >&2; return 2; }
  for c in $shas; do
    i=$((i+1))
    local saw_spec=0 saw_impl=0
    while IFS= read -r f; do
      case "$f" in skills/*) ;; *) continue ;; esac
      if is_spec_path "$f"; then saw_spec=1; else saw_impl=1; fi
    done < <(git -C "$repo" diff-tree --no-commit-id --name-only -r "$c")
    [ "$saw_spec" -eq 1 ] && [ "$spec_at" -lt 0 ] && spec_at=$i
    [ "$saw_impl" -eq 1 ] && [ "$impl_at" -lt 0 ] && impl_at=$i
  done
  if [ "$impl_at" -lt 0 ]; then
    if [ "$spec_at" -lt 0 ]; then
      echo "INCONCLUSIVE: range touches no skills/** path at all" >&2; return 2
    fi
    echo "ok: a spec commit exists (#$spec_at) and no non-spec skills/** commit yet"
    return 0
  fi
  if [ "$spec_at" -lt 0 ]; then
    echo "FAIL: a non-spec skills/** commit exists (#$impl_at) with NO spec commit before it" >&2
    return 1
  fi
  if [ "$spec_at" -ge "$impl_at" ]; then
    echo "FAIL: first spec commit is #$spec_at but first non-spec skills/** commit is #$impl_at" >&2
    return 1
  fi
  echo "ok: first spec commit #$spec_at precedes first non-spec skills/** commit #$impl_at"
  return 0
}

# --- pinned negative fixture: impl BEFORE spec, in a scratch repo -----------------
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
git -C "$tmp" init -q -b main 2>/dev/null || { echo "INCONCLUSIVE: git init failed" >&2; exit 2; }
git -C "$tmp" config user.email c@example.invalid; git -C "$tmp" config user.name c
mkdir -p "$tmp/skills/yf-x/spec" "$tmp/skills/yf-x/scripts"
echo base > "$tmp/README"; git -C "$tmp" add -A; git -C "$tmp" commit -qm base
echo 'impl' > "$tmp/skills/yf-x/scripts/a.py"; git -C "$tmp" add -A
git -C "$tmp" commit -qm "impl first (the violation)"
echo 'REQ-X-001: ...' > "$tmp/skills/yf-x/spec/data.md"; git -C "$tmp" add -A
git -C "$tmp" commit -qm "spec second"

if [ "${CTL_RED:-0}" = "1" ]; then
  predicate "$tmp" "main~2..main"; rc=$?
  echo "CTL_RED: predicate over the pinned negative fixture returned $rc (1 = real negative)"
  exit $rc
fi

predicate "$tmp" "main~2..main" 2>/dev/null; neg=$?
if [ "$neg" -ne 1 ]; then
  echo "FAIL: the pinned negative fixture did NOT produce a real negative (got $neg)" >&2
  exit 1
fi
echo "ok: pinned negative fixture -> exit 1 (a real negative)"

# --- live branch, PRE-MERGE and PRE-SQUASH ---------------------------------------
# THE RANGE MUST STILL RESOLVE AFTER THE MERGE. `<base>..HEAD` is the pre-merge range and is
# EMPTY once the branch has landed and HEAD is the base — so at completion this control
# returned 2 (INCONCLUSIVE) and `recheck-criteria` read that as SC1c being FALSE. The
# criterion was true; the range had simply stopped naming anything.
#
# So: use `<base>..HEAD` while it is non-empty, and otherwise fall back to the MOST RECENT
# MERGE COMMIT's parent range (`M^1..M^2`), which is exactly the set of commits the branch
# contributed — the same commits the pre-merge range named, still in order. No literal sha
# appears anywhere, so this does not go stale.
BASE="${CTL_BASE:-main}"
RANGE="${BASE}..HEAD"
if [ -z "$(git -C "$REPO" rev-list "$RANGE" 2>/dev/null)" ]; then
  M="$(git -C "$REPO" rev-list --merges -1 HEAD 2>/dev/null)"
  if [ -n "$M" ] && git -C "$REPO" rev-parse -q --verify "${M}^2" >/dev/null 2>&1; then
    RANGE="${M}^1..${M}^2"
    echo "ok: '${BASE}..HEAD' is empty (post-merge); using the merge's parent range instead"
  else
    # SQUASH-MERGE GUARD. Under a squash the branch's commits do NOT survive as a second
    # parent, so there is no range that preserves their ORDER — and order is the entire
    # claim. INCONCLUSIVE is the only honest answer: the instrument cannot see the property,
    # which is a different fact from the property being false.
    #
    # §6.1 mandates `--no-ff`, so this arm does not fire today. It is stated anyway, because
    # a control that silently mis-measures when the landing strategy changes is worse than
    # one that says it cannot tell.
    echo "INCONCLUSIVE: '${BASE}..HEAD' is empty and no merge with a second parent was found." >&2
    echo "              Under a SQUASH merge the branch's commits do not survive as a parent," >&2
    echo "              so commit ORDER — which is the whole claim — is unrecoverable." >&2
    exit 2
  fi
fi
predicate "$REPO" "$RANGE"; live=$?
[ "$live" -eq 2 ] && exit 2
[ "$live" -eq 0 ] || exit 1
echo "PASS: SPEC-first ordering holds on ${RANGE}; the fixture is a real negative"
