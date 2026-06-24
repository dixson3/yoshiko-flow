# /// script
# requires-python = ">=3.11"
# ///
"""yf-beads-hygiene engine — read-only-first audit + gated repair of a beads graph.

Subcommands:
  audit              Read-only. Build the full universe, resolve every dependency edge via
                     `bd show`, classify each edge, and report. Never mutates.
  repair             Gated repair. Re-run the audit, propose ONLY truly-dangling edge
                     removals, require confirmation, mutate, then verify with `bd dep cycles`.
  restore            Round-trip: re-add edges from a removal record produced by `repair`.

Classification (the #29 contract): every blocking/parent-child edge falls into EXACTLY one of
four classes by resolving its TARGET (the blocker) with `bd show` over the full universe
(which includes gate beads, unlike `bd list`):

  true-orphan     parent-child edge whose target (the molecule root/parent) does not exist.
  truly-dangling  blocks edge whose target does not resolve to any bead.
  satisfied-gate  target is a CLOSED gate bead (harmless; leave it — removing loses provenance).
  live-gate       target is an OPEN gate bead (NOT dangling; MUST be preserved).

The whole point of #29: a live-gate edge must NEVER be reported as dangling. `bd list` hides
gate beads and truncates at 50 rows, so an audit that diffs edges against `bd list` membership
flags live-gate edges as "dangling" and a blind cleanup un-gates live work. This engine
resolves targets with `bd show` and classifies gates by status — never by `bd list` membership.

Direct-CLI gotchas (gate semantics, `bd show` vs `bd list`, edge mutation, defensive JSON
parsing, `bd dep cycles`) live in the `yf-beads-extra` skill — referenced, not restated.

Run:  uv run beads_hygiene.py audit [--json]
      uv run beads_hygiene.py repair [--apply] [--yes] [--record <file>]
      uv run beads_hygiene.py restore --record <file> [--apply]
Tests: uv run --with pytest python3 -m pytest test_beads_hygiene.py -q
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field, asdict

# --- classification constants -------------------------------------------------

TRUE_ORPHAN = "true-orphan"
TRULY_DANGLING = "truly-dangling"
SATISFIED_GATE = "satisfied-gate"
LIVE_GATE = "live-gate"

# Only this class is ever proposed for removal.
REMOVABLE = {TRULY_DANGLING}
# These are never touched, by contract.
PRESERVE = {LIVE_GATE, SATISFIED_GATE, TRUE_ORPHAN}

GATE_TYPE = "gate"
CLOSED_STATUSES = {"closed", "resolved", "done"}
PARENT_CHILD = "parent-child"


# --- defensive bd JSON parsing (see yf-beads-extra) ---------------------------

def parse_bd_json(text: str):
    """Parse `bd ... --json` output defensively.

    `bd` may prepend warning lines and emits an array even for a single id. Returns the
    parsed top-level value (list or dict), or None if nothing parseable is found. See
    yf-beads-extra SKILL.md "`--json` is not always a single JSON document".
    """
    text = (text or "").strip()
    if not text:
        return None
    # Fast path: clean document.
    try:
        return json.loads(text)
    except Exception:
        pass
    # Slow path: extract the first balanced top-level {...} or [...] block.
    for opener, closer in (("[", "]"), ("{", "}")):
        depth = 0
        start = None
        for i, c in enumerate(text):
            if c == opener:
                if depth == 0:
                    start = i
                depth += 1
            elif c == closer and depth:
                depth -= 1
                if depth == 0 and start is not None:
                    try:
                        return json.loads(text[start : i + 1])
                    except Exception:
                        start = None
    return None


def rows_of(value) -> list[dict]:
    """Normalize a parsed bd value to a list of issue dicts."""
    if value is None:
        return []
    if isinstance(value, list):
        return [r for r in value if isinstance(r, dict)]
    if isinstance(value, dict):
        if isinstance(value.get("issues"), list):
            return [r for r in value["issues"] if isinstance(r, dict)]
        return [value]
    return []


# --- bd command layer (only this layer touches the live DB) -------------------

class BdError(RuntimeError):
    pass


def run_bd(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    try:
        proc = subprocess.run(
            ["bd", *args], capture_output=True, text=True, timeout=120
        )
    except FileNotFoundError as e:
        raise BdError("bd not on PATH") from e
    if check and proc.returncode != 0:
        raise BdError(f"bd {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc


def db_is_wedged() -> tuple[bool, str]:
    """Detect a wedged/corrupted DB (route to yf-beads-init, do not clean a broken store).

    The false-negative invariant (BEADS_INIT.md): `bd status --json` can return error JSON
    with exit 0. We treat the DB as wedged when `bd status` fails OR returns an `error` key
    while `bd list`/`bd ready` still work. This engine NEVER repairs config/DB health — it
    only signals the caller to route to yf-beads-init.
    """
    status = run_bd(["status", "--json"], check=False)
    parsed = parse_bd_json(status.stdout)
    status_ok = status.returncode == 0 and not (
        isinstance(parsed, dict) and parsed.get("error")
    )
    if status_ok:
        return False, ""
    # status is unhappy — is the graph still queryable? (init-but-wedged, not uninitialized)
    listing = run_bd(["list", "--all", "--json"], check=False)
    if listing.returncode == 0:
        detail = (parsed or {}).get("error") if isinstance(parsed, dict) else status.stderr
        return True, f"bd status reports a problem but the graph is queryable: {detail}"
    return True, f"bd status failed: {status.stderr.strip()}"


def load_universe() -> dict[str, dict]:
    """Build the FULL bead universe as {id: issue}.

    MUST include gate beads and MUST NOT truncate. `bd list` hides gates and truncates at 50
    rows (yf-beads-extra REQ-CLI-009), so we merge `bd list --all` with `bd list --all
    --type gate`. Both are needed: the first omits gates, the second is gate-only.
    """
    universe: dict[str, dict] = {}
    for extra in ([], ["--type", "gate"]):
        proc = run_bd(["list", "--all", "--json", *extra])
        for row in rows_of(parse_bd_json(proc.stdout)):
            if row.get("id"):
                universe[row["id"]] = row
    return universe


def show(issue_id: str) -> dict | None:
    """Resolve a single bead via `bd show` — sees gates, unlike `bd list`. None if absent."""
    proc = run_bd(["show", issue_id, "--json"], check=False)
    if proc.returncode != 0:
        return None
    rows = rows_of(parse_bd_json(proc.stdout))
    return rows[0] if rows else None


def collect_edges(universe: dict[str, dict], resolver=show) -> list["Edge"]:
    """Enumerate every dependency edge in the universe via `bd show` on each bead.

    `bd show <id> --json` returns a `dependencies` array, each entry a fully-resolved target
    (id, issue_type, status, dependency_type) — INCLUDING gate targets that `bd list` hides.
    The target's existence is confirmed by re-resolving it against the universe and (for the
    truly-dangling check) `bd show`, never by `bd list` membership.
    """
    edges: list[Edge] = []
    for bead_id in sorted(universe):
        detail = resolver(bead_id)
        if not detail:
            continue
        for dep in detail.get("dependencies") or []:
            target_id = dep.get("id")
            if not target_id:
                continue
            # Resolve the target authoritatively: universe first, then bd show (gates).
            target = universe.get(target_id)
            if target is None:
                target = resolver(target_id)
            edges.append(
                Edge(
                    blocked=bead_id,
                    blocker=target_id,
                    dep_type=dep.get("dependency_type") or "blocks",
                    target=target,
                )
            )
    return edges


# --- pure classification core (no I/O — driven by fixtures in tests) ----------

@dataclass
class Edge:
    blocked: str          # the bead that carries the edge (depends on `blocker`)
    blocker: str          # the edge target (id referenced by the dependency)
    dep_type: str         # blocks | parent-child | related | discovered-from
    target: dict | None   # resolved target bead, or None if it does not exist

    def classify(self) -> str:
        """Return exactly one of the four classes. The #29 invariant lives here."""
        if self.target is None:
            # Target does not resolve anywhere. A missing parent (molecule root) is a true
            # orphan; any other missing target is a truly-dangling edge.
            return TRUE_ORPHAN if self.dep_type == PARENT_CHILD else TRULY_DANGLING
        if self.target.get("issue_type") == GATE_TYPE:
            status = (self.target.get("status") or "").lower()
            # CRITICAL (#29): an OPEN gate target is a LIVE gate — never dangling, never removed.
            return SATISFIED_GATE if status in CLOSED_STATUSES else LIVE_GATE
        # Non-gate target that resolves: a healthy edge — not a finding.
        return "healthy"


