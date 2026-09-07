#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_web_backend_claim.py — the upstream-tracking backend claim.

THE FACT. **GitHub is the only supported upstream backend.** `UPSTREAM_TRACKING.md` states that
writes are gh-direct and that "no `bd <backend>` write command is issued at all"; GitLab and Jira
are config-only stubs at best. Docs that offer a choice of three teach a capability that does not
exist.

WHY THIS CHECKER EXISTS AT ALL — a natural experiment, measured (plan-066 EXP-002). Five sites
state the backend set. The ONE that is correct is the ONE an edge covers:

    web/content/skills/yf-beads-upstream.md   "GitHub is the only supported backend"   CORRECT
    web/content/pages/architecture.md         "(GitHub, GitLab, or Jira)"              wrong
    web/content/pages/glossary.md             "(GitHub, GitLab, or Jira)"              wrong
    web/content/pages/beads-concepts.md       "(GitHub, GitLab, or Jira)"              wrong
    web/content/images/architecture.d2        "GitHub / GitLab / Jira"                 wrong

A 4-false / 1-true split falling PRECISELY along the coverage boundary is the cleanest causal
evidence in the plan's finding set. `README.md` is a sixth site the corpus widening exposed.

DENYLIST **PLUS A LEGITIMATE-MENTION ALLOWLIST.** `README.md`'s "`gh` / `glab` — GitHub / GitLab
CLI" is a correct mention of two CLI TOOLS, not a backend claim, and must not false-positive.
A checker that cries wolf on a correct line costs review attention exactly as a missed defect
costs coverage.

CORPUS IS A PARAMETER (`--corpus`) — the SAME widened set as `check_web_counts` and
`check_web_harness_paths` (plan-066 pass-2 C11: this was the only checker whose corpus was
left unstated).

EXIT  0 clean  ·  1 a multi-backend claim survives  ·  2 INCONCLUSIVE
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _web_corpus import DEFAULT_CORPUS, expand_corpus, repo_root  # noqa: E402

CHECK = "check_web_backend_claim"
MIN_FILES = 5

DENY = [
    (re.compile(r"GitHub\s*[,/]\s*GitLab", re.I), "offers GitHub/GitLab as alternatives"),
    # The conjunction form, not just the punctuation form. `web/content/skills/yf-plan.md:90`
    # reads "scans GitHub or GitLab for issues" — a 5th wrong site on a page #317 counts as
    # clean, and invisible to a comma/slash-only matcher.
    (re.compile(r"GitHub\s+or\s+GitLab", re.I), "offers GitHub or GitLab as alternatives"),
    (re.compile(r"GitLab\s*[,/]?\s*(?:or\s+)?Jira", re.I), "offers GitLab/Jira"),
    (re.compile(r"github\s*\|\s*gitlab", re.I), "a `github | gitlab | …` backend enum"),
    (re.compile(r"\bbd\s+(?:github|gitlab|jira)\s+push\b", re.I),
     "teaches the pre-gh-direct `bd <backend> push` verb, which is never issued"),
]
ALLOW = [
    (re.compile(r"`gh`\s*/\s*`glab`"), "a mention of the gh/glab CLI tools"),
    (re.compile(r"GitHub\s*/\s*GitLab\s+CLI", re.I), "names the CLIs, not the backend set"),
]


def inconclusive(msg: str) -> int:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", action="append", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--min-files", type=int, default=MIN_FILES)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else repo_root()
    files = expand_corpus(root, a.corpus or DEFAULT_CORPUS)
    if len(files) < a.min_files:
        return inconclusive(f"corpus expanded to {len(files)} file(s), below the floor "
                            f"{a.min_files}")

    findings, allowed = [], []
    for path in files:
        rel = str(path.relative_to(root))
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            hit = next(((r, why) for r, why in ALLOW if r.search(line)), None)
            if hit:
                allowed.append(f"{rel}:{n}: {hit[1]}")
                continue
            for rex, why in DENY:
                if rex.search(line):
                    findings.append(f"{rel}:{n}: {why} — {line.strip()[:110]}")
                    break

    out = {"check": CHECK, "verdict": "FAIL" if findings else "PASS",
           "files_scanned": len(files), "findings": findings,
           "allowlisted": allowed,
           "not_checked": ["prose that DESCRIBES multi-backend support historically without "
                           "asserting it is available — an intent judgement that keeps its "
                           "prose route (REQ-CHECK-009)"]}
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        for f in findings:
            print(f"FAIL {f}")
        for al in allowed:
            print(f"ALLOWED {al}")
        print(f"{CHECK}: scanned {len(files)} file(s); {len(findings)} multi-backend claim(s), "
              f"{len(allowed)} legitimate mention(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
