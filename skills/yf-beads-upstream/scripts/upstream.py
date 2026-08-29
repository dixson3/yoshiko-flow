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
  hoist --issues <csv> --dest <plan-or-url> [--apply]
                                Ensure an upstream issue exists per granularity, then
                                close the bead(s) locally with a destination-recording
                                reason. Dry-run (emit-only) by default; --apply executes.
  land --parent <id> --intake <rfc3339> --dest <plan-or-url> [--apply]
                                Land-the-plane: detect follow-on beads under the subtree
                                and hoist them. DEFAULT proposes the batch for a single
                                confirm; the NO-PROMPT path runs only when
                                custom.upstream.auto_hoist_followons is true and is
                                restricted to the NARROW signal set.
  unhoist (--issues <csv> | --record <file>) [--apply]
                                Reopen wrongly-hoisted bead(s) from their tombstone.
                                Dry-run by default; --apply executes.

`bd list --json` may be a multi-document array and may carry warning prefixes on
stdout; we parse defensively (see the `beads-extra` skill → defensive JSON). The
upstream mapping is read from `bd show <id>` text — a single line anchored as
`External: <url>` — verified stable on bd 1.0.5.

WRITES ARE gh-DIRECT (REQ-BUP-057, plan-040). `bd` reads bead content, `gh` creates or
edits the issue, and `bd update --external-ref` records the mapping. GitHub is the only
supported backend — the `--backend` flag and the per-backend auth table are gone.

