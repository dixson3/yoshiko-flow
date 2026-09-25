#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Cross-harness skill trigger eval (REQ-SKAUTH-062; rating REQ-SKAUTH-061; plan-072).

Measures whether each skill's `description` still ROUTES: every intent in
`skills/<n>/evals/triggers.json` runs as a fresh headless session on pi and/or claude-code,
and the run is scored by which skills it activated. Promoted from plan-072's EXP-003 tooling.

LIVE (calls models):
  --mode candidate|installed  --harness pi|cc|both  --skills <csv>|all  --reps N
  [--record] [--ledger PATH] [--budget-usd N] [--json]

OFFLINE (no model call):
  --validate-intents [--min-trigger N --min-nearmiss N]
  --report [--require-rated] [--forbid <ratings csv>] [--require-decision-for-noncrisp]

Exit: 0 PASS, 1 FAIL, 4 INCONCLUSIVE (a harness binary/auth missing, a staging or
load-verification mismatch, an unreadable ledger/rate table, or the --budget-usd ceiling).

Progress goes to stderr; stdout carries only the result. Scratch clones and staging live
under ~/.cache/yf-trigger-eval/ with the origin remote removed, and staging is cleared at
every reset. Only --record writes triggers.json. Every live run appends to --ledger when
given.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _trigger_eval_core as core  # noqa: E402

REPO = HERE.parent.parent
RATES = HERE / "trigger_eval_rates.json"
CACHE = Path(os.path.expanduser("~/.cache/yf-trigger-eval"))
CC_PROJECTS = Path(os.path.expanduser("~/.claude/projects"))
RESET = "git reset -q --hard && git clean -fdqx -e .claude/skills && rm -rf .agents/rules .claude/rules"
_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()


# ---------------------------------------------------------------------------
# corpus
# ---------------------------------------------------------------------------

def skill_names(root: Path) -> list[str]:
    return sorted(p.parent.name for p in root.glob("skills/*/SKILL.md"))


def frontmatter(p: Path) -> dict:
    text = p.read_text()
    lines = text.split("\n")
    end = lines.index("---", 1)
    return yaml.safe_load("\n".join(lines[1:end])) or {}


def triggers_path(root: Path, name: str) -> Path:
    return root / "skills" / name / "evals" / "triggers.json"


def load_triggers(root: Path, name: str) -> dict | None:
    p = triggers_path(root, name)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except ValueError as e:
        raise core.EvalInconclusive(f"{p}: {e}") from e


# ---------------------------------------------------------------------------
# offline verbs
# ---------------------------------------------------------------------------

def cmd_validate(root: Path, min_t: int, min_n: int) -> int:
    names = skill_names(root)
    errs = []
    for n in names:
        doc = load_triggers(root, n)
        if doc is None:
            errs.append(f"{n}: no evals/triggers.json")
            continue
        errs.extend(core.validate_intents(n, doc, set(names), min_t, min_n))
    for e in errs:
        print(f"FAIL {e}")
    print(f"validate-intents: {len(names)} skills, {len(errs)} problem(s)")
    return core.EXIT_FAIL if errs else core.EXIT_PASS


def skill_report(root: Path, name: str) -> dict:
    desc = str(frontmatter(root / "skills" / name / "SKILL.md").get("description") or "")
    doc = load_triggers(root, name) or {}
    decision = doc.get("decision") or {}
    accepted = decision.get("accepted_misses") or [] if decision.get("status") == "accepted" else []
    r = core.rating(core.utf16_len(desc), doc.get("recorded"), accepted, doc.get("intents") or [])
    rec = doc.get("recorded") or {}
    stale = bool(rec) and rec.get("description_sha256") != core.sha256_text(desc)
    return {"skill": name, "chars": core.utf16_len(desc), "rating": r.get("rating"),
            "display": core.display(r), "misses": r.get("misses", []),
            "decision": decision.get("status"), "recorded_stale": stale,
            "cells": len(doc.get("intents") or []) * len(core.HARNESSES)}


