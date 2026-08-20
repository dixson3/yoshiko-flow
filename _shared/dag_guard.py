#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""The four-layer corpus-write postcondition (REQ-DATA-051, plan-049 Epic 1).

WHY THIS EXISTS, AND WHY ITS PREDECESSOR DID NOT WORK
-----------------------------------------------------
plan-048 bracketed corpus writes with an all-or-nothing content hash. plan-049 EXP-002
implemented its declared successor *exactly as worded* and drove it with the harm it was
written for — the 23-emptied-`depends-on:` replay — and measured **PASS, exit 0**: edges went
*up* two and residue went *down* 22, so destroying 23 declarations read as an improvement on
both instruments.

The blindness is structural, not a bug. **A refused declaration contributes no issue, no edge
and no gate.** Emptying it therefore destroys nothing any parsed view ever saw. plan-048's
all-or-nothing refusal *widened* the blind spot rather than narrowing it.

THE FOUR LAYERS
---------------
    L1  issue ids per plan                                      set containment
    L2  materialised edges (from, to) per plan                  set containment
    L3  the MULTISET of raw referent tokens literally written   multiset containment
    L4  gate name -> {type, condition, test, blocks}            per-gate, field-by-field

**L3 is primary.** It reads the raw token stream directly out of the document, whether or not
the extractor can parse it, which is the only reason it fires on the emptied-declaration
mutant. It is deliberately independent of the grammar it guards: a guard that reads the plan
through the same parser it is protecting inherits every one of that parser's blind spots.

**L4 is what observes a corpus write.** A relocation moves gate content between sections;
L1-L3 are measurably unchanged by it (EXP-002 mutant C), so a guard asserting only those would
be a no-op over exactly the write it brackets. L4 is parsed from *any* `### ...Gate...`
heading in the document rather than only from inside `## Gates`, which is what makes a legal
relocation a no-op and a lossy one a failure.

**COUNTS ARE FORBIDDEN AS THE COMPARISON, IN EVERY LAYER.** `len(post) >= len(pre)` passes the
edge-target substitution mutant with totals exactly unchanged, and passes the emptied-
declaration mutant with the totals moving favourably. Containment is the requirement; a count
is a summary of it that discards the identity the guard exists to check. Every comparison in
this file is over identities.

EXIT CONTRACT
-------------
    0  no loss on any layer            -- the write is legal
    1  containment violated            -- a real loss; `git checkout -- docs/plans`
    2  INCONCLUSIVE                    -- the guard could not judge (a plan present in the
                                          pre-snapshot vanished from the post-snapshot, or a
                                          document could not be read)

2 is never collapsed into 1. "A plan disappeared" is a statement about the *population*, not
about the write; reporting it as FAIL would send an operator to revert a document that may be
fine, and reporting it as PASS would hide a deletion.

THE FINGERPRINT IS A NOTE, NEVER A VERDICT (Issue 1.5)
------------------------------------------------------
The content hash is RECOMPUTED here (not read from the `**Fingerprint:**` field, which would
report a stored value that never moves) and emitted as `hash_note`. It never changes the exit
code: **a hash-moving, DAG-preserving write is exactly what a legal relocation is.** Gating on
it is what made the predecessor all-or-nothing.

    snapshot  <path>...  [--out FILE]      take a snapshot of the four layers
    verify    --pre FILE [--post FILE]     compare; --post defaults to a live re-snapshot
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

SHARED = Path(__file__).resolve().parent
REPO_ROOT = SHARED.parent

# --- L3: the raw referent token stream ------------------------------------------------
#
# Searched, not matched: a trailing-inline declaration lives mid-line, and those are precisely
# the ones the extractor refuses. Nothing here consults the extractor's grammar.
_DECL = re.compile(r"(?P<key>depends-on|resolves-upstream)\s*:\s*(?P<val>[^\n]*)", re.I)

# --- L4: gate blocks, wherever they appear --------------------------------------------
#
# ANY `### ...Gate...` heading, NOT only headings under `## Gates`. A relocation that moves a
# gate block into `## Gates` must read as a no-op; scoping to `## Gates` would instead make
# every relocation look like a pure addition and hide a lossy one.
# `###`/`####` only. `## Gates` is the SECTION heading, not a gate, and admitting it produced
# a phantom field-empty "gate" named `Gates` in every plan.
_GATE_H = re.compile(r"^#{3,4} +(?P<name>.*?\bgates?\b.*?)\s*$", re.I)
_ANY_H = re.compile(r"^#{1,6} +")
_GATE_FIELD = re.compile(
    r"^\s*[-*] +\*{0,2}(?P<k>Type|Approvers|Condition|Test|Blocks|Instructions)\*{0,2}"
    r"\s*:\s*(?P<v>.*)$", re.I)

