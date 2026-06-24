#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""beads-upstream helper: enumerate push candidates, read External: mappings,
read upstream config knobs, and hoist / un-hoist beads against an upstream tracker.

Subcommands the SKILL.md push / reconcile steps call:

  enumerate [--json]            List open+blocked+deferred beads (push candidates),
                                flagging those that already carry an upstream
                                `External:` mapping.
  mappings --issues <csv> [--json]
                                For each bead ID, report its `External:` upstream
                                URL (or null if unmapped).
  granularity [--json]          Report custom.upstream.granularity (coarse|granular),
                                default coarse.
  config [--json]               Report the upstream config knobs (granularity,
                                auto_hoist_followons).
  followons --parent <id> --intake <rfc3339> [--json]
                                Detect follow-on beads under a plan subtree; returns
                                the narrow (auto-eligible) and broad (gated-only) sets.
  hoist --issues <csv> --dest <plan-or-url> [--backend gh] [--apply]
                                Ensure an upstream issue exists per granularity, then
                                close the bead(s) locally with a destination-recording
                                reason. Dry-run (emit-only) by default; --apply executes.
  unhoist (--issues <csv> | --record <file>) [--apply]
                                Reopen wrongly-hoisted bead(s) from their tombstone.
                                Dry-run by default; --apply executes.

`bd list --json` may be a multi-document array and may carry warning prefixes on
stdout; we parse defensively (see the `beads-extra` skill → defensive JSON). The
upstream mapping is read from `bd show <id>` text — a single line anchored as
`External: <url>` — verified stable on bd 1.0.5.

SAFETY INVARIANTS preserved (see spec/safety.md):
  - Removal is `bd close -r` (reversible tombstone), NEVER `bd delete`.
  - Hoist ALWAYS dry-runs the push first (`bd <backend> push <ids> --dry-run`)
    before the real push (REQ-BUP-013 / REQ-SAFE-001).
  - Never a bare `bd <backend> sync` — push is scoped to explicit `--issues`.
  - Auth is inline-only (`GITHUB_TOKEN=$(gh auth token) bd github push …`),
    never written to config.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

CANDIDATE_STATUSES = "open,blocked,deferred"
# Anchored: real mapping line starts the line and is a URL — avoids matching the
# word "External:" inside a description body.
EXTERNAL_RE = re.compile(r"^\s*External:\s*(https?://\S+)", re.MULTILINE)

# Statuses that count as "non-active" for follow-on auto-eligibility (a bead that
# is in_progress is being worked and is never auto-hoisted).
NONACTIVE_STATUSES = frozenset({"open", "blocked", "deferred"})

# Recognized granularity values; anything else (or unset) falls back to coarse.
VALID_GRANULARITIES = frozenset({"coarse", "granular"})
DEFAULT_GRANULARITY = "coarse"

# `bd config get <key>` prints this literal on stdout (exit 0) when a key is unset.
# NEVER trust exit code — the false-negative invariant.
NOT_SET_SENTINEL = "(not set)"


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd)}")
    return proc.stdout


def _config_get(key: str) -> str:
    """Read a bd config value as raw stdout text (may be `(not set)`).

    Tolerates a non-zero exit (treated as unset) — we never branch on the exit
    code for the unset decision; inspection of the text is authoritative.
    """
    proc = subprocess.run(["bd", "config", "get", key], capture_output=True, text=True)
    return proc.stdout


def granularity(config_get=_config_get) -> str:
    """Return custom.upstream.granularity, defaulting to coarse.

    Unset (`(not set)` substring) or any unrecognized value → coarse.
    `config_get` is injectable so this is unit-testable without shelling out.
    """
    raw = config_get("custom.upstream.granularity")
    if raw is None or NOT_SET_SENTINEL in raw:
        return DEFAULT_GRANULARITY
    value = raw.strip()
    return value if value in VALID_GRANULARITIES else DEFAULT_GRANULARITY


def auto_hoist_followons(config_get=_config_get) -> bool:
    """Return True only when custom.upstream.auto_hoist_followons is literal "true".

    Default-DENY: unset / empty / "false" / any other value → False. Mirrors the
    custom.upstream.enabled short-circuit shape. `config_get` is injectable.
    """
    raw = config_get("custom.upstream.auto_hoist_followons")
    if raw is None or NOT_SET_SENTINEL in raw:
        return False
    return raw.strip() == "true"