def cmd_report(root: Path, require_rated: bool, forbid: set[str], need_decision: bool,
               as_json: bool) -> int:
    rows = [skill_report(root, n) for n in skill_names(root)]
    n_cells = sum(r["cells"] for r in rows)
    measured = measured_reliability(root)
    rel = measured if measured is not None else 0.95
    ffr = core.false_fail_rate(n_cells, rel)
    fails = []
    for r in rows:
        if require_rated and (r["rating"] is None or r["recorded_stale"]):
            fails.append(f"{r['skill']}: " + ("recorded rating is stale (description changed)"
                                               if r["recorded_stale"] else "no recorded rating"))
        if r["rating"] in forbid and not (r["rating"] == "unrouted" and r["decision"] == "accepted"):
            fails.append(f"{r['skill']}: rating {r['display']} is forbidden")
        if need_decision and r["rating"] not in (None, "crisp") and not r["decision"]:
            fails.append(f"{r['skill']}: not crisp ({r['display']}) and has no operator decision")
    if as_json:
        print(json.dumps({"skills": rows, "n_cells": n_cells, "reliability": rel,
                          "reliability_source": "measured" if measured is not None else "assumed",
                          "false_fail_rate": ffr, "failures": fails}, indent=1))
    else:
        for r in rows:
            print(f"{r['skill']:28} {r['chars']:5}  {r['display']}"
                  + ("  [STALE]" if r["recorded_stale"] else ""))
        print(f"cells N={n_cells}; per-run reliability p={rel:.3f} "
              f"({'measured' if measured is not None else 'assumed'}); "
              f"implied FULL false-FAIL rate {ffr:.4f}")
        for f in fails:
            print(f"FAIL {f}")
    return core.EXIT_FAIL if fails else core.EXIT_PASS


def measured_reliability(root: Path) -> float | None:
    """Pooled correct-outcome rate over every recorded cell, or None if nothing is recorded."""
    num = den = 0
    for n in skill_names(root):
        doc = load_triggers(root, n) or {}
        for c in ((doc.get("recorded") or {}).get("cells") or {}).values():
            num += c.get("correct", 0)
            den += c.get("reps", 0)
    return (num / den) if den else None


# ---------------------------------------------------------------------------
# live: staging, clones, runs
# ---------------------------------------------------------------------------

def sh(script: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", "-c", script], cwd=str(cwd), capture_output=True, text=True,
                          check=False)


def prepare_clone(root: Path, harness: str, run_tag: str) -> Path:
    """A scratch clone of the checkout under test with origin removed."""
    clone = CACHE / f"clone-{harness}-{run_tag}"
    shutil.rmtree(clone, ignore_errors=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(root), str(clone)],
                       capture_output=True, text=True, check=False)
    if r.returncode:
        raise core.EvalInconclusive(f"clone failed: {r.stderr.strip()}")
    # Carry the checkout's UNCOMMITTED skills/ too: candidate mode tests the tree as it is.
    shutil.rmtree(clone / "skills", ignore_errors=True)
    shutil.copytree(root / "skills", clone / "skills")
    sh("git remote remove origin 2>/dev/null; git add -A && git -c user.email=eval@local "
       "-c user.name=eval commit -qm 'eval snapshot' --allow-empty", clone)
    return Path(os.path.realpath(clone))


def stage(clone: Path, root: Path, harness: str, names: list[str]) -> tuple[Path, dict]:
    """Stage every skill fresh; return (staging_root, {name: sha256 of every staged file})."""
    st = clone / ".claude" / "skills" if harness == "cc" else CACHE / f"staging-{clone.name}"
    shutil.rmtree(st, ignore_errors=True)
    st.mkdir(parents=True)
    for n in names:
        shutil.copytree(root / "skills" / n, st / n)
    hashes = {}
    for f in sorted(st.rglob("*")):
        if f.is_file():
            hashes[str(f.relative_to(st))] = core.hashlib.sha256(f.read_bytes()).hexdigest()
    return Path(os.path.realpath(st)), hashes


def verify_staged(st: Path, hashes: dict) -> tuple[bool, str]:
    for rel, h in hashes.items():
        f = st / rel
        if not f.is_file() or core.hashlib.sha256(f.read_bytes()).hexdigest() != h:
            return False, f"staged file changed before launch: {rel}"
    return True, "ok"


def reset(clone: Path, fixture: str | None) -> None:
    sh(RESET, clone)
    if fixture:
        r = sh(fixture, clone)
        if r.returncode:
            raise core.EvalInconclusive(f"fixture failed: {r.stderr.strip()}")


