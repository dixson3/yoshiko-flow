# VOICE.md — house voice for yoshiko-flow docs

## Purpose and scope

This file is the voice contract for every human-facing prose surface in the repo:
`web/content/**`, READMEs, and the exposition inside a skill's `SKILL.md`. It is repo-owned
and read at drafting time by any human or agent that writes or rewrites that prose — the same
"approved manifest at the repo root" pattern `yf-drift-check` and `yf-change-validation` use.

It does **not** govern code, code comments, bead titles/bodies, or commit and PR text.

**Reader:** an engineer or operator adopting the tool — someone who wants the precise mechanism
and the exact command, not a pitch. Write for that reader; do not pitch to an executive.

The in-repo exemplars already in register are [`web/content/pages/why.md`](web/content/pages/why.md)
and [`web/content/pages/architecture.md`](web/content/pages/architecture.md). When in doubt,
match them.

## House voice

- **Matter-of-fact and precise.** State the mechanism, then its consequence. No hype, no
  sycophancy (inherits the global "no sycophantic language, to-the-point" tone floor).
- **Lead with the substance.** A bolded lead-in phrase can carry a bullet or open a paragraph,
  as `why.md` does ("**yoshiko-flow is a bet that…**").
- **Concrete over abstract.** Name the file, the command, the count. Write "`yf` ships 18 skills,"
  not "many skills."
- **Second person for the reader's actions.** "Run `/yf-plan execute` in a new session, and the
  coordinator resolves the start gate before touching the DAG."
- **Payoff after setup.** State the mechanism before the verdict or benefit line, never the
  reverse.

## Density and exposition

This is the load-bearing section. The failure mode in these docs is not thin writing — it is a
dense paragraph that stacks four ideas behind semicolons and colons. The fix is always the same:
**more exposition, not more density.** Expand by adding a worked example, a list, a table, or a
diagram — never by packing more into a sentence.

- **One idea per sentence.** A sentence that stacks clauses behind a colon or semicolon becomes
  short sequential sentences. Prefer a period to a third em dash.
- **Break walls of prose.** Convert to a list when a paragraph runs past roughly four or five
  sentences, or whenever it enumerates a set — steps, options, or components.

  | Content shape                                  | Use              |
  | :--------------------------------------------- | :--------------- |
  | An ordered sequence of steps                   | numbered list    |
  | An unordered set of items or options           | bullet list      |
  | Keyed or comparative data (term→def, opt→effect) | table          |
  | A structural or flow relationship              | diagram          |

- **Prefer a table** when the content is comparative or keyed. The skill-grouping list in
  `architecture.md` is the in-repo model for keyed content.
- **Prefer a diagram** for structure or flow. Render an image (the repo has `yf-diagram-authoring`
  / d2 for this) with alt text and a caption. Cap it at one `![…](…)` per major page section.
- **Payoff after setup.** Give the reader the mechanism before the conclusion that depends on it.

## Do / Don't

- **Do** open with the substance, and use bold lead-ins, bullets, and tables freely.
- **Do** gloss a technical term on first use, then use it precisely. Keep the term — do not
  replace it with a vaguer plain-language stand-in.
- **Don't** throat-clear. No "In this section we will…", "It's worth noting that…", or "Now the
  interesting part."
- **Don't** narrate the document's own structure. No "as we saw above" or "the rest of this page
  covers…". (Anti-meta-narration is a hard rule: say the thing, do not announce that you are
  about to say it.)
- **Don't** use marketing or filler words: "powerful", "seamless", "robust", "simply", "just",
  "easily".
- **Don't** write a paragraph where a list, table, or diagram is clearer.

## Before / after

### 1. One idea per sentence (from `why.md`)

**Before** — three clauses stacked behind semicolons and an interrupting em-dash pair:

> It spans days, environments, and people; it needs to be investigated before it's committed to;
> and it should leave durable artifacts a teammate — or a future you — can pick up.

**After** — a lead sentence, then the three properties as bullets:

> Real work spans days, environments, and people. Three things follow:
>
> - it must be investigated before it is committed to;
> - it must leave durable artifacts a teammate, or a future you, can pick up;
> - it must survive the end of any one session.

### 2. Colon-chain of steps → numbered list (from `workflows.md`, RECONCILE)

**Before** — an ordered procedure buried in one colon-chained sentence:

> The order is merge-back first, then validate the merged state, then push: acquire the landing
> lock, merge `<plan-id>-execute` into the pinned target with `--no-ff`, run the cross-plan
> `validate-merged` safety net, and only on pass commit the merge and release the lock.

**After** — the ordered steps as an ordered list:

> RECONCILE lands the branch in a fixed order:
>
> 1. Acquire the landing lock.
> 2. Merge `<plan-id>-execute` into the pinned target with `--no-ff`.
> 3. Run the cross-plan `validate-merged` safety net.
> 4. On pass, commit the merge and release the lock.

### 3. Prose enumeration → table (from `architecture.md`, embedded skills)

**Before** — a keyed set flattened into a sentence:

> The 18 skills fall into four install groups: workflows has 3 end-to-end skills, beads has the
> 5 `bd` support skills, utility has 6 beads-free helpers, and markdown has 4 GFM tools.

**After** — the same keyed data as a table:

> `yf` ships 18 skills in four install groups:
>
> | Group     | Count | What it is                          |
> | --------- | ----- | ----------------------------------- |
> | workflows | 3     | end-to-end, beads-tracked skills    |
> | beads     | 5     | the `bd` support layer they build on |
> | utility   | 6     | beads-free helpers                  |
> | markdown  | 4     | standalone GFM tooling              |

## Mini-glossary

Load-bearing terms, glossed once. Use the term precisely thereafter; do not replace it. The
canonical, fuller list lives in [`web/content/pages/glossary.md`](web/content/pages/glossary.md).

| Term          | Gloss                                                                        |
| :------------ | :--------------------------------------------------------------------------- |
| bead          | one tracked issue in the `bd` (beads) database, versioned next to the code   |
| gate          | a dependency edge that blocks work until a condition (e.g. a platform) holds |
| fingerprint   | a content hash over a plan's reviewed sections that binds approval to them   |
| preflight     | the shared readiness check `yf` runs before any beads-backed skill acts      |
| land-the-plane | the close-out step that validates, merges, and pushes deferred work         |
