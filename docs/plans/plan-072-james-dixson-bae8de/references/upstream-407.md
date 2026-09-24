---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #407 - Five skill descriptions exceed the Agent Skills
  1024-char cap — pi warns on every startup; cap is unenforced'
---
# Upstream #407: Five skill descriptions exceed the Agent Skills 1024-char cap — pi warns on every startup; cap is unenforced

- **Number:** 407
- **Title:** Five skill descriptions exceed the Agent Skills 1024-char cap — pi warns on every startup; cap is unenforced
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

Five skills ship a `description` frontmatter field longer than the Agent Skills spec's 1024-character cap. Harnesses that enforce the cap emit a startup warning for each one, on every session.

## Symptom

Observed on `pi` (`@earendil-works/pi-coding-agent` v0.87.1) startup. Reproduced by driving pi's own skill loader over the installed skill set:

```
LOADED: 38
--- DIAGNOSTICS ---
warning | description exceeds 1024 characters (1183) | ~/.agents/skills/yf-beads-upstream/SKILL.md
warning | description exceeds 1024 characters (1136) | ~/.agents/skills/yf-change-validation/SKILL.md
warning | description exceeds 1024 characters (1325) | ~/.agents/skills/yf-drift-check/SKILL.md
warning | description exceeds 1024 characters (1209) | ~/.agents/skills/yf-okf/SKILL.md
warning | description exceeds 1024 characters (1319) | ~/.agents/skills/yf-skill-authoring/SKILL.md
```

`pi` enforces the limit in `dist/core/skills.js`:

```js
/** Max description length per spec */
const MAX_DESCRIPTION_LENGTH = 1024;
```

Claude Code does not enforce it, which is why these were authored long and the drift went unnoticed.

## Not a duplicate-skill problem

Worth stating explicitly, because a multi-surface install invites that hypothesis. Two mechanisms already prevent collisions, and **zero** `collision` diagnostics are emitted:

- `~/.claude/skills` is not a path `pi` scans at all (it reads `~/.pi/agent/skills`, `~/.agents/skills`, ancestor `<dir>/.agents/skills`, and `.pi/skills`).
- Symlinked duplicates are canonicalized and skipped silently — `loadSkills` keeps a `realPathSet` keyed on the resolved real path.

The warnings are purely field-length.

## Scope

Five skills. Counts are the parsed YAML scalar length (what a harness measures after folding), taken from `main`:

| skill | chars | over by |
|:--|--:|--:|
| `yf-drift-check` | 1325 | 301 |
| `yf-skill-authoring` | 1319 | 295 |
| `yf-okf` | 1209 | 185 |
| `yf-beads-upstream` | 1183 | 159 |
| `yf-change-validation` | 1136 | 112 |

The other 15 skills in `skills/` are within the cap (`yf-plan` 331, `yf-research` 718, etc.), so this is a five-file fix, not a corpus-wide rewrite.

## Why it's worth fixing beyond silencing a warning

The `description` is loaded into the system prompt for **every** session, for every skill, whether or not the skill is used. These five contribute ~6.1 KB combined. The spec's cap is a ceiling; agentskills.io's own guidance recommends staying under ~600 characters for discovery quality, so there is real headroom here — the TRIGGER/SKIP prose in the offenders carries substantial slack (repeated axis restatements, parenthetical asides, and in several cases a full sentence of rationale that belongs in `SKILL.md`'s body rather than the routing description).

Constraint on the edit: these descriptions are load-bearing. They are the routing surface that decides whether a skill fires, and several encode deliberate negative routing ("SKIP for: ... use X instead") that resolves genuine ambiguity between sibling skills. Trimming must preserve the TRIGGER/SKIP discrimination, not just hit a character budget.

## Proposed remedy

1. Trim the five `description` fields to ≤1024, targeting ≤600 where it does not cost routing fidelity.
2. Add a mechanical guard so this cannot silently recur. `scripts/check_frontmatter.py` is the natural home — it already globs `skills/*/SKILL.md` and `skills/*/agents/*.md`, already parses the YAML block, and is already wired into `CHANGE-VALIDATION.md` §3 under the `frontmatter` id for exactly those paths. It currently validates *structure only* (delimiters, YAML parses, maps to a dict) and checks no field lengths. Adding a `len(description) > 1024` failure (and, for spec completeness, `len(name) > 64` plus the lowercase/hyphen name charset) is a small, well-scoped extension to an existing gated check — no new checker, no new `CHANGE-VALIDATION.md` recipe row, no new trigger glob.

Both spec constraints are worth encoding together since the script is being touched anyway: per the Agent Skills specification, `name` is max 64 characters and `description` is max 1024.

## Verification

After the fix, this should print nothing:

```bash
python3 - <<'EOF'
import glob, re, yaml
for p in sorted(glob.glob('skills/*/SKILL.md')):
    fm = yaml.safe_load(re.match(r'^---\n(.*?)\n---\n', open(p).read(), re.S).group(1))
    d = fm.get('description', '')
    if len(d) > 1024:
        print(f'{p}: {len(d)} (over by {len(d)-1024})')
EOF
```

And `pi` startup should emit no skill diagnostics.

