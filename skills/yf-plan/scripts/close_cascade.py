# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
# ]
# ///
"""Close-cascade helper for the /yf-plan skill (REQ-PLAN-067, #73).

On plan COMPLETE, walk the plan's bead tree bottom-up and close every **container**
(intermediate epic and the top-level plan molecule) whose children are **all terminal**,
with a close reason referencing the plan. A container with **any still-open child** while
the plan is being marked complete is a **hard failure**: it is reported in the `blocked`
set (a non-empty `blocked` set is the fail-loud signal) and never silently closed.

"Terminal" is defined consistently with `resume-scan`'s gate accounting: a child is
terminal when it is `status: closed` **or** a **resolved/verified gate** (even if bd does
not mark it `status: closed`). In bd >= 1.1.0 a resolved gate is already `status: closed`,
so the first rule covers it; the gate-flag check is forward-compatible. An **unsatisfied**
gate is a genuine open child (part of the fail-loud signal) — the helper **never forces**
closure of a container with an unsatisfied-gate child.

Self-contained on purpose: uses only `bd children` / `bd list` / `bd close` and a private
copy of the defensive `bd --json` parser. Extraction to `_shared/` is deferred until a
genuine second in-repo runtime consumer exists (rule-of-three) — see REQ-PLAN-067.
"""

import json
import subprocess
import sys

import click


def _parse_bd_json(text: str) -> list[dict]:
    """Defensively parse `bd ... --json` output to a flat list of issue dicts.

    bd output may be a single object, an array, an `{"issues": [...]}` envelope, or —
    rarely — concatenated documents. This tolerates all four and flattens to issues.
    (Mirrors `plan_manager.py::_parse_bd_json`; kept private so this helper stays
    self-contained.)
    """
    text = text.strip()
    if not text:
        return []
    docs: list = []
    try:
        docs = [json.loads(text)]
    except json.JSONDecodeError:
        dec = json.JSONDecoder()
        idx, n = 0, len(text)
        while idx < n:
            while idx < n and text[idx] in " \t\r\n":
                idx += 1
            if idx >= n:
                break
            try:
                obj, end = dec.raw_decode(text, idx)
            except json.JSONDecodeError:
                break
            docs.append(obj)
            idx = end
    issues: list[dict] = []
    for d in docs:
        if isinstance(d, list):
            issues.extend(x for x in d if isinstance(x, dict))
        elif isinstance(d, dict):
            if isinstance(d.get("issues"), list):
                issues.extend(x for x in d["issues"] if isinstance(x, dict))
            elif "id" in d:
                issues.append(d)
    return issues