@dataclass
class AuditReport:
    edges_total: int = 0
    findings: dict[str, list[dict]] = field(default_factory=dict)

    @property
    def removable(self) -> list[dict]:
        return self.findings.get(TRULY_DANGLING, [])

    def to_json(self) -> dict:
        return {
            "edges_total": self.edges_total,
            "counts": {k: len(v) for k, v in self.findings.items()},
            "findings": self.findings,
            "removable_count": len(self.removable),
        }


def classify_edges(edges: list[Edge]) -> AuditReport:
    report = AuditReport(edges_total=len(edges))
    for edge in edges:
        cls = edge.classify()
        if cls == "healthy":
            continue
        report.findings.setdefault(cls, []).append(
            {
                "blocked": edge.blocked,
                "blocker": edge.blocker,
                "dep_type": edge.dep_type,
                "class": cls,
                "target_type": (edge.target or {}).get("issue_type"),
                "target_status": (edge.target or {}).get("status"),
            }
        )
    return report


# --- subcommands --------------------------------------------------------------

def cmd_audit(args) -> int:
    wedged, why = db_is_wedged()
    if wedged:
        return _route_to_init(why, as_json=args.json)
    report = classify_edges(collect_edges(load_universe()))
    if args.json:
        print(json.dumps(report.to_json(), indent=2))
    else:
        _print_human(report)
    return 0


