---
type: Note
okf_spec: OKF-PLAN
---

# Gate pre-work RED runs (Issue 1.4 / SC9d)

Each `<gate>.txt` records the **gate `Test:` string** — not the bare script — executed against
the tree *before* the work that makes its condition true, with its exit code, the script's JSON
verdict, and the stderr tail.

Archiving the pipeline rather than the script is the point. Without `set -o pipefail` a pipeline
reports jq's status alone, so "script missing" (127) and "assertion failed" become
indistinguishable — and it was a bare-script run that made the drafted gates look tested when
what the resolver actually runs is the pipeline.

## Result: all four RED at exit 1, for reason 1 only

| Gate | script exit | JSON verdict | why it is red |
| :-- | --: | :-- | :-- |
| `doclint` | 1 | `{"commands":[],"engine_status":"pass"}` | **the vacuous green, verbatim** — §3 has no `docs/plans/**` glob, so a plan edit selects zero commands and the FAST tier reports `pass`. Satisfied by Epic 3. |
| `carveouts` | 1 | `{"carved_findings":0,"control_fired":false}` | the positive control does not fire yet. Satisfied by Epic 2. **See the note below — this one taught us something.** |
| `normalizer` | 1 | `{"diff_bytes":0,"fingerprints_moved":null,...}` | `assets/normalizer-aggregate.diff` does not exist. Satisfied by Issue 8.8a. |
| `upstream` | 1 | `{"comments":1,"auth":true}` | 1 `comment-*.md` exists against a threshold of 8. **The drafted Test asserted only that *some* comment file existed and was therefore already green** (review M7). |

## The exit-code discipline, falsified rather than asserted

Three properties, each executed:

1. **An empty stub cannot satisfy the gate.** `: > gate-doclint.sh` makes the bare script exit
   **0** — measured, and the gate resolver is exit-code only, so an assertion *inside* the script
   could not stop it. The gate `Test:` exits **4**, because `jq -e` gets no input. The assertion
   living *outside* the artifact it polices is what closes this.
2. **A harness failure is exit 2, not exit 1.** An unresolvable required tool, and an
   unsourceable `_common.sh`, both yield `{"harness_ok":false,...}` and exit **2** — with none of
   the gate's assertion keys present, so `jq -e` cannot read a harness failure as a satisfied
   capability.
3. **A missing script is non-zero.** `bash gate-nonexistent.sh | jq -e ...` exits 4. Note the
   honest bound: at the *pipeline* level that is not distinguishable from an assertion failure.
   The distinction lives in the committed script's own 0/1/2, which is why the scripts are
   committed files rather than inline one-liners.

## A defect found by running the falsification, not by writing it

Property 2 **failed on the first attempt**: with `_common.sh` unsourceable, `need` and
`harness_fail` were undefined, the script carried on regardless, and a genuine harness failure
was reported as **exit 1 — "capability absent"**. That is precisely the misclassification the
0/1/2 discipline exists to prevent, reproduced inside the mechanism built to prevent it. Fixed
by making the source fail-closed (`. _common.sh || { …; exit 2; }`) in all four scripts, and
re-verified.

## A second, still-open one: the `carveouts` control is currently vacuous

`control_fired: false` is the *correct* verdict today, but not for the reason the gate
intends. `--no-exclude` finds 0 findings in the carved regions because `finding.toml`'s
`paths` glob is `docs/plans/*/findings/*.md` — a **single** level, which does not reach
`findings/okf-migration-samples/**/…` at all. So the carve-out is not being *tested*; the files
are simply never selected. **Epic 2 (Issues 2.2–2.4) must widen the `paths` globs to recurse
before declaring the carve-out globs**, or the positive control stays decorative — a control
that cannot fire is the same defect class as a gate that cannot fail.