def eval_env() -> dict:
    """The environment every eval session runs in. A missed route runs up to MAX_TOOLS tool
    calls under bypassPermissions, so an eval must be UNABLE to make an outward-facing write:
    gh gets an empty config dir and no token, and herdr/parent-pane handles are removed so a
    yf-herdr intent cannot drive real panes. Model auth (claude/pi) is untouched."""
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("HERDR", "YF_PARENT", "GH_", "GITHUB_"))}
    ghdir = CACHE / "gh-empty"
    ghdir.mkdir(parents=True, exist_ok=True)
    env.update({"GH_CONFIG_DIR": str(ghdir), "GH_TOKEN": "", "GITHUB_TOKEN": "",
                "GH_PROMPT_DISABLED": "1", "GIT_TERMINAL_PROMPT": "0"})
    return env


def kill(p: subprocess.Popen) -> None:
    if p.poll() is not None:
        return
    # PermissionError is what macOS raises for killpg on a group whose leader already exited
    # (measured: it aborted the Issue 3.2 baseline). Either error means "nothing left to kill".
    try:
        os.killpg(p.pid, signal.SIGTERM)
        p.wait(10)
    except (ProcessLookupError, PermissionError):
        return
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(p.pid, signal.SIGKILL)


def run_once(harness: str, clone: Path, st: Path, names: list[str], intent: dict,
             expected_desc: dict, user_invocable: set[str], rates: dict, mode: str) -> dict:
    sid = str(uuid.uuid4())
    debug = CACHE / f"debug-{sid}.log"
    if harness == "cc":
        cmd = ["claude", "-p", intent["prompt"], "--output-format", "stream-json", "--verbose",
               "--session-id", sid]
        if mode == "candidate":
            cmd += ["--setting-sources", "project", "--permission-mode", "bypassPermissions",
                    "--debug-file", str(debug)]
    else:
        cmd = ["pi", "-p", "--mode", "json", "--no-session"]
        if mode == "candidate":
            cmd += ["--no-skills"] + [a for n in names for a in ("--skill", str(st / n))]
        cmd.append(intent["prompt"])
    t0 = time.time()
    events, stop, acts, n_tools, stderr_tail = [], "exit", [], 0, ""
    p = subprocess.Popen(cmd, cwd=str(clone), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True, env=eval_env())
    err_buf: list[str] = []
    th = threading.Thread(target=lambda: err_buf.extend(p.stderr or []), daemon=True)
    th.start()
    timer = threading.Timer(core.TIMEOUT_S, lambda: kill(p))
    timer.start()
    text_tail: list[str] = []
    try:
        for line in p.stdout or []:
            text_tail.append(line)
            del text_tail[:-40]
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            events.append(ev)
            for name, args in core.tool_calls(harness, ev):
                n_tools += 1
                for a in core.activations(harness, name, args,
                                          str(st) if mode == "candidate" else None):
                    if a not in acts:
                        acts.append(a)
            if intent["kind"] == "trigger" and intent["skill"] in acts:
                stop = "target"
                break
            if n_tools >= core.MAX_TOOLS:
                stop = "max_tools"
                break
    finally:
        timer.cancel()
        kill(p)
        th.join(timeout=5)
    if time.time() - t0 >= core.TIMEOUT_S and stop == "exit":
        stop = "timeout"
    stderr_tail = "".join(err_buf)[-2000:]
    res = {"harness": harness, "intent": intent["id"], "activated": acts, "n_tools": n_tools,
           "stop": stop, "secs": round(time.time() - t0, 1), "session_id": sid}
    # --- load verification (candidate) ---
    if mode == "candidate":
        if harness == "cc":
            init = next((e for e in events if e.get("type") == "system"
                         and e.get("subtype") == "init"), None)
            ok, why = core.cc_init_ok(init, user_invocable)
            if ok:
                dtext = debug.read_text() if debug.exists() else ""
                ok, why = core.cc_debug_load_ok(dtext, len(names))
        else:
            ok, why = core.pi_load_ok(events, expected_desc)
        if not ok:
            res["inconclusive"] = why
    if not events and core.looks_like_auth_failure(stderr_tail):
        res["inconclusive"] = f"{harness} auth failure: {stderr_tail.strip()[:200]}"
    elif not events:
        res["inconclusive"] = f"{harness} produced no events: {stderr_tail.strip()[:200]}"
    # --- spend ---
    if harness == "cc":
        pdir = CC_PROJECTS / core.cc_project_slug(str(clone))
        main = pdir / f"{sid}.jsonl"
        subs = sorted((pdir / sid / "subagents").glob("*.jsonl")) if (pdir / sid).exists() else []
        if main.exists():
            priced = core.price_session(main.read_text().splitlines(),
                                        [s.read_text().splitlines() for s in subs], rates)
        else:
            priced = {"inconclusive": f"transcript {main} not found"}
        if "inconclusive" in priced:
            res["spend_inconclusive"] = priced["inconclusive"]
            res["cc_usd"], res["tokens"] = 0.0, {}
        else:
            res["cc_usd"], res["tokens"], res["model"] = priced["usd"], priced["tokens"], priced["model"]
    else:
        tok = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
        for e in events:
            if e.get("type") == "message_end" and (e.get("message") or {}).get("role") == "assistant":
                u = e["message"].get("usage") or {}
                tok["input"] += u.get("input", 0)
                tok["output"] += u.get("output", 0)
                tok["cache_read"] += u.get("cacheRead", 0)
                tok["cache_write"] += u.get("cacheWrite", 0)
        res["cc_usd"], res["tokens"] = 0.0, tok
    if debug.exists():
        debug.unlink()
    # A run that spent nothing measured nothing (REQ-SKAUTH-062 as amended): never scored.
    validity, reset_s = core.run_validity("".join(text_tail), stderr_tail, res.get("tokens"))
    if validity != "ok":
        res["invalid"] = validity
        res["reset_seconds"] = reset_s
        res.setdefault("inconclusive", f"{harness} run {validity}")
    res["correct"] = core.correct(intent, acts) if "inconclusive" not in res else None
    return res


