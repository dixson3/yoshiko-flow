---
type: Asset
okf_spec: OKF-PLAN
id: red-baseline-1.1
plan: plan-055-james-dixson-5f1c40
author: james-dixson
created: '2026-08-27'
title: RED baseline (Issue 1.1)
---
# RED baseline — Issue 1.1

**Recorded:** 2026-08-27 · **Plan:** plan-055-james-dixson-5f1c40 · **Machine:** the migration target

Recorded **before any remover code existed** (Epic 1 issues 1.2–1.5 are open at the time of
writing). It **demonstrates** the enumeration gap rather than asserting it: every number below is
a command's output, not a claim.

## 1. The four-outcome fixture

A synthetic skills root with one member per outcome `REQ-YF-MARK-006` declares:

| Member | Intended outcome | How it was built |
| :-- | :-- | :-- |
| `yf-markdown-lint` | `owned-and-unmodified` | verbatim copy of a deployed yf tree (marker intact) |
| `yf-okf` | `owned-but-modified` | deployed copy with one line appended to `SKILL.md` |
| `operator-notes` | `no-marker` (foreign) | hand-built `SKILL.md` + `OPERATOR-DATA.txt`, **no** yf marker |
| `linked-skill` | `undetermined` | a **symlink** to a skill directory elsewhere |

Marker presence, measured (`grep -c 'yf-skills:' <member>/SKILL.md`):

```
yf-markdown-lint     1
yf-okf               1
operator-notes       0
linked-skill         (symlink — not a directory yf owns)
```

## 2. THE GAP — what the existing name-keyed walk sees

`yf harness skills status --target <fixture>` over that four-member root:

```
installed-visible: ["yf-markdown-lint","yf-okf"]
yf-markdown-lint  unmodified=true
yf-okf            unmodified=false
```

**Two of four members are invisible.** `status` is keyed on the *embedded skill set*, so it can
only ever answer questions about names `yf` already knows. `operator-notes` and `linked-skill`
are not absent from its report as *findings* — they are absent from its **input**. This is the
primitive Epic 1 exists to build: a directory walk.

Note also what `status` *does* get right: it correctly separates the unmodified copy from the
modified one. The gap is **enumeration**, not classification — which is why 1.3 builds the
classifier over the existing `marker` helpers rather than replacing them.

## 3. Live-tree re-measure (EXP-007's falsifier, re-run rather than inherited)

Re-measured rather than inherited, because an operator with hand-edited skills legitimately gets
a different distribution and the migration gate's deliberate empty-`delete`-set failure is only
correct if the live population is genuinely deletable:

| Root | embedded skills seen | `unmodified: true` |
| :-- | --: | --: |
| `~/.claude/skills` | 19 | 19 |
| `~/.agents/skills` | 19 | 19 |
| `~/.config/opencode/skills` | 19 | 19 |
| `~/.pi/agent/skills` | 19 | 19 |
| **total** | **76** | **76** |

**76 of 76 — EXP-007 reproduced.** Deployment residue does not escape the ignore-list, so the
`delete` set will be non-empty and the migration gate's empty-set failure will not fire
spuriously.

## 4. Do NOT over-read the 76/76 — and here is the measurement that shows why

The figure speaks only to the **19 embedded skills per root**. The roots actually hold far more:

| Root | directories present | seen by the name-keyed walk | **structurally invisible** |
| :-- | --: | --: | --: |
| `~/.claude/skills` | 37 | 19 | **18** |
| `~/.agents/skills` | 22 | 19 | **3** |
| `~/.config/opencode/skills` | 32 | 19 | **13** |
| `~/.pi/agent/skills` | 33 | 19 | **14** |
| **total** | **124** | **76** | **48** |

**48 directories across the four roots are invisible to every existing enumeration in `yf`.**
That is the RED baseline in one number.

Two of the plan's claims are corroborated in passing:

- **R11 is exact.** The 13 invisible members of `~/.config/opencode/skills` are precisely the
  cloudflare/sandbox family R11 names: `agents-sdk`, `cloudflare`, `cloudflare-email-service`,
  `cloudflare-one`, `cloudflare-one-migrations`, `durable-objects`,
  `sandbox-migrate-to-next`, `sandbox-next`, `sandbox-stable`, `turnstile-spin`, `web-perf`,
  `workers-best-practices`, `wrangler`.
- **D-2b's `undetermined` outcome is LIVE on this machine, not hypothetical.** Real symlinked
  members exist in three of the four roots:
  `~/.agents/skills/terminal-browser` → `~/.local/share/terminal-browser/app/skills/default/terminal-browser`
  (into an application's own directory — a tree-hash walk that *followed* it would hash someone
  else's tree), plus `convert-documents-to-markdown` in `~/.pi/agent/skills` and
  `~/.claude/skills`, and `terminal-browser` again in `~/.claude/skills`.

## Reproduction

The fixture is re-runnable; "was recorded first" is a git-history property with no stable
predicate, which is why SC5b is a `manual:` criterion. The live measurements above are
reproduced by `yf harness skills status --harness <h> --json` and `ls -1 <root>`.
