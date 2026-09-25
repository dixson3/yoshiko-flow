#!/usr/bin/env python3
"""plan-072 Issue 3.3 driver: best-effort trim toward ≤600 with a measured accept rule.

For each candidate skill:
  1. write the candidate description into the TRIM worktree (a detached checkout outside
     the repo) — the repo's skills/ is only updated for ACCEPTED texts;
  2. re-rate, in candidate mode against that worktree, the scoped set REQ Issue 3.3 names:
     the skill's own intents + every near-miss naming it + every intent of each skill that
     lists it as a sibling;
  3. ACCEPT iff no cell drops below 0.5 on either harness versus the baseline recorded rate
     (a cell that was already <0.5 must not get WORSE; a new/re-measured cell must be ≥0.5);
  4. otherwise REVERT the worktree text and record the rejection.

Every run goes through skill_trigger_eval.py with --ledger/--budget-usd (D9; ceiling file) and
the global throttle. The harness exits 4 at the ceiling; this driver then stops and reports.

Usage: trim_loop.py <candidates.json> [--only a,b]
  candidates.json: {"<skill>": "<candidate description>", ...}
Writes/extends assets/trim-log.jsonl (one line per attempt).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
ASSETS = Path(__file__).resolve().parent
TRIM = Path.home() / ".cache/yf-trigger-eval/trim"
EVAL = REPO / "scripts/checks/skill_trigger_eval.py"
LEDGER = ASSETS / "spend.jsonl"
CEIL = ASSETS / "spend-ceiling.txt"
LOG = ASSETS / "trim-log.jsonl"


def u16(s):
    return len(s.encode("utf-16-le")) // 2


def set_desc(root: Path, name: str, desc: str) -> None:
    p = root / "skills" / name / "SKILL.md"
    lines = p.read_text().split("\n")
    close = lines.index("---", 1)
    fm = lines[1:close]
    i = next(k for k, ln in enumerate(fm) if ln.startswith("description:"))
    j = i + 1
    while j < len(fm) and (fm[j].startswith(" ") or fm[j] == ""):
        j += 1
    block = ["description: >-"] + ["  " + ln for ln in textwrap.wrap(
        desc, 96, break_on_hyphens=False, break_long_words=False)]
    fm = fm[:i] + block + fm[j:]
    if yaml.safe_load("\n".join(fm))["description"] != desc:
        raise SystemExit(f"{name}: candidate does not round-trip through YAML")
    p.write_text("\n".join(["---"] + fm + lines[close:]))


def get_desc(root: Path, name: str) -> str:
    lines = (root / "skills" / name / "SKILL.md").read_text().split("\n")
    close = lines.index("---", 1)
    return str(yaml.safe_load("\n".join(lines[1:close]))["description"]).strip()


def triggers(root: Path) -> dict:
    out = {}
    for p in sorted(root.glob("skills/*/evals/triggers.json")):
        try:
            out[p.parent.parent.name] = json.loads(p.read_text())
        except (OSError, ValueError) as e:
            raise SystemExit(f"cannot read {p}: {e}") from e
    return out


def scope(docs: dict, name: str) -> tuple[list[str], list[str]]:
    """(skills to stage-rate, intent ids) for the Issue 3.3 scoped set."""
    ids, skills = set(), {name}
    for it in docs[name]["intents"]:
        ids.add(it["id"])
    for s, d in docs.items():
        for it in d["intents"]:
            if it["kind"] == "near-miss" and name in it.get("siblings", []):
                ids.add(it["id"])
                skills.add(s)
        if any(name in it.get("siblings", []) for it in d["intents"] if it["kind"] == "near-miss"):
            for it in d["intents"]:
                ids.add(it["id"])
            skills.add(s)
    return sorted(skills), sorted(ids)


def baseline_rate(docs, iid, h):
    for d in docs.values():
        c = ((d.get("recorded") or {}).get("cells") or {}).get(f"{iid}:{h}")
        if c:
            return c["rate"]
    return None


def rate(skills, ids, tag) -> dict:
    budget = CEIL.read_text().strip() if CEIL.exists() else "200"
    cmd = ["uv", "run", str(EVAL), "--root", str(TRIM), "--mode", "candidate", "--harness", "both",
           "--skills", ",".join(skills), "--intents", ",".join(ids), "--reps", "3",
           "--ledger", str(LEDGER), "--budget-usd", budget, "--max-runs-per-hour", "150", "--json"]
    # stderr streams live (progress lines) instead of being buffered until the child exits
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=None, text=True)
    out: dict = {"status": "unparseable", "raw": r.stdout[-500:]}
    try:
        out = dict(json.loads(r.stdout))
    except ValueError:
        pass
    out["_rc"] = r.returncode
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates")
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    try:
        cands = json.loads(Path(a.candidates).read_text())
    except (OSError, ValueError) as e:
        raise SystemExit(f"cannot read candidates: {e}") from e
    if a.only:
        cands = {k: v for k, v in cands.items() if k in a.only.split(",")}
    base_docs = triggers(REPO)
    for name, desc in cands.items():
        old = get_desc(TRIM, name)
        set_desc(TRIM, name, desc)
        skills, ids = scope(base_docs, name)
        res = rate(skills, ids, name)
        cells = res.get("cells") or {}
        drops, inconcl = [], []
        for k, c in cells.items():
            iid, h = k.split(":")
            if c.get("inconclusive"):
                inconcl.append(k)
                continue
            b = baseline_rate(base_docs, iid, h)
            new = c.get("rate")
            if new is None:
                inconcl.append(k)
                continue
            regressed = (b is None or b >= 0.5) and new < 0.5
            worse = b is not None and b < 0.5 and new < b
            if regressed or worse:
                drops.append((k, b, new))
        budget_hit = bool(res.get("budget_tripped"))
        accepted = not drops and not inconcl and res.get("_rc") in (0, 1) and not budget_hit
        entry = {"skill": name, "old_chars": u16(old), "new_chars": u16(desc), "accepted": accepted,
                 "drops": drops, "inconclusive": inconcl, "rc": res.get("_rc"),
                 "ledger_cc_usd": res.get("ledger_cc_usd"), "cells": cells, "text": desc}
        with LOG.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        if accepted:
            set_desc(REPO, name, desc)
            print(f"ACCEPT {name} {u16(old)} -> {u16(desc)} (ledger ${res.get('ledger_cc_usd')})", flush=True)
        else:
            set_desc(TRIM, name, old)
            print(f"REJECT {name} drops={drops} inconclusive={inconcl} rc={res.get('_rc')} "
                  f"(ledger ${res.get('ledger_cc_usd')})", flush=True)
        if res.get("budget_tripped"):
            print("BUDGET CEILING REACHED — stopping 3.3 (gate yf-mol-t42s.8 decides)", flush=True)
            return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
