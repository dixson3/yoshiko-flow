---
title: Install
sidebar_position: 2
---

# Install

## Homebrew (recommended)

```bash
brew install dixson3/tap/yf
```

The Homebrew formula declares its dependencies, so Homebrew pulls in
[`beads`](https://github.com/gastownhall/beads) (the `bd` issue tracker) and
[`uv`](https://docs.astral.sh/uv/) (the Python runner several skills use)
transitively (REQ-YF-DIST-002). `yf` itself is distributed for
`{darwin,linux} × {amd64,arm64}` with checksums (REQ-YF-DIST-001).

Verify the binary:

```bash
yf version
```

## Install the skills

`yf` embeds the whole skill tree, so a single command deploys them into your
harness (REQ-YF-EMBED-001, REQ-YF-INSTALL-001):

```bash
# Everything (default) — all skills + their companion rules
yf skills install
```

By default this installs into the **user / claude** surface
(`~/.claude/skills/`), with companion rules in the sibling `~/.claude/rules/`
(REQ-YF-INSTALL-002). Each skill is copied with its `protocols/*.md` companion
rules so the always-loaded trigger contracts are present.

### Scope, surface, and destination

```bash
yf skills install --scope project        # <git-root>/.claude/skills/ (+ rules/)
yf skills install --surface agents       # ~/.agents/skills/ (+ rules/)
yf skills install --target /path/to/skills   # explicit dir; rules in sibling rules/
```

- `--scope {user,project}` (default `user`) — anchor is `$HOME` (user) or the
  git-root/cwd (project).
- `--surface {claude,agents}` (default `claude`) — picks the `.claude` or
  `.agents` surface.
- `--target <PATH>` — wins over scope/surface resolution; rules go to a sibling
  `rules/` dir.

### Selecting what to install

```bash
yf skills install --group utility        # only the beads-free utility skills
yf skills install --group beads          # only the beads-dependent skills
yf skills install yf-plan yf-research    # named skills (pulls their in-repo deps)
```

Groups are computed from each skill's `skill-group` frontmatter
(`beads`, `utility`, `markdown`) — not hardcoded (REQ-YF-INSTALL-003). Naming a
skill pulls in its transitive `depends-on-skill` closure; unresolved external
deps are logged, not fatal (REQ-YF-INSTALL-004).

### Preview and strictness

```bash
yf skills install --dry-run              # show what would change, write nothing
yf skills install --strict               # fail if a depends-on-tool binary is absent
yf skills install --force                # overwrite an existing companion rule
```

By default a missing `depends-on-tool` is a warning and the install still
proceeds (skill files are inert until the tool is present); `--strict` makes it a
hard failure. An existing companion rule is **preserved** unless `--force` is
given, so hand-edits survive a reinstall (REQ-YF-INSTALL-005,
REQ-YF-INSTALL-006).

## Verify the install

```bash
yf doctor
```

`yf doctor` checks the environment (`bd` present and ≥ 1.0.5, `uv`, `git`) and
every installed skill's marker + companion rule, exiting non-zero if any axis
fails (REQ-YF-DOCTOR-001/002). See the [Command Reference](./commands.md#yf-doctor)
for the full axis list.
