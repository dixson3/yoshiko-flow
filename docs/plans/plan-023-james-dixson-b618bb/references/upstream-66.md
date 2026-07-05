# Upstream #66: yf-beads-init: gitignore .beads/interactions.jsonl in repair's gitignore top-up (canonicalization #39 gap)

- **Number:** 66
- **Title:** yf-beads-init: gitignore .beads/interactions.jsonl in repair's gitignore top-up (canonicalization #39 gap)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Problem

The `yf-beads-init` canonicalization repair (`yf doctor --repair`, REQ-BINIT-023 / #39)
untracks the pinned runtime set with `git rm --cached`:

`.beads/interactions.jsonl`, `.beads/embeddeddolt/`, `.beads/backup/`,
`.beads/export-state.json`, `.beads/push-state.json`, `.beads/dolt-server.*`

Five of these six are also covered by bd's managed `.beads/.gitignore` (`embeddeddolt/`,
`backup/`, `export-state.json`, `push-state.json`, `dolt-server.*`). But
**`interactions.jsonl` has no ignore pattern** — not in bd's default `.beads/.gitignore`,
and not in the repair's gitignore top-up list.

Net effect: the repair untracks `interactions.jsonl`, but nothing ignores it, so it
immediately resurfaces as an untracked `?? .beads/interactions.jsonl` — persistent
`git status` noise. A bare `git add -A` in `.beads/` will also silently re-track it.

## Repair's current gitignore top-up list

Per `SKILL.md`, the engine tops up `.beads/.gitignore` with:

`.env, export-state.json, embeddeddolt/, proxieddb/, dolt-server.activity, daemon.*,
*.lock, *.corrupt.backup/, .beads-credential-key, proxied_server_client_info.json`

`interactions.jsonl` is absent.

## Proposed fix

Add `interactions.jsonl` to the repair's `.beads/.gitignore` top-up set (the "ensure
`.beads/.gitignore` exclusions" step), so the file that canonicalization untracks is also
ignored — consistent with the other five runtime artifacts. Idempotent; no-op if already
present. Update `SKILL.md`/`SPEC.md` (REQ-BINIT-023) to reflect that untracking a runtime
artifact implies also ignoring it.

## Workaround applied downstream

In `dixson3/writing` I added the pattern to `.beads/.gitignore` by hand
(commit adds `interactions.jsonl` under the Runtime files section). Since `.beads/.gitignore`
is bd-managed, a future bd regenerate could drop it — the durable fix belongs in the repair
engine here.

## Note

Ideally bd itself would add `interactions.jsonl` to its default `.beads/.gitignore`; that's
an upstream-bd fix. This issue tracks the yf-beads-init-side belt-and-suspenders that doesn't
depend on the bd change landing.
