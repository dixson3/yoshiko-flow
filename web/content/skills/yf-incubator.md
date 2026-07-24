`/yf-incubator` gives exploratory research a place to pause and resume. It creates, forks, bookmarks, resumes, and triages long-lived topics — "incubators" — that live as portable markdown files under an `Incubator/` tree. The unit of pause and resume is the **topic**, not the session. Resuming a session means reconstructing scattered context; a topic carries its own state, so you can walk away and pick it up later — on another day, in another harness, on another machine.

## When it fires

Reach for `/yf-incubator` when you want to park or resume an investigation:

- starting a new investigation mid-conversation;
- a conversation descending into a sidequest off its main topic;
- a signal that you are walking away, pausing, or stopping a topic;
- asking what incubators exist or which to work next;
- resuming a parked topic.

Skip it for beads-tracked, multi-step build planning — that is [yf-plan](/skills/yf-plan/) — and for routine note edits with no park-or-resume intent.

It also watches for tangents. When a conversation descends into a substantive sidequest off its main topic, the skill offers **once** to fork that tangent into its own incubator, and proceeds only if you confirm — one offer per tangent, no nagging. That detection is driven from `AGENTS.md`, so it fires even when the skill is not pre-loaded.

## What an incubator is

An incubator is a directory (or a single file) under `Incubator/` whose state file holds YAML frontmatter plus a standard, ordered body. The body sections appear verbatim and in order:

`## Resume` · `## Status` · `## Premise` · `## Open questions` · `## Decision log` · `## Files` · `## Beads to file`

Two of them are load-bearing and never dropped, even when empty:

- **`## Decision log`** — a first-class, append-only record of what was decided and why.
- **`## Beads to file`** — the incubation-to-build hand-off: bead stubs ready for `bd create`, kept human-readable until you file them.

The one section the skill adds on top of the surveyed vault convention is **`## Resume`**. It consolidates into a single predictable block what the best hand-rolled resume notes scatter across "next steps", "beads to file", and "open invitation". A `## Resume` block lets a cold reader — or another harness, on another machine — continue with a concrete next action plus the exact files to re-read under "Context to reload", with no session history.

All state lives in vault files. Nothing is kept in session-only or Claude-only stores, so an incubator is portable across harnesses by construction.

## Subcommands

| Command | Effect |
| :--- | :--- |
| `/yf-incubator new <name> [seed notes]` | Create a fresh incubator and set it active. |
| `/yf-incubator fork <name>` | Fork the current sidequest into a new incubator and set it active. |
| `/yf-incubator bookmark [notes]` | Rewrite the active incubator's `## Resume` and bump `last_reviewed`. |
| `/yf-incubator resume <name>` | Load the bookmark and named context files, set active. |
| `/yf-incubator list` | Index every incubator by state and staleness. |
| `/yf-incubator touch <name>` | Bump `last_reviewed` only, for triage. |

**Bookmarking is deliberate, not automatic.** `bookmark` fires only on a departure signal or a phase boundary — never every turn, and never through a hook. The trade-off is explicit: a turn killed mid-write loses only that turn's delta, in exchange for no per-turn churn and no surprise writes.

**Forking records provenance.** `fork` additionally notes, in `## Status`, the originating main topic, why it was forked, and the context produced so far — so the tangent is not lost.

## Triage without mutation

`list` runs the `incubator-index.py` helper over the whole `Incubator/` tree. An entry is classified **managed** only when its frontmatter carries both `status` and `last_reviewed`; everything else is **unmanaged**. Managed incubators sort by priority rank (`high` before `normal` before `low`), then stalest-first within a band. Unmanaged entries are listed with a reason — and never mutated. A pre-existing, hand-made incubator shows up in the index untouched; it is retrofitted to the schema only when you next actively work it, never bulk-rewritten on a `list`.

`status` is the maturity ladder actually used in the vault:

`incubating → scoping → exploring → converging → concluded`

plus `parked` (deliberately paused) and `abandoned`.

## Where it hands off

An incubator holds research state, not an execution DAG. When the parked thinking is ready to become work, `## Beads to file` routes to the beads skills — `bd create`, dependency edges per the direct-CLI conventions — or to [yf-plan](/skills/yf-plan/) for a full plan-and-execute DAG. The stubs stay human-readable until that hand-off. This keeps one durable task system (beads) and one research-parking surface, without one masquerading as the other.

`/yf-incubator` is a beads-free utility skill. It has no companion rule and stores no runtime state of its own — every durable thing is the per-incubator markdown under `Incubator/`.