def usd(row: dict) -> float:
    v = row.get("cc_usd")
    return v if isinstance(v, (int, float)) else 0.0


class Budget:
    def __init__(self, ledger: Path | None, ceiling: float | None):
        self.ledger, self.ceiling = ledger, ceiling
        self.lock = threading.Lock()
        self.total = core.ledger_total(ledger) if ledger else 0.0
        self.tripped = False

    def check(self) -> bool:
        with self.lock:
            if self.ceiling is not None and self.total >= self.ceiling:
                self.tripped = True
            return not self.tripped

    def record(self, row: dict) -> None:
        with self.lock:
            self.total += usd(row)
            if self.ledger:
                self.ledger.parent.mkdir(parents=True, exist_ok=True)
                with self.ledger.open("a") as f:
                    f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                                        "harness": row["harness"], "intent": row["intent"],
                                        "tokens": row.get("tokens", {}),
                                        "cc_usd": usd(row),
                                        "model": row.get("model")}) + "\n")


def harness_available(h: str) -> str | None:
    binary = "claude" if h == "cc" else "pi"
    return None if shutil.which(binary) else f"{binary} not on PATH"


class Results:
    """Crash-safe append-only per-run results (REQ-SKAUTH-062 as amended)."""

    def __init__(self, path: Path | None, done: dict[str, dict]):
        self.path, self.done = path, done
        self.lock = threading.Lock()

    def has(self, h, iid, rep) -> bool:
        return core.run_key(h, iid, rep) in self.done

    def add(self, r: dict) -> None:
        if r.get("correct") is None:
            return  # only VALID results are persisted
        with self.lock:
            self.done[core.run_key(r["harness"], r["intent"], int(r["rep"]))] = r
            if self.path:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a") as f:
                    f.write(json.dumps({k: r.get(k) for k in (
                        "harness", "intent", "rep", "correct", "activated", "stop", "n_tools",
                        "secs", "cc_usd", "session_id", "source")}) + "\n")


