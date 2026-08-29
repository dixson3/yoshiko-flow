#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""churn_signature.py — git-history churn signals for one plan bundle's commit window.

Read-only (`git log`/`git show` only; never mutates the corpus repos). For a plan bundle,
finds the commit window a plan touched — the union of (a) commits whose path-scoped `git log`
touches the bundle directory itself (`docs/plans/<id>/**` or `Incubator/*/plans/<id>/**`) and
(b) commits on the current branch whose message mentions the plan's short id (`plan-NNN`),
which is how this corpus's commit convention (`plan-NNN Issue X.Y: ...`, `plan-NNN: ...`)
attributes CODE commits to a plan that the path-scoped log alone would miss (the bundle's docs
commits and the plan's implementation commits are mostly disjoint commit sets).

Within that window it reports two churn signals, each with a resolvable commit SHA:

  1. Revert/redo COMMIT-MESSAGE patterns: "revert", "redo", "take 2"/"take two", "actually",
     "fix the fix", "oops", "undo", "wrong" / "incorrect" (as a correction admission, not just
     a description), "correct ... in place". Conservative — a plain `git revert` commit is a
     strong signal; the free-text patterns are weaker and are reported with the MATCHED PHRASE
     so a human can judge false positives (a commit that says "this was wrong before" is not
     automatically thrash — it may be the FIRST and only fix).
  2. File re-touch counts: files (outside the bundle's own doc directory) touched by >= 3
     distinct commits within the window — a candidate "re-touched for one purpose" signal per
     the research plan's `git-churn-signatures` source cluster. Reports every touching commit
     SHA for each such file, not just the count.

Usage:
    uv run churn_signature.py --bundle <path/to/plan-bundle-dir> [--repo-root <path>] [--json]
    uv run churn_signature.py --census <corpus_scan.json> [--min-file-touches 3] [--json]

Exit codes:
    0  ran to completion
    1  named bundle/census path does not exist, or repo is not a git work tree
    2  bad arguments
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

REVERT_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("literal_revert", re.compile(r'^revert\b', re.IGNORECASE)),
    ("redo", re.compile(r'\bredo\b', re.IGNORECASE)),
    ("take_n", re.compile(r'\btake (?:2|3|4|two|three|four) \b|\btake-\d\b', re.IGNORECASE)),
    ("actually", re.compile(r'\bactually\b', re.IGNORECASE)),
    ("fix_the_fix", re.compile(r"\bfix(?:ed|ing)? the fix\b|\bre-?fix\b", re.IGNORECASE)),
    ("oops_undo", re.compile(r'\boops\b|\bundo\b', re.IGNORECASE)),
    ("wrong_correction", re.compile(r'\bwas wrong\b|\bwrong (?:in place|again|three ways|twice)\b|\bincorrect(?:ly)?\b.*\bfix', re.IGNORECASE)),
    ("correct_in_place", re.compile(r'\bcorrect\b.*\bin place\b', re.IGNORECASE)),
    ("still_broken", re.compile(r'\bstill (?:broken|wrong|fails?|failing)\b', re.IGNORECASE)),
]

PLAN_ID_RE = re.compile(r"^(plan-\d+)")


@dataclass
class Commit:
    sha: str
    date: str
    subject: str
    files: list[str]


@dataclass
class ChurnSignal:
    sha: str
    date: str
    subject: str
    pattern: str
    matched_phrase: str


@dataclass
class FileRetouch:
    file: str
    touch_count: int
    commits: list[str]  # shas


@dataclass
class BundleChurn:
    bundle: str
    plan_short_id: str | None
    repo_root: str
    commit_window_start: str | None
    commit_window_end: str | None
    total_commits_in_window: int
    path_scoped_commits: int
    grep_scoped_commits: int
    churn_signals: list[ChurnSignal]
    repeatedly_touched_files: list[FileRetouch]
    error: str | None = None


def run_git(repo_root: Path, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.returncode, proc.stdout, proc.stderr


def find_repo_root(bundle_dir: Path) -> Path | None:
    rc, out, _err = run_git(bundle_dir, ["rev-parse", "--show-toplevel"])
    if rc != 0 or not out.strip():
        return None
    return Path(out.strip())


def log_commits(repo_root: Path, args: list[str]) -> list[tuple[str, str, str]]:
    """Returns list of (sha, date_iso, subject), newest first."""
    rc, out, err = run_git(repo_root, ["log", "--format=%H%x1f%aI%x1f%s", *args])
    if rc != 0:
        return []
    commits = []
    for line in out.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        commits.append((parts[0], parts[1], parts[2]))
    return commits


def files_for_commit(repo_root: Path, sha: str) -> list[str]:
    rc, out, _err = run_git(repo_root, ["show", "--name-only", "--format=", sha])
    if rc != 0:
        return []
    return [f for f in out.strip().split("\n") if f]


def scan_bundle_churn(bundle_dir: Path, repo_root_override: Path | None, min_file_touches: int) -> BundleChurn:
    repo_root = repo_root_override or find_repo_root(bundle_dir)
    if repo_root is None:
        return BundleChurn(
            bundle=str(bundle_dir),
            plan_short_id=None,
            repo_root="",
            commit_window_start=None,
            commit_window_end=None,
            total_commits_in_window=0,
            path_scoped_commits=0,
            grep_scoped_commits=0,
            churn_signals=[],
            repeatedly_touched_files=[],
            error=f"{bundle_dir} is not inside a git work tree",
        )

    rel = bundle_dir.relative_to(repo_root)
    plan_dir_name = bundle_dir.name
    m = PLAN_ID_RE.match(plan_dir_name)
    short_id = m.group(1) if m else None

    path_commits = log_commits(repo_root, ["--follow", "--", str(rel)])
    grep_commits: list[tuple[str, str, str]] = []
    if short_id:
        grep_commits = log_commits(repo_root, [f"--grep={short_id}", "-i"])

    by_sha: dict[str, tuple[str, str]] = {}
    for sha, date, subj in path_commits + grep_commits:
        by_sha[sha] = (date, subj)

    if not by_sha:
        return BundleChurn(
            bundle=str(bundle_dir),
            plan_short_id=short_id,
            repo_root=str(repo_root),
            commit_window_start=None,
            commit_window_end=None,
            total_commits_in_window=0,
            path_scoped_commits=0,
            grep_scoped_commits=0,
            churn_signals=[],
            repeatedly_touched_files=[],
            error=None,
        )

    ordered = sorted(by_sha.items(), key=lambda kv: kv[1][0])  # by date asc
    window_start = ordered[0][1][0]
    window_end = ordered[-1][1][0]

    commits: list[Commit] = []
    for sha, (date, subj) in ordered:
        files = files_for_commit(repo_root, sha)
        commits.append(Commit(sha=sha, date=date, subject=subj, files=files))

    # churn signals from commit-message patterns
    signals: list[ChurnSignal] = []
    for c in commits:
        for pattern_name, rx in REVERT_PATTERNS:
            mm = rx.search(c.subject)
            if mm:
                signals.append(
                    ChurnSignal(
                        sha=c.sha, date=c.date, subject=c.subject,
                        pattern=pattern_name, matched_phrase=mm.group(0),
                    )
                )

    # file re-touch counts, excluding files inside the bundle's own doc directory
    bundle_prefix = str(rel) + "/"
    file_commits: dict[str, list[str]] = {}
    for c in commits:
        for f in c.files:
            if f.startswith(bundle_prefix):
                continue
            file_commits.setdefault(f, []).append(c.sha)

    retouched = [
        FileRetouch(file=f, touch_count=len(shas), commits=shas)
        for f, shas in file_commits.items()
        if len(shas) >= min_file_touches
    ]
    retouched.sort(key=lambda r: -r.touch_count)

    return BundleChurn(
        bundle=str(bundle_dir),
        plan_short_id=short_id,
        repo_root=str(repo_root),
        commit_window_start=window_start,
        commit_window_end=window_end,
        total_commits_in_window=len(commits),
        path_scoped_commits=len(path_commits),
        grep_scoped_commits=len(grep_commits),
        churn_signals=signals,
        repeatedly_touched_files=retouched,
        error=None,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--bundle", type=Path, help="path to a single plan bundle directory")
    src.add_argument("--census", type=Path, help="corpus_scan.py --json output; process every bundle it names")
    ap.add_argument("--min-file-touches", type=int, default=3, help="minimum distinct commits touching one file within the window to report it (default 3)")
    ap.add_argument("--json", action="store_true", help="emit JSON (default: human summary)")
    args = ap.parse_args()

    bundle_dirs: list[Path] = []
    if args.bundle:
        if not args.bundle.is_dir():
            print(f"error: bundle path does not exist: {args.bundle}", file=sys.stderr)
            return 1
        bundle_dirs = [args.bundle]
    else:
        if not args.census.is_file():
            print(f"error: census file does not exist: {args.census}", file=sys.stderr)
            return 1
        census = json.loads(args.census.read_text())
        for repo in census.get("repos", []):
            for b in repo.get("bundles", []):
                bundle_dirs.append(Path(b["bundle_path"]))

    if not bundle_dirs:
        print("error: no bundles to process", file=sys.stderr)
        return 1

    results = [scan_bundle_churn(bd, None, args.min_file_touches) for bd in bundle_dirs]

    error_bundles = [r.bundle for r in results if r.error]
    total_signals = sum(len(r.churn_signals) for r in results)
    total_retouch = sum(len(r.repeatedly_touched_files) for r in results)

    if args.json:
        out = {
            "bundles_processed": len(results),
            "bundles_with_errors": error_bundles,
            "total_churn_signals": total_signals,
            "total_repeatedly_touched_files": total_retouch,
            "results": [asdict(r) for r in results],
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"bundles processed: {len(results)}")
        print(f"churn signals (commit-message patterns): {total_signals}")
        print(f"repeatedly-touched files (>= {args.min_file_touches} commits in window): {total_retouch}")
        if error_bundles:
            print(f"bundles with errors: {error_bundles}", file=sys.stderr)
        for r in results:
            if r.churn_signals or r.repeatedly_touched_files:
                print(f"\n--- {r.bundle} ({r.commit_window_start} .. {r.commit_window_end}, {r.total_commits_in_window} commits) ---")
                for s in r.churn_signals:
                    print(f"  [{s.pattern}] {s.sha[:10]} {s.date} \"{s.subject[:90]}\" (matched: {s.matched_phrase!r})")
                for f in r.repeatedly_touched_files:
                    print(f"  RETOUCH x{f.touch_count}: {f.file} ({', '.join(sh[:10] for sh in f.commits)})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
