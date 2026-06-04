#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Dependency-aware installer for the beads-backed skills.

Reads each skill's SKILL.md frontmatter (skill-group / depends-on-tool /
depends-on-skill), computes install groups dynamically, resolves transitive in-repo
skill dependencies, and checks tool prerequisites — then installs the selected skills
(and their companion rules) into a Claude Code / agent tree.

This is the implementation behind install.sh (a thin wrapper that execs `uv run`
this file). Group membership and dependencies live in frontmatter, so adding or
regrouping a skill needs no edit here.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_DIR = Path(__file__).resolve().parent
SKILLS_DIR = REPO_DIR / "skills"


# --- Frontmatter parsing -------------------------------------------------------


def parse_frontmatter(skill_md: Path) -> dict:
    """Return the YAML frontmatter (first --- ... --- block) of a SKILL.md as a dict."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    # Split on the fence: ["", <frontmatter>, <body...>]
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return {}
    front = parts[0][len("---"):]
    data = yaml.safe_load(front)
    return data if isinstance(data, dict) else {}


def load_skills() -> dict[str, dict]:
    """Discover every skills/<name>/ with a SKILL.md; return {name: meta}.

    meta = {group, tools: [...], skills: [...]} where missing keys default empty.
    """
    skills: dict[str, dict] = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        fm = parse_frontmatter(skill_md)
        skills[skill_dir.name] = {
            "group": fm.get("skill-group"),
            "tools": _as_list(fm.get("depends-on-tool")),
            "skills": _as_list(fm.get("depends-on-skill")),
        }
    return skills


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value]


def computed_groups(skills: dict[str, dict]) -> list[str]:
    return sorted({m["group"] for m in skills.values() if m["group"]})


# --- Selection + dependency closure -------------------------------------------


def resolve_install_set(
    skills: dict[str, dict], base: set[str], log: list[str]
) -> set[str]:
    """Close `base` over depends-on-skill (bare in-repo names).

    Unresolved names are warned as external/assumed-provided and skipped. Cross-group
    pulls are logged.
    """
    install: set[str] = set()
    queue = list(base)
    while queue:
        name = queue.pop()
        if name in install:
            continue
        install.add(name)
        for dep in skills[name]["skills"]:
            if dep not in skills:
                log.append(
                    f"  note: {name} depends-on-skill '{dep}' — not found in-repo; "
                    f"external / assumed-provided, skipped"
                )
                continue
            if dep not in install:
                if (
                    skills[name]["group"]
                    and skills[dep]["group"]
                    and skills[dep]["group"] != skills[name]["group"]
                ):
                    log.append(
                        f"  note: pulling '{dep}' (group {skills[dep]['group']}) as a "
                        f"dependency of '{name}' (group {skills[name]['group']}) — "
                        f"crosses group boundary"
                    )
                queue.append(dep)
    return install


# --- Tool prereq check ---------------------------------------------------------


def check_tools(skills: dict[str, dict], install: set[str]) -> list[str]:
    """Return the sorted list of required tools that are missing from PATH."""
    required: set[str] = set()
    for name in install:
        required.update(skills[name]["tools"])
    return sorted(t for t in required if shutil.which(t) is None)


# --- Destination resolution (parity with install.sh) ---------------------------


def resolve_dests(scope: str, surface: str, target: str | None) -> tuple[Path, Path]:
    if target:
        skills_dest = Path(target)
        rules_dest = skills_dest.parent / "rules"
    else:
        anchor = (
            Path.home()
            if scope == "user"
            else _git_root_or_cwd()
        )
        skills_dest = anchor / f".{surface}" / "skills"
        rules_dest = anchor / f".{surface}" / "rules"
    return skills_dest, rules_dest


def _git_root_or_cwd() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        return Path(out.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


# --- Install -------------------------------------------------------------------


def install_skill(name: str, skills_dest: Path) -> None:
    src = SKILLS_DIR / name
    dest = skills_dest / name
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["rsync", "-a", "--delete", "--exclude=.gitignore",
         f"{src}/", f"{dest}/"],
        check=True,
    )
    print(f"  OK: {name} -> {dest}")


def install_rules(name: str, rules_dest: Path, force: bool) -> bool:
    """Surface a skill's protocols/*.md to the rules dir. Returns True if any rule handled."""
    protocols = SKILLS_DIR / name / "protocols"
    if not protocols.is_dir():
        return False
    handled = False
    for rule in sorted(protocols.glob("*.md")):
        rules_dest.mkdir(parents=True, exist_ok=True)
        target = rules_dest / rule.name
        if target.exists() and not force:
            print(f"      rule {rule.name}: kept (exists; --force to overwrite)")
        else:
            shutil.copyfile(rule, target)
            print(f"      rule {rule.name} -> {target}")
        handled = True
    return handled


