import os
from datetime import datetime

AUTHOR = "James Dixson"
CURRENT_YEAR = datetime.now().year
SITENAME = "yoshiko-flow"
SITESUBTITLE = "portable, beads-backed agent skills + the yf CLI"
# Latest released version, shown in the site header so visitors see it immediately.
# MUST be bumped in lockstep with every release tag (see AGENTS.md "Upstream Tracking"
# / the yf workspace version in yf/Cargo.toml).
YOSHIKOFLOW_RELEASE = "v0.5.0"
# Full-sentence description for meta/OG (crawlers want >=100 chars).
SITE_DESCRIPTION = (
    "yoshiko-flow is a family of portable, cross-harness AI-agent skills plus a single "
    "compiled CLI, yf, that installs, upgrades, verifies, and preflights those skills and the "
    "toolchain they depend on. Beads-backed planning and research, drift checking, markdown "
    "tooling, and more — installed into Claude Code or any agent harness."
)
# Canonical public site URL, from the environment (local .envrc / CI). Kept as a separate
# setting because SITEURL must stay EMPTY in dev — a non-empty SITEURL makes Pelican anchor
# every generated link on it (absolute prod URLs under the dev server). publishconf.py sets
# SITEURL = PUBLISH_URL for the production build; here it only feeds absolute-URL needs.
PUBLISH_URL = os.environ.get("PUBLISH_URL", "")
SITEURL = ""

# The GitHub project — canonical for binaries + self-update.
GITHUB_URL = "https://github.com/dixson3/yoshiko-flow"
GITHUB_RELEASES_URL = "https://github.com/dixson3/yoshiko-flow/releases"
# The short, memorable bootstrap install command surfaced on the site. Uses PUBLISH_URL (not
# SITEURL) so the hero renders the real absolute install URL even under the dev server.
INSTALL_URL = (PUBLISH_URL or SITEURL) + "/install.sh"

# Repo root, so the skill_pages plugin can read skills/*/SKILL.md relative to it. web/ is one
# level below the repo root; resolved absolutely so it works under the dev server and CI alike.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

PATH = "content"
OUTPUT_PATH = "output"

TIMEZONE = "America/Los_Angeles"
DEFAULT_LANG = "en"

# Feed generation is not desired for a docs site.
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Sitemap + two local plugins. `home_content` reads content/home/hero.md + content/cards/*.md
# and exposes them to the index template as HOME_HERO / HOME_CARDS. `skill_pages` reads each
# skills/*/SKILL.md and emits one page per skill plus a grouped /skills/ index, so counts and
# descriptions are generated from source and never drift.
PLUGIN_PATHS = ["plugins"]
PLUGINS = ["pelican.plugins.sitemap", "home_content", "skill_pages"]
SITEMAP = {
    "format": "xml",
    "priorities": {"articles": 0.5, "indexes": 0.5, "pages": 0.8},
    "changefreqs": {"articles": "monthly", "indexes": "monthly", "pages": "monthly"},
}

# Pretty, directory-style, extension-less URLs (pins the CloudFront index-rewrite
# Function in Issue 5.2: /install/ -> install/index.html). A private-bucket + OAC
# origin does NOT append index.html to subdirectory requests, so this URL style is a
# first-class hosting requirement, not a cosmetic choice.
PAGE_URL = "{slug}/"
PAGE_SAVE_AS = "{slug}/index.html"
# No articles/blog on this site, but pin the article scheme for consistency.
ARTICLE_URL = "posts/{slug}/"
ARTICLE_SAVE_AS = "posts/{slug}/index.html"

# Pages ARE the site — surface them, drive nav explicitly via MENUITEMS below.
# No articles/blog: keep ARTICLE_PATHS empty so content/cards/*.md (read by the
# home_content plugin, not the article generator) is not scanned as an article.
DIRECT_TEMPLATES = ["index"]
ARTICLE_PATHS = ["_no_articles"]
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = False

# Bespoke dark terminal/technical theme.
THEME = "themes/yoshikoflow"

# Header nav (title, url). Pretty directory-style URLs.
MENUITEMS = (
    ("home", "/"),
    ("install", "/install/"),
    ("usage", "/usage/"),
    ("architecture", "/architecture/"),
    ("lifecycle", "/lifecycle/"),
    ("skills", "/skills/"),
    ("github", GITHUB_URL),
)

MARKDOWN = {
    "extension_configs": {
        "markdown.extensions.codehilite": {"css_class": "highlight"},
        "markdown.extensions.extra": {},
        "markdown.extensions.meta": {},
        "markdown.extensions.toc": {"permalink": False, "toc_depth": "2-3"},
    },
    "output_format": "html5",
}

# Static assets. `extra/` files are copied to the site root (robots, install.sh)
# via EXTRA_PATH_METADATA below.
STATIC_PATHS = ["images", "extra"]
EXTRA_PATH_METADATA = {
    "extra/robots.txt": {"path": "robots.txt"},
    # install.sh is staged into extra/ by web/scripts/sync_installer.sh; it lands at the
    # site root in the normal build/output (and tree-wide `s3 sync`). The Makefile
    # `sync_installer` target re-uploads this one key with an explicit short Cache-Control
    # and invalidates it — the tree-wide sync does NOT set per-key cache headers.
    "extra/install.sh": {"path": "install.sh"},
}

# Uncomment for document-relative URLs when developing.
# RELATIVE_URLS = True
