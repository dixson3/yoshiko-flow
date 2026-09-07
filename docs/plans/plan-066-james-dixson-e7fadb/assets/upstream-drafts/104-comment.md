## Fixed in plan-066

Three parts, and the shape is forced by a measurement rather than chosen:

- **`IGNORE_FILES`** in `web/pelicanconf.py` — dotfiles, editor swap files, and `*.d2` sources.
  Verified on a **clean** rebuild, not an incremental one: the six `.d2` sources were being copied
  into `output/images/` as dead weight, and a stale output directory would have shown them either
  way. Fresh build now emits 0.
- **`make devserver`** runs pelican under `set -m`, in its **own process group**, recording the
  pgid to `web/.devserver.pgid`. Reproduced the original failure exactly: killing the `pelican -lr`
  parent leaves **three** children reparented to `ppid=1`, one still holding the port, and **none
  carries `pelican` in argv** — so `pkill pelican` misses every one.
- **`make stopserver`** reads that pgid and kills the group. Idempotent: a missing or stale pgid
  file reports and exits 0.

**`set -m` is the safety property, not a detail.** Without it the pgid is the *calling shell's*,
and `kill -- -$PGID` would kill the operator's own shell.

`.devserver.pgid` is gitignored.

Measured incidentally and worth recording: **#104 bites only the devserver.** A one-shot
`pelican content` leaves nothing behind, so a batch regeneration is unaffected — which is why this
was sequenced so it could not block the build fix.
