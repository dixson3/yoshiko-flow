#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""plan-066's verification instrument — ONE script, one subcommand per Success Criterion.

Every subcommand answers exactly one criterion with an **exit code**:

    0  PASS          — the condition holds
    1  FALSE         — the condition was checked and does NOT hold
    2  INCONCLUSIVE  — the check could not run (input absent, tool missing, bad JSON)

**2 IS NOT 1** (the `plan065_checks.py` precedent). An absent input says the instrument could
not look, not that the condition is false. Reading the two as one is `#181`/`#207`'s
two-facts-one-signal conflation, which this repository has now hit four times.

FOUR IMPLEMENTATION MANDATES, each from a MEASURED failure (plan.md Issue 0.4):

(a) `choices=sorted(SUBCOMMANDS)` — an unknown verb exits **2**, never 0. A permissive
    dispatcher returns 0 for a typo, which is `#364`'s silent false PASS.

(b) **NEVER PIPE PELICAN.** `pelican … | tail` reports the exit code of `tail`, so a broken
    build reads green — measured: bare `pelican` exits **1**, the same command through `tail`
    exits **0**. The reflexive fix `${PIPESTATUS[@]}` is a **bash-ism that expands to NOTHING
    under this repo's zsh**, turning a "hardened" check into a silently empty one. This file
    runs pelican through `subprocess.run` with **no shell and no pipe**, so the exit code is
    the process's own.

(c) **The build verb must not hardcode `web/.venv`.** It is untracked and absent from an
    execute worktree, where hardcoding it exits **127**. The route is
    `uv run --with-requirements web/requirements.txt pelican`.

(d) **The site-specific verbs assert their ENUMERATED SITES AND LITERALS BY NAME** —
    `harness-sites`, `backend-sites`, `group-membership`, `formulas-diagram`. A verb that
    merely re-invokes the Epic-2 checker asserts nothing beyond SC5, and the site language in
    SC7/SC8/SC9/SC23 would become prose no criterion checks (pass-4 C6). Each names its files
    and its literals below, in module constants, so the enumeration is auditable.

