---
type: Finding
okf_spec: OKF-PLAN
---
## Finding: EXP-04 blog-voice adaptation

EXP verdict: `blog-voice` **exists and is mature** in `~/workspace/dixson3/writing`. Its
architecture (repo-owned `VOICE.md` + `AUDIENCE.md`, read at trigger time) is a clean template,
but its *content* is essay/op-ed-specific. yoshiko-flow needs a **docs/technical VOICE.md**, not a
direct copy. A local voice SKILL is **not warranted now** — author `VOICE.md` first.

### What blog-voice provides (cited, paths in `~/workspace/dixson3/writing`)

The skill is a repo-scoped, multi-agent editorial pipeline that reads voice/audience from the git
root rather than hard-coding them — the same "manifest at repo root" pattern yoshiko-flow's own
`yf-drift-check` / `yf-change-validation` use.

- `VOICE.md` (repo root, 7.4 KB) — the canonical voice reference. Structure:
  - **How the author argues (patterns to preserve)** — first-principles→verdict, analogy-as-argument,
    historical/economic framing, named incentives, systems-over-silos, owned (once) hedging,
    builder's pragmatism.
  - **Register / mechanics** — short declaratives next to long reasoning runs; concrete numbers as
    rhetoric; prefer the concrete mechanism to the slogan.
  - **Readability (flow & density)** — the section most relevant to this plan: *unpack dense
    sentences (one idea per sentence)*, *cut interrupting mid-sentence hedges*, *staccato must earn
    its interruption*, *payoff after setup*, *watch odd punctuation beats (colon-chains, semicolon
    pileups)*.
  - **Do / Don't** — concrete anti-patterns: no throat-clearing meta-exposition ("Now the
    uncomfortable part…"), no "it's worth X-ing because Y" self-narration, no pre-empting the
    reader's objection, no narrating the essay's own architecture, no announcing your own conviction
    ("make no mistake").
- `AUDIENCE.md` (repo root, 3.5 KB) — deliberately split from voice: **The reader** (persona),
  **Register** (Atlantic/WSJ op-ed, plainspoken, dry), **Loosen for the reader (density)** — "one
  idea per sentence, prefer a period to a third em dash, unpack analogies", a **De-jargon table**
  (insider term → plain replacement), and a **Figure text** convention (alt vs. title).
- `.claude/skills/blog-voice/SKILL.md` + `README.md` — stage-gates mapped to essay `status:`
  (`idea`/`draft`/`review`/`ready`), a Preflight (`harper-cli`, `naba` soft deps), and a **Bounded
  write authority** section (reviews report; caller applies; preserve-wins; auto-apply only exact
  de-jargon-table matches).
- `.claude/skills/blog-voice/agents/*.md` — 11 read-only EVALUATE agents. The two directly reusable
  for a docs context:
  - `agents/voice-stylist.md` — checks jargon, snobbery, density-as-voice-loss, voice-loss; reports
    findings with concrete plain-language rewrites. **Read-only, reports; caller applies.**
  - `agents/readability-critic.md` — the **mechanical/measurable** axis: sentence length,
    punctuation-beat density (counts em-dashes/colons/semicolons), overpacked sentences, buried
    callouts / payoff position. Explicitly separated from voice-stylist by a "Boundary" section.
  - Others (`red-team`, `cold-read`, `curmudgeon`, `steelman-response`, `fact-checker`, `footnoter`,
    `illustrator`, `grammar-check`) are essay/argument/publishing-specific and **out of scope** for
    docs.

### Reusable vs blog-specific

**Reusable (structure and mechanics):**
- The **repo-root manifest pattern** (`VOICE.md` at git root, read at trigger time) — matches
  yoshiko-flow's existing convention.
- The **voice ÷ audience split** — "how we write" vs. "who reads and how to pitch to them".
- The **Readability (flow & density) section wholesale** — one-idea-per-sentence, cut mid-sentence
  hedges, payoff-after-setup, watch punctuation beats. This is directly the operator's density goal.
- The **Do/Don't anti-meta-narration list** — no throat-clearing, no self-narration, no announcing
  conviction. Aligns with `~/.claude/CLAUDE.md` "no sycophantic language, matter-of-fact".
