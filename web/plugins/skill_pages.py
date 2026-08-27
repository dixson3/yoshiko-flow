"""skill_pages — one site page per skill, HYBRID composition.

The skill catalog's mechanical facts come from the ``SKILL.md`` frontmatter that ships with
each skill (``name``, ``description``, ``skill-group``, ``user-invocable``, ``depends-on-*``).
This plugin reads every ``skills/*/SKILL.md`` under the repo root at build time and emits:

- one page per skill at ``/skills/<name>/`` (themed via the standard ``page`` template), and
- a grouped index at ``/skills/`` listing every skill under its ``skill-group``,

and builds the theme's left-sidebar ``SKILL_NAV``.

**Hybrid page composition.** Each skill page is, top to bottom:

1. the skill title + one-line summary (frontmatter), then
2. an auto-generated **"At a glance"** block (frontmatter: group, invocation, required tools,
   ``depends-on-skill``, reverse dependents, source links) — mechanical facts that literally
   cannot drift, then
3. the **authored prose** body from ``content/skills/<name>.md`` — the hand-editable page
   content, with its own headings (typically *when it fires*, *how it works*, *usage*,
   behavior notes).

The ``/skills/`` index, the per-skill "At a glance" block, and ``SKILL_NAV`` stay derived
from frontmatter, so the skill count, groups, invocation, and dependency columns can never
drift. Only the authored prose is hand-written; a repo-root ``DRIFT-CHECK.md`` edge
(``e-skill-page-*``) keeps that prose honest against each skill's ``SKILL.md`` / ``README.md``
/ ``SPEC.md``.

**Fail-closed on a missing page.** Every skill MUST have an authored
``content/skills/<name>.md``. A skill without one is a hard build error naming the missing
skill(s) — a newly added skill cannot ship an ungoverned page. ``add_skill_pages`` raises
before generating any page and reports the offending names in
``generator.context["missing_authored_page"]``.

**Orphan pages.** A stray ``content/skills/<name>.md`` with no matching ``skills/<name>/`` dir
is simply never read — the plugin iterates skills, not content files — so it generates no page
and lints/builds harmlessly.

An authored page MAY carry a leading YAML frontmatter block; it is stripped before render, and
the page title/subtitle stay plugin-set from frontmatter (unlike ordinary content pages).

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

# Install groups (the `skill-group` frontmatter). Display order + human labels; any group not
# listed here is appended alphabetically, so a new skill-group never silently disappears.
GROUP_ORDER = ["workflows", "beads", "utility", "markdown"]
GROUP_LABELS = {
    "workflows": "workflows",
    "beads": "beads",
    "utility": "utility",
    "markdown": "markdown",
}
GROUP_BLURBS = {
    "workflows": "End-to-end, beads-tracked user workflows — the skills you invoke to get work done. Installing this group pulls in the beads skills it depends on.",
    "beads": "The <code>bd</code> (beads) support layer the workflows build on: init/health, direct-CLI gotchas, authoring conventions, graph hygiene, and upstream tracking.",
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

    Only ``summary`` reaches the rendered page (the title one-liner). ``trigger`` / ``skip``
    are no longer surfaced as generated blocks — the authored prose folds trigger/skip
    guidance into its own narrative — but are kept on the skill dict for the index/nav layer
    and any future consumer.
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
                "depends_on_tool": list(fm.get("depends-on-tool") or []),
                "depends_on_skill": list(fm.get("depends-on-skill") or []),
                "dependents": [],  # filled in by add_skill_pages (reverse of depends_on_skill)
            }
        )
    return skills


def _ordered_groups(skills):
    """Group skills by site category (GROUP_ORDER), extras alphabetical."""
    by_group = {}
    for skill in skills:
        by_group.setdefault(skill.get("group", "other"), []).append(skill)
    ordered = [g for g in GROUP_ORDER if g in by_group]
    ordered += sorted(g for g in by_group if g not in GROUP_ORDER)
    return [(g, sorted(by_group[g], key=lambda s: s["name"])) for g in ordered]


def _authored_page_path(settings, name):
    """Filesystem path of the authored content/skills/<name>.md (may not exist)."""
    return os.path.join(settings["PATH"], "skills", name + ".md")


def _authored_page_html(settings, name):
    """Rendered prose body of the authored content/skills/<name>.md, or '' if absent/empty.

    A leading YAML frontmatter block (if the author included one) is stripped before render —
    the page title/subtitle stay plugin-set from the skill frontmatter, not the authored file.
    """
    path = _authored_page_path(settings, name)
    if not os.path.isfile(path):
        return ""
    md = _fresh_md()
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    # Drop a leading YAML frontmatter block if the author included one.
    text = _FRONTMATTER.sub("", text)
    return md.convert(text)


def _skill_link(name, known):
    """A link to another skill's page when it is an in-repo skill, else plain code."""
    if name in known:
        return f'<a href="/skills/{name}/"><code>{name}</code></a>'
    return f"<code>{name}</code>"