# --- CLI -----------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="install.py",
        description="Install beads-backed skills (and companion rules), "
                    "dependency-aware, into a Claude Code / agent tree.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--scope", choices=["user", "project"], default="user",
                   help="user → $HOME; project → git root (else cwd). Default: user")
    p.add_argument("--surface", choices=["claude", "agents"], default="claude",
                   help="claude → <root>/.claude/...; agents → <root>/.agents/... Default: claude")
    p.add_argument("--target", metavar="PATH",
                   help="override skills destination (rules go to <dirname>/rules)")
    p.add_argument("--group", metavar="NAME",
                   help="install only skills in this group (computed from frontmatter)")
    p.add_argument("--strict", action="store_true",
                   help="treat a missing depends-on-tool as a hard failure (no install)")
    p.add_argument("--dry-run", action="store_true",
                   help="print the resolved install set + tool report; install nothing")
    p.add_argument("--list-groups", action="store_true",
                   help="print the computed group set and exit")
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing companion rule (default keeps hand-edits)")
    p.add_argument("skills", nargs="*", metavar="skill",
                   help="explicit skill names (override --group); omit to install all")
    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    skills = load_skills()
    if not skills:
        print(f"Error: no skills found under {SKILLS_DIR}", file=sys.stderr)
        return 1
    groups = computed_groups(skills)

    if args.list_groups:
        print("Install groups (computed from skill-group frontmatter):")
        for g in groups:
            members = sorted(n for n, m in skills.items() if m["group"] == g)
            print(f"  {g}: {', '.join(members)}")
        return 0

    # --- Selection precedence: explicit names > --group > all ---
    log: list[str] = []
    if args.skills:
        unknown = [s for s in args.skills if s not in skills]
        if unknown:
            print(f"Error: unknown skill(s): {', '.join(unknown)}", file=sys.stderr)
            print(f"Available: {', '.join(sorted(skills))}", file=sys.stderr)
            return 1
        if args.group:
            log.append("  note: explicit skill names given — ignoring --group")
        base = set(args.skills)
    elif args.group:
        if args.group not in groups:
            print(f"Error: unknown group '{args.group}'. "
                  f"Valid groups: {', '.join(groups)}", file=sys.stderr)
            return 1
        base = {n for n, m in skills.items() if m["group"] == args.group}
    else:
        base = set(skills)

    install = resolve_install_set(skills, base, log)

    # --- Tool prereq check ---
    missing = check_tools(skills, install)

    # --- Report ---
    print(f"Skills to install ({len(install)}): {', '.join(sorted(install))}")
    for line in log:
        print(line)
    if missing:
        print(f"Missing tool(s) on PATH: {', '.join(missing)}")
        if args.strict:
            print("  --strict: aborting (no skill installed).", file=sys.stderr)
            return 2
        print("  warning: installing anyway — these skills are inert until the "
              "tool(s) are present.")

    if args.dry_run:
        print("(dry run — nothing installed)")
        return 0

    skills_dest, rules_dest = resolve_dests(args.scope, args.surface, args.target)

    if shutil.which("rsync") is None:
        print("Error: rsync not found on PATH (required to copy skill files).",
              file=sys.stderr)
        return 1

    installed = 0
    have_rules = False
    for name in sorted(install):
        install_skill(name, skills_dest)
        if install_rules(name, rules_dest, args.force):
            have_rules = True
        installed += 1

    print()
    print(f"Installed {installed} skill(s) -> {skills_dest}")
    if have_rules:
        print(f"Companion rules -> {rules_dest}")
        print()
        print("Per-project setup (run once from the project root, for skills that ship rules):")
        print("  /<skill> init   # checks prerequisites + consent-only setup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