def parse_json_array(text: str) -> list[dict]:
    """Defensive parse of `bd ... --json`. Returns a list of issue dicts.

    Tolerates a warning prefix before the JSON and both shapes (top-level array,
    or {"issues":[...]}/single object). Falls back to extracting the first
    balanced [...] / {...} block if a direct load fails.
    """
    for candidate in (text, _first_balanced(text)):
        if not candidate:
            continue
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("issues", [data])
    return []


def _first_balanced(text: str) -> str | None:
    open_ch = None
    for opener, closer in (("[", "]"), ("{", "}")):
        i = text.find(opener)
        if i != -1 and (open_ch is None or i < open_ch[1]):
            open_ch = (opener, i, closer)
    if open_ch is None:
        return None
    opener, start, closer = open_ch
    depth = 0
    for j in range(start, len(text)):
        if text[j] == opener:
            depth += 1
        elif text[j] == closer:
            depth -= 1
            if depth == 0:
                return text[start : j + 1]
    return None


def external_for(bead_id: str) -> str | None:
    out = run(["bd", "show", bead_id])
    m = EXTERNAL_RE.search(out)
    return m.group(1) if m else None


CONTAINER_TYPES = frozenset({"epic", "molecule", "gate"})


def candidate_filter(rows: list[dict]) -> list[dict]:
    """Pure: drop container types (epic/molecule/gate); keep real work items.

    Factored out of cmd_enumerate so it is unit-testable without a live bd.
    """
    return [r for r in rows if r.get("issue_type") not in CONTAINER_TYPES]


def cmd_enumerate(as_json: bool) -> int:
    rows = parse_json_array(run(["bd", "list", "--status", CANDIDATE_STATUSES, "--json"]))
    # Skip container types — only push real work items.
    rows = candidate_filter(rows)
    out = []
    for r in rows:
        bid = r.get("id")
        if not bid:
            continue
        ext = external_for(bid)
        out.append(
            {
                "id": bid,
                "title": r.get("title", ""),
                "status": r.get("status", ""),
                "type": r.get("issue_type", ""),
                "mapped": ext is not None,
                "external": ext,
            }
        )
    if as_json:
        print(json.dumps(out, indent=2))
    else:
        unmapped = [r for r in out if not r["mapped"]]
        print(f"{len(out)} candidate(s) (open/blocked/deferred); {len(unmapped)} not yet mapped:")
        for r in out:
            flag = r["external"] if r["mapped"] else "—"
            print(f"  {r['id']:<16} [{r['status']}/{r['type']}] {r['title']}  ({flag})")
    return 0


def cmd_mappings(issues_csv: str, as_json: bool) -> int:
    ids = [s.strip() for s in issues_csv.split(",") if s.strip()]
    out = [{"id": bid, "external": external_for(bid)} for bid in ids]
    if as_json:
        print(json.dumps(out, indent=2))
    else:
        for r in out:
            print(f"  {r['id']:<16} {r['external'] or '(unmapped)'}")
    return 0


# --- follow-on detection (C.2) -----------------------------------------------

def edge_type(dep: dict) -> str | None:
    """Return the edge type, handling the field-name divergence.

    `bd show --json` uses `dependency_type`; `bd dep list --json` uses `type`.
    Accept either so callers don't care which query produced the dep dict.
    """
    return dep.get("dependency_type") or dep.get("type")


def is_nonactive(bead: dict) -> bool:
    """A bead is non-active when its status is open/blocked/deferred AND, for
    open beads, it is unclaimed (no owner). in_progress is always active."""
    status = bead.get("status")
    if status not in NONACTIVE_STATUSES:
        return False
    if status == "open" and (bead.get("owner") or "").strip():
        return False  # claimed open bead is active
    return True


def detect_followons(
    parent_id: str,
    intake_ts: str,
    *,
    list_subtree,
    deps_for,
):
    """Detect follow-on beads under a plan subtree.

    Returns a dict with two SEPARATE sets:
      - "narrow": auto-eligible — carries a `discovered-from` edge pointing into
        the subtree AND is non-active. The no-prompt path uses ONLY this set.
      - "broad": gated-proposal-only — created under the subtree after the epic's
        intake timestamp (may catch a bead still being worked, so never unattended).

    Injectable query layer (unit-testable, no live bd):
      list_subtree(parent_id) -> list[bead-dict]  (descendants of the subtree)
      deps_for(bead_id)       -> list[dep-dict]    (the bead's dependency edges)
    """
    subtree = list_subtree(parent_id)
    subtree_ids = {b.get("id") for b in subtree if b.get("id")}

    narrow, broad = [], []
    for bead in subtree:
        bid = bead.get("id")
        if not bid:
            continue
        # Narrow: discovered-from edge into the subtree AND non-active.
        deps = deps_for(bid)
        discovered_into_subtree = any(
            edge_type(d) == "discovered-from"
            and (d.get("depends_on_id") or d.get("target") or d.get("to")) in subtree_ids
            for d in deps
        )
        if discovered_into_subtree and is_nonactive(bead):
            narrow.append(bid)
        # Broad: created after intake under the subtree (regardless of activity).
        created = bead.get("created_at") or bead.get("created", "")
        if intake_ts and created and created > intake_ts:
            broad.append(bid)

    return {"narrow": narrow, "broad": broad}


