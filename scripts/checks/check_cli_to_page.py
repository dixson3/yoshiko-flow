#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_cli_to_page.py — REQ-CHECK-011: the MISSING DIRECTION of ``e-web-cli-surface``.

THE GAP.  That edge is ``path-resolves`` and **both** of its declared failure directions run
page->CLI: they catch a page naming a command that does not exist.  Neither can see the reverse —
a command that SHIPS and that no page documents.  Measured consequence: ``yf harness skills
prune-private``, which is live and **destructive**, is documented nowhere, and grepping the whole
published corpus for it returns no output.  One new direction reaches it.

REALIZER.  A set difference with an exit code (``REQ-CHECK-008(c)``), in the shape of
``check_skill_page_contract.py`` — not a prose edge.  A well-specified prose edge that is never
dispatched has a catch rate indistinguishable from having no edge at all.

THE PREDICATE, STATED EXPLICITLY: **corpus-wide TOKEN presence**.  "Does this token appear
anywhere on the published site?"  Not "on the right page", not "in the right sense".  Two
consequences follow, and both are declared rather than discovered later:

  * A token already documented for ANOTHER reason passes.  ``--force`` is documented at
    ``install.md`` and ``README.md``, so this checker cannot flag ``self install --force``, and
    plan-067 SC8 says so rather than claiming it.  A pair-level predicate ("this flag, on this
    command") would contradict the corpus-wide rule and reopen the ~30-false-failure per-page
    problem EXP-003 self-demonstrated.
  * **POSITIONAL ARGUMENTS ARE EXCLUDED.**  clap derives long flags from FIELD NAMES, so a naive
    extractor missed ``--prune-formulas`` while a corrected one returned 12 "missing" of which
    **5 were positionals** — a ~40% artifact rate.  A positional is not a documentable flag; it
    is a parameter shape.  The exclusion count is REPORTED (``artifact_rate``), never silent.

EXIT  0 every shipped surface is documented  ·  1 at least one is not  ·  2 INCONCLUSIVE
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECK = "check_cli_to_page"

ENUM_RE = re.compile(r"pub enum (\w*Command)\s*\{", re.M)
STRUCT_RE = re.compile(r"pub struct (\w+)\s*\{", re.M)


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    try:
        return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True, check=True).stdout.strip())
    except Exception:
        return Path(__file__).resolve().parent.parent.parent


def kebab(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def block_of(text: str, start: int) -> str:
    """The brace-balanced body beginning at the `{` at or after `start`."""
    i = text.index("{", start)
    depth, j = 0, i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1: j]
        j += 1
    raise ValueError("unbalanced braces")


