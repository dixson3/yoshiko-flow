# Upstream spec excerpt — a deliberately UNMARKED vendored reference

This file is verbatim third-party content copied into a plan bundle, and it carries
**no** `source:` / `retrieved:` frontmatter. That absence is the whole defect.

REQ-DATA-027 makes the marker the exclusion predicate itself: the `reference` type declares
no content checks precisely *because* vendored content must not be linted against an authored
template. An unmarked vendored file is therefore not a minor omission — it is a hole in the
carve-out, because nothing can tell it apart from a hand-authored note.

> Verbatim excerpt follows. Nothing below is authored by this repository.
>
> The quick brown fox jumps over the lazy dog.
