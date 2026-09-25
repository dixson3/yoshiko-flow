"""Pure logic for `skill_trigger_eval.py` (REQ-SKAUTH-061 / REQ-SKAUTH-062, plan-072).

No subprocesses, no model calls, no filesystem writes. Everything here is importable by the
offline tests: activation detection over stream events, cell scoring, CC transcript pricing,
the four-state rating, the FULL-row regression verdict, and the stated false-FAIL rate.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from math import comb
from pathlib import Path

MAX_TOOLS = 6
TIMEOUT_S = 150
CRISP_MAX = 600
HARD_MAX = 1024
THRESHOLD = 0.5
HARNESSES = ("pi", "cc")

YF_SKILL_DIR_RE = re.compile(r"yf skill-dir ([a-z0-9-]+)")
# An INSTALLED skill dir. Matches both harnesses' install roots, in both scopes.
INSTALLED_RE = re.compile(r"\.(?:agents|claude)/skills/([a-z0-9-]+)/")

EXIT_PASS, EXIT_FAIL, EXIT_INCONCLUSIVE = 0, 1, 4


class EvalInconclusive(Exception):
    """The instrument could not measure (unreadable ledger/rates, load mismatch). Exit 4."""


# ---------------------------------------------------------------------------
# lengths / hashes
# ---------------------------------------------------------------------------

def utf16_len(s: str) -> int:
    """REQ-YF-EMBED-007's unit: UTF-16 code units (JS `String.length`)."""
    return len(s.encode("utf-16-le")) // 2


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# activation detection (REQ-SKAUTH-062 "Detector")
# ---------------------------------------------------------------------------

def tool_calls(harness: str, ev: dict):
    """Yield (name, args) for each tool call carried by one stream event."""
    if harness == "cc" and ev.get("type") == "assistant":
        for c in (ev.get("message") or {}).get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                yield c.get("name"), c.get("input") or {}
    elif harness == "pi" and ev.get("type") == "message_end":
        m = ev.get("message") or {}
        if m.get("role") == "assistant":
            for c in m.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "toolCall":
                    yield c.get("name"), c.get("arguments") or {}


def activations(harness: str, name: str | None, args: dict,
                staging_root: str | None) -> list[str]:
    """Skill names this ONE tool call activates.

    Signals: a CC `Skill` tool call; args touching `<staging_root>/<n>/`; args touching an
    INSTALLED `.agents|.claude/skills/<n>/`; `yf skill-dir <n>`. The repository's own
    `skills/<n>/` is never counted, because reading source is not activation: a bare
    `skills/<n>/` path matches none of the patterns unless it sits under the staging root.
    """
    out: list[str] = []

    def add(n: str):
        if n and n not in out:
            out.append(n)

    if harness == "cc" and name == "Skill":
        add(str(args.get("skill") or args.get("command") or "").split(":")[-1].strip())
    blob = json.dumps(args)
    if staging_root:
        root = staging_root.rstrip("/") + "/"
        for m in re.finditer(re.escape(root) + r"([a-z0-9-]+)/", blob):
            add(m.group(1))
    for n in INSTALLED_RE.findall(blob):
        add(n)
    for n in YF_SKILL_DIR_RE.findall(blob):
        add(n)
    return out


def score_stream(harness: str, events, staging_root: str | None,
                 max_tools: int = MAX_TOOLS) -> dict:
    """Walk a run's events up to `max_tools` tool calls; return activations in order."""
    acts: list[str] = []
    n = 0
    for ev in events:
        for name, args in tool_calls(harness, ev):
            n += 1
            if n > max_tools:
                return {"activated": acts, "n_tools": n - 1}
            for a in activations(harness, name, args, staging_root):
                if a not in acts:
                    acts.append(a)
    return {"activated": acts, "n_tools": n}


