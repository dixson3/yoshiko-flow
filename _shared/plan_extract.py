#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Machine-read a `plan.md` into JSON: the epic/issue DAG, gates, criteria, upstream rows.

**Why this exists.** `plan_manager.py` is ~4800 lines and contains ZERO parses of
`### Epic N:` or `- Issue N.M:`. The epic/issue DAG — the thing the document exists to
express — had exactly one consumer: an LLM freehanding `bd create` calls at SKILL.md §5.2a.
Pour fidelity was checked by nobody. Measured over 43 comparable plans, **17 carried a pour
divergence**: 885 declared dependency edges against 860 in `bd`, 45 dropped and 20 invented.
A dropped `blocks` edge means the coordinator marked a bead ready *before its declared
predecessor*.

**The governing rule: FAIL LOUDLY, NEVER DEGRADE (plan-047 Issue 5.1).** Every construct this
parser cannot read lands in `unparsed[]` with its line number and the reason. EXP-003's
prototype silently corrupted its own fidelity number **four times** before each widening was
found — a parser that quietly drops what it does not understand produces a number that looks
like a measurement and is not one.

## The grammar is ANCHORED, and that is load-bearing

The prototype matched dependencies with an unanchored search:

    DEPENDS = re.compile(r'depends[- ]on:\\s*(?P<val>.+?)\\s*$', re.I)

Run against plan-047 itself, that reports two dependency edges **that do not exist**. Issue
5.2's body contains the literal ``(`2.5 depends-on: 2.6, 2.7` — correct execution order,
inverted numbering)`` — inside an inline code span, quoting *another* issue's edge as a parser
hazard to test for. The unanchored search reads it and attributes 2.6 and 2.7 to Issue **5.2**.

So keys are matched only in their canonical bullet position, and inline code spans are masked
before any key match. Both hazards are in the test set.

Usage:

    uv run _shared/plan_extract.py <plan.md> [...] [--json] [--strict]

`--strict` exits 1 if any input produced an `unparsed[]` entry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --- grammar (REQ-DATA-019 + the SKILL.md "Epics and Gates grammar" block) --------------

H2 = re.compile(r"^## +(.+?)\s*$")
H3 = re.compile(r"^### +(.+?)\s*$")

# An epic heading. Bold and an em-dash separator are tolerated because the historical corpus
# contains both; a LETTERED epic (`### Epic B:`) is also accepted and flagged, since plan-012
# used letters and the normalizer's letter->numeric rewrite is Issue 8.5's subject.
EPIC = re.compile(r"^### +(?:\*\*)?Epic +([0-9]+|[A-Z])(?:\*\*)?\s*[:—-]\s*(.+?)\s*$")

# An issue bullet at COLUMN 0 of the `## Epics` body. Canonical form only; anything else that
# looks like a list item in that section is reported as `unparsed`, never guessed at.
# The id may be LETTERED (`A.1`, `B.3`) as well as numeric. Plans 012-017 used lettered
# epics, and rejecting that form is not strictness — it is a silent loss of six plans from
# every downstream join. The letter form is extracted and FLAGGED (`lettered`); converting
# it is the normalizer's job (Issue 8.5), not the reader's.
ISSUE = re.compile(r"^- +(?:\*\*)?(?:Issue +)?(?P<id>[0-9]+|[A-Z])\.(?P<sub>[0-9]+[a-z]?)"
                   r"(?:\*\*)?\s*:\s*(?P<rest>.*)$")

# Sub-keys are TWO-SPACE-INDENTED bullets under their issue. Anchored: `^ {2}- key:`.
SUBKEY = re.compile(r"^ {2}- +(depends-on|resolves-upstream)\s*:\s*(?P<val>.*)$", re.I)

# A gate field. Anchored to a bullet so gate prose cannot be read as a field.
GATE_FIELD = re.compile(
    r"^- +\*{0,2}(Type|Approvers|Condition|Test|Blocks|Instructions)\*{0,2}\s*:\s*(?P<val>.*)$",
    re.I)

ISSUE_ID = re.compile(r"^(?:[0-9]+|[A-Z])\.[0-9]+[a-z]?$")
EPIC_REF = re.compile(r"^epic:([0-9]+|[A-Z])$", re.I)
UPSTREAM_ROW = re.compile(r"#(\d+)")
REQ_ID = re.compile(r"\bREQ-[A-Z0-9]+-[0-9]+[a-z]?\b")
FILE_LINE = re.compile(r"([\w./\-]+\.(?:py|md|rs|toml|sh|json|yaml|yml)):(\d+)")
CRITERION_ID = re.compile(r"^SC[0-9]+[a-z]?$")

