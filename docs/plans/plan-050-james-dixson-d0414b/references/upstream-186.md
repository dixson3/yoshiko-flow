---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #186: CRITICAL: plan_extract.py emits masked titles — inline code spans are blanked out of every issue/epic title it returns

- **Number:** 186
- **Title:** CRITICAL: plan_extract.py emits masked titles — inline code spans are blanked out of every issue/epic title it returns
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/186
- **State:** OPEN
- **Labels:** type::bug, priority::critical

## Body

## Summary

`skills/yf-plan/scripts/plan_extract.py` blanks inline code spans for **parsing**, then reads the
**title out of the masked line**. Every consumer of `issues[].title` (and `epics[].name`) therefore
receives corrupted text whenever a title contains a backticked span.

`mask_inline_code` is correct in intent — line 142 explains it: *"a `depends-on:` quoted inside an
inline code span is DOCUMENTATION, not a declaration."* The bug is that the masked line is never
un-masked before the title is captured.

```python
# plan_extract.py:139-145
def mask_inline_code(line: str) -> str:
    """Blank out `inline code spans`, preserving length so column offsets still line up."""
    return re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)

# plan_extract.py:308-330 — the ONLY call site
raw = lines[i]
ln = mask_inline_code(raw)          # <-- masked
m = EPIC.match(ln)                  # epic NAME captured from the masked line
    cur_epic = {"num": m.group(1), "name": m.group(2).strip(), ...}
m = ISSUE.match(ln)                 # issue TITLE captured from the masked line
    cur_issue = {"id": iid, "title": ..., ...}
```

`raw` is already in scope at the call site, so the fix is local.

## Measured impact

From `dixson3/astrospike` `plan-001-james-dixson-9153de` (35 issues). Four titles contain code
spans; **all four came back blanked**, with length preserved so the damage looks like stray
whitespace rather than an error:

| Issue | `plan.md` | `plan_extract.py --json` |
| :-- | :-- | :-- |
| 1.1 | ``Instantiate `milzamsz/astro-cloudflare-starter` into this repo`` | `Instantiate                                     into this repo` |
| 4.2 | ``Port `ContactFormDurableObject` with the SQLite storage backend`` | `Port                            with the SQLite storage backend` |
| 5.2 | ``First deploy to the generated `workers.dev` hostname`` | `First deploy to the generated               hostname` |
| 5.3 | ``Attach the `astrospike.ysapp.page` custom domain`` | `Attach the                         custom domain` |

## Why this is critical, not cosmetic

SKILL.md §5.2a instructs **"Derive the DAG mechanically, do not transcribe it"** and drives
`bd create "Issue ${issue_id}: ${issue_description}"` from this output. So the corruption is
**written straight into the bead DAG** and becomes the executor's working text. Measured on
plan-001: 4 of 35 poured beads carry mangled titles, and `bd show` renders them as the executable
instruction. Issue 4.2's title is what tells an executor *which Durable Object class to port* —
the class name is the part that vanished.

It also **fails silently in the worst possible way**: `--strict` reports `unparsed: []` and exit 0,
because the line parsed fine. Nothing downstream can tell a blanked span from an author who typed
runs of spaces.

## Blast radius

Every plan whose issue or epic titles use backticks — which is the documented house style; the
plan.md skeleton and grammar in SKILL.md use inline code throughout. Any consumer of
`issues[].title` / `epics[].name` is affected, not just the pour.

## Suggested fix

Keep the mask for *detection*, take the captured text from `raw`. Either re-match the raw line once
the masked line has established the record is an issue/epic, or capture spans and restore them
after the match. A regression test asserting a backticked title round-trips would pin it.

## Related

Filed alongside the companion defect: the extractor carries no description/detail field, so the
same mechanical pour leaves **all** bead descriptions empty. The check that would have caught both
— `_shared/pour_fidelity.py`, referenced by SKILL.md §6.4 — is not shipped in the installed skill.

Found while executing `dixson3/astrospike` plan-001 (7 red-team passes, 5 independent).
