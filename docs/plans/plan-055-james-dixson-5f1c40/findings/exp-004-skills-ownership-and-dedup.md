---
type: Finding
okf_spec: OKF-PLAN
id: exp-004-skills-ownership-and-dedup
description: Does an ownership manifest cover the SKILLS surface, and how does install behave on duplicate destinations?
---

# EXP-004 — skills ownership record + duplicate-destination behaviour

## Approach Tested

Source read of `yf/src/cmd/harness/{manifest,revert,tune}.rs`, `yf/src/cmd/{install,common,status}.rs`,
`yf/src/marker.rs`, `yf/src/dest.rs`, `yf/src/harness_desc.rs`, `yf/src/cmd/self_cmd/{sync,uninstall}.rs`,
and `SPEC.md` (`REQ-YF-INSTALL-002/007/008`, `REQ-YF-MARK-002/003`, `REQ-YF-TUNE-021/022/029`).

Then five sandbox experiments under **fake `HOME`s** (`sbA`–`sbE`) driving a locally built
`./target/debug/yf`, with `GIT_CONFIG_GLOBAL=/dev/null`. The operator's real `HOME` was never
touched; all sandboxes were removed and the worktree left clean.

## Result

### 1. The ownership manifest covers CONFIG and RULES only — there is no skills record

**measured.** The manifest is `<surface_dir>/.yf/harness-tune-manifest.json`, written by
`yf harness tune` — **not** by `yf harness skills install`. `SurfaceRecord` carries exactly three
fields and no fourth:

```rust
pub struct SurfaceRecord {
    pub harness: String,
    pub scope: String,
    pub config: Option<ConfigRecord>,   // keys_added + sets_unioned
    pub rules: Option<RuleRecord>,      // path, kind, begin/end marker, sha256
}
```

`grep -i skill` over `manifest.rs` returns **one** hit and it is a gitignore comment string, not a
field; over `revert.rs` it returns **zero**. After a `--tune` install under a fake HOME, all four
written manifests contained only a `rules` record, and
`find … -name harness-tune-manifest.json -exec grep -l skills {} \;` matched nothing. After a plain
`yf harness skills install`, `find $HOME -name '*manifest*' -o -name '.yf'` returned **empty** — the
skills install path writes no ownership record of any kind. `SPEC.md:1525` (`REQ-YF-TUNE-021`) scopes
the manifest to config dot-paths, unioned set elements, and rule managed-block markers; no REQ
describes a skills-surface ownership record.

**This is the decisive finding: nothing anywhere records that `yf` authored a skill tree.**

### 2. Install silently overwrites an operator-authored skill file

**measured (sbB1).** A hand-written `~/.agents/skills/yf-markdown-lint/SKILL.md` containing
`OPERATOR HAND-WRITTEN SKILL` was overwritten by `yf harness skills install` with `status:"ok"`, no
warning and no refusal. A sibling `MY-NOTES.md` survived (prune is opt-in, `REQ-YF-INSTALL-010`) and a
foreign sibling skill directory was untouched. `common::deploy_skill` performs a per-file
`std::fs::write` with no existence or marker check.

### 3. `yf harness skills remove` is a blind `remove_dir_all` — it deleted operator data

**measured (sbD1).** A hand-placed `~/.agents/skills/yf-markdown-lint/` (operator `SKILL.md`, no yf
marker, plus `OPERATOR-DATA.txt`) was **entirely deleted** by
`yf harness skills remove --harness agents yf-markdown-lint`, which reported
`"removed":["yf-markdown-lint"]`. The implementation (`yf/src/cmd/status.rs:249-254`) is a bare
name-match with no marker check and no manifest lookup:

```rust
for name in &sel.install {
    let skill_root = skills_dir.join(name);
    if skill_root.exists() {
        if !args.dry_run { std::fs::remove_dir_all(&skill_root)?; }
```

Side observation, out of this plan's scope: it joins the **raw** `name` rather than
`transform_skill_name`, so `remove` is already wrong for pi.

### 4. Duplicate destinations are already handled correctly

**measured (sbA).** `--harness codex --harness agents` resolves to **exactly one** destination —
`common::resolved_dests` dedupes by resolved absolute path, per `REQ-YF-INSTALL-002` and pinned by
`codex_and_agents_dedupe_to_one_destination`.

**measured (sbB2).** The cross-process case — `--harness codex` then `--harness agents` as two
invocations — writes the shared root twice, **sequentially, idempotently, byte-identically**. The
`SKILL_DIR_INSTALLED_AT` stamp was **identical** both times, because it derives from the destination
root (`marker::stamp_install_dest`) and not from the harness id. Two harness rows sharing one root
necessarily stamp the same string. This is reachable in practice: `yf self install`'s sync fans out
one child process per detected harness, and `SYNC_PRESENCE` lists `agents` and `codex` separately.
It is redundant work, **not a race and not a clobber**.

