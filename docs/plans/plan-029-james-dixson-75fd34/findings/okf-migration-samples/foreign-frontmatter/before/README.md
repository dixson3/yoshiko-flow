---
title: Agent-Optimized Websites
created: 2026-05-13
tags: [incubator, agents, web, seo, geo, aeo, llms-txt, pelican]
status: incubating
last_reviewed: 2026-05-17
priority: normal
aliases: [agent-optimized-websites]
---

## Resume

- **Last reviewed**: 2026-05-17
- **State**: Research consolidated across three sibling notes (now sibling incubators). Pelican path identified; no code yet.
- **Next action**: Build the Pelican `llms.txt` plugin sketched in `[[pelican-dual-format-publishing]]`.
- **Open threads**:
  - Server-side content negotiation vs Cloudflare Markdown-for-Agents for deployment.
  - JSON-LD rollout plan on existing sites.
  - Tracking whether GPTBot/ClaudeBot are unblocked across managed sites.
- **Context to reload**: this README; sibling incubators `agent-seo-research`, `dual-publish-markdown-html-research`, `pelican-dual-format-publishing`.

## Status

Research complete. Three sibling incubators capture the underlying research; this one is the synthesis / decision hub. Implementation is the open work.

## Premise

Research and planning for making web content accessible to AI agents alongside human visitors.

### Key Concepts

#### Dual-Format Publishing
Serving the same content as both rendered HTML and raw markdown at distinct URLs (e.g., `/page.html` and `/page.md`), or via HTTP content negotiation (`Accept: text/markdown`).

#### Two Approaches

**A. Static dual-output (separate URLs)**
- Serve both `.html` and `.md` files at matching paths
- Simple, works with any static host
- Agents/users must know to append `.md`

**B. Content negotiation (same URL, different response)**
- Client sends `Accept: text/markdown`, server returns markdown
- Defined by RFC 7763 (`text/markdown` media type)
- Site-agnostic — agent needs no URL knowledge, just the right header
- Requires server/CDN/middleware support

#### Agent Adoption (Feb 2026)

| Agent | Sends `Accept: text/markdown`? |
|-------|------|
| Claude Code | Yes |
| Cursor | Yes |
| OpenCode | Yes |
| OpenAI Codex | No |
| Gemini CLI | No |
| GitHub Copilot | No |

### Emerging Standards

