# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Change-validation engine for the `yf-change-validation` skill.

A fixed, repo-agnostic engine that infers, runs, and drift-checks a per-repo
`CHANGE-VALIDATION.md` validation recipe. Stdlib only (tomllib for TOML parsing,
py3.11+). Three subcommands:

- ``infer``       — read toolchain signals, emit a DRAFT manifest (§0 approved: no).
- ``run``         — execute the approved tier; clean refusal if unapproved/absent.
- ``check-drift`` — diff live signals vs the recorded §2 fingerprint; re-propose.

Spec requirements implemented (skills/yf-change-validation/spec/*.md):

infer       — REQ-INFER-001 (CI > runner > defaults precedence), REQ-INFER-002
              (PEP-723 per-file idiom), REQ-INFER-003 (skip disabled/tag-only CI),
              REQ-INFER-004 (validate-cmd seed / migration clause M4), REQ-INFER-005
              (FULL ⊇ CI ∪ repo-checks). Emits REQ-SCHEMA-001..007 manifest with
              §0 approved: no (REQ-SCHEMA-008 / REQ-ENGINE-002).
run         — REQ-ENGINE-001 (clean refusal, no stack trace), REQ-ENGINE-003 (run
              only recorded commands), REQ-ENGINE-004 (PASS/FAIL + first_failure,
              never auto-fix), REQ-ENGINE-005 (fail-closed → INCONCLUSIVE on missing
              tool), REQ-SCHEMA-006 (--changed affected-scoping).
check-drift — REQ-ENGINE-006 (re-propose, never auto-rewrite), REQ-SCHEMA-005
              (pure file-read + parse fingerprint).
"""

import argparse
import fnmatch
import glob as globmod
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

MANIFEST_NAME = "CHANGE-VALIDATION.md"
VALIDATE_CMD_CONFIG = ".yf-plan.local.json"

# Exit codes — distinct so callers can tell refusal from fail.
EXIT_OK = 0
EXIT_FAIL = 1
EXIT_REFUSED = 3
EXIT_INCONCLUSIVE = 4


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def repo_root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=2)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.cwd()


def tool_on_path(name: str) -> bool:
    """Fail-closed tool probe (REQ-ENGINE-005). Resolve the first shell token
    of a command to a binary on PATH; absent ⇒ INCONCLUSIVE, never a false PASS."""
    if not name:
        return True
    return shutil.which(name) is not None


def first_token(cmd: str) -> str:
    """The leading executable of a shell command, ignoring leading ``cd x && ``
    and ``VAR=val`` prefixes — used by the fail-closed tool probe."""
    s = cmd.strip()
    # strip a leading `cd <dir> && ` chain
    while True:
        m = re.match(r"^cd\s+\S+\s*&&\s*(.*)$", s)
        if not m:
            break
        s = m.group(1).strip()
    for tok in s.split():
        if "=" in tok and not tok.startswith("-") and re.match(r"^\w+=", tok):
            continue  # env assignment prefix
        return tok
    return s.split()[0] if s.split() else ""


def out_json(obj, fp=sys.stdout):
    json.dump(obj, fp, indent=2)
    fp.write("\n")


def _excluded(rel: Path) -> bool:
    """Skip generated / nested-worktree / vendored trees. Checked on a path
    relative to the repo root so a repo that itself lives under `.worktrees`
    (a git worktree checkout) is not wholesale excluded."""
    return any(part in (".worktrees", "node_modules", ".git", ".venv")
               for part in rel.parts)


def sha(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


# ===========================================================================
# SIGNAL READERS — best-effort; absent ⇒ skipped, recorded in fingerprint.
# Each returns a dict; reading is pure file-read + parse (REQ-SCHEMA-005).
# ===========================================================================

def read_cargo(root: Path) -> dict | None:
    """Cargo.toml incl. [workspace] members → cargo fmt/clippy/test (REQ-INFER-001
    default mapping). Workspace ⇒ --workspace flag."""
    p = root / "Cargo.toml"
    if not p.exists():
        return None
    try:
        data = tomllib.loads(p.read_text())
    except (OSError, tomllib.TOMLDecodeError):
        return None
    members = data.get("workspace", {}).get("members")
    ws = members is not None
    wflag = " --workspace" if ws else ""
    cmds = [
        "cargo fmt --all -- --check",
        f"cargo clippy{wflag} --all-targets -- -D warnings",
        f"cargo test{wflag}",
    ]
    return {
        "source": "Cargo.toml",
        "members": members,
        "fingerprint": sha(json.dumps(members, sort_keys=True)),
        "commands": cmds,
    }


def _yaml_run_steps(text: str) -> list[str]:
    """Tolerant extraction of YAML ``run:`` step bodies without a YAML dep.
    Handles inline ``run: cmd`` and block scalars ``run: |``. Good enough for
    seeding; the operator reviews the draft before approval."""
    steps: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)(-\s*)?run:\s*(.*)$", line)
        if m:
            indent = len(m.group(1))
            rest = m.group(3).strip()
            if rest in ("|", ">", "|-", ">-", "|+", ">+"):
                # block scalar: gather more-indented lines
                body = []
                j = i + 1
                while j < len(lines):
                    bl = lines[j]
                    if bl.strip() == "":
                        body.append("")
                        j += 1
                        continue
                    bindent = len(bl) - len(bl.lstrip())
                    if bindent <= indent:
                        break
                    body.append(bl[indent:].rstrip())
                    j += 1
                block = "\n".join(b for b in body if b.strip())
                for b in block.splitlines():
                    if b.strip():
                        steps.append(b.strip())
                i = j
                continue
            elif rest:
                steps.append(rest.strip("'\""))
        i += 1
    return steps


def _job_is_disabled(text: str) -> bool:
    """Whole-file heuristic: a workflow double-disabled with ``if: ${{ false }}``
    or tag-only (``tags:`` filter / ``on: [v*]``) is skipped (REQ-INFER-003).
    Conservative whole-file skip — the operator reviews the draft regardless."""
    if re.search(r"if:\s*\$\{\{\s*false\s*\}\}", text):
        return True
    if re.search(r"^\s*tags:\s*", text, re.MULTILINE):
        return True
    if re.search(r"on:\s*\[\s*['\"]?v\*", text):
        return True
    return False


def read_ci(root: Path) -> dict | None:
    """`.github/workflows/*.yml` run: steps — highest-fidelity seed, adopted
    verbatim (REQ-INFER-001). Skip disabled / tag-only workflows (REQ-INFER-003)."""
    wf_dir = root / ".github" / "workflows"
    if not wf_dir.is_dir():
        return None
    steps: list[str] = []
    skipped: list[str] = []
    per_file: dict[str, list[str]] = {}
    for wf in sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml")):
        try:
            text = wf.read_text()
        except OSError:
            continue
        if _job_is_disabled(text):
            skipped.append(wf.name)
            continue
        fsteps = _yaml_run_steps(text)
        if fsteps:
            per_file[wf.name] = fsteps
            steps.extend(fsteps)
    # de-dup preserving order
    seen = set()
    uniq = []
    for s in steps:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return {
        "source": ".github/workflows/*.yml",
        "skipped": skipped,
        "per_file": per_file,
        "steps": uniq,
        "fingerprint": sha("\n".join(uniq)),
    }


def _has_pep723_header(text: str) -> dict:
    """Detect a PEP-723 inline header and whether it declares dependencies."""
    m = re.search(r"^# /// script\s*$(.*?)^# ///\s*$", text, re.MULTILINE | re.DOTALL)
    if not m:
        return {"pep723": False, "has_deps": False}
    body = m.group(1)
    deps = re.search(r"dependencies\s*=\s*\[(.*?)\]", body, re.DOTALL)
    has_deps = bool(deps and deps.group(1).strip().strip("\n").strip())
    return {"pep723": True, "has_deps": has_deps}


def read_pytests(root: Path) -> dict | None:
    """`**/test_*.py` glob + per-file PEP-723 header detection → per-file
    invocation idiom (REQ-INFER-002). PEP-723 w/ deps ⇒ `uv run <f>`; PEP-723
    w/o deps ⇒ `uv run --with pytest python3 -m pytest <f> -q`; no header +
    pyproject ⇒ project pytest."""
    files = sorted(
        p for p in root.glob("**/test_*.py")
        if not _excluded(p.relative_to(root))
    )
    if not files:
        return None
    has_pyproject = (root / "pyproject.toml").exists()
    commands: list[str] = []
    headers: dict[str, dict] = {}
    no_header_files: list[str] = []
    for f in files:
        rel = str(f.relative_to(root))
        try:
            text = f.read_text()
        except OSError:
            continue
        hdr = _has_pep723_header(text)
        headers[rel] = hdr
        if hdr["pep723"]:
            if hdr["has_deps"]:
                commands.append(f"uv run {rel}")
            else:
                commands.append(f"uv run --with pytest python3 -m pytest {rel} -q")
        else:
            no_header_files.append(rel)
    if no_header_files:
        if has_pyproject:
            commands.append("uv run pytest")
        else:
            # No project config to anchor a single pytest — run each per-file.
            for rel in no_header_files:
                commands.append(f"uv run --with pytest python3 -m pytest {rel} -q")
    return {
        "source": "**/test_*.py",
        "files": [str(f.relative_to(root)) for f in files],
        "headers": headers,
        "fingerprint": sha(json.dumps(headers, sort_keys=True)),
        "commands": commands,
    }


def read_package_json(root: Path) -> dict | None:
    """package.json scripts → npm ci + test/build/lint scripts present."""
    p = root / "package.json"
    cwd = ""
    if not p.exists():
        # common docs subdir
        alt = root / "website" / "package.json"
        if alt.exists():
            p = alt
            cwd = "website"
        else:
            return None
    try:
        data = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    scripts = data.get("scripts", {}) or {}
    cmds = []
    if scripts:
        prefix = f"cd {cwd} && " if cwd else ""
        cmds.append(f"{prefix}npm ci")
        for name in ("lint", "test", "build"):
            if name in scripts:
                cmds.append(f"{prefix}npm run {name}")
    return {
        "source": str(p.relative_to(root)),
        "cwd": cwd,
        "scripts": sorted(scripts.keys()),
        "fingerprint": sha(json.dumps(sorted(scripts.keys()))),
        "commands": cmds,
    }


def _runner_targets(text: str, kind: str) -> list[str]:
    targets = []
    if kind == "just":
        for m in re.finditer(r"^([a-zA-Z_][\w-]*)\s*:", text, re.MULTILINE):
            targets.append(m.group(1))
    else:  # make
        for m in re.finditer(r"^([a-zA-Z_][\w-]*)\s*:(?!=)", text, re.MULTILINE):
            targets.append(m.group(1))
    return [t for t in targets if t in ("test", "lint", "check", "build", "fmt")]


def read_runners(root: Path) -> dict | None:
    """justfile / Makefile targets (runner-target precedence tier — REQ-INFER-001)."""
    found = {}
    cmds = []
    for fname, kind, runner in (("justfile", "just", "just"),
                                ("Makefile", "make", "make")):
        p = root / fname
        if not p.exists():
            continue
        try:
            text = p.read_text()
        except OSError:
            continue
        tgts = _runner_targets(text, kind)
        found[fname] = tgts
        for t in tgts:
            cmds.append(f"{runner} {t}")
    if not found:
        return None
    return {
        "source": "justfile/Makefile",
        "targets": found,
        "fingerprint": sha(json.dumps(found, sort_keys=True)),
        "commands": cmds,
    }


def read_check_scripts(root: Path) -> dict | None:
    """Repo `--check` scripts (e.g. _shared/sync.py --check) — repo-checks that
    CI may omit but that exist on disk (REQ-INFER-005). Heuristic: a *.py that
    parses a ``--check`` flag in its source."""
    found = []
    cmds = []
    for p in sorted(root.glob("**/*.py")):
        rel_p = p.relative_to(root)
        if _excluded(rel_p):
            continue
        rel = str(rel_p)
        if "test_" in p.name:
            continue
        try:
            text = p.read_text()
        except OSError:
            continue
        if re.search(r"add_argument\(\s*[\"']--check[\"']", text) or \
           re.search(r"['\"]--check['\"]", text) and "argparse" in text:
            found.append(rel)
            cmds.append(f"uv run {rel} --check")
    if not found:
        return None
    return {
        "source": "repo --check scripts",
        "scripts": found,
        "fingerprint": sha(json.dumps(found, sort_keys=True)),
        "commands": cmds,
    }


def read_validate_cmd(root: Path) -> dict | None:
    """Migration clause M4 / REQ-INFER-004: an existing `.yf-plan.local.json`
    `validate-cmd` SEEDS the FULL tier."""
    p = root / VALIDATE_CMD_CONFIG
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    vc = data.get("validate-cmd")
    if not vc:
        return None
    return {
        "source": VALIDATE_CMD_CONFIG,
        "validate_cmd": vc,
        "fingerprint": sha(vc),
        "commands": [vc],
    }


def gather_signals(root: Path) -> dict:
    """Run every reader; absent signals are simply omitted (skipped)."""
    return {
        name: reader(root)
        for name, reader in (
            ("validate_cmd", read_validate_cmd),
            ("cargo", read_cargo),
            ("ci", read_ci),
            ("pytests", read_pytests),
            ("package_json", read_package_json),
            ("runners", read_runners),
            ("check_scripts", read_check_scripts),
        )
        if reader(root) is not None
    }


# ===========================================================================
# infer — build a draft manifest from signals (FULL ⊇ CI ∪ repo-checks)
# ===========================================================================

def _slug_id(cmd: str, taken: set) -> str:
    """Stable short id for a FAST row, referenced by §3."""
    tok = first_token(cmd)
    base = re.sub(r"[^a-z0-9]+", "-", tok.lower()).strip("-") or "cmd"
    # add a discriminator from the command to keep ids unique
    extra = re.findall(r"[a-z0-9_]+", cmd.lower())
    cand = base
    n = 1
    while cand in taken:
        suffix = extra[n] if n < len(extra) else str(n)
        cand = f"{base}-{suffix}"
        n += 1
    taken.add(cand)
    return cand


def build_recipe(signals: dict) -> dict:
    """Construct FAST + FULL tiers and §3 trigger scope from signals.

    Precedence (REQ-INFER-001): CI run: steps win on flags, glob-scan wins on
    existence. FULL ⊇ CI ∪ repo-checks ∪ seeded validate-cmd (REQ-INFER-005)."""
    full_cmds: list[str] = []
    seen = set()

    def add(cmd, cwd=""):
        key = (cmd, cwd)
        if key in seen:
            return
        seen.add(key)
        full_cmds.append({"cmd": cmd, "cwd": cwd})

    # 1. seeded validate-cmd first (migration clause M4 / REQ-INFER-004)
    if signals.get("validate_cmd"):
        for c in signals["validate_cmd"]["commands"]:
            add(c)
    # 2. CI run: steps — verbatim, highest fidelity
    if signals.get("ci"):
        for c in signals["ci"]["steps"]:
            add(c)
    # 3. runner targets when CI silent
    if signals.get("runners"):
        for c in signals["runners"]["commands"]:
            add(c)
    # 4. manifest-derived defaults (cargo) — existence-driven
    if signals.get("cargo"):
        for c in signals["cargo"]["commands"]:
            add(c)
    # 5. repo-checks that exist on disk (CI may omit) — glob-scan wins on existence
    if signals.get("pytests"):
        for c in signals["pytests"]["commands"]:
            add(c)
    if signals.get("check_scripts"):
        for c in signals["check_scripts"]["commands"]:
            add(c)
    if signals.get("package_json"):
        for c in signals["package_json"]["commands"]:
            cwd = signals["package_json"].get("cwd", "")
            add(c, "")  # cwd already embedded in cmd via `cd …` when present

    # FAST tier: cheap, affected-scoped subset. Heuristic seed — derive ids and
    # a §3 glob→id map. The operator refines this before approval.
    taken: set = set()
    fast_rows = []
    scope_map: list[tuple[str, str]] = []  # (glob, id)

    def fast_add(cmd, globs, cwd=""):
        rid = _slug_id(cmd, taken)
        fast_rows.append({"id": rid, "cmd": cmd, "cwd": cwd})
        for g in globs:
            scope_map.append((g, rid))
        return rid

    if signals.get("cargo"):
        fast_add("cargo test --workspace" if "--workspace"
                 in " ".join(signals["cargo"]["commands"]) else "cargo test",
                 ["*.rs", "**/*.rs", "Cargo.toml", "**/Cargo.toml"])
    if signals.get("pytests"):
        for cmd, rel in zip(signals["pytests"]["commands"],
                            signals["pytests"]["files"]):
            # scope each suite to its own directory tree
            d = str(Path(rel).parent)
            globs = [f"{d}/**", rel] if d not in (".", "") else [rel]
            fast_add(cmd, globs)
    if signals.get("check_scripts"):
        for cmd, rel in zip(signals["check_scripts"]["commands"],
                            signals["check_scripts"]["scripts"]):
            d = str(Path(rel).parent)
            globs = [f"{d}/**"] if d not in (".", "") else [rel]
            fast_add(cmd, globs)

    return {
        "fast": fast_rows,
        "full": full_cmds,
        "scope": scope_map,
    }


def render_manifest(recipe: dict, signals: dict) -> str:
    """Render the four-section CHANGE-VALIDATION.md (REQ-SCHEMA-001..007),
    drafted with §0 approved: no (REQ-SCHEMA-008 / REQ-ENGINE-002)."""
    lines = []
    lines.append("# CHANGE-VALIDATION.md")
    lines.append("")
    lines.append("> DRAFT — inferred by `change_validation.py infer`. Review every row,")
    lines.append("> then set §0 `approved: yes` to enforce. Inert until approved.")
    lines.append("")

    # §0
    lines.append("## 0. Status")
    lines.append("")
    lines.append("approved: no")
    lines.append("")

    # §1
    lines.append("## 1. Tiers")
    lines.append("")
    lines.append("### fast")
    lines.append("")
    lines.append("| id | cmd | cwd | timeout |")
    lines.append("|:--|:--|:--|--:|")
    for r in recipe["fast"]:
        lines.append(f"| `{r['id']}` | `{r['cmd']}` | {r.get('cwd','') or ''} |  |")
    if not recipe["fast"]:
        lines.append("| | | | |")
    lines.append("")
    lines.append("### full")
    lines.append("")
    lines.append("| id | cmd | cwd | timeout |")
    lines.append("|:--|:--|:--|--:|")
    for r in recipe["full"]:
        lines.append(f"|  | `{r['cmd']}` | {r.get('cwd','') or ''} |  |")
    if not recipe["full"]:
        lines.append("| | | | |")
    lines.append("")

    # §2
    lines.append("## 2. Signal Fingerprint")
    lines.append("")
    lines.append("| source-path | parsed-value-or-hash |")
    lines.append("|:--|:--|")
    for name, sig in signals.items():
        src = sig.get("source", name)
        fp = sig.get("fingerprint", "")
        lines.append(f"| `{src}` | `{fp}` |")
    if not signals:
        lines.append("| | |")
    lines.append("")

    # §3
    lines.append("## 3. Trigger Scope")
    lines.append("")
    lines.append("| changed-path glob | scopes to (FAST ids) |")
    lines.append("|:--|:--|")
    # group ids by glob
    by_glob: dict[str, list[str]] = {}
    for g, rid in recipe["scope"]:
        by_glob.setdefault(g, []).append(rid)
    for g, ids in by_glob.items():
        lines.append(f"| `{g}` | {', '.join(f'`{i}`' for i in ids)} |")
    if not by_glob:
        lines.append("| | |")
    lines.append("")
    return "\n".join(lines)


def cmd_infer(args) -> int:
    root = repo_root()
    signals = gather_signals(root)
    recipe = build_recipe(signals)
    manifest_text = render_manifest(recipe, signals)

    if args.write:
        dest = root / MANIFEST_NAME
        dest.write_text(manifest_text)

    if args.json:
        out_json({
            "status": "draft",
            "approved": False,
            "signals": {k: {kk: vv for kk, vv in v.items() if kk != "commands"}
                        for k, v in signals.items()},
            "recipe": recipe,
            "manifest_written": bool(args.write),
            "manifest_path": str((root / MANIFEST_NAME)) if args.write else None,
            "manifest_preview": manifest_text,
        })
    else:
        sys.stdout.write(manifest_text + "\n")
    return EXIT_OK


# ===========================================================================
# manifest parsing — pure read, used by run + check-drift
# ===========================================================================

def _section_blocks(text: str) -> dict:
    """Split a manifest into its `##`-headed sections keyed by leading number."""
    blocks: dict[str, str] = {}
    cur_key = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(\d+)\.", line)
        if m:
            if cur_key is not None:
                blocks[cur_key] = "\n".join(buf)
            cur_key = m.group(1)
            buf = []
        else:
            buf.append(line)
    if cur_key is not None:
        blocks[cur_key] = "\n".join(buf)
    return blocks


def _parse_table_rows(block: str) -> list[list[str]]:
    """Parse a GFM table body into lists of cell strings (header + delimiter
    rows skipped). The row immediately above a delimiter row is the header and
    is dropped along with the delimiter."""
    raw = []
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        is_delim = (all(re.match(r"^:?-{1,}:?$", c) or c == "" for c in cells)
                    and any("-" in c for c in cells))
        raw.append((is_delim, cells))
    rows = []
    for i, (is_delim, cells) in enumerate(raw):
        if is_delim:
            continue
        # drop the header row that immediately precedes a delimiter row
        if i + 1 < len(raw) and raw[i + 1][0]:
            continue
        rows.append(cells)
    return rows


def _strip_code(s: str) -> str:
    return s.strip().strip("`").strip()


def parse_manifest(root: Path):
    """Parse an approved manifest into structured form, or return a refusal
    dict if absent / unapproved (REQ-ENGINE-001/002). Never raises on the
    expected unapproved/absent conditions."""
    p = root / MANIFEST_NAME
    if not p.exists():
        return None, {"status": "refused", "reason": "not approved",
                      "detail": "manifest absent"}
    try:
        text = p.read_text()
    except OSError as e:
        return None, {"status": "refused", "reason": "not approved",
                      "detail": f"manifest unreadable: {e}"}
    blocks = _section_blocks(text)

    # §0 approval gate
    status_block = blocks.get("0", "")
    approved = bool(re.search(r"approved:\s*yes", status_block, re.IGNORECASE))
    if not approved:
        return None, {"status": "refused", "reason": "not approved",
                      "detail": "§0 approved: no"}

    # §1 tiers
    tiers = {"fast": [], "full": []}
    tier_block = blocks.get("1", "")
    cur = None
    sub_buf: dict[str, list[str]] = {"fast": [], "full": []}
    for line in tier_block.splitlines():
        h = re.match(r"^###\s+(fast|full)\b", line, re.IGNORECASE)
        if h:
            cur = h.group(1).lower()
            continue
        if cur:
            sub_buf[cur].append(line)
    for tier in ("fast", "full"):
        for cells in _parse_table_rows("\n".join(sub_buf[tier])):
            # columns: id | cmd | cwd | timeout
            cells = (cells + ["", "", "", ""])[:4]
            rid = _strip_code(cells[0]) or None
            cmd = _strip_code(cells[1])
            cwd = _strip_code(cells[2]) or None
            tmo = _strip_code(cells[3])
            timeout = int(tmo) if tmo.isdigit() else None
            if not cmd:
                continue
            tiers[tier].append({"id": rid, "cmd": cmd, "cwd": cwd,
                                "timeout": timeout})

    # §3 trigger scope
    scope = []
    for cells in _parse_table_rows(blocks.get("3", "")):
        if len(cells) < 2:
            continue
        g = _strip_code(cells[0])
        ids = [_strip_code(x) for x in re.split(r"[,\s]+", cells[1]) if _strip_code(x)]
        if g:
            scope.append({"glob": g, "ids": ids})

    return {"tiers": tiers, "scope": scope, "text": text}, None


# ===========================================================================
# run — execute the approved tier (REQ-ENGINE-004/005)
# ===========================================================================

def _scoped_ids(scope, changed: list[str]) -> set:
    """Union of FAST ids selected by §3 globs that any changed path matches
    (REQ-SCHEMA-006)."""
    selected: set = set()
    for path in changed:
        for entry in scope:
            if fnmatch.fnmatch(path, entry["glob"]) or \
               fnmatch.fnmatch(path, entry["glob"].replace("/**", "/*")):
                selected.update(entry["ids"])
    return selected


def run_command(row: dict, root: Path) -> dict:
    """Run one row via `sh -c`. Fail-closed: missing tool ⇒ inconclusive."""
    cmd = row["cmd"]
    tok = first_token(cmd)
    result = {"id": row.get("id"), "cmd": cmd}
    if not tool_on_path(tok):
        result.update({"ok": False, "returncode": None,
                       "status": "inconclusive",
                       "output_tail": f"required tool not on PATH: {tok}"})
        return result
    cwd = root / row["cwd"] if row.get("cwd") else root
    try:
        proc = subprocess.run(
            ["sh", "-c", cmd], cwd=str(cwd),
            capture_output=True, text=True,
            timeout=row.get("timeout") or None,
        )
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-20:]
        result.update({
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "status": "pass" if proc.returncode == 0 else "fail",
            "output_tail": "\n".join(tail),
        })
    except subprocess.TimeoutExpired:
        result.update({"ok": False, "returncode": None, "status": "fail",
                       "output_tail": f"timeout after {row.get('timeout')}s"})
    return result


