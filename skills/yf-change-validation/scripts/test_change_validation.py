# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest"]
# ///
"""Tests for change_validation.py — signal readers, infer, run, check-drift.

Run:  uv run skills/yf-change-validation/scripts/test_change_validation.py
  or:  uv run --with pytest python3 -m pytest test_change_validation.py -q

Two invocation styles, matching the engine's structure:

- **Signal readers** (`read_cargo`, `read_ci`, …) take an explicit `root` arg, so
  they are imported and called directly against a fixture tree in `tmp_path`.
- **Subcommands** (`infer` / `run` / `check-drift`) resolve the repo via
  `repo_root()` (a `git rev-parse`), so they are invoked as a subprocess inside a
  `git init`-ed fixture repo — the most faithful reproduction of the real CLI.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ENGINE = Path(__file__).parent / "change_validation.py"

_spec = importlib.util.spec_from_file_location("change_validation", ENGINE)
cv = importlib.util.module_from_spec(_spec)
sys.modules["change_validation"] = cv
_spec.loader.exec_module(cv)


# ---------------------------------------------------------------------------
# fixtures / helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def git_repo(tmp_path):
    """A minimal git repo so the engine's `git rev-parse --show-toplevel`
    resolves to `tmp_path` when the engine runs there."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    # macOS resolves /var -> /private/var; canonicalize so path comparisons hold.
    return Path(os.path.realpath(tmp_path))


def run_engine(repo: Path, *args, changed=None):
    """Invoke the engine as a subprocess from inside `repo`; return (rc, json)."""
    argv = [sys.executable, str(ENGINE), *args, "--json"]
    proc = subprocess.run(argv, cwd=str(repo), capture_output=True, text=True)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"_raw_stdout": proc.stdout, "_stderr": proc.stderr}
    return proc.returncode, payload


# ===========================================================================
# SIGNAL READERS
# ===========================================================================

def test_read_cargo_plain(tmp_path):
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "x"\nversion = "0.1.0"\n')
    sig = cv.read_cargo(tmp_path)
    assert sig is not None
    assert "cargo fmt --all -- --check" in sig["commands"]
    # no [workspace] -> no --workspace flag
    assert all("--workspace" not in c for c in sig["commands"])


def test_read_cargo_workspace_adds_flag(tmp_path):
    (tmp_path / "Cargo.toml").write_text(
        '[workspace]\nmembers = ["a", "b"]\n'
    )
    sig = cv.read_cargo(tmp_path)
    assert sig["members"] == ["a", "b"]
    assert any("cargo clippy --workspace" in c for c in sig["commands"])
    assert any("cargo test --workspace" in c for c in sig["commands"])


def test_read_cargo_absent(tmp_path):
    assert cv.read_cargo(tmp_path) is None


def _wf_dir(root: Path) -> Path:
    d = root / ".github" / "workflows"
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_read_ci_extracts_run_steps(tmp_path):
    (_wf_dir(tmp_path) / "ci.yml").write_text(
        "name: CI\n"
        "on: [push]\n"
        "jobs:\n"
        "  build:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - run: cargo build\n"
        "      - run: |\n"
        "          cargo test\n"
        "          cargo clippy\n"
    )
    sig = cv.read_ci(tmp_path)
    assert sig is not None
    assert "cargo build" in sig["steps"]
    assert "cargo test" in sig["steps"]
    assert "cargo clippy" in sig["steps"]


def test_read_ci_skips_if_false_gated_workflow(tmp_path):
    # a workflow double-disabled with `if: ${{ false }}` must be skipped entirely
    (_wf_dir(tmp_path) / "disabled.yml").write_text(
        "name: Disabled\n"
        "on: [push]\n"
        "jobs:\n"
        "  noop:\n"
        "    if: ${{ false }}\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - run: should-not-appear\n"
    )
    (_wf_dir(tmp_path) / "live.yml").write_text(
        "name: Live\n"
        "on: [push]\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - run: real-step\n"
    )
    sig = cv.read_ci(tmp_path)
    assert "disabled.yml" in sig["skipped"]
    assert "real-step" in sig["steps"]
    assert all("should-not-appear" not in s for s in sig["steps"])


