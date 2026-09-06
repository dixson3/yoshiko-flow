#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""plan-065's verification instrument — ONE script, eleven subcommands.

Every subcommand answers exactly one question about the repository or about an
artifact this plan wrote, and answers it with an **exit code**:

    0  PASS          — the condition holds
    1  FALSE         — the condition was checked and does NOT hold
    2  INCONCLUSIVE  — the check could not run (input absent, tool missing, bad JSON)

**2 IS NOT 1, AND THE DISTINCTION IS THE POINT.** A `FileNotFoundError` says the
instrument is absent, not that the condition is false — plan-065 Issue 0.5 exists
because an absent input had been read as evidence. Every INCONCLUSIVE carries
`reason: "input absent"` (or another explicit reason) in its JSON envelope so a
caller can tell the two apart without guessing.

Ten subcommands are the set Issue 0.1 enumerates:

    audit-strict        bundle-shape        phaselog-bullets    merged-objectives
    no-engine-edits     index-drift-strict  apply-result        restore-roundtrip
    finding-counts      negative-controls

An eleventh, `registered`, is required by SC15 (it verifies this script is wired
into CHANGE-VALIDATION.md's FULL tier). It is deliberately outside the "ten"
because it is a check on the *manifest*, not on the corpus or on a plan artifact.

FOUR of the ten are **tree-property** subcommands — they read the repository
itself and can therefore report FALSE before this plan has written anything:

    audit-strict  bundle-shape  phaselog-bullets  index-drift-strict

The other six read artifacts this plan creates. Pre-transform they can only say
"input absent" (exit 2), which Issue 0.5 must REJECT as a FALSE report.

`--input PATH` overrides the artifact path for every artifact-reading subcommand,
so the negative controls in Issue 0.4 can be driven from synthesized fixtures
**without mutating the live repository** (SC12 forbids touching engine sources,
and a literal "mutate the condition" for `no-engine-edits` would breach it).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CHECK = "plan065-checks"

PLAN_ID = "plan-065-james-dixson-7c8cd4"
PLAN_DIR = f"docs/plans/{PLAN_ID}"
FINDINGS = f"{PLAN_DIR}/findings"

#: The eight legacy-readme bundles this plan transforms. Pinned, not discovered:
#: a discovered list is empty-able, and an empty list makes `bundle-shape`
#: vacuously green (R9). `bundle-shape` asserts the list is non-empty anyway.
TARGETS = [
    "docs/plans/plan-010-james-dixson-73eebd",
    "docs/plans/plan-012-james-dixson-a99822",
    "docs/plans/plan-013-james-dixson-0af2f8",
    "docs/plans/plan-014-james-dixson-916de2",
    "docs/plans/plan-021-james-dixson-bb3558",
    "docs/plans/plan-023-james-dixson-b618bb",
    "docs/plans/plan-026-james-dixson-6e0e2f",
    "docs/plans/plan-030-james-dixson-65526e",
]

#: The corpus floor. `legacy == 0` alone is blind to the measured failure mode:
#: `legacy` sums only legacy-readme + legacy-underscore-index + hybrid-partial
#: (okf_hygiene.py:977-978), so a bundle wrecked into `unclassifiable` yields
#: `legacy: 0`, `verdict: pass`, exit 0. The floor closes the enumerate-nothing
#: vacuity on top of that.
MIN_BUNDLES = 70

#: The two merged objectives from exp-001, verbatim. Each MUST be one physical
#: line: `_objective()` (okf_hygiene.py:565) matches with `.` excluding newline,
#: so a soft-wrapped H1 is silently truncated.
MERGED_OBJECTIVES = {
    "docs/plans/plan-010-james-dixson-73eebd":
        "Rename skills to `yf-` prefix and build the `yf` Rust CLI — skill install/upgrade "
        "lifecycle, Homebrew distribution, replacing `install.{sh,py}`",
    "docs/plans/plan-013-james-dixson-0af2f8":
        "Reconcile policy — local beads = active work only; non-active work lives upstream "
        "until pulled via a plan (yf-beads-hygiene reconcile pass + yf-beads-upstream "
        "land-the-plane hoist-and-remove)",
}

PLAN_030 = "docs/plans/plan-030-james-dixson-65526e"

#: plan-030's ten phase-log bullets, DATE PREFIX STRIPPED, embedded literally.
#: The input VANISHES — Issue 2.2 deletes the `**Phase log:**` block — so the
#: expectation cannot be re-derived from the tree after the repair lands.
#: Compared as BULLET TEXT, never as dates: the engine's own guard compares
#: dates only and would not catch a lost bullet under a surviving date (R2).
PHASELOG_BULLETS = [
    "scoping: initial scope captured",
    "scoping: upstream #89 triaged (include); 3 scope decisions resolved (detection / enforcement / evidence)",
    "drafting: plan v1 presented",
    "review: plan v1 presented",
    "review: pass-1 REVISE resolved (C1-C4); re-review",
    "ready-for-approval: ready-check green — last red-team APPROVE (pass-2) + audit pass",
    "approved: operator approved",
    "intake: epic yf-mol-tmm poured",
    "executing: start gate resolved",
    "reconciling: post-execution reconciliation",
]

#: Engine sources SC12 forbids this plan from modifying.
ENGINE_PATTERNS = (
    re.compile(r"^skills/.*\.py$"),
    re.compile(r"^_shared/[^/]*\.py$"),
)

TREE_PROPERTY = ("audit-strict", "bundle-shape", "phaselog-bullets", "index-drift-strict")

#: The ten Issue 0.1 enumerates. `registered` is intentionally absent (see module docstring).
TEN = (
    "audit-strict", "bundle-shape", "phaselog-bullets", "merged-objectives",
    "no-engine-edits", "index-drift-strict", "apply-result", "restore-roundtrip",
    "finding-counts", "negative-controls",
)


class Inconclusive(Exception):
    """The check could not run. Always exit 2, never 1."""


def repo_root() -> Path:
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return Path(r.stdout.strip())
    # Fall back to this file's location: scripts/checks/plan065_checks.py
    return Path(__file__).resolve().parents[2]


def load_artifact(root: Path, default_rel: str, override: str | None):
    """THE MISSING-INPUT CONTRACT, implemented ONCE.

    Absent -> Inconclusive("input absent"). Unparseable -> Inconclusive.
    Neither is ever FALSE.
    """
    p = Path(override) if override else (root / default_rel)
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    if not p.exists():
        raise Inconclusive(f"input absent: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8")), p
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise Inconclusive(f"input unreadable: {p}: {exc}") from exc