def extract(src: str) -> tuple[list[str], list[str], list[str]]:
    """-> (subcommand verbs, long flags, EXCLUDED positional field names)."""
    verbs: list[str] = []
    for m in ENUM_RE.finditer(src):
        body = block_of(src, m.end() - 1)
        # A variant is an identifier at the start of a line inside the enum body, after any
        # attributes/doc comments. `#[command(name = "x")]` overrides the derived kebab name.
        pending_name = None
        for line in body.splitlines():
            s = line.strip()
            if s.startswith("#[command(name"):
                nm = re.search(r'name\s*=\s*"([^"]+)"', s)
                pending_name = nm.group(1) if nm else None
                continue
            if s.startswith(("///", "//", "#[")) or not s:
                continue
            v = re.match(r"([A-Z]\w*)\s*[({,]", s)
            if v:
                verbs.append(pending_name or kebab(v.group(1)))
                pending_name = None
    flags: list[str] = []
    positionals: list[str] = []
    for m in STRUCT_RE.finditer(src):
        body = block_of(src, m.end() - 1)
        pending_long = None      # None = no #[arg(long…)] seen for the next field
        pending_aliases: list[str] = []
        saw_arg = False
        for line in body.splitlines():
            s = line.strip()
            if s.startswith("#[arg("):
                saw_arg = True
                if re.search(r"\blong\b", s):
                    lm = re.search(r'long\s*=\s*"([^"]+)"', s)
                    pending_long = lm.group(1) if lm else True
                for am in re.finditer(r'visible_alias\s*=\s*"([^"]+)"', s):
                    pending_aliases.append(am.group(1))
                continue
            if s.startswith(("///", "//", "#[")) or not s:
                continue
            fm = re.match(r"pub (\w+)\s*:", s)
            if not fm:
                continue
            field = fm.group(1)
            if pending_long is True:
                flags.append("--" + kebab(field).replace("_", "-"))
            elif isinstance(pending_long, str):
                flags.append("--" + pending_long)
            else:
                # NO `#[arg(long…)]` -> a POSITIONAL. Excluded, and counted.
                positionals.append(field)
            flags.extend("--" + a for a in pending_aliases)
            pending_long, pending_aliases, saw_arg = None, [], False
    return sorted(set(verbs)), sorted(set(flags)), sorted(set(positionals))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=None)
    ap.add_argument("--cli", default="yf/src/cli.rs")
    ap.add_argument("--min-surfaces", type=int, default=20,
                    help="vacuity floor on the extracted shipped surface")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else repo_root()
    cli = root / a.cli
    if not cli.is_file():
        inconclusive(f"no CLI source at {a.cli}")
    try:
        verbs, flags, positionals = extract(cli.read_text(encoding="utf-8", errors="replace"))
    except ValueError as exc:
        inconclusive(f"could not parse {a.cli}: {exc}")

    surfaces = verbs + flags
    if len(surfaces) < a.min_surfaces:
        inconclusive(f"extracted {len(surfaces)} shipped surface(s) from {a.cli}, below the "
                     f"--min-surfaces floor of {a.min_surfaces} — the extractor, not the CLI, "
                     f"is what to fix")

    web = root / "web" / "content"
    if not web.is_dir():
        inconclusive("web/content is absent — the corpus cannot be assembled")
    files = sorted(web.rglob("*.md"))
    for extra in ("README.md", "AGENTS.md"):
        p = root / extra
        if p.is_file():
            files.append(p)
    if len(files) < 5:
        inconclusive(f"corpus expanded to {len(files)} file(s) — vacuous")
    corpus = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in files)

    missing = [s for s in surfaces
               if re.search(rf"(?<![\w-]){re.escape(s)}(?![\w-])", corpus) is None]
    # THE ARTIFACT RATE IS MEASURED WHERE IT BITES — inside the MISSING set, not over the
    # whole extraction. Pass-1 C5's ~40% is that ratio: a naive extractor that treated
    # positional fields as long flags returned 12 "missing" of which 5 were positionals. A rate
    # computed over all candidates would report a comfortable single digit and hide exactly the
    # thing the exclusion exists to remove.
    naive_extra = ["--" + kebab(f).replace("_", "-") for f in positionals]
    naive_missing = missing + [s_ for s_ in naive_extra
                               if re.search(rf"(?<![\w-]){re.escape(s_)}(?![\w-])",
                                            corpus) is None]
    artifacts = len(naive_missing) - len(missing)
    rate = round(100.0 * artifacts / len(naive_missing), 1) if naive_missing else 0.0
    candidates = len(surfaces) + len(positionals)

    rc = 1 if missing else 0
    if missing:
        print(f"{CHECK}: FAIL — shipped surface(s) documented NOWHERE on the site: "
              + ", ".join(missing), file=sys.stderr)

    out = {"check": CHECK, "verdict": "FAIL" if missing else "PASS",
           "predicate": "corpus-wide TOKEN presence (never per-page, never pair-level)",
           "subcommands": verbs, "long_flags": flags,
           "surfaces": len(surfaces), "floor": a.min_surfaces,
           "excluded_positionals": positionals,
           "extracted_candidates": candidates,
           "naive_missing": len(naive_missing),
           "artifact_rate_percent": rate,
           "artifact_rate_note": (f"a naive extractor that treated POSITIONAL fields as long "
                                  f"flags would report {len(naive_missing)} 'missing', of which "
                                  f"{artifacts} are artifacts — {rate}%. Pass-1 C5 measured this "
                                  f"class at ~40% and it is why positionals are excluded."),
           "missing": missing,
           "not_checked": [
               "a token documented for ANOTHER reason passes — `--force` is already documented "
               "at install.md and README.md, so this predicate cannot flag `self install "
               "--force`, and SC8 disowns that claim rather than asserting it",
               "whether the documentation is CORRECT or in the right place — token presence is "
               "the predicate; intent and placement are prose judgements",
               "script-verb coverage — irreducibly editorial, out of this edge's scope",
           ]}
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        print(f"{CHECK}: {len(surfaces)} shipped surface(s) ({len(verbs)} subcommand(s), "
              f"{len(flags)} long flag(s)); {len(positionals)} positional(s) EXCLUDED; "
              f"{len(missing)} undocumented vs {len(naive_missing)} naive "
              f"({rate}% artifact rate)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