def run_harness(h, root, names, work, reps, mode, budget, rates, run_tag, throttle=None,
                results=None, rep_offset=0):
    """Run every (intent, rep) for one harness sequentially in its own clone."""
    clone = prepare_clone(root, h, run_tag)
    st, hashes = stage(clone, root, h, names) if mode == "candidate" else (clone / ".none", {})
    fm = {n: frontmatter(root / "skills" / n / "SKILL.md") for n in names}
    expected = {n: str(fm[n].get("description") or "") for n in names}
    user_inv = {n for n in names if fm[n].get("user-invocable", True) not in (False, "false")}
    out = []
    for rep in range(rep_offset, rep_offset + reps):
        for intent in work:
            if results is not None and results.has(h, intent["id"], rep):
                out.append(dict(results.done[core.run_key(h, intent["id"], rep)]))
                continue
            while True:
                if not budget.check():
                    return out
                if throttle is not None and not throttle.acquire():
                    return out
                r = run_one(h, clone, root, st, hashes, names, intent, expected, user_inv,
                            rates, mode)
                r["rep"] = rep
                budget.record(r)
                if r.get("invalid") == "rate-limited" and throttle is not None:
                    ok = throttle.rate_limited(r.get("reset_seconds"))
                    log(f"[{h}] {intent['id']} r{rep} RATE-LIMITED (reset_seconds="
                        f"{r.get('reset_seconds')}); both harnesses pause, rate now "
                        f"{throttle.per_hour:.0f}/h, backoff so far {throttle.backoff_total:.0f}s"
                        + ("" if ok else " — BACKOFF BOUND EXCEEDED, stopping"))
                    if not ok:
                        return out
                    continue  # retry the same run, never record it
                if throttle is not None and not r.get("invalid"):
                    throttle.succeeded()
                break
            out.append(r)
            if results is not None:
                results.add(r)
            mark = ("INCONCLUSIVE " + r["inconclusive"]) if r.get("inconclusive") else \
                ("ok" if r["correct"] else "MISS")
            log(f"[{h}] {intent['id']} r{rep} {mark} acts={r.get('activated')} "
                f"stop={r.get('stop')} {r.get('secs')}s ${usd(r):.4f} "
                f"(ledger ${budget.total:.2f})")
    return out


def run_one(h, clone, root, st, hashes, names, intent, expected, user_inv, rates, mode):
    reset(clone, intent.get("fixture"))
    if mode == "candidate":
        st2, hashes2 = stage(clone, root, h, names)  # staging cleared every reset
        ok, why = verify_staged(st2, hashes2)
        if not ok or hashes2 != hashes:
            return {"harness": h, "intent": intent["id"], "correct": None,
                    "inconclusive": why if not ok else "staged tree differs from the first staging"}
        st = st2
    return run_once(h, clone, st, names, intent, expected, user_inv, rates, mode)


