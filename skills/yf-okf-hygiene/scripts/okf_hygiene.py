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
    restore   record-driven reversal, per-path op kind      (REQ-OKFH-010/013)
    recover   finish or roll back an interrupted backfill   (REQ-OKFH-008)

EXIT CONTRACT (REQ-OKFH-002, inheriting REQ-CLI-029):
    0  the criterion holds   1  it does not   2  the check could NOT RUN
`126`/`127` are reserved to the caller and are never returned.

WHY THIS SKILL IS SEPARATE FROM `yf-okf`. `yf-okf` owns the PER-BUNDLE engine; this owns the
CORPUS. Nothing here re-decides a conformance rule — every single-bundle verdict reported below
is the engine's own verdict, surfaced at population scale.
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
from pathlib import Path

CHECK = "okf-hygiene"

#: THE RECORD SCHEMA VERSION (REQ-OKFH-013). Bumped whenever the meaning of a `--record`
#: artifact changes in a way `restore` must not misread.
#:
#: Version 1 is the FIRST versioned schema, and its arrival is itself the breaking change: the
#: pre-1 (unversioned) record carried a before/after audit VERDICT and no operations at all,
#: while `restore` re-derived the operation list by `rglob` + `git ls-files` at restore time.
#: Read under the record-driven contract, that legacy shape yields an EMPTY operation list —
#: which a record-driven `restore` would faithfully execute as "reverse nothing" and report as
#: `pass`. That is why an unversioned record is REFUSED rather than tolerated: the failure it
#: prevents is silent, and the check is one field.
RECORD_SCHEMA_VERSION = 1

#: The internal switch Issue 3.8's negative control flips (SC13b). It forces `restore` back onto
#: the PRE-record-driven derivation, so the mutation the control needs is ONE FLAG rather than a
#: hand-reconstructed revert of a function. A control that has to rebuild the defect it is
#: testing for is a control nobody re-runs.
#:
#: It is deliberately an ENV VAR and not a CLI flag: it must never appear in `--help` as
#: something an operator could reach for, because selecting it re-opens all three data-loss
#: paths EXP-001 measured.
LEGACY_DERIVATION_ENV = "OKFH_FORCE_LEGACY_DERIVATION"

#: The sibling switch for `REQ-OKFH-008` (Issue 3.8 / SC13a). It restores the PRE-Issue-3.1
#: phase ordering — each phase written AFTER the operation it names — so the negative control
#: reproduces that defect by FLIPPING A SWITCH rather than by reconstructing a revert with `sed`.
#:
#: A control whose mutant must be hand-rebuilt drifts from the code the moment either changes,
#: and then silently tests nothing. Both of this plan's false-green mutations are therefore one
#: switch each. Like its sibling it is an ENV VAR, never a CLI flag: selecting it re-opens the
#: total-loss window EXP-001 measured.
LEGACY_PHASE_ORDER_ENV = "OKFH_FORCE_LEGACY_PHASE_ORDER"

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


ERRNO_DIR_NOT_EMPTY = 66          # macOS ENOTEMPTY; Linux reports 39. Both are handled below.


def _rename_onto(src: Path, dst: Path) -> tuple[bool, str]:
    """`os.rename(src, dst)` with the errno-66 window handled (Issue 3.3).

    `os.rename` onto a NON-EMPTY directory raises `OSError` (`ENOTEMPTY`: errno 66 on macOS, 39
    on Linux). That is the whole reason the swap is two renames rather than one, and it is
    reachable during recovery in BOTH `S2`-branch renames — so both are wrapped here rather than
    each open-coding a `try`.

    Returns ``(ok, note)`` instead of raising: recovery must be able to REPORT that it could not
    proceed. An uncaught `OSError` here wedges `recover()` idempotently — no data is lost, but
    every subsequent invocation raises the same exception, which SC11 forbids.
    """
    try:
        os.rename(src, dst)
        return True, ""
    except OSError as exc:
        if exc.errno in (ERRNO_DIR_NOT_EMPTY, 39):
            return False, (f"cannot rename {src.name} onto {dst.name}: the destination exists and "
                           f"is not empty (errno {exc.errno})")
        return False, f"cannot rename {src.name} onto {dst.name}: {exc}"