def correct(intent: dict, activated: list[str]) -> bool:
    """REQ-SKAUTH-062 cell outcome. Should-trigger: the expected skill activated.
    Near-miss: none of its named siblings activated."""
    if intent["kind"] == "trigger":
        return intent["skill"] in activated
    return not (set(activated) & set(intent.get("siblings") or []))


# ---------------------------------------------------------------------------
# load verification (candidate mode)
# ---------------------------------------------------------------------------

LOADED_RE = re.compile(r"Loaded (\d+) unique skills \((.*?)\)")


def cc_debug_load_ok(debug_text: str, staged_count: int) -> tuple[bool, str]:
    """The debug log must show `user: 0, project: <N>` with N = the staged count."""
    found = list(LOADED_RE.finditer(debug_text))
    m = found[-1] if found else None  # the last load line is the settled one
    if m is None:
        return False, "debug log has no 'Loaded <N> unique skills' line"
    detail = m.group(2)
    user = re.search(r"\buser: (\d+)", detail)
    proj = re.search(r"\bproject: (\d+)", detail)
    if not user or not proj:
        return False, f"unparseable load line: {m.group(0)}"
    if user.group(1) != "0" or proj.group(1) != str(staged_count):
        return False, (f"load line {m.group(0)!r} is not user: 0, project: {staged_count} "
                       "(the user-scope install may be shadowing the candidate)")
    return True, "ok"


def cc_init_ok(init: dict | None, user_invocable: set[str]) -> tuple[bool, str]:
    if not init:
        return False, "no CC init event"
    if init.get("permissionMode") != "bypassPermissions":
        return False, f"init permissionMode is {init.get('permissionMode')!r}, not bypassPermissions"
    missing = user_invocable - set(init.get("skills") or [])
    if missing:
        return False, f"init skills missing staged user-invocable {sorted(missing)}"
    return True, "ok"


PI_SKILL_RE = re.compile(r"<skill>\s*<name>(.*?)</name>\s*<description>(.*?)</description>", re.S)


def pi_descriptions(system_event: dict) -> dict[str, str]:
    """{name: description} from pi's system-message `sections.skills` (XML-escaped)."""
    sec = ((system_event.get("message") or {}).get("sections") or {}).get("skills") or ""
    return {html.unescape(n).strip(): html.unescape(d) for n, d in PI_SKILL_RE.findall(sec)}


def pi_load_ok(events, expected: dict[str, str]) -> tuple[bool, str]:
    """Every staged description must appear verbatim (by sha256) in pi's system prompt."""
    for ev in events:
        if ev.get("type") == "message_end" and (ev.get("message") or {}).get("role") == "system":
            seen = pi_descriptions(ev)
            for name, desc in expected.items():
                if name not in seen:
                    return False, f"pi did not load staged skill {name}"
                # Compare after trimming SURROUNDING whitespace only. A `>` block scalar's
                # clip-chomping newline survives differently through pi's YAML parser and
                # PyYAML (measured: yf-markdown-format, 583 vs 582); interior text, which
                # is what routes, must match byte-for-byte.
                if sha256_text(seen[name].strip()) != sha256_text(desc.strip()):
                    return False, f"pi description hash mismatch for {name}"
            return True, "ok"
    return False, "no pi system-message event"


AUTH_FAIL_RE = re.compile(r"not logged in|please run /login|authentication|unauthori[sz]ed|"
                          r"invalid api key|no api key", re.I)


def looks_like_auth_failure(text: str) -> bool:
    return bool(AUTH_FAIL_RE.search(text or ""))


# ---------------------------------------------------------------------------
# CC spend (REQ-SKAUTH-062 "Spend ledger")
# ---------------------------------------------------------------------------

def load_rates(path: Path) -> dict:
    try:
        doc = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        raise EvalInconclusive(f"cannot read rate table {path}: {e}") from e
    return {k: v for k, v in doc.items() if not k.startswith("_")}


