# Upstream #60: yf-beads-upstream: support mutually-exclusive requires:<platform> labels in worklist filtering + hoist

- **Number:** 60
- **Title:** yf-beads-upstream: support mutually-exclusive requires:<platform> labels in worklist filtering + hoist
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

Teach the `yf-beads-upstream` skill about platform-constraint labels (`requires:linux`,
`requires:macos`, `requires:windows`) so the **status / pull** worklist hides issues that
can't be worked on the current OS, and so **hoist / push** can attach and validate these
labels.

## Motivation

Some upstream issues are inherently platform-bound (e.g. an Emacs-config follow-up that can
only be verified on a Linux GUI build). When reviewing the upstream worklist on macOS I do
not want to see `requires:linux` issues, and vice versa. These labels are **mutually
exclusive** — an issue carries at most one `requires:<platform>`.

## Proposed behavior

**Label convention (document in SKILL.md):**
- `requires:linux` / `requires:macos` / `requires:windows`, mutually exclusive (at most one
  per issue). No label = workable anywhere.
- Suggested creation as part of `init` (optional), idempotent (`gh label create --force`).

**Status / pull (worklist filtering):**
- Detect the current platform (e.g. `uname`/`$OSTYPE`, or a `custom.upstream.platform`
  override).
- When enumerating open upstream issues, **exclude** any issue whose `requires:<platform>`
  label differs from the current platform. Issues with no `requires:*` label always show.
- Provide an escape hatch (e.g. `--all-platforms`) to show everything.

**Hoist / push:**
- Allow attaching a `requires:<platform>` label at hoist time (e.g.
  `hoist --issues <ids> --requires linux`).
- Validate mutual exclusivity: refuse to add a second `requires:*` to an issue that already
  has one (or replace, with a warning).
- Ensure scoped `bd <backend> push` does not strip an existing `requires:*` label (verified
  on bd 1.0.5 that bd-managed `priority::`/`type::` labels are added alongside, and a
  manually-applied `requires:linux` survived a re-push).

## Context / first real use

First applied manually in `dixson3/emacs.d`: labels created there and
[issue #6](https://github.com/dixson3/emacs.d/issues/6) tagged `requires:linux` (a Linux-only
tall-glyph fallback follow-up). The skill should make this a first-class, documented flow
rather than manual `gh label` calls.

