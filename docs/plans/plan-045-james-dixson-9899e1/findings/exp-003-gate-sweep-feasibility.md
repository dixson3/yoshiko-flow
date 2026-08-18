---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-gate-sweep-feasibility
plan: plan-045-james-dixson-9899e1
created: '2026-08-17'
---

# exp-003 — Gate-sweep feasibility (D-4) — REFUTES the scoped design

**Question:** Is an execute-start capability-gate sweep mechanically implementable?
**Method:** read of the §5.2a `bd create` recipe, live read-only inspection of **113 gate beads** (`bd gate list --all`), a corpus survey of 34 `- Test:` lines across 45 plan bundles, and timed execution of the probe-class tests. No bead mutated; no build run.

## Verdict

**Mechanically implementable — but the design target as stated is wrong on three counts.** The
cost is negligible; **the semantics are the blocker.**

## 1. Gates carry no structure at all

The §5.2a recipe stores everything as freeform prose:

```bash
bd create "Gate: ${gate_name}" \
  --description="Condition: ${condition}\nTest: ${test_cmd}\nInstructions: ${instructions}" \
  -t gate --parent ${EPIC}
```

`bd show --json` on a gate returns only `id/title/description/status/priority/issue_type/
dependencies/parent`. **No `gate_type`, no structured test field, no metadata.**

Corpus of 113 gates: 48 poured start gates, 29 reconcile gates, **36 capability gates**.

**Two measured corruptions.** *Literal `\n`* in 3 of 113 — bash double quotes don't interpret
`\n`, so `--description="…\nTest: …"` stores the two-character escape. Whether a gate is corrupted
depends on how the authoring agent happened to type it. And *lossy flattening*: plan-037's fenced
multi-line bash Test lost its fences, joined its `\`-continuations, and left `Test:` **empty** with
the command on following lines terminated only by the next label.

## 2. The parse fails — this is the real feasibility gate

Over the 36 capability gates, after normalizing literal `\n`:

| Parse outcome (`(?m)^Test:\s*\S`) | Count |
| :-- | --: |
| **STRICT** — usable command on the same line | **15** |
| LOOSE — a `Test`-ish label a strict regex misses | 15 |
| NOTEST — no test text at all | 6 |

**58% (21/36) do not yield a command to a strict regex. Machine-runnable yield is ~12/36 (33%).**

Failure modes, all real strings:

- **Decorated labels — the largest class.** `Test (plan text, hardcoded ids):`,
  `Test (SMOKE CHECK ONLY — it proves read access, NOT that a write was authorized …):`,
  `Test (NEGATIVE assertions are what matter — pass-1 C13):`. Authors annotate the label, moving
  the colon.
- **Mid-sentence `Test:`** — `"Condition: dist 0.32.0 installed & runnable. Test: dist --version
  (expect 0.32.0). Blocks Issue 1.1."` — all labels on one line.
- **Colons inside commands** — `grep -c ": test$"`, `--query "HostedZones[?Name=='…']"`.
- **Prose, not commands** — `Test: human review; sample migrations apply cleanly`;
  `Test: the Issue 1.2 test (in-suite via cargo test, or …)`.

> **The worst brittleness:** a regex cannot tell a command from a sentence, and will hand `sh -c`
> a sentence. It fails **loudly and wrongly** — a nonzero exit reported as "gate FAILED" rather
> than "not machine-testable", flooding the very prompt the batching was meant to clean up.

## 3. Auto-resolving on green would grant consent that was never given

`Type:` lives in plan.md, **not on the bead — only 3 of 113 gate beads carry a `Type:` line**,
because the §5.2a template omits it entirely. On the plan.md side, across 34 capability gates:

| `- Type:` | Count |
| :-- | --: |
| **`human`** | **20 (59%)** |
| `auto` | 12 |
| malformed / absent | 2 |

The template's own default for a capability gate is `- Type: human`, and authors follow it. For
those the `Test:` is **evidence for the operator, not the release condition** — the gates say so:

> `Test (SMOKE CHECK ONLY — it proves read access, NOT that a write was authorized; the Condition
> is the contract. **NEVER treat a green test here as consent**)`

Two `Gate: Upstream write` gates have `Condition: operator … authorizes publishing against
dixson3/yoshiko-flow` with a test (`gh auth status && test -s <file>`) that is **green whether or
not the operator authorized anything**.

> **A sweep that auto-resolves on green would silently grant publish authorization on at least
> three historical gates** — the only thing standing between the coordinator and an outward-facing
> GitHub write.

