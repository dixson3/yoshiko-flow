# Experiment 001 — embedded-mode wedge escape hatch

**Question:** For the embedded-storage wedged-migration repair, which escape-hatch mechanism
clears the dirty Dolt working set, how is embedded mode detected, how is the dolt repo path
derived, and how is the commit step made a safe no-op? Is an end-to-end wedged-repo test feasible?

**Method:** throwaway `git init && bd init` repo under `mktemp -d`; `bd 1.0.5` (Homebrew),
`dolt 2.1.10`, both on PATH. No project files touched.

## Findings

### Layout & path derivation
`bd init` reports `Mode: embedded`. Dolt repo root is `.beads/embeddeddolt/<dolt_database>` where
`<dolt_database>` is the sanitized db name (dir `e-layout` → db `e_layout`), **not** a hardcoded
`.beads/embeddeddolt/dolt`. `bd dolt --help` documents a `data-dir` override (default base can
vary), so the base path is not guaranteed.

**Robust derivation (chosen):** find the unique directory under `.beads/` containing a `.dolt/`
child; its parent is the dolt repo root (`find .beads -type d -name .dolt` → `dirname`). Verified:
`.beads/embeddeddolt/e_layout/.dolt`. Config-agnostic, survives `data-dir` overrides.
**Fallback:** `metadata.json.dolt_database` joined under the data-dir base.

### Mode detection
`metadata.json` carries `"dolt_mode": "embedded"` — authoritative, filesystem-only, no exit-code
inference. Corroborating: no `dolt-server.pid`/`.port` for embedded repos; `bd dolt status` prints
`embedded (in-process, no server)` (exit 0). `bd dolt stop` in embedded mode →
`Error: 'bd dolt stop' is not supported in embedded mode (no Dolt server)` exit 1 (the reported
failure). **Do not** detect mode from `bd dolt stop`'s exit code — read `metadata.json`.

### Escape hatch (crux)
Both `bd dolt commit` and raw `dolt add -A && dolt commit` clear a dirty working set (exit 0,
data preserved) on a merely-dirty set. **Could NOT reproduce a genuine wedged migration** with a
single bd 1.0.5 binary (a true wedge needs binary/DB schema-version skew from an upgrade + a
persisted dirty set; bd's aggressive auto-commit/schema re-derivation prevents synthesizing one) —
explicit absence finding. Therefore `bd dolt commit`'s behavior *while bd is wedged* is
**unverified**. The real-world manual fix deliberately used **raw** dolt because bd was wedged; a
bd subcommand may hit the same wedged migration preflight. **Chosen: raw `dolt` with derived cwd**
— it bypasses bd entirely and (in embedded mode, no server) faces no lock contention.
Never `reset --hard` — `add -A && commit` preserves data.

### No-op / idempotency
- `dolt add -A` on clean tree → exit 0 (no-op).
- raw `dolt commit` on clean tree → exit 1, `no changes added to commit` — must be tolerated.
- `dolt commit --allow-empty` → exit 0 but creates a noise empty commit — **do not use**.
- `bd dolt commit` on clean → `Nothing to commit.` exit 0 (but see wedge caveat).

**Chosen guard:** run `dolt status`/`dolt diff` first and commit only if dirty (or tolerate the
exit-1 "no changes added" as success). No `--allow-empty`.

### Test feasibility
A deterministic end-to-end wedged-repo test is **not cheaply constructible** (needs schema-version
skew + persisted dirty set; bd prevents synthesizing one; an old-binary fixture DB is heavy and
version-pinned). **Recommendation (operator-approved tier):** (1) plan-shape unit assertions —
embedded detection emits `dolt add -A && dolt commit` in the derived cwd → `bd migrate schema` →
`bd migrate`, and NOT `bd dolt stop`, with a derived (not hardcoded) path; (2) native-step
idempotency integration — `bd init` a real embedded repo, dirty via `dolt sql`, run the step,
assert clean + data preserved, re-run and assert safe no-op; assert mode detection reads
`metadata.json`.

## Non-verifications (absence findings)
- Genuine wedged migration not reproduced → `bd dolt commit`-while-wedged unverified (basis for
  preferring raw dolt).
- Server-mode layout not exercised → all findings are for the embedded layout the fix targets; the
  server-mode path must be left intact and untested-by-this-change.
