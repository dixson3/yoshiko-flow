#!/usr/bin/env python3
"""Rescore plan-072 eval runs from raw streams with the widened activation detector.

Signals, first one per skill wins:
  skill_tool   claude-code Skill tool_use naming the skill
  skill_md     tool args reference an installed <.agents|.claude>/skills/<n>/SKILL.md
  skill_dir    tool args reference any other file under an installed skills/<n>/ dir
  skill_dir_q  tool args contain `yf skill-dir <n>`
Only tool calls up to the runner's cutoff (MAX_TOOLS=6) are counted, so rescoring
cannot credit activations the live run never reached.

Evidence copy for plan-072 EXP-003. Reads raw/*.jsonl beside this file.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

E = os.path.dirname(os.path.abspath(__file__))
MAX_TOOLS = 6
MD = re.compile(r"\.(?:agents|claude)/skills/([a-z0-9-]+)/SKILL\.md")
DIR = re.compile(r"\.(?:agents|claude)/skills/([a-z0-9-]+)/")
Q = re.compile(r"yf skill-dir ([a-z0-9-]+)")


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise SystemExit(f"cannot load {path}: {e}") from e


def read_events(path):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        raise SystemExit(f"cannot read {path}: {e}") from e
    for line in lines:
        try:
            yield json.loads(line)
        except ValueError:
            continue


def calls(h, ev):
    if h == "cc" and ev.get("type") == "assistant":
        for c in (ev.get("message") or {}).get("content") or []:
            if c.get("type") == "tool_use":
                yield c.get("name"), c.get("input") or {}
    if h == "pi" and ev.get("type") == "message_end":
        m = ev.get("message") or {}
        if m.get("role") == "assistant":
            for c in m.get("content") or []:
                if c.get("type") == "toolCall":
                    yield c.get("name"), c.get("arguments") or {}


def signals(h, name, args, n, acts):
    s = json.dumps(args)
    if h == "cc" and name == "Skill":
        k = str(args.get("skill") or "").split(":")[-1].strip()
        if k:
            acts.setdefault(k, ("skill_tool", n))
    for kind, rx in (("skill_md", MD), ("skill_dir", DIR), ("skill_dir_q", Q)):
        for k in rx.findall(s):
            acts.setdefault(k, (kind, n))


def score(path, intents):
    h, iid = os.path.basename(path).split("-")[:2]
    acts, n = {}, 0
    for ev in read_events(path):
        for name, args in calls(h, ev):
            n += 1
            if n <= MAX_TOOLS:
                signals(h, name, args, n, acts)
    it = intents[iid]
    exp = it.get("expect")
    ok = (exp in acts) if exp else not (set(acts) & set(it.get("near") or []))
    return h, iid, ok, acts, n


def collect(intents):
    runs = defaultdict(list)
    for p in sorted(glob.glob(os.path.join(E, "raw", "*-*-[0-9]*.jsonl"))):
        if "manual" not in p:
            h, iid, ok, acts, n = score(p, intents)
            runs[(h, iid)].append((ok, acts, n))
    return runs


def report(runs, intents):
    print(f"{'id':4} {'expect':24} {'cc':8} {'pi':8}  cc-signals / pi-signals")
    tot = defaultdict(lambda: [0, 0])
    for iid in intents:
        row, sig = [], []
        for h in ("cc", "pi"):
            rs = runs.get((h, iid), [])
            tot[h][0] += sum(r[0] for r in rs)
            tot[h][1] += len(rs)
            row.append(f"{sum(r[0] for r in rs)}/{len(rs)}")
            sig.append(" | ".join(
                ",".join(f"{k}:{v[0]}@{v[1]}" for k, v in r[1].items()) or "-" for r in rs))
        print(f"{iid:4} {str(intents[iid].get('expect')):24} {row[0]:8} {row[1]:8}  "
              f"{sig[0]}  //  {sig[1]}")
    for h in ("cc", "pi"):
        print(f"TOTAL {h}: {tot[h][0]}/{tot[h][1]}")


def main():
    intents = {i["id"]: i for i in load_json(os.path.join(E, "intents.json"))}
    runs = collect(intents)
    report(runs, intents)
    if "--json" in sys.argv:
        out = os.path.join(E, "rescored.json")
        try:
            with open(out, "w", encoding="utf-8") as f:
                json.dump({f"{h}:{i}": v for (h, i), v in runs.items()}, f, default=str)
        except OSError as e:
            raise SystemExit(f"cannot write {out}: {e}") from e


if __name__ == "__main__":
    main()
