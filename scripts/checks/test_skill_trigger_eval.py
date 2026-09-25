#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest", "pyyaml>=6"]
# ///
"""Offline tests for `skill_trigger_eval.py` (REQ-SKAUTH-061 / REQ-SKAUTH-062, plan-072 Issue 2.3).

No live model, no network, no `~/.cache`. Fixtures under `fixtures/trigger-eval/` are trimmed
from plan-072's EXP-003 runs:

- `streams/<h>-<id>-<n>.jsonl`: tool-call events only, the first 8 per run, with absolute paths
  rewritten to `$HOME` / `$CLONE`. EXP-003 ran INSTALLED mode, so its activations are reads
  of `$HOME/.agents|.claude/skills/<n>/`. The detector is exercised with injected roots.
- `transcripts/`: 13 completed CC runs, the D1-manual main + subagent pair, and one KILLED run
  (no `result`, duplicated `message.id`s), reduced to the assistant usage records the pricer
  reads. `manifest.json` carries each run's recorded `modelUsage.costUSD`.

Run:  uv run scripts/checks/test_skill_trigger_eval.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest  # pyright: ignore[reportMissingImports]  (PEP 723 dependency)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import _trigger_eval_core as core  # noqa: E402  # pyright: ignore[reportMissingImports]
import skill_trigger_eval as ste  # noqa: E402  # pyright: ignore[reportMissingImports]

FIX = HERE / "fixtures" / "trigger-eval"
EXP_INTENTS = json.loads((HERE.parent.parent / "docs/plans/plan-072-james-dixson-bae8de/assets/"
                          "exp-003/intents.json").read_text()) if (HERE.parent.parent /
                          "docs/plans/plan-072-james-dixson-bae8de/assets/exp-003/intents.json").exists() else None
RATES = core.load_rates(HERE / "trigger_eval_rates.json")
HOME = "/home/test"


def stream(path: Path, home=HOME, clone="/clone"):
    for line in path.read_text().splitlines():
        if line.strip():
            yield json.loads(line.replace("$HOME", home).replace("$CLONE", clone))


# ---------------------------------------------------------------------------
# EXP-003 reproduction
# ---------------------------------------------------------------------------

def test_exp003_totals_reproduce():
    """Per-intent totals from committed fixtures: CC 59/63, pi 57/63 (EXP-003's rescore)."""
    if EXP_INTENTS is None:
        pytest.skip("plan-072 EXP-003 intents.json absent (bundle archived); fixture arms below still run")
    assert EXP_INTENTS is not None
    intents = {i["id"]: i for i in EXP_INTENTS}
    tot = {"cc": [0, 0], "pi": [0, 0]}
    for p in sorted((FIX / "streams").glob("*.jsonl")):
        h, iid = p.stem.split("-")[:2]
        it = intents[iid]
        # EXP-003 had no staging root: installed mode.
        acts = core.score_stream(h, stream(p), staging_root=None)["activated"]
        exp = it.get("expect")
        ok = (exp in acts) if exp else not (set(acts) & set(it.get("near") or []))
        tot[h][0] += ok
        tot[h][1] += 1
    assert tot["cc"] == [59, 63]
    assert tot["pi"] == [57, 63]


# ---------------------------------------------------------------------------
# detector
# ---------------------------------------------------------------------------

def _pi_read(path):
    return {"type": "message_end", "message": {"role": "assistant", "content": [
        {"type": "toolCall", "name": "read", "arguments": {"path": path}}]}}


def test_pi_staging_read_counts_repo_read_does_not():
    st = "/cache/staging-x"
    assert core.score_stream("pi", [_pi_read(f"{st}/yf-okf/SKILL.md")], st)["activated"] == ["yf-okf"]
    assert core.score_stream("pi", [_pi_read("/clone/skills/yf-okf/SKILL.md")], st)["activated"] == []
    assert core.score_stream("pi", [_pi_read("skills/yf-okf/SKILL.md")], st)["activated"] == []


def test_cc_skill_tool_and_yf_skill_dir_count():
    ev = {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Skill", "input": {"skill": "yf-drift-check"}},
        {"type": "tool_use", "name": "Bash", "input": {"command": "D=$(yf skill-dir yf-okf)"}}]}}
    assert core.score_stream("cc", [ev], None)["activated"] == ["yf-drift-check", "yf-okf"]


