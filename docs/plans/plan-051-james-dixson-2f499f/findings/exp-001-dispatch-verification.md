---
type: Finding
okf_spec: OKF-PLAN
id: exp-001
description: For #184's new REQ-AGENT-*, what can a Verification line assert with an exit code?
---

# EXP-001 — what #184's `Verification:` line can honestly assert

## Approach Tested

Classified all 26 `Verification:` clauses in `skills/yf-plan/spec/agents.md`; grepped SKILL.md's
Phase-3 span and all 7 `agents/*.md` for the RED; enumerated frontmatter keys across **141**
`reviews/pass-*.md`; read `yf/src/marker.rs` and `yf/src/parity.rs`; and built a sandbox spike under
a throwaway `HOME` that installed skills, tampered a deployed file, reimplemented the tree hash in
Python, and **tried to game each candidate check**. Sandbox deleted; repo untouched.

## Result

**measured:** `spec/agents.md` has **0 of 26** exit-code-decidable Verification clauses. REQ-AGENT-040
through 048 are all prose naming a document (9/9). The single clause containing a command
(REQ-AGENT-001) **exits 0 with a match** when run, because it carves out "(except the prohibition
itself)" in prose. So a prose Verification for #184 would be in keeping with the file — but this plan
can do better, and #165 says it should.

**measured:** **no REQ covers WHO RUNS the review.** `REQ-AGENT-020` is the only dispatch-specifying
requirement and it is the *investigator*. `REQ-AGENT-043` covers read-only-ness and is deliberately
actor-agnostic about the *resolver*. Grep for `dispatch|sub-agent|Agent tool` across
`skills/yf-plan/spec/*.md` returns nothing on the review axis. **A new id is required, not an
amendment.**

**measured:** the RED is genuine and section-scoped. `grep -c 'Agent' skills/yf-plan/agents/*.md` → **0**
for all seven. `awk '/^### Review$/{f=1} f&&/^### Portability audit/{f=0} f' SKILL.md | grep -q 'Agent'`
→ **exit 1**.

**measured:** highest existing id is **`REQ-AGENT-064`**; used set is 001-006, 010-013, 020, 021, 030,
031, 040-048, 050, 051, 060-064. **`REQ-AGENT-049` is free and sits inside the red-team block.**

### Candidate 1 — deployed↔source parity: REAL, and stronger than D-8 knew

**measured:** D-8 called this "class M3" without naming a mechanism. One is already shipped —
`REQ-YF-MARK-001/002` in `yf/src/marker.rs`. Every deployed `SKILL.md` carries
`<!-- yf-skills: v=… tree=<sha256> -->`, hashed over the skill's files sorted by relpath with
`SKILL.md` marker-stripped and residue (`*.pyc`, `__pycache__`, `.DS_Store`, …) excluded on both
sides. A ~25-line Python reimplementation over **repo source** reproduced the deployed markers
exactly:

| Tree | tree hash |
| :-- | :-- |
| repo `skills/yf-plan` | `a63ba8c1…f0f9` |
| `~/.claude/skills/yf-plan` | `a63ba8c1…f0f9` (marker matches) |
| `~/.agents/skills/yf-plan` | `a63ba8c1…f0f9` (marker matches) |
| tampered (+1 line in `agents/red-team.md`) | `514f1491…` — **detects** |
| noise (+`.pyc`, +`.DS_Store`) | `a63ba8c1…f0f9` — **no false positive** |

**measured:** `yf skills status` **exits 0 even when the tree is modified** — tampering flipped
`"unmodified":false` while `EXIT=0`. It is usable only wrapped:
`yf skills status yf-plan --json | jq -e '[.skills[]|select(.unmodified==false)]|length==0'` → exit 1
on the tampered tree.

