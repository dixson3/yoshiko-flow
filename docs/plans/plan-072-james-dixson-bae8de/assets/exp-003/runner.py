#!/usr/bin/env python3
"""plan-072 EXP-001/003 trigger-eval runner (scratch tooling, not shipped).

Usage: runner.py <cc|pi> <clone-dir> <out.jsonl> [--ids D1,V2] [--reps N]

Each intent runs as a fresh headless session in <clone-dir>, after the clone is reset
and the intent's fixture applied. Activation means a Skill tool call naming the skill
(claude-code), or any tool call whose arguments reference an INSTALLED
`.agents/skills/<n>/SKILL.md` or `.claude/skills/<n>/SKILL.md` (both harnesses). The
repo's own `skills/<n>/SKILL.md` is not counted, since skill-authoring intents
legitimately read it as a target. The run is killed once the expected skill activates,
or after MAX_TOOLS tool calls, or after TIMEOUT seconds.

Evidence copy for plan-072 EXP-003. Fixtures are shell snippets authored in
intents.json, so they run through `bash -c` inside the scratch clone.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_TOOLS, TIMEOUT = 6, 150
INSTALLED = re.compile(r"\.(?:agents|claude)/skills/([a-z0-9-]+)/SKILL\.md")
RESET = "git reset -q --hard && git clean -fdq && rm -rf .agents/rules .claude/rules"


def sh(script, cwd):
    return subprocess.run(["bash", "-c", script], cwd=cwd, capture_output=True, text=True,
                          check=False)


def reset(clone, fixture):
    sh(RESET, clone)
    if fixture:
        r = sh(fixture, clone)
        if r.returncode:
            raise SystemExit(f"fixture failed: {r.stderr}")


def tool_calls(harness, ev):
    """Yield (name, args_dict) for tool calls in one stream event."""
    if harness == "cc" and ev.get("type") == "assistant":
        for c in (ev.get("message") or {}).get("content") or []:
            if c.get("type") == "tool_use":
                yield c.get("name"), c.get("input") or {}
    if harness == "pi" and ev.get("type") == "message_end":
        m = ev.get("message") or {}
        if m.get("role") == "assistant":
            for c in m.get("content") or []:
                if c.get("type") == "toolCall":
                    yield c.get("name"), c.get("arguments") or {}


def activated(harness, name, args):
    out = set()
    if harness == "cc" and name == "Skill":
        s = str(args.get("skill") or args.get("command") or "").split(":")[-1].strip()
        if s:
            out.add(s)
    out.update(INSTALLED.findall(json.dumps(args)))
    return out


def stop_reason(intent, acts, tools, t0):
    if time.time() - t0 > TIMEOUT:
        return "timeout"
    if intent.get("expect") and intent["expect"] in acts:
        return "target"
    if len(tools) >= MAX_TOOLS:
        return "max_tools"
    return None


def consume(harness, intent, stream, raw, t0):
    tools, acts, cost, stop = [], [], None, "exit"
    for line in stream:
        raw.write(line)
        try:
            ev = json.loads(line)
        except ValueError:
            ev = {}
        if ev.get("type") == "result":
            cost = ev.get("total_cost_usd")
        for name, args in tool_calls(harness, ev):
            tools.append(name)
            for s in activated(harness, name, args):
                if s not in acts:
                    acts.append(s)
        reason = stop_reason(intent, acts, tools, t0)
        if reason:
            stop = reason
            break
    return tools, acts, cost, stop


def kill(p):
    if p.poll() is not None:
        return
    os.killpg(p.pid, signal.SIGTERM)
    try:
        p.wait(10)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)


def run(harness, clone, intent):
    if harness == "cc":
        cmd = ["claude", "-p", intent["prompt"], "--output-format", "stream-json", "--verbose"]
    else:
        cmd = ["pi", "-p", "--mode", "json", "--no-session", intent["prompt"]]
    t0 = time.time()
    raw_path = os.path.join(HERE, "raw", f"{harness}-{intent['id']}-{int(t0)}.jsonl")
    with subprocess.Popen(cmd, cwd=clone, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          text=True, start_new_session=True) as p, \
            open(raw_path, "w", encoding="utf-8") as raw:
        try:
            tools, acts, cost, stop = consume(harness, intent, p.stdout or [], raw, t0)
        finally:
            kill(p)
    exp = intent.get("expect")
    ok = (exp in acts) if exp else not (set(acts) & set(intent.get("near") or []))
    return {"harness": harness, "id": intent["id"], "expect": exp, "activated": acts,
            "first": acts[0] if acts else None, "pass": ok, "tools": tools,
            "n_tools": len(tools), "stop": stop, "secs": round(time.time() - t0, 1),
            "cost_usd": cost}


USAGE = "usage: runner.py <cc|pi> <clone-dir> <out.jsonl> [--ids D1,V2] [--reps N]"


def parse_args(argv):
    try:
        harness, clone, out = argv[1:4]
        rest = argv[4:]
        ids = set(rest[rest.index("--ids") + 1].split(",")) if "--ids" in rest else None
        reps = int(rest[rest.index("--reps") + 1]) if "--reps" in rest else 1
    except (ValueError, IndexError) as e:
        raise SystemExit(f"{USAGE}\n({e})") from e
    return harness, clone, out, ids, reps


def load_intents(ids):
    path = os.path.join(HERE, "intents.json")
    try:
        with open(path, encoding="utf-8") as f:
            return [i for i in json.load(f) if not ids or i["id"] in ids]
    except (OSError, ValueError) as e:
        raise SystemExit(f"cannot load {path}: {e}") from e


def main():
    harness, clone, out, ids, reps = parse_args(sys.argv)
    intents = load_intents(ids)
    try:
        f = open(out, "a", encoding="utf-8")  # noqa: SIM115 - closed by the with below
    except OSError as e:
        raise SystemExit(f"cannot open {out}: {e}") from e
    with f:
        for rep in range(reps):
            for it in intents:
                reset(clone, it.get("fixture"))
                r = run(harness, clone, it)
                r["rep"] = rep
                f.write(json.dumps(r) + "\n")
                f.flush()
                mark = "PASS" if r["pass"] else "FAIL"
                print(f"[{harness}] {it['id']} r{rep} {mark} acts={r['activated']} "
                      f"tools={r['n_tools']} stop={r['stop']} {r['secs']}s", flush=True)
    reset(clone, "")
    print(f"[{harness}] DONE", flush=True)


if __name__ == "__main__":
    main()