def cmd_repair(args) -> int:
    wedged, why = db_is_wedged()
    if wedged:
        return _route_to_init(why, as_json=False)
    report = classify_edges(collect_edges(load_universe()))
    removable = report.removable
    if not removable:
        print("No truly-dangling edges. Nothing to repair (live/satisfied gates preserved).")
        return 0

    print(f"Proposed removals — {len(removable)} truly-dangling edge(s):")
    for f in removable:
        print(f"  remove: {f['blocked']} depends-on {f['blocker']} (dangling, type={f['dep_type']})")
    preserved = sum(len(v) for k, v in report.findings.items() if k in PRESERVE)
    if preserved:
        print(f"Preserved (never removed): {preserved} live/satisfied-gate / orphan finding(s).")

    if not args.apply:
        print("\nDry run. Re-run with --apply (and --yes to skip the prompt) to mutate.")
        return 0
    if not args.yes and not _confirm(f"Remove {len(removable)} dangling edge(s)?"):
        print("Aborted — no changes made.")
        return 1

    removed = []
    for f in removable:
        run_bd(["dep", "remove", f["blocked"], f["blocker"]])
        removed.append({"blocked": f["blocked"], "blocker": f["blocker"], "dep_type": f["dep_type"]})
    record = {"removed": removed}
    if args.record:
        with open(args.record, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2)
        print(f"Removal record written to {args.record} (restore with: restore --record).")

    # Post-mutation integrity check (yf-beads-extra REQ-CLI-010).
    cycles = run_bd(["dep", "cycles"], check=False)
    print(cycles.stdout.strip() or "bd dep cycles: clean")
    print(
        "\nMutated. Land the plane: bd dolt commit && bd dolt push && git push "
        "(keeps the graph + audit trail consistent)."
    )
    return 0


def cmd_restore(args) -> int:
    with open(args.record, encoding="utf-8") as fh:
        record = json.load(fh)
    removed = record.get("removed", [])
    if not removed:
        print("Nothing to restore (empty record).")
        return 0
    print(f"Restoring {len(removed)} edge(s) from {args.record}:")
    for r in removed:
        print(f"  re-add: {r['blocked']} depends-on {r['blocker']}")
    if not args.apply:
        print("\nDry run. Re-run with --apply to re-add the edges.")
        return 0
    for r in removed:
        # Round-trip the exact edge: `bd dep add <blocked> <blocker>` (yf-beads-extra).
        run_bd(["dep", "add", r["blocked"], r["blocker"]])
    cycles = run_bd(["dep", "cycles"], check=False)
    print(cycles.stdout.strip() or "bd dep cycles: clean")
    print("Edges restored.")
    return 0


def _route_to_init(why: str, *, as_json: bool) -> int:
    msg = (
        "DB appears wedged/corrupted — hygiene operates on graph CONTENT of a HEALTHY DB. "
        "Route to yf-beads-init (verify then repair) before auditing: " + why
    )
    if as_json:
        print(json.dumps({"status": "db_wedged", "route_to": "yf-beads-init", "detail": why}))
    else:
        print(msg)
    return 2


def _confirm(prompt: str) -> bool:
    try:
        return input(f"{prompt} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def _print_human(report: AuditReport) -> None:
    print(f"Audited {report.edges_total} dependency edge(s).")
    order = [TRULY_DANGLING, TRUE_ORPHAN, LIVE_GATE, SATISFIED_GATE]
    if not report.findings:
        print("Clean: no orphans, no dangling edges. (Healthy edges are not listed.)")
        return
    for cls in order:
        items = report.findings.get(cls, [])
        if not items:
            continue
        print(f"\n{cls} ({len(items)}):")
        for f in items:
            print(f"  {f['blocked']} -> {f['blocker']} (type={f['dep_type']}, "
                  f"target={f['target_type']}/{f['target_status']})")
    print(f"\nProposable for removal (truly-dangling only): {len(report.removable)}.")
    if report.findings.get(LIVE_GATE):
        print("Live-gate edges are PRESERVED — removing them would un-gate live work (#29).")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="beads_hygiene.py",
        description="Read-only-first audit + gated repair of a beads dependency graph (#29).",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_audit = sub.add_parser("audit", help="Read-only audit + four-class report.")
    p_audit.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    p_audit.set_defaults(func=cmd_audit)

    p_repair = sub.add_parser("repair", help="Gated removal of truly-dangling edges only.")
    p_repair.add_argument("--apply", action="store_true", help="Actually mutate (default: dry run).")
    p_repair.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")
    p_repair.add_argument("--record", help="Write a removal record for round-trip restore.")
    p_repair.set_defaults(func=cmd_repair)

    p_restore = sub.add_parser("restore", help="Re-add edges from a removal record.")
    p_restore.add_argument("--record", required=True, help="Removal record from `repair`.")
    p_restore.add_argument("--apply", action="store_true", help="Actually re-add (default: dry run).")
    p_restore.set_defaults(func=cmd_restore)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except BdError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