_L4_FIELDS = ("type", "condition", "test", "blocks")


class Inconclusive(Exception):
    """The guard could not judge. Always exit 2, never 1."""


def _norm(s: str) -> str:
    """Collapse whitespace and strip markdown emphasis so cosmetic edits are not losses."""
    s = s.replace("**", "").replace("`", "").strip()
    return re.sub(r"\s+", " ", s)


def raw_referent_tokens(text: str) -> list[str]:
    """L3. Every referent token LITERALLY WRITTEN in a declaration, parseable or not.

    Returned as a list so the caller can build a MULTISET: two plans each declaring
    `depends-on: 1.1` is two tokens, and losing one of them is a loss. A set would silently
    absorb that.
    """
    out: list[str] = []
    for m in _DECL.finditer(text):
        val = m.group("val")
        # Stop at a sentence break so a prose tail cannot inflate the token stream, but keep
        # everything before it verbatim — the point of L3 is to be literal.
        val = re.split(r"\s+—\s+|\s+--\s+", val)[0]
        for tok in re.split(r"[,;]", val):
            tok = _norm(tok)
            if tok:
                out.append(f'{m.group("key").lower()}:{tok}')
    return out


def gate_blocks(text: str) -> dict[str, dict[str, str]]:
    """L4. `gate name -> {type, condition, test, blocks}` for every gate heading."""
    lines = text.split("\n")
    gates: dict[str, dict[str, str]] = {}
    cur: str | None = None
    for raw in lines:
        h = _GATE_H.match(raw)
        if h:
            cur = _norm(h.group("name"))
            gates.setdefault(cur, {})
            continue
        if cur is None:
            continue
        if _ANY_H.match(raw):          # any other heading closes the block
            cur = None
            continue
        f = _GATE_FIELD.match(raw)
        if f:
            k = f.group("k").lower()
            if k in _L4_FIELDS:
                gates[cur][k] = _norm(f.group("v"))
    return gates


