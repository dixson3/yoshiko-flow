## plan-066 PARTIALLY landed — the site builds again. This issue STAYS OPEN.

Executed as `plan-066-james-dixson-e7fadb`, merged to `main` as a **deliberate partial land**.
**The issue is right on intent and wrong in six places on fact**; the implementation followed the
measurements in the plan's `findings/`.

> ### Why this is not closed
>
> **This issue's own acceptance requires a retrospective distinguishing content defects from
> process defects, with counts. That has not been written.** It is gated behind a diagram
> human-read gate the operator has **not accepted** (see *What is still open*, below).
>
> Closing now would publish a completion claim that is not true — which is the exact defect class
> this issue commissioned a plan to close. So it stays open, and this comment records what landed
> and what did not.
>
> The **P0 was landed early on purpose**: the build fix existed only on the execute branch while
> `main` still shipped 19 skill pages and still failed to build. The site should stop being broken
> today rather than when the remaining work lands.

### The P0

`web/content/skills/yf-okf-hygiene.md` was the one missing file. Nothing was behind it —
`pelican` now exits 0 under `--fatal warnings` on **both** `pelicanconf.py` and `publishconf.py`,
20/20 skills emit pages, zero warnings.

"The build passes" was **not** accepted as the criterion, because the plugin's guard is
existence-only and a **zero-byte page satisfies it**. The criterion is conjunctive: exit 0 **and**
the emitted HTML has real content (measured: 1 `<hr>`, 9 `<h2>`, 863 body words).

### Class B — the payload was item 5, and it is a DISPATCH gap

Measured: the engine scored **4 firing opportunities, 0 catches** on `e-skill-page-desc`, an edge
that returned **3 FAILs with quoted evidence** the moment it was dispatched by hand. A manifest
edit cannot fix that. So this plan shipped a mechanical gate:

- four checkers — `check_web_counts.py`, `check_web_harness_paths.py`,
  `check_skill_page_contract.py`, `check_web_backend_claim.py`;
- six `CHANGE-VALIDATION.md` recipe rows in **both** tiers, with §3 globs naming the **source**
  side as well as the doc side;
- a `web-doc-checks` CI job invoking all four **by name**, unfiltered.

`grep 'web/' CHANGE-VALIDATION.md` returned **nothing** before this.

The source-side triggers are not a nicety: commit `75a5796` added the twentieth skill, broke the
build and drifted the 19→20 count while touching **zero** `web/` files.

### Six corrections this plan carries

1. "images/cards/home have no §6 trigger row" — **false**; `web/content/**` matched all three. The
   defect was the narrow fan-out, so the proposed remedy was a **no-op**.
2. "flipping `optional`→`required` does not fix it" — correct, and now proven by A/B rather than
   argued. The flip was dropped from the remedy entirely.
3. "`yf-okf-hygiene` has neither a page nor a README" — **stale**; it had a README since `4cf61c7`.
4. "`harness-tune.md:156` contradicts `install.md`" — no longer true, and was already untrue at
   filing. The narrower defect (an unconditional bullet vs a sha256 guard) was real and is fixed.
5. Rows 4-6 name ~4 sites — **the real count was 40 findings across 10 files**, including
   `README.md` and `AGENTS.md`, which a `web/content/**`-scoped checker cannot reach at all.
6. "no mention of `land` … is a coverage gap" — omissions **PASS by design**; these were never
   enforcement misses. Done as editorial work instead.

### What is still open

- **The diagram human-read gate was NOT accepted.** The six diagrams are **factually correct and
  mechanically checked** — counts, group membership, harness paths and backend claims all verified
  against their sources, and all six re-rendered byte-identically under a pinned `d2 v0.8.2`. What
  is outstanding is a **redesign**, not a correction: a layered marketecture with tool
  dependencies, per-skill and per-formula diagrams, a combined phase-model/lifecycle, and a
  combined install/tune matrix — together with a `DRIFT-CHECK.md` amendment making **omissions**
  FAIL rather than pass by design. That is a follow-on plan, filed separately.
- **The retrospective** (content vs process defects, with counts) — gated behind the above.
- The remaining verification-sweep, upstream-reconcile and `CHANGE-VALIDATION`-row bookkeeping
  that depend on it.

### Acceptance status

Local clean build, no deploy, per this issue's own acceptance. FULL validation tier: **79 rows, 0
failing**. Success criteria: **27 total — 25 hold, 1 FALSE (the ungated retrospective), 1
not-evaluated (the manual diagram read)**.

*(An earlier draft of this paragraph said "23 of 24". That was a count of the criteria **script's
subcommands**, not of the **criteria** — two different sets, since three criteria do not route
through that script. Correcting it rather than quietly is the point: a counted-set claim drifting
from its source of truth is the exact defect class this plan exists to close, and it recurred
inside the plan that closes it.)*

*(An earlier draft of this paragraph said "23 of 24". That was a count of the criteria **script's
subcommands**, not of the **criteria** — two different sets, since three criteria do not route
through that script. Correcting it here rather than quietly is the point: a counted-set claim
drifting from its source of truth is the exact defect class this plan exists to close, and it
recurred inside the plan that closes it.)*

Plan bundle: `docs/plans/plan-066-james-dixson-e7fadb/`.
