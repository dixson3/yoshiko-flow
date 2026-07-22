"""home_content — surface the homepage hero + feature cards as markdown artifacts.

The homepage (`index` direct template) is kept structural: its *content* lives in
markdown under `content/home/hero.md` and `content/cards/*.md`, and this plugin
injects the rendered pieces into the template context as ``HOME_HERO`` and
``HOME_CARDS``. The theme then only lays out structure.

Feature cards — one file per card, ``content/cards/NN-slug.md``::

    Title: plan
    Href: /usage/#yf-plan
    Glyph: #
    Order: 1
    Command: /yf-plan build the auth service

    Structured, beads-tracked planning with upstream issue reconciliation.

Hero — one file, ``content/home/hero.md``::

    Name: yoshiko-flow
    Glyph: >_
    Install: curl --proto '=https' --tlsv1.2 -LsSf {install_url} | sh
    Cta: install guide | /install/ | primary
    Cta: usage | /usage/
    Cta: github | {github_url} | external

    yoshiko-flow is a family of portable, cross-harness agent skills plus the yf CLI.

The ``{install_url}`` / ``{github_url}`` / ``{site_url}`` tokens are substituted
per-build from the resolved settings (dev vs prod URLs), so the markdown stays
config-driven. The markdown body is the hero description; a single enclosing
``<p>`` is unwrapped so the theme can place it in ``<p class="hero-desc">`` and a
plain-text form is exposed for the ``<meta>``/OG description.
"""

import glob
import html
import os
import re

from markdown import Markdown

from pelican import signals

_SINGLE_P = re.compile(r"\s*<p>(.*)</p>\s*\Z", re.S)
_TAGS = re.compile(r"<[^>]+>")


def _fresh_md():
    # A fresh Markdown instance per file — the meta extension stashes state on the
    # instance and is not safe to reuse across documents.
    return Markdown(extensions=["markdown.extensions.meta", "markdown.extensions.extra"])


def _first(meta, key, default=""):
    values = meta.get(key)
    return values[0] if values else default


def _tokens(settings):
    return {
        "install_url": settings.get("INSTALL_URL", ""),
        "github_url": settings.get("GITHUB_URL", ""),
        "site_url": settings.get("SITEURL", ""),
    }


def _sub(text, tokens):
    for name, value in tokens.items():
        text = text.replace("{" + name + "}", value)
    return text


def _read_cards(settings):
    cards_dir = os.path.join(settings["PATH"], "cards")
    if not os.path.isdir(cards_dir):
        return []

    cards = []
    for path in sorted(glob.glob(os.path.join(cards_dir, "*.md"))):
        md = _fresh_md()
        with open(path, encoding="utf-8") as fh:
            body_html = md.convert(fh.read())
        meta = getattr(md, "Meta", {})

        try:
            order = int(_first(meta, "order", "99"))
        except ValueError:
            order = 99

        cards.append(
            {
                "title": _first(meta, "title"),
                "href": _first(meta, "href", "#"),
                "glyph": _first(meta, "glyph", "#"),
                "command": _first(meta, "command"),
                "order": order,
                "filename": os.path.basename(path),
                "body": body_html,
            }
        )

    cards.sort(key=lambda card: (card["order"], card["filename"]))
    return cards


def _read_hero(settings):
    path = os.path.join(settings["PATH"], "home", "hero.md")
    if not os.path.isfile(path):
        return None

    md = _fresh_md()
    with open(path, encoding="utf-8") as fh:
        body_html = md.convert(fh.read())
    meta = getattr(md, "Meta", {})
    tokens = _tokens(settings)

    ctas = []
    for line in meta.get("cta", []):
        parts = [part.strip() for part in line.split("|")]
        flags = parts[2].split() if len(parts) > 2 else []
        ctas.append(
            {
                "label": parts[0] if parts else "",
                "href": _sub(parts[1], tokens) if len(parts) > 1 else "#",
                "primary": "primary" in flags,
                "external": "external" in flags,
            }
        )

    match = _SINGLE_P.match(body_html)
    description_html = match.group(1) if match else body_html
    description_text = html.unescape(_TAGS.sub("", description_html))
    description_text = " ".join(description_text.split())

    return {
        "name": _first(meta, "name"),
        "glyph": _first(meta, "glyph", ">_"),
        "install_cmd": _sub(_first(meta, "install"), tokens),
        "description_html": description_html,
        "description_text": description_text,
        "ctas": ctas,
    }


def inject_content(generators):
    # All generators share one context dict; direct templates (index) render it
    # during generate_output(), which runs after this signal fires.
    if not generators:
        return
    context = generators[0].context
    settings = generators[0].settings
    context["HOME_CARDS"] = _read_cards(settings)
    context["HOME_HERO"] = _read_hero(settings)


def register():
    signals.all_generators_finalized.connect(inject_content)
