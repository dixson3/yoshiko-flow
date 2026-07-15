# /// script
# requires-python = ">=3.11"
# ///
"""Tests for md2html.py — self-contained HTML render (embed-resources, default
stylesheet, self-contained math), the opt-in CriticMarkup filter, and the
single-vs-batch / -o argument constraints.

Run:  uv run --with pytest python3 -m pytest test_md2html.py -q

The full-render tests need pandoc on PATH and skip without it; the unit tests
(file presence, flags, filter transform) always run. Tests name the REQ id they
exercise (per the repo's coverage-gate convention).
"""
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("md2html", _HERE / "md2html.py")
md2html = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(md2html)

_HAS_PANDOC = shutil.which("pandoc") is not None
_needs_pandoc = pytest.mark.skipif(not _HAS_PANDOC, reason="needs pandoc")

CM_FIXTURE = (
    "# CriticMarkup fixture\n\n"
    "Add: {++added several words++}. "
    "Del: {--gone--}. "
    "Sub: {~~old~>new~~}. "
    "HL: {==important==}. "
    "Comment: {>>note<<}.\n\n"
    "Special: {++a<b & c++}.\n\n"
    "Literal in code: `{++x++}` stays.\n"
)


def _run(args, cwd=None, env=None):
    return subprocess.run(
        [sys.executable, str(_HERE / "md2html.py"), *args],
        capture_output=True, text=True, cwd=cwd, env=env,
    )


# --- unit: wiring / helper files present (no toolchain needed) ---------------

def test_helper_files_exist():
    # REQ-MDHTML-010 / REQ-MDHTML-021: default stylesheet + CriticMarkup filter ship.
    assert md2html.DEFAULT_CSS.is_file()
    assert md2html.CRITICMARKUP_FILTER.is_file()


def test_default_css_has_criticmarkup_classes():
    # REQ-MDHTML-023: default stylesheet carries an entry for each cm-* class.
    css = md2html.DEFAULT_CSS.read_text(encoding="utf-8")
    for cls in ("cm-add", "cm-del", "cm-hl", "cm-comment"):
        assert cls in css, cls


def test_help_lists_flags():
    # --help exits during arg parse, before check_deps — runs without pandoc.
    proc = _run(["--help"])
    assert proc.returncode == 0
    assert "--criticmarkup" in proc.stdout
    assert "--no-default-css" in proc.stdout


def test_output_rejects_multiple_inputs(tmp_path):
    # REQ-MDHTML-030: -o is single-input only.
    a, b = tmp_path / "a.md", tmp_path / "b.md"
    a.write_text("# a\n", encoding="utf-8")
    b.write_text("# b\n", encoding="utf-8")
    proc = _run([str(a), str(b), "-o", str(tmp_path / "out.html")])
    assert proc.returncode != 0
    assert "single input" in (proc.stdout + proc.stderr)


def test_non_file_input_errors(tmp_path):
    # REQ-MDHTML-031: a non-file input errors.
    if not _HAS_PANDOC:
        pytest.skip("needs pandoc (check_deps runs before the file check)")
    proc = _run([str(tmp_path / "missing.md")])
    assert proc.returncode != 0
    assert "not a file" in (proc.stdout + proc.stderr)


def test_missing_pandoc_fails_closed(tmp_path):
    # REQ-MDHTML-005: with pandoc absent from PATH the run entrypoint fails CLOSED —
    # a single readable message naming the missing tool + install hint, non-zero exit,
    # and never a raw FileNotFoundError/traceback. PATH is masked to an empty dir so
    # shutil.which("pandoc") returns None even where pandoc is installed.
    src = tmp_path / "doc.md"
    src.write_text("# Title\n\nBody.\n", encoding="utf-8")
    empty = tmp_path / "emptybin"
    empty.mkdir()
    env = dict(os.environ, PATH=str(empty))
    proc = _run([str(src)], env=env)
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "pandoc" in combined                 # names the missing tool
    assert "install" in combined.lower()        # carries an install hint
    assert "Traceback" not in combined          # fail-closed, no raw traceback
    assert "FileNotFoundError" not in combined
    assert not (tmp_path / "doc.html").exists()  # nothing rendered


# --- integration: full render (needs pandoc) ---------------------------------

