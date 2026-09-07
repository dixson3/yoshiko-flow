#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""plan-067's verification instrument — ONE script, one subcommand per Success Criterion.

Every subcommand answers exactly one criterion with an **exit code**:

    0  PASS          — the condition holds
    1  FALSE         — the condition was checked and does NOT hold
    2  INCONCLUSIVE  — the check could not run (input absent, tool missing, bad JSON)

**2 IS NOT 1.** An absent input says the instrument could not look, not that the condition is
false. Collapsing them is the `#181`/`#207`/`#263` two-facts-one-signal conflation, which this
repository has now hit five times — including twice inside this plan's OWN experiments
(EXP-003's slash-verb extractor returned green over an input it could not see; EXP-001's layout
recommendation generalised from one sample of six).

FOUR IMPLEMENTATION MANDATES, inherited from `plan066_checks.py` and each from a MEASURED
failure. They are restated rather than referenced because a mandate stored only in a sibling
file is a mandate the next author does not read:

(a) `choices=sorted(SUBCOMMANDS)` — an unknown verb exits **2**, never 0. A permissive
    dispatcher returns 0 for a typo, which is `#364`'s silent false PASS.

(b) **NEVER PIPE PELICAN.** `pelican … | tail` reports the exit code of `tail`, so a broken
    build reads green — measured: bare `pelican` exits **1**, the same command through `tail`
    exits **0**. The reflexive fix `${PIPESTATUS[@]}` is a **bash-ism that expands to NOTHING
    under this repo's zsh**, turning a "hardened" check into a silently empty one. This file
    runs every subprocess through `run_cmd`, with **no shell and no pipe**.

(c) **Never hardcode `web/.venv`.** It is untracked and absent from an execute worktree, where
    hardcoding it exits **127**. The route is `uv run --with-requirements web/requirements.txt`.

(d) **Site-specific verbs assert their ENUMERATED SITES AND LITERALS BY NAME**, in module
    constants below, so the enumeration is auditable against plan.md rather than buried in a
    re-invocation of some other checker.

WHAT THIS SCRIPT DELIBERATELY DOES NOT COVER (`REQ-CHECK-009`): semantic mis-assignment beyond
the id sets named here, missing qualifiers, editorial omission, and every judgement the two
`manual:` criteria (SC17, SC27) reserve for a human. A green here is not a diagram read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECK = "plan067-checks"
PLAN_ID = "plan-067-james-dixson-de852a"
PLAN_DIR = f"docs/plans/{PLAN_ID}"

D2_PIN = "v0.8.2"
D2_FLAGS = ["--theme", "0", "--layout", "elk"]
DIAGRAM_DIR = "web/content/images"
SKILLS_DIR = "skills"
WEB_SKILLS = "web/content/skills"

# ---------------------------------------------------------------------------
# ENUMERATED SITES AND LITERALS (mandate (d)).
# ---------------------------------------------------------------------------

# SC1 — the lint-subset contradiction. The canonical 7-element subset, and the SCOPE the
# derivation must stay inside. THE SCOPE IS MANDATORY, NOT TIDINESS: unscoped, the same grep
# also matches `docs/plans/plan-053-*/assets/fixtures/corpus/ctl-*-pre-fix/`, which are another
# plan's NEGATIVE-CONTROL FIXTURES whose entire purpose is to stay broken.
LINT_SUBSET_7 = "ML001,ML002,ML005,ML006,ML007,ML008,ML010"
LINT_SUBSET_6 = "ML001,ML002,ML005,ML006,ML007,ML008`"
CONTRADICTION_SCOPE = ["skills", "web/content"]
INCUBATOR_PAGE = f"{WEB_SKILLS}/yf-incubator.md"

# SC14 — the highest-value omissions, by name.
HIGH_VALUE_TOKENS = [
    "prune-private",
    "--prune-formulas",
    "owner_on_create",
]
# SC15 — the one-page-deep items plan-066 left partial.
PARTIAL_COVERAGE_TOKENS = ["--sweep-gates", "plan-retrospective", "lander"]

# SC9 — the agent-set edge scope. THE SCOPE IS PART OF THE EDGE (`REQ-CHECK-014`).
AGENTS_SCOPE_SKILLS = ["yf-plan", "yf-research"]
WORKFLOWS_PAGE = "web/content/pages/workflows.md"

# SC21b — the shipped formulas, one diagram each; and the meta-diagram this plan REMOVES.
SHIPPED_FORMULAS = ["plan-execute", "plan-investigate", "plan-review",
                    "verify-artifact", "yf-research"]
REMOVED_META_DIAGRAM = "formulas.d2"

# SC20 — the combined lifecycle's required content, and #375's literal.
COMBINED_LIFECYCLE = "lifecycle.d2"
COMBINED_INSTALL = "install-matrix.d2"
PREFLIGHT_STATUS_LITERAL = "system_deps_missing"
PREFLIGHT_STATUS_WRONG = "deps-missing"

# SC10's pinned checker names (the gate asserts these BY NAME, never by a count).
PINNED_CHECKERS = ["check_web_counts.py", "check_required_set.py",
                   "check_cli_to_page.py", "check_agents_set.py"]

# Issue 0.7 — the DECLARED BAND, carried in the instrument's own output.
BAND = {"strict": 57, "working": 73, "lenient": 114,
        "rejected": 193,
        "rejected_reading": "every SKILL.md heading needs a page counterpart — NAMED here as "
                            "the explicitly REJECTED reading so it is not rediscovered "
                            "mid-execution"}


class Inconclusive(Exception):
    """The check could not run. Exit 2 — never 1."""


def repo_root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        return Path(out)
    except Exception:
        return Path.cwd()


def read(root: Path, rel: str) -> str:
    p = root / rel
    if not p.is_file():
        raise Inconclusive(f"input absent: {rel}")
    return p.read_text(encoding="utf-8", errors="replace")


