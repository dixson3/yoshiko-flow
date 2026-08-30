---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 7 — VERDICT APPROVE. No high. Six concerns, all prose corrections; the sharpest falsifies the spike''s CAUSAL attribution (nested-repo opacity, not gitignore) while confirming all 18 of its counts. All resolved.'
---
# Review pass 7 — adversarial (red-team)

## Verdict: APPROVE

No high. Six concerns, all corrections to prose — *"none changes an issue, a criterion, a gate, or an
upstream disposition."* **All 6 resolved** by the main session.

**Date:** 2026-08-29
**Dispatched as:** sub-agent (REQ-AGENT-049), read-only with respect to the repository under review.
**Subject:** the spike-backed revision, on a second operator-granted bound raise (ESC-002), as a
**full** pass rather than a narrowed one.

## Strengths

- **The spike reproduces exactly — all 18 rows, independently.** The reviewer built a separate
  fixture and re-ran every candidate from both cwds. F1, F2, F3 and F5 all confirmed.
  *"`assets/enumeration-spike.md` is accurate as measured."*
- **The commissioning decision was correct.** *"The spike settled in one round what five prose rounds
  moved laterally on"*, and the reviewer could not construct a case where either prescribed branch is
  wrong that the plan does not already exclude.
- **F5 is stronger than the spike claimed.** The two candidates an implementer reaches for next —
  `status --porcelain=v2 --ignored=matching` (the documented fix for directory-collapsing) and
  `ls-files --others --ignored --exclude-standard` — **both also return 1**. *"The trap survives its
  own documented workaround."*
- **Bidirectional integrity holds at 49 / 41 / 86 / 18, verified programmatically** — zero dangling
  either way, zero issues discharging nothing, zero duplicate SC ids, zero forward references,
  **zero cycles (DFS over all 86 edges)**.
- **Seventh vacuity sweep clean.** 32 guard-routed criteria with 32 distinct names, plus 9 non-pytest
  all recorded under `bash -c`. SC1's script carries its own vacuity guard; SC2 has `--min-issues`;
  SC2b is an explicit count comparison; SC34's negative half is guarded by its positive half.
  *"I found no criterion satisfiable by absent or defective work."*
- **All mechanical checks green** on a tree that post-dates pass 6.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | medium-high | **The spike's causal attribution is falsified by measurement: gitignore is not why the primary-cwd case returns 0.** With `/.worktrees/` removed from `.gitignore` entirely, every git candidate **still** returns 0 while `find` returns 4. The real mechanism is **nested-repo opacity** — the worktree carries a `.git` marker and git will not descend. Gitignore is a *second, independent* reason: **exactly the two-facts-one-signal shape (#263) recurring inside the plan's own remedy.** Two consequences: F4's *"the only tool that crosses the gitignore boundary at all"* is **false** — on a plain gitignored directory `ls-files --others --ignored --exclude-standard` returns 2 of 2 — and the applicability condition *"only when run inside a repository where the path is not ignored"* **mispredicts**, since un-ignoring fixes nothing. | Reframe on the **cross-checkout** axis. Drop F4's universal. Record the un-ignored control as its own case — *"it is one command and it is the row that makes the mechanism legible."* |
| C2 | medium | **Issue 1.9 carries two contradictory theses and the bolded one is the refuted one.** It still asserted, in bold, *"the rule is about WHERE the enumerating process runs, **not which flag it passes**"* — the pass-5 thesis — while eleven lines later forbidding `ls-files` alone and `--others` alone. The flag demonstrably matters. Worse, the sentence before it exhibits `git -C <worktree> ls-files --others --exclude-standard` -> **37** as the worked correct answer: **the exact form the same paragraph later forbids.** Residue from bolting the spike's conclusion onto the pass-5 text — *"the incremental-patching pattern that produced five consecutive misses."* | Rewrite around the spike rather than appending. The thesis is **both** which flag and which checkout. Delete the worked example. |
| C3 | low-medium | **"A scoped directory listing" is prescribed as a class whose only measured member is wrong in two directions.** Adding a **symlinked** file: `find -type f` returns 4 against 5 on disk — it *undercounts* where git is right. Adding `.DS_Store` and `.venv/`: `find` returns 6 against git's 5 — it *overcounts*. Neither appears in the spike, and SC10b's fixture cannot discriminate either. | Name the concrete command (`find <dir> ! -type d`). State that the two branches answer **different questions** and pick one deliberately for `draft_present`. |
| C4 | low-medium | **A resolution is again recorded as landed in a form that is not present — the second consecutive instance.** Pass-6's C5 cell claims *"the 37s are marked 'AT THE TIME. Now 0'"*; `grep -c "AT THE TIME" plan.md` -> **0**. The substance landed in different words, so it is a recording defect — but it sits immediately below a cell asserting *"every edit in this round is assert-guarded"*. | Correct the cell. More usefully: **an assert on the edit string cannot catch a resolution cell that describes a different edit.** |
| C5 | low | **Three live counts for the same measurement, unqualified, in the plan that builds the instrument for exactly this.** 40 / 41 / 42 across `plan.md`, the spike, and a fresh measurement; `escalations.md` says 40, `plan-retrospective.md` 41. RE-003 attributes *"After: 41 and 0"* to `a5664e7`, which is **39 files changed**. | Replace absolute counts with the invariant, which does not decay. Fix RE-003's attribution to a commit range. |
| C6 | low | **The `asked_of` fix landed on one entry, not the class.** ESC-001 carries the note; **ESC-002's is blank** — and ESC-002 is the escalation that authorized this pass. Same shape as pass-6 C3's mis-targeted edit, one entry over. | Add the same note to ESC-002. |