RECONCILE_SENTINEL = "reconcile step"


def natural_key(issue_id: str) -> tuple:
    """Sort key for an issue id. `6.10` sorts AFTER `6.2` — lexically it does not.

    Issue 5.2 names this as a required test case: the corpus contains ids that sort wrongly
    under a plain string comparison, and an extractor that emits them in lexical order hands
    the comparator a DAG whose edges look reordered.
    """
    m = re.match(r"^(\d+|[A-Z])\.(\d+)([a-z]?)$", issue_id)
    if not m:
        return (999, 999, "", issue_id)
    head = m.group(1)
    # Lettered epics sort after numeric ones; within each family, numerically.
    return ((0, int(head)) if head.isdigit() else (1, ord(head)),
            int(m.group(2)), m.group(3), issue_id)


def mask_inline_code(line: str) -> str:
    """Blank out `inline code spans`, preserving length so column offsets still line up.

    This is the fix for the prototype's headline defect: a `depends-on:` quoted inside an
    inline code span is DOCUMENTATION, not a declaration.
    """
    return re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)


def _split_h2(lines: list[str]) -> dict[str, tuple[int, int]]:
    """`{h2 title: (start, end)}` over body lines, fence-aware."""
    out: dict[str, tuple[int, int]] = {}
    cur, start, fenced = None, 0, False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = H2.match(ln)
        if m:
            if cur is not None:
                out[cur] = (start, i)
            cur, start = m.group(1), i + 1
    if cur is not None:
        out[cur] = (start, len(lines))
    return out


def _fenced_spans(lines: list[str]) -> set[int]:
    inside, fenced = set(), False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            inside.add(i)
            continue
        if fenced:
            inside.add(i)
    return inside


def _table_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("|") and s.endswith("|"):
            rows.append([c.strip() for c in s[1:-1].split("|")])
    return rows


def classify_test(value: str, fenced: bool) -> str:
    """`executable` | `fenced` | `sentinel` — what kind of `Test:` this is."""
    v = value.strip().strip("`").strip()
    if fenced:
        return "fenced"
    if not v or v.lower() in {"none", "n/a", "na", "-", "_(none)_", "*(none)*"}:
        return "sentinel"
    return "executable"