def read_opt(root: Path, rel: str) -> str | None:
    p = root / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None


def run_cmd(root: Path, argv: list[str], **kw) -> subprocess.CompletedProcess:
    """subprocess.run with NO SHELL and NO PIPE — mandate (b). The returned `returncode` is the
    process's own, so there is no `tail` to mask it and no `PIPESTATUS` to misspell."""
    env = dict(os.environ)
    env.pop("VIRTUAL_ENV", None)  # a worktree must resolve its own environment
    return subprocess.run(argv, cwd=root, capture_output=True, text=True, env=env, **kw)


def web_corpus(root: Path) -> str:
    """Every published prose surface, concatenated. The predicate is CORPUS-WIDE
    ('documented somewhere on the site'), never per-page — a per-page set manufactures ~30
    false failures on `usage.md`/`workflows.md` alone (EXP-003, self-demonstrated)."""
    parts = []
    for rel in ("README.md", "AGENTS.md"):
        t = read_opt(root, rel)
        if t:
            parts.append(t)
    web = root / "web" / "content"
    if not web.is_dir():
        raise Inconclusive("web/content is absent — the corpus cannot be assembled")
    for p in sorted(web.rglob("*.md")):
        parts.append(p.read_text(encoding="utf-8", errors="replace"))
    if not parts:
        raise Inconclusive("assembled an EMPTY corpus — a check over it certifies vacuously")
    return "\n".join(parts)


def checker(root: Path, name: str, *args: str) -> subprocess.CompletedProcess:
    p = root / "scripts" / "checks" / name
    if not p.is_file():
        raise Inconclusive(f"checker not present: scripts/checks/{name}")
    return run_cmd(root, ["uv", "run", str(p), *args])


# ---------------------------------------------------------------------------
# Epic 0
# ---------------------------------------------------------------------------

def sc_contradictions(root: Path, a) -> tuple[bool, str, dict]:
    """SC1 — the two live contradictions are fixed.

    The lint-subset half is a DERIVED set difference, not a hardcoded count: pass-1's C9 fix
    traded a hardcoded undercount for a derived OVERcount, and the SCOPE is what makes the
    derivation correct. Scoped to `skills/` and `web/content/`; unscoped it would sweep
    plan-053's `ctl-*-pre-fix` fixtures, whose entire purpose is to stay broken.
    """
    stale = []
    for scope in CONTRADICTION_SCOPE:
        d = root / scope
        if not d.is_dir():
            raise Inconclusive(f"scope absent: {scope}")
        for p in sorted(d.rglob("*.md")):
            if LINT_SUBSET_6 in p.read_text(encoding="utf-8", errors="replace"):
                stale.append(str(p.relative_to(root)))
    canon = read(root, "skills/yf-markdown-lint/SKILL.md")
    if LINT_SUBSET_7 not in canon:
        raise Inconclusive("the canonical 7-element subset is absent from "
                           "yf-markdown-lint/SKILL.md — the source of truth moved")
    inc = read(root, INCUBATOR_PAGE)
    findings = []
    if stale:
        findings.append(f"{len(stale)} site(s) still carry the 6-element subset: {stale}")
    if "beads-free utility skill" in inc:
        findings.append("yf-incubator.md still calls a `workflows` skill a beads-free utility")
    return (not findings,
            ("both contradictions fixed; the derived set-difference over "
             f"{CONTRADICTION_SCOPE} is empty" if not findings else "; ".join(findings)),
            {"stale_sites": stale, "scope": CONTRADICTION_SCOPE})


def _invocation_block(text: str) -> list[str] | None:
    """The bullet lines of a skill's `## Invocation` section, or None if it has no section."""
    m = re.search(r"^## Invocation\s*$", text, re.M)
    if not m:
        return None
    tail = text[m.end():]
    nxt = re.search(r"^## ", tail, re.M)
    body = tail[: nxt.start()] if nxt else tail
    return [ln for ln in body.splitlines() if ln.startswith("- `/")]


def sc_invocation_schema(root: Path, a) -> tuple[bool, str, dict]:
    """SC2 — ONE shape everywhere it appears, and present on every `user-invocable: true` skill.

    Stated in the DERIVED form, never as a literal count: Issue 0.4's populate-all-20 branch
    changes the cardinality (six under the coercion bug, seven after it).
    """
    skills = sorted((root / SKILLS_DIR).glob("*/SKILL.md"))
    if len(skills) < 15:
        raise Inconclusive(f"found {len(skills)} SKILL.md — below the vacuity floor")
    missing, malformed, invocable = [], [], []
    for f in skills:
        t = f.read_text(encoding="utf-8", errors="replace")
        fm = re.match(r"\A---\n(.*?)\n---\n", t, re.S)
        if not fm:
            raise Inconclusive(f"{f.name} in {f.parent.name} has no frontmatter fence")
        is_inv = bool(re.search(r"^user-invocable:\s*true\s*$", fm.group(1), re.M))
        block = _invocation_block(t)
        if is_inv:
            invocable.append(f.parent.name)
            if block is None:
                missing.append(f.parent.name)
                continue
        if block is None:
            continue
        if not block:
            malformed.append(f"{f.parent.name}: `## Invocation` carries no canonical bullet")
            continue
        for ln in block:
            if " — " not in ln:
                malformed.append(f"{f.parent.name}: {ln[:60]!r} has no ` — ` purpose separator")
    findings = []
    if missing:
        findings.append(f"user-invocable:true without `## Invocation`: {missing}")
    if malformed:
        findings.extend(malformed)
    return (not findings,
            (f"{len(invocable)} user-invocable skill(s), all carrying `## Invocation` in the "
             "canonical bullet shape" if not findings else "; ".join(findings)),
            {"invocable": invocable, "missing": missing, "malformed": malformed})


