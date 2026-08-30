#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""REQ-YF-DOC-010..018 — the skill-README contract driver.

`DRIFT-CHECK.md` declares four README edges (`e-readme-layout`, `e-readme-prereqs`,
`e-readme-usage`, `e-readme-desc`). **Nothing ran them.** `CHANGE-VALIDATION.md` excludes
`yf-drift-check` as a *"prose/LLM trigger, not a runnable command"*, so the only firing surface
was an on-edit obligation — and #273 measured that prose naming an OBLIGATION is skipped where
prose naming a COMMAND is followed.

The consequence was measurable and it moved: #244 reported "16/19 skills failing"; re-derived at
HEAD on 2026-08-30 every figure in it was stale-low (18 FAIL / 1 PASS / 1 N-A of 20). **#244's
numbers went stale inside a single plan-cycle**, which is the strongest available argument that
the fix must be a runnable check rather than a repair pass.

FIVE PROPERTIES, each written because its absence is a way to report a false clean:

1. **Depth-1 `skills/*/` enumeration, NEVER `rglob`** (REQ-YF-DOC-011). `rglob` would descend
   into a skill's own fixture trees and count each nested directory as a skill.

2. **`skills_enumerated` + `--min-skills N`, tripping at exit 2** (REQ-YF-DOC-015). A checker
   that enumerated nothing exits 0 on every rule it applies. The floor is what makes "the corpus
   is clean" distinguishable from "the corpus was not read" — and the EXIT CODE is the
   requirement, not the floor: a floor tripping at `1` is byte-identical to a real FAIL, so a
   sensitivity gate of the form "exits non-zero" would be satisfied by a checker that read
   nothing. That is the risk realised through its own mitigation.

3. **A CLOSED `class` enum** (REQ-YF-DOC-014) — `layout | prereqs | usage | missing-readme |
   fence-unparseable`. Pinned as a set, not merely as a field name: a criterion of the form
   "the `fence-unparseable` array is empty" is satisfied VACUOUSLY by a producer that never
   emits that class (#263).

4. **`missing-readme` is its own class** (REQ-YF-DOC-018), never collapsed into a mismatch.
   `yf-okf-hygiene` has no README, so there is nothing for a contract to be measured against.
   Absence and mismatch are two facts; one signal for both is the conflation this repository has
   hit three times (#181, #207, #263).

5. **`e-readme-desc` is deliberately NOT implemented** (REQ-YF-DOC-013). Its predicate is that
   the README one-liner matches the SKILL.md `description` INTENT, which tolerates paraphrase and
   is not mechanically decidable. It keeps its LLM route, and this checker makes no claim about
   it. Claiming it would be exactly the vacuous check this file exists to close.

EXIT  0 clean  ·  1 contract failure  ·  2 INCONCLUSIVE (could not run)
      126/127 reserved to the shell.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECK = "check-skill-readme-contract"

# REQ-YF-DOC-014 — the CLOSED enum. Declared once, asserted at every emit site.
CLASSES = ("layout", "prereqs", "usage", "missing-readme", "fence-unparseable")

# REQ-YF-DOC-006 — the exclusion set, pinned in SPEC and mirrored here.
EXCLUDE_PARTS = ("__pycache__", ".pytest_cache")
EXCLUDE_SUFFIX = (".pyc", ".pyo")
EXCLUDE_NAMES = (".DS_Store",)

# REQ-YF-DOC-003 — the ASCII-tree drawing prefixes.
TREE_BRANCH = re.compile(r"^(?:(?:│   |    )*)(?:├── |└── )(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*```")
HEADING_RE = re.compile(r"^(#{2,6})\s+(.*?)\s*$")


def inconclusive(msg: str, **extra) -> int:
    """A statement about the INSTRUMENT, never a verdict on the corpus."""
    print(json.dumps({
        "check": CHECK, "verdict": "INCONCLUSIVE", "exit": 2,
        "skills_enumerated": extra.pop("skills_enumerated", 0),
        "failures": [], "reason": msg, **extra,
    }, indent=1))
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def repo_root() -> Path:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                      text=True, stderr=subprocess.DEVNULL).strip()
        return Path(out)
    except Exception:
        return Path.cwd()


def git_ignored(root: Path, paths: list[Path]) -> set[str]:
    """The subset git ignores. A generated artifact is not part of the contract."""
    if not paths:
        return set()
    try:
        proc = subprocess.run(["git", "-C", str(root), "check-ignore", "--stdin"],
                              input="\n".join(str(p) for p in paths),
                              capture_output=True, text=True)
        return {ln.strip() for ln in proc.stdout.splitlines() if ln.strip()}
    except Exception:
        return set()  # gitignore-awareness is a refinement, never a blocker


# --------------------------------------------------------------------------- parsing

def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def sections(text: str) -> dict[str, str]:
    """`## Heading` -> body, lowercased keys. Nested `###` stay inside their parent."""
    out: dict[str, str] = {}
    cur, buf = None, []
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) == 2:
            if cur is not None:
                out[cur] = "\n".join(buf)
            cur, buf = m.group(2).strip().lower(), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf)
    return out