## 4. Most auto gates are DESIGNED to fail at t=0

They assert the plan's **own deliverables**: *"push verb exists before the prose points at it"*,
negative greps on files the plan will edit, `test -s …/decisions/config-tier.md` (a file Issue 2.1
creates), "the Issue 1.2 test". Sweeping them at execute start produces a batch of **expected
failures carrying no information**.

Only the **environment/precondition subset** — toolchain present, credentials present, corpus
present — is meaningfully evaluable before work begins. Roughly **12 of 36**.

## 5. Standalone bug found: `bd ready` never returns gates

Measured: `bd ready --json` returned 20 beads, **none of type `gate`**, while two gates were open.
`bd list` hides gates behind `--include-gates`; `bd ready` has no such flag.

> So `coordinator.md` loop step 2 — *"For gate-type beads: read description, run test command"* —
> **operates on a list that never contains a gate.** The existing lazy mechanism is already
> broken. This is worth fixing regardless of what this plan decides about sweeping.

## 6. Cost

All twelve probe-class tests, timed against the live repo: **~3s total** (`d2 --version` 0.14s,
`gh auth status` 0.98s, `bd version` 0.46s, `test -s …` 0.02s, …). For probe-class the sweep is
**free**.

The cargo/full-tier class is where cost lives — plan-044's own gate is
`cargo test -p yf --test harness_cross_e2e`. *(Not measured — running it would write to `target/`
in a live-executing repo.)* The corroborating signal: the always-loaded rule characterizes the
FULL tier as *"the multi-minute gate paid once per land — not on every on-edit step."*
Front-loading it inverts that principle and pays a cost that would otherwise be skipped entirely
if the gated work were never reached.

## 7. Placement, and `bd gate resolve` semantics

**Insertion point: between `worktree ensure` (step 9) and §5.3 (step 10).** After `worktree
ensure` for a stronger reason than "tests may need the worktree": §5.3's address-space model
routes *code* operations to the worktree and *plan-folder* operations primary-side. The sweep
cannot route a test correctly until the worktree path exists. It must also run **after** the
start-gate resolve, so it does not compete with REQ-SESSION-001.

**Reuse, don't duplicate:** §6.1.5 already says *"**Layer (a)** — the plan's own Gate `Test:`
commands — runs against the merged checkout in the §5.3 coordinator loop."* A sweep is a
**relocation of layer (a) from lazy to eager** — extract one shared routine or the two will drift.

`bd gate resolve` has **no precondition** — *"equivalent to `bd close <gate-id>` but with a more
explicit name"*. It does not consult the description or evaluate a condition. Bulk resolution
releases N blocked sub-graphs at once, so the next `bd ready` returns a far wider frontier than the
operator saw. Reversible via `bd reopen` — but **the downstream work the release triggers is not.**

## Recommendations

1. **Do not implement "run all gate Tests at execute start."** Implement **"classify all gates at
   execute start, run only the SAFE-PROBE class, and batch everything else into one prompt."**
   The batched-prompt half — the actual win — needs **no test execution at all**: enumerate every
   gate, report Condition/Type/Blocks, ask once.
2. **Make the gate a structured bead before making it sweepable.** Add fields the sweep can trust
   rather than parse:
   `--metadata '{"gate_type":"human|auto","test":"<cmd>","test_class":"probe|build|consent|manual","cwd":"repo-root|plan-dir"}'`.
   Keep the prose for humans. **This is the single change that converts the sweep from brittle to
   mechanical, and it costs one line in §5.2a. Without it, do not build the sweep.**
3. **Fix §5.2a's `--description` to emit real newlines** (`printf` or `$'…'`) so the literal-`\n`
   class stops growing.
4. **Hard-exclude `Type: human` from auto-resolution, permanently and by default.** Where `Type:`
   is absent from the bead (110 of 113), fall back to plan.md; where absent there too, **default
   to human**.
5. **Gate the expensive class behind an opt-in** (`--sweep-gates=probe|all`, default `probe`).
6. **Treat a non-zero exit as INCONCLUSIVE, not FAIL, when the test text is not clearly a command**
   — measured stale-id failures (`bd show yf-9c09122b.1` now exits 1; the id no longer exists) and
   prose tests would otherwise dominate the prompt with false alarms.
7. **cwd is prose-encoded and inconsistent** — one gate says *"paths are plan-dir-relative"*,
   another *"repo-root-relative"*. No structured field carries it; a wrong choice yields a **false
   FAIL**. Covered by recommendation 2.
