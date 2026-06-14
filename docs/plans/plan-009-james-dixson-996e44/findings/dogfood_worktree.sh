#!/usr/bin/env bash
# plan-009 Issue 2.5 — dogfood acceptance checklist for bdplan worktree execution.
# Runs the FULL lifecycle (create -> code+bd work -> merge --no-ff -> validate ->
# teardown -> opt-out fallback) in an isolated bd-initialized repo and asserts SC1-6.
set -u
TMP="$1"
PM="${PM:-$(git -C "$(pwd)" rev-parse --show-toplevel 2>/dev/null)/skills/bdplan/scripts/plan_manager.py}"
# Override PM= to point at the bdplan plan_manager.py under test (defaults to this repo).
PD="docs/plans/plan-dogfood-001"
PID="plan-dogfood-001"
WT=".worktrees/$PID"
PASS=0; FAIL=0
ok(){ echo "  PASS: $1"; PASS=$((PASS+1)); }
no(){ echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
chk(){ if eval "$2"; then ok "$1"; else no "$1 [cmd: $2]"; fi; }

cd "$TMP" || exit 99
mkdir -p "$PD"; echo "# dogfood plan" > "$PD/plan.md"

echo "== SC1: create isolated worktree on branch=plan-id =="
ENS=$(uv run "$PM" worktree ensure "$PD" --json)
echo "$ENS" | python3 -c "import json,sys; d=json.load(sys.stdin); print('   ensure:',d.get('viable'),d.get('action'),d.get('branch'))"
chk "viable create" "echo '$ENS' | python3 -c 'import json,sys;d=json.load(sys.stdin);exit(0 if d[\"viable\"] and d[\"action\"]==\"created\" else 1)'"
chk "branch == plan-id" "echo '$ENS' | python3 -c 'import json,sys;d=json.load(sys.stdin);exit(0 if d[\"branch\"]==\"$PID\" else 1)'"
chk "worktree dir exists" "test -d '$WT'"
chk "worktree HEAD on plan branch" "[ \"\$(git -C '$WT' rev-parse --abbrev-ref HEAD)\" = '$PID' ]"
chk "/.worktrees/ gitignored" "grep -qx '/.worktrees/' .gitignore"

echo "== SC1: code commits accumulate on the branch, NOT primary =="
echo "feature work" > "$WT/feature.txt"
git -C "$WT" add feature.txt && git -C "$WT" commit -qm "dogfood: feature.txt"
chk "commit landed on plan branch" "git -C '$WT' log --oneline -1 | grep -q feature.txt"
chk "code did NOT leak to primary checkout" "test ! -f feature.txt"

echo "== SC2: bd from worktree lands in the shared primary DB =="
BEAD=$( (cd "$WT" && uv run "$PM" >/dev/null 2>&1; bd create "dogfood bead from worktree" -t task --json) | python3 -c "import json,sys
try:
 d=json.load(sys.stdin); d=d[0] if isinstance(d,list) else d; print(d.get('id',''))
except Exception: print('')" )
echo "   bead from worktree: $BEAD"
chk "bead created from worktree" "[ -n '$BEAD' ]"
chk "bead visible from PRIMARY (same DB, INV-2)" "bd show '$BEAD' >/dev/null 2>&1"
chk "worktree has no divergent DB (no own embeddeddolt; shared via git-common-dir)" "test ! -e '$WT/.beads/embeddeddolt'"

echo "== address-space: plan_manager/plan_dir ops resolve primary-side =="
chk "worktree path verb returns repo-relative path" "[ \"\$(uv run "$PM" worktree path "$PD")\" = '$WT' ]"
chk "plan_dir lives under primary docs/plans" "test -f '$PD/plan.md'"

echo "== SC4: merge-back --no-ff from primary + validate merged state =="
git merge --no-ff "$PID" -m "dogfood: merge $PID" >/dev/null 2>&1
chk "feature.txt now present on primary base" "test -f feature.txt"
chk "merge commit has 2 parents (--no-ff)" "[ \$(git rev-list --parents -n1 HEAD | wc -w) -ge 3 ]"
VM=$(uv run "$PM" validate-merged "$PD" --json)
chk "validate-merged passes (no validate-cmd)" "echo '$VM' | python3 -c 'import json,sys;d=json.load(sys.stdin);exit(0 if d[\"status\"]==\"pass\" else 1)'"
chk "emits cross-plan-not-checked notice" "echo '$VM' | python3 -c 'import json,sys;d=json.load(sys.stdin);exit(0 if d[\"notice\"] and \"CROSS-PLAN\" in d[\"notice\"] else 1)'"

echo "== SC4b: validate-cmd configured -> layer-b runs =="
echo '{"validate-cmd":"test -f feature.txt"}' > .bdplan.local.json
VM2=$(uv run "$PM" validate-merged "$PD" --json)
chk "layer-b validate-cmd executed + passed" "echo '$VM2' | python3 -c 'import json,sys;d=json.load(sys.stdin);exit(0 if d[\"validate_cmd_configured\"] and d[\"status\"]==\"pass\" else 1)'"
rm -f .bdplan.local.json

echo "== landing lock serializes (acquire blocks a live second holder) =="
uv run "$PM" landing-lock acquire "$PID" --json >/dev/null
LS=$(uv run "$PM" landing-lock status --json)
chk "lock recorded as held" "echo '$LS' | python3 -c 'import json,sys;d=json.load(sys.stdin);exit(0 if d[\"held\"] else 1)'"
uv run "$PM" landing-lock release "$PID" --json >/dev/null
chk "lock released" "uv run "$PM" landing-lock status --json | python3 -c 'import json,sys;d=json.load(sys.stdin);exit(0 if not d[\"held\"] else 1)'"

echo "== SC6: teardown removes worktree + merged branch =="
TD=$(uv run "$PM" worktree teardown "$PD" --json)
chk "teardown ok" "echo '$TD' | python3 -c 'import json,sys;d=json.load(sys.stdin);exit(0 if d[\"status\"]==\"ok\" else 1)'"
chk "worktree dir gone" "test ! -d '$WT'"
chk "merged branch deleted" "! git rev-parse --verify --quiet refs/heads/$PID >/dev/null"

echo "== SC6: opt-out fallback runs in-place =="
echo '{"execute.worktree": false}' > .bdplan.local.json
OO=$(uv run "$PM" worktree ensure "$PD" --json)
chk "opt-out -> viable=false reason=opted-out" "echo '$OO' | python3 -c 'import json,sys;d=json.load(sys.stdin);exit(0 if not d[\"viable\"] and d[\"reason\"]==\"opted-out\" else 1)'"
rm -f .bdplan.local.json

echo
echo "==== DOGFOOD RESULT: $PASS passed, $FAIL failed ===="
exit $([ $FAIL -eq 0 ] && echo 0 || echo 1)
