---
type: Finding
okf_spec: OKF-PLAN
---

# EXP-004 — The escalation mechanism: what exists, what a question must contain, where it is written

## Finding: What escalation mechanism exists today, what must a structured question contain, and where is it written?

### Approach Tested

Read `yf-herdr` `SKILL.md` + `SPEC.md` in full; a **live read-only spike** against the
`herdr` binary including a dump and parse of the full socket API schema (`herdr api schema --json`,
251 KB); measurement of the live session topology via `ps eww` on each agent pid; failure-mode
tests against nonexistent targets only; and a mining of the **actual retrospective corpus** — 81
`## RE-NNN` entries across 11 bundles.

### Result

**measured:** every figure below is reproduced from the commands named inline; **inferred:** claims are marked as such where no command establishes them.

#### Verdict

**A one-hop escalation is implementable today — but only as WRITE-THEN-NOTIFY, never as a
DIALOGUE. The specific gap is that no answer-return primitive exists.**

- `AgentPromptWaitOptions` has exactly two properties — `until: [AgentStatus]` and `timeout_ms`.
  **No message id, no correlation token, no response payload** anywhere in `AgentPromptParams`.
- The `EventMatch` set usable by `events.wait` contains **no metadata event at all**.
  `pane.metadata_updated` does not exist even as a subscription, and no CLI surfaces `events.wait`.
- `--wait --until <status>` observes **the recipient's `agent_status`**, not a reply — and
  `REQ-HERDR-026` forbids it outright, recording it as *measurably wrong* for a claude subordinate.

So a child can **ask** and a parent can **answer**, but the child cannot **block on**, **detect the
arrival of**, or **correlate** an answer. The answer lands as an ordinary injected prompt starting a
**new turn with no link to the question.**

**Design consequence, and it is fundamental: the escalation's durable form must be a WRITTEN BUNDLE
ARTIFACT, and the push is a notification *about* the artifact.** Anything treating the ask as a
request/response round-trip builds a primitive herdr does not have. **Every success criterion
phrased as a round-trip is unachievable against today's herdr.**

**Corroboration that this is the right shape anyway:** 4 of the 11 `stop` entries in the corpus
record an ask whose answer **never arrived** — `answered` reads `PENDING — halted for the operator`,
`(pending)`, `PENDING — presented to the operator; not yet answered`, `PENDING — brought to the
operator; not resolved by the main session`. **The written record survived the un-answered ask. A
message channel would have left nothing.**

*(This independently confirms what escalation E-3 observed live in this session: the ask cost no
stop because it could not block. The non-blocking property is not a design choice — it is the only
available semantics.)*

#### Three channel defects, none of them documented

1. **`herdr agent prompt` exits 0 on `agent_not_found`.** Measured against nonexistent targets:
   `{"error":{"code":"agent_not_found",...}}` with **exit code 0**. A child that shell-tests `$?`
   after a push **reads success on a total delivery failure.** This is the injection-vs-submission
   class the skill already documents, one layer lower, and it is written down nowhere.
2. **The token channel cannot carry a question.** `PaneReportMetadataParams`: keys ≤32 chars matching
   `^[A-Za-z0-9_-]{1,32}$`, a **hard ceiling of 16 keys per pane** (already partly consumed by phase
   stamps), `ttl_ms` ≤ 24h, and the CLI's own description is **"display-only"**. It can carry a
   *flag or pointer* (`esc=raised`) that a parent's poll reads as a mechanical postcondition. It
   cannot carry the question.
3. **A push into a `blocked` parent is swallowed.** `SKILL.md:194-197`. During this experiment the
   live `wK:p1` **was** `blocked` — the state is common, not hypothetical.

#### Session topology, measured — N-hop does not merely lack data, it is NOT REPRESENTABLE

`ps eww` on every claude pid in the live workspace:

```
wK:p1  (root, no YF_PARENT_PANE)      — unrelated
wK:p15 (root, no YF_PARENT_PANE)
  |-- wK:p17  name=bug-268       YF_PARENT_PANE=wK:p15
  +-- wK:p18  name=yf-judgement  YF_PARENT_PANE=wK:p15
```

**Depth 1, fan-out 2. Not one pane in the workspace has a parent that itself has a parent.**