def cmd_live(args, root: Path) -> int:
    names = skill_names(root)
    targets = names if args.skills == "all" else [s for s in args.skills.split(",") if s]
    unknown = set(targets) - set(names)
    if unknown:
        log(f"unknown skills {sorted(unknown)}")
        return core.EXIT_FAIL
    harnesses = ["pi", "cc"] if args.harness == "both" else [args.harness]
    for h in harnesses:
        why = harness_available(h)
        if why:
            print(json.dumps({"status": "inconclusive", "reason": why}))
            return core.EXIT_INCONCLUSIVE
    rates = core.load_rates(RATES)
    work = []
    docs = {}
    for n in targets:
        doc = load_triggers(root, n)
        if doc is None:
            log(f"{n}: no evals/triggers.json")
            return core.EXIT_FAIL
        docs[n] = doc
        work.extend(dict(it, owner=n) for it in doc["intents"])
    if args.intents:
        keep = set(args.intents.split(","))
        work = [w for w in work if w["id"] in keep]
    budget = Budget(Path(args.ledger) if args.ledger else None, args.budget_usd)
    if not budget.check():
        print(json.dumps({"status": "inconclusive", "reason": "budget ceiling already reached",
                          "ledger_cc_usd": budget.total}))
        return core.EXIT_INCONCLUSIVE
    tag = uuid.uuid4().hex[:8]
    throttle = core.Throttle(args.max_runs_per_hour, args.max_backoff_seconds,
                             clock=time.monotonic, sleep=time.sleep,
                             deadline_s=args.deadline_seconds)
    done = core.load_results(Path(args.resume)) if args.resume else {}
    res_path = Path(args.results) if args.results else (Path(args.resume) if args.resume else None)
    store = Results(res_path, done)
    total = len(work) * args.reps * len(harnesses)
    already = sum(store.has(h, w["id"], r) for h in harnesses for w in work for r in range(args.reps))
    log(f"eval: mode={args.mode} harness={','.join(harnesses)} skills={len(targets)} "
        f"intents={len(work)} reps={args.reps} ({total} runs; {already} already in results, "
        f"{total - already} to run) throttle={args.max_runs_per_hour:.0f}/h global")
    with ThreadPoolExecutor(max_workers=len(harnesses)) as ex:
        futs = {h: ex.submit(run_harness, h, root, names, work, args.reps, args.mode, budget,
                             rates, f"{tag}-{h}", throttle, store) for h in harnesses}
        results = {h: f.result() for h, f in futs.items()}
    # Confirmation re-runs: a cell <0.5 whose RECORDED rate was >=0.5 gets 3 more reps.
    cells = aggregate(results)
    for h in harnesses:  # a cell short of its reps (budget/backoff stop) is not a measurement
        for w in work:
            c = cells.setdefault((w["id"], h), {"first": [], "confirm": [], "inconclusive": None,
                                                "rows": []})
            if not c["inconclusive"] and len(c["first"]) < args.reps:
                c["inconclusive"] = f"only {len(c['first'])}/{args.reps} valid reps"
    confirm = []
    for (iid, h), c in cells.items():
        owner = next(w["owner"] for w in work if w["id"] == iid)
        prev = recorded_cell(docs[owner], iid, h)
        acc = iid in accepted_misses(docs[owner])
        if not c["inconclusive"] and core.cell_verdict(c["first"], None, prev, acc) == "needs-confirm":
            confirm.append((iid, h))
    if confirm and not budget.tripped:
        log(f"confirmation re-runs for {len(confirm)} regressed cell(s): {confirm}")
        with ThreadPoolExecutor(max_workers=len(harnesses)) as ex:
            futs = {h: ex.submit(run_harness, h, root, names,
                                 [w for w in work if (w["id"], h) in set(confirm)], 3,
                                 args.mode, budget, rates, f"{tag}-{h}-c", throttle, store,
                                 args.reps)
                    for h in {h for _, h in confirm}}
            for h, f in futs.items():
                for r in f.result():
                    cells[(r["intent"], h)]["confirm"].append(r)
    verdicts = {}
    for (iid, h), c in cells.items():
        owner = next(w["owner"] for w in work if w["id"] == iid)
        if c["inconclusive"]:
            verdicts[(iid, h)] = "inconclusive"
            continue
        conf = [bool(r["correct"]) for r in c["confirm"] if r.get("correct") is not None] or None
        verdicts[(iid, h)] = core.cell_verdict(c["first"], conf, recorded_cell(docs[owner], iid, h),
                                               iid in accepted_misses(docs[owner]))
    status = "pass"
    if any(v == "fail" for v in verdicts.values()):
        status = "fail"
    elif (any(v in ("inconclusive", "needs-confirm") for v in verdicts.values()) or budget.tripped
          or throttle.exhausted):
        status = "inconclusive"
    if args.record and not budget.tripped and not throttle.exhausted:
        for n in targets:
            write_record(root, n, docs[n], cells, args.mode)
    summary = {"status": status, "mode": args.mode, "harnesses": harnesses,
               "runs": sum(len(v) for v in results.values()),
               "budget_tripped": budget.tripped, "ledger_cc_usd": round(budget.total, 4),
               "throttle": {"final_per_hour": throttle.per_hour, "backoff_s": throttle.backoff_total,
                            "exhausted": throttle.exhausted, "deadline_hit": throttle.deadline_hit},
               "cells": {f"{i}:{h}": {"rate": core.rate(c["first"]), "verdict": verdicts[(i, h)],
                                      "inconclusive": c["inconclusive"]}
                         for (i, h), c in cells.items()},
               "recorded": bool(args.record and not budget.tripped and not throttle.exhausted)}
    print(json.dumps(summary, indent=1) if args.json else
          f"trigger-eval: {status} ({summary['runs']} runs, CC ${budget.total:.2f} ledger)")
    if budget.tripped:
        log(f"BUDGET CEILING ${args.budget_usd} reached (ledger ${budget.total:.2f}); stopped.")
    return {"pass": 0, "fail": 1}.get(status, 4)