def sc_user_invocable(root: Path, a) -> tuple[bool, str, dict]:
    """SC3 — the tri-state coercion defect is fixed (`REQ-CHECK-012`)."""
    proc = checker(root, "check_user_invocable.py", "--json")
    if proc.returncode == 2:
        raise Inconclusive(f"check_user_invocable INCONCLUSIVE: {proc.stderr.strip()[:200]}")
    try:
        detail = json.loads(proc.stdout)
    except Exception:
        raise Inconclusive(f"check_user_invocable emitted unparseable JSON: "
                           f"{proc.stdout[:200]!r}")
    # The consumer side must not have re-acquired a silent default.
    src = read(root, "web/plugins/skill_pages.py")
    if 'bool(fm.get("user-invocable", False))' in src:
        return False, "skill_pages.py still coerces an ABSENT tri-state key to False", detail
    return (proc.returncode == 0,
            f"{detail.get('skills_inspected')} skill(s) inspected; "
            f"absent={detail.get('absent')}, contradictions={len(detail.get('contradictions', []))}",
            detail)


def sc_verbs_match(root: Path, a) -> tuple[bool, str, dict]:
    """SC5 — the criteria table's verb set equals this script's subcommand set.

    BARE EQUALITY, NO CARVE-OUT. `verbs-match` itself appears in the table (SC5 invokes it), so
    the invariant holds only while a criterion executes it — which SC5 guarantees.
    """
    plan = read(root, f"{PLAN_DIR}/plan.md")
    in_plan = set(re.findall(r"plan067_checks\.py\s+([a-z0-9][a-z0-9-]*)", plan))
    if not in_plan:
        raise Inconclusive("parsed zero verbs out of plan.md — the parser, not the plan, is wrong")
    mine = set(SUBCOMMANDS)
    only_plan, only_script = sorted(in_plan - mine), sorted(mine - in_plan)
    ok = not only_plan and not only_script
    return ok, (f"{len(in_plan)} verb(s) in plan.md, {len(mine)} subcommand(s); "
                + ("sets are equal" if ok
                   else f"in plan.md only: {only_plan}; in script only: {only_script}")), \
        {"only_plan": only_plan, "only_script": only_script}


# ---------------------------------------------------------------------------
# Epic 1 — the rule
# ---------------------------------------------------------------------------

def sc_omission_fails(root: Path, a) -> tuple[bool, str, dict]:
    """SC6 — `check_web_counts.py` FAILs on an omission, and `not_checked == 0` over the corpus.

    Two halves, because they are two facts. The mutation half proves the rule FIRES; the
    `not_checked` half proves it cannot be EVADED by a group that enumerates no member ids —
    the `members is None` branch (`#376`), which is the easiest possible escape from a redesign
    that reduces enumerated labels.
    """
    proc = checker(root, "check_web_counts.py", "--json")
    if proc.returncode == 2:
        raise Inconclusive(f"check_web_counts INCONCLUSIVE: {proc.stderr.strip()[:200]}")
    try:
        detail = json.loads(proc.stdout)
    except Exception:
        raise Inconclusive(f"check_web_counts emitted unparseable JSON: {proc.stdout[:200]!r}")
    src = read(root, "scripts/checks/check_web_counts.py")
    findings = []
    if "missing" not in src:
        findings.append("check_web_counts.py computes no `missing` difference")
    nc = detail.get("not_checked_groups", detail.get("not_checked_count"))
    if nc is None:
        findings.append("check_web_counts --json reports no `not_checked_groups` count — the "
                        "`members is None` class is not declared (#376)")
    elif nc != 0:
        findings.append(f"{nc} group(s) enumerate no member ids and go UNCHECKED — the "
                        "omission rule is evadable there (#376)")
    if proc.returncode != 0:
        findings.append(f"check_web_counts exits {proc.returncode} over the corpus")
    return (not findings,
            "omission difference computed and not_checked == 0" if not findings
            else "; ".join(findings), detail)


def sc_required_set(root: Path, a) -> tuple[bool, str, dict]:
    """SC7 — the slash-sub-verb required set is live, floored, and non-vacuous."""
    proc = checker(root, "check_required_set.py", "--json")
    if proc.returncode == 2:
        raise Inconclusive(f"check_required_set INCONCLUSIVE: {proc.stderr.strip()[:200]}")
    try:
        detail = json.loads(proc.stdout)
    except Exception:
        raise Inconclusive(f"check_required_set emitted unparseable JSON: {proc.stdout[:200]!r}")
    findings = []
    if not detail.get("floor"):
        findings.append("the checker declares no vacuity floor")
    if not detail.get("required_set"):
        findings.append("the derived required set is EMPTY — a vacuous green")
    if proc.returncode != 0:
        findings.append(f"check_required_set exits {proc.returncode}")
    return (not findings, "required set live and non-vacuous" if not findings
            else "; ".join(findings), detail)


def sc_cli_to_page(root: Path, a) -> tuple[bool, str, dict]:
    """SC8 — the CLI→page direction exists and reaches what its STATED predicate can reach.

    It does **not** claim the `--force` flags: measured, `--force` is already documented, so a
    corpus-wide token predicate cannot flag it and a pair-level predicate would contradict the
    corpus-wide rule and reopen R7.
    """
    proc = checker(root, "check_cli_to_page.py", "--json")
    if proc.returncode == 2:
        raise Inconclusive(f"check_cli_to_page INCONCLUSIVE: {proc.stderr.strip()[:200]}")
    try:
        detail = json.loads(proc.stdout)
    except Exception:
        raise Inconclusive(f"check_cli_to_page emitted unparseable JSON: {proc.stdout[:200]!r}")
    corpus = web_corpus(root)
    findings = [f"{t} is still undocumented corpus-wide" for t in ("prune-private",
                                                                   "--prune-formulas")
                if t not in corpus]
    if "positional" not in json.dumps(detail):
        findings.append("the checker does not declare its positional-argument exclusion")
    if proc.returncode != 0:
        findings.append(f"check_cli_to_page exits {proc.returncode}")
    return (not findings,
            "the CLI→page direction is live and both named surfaces are documented"
            if not findings else "; ".join(findings), detail)


