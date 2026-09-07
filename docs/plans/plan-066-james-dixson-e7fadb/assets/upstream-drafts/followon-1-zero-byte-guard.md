---
type: Asset
okf_spec: OKF-PLAN
description: "Body for the follow-on filed as #374 — the existence-only zero-byte skill-page guard."
---
<!-- THE POSTED BODY IS EVERYTHING BELOW THIS COMMENT. The frontmatter above is
     bundle metadata (OKF REQ-OKF-003) and was NOT part of the upstream write:
     filed as #374. -->

The authored-skill-page guard in `web/plugins/skill_pages.py` calls itself **fail-closed**, but it
only checks `os.path.isfile`. A **zero-byte** `web/content/skills/<name>.md` satisfies it: the
build exits **0**, and the page renders with the generated "At a glance" block, no body, and no
`<hr>` at all.

**Measured** during plan-066 (EXP-003, Result B).

### Why it matters

It makes *"the site builds"* an inadequate acceptance criterion for "the page exists", which is
the recurring defect class in this repository — **an instrument reporting success without the
thing having happened**. plan-066 worked around it by making its own criterion conjunctive (exit 0
**and** the emitted HTML has an `<hr>`, ≥2 `<h2>` and a non-trivial body), but the guard itself is
unchanged and the next page can still ship empty.

### Suggested fix

Have the guard reject a page whose authored body is empty or whitespace-only, with the same
`RuntimeError` it already raises for an absent one. Absence and emptiness are two facts, so they
should probably be two distinct messages rather than one.

Filed from plan-066 under D5 (file, do not fix — a pipeline defect outside the four Class-B items
that plan took on).