def aggregate(results: dict) -> dict:
    cells: dict = {}
    for h, rows in results.items():
        for r in rows:
            c = cells.setdefault((r["intent"], h), {"first": [], "confirm": [], "inconclusive": None,
                                                    "rows": []})
            c["rows"].append(r)
            if r.get("correct") is None:
                c["inconclusive"] = r.get("inconclusive") or "no outcome"
            else:
                c["first"].append(bool(r["correct"]))
    return cells


def recorded_cell(doc: dict, iid: str, h: str) -> float | None:
    c = ((doc.get("recorded") or {}).get("cells") or {}).get(core.cell_key(iid, h))
    return c.get("rate") if c else None


def accepted_misses(doc: dict) -> set:
    d = doc.get("decision") or {}
    return set(d.get("accepted_misses") or []) if d.get("status") == "accepted" else set()


def write_record(root: Path, name: str, doc: dict, cells: dict, mode: str) -> None:
    """--record: the ONLY writer of triggers.json's `recorded` block."""
    desc = str(frontmatter(root / "skills" / name / "SKILL.md").get("description") or "")
    rec_cells = {}
    for it in doc["intents"]:
        for h in core.HARNESSES:
            c = cells.get((it["id"], h))
            if c and not c["inconclusive"]:
                outs = c["first"] + [bool(r["correct"]) for r in c["confirm"]
                                     if r.get("correct") is not None]
                rec_cells[core.cell_key(it["id"], h)] = {"rate": core.rate(outs),
                                                        "correct": sum(outs), "reps": len(outs)}
    if len(rec_cells) != len(doc["intents"]) * len(core.HARNESSES):
        log(f"{name}: not every cell measured on both harnesses; record NOT written")
        return
    doc["recorded"] = {"date": date.today().isoformat(), "mode": mode,
                       "description_sha256": core.sha256_text(desc),
                       "description_chars": core.utf16_len(desc), "cells": rec_cells}
    triggers_path(root, name).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    log(f"{name}: recorded ({core.display(core.rating(core.utf16_len(desc), doc['recorded'], sorted(accepted_misses(doc)), doc['intents']))})")


# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Cross-harness skill trigger eval (REQ-SKAUTH-062).")
    ap.add_argument("--root", type=Path, default=REPO)
    ap.add_argument("--mode", choices=("candidate", "installed"), default="candidate")
    ap.add_argument("--harness", choices=("pi", "cc", "both"), default="both")
    ap.add_argument("--skills", default="all")
    ap.add_argument("--intents", default=None, help="restrict to these intent ids (csv)")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--budget-usd", type=float, default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-runs-per-hour", type=float, default=150.0,
                    help="GLOBAL run-start ceiling across both harnesses (shared quota)")
    ap.add_argument("--max-backoff-seconds", type=float, default=4 * 3600.0,
                    help="bound on total rate-limit pause; exceeding it exits 4")
    ap.add_argument("--deadline-seconds", type=float, default=None,
                    help="wall-clock bound; stop at exit 4 before an outer timeout would kill the run")
    ap.add_argument("--results", default=None, help="append valid per-run results here")
    ap.add_argument("--resume", default=None,
                    help="skip runs already in this results jsonl (and keep appending to it)")
    ap.add_argument("--validate-intents", action="store_true")
    ap.add_argument("--min-trigger", type=int, default=3)
    ap.add_argument("--min-nearmiss", type=int, default=3)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--require-rated", action="store_true")
    ap.add_argument("--forbid", default="")
    ap.add_argument("--require-decision-for-noncrisp", action="store_true")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if args.validate_intents:
            return cmd_validate(root, args.min_trigger, args.min_nearmiss)
        if args.report:
            forbid = {x for x in args.forbid.split(",") if x}
            return cmd_report(root, args.require_rated, forbid,
                              args.require_decision_for_noncrisp, args.json)
        return cmd_live(args, root)
    except core.EvalInconclusive as e:
        print(json.dumps({"status": "inconclusive", "reason": str(e)}))
        return core.EXIT_INCONCLUSIVE


if __name__ == "__main__":
    sys.exit(main())