# --- hoist / un-hoist command planning (C.1 / C.4) ---------------------------

def hoist_issue_count(bead_ids: list[str], gran: str) -> int:
    """Number of upstream issues a hoist would ensure: coarse → 1 per plan,
    granular → 1 per bead."""
    if gran == "granular":
        return len(bead_ids)
    return 1 if bead_ids else 0


def close_reason(dest: str) -> str:
    """The close_reason recording the upstream destination (reversible tombstone)."""
    return f"hoisted upstream to {dest} (reversible tombstone; un-hoist to restore)"


# Map the bd push backend -> (auth-token CLI, env var) for inline auth.
BACKEND_AUTH = {
    "github": ("gh", "GITHUB_TOKEN"),
    "gitlab": ("glab", "GITLAB_TOKEN"),
}
DEFAULT_BACKEND = "github"


def plan_hoist(bead_ids: list[str], dest: str, *, backend: str, gran: str) -> list[str]:
    """Build the EXACT command sequence a hoist would run (no execution).

    `backend` is the bd push backend (github|gitlab). ALWAYS emits the dry-run
    push first, then the real push, then per-bead reversible close. Auth is
    inline-only (never written to config). Used both for the dry-run preview and
    as the command list executed under --apply.
    """
    ids_csv = ",".join(bead_ids)
    auth_cli, env_var = BACKEND_AUTH.get(backend, ("gh", "GITHUB_TOKEN"))
    auth = f"{env_var}=$({auth_cli} auth token)"
    cmds: list[str] = []
    # 1. Dry-run the push FIRST (REQ-BUP-013 / REQ-SAFE-001) — scoped, never bare sync.
    cmds.append(f"{auth} bd {backend} push {ids_csv} --dry-run")
    # 2. Real push (create-or-map via External:; dedup keeps coarse trackers).
    cmds.append(f"{auth} bd {backend} push {ids_csv}")
    # 3. Remove locally — reversible tombstone, never bd delete.
    reason = close_reason(dest)
    for bid in bead_ids:
        cmds.append(f'bd close {bid} -r "{reason}"')
    return cmds


def plan_unhoist(bead_ids: list[str]) -> list[str]:
    """Build the command sequence to reopen wrongly-hoisted bead(s) from their
    tombstone. The upstream issue stays; only the local bead is reopened."""
    return [f"bd update {bid} --status open" for bid in bead_ids]


def cmd_granularity(as_json: bool) -> int:
    gran = granularity()
    if as_json:
        print(json.dumps({"granularity": gran}, indent=2))
    else:
        print(f"custom.upstream.granularity = {gran}")
    return 0


def cmd_config(as_json: bool) -> int:
    cfg = {
        "granularity": granularity(),
        "auto_hoist_followons": auto_hoist_followons(),
    }
    if as_json:
        print(json.dumps(cfg, indent=2))
    else:
        print(f"granularity           = {cfg['granularity']}")
        print(f"auto_hoist_followons  = {cfg['auto_hoist_followons']}")
    return 0


def cmd_followons(parent_id: str, intake_ts: str, as_json: bool) -> int:
    def list_subtree(pid: str) -> list[dict]:
        return parse_json_array(
            run(["bd", "list", "--parent", pid, "--all", "--json"])
        )

    def deps_for(bid: str) -> list[dict]:
        return parse_json_array(run(["bd", "dep", "list", bid, "--json"]))

    result = detect_followons(
        parent_id, intake_ts, list_subtree=list_subtree, deps_for=deps_for
    )
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"narrow (auto-eligible): {len(result['narrow'])} -> {result['narrow']}")
        print(f"broad  (gated-only)   : {len(result['broad'])} -> {result['broad']}")
    return 0


