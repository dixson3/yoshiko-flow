# The primary checkout carries the fixes (Issue 6.4 / SC13)

Confirmed **before** any `land --apply`. This is R3's mitigation, checked rather than assumed.

```
$ P="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"
/Users/james/workspace/dixson3/yoshiko-flow
$ git -C "$P" grep -q 'force=False' -- skills/yf-plan/scripts/plan_manager.py \
    && ! git -C "$P" grep -q '_worktree_teardown(ctx.plan_dir)$' -- skills/yf-plan/scripts/plan_manager.py
rc=0
```

## Why `--git-common-dir` and not `--show-toplevel`

`--show-toplevel` answers "the root of the checkout I am in", which inside
`.worktrees/<plan-id>` is **the worktree**. `--git-common-dir` points at the primary's
`.git` from either address space, because that is where the shared object store and refs
live — so its parent is the primary checkout unambiguously. Using `--show-toplevel` here
would have verified the wrong tree and reported a green about it.

## Why this plan needed it at all

This plan runs **in-place** (`execute.worktree: false`), so the primary checkout and the work
tree are the same directory and the check is trivially satisfiable today. It is recorded
anyway because the *reason* it must hold is not trivial: this plan edits the
`plan_manager.py` the landing itself runs from. Under worktree mode the primary would have
stayed on `main` carrying the **unfixed L18**, and the landing would have crashed at the
prune — exactly as plan-062's did. The capability gate `execution is in-place, not in a
worktree` fired at execute start and resolved green; this is the same invariant re-checked at
the other end, at the point where being wrong is expensive.

| fact | value |
| :-- | :-- |
| primary checkout | `/Users/james/workspace/dixson3/yoshiko-flow` |
| current branch | `plan-063-james-dixson-3f74c1-execute` |
| HEAD | `fb33e102c8d9f8dac79512d49b9152783084e353` |
| `execute.worktree` | `false` (config.local.json, resolved at the §5.2c sweep) |
| `execute_worktree_present` (manifest) | `false` — no worktree exists, correctly reported |