def run_json(root: Path, args: list[str]) -> dict:
    """Run a repo tool that speaks --json and parse stdout. Never trusts exit code."""
    try:
        r = subprocess.run(args, capture_output=True, text=True, cwd=root)
    except OSError as exc:
        raise Inconclusive(f"could not execute {args[0]}: {exc}") from exc
    out = r.stdout.strip()
    if not out:
        raise Inconclusive(f"{' '.join(args[:3])} produced no JSON (exit {r.returncode}): "
                           f"{r.stderr.strip()[:300]}")
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise Inconclusive(f"{' '.join(args[:3])} JSON unparseable: {exc}") from exc


# --------------------------------------------------------------------------
# subcommands. Each returns (ok: bool, reason: str, detail: dict)
# --------------------------------------------------------------------------

def sub_audit_strict(root: Path, a) -> tuple[bool, str, dict]:
    if a.input:
        d, _ = load_artifact(root, "", a.input)
    else:
        d = run_json(root, ["uv", "run", "skills/yf-okf-hygiene/scripts/okf_hygiene.py",
                            "audit", "--json"])
    counts = d.get("counts") or {}
    legacy = d.get("legacy")
    checked = d.get("bundles_checked")
    if legacy is None or checked is None or not counts:
        raise Inconclusive("audit JSON missing legacy/bundles_checked/counts")
    fails = []
    if legacy != 0:
        fails.append(f"legacy={legacy} (want 0)")
    if counts.get("unclassifiable", 0) != 0:
        fails.append(f"unclassifiable={counts.get('unclassifiable')} (want 0)")
    if counts.get("hybrid-partial", 0) != 0:
        fails.append(f"hybrid-partial={counts.get('hybrid-partial')} (want 0)")
    if checked < MIN_BUNDLES:
        fails.append(f"bundles_checked={checked} (want >= {MIN_BUNDLES})")
    detail = {"legacy": legacy, "bundles_checked": checked, "counts": counts,
              "verdict_reported_by_audit": d.get("verdict")}
    return (not fails), ("; ".join(fails) or "legacy 0, no unclassifiable/hybrid, corpus floor met"), detail