def cmd_hoist(issues_csv: str, dest: str, backend: str, apply: bool) -> int:
    ids = [s.strip() for s in issues_csv.split(",") if s.strip()]
    if not ids:
        print("No bead IDs given; nothing to hoist.")
        return 1
    gran = granularity()
    n_issues = hoist_issue_count(ids, gran)
    cmds = plan_hoist(ids, dest, backend=backend, gran=gran)

    print(f"Hoist plan ({gran}): {len(ids)} bead(s) -> {n_issues} upstream issue(s) at {dest}")
    print("Command sequence (dry-run push always runs first):")
    for c in cmds:
        print(f"  {c}")
    if not apply:
        print("\nDry run. Re-run with --apply to execute the sequence above.")
        return 0
    for c in cmds:
        print(f"+ {c}")
        run(["bash", "-c", c])
    print("Hoist complete (beads closed with reversible tombstone reason).")
    return 0


def cmd_unhoist(issues_csv: str | None, record: str | None, apply: bool) -> int:
    if record:
        with open(record, encoding="utf-8") as fh:
            ids = [line.strip() for line in fh if line.strip()]
    else:
        ids = [s.strip() for s in (issues_csv or "").split(",") if s.strip()]
    if not ids:
        print("No bead IDs to un-hoist.")
        return 1
    cmds = plan_unhoist(ids)
    print(f"Un-hoist plan: reopen {len(ids)} bead(s) from tombstone (upstream issue stays):")
    for c in cmds:
        print(f"  {c}")
    if not apply:
        print("\nDry run. Re-run with --apply to reopen the bead(s).")
        return 0
    for c in cmds:
        print(f"+ {c}")
        run(["bash", "-c", c])
    print("Un-hoist complete.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="beads-upstream push helpers.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_enum = sub.add_parser("enumerate", help="list open/blocked/deferred push candidates")
    p_enum.add_argument("--json", action="store_true", dest="as_json")

    p_map = sub.add_parser("mappings", help="report External: mappings for given bead IDs")
    p_map.add_argument("--issues", required=True, help="comma-separated bead IDs")
    p_map.add_argument("--json", action="store_true", dest="as_json")

    p_gran = sub.add_parser("granularity", help="report custom.upstream.granularity (default coarse)")
    p_gran.add_argument("--json", action="store_true", dest="as_json")

    p_cfg = sub.add_parser("config", help="report upstream config knobs")
    p_cfg.add_argument("--json", action="store_true", dest="as_json")

    p_fo = sub.add_parser("followons", help="detect follow-on beads under a plan subtree")
    p_fo.add_argument("--parent", required=True, help="plan molecule/epic id")
    p_fo.add_argument("--intake", required=True, help="epic intake timestamp (RFC3339)")
    p_fo.add_argument("--json", action="store_true", dest="as_json")

    p_hoist = sub.add_parser("hoist", help="ensure upstream issue per granularity, then close locally")
    p_hoist.add_argument("--issues", required=True, help="comma-separated bead IDs")
    p_hoist.add_argument("--dest", required=True, help="plan id or upstream URL recorded in close reason")
    p_hoist.add_argument("--backend", default=DEFAULT_BACKEND, help="bd push backend (default: github)")
    p_hoist.add_argument("--apply", action="store_true", help="Execute (default: dry-run/plan only).")

    p_unh = sub.add_parser("unhoist", help="reopen wrongly-hoisted bead(s) from tombstone")
    p_unh.add_argument("--issues", help="comma-separated bead IDs")
    p_unh.add_argument("--record", help="file of hoisted bead IDs (one per line) for batch round-trip")
    p_unh.add_argument("--apply", action="store_true", help="Execute (default: dry-run/plan only).")

    args = parser.parse_args()
    if args.cmd == "enumerate":
        return cmd_enumerate(args.as_json)
    if args.cmd == "mappings":
        return cmd_mappings(args.issues, args.as_json)
    if args.cmd == "granularity":
        return cmd_granularity(args.as_json)
    if args.cmd == "config":
        return cmd_config(args.as_json)
    if args.cmd == "followons":
        return cmd_followons(args.parent, args.intake, args.as_json)
    if args.cmd == "hoist":
        return cmd_hoist(args.issues, args.dest, args.backend, args.apply)
    if args.cmd == "unhoist":
        if not args.issues and not args.record:
            parser.error("unhoist requires --issues or --record")
        return cmd_unhoist(args.issues, args.record, args.apply)
    return 1


if __name__ == "__main__":
    sys.exit(main())
