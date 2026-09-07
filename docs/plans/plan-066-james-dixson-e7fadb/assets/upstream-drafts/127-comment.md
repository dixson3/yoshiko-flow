---
type: Asset
okf_spec: OKF-PLAN
description: "Posted reconcile comment for upstream #127 (idiomatic-terms glossary) — POSTED and issue CLOSED 2026-09-07."
---
<!-- THE POSTED BODY IS EVERYTHING BELOW THIS COMMENT. The frontmatter above is
     bundle metadata (OKF REQ-OKF-003) and was NOT part of the upstream write:
     posted; #127 closed. -->

## Largely already satisfied — closing with the delta, not a duplicate

Measured during plan-066: **`web/content/pages/glossary.md` already defined every term this issue
names** — *pouring beads*, *landing the plane*, *red-team*, plus molecules, wisps and gates. It is
exactly the "glossary a cold reader can use to decode the docs" the issue asks for, and it has
been live at `/glossary/` this whole time.

Authoring a second `concepts/` page would have created a **duplicate competing with it**, so the
plan extended the existing glossary instead with the six terms genuinely missing:

- **escalation** — `## ESC-NNN` in a plan bundle, write-then-notify rather than ask-and-await
- **autonomy level** — autonomous vs checkpointed, and the fact that autonomy never widens
  *authority*
- **negative control** — checking that an instrument can *fail*, and why the code-side form is
  the strong one
- **vacuity floor** — the assertion that turns "I inspected nothing" into a loud failure
- **aspect** — a formula that weaves into another's steps at cook time rather than being poured
- **closable** — propose-only, and why a clean run does not mean nothing needs closing

27 → 33 terms.

**One incidental finding worth recording.** The plan had budgeted for a new page under
`web/content/concepts/`, and that would have rendered **nothing**: `pelicanconf.py` sets no
`PAGE_PATHS`, so Pelican's default `["pages"]` silently excludes any other content directory —
measured as exit 0, an unchanged page count, zero warnings, and no output. The glossary already
lives under `pages/`, so the trap is avoided structurally rather than by remembering it.