def extract(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    fenced_lines = _fenced_spans(lines)
    h2 = _split_h2(lines)
    unparsed: list[dict] = []

    def bad(i: int, reason: str, raw: str) -> None:
        unparsed.append({"line": i + 1, "reason": reason, "raw": raw[:200]})

    # --- header fields -----------------------------------------------------------------
    def field(name: str) -> str | None:
        m = re.search(rf"^\*\*{name}:\*\*\s*(.+?)\s*$", text, re.M)
        return m.group(1).strip() if m else None

    # --- ## Epics ----------------------------------------------------------------------
    epics: list[dict] = []
    issues: list[dict] = []
    edges: list[dict] = []
    cur_epic: dict | None = None
    cur_issue: dict | None = None

    if "Epics" in h2:
        s, e = h2["Epics"]
        for i in range(s, e):
            raw = lines[i]
            if i in fenced_lines:
                continue
            ln = mask_inline_code(raw)

            m = EPIC.match(ln)
            if m:
                cur_epic = {"num": m.group(1), "name": m.group(2).strip(),
                            "lettered": not m.group(1).isdigit(), "line": i + 1,
                            "issue_ids": []}
                epics.append(cur_epic)
                cur_issue = None
                continue
            if H3.match(ln) and not m:
                # An H3 inside ## Epics that is not an epic heading. Deliberately-not-poured
                # epics (plan-041's "MOVED to plan-042") land here — D-12 requires an explicit
                # marker rather than a silent drop.
                bad(i, "H3 inside ## Epics is not an epic heading", raw)
                cur_epic, cur_issue = None, None
                continue

            m = ISSUE.match(ln)
            if m:
                if cur_epic is None:
                    bad(i, "issue bullet outside any epic", raw)
                    continue
                iid = f'{m.group("id")}.{m.group("sub")}'
                cur_issue = {"id": iid, "lettered": not m.group("id").isdigit(),
                             "title": m.group("rest").strip(),
                             "epic": cur_epic["num"], "line": i + 1,
                             "depends_on": [], "resolves_upstream": []}
                issues.append(cur_issue)
                cur_epic["issue_ids"].append(cur_issue["id"])
                continue

            m = SUBKEY.match(ln)
            if m:
                if cur_issue is None:
                    bad(i, "sub-key bullet with no owning issue", raw)
                    continue
                key, val = m.group(1).lower(), m.group("val").strip()
                if key == "depends-on":
                    parts = [p.strip() for p in val.split(",") if p.strip()]
                    for p in parts:
                        if not ISSUE_ID.match(p):
                            bad(i, f"depends-on referent {p!r} is not an issue id "
                                   "(a prose tail is forbidden — REQ-DATA-019)", raw)
                            continue
                        cur_issue["depends_on"].append(p)
                        edges.append({"from": cur_issue["id"], "to": p, "kind": "depends-on",
                                      "line": i + 1})
                else:
                    for num in UPSTREAM_ROW.findall(val):
                        d = re.search(r"\((\w+)\)", val)
                        cur_issue["resolves_upstream"].append(
                            {"issue": f"#{num}", "disposition": d.group(1) if d else None})
                continue

            # Anything else at column 0 that looks like a list item in ## Epics.
            # Reported REGARDLESS of whether an issue is open: a column-0 bullet is never a
            # continuation (continuations are two-space indented), so one appearing after an
            # issue bullet is a non-conformant construct, not that issue's body. An earlier
            # version guarded on `cur_issue is None` and therefore silently dropped every
            # such bullet that followed an issue — which is the degrade-quietly behaviour
            # this parser exists to not have.
            if re.match(r"^- +\S", ln):
                bad(i, "column-0 bullet in ## Epics is not a conformant issue bullet", raw)
                cur_issue = None

    # --- ## Gates ----------------------------------------------------------------------
    gates: list[dict] = []
    if "Gates" in h2:
        s, e = h2["Gates"]
        cur_gate: dict | None = None
        pending_test: bool = False
        for i in range(s, e):
            raw = lines[i]
            m = H3.match(raw) if i not in fenced_lines else None
            if m:
                cur_gate = {"name": m.group(1).strip(), "line": i + 1, "type": None,
                            "condition": None, "test": None, "test_kind": None,
                            "blocks": [], "blocks_raw": None, "instructions": None}
                gates.append(cur_gate)
                pending_test = False
                continue
            if cur_gate is None:
                continue

            # A `Test:` whose value is empty and whose next content is a fenced block —
            # 4 plans (037, 038, 042, 046) do this. A one-physical-line parser mis-reads them.
            if pending_test and raw.lstrip().startswith("```"):
                body, j = [], i + 1
                while j < e and not lines[j].lstrip().startswith("```"):
                    body.append(lines[j])
                    j += 1
                cur_gate["test"] = "\n".join(body).strip()
                cur_gate["test_kind"] = classify_test(cur_gate["test"], fenced=True)
                pending_test = False
                continue

            if i in fenced_lines:
                continue
            gm = GATE_FIELD.match(raw)
            if gm:
                key, val = gm.group(1).lower(), gm.group("val").rstrip()
                pending_test = False
                # MULTI-LINE VALUES (Issue 5.2): plan-040 L360's parenthetical wraps across
                # two physical lines, putting the colon on a continuation line. A value
                # continues while following lines are indented and are not a new field.
                j = i + 1
                while (j < e and lines[j].strip()
                       and not GATE_FIELD.match(lines[j])
                       and not H3.match(lines[j])
                       and lines[j].startswith(("  ", "\t"))):
                    val += " " + lines[j].strip()
                    j += 1
                if key == "type":
                    cur_gate["type"] = val.strip().split()[0].lower() if val.strip() else None
                elif key == "condition":
                    cur_gate["condition"] = val.strip()
                elif key == "instructions":
                    cur_gate["instructions"] = val.strip()
                elif key == "test":
                    if not val.strip():
                        pending_test = True
                    else:
                        cur_gate["test"] = val.strip().strip("`")
                        cur_gate["test_kind"] = classify_test(val, fenced=False)
                elif key == "blocks":
                    cur_gate["blocks_raw"] = val.strip()
                    for tok in [p.strip() for p in val.split(",") if p.strip()]:
                        t = tok.strip("`").strip()
                        if ISSUE_ID.match(t):
                            cur_gate["blocks"].append({"kind": "issue", "ref": t})
                        elif EPIC_REF.match(t):
                            cur_gate["blocks"].append(
                                {"kind": "epic", "ref": EPIC_REF.match(t).group(1)})
                        elif t.lower() == RECONCILE_SENTINEL:
                            cur_gate["blocks"].append({"kind": "sentinel", "ref": t.lower()})
                        else:
                            bad(i, f"Blocks referent {t!r} is outside the REQ-DATA-019 "
                                   "alphabet (issue-id | epic:<N> | 'reconcile step')", raw)

    # --- ## Success Criteria / ## Risks & Mitigations -----------------------------------
    def table_of(section: str) -> list[list[str]]:
        if section not in h2:
            return []
        s, e = h2[section]
        return _table_rows(lines[s:e])

    criteria: list[dict] = []
    rows = table_of("Success Criteria")
    for r in rows[2:] if len(rows) > 2 else []:
        cid = r[0].strip().strip("*")
        if not CRITERION_ID.match(cid):
            criteria.append({"id": None, "raw_id": r[0].strip(), "malformed": True})
            continue
        criteria.append({
            "id": cid,
            "criterion": r[1] if len(r) > 1 else "",
            "verification": r[2] if len(r) > 2 else "",
            "discharged_by": [x.strip() for x in (r[3] if len(r) > 3 else "").split(",")
                              if x.strip()],
        })

    risks: list[dict] = []
    rows = table_of("Risks & Mitigations")
    for r in rows[2:] if len(rows) > 2 else []:
        risks.append({"id": r[0].strip().strip("*"),
                      "risk": r[1] if len(r) > 1 else "",
                      "severity": r[2] if len(r) > 2 else "",
                      "mitigation": r[3] if len(r) > 3 else ""})

    upstream: list[dict] = []
    rows = table_of("Upstream Issues")
    for r in rows[2:] if len(rows) > 2 else []:
        m = UPSTREAM_ROW.search(r[0])
        upstream.append({"issue": f"#{m.group(1)}" if m else r[0].strip(),
                         "title": r[1] if len(r) > 1 else "",
                         "disposition": (r[2] if len(r) > 2 else "").strip().strip("*"),
                         "resolved_by": [x.strip() for x in (r[4] if len(r) > 4 else "")
                                         .split(",") if x.strip()]})

    # --- dangling-edge check ------------------------------------------------------------
    known = {i["id"] for i in issues}
    for ed in edges:
        if ed["to"] not in known:
            unparsed.append({"line": ed["line"],
                             "reason": f"depends-on target {ed['to']!r} is not a declared "
                                       "issue in this plan",
                             "raw": f"{ed['from']} -> {ed['to']}"})
    for g in gates:
        for b in g["blocks"]:
            if b["kind"] == "issue" and b["ref"] not in known:
                unparsed.append({"line": g["line"],
                                 "reason": f"gate {g['name']!r} Blocks undeclared issue "
                                           f"{b['ref']!r}",
                                 "raw": g["blocks_raw"] or ""})

    return {
        "path": str(path),
        "plan_id": field("ID"),
        "status": field("Status"),
        "epic_bead": field("Epic"),
        "fingerprint": field("Fingerprint"),
        "epics": epics,
        "issues": sorted(issues, key=lambda x: natural_key(x["id"])),
        "issue_order_declared": [i["id"] for i in issues],
        "edges": edges,
        "gates": gates,
        "criteria": criteria,
        "risks": risks,
        "upstream": upstream,
        "reqs": sorted(set(REQ_ID.findall(text))),
        "file_refs": sorted({f"{a}:{b}" for a, b in FILE_LINE.findall(text)}),
        "counts": {"epics": len(epics), "issues": len(issues), "edges": len(edges),
                   "gates": len(gates), "criteria": len(criteria), "risks": len(risks),
                   "upstream": len(upstream), "unparsed": len(unparsed)},
        "unparsed": unparsed,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract a plan.md into JSON.")
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="Exit 1 if any input produced an `unparsed` entry.")
    a = ap.parse_args()
    out = []
    for p in a.paths:
        pm = p / "plan.md" if p.is_dir() else p
        if not pm.is_file():
            out.append({"path": str(pm), "error": "no plan.md"})
            continue
        out.append(extract(pm))
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        for d in out:
            if "error" in d:
                print(f"{d['path']}: {d['error']}")
                continue
            c = d["counts"]
            print(f"{Path(d['path']).parent.name}: {c['epics']} epics, {c['issues']} issues, "
                  f"{c['edges']} edges, {c['gates']} gates, {c['criteria']} criteria, "
                  f"{c['unparsed']} unparsed")
            for u in d["unparsed"]:
                print(f"    L{u['line']}: {u['reason']}")
    if a.strict and any(d.get("counts", {}).get("unparsed") for d in out):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