def recover(tree: Path, bundle: Path) -> dict:
    """Deterministically finish or roll back, FROM ANY OF THE FIVE PHYSICAL STATES.

    Keyed on the JOURNAL's recorded phase, never on directory presence — that distinction is what
    makes the states separable at all.

    **BUT EVERY BRANCH TOLERATES A PHYSICAL PHASE ONE STEP BEHIND ITS RECORDED PHASE**
    (REQ-OKFH-008 as amended, Issue 3.9). This is the obligation the over-approximation creates,
    and it is NOT optional: because Issue 3.1 writes each phase BEFORE its operation, a crash in
    the window between the write and the operation records a phase the code had not yet reached.
    A branch that reads its recorded phase and ASSUMES the named operation completed is a
    data-loss path under this very invariant.

    Concretely, and measured: the shipped `S3`/`S4` branch unconditionally `rmtree`d both stash
    and staging and returned ``recovered: True, "completed cleanup"``. Under the fixed ordering
    that branch is reachable with the physical state at `S2` — bundle ABSENT, staging present,
    rename 2 not yet performed — so it would have DESTROYED THE BUNDLE. The phase-ordering fix
    would have introduced exactly the failure EXP-001 refuted the plan's premise with, relocated
    from `S1` to `S3`. Hence: complete the pending rename FIRST, clean up second.
    """
    j = Journal(tree, bundle)
    rec = j.read()
    if rec is None:
        return {"recovered": False, "phase": "S0", "action": "nothing to recover"}
    phase = rec.get("phase", "S0")
    staging, stash = Path(rec["staging"]), Path(rec["stash"])

    if phase in ("S0", "S1"):
        # Legacy records only — the fixed ordering never writes these. Nothing irreversible
        # happened: discard the staged copy; the bundle is untouched.
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        j.clear()
        return {"recovered": True, "phase": phase, "action": "discarded staging; bundle untouched"}

    if phase == "S2":
        # Recorded `S2` spans TWO physical states, because it is written before staging:
        #   (a) physical S0/S1 — the bundle is STILL PRESENT, rename 1 has not run;
        #   (b) physical S2    — the bundle is ABSENT, rename 1 has run.
        # They are distinguishable without ambiguity: after rename 2 the staging directory no
        # longer exists, so `bundle present AND staging present` can only mean (a).
        if bundle.exists():
            # (a) NOTHING IRREVERSIBLE HAPPENED — rename 1 has not completed. Rolling "forward"
            # here would rename staging onto a LIVE directory, which is the uncaught errno-66
            # red-team pass 5 measured. Discard staging (it may not even exist yet: `S2` is
            # written before staging begins, so this branch also covers a crash at physical S0).
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)
            j.clear()
            return {"recovered": True, "phase": phase, "physical": "S0/S1",
                    "action": "discarded staging; bundle untouched (crashed before rename 1)"}
        if staging.exists():
            # (b) The dangerous window: roll FORWARD.
            ok, note = _rename_onto(staging, bundle)
            if not ok:
                return {"recovered": False, "phase": phase, "physical": "S2",
                        "action": f"UNRECOVERABLE without operator action: {note}",
                        "staging": str(staging), "stash": str(stash)}
            if stash.exists():
                shutil.rmtree(stash, ignore_errors=True)
            j.clear()
            return {"recovered": True, "phase": phase, "physical": "S2",
                    "action": "rolled forward from staging"}
        if stash.exists():
            ok, note = _rename_onto(stash, bundle)
            if not ok:
                return {"recovered": False, "phase": phase, "physical": "S2",
                        "action": f"UNRECOVERABLE without operator action: {note}",
                        "stash": str(stash)}
            j.clear()
            return {"recovered": True, "phase": phase, "physical": "S2",
                    "action": "rolled back from stash"}
        j.clear()
        return {"recovered": False, "phase": phase,
                "action": "UNRECOVERABLE: neither staging nor stash survives"}

    if phase in ("S3", "S4"):
        # PRESENCE-TOLERANT (Issue 3.9). `S3` is written BEFORE rename 2 and `S4` BEFORE the
        # cleanup, so either may be recorded while the physical state is one step behind.
        # COMPLETE THE PENDING OPERATION BEFORE CLEANING UP — never the other way round.
        if not bundle.exists() and staging.exists():
            # Physical S2: rename 2 never ran. Cleaning up here is the total-loss path.
            ok, note = _rename_onto(staging, bundle)
            if not ok:
                return {"recovered": False, "phase": phase, "physical": "S2",
                        "action": f"UNRECOVERABLE without operator action: {note}",
                        "staging": str(staging), "stash": str(stash)}
            if stash.exists():
                shutil.rmtree(stash, ignore_errors=True)
            j.clear()
            return {"recovered": True, "phase": phase, "physical": "S2",
                    "action": "completed rename 2 from staging, then cleaned up"}
        if not bundle.exists() and stash.exists():
            # Staging is gone and the bundle is absent: the only surviving copy is the stash.
            # Rolling back is strictly better than cleaning up, which would delete it.
            ok, note = _rename_onto(stash, bundle)
            if not ok:
                return {"recovered": False, "phase": phase,
                        "action": f"UNRECOVERABLE without operator action: {note}",
                        "stash": str(stash)}
            j.clear()
            return {"recovered": True, "phase": phase, "physical": "S2",
                    "action": "rolled back from stash (staging did not survive)"}
        if not bundle.exists():
            j.clear()
            return {"recovered": False, "phase": phase,
                    "action": "UNRECOVERABLE: the bundle is absent and neither staging nor "
                              "stash survives"}
        # The swap completed; only cleanup remains. Idempotent.
        if stash.exists():
            shutil.rmtree(stash, ignore_errors=True)
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        j.clear()
        return {"recovered": True, "phase": phase, "physical": phase,
                "action": "completed cleanup"}

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


def halts(bundle: Path, cls: str, *, reconcile_objective: bool = False) -> list[dict]:
    """The two declared halt classes (REQ-OKFH-007).

    `hybrid-partial` is never auto-resolvable — which of two indexes the author meant is not
    derivable from anything on disk.

    `objective-divergence` IS auto-resolvable, OPT-IN, via `--reconcile-objective`
    (REQ-OKFH-012): `plan.md`'s `H1` is authoritative and the stale legacy `>` line is rewritten
    from it. THE HALT REMAINS THE DEFAULT — a guard whose remedy is enabled by default is a guard
    that has been removed.
    """
    out: list[dict] = []
    if cls == "hybrid-partial":
        out.append({"kind": "hybrid-partial",
                    "detail": "the bundle carries BOTH index.md and a legacy index; "
                              "which one the author meant is not derivable"})
    legacy = next((bundle / n for n in LEGACY_INDEX_NAMES if (bundle / n).is_file()), None)
    if legacy is not None:
        lo, po = _legacy_objective(legacy), _objective(bundle / "plan.md")
        if lo and po and lo != po and not reconcile_objective:
            out.append({"kind": "objective-divergence",
                        "detail": "the legacy index's objective differs from plan.md's",
                        "legacy": lo, "plan": po,
                        "remediation": "re-run with --reconcile-objective to adopt plan.md's H1 "
                                       "as authoritative (the rewrite is reported per bundle)"})
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