def _bd_ex(*args: str) -> tuple[list[dict], str | None]:
    """Run `bd <args> --json`. Returns (issues, unavailable_reason).

    The second element separates the two outcomes the old `_bd` collapsed:

      * `None`      — **bd answered.** An empty list then means "no such bead", which is
                      a DEFINITE negative.
      * a string    — **bd did not answer** (binary absent, wedged DB, unparseable
                      output). The list is empty but says NOTHING about the bead.

    `_bd` returned `[]` for `CalledProcessError`, `FileNotFoundError` AND `OSError`
    alike, so a typo'd root, a missing binary and a wedged Dolt DB were indistinguishable.
    Fixing the silent-pass without this split would have turned a `bd` outage into a hard
    completion halt on healthy work.

    NOTE: a non-zero exit is AMBIGUOUS on its own — `bd show <missing-id>` exits non-zero,
    and so does a broken `bd`. It is disambiguated by `_bd_healthy()`, a separate probe
    against the DB rather than against the bead; see `_bd_show_ex`.
    """
    try:
        out = subprocess.check_output(["bd", *args, "--json"],
                                      text=True, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return [], "`bd` not found on PATH"
    except subprocess.CalledProcessError as e:
        return [], f"`bd {' '.join(args)}` exited {e.returncode}"
    except OSError as e:
        return [], f"`bd` could not be run: {e}"
    try:
        return _parse_bd_json(out), None
    except Exception as e:                                  # pragma: no cover - defensive
        return [], f"unparseable `bd` output: {e}"


def _bd(*args: str) -> list[dict]:
    """Back-compat view over `_bd_ex`; [] on any failure. Callers that must
    distinguish absent-from-unavailable use `_bd_ex` directly."""
    issues, _ = _bd_ex(*args)
    return issues


def _bd_show(node_id: str) -> dict | None:
    beads = _bd("show", node_id)
    return beads[0] if beads else None


def _bd_healthy() -> bool:
    """Is `bd` itself functioning, independent of any particular bead?

    This is the probe that makes the absent/unavailable split REAL rather than nominal.
    `bd show <missing-id>` exits non-zero, so the failure of a bead-specific command
    cannot distinguish "that bead does not exist" from "bd is broken". A cheap
    bead-independent query can: if it succeeds, `bd` works and the earlier failure was
    about the BEAD; if it also fails, `bd` is the problem.
    """
    try:
        subprocess.check_output(["bd", "list", "--limit", "1", "--json"],
                                text=True, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return False


def _bd_show_ex(node_id: str) -> tuple[dict | None, str | None]:
    """(bead, unavailable_reason). `(None, None)` means bd answered: no such bead.

    Deliberately routed through `_bd_show`, which stays THE bead-lookup seam the test
    suite monkeypatches. Only the *disambiguation* of a None result is new.
    """
    bead = _bd_show(node_id)
    if bead is not None:
        return bead, None

    # `bead is None` is ambiguous: the bead may be absent, or `bd` may be broken.
    # Resolve it with a bead-INDEPENDENT probe — a bead-specific failure cannot tell
    # the two apart, since `bd show <missing-id>` also exits non-zero.
    if _bd_healthy():
        return None, None                       # bd works, bead absent -> definite `fail`
    _, reason = _bd_ex("show", node_id)
    return None, reason or "`bd` is not answering"


def _node_children(node_id: str) -> list[dict]:
    """All direct children of `node_id`, **including gates and closed beads**.

    `bd children` (an alias for `bd list --parent`) omits gate-type children, so the
    result is merged with an explicit gate query. De-duplicated by id, sorted for
    deterministic output.
    """
    by_id: dict[str, dict] = {}
    for child in _bd("children", node_id):
        cid = child.get("id")
        if cid:
            by_id[cid] = child
    for gate in _bd("list", "--parent", node_id, "--type", "gate", "--status", "all"):
        gid = gate.get("id")
        if gid:
            by_id[gid] = gate
    return [by_id[k] for k in sorted(by_id)]


def _bead_is_terminal(bead: dict) -> bool:
    """Terminal per REQ-PLAN-067: `status: closed`, or a resolved/verified gate.

    An unsatisfied (open, unresolved) gate is NOT terminal — it is a genuine open child.
    """
    if bead.get("status") == "closed":
        return True
    if bead.get("issue_type") == "gate":
        # Forward-compat: a gate marked resolved/verified without status:closed.
        for key in ("resolved", "verified", "gate_resolved"):
            if bead.get(key) is True:
                return True
        gate_status = str(bead.get("gate_status", "")).lower()
        if gate_status in ("resolved", "verified", "satisfied", "passed", "closed"):
            return True
    return False


def _bd_close(node_id: str, reason: str) -> tuple[bool, str]:
    """Close a container (never `--force`). Returns (ok, error_text)."""
    try:
        subprocess.check_output(["bd", "close", node_id, "-r", reason, "--json"],
                                text=True, stderr=subprocess.STDOUT)
        return (True, "")
    except subprocess.CalledProcessError as e:
        return (False, (e.output or "").strip() or f"bd close exited {e.returncode}")
    except (FileNotFoundError, OSError) as e:
        return (False, str(e))


def cascade(root_id: str, reason: str, dry_run: bool) -> dict:
    """Bottom-up close-cascade over the plan tree rooted at `root_id`.

    Returns `{closed:[...], blocked:[{id,title,open_children,[close_error]}],
    errors:[...], dry_run}`. A non-empty `blocked` set is the fail-loud signal.
    """
    closed: list[str] = []
    blocked: list[dict] = []
    errors: list[dict] = []
    visited: set[str] = set()

    def visit(bead: dict) -> bool:
        nid = bead.get("id")
        if not nid:
            return False
        if nid in visited:
            return _bead_is_terminal(bead)
        visited.add(nid)

        children = _node_children(nid)
        if not children:
            # Leaf: terminal per its own status (closed task/epic, or resolved gate).
            return _bead_is_terminal(bead)

        # Container: process children first (post-order / bottom-up).
        open_children: list[str] = []
        for child in children:
            if not visit(child):
                open_children.append(child.get("id"))

        if open_children:
            blocked.append({"id": nid, "title": bead.get("title"),
                            "open_children": open_children})
            return False

        # All children terminal → close this container unless already closed.
        if bead.get("status") == "closed":
            return True
        if dry_run:
            closed.append(nid)
            return True
        ok, err = _bd_close(nid, reason)
        if ok:
            closed.append(nid)
            return True
        errors.append({"id": nid, "error": err})
        blocked.append({"id": nid, "title": bead.get("title"),
                        "open_children": [], "close_error": err})
        return False

    root, unavailable = _bd_show_ex(root_id)
    if unavailable:
        # `bd` did not answer. We know NOTHING about the tree — reporting a clean
        # cascade would be a lie, and halting would block healthy work on an outage.
        return {
            "closed": [], "blocked": [],
            "errors": [{"id": root_id, "error": unavailable}],
            "verdict": "inconclusive", "passed": False,
            "reason": f"could not resolve root {root_id}: {unavailable}",
            "remediation": "Restore `bd` (see `bd doctor` / `/yf-beads-init`), then "
                           "re-run §6.4. Completion is NOT blocked by this verdict.",
            "dry_run": dry_run,
        }
    if root is None:
        # `bd` answered and the bead does not exist. DEFINITE negative — fail loud.
        # Previously this returned exit 0 with an empty walk, so a typo'd or stale
        # ${EPIC} reported a clean cascade over nothing: a silent pass indistinguishable
        # from success.
        return {
            "closed": [], "blocked": [],
            "errors": [{"id": root_id, "error": "root bead not found"}],
            "verdict": "fail", "passed": False,
            "reason": f"root bead {root_id} does not exist — nothing was cascaded",
            "remediation": f"Check the root id. `bd show {root_id}` returns nothing, so "
                           "the plan's **Epic:** field or the ${EPIC} variable is wrong "
                           "or stale.",
            "dry_run": dry_run,
        }

    visit(root)
    verdict = "fail" if blocked else "pass"
    return {
        "closed": closed, "blocked": blocked, "errors": errors,
        "verdict": verdict, "passed": verdict == "pass",
        "reason": (f"{len(blocked)} container(s) have a non-terminal child or failed to "
                   "close" if blocked else
                   f"cascade clean — {len(closed)} container(s) closed"),
        "remediation": ("Resolve the blocked beads listed above, then re-run §6.4."
                        if blocked else None),
        "dry_run": dry_run,
    }


@click.command()
@click.argument("root_id")
@click.option("--plan", "plan_ref", default=None,
              help="Plan id/ref for the close reason (e.g. plan-024-...). "
                   "Defaults to the root bead id.")
@click.option("--dry-run", is_flag=True,
              help="Report what would close without mutating any bead.")
@click.option("--json-output", "--json", "as_json", is_flag=True,
              help="Emit structured JSON. Default is a human-readable report.")
def main(root_id: str, plan_ref: str, dry_run: bool, as_json: bool):
    """Cascade-close all-terminal containers under ROOT_ID (REQ-PLAN-067).

    Exit code: `0` when every container either closed or was already closed (clean);
    `2` when the `blocked` set is non-empty (fail-loud — a container has a still-open
    child, or a close failed). The caller (yf-plan §6.4) must **halt** completion on a
    non-zero exit and never set status `complete`.
    """
    ref = plan_ref or root_id
    reason = f"Plan {ref} complete — cascade-close container (REQ-PLAN-067)"
    result = cascade(root_id, reason, dry_run)
    result["root"] = root_id

    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        verb = "would close" if dry_run else "closed"
        if result.get("verdict") in ("fail", "inconclusive") and not result["closed"] \
                and not result["blocked"]:
            # Root-resolution verdicts: report the reason rather than the misleading
            # "no containers to close", which reads as success.
            label = "FAIL-LOUD" if result["verdict"] == "fail" else "INCONCLUSIVE"
            click.echo(f"cascade: {label} — {result['reason']}")
            if result.get("remediation"):
                click.echo(f"  {result['remediation']}")
            sys.exit(2 if result["verdict"] == "fail" else 0)
        if result["closed"]:
            click.echo(f"cascade: {verb} {len(result['closed'])} container(s): "
                       + ", ".join(result["closed"]))
        else:
            click.echo(f"cascade: no containers to close")
        if result["blocked"]:
            click.echo("cascade: BLOCKED (fail-loud) — completion must halt:")
            for b in result["blocked"]:
                if b.get("close_error"):
                    click.echo(f"  - {b['id']}: close failed — {b['close_error']}")
                else:
                    click.echo(f"  - {b['id']}: open child(ren) "
                               + ", ".join(b["open_children"]))

    # REQ-PLAN-067 / REQ-COMPLETE-003(c):
    #   fail          -> exit 2 (halt)   — blocked containers, OR a root bd says is absent
    #   inconclusive  -> exit 0 (report) — bd did not answer; never halt on an outage
    #   pass          -> exit 0
    sys.exit(2 if result.get("verdict") == "fail" else 0)


if __name__ == "__main__":
    main()