def test_detector_stops_at_max_tools():
    evs = [_pi_read("/x/a") for _ in range(core.MAX_TOOLS)] + [_pi_read("/st/yf-okf/SKILL.md")]
    assert core.score_stream("pi", evs, "/st")["activated"] == []


def test_cc_slash_command_expansion_counts_from_transcript():
    st = "/cache/clone/.claude/skills"
    user_cmd = json.dumps({"type": "user", "message": {"role": "user", "content":
        "<command-message>yf-research</command-message>\n<command-name>/yf-research</command-name>"}})
    user_base = json.dumps({"type": "user", "message": {"role": "user", "content": [{"type": "text",
        "text": f"Base directory for this skill: {st}/yf-plan\n\n# yf-plan"}]}})
    quoted = json.dumps({"type": "assistant", "message": {"content": [{"type": "text",
        "text": "you could run <command-name>/yf-herdr</command-name>"}]}})
    assert core.transcript_activations([user_cmd, user_base, quoted], st) == ["yf-research", "yf-plan"]
    assert core.transcript_activations([quoted], st) == []


def test_near_miss_cell_rate_is_correct_outcome_rate():
    nm = {"id": "N", "kind": "near-miss", "siblings": ["yf-okf"]}
    assert core.correct(nm, []) is True
    assert core.correct(nm, ["yf-okf-hygiene"]) is True  # a different, correct route
    assert core.correct(nm, ["yf-okf"]) is False
    tr = {"id": "T", "kind": "trigger", "skill": "yf-okf"}
    assert core.correct(tr, ["yf-plan", "yf-okf"]) is True
    assert core.correct(tr, ["yf-plan"]) is False


# ---------------------------------------------------------------------------
# load verification → INCONCLUSIVE
# ---------------------------------------------------------------------------

REAL_CC_INIT = {  # captured at pass-2: 15 yf names with 20 staged (5 are user-invocable: false)
    "type": "system", "subtype": "init", "permissionMode": "bypassPermissions",
    "skills": ["yf-beads-hygiene", "yf-beads-init", "yf-beads-upstream", "yf-change-validation",
               "yf-diagram-authoring", "yf-herdr", "yf-incubator", "yf-markdown-format",
               "yf-markdown-html", "yf-markdown-lint", "yf-markdown-pdf", "yf-okf",
               "yf-okf-hygiene", "yf-plan", "yf-research", "update-config", "debug"]}
USER_INVOCABLE = set(REAL_CC_INIT["skills"]) - {"update-config", "debug"}


def test_real_cc_init_passes_user_invocable_subset():
    assert len(USER_INVOCABLE) == 15
    ok, why = core.cc_init_ok(REAL_CC_INIT, USER_INVOCABLE)
    assert ok, why


def test_cc_init_wrong_permission_mode_inconclusive():
    ok, why = core.cc_init_ok(dict(REAL_CC_INIT, permissionMode="default"), USER_INVOCABLE)
    assert not ok and "permissionMode" in why


def test_cc_debug_log_load_line():
    good = "... Loaded 20 unique skills (20 unconditional, 0 conditional, managed: 0, user: 0, project: 20, additional: 0)"
    shadowed = "Loaded 59 unique skills (59 unconditional, 0 conditional, managed: 0, user: 39, project: 20, additional: 0)"
    assert core.cc_debug_load_ok(good, 20)[0]
    assert not core.cc_debug_load_ok(shadowed, 20)[0]
    assert not core.cc_debug_load_ok("no load line here", 20)[0]
    assert not core.cc_debug_load_ok(good, 19)[0]