**A child knows EXACTLY ONE THING about its parent: an opaque pane-id string.** No parent name, no
grandparent, no depth counter, no plan identity, no chain, no correlation id. So #264's point 1
(provenance-derived autonomy — *"if `YF_PARENT_PANE` is set, a controller exists"*) **is
implementable today from a one-line env test**; anything requiring *how far up the chain we are* is
not, because **the depth is not representable in what is seeded.** A child spawning a grandchild
would seed `YF_PARENT_PANE` with its **own** pane id, **silently overwriting the chain**.

**The bead graph is NOT the session graph, and this needs saying plainly.** Research 005's
`discovered-from` depth-3 measurement is about **beads** within one bd DAG usually executed by
**one** session. Nothing in a bead records which pane created it; nothing in a pane records which
beads it owns. **A depth-3 `discovered-from` chain is entirely compatible with a depth-0 session
graph — and on this corpus that is exactly what it is.**

`yf-herdr` is **silent on nesting** — neither forbids nor permits. REQ-HERDR-014 (*"at most one
subordinate per plan/research project"*) constrains **breadth per target**, not depth, so the
observed fan-out of 2 is conformant. Nothing prevents a grandchild; nothing contemplates one.

#### The prior art is weaker than research 005 reads, and one citation is a local artifact

**`writing`'s convention — FOUND, and it is n=2 in one repo.**
`writing/docs/plans/plan-005-james-dixson-44ae6f/plan.md:110-118`, resolved in one phase-log line
at `plan.md:13`. A second variant at `plan-007` hardens it into a beads Decision Gate. **It exists
nowhere as a template, schema, skill instruction or rule** — greps over that repo's `CLAUDE.md`,
`AGENTS.md`, `.claude/`, `skills/` and over `~/.claude/skills/yf-plan` return zero. **Purely ad hoc.**

**And its central promise is not kept.** The *"(defaults in brackets)"* defaults were **overwritten
in place** by the `RESOLVED (…)` annotations. **A schema where the answer destroys the question is
not a corpus** — inherit against this, by storing `recommended` separately from `answer`.

**`grilling` — ABSENCE FINDING, and a citation correction.** The skill is **not installed anywhere
on this machine** (searched all four harness roots, `~/.claude/plugins`, all of `~/workspace`). It
exists locally only as uninstalled marketplace catalog metadata. **The G1–G7 numbering does not
exist upstream — it is an invention of research 005's own `cluster-prior-art.md:80-92`.** The two
load-bearing quotes are real and were fetched from `raw.githubusercontent.com`. **Any design citing
"G3/G4/G5" is citing a local paraphrase layer, and this plan does not.**

**So "two independent surfaces converged" is weaker than it reads**: one is 2 ad-hoc instances in
one repo; the other is one author's uninstalled skill file that research 005 itself grades
*"T1-primary for its own content and nothing else … carrying no evidence that the technique works."*

#### The single most important observation: the schema forces the dominant payload OUT of the record

The corpus already holds **81 entries across 11 bundles** — 70 `deviation`, **11 `stop`**. **All 11
stops carry `detected_by: mechanical-check`**, so C3 is already satisfied in practice by the
existing write sites.

But in `plan-047 RE-009` the **drafted alternatives went to a separate file**:

> *"D-13 split gate (Issue 10.0): with 4 review cycles recorded at the end of Epic 5, should
> execution continue into Epics 6-10 or split?"* → `answered: PENDING — halted for the operator.
> The gate exited 1 as designed; the proposal is rendered at **assets/split-proposal.md with three
> options** (split / continue / land-and-pause)."`

**The schema had no field for them, so the dominant payload was written outside the record.** That
payload is T1 — *a selection among alternatives the agent already drafted* — 45/119, the only
category present in all 7 repos. **An escalation that does not carry drafted alternatives is asking
the wrong shape of question, and the existing schema structurally forces that mistake.**

And `plan-047` needed **two entries** (RE-009 raised, RE-010 resolved) to express raise-then-resolve,
because `append_retrospective` is append-only with no update verb.

#### Proposed field list, each justified by a citation

| field | domain | justification |
| :-- | :-- | :-- |
| `id` | `ESC-NNN`, append-only | REQ-PORT-051's `RE-NNN` precedent. **Also the only candidate dedup key that survives a hop.** |
| `question` | free text, verbatim | existing `--asked` semantics (`plan_manager.py:6065`) |
| **`alternatives`** | **enumerated, >= 2** | **the measured gap** — T1 is the dominant input and `plan-047` had to spill three options to `assets/` |
| **`recommended`** | must name one of `alternatives` | the one shape both prior-art artifacts converge on. **Stored separately from `answer`** — `writing`'s defaults were destroyed by their own resolution |
| `evidence` | command + output, or `unverified` | REQ-PORT-052 verbatim: *"a state assertion with no evidence is a narration, not a finding"* |
| `detected_by` | `self-report \| operator \| mechanical-check` | consensus C3; all 11 existing stops are `mechanical-check` |
| `stop_class` | `1`–`5` or empty | reuse SKILL.md's write-site table — **but validate it**; it is currently free text despite a documented closed domain |
| **`on_no_answer`** | free text, **REQUIRED** | direct consequence of the no-answer-path verdict. 4 measured `PENDING` entries where no answer ever came |
| **`state`** | `raised \| answered \| resolved \| withdrawn` | **not currently expressible**; encoded today in ad-hoc `answered` prose |
| `answer` + resolver | verbatim | `plan-047 RE-010` already writes the resolver by hand; REQ-PORT-008's `actor` column is the precedent |
| `asked_of` | pane id or `operator` | the minimum viable N-hop hook; a constant at one hop, free |

**Explicitly NOT proposed: a `stuckness` or `confidence` field.** C3 forbids the agent's
self-assessment as the trigger, and there is no measured trigger to record.

#### Where it is written: a new `escalations.md`, cloning the retrospective activation pattern

| candidate | verdict |
| :-- | :-- |
| `plan-retrospective.md` | closest, but **append-only by contract with no mutation verb**; folding a mutable lifecycle in would break REQ-PORT-051's *"never reused or renumbered"* |
| `log.md` | **reserved** (`okf.py:51-53`), carries no `type`/`okf_spec`, and **REQ-PORT-006 keys a hard count-equality invariant on its `review:` lines** |
| `reviews/pass-N.md` | REQ-PORT-008 *"mutable until resolved, then frozen"* + the REQ-PORT-006 count pin. **An escalation raised outside a review cycle has no pass to live in. Fatal.** |
| `plan.md` frontmatter | cannot hold a list of entries; and a `##` body section **is** hashed, so every escalation would flip the fingerprint and trip REQ-PORT-041 stale-approval mid-execution |

**`scope-answers.md` is the cautionary tale.** Six sections each followed by a bare `**Answer:**` —
no ids, no state, no alternatives, **no TOML schema, no `_INDEX_MEMBERS` entry, no OKF-EXTENSION
type row, no audit awareness**; it falls through to `type: Concept`. **Measured: exactly 1 exists in
the entire 114-bundle corpus.** That is what an un-schema'd bundle-root question file decays into.

**Six mechanical edit sites, all identified in code:** a generator calling `_stamp_okf_type` and
**`_ensure_index_lists_member`** (the latter fixes a *measured* bug — `upstream-triage.md` was
unlisted in 8 of 19 root indexes, *"one systematic producer bug rather than 8 independent
oversights"*); an `OKF-EXTENSION.md` §1 vocabulary row **and** §1a glob row (without which
`_assign_type` falls through to `Concept`, exactly what happened to `scope-answers.md`); an
`_INDEX_MEMBERS` entry; a TOML schema written to **both** `_shared/document_types/` and the vendored
`skills/yf-plan/scripts/document_types/`; **both** `docs/plans/*/` and `Incubator/*/plans/*/` globs;
and **the audit: write nothing** — mirror REQ-PORT-ACT-RETROSPECTIVE's *"added to no audit presence
list"*.

**A schema defect to fix rather than inherit:** `plan-retrospective.toml` has three checks and
**none validates the field set at all**; `--frontloadable` and `--stop-class` are unvalidated free
strings despite documenting closed domains. **An escalation schema whose `recommended` need not name
one of its `alternatives` is not a schema.**

#### Dogfooding evidence (Q5)

**#264's three-boundary experiment is the only verbatim parent-child exchange on record, and it is
not a question — it is a nudge.** Both stalls were resolved by the parent detecting silence via
polling and pushing text *downward*. **Measured: zero upward questions in the entire recorded
exchange.** That is the strongest available support for #264's reframing that the missing behaviour
is *"ask upward"*, not *"don't stop"*.

**What was usable was not the message — it was the token stamp and the artifact.** The parent's one
*wrong* report came from reading `agent_status`: it saw `working`, reported the child had advanced,
and had to correct the record a turn later. **Status is not a message, and a message is not a
record.** Only the token stamp and the written artifact were reliable.

**Live residue this session:** `wK:p18` carries `{"scoping":"done"}`; `wK:p17` carries
`{"draft":"done","investigation":"done","scoping":"done"}`. **No escalation residue in either
pane's tokens, and none in the research-005 bundle** — its `log.md` records 12 phase entries, every
one an *output* report, **not one question**, despite two stalls requiring parent intervention.
**The bundle's own log confirms §8.4's claim on itself.**

**But the plan corpus contradicts §8.4's generalisation.** §8.4's evidence is one `low`-severity
self-observation, and *"no corpus-wide count of recorded-versus-unrecorded questions was ever run."*
This experiment ran one: **81 entries, 11 `stop`-kind with a verbatim `asked` field, all 11
`detected_by: mechanical-check`.** **The counterfactual arm §9.4 says does not exist is 11 rows deep
and growing** — on a surface the study did not read, landed for a different reason by plan-045.

#### Absence findings

1. **⚠️ No answer-return path.** Restated here as the headline absence: one-hop escalation today is
   **fire-and-forget**. Every question must ship `on_no_answer`.
2. **`herdr agent prompt` exits 0 on `agent_not_found`** — undocumented silent-failure channel
   underneath the whole design.
3. **The token channel cannot carry a question** — 16 keys, 32 chars, display-only.
4. **A child knows one opaque pane id.** N-hop state is **not representable**.
5. **`grilling` is not installed and was never read locally**; its G-numbering is a research-005
   artifact.
6. **`writing`'s convention is n=2, unwritten as a template, and its defaults promise is not kept.**
7. **`plan-retrospective.md` has no lifecycle and no update verb.**
8. **The existing schema has no field for drafted alternatives** — measured to have pushed
   `plan-047`'s three options out to `assets/`.
9. **`--frontloadable` / `--stop-class` unvalidated**; `plan-retrospective.toml` validates no field.
10. **`SKILL.md:185` narrows `REQ-HERDR-024` to the `blocked` arrival path only.** The REQ governs
    *any* subordinate question; **a pushed question has no SKILL.md decision procedure.**
11. **A measured spec/corpus contradiction.** `plan-049 RE-002` records `stop_class: 1`, while
    `SKILL.md:1897` states *"stop class 1 has NO write site, and that is the whole of the
    exclusion"*. One is wrong — and **a `yf-judgement` consumer mining for "stops to frontload"
    would read that row and propose removing a designed consent gate**, the exact failure
    `SKILL.md:1902-1904` warns of.
12. **Recall never measured; no counterfactual arm** — though the second premise is now *partly
    falsified* by the 11-entry stop corpus above.

### Implications for Plan

**The plan must be scoped as "write the escalation, notify about it" and NOT as "ask and await."**
The awaiting primitive does not exist; **any success criterion phrased as a round-trip is
unachievable against today's herdr.**

**The cheapest, highest-value deliverable is a schema, not a detector.**

**The one-hop / N-hop split is cleanly enforceable at the artifact boundary**: ship `id` + `asked_of`
now (free), ship no hop counter (unmeasurable), and N-hop becomes additive rather than a redesign.

**The propagation budget is free** if escalations ride `REQ-HERDR-026`'s existing three triggers.

### Recommendations

1. **Ship one-hop as `escalations.md`** — presence-optional, `type: Escalation`, cloning
   REQ-PORT-ACT-RETROSPECTIVE's activation pattern verbatim, with the six mechanical edit sites.
2. **Fields:** `id`, `question`, `alternatives` (>=2), `recommended` (must name one), `evidence`,
   `detected_by`, `stop_class`, `on_no_answer` (required), `state`, `answer` + resolver, `asked_of`.
3. **Allow mutation** — which is why this must be a new file rather than a retrospective entry kind.
4. **The push is one line naming the artifact**, batched to the three existing classes, paired with a
   token stamp, never `--wait`.
5. **Amend `yf-herdr` SPEC-first** with three narrow additions.
6. **Label N-hop an explicit bet**, citing the measured depth-1 topology as the reason it is deferred.
7. **Instrument the cost ratio** — the `escalations.md` corpus is that instrument.
