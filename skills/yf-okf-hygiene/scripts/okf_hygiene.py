#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""okf_hygiene.py — corpus-level OKF health (`yf-okf-hygiene`, REQ-OKFH-001..010).

Four verbs, plus `assess` as a declared alias of `audit`:

    audit     read-only discovery + classification          (REQ-OKFH-003/004/005)
    backfill  the THREE-STEP legacy transform, journalled   (REQ-OKFH-006/007/008/009)
    reindex   index repair, REFUSING a legacy prose index   (REQ-OKFH-010)
    restore   record-driven reversal, per-path op kind      (REQ-OKFH-010)

EXIT CONTRACT (REQ-OKFH-002, inheriting REQ-CLI-029):
    0  the criterion holds   1  it does not   2  the check could NOT RUN
`126`/`127` are reserved to the caller and are never returned.

WHY THIS SKILL IS SEPARATE FROM `yf-okf`. `yf-okf` owns the PER-BUNDLE engine; this owns the
CORPUS. Nothing here re-decides a conformance rule — every single-bundle verdict reported below
is the engine's own verdict, surfaced at population scale.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHECK = "okf-hygiene"

# The engine is vendored beside this script (registered as okf.py's fifth consumer in
# `_shared/sync.py`, plan-057 Issue 1.6). Skills deploy STANDALONE, so a `sys.path` hack to
# `_shared/` is not available — an unregistered vendored copy would drift silently forever.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import okf  # noqa: E402
except Exception as _exc:  # pragma: no cover - environment condition
    print(json.dumps({"check": CHECK, "verdict": "inconclusive", "exit": 2,
                      "reason": f"the vendored okf engine could not be imported: {_exc}"}))
    raise SystemExit(2)


# --------------------------------------------------------------------------------------
# Classification (REQ-OKFH-004)
# --------------------------------------------------------------------------------------

#: The legacy index filenames, in probe order. `_index.md` is routed BY DETECTED MEMBER
#: rather than by filename (REQ-OKFH-010) — the name only tells us where to look.
LEGACY_INDEX_NAMES = ("README.md", "_index.md")

CLASSES = ("conformant", "legacy-readme", "legacy-underscore-index",
           "hybrid-partial", "unclassifiable")

#: A bundle is a bundle because it carries one of these. Membership is what makes a directory
#: a UNIT OF DISTRIBUTION; OKF v0.2 itself specifies no bundle-root marker (REQ-OKF-034), so
#: the yf layer supplies the predicate.
#:
#: THE MARKER ALSO NAMES THE MEMBER, and that mapping is load-bearing rather than incidental.
#: `okf.migrate` is MEMBER-DRIVEN: the member's `index_source` is what tells it which legacy
#: file to rename to `index.md` (OKF-PLAN says `README.md`, OKF-RESEARCH says `_index.md`).
#: Migrating a research bundle under the OKF-PLAN member therefore finds no `README.md`,
#: SCAFFOLDS a fresh `index.md`, and leaves `_index.md` in place — manufacturing the exact
#: `hybrid-partial` state this tool refuses to create. Measured: that is precisely what a
#: global `--skill yf-plan` did to `docs/research/001-okf-compliance-delta` on the first
#: apply run. The member is DETECTED PER BUNDLE; `--skill` is an OVERRIDE, never the default.
MEMBER_FOR_MARKER = {
    "plan.md": "yf-plan",
    "Summary.md": "yf-research",
    "research.md": "yf-research",
    "topic.md": "yf-incubator",
}
MEMBER_MARKERS = tuple(MEMBER_FOR_MARKER)

#: Hard exclusions (REQ-OKFH-005). SELF-CONTAINED: this set names no consumer-private file,
#: because the 40 foreign repositories the skill must be able to run in carry none.
DEFAULT_EXCLUDE_DIRS = (
    ".git", ".worktrees", ".claude", ".yf", ".beads", ".venv", "node_modules",
    "target", "__pycache__", "archive", "archives",
)
#: Frozen fixture trees: their exact bytes ARE a test, so classifying them invites a repair
#: that would destroy the fixture.
DEFAULT_EXCLUDE_GLOBS = (
    "**/fixtures/**",
    "**/okf-migration-samples/**",
    "**/test-harness/**",
)


