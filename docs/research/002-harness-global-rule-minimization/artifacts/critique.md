---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Red-Team Critique — 002-harness-global-rule-minimization

Adversarial review of `Summary.md`, evaluated on its own merits against `sources.json`.
Citation anchors were checked: all 39 `### S-XX` headings in `sources.md` produce the
lowercase GitHub anchors (`#s-cc-2` etc.) the Summary links to, and every source ID cited in
the report exists in both `sources.md` and `sources.json`. No broken anchors.

Priority key: **BLOCKING** (must fix before packaging) · **RECOMMENDED** · **MINOR**.

---

## BLOCKING

### B1 — The core "irreducible" verdicts rest on the subject artifact's own self-assertion, uncorroborated

The load-bearing verdicts — PLANS/RESEARCH are "Irreducible everywhere" because "the built-in
is compiled into the CLI," and the two bd mandates are irreducible because "no single skill
owns them" — are cited **only to S-LC-1**, which is `YOSHIKO_FLOW.md` itself: the very
artifact whose minimizability the research question asks about. This is circular. The report
repeatedly frames these as "corroborated by Claude Code docs [S-CC-3]/[S-CC-2]," but the
first-party corroboration covers **only** the narrow point that a description is *probabilistic
and truncatable* (S-CC-2, S-CC-3). No cited source independently confirms (a) that native plan
mode / the deep-research harness are compiled-in and cannot be overridden by a skill
description, or (b) that a cross-cutting mandate has no possible skill home. Those premises are
purely the local rule's self-description.

Locations: Executive summary; Q4 table rows 1–2 (lines 202–203); Minimization verdict item 2
(lines 307–309); the Q3 verdict table PLANS/RESEARCH/bd rows (lines 178–181).

Fix: soften "Irreducible everywhere" / "Irreducible" to something like "irreducible **per the
local rules' own design rationale** — self-asserted (S-LC-1), not independently corroborated;
the first-party corroboration [S-CC-2, S-CC-3] establishes only that descriptions are
probabilistic, not that these specific mechanisms are un-overridable." Add this limitation
explicitly to the "Answerable vs. open" paragraph.

### B2 — Pi's always-loaded rules mechanism is stated as fact but rests only on questionable-tier sources

The claim that Pi loads an always-loaded `AGENTS.md` concatenated from `~/.pi/agent/AGENTS.md`
+ parent dirs + cwd (Q2 table Pi row, line 140; Q6 lines 244–249) is cited to **S-PI-4
(score 58, `questionable`)** and **S-PI-6 (score 54, `questionable`)**. No first-party Pi
source attests the AGENTS.md loading mechanism — S-PI-1 (pi.dev homepage) does not cover it,
and S-PI-3 (the one `high_trust` Pi source, 80) covers **skills**, not the rules surface. Per
the triangulator rubric, a claim resting only on `questionable` sources must carry an
`[uncertain]` tag; this one does not.

Compounding it, the **Executive summary** (lines 19–20) cites **S-PI-6 (questionable, 54)** as
the Pi leg of the headline "all four harnesses … the same two-tier architecture holds … the
strongest and most portable finding." The strongest finding in the corpus should not have its
Pi leg anchored to a personal config repo.

Fix: (1) tag the Pi rules-surface mechanism `[uncertain]` and state explicitly it rests on
`questionable`-tier community sources only, no first-party attestation; (2) in the exec
summary, cite the `high_trust` first-party S-PI-3 for the Pi *skills* half of the split and
make clear the Pi *rules* half is the weakly-sourced half.

---

## RECOMMENDED

### R1 — "No settings key fires a skill" is an absence/inference but is cited as if direct

