---
type: Reference
okf_spec: OKF-PLAN
---
# Issue 2.5 — replay results

Falsifiability check for the amended `red-team.md` (plan-039 R1). Four fixtures, each
reviewed in a **fresh session with no access to this plan**, its findings, its reviews, or
the drafting conversation — given only the amended `red-team.md` and **one fixture at a
time**, with no statement of what defect it contained or that it contained one at all.

A replay that already knows the expected answer proves nothing. Each session was
instructed to read only those two files and to review the document on its own terms.

Run 2026-08-15 against `skills/yf-plan/agents/red-team.md` at commit `d2b4a10`.

## Outcomes

- FLAGGED `replay-plan-013-gate.md` — new: gate reachability (2.2 / REQ-AGENT-046)
- FLAGGED `replay-plan-014-premise.md` — new: premise check (2.3 / REQ-AGENT-048)
- FLAGGED `replay-plan-013-epic6.md` — new: precondition cross-check (2.4 / REQ-AGENT-047)
- FLAGGED `replay-plan-013-capability.md` — **existing** checks (no-regression fixture)

All four flagged. No revision cycle was needed, so the one-cycle-per-fixture cap (2.5) was
never approached and no tuning occurred.

## Fixture provenance — read this before trusting the fixtures

The three plan-013/014 fixtures needed text *as it was before review fixed it*. A dedicated
evidence sweep established that **only two of the four survive verbatim**, and this section
records that honestly rather than presenting reconstructions as captures.

| Fixture | Provenance | Source |
| :-- | :-- | :-- |
| `replay-plan-013-gate.md` | **VERBATIM** | d3-pxe commit `e4d69a7`, `plan-013.../plan.md` — the gate block quoted exactly |
| `replay-plan-014-premise.md` | **VERBATIM** | `plan-014.../findings/exp-001-otel-fleet-live-state.md` §4, single-commit file never amended |
| `replay-plan-013-epic6.md` | **RECONSTRUCTION** | the as-landed Epic 6 with the `depends-on` line and its explanatory Note removed |
| `replay-plan-013-capability.md` | **RECONSTRUCTION** | rebuilt from the defect as described in `plan-013.../reviews/pass-1.md`, which quotes only the fragment `byte-identical to pre-change for all 8 guests + host` |

**Why two are reconstructions.** Both d3-pxe bundles were committed to git *only after*
intake approval. Every pass-0 and pass-1 fix therefore predates the first commit, so the
pre-fix text never entered version control. A full sweep confirmed this — all four
`reviews/pass-*.md`, `git log -p --follow` on both plan.md files, all branches, the stash,
the reflog, and every blob in the object store over 20 KB. The pre-fix Epic 6 does not
exist anywhere in the object database; the reviews *describe* the defect but never quote it.

The one defect whose pre-fix text **does** survive verbatim (the gate) survives precisely
because it escaped all three review passes and was fixed mid-execution, after the intake
commit — which is also why it is the defect that motivated #112.

**Structural finding worth carrying forward:** if pre-fix fixtures are wanted reliably in
future, the plan folder must be committed at *plan v1 presented*, before the review cycle
runs. Today the review prose is the sole record of what a plan looked like before review.