def transcript_usage(lines) -> tuple[dict[str, dict], str | None]:
    """{message.id: usage} (LAST usage per id wins) and the model, from transcript lines."""
    by: dict[str, dict] = {}
    model = None
    for line in lines:
        try:
            e = json.loads(line)
        except ValueError:
            continue
        m = e.get("message") or {}
        if e.get("type") == "assistant" and m.get("id") and m.get("usage"):
            by[m["id"]] = m["usage"]
            model = m.get("model") or model
    return by, model


def price_usage(usages, rates: dict) -> tuple[float, dict]:
    """USD and token totals for a list of CC usage objects at per-class list rates."""
    tok = {"input": 0, "cache_write_1h": 0, "cache_write_5m": 0, "cache_read": 0, "output": 0}
    for u in usages:
        cc = u.get("cache_creation") or {}
        tok["input"] += u.get("input_tokens", 0) or 0
        if cc:
            tok["cache_write_1h"] += cc.get("ephemeral_1h_input_tokens", 0) or 0
            tok["cache_write_5m"] += cc.get("ephemeral_5m_input_tokens", 0) or 0
        else:
            tok["cache_write_5m"] += u.get("cache_creation_input_tokens", 0) or 0
        tok["cache_read"] += u.get("cache_read_input_tokens", 0) or 0
        tok["output"] += u.get("output_tokens", 0) or 0
    usd = sum(tok[k] * rates[k] for k in tok) / 1e6
    return usd, tok


def price_session(main_lines, subagent_line_lists, rates_by_model: dict) -> dict:
    """Price one CC session: the main transcript plus every subagent transcript.

    Returns {"usd", "tokens", "model"} or {"inconclusive": reason}."""
    usages, models = [], set()
    for lines in [main_lines, *subagent_line_lists]:
        by, model = transcript_usage(lines)
        usages.extend(by.values())
        if model:
            models.add(model)
    if not usages:
        return {"inconclusive": "no assistant usage in transcript"}
    unknown = models - set(rates_by_model)
    if unknown or not models:
        return {"inconclusive": f"model(s) {sorted(unknown) or ['<none>']} not in rate table"}
    if len(models) > 1:
        return {"inconclusive": f"mixed models {sorted(models)} in one session"}
    model = models.pop()
    usd, tok = price_usage(usages, rates_by_model[model])
    return {"usd": usd, "tokens": tok, "model": model}


def cc_project_slug(cwd: str) -> str:
    """~/.claude/projects/<slug>: CC replaces `/` and `.` in the realpath cwd with `-`."""
    return re.sub(r"[/.]", "-", cwd)


def ledger_total(path: Path) -> float:
    if not path.exists():
        return 0.0
    total = 0.0
    try:
        for line in path.read_text().splitlines():
            if line.strip():
                total += float(json.loads(line).get("cc_usd") or 0)
    except (OSError, ValueError, TypeError) as e:
        raise EvalInconclusive(f"cannot read spend ledger {path}: {e}") from e
    return total


# ---------------------------------------------------------------------------
# rating + verdict (REQ-SKAUTH-061, REQ-SKAUTH-062 "FULL-row verdict")
# ---------------------------------------------------------------------------

def cell_key(intent_id: str, harness: str) -> str:
    return f"{intent_id}:{harness}"


def rate(results: list[bool]) -> float | None:
    return (sum(results) / len(results)) if results else None