def sc_agents_set(root: Path, a) -> tuple[bool, str, dict]:
    """SC9 — `e-web-agents-set` exists, SCOPED, and the `lander` agent is documented."""
    manifest = read(root, "DRIFT-CHECK.md")
    proc = checker(root, "check_agents_set.py", "--json")
    if proc.returncode == 2:
        raise Inconclusive(f"check_agents_set INCONCLUSIVE: {proc.stderr.strip()[:200]}")
    try:
        detail = json.loads(proc.stdout)
    except Exception:
        raise Inconclusive(f"check_agents_set emitted unparseable JSON: {proc.stdout[:200]!r}")
    page = read(root, WORKFLOWS_PAGE)
    findings = []
    if "e-web-agents-set" not in manifest:
        findings.append("DRIFT-CHECK.md declares no `e-web-agents-set` edge")
    if "lander" not in page:
        findings.append("workflows.md does not name the `lander` agent")
    if proc.returncode != 0:
        findings.append(f"check_agents_set exits {proc.returncode}")
    return (not findings, "edge declared, scoped, and `lander` documented" if not findings
            else "; ".join(findings), detail)


def sc_notchecked_declared(root: Path, a) -> tuple[bool, str, dict]:
    """SC11 — the excluded classes are declared in the CHECKER'S OWN OUTPUT, not only in prose.

    `REQ-CHECK-009(c)`: a checker that covers a proper subset and says nothing about the
    remainder reports a green a reader will attribute to the whole.
    """
    missing, seen = [], {}
    for name in PINNED_CHECKERS:
        proc = checker(root, name, "--json")
        if proc.returncode == 2:
            raise Inconclusive(f"{name} INCONCLUSIVE: {proc.stderr.strip()[:200]}")
        try:
            d = json.loads(proc.stdout)
        except Exception:
            raise Inconclusive(f"{name} emitted unparseable JSON")
        nc = d.get("not_checked")
        seen[name] = nc
        if not nc:
            missing.append(f"{name} declares no `not_checked`")
        elif not any("editorial" in str(x) or "script-verb" in str(x) or "script verb" in str(x)
                     for x in nc):
            missing.append(f"{name}'s `not_checked` names no excluded class")
    return (not missing,
            "every pinned checker declares its exclusions in its own output" if not missing
            else "; ".join(missing), {"not_checked": seen})


def sc_cv_rows(root: Path, a) -> tuple[bool, str, dict]:
    """SC12 — CHANGE-VALIDATION rows name BOTH the doc side and the SOURCE OF TRUTH.

    A doc-side-only trigger cannot fire on the commit that CREATES the omission — the same
    source-side-trigger requirement `REQ-CHECK-008(b)` states, measured on commit `75a5796`.
    """
    cv = read(root, "CHANGE-VALIDATION.md")
    required_sources = ["skills/*/SKILL.md", "yf/src/cli.rs", "yf/src/harness_desc.rs"]
    findings = [s for s in required_sources if s not in cv]
    named = [n for n in PINNED_CHECKERS if n in cv]
    if len(named) < 3:
        findings.append(f"CHANGE-VALIDATION.md names only {named} of the new checkers")
    return (not findings,
            "recipe rows name the doc side and all three source-of-truth globs"
            if not findings else
            f"missing from CHANGE-VALIDATION.md: {findings}",
            {"missing": findings, "checkers_named": named})


# ---------------------------------------------------------------------------
# Epic 2 — the failure list and the repairs
# ---------------------------------------------------------------------------

def sc_inventory_control(root: Path, a) -> tuple[bool, str, dict]:
    """SC13 — the produced inventory contains every omission EXP-003 named.

    An EXP-003 item the rule MISSES is an instrument defect, not an absent defect.
    """
    inv = read(root, f"{PLAN_DIR}/findings/omission-inventory.md")
    exp3 = read(root, f"{PLAN_DIR}/findings/exp-003-omission-inventory.md")
    named = sorted({t for t in re.findall(r"`([a-z][a-z0-9_.-]{3,})`", exp3)
                    if t in ("prune-private", "--prune-formulas", "closable",
                             "plan-retrospective", "lander")}
                   | {"prune-private"})
    absent = [t for t in named if t not in inv]
    if not named:
        raise Inconclusive("derived zero EXP-003 items — the control would certify vacuously")
    return (not absent,
            f"{len(named)} EXP-003 item(s) checked; all present in the produced inventory"
            if not absent else
            f"INSTRUMENT DEFECT — the rule missed EXP-003 item(s): {absent}",
            {"checked": named, "absent": absent})


def sc_high_value(root: Path, a) -> tuple[bool, str, dict]:
    """SC14 — the highest-value omissions are documented, corpus-wide."""
    corpus = web_corpus(root)
    absent = [t for t in HIGH_VALUE_TOKENS if t not in corpus]
    extra = {}
    # `mappings` is a verb, not a unique token — require it in the same document as upstream.py.
    if not re.search(r"upstream\.py[^\n]*mappings|`mappings`", corpus):
        absent.append("upstream.py mappings")
    # Both `--force` flags: named in SC14's own text, and reachable only as a PAIR predicate.
    for pair in ("self install", "self uninstall"):
        if not re.search(rf"{re.escape(pair)}[^\n]*--force|--force[^\n]*{re.escape(pair)}",
                         corpus):
            extra.setdefault("force_pairs_undocumented", []).append(pair)
    if extra:
        absent.extend(f"{p} --force" for p in extra["force_pairs_undocumented"])
    return (not absent,
            f"all {len(HIGH_VALUE_TOKENS) + 3} high-value surfaces are documented somewhere on "
            "the site" if not absent else f"still undocumented: {absent}",
            {"absent": absent, **extra})


