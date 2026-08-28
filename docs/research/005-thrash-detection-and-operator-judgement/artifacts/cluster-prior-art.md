---
type: Research Artifact
okf_spec: OKF-RESEARCH
---
# Cluster: prior-art

Retriever cluster for yf-research project 005 (thrash-detection-and-operator-judgement). This is
the sole web/external cluster; every other cluster mines the local corpus. All work here is
web/GitHub retrieval — nothing in this repository was modified.

Sources are cited `[N]` against `artifacts/sources-prior-art.json` (ids `601`–`623`).

## 0. Method

Providers used: `gh api` / `curl` against `raw.githubusercontent.com` for the two named GitHub
targets (verbatim, no HTML scraping); `mcp__exa__web_search_advanced_exa` for literature and
GitHub-tool discovery (search areas 1–4); `mcp__exa__crawling_exa` for full-content reads of the
strongest hits. No WebFetch/WebSearch fallback was needed — exa and `gh` answered every query.

One provider correction: the task brief suggested `category:"research paper"` and `type:"neural"`
for exa's advanced search; the live tool schema does not have those enum values (`category` is
one of `company|publication|news|pdf|github|personal site|people|financial report`; `type` is
`auto|fast|instant`). Substituted `category:"pdf"` (catches arXiv/ACL PDFs effectively) and
`type:"auto"`, and `category:"github"` for area 4. Recorded here per the epistemic-rules
requirement to log method deviations, not silently paper over them.

Queries run (verbatim):

1. `clarifying question generation ambiguity detection large language model when to ask vs act underspecified task` (category:pdf)
2. `agent trajectory looping detection stuck state repetition non-progress LLM agent thrashing oscillation` (category:pdf)
3. `requirements elicitation question taxonomy underspecification requirements engineering interview framework` (category:pdf)
4. `claude code skill interrogate user before planning ask clarifying questions before coding agent` (category:github)
5. `interruption cost human computer interaction notification timing task switching cost theory` (default)
6. `coding agent harness detects repeated failed attempts asks user for help escalation Devin Cursor Claude Code` (default)

Plus direct `gh api repos/<owner>/<repo>/contents/...` traversal of the two named target repos.

---

## 1. grill-me / grilling — verbatim move catalogue

`grill-me` (user-invoked, `disable-model-invocation: true`) is a one-line stub:

> "Call the Skill tool with \"grilling\"." [1]

The actual engine is `grilling` (model-invocable). Full verbatim text, fetched from
`raw.githubusercontent.com/mattpocock/skills/main/skills/productivity/grilling/SKILL.md` [2]:

> "Interview the user relentlessly until you reach a shared understanding. Map this as a **design
> tree**: every decision branches into the decisions that hang off it."
>
> "Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already
> settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask
> the whole frontier in one round: number each question and give your recommended answer. Then
> wait for the user's answers before the next round." [2]
>
> "Each round the user answers reshapes the tree: settled decisions push the frontier outward and
> unblock questions that depended on them. Recompute the frontier and ask the next round. A
> question whose answer depends on another question still open in this round belongs to a _later_
> round, not this one." [2]
>
> "Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the
> environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for
> anything you could look up yourself. Don't block on it: a running exploration is an unsettled
> prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the
> rest of the frontier now. The _decisions_ are the user's: put each to them and wait." [2]
>
> "The session is done when the frontier is empty: every branch of the design tree visited,
> nothing left silently assumed. Do not act on it until the user confirms you have reached a
> shared understanding." [2]

The output format is fixed (from the same file):

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

### The moves, decomposed

| # | Move | What it does |
|--:|:--|:--|
| G1 | **Design-tree modeling** | Represent the open decision space as a dependency tree before asking anything. |
| G2 | **Frontier computation** | Only ask questions whose prerequisites are already settled — never a question that depends on an unresolved earlier answer. |
| G3 | **Batched-round asking** | Ask the entire frontier in one round, not one question at a time. |
| G4 | **Recommended-default annotation** | Every question ships with the asker's own best-guess answer (➡️), so the user can accept-by-default rather than derive from scratch. |
| G5 | **Fact/decision separation** | Anything answerable by looking (filesystem, tools) is the agent's job via a dispatched sub-agent, never asked of the user. Only genuine decisions go to the user. |
| G6 | **Non-blocking fact-finding** | A pending sub-agent lookup blocks only the questions downstream of it, not the rest of the frontier. |
| G7 | **Empty-frontier termination + explicit confirmation gate** | Stop only when nothing is left silently assumed, and require the user's explicit confirmation of shared understanding before acting. |