def sub_bundle_shape(root: Path, a) -> tuple[bool, str, dict]:
    targets = TARGETS
    if a.input:
        d, _ = load_artifact(root, "", a.input)
        targets = d.get("targets", [])
    if not targets:
        return False, "target list is EMPTY — the check would be vacuous", {"targets": []}
    rows, fails = [], []
    for t in targets:
        b = root / t
        row = {"bundle": t,
               "index.md": (b / "index.md").is_file(),
               "log.md": (b / "log.md").is_file(),
               "README.md": (b / "README.md").is_file()}
        rows.append(row)
        if not row["index.md"] or not row["log.md"] or row["README.md"]:
            fails.append(t)
    return (not fails), (f"{len(fails)} bundle(s) wrong shape: {fails}" if fails
                         else f"all {len(targets)} bundles carry index.md + log.md and no README.md"), \
           {"targets": targets, "rows": rows}


def sub_phaselog_bullets(root: Path, a) -> tuple[bool, str, dict]:
    if len(PHASELOG_BULLETS) != 10:
        raise Inconclusive(f"embedded expectation is {len(PHASELOG_BULLETS)} bullets, not 10")
    log = Path(a.input) if a.input else (root / PLAN_030 / "log.md")
    if not log.exists():
        raise Inconclusive(f"input absent: {log}")
    text = log.read_text(encoding="utf-8")
    missing = [b for b in PHASELOG_BULLETS if b not in text]
    return (not missing), (f"{len(missing)} bullet(s) missing from log.md: {missing}" if missing
                           else "all 10 phase-log bullets present in log.md"), \
           {"log": str(log), "expected": len(PHASELOG_BULLETS), "missing": missing}


def _objective_line(path: Path) -> str | None:
    """The reserved index.md's `> ` objective line, first one wins."""
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("> "):
            return line[2:].strip()
    return None


def sub_merged_objectives(root: Path, a) -> tuple[bool, str, dict]:
    expected = MERGED_OBJECTIVES
    base = root
    if a.input:
        d, p = load_artifact(root, "", a.input)
        expected = d.get("expected", {})
        base = Path(d.get("root", str(root)))
    rows, fails = [], []
    for bundle, want in expected.items():
        got = _objective_line(base / bundle / "index.md")
        rows.append({"bundle": bundle, "want": want, "got": got, "match": got == want})
        if got != want:
            fails.append(bundle)
    if not rows:
        return False, "no merged objectives to check — vacuous", {"rows": rows}
    return (not fails), (f"{len(fails)} objective(s) differ: {fails}" if fails
                         else f"{len(rows)} merged objective(s) match verbatim"), {"rows": rows}


def sub_no_engine_edits(root: Path, a) -> tuple[bool, str, dict]:
    base_file = Path(a.input) if a.input else (root / FINDINGS / "diff-base.txt")
    if not base_file.exists():
        raise Inconclusive(f"input absent: {base_file} (Issue 0.2 pins the diff base)")
    base = base_file.read_text(encoding="utf-8").strip()
    if not base:
        raise Inconclusive(f"pinned diff base is EMPTY in {base_file}")
    r = subprocess.run(["git", "diff", "--name-only", base], capture_output=True, text=True, cwd=root)
    if r.returncode != 0:
        raise Inconclusive(f"git diff against {base} failed: {r.stderr.strip()[:200]}")
    changed = [p for p in r.stdout.splitlines() if p.strip()]
    u = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                       capture_output=True, text=True, cwd=root)
    untracked = [p for p in u.stdout.splitlines() if p.strip()]
    all_paths = sorted(set(changed) | set(untracked))
    hits = [p for p in all_paths if any(pat.match(p) for pat in ENGINE_PATTERNS)]
    return (not hits), (f"{len(hits)} engine source(s) modified: {hits}" if hits
                        else f"no engine source touched across {len(all_paths)} changed path(s)"), \
           {"base": base, "changed": len(changed), "untracked": len(untracked), "engine_hits": hits}