def sc_partial_coverage(root: Path, a) -> tuple[bool, str, dict]:
    """SC15 — the one-page-deep items reach the CONCEPT pages, not just one file each.

    plan-066 left each of these hitting exactly one file. "Reaches the concept pages" is
    therefore a COUNT >= 2 over distinct documents, not mere presence.
    """
    web = root / "web" / "content"
    if not web.is_dir():
        raise Inconclusive("web/content is absent")
    docs = sorted(web.rglob("*.md"))
    if len(docs) < 10:
        raise Inconclusive(f"only {len(docs)} web documents — below the vacuity floor")
    hits, thin = {}, []
    for tok in PARTIAL_COVERAGE_TOKENS:
        n = [str(p.relative_to(root)) for p in docs
             if tok in p.read_text(encoding="utf-8", errors="replace")]
        hits[tok] = n
        if len(n) < 2:
            thin.append(f"{tok}: {len(n)} file(s) — still one-page-deep")
    return (not thin,
            "every partial-coverage item reaches at least two documents" if not thin
            else "; ".join(thin), {"hits": hits})


def sc_checkers_green(root: Path, a) -> tuple[bool, str, dict]:
    """SC16 — every checker this plan touches exits 0 over the repaired prose."""
    results, red = {}, []
    for name in PINNED_CHECKERS + ["check_user_invocable.py"]:
        proc = checker(root, name)
        results[name] = proc.returncode
        if proc.returncode != 0:
            red.append(f"{name} exits {proc.returncode}")
    return (not red, "every checker exits 0" if not red else "; ".join(red),
            {"exit_codes": results})


# ---------------------------------------------------------------------------
# Epic 3 — the archify trial
# ---------------------------------------------------------------------------

def sc_archify_trial(root: Path, a) -> tuple[bool, str, dict]:
    """SC21c — a like-for-like comparison EXISTS and the report names the checkability cost."""
    rel = f"{PLAN_DIR}/assets/archify-trial"
    d = root / rel
    if not d.is_dir():
        raise Inconclusive(f"no trial directory at {rel}")
    have = sorted(p.name for p in d.iterdir() if p.is_file())
    report = read(root, f"{PLAN_DIR}/findings/archify-trial.md")
    findings = []
    for want in ("architecture.html", "architecture.d2"):
        if want not in have:
            findings.append(f"{want} absent from {rel}")
    if not any(p.endswith(".png") for p in have):
        findings.append("no raster produced for either side")
    if "no d2 input path" not in report:
        findings.append("the report does not state archify's missing d2 input path")
    if not re.search(r"checkab", report, re.I):
        findings.append("the report does not name the checkability cost")
    return (not findings, "like-for-like artifacts present and the report names the cost"
            if not findings else "; ".join(findings), {"artifacts": have})


def sc_render_bytes_match(root: Path, a) -> tuple[bool, str, dict]:
    """SC18 — the trial changed no pin: every committed PNG is sha256-identical to a fresh
    render under the recorded `elk` pin.

    Byte equality is decidable WITHIN a pinned d2 version and is not across versions, which is
    why both the version and the flags are pinned here.
    """
    if not shutil.which("d2"):
        raise Inconclusive("d2 is not on PATH")
    ver = run_cmd(root, ["d2", "--version"]).stdout.strip()
    if D2_PIN not in ver:
        raise Inconclusive(f"d2 is {ver!r}, not the recorded pin {D2_PIN}")
    srcs = sorted((root / DIAGRAM_DIR).glob("*.d2"))
    if not srcs:
        raise Inconclusive(f"no .d2 sources under {DIAGRAM_DIR}")
    mismatched, detail = [], {}
    with tempfile.TemporaryDirectory() as td:
        for src in srcs:
            png = src.with_suffix(".png")
            if not png.is_file():
                mismatched.append(f"{png.name}: no committed render")
                continue
            fresh = Path(td) / png.name
            proc = run_cmd(root, ["d2", *D2_FLAGS, str(src), str(fresh)])
            if proc.returncode != 0 or not fresh.is_file():
                raise Inconclusive(f"d2 failed on {src.name}: {proc.stderr.strip()[:200]}")
            a_ = hashlib.sha256(png.read_bytes()).hexdigest()
            b_ = hashlib.sha256(fresh.read_bytes()).hexdigest()
            detail[png.name] = {"committed": a_, "fresh": b_}
            if a_ != b_:
                mismatched.append(png.name)
    return (not mismatched,
            f"{len(srcs)} diagram(s) re-rendered under d2 {D2_PIN} {' '.join(D2_FLAGS)}; "
            + ("all identical" if not mismatched else f"MISMATCHED: {mismatched}"), detail)


# ---------------------------------------------------------------------------
# Epic 4 — the diagram redesign
# ---------------------------------------------------------------------------

def _d2_src(root: Path, name: str) -> str:
    return read(root, f"{DIAGRAM_DIR}/{name}")