@_needs_pandoc
def test_renders_standalone_self_contained(tmp_path):
    # REQ-MDHTML-001/010/030: single standalone HTML file with an inlined <style>.
    src = tmp_path / "doc.md"
    src.write_text("# Title\n\nSome **body** text.\n", encoding="utf-8")
    proc = _run([str(src)])
    assert proc.returncode == 0, proc.stderr
    out = tmp_path / "doc.html"
    assert out.is_file()
    html = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html or "<!doctype html>" in html.lower()
    assert "<style" in html                      # default stylesheet embedded
    assert "cm-add" in html                      # cm-* classes present in style


@_needs_pandoc
def test_embeds_image_as_data_uri(tmp_path):
    # REQ-MDHTML-001/002: a relative image resolves against the source dir and is
    # embedded as a data: URI (no sidecar reference).
    png = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
           b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc````"
           b"\x00\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "p.png").write_bytes(png)
    src = tmp_path / "doc.md"
    src.write_text("![alt](img/p.png)\n", encoding="utf-8")
    proc = _run([str(src)])
    assert proc.returncode == 0, proc.stderr
    html = (tmp_path / "doc.html").read_text(encoding="utf-8")
    assert "data:image/png;base64," in html      # embedded, not linked


@_needs_pandoc
def test_math_is_self_contained_mathml(tmp_path):
    # REQ-MDHTML-011: math renders as MathML, no CDN script reference.
    src = tmp_path / "m.md"
    src.write_text("Inline $x^2 + 1$ math.\n", encoding="utf-8")
    proc = _run([str(src)])
    assert proc.returncode == 0, proc.stderr
    html = (tmp_path / "m.html").read_text(encoding="utf-8")
    assert "<math" in html                       # MathML, self-contained
    assert "mathjax" not in html.lower()          # no CDN
    assert "cdn" not in html.lower()


@_needs_pandoc
def test_criticmarkup_off_by_default_literal(tmp_path):
    # REQ-MDHTML-020: default OFF — no cm-* tag is emitted in the body.
    src = tmp_path / "c.md"
    src.write_text("Add: {++text++} here.\n", encoding="utf-8")
    proc = _run([str(src)])
    assert proc.returncode == 0, proc.stderr
    html = (tmp_path / "c.html").read_text(encoding="utf-8")
    # The literal braces survive; no <ins class="cm-add"> is produced.
    assert '<ins class="cm-add">' not in html


@_needs_pandoc
def test_criticmarkup_renders_five_constructs(tmp_path):
    # REQ-MDHTML-021/022/023/024: opt-in render of all five constructs, escaping,
    # and code protection.
    src = tmp_path / "cm.md"
    src.write_text(CM_FIXTURE, encoding="utf-8")
    proc = _run([str(src), "--criticmarkup"])
    assert proc.returncode == 0, proc.stderr
    html = (tmp_path / "cm.html").read_text(encoding="utf-8")
    assert '<ins class="cm-add">added several words</ins>' in html   # multi-word add
    assert '<del class="cm-del">gone</del>' in html                  # deletion
    assert ('<del class="cm-del">old</del><ins class="cm-add">new</ins>'
            in html)                                                  # substitution
    assert '<mark class="cm-hl">important</mark>' in html            # highlight
    assert '<span class="cm-comment">note</span>' in html           # comment
    assert '<ins class="cm-add">a&lt;b &amp; c</ins>' in html        # HTML-escaped body
    assert "<code>{++x++}</code>" in html                            # code untouched


@_needs_pandoc
def test_criticmarkup_disables_gfm_strikethrough(tmp_path):
    # REQ-MDHTML-025: the documented tradeoff — while --criticmarkup is on, real GFM
    # ~~strike~~ is disabled and renders literally (so substitutions survive).
    src = tmp_path / "s.md"
    src.write_text("A ~~struck~~ word.\n", encoding="utf-8")
    with_cm = _run([str(src), "--criticmarkup", "-o", str(tmp_path / "on.html")])
    assert with_cm.returncode == 0, with_cm.stderr
    on_html = (tmp_path / "on.html").read_text(encoding="utf-8")
    assert "<del>" not in on_html and "~~struck~~" in on_html   # literal, not struck
    # Control: default off, ~~strike~~ IS honored as GFM strikethrough.
    off = _run([str(src), "-o", str(tmp_path / "off.html")])
    assert off.returncode == 0
    off_html = (tmp_path / "off.html").read_text(encoding="utf-8")
    assert "<del>" in off_html


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