def sub_index_drift_strict(root: Path, a) -> tuple[bool, str, dict]:
    if a.input:
        d, _ = load_artifact(root, "", a.input)
    else:
        d = run_json(root, ["uv", "run", "scripts/checks/check_okf_index_drift.py",
                            "--min-roots", "30", "--json"])
    exit_code = d.get("exit")
    no_index = d.get("no_index")
    if exit_code is None or no_index is None:
        raise Inconclusive("index-drift JSON missing exit/no_index")
    fails = []
    if exit_code != 0:
        fails.append(f"check exit={exit_code} verdict={d.get('verdict')} ({d.get('reason')})")
    # `no_index` contributes NOTHING to the bare check's verdict — measured at
    # drafting it reported no_index: 8 and still exited 0. This is the addition.
    if no_index != 0:
        fails.append(f"no_index={no_index} (want 0)")
    return (not fails), ("; ".join(fails) or "index-drift green and no_index == 0"), \
           {"exit": exit_code, "no_index": no_index, "drifting": d.get("drifting"),
            "bundles_checked": d.get("bundles_checked"), "rows": d.get("rows")}


def sub_apply_result(root: Path, a) -> tuple[bool, str, dict]:
    d, p = load_artifact(root, f"{FINDINGS}/apply-result.json", a.input)
    transformed = d.get("transformed")
    halted = d.get("halted")
    checked = d.get("bundles_checked")
    bundles = d.get("bundles")
    if transformed is None or halted is None or checked is None or bundles is None:
        raise Inconclusive("apply-result JSON missing transformed/halted/bundles_checked/bundles")
    # NOT "8 bundle rows": the run JSON carries one row per bundle CHECKED.
    backfilled = [b for b in bundles if b.get("action") == "backfilled"]
    fails = []
    if transformed != 8:
        fails.append(f"transformed={transformed} (want 8)")
    if halted != 0:
        fails.append(f"halted={halted} (want 0)")
    if checked < MIN_BUNDLES:
        fails.append(f"bundles_checked={checked} (want >= {MIN_BUNDLES})")
    if len(backfilled) != 8:
        fails.append(f"rows with action=backfilled: {len(backfilled)} (want exactly 8)")
    return (not fails), ("; ".join(fails) or "8 transformed, 0 halted, 8 backfilled rows, corpus floor met"), \
           {"input": str(p), "transformed": transformed, "halted": halted,
            "bundles_checked": checked, "backfilled": [b.get("bundle") for b in backfilled]}


def sub_restore_roundtrip(root: Path, a) -> tuple[bool, str, dict]:
    d, p = load_artifact(root, f"{FINDINGS}/restore-roundtrip.json", a.input)
    need = ("pre_backfill", "post_backfill", "post_reversal", "post_reapply")
    missing = [k for k in need if k not in d]
    if missing:
        raise Inconclusive(f"restore-roundtrip JSON missing keys: {missing}")
    pre, post, rev, re_ = (d["pre_backfill"], d["post_backfill"],
                           d["post_reversal"], d["post_reapply"])
    fails = []
    if post != re_:
        fails.append("post_backfill != post_reapply (re-apply did not reproduce the transform)")
    if rev != pre:
        fails.append("post_reversal != pre_backfill (restore did not reverse cleanly)")
    # LOAD-BEARING. An earlier draft asserted pre- and post-reversal were EQUAL and
    # said nothing about post_backfill — which is exactly what a NO-OP restore
    # produces. That draft would have reported green on the silent total-loss path.
    if rev == post:
        fails.append("post_reversal == post_backfill — restore was a NO-OP, not a reversal")
    return (not fails), ("; ".join(fails) or "round-trip clean and demonstrably non-vacuous"), \
           {"input": str(p),
            "pre_backfill": pre, "post_backfill": post,
            "post_reversal": rev, "post_reapply": re_}


def _finding_count(root: Path, bundle: str) -> int:
    d = run_json(root, ["uv", "run", "skills/yf-okf/scripts/okf.py", "check", bundle, "--json"])
    f = d.get("findings")
    if f is None:
        raise Inconclusive(f"okf.py check {bundle} returned no findings list")
    return len(f)