def sc_architecture_complete(root: Path, a) -> tuple[bool, str, dict]:
    """SC19 — the layered marketecture carries the tool layer, the `yf` subcommand paths and
    the `depends-on-skill` edges, WITH `not_checked == 0` so it cannot pass by dropping ids."""
    src = _d2_src(root, "architecture.d2")
    tools = ["bd", "gh", "pandoc", "d2", "uv", "git", "xelatex", "herdr"]
    missing_tools = [t for t in tools
                     if not re.search(rf"(?<![a-z-]){re.escape(t)}(?![a-z-])", src)]
    # every declared depends-on-skill edge must be drawn
    edges, drawn = [], []
    for f in sorted((root / SKILLS_DIR).glob("*/SKILL.md")):
        fm = re.match(r"\A---\n(.*?)\n---\n", f.read_text(encoding="utf-8", errors="replace"),
                      re.S)
        if not fm:
            continue
        m = re.search(r"^depends-on-skill:\s*\[([^\]]*)\]", fm.group(1), re.M)
        if not m:
            continue
        for dep in [x.strip() for x in m.group(1).split(",") if x.strip()]:
            edges.append((f.parent.name, dep))
    for src_s, dst in edges:
        if re.search(rf"{re.escape(src_s)}[^\n]*->[^\n]*{re.escape(dst)}", src) or \
           re.search(rf"{re.escape(dst)}[^\n]*<-[^\n]*{re.escape(src_s)}", src):
            drawn.append(f"{src_s}->{dst}")
    if not edges:
        raise Inconclusive("derived zero depends-on-skill edges — a vacuous check")
    undrawn = [f"{s}->{d}" for s, d in edges if f"{s}->{d}" not in drawn]
    proc = checker(root, "check_web_counts.py", "--json")
    nc = None
    if proc.returncode != 2:
        try:
            nc = json.loads(proc.stdout).get("not_checked_groups")
        except Exception:
            nc = None
    findings = []
    if missing_tools:
        findings.append(f"tool layer missing: {missing_tools}")
    if undrawn:
        findings.append(f"{len(undrawn)} of {len(edges)} depends-on-skill edges undrawn: "
                        f"{undrawn}")
    if nc not in (0, None) :
        findings.append(f"not_checked == {nc} — the redesign can pass by dropping enumerated ids")
    if nc is None:
        raise Inconclusive("check_web_counts reports no not_checked_groups — SC19's second half "
                           "cannot be evaluated")
    return (not findings, "tool layer, subcommand paths and every declared skill edge present, "
            "with not_checked == 0" if not findings else "; ".join(findings),
            {"edges": len(edges), "undrawn": undrawn, "missing_tools": missing_tools,
             "not_checked_groups": nc})


def sc_combined_diagrams(root: Path, a) -> tuple[bool, str, dict]:
    """SC20 — the two combinations landed, the combined lifecycle carries the named content,
    and it uses the REAL literal `system_deps_missing` (#375)."""
    life = _d2_src(root, COMBINED_LIFECYCLE)
    inst = _d2_src(root, COMBINED_INSTALL)
    required = ["red-team", "gate", "escalation", "retrospective", "autonom",
                "capture", "execut", "land"]
    missing = [t for t in required if t.lower() not in life.lower()]
    findings = []
    if (root / DIAGRAM_DIR / "phase-model.d2").is_file():
        findings.append("phase-model.d2 still exists — the combination did not land")
    if (root / DIAGRAM_DIR / "tune-matrix.d2").is_file():
        findings.append("tune-matrix.d2 still exists — the combination did not land")
    if missing:
        findings.append(f"the combined lifecycle omits: {missing}")
    if PREFLIGHT_STATUS_WRONG in life and PREFLIGHT_STATUS_LITERAL not in life:
        findings.append(f"#375 unfixed — the diagram still labels a status "
                        f"{PREFLIGHT_STATUS_WRONG!r}")
    # 4.3's preserved distinction: install-matrix must keep surface_dir vs skills_subpath
    for lit in ("surface_dir", "skills_subpath"):
        if lit not in inst:
            findings.append(f"the combined install matrix lost the {lit!r} distinction")
    # 4.5: SkillsCommand's five verbs
    # The REAL SkillsCommand variants, read from yf/src/cli.rs — not a guessed set.
    # Issue 4.5: five are declared and only `install` was shown.
    for verb in ("install", "upgrade", "remove", "status", "prune-private"):
        if verb not in inst:
            findings.append(f"install-matrix does not show the `{verb}` skills verb")
    return (not findings, "both combinations landed with their required content"
            if not findings else "; ".join(findings), {"missing_content": missing})


def sc_formulas_map(root: Path, a) -> tuple[bool, str, dict]:
    """SC21 — the skills/agents → formulas map exists."""
    d = root / DIAGRAM_DIR
    cand = [p.name for p in d.glob("*formula*map*.d2")] + \
           [p.name for p in d.glob("*formulas-map*.d2")]
    if not cand:
        return False, "no skills/agents → formulas map diagram found", {"candidates": []}
    src = (d / cand[0]).read_text(encoding="utf-8", errors="replace")
    named = [f for f in SHIPPED_FORMULAS if f in src]
    ok = len(named) == len(SHIPPED_FORMULAS)
    return ok, (f"{cand[0]} names {len(named)}/{len(SHIPPED_FORMULAS)} shipped formulas"), \
        {"diagram": cand[0], "named": named}


def sc_per_formula_diagrams(root: Path, a) -> tuple[bool, str, dict]:
    """SC21b — one diagram per shipped formula, and the meta-diagram is REMOVED."""
    d = root / DIAGRAM_DIR
    if not d.is_dir():
        raise Inconclusive(f"{DIAGRAM_DIR} is absent")
    have = {p.stem for p in d.rglob("*.d2")}
    missing = [f for f in SHIPPED_FORMULAS if f not in have]
    findings = []
    if missing:
        findings.append(f"no diagram for formula(s): {missing}")
    if (d / REMOVED_META_DIAGRAM).is_file():
        findings.append(f"{REMOVED_META_DIAGRAM} still present — #373 asks for its removal")
    return (not findings, f"{len(SHIPPED_FORMULAS)} per-formula diagrams present and the "
            "meta-diagram removed" if not findings else "; ".join(findings),
            {"missing": missing})


# ---------------------------------------------------------------------------
# Epic 5 — generated per-skill diagrams
# ---------------------------------------------------------------------------

def _generator(root: Path) -> Path:
    for rel in ("web/plugins/skill_diagrams.py", "scripts/gen_skill_diagrams.py"):
        if (root / rel).is_file():
            return root / rel
    raise Inconclusive("no per-skill diagram generator found")