def find_layout_section(secs: dict[str, str]) -> tuple[str, str] | None:
    """REQ-YF-DOC-002 — the heading whose text matches `layout`, case-insensitively."""
    for name, body in secs.items():
        if "layout" in name:
            return name, body
    return None


def first_fence(body: str) -> list[str] | None:
    """The first fenced block's lines, or None when the section carries no fence."""
    lines, inside, buf = body.splitlines(), False, []
    for line in lines:
        if FENCE_RE.match(line):
            if inside:
                return buf
            inside = True
            continue
        if inside:
            buf.append(line)
    return buf if inside else None


def parse_tree_fence(fence: list[str]) -> tuple[str | None, list[str], str | None]:
    """REQ-YF-DOC-003/004 — the SINGLE ASCII-tree parser.

    Returns `(root_line, entry_paths, error)`. `error` non-None means
    `fence-unparseable`: the fence is not in the one conformant form, so no layout
    comparison can honestly be made against it.
    """
    body = [ln for ln in fence if ln.strip()]
    if not body:
        return None, [], "the layout fence is empty"

    root = body[0].strip()
    if not root.endswith("/"):
        return None, [], (f"the fence's first line {root!r} is not a directory root "
                          "(no trailing '/') — REQ-YF-DOC-003")

    # Walk the tree, maintaining a directory stack keyed by indent depth.
    stack: list[str] = []
    entries: list[str] = []
    saw_branch = False
    for raw in body[1:]:
        m = TREE_BRANCH.match(raw.rstrip())
        if not m:
            return None, [], (f"line {raw.strip()!r} is not an ASCII-tree branch "
                              "(expected a '├── ' / '└── ' prefix) — REQ-YF-DOC-003")
        saw_branch = True
        prefix_len = len(raw) - len(raw.lstrip("│ "))
        # Each level of nesting is exactly 4 columns of '│   ' or '    '.
        depth = max(0, (len(raw[:raw.index("├── ") if "├── " in raw
                                 else raw.index("└── ")])) // 4)
        del prefix_len
        name = m.group(1)
        # Strip a trailing `# description` comment (REQ-YF-DOC-005).
        name = re.split(r"\s+#\s", name, maxsplit=1)[0].strip()
        name = name.rstrip()
        stack = stack[:depth]
        if name.endswith("/"):
            stack.append(name.rstrip("/"))
            continue
        entries.append("/".join(stack + [name]))

    if not saw_branch:
        return None, [], "the layout fence has a root line but no entries — REQ-YF-DOC-003"
    return root, entries, None


def frontmatter_tools(skill_md: str) -> list[str]:
    """SKILL.md frontmatter `depends-on-tool: [a, b]` — the fixed authority (REQ-YF-DOC-007)."""
    m = re.search(r"^depends-on-tool:\s*\[(.*?)\]\s*$", skill_md, re.M)
    if not m:
        return []
    return [t.strip() for t in m.group(1).split(",") if t.strip()]


def user_invocable(skill_md: str) -> bool:
    """SKILL.md frontmatter `user-invocable:` — absent is treated as false."""
    m = re.search(r"^user-invocable:\s*(true|false)\s*$", skill_md, re.M)
    return bool(m and m.group(1) == "true")


_SROOT: Path | None = None


def sroot_of(root: Path, name: str) -> Path:
    """The skill dir, honouring a `--skills-root` override."""
    return (_SROOT or (root / "skills")) / name


# --------------------------------------------------------------------------- checks

def check_layout(root: Path, name: str, secs: dict[str, str]) -> list[dict]:
    """REQ-YF-DOC-002..006 — the `e-readme-layout` edge.

    Emits **at most one `layout` finding per skill**, so `by_class.layout` counts SKILLS
    FAILING THE EDGE rather than sub-reasons. A skill whose fence cannot be parsed fails the
    layout edge too — it gets BOTH findings: the `layout` one says *the edge failed*, the
    `fence-unparseable` one says *why*. Collapsing them would make the layout count depend on
    how a README happens to be malformed.
    """
    sd = sroot_of(root, name)
    found = find_layout_section(secs)
    if found is None:
        return [
            {"skill": name, "class": "layout",
             "detail": "the layout edge fails: no `## ...layout...` section — REQ-YF-DOC-002"},
            {"skill": name, "class": "fence-unparseable",
             "detail": "no `## ...layout...` section — REQ-YF-DOC-002"},
        ]
    _, body = found
    fence = first_fence(body)
    if fence is None:
        why = ("the layout section carries no fenced code block (a bullet list is not the "
               "conformant form) — REQ-YF-DOC-002")
        return [{"skill": name, "class": "layout", "detail": f"the layout edge fails: {why}"},
                {"skill": name, "class": "fence-unparseable", "detail": why}]
    tree_root, entries, err = parse_tree_fence(fence)
    if err:
        return [{"skill": name, "class": "layout", "detail": f"the layout edge fails: {err}"},
                {"skill": name, "class": "fence-unparseable", "detail": err}]

    reasons: list[str] = []
    expected_root = f"skills/{name}/"
    if tree_root != expected_root:
        reasons.append(f"the fence root is {tree_root!r}, not the skill's real directory "
                       f"{expected_root!r} (REQ-YF-DOC-004)")

    raw: list[Path] = []
    for p in sorted(sd.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(sd)
        if any(part in EXCLUDE_PARTS for part in rel.parts):
            continue
        if p.suffix in EXCLUDE_SUFFIX or p.name in EXCLUDE_NAMES:
            continue
        raw.append(p)
    ignored = git_ignored(root, raw)
    actual = [str(p.relative_to(sd)) for p in raw
              if str(p) not in ignored and str(p.relative_to(root)) not in ignored]

    declared, real = set(entries), set(actual)
    missing, extra = sorted(real - declared), sorted(declared - real)
    if missing:
        reasons.append(f"{len(missing)} file(s) on disk are absent from the fence: "
                       + ", ".join(missing[:12]) + ("…" if len(missing) > 12 else ""))
    if extra:
        reasons.append(f"{len(extra)} fence entr(ies) do not exist on disk: "
                       + ", ".join(extra[:12]) + ("…" if len(extra) > 12 else ""))
    if not reasons:
        return []
    return [{"skill": name, "class": "layout",
             "detail": "the layout edge fails: " + "; ".join(reasons)}]


def check_prereqs(name: str, secs: dict[str, str], tools: list[str]) -> list[dict]:
    """REQ-YF-DOC-007 — README Prerequisites ⊇ frontmatter `depends-on-tool`."""
    if not tools:
        return []
    body = None
    for h, b in secs.items():
        if "prerequisite" in h:
            body = b
            break
    if body is None:
        return [{"skill": name, "class": "prereqs",
                 "detail": (f"no `## Prerequisites` section, but SKILL.md frontmatter declares "
                            f"depends-on-tool: {tools} — REQ-YF-DOC-007")}]
    absent = [t for t in tools if not re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", body)]
    if absent:
        return [{"skill": name, "class": "prereqs",
                 "detail": (f"Prerequisites does not mention {absent} declared in the SKILL.md "
                            "frontmatter `depends-on-tool` — REQ-YF-DOC-007")}]
    return []


def check_usage(name: str, secs: dict[str, str], skill_md: str) -> list[dict]:
    """REQ-YF-DOC-008 — Usage present, and it teaches no command the skill does not answer to.

    The **unprefixed-invocation** half is the load-bearing one: a README teaching
    `/beads-upstream` where the skill answers to `/yf-beads-upstream` does not merely omit
    something, it teaches a command that fails. Measured pre-backfill: four instances.

    The check deliberately does **not** demand that Usage mention `/<name>` for every skill.
    A `user-invocable: false` skill is reached by trigger, not by a slash command, and
    requiring one would manufacture eleven findings against correct documents — the
    manufactured-blocker failure mode the plan's own gate instructions warn about.
    """
    body = None
    for h, b in secs.items():
        if h.startswith("usage"):
            body = b
            break
    if body is None:
        return [{"skill": name, "class": "usage",
                 "detail": "no `## Usage` section — REQ-YF-DOC-008"}]

    out: list[dict] = []
    if user_invocable(skill_md) and "/" not in body:
        out.append({"skill": name, "class": "usage",
                    "detail": (f"`user-invocable: true`, but Usage teaches no `/{name}` "
                               "invocation at all — REQ-YF-DOC-008")})
    if name.startswith("yf-"):
        bare = name[3:]
        if re.search(rf"(?<![\w/-])/{re.escape(bare)}(?![\w-])", body):
            out.append({"skill": name, "class": "usage",
                        "detail": (f"Usage teaches the unprefixed `/{bare}`, a command the skill "
                                   f"does not answer to; it is `/{name}` — REQ-YF-DOC-008")})
    return out


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="Skill-README contract check (REQ-YF-DOC-010..018).")
    ap.add_argument("--min-skills", type=int, default=1,
                    help="Fail-loud floor on skills_enumerated. Trips at exit 2, never 1 "
                         "(REQ-YF-DOC-015).")
    ap.add_argument("--json", action="store_true", dest="as_json",
                    help="Accepted for interface symmetry; output is JSON on every path.")
    ap.add_argument("--skills-root", default=None,
                    help="Override the skills root (default: <git-root>/skills).")
    ap.add_argument("--changed", action="append", default=None, metavar="PATH",
                    help="Scope to the skills these changed paths belong to (FAST tier).")
    a = ap.parse_args()

    global _SROOT
    root = repo_root()
    sroot = Path(a.skills_root) if a.skills_root else root / "skills"
    _SROOT = sroot
    if not sroot.is_dir():
        return inconclusive(f"skills root {sroot} does not exist — the checker could not run")
    if a.skills_root:
        root = sroot.parent

    # PROPERTY 1 — depth-1 globbing, never rglob.
    names = sorted(p.name for p in sroot.glob("*") if p.is_dir() and (p / "SKILL.md").is_file())

    if a.changed:
        scoped = set()
        for c in a.changed:
            parts = Path(c).parts
            if "skills" in parts:
                i = parts.index("skills")
                if i + 1 < len(parts):
                    scoped.add(parts[i + 1])
        if scoped:
            names = [n for n in names if n in scoped]

    failures: list[dict] = []
    for name in names:
        sd = sroot / name
        readme = sd / "README.md"
        if not readme.is_file():
            # PROPERTY 4 — absence is its OWN class, never a mismatch.
            failures.append({"skill": name, "class": "missing-readme",
                             "detail": (f"skills/{name}/ has no README.md — there is no contract "
                                        "to measure against (REQ-YF-DOC-001/018)")})
            continue
        text = read(readme)
        skill_md = read(sd / "SKILL.md")
        secs = sections(text)
        failures += check_layout(root, name, secs)
        failures += check_prereqs(name, secs, frontmatter_tools(skill_md))
        failures += check_usage(name, secs, skill_md)

    enumerated = len(names)

    # PROPERTY 3 — the enum is CLOSED, and that is asserted rather than assumed.
    bad = sorted({f["class"] for f in failures} - set(CLASSES))
    if bad:
        return inconclusive(f"emitted class(es) outside the closed enum: {bad}",
                            skills_enumerated=enumerated)

    # PROPERTY 2 — the floor, tripping at 2. Checked AFTER enumeration and BEFORE any verdict.
    if enumerated < a.min_skills:
        return inconclusive(
            f"enumerated {enumerated} skill(s), below the --min-skills floor of {a.min_skills} "
            "— a checker that read nothing cannot report clean, and reporting this as a FAIL "
            "(exit 1) would be byte-identical to a real contract failure (REQ-YF-DOC-015)",
            skills_enumerated=enumerated, min_skills=a.min_skills)

    by_class = {c: sum(1 for f in failures if f["class"] == c) for c in CLASSES}
    out = {
        "check": CHECK,
        "verdict": "FAIL" if failures else "PASS",
        "exit": 1 if failures else 0,
        "skills_enumerated": enumerated,
        "skills": names,
        "classes": list(CLASSES),
        "by_class": by_class,
        "failures": failures,
        "not_checked": ["e-readme-desc"],
        "reason": (f"{len(failures)} finding(s) across {enumerated} skill(s)"
                   if failures else f"{enumerated} skill(s) enumerated; README contract clean"),
    }
    if failures:
        out["remediation"] = ("Regenerate the layout fences and author the residue; see "
                              "SPEC.md §3.11 REQ-YF-DOC-001..018. `e-readme-desc` is NOT checked "
                              "here (REQ-YF-DOC-013) — it keeps its LLM route.")
    print(json.dumps(out, indent=1))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