def sub_finding_counts(root: Path, a) -> tuple[bool, str, dict]:
    before, p = load_artifact(root, f"{FINDINGS}/finding-counts-before.json", a.input)
    counts = before.get("counts") if isinstance(before, dict) else None
    if not isinstance(counts, dict) or not counts:
        raise Inconclusive("finding-counts-before.json has no non-empty `counts` object")
    after_override = None
    if a.after:
        after_override, _ = load_artifact(root, "", a.after)
        after_override = after_override.get("counts", {})
    rows, fails = [], []
    decreased = 0
    for bundle, b4 in sorted(counts.items()):
        aft = after_override.get(bundle) if after_override is not None else _finding_count(root, bundle)
        if aft is None:
            raise Inconclusive(f"no after-count available for {bundle}")
        rows.append({"bundle": bundle, "before": b4, "after": aft, "delta": aft - b4})
        if aft > b4:
            fails.append(f"{bundle}: {b4} -> {aft} (REGRESSED)")
        if aft < b4:
            decreased += 1
    if decreased == 0:
        fails.append("no bundle strictly decreased — the transform improved nothing")
    return (not fails), ("; ".join(fails) or
                         f"no regression across {len(rows)} bundle(s); {decreased} strictly decreased"), \
           {"input": str(p), "rows": rows, "decreased": decreased}


def sub_negative_controls(root: Path, a) -> tuple[bool, str, dict]:
    d, p = load_artifact(root, f"{FINDINGS}/negative-controls.json", a.input)
    rows = d.get("rows") if isinstance(d, dict) else None
    if not isinstance(rows, list):
        raise Inconclusive("negative-controls.json has no `rows` list")
    fails = []
    # "ten rows all with exit != 0". Implemented as: every one of the TEN enumerated
    # subcommands has a control row, and NO row records a passing exit. Stated as a
    # coverage set rather than len()==10 so an extra control (e.g. `registered`)
    # strengthens the evidence instead of failing the check.
    covered = {r.get("subcommand") for r in rows}
    uncovered = [s for s in TEN if s not in covered]
    if uncovered:
        fails.append(f"no negative control recorded for: {uncovered}")
    if len(rows) < 10:
        fails.append(f"{len(rows)} control row(s) recorded (want >= 10)")
    passing = [r for r in rows if r.get("exit") in (0, None)]
    if passing:
        fails.append(f"{len(passing)} control(s) did NOT report non-zero: "
                     f"{[r.get('subcommand') for r in passing]}")
    for r in rows:
        if not r.get("mutation"):
            fails.append(f"control for {r.get('subcommand')} records no mutation")
    # The Issue 0.5 half: a recorded FALSE (exit 1) — never "input absent" — for
    # every tree-property subcommand, against the pre-transform tree.
    tp = d.get("tree_property_false")
    if not isinstance(tp, list):
        fails.append("no `tree_property_false` list (Issue 0.5 evidence, SC14)")
    else:
        tp_by = {r.get("subcommand"): r for r in tp}
        for s in TREE_PROPERTY:
            r = tp_by.get(s)
            if r is None:
                fails.append(f"no pre-transform FALSE recorded for tree-property `{s}`")
                continue
            if r.get("exit") != 1:
                fails.append(f"tree-property `{s}` recorded exit {r.get('exit')} — "
                             f"only exit 1 is a FALSE report")
            reason = (r.get("reason") or "").lower()
            if "input absent" in reason or "could not run" in reason:
                fails.append(f"tree-property `{s}` recorded `{reason}` — an absent input "
                             f"is NOT evidence the condition is false")
    return (not fails), ("; ".join(fails) or
                         f"{len(rows)} negative controls all non-zero; "
                         f"{len(TREE_PROPERTY)} tree-property FALSE reports recorded"), \
           {"input": str(p), "rows": len(rows), "covered": sorted(covered)}


