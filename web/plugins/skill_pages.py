"""skill_pages — generate one site page per skill from ``skills/*/SKILL.md``.

The single source of truth for the skill catalog is the ``SKILL.md`` frontmatter that ships
with each skill (``name``, ``description``, ``skill-group``, ``user-invocable``). This plugin
reads every ``skills/*/SKILL.md`` under the repo root at build time and emits:

- one page per skill at ``/skills/<name>/`` (themed via the standard ``page`` template), and
- a grouped index at ``/skills/`` listing every skill under its ``skill-group``.

Because the pages are generated from the same frontmatter Claude Code loads, the site's skill
count and descriptions can never drift from the installed skills. There is no separate
``triggers`` field in the frontmatter — the ``TRIGGER when:`` / ``SKIP for:`` guidance lives in
the ``description`` prose, so this plugin splits those clauses out of ``description``.

Optional per-skill intro override: if ``content/skills/<name>.md`` exists, its rendered body is
layered ABOVE the generated frontmatter-derived content on that skill's page (hand-authored
prose without giving up the always-current generated block).

Pages are appended to the PagesGenerator in ``page_generator_finalized`` (which fires after the
generator has read the on-disk pages but before ``generate_output`` writes them), so the
generated pages are written through Pelican's normal page pipeline and theme.
"""

import glob
import os
import re

import yaml
from markdown import Markdown

from pelican import signals
from pelican.contents import Page

# Display order + human labels for the groups. Any group not listed here is appended
# alphabetically after these, so a new skill-group never silently disappears.
GROUP_ORDER = ["beads", "utility", "markdown"]
GROUP_LABELS = {
    "beads": "beads",
    "utility": "utility",
    "markdown": "markdown",
}
GROUP_BLURBS = {
    "beads": "Skills that depend on (or feed) the <code>bd</code> issue tracker (beads).",
    "utility": "Beads-free helper skills — no <code>bd</code> binary required.",
    "markdown": "Standalone GitHub-Flavored-Markdown tooling, beads-free.",
}

_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def _fresh_md():
    return Markdown(extensions=["markdown.extensions.extra", "markdown.extensions.codehilite"])


def _parse_frontmatter(text):
    """Return the YAML frontmatter of a SKILL.md as a dict (empty dict if none/invalid)."""
    match = _FRONTMATTER.match(text)
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _split_description(description):
    """Split a skill ``description`` into (summary, trigger, skip) prose blocks.

    The convention: free prose, then ``TRIGGER when: …`` then optional ``SKIP for: …``.
    Whitespace/newlines from a folded YAML scalar are collapsed to single spaces.
    """
    text = " ".join((description or "").split())
    trigger = skip = ""
    skip_idx = text.find("SKIP for:")
    trig_idx = text.find("TRIGGER when:")

    if skip_idx != -1:
        skip = text[skip_idx + len("SKIP for:") :].strip()
        text = text[:skip_idx].strip()
    if trig_idx != -1 and (skip_idx == -1 or trig_idx < skip_idx):
        # trig_idx is relative to the original text; recompute against the (possibly
        # skip-trimmed) text, which shares the same prefix up to trig_idx.
        trigger = text[trig_idx + len("TRIGGER when:") :].strip()
        summary = text[:trig_idx].strip()
    else:
        summary = text
    return summary, trigger, skip


def _read_skills(repo_root):
    """Read every skills/*/SKILL.md; return a sorted list of skill dicts."""
    skills = []
    pattern = os.path.join(repo_root, "skills", "*", "SKILL.md")
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as fh:
            fm = _parse_frontmatter(fh.read())
        name = fm.get("name") or os.path.basename(os.path.dirname(path))
        summary, trigger, skip = _split_description(fm.get("description", ""))
        skills.append(
            {
                "name": name,
                "group": fm.get("skill-group", "other"),
                "invocable": bool(fm.get("user-invocable", False)),
                "summary": summary,
                "trigger": trigger,
                "skip": skip,
            }
        )
    return skills


def _ordered_groups(skills):
    """Group skills by skill-group in GROUP_ORDER, extras alphabetical."""
    by_group = {}
    for skill in skills:
        by_group.setdefault(skill["group"], []).append(skill)
    ordered = [g for g in GROUP_ORDER if g in by_group]
    ordered += sorted(g for g in by_group if g not in GROUP_ORDER)
    return [(g, sorted(by_group[g], key=lambda s: s["name"])) for g in ordered]


def _skill_override_html(settings, name):
    """Rendered body of content/skills/<name>.md, or '' if absent."""
    path = os.path.join(settings["PATH"], "skills", name + ".md")
    if not os.path.isfile(path):
        return ""
    md = _fresh_md()
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    # Drop a leading YAML frontmatter block if the author included one.
    text = _FRONTMATTER.sub("", text)
    return md.convert(text)


