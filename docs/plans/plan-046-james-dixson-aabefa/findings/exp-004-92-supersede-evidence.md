---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-92-supersede-evidence
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# exp-004 — Is #92 superseded? (and the true extent of #118)

**Question:** Establish mechanical evidence for — or against — reconciling #92 as superseded, and scope #118.
**Method:** measured emit coverage across the 50-bundle corpus with a scripted frontmatter parser; git-archaeology on the emit commit vs the deferral commit; traced every `check_conformance` / `emit_conformant_copy` / `okf_conformance_check.py` call site; ran the live engine and three test suites; queried `gh api` for OKF releases and non-Google adopters; ran bookpipe's `okf-lint` read-only; grepped every skill's README/SKILL/SPEC for README-as-orientation drift. Read-only.

## Verdict

> **D-1 is substantially but not cleanly correct.** "Supersede #92" is defensible. **"Supersede #92 as fully covered by #140" is not** — a clean close would silently drop three things. The honest outcome is **supersede with three named carve-outs.**

## 1. The emit half — SHIPPED

All five copies of `okf.py` byte-identical. First landed:

```
$ git log --diff-filter=A --format="%h %ad %s" --date=short -- _shared/okf.py
aaf2b6c 2026-07-19 plan-029: OKF-* framework — yf-okf skill + engine + 3 skill integrations
```