WHAT THIS SCRIPT DELIBERATELY DOES NOT COVER (REQ-CHECK-009, added by this plan's own Epic 0):
semantic mis-assignment (a group whose count is right and whose membership is wrong beyond the
id sets checked here), missing qualifiers outside the two `prose-rows` checks, and editorial
omission. Those are discharged by a human read — `diagram-reads` records that the read happened,
it does not perform it. Declaring this is the requirement, not a courtesy: a green with an
undeclared boundary is indistinguishable from a green with none.
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

CHECK = "plan066-checks"
PLAN_ID = "plan-066-james-dixson-e7fadb"
PLAN_DIR = f"docs/plans/{PLAN_ID}"

# ---------------------------------------------------------------------------
# ENUMERATED SITES AND LITERALS (mandate (d)). Named here, once, so every
# site-specific verb asserts a set a reviewer can audit against plan.md.
# ---------------------------------------------------------------------------

# SC7 — the path/identifier corpus. `README.md` and `AGENTS.md` are IN IT (pass-1 C4): both
# carry the identical drifted harness matrix and a `web/content/**`-scoped checker cannot
# reach either.
HARNESS_SITES = [
    "README.md",
    "AGENTS.md",
    "web/content/pages/install.md",
    "web/content/pages/architecture.md",
    "web/content/images/install-matrix.d2",
]

# Retired SKILLS subpaths. THE TUPLE, NOT A FLAT STRING (pass-2 C12): `.config/opencode` and
# `.pi/agent` are the CORRECT `user_surface_dir` values and must NOT be flagged; only their
# `/skills` forms are retired, since every harness now installs skills to `.agents/skills`
# (claude-code excepted, which uses `.claude/skills`).
RETIRED_SKILLS_SUBPATHS = [
    ".config/opencode/skills",
    ".opencode/skills",
    ".pi/agent/skills",
    ".pi/skills",
]
# `harness_desc.rs:381` asserts no shipped row may carry a `name_transform`.
RETIRED_NAME_TRANSFORMS = ["lowercase-hyphen", "max64"]

# SC8 — the SIX upstream-backend sites. `README.md` is the sixth, exposed by the corpus
# widening (pass-2 C11).
BACKEND_SITES = [
    "web/content/pages/architecture.md",
    "web/content/pages/glossary.md",
    "web/content/pages/beads-concepts.md",
    "web/content/images/architecture.d2",
    "web/content/skills/yf-plan.md",
    "README.md",
]
# Multi-backend claims. GitHub is the only supported backend.
BACKEND_CLAIM_RES = [
    re.compile(r"GitHub\s*[,/]\s*GitLab", re.I),
    re.compile(r"GitLab\s*[,/]?\s*(or\s+)?Jira", re.I),
    re.compile(r"github\s*\|\s*gitlab", re.I),
    re.compile(r"\bbd\s+(github|gitlab|jira)\s+push", re.I),
]
# `README.md:25`'s "`gh` / `glab` — GitHub / GitLab CLI" is a CORRECT mention of a CLI tool,
# not a backend claim, and must not false-positive.
BACKEND_ALLOW_RES = [
    re.compile(r"`gh`\s*/\s*`glab`"),
    re.compile(r"GitHub\s*/\s*GitLab\s+CLI", re.I),
]

# SC9 / SC23 — diagram sites and the five shipped formula names.
ARCH_D2 = "web/content/images/architecture.d2"
FORMULAS_D2 = "web/content/images/formulas.d2"
SHIPPED_FORMULAS = ["plan-execute", "plan-investigate", "plan-review",
                    "verify-artifact", "yf-research"]
SKILL_GROUPS = ["beads", "markdown", "utility", "workflows"]

# SC10 — the D7 pin and its flags. sha256 equality is FLAG-SENSITIVE, hence both are pinned.
D2_PIN = "v0.8.2"
D2_FLAGS = ["--theme", "0", "--layout", "elk"]
DIAGRAM_DIR = "web/content/images"

# SC1/SC2/SC15 — the build.
P0_PAGE = "web/content/skills/yf-okf-hygiene.md"
P0_HTML = "output/skills/yf-okf-hygiene/index.html"
EPIC6_PAGES = [
    ("web/content/skills/yf-plan.md", "output/skills/yf-plan/index.html"),
    ("web/content/skills/yf-beads-upstream.md", "output/skills/yf-beads-upstream/index.html"),
]

# SC5/SC20/SC25 — the four Epic-2 checkers, BY NAME. `check_skill_page_contract.py` does not
# match a `check_web_*` glob (pass-3 C4), which is exactly why these are enumerated.
EPIC2_CHECKERS = [
    "scripts/checks/check_web_counts.py",
    "scripts/checks/check_web_harness_paths.py",
    "scripts/checks/check_skill_page_contract.py",
    "scripts/checks/check_web_backend_claim.py",
]

# SC16 — the six Class-B defects, by name.
CLASSB_ITEMS = ["item-1", "item-2", "item-3", "item-4", "item-5", "item-6"]


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


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

NEGATION_RE = re.compile(
    r"\b(not|never|no longer|isn't|is not|are not|rather than|instead of|"
    r"does not|do not|doesn't|don't|NOT|without)\b", re.I)


def affirms(line: str, token: str) -> bool:
    """True iff `line` states `token` AFFIRMATIVELY.

    SC13/SC14's negative leg must IGNORE a negated mention (pass-3 C6): the idiomatic
    correcting sentence — "`land` is not a `/yf-plan land` slash command" — WRITES the
    forbidden string, so a naive grep flips to FALSE and punishes the correct way to do the
    work. The carve-out is deliberately conservative: any negation anywhere on the line
    disqualifies it as an affirmation.
    """
    return token in line and not NEGATION_RE.search(line)


RETIREMENT_RE = re.compile(
    r"\b(retired|legacy|formerly|no longer|deprecated|pre-collapse|used to|historical)\b", re.I)


def paragraphs(text: str):
    """Yield `(lineno, paragraph_text, line)` — the paragraph being the contiguous non-blank run.

    The paragraph is the unit a prose claim is made in; a per-line view splits a sentence in
    half and reads each half as if it stood alone.
    """
    lines = text.splitlines()
    start = 0
    while start < len(lines):
        if not lines[start].strip():
            start += 1
            continue
        end = start
        while end < len(lines) and lines[end].strip():
            end += 1
        para = "\n".join(lines[start:end])
        for i in range(start, end):
            yield i + 1, para, lines[i]
        start = end


def skill_group_census(root: Path) -> dict[str, list[str]]:
    """Group -> sorted skill ids, from `skills/*/SKILL.md` frontmatter. The SOURCE OF TRUTH."""
    census: dict[str, list[str]] = {}
    for skill_md in sorted((root / "skills").glob("*/SKILL.md")):
        m = re.search(r"^skill-group:\s*(\S+)\s*$", skill_md.read_text(encoding="utf-8"), re.M)
        if m:
            census.setdefault(m.group(1), []).append(skill_md.parent.name)
    if not census:
        raise Inconclusive("parsed zero skill-group values — the parser, not the docs, is wrong")
    return {k: sorted(v) for k, v in census.items()}


def run_cmd(root: Path, argv: list[str], **kw) -> subprocess.CompletedProcess:
    """subprocess.run with NO SHELL and NO PIPE — mandate (b). The returned `returncode` is
    the process's own, so there is no `tail` to mask it and no `PIPESTATUS` to misspell."""
    env = dict(os.environ)
    env.pop("VIRTUAL_ENV", None)  # a worktree must resolve its own environment
    return subprocess.run(argv, cwd=kw.pop("cwd", root), capture_output=True, text=True,
                          env=env, **kw)


def pelican_build(root: Path, outdir: str | None = None) -> tuple[int, str, str]:
    """Build the site. NO PIPE, `--fatal warnings`, and NO `web/.venv` — mandates (b) and (c).

    `uv run --with-requirements web/requirements.txt` resolves the toolchain from the
    requirements file, so this works in an execute worktree where `web/.venv` does not exist
    (a check hardcoding it exits 127).
    """
    web = root / "web"
    if not (web / "requirements.txt").is_file():
        raise Inconclusive("web/requirements.txt absent — cannot resolve the pelican toolchain")
    out = outdir or str(web / "output")
    proc = run_cmd(root, ["uv", "run", "--with-requirements", "requirements.txt",
                          "pelican", "content", "-s", "pelicanconf.py", "-o", out,
                          "--fatal", "warnings"], cwd=web)
    return proc.returncode, proc.stdout, proc.stderr


def html_is_substantial(text: str) -> tuple[bool, dict]:
    """SC2's shape: >= 1 `<hr>` and >= 2 `<h2>`, with a non-trivial body after the `<hr>`.

    Measured (EXP-003 Result B): a ZERO-BYTE authored page satisfies the plugin's
    existence-only guard and builds green, rendering the generated "At a glance" block with no
    body and no `<hr>`. So "the build passes" is not a criterion — this is.
    """
    hrs = len(re.findall(r"<hr\b", text, re.I))
    h2s = len(re.findall(r"<h2\b", text, re.I))
    body = text.split("<hr", 1)[1] if hrs else ""
    body_text = re.sub(r"<[^>]+>", " ", body)
    body_words = len(body_text.split())
    ok = hrs >= 1 and h2s >= 2 and body_words >= 100
    return ok, {"hr": hrs, "h2": h2s, "body_words": body_words}


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def sc_build_clean(root: Path, a) -> tuple[bool, str, dict]:
    """SC1 — Pelican builds with zero errors AND zero warnings."""
    rc, out, err = pelican_build(root)
    tail = (err or out).strip().splitlines()[-3:]
    return rc == 0, (f"pelican exited {rc} under --fatal warnings"
                     + ("" if rc == 0 else f": {' / '.join(tail)}")), {"returncode": rc}


def sc_page_content(root: Path, a) -> tuple[bool, str, dict]:
    """SC2 — the authored page has REAL CONTENT, not merely a file."""
    if not (root / P0_PAGE).is_file():
        raise Inconclusive(f"input absent: {P0_PAGE}")
    rc, _, err = pelican_build(root)
    if rc != 0:
        raise Inconclusive(f"pelican exited {rc}; cannot inspect an unbuilt page")
    html = root / "web" / P0_HTML
    if not html.is_file():
        return False, f"{P0_HTML} was not emitted", {}
    ok, detail = html_is_substantial(html.read_text(encoding="utf-8"))
    return ok, (f"{P0_HTML}: {detail['hr']} <hr>, {detail['h2']} <h2>, "
                f"{detail['body_words']} body words (need >=1, >=2, >=100)"), detail


def sc_checkers_green(root: Path, a) -> tuple[bool, str, dict]:
    """SC5 — every checker the plan shipped exits 0 over the repaired tree."""
    results, missing = {}, []
    for c in EPIC2_CHECKERS:
        if not (root / c).is_file():
            missing.append(c)
            continue
        results[c] = run_cmd(root, ["uv", "run", c]).returncode
    if missing:
        raise Inconclusive(f"checker(s) not yet authored: {', '.join(missing)}")
    bad = {k: v for k, v in results.items() if v != 0}
    return not bad, (f"{len(results)} checker(s) run; "
                     + ("all exit 0" if not bad else f"non-zero: {bad}")), results


def sc_inventory_control(root: Path, a) -> tuple[bool, str, dict]:
    """SC6 — the checker-derived inventory contains every row #317 names.

    A row #317 lists that the checkers MISS means a checker is BLIND. This is a defect in the
    instrument, not an absent defect (D1's negative-control half).
    """
    inv = read(root, a.input or f"{PLAN_DIR}/findings/class-a-inventory.md")
    required = HARNESS_SITES + BACKEND_SITES + [ARCH_D2, FORMULAS_D2, P0_PAGE]
    absent = [s for s in dict.fromkeys(required) if s not in inv]
    return not absent, (f"{len(set(required))} #317-named site(s) checked; "
                        + ("all present in the inventory" if not absent
                           else f"ABSENT (checker is blind here): {absent}")), {"absent": absent}


def sc_harness_sites(root: Path, a) -> tuple[bool, str, dict]:
    """SC7 — every path/identifier site repaired, ACROSS THE NAMED FILES (mandate (d)).

    Asserts the enumerated sites by name — including `README.md` and `AGENTS.md`, which a
    `web/content/**`-scoped checker cannot reach — rather than delegating to the Epic-2
    checker, which would assert nothing beyond SC5.
    """
    findings: dict[str, list[str]] = {}
    allowed: dict[str, list[str]] = {}
    for site in HARNESS_SITES:
        text = read_opt(root, site)
        if text is None:
            raise Inconclusive(f"input absent: {site}")
        hits, ok = [], []
        for n, para, line in paragraphs(text):
            # SAME CARVE-OUT AS SC13/SC14, and for the same reason: a document may NAME a
            # retired root IN ORDER TO SAY IT IS RETIRED, and that is correct prose. Measured:
            # AGENTS.md documents the SKILL_DIR resolver, whose fallback loop genuinely still
            # searches the pre-collapse roots so an old layout still resolves — searching a root
            # is not installing to one. install.md says `pi` "formerly applied" a transform.
            # Flagging either would forbid documenting the truth.
            #
            # PARAGRAPH-SCOPED, because prose WRAPS: AGENTS.md puts "**retired**" at the end of
            # one line and the four root names at the start of the next, so a per-line carve-out
            # would suppress nothing and punish the correct text anyway.
            retired_ctx = RETIREMENT_RE.search(para)
            for tok in RETIRED_SKILLS_SUBPATHS:
                if tok in line:
                    (ok if retired_ctx else hits).append(
                        f"{n}: retired skills subpath `{tok}`"
                        + (" (named AS retired — allowed)" if retired_ctx else ""))
            for tok in RETIRED_NAME_TRANSFORMS:
                if tok in line:
                    (ok if retired_ctx else hits).append(
                        f"{n}: retired name_transform `{tok}`"
                        + (" (named AS retired — allowed)" if retired_ctx else ""))
        if hits:
            findings[site] = hits
        if ok:
            allowed[site] = ok
    n_ok = sum(len(v) for v in allowed.values())
    return not findings, (f"{len(HARNESS_SITES)} enumerated site(s) checked by name; "
                          + ("clean" if not findings
                             else f"{sum(len(v) for v in findings.values())} finding(s)")
                          + f"; {n_ok} retirement mention(s) allowed"), \
        {"findings": findings, "allowed": allowed}


def sc_backend_sites(root: Path, a) -> tuple[bool, str, dict]:
    """SC8 — all SIX upstream-backend sites repaired, BY NAME (mandate (d))."""
    findings: dict[str, list[str]] = {}
    for site in BACKEND_SITES:
        text = read_opt(root, site)
        if text is None:
            raise Inconclusive(f"input absent: {site}")
        hits = []
        for n, line in enumerate(text.splitlines(), 1):
            if any(r.search(line) for r in BACKEND_ALLOW_RES):
                continue  # a correct mention of the `gh` / `glab` CLI tools
            for r in BACKEND_CLAIM_RES:
                if r.search(line):
                    hits.append(f"{n}: {line.strip()[:100]}")
                    break
        if hits:
            findings[site] = hits
    return not findings, (f"{len(BACKEND_SITES)} enumerated site(s) checked by name; "
                          + ("clean" if not findings
                             else f"{sum(len(v) for v in findings.values())} finding(s)")), findings


def sc_group_membership(root: Path, a) -> tuple[bool, str, dict]:
    """SC9 — `architecture.d2` depicts the WORKFLOWS group it previously omitted entirely, and
    every group's enumerated member NAMES agree with frontmatter (mandate (d))."""
    # NORMALIZE THE `.d2` ESCAPE FIRST. A label is one physical line with `\n` as a literal
    # two-character escape, so "(5)\nbeads-init" puts an `n` immediately before the member name
    # and any word-boundary match fails. Measured: without this, 9 of 20 members read as absent
    # from a diagram that names every one of them.
    d2 = read(root, ARCH_D2).replace("\\n", " · ")
    census = skill_group_census(root)
    findings = []
    for group in SKILL_GROUPS:
        if not re.search(rf"\b{group}\b", d2, re.I):
            findings.append(f"group `{group}` is NOT DEPICTED in {ARCH_D2}")
            continue
        expected = census.get(group, [])
        # ACCEPT THE SHORTHAND FORM. The diagram labels read `beads-init · beads-extra`, not
        # `yf-beads-init · yf-beads-extra`: on a rendered image the `yf-` on every name is pure
        # noise, and dropping it is the right authoring choice. `check_web_counts` already
        # resolves shorthand against the same census, so requiring the long form HERE would put
        # two criteria in disagreement about one fact — which is its own defect, and exactly the
        # class this plan exists to close.
        absent = [s for s in expected
                  if s not in d2 and not re.search(rf"(?<![a-z0-9-]){re.escape(s[3:])}(?![a-z0-9-])", d2)]
        if absent:
            findings.append(f"group `{group}`: member id(s) absent from the diagram "
                            f"(neither the full id nor its `yf-`-stripped form): {absent}")
    return not findings, (f"{len(SKILL_GROUPS)} group(s) checked by name against frontmatter "
                          f"({sum(len(v) for v in census.values())} skills); "
                          + ("clean" if not findings else "; ".join(findings))), \
        {"census": census, "findings": findings}


def sc_formulas_diagram(root: Path, a) -> tuple[bool, str, dict]:
    """SC23 — `formulas.d2` states FIVE shipped formulas and depicts all five BY NAME."""
    d2 = read(root, FORMULAS_D2)
    on_disk = sorted(p.name.replace(".formula.toml", "")
                     for p in (root / "skills").glob("*/formulas/*.formula.toml"))
    findings = []
    if re.search(r"\bthree\b\s+shipped", d2, re.I):
        findings.append("still states 'three shipped'")
    undepicted = [f for f in SHIPPED_FORMULAS if f not in d2]
    if undepicted:
        findings.append(f"not depicted: {undepicted}")
    if sorted(on_disk) != sorted(SHIPPED_FORMULAS):
        raise Inconclusive(f"the enumerated formula set {SHIPPED_FORMULAS} no longer matches "
                           f"what ships ({on_disk}) — update this constant before trusting SC23")
    return not findings, (f"{len(SHIPPED_FORMULAS)} shipped formula(s) checked by name; "
                          + ("clean" if not findings else "; ".join(findings))), \
        {"shipped": on_disk, "findings": findings}


def sc_render_bytes_match(root: Path, a) -> tuple[bool, str, dict]:
    """SC10 — every committed PNG is sha256-identical to a FRESH render under the recorded pin.

    Byte equality IS decidable WITHIN a pinned version (measured twice) and is NOT across
    versions — which is why both `d2 --version` and the render flags are pinned here. It
    replaces an encoding-signature form measured NON-discriminating: all six fresh renders
    share one signature, and committed `lifecycle.png` already matched it while differing in
    sha256 — 1/6 satisfied with zero work, and satisfiable by a stale PNG.
    """
    if not shutil.which("d2"):
        raise Inconclusive("d2 is not on PATH")
    ver = run_cmd(root, ["d2", "--version"]).stdout.strip()
    if D2_PIN not in ver:
        raise Inconclusive(f"d2 is {ver!r}, not the recorded pin {D2_PIN} — sha256 equality is "
                           f"decidable only WITHIN a version")
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
            detail[png.name] = {"committed": a_[:12], "fresh": b_[:12]}
            if a_ != b_:
                mismatched.append(png.name)
    return not mismatched, (f"d2 {ver} == pin; {len(srcs)} diagram(s) compared by sha256 under "
                            f"{' '.join(D2_FLAGS)}; "
                            + ("all identical" if not mismatched
                               else f"MISMATCHED: {mismatched}")), detail


def sc_diagram_reads(root: Path, a) -> tuple[bool, str, dict]:
    """SC11b — the human reads were RECORDED: one dated entry per diagram."""
    text = read(root, a.input or f"{PLAN_DIR}/findings/diagram-reads.md")
    srcs = sorted(p.stem for p in (root / DIAGRAM_DIR).glob("*.d2"))
    if not srcs:
        raise Inconclusive(f"no .d2 sources under {DIAGRAM_DIR}")
    missing = []
    for slug in srcs:
        block = re.search(rf"^#+\s.*\b{re.escape(slug)}\b.*$", text, re.M)
        if not block:
            missing.append(f"{slug}: no entry")
            continue
        # INCLUDE THE HEADING ITSELF. The entries date themselves in the heading
        # ("### `x.png` — 2026-09-05 — CLEAN"), which is the natural place to put it; a window
        # starting AFTER the heading cannot see it, and reported the last section as undated
        # while every section was dated.
        after = text[block.start():block.end() + 1200]
        if not re.search(r"\b20\d\d-\d\d-\d\d\b", after):
            missing.append(f"{slug}: entry carries no date")
    return not missing, (f"{len(srcs)} diagram(s); "
                         + ("each has a dated entry" if not missing else "; ".join(missing))), \
        {"missing": missing}


def sc_diagram_orphans(root: Path, a) -> tuple[bool, str, dict]:
    """SC24 — no `.d2` lacks a sibling `.png`. ORPHAN DETECTION ONLY.

    `render.py check-dir` exits non-zero ONLY on orphans; staleness never affects its exit code
    (measured, pass-1 C6: it returns `{"status":"ok"}` over the very diagrams this plan calls
    wrong). It is therefore NOT cited as a staleness check — SC10 is what compares bytes.
    """
    srcs = sorted((root / DIAGRAM_DIR).glob("*.d2"))
    if not srcs:
        raise Inconclusive(f"no .d2 sources under {DIAGRAM_DIR}")
    orphans = [p.name for p in srcs if not p.with_suffix(".png").is_file()]
    return not orphans, (f"{len(srcs)} source(s); "
                         + ("no orphans" if not orphans else f"ORPHANS: {orphans}")), \
        {"orphans": orphans}


def sc_manifest_rows(root: Path, a) -> tuple[bool, str, dict]:
    """SC12 — the DRIFT-CHECK nodes/edges/§6 rows Class-B requires, and every §6 row names
    something that EXISTS (referential closure, via the Epic-0 tagged test)."""
    closure = run_cmd(root, ["uv", "run", "scripts/checks/check_drift_manifest_closure.py"])
    if closure.returncode == 2:
        raise Inconclusive(f"closure check INCONCLUSIVE: {closure.stderr.strip()[:200]}")
    manifest = read(root, "DRIFT-CHECK.md")
    required = ["web-diagram-src", "yf/src/harness_desc.rs", "e-web-cli-surface"]
    absent = [r for r in required if r not in manifest]
    # `e-okf-version-pin`'s §2 Check Category was `value-equal` — a §3 CONTRACT term outside
    # the declared §2 vocabulary, so the edge selected no check engine.
    bad_category = bool(re.search(r"^\|\s*`e-okf-version-pin`\s*\|[^|]*\|[^|]*\|\s*`?value-equal",
                                  manifest, re.M))
    findings = ([f"absent from the manifest: {absent}"] if absent else []) + \
               (["`e-okf-version-pin` still carries a §3 contract term as its §2 category"]
                if bad_category else []) + \
               ([f"closure check exit {closure.returncode}"] if closure.returncode else [])
    return not findings, ("manifest rows + referential closure: "
                          + ("clean" if not findings else "; ".join(findings))), \
        {"closure_exit": closure.returncode, "absent": absent}


def sc_land_documented(root: Path, a) -> tuple[bool, str, dict]:
    """SC13 — `land` documented as a `plan_manager.py` verb; NO page AFFIRMS the slash form.

    The negative leg ignores a negated mention (pass-3 C6): naming the wrong form IN ORDER TO
    CORRECT IT is the right way to do the work and must not be punished.
    """
    page = read(root, "web/content/skills/yf-plan.md")
    positive = bool(re.search(r"plan_manager\.py\b[^\n]*\bland\b|`land`[^\n]*plan_manager\.py",
                              page))
    affirmations = []
    for rel in sorted(str(p.relative_to(root)) for p in (root / "web/content").rglob("*.md")):
        for n, line in enumerate(read(root, rel).splitlines(), 1):
            if affirms(line, "/yf-plan land"):
                affirmations.append(f"{rel}:{n}")
    ok = positive and not affirmations
    return ok, ("verb form stated" if positive else "the plan_manager.py verb form is NOT stated") \
        + ("; no affirmative slash-form claim" if not affirmations
           else f"; AFFIRMS the slash form at {affirmations}"), \
        {"positive": positive, "affirmations": affirmations}


def sc_escalation_documented(root: Path, a) -> tuple[bool, str, dict]:
    """SC14 — the escalation surface documented as a yf-plan mechanism; no page ASSERTS a
    `yf-judgement` skill exists. Same negated-mention carve-out as SC13."""
    page = read(root, "web/content/skills/yf-plan.md")
    positive = bool(re.search(r"escalat", page, re.I))
    affirmations = []
    for rel in sorted(str(p.relative_to(root)) for p in (root / "web/content").rglob("*.md")):
        for n, line in enumerate(read(root, rel).splitlines(), 1):
            if affirms(line, "yf-judgement"):
                affirmations.append(f"{rel}:{n}")
    ok = positive and not affirmations
    return ok, ("escalation surface documented" if positive else "escalation is NOT documented") \
        + ("; no affirmative yf-judgement claim" if not affirmations
           else f"; AFFIRMS a yf-judgement skill at {affirmations}"), \
        {"positive": positive, "affirmations": affirmations}


def sc_epic6_renders(root: Path, a) -> tuple[bool, str, dict]:
    """SC15 — every page Epic 6 authored ACTUALLY RENDERED.

    Measured (pass-1 C5): a page under a directory absent from `PAGE_PATHS` yields exit 0, an
    unchanged page count, zero warnings and NO OUTPUT. A page that silently never renders is
    this plan's own thesis firing inside the plan.
    """
    rc, _, _ = pelican_build(root)
    if rc != 0:
        raise Inconclusive(f"pelican exited {rc}; cannot inspect rendered pages")
    glossary = root / "web/content/pages/concepts.md"
    pages = list(EPIC6_PAGES)
    if glossary.is_file():
        pages.append((str(glossary.relative_to(root)), "output/concepts/index.html"))
    findings = []
    for src, out in pages:
        if not (root / src).is_file():
            raise Inconclusive(f"input absent: {src}")
        html = root / "web" / out
        if not html.is_file():
            findings.append(f"{src} -> {out} WAS NOT EMITTED")
            continue
        ok, d = html_is_substantial(html.read_text(encoding="utf-8"))
        if not ok:
            findings.append(f"{out} is trivial ({d})")
    return not findings, (f"{len(pages)} Epic-6 page(s) checked; "
                          + ("all emitted non-trivial HTML" if not findings
                             else "; ".join(findings))), {"findings": findings}


def sc_classb_disposition(root: Path, a) -> tuple[bool, str, dict]:
    """SC16 — every Class-B defect explicitly CLOSED or FILED WITH AN OWNER, ENUMERATED BY
    NAME — never implied by a green build."""
    text = read(root, a.input or f"{PLAN_DIR}/findings/classb-disposition.md")
    missing = []
    for item in CLASSB_ITEMS:
        m = re.search(rf"^.*\b{re.escape(item)}\b.*$", text, re.M | re.I)
        if not m:
            missing.append(f"{item}: no disposition line")
        elif not re.search(r"\b(closed|filed)\b", m.group(0), re.I):
            missing.append(f"{item}: named but neither CLOSED nor FILED")
    return not missing, (f"{len(CLASSB_ITEMS)} Class-B item(s); "
                         + ("each explicitly disposed" if not missing else "; ".join(missing))), \
        {"missing": missing}


def sc_retro_classes(root: Path, a) -> tuple[bool, str, dict]:
    """SC17 — the retrospective distinguishes content defects from process defects, WITH
    COUNTS."""
    text = read(root, a.input or f"{PLAN_DIR}/plan-retrospective.md")
    has_content = bool(re.search(r"content defect", text, re.I))
    has_process = bool(re.search(r"process defect", text, re.I))
    counts = re.findall(r"\b(\d+)\s+(?:content|process|Class-[AB])\b", text, re.I)
    findings = ([] if has_content else ["no 'content defect' class"]) + \
               ([] if has_process else ["no 'process defect' class"]) + \
               ([] if len(counts) >= 2 else [f"fewer than two counts found ({counts})"])
    return not findings, ("retrospective distinguishes both classes with counts"
                          if not findings else "; ".join(findings)), {"counts": counts}


def sc_notchecked_declared(root: Path, a) -> tuple[bool, str, dict]:
    """SC18 — the plan DECLARED which claim classes the mechanical gate does NOT cover
    (REQ-CHECK-009, this plan's own Epic-0 requirement)."""
    cv = read(root, "CHANGE-VALIDATION.md")
    classes = ["semantic mis-assignment", "missing qualifier", "editorial omission"]
    absent = [c for c in classes if not re.search(c.replace(" ", r"\s+"), cv, re.I)]
    declared = bool(re.search(r"not[_ ]checked", cv, re.I))
    findings = ([] if declared else ["no `not_checked` declaration in CHANGE-VALIDATION.md"]) + \
               ([f"undeclared class(es): {absent}"] if absent else [])
    return not findings, ("the mechanical/prose split is declared"
                          if not findings else "; ".join(findings)), {"absent": absent}


def sc_adjacent_surfaces(root: Path, a) -> tuple[bool, str, dict]:
    """SC19 — the three adjacent surfaces (#363, #322, #104)."""
    findings = []
    okf_ext = read_opt(root, "skills/yf-okf/OKF-EXTENSION.md") or ""
    if re.search(r"^\s*(>\s*)?\**Status:?\**\s*DRAFT", okf_ext, re.M | re.I):
        findings.append("#363: OKF-EXTENSION.md still carries a DRAFT banner")
    hyg = read_opt(root, "skills/yf-okf-hygiene/SKILL.md") or ""
    if re.search(r"31 legacy", hyg) and not re.search(
            r"(this repo|in this repository|measured (in|on)|as of)", hyg, re.I):
        findings.append("#322: the '31 legacy' figure still reads as repo-agnostic")
    pconf = read_opt(root, "web/pelicanconf.py") or ""
    mk = read_opt(root, "web/Makefile") or ""
    if "IGNORE_FILES" not in pconf:
        findings.append("#104: no IGNORE_FILES in pelicanconf.py")
    if "stopserver" not in mk:
        findings.append("#104: no stopserver target in web/Makefile")
    return not findings, ("all three adjacent surfaces repaired"
                          if not findings else "; ".join(findings)), {"findings": findings}


def sc_ci_wired(root: Path, a) -> tuple[bool, str, dict]:
    """SC20 — the new coverage fires OUTSIDE the yf-plan land path.

    A CI job invokes all four checker scripts BY NAME and is REACHED on every PR and every push
    to `main`. **Do NOT add a `paths:` filter** (pass-3 C2): `ci.yml` runs unfiltered today, so
    a filtered job would give strictly LESS coverage.
    """
    ci = read(root, ".github/workflows/ci.yml")
    absent = [c for c in EPIC2_CHECKERS if Path(c).name not in ci]
    findings = [f"not invoked by name in ci.yml: {absent}"] if absent else []
    if re.search(r"^\s*if:\s*false\b", ci, re.M):
        findings.append("a job is gated behind `if: false`")
    if re.search(r"^\s{2,}paths(-ignore)?:", ci, re.M):
        findings.append("ci.yml gained a `paths:` filter — that is strictly LESS coverage")
    return not findings, ("all four checkers invoked by name in an unfiltered ci.yml job"
                          if not findings else "; ".join(findings)), {"absent": absent}


def sc_cv_rows(root: Path, a) -> tuple[bool, str, dict]:
    """SC25 — `CHANGE-VALIDATION.md` §1 rows for all FOUR checkers NAMED EXPLICITLY, and §3
    globs covering BOTH the doc side AND the SOURCE side.

    Not a `check_web_*` glob: `check_skill_page_contract.py` lacks that prefix, so a glob
    silently drops it (pass-3 C4). The source side is as load-bearing as the doc side — an
    absent file is never edited and can never fire its own on-edit check.
    """
    cv = read(root, "CHANGE-VALIDATION.md")
    absent = [c for c in EPIC2_CHECKERS if Path(c).name not in cv]
    doc_side = ["web/content/**", "README.md", "AGENTS.md"]
    src_side = ["skills/*/SKILL.md", "skills/*/formulas/**", "yf/src/harness_desc.rs"]
    miss_doc = [g for g in doc_side if g not in cv]
    miss_src = [g for g in src_side if g not in cv]
    findings = ([f"§1 recipe rows absent for: {absent}"] if absent else []) + \
               ([f"§3 doc-side glob(s) absent: {miss_doc}"] if miss_doc else []) + \
               ([f"§3 SOURCE-side glob(s) absent: {miss_src}"] if miss_src else [])
    return not findings, ("four §1 rows named explicitly; §3 covers both sides"
                          if not findings else "; ".join(findings)), \
        {"absent": absent, "miss_doc": miss_doc, "miss_src": miss_src}


def sc_removed_features(root: Path, a) -> tuple[bool, str, dict]:
    """SC21 — removed-feature claims repaired at EVERY site, INCLUDING the `SKILL.md` copy.

    Fixing the page alone would leave the `e-skillspec-skillmd` edge unexamined.
    """
    page = read(root, "web/content/skills/yf-okf.md")
    skill = read(root, "skills/yf-okf/SKILL.md")
    findings = []
    if re.search(r"assess\s+<corpus>", page):
        findings.append("`assess <corpus>` still present in web/content/skills/yf-okf.md")
    claim = re.compile(r"migration is the only write path", re.I)
    for label, text in (("web/content/skills/yf-okf.md", page), ("skills/yf-okf/SKILL.md", skill)):
        for n, line in enumerate(text.splitlines(), 1):
            if claim.search(line) and not NEGATION_RE.search(line):
                findings.append(f"{label}:{n} still affirms 'migration is the only write path'")
    return not findings, ("removed-feature claims repaired at both sites"
                          if not findings else "; ".join(findings)), {"findings": findings}


def sc_prose_rows(root: Path, a) -> tuple[bool, str, dict]:
    """SC22 — the two PROSE-ONLY rows repaired by hand, and the unverifiable ones FLAGGED."""
    findings = []
    tune = read(root, "web/content/pages/harness-tune.md")
    if not re.search(r"sha256", tune, re.I):
        findings.append("harness-tune.md carries no sha256-guard qualifier")
    auth = read(root, "web/content/skills/yf-skill-authoring.md")
    if "ML010" not in auth:
        findings.append("yf-skill-authoring.md does not name ML010")
    if re.search(r"\bsix\b[^\n]*rule|rule[^\n]*\bsix\b", auth, re.I):
        findings.append("yf-skill-authoring.md still says the subset is six rules")
    why = read(root, "web/content/pages/why.md")
    if not re.search(r"unverifiab|no in-repo source of truth|not verifiable", why, re.I):
        findings.append("why.md's competitor table carries no explicit unverifiable marker")
    return not findings, ("prose rows repaired and unverifiable claims flagged"
                          if not findings else "; ".join(findings)), {"findings": findings}


def sc_verbs_match(root: Path, a) -> tuple[bool, str, dict]:
    """SC26 — the criteria table's verb set agrees with this script's subcommands.

    **BARE EQUALITY, NO CARVE-OUT** (pass-4 C1). A carve-out for `verbs-match` itself was added
    on the reasoning that it appears in no criterion — but the SAME remediation added SC26,
    whose Verification cell invokes it. The two cancel: with SC26 present the verb IS in the
    table, so a carved-out equality is unsatisfiable by construction and would surface only at
    completion, blocking close. The bare equality is right BECAUSE SC26 runs the verb — the
    invariant holds only while a criterion executes it, which is what SC26 guarantees.
    """
    plan = read(root, f"{PLAN_DIR}/plan.md")
    in_plan = set(re.findall(r"plan066_checks\.py\s+([a-z0-9][a-z0-9-]*)", plan))
    if not in_plan:
        raise Inconclusive("parsed zero verbs out of plan.md — the parser, not the plan, is wrong")
    mine = set(SUBCOMMANDS)
    only_plan, only_script = sorted(in_plan - mine), sorted(mine - in_plan)
    ok = not only_plan and not only_script
    return ok, (f"{len(in_plan)} verb(s) in plan.md, {len(mine)} subcommand(s); "
                + ("sets are equal" if ok
                   else f"in plan.md only: {only_plan}; in script only: {only_script}")), \
        {"only_plan": only_plan, "only_script": only_script}


SUBCOMMANDS = {
    "adjacent-surfaces": sc_adjacent_surfaces,
    "backend-sites": sc_backend_sites,
    "build-clean": sc_build_clean,
    "checkers-green": sc_checkers_green,
    "ci-wired": sc_ci_wired,
    "classb-disposition": sc_classb_disposition,
    "cv-rows": sc_cv_rows,
    "diagram-orphans": sc_diagram_orphans,
    "diagram-reads": sc_diagram_reads,
    "epic6-renders": sc_epic6_renders,
    "escalation-documented": sc_escalation_documented,
    "formulas-diagram": sc_formulas_diagram,
    "group-membership": sc_group_membership,
    "harness-sites": sc_harness_sites,
    "inventory-control": sc_inventory_control,
    "land-documented": sc_land_documented,
    "manifest-rows": sc_manifest_rows,
    "notchecked-declared": sc_notchecked_declared,
    "page-content": sc_page_content,
    "prose-rows": sc_prose_rows,
    "removed-features": sc_removed_features,
    "render-bytes-match": sc_render_bytes_match,
    "retro-classes": sc_retro_classes,
    "verbs-match": sc_verbs_match,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="plan066_checks.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # MANDATE (a): `choices` makes an unknown verb exit 2 (argparse's usage error), never 0.
    ap.add_argument("subcommand", choices=sorted(SUBCOMMANDS))
    ap.add_argument("--input", help="override the artifact this subcommand reads "
                                    "(negative-control fixtures; never mutates the repo)")
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
           "not_checked": ["semantic mis-assignment beyond the id sets named here",
                           "missing qualifiers outside prose-rows",
                           "editorial omission"]}
    if a.json:
        print(json.dumps(env, indent=1))
    else:
        print(f"{verdict} ({code}) {a.subcommand}: {reason}")
    return code


if __name__ == "__main__":
    sys.exit(main())