def _skill_page_html(settings, skill, known):
    """Compose a skill page: summary + generated "At a glance" + authored prose body.

    The prose body is the authored ``content/skills/<name>.md`` (guaranteed present by the
    fail-closed guard in ``add_skill_pages``). The "At a glance" block is always generated from
    frontmatter, so the mechanical catalog facts never drift.
    """
    github = settings.get("GITHUB_URL", "")
    name = skill["name"]
    skmd = f"{github}/blob/main/skills/{name}/SKILL.md" if github else ""
    rdme = f"{github}/blob/main/skills/{name}/README.md" if github else ""
    invoke = (
        f"<code>/{name}</code> (user-invocable)"
        if skill["invocable"]
        else "auto (fires from its description conditions when relevant work appears)"
    )
    parts = []
    if skill["summary"]:
        parts.append(f"<p>{skill['summary']}</p>")
    parts.append("<h2>At a glance</h2>")
    parts.append("<ul>")
    parts.append(f"<li><strong>Group:</strong> <code>{skill.get('group', 'other')}</code></li>")
    parts.append(f"<li><strong>Invocation:</strong> {invoke}</li>")
    if skill["depends_on_tool"]:
        tools = ", ".join(f"<code>{t}</code>" for t in skill["depends_on_tool"])
        parts.append(f"<li><strong>Requires tools:</strong> {tools}</li>")
    else:
        parts.append("<li><strong>Requires tools:</strong> none (self-contained)</li>")
    if skill["depends_on_skill"]:
        deps = ", ".join(_skill_link(d, known) for d in skill["depends_on_skill"])
        parts.append(f"<li><strong>Depends on skills:</strong> {deps}</li>")
    if skill["dependents"]:
        rev = ", ".join(_skill_link(d, known) for d in skill["dependents"])
        parts.append(f"<li><strong>Depended on by:</strong> {rev}</li>")
    if skmd:
        parts.append(
            f'<li><strong>Source:</strong> <a href="{skmd}"><code>SKILL.md</code></a>'
            f' &middot; <a href="{rdme}"><code>README.md</code></a></li>'
        )
    parts.append("</ul>")
    # Prose body: the authored content/skills/<name>.md (the fail-closed guard guarantees it
    # exists; an intentionally empty file simply renders no body below the quick reference).
    authored = _authored_page_html(settings, name)
    if authored:
        parts.append("<hr>")
        parts.append(authored)
    return "\n".join(parts)


def _index_html(settings, grouped, known):
    total = sum(len(items) for _, items in grouped)
    parts = [
        f"<p>yoshiko-flow ships <strong>{total} skills</strong>, grouped by their "
        "<code>skill-group</code> — the <strong>workflows</strong> you invoke to get work done, "
        "the <strong>beads</strong> support layer they build on, and the beads-free "
        "<strong>utility</strong> and <strong>markdown</strong> helpers. User-invocable skills "
        "are triggered with <code>/yf-&lt;skill&gt;</code>; <code>auto</code> skills fire from "
        "their description conditions when relevant work appears. Install them all with "
        "<code>yf harness skills install</code>, or one group with "
        "<code>yf harness skills install --group &lt;workflows|beads|utility|markdown&gt;</code> (see "
        '<a href="/install/">install</a>). The <strong>Depends on</strong> column shows each '
        "skill's <code>depends-on-skill</code> — installing a skill or a group pulls its "
        "transitive dependency closure automatically, so <code>--group workflows</code> also "
        "installs the beads skills the workflows need.</p>"
    ]
    for group, items in grouped:
        label = GROUP_LABELS.get(group, group)
        blurb = GROUP_BLURBS.get(group, "")
        parts.append(f"<h2>{label}</h2>")
        if blurb:
            parts.append(f"<p>{blurb}</p>")
        parts.append("<table>")
        parts.append("<thead><tr><th>Skill</th><th>Invocation</th><th>Purpose</th><th>Depends on</th></tr></thead>")
        parts.append("<tbody>")
        for skill in items:
            invoke = f"<code>/{skill['name']}</code>" if skill["invocable"] else "auto"
            purpose = skill["summary"] or ""
            deps = ", ".join(_skill_link(d, known) for d in skill["depends_on_skill"]) or "&mdash;"
            parts.append(
                f'<tr><td><a href="/skills/{skill["name"]}/"><code>{skill["name"]}</code></a></td>'
                f"<td>{invoke}</td><td>{purpose}</td><td>{deps}</td></tr>"
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

    # Fail-closed: every skill MUST have an authored content/skills/<name>.md. A skill without
    # one would otherwise ship an ungoverned, drift-check-less page, so the build stops here and
    # names the offenders. The signal is also recorded on the context for tests / diagnostics.
    missing = sorted(
        s["name"] for s in skills if not os.path.isfile(_authored_page_path(settings, s["name"]))
    )
    generator.context["missing_authored_page"] = missing
    if missing:
        raise RuntimeError(
            "skill_pages: no authored web/content/skills/<name>.md for: "
            + ", ".join(missing)
            + ". Every skill needs an authored page (add one under web/content/skills/)."
        )

    # Reverse the depends-on-skill graph so each skill page can show what depends on IT.
    known = {s["name"] for s in skills}
    for s in skills:
        for dep in s["depends_on_skill"]:
            for other in skills:
                if other["name"] == dep:
                    other["dependents"].append(s["name"])
    for s in skills:
        s["dependents"] = sorted(set(s["dependents"]))

    grouped = _ordered_groups(skills)

    pages = [
        _make_page(
            generator,
            "skills",
            "skills",
            _index_html(settings, grouped, known),
            subtitle=f"the {len(skills)} yf-* skills, grouped by what they do",
        )
    ]
    for skill in skills:
        pages.append(
            _make_page(
                generator,
                f"skills/{skill['name']}",
                skill["name"],
                _skill_page_html(settings, skill, known),
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
