#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8.1"]
# ///
"""Remediation-pair candidate extractor over yf-plan / yf-research bundles.

METHOD CONSTRAINT (from plan.yaml method_notes):

    Remediation pairs are an INFERENCE, not a record. Nothing in a bundle
    declares "this fixes plan-031". This tool proposes CANDIDATES from
    textual / temporal / artifact / git / bead signals. Each candidate MUST be
    confirmed by a human against BOTH bundles before it can carry a finding.

Accordingly this tool NEVER emits a "confirmed" verdict and never collapses
evidence into an opaque score. Every candidate row carries the verbatim quotes
(with file:line), commit subjects, and bead edges that produced it.

Subcommands:
    inventory  enumerate the bundles found per repo (verifies the 83 count)
    pairs      emit candidate remediation pairs with per-signal evidence
    bundle     dump the parsed signal set for one bundle (debugging / drilldown)

All subcommands support --json / --markdown and --out <path>.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import click

# --------------------------------------------------------------------------
# Corpus definition (plan.yaml `corpus.repos`)
# --------------------------------------------------------------------------

DEFAULT_REPOS: dict[str, str] = {
    "yoshiko-flow": "~/workspace/dixson3/yoshiko-flow",
    "d3-pxe": "~/workspace/dixson3/d3-pxe",
    "pybridge": "~/workspace/evri/pybridge",
    "evri_py": "~/workspace/evri/evri_py",  # underscore, NOT evri-py
    "emacs.d": "~/_dotfiles/emacs.d",
}

# plan.yaml corpus expectation, for the inventory reconciliation report.
EXPECTED_PLANS: dict[str, int] = {
    "yoshiko-flow": 43,
    "d3-pxe": 16,
    "pybridge": 11,
    "evri_py": 9,
    "emacs.d": 4,
}
EXPECTED_RESEARCH: dict[str, int] = {"yoshiko-flow": 3, "pybridge": 1}

SKIP_DIR_PARTS = {".git", ".worktrees", "node_modules", ".venv", "target", ".beads"}

# Paths rooted at these live INSIDE a bundle; every bundle has them, so they are
# boilerplate, not artifact overlap.
BUNDLE_INTERNAL_DIRS = {"reviews", "references", "findings", "diagrams", "assets", "decisions"}

# Bundle files worth scanning. Missing files are simply absent — never fatal.
BUNDLE_TEXT_GLOBS = [
    "plan.md",
    "index.md",
    "README.md",  # pre-OKF vintage
    "log.md",
    "context.md",
    "upstream-triage.md",
    "reviews/*.md",
    "findings/*.md",
    "decisions/*.md",
    "references/*.md",  # inlined upstream issue bodies — quoted, not the plan's own voice
    "*.md",  # catch-alls like REDEPLOY-HANDOFF.md
]

# --------------------------------------------------------------------------
# Signal vocabulary
# --------------------------------------------------------------------------

PLAN_ID_RE = re.compile(r"\bplan-(\d{3})\b")
RESEARCH_ID_RE = re.compile(r"\bresearch[ -](\d{3})\b", re.I)
ISSUE_RE = re.compile(r"(?<![\w/])#(\d{1,5})\b")
REQ_RE = re.compile(r"\bREQ-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
BEAD_RE = re.compile(r"\b[a-z][a-z0-9]*-mol-[a-z0-9]{3}(?:\.\d+)*\b")
# Paths: backticked or bare tokens containing a slash and a file-ish suffix.
PATH_RE = re.compile(r"\b((?:[\w.@+-]+/){1,6}[\w.@+-]+\.[A-Za-z0-9]{1,5})\b")

REMEDIATION_TERMS = [
    "fix", "fixes", "fixed", "fixing", "hotfix",
    "correct", "corrects", "corrected", "correction",
    "revert", "reverts", "reverted",
    "stale", "staleness", "blind spot", "blind-spot",
    "defect", "bug", "buggy",
    "regress", "regression", "regressed",
    "broke", "broken", "breaks",
    "wrong", "incorrect", "mistake", "mistaken", "error",
    "missed", "miss", "oversight", "gap", "hole", "omission", "omitted",
    "supersede", "supersedes", "superseded", "supersedes",
    "retract", "retracted", "refute", "refuted", "refutes",
    "rework", "redo", "undo", "amend", "amended", "amendment",
    "obsolete", "retire", "retired", "retires",
    "failed", "failure", "false", "wrongly", "silently",
    "did not", "does not", "never ran", "no-op",
    "overstate", "overstated", "over-reported", "unverified",
    "should have", "left behind", "residue", "leftover", "cleanup",
    "follow-up", "follow up", "followup", "deferred",
]
# longest-first so "blind spot" wins over "spot"
REMEDIATION_RE = re.compile(
    r"(?<![\w-])(" + "|".join(re.escape(t) for t in sorted(REMEDIATION_TERMS, key=len, reverse=True)) + r")(?![\w-])",
    re.I,
)

SPLIT_TERMS_RE = re.compile(r"(?<![\w-])(split from|split out|carved out|descoped|deferred to)(?![\w-])", re.I)

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def die(msg: str, code: int = 2) -> None:
    click.echo(f"error: {msg}", err=True)
    sys.exit(code)


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 60) -> tuple[int, str, str]:
    """Run a command, never hang, never raise. Returns (rc, stdout, stderr)."""
    try:
        p = subprocess.run(
            cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True,
            timeout=timeout, stdin=subprocess.DEVNULL,
        )
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", f"{cmd[0]}: not found on PATH"
    except subprocess.TimeoutExpired:
        return 124, "", f"{' '.join(cmd[:3])}: timed out after {timeout}s"
    except OSError as exc:  # pragma: no cover
        return 1, "", str(exc)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Deliberately minimal YAML-ish frontmatter reader (flat scalars only)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#") or line.startswith(" "):
            continue
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip().strip("'\"")
    return out


def sentences(line: str) -> list[str]:
    """Rough sentence split; a markdown line is usually already short enough."""
    parts = re.split(r"(?<=[.!?])\s+", line.strip())
    return [p for p in parts if p]


# --------------------------------------------------------------------------
# Bundle model
# --------------------------------------------------------------------------

@dataclass
class Mention:
    target: str          # "plan-031" or "research-003"
    kind: str            # plan | research
    file: str            # repo-relative path
    line: int
    quote: str
    terms: list[str]
    context: str         # remediation | split | mention

    def as_dict(self) -> dict:
        return {
            "target": self.target, "kind": self.kind,
            "location": f"{self.file}:{self.line}",
            "quote": self.quote, "terms": self.terms, "context": self.context,
        }


@dataclass
class Bundle:
    repo: str
    repo_root: Path
    path: Path
    bundle_id: str
    kind: str            # plan | research
    number: int | None
    scope: str           # "docs" or "Incubator/<slug>"
    files: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    layout: str = "unknown"      # okf (index.md+log.md) | legacy (README.md) | partial
    title: str = ""
    status: str = ""
    created: str = ""
    epic: str = ""
    mentions: list[Mention] = field(default_factory=list)
    issues: set[str] = field(default_factory=set)
    reqs: set[str] = field(default_factory=set)
    beads: set[str] = field(default_factory=set)
    paths: set[str] = field(default_factory=set)
    review_passes: int = 0
    parse_errors: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.repo}/{self.bundle_id}"

    def as_inventory_dict(self) -> dict:
        return {
            "repo": self.repo,
            "bundle_id": self.bundle_id,
            "kind": self.kind,
            "number": self.number,
            "scope": self.scope,
            "path": str(self.path),
            "layout": self.layout,
            "status": self.status,
            "created": self.created,
            "epic": self.epic,
            "title": self.title,
            "files": self.files,
            "missing_expected": self.missing,
            "review_passes": self.review_passes,
            "parse_errors": self.parse_errors,
        }


def _iter_bundle_files(bundle_dir: Path) -> list[Path]:
    seen: dict[Path, None] = {}
    for pattern in BUNDLE_TEXT_GLOBS:
        try:
            for p in sorted(bundle_dir.glob(pattern)):
                if p.is_file() and p.suffix == ".md":
                    seen.setdefault(p, None)
        except OSError:
            continue
    return list(seen)


def _classify_layout(names: set[str]) -> str:
    if "index.md" in names and "log.md" in names:
        return "okf"
    if "README.md" in names and "log.md" in names:
        return "transitional"
    if "README.md" in names:
        return "legacy"
    return "partial"


def parse_bundle(repo: str, repo_root: Path, bundle_dir: Path, kind: str) -> Bundle:
    name = bundle_dir.name
    if kind == "plan":
        m = re.match(r"plan-(\d+)", name)
    else:
        m = re.match(r"(\d+)", name)
    number = int(m.group(1)) if m else None

    rel = bundle_dir.relative_to(repo_root)
    parts = rel.parts
    scope = f"Incubator/{parts[1]}" if parts and parts[0] == "Incubator" and len(parts) > 1 else "docs"

    b = Bundle(repo=repo, repo_root=repo_root, path=bundle_dir, bundle_id=name,
               kind=kind, number=number, scope=scope)

    files = _iter_bundle_files(bundle_dir)
    names = {p.name for p in files}
    b.files = sorted(str(p.relative_to(bundle_dir)) for p in files)
    b.layout = _classify_layout(names)
    for expected in ("plan.md", "context.md"):
        if kind == "plan" and expected not in names:
            b.missing.append(expected)
    if kind == "plan" and not (names & {"index.md", "README.md"}):
        b.missing.append("index.md|README.md")
    if kind == "plan" and "log.md" not in names:
        b.missing.append("log.md (in-plan.md phase log vintage)")
    try:
        b.review_passes = len(list((bundle_dir / "reviews").glob("*.md")))
    except OSError:
        b.review_passes = 0

    self_re = re.compile(rf"\b{re.escape(name.split('-james-')[0])}\b") if "-james-" in name else None

    for p in files:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            b.parse_errors.append(f"{p.name}: {exc}")
            continue
        relf = str(p.relative_to(repo_root))

        if p.name in ("plan.md", "index.md", "README.md") and not b.title:
            fm = parse_frontmatter(text)
            b.status = b.status or fm.get("status", "")
            b.created = b.created or fm.get("created", "")
            b.epic = b.epic or fm.get("epic", "")
            for line in text.splitlines():
                if line.startswith("# "):
                    b.title = line[2:].strip()
                    break
        if p.name == "plan.md":
            fm = parse_frontmatter(text)
            b.status = fm.get("status", b.status)
            b.created = fm.get("created", b.created)
            b.epic = fm.get("epic", b.epic)
            # Pre-OKF bundles have no frontmatter — the same fields appear as
            # bold header lines in the plan body.
            for key, attr in (("Status", "status"), ("Created", "created"), ("Epic", "epic")):
                if getattr(b, attr):
                    continue
                mm = re.search(rf"^\*\*{key}:\*\*\s*(.+?)\s*$", text, re.M)
                if mm:
                    setattr(b, attr, mm.group(1).strip("`* "))

        for i, line in enumerate(text.splitlines(), start=1):
            b.issues.update(f"#{m.group(1)}" for m in ISSUE_RE.finditer(line))
            b.reqs.update(m.group(0) for m in REQ_RE.finditer(line))
            b.beads.update(m.group(0) for m in BEAD_RE.finditer(line))
            b.paths.update(m.group(1) for m in PATH_RE.finditer(line))

            if "plan-" not in line and not RESEARCH_ID_RE.search(line):
                continue
            for sent in sentences(line):
                targets: list[tuple[str, str]] = []
                targets += [(f"plan-{m.group(1)}", "plan") for m in PLAN_ID_RE.finditer(sent)]
                targets += [(f"research-{m.group(1)}", "research") for m in RESEARCH_ID_RE.finditer(sent)]
                if not targets:
                    continue
                terms = sorted({t.group(1).lower() for t in REMEDIATION_RE.finditer(sent)})
                split = bool(SPLIT_TERMS_RE.search(sent))
                ctx = "remediation" if terms else ("split" if split else "mention")
                if split and terms:
                    ctx = "remediation+split"
                quote = sent.strip()
                if len(quote) > 400:
                    quote = quote[:397] + "..."
                for tgt, tkind in dict.fromkeys(targets):
                    if self_re and self_re.match(tgt):
                        continue
                    b.mentions.append(Mention(tgt, tkind, relf, i, quote, terms, ctx))
    # de-dup identical mentions
    seen_m: set[tuple] = set()
    uniq: list[Mention] = []
    for m_ in b.mentions:
        k = (m_.target, m_.file, m_.line, m_.quote)
        if k in seen_m:
            continue
        seen_m.add(k)
        uniq.append(m_)
    b.mentions = uniq
    return b


def discover_bundles(repo: str, repo_root: Path) -> tuple[list[Bundle], list[str]]:
    """Find every plan and research bundle under a repo root."""
    warnings: list[str] = []
    if not repo_root.is_dir():
        return [], [f"{repo}: repo root {repo_root} does not exist — skipped"]

    plan_dirs: list[Path] = []
    research_dirs: list[Path] = []
    for dirpath, dirnames, _ in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_PARTS and not d.startswith(".")]
        here = Path(dirpath)
        if here.name == "plans":
            plan_dirs.append(here)
        elif here.name == "research":
            research_dirs.append(here)

    bundles: list[Bundle] = []
    for parent in sorted(plan_dirs):
        for d in sorted(parent.iterdir()):
            if d.is_dir() and re.match(r"plan-\d+", d.name):
                bundles.append(parse_bundle(repo, repo_root, d, "plan"))
    for parent in sorted(research_dirs):
        for d in sorted(parent.iterdir()):
            # Newer research bundles are `NNN-<slug>/`; older vintages are just
            # `<slug>/` (sometimes only a SUMMARY.md). Any subdirectory of a
            # research root counts.
            if d.is_dir():
                bundles.append(parse_bundle(repo, repo_root, d, "research"))

    dupes = defaultdict(list)
    for b in bundles:
        if b.kind == "plan" and b.number is not None:
            dupes[b.number].append(b.bundle_id)
    for num, ids in sorted(dupes.items()):
        if len(ids) > 1:
            warnings.append(f"{repo}: plan number {num:03d} is used by {len(ids)} bundles: {', '.join(ids)}")
    return bundles, warnings


# --------------------------------------------------------------------------
# Git signal
# --------------------------------------------------------------------------

@dataclass
class GitIndex:
    available: bool
    reason: str = ""
    commits: list[dict] = field(default_factory=list)          # sha,date,subject,body,files
    by_plan: dict[str, list[int]] = field(default_factory=dict)  # "plan-041" -> commit idxs

    @staticmethod
    def build(repo_root: Path, max_commits: int = 4000) -> "GitIndex":
        rc, _, err = run(["git", "rev-parse", "--git-dir"], cwd=repo_root, timeout=20)
        if rc != 0:
            return GitIndex(False, f"not a git repo or git unavailable: {err.strip() or rc}")
        SEP = "\x1e"
        FS = "\x1f"
        rc, out, err = run(
            ["git", "log", "--all", f"--max-count={max_commits}", "--date=short",
             "--name-only", f"--pretty=format:{SEP}%H{FS}%ad{FS}%s{FS}%b{FS}"],
            cwd=repo_root, timeout=180,
        )
        if rc != 0:
            return GitIndex(False, f"git log failed: {err.strip() or rc}")
        idx = GitIndex(True)
        for chunk in out.split(SEP):
            if not chunk.strip():
                continue
            fields = chunk.split(FS)
            if len(fields) < 5:
                continue
            sha, date, subject, body, tail = fields[0], fields[1], fields[2], fields[3], fields[4]
            files = [ln.strip() for ln in tail.splitlines() if ln.strip()]
            msg = f"{subject}\n{body}"
            kind = []
            if re.match(r"\s*revert\b", subject, re.I) or "This reverts commit" in body:
                kind.append("revert")
            if re.match(r"\s*fix(\(|:|\b)", subject, re.I) or re.search(r"\bfix(es|ed)?\b", subject, re.I):
                kind.append("fix")
            rec = {"sha": sha[:9], "date": date, "subject": subject.strip(),
                   "files": files, "kind": kind}
            i = len(idx.commits)
            idx.commits.append(rec)
            for key in {f"plan-{m.group(1)}" for m in PLAN_ID_RE.finditer(msg)}:
                idx.by_plan.setdefault(key, []).append(i)
        return idx

    def files_for(self, plan_key: str) -> set[str]:
        out: set[str] = set()
        for i in self.by_plan.get(plan_key, []):
            out.update(self.commits[i]["files"])
        return out


# --------------------------------------------------------------------------
# Beads signal
# --------------------------------------------------------------------------

@dataclass
class BeadIndex:
    available: bool
    reason: str = ""
    by_id: dict[str, dict] = field(default_factory=dict)
    edges: list[tuple[str, str, str]] = field(default_factory=list)  # (src, dst, type)

    @staticmethod
    def build(repo_root: Path) -> "BeadIndex":
        if not (repo_root / ".beads").is_dir():
            return BeadIndex(False, "no .beads/ directory in repo — bead signals unavailable")
        rc, out, err = run(["bd", "list", "--all", "--json"], cwd=repo_root, timeout=120)
        if rc != 0 or not out.strip():
            return BeadIndex(False, f"`bd list --all --json` failed (rc={rc}): {err.strip()[:200] or 'empty output'}")
        try:
            data = json.loads(out)
        except json.JSONDecodeError as exc:
            return BeadIndex(False, f"bd JSON unparseable: {exc}")
        if isinstance(data, dict):
            if "error" in data:  # bd can return error JSON with exit 0
                return BeadIndex(False, f"bd returned error JSON: {str(data['error'])[:200]}")
            data = data.get("issues", [])
        if not isinstance(data, list):
            return BeadIndex(False, "unexpected bd JSON shape")
        idx = BeadIndex(True)
        for item in data:
            if not isinstance(item, dict) or "id" not in item:
                continue
            idx.by_id[item["id"]] = item
            for dep in item.get("dependencies") or []:
                idx.edges.append((dep.get("issue_id", item["id"]),
                                  dep.get("depends_on_id", ""),
                                  dep.get("type") or dep.get("dep_type") or "?"))
        return idx

    @staticmethod
    def root(bead_id: str) -> str:
        return bead_id.split(".")[0]


# --------------------------------------------------------------------------
# Pair construction
# --------------------------------------------------------------------------

@dataclass
class Candidate:
    repo: str
    a: Bundle
    b: Bundle
    origins: set[str] = field(default_factory=set)
    textual: list[Mention] = field(default_factory=list)
    shared_issues: list[str] = field(default_factory=list)
    shared_reqs: list[str] = field(default_factory=list)
    shared_paths: list[str] = field(default_factory=list)
    git_commits: list[dict] = field(default_factory=list)
    git_shared_files: list[str] = field(default_factory=list)
    bead_edges: list[dict] = field(default_factory=list)
    bead_note: str = ""
    ordering_basis: str = "number"

    @property
    def remediation_quotes(self) -> list[Mention]:
        return [m for m in self.textual if m.context.startswith("remediation")]

    def signal_names(self) -> list[str]:
        s = []
        if self.remediation_quotes:
            s.append("textual:remediation")
        elif self.textual:
            s.append("textual:mention")
        if any(m.context.endswith("split") for m in self.textual):
            s.append("textual:split")
        s.append("temporal:ordered")
        if self.shared_issues:
            s.append("artifact:issue")
        if self.shared_reqs:
            s.append("artifact:req")
        if self.shared_paths:
            s.append("artifact:path")
        if any("revert" in c["kind"] for c in self.git_commits):
            s.append("git:revert")
        if any("fix" in c["kind"] for c in self.git_commits):
            s.append("git:fix")
        if self.git_shared_files:
            s.append("git:file-churn-overlap")
        if self.bead_edges:
            s.append("beads:discovered-from")
        return s

    def as_dict(self) -> dict:
        return {
            "verdict": "candidate",  # NEVER "confirmed" — see module docstring
            "confirmation_required": "read BOTH bundles before this pair may carry a finding",
            "repo": self.repo,
            "earlier_plan": {
                "id": self.a.bundle_id, "number": self.a.number, "kind": self.a.kind,
                "scope": self.a.scope, "created": self.a.created, "status": self.a.status,
                "title": self.a.title, "path": str(self.a.path),
            },
            "later_plan": {
                "id": self.b.bundle_id, "number": self.b.number, "kind": self.b.kind,
                "scope": self.b.scope, "created": self.b.created, "status": self.b.status,
                "title": self.b.title, "path": str(self.b.path),
            },
            "pair_origin": sorted(self.origins),
            "signals": self.signal_names(),
            "evidence": {
                "textual": [m.as_dict() for m in self.textual],
                "temporal": {
                    "earlier_number": self.a.number, "later_number": self.b.number,
                    "earlier_created": self.a.created, "later_created": self.b.created,
                    "ordering_basis": self.ordering_basis,
                    "ordering_basis_note": "same-kind pairs order by bundle number within the repo; "
                                           "cross-kind (research->plan) pairs order by frontmatter `created`",
                },
                "artifact_overlap": {
                    "shared_upstream_issues": self.shared_issues,
                    "shared_req_ids": self.shared_reqs,
                    "shared_paths": self.shared_paths,
                },
                "git": {
                    "commits": self.git_commits,
                    "shared_touched_files": self.git_shared_files,
                },
                "beads": {
                    "discovered_from_edges": self.bead_edges,
                    "note": self.bead_note,
                },
            },
        }


def _epic_ownership(bundles: list[Bundle]) -> dict[str, list[Bundle]]:
    """Map a bead-epic root -> the bundle(s) that own it.

    Only ~1 in 4 plan bundles carries an `epic:` frontmatter key (it is a newer
    OKF field), so ownership falls back to text mentions. A root mentioned by
    many bundles is a cross-reference table (e.g. a reconciliation plan listing
    every epic), not ownership, so those are dropped; among a small mention set
    the earliest-numbered bundle is taken as the owner.
    """
    owner: dict[str, list[Bundle]] = defaultdict(list)
    mentions: dict[str, list[Bundle]] = defaultdict(list)
    for b in bundles:
        if b.epic:
            owner[BeadIndex.root(b.epic)].append(b)
        for bead in b.beads:
            mentions[BeadIndex.root(bead)].append(b)
    for root, bs in mentions.items():
        if root in owner or len(bs) > 5:
            continue
        owner[root] = [min(bs, key=lambda x: (x.number is None, x.number or 0))]
    return owner


def build_candidates(
    repo: str,
    bundles: list[Bundle],
    git: GitIndex,
    beads: BeadIndex,
    *,
    include_mentions: bool,
    max_paths: int,
) -> list[Candidate]:
    by_num: dict[tuple[str, int], list[Bundle]] = defaultdict(list)
    for b in bundles:
        if b.number is not None:
            by_num[(b.kind, b.number)].append(b)

    pairs: dict[tuple[str, str], Candidate] = {}

    def ordering(a: Bundle, b: Bundle) -> str | None:
        """Return the basis on which A precedes B, or None if it does not.

        Same-kind bundles order by number (numbering is monotonic per kind per
        repo). Cross-kind (research -> plan) has no shared number line, so it
        orders by frontmatter `created` date; absent a date, the pair is
        emitted with the basis flagged as UNVERIFIED so a human can check.
        """
        if a.kind == b.kind:
            if a.number is None or b.number is None:
                return None
            return "number" if a.number < b.number else None
        if a.created and b.created:
            return "created-date" if a.created <= b.created else None
        return "UNVERIFIED (cross-kind, one or both `created` dates missing)"

    def get_pair(a: Bundle, b: Bundle) -> Candidate | None:
        basis = ordering(a, b)
        if basis is None:
            return None
        k = (a.bundle_id, b.bundle_id)
        if k not in pairs:
            pairs[k] = Candidate(repo=repo, a=a, b=b, ordering_basis=basis)
        return pairs[k]

    # --- origin 1: an explicit textual reference from B back to A -------------
    for b in bundles:
        for m in b.mentions:
            tnum = int(m.target.split("-")[-1])
            for a in by_num.get((m.kind, tnum), []):
                if a.bundle_id == b.bundle_id:
                    continue
                c = get_pair(a, b)   # None when A does not precede B
                if c is None:
                    continue
                c.origins.add("textual-reference")
                c.textual.append(m)

    # --- origin 2: both bundles cite the same upstream issue ------------------
    issue_map: dict[str, list[Bundle]] = defaultdict(list)
    for b in bundles:
        for iss in b.issues:
            issue_map[iss].append(b)
    for iss, bs in issue_map.items():
        if len(bs) < 2 or len(bs) > 8:  # a very widely cited issue is not a signal
            continue
        ordered = sorted([x for x in bs if x.number is not None], key=lambda x: (x.kind, x.number))
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                if a.kind != b.kind:
                    continue
                c = get_pair(a, b)
                if c is None:
                    continue
                c.origins.add("shared-upstream-issue")

    # --- origin 3: a discovered-from edge between two plans' bead trees -------
    epic_owner = _epic_ownership(bundles)
    if beads.available:
        for src, dst, typ in beads.edges:
            if typ != "discovered-from":
                continue
            sr, dr = BeadIndex.root(src), BeadIndex.root(dst)
            if sr == dr:
                continue
            # the bead was DISCOVERED FROM dst's work -> dst is the earlier plan
            for a in epic_owner.get(dr, []):
                for b in epic_owner.get(sr, []):
                    c = get_pair(a, b)
                    if c is None:
                        continue
                    c.origins.add("bead-discovered-from")

    # --- enrich every pair with the remaining signals -------------------------
    for c in list(pairs.values()):
        a, b = c.a, c.b
        c.shared_issues = sorted(a.issues & b.issues)
        c.shared_reqs = sorted(a.reqs & b.reqs)
        # Bundle-internal boilerplate (`reviews/pass-1.md`, `references/...`) is
        # present in nearly every bundle and carries no artifact-overlap signal.
        shared_paths = sorted(p for p in (a.paths & b.paths)
                              if p.split("/", 1)[0] not in BUNDLE_INTERNAL_DIRS
                              and not p.startswith("docs/plans/")
                              and not p.startswith("docs/research/"))
        c.shared_paths = shared_paths[:max_paths]
        if len(shared_paths) > max_paths:
            c.shared_paths.append(f"... +{len(shared_paths) - max_paths} more")

        if git.available:
            akey = f"plan-{a.number:03d}" if a.kind == "plan" and a.number is not None else None
            bkey = f"plan-{b.number:03d}" if b.kind == "plan" and b.number is not None else None
            commits: list[dict] = []
            if bkey:
                for i in git.by_plan.get(bkey, []):
                    rec = git.commits[i]
                    interesting = bool(rec["kind"]) or (akey and akey in rec["subject"])
                    if interesting:
                        commits.append({"sha": rec["sha"], "date": rec["date"],
                                        "subject": rec["subject"], "kind": rec["kind"],
                                        "attributed_to": bkey})
            if akey:
                for i in git.by_plan.get(akey, []):
                    rec = git.commits[i]
                    if "revert" in rec["kind"]:
                        commits.append({"sha": rec["sha"], "date": rec["date"],
                                        "subject": rec["subject"], "kind": rec["kind"],
                                        "attributed_to": akey})
            c.git_commits = commits[:25]
            if akey and bkey:
                shared = sorted(git.files_for(akey) & git.files_for(bkey))
                shared = [f for f in shared if not f.startswith("docs/plans/")]
                c.git_shared_files = shared[:max_paths]
                if len(shared) > max_paths:
                    c.git_shared_files.append(f"... +{len(shared) - max_paths} more")

        if not beads.available:
            c.bead_note = beads.reason
        else:
            aroots = {r for r, owners in epic_owner.items() if any(o.bundle_id == a.bundle_id for o in owners)}
            broots = {r for r, owners in epic_owner.items() if any(o.bundle_id == b.bundle_id for o in owners)}
            if not aroots or not broots:
                c.bead_note = ("no bead epic could be attributed to one or both bundles "
                               "(no `epic:` frontmatter and no unambiguous bead mention)")
            else:
                found = []
                for src, dst, typ in beads.edges:
                    if typ != "discovered-from":
                        continue
                    sr, dr = BeadIndex.root(src), BeadIndex.root(dst)
                    if (sr in broots and dr in aroots) or (sr in aroots and dr in broots):
                        found.append({"from": src, "to": dst, "type": typ,
                                      "from_status": (beads.by_id.get(src) or {}).get("status", "?"),
                                      "from_title": (beads.by_id.get(src) or {}).get("title", "")[:120]})
                c.bead_edges = found[:25]
                if not found:
                    c.bead_note = "no discovered-from edge between the two epics' bead trees"

    out = list(pairs.values())
    if not include_mentions:
        out = [c for c in out
               if c.remediation_quotes
               or any(m.context.endswith("split") for m in c.textual)
               or c.bead_edges
               or any("revert" in x["kind"] for x in c.git_commits)]
    out.sort(key=lambda c: (c.repo, -(len(c.remediation_quotes)), c.a.number or 0, c.b.number or 0))
    return out


# --------------------------------------------------------------------------
# Output helpers
# --------------------------------------------------------------------------

def emit(payload: str, out: str | None) -> None:
    if out:
        p = Path(out).expanduser()
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(payload, encoding="utf-8")
        except OSError as exc:
            die(f"cannot write --out {p}: {exc}")
        click.echo(f"wrote {p}", err=True)
    else:
        click.echo(payload)


def resolve_repos(repo_opt: tuple[str, ...]) -> dict[str, Path]:
    if not repo_opt:
        chosen = DEFAULT_REPOS
    else:
        chosen = {}
        for r in repo_opt:
            if r in DEFAULT_REPOS:
                chosen[r] = DEFAULT_REPOS[r]
            elif Path(r).expanduser().is_dir():
                chosen[Path(r).expanduser().name] = r
            else:
                die(f"unknown --repo {r!r}; known: {', '.join(DEFAULT_REPOS)} (or an existing path)")
    return {k: Path(v).expanduser() for k, v in chosen.items()}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

@click.group(help=__doc__)
@click.version_option("1.0.0")
def cli() -> None:
    pass


repo_opt = click.option("--repo", multiple=True,
                        help="Restrict to one repo (name from the corpus, or a path). Repeatable. Default: all five.")
out_opt = click.option("--out", default=None, help="Write output to this path instead of stdout.")
fmt_opts = [
    click.option("--json", "as_json", is_flag=True, help="JSON output."),
    click.option("--markdown", "as_md", is_flag=True, help="Markdown output (default)."),
]


def add_fmt(f):
    for o in reversed(fmt_opts):
        f = o(f)
    return f


@cli.command(help="Enumerate the plan/research bundles found per repo (verifies the 83-plan count).")
@repo_opt
@add_fmt
@out_opt
@click.option("--detail", is_flag=True, help="List every bundle, not just per-repo totals.")
def inventory(repo: tuple[str, ...], as_json: bool, as_md: bool, out: str | None, detail: bool) -> None:
    repos = resolve_repos(repo)
    result = {"repos": {}, "warnings": [], "totals": {}}
    all_bundles: list[Bundle] = []
    for name, root in repos.items():
        bundles, warns = discover_bundles(name, root)
        result["warnings"].extend(warns)
        all_bundles.extend(bundles)
        plans = [b for b in bundles if b.kind == "plan"]
        research = [b for b in bundles if b.kind == "research"]
        layouts = defaultdict(int)
        for b in plans:
            layouts[b.layout] += 1
        entry = {
            "root": str(root),
            "exists": root.is_dir(),
            "plans_found": len(plans),
            "plans_expected": EXPECTED_PLANS.get(name),
            "plans_delta": (len(plans) - EXPECTED_PLANS[name]) if name in EXPECTED_PLANS else None,
            "research_found": len(research),
            "research_expected": EXPECTED_RESEARCH.get(name, 0),
            "layouts": dict(layouts),
            "scopes": dict(sorted(defaultdict(int, {s: sum(1 for b in plans if b.scope == s) for s in {b.scope for b in plans}}).items())),
        }
        if detail:
            entry["bundles"] = [b.as_inventory_dict() for b in bundles]
        result["repos"][name] = entry

    tp = sum(r["plans_found"] for r in result["repos"].values())
    te = sum(EXPECTED_PLANS.get(n, 0) for n in result["repos"])
    result["totals"] = {
        "plans_found": tp, "plans_expected": te, "plans_delta": tp - te,
        "research_found": sum(r["research_found"] for r in result["repos"].values()),
        "reconciles_with_plan_yaml": tp == te,
    }

    if as_json:
        emit(json.dumps(result, indent=2), out)
        return

    lines = ["# Bundle inventory", "",
             "| repo | root | plans found | plans expected | delta | research | layouts |",
             "| --- | --- | ---: | ---: | ---: | ---: | --- |"]
    for name, r in result["repos"].items():
        lay = ", ".join(f"{k}={v}" for k, v in sorted(r["layouts"].items())) or "-"
        lines.append(f"| {name} | `{r['root']}` | {r['plans_found']} | "
                     f"{r['plans_expected'] if r['plans_expected'] is not None else '-'} | "
                     f"{r['plans_delta'] if r['plans_delta'] is not None else '-'} | "
                     f"{r['research_found']} | {lay} |")
    t = result["totals"]
    lines += ["", f"**Total plans found: {t['plans_found']}** (plan.yaml expects {t['plans_expected']}; "
                  f"delta {t['plans_delta']:+d}) · research bundles: {t['research_found']}"]
    if result["warnings"]:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in result["warnings"]]
    if detail:
        lines += ["", "## Bundles", "",
                  "| repo | bundle | kind | scope | layout | status | created | epic | reviews | missing |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- |"]
        for name, r in result["repos"].items():
            for b in r.get("bundles", []):
                lines.append(f"| {name} | {b['bundle_id']} | {b['kind']} | {b['scope']} | {b['layout']} | "
                             f"{b['status'] or '-'} | {b['created'] or '-'} | {b['epic'] or '-'} | "
                             f"{b['review_passes']} | {', '.join(b['missing_expected']) or '-'} |")
    emit("\n".join(lines), out)


@cli.command(help="Emit CANDIDATE remediation pairs with a per-signal evidence breakdown. "
                  "Never emits a confirmed verdict — every row must be adjudicated against both bundles.")
@repo_opt
@add_fmt
@out_opt
@click.option("--include-mentions", is_flag=True,
              help="Also emit pairs whose only textual link is a neutral mention (noisier, higher recall).")
@click.option("--no-git", is_flag=True, help="Skip the git-history signal.")
@click.option("--no-beads", is_flag=True, help="Skip the bead-graph signal.")
@click.option("--max-paths", default=15, show_default=True, help="Cap on listed overlapping paths/files per pair.")
@click.option("--limit", default=0, help="Emit at most N pairs (0 = all).")
def pairs(repo: tuple[str, ...], as_json: bool, as_md: bool, out: str | None,
          include_mentions: bool, no_git: bool, no_beads: bool,
          max_paths: int, limit: int) -> None:
    repos = resolve_repos(repo)
    all_rows: list[Candidate] = []
    meta: dict[str, dict] = {}
    warnings: list[str] = []

    for name, root in repos.items():
        bundles, warns = discover_bundles(name, root)
        warnings.extend(warns)
        if not bundles:
            meta[name] = {"bundles": 0, "git": "n/a", "beads": "n/a"}
            continue
        git = GitIndex(False, "skipped (--no-git)") if no_git else GitIndex.build(root)
        beads = BeadIndex(False, "skipped (--no-beads)") if no_beads else BeadIndex.build(root)
        rows = build_candidates(name, bundles, git, beads,
                                include_mentions=include_mentions, max_paths=max_paths)
        all_rows.extend(rows)
        owners = _epic_ownership(bundles)
        df = [(s, d_, t) for (s, d_, t) in beads.edges if t == "discovered-from"] if beads.available else []
        cross = [(s, d_) for (s, d_, _t) in df if BeadIndex.root(s) != BeadIndex.root(d_)]
        both_owned = [(s, d_) for (s, d_) in cross
                      if BeadIndex.root(s) in owners and BeadIndex.root(d_) in owners]
        meta[name] = {
            "bundles": len(bundles),
            "git": "available" if git.available else f"unavailable: {git.reason}",
            "beads": ("available" if beads.available else f"unavailable: {beads.reason}"),
            "bead_stats": ({
                "discovered_from_edges": len(df),
                "cross_epic": len(cross),
                "between_two_plan_epics": len(both_owned),
                "plan_epics_attributed": sum(1 for r in owners),
                "note": "0 `between_two_plan_epics` means the bead graph carries NO plan-to-plan "
                        "remediation signal in this repo — an absence, not a tool failure.",
            } if beads.available else None),
            "candidates": len(rows),
        }

    if limit:
        all_rows = all_rows[:limit]

    payload = {
        "verdict_vocabulary": {
            "candidate": "proposed by signal; NOT a record. Must be confirmed against BOTH bundles.",
            "note": "This tool never emits 'confirmed'. There is no score — only per-signal evidence.",
        },
        "corpus": meta,
        "warnings": warnings,
        "candidate_count": len(all_rows),
        "candidates": [c.as_dict() for c in all_rows],
    }

    if as_json:
        emit(json.dumps(payload, indent=2), out)
        return

    lines = ["# Candidate remediation pairs", "",
             "> **These are CANDIDATES, not records.** Nothing in a bundle declares "
             "\"this fixes plan-031\". Every row below was INFERRED from textual / temporal / "
             "artifact / git / bead signals and MUST be confirmed against BOTH bundles before "
             "it can carry a finding. There is deliberately no score.", ""]
    lines += ["## Corpus & signal availability", "",
              "| repo | bundles | candidates | git signal | bead signal |",
              "| --- | ---: | ---: | --- | --- |"]
    for name, m in meta.items():
        bs = m.get("bead_stats")
        beadcell = m["beads"]
        if bs:
            beadcell += (f" ({bs['discovered_from_edges']} discovered-from, "
                         f"{bs['between_two_plan_epics']} between two plan epics)")
        lines.append(f"| {name} | {m['bundles']} | {m.get('candidates', 0)} | {m['git']} | {beadcell} |")
    if warnings:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in warnings]

    lines += ["", f"## Candidates ({len(all_rows)})", "",
              "| # | repo | earlier (P_a) | later (P_b) | origin | signals | remediation quotes |",
              "| ---: | --- | --- | --- | --- | --- | ---: |"]
    for i, c in enumerate(all_rows, 1):
        lines.append(f"| {i} | {c.repo} | {c.a.bundle_id} | {c.b.bundle_id} | "
                     f"{', '.join(sorted(c.origins))} | {', '.join(c.signal_names())} | "
                     f"{len(c.remediation_quotes)} |")

    lines += ["", "## Evidence detail", ""]
    for i, c in enumerate(all_rows, 1):
        lines += [f"### {i}. {c.repo}: {c.a.bundle_id} -> {c.b.bundle_id} — **candidate**", "",
                  f"- **P_a** `{c.a.bundle_id}` ({c.a.created or 'date?'}, {c.a.status or 'status?'}) — {c.a.title or '(no title)'}",
                  f"- **P_b** `{c.b.bundle_id}` ({c.b.created or 'date?'}, {c.b.status or 'status?'}) — {c.b.title or '(no title)'}",
                  f"- **origin:** {', '.join(sorted(c.origins))}",
                  f"- **signals:** {', '.join(c.signal_names())}", ""]
        if c.textual:
            lines.append("**Textual evidence** (verbatim, with file:line):")
            lines.append("")
            for m in c.textual[:20]:
                lines.append(f"- `{m.file}:{m.line}` [{m.context}"
                             + (f"; terms: {', '.join(m.terms)}" if m.terms else "") + "]")
                lines.append(f"  > {m.quote}")
            if len(c.textual) > 20:
                lines.append(f"- ... +{len(c.textual) - 20} more mentions")
            lines.append("")
        lines.append("**Temporal:** "
                     f"P_a #{c.a.number} ({c.a.created or '?'}) precedes P_b #{c.b.number} "
                     f"({c.b.created or '?'}) — basis: {c.ordering_basis}")
        lines.append("")
        ao = []
        if c.shared_issues:
            ao.append(f"upstream issues: {', '.join(c.shared_issues)}")
        if c.shared_reqs:
            ao.append(f"REQ ids: {', '.join(c.shared_reqs[:20])}")
        if c.shared_paths:
            ao.append(f"paths: {', '.join('`' + p + '`' for p in c.shared_paths)}")
        lines.append("**Artifact overlap:** " + ("; ".join(ao) if ao else "none detected"))
        lines.append("")
        if c.git_commits:
            lines.append("**Git:**")
            lines.append("")
            for gc in c.git_commits:
                kind = f" [{', '.join(gc['kind'])}]" if gc["kind"] else ""
                lines.append(f"- `{gc['sha']}` {gc['date']} ({gc['attributed_to']}){kind} — {gc['subject']}")
            if c.git_shared_files:
                lines.append(f"- shared touched files: {', '.join('`' + f + '`' for f in c.git_shared_files)}")
            lines.append("")
        else:
            lines += ["**Git:** no revert/fix commit correlating the two plan ids", ""]
        if c.bead_edges:
            lines.append("**Beads (`discovered-from`):**")
            lines.append("")
            for e in c.bead_edges:
                lines.append(f"- `{e['from']}` --{e['type']}--> `{e['to']}` [{e['from_status']}] {e['from_title']}")
            lines.append("")
        else:
            lines += [f"**Beads:** {c.bead_note or 'none'}", ""]
        lines.append("**Confirmation required:** read both bundles before this pair carries a finding.")
        lines.append("")
    emit("\n".join(lines), out)


@cli.command(help="Dump the parsed signal set for a single bundle (drilldown / parser debugging).")
@click.argument("bundle_id")
@repo_opt
@add_fmt
@out_opt
def bundle(bundle_id: str, repo: tuple[str, ...], as_json: bool, as_md: bool, out: str | None) -> None:
    repos = resolve_repos(repo)
    hits: list[Bundle] = []
    for name, root in repos.items():
        bs, _ = discover_bundles(name, root)
        hits += [b for b in bs if bundle_id in b.bundle_id]
    if not hits:
        die(f"no bundle matching {bundle_id!r} in {', '.join(repos)}")
    payload = []
    for b in hits:
        d = b.as_inventory_dict()
        d["upstream_issues"] = sorted(b.issues)
        d["req_ids"] = sorted(b.reqs)
        d["bead_ids"] = sorted(b.beads)
        d["paths_mentioned"] = sorted(b.paths)[:200]
        d["mentions"] = [m.as_dict() for m in b.mentions]
        payload.append(d)
    if as_json:
        emit(json.dumps(payload, indent=2), out)
        return
    lines: list[str] = []
    for d in payload:
        lines += [f"# {d['repo']}/{d['bundle_id']}", "",
                  f"- kind: {d['kind']} · number: {d['number']} · scope: {d['scope']} · layout: {d['layout']}",
                  f"- status: {d['status'] or '-'} · created: {d['created'] or '-'} · epic: {d['epic'] or '-'}",
                  f"- files: {', '.join(d['files']) or '-'}",
                  f"- missing expected: {', '.join(d['missing_expected']) or '-'}",
                  f"- upstream issues: {', '.join(d['upstream_issues']) or '-'}",
                  f"- REQ ids: {', '.join(d['req_ids']) or '-'}",
                  f"- bead ids: {', '.join(d['bead_ids']) or '-'}", "",
                  "## Cross-bundle mentions", ""]
        for m in d["mentions"]:
            lines.append(f"- `{m['location']}` -> {m['target']} [{m['context']}"
                         + (f"; {', '.join(m['terms'])}" if m["terms"] else "") + "]")
            lines.append(f"  > {m['quote']}")
        lines.append("")
    emit("\n".join(lines), out)


if __name__ == "__main__":
    cli()