def _pi_system(skills: dict):
    body = "".join(f"<skill>\n<name>{n}</name>\n<description>{core.html.escape(d)}</description>\n"
                   f"<location>/x/{n}/SKILL.md</location>\n</skill>\n" for n, d in skills.items())
    return {"type": "message_end", "message": {"role": "system", "sections": {
        "skills": f"<skills>\n<available_skills>\n{body}</available_skills>\n</skills>"}}}


def test_pi_description_hash_match_and_mismatch():
    want = {"yf-okf": "Checks one bundle's 'OKF' conformance & more."}
    assert core.pi_load_ok([_pi_system(want)], want)[0]
    # a trailing block-scalar newline must not count as a mismatch
    assert core.pi_load_ok([_pi_system({"yf-okf": want["yf-okf"] + "\n"})], want)[0]
    ok, why = core.pi_load_ok([_pi_system({"yf-okf": "OLD INSTALLED TEXT"})], want)
    assert not ok and "hash mismatch" in why
    assert not core.pi_load_ok([_pi_system({})], want)[0]


def test_auth_failure_text_detected():
    assert core.looks_like_auth_failure("Not logged in · Please run /login")
    assert not core.looks_like_auth_failure("some other stderr")


def test_missing_binary_inconclusive(monkeypatch):
    monkeypatch.setattr(ste.shutil, "which", lambda b: None)
    assert ste.harness_available("cc") == "claude not on PATH"
    assert ste.main(["--harness", "pi", "--skills", "yf-okf", "--reps", "1"]) == core.EXIT_INCONCLUSIVE


# ---------------------------------------------------------------------------
# staging, confirmation, verdict, false-FAIL rate
# ---------------------------------------------------------------------------

def test_staging_cleared_on_reset(tmp_path):
    root = tmp_path / "repo"
    (root / "skills" / "a").mkdir(parents=True)
    (root / "skills" / "a" / "SKILL.md").write_text("---\nname: a\ndescription: x\n---\n")
    clone = tmp_path / "clone"
    clone.mkdir()
    st, h1 = ste.stage(clone, root, "cc", ["a"])
    (st / "a" / "STRAY").write_text("left behind by a run")
    (st / "zzz").mkdir()
    st2, h2 = ste.stage(clone, root, "cc", ["a"])
    assert not (st2 / "a" / "STRAY").exists() and not (st2 / "zzz").exists()
    assert h1 == h2
    (st2 / "a" / "SKILL.md").write_text("tampered")
    assert not ste.verify_staged(st2, h2)[0]


def test_confirmation_only_for_regressed_cells():
    miss3 = [False, False, True]
    assert core.cell_verdict([True, True, False], None, 1.0, False) == "pass"
    assert core.cell_verdict(miss3, None, 1.0, False) == "needs-confirm"   # regressed
    assert core.cell_verdict(miss3, None, 0.33, False) == "pass"           # never passed
    assert core.cell_verdict(miss3, None, None, False) == "pass"           # never recorded
    assert core.cell_verdict(miss3, None, 1.0, True) == "pass"             # accepted miss
    assert core.cell_verdict(miss3, [True, True, False], 1.0, False) == "pass"   # pooled 3/6
    assert core.cell_verdict(miss3, [False, True, False], 1.0, False) == "fail"  # pooled 2/6


def test_false_fail_rate_two_stage_formula():
    assert abs(core.false_fail_rate(240, 0.95) - 0.0165) <= 0.0005
    assert abs(core.false_fail_rate(240, 0.90) - 0.219) <= 0.0005