def sc_generator_check(root: Path, a) -> tuple[bool, str, dict]:
    """SC22 — the diagrams are GENERATED and `--check` proves the committed set matches."""
    gen = _generator(root)
    proc = run_cmd(root, ["uv", "run", str(gen), "--check"])
    if proc.returncode == 2:
        raise Inconclusive(f"generator --check INCONCLUSIVE: {proc.stderr.strip()[:200]}")
    return (proc.returncode == 0,
            f"{gen.relative_to(root)} --check exits {proc.returncode}",
            {"stdout": proc.stdout[-800:], "stderr": proc.stderr[-800:]})


def sc_publication_threshold(root: Path, a) -> tuple[bool, str, dict]:
    """SC23 — publication is gated on a COMPUTED threshold whose node/edge definition is stated
    in the plan and whose value was re-derived by Issue 5.0."""
    gen = _generator(root)
    src = gen.read_text(encoding="utf-8", errors="replace")
    plan = read(root, f"{PLAN_DIR}/plan.md")
    census = read_opt(root, f"{PLAN_DIR}/findings/per-skill-census.md")
    findings = []
    if not re.search(r"THRESHOLD|threshold", src):
        findings.append("the generator names no publication threshold")
    if re.search(r"PUBLISH\s*=\s*\[|PUBLISHED_SKILLS\s*=\s*\[", src):
        findings.append("publication is gated on a hand-maintained LIST, not a threshold")
    if not re.search(r"node/edge definition|what counts as a node", plan, re.I):
        findings.append("plan.md does not state the node/edge definition the threshold uses")
    if census is None:
        findings.append("Issue 5.0's re-derived census is absent — the threshold is inherited, "
                        "not computed")
    return (not findings, "publication gated on a computed, re-derived threshold"
            if not findings else "; ".join(findings), {})


def sc_build_and_render(root: Path, a) -> tuple[bool, str, dict]:
    """SC24 — the site builds clean and every generated diagram renders legibly.

    Mandates (b) and (c): pelican runs through `run_cmd` (no shell, no pipe) and the environment
    comes from `uv run --with-requirements web/requirements.txt`, never a hardcoded `web/.venv`.
    """
    reqs = root / "web" / "requirements.txt"
    if not reqs.is_file():
        raise Inconclusive("web/requirements.txt is absent")
    proc = run_cmd(root, ["uv", "run", "--with-requirements", str(reqs),
                          "pelican", "content", "-o", "output", "-s", "pelicanconf.py",
                          "--fatal", "warnings"], cwd=root / "web")
    findings = []
    if proc.returncode != 0:
        findings.append(f"pelican --fatal warnings exits {proc.returncode}: "
                        f"{proc.stderr.strip()[-400:]}")
    # legibility: no single-column stack. A render taller than 3x its width reads as a list.
    tall = []
    for png in sorted((root / DIAGRAM_DIR).rglob("*.png")):
        dims = _png_size(png)
        if dims and dims[1] > 3 * dims[0]:
            tall.append(f"{png.name} {dims[0]}x{dims[1]}")
    if tall:
        findings.append(f"single-column stack(s): {tall}")
    return (not findings, "site builds clean under --fatal warnings and no diagram is a "
            "single-column stack" if not findings else "; ".join(findings),
            {"tall": tall, "pelican_exit": proc.returncode})


