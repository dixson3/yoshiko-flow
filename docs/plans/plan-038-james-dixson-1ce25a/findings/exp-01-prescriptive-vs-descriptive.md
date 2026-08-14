---
type: Finding
okf_spec: OKF-PLAN
---
# Experiment 1: Which `bd <backend>` mentions in SKILL.md are the bug?

**Question.** The companion rule forbids hand-running `bd <backend>` push commands; SKILL.md
contains 20 such mentions. Which must be rewritten, and which must be left alone?

**Why it matters.** A blind find-replace over all 20 would strip the skill of the explanations
that make it usable — including the statement of the invariant itself. Leaving all 20 keeps the
contradiction. The fix depends entirely on getting this split right.

## The contradiction, demonstrated live

While pushing 11 orphaned beads in the session that produced this plan, the operator's agent ran:

```bash
GITHUB_TOKEN=$(gh auth token) bd github push yf-m78m yf-252c … --dry-run
GITHUB_TOKEN=$(gh auth token) bd github push yf-m78m yf-252c …
```

It did so **because SKILL.md Push step §3 documents exactly that as the procedure.** The
always-loaded companion rule `protocols/UPSTREAM_TRACKING.md` says:

> **Route every upstream push through `/yf-beads-upstream` — do not hand-run `bd <backend>` push
> commands.** … If `/yf-beads-upstream` is unavailable, stop and report — do not substitute a
> hand-run push.

So following the skill violated the rule. This is the #106 defect reproduced in practice, not in
theory. Note the push itself was harmless — enumeration and mapping were done through the
skill's own helper — which is precisely why the contradiction survives: it does not fail loudly,
it just makes compliance impossible.

## The split

All 20 mentions, classified by whether they **instruct** or **explain**.

### Prescriptive — the bug (must route through `upstream.py`)

| Line(s) | Context | What it tells the reader to run |
|:--|:--|:--|
| 289–294 | Push §3 | `bd github push <ids> --dry-run` then the real push — the primary offender |
| 297 | Push §3 | subtree form `bd github sync --push-only --parent <id> --dry-run` |
| 308 | Push §4 | failure handling keyed on "non-zero `bd github push` exit" |
| 343 | Push §6 | re-push step 2: "`bd github push <id>`" |
| 451 | Backend table | *Scoped push* row: `bd github push <ids>` / `bd gitlab push <ids>` / `bd jira push <ids>` |
| 456–459 | Jira note | "Prefer the dedicated `bd jira push <ids>` subcommand" |

### Descriptive — must stay

| Line(s) | Why it stays |
|:--|:--|
| 42 | "Built on bd 1.0.5's first-class `bd github`…" — provenance, not instruction |
| 80, 93 | The three-mechanism disambiguation (`git push` vs `bd dolt push` vs this mirror). Removing this re-opens the #61 confusion the table exists to prevent |
| 116, 188 | The inline-auth invariant (`TOKEN=$(...) bd <backend> …` — never persisted) |
| 327–328 | Dated empirical verification blockquote (bd 1.0.5, throwaway repo, 2026-06-01) — evidence, and rewriting it would falsify what was actually tested |
| 343 (blockquote) | Second dated verification (2026-06-07, notes-vs-description sync) |
| 435 | "`bd github status` shows sync state but is not the worklist" — a *don't* |
| 446, 463–464 | "flags confirmed present on backend-generic `bd <backend> sync`" — capability evidence |
| 468, 471 | **The safety invariants themselves** — the never-bare-`sync` and inline-auth rules. These *quote* the command in order to forbid it |

The 468/471 case is the sharpest illustration: an automated rewrite would mangle the very rule
the plan exists to enforce.

## Consequence for the plan

Two distinct kinds of edit, and they must not be conflated:

1. **Six prescriptive sites** get rewritten to call a new `upstream.py push`. Mechanical once the
   verb exists.
2. **Fourteen descriptive sites** stay, but §3's rewrite changes what the surrounding recovery
   prose (§4, §6) *means* — those sections describe recovering from a raw `bd` invocation that
   will no longer be what the reader ran. They need re-derivation, not find-replace.

An acceptance check that greps for `bd github push` and expects zero hits would be **wrong** —
it would fail on the invariant statements that must survive. The check must be scoped to the
prescriptive sections.