def test_rating_four_states():
    its = [{"id": "T1"}, {"id": "N1"}]

    def rec(r):
        return {"cells": {f"{i}:{h}": {"rate": r.get(i, 1.0)} for i in ("T1", "N1") for h in ("pi", "cc")}}
    assert core.rating(1100, rec({}), [], its)["rating"] == "loose"
    assert core.rating(500, rec({}), [], its)["rating"] == "crisp"
    assert core.rating(800, rec({}), [], its)["rating"] == "satisfactory"
    assert core.rating(500, rec({"T1": 0.33}), [], its)["rating"] == "unrouted"
    acc = core.rating(500, rec({"T1": 0.33}), ["T1"], its)
    assert acc["rating"] == "satisfactory" and core.display(acc) == "satisfactory (accepted misses: T1)"
    assert core.rating(500, None, [], its)["rating"] is None


# ---------------------------------------------------------------------------
# spend
# ---------------------------------------------------------------------------

def _lines(name):
    return (FIX / "transcripts" / name).read_text().splitlines()


def test_rates_reproduce_recorded_costs():
    manifest = json.loads((FIX / "transcripts" / "manifest.json").read_text())
    runs = [m for m in manifest if m["run"] not in ("killed", "cc-D1-manual")]
    assert len(runs) == 13
    for m in runs:
        got = core.price_session(_lines(f"{m['run']}.jsonl"), [], RATES)
        assert abs(got["usd"] - m["recorded_cost_usd"]) < 1e-9, m["run"]


def test_main_plus_subagents_prices_manual_run():
    main, sub = _lines("cc-D1-manual.jsonl"), _lines("cc-D1-manual.sub0.jsonl")
    got = core.price_session(main, [sub], RATES)
    assert round(got["usd"], 4) == 0.6732
    assert got["tokens"]["cache_write_1h"] > 0 and got["tokens"]["cache_write_5m"] > 0
    assert core.price_session(main, [], RATES)["usd"] < 0.5  # main-only undercounts


def test_killed_run_dedup_by_message_id():
    lines = _lines("killed.jsonl")
    ids = [json.loads(x)["message"]["id"] for x in lines]
    assert len(ids) > len(set(ids)), "fixture must carry duplicated message.ids"
    by, _ = core.transcript_usage(lines)
    last = {}
    for x in lines:
        e = json.loads(x)
        last[e["message"]["id"]] = e["message"]["usage"]
    want, _ = core.price_usage(list(last.values()), RATES["claude-opus-5-5"])
    got = core.price_session(lines, [], RATES)
    assert len(by) == len(set(ids))
    assert abs(got["usd"] - want) < 1e-12


def test_unknown_model_inconclusive():
    lines = [x.replace("claude-opus-5-5", "claude-future-9") for x in _lines("cc-V1-1790284984.jsonl")]
    assert "inconclusive" in core.price_session(lines, [], RATES)


def test_ledger_accumulates_and_budget_trips(tmp_path):
    led = tmp_path / "spend.jsonl"
    b = ste.Budget(led, 1.0)
    b.record({"harness": "cc", "intent": "X", "cc_usd": 0.6})
    b.record({"harness": "pi", "intent": "Y", "cc_usd": 0.0})
    assert b.check()
    b2 = ste.Budget(led, 1.0)  # a NEW invocation reads the cumulative total
    assert abs(b2.total - 0.6) < 1e-12
    b2.record({"harness": "cc", "intent": "Z", "cc_usd": 0.5})
    assert not b2.check() and b2.tripped
    assert all(isinstance(json.loads(x)["cc_usd"], float) for x in led.read_text().splitlines())


def test_cc_project_slug():
    assert core.cc_project_slug("/Users/james/.cache/plan072-eval/clone-cc") == \
        "-Users-james--cache-plan072-eval-clone-cc"


# ---------------------------------------------------------------------------
# offline verbs (each exits 1 on a violating fixture), and --record as sole writer
# ---------------------------------------------------------------------------

