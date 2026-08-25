#!/usr/bin/env bash
# ctl-req-landed (SC1) — every REQ-* this plan introduces EXISTS on the merged tree.
#
# THE ONE BUILDER/FIXER INVERSION IN THE PLAN, found by ctl-harness-contract's third arm:
# this control's builder (0.3) has its fixer (0.1) among its own ancestors, so the LIVE TREE
# IS ALREADY GREEN here. A control that cannot be RED proves nothing, so RED is obtained from
# a PINNED NEGATIVE FIXTURE: a scratch spec tree with one REQ-* absent.
#
#   CTL_RED=1   run the predicate against the negative fixture ALONE and return its verdict
#               (a real negative, exit 1) — this is how the ledger's RED observation is made.
#   (unset)     both arms: the negative fixture must FAIL *and* the live tree must PASS.
#
# The merged-tree assertion is discharged at 7.1.
# Exit: 0 both arms hold · 1 a real negative · 2 the instrument could not run
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$ASSETS/../../../.." && pwd)"

REQS=(REQ-DATA-070 REQ-DATA-071 REQ-PLAN-080 REQ-BUP-070)
FILES=(skills/yf-plan/spec/data.md skills/yf-plan/spec/phases.md skills/yf-beads-upstream/SPEC.md)

# predicate <root> -> 0 all REQ ids DEFINED there, 1 one absent, 2 the tree is unreadable
predicate() {
  local root="$1" missing=0 r found any=0
  for f in "${FILES[@]}"; do [ -r "$root/$f" ] && any=1; done
  [ "$any" -eq 1 ] || { echo "INCONCLUSIVE: no spec file readable under $root" >&2; return 2; }
  for r in "${REQS[@]}"; do
    found=0
    for f in "${FILES[@]}"; do
      [ -r "$root/$f" ] || continue
      # A DEFINITION, not a mention: the id at the start of a line or as a bolded list item.
      if grep -Eq "^(- \*\*)?${r}(\*\*)?[:[:space:]]" "$root/$f"; then found=1; break; fi
    done
    if [ "$found" -eq 0 ]; then echo "FAIL: $r is defined in no spec file under $root" >&2; missing=1; fi
  done
  return $missing
}

# Build the pinned negative fixture: the live spec tree with ONE REQ-* removed.
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
for f in "${FILES[@]}"; do
  mkdir -p "$tmp/$(dirname "$f")"
  if [ -r "$REPO/$f" ]; then cp "$REPO/$f" "$tmp/$f"; else : > "$tmp/$f"; fi
done
# Excise REQ-PLAN-080's definition line, leaving every other REQ intact.
grep -v '^REQ-PLAN-080:' "$tmp/skills/yf-plan/spec/phases.md" > "$tmp/.p" 2>/dev/null || true
mv "$tmp/.p" "$tmp/skills/yf-plan/spec/phases.md"

if [ "${CTL_RED:-0}" = "1" ]; then
  predicate "$tmp"; rc=$?
  echo "CTL_RED: predicate over the pinned negative fixture returned $rc (1 = real negative)"
  exit $rc
fi

predicate "$tmp" 2>/dev/null; neg=$?
if [ "$neg" -ne 1 ]; then
  echo "FAIL: the pinned negative fixture did NOT produce a real negative (got $neg)" >&2
  echo "      a control that cannot be RED proves nothing" >&2
  exit 1
fi
echo "ok: pinned negative fixture -> exit 1 (a real negative)"

predicate "$REPO"; live=$?
[ "$live" -eq 2 ] && exit 2
if [ "$live" -ne 0 ]; then
  echo "FAIL: a REQ-* this plan introduces is absent from the live tree" >&2
  exit 1
fi
echo "PASS: all ${#REQS[@]} REQ-* defined on the tree; the negative fixture is a real negative"