- The **voice-stylist / readability-critic split** as a future agent model (mechanical vs. register).
- The **bounded-write / report-then-apply** discipline.

**Blog-specific (do NOT port):**
- The op-ed persona (Atlantic/WSJ senior-business-leader reader). yoshiko-flow docs address
  **engineers/operators adopting a tool**, not executives being persuaded.
- "How the author argues" (first-principles→verdict, blunt verdicts, analogy-as-argument,
  historical framing) — that is an *essayist's* rhetorical stance, wrong for reference docs.
- The whole essay lifecycle (`status:` stage-gates, illustrator/`naba`, footnoter/citations,
  curmudgeon/steelman adversarial pair, blog-artifacts). Docs have no publish pipeline.
- The de-jargon table's specific rows (they translate AI-insider terms for executives; yoshiko-flow
  docs *want* precise technical terms, glossed once).

**Cross-reference — yoshiko-flow's house voice already exists implicitly and is good.** The `web/`
prose (`web/content/pages/why.md`, `architecture.md`) already demonstrates the target style:
matter-of-fact, bold lead-in phrases, short sections, **bullet lists over dense paragraphs**, tables
(`architecture.md` skill grouping), one diagram embed. `~/.claude/CLAUDE.md` supplies the tone floor
(no sycophancy, to-the-point). The repo `AGENTS.md` supplies SPEC-first / precision discipline but no
prose-voice section. So VOICE.md's job is to **codify the good tone the web pages already exhibit**
plus make the operator's density/exposition/tables/diagrams goal explicit and checkable.

### Recommended VOICE.md shape for yoshiko-flow

Author a **technical-docs variant** at repo root `VOICE.md`. Concrete outline:

1. **Purpose / scope** (3–4 lines). What VOICE.md governs (repo docs, `web/content/**`, READMEs,
   skill exposition) and what it does not (code comments, bd/commit text). Note it is repo-owned and
   read by any future voice tooling — mirror the `blog-voice` framing line.

2. **House voice (patterns to keep).** The docs analogue of "how the author argues":
   - Matter-of-fact and precise; state the mechanism, then the consequence. No hype, no sycophancy
     (inherits `~/.claude/CLAUDE.md`).
   - Lead with the substance; a bolded lead-in phrase can carry a bullet (as `why.md` does).
   - Concrete over abstract: name the file, the command, the count. "`yf` ships 18 skills," not
     "many skills."
   - Second person for the reader's actions ("push the repo, and someone… picks up").