def _mini_repo(tmp_path, desc="Short. TRIGGER when: x. SKIP for: y.", recorded=True, decision=None,
               rate_t=1.0, n_t=3, n_n=3):
    root = tmp_path / "r"
    for name in ("sk-a", "sk-b"):
        d = root / "skills" / name
        (d / "evals").mkdir(parents=True)
        (d / "SKILL.md").write_text(f'---\nname: {name}\ndescription: "{desc}"\n---\n')
        other = "sk-b" if name == "sk-a" else "sk-a"
        its = [{"id": f"{name}-T{i}", "kind": "trigger", "skill": name, "prompt": "p"} for i in range(n_t)]
        its += [{"id": f"{name}-N{i}", "kind": "near-miss", "siblings": [name, other], "prompt": "p"}
                for i in range(n_n)]
        doc = {"skill": name, "intents": its}
        if recorded:
            doc["recorded"] = {"description_sha256": core.sha256_text(desc), "cells": {
                f"{i['id']}:{h}": {"rate": rate_t if i["kind"] == "trigger" else 1.0, "correct": 3, "reps": 3}
                for i in its for h in ("pi", "cc")}}
        if decision:
            doc["decision"] = decision
        (d / "evals" / "triggers.json").write_text(json.dumps(doc))
    return root


def _run(root, *args):
    return ste.main(["--root", str(root), *args])


def test_validate_intents_verb(tmp_path):
    assert _run(_mini_repo(tmp_path), "--validate-intents") == 0
    assert _run(_mini_repo(tmp_path / "x", n_n=2), "--validate-intents") == 1


def test_require_rated_verb(tmp_path):
    assert _run(_mini_repo(tmp_path), "--report", "--require-rated") == 0
    assert _run(_mini_repo(tmp_path / "x", recorded=False), "--report", "--require-rated") == 1


def test_require_rated_flags_stale_record(tmp_path):
    root = _mini_repo(tmp_path)
    p = root / "skills" / "sk-a" / "SKILL.md"
    p.write_text('---\nname: sk-a\ndescription: "Edited after the record."\n---\n')
    assert _run(root, "--report", "--require-rated") == 1


def test_forbid_verb(tmp_path):
    assert _run(_mini_repo(tmp_path), "--report", "--forbid", "loose,unrouted") == 0
    assert _run(_mini_repo(tmp_path / "x", rate_t=0.33), "--report", "--forbid", "loose,unrouted") == 1
    long = "x" * 1100
    assert _run(_mini_repo(tmp_path / "y", desc=long), "--report", "--forbid", "loose,unrouted") == 1


def test_require_decision_for_noncrisp_verb(tmp_path):
    long = "y" * 700  # satisfactory, not crisp
    assert _run(_mini_repo(tmp_path, desc=long), "--report", "--require-decision-for-noncrisp") == 1
    dec = {"status": "accepted", "reason": "r", "date": "2026-09-25"}
    assert _run(_mini_repo(tmp_path / "x", desc=long, decision=dec), "--report",
                "--require-decision-for-noncrisp") == 0
    assert _run(_mini_repo(tmp_path / "y"), "--report", "--require-decision-for-noncrisp") == 0


def test_record_is_the_only_writer(tmp_path):
    """Offline verbs never write; only write_record (reached only via --record) does."""
    root = _mini_repo(tmp_path)
    before = {p: p.read_bytes() for p in root.rglob("triggers.json")}
    for args in (["--validate-intents"], ["--report", "--require-rated"], ["--report", "--json"]):
        _run(root, *args)
    assert before == {p: p.read_bytes() for p in root.rglob("triggers.json")}
    src = (HERE / "skill_trigger_eval.py").read_text()
    writes = [ln for ln in src.splitlines() if "triggers_path(" in ln and ".write_text(" in ln]
    assert len(writes) == 1
    assert "if args.record and not budget.tripped and not throttle.exhausted:" in src


def test_report_prints_n_and_rate(tmp_path, capsys):
    _run(_mini_repo(tmp_path), "--report")
    out = capsys.readouterr().out
    assert "cells N=24" in out and "false-FAIL rate" in out