def _sha256(path: Path) -> str | None:
    """Content hash of a file, or ``None`` when it cannot be read."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 16), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _snapshot(tree: Path, bundle: Path) -> dict[str, str]:
    """{repo-relative path -> sha256} for every file in ``bundle``.

    Taken on BOTH sides of the transform so the operation list below is a DIFF OF MEASURED
    STATE, not an inference from what the transform intended to do. The distinction matters:
    the three-step transform delegates to `okf.migrate`, so the set of files it touches is not
    fully knowable from this module's own code.
    """
    out: dict[str, str] = {}
    if not bundle.is_dir():
        return out
    for p in sorted(bundle.rglob("*")):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(tree).as_posix()
        except ValueError:
            rel = p.as_posix()
        digest = _sha256(p)
        if digest is not None:
            out[rel] = digest
    return out


def _diff_ops(before: dict[str, str], after: dict[str, str]) -> list[dict]:
    """The PER-PATH OPERATION LIST `REQ-OKFH-010` requires, as created / deleted / modified.

    This is the artifact that makes a reversal claim CHECKABLE. Re-deriving it at restore time
    from `rglob` + `git ls-files` — what the shipped code did — cannot distinguish a file the
    transform created from one that merely happens to be untracked now, so the reversal was
    incidental to `git` rather than driven by a record of what was done.

    A path present on both sides with an unchanged hash is NOT an operation: recording it would
    bloat the record with the overwhelming majority of a bundle's files and bury the few paths a
    reviewer needs to look at.
    """
    ops: list[dict] = []
    for rel in sorted(set(before) | set(after)):
        b, a = before.get(rel), after.get(rel)
        if b is None and a is not None:
            ops.append({"path": rel, "kind": "created", "sha256_before": None, "sha256_after": a})
        elif b is not None and a is None:
            ops.append({"path": rel, "kind": "deleted", "sha256_before": b, "sha256_after": None})
        elif b != a:
            ops.append({"path": rel, "kind": "modified", "sha256_before": b, "sha256_after": a})
    return ops


#: `description:` stamping exemptions (REQ-DATA-075). DECLARED, never inferred — an inferred
#: exemption is indistinguishable from an unstamped producer, which is the defect the
#: requirement addresses. `index.md`/`log.md` are already exempt by carrying no frontmatter.
DESCRIPTION_EXEMPT = ("context.md", "plan-retrospective.md")


def _stamp_descriptions(staging: Path, objective: str) -> list[str]:
    """Stamp `description:` onto the frontmatter this transform writes (REQ-DATA-075, Issue 4.3).

    MEASURED GAP THIS CLOSES (EXP-001): the transform adds `type:` and `okf_spec:` to every
    non-reserved `.md` and stamps `description:` on NONE of them, so a freshly backfilled bundle
    still fails a convention this repository's own producers are held to.

    THE DERIVATION USES ONLY CONTENT THE PRODUCER ALREADY HOLDS, and NEVER INVENTS ONE. `plan.md`
    takes the bundle objective; anything else takes its own `H1`. A file with neither is left
    UNSTAMPED — REQ-OKF-011's "never invent a description" rule applies here too, and a
    manufactured string like "A finding" satisfies the letter of REQ-DATA-075 while defeating its
    purpose.

    An existing non-empty `description:` is never overwritten.
    """
    stamped: list[str] = []
    for md in sorted(staging.rglob("*.md")):
        if md.name in okf.RESERVED_FILES or md.name in DESCRIPTION_EXEMPT:
            continue
        try:
            fm, body = okf.read_frontmatter(md)
        except Exception:
            continue
        if not fm:
            continue                       # migrate stamps no frontmatter here; nothing to add to
        if str(fm.get("description") or "").strip():
            continue                       # already carries one — never overwrite
        if md.name == "plan.md" and objective:
            desc = objective
        else:
            desc = okf._one_line(okf._first_h1(body))
        if not desc:
            continue                       # NEVER INVENT ONE
        try:
            okf.write_frontmatter(md, {"description": desc})
            stamped.append(md.relative_to(staging).as_posix())
        except Exception:
            continue
    return stamped


def _stage_transformed(src: Path, staging: Path, member_skill: str, objective: str) -> list[str]:
    """The THREE-STEP transform, applied to a staging copy. Shared by the dry run and by apply.

    ONE implementation, deliberately (REQ-OKFH-011). The dry run reaches the apply-only guards by
    staging without swapping, never by duplicating each guard on a second code path — two
    implementations of one guard is the defect restated, not repaired: they agree until they do
    not, and nothing detects the day they stop.
    """
    if staging.exists():
        shutil.rmtree(staging)
    staging.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, staging)
    # STEP 1 — migrate (renames the legacy index to index.md, stamps frontmatter,
    #                   extracts the phase log into log.md).
    okf.migrate(staging, skill=member_skill)
    # STEP 2 — DELETE the renamed legacy index. It is legacy PROSE, not a listing, and
    #          `reindex --write` would append a generated listing BENEATH it, producing one
    #          file with two contradictory listings.
    (staging / "index.md").unlink(missing_ok=True)
    # STEP 2b — stamp `description:` (REQ-DATA-075, Issue 4.3), BEFORE the listing is rendered
    #           so the generated entries can pick the new descriptions up.
    stamped = _stamp_descriptions(staging, objective)
    # STEP 3 — REGENERATE the listing.
    (staging / "index.md").write_text(_render_backfilled_index(staging, objective),
                                      encoding="utf-8")
    return stamped


def _staged_halts(plan_before: str, staging: Path, member_skill: str) -> list[dict]:
    """Every halt that can only be judged AFTER staging (REQ-OKFH-011).

    These used to run inside `if apply:`, which made `would-backfill` a WEAKER CLAIM THAN IT
    READS AS: measured, `plan-030` cleared the dry run and then halted under `--apply` on
    `phase-log-loss`. A dry run that under-reports halts is worse than one that reports none,
    because an operator consents to the transform on evidence that does not cover the condition
    that stops it.
    """
    out: list[dict] = []

    # ---- the phase-log guarantee (REQ-OKFH-009) --------------------------------------
    # The FINGERPRINT IS NOT THE GUARANTEE: it covers plan.md's content sections only and
    # excludes every file this transform mutates. The phase log lives ABOVE the first `## `
    # and is excluded from the hash, and it is the one MEASURED data-loss mode.
    src_bul, src_dates = _log_signature(plan_before)
    log_after = staging / "log.md"
    dst_bul, dst_dates = _log_signature(
        log_after.read_text(encoding="utf-8") if log_after.is_file() else "")
    lost_dates = src_dates - dst_dates
    if lost_dates:
        out.append({"kind": "phase-log-loss",
                    "detail": f"{len(lost_dates)} phase-log date(s) would be lost",
                    "dates": sorted(lost_dates)})

    # ---- the manufactured-hybrid post-condition --------------------------------------
    # Judged on the STAGED result, so the dry run predicts it too. Creating a hybrid is
    # strictly worse than not running, so it is asserted rather than merely avoided.
    leftover = [n_ for n_ in LEGACY_INDEX_NAMES if (staging / n_).exists()]
    if leftover and (staging / "index.md").exists():
        out.append({"kind": "manufactured-hybrid",
                    "detail": f"the transform would leave {leftover} beside a new index.md — "
                              f"member {member_skill!r} is wrong for this bundle"})
    return out


def backfill_one(tree: Path, bundle: Path, *, apply: bool, skill: str | None,
                 reconcile_objective: bool = False) -> dict:
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

    h = halts(bundle, cls, reconcile_objective=reconcile_objective)
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
    legacy_obj = _legacy_objective(bundle / legacy_name)
    plan_obj = _objective(bundle / "plan.md")

    # OBJECTIVE RECONCILIATION (REQ-OKFH-012, Issue 4.2). `plan.md`'s H1 is the authority: the
    # divergence is directional — the plan's H1 is revised during re-scoping while the legacy
    # `>` line is not — so the H1 is correct and the legacy line is stale. Reported per bundle,
    # because rewriting an objective line is a content change to a reviewed artifact and must
    # never be a silent consequence of running the verb.
    if reconcile_objective and legacy_obj and plan_obj and legacy_obj != plan_obj:
        objective = plan_obj
        rec["reconciled_objective"] = {"from": legacy_obj, "to": plan_obj,
                                       "authority": "plan.md H1"}
    else:
        objective = legacy_obj or plan_obj
    plan_before = (bundle / "plan.md").read_text(encoding="utf-8") \
        if (bundle / "plan.md").is_file() else ""

    if not apply:
        # THE DRY RUN IS PREDICTIVE OF APPLY (REQ-OKFH-011, Issue 4.1). It stages into a
        # throwaway copy and evaluates EVERY guard apply evaluates — it simply never swaps.
        # Previously the post-staging guards lived inside `if apply:`, so `would-backfill` was a
        # weaker claim than it read as.
        #
        # The staging copy is removed on BOTH exit paths, and NO JOURNAL IS WRITTEN: a dry run
        # must leave nothing behind, least of all a journal that would make the next `backfill`
        # refuse (Issue 3.4).
        dry = bundle.parent / STAGING_DIR / f"{bundle.name}.dry-run"
        try:
            stamped = _stage_transformed(bundle, dry, member_skill, objective)
            dh = _staged_halts(plan_before, dry, member_skill)
            if dh:
                rec["action"] = "halt"
                rec["halts"] = dh
                return rec
            rec["action"] = "would-backfill"
            rec["steps"] = ["migrate", f"delete-renamed-{legacy_name}-prose",
                            "stamp-descriptions", "regenerate-listing"]
            rec["would_stamp_descriptions"] = stamped
            return rec
        finally:
            shutil.rmtree(dry, ignore_errors=True)
            try:
                dry.parent.rmdir()      # only if empty — never destroys a concurrent staging
            except OSError:
                pass

    j = Journal(tree, bundle)
    # THE JOURNAL INVARIANT (REQ-OKFH-008 as amended, Issue 3.1): the RECORDED phase is always
    # `>=` the PHYSICAL phase, because every phase is written and fsynced BEFORE the operation
    # it names. The recorded phase is an OVER-APPROXIMATION, so the only error recovery can make
    # is to believe MORE has happened than has — which is recoverable. The converse ordering is
    # not: a phase written AFTER its operation leaves a window where the physical state is AHEAD
    # of the record, and recovery then rolls back work it cannot see.
    #
    # MEASURED, and this is why the ordering changed: the shipped code wrote `S2` AFTER rename 1,
    # so a crash in that window left the journal reading `S1`, `recover()` took its "nothing
    # irreversible happened" branch, `rmtree`d the transformed staging copy, and reported
    # `recovered: true` WITH THE BUNDLE GONE.
    #
    # `S2` is written before STAGING, not merely before rename 1. Everything from "about to
    # stage" through "about to rename 1" is recovered identically (discard staging, the bundle is
    # untouched), so one phase covers the whole span and `S1` is never written at all — it
    # remains a reachable PHYSICAL state that the journal records as `S2`, exactly as the
    # amended five-state table says.
    _legacy_order = bool(os.environ.get(LEGACY_PHASE_ORDER_ENV))   # Issue 3.8's mutation switch
    j.write("S0" if _legacy_order else "S2")
    # ---- stage: a full copy, transformed, INSIDE THE REPO TREE ------------------------
    # Never `$(mktemp -d)`: a cross-filesystem staging turns the rename below into a COPY,
    # which voids every durability claim the journal makes (measured EXDEV risk).
    rec["stamped_descriptions"] = _stage_transformed(bundle, j.staging, member_skill, objective)

    # THE SAME guards the dry run ran, on the same staged result (REQ-OKFH-011).
    ah = _staged_halts(plan_before, j.staging, member_skill)
    if ah:
        shutil.rmtree(j.staging, ignore_errors=True)
        j.clear()
        rec["action"] = "halt"
        rec["halts"] = ah
        return rec

    # PER-PATH OPERATION LIST (REQ-OKFH-010, Issue 2.1). Both sides are snapshotted around the
    # swap, HERE, where the transform actually knows what it did — the information the shipped
    # record threw away, forcing `restore` to guess it back from the filesystem.
    snap_before = _snapshot(tree, bundle)

    # ---- the swap: TWO renames, with a window in which the bundle is absent -----------
    # Each phase is written BEFORE the operation it names (Issue 3.1). `S2` is already on disk
    # from before staging, so rename 1 is covered.
    if _legacy_order:
        # THE DEFECT, reproduced on demand for the negative control ONLY. Each phase is written
        # AFTER the operation it names, so a crash lands in a window where the physical state is
        # AHEAD of the record — and recovery rolls back work it cannot see.
        j.write("S1")
        os.rename(bundle, j.stash)
        j.write("S2")
        os.rename(j.staging, bundle)
        j.write("S3")
        shutil.rmtree(j.stash, ignore_errors=True)
        j.write("S4")
    else:
        os.rename(bundle, j.stash)      # rename 1  — recorded S2, physical S2
        j.write("S3")                   # BEFORE rename 2
        os.rename(j.staging, bundle)    # rename 2  — the window Issue 3.9's branch must tolerate
        j.write("S4")                   # BEFORE the cleanup
        shutil.rmtree(j.stash, ignore_errors=True)
    j.clear()

    # POST-CONDITION, RETAINED even though `_staged_halts` now predicts it. Predicting a
    # condition on a staged copy and asserting it on the real bundle are different claims: the
    # second is what catches a swap that did not do what staging said it would.
    leftover = [n_ for n_ in LEGACY_INDEX_NAMES if (bundle / n_).exists()]
    if leftover and (bundle / "index.md").exists():
        rec["action"] = "halt"
        rec["halts"] = [{"kind": "manufactured-hybrid",
                         "detail": f"the transform left {leftover} beside a new index.md — "
                                   f"member {member_skill!r} was wrong for this bundle"}]
        return rec

    rec["after"] = {"verdict": audit_verdict(bundle)}
    rec["operations"] = _diff_ops(snap_before, _snapshot(tree, bundle))
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


def stale_journals(tree: Path) -> list[dict]:
    """Every journal left on disk from a previous run (Issue 3.4).

    A journal exists ONLY between `backfill`'s first phase write and `Journal.clear()`, so any
    journal present at ENTRY is the residue of a run that did not finish — i.e. a crash whose
    recovery has never been performed. Measured: nothing looked. `recover()` had no CLI verb and
    `backfill` never called it, so a stale journal was never noticed by anything, and the next
    `backfill` would stage over a bundle whose previous swap was half-done.
    """
    jdir = tree / JOURNAL_DIR
    out: list[dict] = []
    if not jdir.is_dir():
        return out
    for f in sorted(jdir.glob("*.json")):
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            rec = {"phase": "?", "unreadable": True}
        out.append({"journal": str(f.relative_to(tree) if f.is_relative_to(tree) else f),
                    "bundle": rec.get("bundle"), "phase": rec.get("phase")})
    return out


def cmd_recover(a) -> int:
    """The `recover` VERB (Issue 3.2 / REQ-OKFH-008 as amended).

    `recover()` shipped as a module function with NO CLI VERB and no caller, so the durability
    mechanism the SPEC describes was, in practice, unreachable. A recovery mechanism that cannot
    be invoked is a recovery mechanism only in the sense that the code exists.
    """
    tree = Path.cwd()
    stale = stale_journals(tree)
    if not stale:
        print(json.dumps({"check": CHECK, "command": "recover", "verdict": "pass", "exit": 0,
                          "journals": [], "reason": "no journal on disk — nothing to recover"},
                         indent=1))
        return 0

    targets = stale
    if getattr(a, "bundle", None):
        wanted = set(a.bundle)
        targets = [j for j in stale if j["bundle"] and Path(j["bundle"]).name in wanted]
        if not targets:
            print(json.dumps({"check": CHECK, "command": "recover", "verdict": "inconclusive",
                              "exit": 2, "journals": stale,
                              "reason": f"--bundle {sorted(wanted)} matched no journal"}, indent=1))
            return 2

    if not a.apply:
        # DRY RUN BY DEFAULT, like `backfill`. Recovery moves directories on disk.
        print(json.dumps({"check": CHECK, "command": "recover", "apply": False,
                          "verdict": "pass", "exit": 0, "journals": targets,
                          "reason": "dry run — re-run with --apply to recover"}, indent=1))
        return 0

    results = []
    for j in targets:
        if not j["bundle"]:
            results.append({"journal": j["journal"], "recovered": False,
                            "action": "unreadable journal — no bundle path recorded"})
            continue
        results.append({"journal": j["journal"], **recover(tree, Path(j["bundle"]))})
    failed = [r for r in results if not r.get("recovered")]
    out = {"check": CHECK, "command": "recover", "apply": True,
           "recovered": len(results) - len(failed), "failed": len(failed),
           "results": results,
           "verdict": "fail" if failed else "pass", "exit": 1 if failed else 0}
    print(json.dumps(out, indent=1))
    return out["exit"]


def cmd_backfill(a) -> int:
    tree = Path.cwd()

    # ---- REFUSE ON A STALE JOURNAL (Issue 3.4 / REQ-OKFH-008 as amended) -----------------
    # A journal on disk at entry means a previous run crashed mid-swap and was never recovered.
    # Proceeding would stage over a bundle whose swap is half-done. REFUSING rather than
    # auto-recovering is deliberate: recovery moves directories, and doing that as a silent side
    # effect of an unrelated invocation is precisely the class of surprise `--apply` is gated on.
    stale = stale_journals(tree)
    if stale:
        print(json.dumps({"check": CHECK, "command": "backfill", "verdict": "refused", "exit": 1,
                          "stale_journals": stale,
                          "reason": f"{len(stale)} journal(s) from an unfinished previous run are "
                                    f"on disk — a crash mid-swap has never been recovered.",
                          "remediation": "Inspect with `okf_hygiene.py recover`, then run "
                                         "`okf_hygiene.py recover --apply`. Re-run backfill "
                                         "afterwards."}, indent=1))
        return 1

    roots = a.root or ["docs/plans", "docs/research"]
    bundles = discover(roots, a.maxdepth, DEFAULT_EXCLUDE_GLOBS)
    records = [backfill_one(tree, b, apply=a.apply, skill=a.skill,
                            reconcile_objective=bool(getattr(a, 'reconcile_objective', False)))
               for b in bundles]
    touched = [r for r in records if r.get("action") in ("backfilled", "would-backfill")]
    halted = [r for r in records if r.get("action") == "halt"]
    # MIXED-RUN LEGIBILITY (Issue 2.6). A run that MUTATED N bundles and halted on M must never
    # be readable as "nothing happened". The exit code alone cannot carry that: `exit 1` is the
    # same number whether the first bundle halted before touching anything or the tenth halted
    # after nine were rewritten — and the second is the state an operator must not walk away
    # from. So the counts are reported SEPARATELY and named.
    mutated = [r for r in records if r.get("action") == "backfilled"]
    reconciled = [r for r in records if r.get("reconciled_objective")]
    out = {"check": CHECK, "command": "backfill", "apply": bool(a.apply),
           "bundles_checked": len(records), "transformed": len(touched),
           "mutated": len(mutated), "halted": len(halted),
           "reconciled_objectives": [
               {"bundle": r["bundle"], **r["reconciled_objective"]} for r in reconciled],
           "bundles": records,
           "verdict": "fail" if halted else "pass", "exit": 1 if halted else 0}
    if mutated and halted:
        out["mixed_run"] = True
        out["mixed_run_note"] = (
            f"PARTIAL: {len(mutated)} bundle(s) were REWRITTEN ON DISK and {len(halted)} halted. "
            f"exit {out['exit']} does NOT mean 'nothing happened'. The record lists the per-path "
            f"operations for the mutated bundles only; halted bundles were not touched and carry "
            f"no operations."
        )
        out["mutated_bundles"] = [r["bundle"] for r in mutated]
        out["halted_bundles"] = [r["bundle"] for r in halted]
    else:
        out["mixed_run"] = False

    if a.record:
        rp = Path(a.record) if Path(a.record).is_absolute() else tree / a.record
        rp.parent.mkdir(parents=True, exist_ok=True)
        # THE RECORD IS VERSIONED (REQ-OKFH-013) and carries the PER-PATH OPERATIONS
        # (REQ-OKFH-010) rather than a before/after verdict alone. `restore` refuses anything
        # without `schema_version`, because the legacy shape reads as an empty operation list —
        # a silent "reverse nothing" wearing a `pass`.
        rp.write_text(json.dumps({
            "schema_version": RECORD_SCHEMA_VERSION,
            "check": CHECK,
            "apply": bool(a.apply),
            "mixed_run": out["mixed_run"],
            "mutated": len(mutated),
            "halted": len(halted),
            "bundles": [
                {"bundle": r["bundle"],
                 "before": r.get("before"),
                 "after": r.get("after"),
                 "operations": r.get("operations", [])}
                for r in records if "before" in r and "after" in r
            ],
        }, indent=1), encoding="utf-8")
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


def _is_git_tree(tree: Path) -> bool:
    """Is ``tree`` inside a git work tree? REFUSAL CONDITION 1 (REQ-OKFH-010 as amended)."""
    r = subprocess.run(["git", "-C", str(tree), "rev-parse", "--is-inside-work-tree"],
                       capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == "true"


def _tracked_at_head(tree: Path, rel: str) -> bool:
    """Is ``rel`` present in ``HEAD``? REFUSAL CONDITION 2's predicate.

    `HEAD`, not the index: `restore`'s whole mechanism is `git checkout`, which restores
    COMMITTED bytes. A path staged but never committed is not recoverable by it.
    """
    r = subprocess.run(["git", "-C", str(tree), "cat-file", "-e", f"HEAD:{rel}"],
                       capture_output=True)
    return r.returncode == 0


def _bundle_dirty(tree: Path, rel_bundle: str, ops: list[dict]) -> list[str]:
    """Paths in ``rel_bundle`` that differ from the POST-BACKFILL state. REFUSAL CONDITION 3.

    The comparison is against the state `backfill` LEFT, which is exactly what the record's
    `sha256_after` records. Anything else is an edit made since — and `restore`'s unlink pass
    would destroy it with no warning, which is the third measured loss path.

    Untracked files that the record does not mention are also reported: the shipped code
    unlinked every untracked file in the bundle, so a file nobody recorded is precisely the
    thing at risk.
    """
    expected = {op["path"]: op.get("sha256_after") for op in ops
                if op["kind"] in ("created", "modified")}
    deleted = {op["path"] for op in ops if op["kind"] == "deleted"}
    dirty: list[str] = []
    bundle = tree / rel_bundle
    seen = set()
    for p in sorted(bundle.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(tree).as_posix()
        seen.add(rel)
        if rel in expected:
            if _sha256(p) != expected[rel]:
                dirty.append(rel)
        elif rel in deleted:
            dirty.append(rel)          # backfill deleted it; it is back — an edit since.
    for rel in expected:
        if rel not in seen:
            dirty.append(rel)          # backfill created/modified it; it is gone — an edit since.
    return sorted(set(dirty))


def _legacy_derive_ops(tree: Path, rel_bundle: str) -> list[dict]:
    """THE PRE-RECORD-DRIVEN DERIVATION, retained ONLY as Issue 3.8's mutation switch.

    This is the shipped behaviour EXP-001 measured and `REQ-OKFH-010` forbids: it re-derives the
    operation list from the filesystem at restore time, so it cannot distinguish a file the
    transform CREATED from one that merely happens to be untracked now. It is unreachable except
    via ``OKFH_FORCE_LEGACY_DERIVATION``, and it exists so `check-crash-test-detects-lag.sh
    --req REQ-OKFH-010` can produce the defect by FLIPPING A SWITCH rather than by reconstructing
    a deleted function — a control that must rebuild its own mutant is a control nobody re-runs.

    DO NOT "clean this up". Deleting it does not remove a code path an operator can reach; it
    removes the only reproducible mutant for SC13b, turning that criterion back into an
    assertion nothing tests.
    """
    ops: list[dict] = []
    b = tree / rel_bundle
    for path in sorted(p for p in b.rglob("*") if p.is_file()):
        rel = path.relative_to(tree).as_posix()
        tracked = subprocess.run(["git", "-C", str(tree), "ls-files", "--error-unmatch", rel],
                                 capture_output=True).returncode == 0
        ops.append({"path": rel, "kind": "modified" if tracked else "created",
                    "sha256_before": None, "sha256_after": None})
    return ops


def cmd_restore(a) -> int:
    tree = Path.cwd()
    rp = Path(a.record) if Path(a.record).is_absolute() else tree / a.record

    def refuse(reason: str, **extra) -> int:
        print(json.dumps({"check": CHECK, "command": "restore", "verdict": "refused",
                          "exit": 1, "reason": reason, **extra}, indent=1))
        return 1

    try:
        data = json.loads(rp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"check": CHECK, "command": "restore", "verdict": "inconclusive",
                          "exit": 2, "reason": f"cannot read the record: {exc}"}, indent=1))
        return 2

    # ---- REQ-OKFH-013: refuse an unversioned or unrecognised record ----------------------
    # Read BEFORE anything else, because every guard below is stated in terms of what the
    # record knows — and a legacy record knows nothing. Tolerating it would yield an EMPTY
    # operation list, which a record-driven restore executes as "reverse nothing" and reports
    # as `pass`: a silent no-op wearing a success.
    version = data.get("schema_version")
    if version is None:
        return refuse(
            "the record carries no `schema_version` — it is a LEGACY (pre-REQ-OKFH-013) record "
            "written by a `backfill` that stored a before/after audit verdict and NO operations. "
            "Reading it under the record-driven contract yields an empty operation list, which "
            "would be executed as 'reverse nothing' and reported as success.",
            record_schema_version=None, expected=RECORD_SCHEMA_VERSION,
            remediation="This record cannot drive a reversal. For a committed corpus the "
                        "reversal route is `git revert` of the backfill commit; for an "
                        "uncommitted one, re-run `backfill --apply --record <path>` is NOT a "
                        "reversal and must not be used as one.")
    if version != RECORD_SCHEMA_VERSION:
        return refuse(
            f"unrecognised record `schema_version` {version!r} (this build understands "
            f"{RECORD_SCHEMA_VERSION}). Refusing rather than guessing which fields mean what.",
            record_schema_version=version, expected=RECORD_SCHEMA_VERSION,
            remediation="Use the `okf_hygiene.py` build that wrote this record.")

    entries = data.get("bundles", [])

    # ---- Issue 2.4: the PER-BUNDLE FILTER ------------------------------------------------
    # A batch record that can only be replayed IN FULL makes the safe response to one bad
    # bundle indistinguishable from the destructive one.
    if getattr(a, "bundle", None):
        wanted = set(a.bundle)
        known = {e["bundle"] for e in entries}
        unknown = sorted(wanted - known)
        if unknown:
            return refuse(
                f"--bundle named {unknown} which the record does not contain — refusing rather "
                f"than silently reversing a different set.",
                record_bundles=sorted(known))
        entries = [e for e in entries if e["bundle"] in wanted]
    if not entries:
        print(json.dumps({"check": CHECK, "command": "restore", "verdict": "inconclusive",
                          "exit": 2,
                          "reason": "the record contains no reversible bundle. This is NOT a "
                                    "clean reversal — nothing was examined."}, indent=1))
        return 2

    # ---- REFUSAL 1 (REQ-OKFH-010): a non-git tree ----------------------------------------
    # NOT overridable. `restore`'s mechanism is `git checkout` plus an unlink pass; outside a
    # work tree the checkout is a no-op and the unlink pass is all that runs — measured, that
    # DELETES THE ENTIRE BUNDLE while reporting `pass` and exiting 0.
    if not _is_git_tree(tree):
        return refuse(
            f"{tree} is not a git work tree. `restore` reverses tracked content by `git "
            f"checkout`; without it only the unlink pass would run, which DELETES THE BUNDLE. "
            f"Refusing — this condition is not overridable.",
            remediation="Run `restore` from inside the repository the backfill ran in.")

    plan: list[dict] = []
    for entry in entries:
        rel_bundle = entry["bundle"]
        ops = entry.get("operations") or []
        if os.environ.get(LEGACY_DERIVATION_ENV):
            # Issue 3.8's mutation switch — see `_legacy_derive_ops`.
            ops = _legacy_derive_ops(tree, rel_bundle)

        # ---- REFUSAL 2 (REQ-OKFH-010): the bundle is untracked at HEAD -------------------
        # NOT overridable. This is the realistic case for an uncommitted plan, and it was
        # measured as TOTAL LOSS: nothing to check out, everything unlinked.
        recoverable = [op["path"] for op in ops
                       if op["kind"] in ("modified", "deleted") and _tracked_at_head(tree, op["path"])]
        if not recoverable:
            return refuse(
                f"no path in {rel_bundle!r} is present at HEAD, so `git checkout` can restore "
                f"nothing and only the unlink pass would run — TOTAL LOSS. This is the "
                f"uncommitted-bundle case. Refusing; not overridable.",
                bundle=rel_bundle,
                remediation="Commit the bundle before backfilling, or reverse by other means.")

        # ---- REFUSAL 3 (REQ-OKFH-010): dirty relative to the POST-BACKFILL state ---------
        # Overridable by explicit --force, because a deliberate re-reversal over known local
        # edits is legitimate if rare — but the operator must say so. Measured consequence of
        # NOT guarding it: every untracked file in the bundle unlinked, no warning.
        dirty = _bundle_dirty(tree, rel_bundle, ops)
        if dirty and not a.force:
            return refuse(
                f"{rel_bundle!r} has {len(dirty)} path(s) that differ from the state `backfill` "
                f"left. Reversing would discard those edits without warning. Refusing.",
                bundle=rel_bundle, dirty=dirty[:50],
                remediation="Inspect the listed paths. Re-run with `--force` only if discarding "
                            "them is intended.")

        plan.append({"bundle": rel_bundle, "operations": ops, "dirty": dirty})

    if a.apply:
        for item in plan:
            # A `created` path is ABSENT FROM HEAD and must be UNLINKED — `git checkout` alone
            # would leave every created file behind and report success.
            for op in item["operations"]:
                if op["kind"] == "created":
                    (tree / op["path"]).unlink(missing_ok=True)
            paths = [op["path"] for op in item["operations"]
                     if op["kind"] in ("modified", "deleted")]
            if paths:
                subprocess.run(["git", "-C", str(tree), "checkout", "--", *paths],
                               capture_output=True)

    print(json.dumps({"check": CHECK, "command": "restore", "apply": bool(a.apply),
                      "record_schema_version": version,
                      "bundles": [i["bundle"] for i in plan],
                      "operations": [op for i in plan for op in i["operations"]],
                      "forced": bool(a.force),
                      "verdict": "pass", "exit": 0}, indent=1))
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
    p.add_argument("--reconcile-objective", action="store_true",
                   help="adopt plan.md's H1 as authoritative for a divergent legacy objective "
                        "line instead of halting (REQ-OKFH-012). OPT-IN: the halt is the "
                        "default, and each rewrite is reported per bundle.")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_backfill)

    p = sub.add_parser("reindex", help="index repair; REFUSES a legacy prose index")
    p.add_argument("bundle")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_reindex)

    p = sub.add_parser("recover", help="finish or roll back an interrupted backfill (REQ-OKFH-008)")
    p.add_argument("--bundle", action="append", default=None,
                   help="recover ONLY these bundles (repeatable)")
    p.add_argument("--apply", action="store_true", help="perform the recovery (dry-run default)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_recover)

    p = sub.add_parser("restore", help="record-driven reversal, per-path operation kind")
    p.add_argument("--record", required=True)
    p.add_argument("--bundle", action="append", default=None,
                   help="reverse ONLY these bundles from the record (repeatable). Without it "
                        "the whole batch is reversed (REQ-OKFH-010 per-bundle filter).")
    p.add_argument("--force", action="store_true",
                   help="override ONLY the dirty-bundle refusal. The non-git-tree and "
                        "untracked-at-HEAD refusals are NOT overridable — there is no state in "
                        "which deleting an unrecoverable bundle is the operator's intent.")
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