def rating(desc_len: int, recorded: dict | None, accepted: list[str], intents: list[dict]) -> dict:
    """Four-state rating from RECORDED per-cell rates. Never hand-asserted."""
    if desc_len > HARD_MAX:
        return {"rating": "loose", "misses": []}
    if not recorded or not recorded.get("cells"):
        return {"rating": None, "misses": [], "reason": "no recorded rating"}
    cells = recorded["cells"]
    misses = []
    for it in intents:
        for h in HARNESSES:
            c = cells.get(cell_key(it["id"], h))
            if c is None or c.get("rate") is None:
                return {"rating": None, "misses": [], "reason": f"cell {it['id']}:{h} unrecorded"}
            if c["rate"] < THRESHOLD:
                misses.append(it["id"])
    misses = sorted(set(misses))
    unaccepted = [m for m in misses if m not in set(accepted)]
    if unaccepted:
        return {"rating": "unrouted", "misses": misses}
    if misses:
        return {"rating": "satisfactory", "misses": misses, "accepted": misses}
    return {"rating": "crisp" if desc_len <= CRISP_MAX else "satisfactory", "misses": []}


def display(r: dict) -> str:
    if r.get("rating") is None:
        return "unrated"
    if r.get("accepted"):
        return f"{r['rating']} (accepted misses: {','.join(r['accepted'])})"
    return r["rating"]


def cell_verdict(first3: list[bool], confirm3: list[bool] | None,
                 recorded_rate: float | None, accepted: bool) -> str:
    """FULL-row per-cell verdict: 'pass' | 'fail' | 'needs-confirm'."""
    r = rate(first3)
    if r is not None and r >= THRESHOLD:
        return "pass"
    if accepted or recorded_rate is None or recorded_rate < THRESHOLD:
        return "pass"  # not a regression: accepted, or it never passed
    if confirm3 is None:
        return "needs-confirm"
    pooled = rate(first3 + confirm3)
    return "pass" if pooled is not None and pooled >= THRESHOLD else "fail"


def false_fail_rate(n_cells: int, p: float) -> float:
    """1 - (1 - q)^N; q = P(first 3 have <=1 correct AND pooled 6 have <=2 correct)."""
    def b(k):
        return comb(3, k) * p ** k * (1 - p) ** (3 - k)
    q = sum(b(a) * b(c) for a in range(2) for c in range(3 - a))
    return 1 - (1 - q) ** n_cells


# ---------------------------------------------------------------------------
# intent-set validation
# ---------------------------------------------------------------------------

def validate_intents(name: str, doc: dict, all_skills: set[str],
                     min_trigger: int, min_nearmiss: int) -> list[str]:
    errs = []
    if doc.get("skill") != name:
        errs.append(f"{name}: 'skill' is {doc.get('skill')!r}")
    intents = doc.get("intents")
    if not isinstance(intents, list):
        return errs + [f"{name}: 'intents' is not a list"]
    ids = [i.get("id") for i in intents]
    if len(ids) != len(set(ids)):
        errs.append(f"{name}: duplicate intent ids")
    nt = nn = 0
    for it in intents:
        iid = it.get("id")
        if not iid or not isinstance(it.get("prompt"), str) or not it["prompt"].strip():
            errs.append(f"{name}: intent {iid!r} lacks id or prompt")
            continue
        if it.get("kind") == "trigger":
            nt += 1
            if it.get("skill") != name:
                errs.append(f"{name}: trigger intent {iid} must name skill {name}")
        elif it.get("kind") == "near-miss":
            nn += 1
            sib = it.get("siblings")
            if not sib or not isinstance(sib, list):
                errs.append(f"{name}: near-miss {iid} names no siblings")
            elif name not in sib:
                errs.append(f"{name}: near-miss {iid} must name {name} among its siblings")
            elif set(sib) - all_skills:
                errs.append(f"{name}: near-miss {iid} names unknown skills {sorted(set(sib) - all_skills)}")
        else:
            errs.append(f"{name}: intent {iid} has kind {it.get('kind')!r}")
        if "fixture" in it and not isinstance(it["fixture"], str):
            errs.append(f"{name}: intent {iid} fixture must be a shell string")
    if nt < min_trigger:
        errs.append(f"{name}: {nt} trigger intents < {min_trigger}")
    if nn < min_nearmiss:
        errs.append(f"{name}: {nn} near-miss intents < {min_nearmiss}")
    return errs
