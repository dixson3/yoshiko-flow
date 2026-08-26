---
type: Finding
okf_spec: OKF-PLAN
id: exp-006-bead-provenance
description: Both #209 remedies are cheap and break nothing — but the corpus severity here is 14%, not 60%, and the citations have migrated into titles
---

# EXP-006: where #209's remedies attach, and what the prepend breaks

**Verdict: BOTH remedies are two-site changes and NOTHING in the repository compares a bead
description to plan text — that absence is what makes remedy (2) cheap. But the corpus
measurement CORRECTS THE SEVERITY downward and surfaces a larger gap the header does not
reach.**

## Attach points — two `jq` calls and two `--description` arguments

`SKILL.md:955-970`, both issue-bead `bd create` calls:

- **Remedy (1)** is literally a third `--arg d "${plan_dir}"` / `plan_dir:$d` in the two
  `jq -nc` calls, mirroring the epic stamp at `SKILL.md:904`.
- **Remedy (2)** attaches at the adjacent `--description="${issue_detail}"`.

**No metadata reader does an exact match.** All four are single-key `.get()`:
`pour_fidelity.py:84`, `verify_beads.py:116` and `:107`, `upstream_render.py:99`. And a
three-key object is **already in production** — `verify_beads.py:124` emits
`{"plan", "plan_issue", "verifies"}` and pour-fidelity joins those beads without complaint.

## The central risk is REFUTED: nothing compares descriptions

`grep -n "descri" -i _shared/pour_fidelity.py` returns **only** `argparse(description=__doc__)`
at line 235. The comparator uses ids, edges, gates and counts — never description text.

Repo-wide, the only code touching a bead's `description` **value**:

| Site | What it does | Effect of the header |
| :-- | :-- | :-- |
| `upstream.py:845` | pushes it as the GitHub issue body | **improves** — the bundle path reaches the issue |
| `beads_hygiene.py:606` | scans title+description for a `plan-NNN` ref to pick a hoist `--dest` | **improves** — today `_dest_for` cannot see `metadata.plan`, so issue beads have no ref |
| `verify_beads.py:125` | **writes** one | unaffected |

`plan_manager.py` has no bead-description reader at all. The #187 control
(`ctl-187-empty-detail.sh`) asserts only on the **extractor's** `detail` field — it never pours
a bead. No test asserts `description == detail`.

> **The "verbatim" identity exists ONLY as SKILL.md prose** (`:989`). There is no `REQ-*`
> asserting it and no executable check enforcing it. So the SPEC-first work here is an
> **amendment**, not a repair — and `REQ-DATA-063` needs no change, since it constrains the
> extractor rather than the pour.

`bd mol distill` is not on this path — yf-plan's issue beads are `bd create`d after the pour,
so #213's gate non-idempotence does not apply.

## Format, round-trip, and limits — all measured on bd 1.1.2

A `·` header round-trips **byte-exact** through `bd`, blank line and all (verified by `od -c`).
The recommendation is still ASCII, because the description also becomes a **GitHub issue body**
and a shell preview:

```
Plan: <plan_id> | Bundle: <plan_dir> (repo-relative)
```

followed by **one blank line**, then the detail. The blank line is load-bearing: without it a
renderer joins the header to the first prose line, corrupting any `detail` that opens with a
list, heading or fence. `Plan:`/`Bundle:` collide with no existing anchored regex —
`upstream.py`'s `EXTERNAL_RE` is line-anchored on `External:`.

`plan_dir` is repo-root-relative and **does** resolve from the execute worktree, since §4.4
lands the bundle before §5.4 cuts the worktree. One caveat for the plan: the worktree sees the
bundle **as of the pinned base** — intake-time content, which is exactly what the descriptions
were poured from, but not later primary-side edits.

**Metadata size is a non-issue:** values of 200 / 1 000 / 4 000 / 16 000 / **65 000** bytes all
round-tripped. A real `plan_dir` is ~40 characters.

**Idempotence is structural.** Beads are created only on the §5.2a `found = false` path; §5.2b
creates none and never rewrites a description. If a backfill verb is ever added,
`bd update --description` **replaces** rather than appends — so the safe shape is
*strip-then-prepend*, which is idempotent by construction.

## The severity correction — and a bigger gap the header misses

Measured across the whole corpus (53 bundles, 1072 issues) by running `plan_extract.py` per
bundle and regexing for `EXP-\d+`, `SC-?\d+`, `(R\d+)`, `pass-\d+`, and bundle-relative paths:

| Scope | Issues citing evidence | Rate |
| :-- | --: | --: |
| `detail` only — **what #187 actually pours** | 152 / 1072 | **14.2%** |
| `title + detail` | 258 / 1072 | 24% |

Density is wildly uneven: plan-040 at 63%, plan-029 at 57% — against **26 of 53 bundles at
exactly zero**.

**The surprise, and it matters:** the four most recent bundles carry **zero** non-empty
`detail` — plan-048 0/39, plan-049 0/43, plan-050 0/28, plan-051 0/23; plan-052 has 1 of 31.
Their authoring style puts all prose on the issue bullet's **first line**, which the extractor
captures as the **title**. Re-run against `title + detail` and plan-050 jumps to **86%**.

So #209's 60% reproduces here — but only in a **high-density minority**, and in this repo the
citations have largely **migrated into titles, where remedy (2) does not reach them at all.**

**Honesty the plan must carry.** #209's author filed this low-to-medium because every operative
instruction restated its evidence, and that holds here too. On this repo's four newest plans
the poured descriptions are **empty**, so there is currently nothing in them to be
unresolvable. A header on an empty description is pure gain — it makes an otherwise-blank
description locatable — but the *urgency* argument does not survive contact with this corpus.
Cite the 14.2% mean alongside the 63%/86% peaks; do not cite the peaks alone.

**A distinct gap this surfaced:** title-borne citations. Scope it explicitly out (recommended —
the header still makes the bundle findable from the bead) or file it separately. Do not let the
plan imply the header resolves them.

## Recommendation

Do both, at the two `bd create` sites, plus an amendment to the §5.2a prose at `:989` that
currently asserts the verbatim identity. Land a new `REQ-*` whose verification asserts (a) a
poured issue bead's metadata carries all three keys and (b) its description's first line
matches `^Plan: \S+ \| Bundle: \S+`.

**Do NOT add a description-equality check anywhere.** The absence of one is what makes this
change safe; adding one would re-create the coupling #209 needs broken.