SAFETY INVARIANTS preserved (see spec/safety.md):
  - Removal is `bd close -r` (reversible tombstone), NEVER `bd delete`.
  - NO `bd <backend>` write command is issued at all — not a bare sync, not a scoped
    push. Every write is scoped to explicit ids and PREVIEWED FIRST: absent `--apply`
    the plan is rendered LOCALLY (no round-trip, no credentials needed to read it).
  - Verification is STRUCTURAL — a returned issue URL on create, a clean exit on edit —
    never a scraped success line. An unverified write raises WriteError and HALTS
    before the destructive local-close stage (REQ-BUP-050's contract, new evidence).
  - Auth is `gh`'s own credential store; this script handles NO token (REQ-BUP-031).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass, field

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


class UpstreamQueryError(RuntimeError):
    """A network/`gh` read failed. Yields INCONCLUSIVE, never a clean proposal."""


def run_unchecked(cmd: list[str]) -> str:
    """Run `cmd` WITHOUT the fail-fast `SystemExit` of [`run`].

    plan-044 Issue 3.2. `run()` raises `SystemExit` on any non-zero exit, which made
    REQ-BUP-064's INCONCLUSIVE verdict UNREACHABLE — a `gh` failure killed the process
    instead of producing a verdict. This is a NEW, separate call path used only by the
    bulk upstream-state resolver; every existing caller keeps `run()` and its fail-fast
    semantics untouched, so nothing else changes behavior.
    """
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError as e:
        raise UpstreamQueryError(f"{cmd[0]} not on PATH") from e
    if proc.returncode != 0:
        raise UpstreamQueryError(
            f"command failed ({proc.returncode}): {' '.join(cmd)}: {proc.stderr.strip()}"
        )
    return proc.stdout


# Sentinel for a mapped ref that the bulk query did not return: a deleted issue, a
# typo'd ref, or one belonging to another repo. These are INDISTINGUISHABLE by this
# signal, which is exactly why they all route to a human and never to an auto-close
# (REQ-BUP-064).
UNRESOLVABLE = "UNRESOLVABLE"


@dataclass
class UpstreamStates:
    """Resolved upstream states, plus whether the read itself succeeded."""

    states: dict = field(default_factory=dict)
    inconclusive: bool = False
    error: str | None = None

    def __getitem__(self, key):
        return self.states[key]

    def __contains__(self, key):
        return key in self.states

    def get(self, key, default=None):
        return self.states.get(key, default)


def resolve_upstream_states(numbers, runner=None) -> UpstreamStates:
    """Resolve issue states with ONE bulk query (REQ-BUP-060).

    `gh issue list --state all --json number,state` returns the whole set in a single
    round trip, so a mapped ref ABSENT from the result classifies as `UNRESOLVABLE` at
    zero extra cost — no per-issue probe needed to discover it.

    On a `gh` failure the verdict is INCONCLUSIVE (REQ-BUP-064), never an empty-and-
    therefore-clean result. That distinction is load-bearing for a verb whose proposal
    needs a network read: an empty proposal is indistinguishable from "nothing to do"
    and reads as success.
    """
    numbers = [n for n in (normalize_external_ref(x) for x in numbers) if n is not None]
    call = runner or (
        lambda cmd: run_unchecked(cmd)
    )
    cmd = ["gh", "issue", "list", "--state", "all", "--limit", "1000",
           "--json", "number,state"]
    try:
        raw = call(cmd)
    except (UpstreamQueryError, OSError) as e:
        return UpstreamStates(states={}, inconclusive=True, error=str(e))

    try:
        rows = json.loads(raw) if isinstance(raw, str) else raw
    except (json.JSONDecodeError, TypeError) as e:
        return UpstreamStates(states={}, inconclusive=True, error=f"unparseable gh output: {e}")

    by_num = {int(r["number"]): str(r.get("state", "")).upper() for r in rows or []}
    return UpstreamStates(
        states={n: by_num.get(n, UNRESOLVABLE) for n in numbers},
        inconclusive=False,
    )


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


def upstream_enabled(config_get=_config_get) -> bool:
    """Return True only when upstream tracking is actually enabled (REQ-BUP-010).

    Default-DENY: `custom.upstream.enabled` must be the literal "true"; unset / empty /
    "false" / any other value resolves disabled. Backend `none` also disables, matching
    the documented test ("unconfigured, `false`, or backend `none`").

    An UNSET backend does NOT disable — the docs are explicit that the explicit `none`
    marker is never required for the short-circuit, so only an explicit `none` (or an
    empty value) counts. Reads the config TEXT for the `(not set)` sentinel, never the
    exit code (the false-negative invariant). `config_get` is injectable.
    """
    raw = config_get("custom.upstream.enabled")
    if raw is None or NOT_SET_SENTINEL in raw or raw.strip() != "true":
        return False
    backend = config_get("custom.upstream.backend")
    if backend is None or NOT_SET_SENTINEL in backend:
        return True  # unset backend is not a disable signal (see docstring)
    return backend.strip() not in ("", "none")


def owner_on_create(config_get=_config_get) -> bool:
    """Return True only when custom.upstream.owner_on_create is literal "true" (#61, REQ-BUP-048).

    Default-DENY: unset / empty / "false" / any other value → False. Mirrors the
    auto_hoist_followons short-circuit shape (reads the config text for the `(not set)`
    sentinel, never the exit code). Set it in repos where `bd create` auto-assigns an owner,
    so enumerate does not read every open bead as claimed→active→excluded. `config_get` is
    injectable.
    """
    raw = config_get("custom.upstream.owner_on_create")
    if raw is None or NOT_SET_SENTINEL in raw:
        return False
    return raw.strip() == "true"


# >>> BEGIN active-set classifier (generated by _shared/sync.py — do not edit) >>>
GATE_TYPE = "gate"
CLOSED_STATUSES = {"closed", "resolved", "done"}
PARENT_CHILD = "parent-child"

IN_PROGRESS = "in_progress"
OPEN = "open"

# Reasons a bead is classified ACTIVE (one of these holds).
ACTIVE_IN_PROGRESS = "in_progress"           # status == in_progress
ACTIVE_CLAIMED = "open_claimed"              # status == open AND owner non-empty
ACTIVE_ANCESTOR = "open_ancestor_of_active"  # open parent-chain ancestor of an active bead


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
            return "true-orphan" if self.dep_type == PARENT_CHILD else "truly-dangling"
        if self.target.get("issue_type") == GATE_TYPE:
            status = (self.target.get("status") or "").lower()
            # CRITICAL (#29): an OPEN gate target is a LIVE gate — never dangling, never removed.
            return "satisfied-gate" if status in CLOSED_STATUSES else "live-gate"
        # Non-gate target that resolves: a healthy edge — not a finding.
        return "healthy"


@dataclass
class ActiveSetReport:
    """Partition of non-closed beads into active vs non-active.

    Closed beads are EXCLUDED (neither active nor non-active). `reasons` maps every
    classified bead id to the reason string it was placed in its bucket.
    """
    active: list[str] = field(default_factory=list)
    non_active: list[str] = field(default_factory=list)
    reasons: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> dict:
        return {
            "active": self.active,
            "non_active": self.non_active,
            "reasons": self.reasons,
            "active_count": len(self.active),
            "non_active_count": len(self.non_active),
        }


def _is_closed(bead: dict) -> bool:
    return (bead.get("status") or "").lower() in CLOSED_STATUSES


def _has_owner(bead: dict) -> bool:
    return bool((bead.get("owner") or "").strip())


def _directly_active(bead: dict) -> str | None:
    """Return the active-reason if a bead is directly active, else None.

    Directly active = status==in_progress, OR (status==open AND owner claimed). The
    ancestor case is resolved by the caller (it requires the full graph).
    """
    status = (bead.get("status") or "").lower()
    if status == IN_PROGRESS:
        return ACTIVE_IN_PROGRESS
    if status == OPEN and _has_owner(bead):
        return ACTIVE_CLAIMED
    return None


def classify_active(beads: dict[str, dict], edges: list[Edge]) -> ActiveSetReport:
    """Partition beads into active vs non-active per the plan-013 glossary (pure, no I/O).

    ACTIVE when, for a bead:
      - status == in_progress; OR
      - status == open AND owner non-empty (claimed); OR
      - it is an OPEN parent-chain ancestor (walk `parent-child` edges upward) of an
        active bead.
    Non-active = every other non-closed bead (open-unclaimed, blocked, deferred).
    Closed beads are EXCLUDED from both buckets.

    `beads` is {id: bead-dict}; `edges` is the resolved Edge set (a parent-child edge has
    blocked=child, blocker=parent — same shape collect_edges produces). This consumes the
    `dep_type` field uniformly, so it is agnostic to the `dependency_type`/`type` source
    divergence (collect_edges already normalizes to `dep_type`).
    """
    # child -> set(parent) from parent-child edges (blocked=child depends-on blocker=parent).
    parents: dict[str, set[str]] = {}
    for e in edges:
        if e.dep_type == PARENT_CHILD:
            parents.setdefault(e.blocked, set()).add(e.blocker)

    # Seed: directly-active beads.
    reasons: dict[str, str] = {}
    for bid, bead in beads.items():
        if _is_closed(bead):
            continue
        r = _directly_active(bead)
        if r is not None:
            reasons[bid] = r

    # Propagate up the parent chain: an OPEN ancestor of any active bead is itself active.
    # Iterate to a fixed point so transitive ancestors (epic of a molecule of a task) are caught.
    changed = True
    while changed:
        changed = False
        for child in list(reasons):
            for parent in parents.get(child, ()):  # noqa: SIM118
                pbead = beads.get(parent)
                if pbead is None or _is_closed(pbead):
                    continue
                # Only an OPEN ancestor is promoted (per glossary). in_progress/claimed
                # ancestors are already seeded directly; we never demote a stronger reason.
                if parent not in reasons and (pbead.get("status") or "").lower() == OPEN:
                    reasons[parent] = ACTIVE_ANCESTOR
                    changed = True

    report = ActiveSetReport()
    for bid, bead in beads.items():
        if _is_closed(bead):
            continue
        if bid in reasons:
            report.active.append(bid)
            report.reasons[bid] = reasons[bid]
        else:
            report.non_active.append(bid)
            report.reasons[bid] = "non_active"
    report.active.sort()
    report.non_active.sort()
    return report
# <<< END active-set classifier <<<


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


def normalize_external_ref(ref) -> int | None:
    """Normalize any spelling of an `external_ref` to an ISSUE NUMBER (REQ-BUP-062).

    The defect this closes: `external_for()` matched a URL only, while
    `external_from_row()` returned any non-empty string. Two readers disagreeing about
    what a ref MEANS is worse than either being wrong — a bead written `gh-91` was
    mapped by one reader and invisible to the other, so it was silently omitted from
    exactly the sweep meant to catch it. (Live instance: `yf-4d7s` = `"gh-91"`.)

    Accepted spellings, all resolving to the same number:

        https://github.com/o/r/issues/91   ->  91
        gh-91                              ->  91
        #91                                ->  91
        91                                 ->  91

    Returns `None` for anything uninterpretable, which the caller must REPORT rather
    than drop (REQ-BUP-063) — an unparseable ref is a finding for a human, not an
    absence.
    """
    if ref is None:
        return None
    text = str(ref).strip()
    if not text:
        return None
    # URL form: trailing /<digits>, tolerating a trailing slash.
    m = re.search(r"/(\d+)/?$", text)
    if m:
        return int(m.group(1))
    # Short forms: gh-91 / GH-91 / #91 / 91.
    m = re.fullmatch(r"(?:gh-|#)?(\d+)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def external_for(bead_id: str) -> str | None:
    """Read one bead's external_ref via `bd show`. One subprocess per call.

    Fine for the handful of ids `mappings`/`plan_hoist` resolve; NEVER call this in a
    loop over the whole universe — see external_from_row (REQ-BUP-052).
    """
    out = run(["bd", "show", bead_id])
    m = EXTERNAL_RE.search(out)
    return m.group(1) if m else None


def external_from_row(row: dict) -> str | None:
    """Read external_ref off a `bd list --json` row — no subprocess (REQ-BUP-052).

    `bd list --all --json` already carries `external_ref`, so resolving it per bead with
    `bd show` is a removable N+1. Measured on this repo (991 beads): `closable` produced
    zero output in 4 minutes and was killed; only 20 beads had a mapping at all, so 991
    subprocesses were spent to find 20 values the bulk query had already returned.

    The field is serialized **omitempty** (measured on bd 1.1.2): the key is *absent* from
    rows with no mapping — missing from 998 of 1019 rows, including the first. Hence a
    defaulting `.get`, never `row["external_ref"]` and never a key-presence test.
    """
    val = row.get("external_ref")
    return val.strip() if isinstance(val, str) and val.strip() else None


CONTAINER_TYPES = frozenset({"epic", "molecule", "gate"})


def candidate_filter(rows: list[dict]) -> list[dict]:
    """Pure: drop container types (epic/molecule/gate); keep real work items.

    Factored out of cmd_enumerate so it is unit-testable without a live bd.
    """
    return [r for r in rows if r.get("issue_type") not in CONTAINER_TYPES]


def load_universe_rows() -> list[dict]:
    """EVERY bead as a raw row — `bd list --all --json`, closed ones included.

    The active-set classifier needs the FULL universe — not just the status-only
    candidate slice — because an active bead's open ancestor (which may itself be
    open-unclaimed) must be resolvable to exclude it. We pull every status so
    in_progress and claimed-open beads are present to seed the active set and to anchor
    the ancestor walk.

    Note the docstring previously read "All non-closed beads
    (open/in_progress/blocked/deferred)", which `--all` contradicts: closed beads ARE
    returned. Corrected rather than narrowed, because `cmd_closable` depends on closed
    rows being present — an issue is closable precisely when its mapped beads are closed,
    so filtering them out here would make every issue read as not-closable (REQ-BUP-052).

    These rows are the SOLE source for the parent-child edge set (REQ-BUP-071). They are
    NOT the seed of a per-bead `bd show` walk — that walk was #268, a 334 s traversal of
    the entire closed universe on the mandated push path, and it is gone. Each row carries
    its own `dependencies[]`, so `collect_parent_edges` reads a payload this one call has
    already paid for. Anything needing a per-row field belongs here, not in a loop.
    """
    return parse_json_array(run(["bd", "list", "--all", "--json"]))


def collect_parent_edges(beads: dict[str, dict]) -> list[Edge]:
    """Resolve parent-child edges for the active-set ancestor walk.

    classify_active only consumes `dep_type == parent-child` edges, so we only need
    those. We read each bead's dependency edges via `bd show` (which exposes
    `dependency_type`) and normalize to the `dep_type` field classify_active expects.
    """
    edges: list[Edge] = []
    for bid in sorted(beads):
        for dep in deps_for_show(bid):
            if edge_type(dep) != "parent-child":
                continue
            target_id = dep.get("depends_on_id") or dep.get("id") or dep.get("target")
            if not target_id:
                continue
            edges.append(
                Edge(
                    blocked=bid,
                    blocker=target_id,
                    dep_type=PARENT_CHILD,
                    target=beads.get(target_id),
                )
            )
    return edges


def deps_for_show(bead_id: str) -> list[dict]:
    """A bead's dependency edges via `bd show <id> --json` (exposes dependency_type)."""
    rows = parse_json_array(run(["bd", "show", bead_id, "--json"]))
    detail = rows[0] if rows else {}
    return detail.get("dependencies") or []


def enumerate_candidates(
    beads: dict[str, dict], edges: list[Edge], ignore_owner_claim: bool = False
) -> list[dict]:
    """Pure: the push-candidate rows = NON-ACTIVE beads (classify_active) minus containers.

    Single active-set definition (plan-013 C.7): candidates are the NON-ACTIVE beads
    from classify_active — NOT the old status-only CANDIDATE_STATUSES slice. This
    refines the old filter by owner + ancestor: a claimed-open bead, or an open
    ancestor of an active bead, is now correctly EXCLUDED (it is active work, not a
    parked push candidate). Container types are still dropped as before. Factored out
    so the enumerate-parity regression test runs without a live bd.

    owner-on-create knob (#61, REQ-BUP-048): when `ignore_owner_claim` is True, owner
    alone is NOT the claimed/active signal. Implemented LOCALLY — by blanking the `owner`
    field on a shallow copy of the universe before classification — so the shared
    `classify_active` / `ACTIVE_CLAIMED` glossary stays byte-identical across its two
    consumers (upstream.py + yf-beads-hygiene). `in_progress` status and ancestor-of-active
    propagation are preserved (they do not depend on owner); only owner-only "claims" fall
    through to candidacy. Default False → byte-for-byte the prior behavior.
    """
    if ignore_owner_claim:
        beads = {bid: {**b, "owner": ""} for bid, b in beads.items()}
    active = classify_active(beads, edges)
    return candidate_filter([beads[bid] for bid in active.non_active if bid in beads])


def owner_claim_exclusions(
    beads: dict[str, dict], edges: list[Edge], ignore_owner_claim: bool
) -> list[str]:
    """Bead ids excluded from candidacy *solely* because of an owner-claim (REQ-BUP-049).

    Pure. Returns [] when `ignore_owner_claim` is already True (nothing is excluded on
    owner grounds), otherwise the set difference between candidacy computed with owner
    claims ignored and candidacy as actually computed. Reuses the REQ-BUP-048 mechanism —
    two classifications, diffed — so the shared plan-013 glossary stays untouched.
    """
    if ignore_owner_claim:
        return []
    effective = {r["id"] for r in enumerate_candidates(beads, edges, ignore_owner_claim=False) if r.get("id")}
    relaxed = {r["id"] for r in enumerate_candidates(beads, edges, ignore_owner_claim=True) if r.get("id")}
    return sorted(relaxed - effective)


def cmd_enumerate(as_json: bool) -> int:
    rows = load_universe_rows()
    beads = {r["id"]: r for r in rows if r.get("id")}
    edges = collect_parent_edges(beads)
    ignore_owner = owner_on_create()
    nonactive_rows = enumerate_candidates(beads, edges, ignore_owner_claim=ignore_owner)
    # REQ-BUP-049: never silently drop owner-claimed beads. Keyed on the excluded COUNT,
    # not on an empty candidate list — a plausible non-zero result can still hide most of
    # the universe (#105: `1 candidate(s)` while ~36 open beads were excluded).
    excluded = owner_claim_exclusions(beads, edges, ignore_owner)
    out = []
    for r in nonactive_rows:
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
    # stderr in BOTH modes: stdout stays a pure JSON array for pipeline consumers, and the
    # warning still reaches a human or an agent reading combined output.
    if excluded:
        print(
            f"WARNING: {len(excluded)} open bead(s) excluded as owner-claimed and will never be "
            f"pushed. If `bd create` auto-assigns owners in this repo, set "
            f"`custom.upstream.owner_on_create true` (see REQ-BUP-048).",
            file=sys.stderr,
        )
        preview = ", ".join(excluded[:5]) + (" …" if len(excluded) > 5 else "")
        print(f"         excluded: {preview}", file=sys.stderr)
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


# --- gh-direct write core (REQ-BUP-054/056/057) -------------------------------
#
# `bd` reads bead content, `gh` writes the issue, `bd update --external-ref` records the
# mapping. There is NO backend dispatch and NO token handling: GitHub is the only
# supported backend (REQ-BUP-040) and `gh` owns its own credential store
# (REQ-BUP-031) — the old per-backend auth table is deliberately gone.

#: bead `priority` (numeric) -> `priority::<word>` label (REQ-BUP-054).
#: P0 and P4 have no label in this repo; restrict-and-drop drops them WITH A REPORT.
PRIORITY_LABELS = {
    0: "priority::critical",
    1: "priority::high",
    2: "priority::medium",
    3: "priority::low",
    4: "priority::backlog",
}


def issue_labels_for(bead: dict) -> list[str]:
    """Derive the issue label set from a bead (REQ-BUP-054).

    `issue_type` -> `type::<t>`, `priority` -> `priority::<word>`, plus the bead's own
    labels passed through unchanged. Order is stable so previews diff cleanly.
    """
    labels: list[str] = []
    itype = (bead.get("issue_type") or "").strip()
    if itype:
        labels.append(f"type::{itype}")
    prio = bead.get("priority")
    if isinstance(prio, int) and prio in PRIORITY_LABELS:
        labels.append(PRIORITY_LABELS[prio])
    for lab in bead.get("labels") or []:
        if isinstance(lab, str) and lab.strip() and lab not in labels:
            labels.append(lab.strip())
    return labels


def restrict_labels(labels: list[str], existing: set[str]) -> tuple[list[str], list[str]]:
    """Restrict-and-drop (REQ-BUP-056): keep labels that exist, drop the rest.

    Returns `(kept, dropped)`. The dropped list is NOT diagnostic noise — it is the
    producer of the GR-BUP-008 revisit signal, and the caller MUST surface it. A silent
    drop would leave that guardrail with no trigger at all.

    Measured (plan-040 Issue 1.1): `gh issue create --label <nonexistent>` fails with
    exit 1 and creates NO issue, while `bd github push` created the label on demand. So
    this is a DELIBERATE DIVERGENCE from bd, not parity — chosen because the genuinely
    uncovered population is 3 beads in 991, and matching bd would cost label-write token
    scope the skill otherwise never needs.
    """
    kept = [l for l in labels if l in existing]
    dropped = [l for l in labels if l not in existing]
    return kept, dropped


def existing_labels() -> set[str]:
    """Label names that already exist upstream. Empty set on any failure.

    ONE `gh label list` for the whole run — never one call per label (that would be the
    same N+1 shape REQ-BUP-052 exists to forbid).
    """
    try:
        # NB: run() raises SystemExit (a BaseException) on a non-zero exit, so
        # `except Exception` alone would NOT catch a failed `gh` call.
        out = run(["gh", "label", "list", "--limit", "500", "--json", "name"])
    except (Exception, SystemExit):
        return set()
    try:
        return {r["name"] for r in json.loads(out) if r.get("name")}
    except (json.JSONDecodeError, TypeError, KeyError):
        return set()


ISSUE_URL_RE = re.compile(r"https://\S+/issues/\d+")


def parse_issue_url(output: str) -> str | None:
    """The issue URL `gh issue create` prints, or None (REQ-BUP-057).

    None means UNVERIFIED and MUST fail closed. This is the structural replacement for
    scraping bd's `Pushed N issues` line — which plan-040 Issue 1.1 measured is also
    printed by `--dry-run`, i.e. emitted when nothing was pushed at all.
    """
    m = ISSUE_URL_RE.search(output or "")
    return m.group(0) if m else None


class WriteError(RuntimeError):
    """A gh-direct write failed verification. Always fail closed, never continue."""


def plan_write(bead: dict, existing: set[str]) -> dict:
    """Resolve the exact action for one bead WITHOUT touching the network.

    This is the preview (REQ-BUP-057): absent `--apply`, rendering these dicts IS the
    dry run. Nothing here calls `gh`, so a preview needs no credentials and costs no
    round-trip — the old mechanism asked bd to ask GitHub what it *would* do.
    """
    ref = external_from_row(bead)
    labels, dropped = restrict_labels(issue_labels_for(bead), existing)
    return {
        "id": bead.get("id"),
        "action": "update" if ref else "create",
        "external": ref,
        "title": bead.get("title") or "",
        "body": bead.get("description") or "",
        "labels": labels,
        "dropped_labels": dropped,
    }


def render_plan(plans: list[dict]) -> str:
    """Human-readable preview of the planned writes, including every dropped label."""
    lines = []
    for p in plans:
        target = p["external"] if p["action"] == "update" else "(new issue)"
        lines.append(f"  [{p['action']:<6}] {p['id']}  -> {target}")
        lines.append(f"             title: {p['title']}")
        if p["labels"]:
            lines.append(f"             labels: {', '.join(p['labels'])}")
        for lab in p["dropped_labels"]:
            # GR-BUP-008: the drop is REPORTED, never silent — this line is the
            # revisit trigger for restrict-and-drop.
            lines.append(
                f"             dropping label {lab!r} (does not exist upstream)")
    return "\n".join(lines)


def apply_write(plan: dict) -> str:
    """Execute one planned write via `gh`, verify STRUCTURALLY, record the mapping.

    Verification is a returned issue URL on create / a clean exit on update — never a
    scraped success string (REQ-BUP-057). A create whose output carries no parseable URL
    raises WriteError so the caller halts BEFORE any destructive follow-on stage
    (REQ-BUP-050's fail-closed contract, preserved with new evidence).
    """
    if plan["action"] == "update":
        cmd = ["gh", "issue", "edit", plan["external"],
               "--title", plan["title"], "--body", plan["body"]]
        for lab in plan["labels"]:
            cmd += ["--add-label", lab]
        try:
            run(cmd)
        except (Exception, SystemExit) as exc:
            raise WriteError(f"{plan['id']}: gh issue edit failed: {exc}") from exc
        return plan["external"]

    cmd = ["gh", "issue", "create", "--title", plan["title"], "--body", plan["body"]]
    for lab in plan["labels"]:
        cmd += ["--label", lab]
    try:
        out = run(cmd)
    except (Exception, SystemExit) as exc:
        raise WriteError(f"{plan['id']}: gh issue create failed: {exc}") from exc

    url = parse_issue_url(out)
    if not url:
        raise WriteError(
            f"{plan['id']}: gh issue create returned no issue URL — treating as "
            f"UNVERIFIED and halting (REQ-BUP-057). Output: {out!r}")

    # Record the mapping. Without this the issue exists but nothing points at it —
    # exactly the invisibility #117/#131 exist to remove.
    try:
        run(["bd", "update", plan["id"], "--external-ref", url, "-q"])
    except (Exception, SystemExit) as exc:
        raise WriteError(
            f"{plan['id']}: issue created at {url} but recording external_ref FAILED "
            f"({exc}). Re-running would create a DUPLICATE — record it by hand: "
            f"bd update {plan['id']} --external-ref {url}") from exc
    return url


def create_or_update(bead_ids: list[str], *, apply: bool) -> dict:
    """The gh-direct write core (REQ-BUP-057). Idempotent on `external_ref`.

    Absent `apply`, renders the plan and writes nothing. Fail-closed: the first
    WriteError aborts the run and is re-raised, so a caller with a destructive
    follow-on stage never reaches it on an unverified write.
    """
    if not bead_ids:
        return {"plans": [], "written": [], "dropped": []}
    rows = {r["id"]: r for r in load_universe_rows() if r.get("id")}
    missing = [b for b in bead_ids if b not in rows]
    if missing:
        raise WriteError(f"unknown bead id(s): {', '.join(missing)}")

    existing = existing_labels()
    plans = [plan_write(rows[b], existing) for b in bead_ids]
    dropped = [(p["id"], lab) for p in plans for lab in p["dropped_labels"]]
    if not apply:
        return {"plans": plans, "written": [], "dropped": dropped}
    written = [{"id": p["id"], "action": p["action"], "url": apply_write(p)}
               for p in plans]
    return {"plans": plans, "written": written, "dropped": dropped}




# REQ-BUP-050's fail-closed CONTRACT survives; its EVIDENCE moved (REQ-BUP-057).
# The old `Pushed N issues` scrape is deleted along with the `bd <backend> push` it
# parsed. plan-040 Issue 1.1 measured why that string was never sound evidence anyway:
# `bd github push --dry-run` prints "✓ Pushed 1 issues" too — the success line is
# emitted when NOTHING was pushed. Verification is now structural: a returned issue URL
# on create (see parse_issue_url / apply_write), which cannot be produced by a no-op.

def hoist_close_commands(bead_ids: list[str], dest: str) -> list[str]:
    """Stage 3 of a hoist: the per-bead reversible tombstone (REQ-BUP-045).

    Kept as `bd close -r` — this is a LOCAL bead operation, not an upstream write, so
    gh-direct does not touch it. It is also the destructive stage REQ-BUP-050 guards:
    the caller must not reach it on an unverified write.
    """
    reason = close_reason(dest)
    return [f'bd close {bid} -r "{reason}"' for bid in bead_ids]


def plan_hoist(bead_ids: list[str], dest: str, *, gran: str) -> list[str]:
    """DEPRECATED SHAPE — retained for the un-hoist/close half only.

    Under gh-direct the upstream write is no longer a shell command string, so a hoist
    is two phases rather than one command list: `create_or_update` (REQ-BUP-057) then
    `hoist_close_commands`. This helper returns only the second, local, phase.
    """
    return hoist_close_commands(bead_ids, dest)


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


# --- land-the-plane follow-on hoist (C.3) ------------------------------------

def plan_land_hoist(followons: dict, *, auto: bool) -> dict:
    """Decide WHICH follow-on beads land-the-plane will hoist, and HOW (pure).

    Inputs: `followons` is the detect_followons() result ({"narrow": [...],
    "broad": [...]}); `auto` is auto_hoist_followons() (custom.upstream.auto_hoist_followons).

    Contract (plan-013 C.3):
      - DEFAULT (auto=False): propose the follow-on batch for a SINGLE confirm. The
        proposed set is the union of narrow+broad (everything detected), but NOTHING is
        hoisted without explicit confirmation (--apply) — matching today's confirm-required
        push contract. `requires_confirm` is True; `auto_eligible` is empty.
      - NO-PROMPT (auto=True): the unattended path may hoist WITHOUT a prompt, but ONLY the
        NARROW signal set (discovered-from into the subtree AND non-active). The BROAD set is
        NEVER auto-hoisted (it may catch a bead still being worked) — it stays in the gated
        proposal. So auto_eligible == narrow; broad remains requires_confirm.

    Non-follow-on reconcile is out of scope here and is always gated elsewhere; a bead that
    is not a detected follow-on can never appear in `auto_eligible`.
    """
    narrow = list(followons.get("narrow", []))
    broad = list(followons.get("broad", []))
    # Broad-minus-narrow keeps the proposal list de-duplicated.
    broad_only = [b for b in broad if b not in narrow]
    if auto:
        return {
            "auto_eligible": narrow,                 # no-prompt: NARROW only
            "requires_confirm": broad_only,          # broad still gated
            "proposed": narrow + broad_only,
            "mode": "auto",
        }
    return {
        "auto_eligible": [],                         # default: nothing without confirm
        "requires_confirm": narrow + broad_only,     # whole batch, single confirm
        "proposed": narrow + broad_only,
        "mode": "propose",
    }


def cmd_land(parent_id: str, intake_ts: str, dest: str, apply: bool) -> int:
    """Land-the-plane: detect follow-ons under the plan subtree and hoist them.

    Default = propose-with-confirm (emit the batch + require --apply). No-prompt
    unattended hoist runs ONLY when custom.upstream.auto_hoist_followons is true, and
    even then is restricted to the NARROW signal set.
    """
    def list_subtree(pid: str) -> list[dict]:
        return parse_json_array(run(["bd", "list", "--parent", pid, "--all", "--json"]))

    def deps_for(bid: str) -> list[dict]:
        return parse_json_array(run(["bd", "dep", "list", bid, "--json"]))

    followons = detect_followons(
        parent_id, intake_ts, list_subtree=list_subtree, deps_for=deps_for
    )
    auto = auto_hoist_followons()
    decision = plan_land_hoist(followons, auto=auto)
    gran = granularity()

    print(f"Land-the-plane follow-on hoist (mode={decision['mode']}, granularity={gran}):")
    print(f"  narrow (auto-eligible signal): {followons['narrow']}")
    print(f"  broad  (gated-only signal)   : {followons['broad']}")

    if decision["mode"] == "auto" and decision["auto_eligible"]:
        ids = decision["auto_eligible"]
        try:
            auto_result = create_or_update(ids, apply=apply)
        except WriteError as exc:
            print(f"FAIL-CLOSED: {exc}\n  No bead was closed.", file=sys.stderr)
            return 1
        cmds = hoist_close_commands(ids, dest)
        print(f"\nNO-PROMPT auto-hoist (narrow only): {ids}")
        print(render_plan(auto_result["plans"]))
        for c in cmds:
            print(f"  {c}")
        if decision["requires_confirm"]:
            print(f"\nStill gated (broad — confirm required): {decision['requires_confirm']}")
        if not apply:
            print("\nDry run. Re-run with --apply to execute the auto-hoist sequence.")
            return 0
        for c in cmds:
            print(f"+ {c}")
            run(["bash", "-c", c])
        print("Auto-hoist complete (narrow follow-ons closed with reversible tombstone).")
        return 0

    # Default / nothing auto-eligible: propose the batch for a single confirm.
    proposed = decision["requires_confirm"]
    if not proposed:
        print("\nNo follow-on beads detected; nothing to hoist.")
        return 0
    try:
        result = create_or_update(proposed, apply=apply)
    except WriteError as exc:
        print(f"FAIL-CLOSED: {exc}\n  No bead was closed.", file=sys.stderr)
        return 1
    print(f"\nProposed follow-on hoist (single confirm required): {proposed}")
    _render_write_phase(result, apply=apply,
                        verb="hoist the proposed follow-on batch")
    closes = hoist_close_commands(proposed, dest)
    print("Then, locally (reversible tombstone):")
    for c in closes:
        print(f"  {c}")
    if not apply:
        return 0
    for w in result["written"]:
        print(f"+ {w['action']}: {w['id']} -> {w['url']}")
    for c in closes:
        print(f"+ {c}")
        run(["bash", "-c", c])
    print("Follow-on hoist complete (closed with reversible tombstone).")
    return 0


def cmd_hoist(issues_csv: str, dest: str, apply: bool) -> int:
    """Ensure the upstream issue, then remove the bead locally (REQ-BUP-045).

    Two phases now that the write is gh-direct: `create_or_update` (REQ-BUP-057), then
    the reversible `bd close -r` tombstone. The tombstone is the DESTRUCTIVE stage
    REQ-BUP-050 guards, so it runs ONLY after every write verified — a WriteError
    returns before any bead is closed. Local-close semantics are unchanged.
    """
    ids = [s.strip() for s in issues_csv.split(",") if s.strip()]
    if not ids:
        print("No bead IDs given; nothing to hoist.")
        return 1
    gran = granularity()
    n_issues = hoist_issue_count(ids, gran)
    try:
        result = create_or_update(ids, apply=apply)
    except WriteError as exc:
        # Fail closed: NOT ONE bead is closed on an unverified write.
        print(f"FAIL-CLOSED: {exc}\n  No bead was closed.", file=sys.stderr)
        return 1

    print(f"Hoist plan ({gran}): {len(ids)} bead(s) -> {n_issues} upstream issue(s) at {dest}")
    _render_write_phase(result, apply=apply, verb="write upstream and close locally")
    closes = hoist_close_commands(ids, dest)
    print("Then, locally (reversible tombstone, never bd delete):")
    for c in closes:
        print(f"  {c}")
    if not apply:
        return 0
    for w in result["written"]:
        print(f"+ {w['action']}: {w['id']} -> {w['url']}")
    for c in closes:
        print(f"+ {c}")
        run(["bash", "-c", c])
    print("Hoist complete (beads closed with reversible tombstone reason).")
    return 0


def owner_claim_warning_lines() -> list[str]:
    """The REQ-BUP-049 owner-claimed exclusion warning as text lines, or [].

    Factored out of `cmd_enumerate`'s stderr write so `push` can surface the same
    signal INLINE in its own stdout (REQ-BUP-051, #105 residual): the shipped
    warning is stderr-only, so an agent piping `--json` to `jq` never sees it, and
    `push` is now the routed path every operator and agent is sent through.
    """
    rows = load_universe_rows()
    beads = {r["id"]: r for r in rows if r.get("id")}
    edges = collect_parent_edges(beads)
    excluded = owner_claim_exclusions(beads, edges, owner_on_create())
    if not excluded:
        return []
    preview = ", ".join(excluded[:5]) + (" …" if len(excluded) > 5 else "")
    return [
        f"WARNING: {len(excluded)} open bead(s) excluded as owner-claimed and will never "
        f"be pushed. If `bd create` auto-assigns owners in this repo, set "
        f"`custom.upstream.owner_on_create true` (see REQ-BUP-048).",
        f"         excluded: {preview}",
    ]


def _render_write_phase(result: dict, *, apply: bool, verb: str) -> None:
    """Shared preview/report rendering for the three write paths."""
    print(render_plan(result["plans"]))
    for bead_id, lab in result["dropped"]:
        pass  # already rendered per-plan by render_plan; kept for the summary below
    if result["dropped"]:
        # GR-BUP-008: surface the drops as a SUMMARY too, so the revisit signal
        # survives a long preview an operator skims.
        print(f"\n{len(result['dropped'])} label(s) dropped as non-existent upstream "
              f"(restrict-and-drop, REQ-BUP-056):")
        for bead_id, lab in result["dropped"]:
            print(f"  {bead_id}: {lab}")
    if not apply:
        print(f"\nPreview only — nothing was written. Re-run with --apply to {verb}.")


def cmd_push(issues_csv: str, apply: bool) -> int:
    """THE documented push path (REQ-BUP-051), now gh-direct (REQ-BUP-057).

    Scoped to explicit ids — never a bare sync. Absent `--apply` IS the dry run, and
    the preview is rendered LOCALLY: no network round-trip and no credentials needed
    to read it. Leaves each bead OPEN and mirrored — removing it locally is `hoist`.
    """
    if not upstream_enabled():
        print("Upstream tracking is disabled (custom.upstream.enabled / backend none); nothing to push.")
        return 0
    ids = [s.strip() for s in issues_csv.split(",") if s.strip()]
    if not ids:
        print("No bead IDs given; nothing to push.")
        return 1
    try:
        result = create_or_update(ids, apply=apply)
    except WriteError as exc:
        print(f"FAIL-CLOSED: {exc}", file=sys.stderr)
        return 1

    print(f"Push plan: {len(ids)} bead(s) -> GitHub (beads stay open and mirrored)")
    _render_write_phase(result, apply=apply, verb="write")
    # #105 residual: surface the owner-claimed exclusion warning INLINE on stdout,
    # so it survives a `| jq` on the routed path.
    for line in owner_claim_warning_lines():
        print(line)
    if apply:
        for w in result["written"]:
            print(f"+ {w['action']}: {w['id']} -> {w['url']}")
        print("Push complete (beads remain open, now mirrored upstream).")
    return 0


# --- closable: propose upstream issues whose work is done (REQ-BUP-052, #117) ---

CLOSABLE_CAVEAT = (
    "Hand-filed coarse plan trackers carry NO bead mapping and are invisible to this "
    "signal — a clean run does NOT mean nothing needs closing."
)


#: A hoist tombstone's close_reason, as `close_reason()` writes it. Matched on the STABLE
#: prefix rather than the whole string, because the destination URL varies per issue.
_TOMBSTONE_MARK = "hoisted upstream to "


def is_hoist_tombstone(bead: dict) -> bool:
    """True when this bead was closed by a HOIST, not by being finished (REQ-BUP-070).

    The follow-on hoist closes a bead locally with a reversible `bd close -r` tombstone
    PRECISELY BECAUSE the work moved upstream and is STILL OPEN there. Counting that closure
    as evidence of completion inverts its meaning: REQ-BUP-052's per-bead signal reads a
    hoisted issue as fully discharged at the exact moment it became least discharged.
    """
    reason = (bead.get("close_reason") or "").strip().lower()
    return reason.startswith(_TOMBSTONE_MARK) or "reversible tombstone" in reason


def load_fixture_rows(path: str) -> list[dict]:
    """Read a PINNED bead snapshot in place of live `bd` state (REQ-BUP-070a).

    Without this, every control over `closable` runs against live machine state — which is not
    a control at all: it passes or fails for reasons unrelated to the code under test, and it
    cannot be made RED on demand.

    An ABSENT fixture is exit 1 (a real negative — the caller named a file that is not there);
    a present-but-MALFORMED one is exit 2 (the instrument failed). Under REQ-BUP-070a's
    exit-1 rule that distinction is load-bearing.
    """
    f = pathlib.Path(path)
    if not f.exists():
        print(f"FAIL: fixture not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    try:
        rows = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"INCONCLUSIVE: fixture is unreadable or malformed: {e}", file=sys.stderr)
        raise SystemExit(2)
    if not isinstance(rows, list):
        print("INCONCLUSIVE: fixture must be a JSON array of bead rows", file=sys.stderr)
        raise SystemExit(2)
    return rows


def closable_candidates(beads: list[dict]) -> list[dict]:
    """Group beads by the upstream issue they map to and report which are closable (pure).

    `beads` is a list of {"id", "status", "external"} dicts. An issue is **closable**
    when EVERY bead carrying an `External:` mapping to it is closed; a single open
    mapped bead makes it **not-closable**, and that bead is named as the reason.

    Beads with no `external` are ignored entirely — they map to no issue. This is the
    deliberate zero-coupling choice of REQ-BUP-052: the signal is per-bead, so it needs
    nothing from `yf-plan`'s configurable plans-root. The price is the recorded gap —
    a hand-filed coarse tracker has no bead pointing at it and can never appear here.
    """
    by_issue: dict[str, list[dict]] = {}
    for b in beads:
        ext = b.get("external")
        if not ext:
            continue
        by_issue.setdefault(ext, []).append(b)

    out: list[dict] = []
    for ext in sorted(by_issue):
        mapped = by_issue[ext]
        open_ids = sorted(b["id"] for b in mapped if not _is_closed(b))
        closed = [b for b in mapped if _is_closed(b)]
        tombstones = sorted(b["id"] for b in closed if is_hoist_tombstone(b))
        # REQ-BUP-070. Suppress ONLY when EVERY closed mapped bead is a tombstone — a mix
        # still carries real completion evidence, and the requirement is scoped to "only".
        tombstone_only = bool(closed) and len(tombstones) == len(closed)
        closable = (not open_ids) and not tombstone_only

        if open_ids:
            reason = f"still open: {', '.join(open_ids)}"
        elif tombstone_only:
            # ANNOTATED, NEVER DROPPED. A dropped row is indistinguishable from "no such
            # issue" — the same silent-absence failure REQ-BUP-064 rejects for an
            # unresolvable ref — so the operator is told WHY rather than shown nothing.
            reason = (f"NOT closable: every closed mapped bead is a HOIST TOMBSTONE "
                      f"({', '.join(tombstones)}) — the work moved upstream and is still "
                      f"open there, so these closures are not evidence of completion")
        else:
            reason = "all mapped beads are closed"

        out.append(
            {
                "external": ext,
                "beads": sorted(b["id"] for b in mapped),
                "closable": closable,
                "blocking": open_ids,
                "hoist_tombstones": tombstones,
                "tombstone_only": tombstone_only,
                "reason": reason,
            }
        )
    return out


def issue_number_from_url(url: str) -> str | None:
    """Issue number of an upstream ref, for the `gh issue close` proposal.

    plan-044 Issue 3.1 (REQ-BUP-062): delegates to `normalize_external_ref`, so this —
    the URL-only reader — and `external_from_row` (any string) resolve every accepted
    spelling identically. It previously matched a trailing `/<digits>` and nothing
    else, so a bead recorded as `gh-91` produced no number and vanished from the
    proposal without a word.

    Name retained for its callers; it is no longer URL-only.
    """
    n = normalize_external_ref(url)
    return str(n) if n is not None else None


@dataclass
class ReconcilePlan:
    """A reconcile proposal. `commands` are LOCAL closes; `reported` needs a human."""

    commands: list = field(default_factory=list)
    rows: list = field(default_factory=list)
    reported: list = field(default_factory=list)
    inconclusive: bool = False
    error: str | None = None


def reconcile_supports_apply(half: str) -> bool:
    """The ASYMMETRIC authority of `reconcile` (REQ-BUP-061), as a predicate.

    - `local`  -> True.  Closing a bead is reversible: `bd close -r` leaves a
                         tombstone and `unhoist` restores it.
    - `upstream` -> False. Closing an upstream ISSUE is outward-facing and gets the
                         same confirm-only contract as a push (REQ-BUP-052 and the
                         always-loaded safety rule). There is no `--apply` for it.
    """
    return half == "local"


def plan_reconcile(beads, states) -> ReconcilePlan:
    """Propose `bd close -r` for each non-closed bead whose upstream issue is CLOSED.

    `beads` is a list of {"id", "status", "external_ref"}. `states` maps issue number
    -> "OPEN" | "CLOSED" | UNRESOLVABLE (or an `UpstreamStates`).

    NEVER proposes a close on an `UNRESOLVABLE` ref (REQ-BUP-064): a deleted issue and
    a typo'd ref are indistinguishable by this signal, so both route to a human.
    """
    plan = ReconcilePlan()
    if isinstance(states, UpstreamStates):
        plan.inconclusive = states.inconclusive
        plan.error = states.error
        if states.inconclusive:
            # A falsely-clean proposal is the failure mode to avoid: an empty
            # command list reads as "nothing to reconcile".
            return plan
    for b in beads or []:
        bid = b.get("id")
        if not bid or _is_closed(b):
            continue
        n = normalize_external_ref(b.get("external_ref") or b.get("external"))
        if n is None:
            plan.reported.append(f"{bid}: unparseable external_ref {b.get('external_ref')!r}")
            continue
        state = states.get(n) if hasattr(states, "get") else None
        row = {"id": bid, "issue": n, "upstream_state": state}
        plan.rows.append(row)
        if state == "CLOSED":
            plan.commands.append(
                f'bd close {bid} -r "upstream #{n} closed"'
            )
        elif state == UNRESOLVABLE or state is None:
            plan.reported.append(
                f"{bid}: issue #{n} is UNRESOLVABLE upstream — NOT auto-closing; "
                "a deleted issue and a typo are indistinguishable here"
            )
    return plan


def cmd_reconcile(as_json: bool, apply: bool) -> int:
    """#144: close beads whose upstream issue is already closed (REQ-BUP-061).

    Authority is ASYMMETRIC by design — the local half is `--apply`-able because a
    `bd close -r` tombstone is reversible; the upstream half is propose-only and has
    no `--apply` at all.
    """
    if not upstream_enabled():
        print("Upstream tracking is disabled (custom.upstream.enabled / backend none); nothing to do.")
        return 0

    rows = load_universe_rows()
    beads = [
        {"id": r["id"], "status": r.get("status", ""), "external_ref": ext}
        for r in rows
        if r.get("id") and (ext := external_from_row(r)) and not _is_closed(r)
    ]
    states = resolve_upstream_states(b["external_ref"] for b in beads)
    plan = plan_reconcile(beads, states)

    if as_json:
        print(json.dumps({
            "commands": plan.commands,
            "rows": plan.rows,
            "reported": plan.reported,
            "inconclusive": plan.inconclusive,
            "error": plan.error,
            "applied": bool(apply) and not plan.inconclusive,
        }, indent=2))
    else:
        if plan.inconclusive:
            print(
                f"INCONCLUSIVE: could not read upstream issue state ({plan.error}). "
                "Proposing nothing — an empty proposal here would be "
                "indistinguishable from 'nothing to reconcile'."
            )
            return 0
        print(f"{len(plan.commands)} bead(s) whose upstream issue is CLOSED:")
        for c in plan.commands:
            print(f"  {c}")
        for r in plan.reported:
            print(f"  REPORT: {r}")
        if not apply:
            print("\n(dry run — re-run with --apply to close these BEADS locally.")
            print(" The upstream half is propose-only and has no --apply.)")

    if apply and not plan.inconclusive:
        for b in plan.rows:
            if b["upstream_state"] == "CLOSED":
                run(["bd", "close", b["id"], "-r", f"upstream #{b['issue']} closed"])
        if not as_json:
            print(f"\nApplied: closed {len(plan.commands)} bead(s) locally (reversible via unhoist).")
    return 0


def _repo_root_for_render() -> pathlib.Path:
    """The repository root, for resolving plan bundles off disk."""
    try:
        out = run(["git", "rev-parse", "--show-toplevel"])
        if out.strip():
            return pathlib.Path(out.strip())
    except Exception:  # noqa: BLE001
        pass
    return pathlib.Path(__file__).resolve().parents[3]


def _load_render_module():
    """Load the co-resident `upstream_render` module.

    Absence is FAIL-SOFT — the proposal still renders, just without the evidence block. A
    missing renderer must not take out `closable` itself; the `evidence_complete` flag is
    what a caller asserts on, and an unenriched row simply lacks it.
    """
    cand = pathlib.Path(__file__).resolve().parent / "upstream_render.py"
    if not cand.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("upstream_render", cand)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:  # noqa: BLE001
        return None


def cmd_closable(as_json: bool, fixture: str | None = None) -> int:
    """Propose which upstream issues can be closed. NEVER closes anything (REQ-BUP-052).

    Closing an upstream issue is outward-facing, so it gets the same confirm contract
    as a push: this verb emits the `gh issue close` commands for operator confirmation
    and stops.
    """
    # A FIXTURE run is a test of THIS code, not an upstream operation, so it bypasses the
    # disabled short-circuit: whether the operator's repo has upstream tracking switched on
    # says nothing about whether the grouping logic is correct.
    if fixture is None and not upstream_enabled():
        print("Upstream tracking is disabled (custom.upstream.enabled / backend none); nothing to report.")
        return 0
    # ONE `bd list` for the whole universe; ZERO per-bead `bd show` (REQ-BUP-052).
    # Filtering to mapped beads here — rather than after building the full list — keeps
    # the unmapped majority (998 of 1019 on this repo) out of closable_candidates, which
    # only groups by external ref anyway.
    rows = load_fixture_rows(fixture) if fixture else load_universe_rows()

    # plan-044 Issue 3.4 (REQ-BUP-063): an UNPARSEABLE ref is REPORTED, never
    # silently dropped. The old code filtered mapped beads with a bare walrus and
    # said nothing about refs it could not interpret — an absence that looked
    # identical to "no such bead".
    beads: list[dict] = []
    unparseable: list[dict] = []
    for r in rows:
        if not r.get("id"):
            continue
        ext = external_from_row(r)
        if not ext:
            continue
        if normalize_external_ref(ext) is None:
            unparseable.append({"id": r["id"], "external": ext})
            continue
        # `close_reason` and `title` are carried through DELIBERATELY. The projection used
        # to drop them, which made the hoist-tombstone signal (REQ-BUP-070) invisible to
        # `closable_candidates` — every tombstoned issue read as fully discharged — and left
        # REQ-BUP-070b with no reason text to render.
        beads.append({"id": r["id"], "status": r.get("status", ""), "external": ext,
                      "close_reason": r.get("close_reason") or "",
                      "title": r.get("title") or "",
                      "metadata": r.get("metadata") or {}})

    report = closable_candidates(beads)

    # REQ-BUP-070b: EVERY proposal renders its mapped beads, their close_reason, AND the plan
    # Success Criteria those beads discharge. A close-out proposal is an outward-facing
    # recommendation the operator is asked to authorize; without this it asks for consent to a
    # claim whose evidence the operator would have to reconstruct by hand.
    _render = _load_render_module()
    if _render is not None:
        _render.enrich(report, {b["id"]: b for b in beads}, _repo_root_for_render())

    # plan-044 Issue 3.3 (REQ-BUP-060/064): annotate each row with its UPSTREAM
    # state and emit NO command for a non-OPEN issue. Baseline before this: 35
    # commands emitted, 6 actionable — 29 were no-ops or errors against issues
    # already closed or deleted.
    # A fixture has no real upstream, so no network read is attempted and no row is
    # actionable. Claiming otherwise would be manufacturing an upstream state.
    # A fixture has no real upstream, so no network read is attempted. An EMPTY
    # UpstreamStates (not None) is used deliberately: every downstream reader keeps its
    # normal shape, and `inconclusive` stays False because nothing failed — nothing was
    # asked. Claiming an upstream state for a fixture would be manufacturing one.
    states = (UpstreamStates() if fixture
              else resolve_upstream_states(r["external"] for r in report))
    for row in report:
        if fixture:
            row["issue"] = normalize_external_ref(row["external"])
            row["upstream_state"] = "FIXTURE"
            row["actionable"] = False
            continue
        n = normalize_external_ref(row["external"])
        row["issue"] = n
        row["upstream_state"] = (
            "INCONCLUSIVE" if states.inconclusive else states.get(n, UNRESOLVABLE)
        )
        # Actionable ONLY when the beads say closable AND the issue is really OPEN.
        row["actionable"] = bool(row["closable"]) and row["upstream_state"] == "OPEN"

    closable = [r for r in report if r["closable"]]
    actionable = [r for r in report if r["actionable"]]
    unresolvable = [r for r in report if r["upstream_state"] == UNRESOLVABLE]

    if as_json:
        print(
            json.dumps(
                {
                    "caveat": CLOSABLE_CAVEAT,
                    "issues": report,
                    "unparseable_refs": unparseable,
                    "unresolvable": [r["external"] for r in unresolvable],
                    "inconclusive": states.inconclusive,
                    "inconclusive_reason": states.error,
                },
                indent=2,
            )
        )
    else:
        if states.inconclusive:
            # REQ-BUP-064: never present a falsely-clean proposal. Say plainly that
            # the upstream read failed, so an empty command list is not mistaken
            # for "nothing needs closing".
            print(
                "INCONCLUSIVE: could not read upstream issue state "
                f"({states.error}). NOT proposing any closes — an empty proposal "
                "here would be indistinguishable from 'nothing to do'."
            )
        print(
            f"{len(report)} mapped upstream issue(s); {len(closable)} closable by beads; "
            f"{len(actionable)} actionable (also OPEN upstream):"
        )
        for r in report:
            tag = "actionable  " if r["actionable"] else "not-actionable"
            print(f"  [{tag}] {r['external']}  [{r['upstream_state']}]  ({r['reason']})")

        if unresolvable:
            # Reported SEPARATELY for a human: a deleted issue and a typo'd ref are
            # indistinguishable by this signal, so neither is ever auto-acted on.
            print("\nUNRESOLVABLE (not found upstream — deleted, typo'd, or another repo):")
            for r in unresolvable:
                print(f"  {r['external']}  (beads: {', '.join(r['beads'])})")

        if unparseable:
            print("\nUNPARSEABLE external_ref (reported, not dropped — REQ-BUP-063):")
            for u in unparseable:
                print(f"  {u['id']}  external_ref={u['external']!r}")

        if actionable:
            print("\nProposed (NOT executed — confirm each before running):")
            for r in actionable:
                print(f"  gh issue close {r['issue']}")
        elif not states.inconclusive:
            print("\nNo close proposed: no mapped issue is both fully closed by beads and OPEN upstream.")
        print(f"\nNOTE: {CLOSABLE_CAVEAT}")
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

    p_clos = sub.add_parser(
        "closable",
        help="propose upstream issues whose mapped beads are all closed (never closes)",
    )
    p_clos.add_argument("--json", action="store_true", dest="as_json")
    p_clos.add_argument(
        "--fixture",
        metavar="PATH",
        help="read a PINNED JSON bead snapshot instead of live `bd` state (REQ-BUP-070a). "
             "An absent fixture exits 1; a malformed one exits 2.",
    )

    p_rec = sub.add_parser(
        "reconcile",
        help="propose closing beads whose upstream issue is already closed (#144)",
    )
    p_rec.add_argument("--json", action="store_true", dest="as_json")
    p_rec.add_argument(
        "--apply",
        action="store_true",
        help="close the BEADS locally (reversible). The upstream half is propose-only.",
    )

    p_push = sub.add_parser(
        "push",
        help="THE documented push path: scoped, dry-run-first, fail-closed (beads stay open)",
    )
    p_push.add_argument("--issues", required=True, help="comma-separated bead IDs")
    p_push.add_argument("--apply", action="store_true", help="Execute (default: dry-run/plan only).")

    p_hoist = sub.add_parser("hoist", help="ensure upstream issue per granularity, then close locally")
    p_hoist.add_argument("--issues", required=True, help="comma-separated bead IDs")
    p_hoist.add_argument("--dest", required=True, help="plan id or upstream URL recorded in close reason")
    p_hoist.add_argument("--apply", action="store_true", help="Execute (default: dry-run/plan only).")

    p_land = sub.add_parser(
        "land", help="land-the-plane: detect + hoist follow-on beads (default propose-with-confirm)"
    )
    p_land.add_argument("--parent", required=True, help="plan molecule/epic id")
    p_land.add_argument("--intake", required=True, help="epic intake timestamp (RFC3339)")
    p_land.add_argument("--dest", required=True, help="plan id or upstream URL recorded in close reason")
    p_land.add_argument("--apply", action="store_true", help="Execute (default: dry-run/plan only).")

    p_unh = sub.add_parser("unhoist", help="reopen wrongly-hoisted bead(s) from tombstone")
    p_unh.add_argument("--issues", help="comma-separated bead IDs")
    p_unh.add_argument("--record", help="file of hoisted bead IDs (one per line) for batch round-trip")
    p_unh.add_argument("--apply", action="store_true", help="Execute (default: dry-run/plan only).")

    # REQ-BUP-059 / SC14: `--backend` was REMOVED (REQ-BUP-040, GitHub-only). Detect the
    # literal flag in argv and explain it, rather than letting argparse emit a bare
    # "unrecognized arguments" error that tells an existing caller nothing about why.
    #
    # NB: the acceptance check greps for the deleted auth table and for an
    # argparse registration of that flag, NOT for the bare string `--backend` — a
    # blanket grep would forbid the very code that makes the removal legible.
    if any(a == "--backend" or a.startswith("--backend=") for a in sys.argv[1:]):
        parser.exit(2, (
            "error: --backend was removed. GitHub is now the only supported backend:\n"
            "  upstream writes are gh-direct (gh creates/edits the issue; bd records the\n"
            "  mapping in external_ref), so there is no backend to dispatch on.\n"
            "  The GitLab/Jira entries were unverified config-only stubs — this deleted a\n"
            "  stub surface, it did not withdraw working support.\n"
            "  Adding a backend is tracked as #51 (GitLab) / #52 (Jira) / #53 (Linear).\n"
            "  Re-run the same command without --backend.\n"))

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
    if args.cmd == "closable":
        return cmd_closable(args.as_json, getattr(args, "fixture", None))
    if args.cmd == "reconcile":
        return cmd_reconcile(args.as_json, args.apply)
    if args.cmd == "push":
        return cmd_push(args.issues, args.apply)
    if args.cmd == "hoist":
        return cmd_hoist(args.issues, args.dest, args.apply)
    if args.cmd == "land":
        return cmd_land(args.parent, args.intake, args.dest, args.apply)
    if args.cmd == "unhoist":
        if not args.issues and not args.record:
            parser.error("unhoist requires --issues or --record")
        return cmd_unhoist(args.issues, args.record, args.apply)
    return 1


if __name__ == "__main__":
    sys.exit(main())