def cmd_run(args) -> int:
    root = repo_root()
    manifest, refusal = parse_manifest(root)
    if refusal is not None:
        if args.json:
            out_json(refusal)
        else:
            sys.stdout.write(f"{refusal['status']}: {refusal['reason']} "
                             f"({refusal.get('detail','')})\n")
        return EXIT_REFUSED

    tier = args.tier
    rows = manifest["tiers"].get(tier, [])

    if args.changed and tier == "fast":
        sel = _scoped_ids(manifest["scope"], args.changed)
        rows = [r for r in rows if r.get("id") in sel]

    results = []
    first_failure = None
    tier_status = "pass"
    for row in rows:
        r = run_command(row, root)
        results.append(r)
        if r["status"] == "inconclusive" and tier_status != "fail":
            tier_status = "inconclusive"
        if r["status"] == "fail":
            tier_status = "fail"
            if first_failure is None:
                first_failure = r
            break  # stop on first failure (run-and-report)

    payload = {
        "tier": tier,
        "status": tier_status,
        "commands": results,
        "first_failure": first_failure,
    }
    if args.json:
        out_json(payload)
    else:
        sys.stdout.write(f"tier={tier} status={tier_status}\n")
        if first_failure:
            sys.stdout.write(f"first_failure: {first_failure['cmd']}\n")

    if tier_status == "fail":
        return EXIT_FAIL
    if tier_status == "inconclusive":
        return EXIT_INCONCLUSIVE
    return EXIT_OK