---

## 2. socrates-skill — verbatim move catalogue

Full verbatim text, fetched from `raw.githubusercontent.com/bevibing/socrates-skill/main/SKILL.md` [4]:

> "**NEVER give a direct answer.** Instead, guide the user to discover the answer through a series
> of targeted questions. This is non-negotiable — even if the user begs for the answer." [4]

The question-type ladder (its own table, reproduced verbatim):

| Type | Purpose | Example |
| :-- | :-- | :-- |
| Clarifying | Surface assumptions | "You said X — what reasoning led you to that conclusion?" |
| Probing | Dig deeper | "What would happen if Y didn't exist?" |
| Connecting | Link concepts | "How do you think this part relates to Z?" |
| Counter | Challenge thinking | "What if we flip it — what if it's B instead of A?" |
| Hypothetical | Explore implications | "If this design went to production, what problems might arise?" |

Source: [4]

Response-branching rules (verbatim):

> "**Correct direction** → Acknowledge briefly, then deepen: 'Good perspective. Now let's take it
> one step further...'"
> "**Wrong direction** → Do NOT correct. Ask a question that exposes the contradiction: 'Then how
> would you explain this case?'"
> "**'I don't know'** → Simplify. Break into smaller sub-questions: 'Let's break it down. Looking
> at just this part first...'"
> "**Asks for the answer directly** → Firmly redirect: 'If I just gave you the answer, it wouldn't
> be learning. How about approaching it this way?'" [4]

Anti-patterns it explicitly forbids (verbatim):

> "- Stating the answer then asking 'do you understand?'
> - Giving hints so obvious they are effectively answers
> - Explaining a concept then asking a rhetorical question
> - Saying 'the answer is X, but let me ask you why'
> - Giving up and providing the answer after a few failed attempts" [4]

### The moves, decomposed

| # | Move | What it does |
|--:|:--|:--|
| S1 | **Opening calibration question** | Assess the user's current understanding before choosing a question depth ("What do you think X does?"). |
| S2 | **Typed escalation ladder** | Clarifying → Probing → Connecting → Counter → Hypothetical, deliberately ordered simple-to-complex. |
| S3 | **Never-answer invariant** | A hard rule against ever emitting the direct answer, even under explicit repeated request. |
| S4 | **Branch on correctness, not content** | The NEXT question depends on whether the prior answer was right/wrong/absent/a demand — four distinct response strategies. |
| S5 | **Contradiction-exposure on wrong answers** | Never corrects directly; instead asks a question the wrong answer cannot survive. |
| S6 | **Decomposition on stall** | "I don't know" triggers breaking the question into smaller sub-questions, not giving up or answering. |
| S7 | **Summarize-to-close** | Session ends when the user, asked to summarize, demonstrates the understanding — confirmation is EARNED via the user's own words, not asserted by the agent. |

---

## 3. Clarifying-question / ambiguity-detection literature

The published literature is almost entirely **pre-task, single-turn, conversational**: a system
receives one ambiguous utterance and must decide, before acting at all, whether to ask.

- **Zhang & Choi (NAACL Findings 2025)** frame "when to clarify" as a function of two things: user
  cost-tolerance and the **entropy of the interpretation distribution** — "whether an ambiguous
  request has one dominant, inferable interpretation" [6]. Their estimator, INTENT-SIM, scores
  clarification utility by entropy over inferred user intents. This is the field's closest thing
  to a formal "ask vs act" decision rule, but it needs an enumerable space of interpretations to
  estimate entropy over — a well-formed requirement for a single utterance, not obviously
  definable over an in-progress multi-step plan.

