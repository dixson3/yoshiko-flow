#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Schema-driven linter for yf artifact documents (REQ-DATA-024).

**MINIMAL engine — plan-047 Epic 1.** Reads `_shared/document_types/<type>.toml`, walks each
type's path set, and emits `{"findings": [...]}` on `--json`. The severity/status-promotion
and full path machinery land in Epic 4; what is here is exactly enough to make the Epic-3 gate
*real*.

**The one thing that must be true from the first commit: `sys.exit(1)` on any error-severity
finding.** EXP-005 reproduced a linter printing `errors=4` while the delegating engine reported
`status: pass`, because it exited 0. A linter with no exit code is not a step.

Exit contract — TWO vocabularies, KEYED BY MODE (REQ-DATA-024 as amended by plan-050, and
REQ-DATA-061). The old "binary at every binding point" wording is retired: `classify` gives this
same executable a second `0/1/2` meaning.

LINT mode (the default):

    0  no error-severity finding            (verdict PASS)
    1  at least one error-severity finding  (verdict FAIL)
    2  the linter could not run             (verdict INCONCLUSIVE)

CLASSIFY mode (`--classify`, REQ-DATA-061) — a PREFLIGHT, not a lint:

    0  lintable      (class `selected` or `empty`)
    1  not lintable  (class `not-selected` or `no-such-path`)
    2  the classifier could not run

A `classify` run over a selected-but-empty document exits 0 while a lint run over the same
document exits 1 on its `E` findings — which is why the contract is stated per mode. Callers
branch on the emitted `class`, never on the classify exit code alone: the two non-lintable
classes are different facts and collapsing them is the very conflation #181 was filed about.
The VERDICT vocabulary is unchanged and closed — `classify` emits a `class`, never a verdict.

`INCONCLUSIVE` means *only* "could not run". "Not finished yet" is a `W` finding **inside a
PASS** — it never changes the exit code. `INCOMPLETE` is the reviewer agent's vocabulary and
never appears here.

Usage:

    uv run _shared/doc_lint.py                       # lint every type over the repo
    uv run _shared/doc_lint.py --json                # machine-readable
    uv run _shared/doc_lint.py --path <p> [--path p] # only these files
    uv run _shared/doc_lint.py --type plan           # only this type
    uv run _shared/doc_lint.py --no-exclude          # POSITIVE CONTROL: ignore carve-outs
"""

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path


def _discover_repo_root() -> Path:
    """The repository root, resolved EXPLICITLY rather than by position (REQ-DATA-056).

    `Path(__file__).parent.parent` is correct for the canonical `_shared/` copy and **wrong
    for every vendored one**: a byte-identical copy at `skills/yf-plan/scripts/doc_lint.py`
    resolves the "repo root" to `skills/yf-plan/`, where no `docs/plans/**` glob matches
    anything. The engine then returns `files_checked: 0` on every real document — and
    `files_checked: 0` is INDISTINGUISHABLE from a clean pass at the exit-code level, so a
    deployed vault would report green while linting nothing.

    **A byte-identical vendor of a root-relative script is not a vendor.** The vendor is only
    real once root resolution stops depending on where the file sits, which is why this
    function exists rather than a second constant.

    Order: `$YF_REPO_ROOT` (explicit override) -> `git rev-parse --show-toplevel` from the CWD
    -> the nearest ancestor of CWD carrying a `.git` -> the positional guess, last. `--root`
    overrides all of it at the CLI.
    """
    env = os.environ.get("YF_REPO_ROOT")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except (OSError, subprocess.SubprocessError):
        pass
    for d in [Path.cwd(), *Path.cwd().parents]:
        if (d / ".git").exists():
            return d.resolve()
    return Path(__file__).resolve().parent.parent


REPO_ROOT = _discover_repo_root()
TYPES_DIR = Path(__file__).resolve().parent / "document_types"

ERROR, WARN, REPORT = "E", "W", "R"

# Status-aware promotion (REQ-DATA-024). A plan's `status` selects the severity mapping.
#
# **Why this is not cosmetic, and why it lands with the recipe row rather than after it.**
# Measured on this corpus: all 46 historical bundles are `complete`, and the raw linter
# reports 320 error-severity findings across 169 files. Adding the `doclint` recipe row
# without this mapping would make the repo's own FAST tier permanently RED — and, decisively,
# it would make the row's own falsification VACUOUS: injecting a mutant and observing
# `status: fail` proves nothing when the tier was already failing. A control that cannot
# distinguish its signal from the background is the same defect class as one that cannot fire.
STATUS_SEVERITY = {
    # drafting statuses: completeness warnings are informational, structure still errors
    "scoping": {WARN: WARN},
    "investigating": {WARN: WARN},
    "drafting": {WARN: WARN},
    # under review: a warning becomes an error — the plan is claiming to be finished
    "review": {WARN: ERROR},
    "ready-for-approval": {WARN: ERROR},
    # a finished plan is REPORT-ONLY, never an error. History is not re-judged by a rule
    # written after it: the 46 completed bundles predate every schema in document_types/.
    # Past the enforcement point. The linter's binding is at INTAKE (`review` /
    # `ready-for-approval`); once a plan is approved its content is frozen by the
    # fingerprint (REQ-PORT-040), so re-judging it mid-execution would manufacture exactly
    # the stale-approved churn REQ-DATA-025 exists to avoid.
    "approved": {WARN: REPORT, ERROR: REPORT},
    "executing": {WARN: REPORT, ERROR: REPORT},
    "reconciling": {WARN: REPORT, ERROR: REPORT},
    "complete": {WARN: REPORT, ERROR: REPORT},
    # `abandoned` (#208, plan-053): a plan deliberately stopped. SAME PROFILE AS `complete`
    # and for the same reason -- both are TERMINAL, so a finding on one is a report about a
    # record, never an actionable defect. Listed EXPLICITLY rather than left to fall through a
    # default, because an unmapped status is exactly what REQ-DATA-072's fail-closed treatment
    # reddens: inheriting this by accident would hard-fail every abandoned bundle.
    "abandoned": {WARN: REPORT, ERROR: REPORT},
}


#: REQ-DATA-072 -- the mapping applied to a status that is PRESENT but UNRECOGNISED. The
#: STRICTEST available: `W` is promoted to `E`, so an invented status cannot silently disable
#: the promotion the linter relies on at `review`. Deliberately NOT the mapping for an ABSENT
#: status, which stays the permissive empty map -- see the two-branch predicate in `lint()`.
_UNRECOGNISED_STATUS_SEVERITY = {WARN: ERROR}


class Inconclusive(RuntimeError):
    """The linter could not run — exit 2, verdict INCONCLUSIVE. Never a FAIL."""


# --- schema loading ----------------------------------------------------------------


def load_schemas(only: str | None = None) -> list[dict]:
    if not TYPES_DIR.is_dir():
        raise Inconclusive(f"no document_types/ directory at {TYPES_DIR}")
    out = []
    for f in sorted(TYPES_DIR.glob("*.toml")):
        try:
            d = tomllib.load(f.open("rb"))
        except Exception as e:  # malformed schema is a harness failure, not a document FAIL
            raise Inconclusive(f"{f.name}: {e}") from e
        if d.get("type") != f.stem:
            raise Inconclusive(f"{f.name}: `type` is {d.get('type')!r}, expected {f.stem!r}")
        if d.get("producer_class") == "code-generated" and not d.get("derive_from"):
            raise Inconclusive(f"{f.name}: code-generated type must set `derive_from`")
        if only and d["type"] != only:
            continue
        out.append(d)
    if only and not out:
        raise Inconclusive(f"no schema for type {only!r}")
    return out


def resolve_derived(dotted: str) -> list[str]:
    """Import `<module>.<ATTR>` from `_shared/` and return it as a list of section names."""
    mod_name, _, attr = dotted.rpartition(".")
    path = Path(__file__).resolve().parent / f"{mod_name}.py"
    if not path.exists():
        raise Inconclusive(f"derive_from: no module {mod_name!r} in _shared/")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, attr):
        raise Inconclusive(f"derive_from: {mod_name} has no attribute {attr!r}")
    return list(getattr(mod, attr))


# --- document parsing --------------------------------------------------------------


def bundle_status(path: Path) -> str | None:
    """The `status` of the plan bundle owning `path`, or None if it is not in one.

    Walks up to the nearest directory containing a `plan.md` and reads its status
    frontmatter-first with a `**Status:**` fallback (REQ-DATA-015 read order).
    """
    for d in [path if path.is_dir() else path.parent, *path.parents]:
        pm = d / "plan.md"
        if not pm.is_file():
            continue
        text = pm.read_text(encoding="utf-8", errors="replace")
        if text.startswith("---\n"):
            end = text.find("\n---\n", 4)
            if end > 0:
                m = re.search(r"^status:\s*['\"]?([\w-]+)", text[4:end], re.M)
                if m:
                    return m.group(1)
        m = re.search(r"^\*\*Status:\*\*\s*(\S+)", text, re.M)
        return m.group(1) if m else None
    return None


def frontmatter_keys(text: str) -> set[str]:
    if not text.startswith("---\n"):
        return set()
    end = text.find("\n---\n", 4)
    if end < 0:
        return set()
    keys = set()
    for line in text[4:end].split("\n"):
        m = re.match(r"^([A-Za-z_][\w.-]*):", line)
        if m:
            keys.add(m.group(1))
    return keys


def sections(text: str, any_level: bool = False) -> list[str]:
    """Ordered headings, skipping fenced code blocks. Level 2 only unless `any_level`."""
    out, fenced = [], False
    for line in text.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = re.match(r"^#{2,6} +(.+?)\s*$" if any_level else r"^## +(.+?)\s*$", line)
        if m:
            out.append(m.group(1))
    return out


def section_body(text: str, name: str) -> str | None:
    lines, body, fenced, capturing = text.split("\n"), [], False, False
    for line in lines:
        if line.startswith("```"):
            fenced = not fenced
            if capturing:
                body.append(line)
            continue
        if not fenced and re.match(r"^## +", line):
            if capturing:
                break
            capturing = re.match(r"^## +(.+?)\s*$", line).group(1) == name
            continue
        if capturing:
            body.append(line)
    return "\n".join(body) if capturing or body else None


# A GFM cell separator is an UNESCAPED pipe. `\|` inside a cell is a literal pipe and must
# not split it. This is the same latent defect fixed in `plan_extract._table_rows`
# (plan-048 Issue 1.1) — both parsers read the same corpus, so both had to be fixed.
_CELL_SPLIT = re.compile(r"(?<!\\)\|")


def _split_row(inner: str) -> list[str]:
    """Split one table row's interior into cells, honouring GFM-escaped pipes."""
    return [c.strip().replace("\\|", "|") for c in _CELL_SPLIT.split(inner)]


