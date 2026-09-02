<!-- Draft for a NEW issue. Not filed by the executing session: `gh issue create` is an
     outward-facing write. File with:
       gh issue create --title "<title below>" --body-file <this file> --label bug
     Strip this comment before posting. -->

**Title:** `land`'s `draft_body_path` posts bundle files verbatim, but OKF requires them to carry frontmatter

## The conflict

Two requirements apply to the same file and cannot both be satisfied:

1. **`land` L7 posts the file verbatim.** `_land_l7_reconcile_writes` runs
   `gh issue comment <n> --body-file <draft_body_path>` (`plan_manager.py:9043`). No
   frontmatter stripping happens anywhere on that path. The read-back verification then
   compares `Path(body_path).read_text().strip()[:200]` against the posted comment
   (`:9059`), so the check actively *depends* on the file being posted byte-for-byte.

2. **OKF requires frontmatter on every bundle `.md`.** `plan_manager.py audit` reports
   `REQ-OKF-003: no YAML frontmatter block` for each file under
   `assets/upstream-drafts/`, and a `fail` audit blocks `ready-check`, which blocks
   approval.

The manifest itself picks the location — `_land_upstream_facts` computes
`draft_body_path` as `<plan_dir>/assets/upstream-drafts/<issue>.md` — so the collision is
structural, not a choice any individual plan made.

**Adding an OKF exclusion is explicitly forbidden** and correctly so.
`skills/yf-plan/OKF-EXTENSION.md` §3b says:

> **These are the fixture carve-outs, and NOTHING ELSE.** … Adding a row to silence a
> finding on a live bundle member converts the conformance check into a record of what
> someone did not want to look at.

## Measured, not inferred

Three prior plans have used `assets/upstream-drafts/`: plan-049, plan-057, plan-059. All of
their draft files **do** carry frontmatter today. But the comment actually posted on
**#140** (plan-057's draft `140.md`) begins `## The conformance gate has a phase-shaped
blind spot`, with **no YAML block** — so that frontmatter was added *after* posting, by a
later OKF backfill.

That is why the conflict has never been observed: **every prior use predates the frontmatter,
and no plan has yet run `land --apply` against drafts that already have it.** plan-061 is the
first, because its drafts were authored and then frontmatter-stamped in the same session to
clear the audit.

## Why it matters more than cosmetics

The obvious harm is a YAML block rendered atop six public GitHub comments. The subtler harm
constrains how this may be fixed: the **read-back verification** compares the first 200
characters of the *file* against the posted body. So an in-`L7` fix that strips frontmatter on
the way to `--body-file` while leaving the file intact would make the two differ in exactly the
region the verification samples — `ok` goes `False` on a write that genuinely succeeded, and a
fail-closed check reports failure **after** the comments are posted.

Any fix must therefore change the strip and the comparison **together**. (plan-061's own
workaround sidesteps this by stripping the committed files themselves, so file and posted body
stay identical — at the cost of the bundle then failing `REQ-OKF-003`, which is the same
conflict paid from the other side.)

## Suggested direction (not prescriptive)

- Strip a leading YAML frontmatter block in L7 before `--body-file`, and compare the
  **stripped** text in the read-back — one change, both collisions closed.
- Or write the posted body to a temp file and keep the bundle copy as the archival artifact,
  making the two roles explicit rather than overloading one file.
- Or move drafts to a bundle-relative path OKF does not type as a member — but this needs
  care, since §3b's reasoning argues against exclusions that hide live artifacts.

## Provenance

Found during **plan-061** (`plan-061-james-dixson-6d8c97`, tracker #315), while preparing its
landing. Not plan-061's remit to fix. Adjacent to the `land` capability delivered by plan-060.