- **Gao, Kang, Wang, Woo (arXiv 2606.11349, AWS)** propose **ActionRating**: clarification is not
  a separate "should I ask" gate bolted onto the agent, it is **one action scored on the same
  ordinal scale as every navigation action**, competing for the decision at every step —
  "asking competes directly with acting at every decision point and help-seeking becomes
  observable at intermediate states" [7]. They further split clarification into two structurally
  distinct modes: **mandatory** (no viable branch exists at all) and **opportunistic** (a leading
  candidate exists but residual uncertainty remains) [7]. This mandatory/opportunistic split is
  conceptually the closest thing in the literature to distinguishing "must interrupt" from
  "could ask, but could also just proceed" — directly relevant to false-positive cost (secondary
  Q2). It is evaluated on a 30,000-node tariff-code classification taxonomy: a hierarchical
  decision task with discrete branches, not open-ended coding/planning.

- **Su & Cardie**, "Knowing but Not Showing" [8], report a gap between an LLM's internal/latent
  recognition of ambiguity and its surfaced behavior — it often "knows" but answers anyway. This
  is suggestive for our setting: even if a model can detect that it is thrashing, nothing compels
  it to surface that unless something outside the model's own next-token choice forces the check.
  (Title-level citation only — full text not crawled this pass; flag `[uncertain]` on any stronger
  claim about its findings.)

- **Tsvilodub & Mulligan**, "Act or Clarify?" [9], explicitly model **the cost of asking** as a
  term traded off against uncertainty — the closest literature analog to "the cost of asking is an
  interruption, not a conversational turn," but modeled within a single conversational turn, not
  an autonomous run.

- **CLAM** (Kuhn, Gal, Farquhar) [10] and **CLAMBER** (ACL 2024) [11] are both **selective
  clarification / benchmark** works confirming the same finding from different angles: LLMs
  "rarely ask users to clarify ambiguous questions and instead provide incorrect answers" [10] —
  the default failure mode is silent guessing, not over-asking. This is a base rate worth carrying
  into design: a detector that fires too rarely reproduces the field's known failure mode; one that
  fires too often risks a different, less-studied failure (interruption fatigue — see §5 below).

**Absence noted:** no paper found in this pass evaluates clarification-need detection **mid-task**,
after partial execution, from **execution residue** rather than from the initiating utterance. Every
clarification paper found treats the moment of ambiguity assessment as coincident with — or prior
to — the first action. Queried explicitly for "mid-execution", "after partial execution", and
"clarification during agent trajectory" phrasing across the same exa calls; no distinct hits beyond
the loop-detection literature in §4, which detects *that something is wrong* but not *what
question would resolve it*. This gap is a headline finding, not a search failure — see §7.

---

## 4. Thrash / loop-detection literature and production tooling

This area, unlike §3, is scoped to **during execution**, and splits into two families: academic
static/structural analysis, and practitioner/OSS runtime detectors. Both are candidate donors for
the "detect" half of yf-judgement even where they say nothing about the "ask" half.

- **Hou, Wang, Zhao, Wang (arXiv 2607.01641, HUST)**, "When Agents Do Not Stop," define
  **Infinite Agentic Loops (IALs)** as "an execution failure in which an agentic feedback path
  repeatedly triggers LLM calls, tool invocations, agent executions, or workflow transitions
  without an effective termination condition" [13], and build **IAL-Scan**, a static analyzer that
  builds an "Agentic Loop Dependence Graph" over a framework-independent IR and checks whether a
  feedback path can reach a costly operation unboundedly. Validated on 6,549 real agent repos:
  74 findings, 68 confirmed (91.9% precision) [13]. This is a **structural** absence-of-a-bound
  detector — it works on agent *code*, checking whether the framework itself guarantees
  termination. It says nothing about semantic thrash (the loop terminates fine; the same *concern*
  just keeps recurring across otherwise-well-bounded review passes). Useful as a boundary case:
  our target phenomenon is explicitly NOT what IAL-Scan detects.

