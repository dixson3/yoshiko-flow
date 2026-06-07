# Upstream #7: bdplan: generate Obsidian-friendly self-consistent links in plan documents

- **Number:** 7
- **Title:** bdplan: generate Obsidian-friendly self-consistent links in plan documents
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Context

The `deep-research` skill was recently updated to generate Obsidian-friendly markdown across its outputs:

- `_index.md` artifact column rendered as Obsidian wikilinks (`[[artifact|artifact.md]]`) so clicking navigates to the artifact
- A `sources.md` is generated per research topic from `sources.json`, with a `## <ID>` heading per source
- Inline citations in `Summary.md` and `artifacts/*.md` use `[[sources#ID|ID]]` wikilinks so each citation is clickable and jumps to the matching source entry
- Rules codified in `AGENTS/OBSIDIAN.md` at the vault level (wikilinks as default, frontmatter required, mermaid/excalidraw for diagrams, consistency grep-pass on rename/move)

## Ask

Apply the same treatment to `bdplan` so plan documents render as navigable Obsidian notes:

1. **Plan index / overview documents** — any table or list that references sibling plan artifacts (plan.md, scope-answers.md, upstream-triage.md, findings, etc.) should render those references as wikilinks, not bare filenames.
2. **Cross-document references** — when `plan.md` or phase documents reference beads IDs, findings, upstream issues, or sibling plan files, use wikilinks (or at minimum markdown links with working anchors) rather than prose-only mentions.
3. **Frontmatter** — every generated markdown file should include YAML frontmatter with `title`, `created`, and `tags` consistent with the vault convention.
4. **Findings with citations** — if/when findings cite external sources, use the same `[[sources#ID|ID]]` pattern or equivalent. Plain `[N]` citations that go nowhere should not be generated.
5. **Consistency on move/rename** — reference the consistency rules in `AGENTS/OBSIDIAN.md`: an inbound-reference grep pass should happen when files are moved or deleted, so no dangling `[[...]]` remain.

## Reference implementation

See `.claude/skills/deep-research/scripts/link_normalizer.py` and the packager/synthesizer agent instructions for the patterns used by deep-research. The script is idempotent and can be adapted as a migration pass for existing plans.

## Acceptance

- A plan generated after this change renders every inter-document reference as a clickable Obsidian link
- Existing plans under `docs/plans/` can be migrated via a one-shot normalizer (or left untouched if non-trivial)
- `AGENTS/OBSIDIAN.md` conventions are honored in all newly generated markdown
