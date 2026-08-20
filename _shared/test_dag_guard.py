#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Mutant suite for `_shared/dag_guard.py` (plan-049 Epic 1; REQ-DATA-051).

THE HEADLINE ASSERTION IS THAT THE GUARD **FAILS**. plan-048's postcondition was trusted on
the strength of passing; EXP-002 then implemented it exactly as declared and measured it
passing the very harm it was written for. So every mutant below is a claim about the
INSTRUMENT, not about the corpus:

    A  23 emptied `depends-on:` declarations   -> exit 1, `L3` in failing_layers  (SC1)
    B  edge-target substitution                 -> exit 1 on L2+L3, and a COUNT-ONLY
                                                   implementation is shown to pass it (SC2)
    C  a hash-moving, DAG-preserving relocation -> exit 0 with a `hash_note`         (SC4)
    D  a real `okf.py migrate` over every bundle-> exit 0  (the false-positive control) (SC3)
    F  fan-out: invented edges from few lines   -> the UPPER BOUND exits 1 while loss-only
                                                   containment exits 0                 (SC38)

Plus the three exit paths of the contract itself (SC26), including the INCONCLUSIVE case.

Every mutant runs on a TEMPORARY COPY of `docs/plans`. Nothing here writes to the corpus.

Run:  uv run _shared/test_dag_guard.py     (exit 0 = every assertion held, 1 = one did not)
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