- **"Loop drift" (practitioner blog, 2026-07-07)** [14] is the single most directly relevant
  finding in this cluster for the *mid-execution, residue-based* framing our study needs, precisely
  because it argues against the most obvious naive design — asking the agent to self-report
  progress:

  > "We trusted the model's self-assessment. This is the deep one. Our loop asked the model, each
  > step, whether it was making progress and whether it was done — and the model said yes, it was
  > progressing, right up to the cap. [...] The model's sense of progress is generated from the
  > same context that's drifting. [...] Asking a stuck agent whether it's stuck is asking the
  > unreliable narrator to review their own reliability." [14]

  This is a direct, on-point argument for exactly the residue-not-self-report design stance the
  005 plan's method notes already assume (004's boundary: reason from residue, not live
  introspection). It is anecdotal (n=1 incident, unreplicated, no peer review) — cited as
  supporting analytic reasoning, not as an established empirical result.

- **`agent-vitals`** (OSS, kneelinghorse) [15] is architecturally the closest external artifact to
  what yf-judgement's detector needs to compute: a **4-signal-per-step health monitor**
  (`findings_count`, `coverage_score`, `total_tokens`, `error_count`) that classifies loop/stuck/
  thrash/runaway-cost states, ships a **backtest harness with P/R/F1 against recorded
  trajectories**, and explicitly names "thrash" as a target class [15]. It is a young, unstarred
  project (0 GitHub stars at retrieval) — no external validation of its detection accuracy beyond
  its own backtest harness. Its signal choice (`coverage_score`, `findings_count`) presupposes an
  instrumented pipeline emitting those fields live; our setting instead has to derive comparable
  signals from static residue (review-pass files, bead state, git history) after the fact, which
  is a materially harder inference problem.

- **`unloop-mcp`** (OSS, synthet1cc) [16] is the single closest prior-art match to yf-judgement's
  *behavioral shape* found in this entire cluster: detect repetition from residue, escalate, and
  eventually hand off to the operator.

  > "The engine normalizes each error into a fingerprint (stripping paths, line numbers,
  > timestamps) and compares fix descriptions using Jaccard similarity. When similarity exceeds
  > 55%, it flags a loop." [16]

  Its escalation ladder is explicit and directly reusable as a design pattern:

  | Level | Trigger | What happens |
  | :-- | :-- | :-- |
  | NONE | 1-2 attempts | Silent tracking. No intervention. |
  | NUDGE | 3-4 attempts | "You're repeating yourself. Change approach." + strategies |
  | WARNING | 5-6 attempts | "STOP. Revert your changes. Research first." + strategies |
  | CRITICAL | 7+ attempts | "STOP. Revert everything. Ask the user for help." |

  Source: [16]

  Note precisely what it does NOT do: the escalation from NUDGE through WARNING is entirely
  agent-directed self-correction ("try something different"); asking the *operator* only happens
  at the final, most expensive tier (CRITICAL, 7+ attempts). It never asks a *targeted question* —
  the CRITICAL message is a blanket "ask the user for help," not a specific elicited constraint.
  This is the clearest evidence in the whole cluster that **detecting thrash and asking the right
  question are two separate, only loosely coupled problems**, and that existing tools solve
  only the first one, generically.

- **`learning-retrospective-skill`** (OSS, Yingqi-Han) [17] contributes the sharpest available
  articulation of the false-positive boundary our secondary Q2 asks about:

  > "Failure is not error — repeated attempts on a novel problem are legitimate exploration. The
  > waste this skill targets is solving the **same** problem twice: struggling through a failure
  > loop that a past session already resolved, because the lesson was never captured or never
  > recalled." [17]

  Its discriminator between thrash and legitimate iteration is **prior-session memory**: a failure
  matching a stored lesson signature is "known" (thrash — recall and stop retrying); a failure with
  no stored match is "novel" (legitimate — explore, but never retry the *exact same* thing twice).
  This discriminator is unavailable to a **first-occurrence** thrash episode within a single plan —
  it only helps once a pattern has been seen and captured before, which does not cover the
  in-the-moment case our primary Q1/Q2 target.

---

## 5. Requirements-engineering question taxonomies

This is the pre-LLM discipline the brief predicted would already own a taxonomy uncited by the
agent literature — confirmed.

