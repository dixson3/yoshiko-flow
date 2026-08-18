---
type: Finding
okf_spec: OKF-PLAN
id: exp-007-160-init-ordering-probe
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
---

# exp-007 — The #160 init-ordering hypothesis: CONFIRMED

**Issue:** 1.6 · **Plan:** plan-044 · **Date:** 2026-08-17 · **Upstream:** #160

## Question

exp-002 (b) proposed, explicitly marked **inferred and unverified**, that `repair()`
(`beads_init.rs`) runs `bd init` **before** `bd config set dolt.local-only true`, and that
because `dolt.local-only` is an *init-time skip flag*, `bd init` wires a Dolt remote from the
git origin first — while the step label asserted *"no remote wired at init"*.

Success Criterion 4 requires this **settled in writing** either way.

## Method

A sandboxed probe reproducing `repair()`'s exact step order in a throwaway repo:

```bash
git init . && git remote add origin https://github.com/dixson3/yoshiko-flow.git
bd init --skip-hooks --skip-agents      # repair()'s first step, verbatim
bd config set dolt.local-only true      # repair()'s next step, verbatim
```

Then both remote layers were read back.

## Result — CONFIRMED, at both layers

`bd init` wires the remote unprompted, from the git origin:

```
✓ Configured Dolt remote: origin → git+https://github.com/dixson3/yoshiko-flow.git
```

And the local-only assertion that follows does **not** remove it. After **both** steps:

| Layer | Reader | Value after both steps |
| :-- | :-- | :-- |
| secondary (config) | `bd config get sync.remote` | `git+https://github.com/dixson3/yoshiko-flow.git` |
| decisive (Dolt DB) | `dolt remote -v` | `origin git+https://github.com/dixson3/yoshiko-flow.git` |

So on the init path, `repair()` **produced the exact #160 state it claimed to prevent**, and the
step label was false.

## Why reordering is not available

The obvious fix — set `dolt.local-only` *before* `bd init` — is impossible:

1. The flag lives in `.beads/config.yaml`, which **does not exist** until `bd init` creates it.
2. `bd init` exposes **no** local-only / no-remote flag. Its only remote-related option is
   `--remote <url>`, which *adds* one. (`bd init --help`, bd 1.1.2.)

## Fix taken — the plan's stated alternative

Imply the `remove-remote` step on the init path when `--local-only` is requested.

The authority question this raises is real: `--remove-remote` is deliberately opt-in because it
inverts an otherwise-conservative "never touch the remote" boundary. Implying it is nonetheless
sound **here specifically**, on a narrow ground: on the init path there was no beads repo moments
earlier, so the implied removal can only ever clear a remote **this very run just created**,
against the operator's explicit local-only request. It can never touch a pre-existing operator
remote. The opt-in gate is unchanged on the already-initialized path.

## Artifacts

- `beads_init.rs` — implied step + the corrected label (the old one asserted the falsehood).
- Test `init_path_under_local_only_implies_remote_removal`, plus a scoping assertion that the
  implication does **not** fire without `--local-only`.
- `remove_remote_step_is_gated` was **narrowed, not deleted**: its `absent when remove_remote
  false` case is still true on an already-initialized repo but no longer on the init path. The
  test now says so rather than being quietly weakened.