def content_fingerprint(text: str) -> str:
    """Recomputed, NEVER read from the stored field (Issue 1.5).

    Reporting the stored `**Fingerprint:**` value would give a note that by construction never
    moves — the prototype's defect. Mirrors `plan_manager._plan_content_fingerprint`'s
    normalization; deliberately REIMPLEMENTED rather than imported, because `_shared/` must not
    depend on a skill-layer module (a layering inversion). Divergence is harmless: this value
    is a note that cannot change a verdict.
    """
    parts: list[str] = []
    title: str | None = None
    body: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            if title is not None and title.strip().lower() != "upstream issues":
                parts.append(title.strip().lower())
                parts.extend(ln.rstrip() for ln in body if ln.strip())
            title, body = m.group(1).strip(), []
        elif title is not None:
            body.append(line)
    if title is not None and title.strip().lower() != "upstream issues":
        parts.append(title.strip().lower())
        parts.extend(ln.rstrip() for ln in body if ln.strip())
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _extract(plan_md: Path) -> dict:
    """L1/L2 via the shared extractor, imported by path (no package install)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("plan_extract_mod", SHARED / "plan_extract.py")
    if spec is None or spec.loader is None:
        raise Inconclusive("cannot load _shared/plan_extract.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.extract(plan_md)


def snapshot_one(plan_md: Path) -> dict:
    try:
        text = plan_md.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        raise Inconclusive(f"{plan_md}: {e}") from e
    d = _extract(plan_md)
    return {
        "plan": plan_md.parent.name,
        "path": str(plan_md),
        "L1": sorted(i["id"] for i in d["issues"]),
        "L2": sorted(f'{e["from"]}<-{e["to"]}' for e in d["edges"]),
        "L3": sorted(raw_referent_tokens(text)),
        "L4": gate_blocks(text),
        "hash_note": content_fingerprint(text),
        "recovered": len(d.get("recovered", [])),
        "unparsed": len(d.get("unparsed", [])),
    }


def _plan_files(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        if p.is_dir():
            pm = p / "plan.md"
            if pm.is_file():
                out.append(pm)
            else:
                out.extend(sorted(p.glob("*/plan.md")))
        elif p.is_file():
            out.append(p)
    return sorted(set(out))


def cmd_snapshot(a) -> int:
    files = _plan_files(a.paths)
    if not files:
        print("INCONCLUSIVE: no plan.md found under the given paths", file=sys.stderr)
        return 2
    try:
        snaps = {s["plan"]: s for s in (snapshot_one(f) for f in files)}
    except Inconclusive as e:
        print(f"INCONCLUSIVE: {e}", file=sys.stderr)
        return 2
    doc = {"schema": 1, "plans": snaps}
    text = json.dumps(doc, indent=1, sort_keys=True)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"snapshot: {len(snaps)} plan(s) -> {a.out}")
    else:
        print(text)
    return 0


def compare(pre: dict, post: dict) -> dict:
    """Four-layer containment. Returns a verdict dict; never raises on a loss."""
    losses: list[dict] = []
    vanished: list[str] = []
    removed_empty: list[dict] = []
    for name, p in sorted(pre["plans"].items()):
        q = post["plans"].get(name)
        if q is None:
            vanished.append(name)
            continue

        # L1 / L2 -- SET containment.
        for layer in ("L1", "L2"):
            missing = sorted(set(p[layer]) - set(q[layer]))
            if missing:
                losses.append({"plan": name, "layer": layer, "missing": missing})

        # L3 -- MULTISET containment. A set here would absorb a duplicate declaration's loss.
        cp, cq = Counter(p["L3"]), Counter(q["L3"])
        short = {k: cp[k] - cq.get(k, 0) for k in cp if cp[k] > cq.get(k, 0)}
        if short:
            losses.append({"plan": name, "layer": "L3",
                           "missing": [f"{k} (x{v})" for k, v in sorted(short.items())]})

        # L4 -- per gate, FIELD BY FIELD. A gate that survives by name while losing its
        # `Test:` is a loss; a gate reduced to a bare heading is the vacuous-gate shape
        # Issue 3.2's check exists to catch, and it must not pass here either.
        for gname, gfields in sorted(p["L4"].items()):
            qf = q["L4"].get(gname)
            if qf is None:
                if not gfields:
                    # A gate heading with NO declared fields carries no content, so its
                    # disappearance cannot be a content loss — containment over an empty
                    # field map is satisfied by anything, including absence.
                    #
                    # This is not a convenience carve-out. It is the exact shape a legal
                    # de-duplicating relocation produces: plan-008 carries the real gate
                    # block inside `## Epics` and a bare
                    # `### Capability Gate: d2 present (see above)` stub under `## Gates`.
                    # Moving the block up and deleting the stub REMOVES a heading that the
                    # sibling `gate-completeness` check (REQ-DATA-055) independently reports
                    # as vacuous. Failing the write for deleting a thing another instrument
                    # calls a defect would make the two checks contradict each other.
                    #
                    # It is REPORTED, never silent: a removal that turns out to matter must
                    # still be visible to whoever reads the verdict.
                    removed_empty.append({"plan": name, "gate": gname})
                    continue
                losses.append({"plan": name, "layer": "L4",
                               "missing": [f"gate {gname!r} is gone, and it declared "
                                           f"{sorted(gfields)}"]})
                continue
            lost = [f"gate {gname!r}.{k}: {v!r} -> {qf.get(k)!r}"
                    for k, v in sorted(gfields.items()) if qf.get(k) != v]
            if lost:
                losses.append({"plan": name, "layer": "L4", "missing": lost})

    notes = [{"plan": n, "pre": pre["plans"][n]["hash_note"][:12],
              "post": post["plans"][n]["hash_note"][:12],
              "moved": pre["plans"][n]["hash_note"] != post["plans"][n]["hash_note"]}
             for n in sorted(pre["plans"]) if n in post["plans"]]

    added = sorted(set(post["plans"]) - set(pre["plans"]))
    return {
        "verdict": "INCONCLUSIVE" if vanished else ("FAIL" if losses else "PASS"),
        "failing_layers": sorted({x["layer"] for x in losses}),
        "losses": losses,
        "vanished": vanished,
        "added_plans": added,
        # Field-empty gate headings that disappeared. A NOTE, not a verdict — see the
        # containment argument above.
        "removed_empty_gates": removed_empty,
        # A NOTE. It never changes the verdict: a hash-moving, DAG-preserving write is
        # exactly what a legal relocation is.
        "hash_note": {"moved": [n["plan"] for n in notes if n["moved"]], "per_plan": notes},
    }


def cmd_verify(a) -> int:
    try:
        pre = json.loads(Path(a.pre).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"INCONCLUSIVE: cannot read --pre snapshot: {e}", file=sys.stderr)
        return 2
    if a.post:
        try:
            post = json.loads(Path(a.post).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"INCONCLUSIVE: cannot read --post snapshot: {e}", file=sys.stderr)
            return 2
    else:
        files = _plan_files([Path(p["path"]).parent for p in pre["plans"].values()])
        try:
            post = {"schema": 1,
                    "plans": {s["plan"]: s for s in (snapshot_one(f) for f in files)}}
        except Inconclusive as e:
            print(f"INCONCLUSIVE: {e}", file=sys.stderr)
            return 2

    res = compare(pre, post)
    if getattr(a, "upper_bound", False):
        res = apply_upper_bound(pre, post, res)

    print(json.dumps(res, indent=1) if a.json else _render(res))
    return {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}[res["verdict"]]


def apply_upper_bound(pre: dict, post: dict, res: dict) -> dict:
    """The PAIRED UPPER BOUND (Issue 1.6 / SC38). Containment is loss-only by construction.

    Loss-only containment is exactly the right shape for a *write* — nothing may disappear —
    and exactly the wrong shape for a *reading* change, because a grammar that mis-attributes
    a declaration does not lose anything: it INVENTS. EXP-001 measured a fan-out producing
    **+141 edges from 11 lines**, which every loss-only layer passes cleanly and correctly.

    The bound, per plan:

        growth(L2)  <=  headroom_pre  +  new_tokens

        headroom_pre = max(0, |L3_pre| - |L2_pre|)   the declarations LITERALLY WRITTEN in the
                                                     document that were not materialised as
                                                     edges — i.e. the dark matter, and the
                                                     only edges a reading widening may add
        new_tokens   = max(0, |L3_post| - |L3_pre|)  a write that adds real declarations may
                                                     of course add the edges they license

    Both terms are derived from the raw token stream, so the ceiling is set by what the
    DOCUMENT says and never by what the parser feels like producing. A widening that recovers
    every one of a plan's unread declarations lands exactly ON the bound; one that invents
    goes over it, and no amount of loss-only checking would ever notice.

    Never downgrades a verdict: an INCONCLUSIVE or a FAIL stays what it was.
    """
    over: list[dict] = []
    for name, p in sorted(pre["plans"].items()):
        q = post["plans"].get(name)
        if q is None:
            continue
        growth = len(q["L2"]) - len(p["L2"])
        if growth <= 0:
            continue
        headroom = max(0, len(p["L3"]) - len(p["L2"]))
        new_tokens = max(0, len(q["L3"]) - len(p["L3"]))
        allowed = headroom + new_tokens
        if growth > allowed:
            over.append({"plan": name, "edge_growth": growth, "allowed": allowed,
                         "headroom_pre": headroom, "new_tokens": new_tokens,
                         "L2_pre": len(p["L2"]), "L2_post": len(q["L2"]),
                         "L3_pre": len(p["L3"]), "L3_post": len(q["L3"])})
    res = dict(res)
    res["over_upper_bound"] = over
    if over and res["verdict"] == "PASS":
        res["verdict"] = "FAIL"
        res["failing_layers"] = sorted(set(res.get("failing_layers", [])) | {"upper-bound"})
    return res


def _render(res: dict) -> str:
    out = [f"{res['verdict']}"]
    for v in res["vanished"]:
        out.append(f"  INCONCLUSIVE: plan {v} is in the pre-snapshot and gone from the post")
    for L in res["losses"]:
        out.append(f"  {L['layer']} loss in {L['plan']}:")
        out.extend(f"      - {m}" for m in L["missing"][:20])
    for r in res.get("removed_empty_gates", []):
        out.append(f"  note: field-empty gate heading {r['gate']!r} removed from {r['plan']} "
                   f"— no content, so not a loss")
    if res["hash_note"]["moved"]:
        out.append(f"  note: content hash moved in {len(res['hash_note']['moved'])} plan(s) "
                   f"— this is NOT a verdict")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="Four-layer DAG-invariance guard (REQ-DATA-051).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("paths", nargs="+", type=Path)
    s.add_argument("--out")
    s.set_defaults(fn=cmd_snapshot)
    v = sub.add_parser("verify")
    v.add_argument("--pre", required=True)
    v.add_argument("--post")
    v.add_argument("--json", action="store_true")
    v.add_argument("--upper-bound", action="store_true",
                   help="also apply the paired upper bound (Issue 1.6)")
    v.set_defaults(fn=cmd_verify)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