def first_table(body: str) -> tuple[list[str], list[list[str]]] | None:
    """Return (header cells, data rows) of the first GFM table in `body`."""
    rows, in_tbl = [], False
    for line in body.split("\n"):
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            rows.append(_split_row(s[1:-1]))
            in_tbl = True
        elif in_tbl:
            break
    if len(rows) < 2:
        return None
    return rows[0], rows[2:]  # rows[1] is the alignment row


# --- REQ-DATA-043: the extractor gate shared by every plan_extract consumer ----------

# Exit code for INCONCLUSIVE. Deliberately distinct from FAIL (1): "this instrument could
# not read the plan" and "the plan is wrong" are different claims, and a caller that
# collapses them has not implemented REQ-DATA-043.
INCONCLUSIVE = 2


def extractor_blocked(plan_dir) -> list[dict]:
    """Return the `unparsed[]` entries for a plan bundle ([] = safe to reason over).

    Every consumer of `plan_extract.extract()` calls this FIRST and returns INCONCLUSIVE
    when it is non-empty. The consumer set is closed and enumerated in REQ-DATA-043: the
    relational checks (`plan-relations`), the pour, and `pour_fidelity.py`.
    """
    from pathlib import Path as _P
    pm = _P(plan_dir)
    pm = pm / "plan.md" if pm.is_dir() else pm
    if not pm.is_file():
        return []
    try:
        return _plan_extract().extract(pm).get("unparsed") or []
    except Exception as exc:  # an extractor crash is also "could not read", never FAIL
        return [{"line": 0, "reason": f"extractor raised {type(exc).__name__}: {exc}",
                 "raw": ""}]


