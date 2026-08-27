`/yf-okf` is the engine behind the folders every stateful yf skill emits. A [yf-plan](/skills/yf-plan/) plan folder, a [yf-research](/skills/yf-research/) report directory, and a [yf-incubator](/skills/yf-incubator/) topic file are all **bundles** — self-contained artifact folders that follow one shared shape. `/yf-okf` constructs those bundles, manages them, and conformance-checks them against that shape. It is also the owner of the OKF-\* spec family: the versioned ruleset that says how each kind of yf artifact is structured and annotated.

The shape it enforces makes yf artifacts **compatible with** the Open Knowledge Format (OKF v0.2). It is a producer and manager plus a conformance self-check — not a third-party OKF validator. The ecosystem already ships linters and MCP servers; the value here is a shared construction engine and an owned spec family, not another validator.

## When it fires

`/yf-okf` is operator-invoked. It never fires on an ordinary file edit — there is no hook and no companion rule. Invoke it to:

- check whether an artifact folder conforms to the OKF model;
- migrate a legacy plan, research, or incubator folder to the reserved-file-plus-frontmatter model;
- assess a whole corpus before adopting OKF across it.

Skip it for a repo's build, test, or lint recipe — that is [yf-change-validation](/skills/yf-change-validation/) — and for checking that already-written docs agree across declared edges, which is [yf-drift-check](/skills/yf-drift-check/). Those are orthogonal axes `/yf-okf` never invokes. `/yf-okf` owns the *shape* of a bundle; the others check its behavior and its cross-edge agreement.

## The bundle shape

Every dir-form bundle carries three structural guarantees:

- a reserved **`index.md`** — a progressive-disclosure listing that replaces a legacy `README.md` or `_index.md`;
- a reserved **`log.md`** — newest-first entries under ISO-8601 date headings, replacing an in-document phase log or decision log;
- **frontmatter with a non-empty `type`** on every non-reserved `.md` file — the one OKF MUST.

Two yoshiko-flow extensions layer on top of the baseline:

- **The dual field model.** Header metadata is written twice from one in-memory model — a YAML frontmatter block (the machine surface) and human-readable `**Field:**` lines. A single writer emits both, so the two can never be authored independently and drift apart. Reads are frontmatter-first with a `**Field:**` fallback, so un-migrated artifacts keep working.
- **The `okf_spec:` member key.** Each non-reserved artifact names the family member it conforms to — `OKF-PLAN`, `OKF-RESEARCH`, or `OKF-INCUBATOR`. The reserved `index.md` and `log.md` carry no `type` and no `okf_spec`; they are structural files, not typed concept documents.

One placement rule ties the model to yf-plan's fingerprint. Both the frontmatter block and the `**Field:**` block sit **above the first `## ` heading**. yf-plan's content fingerprint excludes everything above that heading, so adding frontmatter and relocating a phase log are hash-neutral by construction — migrating an approved plan does not make it stale-approved.

## The OKF-\* family

The ruleset the engine enforces is a composition:

```
OKF-BASELINE  ∪  OKF-YF-EXTENSIONS  ∪  per-skill OKF-EXTENSION.md
```

The BASELINE and YF-EXTENSIONS layers are **baked into the engine** — no cross-skill file read at runtime. Their `spec/` documents are the authored reference, kept in agreement with the baked ruleset by a [yf-drift-check](/skills/yf-drift-check/) edge. Only the per-skill member is resolved at runtime, and it is resolved `__file__`-relative to the running engine — each skill bundles its own `OKF-EXTENSION.md` beside its vendored copy of the engine. Composition therefore runs from any vendored copy, in both the worktree and the installed layout, with no sibling skill required on disk.

## Two survival guarantees

The engine runs over real, messy corpora — including a copy of a live Obsidian vault during impact assessment. Two invariants keep it from doing harm:

- **Merge-and-preserve.** A write adds only yf-owned keys and never drops or overwrites a pre-existing frontmatter key. Foreign frontmatter — Obsidian `tags`, `aliases`, `cssclass` — survives byte-for-byte.
- **Report-only and crash-safe.** `check` and `migrate --dry-run` over unparseable YAML, missing files, or binary content record a finding and continue. A scan of a messy corpus returns a findings report, never a stack trace.

## Behavior model

| Subcommand | Behavior |
| :--- | :--- |
| `init` | Consent-only setup; the skill installs automatically. |
| `check [<dir>]` | Composed-ruleset conformance self-check over a bundle. Report-only — it never mutates the corpus. Exits non-zero when the bundle is not conformant. |
| `migrate <dir> [--dry-run]` | Opt-in, per-folder, in-place migration to the OKF model. `--dry-run` first emits the change plan without touching the folder. |
| `assess <corpus>` | Discover bundles under a root, run `check` and `migrate --dry-run` over each, and produce an aggregate impact report. |

Migration is the only write path, and it is opt-in and per-folder — existing completed folders are grandfathered, never bulk-rewritten. It is also careful about what it preserves. It keeps the content fingerprint stable, carries the first `scoping:` date forward into `log.md` so a downstream grandfather clause still resolves, and assigns each file a `type` from the member's role-to-type map rather than a blanket default — recording any fallback in the change plan so nothing is silently mislabeled.

`/yf-okf` is a beads-free utility skill. It ships no `yf` subcommand of its own; it routes as a skill, on the kernel-versus-skill boundary.