- **Zaremba & Liaskos (IEEE RE 2021)**, "Towards a typology of questions for requirements
  elicitation interviews" [18], is an explicit cross-disciplinary synthesis (software engineering,
  psychology, sociology, knowledge management, library science, journalism, health care, judicial
  investigation) organizing interview questions along **content, style/probing-style, sequence,
  and objective** [18]. Within content, it cites Derr's Aristotelian/Kantian categories — a
  question can interrogate an object's **existence, identity, properties, relations to other
  objects, number, time, location, or whether it is performing an action** [18] — and Burnay et
  al.'s **Elicitation Topic Map**, six topic sets split into scope (items, rules, localization) and
  depth (activities, connections, granularity), with ~30 concrete topics collected empirically from
  interviews with practicing requirements engineers and business analysts [18].

- **Sultan & Miranskyy (RePa 2015)**, "Ordering interrogative questions... The W6H pattern" [19],
  propose ordering elicitation questions by **Who / What / When / Where / Why / hoW** — a compact,
  domain-agnostic interrogative ontology. Of everything found in this cluster, W6H is the most
  directly portable candidate scaffold for a non-conversational question taxonomy, precisely
  because it is not phrased in terms of a live interview turn — it is a content classification
  that could in principle be applied to *any* underspecified statement, including one reconstructed
  from execution residue.

- **Ferrari, Spoletini, Gnesi**, "Ambiguity and tacit knowledge in requirements elicitation
  interviews" [20], connects RE ambiguity to **tacit knowledge** — information the speaker holds
  but does not know is missing from what they said. This reframes what a "good question" is
  doing: not eliciting information the speaker is deliberately withholding, but surfacing an
  assumption the speaker doesn't know they made. That reframing matters for yf-judgement design:
  the operator who set a vague objective is not being cagey, they simply didn't know the
  under-specification existed until the agent's residue makes it visible — closer to Derr's
  "surface an assumption" framing (S1/G5 above) than to an interrogation.

The RE discipline's content/style/sequence/objective structure and the Derr/W6H interrogative
ontologies are all designed for a **live, synchronous, bidirectional interview** — an interviewer
adaptively choosing the next question based on the interviewee's last answer, in real time. None
of them were built to be applied to a **static document** (a plan, a set of review passes) after
the fact, with no interviewee available to redirect the questioning.

---

## 6. Other coding-agent skills/tools

- **`otar/clarify-skill`** [21]: a `/clarify` Claude Code plugin using the native `AskUserQuestion`
  tool, explicitly pre-task: "It interrogates your request with structured, clickable questions
  until it's unambiguous, **before any work starts**" [21]. Manually invoked only
  (`disable-model-invocation: true`), same invocation posture as `grill-me`. Confirms the pattern:
  every publicly discoverable "ask before acting" coding-agent skill found in this search clusters
  at **intake**, not mid-execution. No skill or tool found in this cluster fires its clarifying
  questions *after* the agent has already taken action and left residue.

- Loop/thrash-adjacent tools already covered in §4 (`unloop-mcp`, `agent-vitals`,
  `learning-retrospective-skill`) are the closest thing to "other tools doing something similar" —
  they detect thrash mid-execution but hand off to a generic "ask the user" rather than a
  constructed question.

---

## 7. HCI: interruption cost

Two foundational, peer-reviewed, highly-cited CHI papers ground the "cost of asking is an
interruption to an autonomous run" framing from the brief:

- **Borst, Taatgen, van Rijn (CHI 2015)**, "What Makes Interruptions Disruptive?" [22], model
  disruption cost via the **problem-state bottleneck**: duration, interrupting-task complexity, and
  moment of interruption jointly determine cost, and "problem state requirements of both the
  interrupted and the interrupting task" predict how disruptive an interruption is [22].

- **Adamczyk & Bailey (CHI 2004)**, "If Not Now, When?" [23], is the field's foundational study on
  interruption **timing**: it shows different moments within a task's execution have measurably
  different effects on performance, emotional state, and the user's social attribution toward the
  interrupting system, and argues for identifying low-cognitive-load **breakpoints** between
  subtasks as preferred interruption moments [23].

