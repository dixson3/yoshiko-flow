# Drive-verify — Issue 5.2 (SC17 / SC17b evidence)

**Date:** 2026-08-27 · **Plan:** plan-055-james-dixson-5f1c40

Established by **DRIVING each harness**, not by asking `yf`. That distinction is the whole
point of the criterion: `yf` reporting where it *would* write proves nothing about where a
harness *reads*, and it is precisely the gap that let the shadowing defect ship.

## Order of operations — quarantine BEFORE verify, which is the only order the measurements permit

EXP-002 measured that with the private trees still present, pi resolves `~/.pi/agent/skills`
**3/3** (deterministic first-wins) and opencode picks `.config/opencode` **4 times in 5** (a
race). A pre-move verification would therefore have failed **by construction** on a correctly
built plan. Quarantining first is what makes the verification meaningful; the measured one-line
restore is what makes it safe.

## 1. Pre-verify state

| Root | yf-* directories | foreign directories retained |
| :-- | --: | --: |
| `~/.agents/skills` (shared) | 19 | — |
| `~/.config/opencode/skills` | **0** | 13 |
| `~/.pi/agent/skills` | **0** | 13 |

Quarantine `/Users/james/.yf-quarantine/plan-055-1787886237` holds 38 skill directories + the operator-authorized symlink, each with its
`.origin` recorded. The 26 retained foreign directories are R11's residue, correctly **kept**
— they are not yf's to delete, and the dry-run enumerates every one.

## 2. The drive — three harnesses, one prompt

Each harness was driven headlessly and asked to report the `SKILL_DIR_INSTALLED_AT` value in
the `yf-plan` `SKILL.md` **it actually loaded**:

| Harness | Command | Reported |
| :-- | :-- | :-- |
| pi | `pi -p "…" --approve` | `/Users/james/.agents/skills/yf-plan` |
| opencode | `opencode run "…"` | `/Users/james/.agents/skills/yf-plan` |
| codex | `codex exec --skip-git-repo-check "…"` | `/Users/james/.agents/skills/yf-plan` |

opencode's transcript additionally shows its own tool call resolving the skill in
`/Users/james/.agents/skills/yf-plan` — the harness's own view, not a claim it repeated back.

**All three: the shared root.** opencode in particular no longer has a private root to racily
prefer, so the 4:1 coin flip EXP-002 measured is now **unrepresentable** for yf-authored skills
rather than merely unobserved.

## 3. Why the stamp clause is what distinguishes this from `rm -rf`

SC17 requires not just the right root but that the resolved tree carries the
`SKILL_DIR_INSTALLED_AT` stamp written by the **post-collapse** build. It does, and the value
*is* the shared root:

```
SKILL_DIR_INSTALLED_AT="/Users/james/.agents/skills/yf-plan"
```

That value could only have been written by a post-collapse binary. The stamp is written per
deployed copy with **that copy's own destination root** — so a pre-collapse build deploying for
opencode would have stamped `~/.config/opencode/skills/yf-plan`, and for pi
`~/.pi/agent/skills/yf-plan`. A bare `rm -rf` of the two private trees would have satisfied
the *root* claim while leaving the old stamps in place. It did not happen that way here.

Corroborating: the 5.1a install reported **"Installed 19 skill(s) into 2 destination(s)"**. Before
the collapse that number was 4. The collapse is visible in the installer's own output.

## 4. Verdict

**GREEN.** Migration committed. The quarantine is **retained** (see the run record) rather than
dropped, so the undo remains available.