def test_read_pytests_pep723_with_deps(tmp_path):
    (tmp_path / "test_a.py").write_text(
        "# /// script\n"
        "# requires-python = \">=3.11\"\n"
        "# dependencies = [\"pytest\"]\n"
        "# ///\n"
        "def test_x():\n    assert True\n"
    )
    sig = cv.read_pytests(tmp_path)
    assert sig is not None
    assert sig["headers"]["test_a.py"]["pep723"] is True
    assert sig["headers"]["test_a.py"]["has_deps"] is True
    assert "uv run test_a.py" in sig["commands"]


def test_read_pytests_pep723_headerless_subset(tmp_path):
    # PEP-723 header WITHOUT deps -> the `python3 -m pytest <f>` idiom
    (tmp_path / "test_b.py").write_text(
        "# /// script\n"
        "# requires-python = \">=3.11\"\n"
        "# ///\n"
        "def test_y():\n    assert True\n"
    )
    sig = cv.read_pytests(tmp_path)
    assert sig["headers"]["test_b.py"]["pep723"] is True
    assert sig["headers"]["test_b.py"]["has_deps"] is False
    assert "uv run --with pytest python3 -m pytest test_b.py -q" in sig["commands"]


def test_read_pytests_no_header_with_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    (tmp_path / "test_c.py").write_text("def test_z():\n    assert True\n")
    sig = cv.read_pytests(tmp_path)
    assert sig["headers"]["test_c.py"]["pep723"] is False
    assert "uv run pytest" in sig["commands"]


def test_read_runners_justfile_targets(tmp_path):
    (tmp_path / "justfile").write_text(
        "test:\n    cargo test\n\nlint:\n    cargo clippy\n\nbuild:\n    cargo build\n"
    )
    sig = cv.read_runners(tmp_path)
    assert sig is not None
    assert "just test" in sig["commands"]
    assert "just lint" in sig["commands"]
    assert "just build" in sig["commands"]


def test_read_runners_makefile_targets(tmp_path):
    (tmp_path / "Makefile").write_text(
        "test:\n\tpytest\n\ncheck:\n\truff check\n"
    )
    sig = cv.read_runners(tmp_path)
    assert "make test" in sig["commands"]
    assert "make check" in sig["commands"]


# ===========================================================================
# infer
# ===========================================================================

def _seed_simple_repo(repo: Path):
    """A repo with CI steps + an on-disk pytest suite CI omits, for infer/drift."""
    (_wf_dir(repo) / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  build:\n"
        "    runs-on: ubuntu-latest\n    steps:\n"
        "      - run: cargo test\n"
    )
    (repo / "test_local.py").write_text(
        "# /// script\n# requires-python = \">=3.11\"\n# dependencies = [\"pytest\"]\n# ///\n"
        "def test_x():\n    assert True\n"
    )


def test_infer_draft_shape_two_tiers_and_fingerprint(git_repo):
    _seed_simple_repo(git_repo)
    rc, out = run_engine(git_repo, "infer")
    assert rc == 0
    assert out["status"] == "draft"
    assert out["approved"] is False
    # two tiers present in the recipe
    assert "fast" in out["recipe"]
    assert "full" in out["recipe"]
    # §2 fingerprint signals recorded
    assert "ci" in out["signals"]
    assert out["signals"]["ci"]["fingerprint"].startswith("sha256:")


def test_infer_manifest_marks_approved_no(git_repo):
    _seed_simple_repo(git_repo)
    rc, out = run_engine(git_repo, "infer")
    assert "approved: no" in out["manifest_preview"]
    # the four ordered sections
    text = out["manifest_preview"]
    for heading in ("## 0. Status", "## 1. Tiers",
                    "## 2. Signal Fingerprint", "## 3. Trigger Scope"):
        assert heading in text


def test_infer_full_superset_of_ci_union_repo_checks(git_repo):
    _seed_simple_repo(git_repo)
    rc, out = run_engine(git_repo, "infer")
    full_cmds = {r["cmd"] for r in out["recipe"]["full"]}
    # CI step present in FULL
    assert "cargo test" in full_cmds
    # the on-disk pytest suite CI omits is ALSO in FULL (REQ-INFER-005 / SCHEMA-004)
    assert "uv run test_local.py" in full_cmds


