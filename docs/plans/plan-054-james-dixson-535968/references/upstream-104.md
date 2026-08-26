---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #104: web: prevent runaway Pelican devservers + add clean teardown (port naba#21)

- **Number:** 104
- **Title:** web: prevent runaway Pelican devservers + add clean teardown (port naba#21)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Problem

The Pelican `-lr` (listen + autoreload) devserver leaks runaway processes. Two failure modes, both observed in sibling repos:

1. **Orphaned workers.** When the shell/session that ran `make devserver` exits, the autoreload watcher and its `multiprocessing` children are reparented to `launchd`/`init` and keep running indefinitely. There's no `stopserver` target to reap them, and the rogue children run `python -c 'from multiprocessing.spawn ...'` with **no `pelican` in their command line**, so a plain `pkill pelican` misses them.

2. **CPU busy-loop on editor scratch files.** Without an `IGNORE_FILES` guard, the autoreload watcher chokes on transient editor lock/scratch files (Emacs `.#foo`, `foo~`, vim `.foo.swp`). A flickering `.#page.md` lockfile drives an endless failing regenerate loop that pins a CPU core at ~100%.

In `naba`, two such orphaned workers had each been pinning a core for **days** before they were noticed.

## Fix (as applied in naba)

See **dixson3/naba#21** (commit `383b5af`). Three small changes to the `web/` Pelican project:

1. **`pelicanconf.py`** — ignore editor scratch/lock files so they can't reach the content reader or the autoreload watcher:
   ```python
   IGNORE_FILES = [".#*", "*~", ".*.sw?", "4913"]
   ```

2. **`Makefile`** — run `devserver` in its own process group (`set -m` job control) and record the PGID; add a `stopserver` target that kills the whole group (parent **and** multiprocessing children), even after orphaning:
   ```makefile
   DEVSERVER_PID = $(BASEDIR)/.devserver.pgid
   devserver:
   	@set -m; \
   		"$(PELICAN)" -lr "$(INPUTDIR)" -o "$(OUTPUTDIR)" -s "$(CONFFILE)" $(PELICANOPTS) & \
   		pgid=$$!; echo $$pgid > "$(DEVSERVER_PID)"; \
   		trap 'kill -- -$$pgid 2>/dev/null; rm -f "$(DEVSERVER_PID)"' INT TERM EXIT; \
   		wait $$pgid

   stopserver:
   	@if [ -f "$(DEVSERVER_PID)" ]; then \
   		kill -- -$$(cat "$(DEVSERVER_PID)") 2>/dev/null && echo "Stopped devserver." || echo "Devserver not running (clearing stale pidfile)."; \
   		rm -f "$(DEVSERVER_PID)"; \
   	else \
   		echo "No pidfile — no devserver was started by this Makefile."; \
   	fi
   ```
   (also add `stopserver` to `.PHONY` and a `help` line)

3. **`.gitignore`** — ignore the runtime pidfile:
   ```
   .devserver.pgid
   ```

## Notes

- Adjust the variable names (`PELICAN`, `INPUTDIR`, `OUTPUTDIR`, `CONFFILE`, `PELICANOPTS`, `BASEDIR`) to match this repo's existing Makefile.
- Verified in naba end-to-end: start devserver → pelican + all multiprocessing children share the recorded PGID → `make stopserver` → all killed, pidfile cleaned.