3. **Density & exposition (the operator's goal — the load-bearing section).** Port the blog-voice
   Readability section, retargeted:
   - **One idea per sentence.** Unpack a sentence that stacks clauses behind a colon/semicolon into
     short sequential sentences. Prefer a period to a third em dash.
   - **Break walls of prose.** A paragraph over ~4–5 sentences, or any enumerable set (steps,
     options, components), becomes a **bullet or numbered list**.
   - **Prefer a table** when the content is comparative or keyed (term→definition, skill→group,
     option→effect). Cite `architecture.md`'s skill-grouping table as the exemplar.
   - **Prefer a diagram** for structural/flow relationships; embed a rendered image (yoshiko-flow has
     `yf-diagram-authoring` / d2 for this) with alt + caption. One `![…](…)` per major page section
     max.
   - **More exposition, not more density.** Expand by adding a worked example, a table, or a diagram —
     not by packing more into each sentence.
   - **Payoff after setup.** State the mechanism before the verdict/benefit line.

4. **Do / Don't** (port + retarget the anti-meta-narration list):
   - **Do** open with the substance; use bold lead-ins, bullets, and tables freely.
   - **Do** gloss a technical term on first use, then use it precisely (keep the term — unlike the
     blog de-jargon table which *replaces* it).
   - **Don't** throat-clear ("In this section we will…", "It's worth noting that…", "Now the
     interesting part").
   - **Don't** narrate the document's own structure ("as we saw above", "the rest of this page").
   - **Don't** use sycophantic or marketing filler ("powerful", "seamless", "simply", "just").
   - **Don't** write a wall of paragraph where a list/table/diagram is clearer.

5. **Before / after examples** (2–3 short pairs — the most actionable part for a drafting agent):
   - *Dense paragraph → bullet list* (take a 5-clause sentence, show the 4-bullet rewrite).
   - *Prose enumeration → table* (comparative sentence → 2-column table).
   - *Throat-clearing open → substance-first open.*
   Keep them tiny and concrete; a drafting agent pattern-matches these.

6. **Optional: a thin de-glossary** (term → one-line gloss) — NOT a replace-table. Keeps precise
   terms but ensures each is defined once. Can defer to the existing `web/content/pages/glossary.md`.

This outline is enough for a drafting agent to author VOICE.md end-to-end. Source most sections by
porting `writing/VOICE.md` §Readability and §Do/Don't and `writing/AUDIENCE.md` §"Loosen for the
reader (density)", retargeted from op-ed→technical-docs.

### Local voice skill: now or future?

**Future, not now.** Rationale:
- A `VOICE.md` alone is inert-but-useful: it is a reference a human or any drafting agent reads. It
  delivers the operator's goal (actionable density/exposition rules) with zero skill infrastructure.
- `blog-voice` is heavy (11 agents, `harper-cli`/`naba` deps, a lifecycle) and most of that
  machinery is essay/publishing-specific and irrelevant to docs.
- A future `yf-voice` hoist is justified **only if** an on-edit trigger is wanted (e.g. lint prose
  in `web/content/**` on save, like `yf-markdown-lint`). If pursued, the reusable core is exactly two
  agents — a `voice-stylist` (register/voice-loss) and a `readability-critic` (mechanical density) —
  plus the repo-root `VOICE.md` manifest and the report-then-apply bounded-write discipline. That is
  a clean, small skill, but it is a **later** plan, not this one.
- Precedent in-repo: `yf-drift-check` / `yf-change-validation` show the "approved repo-root manifest,
  silent no-op otherwise, on-edit trigger" shape a future `yf-voice` would follow. Reuse that shape
  when/if hoisted.

### Implications for Plan

- Plan-035 should produce a **repo-root `VOICE.md`** as a deliverable, authored from the outline
  above (a docs/technical variant, not a copy of `writing/VOICE.md`).
- Optionally add a companion `AUDIENCE.md`-lite section *inside* VOICE.md (reader = engineer/operator
  adopting the tool) rather than a separate file — the docs audience is singular, so the blog's
  voice/audience file split is over-engineering here. One `VOICE.md` suffices.
- Do **not** scope a `yf-voice` skill into this plan. File a follow-on bead for the future hoist if
  on-edit voice-linting is later desired (narrow signal: prose-only globs under `web/content/**`).
- The existing `web/` pages are the **de-facto style corpus** — reference `why.md` and
  `architecture.md` as exemplars in VOICE.md, and treat them as the "already in register" baseline.
- If a density/exposition pass over existing docs is in scope, use VOICE.md's before/after patterns
  as the checklist; the `web/` pages are already largely conformant, so the pass is light.

### Recommendations

1. Author repo-root `VOICE.md` as a **technical-docs variant** using the §"Recommended VOICE.md
   shape" outline. Port `writing/VOICE.md` §Readability + §Do/Don't and `writing/AUDIENCE.md`
   §density, retargeting op-ed → reference-docs.
2. Make the density goal **actionable and checkable**: one-idea-per-sentence, list/table/diagram
   thresholds, and 2–3 tiny before/after pairs. That is the single most valuable content for a
   drafting agent.
3. Fold audience into a short section of VOICE.md (engineer/operator reader); skip a separate
   `AUDIENCE.md` — the docs audience is singular.
4. Reference `web/content/pages/why.md` and `architecture.md` as in-repo exemplars.
5. Defer any `yf-voice` skill to a future plan; file a follow-on bead only if on-edit voice-linting
   is later wanted, reusing the `yf-drift-check` manifest/trigger shape and the two reusable agents
   (`voice-stylist`, `readability-critic`).
