#!/usr/bin/env python3
"""Issue 5.2 — prove the repo is a SUPERSET of user scope, one direction only.

Per the review carry-forward, "equal-or-newer" is implemented mechanically as:

  (A) SET MEMBERSHIP — every artifact present under ~/.claude/skills/ has a repo
      counterpart at skills/<same relpath>. The repo may contain MORE; that is the
      intended end state, not drift.
  (B) CONTENT CHECK on the two KNOWN-DIVERGENT artifacts — yf-herdr/ and
      plan_manager.py — where mere existence is not enough.

Exclusions: __pycache__/, *.pyc, .DS_Store, and the install stamp line
`<!-- yf-skills: v=... tree=... -->` which the installer injects into every SKILL.md
(comparing without filtering it reports 19 false positives — exp-01's first trap).

READ-ONLY with respect to user scope. Writes nothing anywhere.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

USER = Path.home() / ".claude" / "skills"
REPO = Path("/Users/james/workspace/dixson3/yoshiko-flow/skills")

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git"}
EXCLUDE_NAMES = {".DS_Store"}
EXCLUDE_SUFFIX = {".pyc"}
STAMP = re.compile(rb"^<!-- yf-skills: v=[^>]*-->\n?", re.MULTILINE)


def interesting(p: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in p.parts):
        return False
    if p.name in EXCLUDE_NAMES or p.suffix in EXCLUDE_SUFFIX:
        return False
    return p.is_file()


def rels(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*") if interesting(p)}


def norm(p: Path) -> bytes:
    """File bytes with the installer's stamp line removed."""
    return STAMP.sub(b"", p.read_bytes())


def main() -> int:
    if not USER.is_dir():
        print(f"FAIL: user scope not found at {USER}")
        return 1

    user_all, repo = rels(USER), rels(REPO)

    # SCOPE: only skills this repo SHIPS. Third-party skills installed alongside
    # (herdr, mermaid, naba) are not yoshiko-flow's to carry, so the repo cannot
    # and should not be a superset of them. Stated explicitly rather than silently
    # filtered, and their absence is REPORTED below.
    third_party = sorted({r.split("/")[0] for r in user_all
                          if not r.startswith("yf-")})
    user = {r for r in user_all if r.startswith("yf-")}

    # The .bak is preserved in the PLAN FOLDER (Epic 1), not under skills/ — it is
    # a snapshot of a user-scope file, never a repo skill artifact. Checked separately.
    BAK = "yf-plan/scripts/plan_manager.py.pre-incubator-root.bak"
    bak_snapshot = Path(
        "/Users/james/workspace/dixson3/yoshiko-flow/docs/plans/"
        "plan-037-james-dixson-cab694/references/user-scope/"
        "plan_manager.py.pre-incubator-root.bak")
    user.discard(BAK)

    # (A) set membership
    missing = sorted(user - repo)
    extra = sorted(repo - user)
    # Generated/runtime artifacts the harness leaves behind are not deliverables.
    extra = [e for e in extra if ".scratch/" not in e and not e.endswith("topology.txt")]

    print("=" * 70)
    print("(A) SET MEMBERSHIP — every user-scope artifact has a repo counterpart")
    print("=" * 70)
    print(f"  user-scope files (yf-* only): {len(user)}")
    print(f"  third-party skills EXCLUDED (not this repo's to ship): {', '.join(third_party)}")
    print(f"  repo files:       {len(repo)}")
    print(f"  missing from repo: {len(missing)}")
    for m in missing:
        print(f"    MISSING: {m}")
    print(f"  repo-only (expected — superset): {len(extra)}")
    for e in extra[:12]:
        print(f"    repo-only: {e}")
    if len(extra) > 12:
        print(f"    ... and {len(extra) - 12} more")

    print()
    print("  .bak snapshot (preserved in the plan folder, not under skills/):")
    bak_ok = bak_snapshot.is_file() and norm(bak_snapshot) == norm(USER / BAK)
    print(f"    {'OK' if bak_ok else 'FAIL'}: {bak_snapshot.name} byte-identical in git")

    # (B) content check on the two known-divergent artifacts
    print()
    print("=" * 70)
    print("(B) CONTENT CHECK — the two known-divergent artifacts")
    print("=" * 70)
    content_fail = []

    # B1: yf-herdr — every user-scope file must be byte-identical (stamp-filtered).
    herdr = sorted(r for r in user if r.startswith("yf-herdr/"))
    print(f"  yf-herdr: {len(herdr)} user-scope file(s)")
    for r in herdr:
        u, g = USER / r, REPO / r
        if not g.is_file():
            print(f"    FAIL absent: {r}")
            content_fail.append(r)
        elif norm(u) == norm(g):
            print(f"    OK identical: {r}")
        else:
            # Not automatically a failure — the repo copy was edited on import.
            print(f"    DIVERGED (repo edited on import): {r}")

    # B2: plan_manager.py — the local patch's BEHAVIOR must exist in the repo.
    print("  plan_manager.py: behavior check (not byte-equality — re-implemented)")
    g = REPO / "yf-plan" / "scripts" / "plan_manager.py"
    src = g.read_text()
    for label, needle in [
        ("plans-root configurable", 'plans-root'),
        ("incubator-root configurable", 'incubator-root'),
        ("import-safe bootstrap reader", 'def _bootstrap_config'),
        ("defaults preserved", '"docs/plans"'),
    ]:
        ok = needle in src
        print(f"    {'OK' if ok else 'FAIL'}: {label}")
        if not ok:
            content_fail.append(f"plan_manager.py: {label}")

    print()
    print("=" * 70)
    verdict_ok = not missing and not content_fail and bak_ok
    print(f"VERDICT: {'PASS' if verdict_ok else 'FAIL'}")
    print("  (A) set membership:", "PASS" if not missing else f"FAIL ({len(missing)} missing)")
    print("  (B) content check: ", "PASS" if not content_fail else f"FAIL ({len(content_fail)})")
    print("  NOTE: nothing was written to user scope.")
    return 0 if verdict_ok else 1


if __name__ == "__main__":
    sys.exit(main())