def _plan_extract():
    """Import the sibling extractor by path (``_shared`` is not an installed package)."""
    import importlib.util
    from pathlib import Path as _P
    global _PE_CACHE
    try:
        return _PE_CACHE
    except NameError:
        pass
    spec = importlib.util.spec_from_file_location(
        "pe_for_doclint", _P(__file__).resolve().parent / "plan_extract.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _PE_CACHE = mod
    return mod


# --- the `plan-relations` check kind (REQ-DATA-044, plan-048 Epic 3) -----------------
#
# A THIRD MECHANISM, not a variant of the two per-document schema flavours REQ-DATA-024
# declares. Those read ONE section in isolation. A relational rule reasons ACROSS sections
# and across tables of the same bundle — `## Epics`, `## Gates`, `## Success Criteria`,
# `## Upstream Issues` — which no per-document check can do.
#
# EVERY RULE HERE IS SEVERITY `W`, and `STATUS_SEVERITY` promotion is OFF for this kind —
# declared by REQ-DATA-044 and IMPLEMENTED by REQ-DATA-053's `promote = false` schema key,
# which `lint()` reads. Before plan-049 Issue 0.2 this sentence described no code. That is deliberate and stated rather than inherited: if `W -> E`
# fired at `review`, every future plan would hard-fail R1b unless every non-bookkeeping
# issue were named by a criterion — a bar plan-048 itself does not clear (it carries four
# such issues). A rule no in-flight plan can satisfy trains authors to write fake criteria,
# which is the exact failure R1b exists to prevent.

#: Recognised `Disposition` literals (REQ-DATA-019 as amended by plan-048 D-7).
DISPOSITIONS = {"include", "exclude", "partial", "supersede", "deferred", "tracker"}

#: An epic may declare itself exempt from R1b with this marker under its heading. The
#: carve-out is DECLARED, never inferred — an inferred exemption is indistinguishable
#: from an oversight.
BOOKKEEPING_MARKER = "<!-- epic-kind: bookkeeping -->"


#: `discharged_by` / `resolved_by` arrive as LISTS from the extractor, and their elements
#: carry prose ("Issue 5.3", "1.4 (lint half)"). One accessor so every rule reads them the
#: same way — two readers of one field is how R3's own defect class starts.
def _refs(value) -> list[str]:
    return re.findall(r"[0-9A-Z]+\.[0-9]+[a-z]?", _joined(value))


def _joined(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return " ".join(str(v) for v in value)
    return str(value)


def _bookkeeping_epics(path: Path) -> set[str]:
    """Epic numbers whose heading is followed by the bookkeeping marker."""
    out: set[str] = set()
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    cur = None
    for ln in lines:
        m = re.match(r"^### +(?:\*\*)?Epic +([0-9]+|[A-Z])", ln)
        if m:
            cur = m.group(1)
            continue
        if cur and BOOKKEEPING_MARKER in ln:
            out.add(cur)
        elif ln.startswith("### ") or ln.startswith("## "):
            cur = None
    return out


def run_plan_relations(chk: dict, path: Path | None) -> list[str]:
    """Run one relational rule over a plan bundle. Never raises on a parse gap."""
    if path is None:
        return []
    rule = chk.get("rule")

    # REQ-DATA-043: gate on `unparsed[]` FIRST. An unparsed construct means the extractor
    # did not SEE part of the plan, so every relational conclusion would be drawn from a
    # knowably incomplete DAG. INCONCLUSIVE is raised (not returned as a failure) so the
    # caller reports exit 2, never exit 1 — "could not read" is not "is wrong".
    blocked = extractor_blocked(path)
    if blocked:
        raise Inconclusive(
            f"{path.name}: {len(blocked)} unparsed construct(s) — relational rule "
            f"{rule!r} cannot be evaluated on an incomplete DAG "
            f"(first: L{blocked[0].get('line')} {blocked[0].get('reason', '')[:80]})")

    pm = path if path.is_file() else path / "plan.md"
    d = _plan_extract().extract(pm)
    issues = {i["id"] for i in d["issues"]}
    out: list[str] = []

    if rule == "R1":
        # `Discharged-by` names a real issue.
        for c in d.get("criteria", []):
            for ref in _refs(c.get("discharged_by")):
                if ref not in issues:
                    out.append(f"criterion {c.get('id')}: Discharged-by names {ref!r}, "
                               f"which is not an issue in this plan")
    elif rule == "R1b":
        # Every issue is named by at least one criterion, except in a DECLARED
        # bookkeeping epic.
        exempt = _bookkeeping_epics(pm)
        named: set[str] = set()
        for c in d.get("criteria", []):
            named.update(_refs(c.get("discharged_by")))
        for i in d["issues"]:
            if i["id"] not in named and i.get("epic") not in exempt:
                out.append(f"issue {i['id']} is named by no success criterion "
                           f"(epic {i.get('epic')} is not declared bookkeeping)")
    elif rule == "R2a":
        # `Resolved By` names a real issue.
        for u in d.get("upstream", []):
            for ref in _refs(u.get("resolved_by")):
                if ref not in issues:
                    out.append(f"upstream #{u.get('issue')}: Resolved By names {ref!r}, "
                               f"which is not an issue in this plan")
    elif rule == "R2b":
        # `exclude` resolves nothing; `include` resolves something.
        for u in d.get("upstream", []):
            disp = (u.get("disposition") or "").strip().strip("*_").lower()
            rb = _joined(u.get("resolved_by"))
            has = bool(_refs(u.get("resolved_by")))
            if disp == "exclude" and has:
                out.append(f"upstream #{u.get('issue')}: disposition `exclude` but "
                           f"Resolved By names {rb!r} — an excluded issue resolves nothing")
            if disp == "include" and not has:
                out.append(f"upstream #{u.get('issue')}: disposition `include` but "
                           f"Resolved By names no issue — an included issue resolves something")
    elif rule == "R2c":
        # The disposition is a recognised literal (bold/italic normalized first).
        for u in d.get("upstream", []):
            raw = (u.get("disposition") or "").strip()
            disp = raw.strip("*_").strip().lower()
            if disp and disp not in DISPOSITIONS:
                out.append(f"upstream #{u.get('issue')}: disposition {raw!r} is not one of "
                           + "|".join(sorted(DISPOSITIONS)))
    elif rule == "R3":
        # TWO-PARSER AGREEMENT. `parse_upstream_rows` (plan_manager) and `plan_extract`
        # must read every disposition cell identically. `verify-reconcile` is FAIL-LOUD,
        # so two parsers disagreeing on row shape is a fail-loud FALSE POSITIVE.
        other = _parse_upstream_rows_view(pm)
        if other is None:
            # "Not checked" is NOT "agreed". Say so, rather than reporting a clean R3.
            out.append("R3 could not run: plan_manager's parse_upstream_rows was "
                       "unavailable, so two-parser agreement is UNVERIFIED (not clean)")
        else:
            # KEY NORMALIZATION IS LOAD-BEARING. `plan_extract` emits `#113`;
            # `parse_upstream_rows` emits `113`. Joined raw, the two dicts share ZERO keys,
            # so the comparison reported "no disagreements" on every plan while comparing
            # nothing at all — R4's defect class inside the very rule meant to catch a
            # two-parser split. Both sides are reduced to a bare number before the join.
            def _num(k: str) -> str:
                return str(k).lstrip("#").strip()
            mine = {_num(u.get("issue")):
                    (u.get("disposition") or "").strip().strip("*_").lower()
                    for u in d.get("upstream", [])}
            theirs = {_num(k): v for k, v in other.items()}
            common = set(mine) & set(theirs)
            # Only a real join failure — BOTH sides non-empty yet sharing nothing. When
            # one side is empty the other is reading a placeholder row (`—`, `_none_`),
            # which is a different finding and R2c's to report.
            if not common and mine and theirs:
                out.append(
                    f"R3 compared NOTHING: {len(mine)} extractor rows and "
                    f"{len(theirs)} parser rows share no issue number — the join key is "
                    "broken, which would silently report agreement forever")
            for num in sorted(common):
                if mine[num] != theirs[num]:
                    out.append(f"upstream #{num}: parsers disagree on disposition — "
                               f"plan_extract {mine[num]!r} vs "
                               f"parse_upstream_rows {theirs[num]!r}")
    return out


def _parse_upstream_rows_view(pm: Path) -> dict[str, str] | None:
    """`{issue-number: normalized-disposition}` per plan_manager's shared parser.

    Extracted BY SOURCE SLICE rather than imported: `plan_manager.py` pulls in `click`,
    `yaml` and a vendored `okf`, none of which `_shared/` may assume are installed.

    THE SLICE MUST CARRY THE PARSER'S DEPENDENCIES. The first version sliced only
    `parse_upstream_rows`, which calls `_normalize_disposition` — so every call raised
    NameError, was swallowed, and returned None. R3 then reported ZERO disagreements across
    the whole corpus while never actually running: a check that cannot fail, which is
    exactly the defect class R4 exists to catch, reproduced inside R3's own harness.
    Returning None is a legitimate "not checked" signal, so nothing looked wrong.
    """
    # A SECOND POSITIONAL-ROOT SITE, found by the vendor (plan-049 Issue 4.1/4.2).
    # `__file__.parent.parent / "skills" / …` is right for the canonical `_shared/` copy and
    # wrong for the vendored one, which resolves it to `skills/skills/yf-plan/…`. The vendored
    # engine therefore returned None here and R3 reported "could not run" forever — the same
    # class of defect as `files_checked: 0`, and equally quiet, because "not checked" is a
    # legitimate-looking signal. The SIBLING candidate is listed first precisely because in a
    # deployed vault `plan_manager.py` sits next to this file.
    cand = next((c for c in (
        Path(__file__).resolve().parent / "plan_manager.py",
        REPO_ROOT / "skills" / "yf-plan" / "scripts" / "plan_manager.py",
        Path(__file__).resolve().parent.parent / "skills" / "yf-plan" / "scripts"
        / "plan_manager.py",
    ) if c.exists()), None)
    if cand is None:
        return None
    try:
        src = cand.read_text(encoding="utf-8", errors="replace")
        # Seed the namespace with the module-level constants the sliced functions close
        # over. A constant is not a `def`, so it cannot be sliced the same way.
        ns: dict = {"re": re, "_CELL_SPLIT": re.compile(r"(?<!\\)\|")}
        # Every name `parse_upstream_rows` depends on, sliced in dependency order.
        for fn in ("def _split_table_row(", "def _normalize_disposition(",
                   "def parse_upstream_rows("):
            start = src.index(fn)
            end = src.index("\ndef ", start + len(fn))
            exec(compile(src[start:end], str(cand), "exec"), ns)
        rows = ns["parse_upstream_rows"](pm.read_text(encoding="utf-8", errors="replace"))
        return {str(r["issue"]): (r.get("disposition") or "").strip().strip("*_").lower()
                for r in rows}
    except Exception:
        return None


# --- checks ------------------------------------------------------------------------


def run_check(chk: dict, text: str, schema: dict, path: Path | None = None) -> list[str]:
    """Return a list of failure detail strings ([] = the check passed)."""
    kind = chk.get("kind")
    if kind == "plan-relations":
        return run_plan_relations(chk, path)
    if kind in ("headings-present", "headings-any-level"):
        want = chk.get("value") or resolve_derived(schema["derive_from"])
        have = sections(text, any_level=(kind == "headings-any-level"))
        missing = [s for s in want if s not in have]
        if missing:
            return ["missing section(s): " + ", ".join(missing)]
        idx = [have.index(s) for s in want]
        if idx != sorted(idx):
            return ["sections out of order: expected " + " -> ".join(want)]
        return []
    if kind == "frontmatter-keys":
        missing = [k for k in chk["value"] if k not in frontmatter_keys(text)]
        return ["missing frontmatter key(s): " + ", ".join(missing)] if missing else []
    if kind == "regex-absent":
        return ([f"forbidden pattern present: {chk['pattern']}"]
                if re.search(chk["pattern"], text, re.M) else [])
    if kind == "regex-present":
        return ([] if re.search(chk["pattern"], text, re.M)
                else [f"required pattern absent: {chk['pattern']}"])
    if kind in ("table-columns", "row-id-grammar"):
        body = section_body(text, chk["section"])
        if body is None:
            return [f"section not found: {chk['section']}"]
        tbl = first_table(body)
        if tbl is None:
            return [f"no table under ## {chk['section']}"]
        header, data = tbl
        if kind == "table-columns":
            return ([] if header == chk["value"]
                    else [f"## {chk['section']} columns are {header}, expected {chk['value']}"])
        pat, seen, bad = re.compile(chk["pattern"]), set(), []
        for r in data:
            cell = r[0].strip() if r else ""
            if not pat.match(cell):
                bad.append(f"row id {cell!r} does not match {chk['pattern']}")
            elif cell in seen:
                bad.append(f"duplicate row id {cell!r}")
            else:
                seen.add(cell)
        return bad
    if kind == "cell-non-empty":
        # plan-049 Issue 3.1 (REQ-DATA-054). A table row whose REQUIRED cells are blank is a
        # row that asserts nothing while looking complete. plan-047's "90-finding exploit" was
        # exactly this shape, and EXP-006 measured the hole still open and WIDER than recorded:
        # a table with **zero rows** also passes every existing check, because
        # `table-columns` only inspects the header and `row-id-grammar` iterates a table with
        # nothing in it. Both are covered here.
        body = section_body(text, chk["section"])
        if body is None:
            return [f"section not found: {chk['section']}"]
        tbl = first_table(body)
        if tbl is None:
            # NOT this check's business. A section with no table at all is what
            # `table-columns` reports, and 44 of the 48 historical plans write their
            # `## Success Criteria` as a LIST rather than a table. Reporting it here too
            # would double-count one defect as two, and would swamp the signal this check
            # exists to carry. A missing table is a different claim from an EMPTY one.
            return []
        header, data = tbl
        if not data:
            # A ZERO-ROW table is UNDER-DETERMINED, not wrong (#185, plan-054 Issue 3.1). It is
            # the identical artifact in two OPPOSITE situations:
            #
            #   author skipped triage entirely      -> the check SHOULD fire (its whole purpose)
            #   author ran triage, upstream is empty -> the check should NOT fire; the emptiness
            #                                          IS the finding
            #
            # The second is not exotic: it is EVERY PLAN AUTHORED IN A FRESHLY CREATED
            # REPOSITORY. Measured live in dixson3/astrospike plan-001, where Phase 1.4 ran
            # `gh issue list`, got `[]`, recorded that in prose beneath the table — and the
            # check failed the plan anyway, because prose is not readable by a check. At
            # `review`/`ready-for-approval` the finding promotes W -> E, so `_audit_plan` failed
            # and `ready-check` blocked approval, leaving only two exits: fabricate a row
            # (strictly worse than the finding it silences) or `--force` (which also suppresses
            # any genuine finding in the same run, and records a bypass on a plan that had
            # nothing wrong with it).
            #
            # So the absence is made DECLARABLE (#185's option 1). A measured absence is an
            # ASSERTION, and an assertion is exactly what the check's own rationale asks for —
            # the complaint was never "no rows", it was "asserting nothing". Two signals count,
            # either alone sufficient:
            #
            #   * an explicit `no-upstream-issues:` sentinel in the section, carrying the
            #     command and date that produced the result; or
            #   * sibling TRIAGE EVIDENCE — an `upstream-triage.md` in the bundle, which
            #     `plan_manager.py triage` writes in Phase 1.4 (#185's option 2). This makes the
            #     distinction mechanical for plans that never hand-write a sentinel.
            #
            # #185's option 3 (drop the promotion) was rejected by the issue itself as its
            # weakest: it trades the false positive for a lost signal. The skipped case still
            # fires, exactly as before.
            body_l = body.lower()
            declared = "no-upstream-issues:" in body_l
            triage_evidence = False
            # `path` is the document under lint, already threaded into `run_check`. Reading it
            # here rather than inventing a new key matters: a key nothing ever sets would make
            # the triage-evidence half INERT — present in the code, never true in practice, and
            # indistinguishable from working.
            if path is not None:
                try:
                    triage_evidence = (path.parent / "upstream-triage.md").is_file()
                except OSError:  # an unreadable bundle is not a finding about the document
                    triage_evidence = False
            if declared or triage_evidence:
                return []
            return [f"## {chk['section']} table has ZERO rows and NO declared absence — a "
                    f"table with no rows satisfies every column and id check while asserting "
                    f"nothing. If triage RAN and measured zero issues, say so: add a "
                    f"`no-upstream-issues:` line recording the command and date, or keep the "
                    f"`upstream-triage.md` the triage step writes."]
        want = chk.get("columns") or []
        idx = {c: header.index(c) for c in want if c in header}
        missing_cols = [c for c in want if c not in header]
        if missing_cols:
            # A required column that is absent is the `table-columns` check's business, not
            # this one. Reporting it here too would double-count one defect.
            return []
        out = []
        for r in data:
            rid_raw = r[0].strip() if r else ""
            # A row whose ID CELL is itself a placeholder is a DECLARED-EMPTY marker — the
            # `| — | | |` / `| _none_ | | |` idiom 29 plans use to say "no upstream issues".
            # That row asserts, correctly, that there is nothing to fill in; firing on it
            # would manufacture 58 findings out of an authoring convention working as
            # intended. An UNFILLED row has a real id and blank cells; a DECLARED-EMPTY row
            # has neither. The two are distinguishable, so they are distinguished.
            if not _norm_cell(rid_raw):
                continue
            rid = rid_raw
            for c, i in idx.items():
                cell = _norm_cell(r[i]) if i < len(r) else ""
                if not cell:
                    out.append(f"row {rid!r}: required cell {c!r} is empty")
        return out
    if kind == "verification-clause":
        # plan-052 Issue 1.2 (REQ-DATA-070). A `Verification` cell written as PROSE cannot be
        # re-run, so the criterion it belongs to is only ever as true as the last time a human
        # read it. Measured over `docs/plans/plan-*/plan.md` at authoring time: **0 of 186**
        # criteria carried a machine-readable clause.
        #
        # THREE-VALUED, because REQ-DATA-024's exit contract is. A two-valued form would let
        # `-> exit non-zero` be satisfied by an INCONCLUSIVE, so a criterion asserting "the
        # harness is not a silent green" would pass WHILE THE HARNESS WAS BROKEN.
        #
        # `manual:` is FIRST-CLASS, not a failure. Without it an unmechanizable criterion gets
        # authored as a fake command written to satisfy a shape check, which is strictly worse
        # than an honest waiver.
        body = section_body(text, chk["section"])
        if body is None:
            return [f"section not found: {chk['section']}"]
        tbl = first_table(body)
        if tbl is None:
            # A section written as a LIST is `table-columns`' business, not this check's.
            return []
        header, data = tbl
        col = chk.get("column", "Verification")
        if col not in header:
            # An absent column is `table-columns`' finding; double-counting one defect as two
            # swamps the signal this check carries.
            return []
        i = header.index(col)
        out = []
        for r in data:
            rid = (r[0].strip() if r else "") or "?"
            if not _norm_cell(rid):
                continue  # a DECLARED-EMPTY marker row asserts nothing, correctly
            cell = (r[i] if i < len(r) else "").strip()
            if not _norm_cell(cell):
                continue  # emptiness is `cell-non-empty`'s finding
            if not _verification_clause_ok(cell):
                out.append(
                    f"row {rid!r}: Verification is PROSE, not a clause — expected "
                    f"`<command>` -> exit 0|1|2|non-zero, or `manual: <why>`; got {cell[:70]!r}"
                )
        return out
    if kind == "stale-measured-literal":
        # plan-049 Issue 5.2 (REQ-DATA-060, upstream #135).
        #
        # A plan that MEASURES the corpus and writes the figure into its own `plan.md` has
        # written a literal that goes stale the moment the corpus moves — and the plan is
        # usually inside the corpus it measured, so its own next edit is what moves it.
        # plan-048 produced three live instances (47->48 dirs, 112->119 review files,
        # 174->180 files_checked); plan-049 produced two more while drafting.
        #
        # SCOPED HARD, because the naive form is unusable. EXP-005 measured a check that
        # simply looks for "a number near a corpus noun" firing **41 out of 41 times, with 39
        # of those being correct historical behaviour** — the measured-marker failure mode: a
        # completed plan's measurement is a HISTORICAL RECORD and is *supposed* to be a frozen
        # literal. Re-judging it manufactures work and teaches nothing. The scoped form
        # measured **2 fires, 2 true positives, 0 false positives**.
        #
        # Three scoping rules, each earned:
        #   1. `status != complete`   -- only an IN-FLIGHT plan can still act on the finding
        #   2. skip `findings/` and `reviews/` -- an experiment writeup and a review verdict
        #      are point-in-time records BY CONSTRUCTION; freezing their numbers is correct
        #   3. severity `W`          -- a hint, never a gate
        if path is not None and any(part in ("findings", "reviews") for part in path.parts):
            return []
        status = bundle_status(path) if path is not None else None
        if status is None or status == "complete":
            return []
        out = []
        for m in _MEASURED_LITERAL.finditer(text):
            line = text[:m.start()].count("\n") + 1
            out.append(f"line {line}: measured literal {m.group('n')!r} beside "
                       f"{m.group('noun')!r} — this plan is in-flight and inside the corpus "
                       f"it measured, so its own next edit can stale this figure. Derive it, "
                       f"or state it as a delta (REQ-DATA-060). "
                       f"DENOMINATOR-ONLY: this finds a stale COUNT, never a stale claim "
                       f"ABOUT a count.")
        return out
    if kind == "gate-completeness":
        # plan-049 Issue 3.2 (REQ-DATA-055). The predicate is ALL THREE of `Type`, `Condition`
        # and `Test` absent — a gate that is a heading and nothing else.
        #
        # THE OBVIOUS PREDICATE IS WRONG AND WAS MEASURED WRONG. `Type` plus one-of fires on
        # **80 of 137 corpus gates**, including all 49 Start Gates AND the canonical template
        # (`plan_template.py`, `SKILL.md`), so binding it fail-closed at intake would leave
        # plan-050 unable to pass its own intake. A `Type: human` + `Approvers: operator`
        # Start Gate is a COMPLETE gate: the approver IS the condition.
        return _gate_completeness(text)
    raise Inconclusive(f"unknown check kind: {kind!r}")


#: REQ-DATA-070's clause grammar. `->` and the arrow are both accepted so an author is not
#: forced into a non-ASCII keystroke. The polarity marker is the load-bearing part: plan-051's
#: SC4 passes on exit 1 and its SC6 on exit 0, and before this rule that fact existed nowhere
#: but prose.
_CLAUSE_RE = re.compile(r"`.+`\s*(?:\u2192|->)\s*exit\s+(?:0|1|2|non-zero)\s*\Z", re.S)
_MANUAL_RE = re.compile(r"\Amanual:\s*\S", re.S)


def _unescape_gfm(s: str) -> str:
    """Undo GFM table escaping so a clause's command is the command the author meant.

    A `Verification` cell lives INSIDE a GFM table, so a piped command is necessarily written
    `\\|`. Executing the raw cell runs a truncated command that means something else — risk
    R9, which fired on plan-052's own first control before this rule existed.
    """
    return s.replace("\\|", "|").replace("\\\\", "\\")


def _verification_clause_ok(cell: str) -> bool:
    """True when `cell` is in the REQ-DATA-070 grammar (either form)."""
    c = _unescape_gfm(cell).strip()
    return bool(_MANUAL_RE.match(c) or _CLAUSE_RE.search(c))


def _norm_cell(s: str) -> str:
    """A cell is empty if it holds nothing a reader could act on.

    `_tbd_`, `TBD`, `-`, `—`, `n/a` and bare emphasis are placeholders, not content. Treating
    them as filled is how an unfilled table passes a completeness check — the placeholder is
    the tell that the author knew something was missing.
    """
    s = s.strip().strip("*_`").strip()
    return "" if s.lower() in {"", "-", "--", "—", "–", "tbd", "_tbd_", "n/a", "na", "none",
                               "?", "todo"} else s


#: The measured-literal shape: a bare number adjacent to a corpus-measurement noun. Kept
#: deliberately NARROW — the wide form is what EXP-005 measured at 39 false positives.
_MEASURED_LITERAL = re.compile(
    r"(?<![\w./-])(?P<n>\d{2,5})\s+(?P<noun>files_checked|plan dirs|report-only findings"
    r"|review files|unparsed constructs|corpus files)\b", re.I)

_GATE_HEADING = re.compile(r"^### +(?P<name>.*?\bgate\b.*?)\s*$", re.I)
_GATE_FIELD_RE = re.compile(
    r"^\s*[-*] +\*{0,2}(?P<k>Type|Approvers|Condition|Test|Blocks|Instructions)\*{0,2}"
    r"\s*:\s*(?P<v>.*)$", re.I)


def _gate_completeness(text: str) -> list[str]:
    """Fire only when ALL THREE of Type/Condition/Test are absent from a gate block."""
    body = section_body(text, "Gates")
    if body is None:
        return []
    out, cur, fields = [], None, {}

    def flush() -> None:
        if cur is None:
            return
        if not ({"type", "condition", "test"} & set(fields)):
            out.append(f"gate {cur!r} declares none of `Type`, `Condition` or `Test` — it is a "
                       f"heading with no content, which every other gate check certifies clean")

    for line in body.split("\n"):
        h = _GATE_HEADING.match(line)
        if h:
            flush()
            cur, fields = h.group("name").strip(), {}
            continue
        if line.startswith("#"):
            flush()
            cur, fields = None, {}
            continue
        if cur is None:
            continue
        f = _GATE_FIELD_RE.match(line)
        if f and _norm_cell(f.group("v")):
            fields[f.group("k").lower()] = f.group("v").strip()
    flush()
    return out


def _rel(p: Path, root: Path) -> str:
    """Repo-relative when possible; an explicit --path outside the root stays absolute."""
    try:
        return str(p.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(p)


# --- walking ------------------------------------------------------------------------


def select(schema: dict, root: Path, use_exclude: bool = True,
           extra_exclude: list[str] | None = None) -> list[Path]:
    hits: set[Path] = set()
    for g in schema["paths"]:
        hits.update(p for p in root.glob(g) if p.is_file())
    # `--exclude` (REQ-DATA-059) is applied UNCONDITIONALLY, including under `--no-exclude`.
    # The two are different kinds of thing: the schema's own `exclude` list is a carve-out that
    # `--no-exclude` deliberately defeats as a positive control, whereas a caller-supplied
    # `--exclude` is the caller saying "this measurement is not about these files". A positive
    # control that silently re-admitted the plan doing the measuring would reintroduce exactly
    # the self-reference `--exclude` exists to remove.
    for g in (extra_exclude or []):
        hits = {p for p in hits
                if not fnmatch.fnmatch(str(p.relative_to(root)), g)
                and not fnmatch.fnmatch(str(p.relative_to(root)), g.rstrip("/*") + "/*")}
    if use_exclude:
        for g in schema.get("exclude", []):
            hits = {p for p in hits
                    if not fnmatch.fnmatch(str(p.relative_to(root)), g)
                    and not fnmatch.fnmatch(str(p.relative_to(root)), g.rstrip("/*") + "/*")}
    return sorted(hits)


def lint(root: Path, only_type: str | None, only_paths: list[Path] | None,
         use_exclude: bool = True, extra_exclude: list[str] | None = None) -> dict:
    """Lint the repo, or an explicit file set.

    `--path` is an **explicit override**, not a filter over the glob-selected set: a caller
    naming a file means "lint this file", and that must work for a path the type's globs do
    not select — a committed fixture under `tests/fixtures/doclint/<type>/` lives deliberately
    outside `docs/plans/**` so the engine does not lint its own test corpus. Without the
    override the fixture test would silently check nothing and pass, which is the exact
    vacuous-green class this plan exists to close.

    With `--path` and no `--type`, a file is linted against every schema whose globs select
    it (so an ordinary on-edit call still routes by path). With `--type`, it is linted against
    that schema regardless of the globs.
    """
    findings, checked = [], 0
    for schema in load_schemas(only_type):
        if only_paths is not None:
            if only_type:
                files = sorted({p for p in only_paths if p.is_file()})
            else:
                selected = {f.resolve() for f in select(schema, root, use_exclude, extra_exclude)}
                files = sorted({p for p in only_paths if p.resolve() in selected})
        else:
            files = select(schema, root, use_exclude, extra_exclude)
        for f in files:
            checked += 1
            text = f.read_text(encoding="utf-8", errors="replace")
            status = bundle_status(f)
            # REQ-DATA-053: `promote` is a per-schema opt-out from STATUS_SEVERITY, and it
            # bypasses the map in BOTH directions — a `W` check on a non-promoting schema
            # stays `W` at `review` (never promoted to `E`) AND at `complete` (never demoted
            # to `R`). Two declarations — this module's `plan-relations` banner and
            # `document_types/plan-relations.toml` — asserted promotion was off for that kind
            # for a whole plan cycle while line 565 applied the map unconditionally; plan-049
            # D-9 measured the same fixture at `executing` -> `R` exit 0 and at `review` ->
            # `E` exit 1. Default is `True`, so every existing schema is unaffected.
            # REQ-DATA-072 (#208): FAIL CLOSED on a status that is PRESENT and UNRECOGNISED.
            #
            # TWO BRANCHES, NOT ONE `.get(status or "", {})` LOOKUP. That single lookup
            # collapsed two different facts into one signal -- "this document is not in a plan
            # bundle" (status is None) and "this bundle claims a status nobody recognises" --
            # and handed BOTH the empty map, which is the most PERMISSIVE setting available.
            # So inventing a status silently DISABLED the promotion the linter relies on at
            # `review`. Fail-open on an unknown input is the wrong default for a gate. Same
            # conflation as `not-selected` vs `no-such-path` (#181) and `resume-scan`'s
            # `found` (#207); same remedy -- distinguish the two and branch on the state.
            #
            # THE SCOPE IS "PRESENT AND UNRECOGNISED", NEVER "ABSENT OR UNRECOGNISED", and the
            # narrowness IS the requirement rather than a weaker compromise. A NULL status is
            # the ordinary state of a great many documents that were never part of a plan
            # bundle -- `skills/**` most of all, whose severity table `document_types/
            # skill.toml` calibrated AGAINST the empty map in as many words. The broad form
            # was measured reddening 31 documents plus this repository's own FAST tier, and a
            # fail-closed rule that reddens the tree is a rule that gets reverted.
            if status is None or status == "":
                status_map = {}                       # not in a bundle: UNCHANGED
            else:
                status_map = STATUS_SEVERITY.get(status, _UNRECOGNISED_STATUS_SEVERITY)
            for chk in schema.get("checks", []):
                # REQ-DATA-058: a check may declare the bundle statuses it APPLIES TO. This is
                # orthogonal to `STATUS_SEVERITY`, which changes a finding's severity — this
                # decides whether the check runs at all.
                #
                # The distinction matters for PRODUCER-VERSION rules: a check asserting that a
                # generated document carries something the CURRENT producer emits will fire on
                # every document an older producer wrote, forever, at whatever severity. That
                # is a constant, and a constant carries zero information. Demoting it to `R`
                # does not fix that — it just makes the noise quieter.
                applies = chk.get("statuses")
                if applies is not None and (status or "") not in applies:
                    continue
                # REQ-DATA-053, generalised to the CHECK level (plan-049 Issue 5.2). A schema
                # may opt out wholesale, and an individual check may opt out on its own — a
                # schema like `plan` carries checks that SHOULD promote (`required-sections`
                # becoming an error at `review` is the intake gate) alongside checks that must
                # not (a HINT promoted to `E` hard-fails intake on advice). Check-level wins;
                # absent, the schema's value; absent, `True`.
                promote = chk.get("promote", schema.get("promote", True))
                mapping = status_map if promote else {}
                # REQ-DATA-043 is scoped to THE DOCUMENT, not the run. A targeted check of
                # one plan answers "is this plan sound?", so an unreadable plan must exit 2
                # (INCONCLUSIVE) — that is SC4. A CORPUS SWEEP answers "what is the state?",
                # and aborting the whole sweep at the first of 24 unreadable plans would
                # report nothing about the other 47. So the sweep degrades per file to a
                # report-only finding and keeps going.
                try:
                    details = run_check(chk, text, schema, path=f)
                except Inconclusive as exc:
                    if only_paths is not None:
                        raise
                    findings.append({
                        "path": _rel(f, root), "type": schema["type"],
                        "check": f'{chk["id"]}-inconclusive',
                        "severity": REPORT, "declared_severity": REPORT,
                        "bundle_status": status, "detail": str(exc),
                    })
                    continue
                for detail in details:
                    declared = chk.get("severity", ERROR)
                    findings.append({
                        "path": _rel(f, root), "type": schema["type"],
                        "check": chk["id"],
                        "severity": mapping.get(declared, declared),
                        "declared_severity": declared,
                        "bundle_status": status,
                        "detail": detail,
                    })
    errors = sum(1 for x in findings if x["severity"] == ERROR)
    warnings = sum(1 for x in findings if x["severity"] == WARN)
    reported = sum(1 for x in findings if x["severity"] == REPORT)
    return {
        "verdict": "FAIL" if errors else "PASS",
        "files_checked": checked, "errors": errors,
        "warnings": warnings, "report_only": reported, "findings": findings,
    }


# --- classify: the PREFLIGHT (REQ-DATA-061 / #181) -----------------------------------


CLASS_SELECTED = "selected"
CLASS_EMPTY = "empty"
CLASS_NOT_SELECTED = "not-selected"
CLASS_NO_SUCH_PATH = "no-such-path"


def classify(root: Path, target: Path, only_type: str | None = None,
             use_exclude: bool = True, extra_exclude: list[str] | None = None) -> dict:
    """Decide whether linting `target` is MEANINGFUL AT ALL, before any lint runs.

    Returns `{"class", "path", "root", "selected_by", "reason"}`. The class is one of
    `selected` | `empty` | `not-selected` | `no-such-path`, and the MODE's exit contract is
    0 = lintable (`selected`, `empty`), 1 = not lintable, 2 = could not run.

    WHY A PREFLIGHT AND NOT A CHANGE TO THE LINT
    --------------------------------------------
    `--path` on a real-but-unselected file and `--path` on a NONEXISTENT file both return
    `files_checked: 0, verdict: PASS`, exit 0 — BYTE-IDENTICAL (EXP-003). Three states, one
    verdict. Three earlier scopes each tried to fix that inside the lint and each was refuted
    by measurement, all three for the same structural reason: they mutated the reporting of
    the component under test, and a shipped assertion pinning that reporting caught them. A
    general `files_checked == 0` form breaks `test_doc_lint.py`'s SC42; a `--path`-keyed-always
    form breaks its SC17 block, which pins an unselected `--path` to `PASS`/rc 0 AND identical
    to a nonexistent path. Stepping one layer upstream removes the collision surface instead of
    negotiating with it: SC17 and SC42 remain LITERALLY TRUE, because the behaviour they
    characterise is not modified.

    `empty` IS ON THE LINTABLE SIDE, DELIBERATELY
    ---------------------------------------------
    A selected-but-empty `plan.md` FAILS its schema and the lint already says so loudly
    (measured: 6 `E` findings, exit 1). Skipping it would manufacture a new silent green
    inside the fix for a silent green. It stays a distinguishable *class* because the
    diagnostic value is real; it does not get skip semantics.

    CALLERS BRANCH ON `class`, NEVER ON THE EXIT CODE ALONE
    -------------------------------------------------------
    The two non-lintable classes are different facts — a caller naming a file that does not
    exist is a caller BUG, while an unselected path is an ordinary skip. Collapsing them
    reinstates #181's conflation one layer up.

    `not-selected` MEANS *NOT SELECTED BY PATH ROUTING*
    ---------------------------------------------------
    A `--type`-forced lint is unaffected: `plan_manager.py` deliberately re-lints a bundle's
    `plan.md` with the type FORCED so the plan document stays checkable wherever the bundle
    lives. A path this returns `not-selected` for IS lintable by that route.
    """
    if not target.exists() or not target.is_file():
        return {
            "class": CLASS_NO_SUCH_PATH,
            "path": str(target), "root": str(root), "selected_by": [],
            "reason": "the path does not exist (or is not a file). This is a CALLER BUG, "
                      "not an ordinary skip — it is reported separately from `not-selected` "
                      "precisely because the lint reports the two identically.",
        }

    resolved = target.resolve()
    selected_by = [
        schema["type"] for schema in load_schemas(only_type)
        if resolved in {f.resolve()
                        for f in select(schema, root, use_exclude, extra_exclude)}
    ]

    if not selected_by:
        return {
            "class": CLASS_NOT_SELECTED,
            "path": str(target), "root": str(root), "selected_by": [],
            "reason": f"no document type's path globs select this path under root {root}. "
                      "Note this means NOT SELECTED BY PATH ROUTING: a `--type`-forced lint "
                      "is unaffected.",
        }

    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise Inconclusive(f"could not read {target}: {exc}") from exc

    if not content.strip():
        return {
            "class": CLASS_EMPTY,
            "path": str(target), "root": str(root), "selected_by": selected_by,
            "reason": "selected, but the document is empty. This is on the LINTABLE side: an "
                      "empty document FAILS its schema and the lint says so loudly. Skipping "
                      "it would manufacture a new silent green.",
        }

    return {
        "class": CLASS_SELECTED,
        "path": str(target), "root": str(root), "selected_by": selected_by,
        "reason": f"selected by {', '.join(selected_by)}",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--type")
    ap.add_argument("--path", action="append", type=Path)
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    ap.add_argument("--show-report-only", action="store_true",
                    help="Print R-severity findings from `complete` bundles too.")
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                    help="Exclude paths matching GLOB (repo-relative), on top of each "
                         "schema's own carve-outs. Repeatable. THE SELF-EXCLUSION LEVER "
                         "(#135): a plan measuring the corpus must not count itself, or its "
                         "own measured literals go stale the moment it edits them.")
    ap.add_argument("--no-exclude", action="store_true",
                    help="POSITIVE CONTROL: ignore every carve-out glob")
    ap.add_argument("--classify", action="store_true",
                    help="PREFLIGHT MODE (REQ-DATA-061): do not lint. Report whether linting "
                         "the given --path is meaningful at all, as a `class` of selected | "
                         "empty | not-selected | no-such-path. THIS MODE HAS ITS OWN EXIT "
                         "CONTRACT: 0 = lintable (selected, empty), 1 = not lintable, 2 = "
                         "could not run. Branch on the CLASS, never on the exit code alone.")
    a = ap.parse_args()

    if a.classify:
        if not a.path or len(a.path) != 1:
            # A harness failure, not a verdict: with no single subject there is nothing to
            # classify, and answering either way would be an invention.
            out = {"class": None, "reason": "`--classify` requires exactly one `--path`",
                   "path": None, "root": str(a.root), "selected_by": []}
            print(json.dumps(out, indent=1) if a.json
                  else f"INCONCLUSIVE: {out['reason']}", file=sys.stdout)
            return 2
        try:
            res = classify(a.root, a.path[0], a.type,
                           use_exclude=not a.no_exclude, extra_exclude=a.exclude)
        except Inconclusive as e:
            out = {"class": None, "reason": str(e), "path": str(a.path[0]),
                   "root": str(a.root), "selected_by": []}
            print(json.dumps(out, indent=1) if a.json
                  else f"INCONCLUSIVE: {e}", file=sys.stdout)
            return 2
        if a.json:
            print(json.dumps(res, indent=1))
        else:
            print(f"{res['class']}: {res['path']} — {res['reason']}")
        # The CLASSIFY mode's exit contract. It is NOT the lint's: the same executable now
        # carries two vocabularies keyed by mode (REQ-DATA-024 as amended by plan-050).
        return 0 if res["class"] in (CLASS_SELECTED, CLASS_EMPTY) else 1

    try:
        res = lint(a.root, a.type, a.path, use_exclude=not a.no_exclude,
                   extra_exclude=a.exclude)
    except Inconclusive as e:
        out = {"verdict": "INCONCLUSIVE", "reason": str(e),
               "files_checked": 0, "errors": 0, "warnings": 0, "findings": []}
        print(json.dumps(out, indent=1) if a.json else f"INCONCLUSIVE: {e}", file=sys.stdout)
        return 2
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        for x in res["findings"]:
            if x["severity"] == REPORT and not a.show_report_only:
                continue
            print(f"{x['severity']} {x['path']}: [{x['check']}] {x['detail']}")
        print(f"{res['verdict']}: {res['files_checked']} file(s), "
              f"{res['errors']} error(s), {res['warnings']} warning(s), "
              f"{res['report_only']} report-only")
    # The whole point of the file: a non-zero exit on an error-severity finding.
    return 1 if res["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
