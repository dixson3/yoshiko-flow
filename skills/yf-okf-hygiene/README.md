# yf-okf-hygiene

Corpus-level OKF health for a repository of artifact bundles: read-only discovery and
classification, the three-step legacy backfill with a crash-recovery journal, index repair, and
record-driven reversal.

`yf-okf` answers *"is **this** bundle conformant?"*. This skill answers *"which bundles exist
here, what state is each one in, and how do I move the whole population forward safely and
reversibly?"* — it owns the corpus; `yf-okf` owns the single bundle, and provides the per-bundle
engine this skill calls.

## Prerequisites

- `uv` on `PATH` — the engine is a PEP 723 `uv run --script`.
- `git` on `PATH` — the backfill stages inside the repository tree and the restore path uses
  `git checkout` for tracked files.
- The `yf-okf` skill installed (`depends-on-skill: [yf-okf]`), which supplies the per-bundle
  `okf.py` engine.

## Install

Deployed by `yf skills install`, which auto-discovers every `skills/*/` by its `SKILL.md`
frontmatter. From a clean `main`, rebuild and deploy in one step:

```bash
yf self install --from-build --build
```

## Usage

User-invocable (`/yf-okf-hygiene`). Five subcommands:

```
/yf-okf-hygiene audit [--root R]...     read-only discovery + classification; writes NOTHING
/yf-okf-hygiene assess [--root R]...    declared ALIAS of audit
/yf-okf-hygiene backfill [--apply]      the three-step legacy transform; DRY-RUN by default
/yf-okf-hygiene reindex <bundle>        index repair; REFUSES a legacy prose index
/yf-okf-hygiene restore --record <p>    record-driven reversal, per-path operation kind
```

Or call the engine directly:

```bash
uv run "$SKILL_DIR/scripts/okf_hygiene.py" audit --root docs/plans --root docs/research \
    --maxdepth 2 --require-legacy 0 --min-roots 64 --json
uv run "$SKILL_DIR/scripts/okf_hygiene.py" backfill --root docs/plans --maxdepth 2   # dry run
uv run "$SKILL_DIR/scripts/okf_hygiene.py" backfill --apply --record assets/backfill.json
uv run "$SKILL_DIR/scripts/okf_hygiene.py" restore --record assets/backfill.json --apply
```

**Exit contract:** `0` holds · `1` does not · `2` could **not** run. `126`/`127` stay reserved to
the caller.

`--min-roots` and `--require-legacy` are the two **fail-loud floors**, and they are not optional
ergonomics: a corpus tool that inspected nothing exits `0` on every rule it applies, so without a
floor *"the corpus is clean"* and *"the corpus was not read"* are the same observation.

**`assess` is an alias, deliberately.** `yf-okf` advertised an `assess` verb its engine never
dispatched. The capability it advertised — discover bundles under a root, report per-bundle
impact, mutate nothing — *is* `audit`. Re-advertising it here as a third distinct verb would
have moved the defect one directory over rather than deleting it.

## Behavior model

### `audit` — read-only, five classes

Each discovered bundle lands in exactly one class:

| Class | Meaning |
| :-- | :-- |
| `conformant` | has `index.md`, no legacy index |
| `legacy-readme` | `README.md`, no `index.md` |
| `legacy-underscore-index` | `_index.md`, no `index.md` |
| `hybrid-partial` | **both** — a halt class, never transformed |
| `unclassifiable` | no member marker, or unreadable |

`unclassifiable` never collapses into a neighbour. Folding it into `conformant` certifies what
was never read; folding it into a legacy class manufactures work.

### `backfill` — three steps, never one

**`migrate` → delete the renamed legacy index → regenerate the listing.** Never `migrate` alone:
measured on `plan-010`, a bare `migrate` takes the portability audit from `pass` to **`fail`** —
it stamps `plan.md` frontmatter and leaves the renamed README's File-map prose in `index.md`,
which `reindex --write` cannot repair.

**Crash-recoverable by mechanism, and not atomic.** `os.rename` onto a non-empty directory
raises `OSError errno 66`, so the swap is two renames with a window in which the bundle is
absent. Recovery keys on a durable per-bundle journal fsynced before the first rename — never on
directory presence, which cannot separate the staged state from the completed one. Staging
happens **inside the repo tree**, never in a system temp dir: cross-filesystem staging turns the
rename into a copy and voids every durability claim.

**Read the safety evidence precisely.** The `plan.md` content fingerprint is **not** the
guarantee — it excludes `README.md`, `index.md` and `log.md`, i.e. every file this transform
mutates. The real guarantees are the separate phase-log bullet-and-date equality check and the
per-bundle audit-delta check.

### `restore` — checkout is not enough

Record-driven, with a **per-path operation kind**. `git checkout` alone cannot undo the
transform: a modified or deleted *tracked* file is restored by checkout, but a *created*
`index.md` / `log.md` is absent from `HEAD` and must be **unlinked**. A restore that only checks
out leaves every created file behind and reports success.

## Rules

- `audit` writes nothing, ever.
- `backfill --apply` is **consent-gated**. No green test substitutes for the authorization: the
  risk here is data loss, not condition failure.
- The default exclusion set is self-contained, so the skill can run in a foreign repository.
  Executing a backfill outside its own repo is out of scope.
- Nothing is filed upstream to the OKF project; it is tracked read-only.

## File layout

```
skills/yf-okf-hygiene/
├── scripts/
│   ├── okf.py                # the per-bundle OKF engine, vendored from yf-okf
│   ├── okf_hygiene.py        # PEP 723 corpus engine: audit / backfill / reindex / restore
│   └── test_okf_hygiene.py   # classification, backfill journal, and restore-kind tests
├── README.md                 # this file
├── SKILL.md                  # trigger boundary with yf-okf, invocation, dispatch, subcommands
└── SPEC.md                   # REQ-OKFH-* requirements
```
