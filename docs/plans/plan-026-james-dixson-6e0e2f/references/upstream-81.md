# Upstream #81: yf-markdown-lint ML003 folds image "title" into the link target — mis-flags GFM `![alt](path "title")`

- **Number:** 81
- **Title:** yf-markdown-lint ML003 folds image "title" into the link target — mis-flags GFM `![alt](path "title")`
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## Summary

`yf-markdown-lint` rule **ML003** (broken link/anchor target) does not parse the **optional GFM title** in link/image syntax. It treats the entire `images/x.png "caption"` string — including the quoted title — as the link *target*, then reports a broken link because no such file exists.

## Repro

Any Markdown image (or link) using the standard title form:

```markdown
![alt text](images/hero.png "A short caption")
```

Run the full link audit:

```bash
uv run <skill-dir>/scripts/markdown_lint.py path/to/ESSAY.md
```

Observed:

```
ESSAY.md:20: ML003 broken link target: images/hero.png "A short caption"
```

The reported target wrongly includes ` "A short caption"`.

## Impact

Repo-wide false positive on every titled image. In the `dixson3/writing` repo this affects all house essays — e.g. the committed, publication-`ready` `Incubator/ai-native-organization/ESSAY.md` flags ML003 on all 4 of its titled interstitial images, and the `RENDER.md` convention (`![alt](images/x.png "print caption")`) *requires* the title form.

- **Not** in the authoring subset (`ML001,ML002,ML005,ML006,ML007,ML008`), so the on-edit trigger stays clean.
- Only the **full link audit** (`/yf-markdown-lint` with no `--rules`) mis-flags.

## Expected

ML003 should parse the optional GFM title in both links and images and resolve **only the path**:

- `![alt](path "title")`
- `[text](path "title")`
- single- and double-quoted titles; optional surrounding whitespace before the quote.

The title is descriptive text, not part of the target, and must be stripped before resolution.

## Provenance

Discovered during the `dixson3/writing` plan-010 dogfood (blog-voice footnoter/illustrator). Tracked locally as bead `blog-d6r`.
