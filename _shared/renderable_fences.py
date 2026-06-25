"""Canonical renderable-fence registry — single source of truth (plan-017 `_shared/`).

A **renderable fence** is a markdown fenced code block whose info-string names a
*source language that is rendered at preview/PDF time* rather than shown verbatim —
a ```` ```d2 ```` diagram or a ```` ```csv ```` table. This module is the **canonical**
`{class -> tool, output-kind, compile-checkability}` registry for that set, shared by
three skills that must agree on which fence classes are "renderable" or they drift:

* `yf-markdown-lint` (`markdown_lint.py`) carries a **marker-fenced region** holding a
  verbatim copy of the REGION delimited below; `_shared/sync.py` regenerates that region
  in-place from this file (skills cannot `import` each other — each must stay
  independently installable, so the shared snippet is *vendored*, never imported). The
  vendored region tells the linter which fence classes are renderable-and-compile-
  checkable (the optional embedded-d2-source lint rule).
* `yf-markdown-pdf` (`blocks.lua`) renders these fences to PDF. The pandoc **Lua** filter
  cannot import Python, so its fence-class list is **generated** from this registry by a
  `_shared/sync.py` Python->Lua emitter; a DRIFT-CHECK `field-set-equal` edge enforces the
  mirror on-edit (mirrors the `json-extract` precedent).
* `yf-diagram-authoring` (`render.py`) `embed`/`lift`/`inline` target the `d2` class.

Do **not** hand-edit the vendored copies. Edit the region here and run
`uv run _shared/sync.py`; `uv run _shared/sync.py --check` reports divergence. This file
is the fixed authority; a divergent region is the copy drifting (FAIL on the copy, never
the canonical).

The region is pure stdlib data + accessors so any consumer (the linter, the sync emitter)
can use it without extra imports.
"""

from __future__ import annotations


# >>> BEGIN renderable-fence registry (canonical) >>>
# Canonical map of renderable markdown fence info-strings -> metadata. A renderable
# fence's interior is *source* rendered at preview/PDF time, not shown verbatim.
#   tool             -- external CLI that renders the source, or None for pandoc-native
#   output_kind      -- "image" (a rendered figure) or "table"
#   compile_checkable-- True if the source has a validate/compile path a linter can shell
# Every renderable fence degrades to a verbatim code listing when its renderer fails
# (the degrade-to-code contract); that invariant is global, not per-class metadata.
RENDERABLE_FENCES = {
    "d2": {
        "tool": "d2",
        "output_kind": "image",
        "compile_checkable": True,
    },
    "csv": {
        "tool": None,
        "output_kind": "table",
        "compile_checkable": False,
    },
}


def renderable_fence_classes():
    """Sorted list of every renderable fence info-string (e.g. ['csv', 'd2'])."""
    return sorted(RENDERABLE_FENCES)


def compile_checkable_fence_classes():
    """Sorted renderable classes that expose a compile/validate path (e.g. ['d2'])."""
    return sorted(c for c, m in RENDERABLE_FENCES.items() if m["compile_checkable"])
# <<< END renderable-fence registry (canonical) <<<