Both papers model interrupting a **human's own task**. Our setting inverts the direction: we
interrupt the *operator's attention* to redirect an *agent's* run, not a human multitasking between
two of their own tasks. The transferable concept is not the cost model itself but the **breakpoint
principle** — that some moments cost less to interrupt at than others, and a boundary between
subtasks (a completed review pass, a closed bead, a phase-log entry) is a structurally low-cost
candidate moment, analogous to the "moment within task execution" variable these papers manipulate.

---

## 8. The transfer table

Every catalogued move, and whether it survives a mid-execution, residue-based, autonomous-run
setting. Grading key for "assumes conversational?": **Y** = built for a live human turn, **N** =
domain-agnostic content classification with no synchrony assumption.

| Move | Origin | Assumes conversational? | Transfers to mid-execution? | What it needs | Verdict |
|:--|:--|:-:|:-:|:--|:--|
| G1 design-tree modeling | grilling [2] | Y | **Partial** | A decision-dependency structure inferable from residue (e.g. a bead graph, a plan revision chain) rather than from a live back-and-forth | The tree structure is domain-agnostic; building it from residue instead of live Q&A is the open design problem |
| G2 frontier computation | grilling [2] | Y | **Partial** | Same as G1, plus a way to tell which "decisions" are already implicitly settled by what the agent did, vs. still open | Requires re-deriving "settled" from artifacts, not from an answer just given |
| G3 batched-round asking | grilling [2] | Y | **Yes** | Nothing extra — batching applies equally to a single post-hoc interruption | Directly portable: ask everything the detector surfaced in one interruption, not serially |
| G4 recommended-default annotation | grilling [2] | N | **Yes** | The agent must already have formed a best guess (which a thrashing agent, by construction, has tried several of) | Strong fit: a thrash episode's failed attempts ARE candidate recommended answers to surface |
| G5 fact/decision separation | grilling [2] | N | **Yes** | Discipline to route anything discoverable in the repo/tools to further investigation, never to the operator | Directly portable and arguably MORE important here, since interrupting costs more than in a live chat |
| G6 non-blocking fact-finding | grilling [2] | N | **Yes** (weakened need) | Less relevant once the agent isn't blocked live on the user; the analog is not re-blocking on a slow investigation before surfacing the rest | Portable but lower-value: mid-execution the agent already ran to completion of its burn, so there's less "meanwhile" to fill |
| G7 empty-frontier termination + confirm gate | grilling [2] | Y | **No, not as-is** | A live acknowledgment loop; mid-execution the agent is not continuing to interview, it interrupts once and hands off | Does not transfer directly — the "session" framing assumes an ongoing dialogue the mid-execution case doesn't have (an interruption is a single event, not an open session) |
| S1 opening calibration question | socrates [4] | Y | **No** | A live respondent to calibrate against before choosing depth | Assumes a synchronous respondent already present; a thrash detector fires once, cold, with no prior calibration turn |
| S2 typed escalation ladder | socrates [4] | Partial | **Partial** | Adapting question TYPES (clarifying/probing/counter/hypothetical) to residue-derived content, not to a live respondent's last utterance | The taxonomy of question *shapes* is domain-agnostic; the *escalation logic* (which type to use *next*, based on the respondent's last answer) assumes a live loop and does not transfer |
| S3 never-answer invariant | socrates [4] | N (as principle) | **No, wrong goal** | N/A — this skill's goal is teaching-by-discovery; yf-judgement's goal is UNBLOCKING an agent, which requires actually incorporating the operator's answer to resume work, not refusing to converge | Actively wrong fit: the never-answer rule optimizes for the human learning, not for the agent resuming — importing it would make yf-judgement worse, not better |
| S4 branch on correctness | socrates [4] | Y | **No** | A live respondent whose answer can be judged right/wrong against ground truth the tutor already holds | Does not transfer: yf-judgement doesn't hold a ground truth the operator's answer is checked against — the operator's answer IS the missing ground truth |
| S5 contradiction-exposure | socrates [4] | Y | **No** | A live wrong answer to expose a contradiction in | Same failure as S4 |
| S6 decomposition on stall | socrates [4] | Partial | **Partial** | Could inform how a detector escalates a too-broad question into a narrower one across repeated non-answers, but assumes multi-turn presence | Weak transfer: useful as a fallback strategy if the operator's first answer doesn't resolve the thrash, but not as the primary detection mechanism |
| S7 summarize-to-close | socrates [4] | Y | **No** | A live respondent producing a confirming summary in their own words | Assumes ongoing dialogue; mid-execution confirmation is closer to "the agent resumed and didn't re-thrash," an outcome measure, not a conversational move |
| INTENT-SIM entropy-over-interpretations [6] | Zhang & Choi | Y (single utterance) | **No, as stated** | An enumerable space of interpretations of a single utterance | Would need reformulation: the analog "space of interpretations" mid-execution is a space of PLAN CONTINUATIONS, not utterance readings — a much less well-defined object |
| ActionRating: asking as a scored action [7] | Gao/Kang/Wang/Woo | N | **Yes, as architecture** | A scoring function over "ask" vs. "continue" comparable to the scoring already used for other agent actions/decisions | The strongest structural transfer found: treating "surface a question to the operator" as one more scored option at a decision point (e.g., a coordinator's dispatch loop) rather than a bolted-on watchdog |
| mandatory vs. opportunistic clarification split [7] | Gao/Kang/Wang/Woo | N | **Yes** | A way to tell "no viable next step exists" from "a viable next step exists but confidence is low" from residue | Directly maps onto thrash vs. convergence (secondary Q2): a bead endlessly reopened with no candidate resolution is "mandatory"; a review pass that is deepening toward agreement is "opportunistic" and should NOT interrupt |
| self-report progress checks [14] | loop-drift blog | N/A (not conversational — it's a rejected design) | **Explicitly rejected, and the rejection transfers** | N/A | The strongest negative transfer finding: whatever the detector reads, it must NOT be the agent's own live claim of progress, because that claim is generated from the same drifting context — directly reinforces 004's residue-based framing |
| 4-signal step monitor [15] | agent-vitals | N | **Partial** | Live per-step instrumentation (`findings_count`, `coverage_score`, `total_tokens`, `error_count`) — our setting has none of this streaming; only after-the-fact artifacts | The SHAPE (small number of composable numeric signals, backtestable against recorded trajectories) transfers; the SPECIFIC signals do not, because they require live pipeline hooks this project's corpus was never instrumented with |
| error-fingerprint + similarity threshold + escalation ladder [16] | unloop-mcp | N | **Yes, closest fit in the whole cluster** | A fingerprinting function for RECURRING CONCERNS across review passes (analogous to fingerprinting errors across fix attempts) and a similarity threshold | Directly analogous to 005's own "review-pass recurrence" cluster's job: fingerprint findings, detect the same concern recurring. The escalation-tier SHAPE (silent → nudge → warn → ask) is portable; note it only asks generically at the top tier — it does not solve question CONSTRUCTION |
| known-vs-novel via stored-lesson match [17] | learning-retrospective-skill | N | **No, for first occurrence** | A prior captured lesson to match against | Does not help distinguish thrash from convergence on a FIRST pass through a novel problem — which is exactly our primary setting; only useful for recurring cross-plan patterns, a different (also valuable, but separate) detector |
| Derr's question-content categories (existence/identity/properties/relations/number/time/location/action) [18] | RE typology | N | **Yes** | Nothing beyond applying the categories to a residue-derived underspecified claim instead of a live interviewee's utterance | Strong candidate ontology for CLASSIFYING what kind of question yf-judgement should construct, once a thrash episode is detected |
| Elicitation Topic Map (scope: items/rules/localization; depth: activities/connections/granularity) [18] | Burnay et al. via [18] | N | **Yes** | A domain mapping from these six topic sets onto software-plan objects (a bead, a constraint, an exclusion) | Plausible scaffold for the "what class of operator-supplied information ended it" question (primary Q3) — the six topics look like a checklist for what a thrash-breaking answer usually IS |
| W6H interrogative ordering [19] | Sultan & Miranskyy | N | **Yes** | Nothing beyond applying the six interrogatives to residue | Most portable single artifact in the RE literature — domain-agnostic, could directly scaffold question-type selection without modification |
| tacit-knowledge framing of ambiguity [20] | Ferrari/Spoletini/Gnesi | Partial | **Yes, as a reframe** | Nothing — it's a stance, not a mechanism | Reframes the whole design goal usefully: the question isn't interrogating a withholding operator, it's surfacing an assumption neither party knew was load-bearing until the residue showed it |
| pre-task-only invocation posture [1][21] | grill-me, clarify-skill | Y (by construction) | **No — this is the gap itself** | A detector that fires unprompted, from residue, not from an explicit user invocation | Every publicly found "ask before acting" skill is opt-in and pre-task; none auto-fires mid-execution from residue. This absence is itself the strongest single finding of the cluster |
| interruption breakpoint principle [22][23] | HCI (CHI 2004/2015) | N (principle) — Y (original mechanism) | **Yes, as a principle; No, as a mechanism** | A structural analog to a "moment within task execution" — a review-pass boundary, a bead close, a phase-log entry | The COST MODEL doesn't transfer directly (it's about interrupting a human's cognition, we interrupt an operator's attention to redirect an agent), but the finding that boundary moments are lower-cost interruption points DOES transfer, and gives a principled place in the yf loop (surface 6, secondary Q3) to prefer firing at |
| IAL structural loop detection (static analysis of feedback paths) [13] | Hou et al. | N | **No** | Agent framework source code with explicit control-flow to analyze | Wrong failure class: IAL-Scan finds loops with NO termination bound; our target is a loop that DOES terminate (each review pass, each plan revision completes) but the same CONTENT recurs. Structurally orthogonal, not a subtype |

---

## 9. Named gaps (headline findings)

1. **No literature or tool found detects clarification-need from post-hoc execution residue.**
   Every clarifying-question paper (§3) and every "ask before acting" skill (§1, §2, §6) operates
   at or before the first action, working from a live utterance or a live respondent. Every
   loop/thrash detector found (§4) operates live, mid-stream, from instrumented per-step signals —
   none from a corpus of already-written artifacts (review passes, bead history, git log) read
   after the run. yf-judgement's actual input shape — a static residue trail — has no direct
   precedent in either literature family. This confirms and sharpens 004's finding (plan bundles
   record artifacts, not live behavior): the entire external clarification/thrash-detection field
   also assumes live access to either an utterance or a running trajectory, and nothing in this
   search surfaces a system built to work only from what's left behind.