def _is_excluded(rel: Path, exclude_globs) -> bool:
    parts = set(rel.parts)
    if parts & set(DEFAULT_EXCLUDE_DIRS):
        return True
    # `.claude/worktrees` and any dot-directory below the root.
    if any(p.startswith(".") and p not in (".", "..") for p in rel.parts[:-1]):
        return True
    s = rel.as_posix()
    for g in exclude_globs:
        if Path(s).match(g) or re.match(_glob_to_re(g), s):
            return True
    return False


def _glob_to_re(g: str) -> str:
    out, i = "", 0
    while i < len(g):
        if g.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif g[i] == "*":
            out += "[^/]*"
            i += 1
        elif g[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(g[i])
            i += 1
    return out + "$"


def classify(bundle: Path) -> tuple[str, dict]:
    """Classify one bundle into exactly one of :data:`CLASSES`.

    `unclassifiable` is a REAL verdict and never collapses into a neighbour: a bundle the
    rules cannot place is a statement about this instrument's coverage. Folding it into
    `conformant` certifies what was never read; folding it into a legacy class manufactures
    work.
    """
    detail: dict = {}
    try:
        names = {p.name for p in bundle.iterdir()}
    except OSError as exc:
        return "unclassifiable", {"reason": f"cannot read the directory: {exc}"}

    member = next((m for m in MEMBER_MARKERS if m in names), None)
    detail["member"] = member
    has_index = "index.md" in names
    legacy = [n for n in LEGACY_INDEX_NAMES if n in names]
    detail["legacy_index"] = legacy
    detail["has_index"] = has_index

    if member is None:
        return "unclassifiable", {**detail, "reason": "no member marker — not a bundle root"}

    if has_index and legacy:
        # PARTIALLY MIGRATED. Both surfaces exist and may disagree, and nothing here can know
        # which one the author meant — so it is a HALT class, not a transform (REQ-OKFH-007).
        return "hybrid-partial", detail
    if has_index:
        return "conformant", detail
    if "README.md" in legacy:
        return "legacy-readme", detail
    if "_index.md" in legacy:
        return "legacy-underscore-index", detail
    return "unclassifiable", {**detail,
                              "reason": "no index.md and no recognised legacy index"}


def discover(roots, maxdepth: int, exclude_globs) -> list[Path]:
    """Bundle roots under each root glob, to `maxdepth` levels (REQ-OKFH-005)."""
    found: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        rp = Path(root)
        if not rp.is_absolute():
            rp = Path.cwd() / rp
        if not rp.is_dir():
            continue
        base = rp.resolve()
        stack = [(base, 0)]
        while stack:
            d, depth = stack.pop()
            if depth > maxdepth:
                continue
            try:
                children = sorted(d.iterdir())
            except OSError:
                continue
            for c in children:
                if not c.is_dir():
                    continue
                try:
                    rel = c.relative_to(base)
                except ValueError:
                    continue
                if _is_excluded(rel, exclude_globs):
                    continue
                names = {p.name for p in c.iterdir()} if c.is_dir() else set()
                if names & set(MEMBER_MARKERS):
                    if c not in seen:
                        seen.add(c)
                        found.append(c)
                    continue          # a bundle root is a leaf: never descend into one
                stack.append((c, depth + 1))
    return sorted(found)


# --------------------------------------------------------------------------------------
# The audit verdict a backfill must not worsen (REQ-OKFH-009)
# --------------------------------------------------------------------------------------

def _plan_manager() -> Path | None:
    here = Path(__file__).resolve()
    for up in here.parents:
        cand = up / "skills" / "yf-plan" / "scripts" / "plan_manager.py"
        if cand.is_file():
            return cand
    return None


def audit_verdict(bundle: Path) -> str:
    """`pass` | `warn` | `fail` for one bundle, FROM THE SHIPPED AUDIT.

    THE VERDICT SOURCE IS `plan_manager.py audit`, NOT `okf.check_conformance`, and the
    distinction is the whole reason the delta check exists. `okf_missing_level` — the flag
    that flips `warn` to `fail` the moment `plan.md` gains frontmatter — lives in
    `_audit_plan`, not in the engine. Measured on plan-010: `okf.check_conformance` reports 9
    warnings either side of a bare `migrate`, while `plan_manager.py audit` goes
    `pass` -> `fail`. Reading the engine would have made the regression INVISIBLE.
    """
    pm = _plan_manager()
    if pm is None:
        return "unknown"
    try:
        proc = subprocess.run(["uv", "run", str(pm), "audit", str(bundle), "--json-output"],
                              capture_output=True, text=True, timeout=120)
        data = json.loads(proc.stdout)
    except Exception:
        return "unknown"
    status = str(data.get("status", "")).lower()
    if status in ("pass", "fail"):
        report = data.get("report", "")
        if status == "pass" and "[warn]" in report:
            return "warn"
        return status
    return "unknown"


# --------------------------------------------------------------------------------------
# The crash-recovery journal (REQ-OKFH-008)
# --------------------------------------------------------------------------------------

JOURNAL_DIR = ".okf-hygiene-journal"
STAGING_DIR = ".okf-hygiene-staging"

#: The FIVE reachable states, enumerated ONCE and normatively (REQ-OKFH-008). They are named
#: here because R2, SC11 and the test suite all key on "a set of five" that no document listed
#: — so a five-state test and a five-state journal could have been five DIFFERENT fives with
#: every instrument green.
STATES = {
    "S0": "nothing staged",
    "S1": "staged, before rename 1",
    "S2": "after rename 1 — the bundle is ABSENT",
    "S3": "after rename 2 — the original is stashed",
    "S4": "after rename 2, before the journal is unlinked",
}


def _fsync_write(path: Path, text: str) -> None:
    """Write and FSYNC — the journal must survive the crash it exists to describe.

    Durability here is the whole mechanism. `os.rename` onto a NON-EMPTY directory raises
    `OSError errno 66`, so the swap below is TWO renames with a window in which the bundle is
    absent; a recovery table keyed on directory presence is not total over the five states and
    reads S1 ("staged, crashed before rename 1") as "done".
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, text.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    dfd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


class Journal:
    """A durable per-bundle record of which of the five states the transform is in."""

    def __init__(self, tree: Path, bundle: Path):
        self.tree = tree
        self.bundle = bundle
        slug = bundle.name
        self.path = tree / JOURNAL_DIR / f"{slug}.json"
        self.staging = bundle.parent / STAGING_DIR / bundle.name
        self.stash = bundle.parent / f"{bundle.name}.okf-stash"

    def write(self, phase: str, **extra) -> None:
        _fsync_write(self.path, json.dumps(
            {"phase": phase, "meaning": STATES.get(phase, "?"),
             "bundle": str(self.bundle), "staging": str(self.staging),
             "stash": str(self.stash), **extra}, indent=1))

    def read(self) -> dict | None:
        if not self.path.is_file():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def clear(self) -> None:
        """Unlink the journal AND remove the now-empty scaffolding directories.

        LEAVING THE EMPTY PARENTS IS RESIDUE, AND RESIDUE IS NOT COSMETIC HERE. The staging
        parent lives at `<root>/.okf-hygiene-staging`, i.e. INSIDE the very directory the
        corpus drift driver enumerates with `docs/plans/*` — so two leftover empty directories
        were counted as two extra bundles (64 -> 66 enumerated, both reported `no-index`). A
        tool that inflates the corpus census it is meant to clean is reporting on itself.

        `rmdir` rather than `rmtree`: it removes the directory ONLY if it is empty, so a
        concurrent bundle still staging is never destroyed.
        """
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        for d in (self.staging.parent, self.path.parent):
            try:
                d.rmdir()
            except OSError:
                pass          # not empty, or already gone — both fine


def recover(tree: Path, bundle: Path) -> dict:
    """Deterministically finish or roll back, FROM ANY OF THE FIVE STATES.

    Keyed on the JOURNAL's recorded phase, never on directory presence — which is exactly the
    distinction that makes S1 and S4 separable at all.
    """
    j = Journal(tree, bundle)
    rec = j.read()
    if rec is None:
        return {"recovered": False, "phase": "S0", "action": "nothing to recover"}
    phase = rec.get("phase", "S0")
    staging, stash = Path(rec["staging"]), Path(rec["stash"])

    if phase in ("S0", "S1"):
        # Nothing irreversible happened. Discard the staged copy; the bundle is untouched.
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        j.clear()
        return {"recovered": True, "phase": phase, "action": "discarded staging; bundle untouched"}
    if phase == "S2":
        # The bundle is ABSENT — the dangerous window. Roll FORWARD if the staged copy is
        # intact, else roll BACK from the stash. Presence alone could not tell these apart.
        if staging.exists():
            os.rename(staging, bundle)
            if stash.exists():
                shutil.rmtree(stash, ignore_errors=True)
            j.clear()
            return {"recovered": True, "phase": phase, "action": "rolled forward from staging"}
        if stash.exists():
            os.rename(stash, bundle)
            j.clear()
            return {"recovered": True, "phase": phase, "action": "rolled back from stash"}
        j.clear()
        return {"recovered": False, "phase": phase,
                "action": "UNRECOVERABLE: neither staging nor stash survives"}
    if phase in ("S3", "S4"):
        # The swap completed; only cleanup remains. Idempotent.
        if stash.exists():
            shutil.rmtree(stash, ignore_errors=True)
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        j.clear()
        return {"recovered": True, "phase": phase, "action": "completed cleanup"}
    j.clear()
    return {"recovered": False, "phase": phase, "action": f"unknown phase {phase!r}"}


# --------------------------------------------------------------------------------------
# The three-step transform (REQ-OKFH-006)
# --------------------------------------------------------------------------------------

_LOG_BULLET = re.compile(r"^[ \t]*[-*][ \t]+(.*\S)[ \t]*$", re.MULTILINE)
_ISO_DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_PHASE_LOG_HEAD = re.compile(r"(?m)^\*\*Phase log:\*\*[ \t]*$")


def _phase_log_block(text: str) -> str:
    """The `**Phase log:**` block ONLY — from its header to the first `## `.

    SCOPING THIS IS NOT TIDINESS. `plan.md` carries ISO dates outside the phase log — a
    `created:` frontmatter key, a `**Created:**` header line, dated measurements in prose —
    and signaturing the WHOLE document sweeps them all in. Measured on a fixture whose phase
    log held 2 dates: the unscoped reading found 3, so the "did any date get lost?" check
    compared a set the destination could never contain and HALTED a transform that had lost
    nothing. A guard that fires on correct input is not a stricter guard; it is a broken one,
    and it trains the operator to override it.

    A document already in the migrated shape carries no `**Phase log:**` header, in which case
    the whole text is the block — that is `log.md`'s case, and it is the destination side.
    """
    m = _PHASE_LOG_HEAD.search(text)
    if not m:
        return text
    rest = text[m.end():]
    stop = re.search(r"(?m)^## ", rest)
    return rest[:stop.start()] if stop else rest


def _log_signature(text: str) -> tuple[set, set]:
    """`(bullet texts, distinct dates)` — READ FROM BOTH PHASE-LOG SHAPES.

    THE TWO SIDES OF THIS COMPARISON ARE WRITTEN DIFFERENTLY, and that is why the extractor
    cannot be anchored to one of them. The SOURCE is `plan.md`'s `**Phase log:**` block, whose
    dates are INLINE in each bullet (`- 2026-08-01 scoping: started`). The DESTINATION is
    `log.md`, whose dates are `## YYYY-MM-DD` HEADINGS with the bullets beneath them stripped
    of their date prefix. A `^## (date)$` extractor therefore reads ZERO dates out of the
    source and would have compared an empty set against a full one — vacuously passing on the
    very data-loss mode this check exists to catch.

    So dates are matched ANYWHERE (heading or inline), and a bullet's identity is its
    date-STRIPPED text, which is the part that survives the move.
    """
    text = _phase_log_block(text)
    dates = set(_ISO_DATE.findall(text))
    bullets = {_ISO_DATE.sub("", b).strip(" -\t") for b in _LOG_BULLET.findall(text)}
    return {b for b in bullets if b}, dates


def _objective(plan_md: Path) -> str:
    """`plan.md`'s H1 — THE comparator D-5's divergence measurement is defined against.

    NOT the `## Objective` SECTION BODY, and the difference is not cosmetic. In the older
    bundles that half of the corpus consists of, `## Objective` opens with a
    motivation-style paragraph rather than a one-line objective, so comparing it against the
    legacy index's `>` line reports a divergence on nearly every bundle. Measured both ways
    over the 31 legacy bundles: the section-body reading flags **22**, the H1 reading flags
    **7** — and 7 is the figure D-5 recorded independently. A halt class that fires on 22 of
    31 is not a halt class; it is an outage, and it would have trained the operator to wave
    the gate through, which is the exact failure the gate exists to prevent.
    """
    try:
        text = plan_md.read_text(encoding="utf-8")
    except OSError:
        return ""
    m = re.search(r"(?m)^# (?:Plan: )?(.+)$", text)
    return okf._one_line(m.group(1)) if m else ""


def _legacy_objective(legacy_index: Path) -> str:
    try:
        text = legacy_index.read_text(encoding="utf-8")
    except OSError:
        return ""
    m = re.search(r"(?m)^> (.+)$", text)
    return okf._one_line(m.group(1)) if m else ""


def halts(bundle: Path, cls: str) -> list[dict]:
    """The two declared halt classes (REQ-OKFH-007). Neither is auto-resolvable."""
    out: list[dict] = []
    if cls == "hybrid-partial":
        out.append({"kind": "hybrid-partial",
                    "detail": "the bundle carries BOTH index.md and a legacy index; "
                              "which one the author meant is not derivable"})
    legacy = next((bundle / n for n in LEGACY_INDEX_NAMES if (bundle / n).is_file()), None)
    if legacy is not None:
        lo, po = _legacy_objective(legacy), _objective(bundle / "plan.md")
        if lo and po and lo != po:
            out.append({"kind": "objective-divergence",
                        "detail": "the legacy index's objective differs from plan.md's",
                        "legacy": lo, "plan": po})
    return out


def _render_backfilled_index(bundle: Path, objective: str) -> str:
    lines = [okf._dump_frontmatter({"okf_version": okf.okf_version}),
             f"\n# {bundle.name}\n\n"]
    if objective:
        lines.append(f"> {objective}\n\n")
    lines.append("This bundle is **portable** — a cold reader understands its purpose, "
                 "environment and history from the files below alone, without the drafting "
                 "conversation.\n\n")
    for member in okf._listing_members(bundle):
        lines.append(okf._index_bullet(member, member,
                                       okf.resolve_description(bundle, member)))
    return "".join(lines)


def backfill_one(tree: Path, bundle: Path, *, apply: bool, skill: str | None) -> dict:
    """`migrate` -> DELETE the renamed legacy index -> REGENERATE the listing.

    NEVER `migrate` ALONE (REQ-OKFH-006). Measured: a bare `migrate` takes plan-010 from audit
    `pass` to audit `fail` — it stamps `plan.md` frontmatter, which flips `okf_missing_level`
    to `fail`, and leaves the renamed README's File-map prose in `index.md`, which
    `reindex --write` cannot repair.
    """
    cls, detail = classify(bundle)
    rec: dict = {"bundle": str(bundle.relative_to(tree)) if bundle.is_relative_to(tree)
                 else str(bundle), "class": cls, "detail": detail}

    if cls == "conformant":
        rec["action"] = "skip"
        rec["reason"] = "already conformant"
        return rec
    if cls == "unclassifiable":
        rec["action"] = "skip"
        rec["reason"] = "unclassifiable — never transformed blind"
        return rec

    h = halts(bundle, cls)
    if h:
        rec["action"] = "halt"
        rec["halts"] = h
        return rec

    # PER-BUNDLE MEMBER RESOLUTION (see MEMBER_FOR_MARKER). An explicit `--skill` overrides,
    # but nothing is assumed from the caller's default.
    member_skill = skill or MEMBER_FOR_MARKER.get(detail.get("member") or "", "yf-plan")
    rec["member_skill"] = member_skill
    rec["before"] = {"verdict": audit_verdict(bundle)}
    legacy_name = detail["legacy_index"][0]
    objective = _legacy_objective(bundle / legacy_name) or _objective(bundle / "plan.md")
    plan_before = (bundle / "plan.md").read_text(encoding="utf-8") \
        if (bundle / "plan.md").is_file() else ""

    if not apply:
        rec["action"] = "would-backfill"
        rec["steps"] = ["migrate", f"delete-renamed-{legacy_name}-prose", "regenerate-listing"]
        return rec

    j = Journal(tree, bundle)
    j.write("S0")
    # ---- stage: a full copy, transformed, INSIDE THE REPO TREE ------------------------
    # Never `$(mktemp -d)`: a cross-filesystem staging turns the rename below into a COPY,
    # which voids every durability claim the journal makes (measured EXDEV risk).
    if j.staging.exists():
        shutil.rmtree(j.staging)
    j.staging.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(bundle, j.staging)

    # STEP 1 — migrate (renames the legacy index to index.md, stamps frontmatter,
    #                   extracts the phase log into log.md).
    okf.migrate(j.staging, skill=member_skill)
    # STEP 2 — DELETE the renamed legacy index. It is legacy PROSE, not a listing, and
    #          `reindex --write` would append a generated listing BENEATH it, producing one
    #          file with two contradictory listings.
    (j.staging / "index.md").unlink(missing_ok=True)
    # STEP 3 — REGENERATE the listing.
    (j.staging / "index.md").write_text(_render_backfilled_index(j.staging, objective),
                                        encoding="utf-8")
    j.write("S1")

    # ---- the phase-log guarantee (REQ-OKFH-009) --------------------------------------
    # The FINGERPRINT IS NOT THE GUARANTEE: it covers plan.md's content sections only and
    # excludes every file this transform mutates. The phase log lives ABOVE the first `## `
    # and is excluded from the hash, and it is the one MEASURED data-loss mode.
    src_bul, src_dates = _log_signature(plan_before)
    log_after = (j.staging / "log.md")
    dst_bul, dst_dates = _log_signature(
        log_after.read_text(encoding="utf-8") if log_after.is_file() else "")
    lost_dates = src_dates - dst_dates
    if lost_dates:
        shutil.rmtree(j.staging, ignore_errors=True)
        j.clear()
        rec["action"] = "halt"
        rec["halts"] = [{"kind": "phase-log-loss",
                         "detail": f"{len(lost_dates)} phase-log date(s) would be lost",
                         "dates": sorted(lost_dates)}]
        return rec

    # ---- the swap: TWO renames, with a window in which the bundle is absent -----------
    j.write("S1")
    os.rename(bundle, j.stash)          # rename 1
    j.write("S2")
    os.rename(j.staging, bundle)        # rename 2
    j.write("S3")
    shutil.rmtree(j.stash, ignore_errors=True)
    j.write("S4")
    j.clear()

    # POST-CONDITION: the transform must not have MANUFACTURED a hybrid. A leftover legacy
    # index beside a new `index.md` is precisely the state `hybrid-partial` exists to refuse,
    # and creating it would be strictly worse than not running — so it is asserted on the way
    # out, not merely avoided on the way in.
    leftover = [n_ for n_ in LEGACY_INDEX_NAMES if (bundle / n_).exists()]
    if leftover and (bundle / "index.md").exists():
        rec["action"] = "halt"
        rec["halts"] = [{"kind": "manufactured-hybrid",
                         "detail": f"the transform left {leftover} beside a new index.md — "
                                   f"member {member_skill!r} was wrong for this bundle"}]
        return rec

    rec["after"] = {"verdict": audit_verdict(bundle)}
    rec["action"] = "backfilled"
    return rec


# --------------------------------------------------------------------------------------
# Verbs
# --------------------------------------------------------------------------------------

def cmd_audit(a) -> int:
    roots = a.root or ["docs/plans", "docs/research"]
    bundles = discover(roots, a.maxdepth, DEFAULT_EXCLUDE_GLOBS)
    rows = []
    for b in bundles:
        cls, detail = classify(b)
        rows.append({"bundle": str(b), "class": cls, "detail": detail})
    counts = {c: sum(1 for r in rows if r["class"] == c) for c in CLASSES}
    legacy_n = counts["legacy-readme"] + counts["legacy-underscore-index"] \
        + counts["hybrid-partial"]

    out = {"check": CHECK, "command": "audit", "roots": list(roots),
           "bundles_checked": len(rows), "counts": counts, "legacy": legacy_n,
           "verdict": "pass", "exit": 0}
    if a.json:
        out["rows"] = rows

    # FAIL LOUDLY ON AN EMPTY INSPECTION (REQ-OKFH-002 / REQ-CLI-029(b)). A corpus tool that
    # inspected nothing exits 0 on every rule it applies, so "clean" and "not read" are the
    # same observation without a declared floor.
    if a.min_roots is not None and len(rows) < a.min_roots:
        out.update({"verdict": "inconclusive", "exit": 2,
                    "reason": f"enumerated {len(rows)} bundle(s), --min-roots {a.min_roots}"})
        print(json.dumps(out, indent=1))
        return 2
    if a.require_legacy is not None and legacy_n != a.require_legacy:
        out.update({"verdict": "fail", "exit": 1,
                    "reason": f"{legacy_n} legacy bundle(s), --require-legacy "
                              f"{a.require_legacy}"})
        print(json.dumps(out, indent=1))
        return 1
    print(json.dumps(out, indent=1))
    return 0


def cmd_backfill(a) -> int:
    tree = Path.cwd()
    roots = a.root or ["docs/plans", "docs/research"]
    bundles = discover(roots, a.maxdepth, DEFAULT_EXCLUDE_GLOBS)
    records = [backfill_one(tree, b, apply=a.apply, skill=a.skill) for b in bundles]
    touched = [r for r in records if r.get("action") in ("backfilled", "would-backfill")]
    halted = [r for r in records if r.get("action") == "halt"]
    out = {"check": CHECK, "command": "backfill", "apply": bool(a.apply),
           "bundles_checked": len(records), "transformed": len(touched),
           "halted": len(halted), "bundles": records,
           "verdict": "fail" if halted else "pass", "exit": 1 if halted else 0}
    if a.record:
        rp = Path(a.record) if Path(a.record).is_absolute() else tree / a.record
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(
            {"bundles": [r for r in records if "before" in r and "after" in r]},
            indent=1), encoding="utf-8")
        out["record"] = str(rp)
    print(json.dumps(out, indent=1))
    return out["exit"]


def cmd_reindex(a) -> int:
    tree = Path.cwd()
    bundle = Path(a.bundle) if Path(a.bundle).is_absolute() else tree / a.bundle
    cls, _detail = classify(bundle)
    if cls in ("legacy-readme", "legacy-underscore-index", "hybrid-partial"):
        # REFUSE (REQ-OKFH-010). A legacy prose index is not a listing with entries missing —
        # it is a DIFFERENT DOCUMENT. Appending a generated listing beneath it produces a file
        # that satisfies the entry regex while carrying two contradictory listings. Converting
        # one is `backfill`'s job, and the refusal is what stops the two verbs from quietly
        # overlapping.
        print(json.dumps({"check": CHECK, "command": "reindex", "verdict": "refused",
                          "exit": 1, "class": cls,
                          "reason": "a legacy prose index is backfill's job, not reindex's — "
                                    "appending beneath it would produce two contradictory "
                                    "listings in one file"}, indent=1))
        return 1
    res = okf.reindex_write(bundle, dry_run=not a.apply)
    print(json.dumps({"check": CHECK, "command": "reindex", "verdict": res["verdict"],
                      "changed": res.get("changed"), "changes": res.get("changes"),
                      "exit": 0 if res["verdict"] == "clean" else 1}, indent=1))
    return 0 if res["verdict"] == "clean" else 1


def cmd_restore(a) -> int:
    tree = Path.cwd()
    rp = Path(a.record) if Path(a.record).is_absolute() else tree / a.record
    try:
        data = json.loads(rp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"check": CHECK, "command": "restore", "verdict": "inconclusive",
                          "exit": 2, "reason": f"cannot read the record: {exc}"}, indent=1))
        return 2
    ops = []
    for entry in data.get("bundles", []):
        b = tree / entry["bundle"]
        for path in sorted(p for p in b.rglob("*") if p.is_file()):
            rel = path.relative_to(tree).as_posix()
            # PER-PATH OPERATION KIND (REQ-OKFH-010). `git checkout` ALONE CANNOT UNDO THIS
            # TRANSFORM: a modified or deleted TRACKED file is restored by checkout, but a
            # CREATED index.md/log.md is absent from HEAD and must be UNLINKED. A restore that
            # only checks out leaves every created file behind and reports success.
            tracked = subprocess.run(["git", "-C", str(tree), "ls-files", "--error-unmatch",
                                      rel], capture_output=True).returncode == 0
            ops.append({"path": rel, "kind": "git-checkout" if tracked else "unlink"})
        ops.append({"path": entry["bundle"], "kind": "git-checkout-tree"})
    if a.apply:
        for op in ops:
            if op["kind"] == "unlink":
                (tree / op["path"]).unlink(missing_ok=True)
        subprocess.run(["git", "-C", str(tree), "checkout", "--"]
                       + [e["bundle"] for e in data.get("bundles", [])],
                       capture_output=True)
    print(json.dumps({"check": CHECK, "command": "restore", "apply": bool(a.apply),
                      "operations": ops, "verdict": "pass", "exit": 0}, indent=1))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="corpus-level OKF health (yf-okf-hygiene)")
    ap.add_argument("--json", action="store_true", help="emit per-bundle rows")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("audit", "assess"):
        # `assess` is a DECLARED ALIAS of `audit` (plan-057 Issue 2.1, option (b)). D-3 has
        # this skill ABSORB `yf-okf`'s advertised-but-unimplemented `assess`; the capability
        # it advertised — discover bundles, report per-bundle impact, never mutate — is
        # exactly `audit`. A third distinct verb for one capability would be the
        # adjacent-names disambiguation problem the plan warns about, and an advertised name
        # that does not dispatch is the defect being deleted from `yf-okf`, relocated.
        p = sub.add_parser(name, help="read-only discovery + classification (never writes)")
        p.add_argument("--root", action="append", help="repeatable root (absolute is fine)")
        p.add_argument("--maxdepth", type=int, default=2)
        p.add_argument("--require-legacy", type=int, default=None)
        p.add_argument("--min-roots", type=int, default=None)
        p.add_argument("--json", action="store_true")
        p.set_defaults(fn=cmd_audit)

    p = sub.add_parser("backfill", help="the three-step legacy transform (dry-run by default)")
    p.add_argument("--root", action="append")
    p.add_argument("--maxdepth", type=int, default=2)
    p.add_argument("--apply", action="store_true", help="perform the transform")
    p.add_argument("--record", default=None, help="write the per-bundle audit record here")
    p.add_argument("--skill", default=None,
                   help="OVERRIDE the per-bundle member detection (rarely correct)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_backfill)

    p = sub.add_parser("reindex", help="index repair; REFUSES a legacy prose index")
    p.add_argument("bundle")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_reindex)

    p = sub.add_parser("restore", help="record-driven reversal, per-path operation kind")
    p.add_argument("--record", required=True)
    p.add_argument("--apply", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_restore)

    a = ap.parse_args()
    try:
        return a.fn(a)
    except Exception as exc:                       # never a traceback as a verdict
        print(json.dumps({"check": CHECK, "verdict": "inconclusive", "exit": 2,
                          "reason": f"{type(exc).__name__}: {exc}"}, indent=1))
        return 2


if __name__ == "__main__":
    sys.exit(main())