**CORRECTED — the finding's supporting example was false.** It claimed `yf --version` was `1517ced`
while `HEAD` was `e2853a9`. Re-measured at the repo root: **both are `1517ced`**. The architectural
caveat survives the correction — `yf skills status` genuinely compares deployed against the
**binary's embedded** tree, not the repo, so a green there is not a repo-parity claim — but the
example offered as evidence for it did not hold.

**What parity does not prove:** that the sentence shipped intact to every surface, and nothing more.
It is a check on the *text*, one level removed from conduct.

### Candidate 2 — text-presence: WEAK, and the naive form is already vacuously GREEN

**measured:** `grep -q 'Agent' skills/yf-plan/SKILL.md` → **exit 0 today**, on the un-fixed tree,
because `Agent` appears at `SKILL.md:21` in the frontmatter `allowed-tools:` list. Shipping the
whole-file form would manufacture a green — the exact M5 vacuity class.

**measured, by gaming it:** the section-scoped form is satisfied by a **prohibition of the thing it
checks for**. Appending `"Do NOT use the Agent tool here; run the review in-session."` → **GREEN**.
Appending `<!-- Agent -->` → **GREEN**.

### Candidate 3 — per-plan provenance: ABSENT

**measured:** across **141** `reviews/pass-*.md`, the complete frontmatter key set is `type`(81),
`okf_spec`(81), `status`(35), `id`(34), `plan`(25), `verdict`(23), `created`(22), `pass`(20),
`date`(3), `plan_version_reviewed`(2). **No key records who produced the review.**
`_shared/document_types/review.toml` has no provenance check; `plan_manager.py` writes none. The only
provenance is ad-hoc body prose — 24 `**Reviewer:**` lines, exactly **two** saying `independent
sub-agent`. It would be **self-attestation** anyway: the same actor that skipped the dispatch writes
the field.

### Candidate 4 — transcript mining: real signal, wrong artifact

**measured:** across this repo's 64 Claude Code transcripts, **353** `Agent` dispatches, of which
**66** match `^Read .*agents/red-team\.md`. So dispatch is already common practice. But it is
harness-local, lives outside the repo (breaking the portable-bundle doctrine), is user-local and
unretained, and **does not reconcile** — 66 dispatch records against 141 pass files, so as a gate it
would fail roughly half the corpus for reasons that are not defects.

## Implications for Plan

1. **The behavioral claim has no exit code, and the plan must say so.** Nothing portable and
   non-gameable can assert *"a reviewer was actually dispatched."* D-8's conclusion for #182
   transfers to #184 intact.
2. **But #184 is strictly better off than #182 was**, and the plan should say that precisely rather
   than reusing D-8's wording. #182's claim was pure prose-obedience; #184 has a real substrate
   (tree-hash parity, shipped and reproduced from scratch) and a genuine, observable RED.
3. **The naive text-presence form must not ship** — it exits 0 on the un-fixed tree today.
4. **`yf skills status` must never be cited bare** — exit 0 on modified, measured.
5. #184's requirement lives in `SKILL.md` Phase 3, **not** `red-team.md`, so a parity assertion
   scoped to `agents/` would not cover the requirement's own text.

## Recommendations

1. **Use `REQ-AGENT-049`** — free, and inside the 040-048 red-team block.
2. **Verification = two mechanical clauses plus an explicit honesty clause.** Clause 1: the
   **section-scoped** `awk … | grep -q 'Agent'` (currently RED, so it distinguishes before/after).
   Clause 2: deployed↔source parity via the tree hash (currently GREEN — a **regression guard**, not
   evidence of the fix; the plan must not let it read otherwise). Clause 3: the D-8 honesty clause,
   stating plainly that obedience has no exit code and a presence check is satisfiable by a
   prohibition.
3. **Do NOT use candidate 3 or 4 as the enforcement mechanism** — self-report and half-corpus failure
   respectively.
4. Optional and non-load-bearing: add `reviewer_dispatch:` to `review.toml` at severity `R` so future
   passes leave a structured trace. **Must not be cited as verification of REQ-AGENT-049.**