def test_eval_env_strips_outward_write_credentials(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "secret")
    monkeypatch.setenv("HERDR_PANE_ID", "w1:p1")
    monkeypatch.setenv("YF_PARENT_PANE", "w1:p1")
    env = ste.eval_env()
    assert env["GITHUB_TOKEN"] == "" and env["GH_TOKEN"] == ""
    assert "HERDR_PANE_ID" not in env and "YF_PARENT_PANE" not in env
    assert env["HERDR_ENV"] == "1" and not Path(env["HERDR_SOCKET_PATH"]).exists()
    assert env["GH_CONFIG_DIR"].endswith("gh-empty")


# ---------------------------------------------------------------------------
# throttling + invalid runs (REQ-SKAUTH-062 as amended at the Issue 3.2 incident)
# ---------------------------------------------------------------------------

# The two measured signatures, verbatim from the incident.
CC_LIMIT_TEXT = ('{"type":"assistant","message":{"content":[{"type":"text","text":'
                 '"You\'ve hit your session limit \u00b7 resets 1:30pm (America/Los_Angeles)"}]}}')
PI_429 = ('Error: 429: {"code":"model_cooldown","last_upstream_error":"rate_limit_error: This request '
          'would exceed your account\'s rate limit.","model":"claude-opus-5-5","provider":"claude",'
          '"reset_seconds":10491,"reset_time":"2h54m51s"}')


def test_zero_token_run_is_inconclusive():
    assert core.run_validity("", "", {}) == ("zero-tokens", None)
    assert core.run_validity("", "", {"input": 0, "output": 0, "cache_read": 0}) == ("zero-tokens", None)
    assert core.run_validity("", "", {"input": 2, "output": 90}) == ("ok", None)


def test_429_signatures_are_inconclusive_with_reset():
    assert core.run_validity("", PI_429, {"input": 0}) == ("rate-limited", 10491)
    v, reset = core.run_validity(CC_LIMIT_TEXT, "", {})
    assert v == "rate-limited" and reset is None
    # A stderr 429 wins even if some tokens were counted.
    assert core.run_validity("", PI_429, {"input": 50})[0] == "rate-limited"


def test_rate_limit_phrase_in_served_stream_is_not_a_limit():
    """Measured false positive: pi's system prompt (tool docs) says 'rate limit'. A run that
    was served (tokens > 0) must not be classed rate-limited from stream text."""
    served = '{"type":"message_end","message":{"role":"system","sections":{"tools":"lower the value when the target host enforces a per-IP rate limit you cannot raise"}}}'
    assert core.run_validity(served, "", {"input": 4, "output": 108}) == ("ok", None)
    assert core.run_validity(served, "", {})[0] == "rate-limited"  # zero tokens: suspicious


