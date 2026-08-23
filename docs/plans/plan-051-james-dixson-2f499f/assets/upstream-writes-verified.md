---
type: Reference
okf_spec: OKF-PLAN
id: upstream-writes-verified
description: Structural verification of every upstream write — an exit 0 is not proof
---

# Upstream writes — verified STRUCTURALLY

**An exit 0 is not proof.** Each write below was verified by reading the result back from
GitHub, not by trusting `gh`'s return code.

## The tracker (Issue 4.3)

Filed **through `/yf-beads-upstream`** (`upstream.py push --issues yf-mol-3he --apply`), never a
bare `gh issue create` — a tracker filed by hand records no mapping, which is how five earlier
trackers went stale.

| Check | Result |
| :-- | :-- |
| returned URL on create | `https://github.com/dixson3/yoshiko-flow/issues/200` |
| URL resolves to a real issue | **#200 OPEN** — `plan-051-james-dixson-2f499f execution tracking` |
| **SC12b** — the epic carries `external_ref` | **yes** — `yf-mol-3he` → the #200 URL |
| title has no doubled prefix | **correct** — the template is `<plan-id>`, and a plan id already begins with `plan-` |

The dry run (absent `--apply`) previewed exactly **1 create** and was inspected before applying.
One label, `type::molecule`, was dropped as non-existent upstream (restrict-and-drop,
`REQ-BUP-056`).

## The seven comments (Issue 4.4)

Each body was posted with `--body-file` from the **authorized** grant text, then **read back**
from GitHub and compared:

| Issue | Comment URL | Body read back | Plan-id mention |
| :-- | :-- | :-- | :-- |
| #182 | `…/issues/182#issuecomment-5387888375` | **identical** | yes |
| #184 | `…/issues/184#issuecomment-5387888420` | **identical** | yes |
| #149 | `…/issues/149#issuecomment-5387888502` | **identical** | yes |
| #165 | `…/issues/165#issuecomment-5387888580` | **identical** | yes |
| #173 | `…/issues/173#issuecomment-5387888647` | **identical** | yes |
| #174 | `…/issues/174#issuecomment-5387888707` | **identical** | yes |
| #150 | `…/issues/150#issuecomment-5387888774` | **identical** | yes |

The readback showed a consistent **1-byte** delta on all seven. That was **checked, not assumed**:
it is `gh -q`'s trailing newline. With trailing whitespace normalized, all seven SHA-match the
authorized text.

The plan-id mention is not cosmetic: `_verify_row` maps `partial` → `requires_mention: True` and
returns `fail: "no comment mentions <plan_id>"` otherwise — and `verify-reconcile` runs **after**
the outward writes have begun.

## The two closes

| Issue | End state | Reason |
| :-- | :-- | :-- |
| #182 | **CLOSED** | `COMPLETED` |
| #184 | **CLOSED** | `COMPLETED` |

**Nothing else was closed.** The five `partial` rows (#149, #150, #165, #173, #174) and the
tracker #200 were confirmed still **OPEN** by readback — matching the grant exactly.

## The two out-of-scope defects (Issue 4.6)

Both **reproduced before filing**, not taken on report.

| Issue | Defect | How it was established |
| :-- | :-- | :-- |
| [#201](https://github.com/dixson3/yoshiko-flow/issues/201) | repeated `--changed` silently drops all but the last path | read at source (`change_validation.py:946` — `nargs="*"`, no `action="append"`) **and** demonstrated with the same parser config: `['--changed','A','--changed','B']` → `['B']` |
| [#202](https://github.com/dixson3/yoshiko-flow/issues/202) | a cancelled `bd mol burn` exits **0** | **reproduced**: poured a throwaway molecule with an open gate, burned it with empty stdin — printed `Canceled.`, exited **0**, molecule still present and `open`. Probe cleaned up with `--force`; no residue |

#202's reproduction is the reason R5's mitigation is worded as it is: `--force` **and check the
output, not the exit code**. Verified during cleanup — the successful `--force` burn also exits 0,
so the exit code distinguishes nothing in either direction.

## Nothing beyond the grant was closed

`closable` is run **propose-only** at land-the-plane and brought to the operator. A clean run
does not mean nothing needs closing: hand-filed coarse trackers carry no bead mapping and are
invisible to it.
