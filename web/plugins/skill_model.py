"""skill_model.py — THE ONE READER of `skills/*/SKILL.md` frontmatter.

Factored out of ``skill_pages.py`` (plan-067 Issue 5.1) so the published skill PAGE and the
generated per-skill DIAGRAM **provably read one source**. Two readers of the same frontmatter is
two grammars, and they disagree exactly where it matters — which is the defect class
``REQ-CHECK-012`` was written for: ``frontmatter.rs`` and ``skill_pages.py`` each read
``user-invocable`` correctly *by their own lights*, and the disagreement lived in a default
argument nobody was looking at.

This module has **no pelican import and no yaml-plugin coupling**, so the diagram generator can
import it from a plain script without pulling in the site build.
"""
from __future__ import annotations

import glob
import logging
import os
import re

import yaml

logger = logging.getLogger(__name__)


def parse_frontmatter(text):
    """The leading `--- … ---` YAML block, or `{}` when absent/unparseable."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except Exception:
        return {}


def split_description(description):
    """-> (summary, trigger, skip) from the `TRIGGER when:` / `SKIP for:` convention."""
    text = " ".join((description or "").split())
    trigger = skip = ""
    trig_idx = text.find("TRIGGER when:")
    skip_idx = text.find("SKIP for:")
    if skip_idx != -1:
        skip = text[skip_idx + len("SKIP for:") :].strip()
        text = text[:skip_idx].strip()
    if trig_idx != -1 and (skip_idx == -1 or trig_idx < skip_idx):
        trigger = text[trig_idx + len("TRIGGER when:") :].strip()
        summary = text[:trig_idx].strip()
    else:
        summary = text
    return summary, trigger, skip


def read_user_invocable(fm, path):
    """Read the TRI-STATE ``user-invocable:`` key (REQ-CHECK-012).

    ``yf/src/frontmatter.rs`` types this ``Option<bool>``: absent means UNKNOWN, which is a
    different fact from a declared ``false``. This used to be ``bool(fm.get(..., False))`` — a
    one-word default that collapsed the two and rendered four skills as "auto (fires from its
    description conditions)" while their own descriptions read ``TRIGGER when:
    /yf-markdown-lint invoked``. A live false claim on the published site, produced by nothing
    but a default argument.

    ``REQ-CHECK-012(a)`` fixes this at the PRODUCER — every ``SKILL.md`` now populates the key,
    and ``scripts/checks/check_user_invocable.py`` asserts it mechanically (b). This reader
    carries (c): where a consumer must still choose, it chooses the reading that FAILS LOUDLY.
    The absent case warns — fatal under the ``--fatal warnings`` build the validation recipe
    runs — instead of silently asserting the more plausible-looking falsehood.
    """
    raw = fm.get("user-invocable", None)
    if raw is None:
        logger.warning(
            "skill_model: %s omits the tri-state `user-invocable:` key (REQ-CHECK-012). "
            "Absent is UNKNOWN, not False; populate it at the producer rather than "
            "defaulting here.", path,
        )
        return False
    return bool(raw)


def _invocation_verbs(text, name):
    """Slash SUB-VERBS from the normalised `## Invocation` bullet list.

    Placeholders (`<objective>`, `[<path> ...]`) declare an ARGUMENT, not a verb, and are
    skipped — the same rule `check_required_set.py` applies, stated once here so the two cannot
    diverge.
    """
    m = re.search(r"^## Invocation\s*$", text, re.M)
    if not m:
        return []
    tail = text[m.end():]
    nxt = re.search(r"^## ", tail, re.M)
    body = tail[: nxt.start()] if nxt else tail
    verbs = []
    for line in body.splitlines():
        bm = re.match(r"^- `(/[a-z0-9-]+)([^`]*)`", line)
        if not bm or bm.group(1) != f"/{name}":
            continue
        rest = bm.group(2).strip()
        if not rest or rest[0] in "<[":
            continue
        v = rest.split()[0]
        if v not in verbs:
            verbs.append(v)
    return verbs


def _listing(skill_dir, sub, suffix=".md"):
    d = os.path.join(skill_dir, sub)
    if not os.path.isdir(d):
        return []
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "*" + suffix)))


def read_skills(repo_root):
    """Read every `skills/*/SKILL.md`; return a sorted list of skill dicts.

    The dict is the SHARED MODEL. `skill_pages.py` renders the page from it and
    `skill_diagrams.py` emits d2 from it, so a frontmatter fact cannot be true on one surface
    and false on the other.
    """
    skills = []
    pattern = os.path.join(repo_root, "skills", "*", "SKILL.md")
    for path in sorted(glob.glob(pattern)):
        skill_dir = os.path.dirname(path)
        text = open(path, encoding="utf-8").read()
        fm = parse_frontmatter(text)
        name = fm.get("name") or os.path.basename(skill_dir)
        summary, trigger, skip = split_description(fm.get("description", ""))
        skills.append(
            {
                "name": name,
                "group": fm.get("skill-group", "other"),
                "invocable": read_user_invocable(fm, path),
                "summary": summary,
                "trigger": trigger,
                "skip": skip,
                "depends_on_tool": list(fm.get("depends-on-tool") or []),
                "depends_on_skill": list(fm.get("depends-on-skill") or []),
                "dependents": [],  # filled by the reverse pass below
                # --- diagram-only fields. The PAGE ignores them; adding them here rather than
                # in a second reader is the whole point of this module.
                "engine": fm.get("engine") or None,
                "verbs": _invocation_verbs(text, name),
                "scripts": [s for s in _listing(skill_dir, "scripts", ".py")
                            if not s.startswith("test_")],
                "agents": _listing(skill_dir, "agents"),
                "formulas": _listing(skill_dir, "formulas", ".formula.toml"),
                "protocols": _listing(skill_dir, "protocols"),
                "dir": skill_dir,
            }
        )
    by_name = {s["name"]: s for s in skills}
    for s in skills:
        for dep in s["depends_on_skill"]:
            if dep in by_name:
                by_name[dep]["dependents"].append(s["name"])
    for s in skills:
        s["dependents"] = sorted(s["dependents"])
    return skills