2. **No tool found couples thrash detection to targeted question construction.** The single
   closest artifact, `unloop-mcp` [16], detects and escalates through three tiers of self-directed
   redirection and only asks the operator generically ("ask the user for help") at its most
   expensive, final tier — it does not construct a specific question from the fingerprinted
   recurring content. Every "ask a good question" resource found (grill-me, socrates, the RE
   typologies) assumes the asking is happening synchronously with a present respondent choosing
   what to answer next, not being handed a single best-shot interruption. yf-judgement's core
   claim — detect thrash AND construct the specific unblocking question in one motion — appears to
   be an unaddressed combination, not a solved problem being reinvented.

3. **The RE typologies and W6H ordering are the most portable raw material found**, precisely
   because they were never conversational to begin with in their strong form — Derr's
   existence/identity/properties/relations/number/time/location/action categories [18] and the
   W6H pattern [19] are content classifications applicable to any underspecified statement, whether
   spoken live or reconstructed from residue. This is the field the brief predicted would be
   uncited by the LLM-agent literature, and it is uncited: none of the clarification papers in §3
   or the loop-detection work in §4 references requirements-elicitation question typologies.

4. **The strongest negative transfer finding is the self-report rejection** [14]: whatever signal
   a mid-execution thrash detector reads, it must not be the agent's own claim of progress or
   stuckness, because that claim is generated by the same process that may be drifting. This
   converges independently with 004's residue-based framing and with the ActionRating [7] finding
   that clarification only becomes a well-behaved decision when scored structurally rather than
   self-reported.

Absence is recorded here as a valid finding per the epistemic rules, not as a search failure: the
queries above were run across exa's `pdf` and `github` categories and its default web index, and
none surfaced a system operating on execution residue rather than a live utterance or a live
trajectory stream.