#### llms.txt (v1.1.1)
- Markdown file at site root declaring business identity for AI
- Proposed by Jeremy Howard (Answer.AI/fast.ai), Sept 2024
- Spec: [www.ai-visibility.org.uk/specifications/llms-txt/](https://www.ai-visibility.org.uk/specifications/llms-txt/)
- Three tiers: `/llms.txt` (index), `/llms-full.txt` (all content), per-page `.md` files
- 600+ adopters (Anthropic, Stripe, Cloudflare, Perplexity, etc.)
- Google included it in their A2A protocol
- Low adoption overall; Google does not use it for search

#### ai.txt (v1.1.1)
- INI-style behavioral permissions (what AI can/can't do with your content)
- Spec: [www.ai-visibility.org.uk/specifications/ai-txt/](https://www.ai-visibility.org.uk/specifications/ai-txt/)
- Covers permissions, restrictions, attribution preferences
- Even lower adoption than llms.txt

#### agents-brief.txt
- Declares what actions agents may perform (book, purchase, submit forms)
- Repo: [github.com/jaspervanveen/agents-txt](https://github.com/jaspervanveen/agents-txt)
- Very early (March 2026), minimal adoption

#### Permission Manifests (Academic)
- Paper: arXiv 2601.02371 (LAS-WG)
- Granular per-agent permission model, built on OAuth 2.0 patterns

#### IETF Drafts
- AI Content Disclosure Header (`draft-abaris-aicdh-00`, April 2025)
- AI Agent Protocols Framework (`draft-rosenberg-ai-protocols-00`, May 2025)
- Nothing near RFC status

**Enforcement problem:** All voluntary standards only work if AI companies choose to respect them.

### GEO / AEO Techniques (What Actually Works Now)

#### Structured Data (Highest ROI)
- 65% of pages cited by Google AI Mode include JSON-LD structured data
- 71% of pages cited by ChatGPT include structured data
- FAQPage schema: 78% more likely to be cited
- Priority types: `Article`, `FAQPage`, `Organization`, `Person`, `Product`, `HowTo`
- Use JSON-LD exclusively; nested schemas outperform flat markup

#### Content Structure
- Direct answers in the first 60-120 words
- Self-contained FAQ answers (40-60 words)
- Tables, numbered lists, checklists positioned prominently
- Comparison content generates 32.5% of all AI citations ("versus" pages)
- Clear H2/H3 heading hierarchy

#### Freshness
- Citation decay within ~3 months without updates
- Monthly refresh with visible "last updated" dates required

#### Authority
- Third-party mentions outweigh on-site optimization
- Earned media, external citations, consistent entity presence across the web
- Comprehensive About pages and author bios

#### Technical
- Don't block AI crawlers in robots.txt (GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot)
- JSON-LD on all key pages
- `<link rel="alternate" type="text/markdown">` in HTML head for discovery
- `X-Robots-Tag: noindex` on `.md` responses to avoid duplicate content issues

#### AI Crawlers

| Crawler | Operator |
|---------|----------|
| GPTBot | OpenAI |
| OAI-SearchBot | OpenAI (ChatGPT search) |
| ClaudeBot | Anthropic |
| PerplexityBot | Perplexity |
| Google-Extended | Google (AI training) |

### Pelican Implementation

#### Dual-Format Publishing (Built-in)

Two lines in `pelicanconf.py`:

```python
OUTPUT_SOURCES = True
OUTPUT_SOURCES_EXTENSION = ".md"
```

Every article at `output/blog/my-post.html` gets a companion `output/blog/my-post.md`. Handled natively by `SourceFileGenerator`.

#### View Source Links (Optional Plugin)

```bash
uv pip install pelican-show-source
```

Adds `show_source_url` attribute to articles/pages for template use.

#### llms.txt Generation

No Pelican plugin exists yet. Needs a custom plugin using `signals.finalized` to generate `llms.txt` and `llms-full.txt` at the site root. See `[[pelican-dual-format-publishing]]` for a working plugin skeleton.

#### Content Negotiation (Server-Side)

Pair `OUTPUT_SOURCES` with server config:

**nginx:**
```nginx
map $http_accept $markdown_suffix {
    ~text/markdown ".md";
    default        "";
}
location / {
    try_files $uri$markdown_suffix $uri $uri/ =404;
}
```

**Static Web Server:** `static-web-server --accept-markdown`

**Cloudflare Pro+:** Enable "Markdown for Agents" toggle (CDN-edge HTML-to-markdown, 80-99% token reduction, zero code changes).

### CDN-Level Solutions

#### Cloudflare Markdown for Agents (Feb 2026)
- Pro, Business, Enterprise plans
- Edge conversion: HTML → markdown on-the-fly when `Accept: text/markdown` is sent
- 80-99% token reduction
- Response headers: `x-markdown-tokens`, `content-signal` framework
- 2 MB max origin response
- Docs: [developers.cloudflare.com/fundamentals/reference/markdown-for-agents/](https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/)

#### Vercel
- Next.js rewrites detect `Accept: text/markdown` and route to markdown endpoint
- Documented on their blog

### CMS Comparison for Dual-Format

| Platform | Dual-Format Support | Notes |
|----------|-------------------|-------|
| **Pelican** | Native (`OUTPUT_SOURCES`) | Best path for this project |
| **Hugo** | Native (Custom Output Formats) | Best SSG support overall |
| **Eleventy** | Passthrough copy or pagination template | Flexible but manual |
| **Docusaurus** | Plugin (`docusaurus-markdown-source-plugin`) | Zero-config with plugin |
| **Quartz** | None (post-build script or Cloudflare) | No native support |
| **Astro** | None (custom integration needed) | No native support |
| **Webflow** | None (Cloudflare workaround only) | HTML-native CMS |
| **Ghost** | API returns markdown, no dual-URL | Would need custom frontend |

### Terminology

| Term | Full Name | Target |
|------|-----------|--------|
| **SEO** | Search Engine Optimization | Google/Bing SERPs |
| **AEO** | Answer Engine Optimization | Featured snippets, voice assistants, AI Overviews |
| **GEO** | Generative Engine Optimization | ChatGPT, Claude, Perplexity, Gemini citations |

GEO coined in 2023 Princeton/Georgia Tech/IIT Delhi paper (KDD 2024).

## Open questions

1. Cloudflare Markdown-for-Agents vs server-side content negotiation for our deployment(s)?
2. Which existing sites should get `OUTPUT_SOURCES = True` first?
3. Should the `llms.txt` plugin live in our own repo or be upstreamed to pelican-plugins?

## Decision log

## Files

- `README.md` — this state file
- `[[agent-seo-research]]` — full GEO/AEO techniques, standards, sources
- `[[dual-publish-markdown-html-research]]` — detailed dual-format implementation research
- `[[pelican-dual-format-publishing]]` — Pelican-specific recipes, plugin code, post-build scripts

## Beads to file

- Build Pelican `llms.txt` plugin
- Add `OUTPUT_SOURCES = True` to existing Pelican sites
- Evaluate Cloudflare vs server-side content negotiation for deployment
- Implement JSON-LD structured data on key pages