def _full_tier_rows(text: str) -> list[dict]:
    """Parse §1 Tiers -> ### full -> the GFM table. STRUCTURAL, never a substring grep.

    A comment, a blockquote line, or a stale FAST row must not satisfy `registered`.
    """
    lines = text.splitlines()
    # locate `## 1. Tiers`
    try:
        t0 = next(i for i, l in enumerate(lines) if re.match(r"^##\s+1\.\s+Tiers\s*$", l))
    except StopIteration:
        raise Inconclusive("CHANGE-VALIDATION.md has no `## 1. Tiers` section")
    t1 = next((i for i in range(t0 + 1, len(lines)) if re.match(r"^##\s+(?!#)", lines[i])), len(lines))
    try:
        f0 = next(i for i in range(t0, t1) if re.match(r"^###\s+full\s*$", lines[i]))
    except StopIteration:
        raise Inconclusive("§1 Tiers has no `### full` subsection")
    f1 = next((i for i in range(f0 + 1, t1) if re.match(r"^###\s+", lines[i])), t1)
    rows = []
    for line in lines[f0 + 1:f1]:
        s = line.strip()
        if not s.startswith("|") or s.startswith(">"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if set(cells[0]) <= set(":- ") and set(cells[1]) <= set(":- "):
            continue  # alignment row
        if cells[0] == "id" and cells[1] == "cmd":
            continue  # header row
        rows.append({"id": cells[0].strip("`"), "cmd": cells[1].strip("`")})
    return rows


def sub_registered(root: Path, a) -> tuple[bool, str, dict]:
    manifest = Path(a.input) if a.input else (root / "CHANGE-VALIDATION.md")
    if not manifest.exists():
        raise Inconclusive(f"input absent: {manifest}")
    rows = _full_tier_rows(manifest.read_text(encoding="utf-8"))
    if not rows:
        raise Inconclusive("§1 `### full` table parsed to zero rows")
    mine = [r for r in rows if "scripts/checks/plan065_checks.py" in r["cmd"]]
    fails = []
    if not mine:
        fails.append("no FULL-tier row invokes scripts/checks/plan065_checks.py")
    else:
        # The two subcommands Issue 5.4c requires, read from the row's ARGV.
        args_seen = set()
        for r in mine:
            toks = r["cmd"].split()
            try:
                i = next(k for k, t in enumerate(toks) if t.endswith("plan065_checks.py"))
            except StopIteration:
                continue
            args_seen.update(t for t in toks[i + 1:] if not t.startswith("-"))
        for want in ("audit-strict", "bundle-shape"):
            if want not in args_seen:
                fails.append(f"no FULL-tier row runs subcommand `{want}`")
    return (not fails), ("; ".join(fails) or
                         f"{len(mine)} FULL-tier row(s) invoke plan065_checks.py"), \
           {"manifest": str(manifest), "full_tier_rows": len(rows),
            "matching_rows": [r["id"] or "(unnamed)" for r in mine],
            "commands": [r["cmd"] for r in mine]}


SUBCOMMANDS = {
    "audit-strict": sub_audit_strict,
    "bundle-shape": sub_bundle_shape,
    "phaselog-bullets": sub_phaselog_bullets,
    "merged-objectives": sub_merged_objectives,
    "no-engine-edits": sub_no_engine_edits,
    "index-drift-strict": sub_index_drift_strict,
    "apply-result": sub_apply_result,
    "restore-roundtrip": sub_restore_roundtrip,
    "finding-counts": sub_finding_counts,
    "negative-controls": sub_negative_controls,
    "registered": sub_registered,
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="plan065_checks.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("subcommand", choices=sorted(SUBCOMMANDS))
    ap.add_argument("--input", help="override the artifact this subcommand reads "
                                    "(negative-control fixtures; never mutates the repo)")
    ap.add_argument("--after", help="finding-counts only: read after-counts from a fixture "
                                    "instead of running okf.py check live")
    ap.add_argument("--json", action="store_true", help="emit the JSON envelope")
    ap.add_argument("--root", help="repository root (default: git toplevel)")
    a = ap.parse_args(argv)

    root = Path(a.root).resolve() if a.root else repo_root()
    fn = SUBCOMMANDS[a.subcommand]
    try:
        ok, reason, detail = fn(root, a)
        verdict, code = ("PASS", 0) if ok else ("FALSE", 1)
    except Inconclusive as exc:
        verdict, code, reason, detail = "INCONCLUSIVE", 2, str(exc), {}
    except Exception as exc:  # an instrument crash is INCONCLUSIVE, never FALSE
        verdict, code, reason, detail = "INCONCLUSIVE", 2, f"{type(exc).__name__}: {exc}", {}

    env = {"check": CHECK, "subcommand": a.subcommand, "verdict": verdict,
           "exit": code, "reason": reason, "root": str(root), "detail": detail}
    if a.json:
        print(json.dumps(env, indent=1))
    else:
        print(f"{verdict} ({code}) {a.subcommand}: {reason}")
    return code


if __name__ == "__main__":
    sys.exit(main())