class FakeClock:
    def __init__(self):
        self.t = 0.0
        self.slept = []

    def clock(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def test_throttle_spacing_is_global():
    fc = FakeClock()
    th = core.Throttle(150, 3600, fc.clock, fc.sleep)
    starts = []
    for _ in range(4):  # both harnesses draw from the same instance
        assert th.acquire()
        starts.append(fc.t)
    gaps = [b - a for a, b in zip(starts, starts[1:], strict=False)]
    assert all(abs(g - 24.0) < 1e-9 for g in gaps)  # 3600/150


def test_backoff_honours_reset_seconds_and_halves_rate():
    fc = FakeClock()
    th = core.Throttle(150, 99999, fc.clock, fc.sleep)
    th.acquire()
    assert th.rate_limited(600)
    assert th.per_hour == 75
    th.acquire()
    assert fc.t >= 605  # reset_seconds + 5 s margin, for BOTH harnesses (shared pause)


def test_backoff_exponential_without_reset_and_bounded():
    fc = FakeClock()
    th = core.Throttle(150, 60 + 120 + 240, fc.clock, fc.sleep)
    assert th.rate_limited(None) and th.backoff_total == 60
    assert th.rate_limited(None) and th.backoff_total == 180
    assert th.rate_limited(None) and th.backoff_total == 420
    assert not th.rate_limited(None)  # 480 more would exceed the bound
    assert th.exhausted and not th.acquire()


def test_deadline_stops_before_outer_timeout():
    fc = FakeClock()
    th = core.Throttle(3600, 99999, fc.clock, fc.sleep, deadline_s=core.TIMEOUT_S + 10)
    assert th.acquire()          # t=0: 0+150 <= 160
    fc.t = 20.0
    assert not th.acquire()      # 20+150 > 160: would be killed mid-run
    assert th.exhausted and th.deadline_hit


def test_resume_skips_completed_runs(tmp_path):
    rp = tmp_path / "results.jsonl"
    rows = [{"harness": "pi", "intent": "K1", "rep": 0, "correct": True},
            {"harness": "cc", "intent": "K1", "rep": 0, "correct": None},  # invalid: never loaded
            {"harness": "pi", "intent": "K1", "rep": 1, "correct": False}]
    rp.write_text("".join(json.dumps(r) + "\n" for r in rows))
    done = core.load_results(rp)
    assert set(done) == {"pi|K1|0", "pi|K1|1"}
    store = ste.Results(rp, done)
    assert store.has("pi", "K1", 0) and not store.has("cc", "K1", 0)
    store.add({"harness": "cc", "intent": "K1", "rep": 0, "correct": True})
    store.add({"harness": "cc", "intent": "K1", "rep": 1, "correct": None})  # not persisted
    assert set(core.load_results(rp)) == {"pi|K1|0", "pi|K1|1", "cc|K1|0"}


def test_run_harness_resume_and_ratelimit_retry(tmp_path, monkeypatch):
    """Resumed runs are not re-run; a rate-limited run is retried, never recorded."""
    calls = []
    seq = iter([{"invalid": "rate-limited", "reset_seconds": 1, "correct": None, "inconclusive": "x"},
                {"correct": True, "activated": ["sk"], "cc_usd": 0.0, "tokens": {"input": 1}}])

    def fake_run_one(h, clone, root, st, hashes, names, intent, *a):
        calls.append(intent["id"])
        return dict(next(seq), harness=h, intent=intent["id"])
    monkeypatch.setattr(ste, "run_one", fake_run_one)
    monkeypatch.setattr(ste, "prepare_clone", lambda root, h, tag: tmp_path)
    monkeypatch.setattr(ste, "stage", lambda *a: (tmp_path, {}))
    monkeypatch.setattr(ste, "frontmatter", lambda p: {"description": "d"})
    fc = FakeClock()
    th = core.Throttle(3600, 999, fc.clock, fc.sleep)
    store = ste.Results(tmp_path / "r.jsonl", {"pi|A|0": {"harness": "pi", "intent": "A", "rep": 0,
                                                           "correct": True}})
    out = ste.run_harness("pi", tmp_path, ["sk"], [{"id": "A"}, {"id": "B"}], 1, "candidate",
                          ste.Budget(None, None), {}, "t", th, store)
    assert calls == ["B", "B"]  # A resumed; B retried once after the rate limit
    assert [r["intent"] for r in out] == ["A", "B"] and all(r["correct"] for r in out)
    assert th.per_hour == 1800 and fc.t >= 6
    assert set(core.load_results(tmp_path / "r.jsonl")) == {"pi|B|0"}


class _Exited:
    pid = 999999

    def poll(self):
        return None  # looks alive, but the group is gone

    def wait(self, t=None):
        return 0


@pytest.mark.parametrize("exc", [ProcessLookupError, PermissionError])
def test_kill_tolerates_gone_group(monkeypatch, exc):
    def boom(pid, sig):
        raise exc()
    monkeypatch.setattr(ste.os, "killpg", boom)
    ste.kill(_Exited())  # type: ignore[arg-type]  # a Popen stand-in; must not raise


if __name__ == "__main__":
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-q"]))