**A correction to this plan's framing of the plan-014 defect.** plan-039 describes it as
"an inference (`the CT rebooted`) recorded with the confidence of a measurement
(`uptime -s`)". The sweep found that `uptime -s` **was** actually run — the measurement is
real. The defect is subtler and worse: `uptime -s` reports *last boot*, and CT 107 had been
**destroyed and re-created** ~16 seconds earlier, so it reported the container's *first*
boot. A genuine measurement was read as evidence of a reboot that never happened. This
strengthens the fixture rather than weakening it: it is exactly the case where marking a
conclusion `measured` is insufficient and REQ-AGENT-048's falsification question is what
catches it. (The refutation is recorded in the source bundle's own
`findings/exp-003-otel-boot-mechanism.md`: *"There was no reboot. CT 107 was destroyed and
re-created."*)

## Verbatim excerpts

### 1. `replay-plan-013-gate.md` → FLAGGED (gate reachability)

Verdict `REVISE`. The **first concern listed**, at high severity:

> **The capability gate is unreachable as written — its `Condition` depends on evidence
> produced inside its own `Blocks` set** — severity: high
>
> The gate `Blocks: 5.1`. Its `Condition` requires the operator to have previewed
> `ansible-playbook host.yml --check --diff --tags otel_agent` and `guests.yml --check
> --diff` **for Issue 5.1**. But Issue 5.1 is the issue that *authors the role change* […]
> The gate blocks the step that produces the evidence the gate demands. This is a cycle,
> and the on-the-ground resolution will be an operator quietly working around the gate,
> which is worse than having no gate.
>
> Recommendation: Gate the mutating step, not the evidence-producing step. Split 5.1 into
> 5.1a "author the role change and produce the `--check --diff` preview for host and
> guests" (ungated — check mode is non-mutating) and 5.1b "apply fleet-wide" […] Move the
> capability gate to `Blocks: 5.1b`.

And in the Gate Assessment section:

> Its `Condition` requires a `--check --diff` preview *of Issue 5.1's change*, while
> `Blocks: 5.1` prevents 5.1 from authoring that change. Evidence required by the
> condition is produced inside the blocked set — a cycle.

**This is the defect that survived conformance and two full red-team cycles in the original
plan.** The amended prompt caught it on the first pass, and independently proposed the
5.1a/5.1b split that the real plan-013 eventually adopted mid-execution.

### 2. `replay-plan-014-premise.md` → FLAGGED (premise check)

Verdict `REVISE`. The premise check fired under its own name, with the falsification
question asked and answered:

> **Premise check — "the unit is `enabled`, so it should have been pulled in at boot" is a
> present-tense measurement projected backward, and the plan never checks whether it held
> at boot time.** — severity: high
>
> This is the load-bearing inference under the entire Approach […] But `enabled` was
> observed ~23 h 38 m after the boot in question — *and the plan tells us that someone was
> actively modifying this unit's configuration during that window* […]
>
> **What would falsify it, and was it checked?** Falsifiers are cheap, read-only, and none
> were run: `stat` the symlink in `/etc/systemd/system/*.wants/` for its mtime; `stat` the
> unit file and the EnvironmentFile; `systemctl show otel_agent -p WantedBy` […]

It also independently reached the neighbourhood of the true root cause — that the machine's
state had changed and the incident conditions no longer existed:

> **The system state has changed since the incident, so Issue 1.1 no longer reproduces the
> original conditions.** — severity: high

And it separated measured from inferred without being asked to, listing the four signals as
genuinely measured while challenging what was concluded from them:

> The timeline evidence is genuinely measured, not inferred: `uptime -s`, journal start
> timestamp, `journalctl -u otel_agent` empty, `ActiveEnterTimestamp` empty, `NRestarts=0`.

Note what this means: the fixture's finding is *four real measurements plus one wrong
inference*, and the check correctly attacked the inference while crediting the
measurements. That is the discrimination REQ-AGENT-048 exists to produce.

### 3. `replay-plan-013-epic6.md` → FLAGGED (precondition cross-check)

Verdict `REVISE`. High severity, naming the missing edge and the node that needed it:

> **Epic 6 has no declared dependency on Epics 1–5, yet its every issue presupposes their
> completion.** — severity: high
>
> 6.1 re-audits "the hardened tree." 6.2 writes a verdict "against the re-audited tree."
> […] Nothing prevents 6.1 from being claimed and run against an unhardened tree the moment
> the Start Gate opens. If that happens the re-audit measures the wrong tree […] **The
> failure is silent — every issue closes green and the output is wrong.**
>
> Recommendation: Add explicit `depends-on` edges from 6.1 to the terminal issue of each
> hardening epic (1.4, 2.3, 3.4, 4.2, 5.4).

The recommended edge set matches the remedy the original plan-013 review actually applied.
The same pass also caught a second precondition failure — 6.1's evidence source ("the new
gates' actual output") referring to gates the plan never declares.

**This fixture exists because pass-2 H3 found that 2.4 — the item discharging #113's
`partial` disposition, which Issue 5.2b announces upstream as shipped — had no evidence it
fires at all.** It now does.

### 4. `replay-plan-013-capability.md` → FLAGGED (existing checks — no regression)

Verdict `REVISE`. The pre-existing capability-gap check still fires at high severity:

> **No capability gate establishes fleet access, yet two of three criteria require it.** —
> severity: high
>
> SC7 and SC14 both require executing playbooks against the host and 8 guests. That needs
> inventory, SSH reachability, credentials, and a maintenance window. The only gate is a
> human Start Gate, which approves *intent*, not *capability*. Verification will be
> discovered to be impossible at the moment it is attempted.

**This is the R2 dilution check, and it passes.** Adding three items to the Evaluate section
did not degrade the checks that already worked. The new items fired *alongside* the existing
one on the same document rather than crowding it out — this pass also produced a
precondition cross-check table and a four-item premise check, and still surfaced the
capability gap as a top-line high-severity concern.

Worth noting: the same pass independently observed the gate-reachability rule as *guidance
for the fix it was recommending* —

> It must not block whatever establishes connectivity — gate the mutating and measuring
> steps, not the enabling one.

— which is the REQ-AGENT-046 rule being applied constructively rather than only as a defect
detector.

## Assessment against R1

R1's claim was that three prompt additions could be made and simply never fire, with no way
to tell. That is now falsified by observation: each new item fired on the fixture built for
it, at high severity, with a specific and correct remedy, in a session that did not know
what it was looking for. The existing checks continue to fire (fixture 4).

The honest limit: this is **one observation per check**, on defects drawn from **two plans
in one repository, authored by one operator**, and two of the four fixtures are
reconstructions rather than verbatim captures. It establishes that the checks *can* fire on
the defect class they were written for. It does not establish a rate, and it does not
establish that they fire on defects unlike these. The re-measure checkpoint filed by Issue
5.3 is what would begin to answer that.