SHARED = Path(__file__).resolve().parent
REPO = SHARED.parent
GUARD = SHARED / "dag_guard.py"
PLANS = REPO / "docs" / "plans"

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def guard(*args: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(GUARD), *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def snap(paths: list[Path], out: Path) -> int:
    return guard("snapshot", *[str(x) for x in paths], "--out", str(out))[0]


def verify(pre: Path, post: Path, *extra: str) -> tuple[int, dict]:
    rc, out = guard("verify", "--pre", str(pre), "--post", str(post), "--json", *extra)
    try:
        return rc, json.loads(out)
    except json.JSONDecodeError:
        return rc, {"verdict": "UNPARSEABLE", "raw": out}


import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("dag_guard_mod", GUARD)
dg = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(dg)


# --- the count-only straw man, implemented HERE so SC2's claim is measured, not asserted ---
#
# This is the implementation a reader who takes REQ-DATA-051's four layers and compares them
# with `len()` would write. It exists so "a count-only implementation passes mutant B" is a
# MEASUREMENT rather than a prediction. If a future refactor makes the real guard count-based,
# this straw man and the real guard will agree and the mutant-B assertion below will fail.
def inherited_verdict(pre: dict, post: dict) -> str:
    """plan-048's DECLARED postcondition, reimplemented literally: edges must not fall and
    residue must not rise. No L3 — that layer did not exist. EXP-002 drove exactly this with
    mutant A and measured PASS at exit 0, which is the finding that produced REQ-DATA-051."""
    e_pre = sum(len(p["L2"]) for p in pre["plans"].values())
    e_post = sum(len(p["L2"]) for p in post["plans"].values())
    u_pre = sum(p["unparsed"] for p in pre["plans"].values())
    u_post = sum(p["unparsed"] for p in post["plans"].values())
    return "FAIL" if (e_post < e_pre or u_post > u_pre) else "PASS"


def count_only_verdict(pre: dict, post: dict) -> str:
    for name, p in pre["plans"].items():
        q = post["plans"].get(name)
        if q is None:
            return "INCONCLUSIVE"
        for layer in ("L1", "L2", "L3"):
            if len(q[layer]) < len(p[layer]):
                return "FAIL"
        if len(q["L4"]) < len(p["L4"]):
            return "FAIL"
    return "PASS"


def corpus_copy(td: Path) -> Path:
    dst = td / "plans"
    shutil.copytree(PLANS, dst)
    return dst


with tempfile.TemporaryDirectory() as _td:
    TD = Path(_td)
    BASE = corpus_copy(TD)
    PRE = TD / "pre.json"
    rc = snap([BASE], PRE)
    check("baseline snapshot succeeds", rc == 0, f"rc={rc}")
    pre_doc = json.loads(PRE.read_text())
    check("baseline L3 population is non-empty (else every mutant is vacuous)",
          sum(len(p["L3"]) for p in pre_doc["plans"].values()) > 0)
    check("baseline L4 population is non-empty (SC11's layer must be able to observe)",
          sum(len(p["L4"]) for p in pre_doc["plans"].values()) > 0)

    # --- MUTANT A: emptied declarations the PARSED VIEW CANNOT SEE -----------------------
    #
    # THE ONE THAT MATTERS. EXP-002 drove plan-048's declared postcondition with this replay
    # and measured PASS at exit 0 — edges UP two, residue DOWN 22 — because a declaration the
    # extractor refuses contributes no issue, no edge and no gate, so emptying it destroys
    # nothing any parsed view ever saw.
    #
    # THE CANDIDATE SET IS CHOSEN BY MEASUREMENT, NOT BY PATTERN. Each candidate line is
    # emptied, the plan is re-extracted, and the mutation is KEPT ONLY IF that plan's edge and
    # residue counts are bit-for-bit unchanged — i.e. only if the parsed view genuinely cannot
    # see the loss. Selecting by regex instead would silently drift: plan-049's own Epic 2
    # widening moved 74 declarations from invisible to visible, so a pattern that named the
    # dark matter correctly before the widening names ordinary edges after it, and the mutant
    # quietly turns into one that any implementation catches.
    A = corpus_copy(TD / "a")
    _pe_spec = _ilu.spec_from_file_location("pe_mod", SHARED / "plan_extract.py")
    _pe = _ilu.module_from_spec(_pe_spec)
    _pe_spec.loader.exec_module(_pe)

    def _counts(pm: Path) -> tuple[int, int]:
        c = _pe.extract(pm)["counts"]
        return c["edges"], c["unparsed"]

    emptied = 0
    for pm in sorted(A.glob("*/plan.md")):
        if emptied >= 23:
            break
        base = _counts(pm)
        lines = pm.read_text(encoding="utf-8").split("\n")
        for idx, ln in enumerate(lines):
            if emptied >= 23:
                break
            if not re.search(r"depends-on\s*:\s*\S", ln, re.I):
                continue
            trial = list(lines)
            trial[idx] = re.sub(r"(depends-on\s*:)[^\n]*", r"\1", ln, flags=re.I)
            pm.write_text("\n".join(trial), encoding="utf-8")
            if _counts(pm) == base:
                lines = trial          # invisible to the parsed view -> keep it
                emptied += 1
            else:
                pm.write_text("\n".join(lines), encoding="utf-8")   # visible -> revert
    check("mutant A: 23 declarations were emptied, each VERIFIED invisible to the parsed "
          "view at the moment it was applied", emptied == 23, f"emptied={emptied}")

    POST_A = TD / "post_a.json"
    snap([A], POST_A)
    post_a_doc = json.loads(POST_A.read_text())
    _e_pre = sum(len(p["L2"]) for p in pre_doc["plans"].values())
    _e_post = sum(len(p["L2"]) for p in post_a_doc["plans"].values())
    _u_pre = sum(p["unparsed"] for p in pre_doc["plans"].values())
    _u_post = sum(p["unparsed"] for p in post_a_doc["plans"].values())
    print(f"     [measured] mutant A: edges {_e_pre} -> {_e_post}, "
          f"unparsed {_u_pre} -> {_u_post}")
    rc_a, res_a = verify(PRE, POST_A)
    check("SC1 mutant A: the guard exits 1", rc_a == 1,
          f'rc={rc_a} verdict={res_a.get("verdict")}')
    check("SC1 mutant A: `L3` is in failing_layers", "L3" in res_a.get("failing_layers", []),
          f'failing_layers={res_a.get("failing_layers")}')
    check("SC1 mutant A: L3 is the layer that CARRIES it — the emptied tokens are named",
          any(L["layer"] == "L3" and L["missing"] for L in res_a.get("losses", [])),
          f'losses={[(L["layer"], L["plan"]) for L in res_a.get("losses", [])][:6]}')
    # The historical blindness, reproduced as an assertion rather than recalled as a story.
    check("SC1 mutant A: the INHERITED postcondition (plan-048's edges-and-residue form, "
          "reimplemented literally) PASSES it — this is the measurement that produced "
          "REQ-DATA-051",
          inherited_verdict(pre_doc, post_a_doc) == "PASS",
          f"inherited said {inherited_verdict(pre_doc, post_a_doc)}")
    check("SC1 mutant A: and it passes because the DAG is untouched — edges and residue are "
          "bit-for-bit identical, so the destruction is invisible to any parsed view",
          _e_pre == _e_post and _u_pre == _u_post,
          f"edges {_e_pre}->{_e_post} unparsed {_u_pre}->{_u_post}")

    # --- MUTANT B: edge-target substitution ----------------------------------------------
    #
    # Totals are EXACTLY unchanged — every count in every layer is identical — so this is the
    # mutant that separates containment from counting.
    B = corpus_copy(TD / "b")
    subbed = 0
    for pm in sorted(B.glob("*/plan.md")):
        if subbed >= 8:
            break
        txt = pm.read_text(encoding="utf-8")
        ids = set(re.findall(r"^- +Issue +([0-9]+\.[0-9]+[a-z]?)\s*:", txt, re.M))
        if len(ids) < 3:
            continue
        lines = txt.split("\n")
        out = []
        for ln in lines:
            m = re.match(r"^(\s*- +depends-on\s*:\s*)([0-9]+\.[0-9]+[a-z]?)\s*$", ln, re.I)
            if m and subbed < 8:
                other = sorted(ids - {m.group(2)})
                if other:
                    out.append(f"{m.group(1)}{other[-1]}")
                    subbed += 1
                    continue
            out.append(ln)
        pm.write_text("\n".join(out), encoding="utf-8")
    check("mutant B: at least 4 edge targets were substituted", subbed >= 4, f"subbed={subbed}")

    POST_B = TD / "post_b.json"
    snap([B], POST_B)
    rc_b, res_b = verify(PRE, POST_B)
    post_b_doc = json.loads(POST_B.read_text())
    check("SC2 mutant B: the guard exits 1", rc_b == 1,
          f'rc={rc_b} verdict={res_b.get("verdict")}')
    check("SC2 mutant B: BOTH L2 and L3 fire",
          {"L2", "L3"} <= set(res_b.get("failing_layers", [])),
          f'failing_layers={res_b.get("failing_layers")}')
    _tot = lambda d, L: sum(len(p[L]) for p in d["plans"].values())  # noqa: E731
    check("SC2 mutant B: every layer TOTAL is unchanged — the counts cannot see it",
          all(_tot(pre_doc, L) == _tot(post_b_doc, L) for L in ("L1", "L2", "L3")),
          f'L1 {_tot(pre_doc,"L1")}/{_tot(post_b_doc,"L1")} '
          f'L2 {_tot(pre_doc,"L2")}/{_tot(post_b_doc,"L2")} '
          f'L3 {_tot(pre_doc,"L3")}/{_tot(post_b_doc,"L3")}')
    check("SC2 mutant B: the count-only implementation PASSES it "
          "(measured, not predicted — the guard against a future simplification)",
          count_only_verdict(pre_doc, post_b_doc) == "PASS",
          f"count-only said {count_only_verdict(pre_doc, post_b_doc)}")

    # --- MUTANT C: a hash-moving, DAG-PRESERVING write ------------------------------------
    #
    # SC4. Prose is rewritten inside a hashed `##` section; not one referent, edge, issue or
    # gate field changes. This is what a legal relocation LOOKS LIKE, so gating on the hash is
    # what made the predecessor all-or-nothing.
    C = corpus_copy(TD / "c")
    moved = 0
    for pm in sorted(C.glob("*/plan.md"))[:6]:
        txt = pm.read_text(encoding="utf-8")
        if "\n## Approach\n" in txt:
            pm.write_text(txt.replace("\n## Approach\n",
                                      "\n## Approach\n\n<!-- cosmetic, DAG-preserving -->\n", 1),
                          encoding="utf-8")
            moved += 1
    check("mutant C: at least 3 documents were touched", moved >= 3, f"moved={moved}")
    POST_C = TD / "post_c.json"
    snap([C], POST_C)
    rc_c, res_c = verify(PRE, POST_C)
    check("SC4 mutant C: a hash-moving DAG-preserving write exits 0", rc_c == 0,
          f'rc={rc_c} losses={res_c.get("losses")}')
    check("SC4 mutant C: and the moved hash IS reported, as a note",
          len(res_c.get("hash_note", {}).get("moved", [])) >= 3,
          f'moved={res_c.get("hash_note", {}).get("moved")}')
    check("SC4 mutant C: the note did not change the verdict",
          res_c.get("verdict") == "PASS", f'verdict={res_c.get("verdict")}')

    # --- MUTANT D: a real `okf.py migrate` over every bundle -------------------------------
    #
    # THE FALSE-POSITIVE CONTROL. Without it, a guard that simply always FAILs would satisfy
    # every assertion above. This is a genuine multi-hundred-diff rewrite of the whole corpus.
    D = corpus_copy(TD / "d")
    migrated = 0
    for bundle in sorted(D.glob("*/")):
        if not (bundle / "plan.md").is_file():
            continue
        # `uv run`, NOT `sys.executable`: okf.py declares PEP 723 dependencies, so a bare
        # interpreter fails to import them and returns non-zero. That would silently make
        # `migrated == 0` and turn the false-positive control into a vacuous green.
        r = subprocess.run(["uv", "run", str(SHARED / "okf.py"), "migrate", str(bundle),
                            "--json", "--skill", "yf-plan"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            migrated += 1
    check("mutant D: `okf.py migrate` ran over the whole corpus", migrated >= 40,
          f"migrated={migrated}")
    _diff = subprocess.run(["diff", "-rq", str(BASE), str(D)], capture_output=True, text=True)
    _ndiff = len([l for l in _diff.stdout.splitlines() if l.strip()])
    print(f"     [measured] mutant D: {_ndiff} differing path(s) across {migrated} bundles")
    POST_D = TD / "post_d.json"
    snap([D], POST_D)
    rc_d, res_d = verify(PRE, POST_D)
    check("SC3 mutant D: a real corpus-wide migrate exits 0 — the guard is not FAIL-happy",
          rc_d == 0,
          f'rc={rc_d} verdict={res_d.get("verdict")} '
          f'losses={[(L["layer"], L["plan"], L["missing"][:2]) for L in res_d.get("losses", [])][:5]}')

    # --- MUTANT F: fan-out — INVENTED edges, with the DOCUMENTS UNCHANGED -----------------
    #
    # SC38 / Issue 1.6. This mutant is applied AT THE SNAPSHOT LEVEL, not to the corpus, and
    # that is the point rather than a shortcut: the harm being modelled is a **grammar** that
    # mis-attributes a trailing-inline declaration to several issues. In that harm the
    # document is untouched — the raw token stream (L3) is byte-identical — and the extractor
    # invents the extra edges by itself. Mutating the documents instead would ADD referent
    # tokens, which legitimately license new edges, and would model a different thing.
    #
    # Loss-only containment passes this cleanly and CORRECTLY: nothing was lost. EXP-001
    # measured the real instance at **+141 edges from 11 lines**.
    F_doc = json.loads(PRE.read_text())
    F_doc = {"schema": 1, "plans": {k: dict(v) for k, v in F_doc["plans"].items()}}
    fanned, gain = 0, 0
    for name, pl in sorted(F_doc["plans"].items()):
        if fanned >= 11 or len(pl["L1"]) < 6:
            continue
        pl["L2"] = sorted(set(pl["L2"]) | {f"{a}<-{b}" for a in pl["L1"][:6] for b in pl["L1"][:6]
                                           if a != b})
        gain += len(pl["L2"]) - len(pre_doc["plans"][name]["L2"])
        fanned += 1
    POST_F = TD / "post_f.json"
    POST_F.write_text(json.dumps(F_doc, indent=1, sort_keys=True), encoding="utf-8")
    post_f_doc = json.loads(POST_F.read_text())
    _gain = _tot(post_f_doc, "L2") - _tot(pre_doc, "L2")
    print(f"     [measured] mutant F: {fanned} plan(s) fanned out -> +{_gain} invented edges, "
          f"L3 unchanged ({_tot(pre_doc, 'L3')} -> {_tot(post_f_doc, 'L3')})")
    check("mutant F really invents edges (else the arm is vacuous)", _gain > 20, f"gain={_gain}")
    check("mutant F leaves the RAW TOKEN STREAM untouched — no document was edited, so no "
          "new declaration licenses these edges",
          _tot(pre_doc, "L3") == _tot(post_f_doc, "L3"),
          f'L3 {_tot(pre_doc,"L3")} -> {_tot(post_f_doc,"L3")}')
    rc_f_loss, res_f_loss = verify(PRE, POST_F)
    check("SC38 mutant F: LOSS-ONLY containment passes it cleanly — which is the whole "
          "argument for a paired upper bound", rc_f_loss == 0,
          f'rc={rc_f_loss} verdict={res_f_loss.get("verdict")}')
    check("SC38 mutant F: the count-only straw man passes it too — invention is not a loss "
          "under ANY loss-only reading",
          count_only_verdict(pre_doc, post_f_doc) == "PASS",
          f"count-only said {count_only_verdict(pre_doc, post_f_doc)}")
    rc_f_ub, res_f_ub = verify(PRE, POST_F, "--upper-bound")
    check("SC38 mutant F: the UPPER BOUND exits 1 on the same snapshot pair", rc_f_ub == 1,
          f'rc={rc_f_ub} verdict={res_f_ub.get("verdict")} '
          f'over={res_f_ub.get("over_upper_bound")}')
    check("SC38 mutant F: the bound names the offending plans with their headroom",
          all({"plan", "edge_growth", "allowed", "headroom_pre"} <= set(x)
              for x in res_f_ub.get("over_upper_bound", [])) and res_f_ub.get("over_upper_bound"),
          f'over={res_f_ub.get("over_upper_bound")}')
    rc_d_ub, _ = verify(PRE, POST_D, "--upper-bound")
    check("SC38: the upper bound does NOT fire on the real migrate (mutant D stays 0)",
          rc_d_ub == 0, f"rc={rc_d_ub}")
    rc_c_ub, _ = verify(PRE, POST_C, "--upper-bound")
    check("SC38: nor on the DAG-preserving write (mutant C stays 0)", rc_c_ub == 0,
          f"rc={rc_c_ub}")
    rc_a_ub, res_a_ub = verify(PRE, POST_A, "--upper-bound")
    check("SC38: and it never DOWNGRADES a verdict — mutant A still exits 1", rc_a_ub == 1,
          f'rc={rc_a_ub} verdict={res_a_ub.get("verdict")}')

    # --- SC26: all three exit paths of the contract, including the address-space case ------
    check("SC26: `snapshot` and `verify` are both exposed",
          all(v in (GUARD.read_text()) for v in ("\"snapshot\"", "\"verify\"")))
    E = corpus_copy(TD / "e")
    _victim = sorted(E.glob("*/plan.md"))[0]
    shutil.rmtree(_victim.parent)
    POST_E = TD / "post_e.json"
    snap([E], POST_E)
    rc_e, res_e = verify(PRE, POST_E)
    check("SC26: a plan that VANISHES from the population exits 2 (INCONCLUSIVE), never 1",
          rc_e == 2, f'rc={rc_e} verdict={res_e.get("verdict")}')
    check("SC26: and the vanished plan is named", res_e.get("vanished"),
          f'vanished={res_e.get("vanished")}')
    rc_x, _ = guard("verify", "--pre", str(TD / "does-not-exist.json"), "--json")
    check("SC26: an unreadable --pre snapshot exits 2, not 1", rc_x == 2, f"rc={rc_x}")
    rc_ok, _ = verify(PRE, PRE)
    check("SC26: an identical pre/post pair exits 0", rc_ok == 0, f"rc={rc_ok}")

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