Emit sites, all from that commit: `plan_manager.py:492-505` (`_stamp_okf_frontmatter`), `index_manager.py:138-162`, `incubator-index.py:89-93` — each `okf.write_frontmatter({"type": typ, "okf_spec": member})`. *(`research_manager.py` has zero `okf` references; yf-research's emit lives entirely in `index_manager.py`.)*

Corpus coverage of non-reserved `.md` carrying `type`:

```
docs/plans:    46 bundles, 590 non-reserved .md, 288 with_type, 288 with_okf_spec
docs/research:  4 bundles,  35 non-reserved .md,  26 with_type,  26 with_okf_spec
okf_spec values: OKF-PLAN 277 · OKF-RESEARCH 33 · OKF-INCUBATOR 4
```

**The 49% aggregate is misleading — it is entirely a legacy tail.** Per-bundle: plan-001…030 are `0/N`; every bundle from plan-031 on is at or near 100% (`6/7, 4/4, 10/12, 4/4, 12/12, 4/4, 42/45, 43/43, 26/26, 26/26, 14/15, 9/9, 16/16, 25/25, 20/20, 8/8`). research-001 is `0/9` (legacy); 002/003/004 are `9/9, 8/8, 9/9`.

The 14 post-migration misses are **vendored foreign content or pre-migration residue**, not emit failures — `plan-030/*` (7), `plan-037/references/user-scope/yf-herdr/{README,SKILL,SPEC}.md` (3, verbatim copies of a foreign skill), 4 hand-authored files.

The engine agrees: `check` returns `OK` on both a plan and a research bundle.

### The sharpest fact: the deferral was recorded AFTER the thing it defers shipped

```
aaf2b6c 2026-07-19 12:54:17 -0700  plan-029: OKF-* framework … + 3 skill integrations
be84937 2026-07-19 21:33:01 -0700  research-001/OKF: record decision to defer OKF integration (#91)
```

**8h39m apart.** This is not evidence the deferral was wrong — plan-029 landed **native in-place typing** while #92 asks for a **non-destructive export projection** (§5). But it means the *"true cost is a whole-bundle conformant tree, not a one-line `type` key"* rationale was already partly obsolete when written. `DECISION.md` §Consequences even claims *"No change to `plan_manager.py`… or the `README.md` / `_index.md` reserved-index names"* — which `aaf2b6c` had falsified nine hours earlier.

## 2. Is the nested-tree half really #140? — **on content yes, on delivery mode NO**

The gap #140 asserts still holds exactly: `find … -mindepth 3 -name index.md | grep -v okf-migration-samples` → **0**.

But the distinction is real and load-bearing. #92 asks for *"whole-bundle nested `index.md` trees **on demand**"* — a **projection**. #140 asks to *"enforce OKF structure below the bundle root"* + add `reindex`/`--fix` — **in-place** generation with drift detection, framed explicitly around *"a stale index asserts something false"*.

**The projection primitive exists but is inert:**

```
$ grep -rn "emit_conformant_copy" . --exclude-dir=.git
_shared/okf.py:928  (+ 4 byte-identical vendored copies)
skills/yf-okf/SPEC.md:28, :194   (spec text)
```

**Zero callers. Zero tests. Not a CLI verb** — `main()` registers only `check`, `migrate`, `scaffold`.

> If #92 is closed as superseded-by-#140, the on-demand-projection axis is silently dropped, and the one function that would implement it is **dead, untested, spec'd code that no gate protects.**

## 3. The gate — shipped for ONE of three skills

`okf_conformance_check.py` exists in exactly three places, all research artifacts / fixtures. Its own header: *"The exact OKF SPEC is NOT yet known at the time this tool was built… Treat every delta this tool reports as PROVISIONAL."* `DECISION.md:44-45` confirms it is *"not wired into any skill gate"* — still true.

Its successor `okf.check_conformance` **is** wired, but only in yf-plan:

| Surface | Wired? | Evidence |
| :-- | :-- | :-- |
| `plan_manager.py audit` | **YES — but scoped to FOUR reqs** (caveat added post-review: the hard-fail applies only to error-level findings whose req is in the `_OKF_PORT050_REQS` allowlist `REQ-OKF-003/030/031/071`; reserved-file presence errors REQ-OKF-001/002 are *deliberately excluded*, so "wired" is narrower than it reads) | `:3965`, `okf_missing_level = fail` for OKF-native non-grandfathered plans |
| `research_manager.py` | **NO** | zero `okf` references |
| `incubator-index.py` | **NO** | writes frontmatter, never checks |
| `CHANGE-VALIDATION.md` | **NO** | `grep okf` → empty |
| `DRIFT-CHECK.md` | partially | only the `e-okf-copy-*` **byte-identity** edges — vendored-copy drift, not bundle conformance |
| CI | **NO** | `grep -rn okf .github/` → empty |

And yf-research's `spec/portability.md:32` states *"Verification: `okf.py check_conformance` over a packaged bundle reports zero errors"* — **nothing executes it at runtime**; the only caller is a `tmp_path` fixture in `test_index_manager.py:189`. **That is precisely open issue #165.**

## 4. The revisit triggers, as of 2026-08-18

**(a) A concrete consumer — NOT FIRED.** The only OKF issues are #83/#91/#92/#128/#140/#141, all internal producer-side work. `Summary.md:40` recorded *"no source establishes any consumer wanting these software-plan/research folders as OKF"*; nothing has changed.

**(b) Stable release AND non-Google adopter — HALF-FIRED, and the half that fired is the half #92 named as its blocker.**

No stable release:

```
$ gh api repos/GoogleCloudPlatform/knowledge-catalog/releases  → []
$ gh api repos/GoogleCloudPlatform/knowledge-catalog/tags      → []
$ gh api repos/… --jq '{pushed_at, stargazers_count, forks_count}'
{"pushed_at":"2026-08-18T19:16:52Z","stargazers_count":8713,"forks_count":743}
```

But non-Google adopters **exist**, verified by fetching actual file contents:

| Repo | Path | Content |
| :-- | :-- | :-- |
| `FastEndpoints/FastEndpoints` | `.okf/index.md` | `okf_version: "0.1"` |
| `dj-nitehawk/MongoDB.Entities` | `.okf/index.md` | `okf_version: "0.1"` |
| `matthiasn/lotti` | `knowledge/index.md` | **`okf_version: "0.2"`** |
| `scaccogatto/okf-skills` | `.okf/index.md` | **`okf_version: "0.2"`** + an `/okf:visualize` renderer |

Also: `kushal-omnius/open-knowledge-compiler` ships a third-party OKF conformance checker.

> The trigger is **conjunctive**, so it has not fired. But #92's stated rationale — *"one confirmed consumer, **no confirmed non-Google adopter**"* — **is now measurably false**, including at v0.2. Citing it as live rationale would be a false statement.

**(c) We adopt an OKF-consuming tool — AMBIGUOUS, and it is the closest call.**

`~/workspace/bookpipe/bp/skills/okf-lint/` exists (dated 2026-08-12), is referenced five times in `bookpipe/bp/CLAUDE.md` as an operational tool, and is genuinely OKF-consuming. **But it does not touch any yf-\* bundle:**

```
$ cd ~/workspace/bookpipe/bp && uv run skills/okf-lint/scripts/okf-lint.py --root "$PWD"
  x …/bp: resolved root has no AGENTS.md — it is the OKF root sentinel …   FAIL
$ find ~/workspace/bookpipe -maxdepth 3 -name AGENTS.md
./500 year challenge/AGENTS.md          ← the book vault; zero yf-* bundles
```

`bp/docs/plans/` (which *does* hold yf-plan bundles) is outside that root entirely. And nothing OKF-third-party is installed in our own harness (`ls ~/.claude/skills ~/.agents/skills | grep -i okf` → `yf-okf` only).

> **Reading:** the *capability* precondition fired — we authored and use an OKF-consuming linter we did not have on 2026-07-19, which is the trigger's literal words. The *demand* precondition (trigger a) did not. **This is a judgment about intent that no command can answer; it needs an operator ruling, not another investigation.**

## 5. The residue — three carve-outs

> **Canonical names (normalized by plan-046 Issue 5.5).** This section originally named the
> carve-outs in prose that varied from the names used in `plan.md` and `upstream-triage.md`, so
> SC9's cross-site check could not discharge. The three canonical names are
> **projection delivery mode**, **conformance gate for yf-research and yf-incubator**, and
> **consumer round-trip fidelity**; each is added in brackets below beside this finding's original
> wording. The original wording is **kept**, not overwritten — a finding is a record of what the
> investigation said, and silently restating it to match a later criterion would falsify the
> record rather than reconcile it.

1. **On-demand / non-destructive export projection** [canonical: **projection delivery mode**]**.** `emit_conformant_copy` is library-only: no verb, no caller, **no test**. #140 is explicitly in-place. **NOT covered.**
2. **Nested `index.md` trees.** Covered by #140 as in-place enforcement — and #140 is a strictly better-specified take. **Covered on content, not delivery mode.**
3. **The gate, for yf-research and yf-incubator** [canonical: **conformance gate for yf-research and yf-incubator**]**.** Shipped for yf-plan only. **NOT covered by #140 or #141.**
4. **Extension-key round-trip fidelity** [canonical: **consumer round-trip fidelity**]**.** **Materially improved, not resolved.** REQ-OKF-070 merge-and-preserve is implemented and tested (`31 passed`) — but #92's claim was round-trip *through a consumer* (`Summary.md:160`: *"producer→consumer→producer round-trip of yf-\* keys through any OKF tool… `[insufficient evidence]`"*). We demonstrate producer→producer only. **Still unverified in the sense #92 meant.**

## 6. #118 — NARROWER than the prior suggested, but with two unnamed omissions

The complete stale-orientation set is **two lines, one file**:

| # | file:line | Text |
| :-- | :-- | :-- |
| 1 | `skills/yf-plan/README.md:97` | `` - `README.md` — orientation (file map, reading order) `` |
| 2 | `skills/yf-plan/README.md:144` | `README.md   Orientation and file map for cold readers` |

**Two *omissions* at the same two sites, which the issue does not name and a fix must also close:**

- the portability-contract bullet list (`:95-101`) lists `context.md`, motivation, `references/`, `reviews/` — but **neither `index.md` nor `log.md`**;
- the per-plan layout block (`:140-155`) lists 10 entries — **no `index.md`, no `log.md`, no `plan-retrospective.md`**;
- `grep -n "index\.md\|log\.md" skills/yf-plan/README.md` → **zero hits in the entire file.**

Everything else is clean — verified: `SPEC.md:38`, `spec/portability.md:19-22`, `spec/data.md:9,23`, `spec/cli.md:57`, `SKILL.md:262`, `protocols/PLANS.md:24`, `web/content/skills/yf-plan.md`, root `README.md`. The other 18 `README.md` hits across skills are the benign self-reference `— this file` or a project-README link. yf-incubator's README-as-state-file is a **deliberate documented divergence** (REQ-INCUB-042), not drift. yf-research's `_index.md` mentions are all correctly historical.

**#118's own citation has drifted:** it cites `SKILL.md:245`; the correct content is now `SKILL.md:262`.

### Adjacent, larger, and NOT part of #118 — file separately

The skill-dir File Layout block in the same file (`README.md:106-138`) is materially stale against the real tree: it omits `SPEC.md`, `OKF-EXTENSION.md`, `spec/ci-release-completion.md`, `test-harness/` (5 files), and **18 of 21 `scripts/` files**.

> If the "previous plans under-estimated doc-drift extent" prior is vindicated anywhere, it is here — **20+ omissions in the block immediately above the two lines #118 names.** But it is a separate defect; folding it into #118 would make #118 unreviewable.

## Implications

1. **D-1 survives, weakened.** Do not record "#92 bifurcated into shipped + #140" — that drops three things.
2. **The deferral's own rationale is partly falsified on the record** — by a commit nine hours older than it, and by four verified non-Google adopters. The close comment must say so, since #92's Why-deferred section is what a future reader will trust.
3. **Trigger (b)'s adopter half has fired.** The conjunction has not, so the letter holds — but the stated rationale is now false.
4. **Trigger (c) needs an operator ruling.**
5. **A new, unfiled gap surfaced** [canonical: **conformance gate for yf-research and yf-incubator**]**:** yf-research and yf-incubator have no runtime conformance gate, and yf-research's SPEC states a verification nothing executes (#165 class).

## Recommendations

1. **Close #92 as superseded with three named carve-outs**, not cleanly.
2. **Do not let `emit_conformant_copy` stay as-is** — it is spec'd, unreachable, and untested. Either expose it as the `emit`/`project` verb #92 wanted, or delete it and amend the SPEC. **Leaving it is how a future investigator concludes the projection "exists."**
3. **Write the close comment against the measured record**, correcting the two now-false rationale bullets.
4. **#118: fix all four things** — the two stale lines *and* the two omissions. Update the `SKILL.md:245` → `:262` citation.
5. **File the File Layout staleness separately** (~20 omissions).
6. **Sequence after #141** — v0.2 changes the frontmatter any projection or nested index would surface.

## Honest limits

- **Trigger (c) is unresolved by design.** Whether bookpipe's `okf-lint` counts as "our workflow" is a judgment about intent no command can answer. Everything measurable around it was measured.
- **"Non-Google production adopter" is inferred, not attested.** Four repos verified to carry literal OKF bundles; "production" is a read of repo prominence. No adopter has stated it consumes external OKF bundles.
- **GitHub code-search totals are unreliable** (12032 hits for a literal string is not credible). Only the four `contents`-API fetches are load-bearing.
- **Incubator emit is untested against a real corpus** — neither this repo nor bookpipe has an `Incubator/`. Verified only by `test_incubator_index.py` (14 passed) and code reading.
- **One benign test artifact:** `pytest test_incubator_index.py test_index_manager.py` together yields `5 failed, 25 passed`; each alone yields `14 passed` / `16 passed`. Cause is a sibling-module name collision on `okf` across two `scripts/` dirs, not a product defect — but a CI author who batches them would see red.
- **Installed-vs-repo skill artifacts were not diffed**; all measurement is against the working tree.