# ===========================================================================
# check-drift — diff live signals vs recorded §2; re-propose (REQ-ENGINE-006)
# ===========================================================================

def _recorded_fingerprint(text: str) -> dict:
    """Read §2 fingerprint rows from a manifest into {source: value}."""
    blocks = _section_blocks(text)
    fp = {}
    for cells in _parse_table_rows(blocks.get("2", "")):
        if len(cells) < 2:
            continue
        src = _strip_code(cells[0])
        val = _strip_code(cells[1])
        if src:
            fp[src] = val
    return fp


def cmd_check_drift(args) -> int:
    root = repo_root()
    p = root / MANIFEST_NAME
    if not p.exists():
        payload = {"drift": False, "reason": "no manifest",
                   "added": [], "removed": [], "changed": [],
                   "proposed_delta": None}
        out_json(payload) if args.json else \
            sys.stdout.write("no manifest; nothing to drift-check\n")
        return EXIT_OK

    recorded = _recorded_fingerprint(p.read_text())
    signals = gather_signals(root)
    live = {sig.get("source", name): sig.get("fingerprint", "")
            for name, sig in signals.items()}

    rec_keys = set(recorded)
    live_keys = set(live)
    added = sorted(live_keys - rec_keys)
    removed = sorted(rec_keys - live_keys)
    changed = sorted(k for k in (rec_keys & live_keys) if recorded[k] != live[k])
    drift = bool(added or removed or changed)

    proposed_delta = None
    if drift:
        recipe = build_recipe(signals)
        proposed_delta = {
            "note": "re-proposal only — never auto-rewritten; operator confirms",
            "proposed_full": recipe["full"],
            "proposed_fast": recipe["fast"],
        }

    payload = {
        "drift": drift,
        "added": [{"source": k, "live": live[k]} for k in added],
        "removed": [{"source": k, "recorded": recorded[k]} for k in removed],
        "changed": [{"source": k, "recorded": recorded[k], "live": live[k]}
                    for k in changed],
        "proposed_delta": proposed_delta,
    }
    if args.json:
        out_json(payload)
    else:
        sys.stdout.write(f"drift={'yes' if drift else 'no'} "
                         f"added={len(added)} removed={len(removed)} "
                         f"changed={len(changed)}\n")
    return EXIT_OK


