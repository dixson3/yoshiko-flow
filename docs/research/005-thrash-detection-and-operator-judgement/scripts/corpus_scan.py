#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""corpus_scan.py — census of every plan bundle across the yf-research-005 corpus.

Read-only. Enumerates plan bundles under docs/plans/** and Incubator/*/plans/** in each
configured repo, and emits one JSON record per bundle: repo, plan id, path, review-pass
count, presence of context.md/log.md/index.md, mtime span of the bundle's files, and the
first/last git commit that touched the bundle (from `git log --follow`-free plain log, since
bundle dirs are not renamed in this corpus).

This is the census the rest of the 005 study indexes on — every other script's `--bundle`
argument is a path this script emitted.

Usage:
    uv run corpus_scan.py [--repos-file repos.json] [--json] [--repo NAME]

Exit codes:
    0  ran to completion (individual repo failures are reported in the output, not fatal)
    1  no repos configured / all repos missing
    2  bad arguments
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_REPOS: dict[str, str] = {
    "yoshiko-flow": "~/workspace/dixson3/yoshiko-flow",
    "d3-pxe": "~/workspace/dixson3/d3-pxe",
    "evri_py": "~/workspace/evri/evri_py",
    "writing": "~/workspace/dixson3/writing",
    "pybridge": "~/workspace/evri/pybridge",
    "emacs.d": "~/_dotfiles/emacs.d",
    "rc-files": "~/_dotfiles/rc-files",
}

PLAN_ROOT_GLOBS = ("docs/plans", "Incubator/*/plans")


@dataclass
class BundleRecord:
    repo: str
    repo_path: str
    plan_id: str
    bundle_path: str
    root_kind: str  # "docs/plans" or "Incubator/plans"
    review_pass_count: int
    review_pass_files: list[str]
    has_context_md: bool
    has_log_md: bool
    has_index_md: bool
    has_plan_md: bool
    mtime_earliest: str | None
    mtime_latest: str | None
    git_first_commit: str | None
    git_first_commit_date: str | None
    git_last_commit: str | None
    git_last_commit_date: str | None
    git_commit_count: int
    error: str | None = None


@dataclass
class RepoResult:
    repo: str
    repo_path: str
    status: str  # "ok" | "missing" | "not_a_git_repo"
    bundle_count: int
    bundles: list[BundleRecord] = field(default_factory=list)
    error: str | None = None