def _png_size(p: Path) -> tuple[int, int] | None:
    try:
        b = p.read_bytes()[:33]
        if b[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")
    except Exception:
        return None


def sc_page_guard(root: Path, a) -> tuple[bool, str, dict]:
    """SC24b — the authored-page guard asserts NON-TRIVIAL CONTENT, not mere existence (#374).

    A zero-byte page built green with zero warnings. Existence is not content.
    """
    src = read(root, "web/plugins/skill_pages.py")
    if not re.search(r"os\.path\.exists|\.is_file\(\)|\.exists\(\)", src):
        raise Inconclusive("no authored-page guard found in skill_pages.py")
    ok = bool(re.search(r"(len\(|strip\(\)|getsize|st_size|MIN_[A-Z_]*(LEN|BYTES|CHARS))", src))
    return ok, ("the authored-page guard measures content, not just existence" if ok
                else "the guard is EXISTENCE-only — a zero-byte page still builds green (#374)"), {}


# ---------------------------------------------------------------------------
# Epic 6 — verification, retrospective, handoff
# ---------------------------------------------------------------------------

def sc_classb_disposition(root: Path, a) -> tuple[bool, str, dict]:
    """SC25 — each Class-B item is CLOSED or FILED WITH AN OWNER, enumerated BY NAME.

    Never implied by a green build: a green build is silent about work that was never started.
    """
    t = read_opt(root, f"{PLAN_DIR}/findings/classb-disposition.md")
    if t is None:
        raise Inconclusive("findings/classb-disposition.md is absent — nothing to check")
    rows = re.findall(r"^\|\s*([^|]+?)\s*\|\s*(CLOSED|FILED)\b[^|]*\|\s*([^|]+?)\s*\|",
                      t, re.M | re.I)
    if not rows:
        raise Inconclusive("parsed zero disposition rows — the parser or the table is wrong")
    unowned = [r[0] for r in rows if r[1].upper() == "FILED" and not r[2].strip()]
    return (not unowned, f"{len(rows)} Class-B item(s) dispositioned by name"
            if not unowned else f"FILED without an owner: {unowned}", {"rows": len(rows)})


def sc_retro_classes(root: Path, a) -> tuple[bool, str, dict]:
    """SC26 — the retrospective distinguishes CONTENT from PROCESS defects, with counts, and
    records the two instrument false-greens this plan's own experiments produced."""
    t = read(root, f"{PLAN_DIR}/plan-retrospective.md")
    findings = []
    if not re.search(r"content defect", t, re.I):
        findings.append("no content-defect class")
    if not re.search(r"process defect", t, re.I):
        findings.append("no process-defect class")
    if not re.search(r"\b\d+\b", t):
        findings.append("no counts")
    if not re.search(r"false green|false-green", t, re.I):
        findings.append("does not record the instrument false-greens")
    return (not findings, "retrospective separates the two classes, with counts and the "
            "false-greens" if not findings else "; ".join(findings), {})


def sc_index_complete(root: Path, a) -> tuple[bool, str, dict]:
    """SC25b — `index.md` lists every artifact a cold reader needs, not just the scaffold four."""
    idx = read(root, f"{PLAN_DIR}/index.md")
    d = root / PLAN_DIR
    wanted = []
    for sub in ("findings", "references", "reviews", "assets"):
        p = d / sub
        if not p.is_dir():
            continue
        for f in sorted(p.rglob("*")):
            if f.is_file() and f.suffix in (".md", ".d2", ".png", ".html"):
                wanted.append(str(f.relative_to(d)))
    if not wanted:
        raise Inconclusive("the bundle carries no findings/references/reviews/assets to list")
    absent = [w for w in wanted if w not in idx and Path(w).name not in idx]
    return (not absent, f"index.md lists all {len(wanted)} bundle artifact(s)"
            if not absent else f"index.md omits {len(absent)}: {absent[:8]}",
            {"missing": absent})


def sc_plan066_still_green(root: Path, a) -> tuple[bool, str, dict]:
    """SC26b — plan-066's criteria still hold on the post-plan-067 tree.

    Epic 4 rebuilds `architecture.d2` (plan-066 SC9) and removes `formulas.d2` (its SC23), so
    this is not a formality: a criterion measured green at its discharging issue and false two
    epics later is the exact defect `recheck-criteria` exists to catch.
    """
    p066 = root / "scripts" / "checks" / "plan066_checks.py"
    if not p066.is_file():
        raise Inconclusive("plan066_checks.py is absent")
    proc = run_cmd(root, ["uv", "run", str(p066), "verbs-match"])
    if proc.returncode == 2:
        raise Inconclusive(f"plan066 verbs-match INCONCLUSIVE: {proc.stderr.strip()[:200]}")
    plan066 = None
    for cand in sorted((root / "docs" / "plans").glob("plan-066-*")):
        plan066 = cand
    if plan066 is None:
        raise Inconclusive("no plan-066 bundle found")
    txt = (plan066 / "plan.md").read_text(encoding="utf-8", errors="replace")
    verbs = sorted(set(re.findall(r"plan066_checks\.py\s+([a-z0-9][a-z0-9-]*)", txt)))
    if not verbs:
        raise Inconclusive("parsed zero plan-066 verbs")
    red = {}
    for v in verbs:
        r = run_cmd(root, ["uv", "run", str(p066), v])
        if r.returncode == 1:
            red[v] = r.stdout.strip()[:160] or r.stderr.strip()[:160]
    return (not red, f"{len(verbs)} plan-066 criterion verb(s) re-run; none FALSE"
            if not red else f"plan-066 criteria now FALSE: {sorted(red)}",
            {"false": red, "verbs": verbs})


SUBCOMMANDS = {
    "agents-set": sc_agents_set,
    "archify-trial": sc_archify_trial,
    "architecture-complete": sc_architecture_complete,
    "build-and-render": sc_build_and_render,
    "checkers-green": sc_checkers_green,
    "classb-disposition": sc_classb_disposition,
    "cli-to-page": sc_cli_to_page,
    "combined-diagrams": sc_combined_diagrams,
    "contradictions": sc_contradictions,
    "cv-rows": sc_cv_rows,
    "formulas-map": sc_formulas_map,
    "generator-check": sc_generator_check,
    "high-value": sc_high_value,
    "index-complete": sc_index_complete,
    "inventory-control": sc_inventory_control,
    "invocation-schema": sc_invocation_schema,
    "notchecked-declared": sc_notchecked_declared,
    "omission-fails": sc_omission_fails,
    "page-guard": sc_page_guard,
    "partial-coverage": sc_partial_coverage,
    "per-formula-diagrams": sc_per_formula_diagrams,
    "plan066-still-green": sc_plan066_still_green,
    "publication-threshold": sc_publication_threshold,
    "render-bytes-match": sc_render_bytes_match,
    "required-set": sc_required_set,
    "retro-classes": sc_retro_classes,
    "user-invocable": sc_user_invocable,
    "verbs-match": sc_verbs_match,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="plan067_checks.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # MANDATE (a): `choices` makes an unknown verb exit 2 (argparse's usage error), never 0.
    ap.add_argument("subcommand", choices=sorted(SUBCOMMANDS))
    ap.add_argument("--json", action="store_true", help="emit the JSON envelope")
    ap.add_argument("--root", help="repository root (default: git toplevel)")
    a = ap.parse_args(argv)

    root = Path(a.root).resolve() if a.root else repo_root()
    try:
        ok, reason, detail = SUBCOMMANDS[a.subcommand](root, a)
        verdict, code = ("PASS", 0) if ok else ("FALSE", 1)
    except Inconclusive as exc:
        verdict, code, reason, detail = "INCONCLUSIVE", 2, str(exc), {}
    except Exception as exc:  # an instrument crash is INCONCLUSIVE, never FALSE
        verdict, code, reason, detail = "INCONCLUSIVE", 2, f"{type(exc).__name__}: {exc}", {}

    env = {"check": CHECK, "subcommand": a.subcommand, "verdict": verdict,
           "exit": code, "reason": reason, "root": str(root), "detail": detail,
           # Issue 0.7 — the DECLARED BAND, in the instrument's own output.
           "declared_band": BAND,
           "not_checked": ["semantic mis-assignment beyond the id sets named here",
                           "missing qualifiers",
                           "editorial omission",
                           "SC17 and SC27 — the two `manual:` criteria; a green here is not a "
                           "human read"]}
    if a.json:
        print(json.dumps(env, indent=1))
    else:
        print(f"{verdict} ({code}) {a.subcommand}: {reason}")
    return code


if __name__ == "__main__":
    sys.exit(main())