def test_infer_validate_cmd_migration_seed(git_repo):
    # `.yf-plan.local.json` validate-cmd SEEDS the FULL tier first (REQ-INFER-004)
    (git_repo / ".yf-plan.local.json").write_text(
        json.dumps({"validate-cmd": "make validate-all"})
    )
    (_wf_dir(git_repo) / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  b:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: cargo test\n"
    )
    rc, out = run_engine(git_repo, "infer")
    full = [r["cmd"] for r in out["recipe"]["full"]]
    assert "make validate-all" in full
    # seeded validate-cmd comes first (precedence tier 1)
    assert full[0] == "make validate-all"


# ===========================================================================
# run — approved fixture manifest with trivial commands
# ===========================================================================

def _write_manifest(repo: Path, *, approved=True, fast_rows=(), full_rows=(),
                    scope_rows=()):
    """Compose a minimal valid four-section manifest."""
    L = ["# CHANGE-VALIDATION.md", "", "## 0. Status", "",
         f"approved: {'yes' if approved else 'no'}", "",
         "## 1. Tiers", "", "### fast", "",
         "| id | cmd | cwd | timeout |", "|:--|:--|:--|--:|"]
    for rid, cmd in fast_rows:
        L.append(f"| `{rid}` | `{cmd}` |  |  |")
    L += ["", "### full", "", "| id | cmd | cwd | timeout |", "|:--|:--|:--|--:|"]
    for cmd in full_rows:
        L.append(f"|  | `{cmd}` |  |  |")
    L += ["", "## 2. Signal Fingerprint", "",
          "| source-path | parsed-value-or-hash |", "|:--|:--|"]
    L += ["", "## 3. Trigger Scope", "",
          "| changed-path glob | scopes to (FAST ids) |", "|:--|:--|"]
    for glob, ids in scope_rows:
        L.append(f"| `{glob}` | {', '.join(f'`{i}`' for i in ids)} |")
    L.append("")
    (repo / cv.MANIFEST_NAME).write_text("\n".join(L))


def test_run_pass(git_repo):
    _write_manifest(git_repo, full_rows=["true"])
    rc, out = run_engine(git_repo, "run", "--tier", "full")
    assert rc == cv.EXIT_OK
    assert out["status"] == "pass"
    assert out["first_failure"] is None


def test_run_fail_records_first_failure(git_repo):
    _write_manifest(git_repo, full_rows=["true", "false", "true"])
    rc, out = run_engine(git_repo, "run", "--tier", "full")
    assert rc == cv.EXIT_FAIL
    assert out["status"] == "fail"
    assert out["first_failure"]["cmd"] == "false"


def test_run_inconclusive_on_missing_tool(git_repo):
    _write_manifest(git_repo, full_rows=["definitely-not-a-real-tool-xyz --check"])
    rc, out = run_engine(git_repo, "run", "--tier", "full")
    assert rc == cv.EXIT_INCONCLUSIVE
    assert out["status"] == "inconclusive"
    assert "not on PATH" in out["commands"][0]["output_tail"]


def test_run_fast_affected_scoping_selects_subset(git_repo):
    # two FAST rows; §3 scopes one glob to only `py` — a python edit runs just that
    _write_manifest(
        git_repo,
        fast_rows=[("py", "true"), ("rs", "false")],
        scope_rows=[("**/*.py", ["py"]), ("**/*.rs", ["rs"])],
    )
    rc, out = run_engine(git_repo, "run", "--tier", "fast", "--changed", "src/a.py")
    # only `py` (which is `true`) ran -> pass; `rs` (false) was NOT selected
    assert rc == cv.EXIT_OK
    assert [c["id"] for c in out["commands"]] == ["py"]


def test_run_fast_no_changed_runs_whole_tier(git_repo):
    _write_manifest(
        git_repo,
        fast_rows=[("py", "true"), ("rs", "false")],
        scope_rows=[("**/*.py", ["py"]), ("**/*.rs", ["rs"])],
    )
    rc, out = run_engine(git_repo, "run", "--tier", "fast")
    # whole tier runs; `rs` is false -> fail
    assert rc == cv.EXIT_FAIL
    assert out["first_failure"]["id"] == "rs"


# ===========================================================================
# approved-gate refusal
# ===========================================================================