def run_git(repo_root: Path, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def git_bundle_history(repo_root: Path, bundle_rel: str) -> dict:
    """First/last commit touching this bundle path, plain `git log`, read-only."""
    rc, out, _err = run_git(
        repo_root,
        ["log", "--follow", "--format=%H|%aI", "--", bundle_rel],
    )
    if rc != 0 or not out:
        return {
            "git_first_commit": None,
            "git_first_commit_date": None,
            "git_last_commit": None,
            "git_last_commit_date": None,
            "git_commit_count": 0,
        }
    lines = out.splitlines()
    commits = [line.split("|", 1) for line in lines if "|" in line]
    if not commits:
        return {
            "git_first_commit": None,
            "git_first_commit_date": None,
            "git_last_commit": None,
            "git_last_commit_date": None,
            "git_commit_count": 0,
        }
    # git log is newest-first
    newest = commits[0]
    oldest = commits[-1]
    return {
        "git_first_commit": oldest[0],
        "git_first_commit_date": oldest[1],
        "git_last_commit": newest[0],
        "git_last_commit_date": newest[1],
        "git_commit_count": len(commits),
    }


def scan_bundle(repo_name: str, repo_root: Path, bundle_dir: Path, root_kind: str, is_git: bool) -> BundleRecord:
    plan_id = bundle_dir.name
    rel = bundle_dir.relative_to(repo_root)

    review_dir = bundle_dir / "reviews"
    pass_files: list[Path] = []
    if review_dir.is_dir():
        pass_files = sorted(review_dir.glob("pass-*.md"))

    all_files = [p for p in bundle_dir.rglob("*") if p.is_file()]
    mtimes = [p.stat().st_mtime for p in all_files] if all_files else []

    def iso(ts: float) -> str:
        import datetime

        return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat()

    git_info = {
        "git_first_commit": None,
        "git_first_commit_date": None,
        "git_last_commit": None,
        "git_last_commit_date": None,
        "git_commit_count": 0,
    }
    error = None
    if is_git:
        try:
            git_info = git_bundle_history(repo_root, str(rel))
        except Exception as exc:  # noqa: BLE001 - report, don't crash the scan
            error = f"git history lookup failed: {exc}"

    return BundleRecord(
        repo=repo_name,
        repo_path=str(repo_root),
        plan_id=plan_id,
        bundle_path=str(bundle_dir),
        root_kind=root_kind,
        review_pass_count=len(pass_files),
        review_pass_files=[str(p) for p in pass_files],
        has_context_md=(bundle_dir / "context.md").is_file(),
        has_log_md=(bundle_dir / "log.md").is_file(),
        has_index_md=(bundle_dir / "index.md").is_file(),
        has_plan_md=(bundle_dir / "plan.md").is_file(),
        mtime_earliest=iso(min(mtimes)) if mtimes else None,
        mtime_latest=iso(max(mtimes)) if mtimes else None,
        error=error,
        **git_info,
    )


def scan_repo(repo_name: str, repo_path_raw: str) -> RepoResult:
    repo_root = Path(repo_path_raw).expanduser()
    if not repo_root.is_dir():
        return RepoResult(
            repo=repo_name,
            repo_path=str(repo_root),
            status="missing",
            bundle_count=0,
            error=f"repo path does not exist: {repo_root}",
        )

    rc, _out, _err = 0, "", ""
    try:
        rc, _out, _err = run_git(repo_root, ["rev-parse", "--is-inside-work-tree"])
    except Exception as exc:  # noqa: BLE001
        rc, _err = 1, str(exc)
    is_git = rc == 0

    bundle_dirs: list[tuple[Path, str]] = []
    docs_plans = repo_root / "docs" / "plans"
    if docs_plans.is_dir():
        for d in sorted(docs_plans.iterdir()):
            if d.is_dir():
                bundle_dirs.append((d, "docs/plans"))

    incubator = repo_root / "Incubator"
    if incubator.is_dir():
        for topic_dir in sorted(incubator.iterdir()):
            plans_dir = topic_dir / "plans"
            if plans_dir.is_dir():
                for d in sorted(plans_dir.iterdir()):
                    if d.is_dir():
                        bundle_dirs.append((d, "Incubator/plans"))

    records = [
        scan_bundle(repo_name, repo_root, bd, kind, is_git) for bd, kind in bundle_dirs
    ]

    status = "ok" if is_git else "not_a_git_repo"
    return RepoResult(
        repo=repo_name,
        repo_path=str(repo_root),
        status=status,
        bundle_count=len(records),
        bundles=records,
        error=None if is_git else f"not recognized as a git work tree by `git -C {repo_root}`",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos-file", type=Path, default=None, help="JSON file mapping repo name -> path; defaults to the built-in 7-repo corpus")
    ap.add_argument("--repo", action="append", default=None, help="restrict to this repo name (repeatable)")
    ap.add_argument("--json", action="store_true", help="emit JSON (default: human summary)")
    args = ap.parse_args()

    repos = DEFAULT_REPOS
    if args.repos_file:
        repos = json.loads(args.repos_file.read_text())

    if args.repo:
        missing_named = [r for r in args.repo if r not in repos]
        if missing_named:
            print(f"error: unknown repo name(s): {missing_named}; known: {sorted(repos)}", file=sys.stderr)
            return 2
        repos = {k: v for k, v in repos.items() if k in args.repo}

    if not repos:
        print("error: no repos configured", file=sys.stderr)
        return 1

    results = [scan_repo(name, path) for name, path in repos.items()]

    total_bundles = sum(r.bundle_count for r in results)
    total_passes = sum(b.review_pass_count for r in results for b in r.bundles)
    missing_repos = [r.repo for r in results if r.status != "ok"]

    if args.json:
        out = {
            "repos": [asdict(r) for r in results],
            "summary": {
                "repo_count": len(results),
                "repo_count_ok": len(results) - len(missing_repos),
                "repos_missing_or_broken": missing_repos,
                "total_bundles": total_bundles,
                "total_review_passes": total_passes,
            },
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"{'repo':<14} {'status':<16} {'bundles':>8} {'passes':>8}")
        for r in results:
            passes = sum(b.review_pass_count for b in r.bundles)
            print(f"{r.repo:<14} {r.status:<16} {r.bundle_count:>8} {passes:>8}")
        print(f"\ntotal: {total_bundles} bundles, {total_passes} review passes across {len(results)} repos")
        if missing_repos:
            print(f"WARNING: {len(missing_repos)} repo(s) missing or not a git work tree: {missing_repos}", file=sys.stderr)

    if missing_repos and len(missing_repos) == len(results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