## Missing

- **The spike lists `--recurse-submodules` against a fixture containing no submodule.** That row
  measures nested-repo opacity like every other. Add a submodule or drop the row.
- **`core.excludesFile` untested** — immaterial to the listing branch, material to the `git -C`
  branch. One sentence, not a fixture.
- Nothing else; no new structural gap.

## RE-002 and RE-003, reviewed skeptically

**RE-002 is now accurate.** It concedes precisely what pass-6 C3 asked and nothing more; the claim it
retains — a positive control on **conduct**, evidenced by an **absence** — is the only claim the
artifact supports, *"and I could not falsify it."*

**RE-003 is mostly true and partly self-serving, and the bundle contains its own correction.**
*"Neither party could reasonably have connected the two"* is fair for the operator and **not** for
the session, which wrote *"untracked by construction"* about a tracked-ness state in a skill shipping
a `commit-plan` verb. RE-003's own `culpability` cell says exactly that — *"so the entry contradicts
itself, with the self-favourable version in the cell a reader quotes and the honest version in the
cell they don't."* The `prevention` cell's transferable rule is *"the strongest single sentence in
this bundle."*

## Gate Assessment

**Clean.** `gate_consistency.py` PASS, 5 gates, zero findings. Reachability holds at every gate; the
two `Test: none` human gates are correctly typed, since neither authorization has a command that
could establish it. **C1 and C2 raise no gate question** — Issue 1.9 sits outside every `Blocks` set
and both are specification-prose defects.

## Upstream Assessment

**Sound.** 18 rows, zero asymmetries in either direction, zero disposition conflicts.
`#263 (partial)` on Issue 1.9 is *"if anything reinforced by C1: a spike that attributed one signal
to one cause when there are two independent causes is a textbook instance of the class #263 names,
found inside the artifact commissioned to close it."* No disposition changes.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 — the spike mis-attributed the cause | medium-high | **Accepted; independently re-measured before fixing, and the refutation holds.** Case D (worktree **not** gitignored): every git candidate still **0**, `find` 4, `check-ignore` NO. Case E (plain gitignored directory, no `.git` marker): `--others --ignored --exclude-standard` returns **2 of 2** — git crosses a gitignore boundary fine. The spike now carries a CORRECTION section with cases D, E and F, states the mechanism as **nested-repo opacity with gitignore as a second independent reason**, and retires F4's universal. The concession is recorded in the spike's own words: this is #263's class *"recurring inside the artifact commissioned to close it."* | `main-session` | `resolved` |
| C2 — Issue 1.9 held two contradictory theses | medium | **Accepted, and the diagnosis mattered more than the defect.** Issue 1.9 was **rewritten around the spike rather than appended to** — the incremental-patching pattern named as the cause of five consecutive misses. It is now four labelled clauses: (a) which question, (b) which checkout, (c) the prescription, (d) the never-list, (e) the retired premise. The bolded refuted thesis is gone (`grep` -> 0) and the `-> 37` worked example is gone with it (`grep` -> 0). | `main-session` | `resolved` |
| C3 — the listing class is wrong in two directions | low-medium | **Accepted; re-measured (case F).** `find -type f` returned **2** where the answer is `a.md` + `link.md` — it dropped the symlink *and* counted the `.DS_Store`. `find ! -type d` returned 3 (junk included); `git -C wt ls-files -co --exclude-standard` returned the correct **2**. So the prescription is **inverted**: the `git -C` form is now PREFERRED, and the listing is the fallback for when the process cannot run inside that checkout, written `find <dir> ! -type d`. The two branches are stated to answer **different questions**, with `draft_present` assigned to the git form deliberately — a `.DS_Store` is not a draft. **SC10b's fixture now carries a tracked draft, an untracked draft, a symlink and a `.DS_Store`**, each defeating a specific wrong implementation. | `main-session` | `resolved` |
| C4 — a resolution recorded in a form not present, twice running | low-medium | **Accepted.** Pass-6's C5 cell is corrected to say what actually landed and to record that it was itself inaccurate. The general point is taken and recorded verbatim: **an assert on the edit string cannot catch a resolution cell that describes a different edit** — the guard added after pass 6 was necessary and insufficient. The 37s are now gone entirely, because C2's rewrite removed the example carrying them. | `main-session` | `resolved` |
| C5 — three live counts for one measurement | low | **Accepted.** The decaying absolutes are replaced with the **invariant** — the two commands swap which returns N and which returns 0, purely on tracked-ness, with no edit to either — and RE-003's attribution is corrected to the commit **range** `a5664e7..d039600`, noting `a5664e7` alone is 39 files. | `main-session` | `resolved` |
| C6 — `asked_of` fixed on one entry, not the class | low | **Accepted.** ESC-002 now carries the same note. The recurrence is itself the lesson: a per-instance fix to a per-class defect leaves the next instance broken, which is the third time in this bundle. | `main-session` | `resolved` |
| Missing — `--recurse-submodules`, `core.excludesFile` | — | **Accepted.** The spike now carries a "Scope limits, stated" section: the `--recurse-submodules` row claims nothing about submodules and is retained only as a negative result about the worktree case, and `core.excludesFile` is named as untested and material to the `git -C` branch. | `main-session` | `resolved` |
| RE-003 self-contradiction | — | **Accepted.** The adjudication is narrowed to the operator, with the session's half stated plainly: it wrote "untracked by construction" about a tracked-ness state in a skill shipping `commit-plan`, so **no commit needed to happen for the premise to be wrong**. The correction and its cause are recorded in the cell. | `main-session` | `resolved` |
