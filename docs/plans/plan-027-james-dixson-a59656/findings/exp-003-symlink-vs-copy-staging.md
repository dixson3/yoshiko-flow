---
type: Finding
okf_spec: OKF-PLAN
question: Can we symlink user-scope skill formulas into project-scope `.beads/formulas/`
verdict: Symlink resolution **works**, but symlink-as-artifact is a portability trap
  and is
---
# exp-003: Symlink vs copy staging for bd formula protos

**Question:** Can we symlink user-scope skill formulas into project-scope `.beads/formulas/`
instead of the per-invocation `cp -f`/`rm -f` copy dance? Is symlink the more maintainable option?

**Verdict:** Symlink resolution **works**, but symlink-as-artifact is a portability trap and is
incompatible with the current lifecycle. The real fix is a **preflight/doctor-owned, gitignored,
copy-based hybrid** — move staging out of the per-invocation SKILL body entirely.

## Empirical results (bd 1.1.0, embedded-dolt, macOS)

1. **Symlink resolution — WORKS.** `bd mol wisp plan-investigate` through a symlinked
   `.beads/formulas/plan-investigate.formula.toml → <source>` succeeds identically to the copy
   control (`created:1`, exit 0). bd follows the symlink transparently.
2. **Dangling symlink — indistinguishable from missing, and worse.** A broken link and an absent
   file both yield `Error: proto not found: plan-investigate` (exit 1). Worse: a dangling link
   still appears in `ls .beads/formulas/`, so an operator sees the formula "present" while bd
   reports it missing — a **false-presence trap** the copy approach never has.
3. **Portability / gitignore — `.beads/formulas/` is NOT gitignored.** bd's default
   `.beads/.gitignore` (verified in scratch and the real repo) has no `formulas/` entry;
   `git add` stages the entry. Git stores a symlink as mode `120000` with the blob = the
   **absolute machine-specific target path** (`/private/tmp/.../src/...` or `~/.claude/...`
   verbatim). A committed symlink hard-codes one machine's home → dangles on every other
   clone/machine. So a symlink must be **gitignored + locally created**, exactly like the copy —
   **no portability advantage earned.**
4. **Self-deletion incompatibility (decisive).** The current SKILL pattern ends each pour with
   `rm -f .beads/formulas/x.formula.toml`. A persistent symlink is incompatible — the skill would
   delete its own link on first use. Symlink only works if the `rm` is removed, i.e. a different
   lifecycle owner.

## Root-cause reframing

The plan-026 bug is **not** a copy-vs-symlink problem. The copy dance's real defect is that it is
**silently omittable** — a caller who skips the `cp` just gets `proto not found`. That is a
**lifecycle-ownership** problem: staging is a step repeated on every call and skippable, rather
than a single verified gate.

## Recommendation — HYBRID (preflight/doctor-owned copy staging)

1. **Preflight/doctor owns staging** — create-or-repair, idempotent: ensure each declared
   `.beads/formulas/<f>.formula.toml` exists and resolves. Prefer a **copy** (self-contained, no
   dangling-on-uninstall, no absolute-path leak); re-copy on source mtime change gives the
   "auto-tracks edits" benefit symlink was reaching for, without the dangle risk. A symlink is
   acceptable only if preflight also verifies-and-repairs dangling links each run.
2. **Gitignore `.beads/formulas/`** so staged formulas (copy or link) are never committed — closes
   the non-portability hole for either mechanism.
3. **Drop the per-invocation `cp`/`rm` from SKILL.md entirely.** The pour becomes just
   `bd mol pour/wisp …`, relying on preflight having staged the formula. This **eliminates the
   silent-omission bug class** — staging is one verified gate, not a skippable per-call step.
4. If a symlink is chosen anyway, the owner is still preflight/doctor and it **must** treat a
   dangling link as a repair action (relink to the current skill dir) — bd gives no distinguishing
   signal.

## Implication for plan-027

This converts the check from "detect the missing-staging bug" into "**own** staging so the bug is
structurally impossible." The new preflight/doctor check both *stages* (create/repair) and
*validates* formula resolvability, across user- and project-scope skills. The exp-001/002 findings
(yf kernel seam) determine where this lands in the kernel.