def _skill_page_html(settings, skill):
    github = settings.get("GITHUB_URL", "")
    src = f"{github}/blob/main/skills/{skill['name']}/SKILL.md" if github else ""
    invoke = (
        f"<code>/{skill['name']}</code> (user-invocable)"
        if skill["invocable"]
        else "auto (fires from its description conditions when relevant work appears)"
    )
    parts = []
    override = _skill_override_html(settings, skill["name"])
    if override:
        parts.append(override)
    if skill["summary"]:
        parts.append(f"<p>{skill['summary']}</p>")
    parts.append("<h2>At a glance</h2>")
    parts.append("<ul>")
    parts.append(f"<li><strong>Group:</strong> <code>{skill['group']}</code></li>")
    parts.append(f"<li><strong>Invocation:</strong> {invoke}</li>")
    if src:
        parts.append(f'<li><strong>Source:</strong> <a href="{src}"><code>skills/{skill["name"]}/SKILL.md</code></a></li>')
    parts.append("</ul>")
    if skill["trigger"]:
        parts.append("<h2>When it fires</h2>")
        parts.append(f"<p>{skill['trigger']}</p>")
    if skill["skip"]:
        parts.append("<h2>When to skip it</h2>")
        parts.append(f"<p>{skill['skip']}</p>")
    return "\n".join(parts)


def _index_html(settings, grouped):
    total = sum(len(items) for _, items in grouped)
    parts = [
        f"<p>yoshiko-flow ships <strong>{total} skills</strong>, grouped by their "
        "<code>skill-group</code> frontmatter. Install them all with "
        "<code>yf skills install</code>, or one group with "
        "<code>yf skills install --group &lt;name&gt;</code> (see "
        '<a href="/install/">install</a>). User-invocable skills are triggered with '
        "<code>/yf-&lt;skill&gt;</code>; <code>auto</code> skills fire from their description "
        "conditions when relevant work appears.</p>"
    ]
    for group, items in grouped:
        label = GROUP_LABELS.get(group, group)
        blurb = GROUP_BLURBS.get(group, "")
        parts.append(f"<h2>{label} group</h2>")
        if blurb:
            parts.append(f"<p>{blurb}</p>")
        parts.append("<table>")
        parts.append("<thead><tr><th>Skill</th><th>Invocation</th><th>Purpose</th></tr></thead>")
        parts.append("<tbody>")
        for skill in items:
            invoke = f"<code>/{skill['name']}</code>" if skill["invocable"] else "auto"
            purpose = skill["summary"] or ""
            parts.append(
                f'<tr><td><a href="/skills/{skill["name"]}/"><code>{skill["name"]}</code></a></td>'
                f"<td>{invoke}</td><td>{purpose}</td></tr>"
            )
        parts.append("</tbody></table>")
    return "\n".join(parts)


def _make_page(generator, slug, title, html, subtitle=""):
    metadata = {"title": title, "slug": slug, "template": "page", "status": "published"}
    if subtitle:
        metadata["subtitle"] = subtitle
    source_path = os.path.join(generator.path, slug + ".md")
    return Page(
        content=html,
        metadata=metadata,
        settings=generator.settings,
        source_path=source_path,
        context=generator.context,
    )


def add_skill_pages(generator):
    settings = generator.settings
    repo_root = settings.get("REPO_ROOT") or os.path.abspath(
        os.path.join(settings["PATH"], "..", "..")
    )
    skills = _read_skills(repo_root)
    if not skills:
        return
    grouped = _ordered_groups(skills)

    pages = [
        _make_page(
            generator,
            "skills",
            "skills",
            _index_html(settings, grouped),
            subtitle=f"the {len(skills)} yf-* skills, grouped",
        )
    ]
    for skill in skills:
        pages.append(
            _make_page(
                generator,
                f"skills/{skill['name']}",
                skill["name"],
                _skill_page_html(settings, skill),
                subtitle=skill["summary"][:120] if skill["summary"] else "",
            )
        )

    # generator.context["pages"] is the SAME list object as generator.pages, so extend once.
    generator.pages.extend(pages)

    # Structured nav for the theme's left sidebar: skills grouped by skill-group, each with
    # its site URL. The sidebar renders these under the "Skills" section.
    generator.context["SKILL_NAV"] = [
        {
            "group": group,
            "label": GROUP_LABELS.get(group, group),
            "skills": [
                {"name": s["name"], "url": f"/skills/{s['name']}/"} for s in items
            ],
        }
        for group, items in grouped
    ]


def register():
    signals.page_generator_finalized.connect(add_skill_pages)
