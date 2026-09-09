---
type: Note
okf_spec: OKF-PLAN
description: "The full upstream write set for plan-066 and plan-067, DRAFTED AND UNPOSTED. Nine bodies, the ordering constraint, and the exact commands. Nothing here has been executed."
id: upstream-drafts
plan: plan-067-james-dixson-de852a
created: 2026-09-08
---
# Upstream write set — DRAFTED, NOTHING POSTED

**Every body in this directory is a draft. No `gh` write has been run.** The Upstream write
authorization gate (`yf-mol-gtcy.11`) is draft-then-confirm, per-issue.

## The set

| # | Issue | Action | Body |
| :-- | :-- | :-- | :-- |
| 1 | `#376` | comment + **CLOSE** | [376-comment.txt](376-comment.txt) |
| 2 | `#375` | comment + **CLOSE** | [375-comment.txt](375-comment.txt) |
| 3 | `#374` | comment + **CLOSE** | [374-comment.txt](374-comment.txt) |
| 4 | `#373` | comment + **CLOSE** | [373-comment.txt](373-comment.txt) |
| 5 | `#247` | comment only — **STAYS OPEN** | [247-comment.txt](247-comment.txt) |
| 6 | `#263` | comment only — **STAYS OPEN** | [263-comment.txt](263-comment.txt) |
| 7 | new | **CREATE** from local bead `yf-w57p` | [w57p-body.txt](w57p-body.txt) |
| 8 | `#317` | comment + **CLOSE** | [317-comment.txt](317-comment.txt) |
| 9 | `#372` | comment + **CLOSE** — plan-066's tracker | [372-comment.txt](372-comment.txt) |
| 10 | `#379` | comment + **CLOSE** — plan-067's tracker, **LAST** | [379-comment.txt](379-comment.txt) |

## The ordering constraint, and what it forbids

**Do not close a tracker for a plan still in `executing`.**

```
1-7   plan-067's own reconcile + the follow-on. Safe now.
8     #317 — plan-066's scope issue. Closes as part of ITS reconcile (8.5),
      while plan-066 is still executing. That is correct: #317 is not a tracker.
      ─── plan-066 then reaches `complete` ───
9     #372 — plan-066's TRACKER. Only after plan-066 is `complete`.
      ─── plan-067 then reaches `complete` ───
10    #379 — plan-067's TRACKER. Last of all.
```

**One thing blocks steps 9-10 today, and it is not an upstream question.** plan-066's Issue 8.4b
has a hard guard requiring `HEAD` on `main` **and** the plan branch merged — it is a land-time
bead, correctly still open on the execute branch.

*(The other blocker is resolved. `d2` was upgraded **v0.8.2 → v0.9.0** outside any session, which
took `render-bytes-match` INCONCLUSIVE in both plans. On 2026-09-09 the operator chose re-render
and re-pin; all 21 were re-rendered under v0.9.0 with unchanged flags in one commit, and both
plans' criteria hold again. Bead `yf-8g5x` is closed. No third human read was needed: geometry is
identical 21/21 and the pixel differences are glyph-edge antialiasing.)*

## Why these are `.txt` and not `.md`

**They are PAYLOADS, not bundle documents.** The OKF model requires YAML frontmatter on every
`.md` in a bundle — and frontmatter in one of these would be **posted verbatim into the GitHub
issue**, because `--body-file` sends the file as-is. The content is still markdown and GitHub
renders it as markdown; the extension declares the file's **role in the bundle**, which is
"input to a command", not "document a cold reader reads".

Adding frontmatter and stripping it at post time was the alternative and is worse: it puts a
transformation between the reviewed text and the posted text, which is exactly what the
read-it-back rule below exists to catch.

## The command form — non-negotiable

Every body goes through **`--body-file -` fed by a QUOTED heredoc**, never `--body`. Issue bodies
are markdown full of backticks and backslashes: a single-quoted `--body` passes backslashes
through literally, and an unquoted one lets the shell expand `` ` `` and `$`. The heredoc is the
only form that survives both.

Here the bodies are already files, so `--body-file <path>` is used directly — same guarantee,
fewer moving parts.

```bash
D=docs/plans/plan-067-james-dixson-de852a/assets/upstream-drafts

# ---- 1-4: comment, then close. Comment FIRST so the rationale is on the issue
#           before its state changes.
for n in 376 375 374 373; do
  gh issue comment "$n" --body-file "$D/$n-comment.txt"
  gh issue close   "$n"
done

# ---- 5-6: comment ONLY. These stay OPEN.
gh issue comment 247 --body-file "$D/247-comment.txt"
gh issue comment 263 --body-file "$D/263-comment.txt"

# ---- 7: the follow-on. Record the returned URL onto the bead.
URL=$(gh issue create \
        --title "$(cat "$D/w57p-title.txt")" \
        --body-file "$D/w57p-body.txt")
bd update yf-w57p --external-ref "$URL"

# ---- 8: #317. plan-066 is still `executing` here, and that is correct.
gh issue comment 317 --body-file "$D/317-comment.txt"
gh issue close   317

# ---- 9: ONLY after plan-066 reaches `complete`.
gh issue comment 372 --body-file "$D/372-comment.txt"
gh issue close   372

# ---- 10: ONLY after plan-067 reaches `complete`. Last of all.
gh issue comment 379 --body-file "$D/379-comment.txt"
gh issue close   379
```

## Verification — read it back, never trust exit 0

A `gh` exit 0 is not proof the body posted correctly; backtick and backslash mangling exits 0 too.
After each write:

```bash
gh issue view <N> --comments | tail -40     # the body, as it actually rendered
gh issue view <N> --json state --jq .state  # OPEN or CLOSED, as intended
```

**The two that must still read `OPEN` afterwards are `#247` and `#263`.** Check them explicitly —
a close is the one mistake here that is outward-facing and awkward to undo:

```bash
gh issue view 247 --json state --jq .state   # must print OPEN
gh issue view 263 --json state --jq .state   # must print OPEN
```
