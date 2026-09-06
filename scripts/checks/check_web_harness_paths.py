#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_web_harness_paths.py — harness path/identifier claims against `harness_desc.rs`.

THE CLAIM CLASS. Install-root path cells ("`pi` installs to `.pi/agent/skills`") and
`name_transform` assertions ("`pi` applies a `lowercase-hyphen,max64` transform"). The source of
truth is the `DESCRIPTORS` table in `yf/src/harness_desc.rs`, parsed here — never restated.

COMPARE AGAINST THE `(scope, field)` TUPLE, NEVER A FLAT STRING DENYLIST (plan-066 pass-2 C12).
`.config/opencode` and `.pi/agent` are the CORRECT `user_surface_dir` values for those harnesses;
only their `/skills` forms are retired, because every harness but claude-code now installs skills
to `.agents/skills`. A bare-string denylist would match the real defects **for the wrong reason**
and false-positive on any correct surface-dir mention.

STRIP PATH TOKENS BEFORE ATTRIBUTING A LINE TO A HARNESS ID. This is not a nicety — it is the
measured cause of a FALSE GREEN. plan-066 EXP-001's checker B first reported `PASS (0
mismatches)` against a tree with 15 real defects, because the shared root `.agents/skills`
CONTAINS the harness id `agents`, so a repaired `pi` row scanned as `{pi, agents}`, was judged
ambiguous, and was silently skipped. The checker was wrong in exactly the direction that looks
like success — the case only a CODE-SIDE negative control can catch.

CORPUS IS A PARAMETER (`--corpus`), defaulting to the widened set including `README.md` and
`AGENTS.md`, which carry the identical drifted matrix and which `web/content/**` cannot reach.

EXIT  0 clean  ·  1 mismatch  ·  2 INCONCLUSIVE (could not run / vacuous corpus)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _web_corpus import DEFAULT_CORPUS, expand_corpus, repo_root  # noqa: E402

CHECK = "check_web_harness_paths"
DESC_RS = "yf/src/harness_desc.rs"
MIN_FILES = 5
MIN_HARNESSES = 4   # fewer than this parsed means the Rust table changed shape

FIELDS = ["user_skills_subpath", "project_skills_subpath",
          "user_surface_dir", "project_surface_dir"]
# A `<dot-root>/skills` path claim. The first character after the leading `.` must be a NAME
# character, not another dot: without that guard `../skills` matches, and `AGENTS.md:228`'s
# `cargo:rerun-if-changed=../skills` — a build-script path with no harness meaning at all —
# is reported as a harness-root defect. A checker's false POSITIVES cost review attention the
# same way its false negatives cost coverage.
PATH_CLAIM_RE = re.compile(
    r"(?:(~|\$HOME|<git-root>|<root>)\s*)?/?"
    r"`?(\.[A-Za-z0-9_-][A-Za-z0-9_./-]*?/skills)`?")

# THE SCOPE IS CARRIED BY THE ANCHOR PREFIX, and reading it there is what makes the comparison
# a `(scope, field)` TUPLE rather than a set-membership test (plan-066 pass-2 C12). It is also
# the one signal that works in BOTH formats: the markdown matrices write `~/.pi/agent/skills`
# and `<git-root>/.pi/skills` in adjacent columns, and `install-matrix.d2` writes the same two
# anchors inside its `user_scope:` / `project_scope:` blocks.
SCOPE_OF_ANCHOR = {"~": "user", "$HOME": "user", "<git-root>": "project", "<root>": "project"}
SCOPE_FIELD = {"user": "user_skills_subpath", "project": "project_skills_subpath"}
NAME_TRANSFORM_RE = re.compile(r"\b(lowercase-hyphen|max64)\b")


def inconclusive(msg: str) -> int:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def parse_descriptors(text: str) -> dict[str, dict[str, str]]:
    """`DESCRIPTORS` -> {harness id: {field: value}}, including `name_transform`."""
    out: dict[str, dict[str, str]] = {}
    for m in re.finditer(r'id:\s*"([a-z-]+)"\s*,(.*?)(?=\n\s*id:\s*"|\Z)', text, re.S):
        hid, body = m.group(1), m.group(2)
        rec: dict[str, str] = {}
        for f in FIELDS:
            fm = re.search(rf'{f}:\s*"([^"]*)"', body)
            if fm:
                rec[f] = fm.group(1)
        nt = re.search(r"name_transform:\s*([A-Za-z]+)", body)
        rec["name_transform"] = nt.group(1) if nt else "?"
        out[hid] = rec
    return out


def attribute(line: str, ids: list[str]) -> set[str]:
    """Which harness ids this line is ABOUT, after STRIPPING PATH TOKENS.

    Every `.<something>` path is removed before the id search, so `.agents/skills` can no longer
    donate the id `agents` to a line that is really about `pi`. Without this the attribution is
    ambiguous and the line is skipped — silently, and in the direction that looks like success.
    """
    stripped = re.sub(r"[`\"]?\.[A-Za-z0-9_./-]+[`\"]?", " ", line)
    return {h for h in ids if re.search(rf"(?<![a-z0-9-]){re.escape(h)}(?![a-z0-9-])", stripped)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", action="append", default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--min-files", type=int, default=MIN_FILES)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else repo_root()
    rs = root / DESC_RS
    if not rs.is_file():
        return inconclusive(f"source of truth absent: {DESC_RS}")
    desc = parse_descriptors(rs.read_text(encoding="utf-8"))
    if len(desc) < MIN_HARNESSES:
        return inconclusive(f"parsed {len(desc)} harness descriptor(s) from {DESC_RS}, below "
                            f"the floor {MIN_HARNESSES} — the parser, not the docs, is wrong")
    ids = sorted(desc)

    # The TUPLE, computed from the table — never a hand-written denylist. A `<root>/skills`
    # string is retired iff no harness declares it as a SKILLS subpath. `.config/opencode` and
    # `.pi/agent` survive as surface dirs and are therefore never flagged.
    live_skills_paths = {desc[h][f] for h in ids
                         for f in ("user_skills_subpath", "project_skills_subpath")
                         if f in desc[h]}
    transform_free = [h for h in ids if desc[h].get("name_transform") == "None"]

    files = expand_corpus(root, a.corpus or DEFAULT_CORPUS)
    if len(files) < a.min_files:
        return inconclusive(f"corpus expanded to {len(files)} file(s), below the floor "
                            f"{a.min_files}")

    findings, claims, ambiguous = [], 0, []
    for path in files:
        rel = str(path.relative_to(root))
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            paths = {(anchor, claimed) for anchor, claimed in PATH_CLAIM_RE.findall(line)}
            transforms = set(NAME_TRANSFORM_RE.findall(line))
            if not paths and not transforms:
                continue
            about = attribute(line, ids)
            # ATTRIBUTED COMPARISON FIRST. When the line names exactly the harnesses it is
            # about, the claim is checked against THOSE harnesses' declared subpaths — the
            # `(scope, field)` tuple — not against the union of every harness's.
            #
            # THE UNION-ONLY FORM IS A MEASURED BLIND SPOT, found by this checker's own
            # code-side negative control: retargeting `pi`'s `user_skills_subpath` to
            # `.control/skills` left docs saying `.agents/skills`, which is STILL some other
            # harness's live value — so a union membership test stayed green while the docs had
            # become wrong. That is pass-2 C12's flat-denylist defect in mirror image, and it is
            # the same shape as EXP-001's original false green on this same checker.
            for anchor, claimed in sorted(paths):
                claims += 1
                scope = SCOPE_OF_ANCHOR.get(anchor)
                if about and scope:
                    # THE TUPLE: this harness, this scope, this field. Strongest form.
                    field = SCOPE_FIELD[scope]
                    expected = {desc[h][field] for h in about if field in desc[h]}
                    if claimed not in expected:
                        findings.append(
                            f"{rel}:{n}: {scope}-scope `{claimed}` is not the "
                            f"`{field}` of {sorted(about)}; declared: {sorted(expected)}")
                    continue
                if about:
                    # Harness known, scope not stated — compare against that harness's two
                    # subpaths. Weaker than the tuple, and reported as such.
                    expected = {desc[h][f] for h in about
                                for f in SCOPE_FIELD.values() if f in desc[h]}
                    if claimed not in expected:
                        findings.append(
                            f"{rel}:{n}: `{claimed}` is not a skills subpath of "
                            f"{sorted(about)} in either scope; declared: {sorted(expected)}")
                    continue
                if claimed not in live_skills_paths:
                    # UNATTRIBUTED FALLBACK — weaker, and reported as such. The line states a
                    # path but names no harness, so only the union can be tested.
                    findings.append(f"{rel}:{n}: `{claimed}` is no harness's skills subpath; "
                                    f"live values are {sorted(live_skills_paths)} "
                                    f"(line names no harness — union test only)")
            for tf in sorted(transforms):
                claims += 1
                findings.append(f"{rel}:{n}: asserts a `{tf}` name_transform, but "
                                f"{len(transform_free)}/{len(ids)} shipped harnesses declare "
                                f"name_transform: None ({', '.join(transform_free)})")
            if paths and not about:
                ambiguous.append(f"{rel}:{n}")

    if claims == 0:
        return inconclusive(f"scanned {len(files)} file(s) and found ZERO path/identifier "
                            "claims — the matcher, not the docs, is what to fix")

    out = {"check": CHECK, "verdict": "FAIL" if findings else "PASS",
           "files_scanned": len(files), "claims": claims,
           "descriptors": desc, "live_skills_paths": sorted(live_skills_paths),
           "findings": findings, "unattributed_lines": ambiguous,
           "not_checked": ["prose ABOUT a harness that states no path or transform literal"]}
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        for f in findings:
            print(f"FAIL {f}")
        print(f"{CHECK}: {len(desc)} harness(es) from {DESC_RS}; scanned {len(files)} file(s), "
              f"{claims} claim(s); {len(findings)} mismatch(es)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