def test_run_refuses_when_manifest_absent(git_repo):
    rc, out = run_engine(git_repo, "run", "--tier", "full")
    assert rc == cv.EXIT_REFUSED
    assert out["status"] == "refused"
    assert out["reason"] == "not approved"
    assert "absent" in out["detail"]


def test_run_refuses_when_not_approved(git_repo):
    _write_manifest(git_repo, approved=False, full_rows=["true"])
    rc, out = run_engine(git_repo, "run", "--tier", "full")
    assert rc == cv.EXIT_REFUSED
    assert out["status"] == "refused"
    assert "approved: no" in out["detail"]
    # clean structured refusal — never a traceback / error type leak
    assert "type" not in out
    assert "error" not in out


# ===========================================================================
# check-drift — fingerprint diff; never rewrites the manifest
# ===========================================================================

def _approved_manifest_with_fingerprint(repo: Path, fp_rows):
    """An approved manifest carrying explicit §2 fingerprint rows."""
    L = ["# CHANGE-VALIDATION.md", "", "## 0. Status", "", "approved: yes", "",
         "## 1. Tiers", "", "### fast", "",
         "| id | cmd | cwd | timeout |", "|:--|:--|:--|--:|",
         "", "### full", "", "| id | cmd | cwd | timeout |", "|:--|:--|:--|--:|",
         "| | `true` | | |",
         "", "## 2. Signal Fingerprint", "",
         "| source-path | parsed-value-or-hash |", "|:--|:--|"]
    for src, val in fp_rows:
        L.append(f"| `{src}` | `{val}` |")
    L += ["", "## 3. Trigger Scope", "",
          "| changed-path glob | scopes to (FAST ids) |", "|:--|:--|", ""]
    (repo / cv.MANIFEST_NAME).write_text("\n".join(L))


def test_check_drift_flags_added_signal(git_repo):
    # manifest records NO signals; live repo grows a CI workflow -> added drift.
    # This is the standing "CI omits the pytest suites" delta in fingerprint form.
    _approved_manifest_with_fingerprint(git_repo, fp_rows=[])
    (_wf_dir(git_repo) / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  b:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: cargo test\n"
    )
    rc, out = run_engine(git_repo, "check-drift")
    assert rc == cv.EXIT_OK
    assert out["drift"] is True
    assert any(a["source"] == ".github/workflows/*.yml" for a in out["added"])


def test_check_drift_flags_changed_signal(git_repo):
    # record a stale fingerprint for the CI source, then change the live steps
    (_wf_dir(git_repo) / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  b:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: cargo test\n"
    )
    _approved_manifest_with_fingerprint(
        git_repo, fp_rows=[(".github/workflows/*.yml", "sha256:stalevalue00000")]
    )
    rc, out = run_engine(git_repo, "check-drift")
    assert out["drift"] is True
    assert any(c["source"] == ".github/workflows/*.yml" for c in out["changed"])


def test_check_drift_flags_removed_signal(git_repo):
    # manifest records a signal source that no longer exists on disk -> removed
    _approved_manifest_with_fingerprint(
        git_repo, fp_rows=[("Cargo.toml", "sha256:deadbeefdeadbeef")]
    )
    rc, out = run_engine(git_repo, "check-drift")
    assert out["drift"] is True
    assert any(r["source"] == "Cargo.toml" for r in out["removed"])


def test_check_drift_never_rewrites_manifest(git_repo):
    (_wf_dir(git_repo) / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  b:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: cargo test\n"
    )
    _approved_manifest_with_fingerprint(git_repo, fp_rows=[])
    before = (git_repo / cv.MANIFEST_NAME).read_text()
    rc, out = run_engine(git_repo, "check-drift")
    assert out["drift"] is True
    # re-proposal only — the engine never auto-rewrites the manifest file
    after = (git_repo / cv.MANIFEST_NAME).read_text()
    assert before == after
    assert out["proposed_delta"] is not None
    assert "never auto-rewritten" in out["proposed_delta"]["note"]


def test_check_drift_no_manifest_is_clean_noop(git_repo):
    rc, out = run_engine(git_repo, "check-drift")
    assert rc == cv.EXIT_OK
    assert out["drift"] is False


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