# ===========================================================================
# CLI
# ===========================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="change_validation.py",
        description="Infer / run / drift-check a CHANGE-VALIDATION.md recipe.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("infer", help="emit a DRAFT CHANGE-VALIDATION.md from "
                                      "toolchain signals (§0 approved: no)")
    pi.add_argument("--json", action="store_true", help="emit JSON")
    pi.add_argument("--write", action="store_true",
                    help="write the draft to CHANGE-VALIDATION.md")
    pi.set_defaults(func=cmd_infer)

    pr = sub.add_parser("run", help="run an approved tier; clean refusal if "
                                    "unapproved/absent")
    pr.add_argument("--tier", choices=["fast", "full"], required=True)
    pr.add_argument("--changed", nargs="*", default=None,
                    help="changed paths; FAST affected-scoping (§3)")
    pr.add_argument("--json", action="store_true", help="emit JSON")
    pr.set_defaults(func=cmd_run)

    pd = sub.add_parser("check-drift", help="diff live signals vs §2 "
                                            "fingerprint; re-propose (no rewrite)")
    pd.add_argument("--json", action="store_true", help="emit JSON")
    pd.set_defaults(func=cmd_check_drift)

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Exception as e:  # defensive: no traceback leaks on unexpected errors
        out_json({"status": "error", "error": str(e),
                  "type": type(e).__name__})
        return EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
