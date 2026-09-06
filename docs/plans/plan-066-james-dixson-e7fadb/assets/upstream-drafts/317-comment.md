## plan-066 landed — the site builds again, and the Class-B dispatch gap is closed

Executed as `plan-066-james-dixson-e7fadb`. **The issue is right on intent and wrong in six
places on fact**; the implementation followed the measurements in the plan's `findings/`.

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

### Acceptance

Local clean build, no deploy, per the issue's own acceptance. FULL validation tier: **79 rows, 0
failing**. 23 of 24 plan criteria green at the time of writing.

Plan bundle: `docs/plans/plan-066-james-dixson-e7fadb/`.