Lines 47 and 318 state "there is no settings key that fires a skill" citing S-CC-2, presenting
an **absence** as a positively-cited fact. Line 113 correctly frames the same claim as "cluster
synthesis of [S-CC-1], [S-CC-2]" — an inference. Make it consistent: everywhere, frame this as
an inference/absence finding ("no cited source describes a settings key that supplies a skill
trigger"), not a direct citation of S-CC-2, whose quote is about `paths` frontmatter.

### R2 — Settings keys `todoFeatureEnabled` / `disableWorkflows` are attested only by the local doc, not first-party

The Q2 Claude Code config row (line 137) and Q1 (line 103) cite **S-CC-1** alongside S-LC-5 for
keys including `todoFeatureEnabled`, `disableWorkflows`, `permissions.deny`. But S-CC-1's
captured snippet/quote enumerates `disableBundledSkills, skillOverrides,
disableSkillShellExecution, claudeMd, claudeMdExcludes, autoMemoryEnabled` — it does **not**
include `todoFeatureEnabled` or `disableWorkflows`. Those two keys are attested only by
S-LC-5, the operator's own recommended-settings doc, which could be aspirational.
(`skillListingBudgetFraction` is fine — it is in S-CC-2's snippet.) Either drop the S-CC-1
citation for those specific keys or flag that their existence is attested only by the local
baseline and not verified against first-party settings docs.

### R3 — Cross-harness absence claims are cited to Claude-Code sources

The "no attested codex/opencode/pi analog" / "unattested elsewhere" claims (exec summary line
41; Q3 table CHANGE-VALIDATION/DRIFT-CHECK/INSTRUCTIONS rows lines 182–186) cite S-CC-2 /
S-CC-4 — Claude Code docs — to support a statement about what Codex/opencode/Pi *lack*. A CC
doc cannot attest an absence in another harness. Reframe these as pure absence findings ("0
sources attest a path-glob or on-edit-hook mechanism for Codex/opencode/Pi"), without hanging
a CC citation on the negative.

### R4 — Exec-summary superlatives slightly over-claim given the Pi leg's weakness

"Every independent retrieval cluster corroborated this split, making it the strongest and most
portable finding" (lines 19–21) overstates, because the Pi cluster's corroboration is
`questionable`-tier (see B2) and the opencode/Codex/CC legs are `verify`/`high_trust` while Pi
is not. Soften to "corroborated across all four clusters, strongest for Claude Code, Codex, and
opencode (first-party); the Pi leg is the weakest-sourced."

---

## MINOR

### M1 — Acknowledge the self-study bias of the local (S-LC-*) sources

All eight S-LC-* sources score `bias_neutrality: 55` and are the operator's own files — the
same corpus the research is deciding whether to minimize. This is inherent and unavoidable, but
the report should name it once in a limitations note: the primary evidence for *what is
irreducible in yf* is yf describing itself. (Related to B1 but broader.)

### M2 — Composite citation on the "read by all five" portability claim

Line 272 ("one file is read … by Claude Code, Codex, opencode, Pi, and Copilot") cites only
S-PI-7, S-PI-12, S-PI-10, none of which is the per-harness source establishing each harness
reads AGENTS.md. Those per-harness sources (S-CC-3, S-CX-1, S-OC-1, S-PI-4) are cited
elsewhere; add them inline here so the composite claim is traceable at the point of assertion.

### M3 — UPSTREAM_TRACKING "close-event hook not attested" is honestly bounded — keep it

The Q3 UPSTREAM_TRACKING row (line 185) and the Hooks handling correctly limit the verdict to
the attested hook set (S-CC-4 lists `FileChanged`, `InstructionsLoaded`, `PreToolUse`) and say
a close-event hook is "not attested" rather than "impossible." This is the right epistemic
posture — no change needed. Optionally note that the hook list retrieved may be non-exhaustive,
so "Irreducible (as trigger)" for UPSTREAM_TRACKING is contingent on the retrieved hook set.

---

## Net assessment

The report is **substantially sound** in structure, cites nearly every claim inline, backs its
novel Claude-Code claims with direct quotes from `verify`/`high_trust` first-party docs, and is
commendably honest about the two genuine absence findings (Pi trigger semantics, quantitative
token cost). Its Claude-Code minimization analysis (paths/hooks/settings) is well-evidenced.
The weaknesses are two: (B1) the irreducibility verdicts that anchor the whole "irreducible
core" thesis lean on the subject artifact's self-description without independent corroboration,
and (B2) the Pi leg of the flagship cross-harness claim rests on `questionable`-tier sources
without the required `[uncertain]` tag. Neither is fatal — both are addressable by softening
over-claims and adding uncertainty tags, not by new retrieval. No fabricated citations, no
broken anchors, no obvious model-knowledge leakage.