**measured (sbB3).** With no `--harness` and all five dirs seeded, install resolved **four**
destinations (`claude-code`, `codex`, `opencode`, `pi`), with `agents` collapsed into `codex`.

### 5. A weaker per-copy provenance signal exists, but no caller consults it before deleting

**measured.** Every yf-deployed `SKILL.md` carries two lines only yf writes: the integrity marker
`<!-- yf-skills: v=… tree=… -->` (`REQ-YF-MARK-002`) and the `SKILL_DIR_INSTALLED_AT` stamp.
`yf harness skills status --json` returns `{installed, up_to_date, complete, unmodified,
embedded_hash, marker_hash, state}`; on a yf-authored copy `marker_hash == embedded_hash` and
`unmodified: true`, and appending one line by hand flips it to `unmodified: false, state:"modified"`.

**measured (sbE).** `status` **cannot see foreign directories at all** — with `hand-placed-foreign/`
present, it appears **zero** times in the status JSON. `status` enumerates the *embedded* skill-name
set and probes for each; it never walks the destination directory.

**measured.** `yf self uninstall` explicitly refuses to touch skills (`uninstall.rs:238`,
`REQ-YF-SELF-004`, test `force_removes_and_leaves_skills_untouched`). The codebase's existing answer
to "can we safely delete a skills tree?" is *no, so don't*.

## Implications for Plan

- **D-2 as written is unimplementable.** "Delete only entries yf's ownership manifest says yf
  authored" names a record that does not exist for skills and never has. The decision must be
  re-scoped, not merely detailed.
- **The gap is smaller than "build a manifest."** The per-copy integrity marker plus the recomputed
  marker-stripped tree hash is already an ownership-and-untouched proof at exactly the granularity
  migration needs — per skill directory — and is already spec'd and already computed by `status`.
- **One primitive is genuinely missing: a directory walk.** `status` is name-keyed and blind to
  directories outside the embedded set, so a skill yf deployed and later renamed or dropped is
  invisible to every existing enumeration. A private-tree sweep needs an enumerator the codebase
  does not have.
- **The existing removal path must not be reused.** Shelling migration out to
  `yf harness skills remove` *is* the unchecked deletion the operator decided against — measured
  destroying operator-authored data.
- **Duplicate destinations need no fix.** The collapse to one shared root does not have to solve a
  race. The residual is the sync's per-harness fan-out writing the shared root repeatedly — after the
  collapse that becomes 4 redundant writes of one tree. Tidiness, not correctness.
- **`REQ-YF-INSTALL-007`'s parity test will fail on the collapse** — `spec_table_matches_shipped_descriptor`
  asserts the SPEC block says `"five rows"` and quotes every literal subpath. SPEC-first is enforced
  mechanically here, confirming D-6.

## Recommendations

1. **Re-scope D-2 from "ownership-checked" to "marker-checked" removal**, with the deployed
   `SKILL.md`'s `<!-- yf-skills: … -->` marker plus a matching recomputed tree hash as the ownership
   token.
2. **Add a SPEC requirement** for a directory-walking, marker-gated skills-tree removal with three
   outcomes: `owned-and-unmodified` → delete; `owned-but-modified` → **keep and report**;
   `no marker` → keep and report as foreign. Cite `REQ-YF-TUNE-029`'s conservative-keep as precedent.
   Default to a dry-run preview.
3. **File `yf harness skills remove`'s blind deletion as its own defect**, together with the
   co-located `transform_skill_name` bug that makes it wrong on pi.
4. **Budget the migration as its own epic ahead of the descriptor change**: a SPEC requirement, a
   directory-walk enumerator (the one missing primitive), a three-outcome classifier over existing
   `marker` helpers, a dry-run/apply CLI surface, and tests.
5. **Optionally dedupe the sync fan-out** by resolved skills path once the rows collapse.

## Confidence

- **measured:** the manifest schema and its three record types; zero skills hits in `manifest.rs`
  (bar a comment) and `revert.rs`; no record written by the skills install path; install's silent
  overwrite of an operator file; `skills remove` deleting an unmarked operator directory;
  within-invocation dedup to one destination; cross-process double-write being sequential and
  byte-identical with an identical stamp; four auto-detected destinations; `status`'s field set and
  its blindness to foreign directories; `self uninstall`'s refusal to touch skills.
- **inferred:** that `deploy_skill` cannot distinguish an operator-authored file it is about to
  overwrite (read from the absence of any check, corroborated by the sbB1 measurement); that a
  marker-gated removal is buildable on existing `marker`/`status` machinery — the primitives were
  measured to work, but **no existing caller consults the marker before deleting**, so the composed
  behaviour is untested.
