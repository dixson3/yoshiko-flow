# Finding INV-1: git worktree mechanics & path safety

**Date:** 2026-06-14 · **Method:** real git commands in throwaway /tmp repos (git 2.54.0, macOS)

## Result

**Q1 — `.git/worktree/<plan>` (singular) vs git's internal `.git/worktrees/` (plural).**
Does NOT hard-collide (git made the checkout at `.git/worktree/<plan>` and admin metadata
at `.git/worktrees/<plan>` side by side; gc/clean/remove all worked). **But reject it
anyway:** it nests a live working tree inside the gitdir one segment from git's reserved
`worktrees/` area — fragile (any `rm -rf .git/...` housekeeping or future git tightening
destroys in-progress work), depends on never typo'ing singular→plural, and has zero upside.

**Q2 — Idiomatic location.** Git imposes no required path. Clean, observed-safe convention:
a **gitignored top-level `.worktrees/<plan>`** (parent `git status` stays empty; shows only
under `--ignored`). An external sibling `../<repo>-worktrees/<plan>` also works but in-repo
gitignored `.worktrees/` is self-contained and easier for a tool to manage.

**Q3 — Branch naming.** `git worktree add … -b plan-009-james-dixson-996e44` succeeds; 60+
char names succeed; plan IDs are `[a-z0-9-]`, all valid. No issue.

**Q4 — Teardown.** `worktree remove` on a clean tree succeeds even with unmerged commits
(commits persist on branch). With uncommitted/untracked files it REFUSES (`fatal: …
contains modified or untracked files, use --force`). **Branch is never deleted by
`remove`** — separate `git branch -d` (merged) / `-D` (force). `git worktree prune` clears
stale admin entries after a manual `rm -rf` of the checkout (crash case).

**Q5 — Merge-back + two-worktrees-on-main constraint.** Confirmed you CANNOT check out
`main` in a second worktree while primary holds it (`fatal: 'main' is already used by
worktree…`). Correct: merge **from the primary checkout** — `git merge <plan-branch>` reads
the plan branch's commits even while that branch is checked out in the plan worktree
(verified ff and `--no-ff`). Never check out the base in the worktree.

**Q6 — Edge cases.** Dirty primary at create: `add` succeeds, new tree starts from HEAD,
dirty changes stay in primary. Branch already exists (resume): `add … -b` FAILS — use
`git worktree add <path> <plan>` WITHOUT `-b` to attach existing branch. Path already a
worktree / branch already checked out elsewhere / non-git dir: all `fatal` with distinct
messages → pre-checkable.

## Implications for Plan
- **Reject the proposed `.git/worktree/<plan>` placement.** Use gitignored
  `.worktrees/<plan-id>`; `bdplan execute` must ensure `.worktrees/` is in `.gitignore`.
- Resume must branch on existing-branch detection (`-b` first run; attach-without-`-b` on
  resume); pre-check existing worktree/branch-in-use for idempotency.
- Merge-back runs in the primary checkout; teardown distinguishes dirty (block/`--force`
  on confirm) from clean; branch deletion is an explicit separate step.

## Recommended recipe (`bdplan execute --worktree`)
1. Preflight: confirm git repo (`git rev-parse --git-dir`); ensure `.worktrees/` in
   `.gitignore`. Do not require a clean primary tree.
2. Placement `WT=.worktrees/<plan-id>`; branch = plan id verbatim.
3. Create idempotent: new `git worktree add "$WT" -b "<plan-id>"`; resume
   `git worktree add "$WT" "<plan-id>"`; existing worktree → reuse.
4. Work with cwd inside `$WT`.
5. Merge-back from primary: `git -C <root> merge --no-ff "<plan-id>"`; re-validate in primary.
6. Teardown: `git worktree remove "$WT"` (refuses if dirty); `git branch -d "<plan-id>"`;
   `git worktree prune`.
