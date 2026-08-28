//! Marker-gated skills-tree removal (`REQ-YF-MARK-006`) — the migration primitive.
//!
//! ## Why this exists, in one sentence
//!
//! `yf harness skills status` is **name-keyed against the embedded skill set**, so it can only
//! answer questions about names `yf` already knows. A directory `yf` deployed and later renamed,
//! a skill an operator placed by hand, a symlink somebody dropped in — none of those are
//! *findings* it reports, they are absent from its **input**. Measured on the plan-055 target
//! machine: **124** directories across the four skills roots, **76** visible to the name-keyed
//! walk, **48 structurally invisible**.
//!
//! Removing private skills trees safely needs to see all 124. That is the primitive this module
//! adds: a **directory walk**, plus a classifier over the existing [`crate::marker`] helpers.
//!
//! ## Four outcomes, not three
//!
//! | Outcome | Evidence | Action |
//! | :-- | :-- | :-- |
//! | [`Outcome::OwnedAndUnmodified`] | well-formed marker **and** recomputed marker-stripped tree hash == the marker's `tree=` | remove (under `apply`) |
//! | [`Outcome::OwnedButModified`] | well-formed marker, hash differs | **keep and report** |
//! | [`Outcome::NoMarker`] | `SKILL.md` readable, no marker | **keep, report as foreign** |
//! | [`Outcome::Undetermined`] | unreadable/absent `SKILL.md`, malformed marker, or a **symlink** | **keep, report as unjudgeable** |
//!
//! Collapsing `Undetermined` into `NoMarker` would assert a positive fact — "an operator placed
//! this" — from an **absence of evidence**. Three genuinely different facts land in that fourth
//! bucket, and on the plan-055 target machine the symlink case is **live**, not hypothetical:
//! `~/.agents/skills/terminal-browser` points into an application's own directory, so a tree-hash
//! walk that *followed* it would hash a tree `yf` does not own and could not have authored.
//! Hence: **the walk does not follow symlinks.**
//!
//! ## The apply is REVERSIBLE
//!
//! `apply` **moves** each removable directory into a timestamped quarantine and never unlinks.
//! That is a property of `REQ-YF-MARK-006` itself rather than of any one caller: an `apply` that
//! cannot be undone is the "overwrites with no backup" hazard, and building a second instance of
//! it on the skills surface while excluding the first on surface grounds would be incoherent.
//!
//! ## What this module deliberately is NOT
//!
//! It is **not** `yf harness skills remove`. That verb is a name-keyed `remove_dir_all` with no
//! ownership check whatsoever — measured deleting a hand-placed operator directory (`SKILL.md` +
//! `OPERATOR-DATA.txt`, no marker) and reporting `"removed":[…]` with no warning. Routing the
//! migration through it *is* the unchecked deletion this module exists to refuse.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use crate::marker;

/// One member directory's classification (`REQ-YF-MARK-006`).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Outcome {
    /// A well-formed marker and a matching recomputed tree hash: `yf` authored it and nothing
    /// has touched it. The **only** removable outcome.
    OwnedAndUnmodified,
    /// A well-formed marker, but the recomputed hash differs — someone edited it. Kept.
    OwnedButModified,
    /// `SKILL.md` reads fine and carries no marker: foreign, hand-placed. Kept.
    NoMarker,
    /// The classification could not be made **at all**. Kept, and reported as unjudgeable.
    Undetermined,
}

impl Outcome {
    /// The wire spelling (the JSON verdict schema's `outcome` values).
    pub fn as_str(self) -> &'static str {
        match self {
            Outcome::OwnedAndUnmodified => "owned-and-unmodified",
            Outcome::OwnedButModified => "owned-but-modified",
            Outcome::NoMarker => "no-marker",
            Outcome::Undetermined => "undetermined",
        }
    }

    /// Whether `apply` may remove a member with this outcome. Exactly one outcome is removable;
    /// the default for everything else is **keep**, per `REQ-YF-TUNE-029`'s conservative-keep.
    pub fn is_removable(self) -> bool {
        matches!(self, Outcome::OwnedAndUnmodified)
    }
}

/// One classified member of a skills root.
#[derive(Debug, Clone)]
pub struct Member {
    /// Absolute path to the member directory.
    pub path: PathBuf,
    /// The directory's own name (what a harness would load it as).
    pub name: String,
    pub outcome: Outcome,
    /// Human-readable evidence for the outcome — the *reason*, never a restatement of it.
    pub reason: String,
    /// D-2f: this kept directory's skill name also exists in the shared skills root, so keeping
    /// it preserves a divergent duplicate — the very hazard the shared root removes.
    pub shadows_shared_root: bool,
}

// --- 1.2 · the enumerator ------------------------------------------------------------------

/// Enumerate every member **directory** of a skills root — including members absent from the
/// embedded skill set, which is the whole point (`REQ-YF-MARK-006`).
///
/// Symlinked members are **included in the enumeration** and marked via `is_symlink`; they are
/// classified `Undetermined` downstream. Including-then-classifying is deliberate: silently
/// dropping them from the walk would make an unjudgeable member indistinguishable from an absent
/// one, which is the conflation the fourth outcome exists to prevent.
///
/// A missing root is `Ok(vec![])` — an absent private tree is a legitimate state (it may already
/// have been migrated). An **unreadable** root is an `Err`: that is the instrument failing, not
/// a finding about the tree.
pub fn enumerate_root(root: &Path) -> io::Result<Vec<(PathBuf, bool)>> {
    if !root.exists() {
        return Ok(Vec::new());
    }
    let mut out = Vec::new();
    for entry in fs::read_dir(root)? {
        let entry = entry?;
        let path = entry.path();
        // `symlink_metadata` does NOT follow the link — that is the whole reason it is used
        // here rather than `metadata`.
        let md = fs::symlink_metadata(&path)?;
        let is_symlink = md.file_type().is_symlink();
        if is_symlink || md.is_dir() {
            out.push((path, is_symlink));
        }
    }
    out.sort_by(|a, b| a.0.cmp(&b.0));
    Ok(out)
}

// --- 1.3 · the four-outcome classifier -----------------------------------------------------

/// Classify one member directory into exactly one [`Outcome`].
///
/// Built over the existing [`crate::marker`] helpers rather than replacing them: the plan-055
/// RED baseline measured that `status` **classifies** correctly (it separated the unmodified copy
/// from the modified one) and only fails to **enumerate**. So the gap is enumeration, and the
/// classifier reuses what already works.
pub fn classify(path: &Path, is_symlink: bool) -> Member {
    let name = path
        .file_name()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_default();

    let mk = |outcome: Outcome, reason: String| Member {
        path: path.to_path_buf(),
        name: name.clone(),
        outcome,
        reason,
        shadows_shared_root: false,
    };

    if is_symlink {
        return mk(
            Outcome::Undetermined,
            "a symlink — the walk does not follow it, because hashing through a link hashes a \
             tree yf does not own and could not have authored"
                .to_string(),
        );
    }

    let skill_md = path.join("SKILL.md");
    let text = match fs::read_to_string(&skill_md) {
        Ok(t) => t,
        Err(e) => {
            return mk(
                Outcome::Undetermined,
                format!("SKILL.md is unreadable or absent ({e}) — nothing can be concluded"),
            )
        }
    };

    // A marker LINE that is present but does not parse is MALFORMED — undetermined, never
    // "no marker". Absence of a marker and a marker we failed to read are different facts.
    let has_marker_line = text
        .lines()
        .any(|l| l.trim_start().starts_with("<!-- yf-skills:"));
    let parsed = marker::parse_marker(&text);

    match (has_marker_line, parsed) {
        (true, None) => mk(
            Outcome::Undetermined,
            "a yf marker line is present but MALFORMED (no parseable `v=`/`tree=`) — a marker we \
             cannot read is not the same fact as no marker at all"
                .to_string(),
        ),
        (_, None) => mk(
            Outcome::NoMarker,
            "SKILL.md reads cleanly and carries no yf marker — foreign, presumed operator-placed"
                .to_string(),
        ),
        (_, Some((_version, tree))) => match marker::deployed_tree_hash(path) {
            Err(e) => mk(
                Outcome::Undetermined,
                format!("the tree hash could not be recomputed ({e}) — the marker cannot be checked"),
            ),
            Ok(actual) if actual == tree => mk(
                Outcome::OwnedAndUnmodified,
                format!("marker tree={} matches the recomputed hash", &tree[..tree.len().min(12)]),
            ),
            Ok(actual) => mk(
                Outcome::OwnedButModified,
                format!(
                    "marker tree={} but the recomputed hash is {} — the copy has been edited",
                    &tree[..tree.len().min(12)],
                    &actual[..actual.len().min(12)]
                ),
            ),
        },
    }
}

/// Classify an entire root, then apply D-2f's shadow flag against `shared_root`.
///
/// The flag is set only on **kept** members: a removable one is about to stop existing, so
/// calling it a divergence hazard would be noise.
pub fn classify_root(root: &Path, shared_root: Option<&Path>) -> io::Result<Vec<Member>> {
    let mut members: Vec<Member> = enumerate_root(root)?
        .into_iter()
        .map(|(p, sym)| classify(&p, sym))
        .collect();
    if let Some(shared) = shared_root {
        for m in members.iter_mut() {
            if !m.outcome.is_removable() && shared.join(&m.name).exists() {
                m.shadows_shared_root = true;
            }
        }
    }
    Ok(members)
}

// --- 1.4 · the verdict + the reversible apply ----------------------------------------------

/// The machine-readable verdict — **the schema is fixed here**, beside the emitting code,
/// because `scripts/checks/check-migration-dryrun.sh` is written against it.
///
/// ```json
/// {"delete":      [{"path": "...", "outcome": "owned-and-unmodified"}],
///  "kept":        [{"path": "...", "outcome": "...", "reason": "...", "shadows_shared_root": false}],
///  "undetermined":[{"path": "...", "reason": "..."}]}
/// ```
///
/// `undetermined` members appear in `undetermined` **only** — not also in `kept`. The gate reads
/// the two keys as disjoint populations, and a member counted twice would read as two findings.
pub fn verdict(members: &[Member], roots: &[PathBuf], applied: Option<&Path>) -> Value {
    let mut delete = Vec::new();
    let mut kept = Vec::new();
    let mut undetermined = Vec::new();
    for m in members {
        match m.outcome {
            Outcome::OwnedAndUnmodified => delete.push(json!({
                "path": m.path.to_string_lossy(),
                "outcome": m.outcome.as_str(),
            })),
            Outcome::Undetermined => undetermined.push(json!({
                "path": m.path.to_string_lossy(),
                "reason": m.reason,
            })),
            _ => kept.push(json!({
                "path": m.path.to_string_lossy(),
                "outcome": m.outcome.as_str(),
                "reason": m.reason,
                "shadows_shared_root": m.shadows_shared_root,
            })),
        }
    }
    let mut v = json!({
        "command": "harness skills prune-private",
        "roots": roots.iter().map(|r| r.to_string_lossy()).collect::<Vec<_>>(),
        "dry_run": applied.is_none(),
        "delete": delete,
        "kept": kept,
        "undetermined": undetermined,
    });
    if let Some(q) = applied {
        v["quarantine"] = json!(q.to_string_lossy());
        v["restore"] = json!(restore_command(q));
    }
    v
}

/// The documented one-line restore for a quarantine directory. Emitted **with** the verdict, so
/// the undo is in the operator's hands at the moment the removal happens rather than in a
/// document they would have to go find.
pub fn restore_command(quarantine: &Path) -> String {
    format!(
        "for d in {}/*/*; do mv -f \"$d\" \"$(cat \"${{d%/*}}/.origin\")/\"; done",
        quarantine.display()
    )
}

/// Quarantine directory name for a run: `<parent>/.yf-quarantine/<timestamp>`.
pub fn quarantine_dir(anchor: &Path, stamp: &str) -> PathBuf {
    anchor.join(".yf-quarantine").join(stamp)
}

/// **Move** every removable member into `quarantine`, recording each one's origin directory so
/// the restore is mechanical rather than reconstructed.
///
/// Never unlinks, and never touches a member whose outcome is not [`Outcome::OwnedAndUnmodified`].
/// Falls back to copy-then-remove across a filesystem boundary (`rename` fails with `EXDEV`).
pub fn quarantine_removable(members: &[Member], quarantine: &Path) -> io::Result<Vec<PathBuf>> {
    let mut moved = Vec::new();
    for m in members.iter().filter(|m| m.outcome.is_removable()) {
        let origin = m
            .path
            .parent()
            .ok_or_else(|| io::Error::other(format!("{} has no parent", m.path.display())))?;
        // One bucket per origin root keeps two same-named skills from different roots apart.
        let bucket = quarantine.join(sanitize(&origin.to_string_lossy()));
        fs::create_dir_all(&bucket)?;
        fs::write(bucket.join(".origin"), origin.to_string_lossy().as_bytes())?;
        let dest = bucket.join(&m.name);
        match fs::rename(&m.path, &dest) {
            Ok(()) => {}
            Err(_) => {
                copy_tree(&m.path, &dest)?;
                fs::remove_dir_all(&m.path)?;
            }
        }
        moved.push(dest);
    }
    Ok(moved)
}

fn sanitize(s: &str) -> String {
    s.chars()
        .map(|c| if c.is_ascii_alphanumeric() { c } else { '_' })
        .collect()
}

fn copy_tree(src: &Path, dst: &Path) -> io::Result<()> {
    fs::create_dir_all(dst)?;
    for entry in fs::read_dir(src)? {
        let entry = entry?;
        let from = entry.path();
        let to = dst.join(entry.file_name());
        if fs::symlink_metadata(&from)?.is_dir() {
            copy_tree(&from, &to)?;
        } else {
            fs::copy(&from, &to)?;
        }
    }
    Ok(())
}

// --- command entry point --------------------------------------------------------------------

/// `yf harness skills prune-private` (REQ-YF-MARK-006).
///
/// Exit code: `SUCCESS` on a clean dry-run or a clean apply; `FAILURE` when a root could not be
/// read or a quarantine move failed — an instrument failure, never a verdict about the tree.
pub fn run(args: &crate::cli::PrunePrivateArgs) -> anyhow::Result<std::process::ExitCode> {

    let roots: Vec<PathBuf> = if !args.root.is_empty() {
        args.root.clone()
    } else {
        default_private_roots(args.scope)
    };

    let shared = args
        .shared_root
        .clone()
        .or_else(|| default_shared_root(args.scope));

    let mut members = Vec::new();
    for r in &roots {
        members.extend(classify_root(r, shared.as_deref())?);
    }

    // The apply anchors the quarantine beside the FIRST root, so the moved tree stays on the
    // same filesystem as its origin in the common case (a `rename`, not a copy).
    let applied = if args.apply {
        let stamp = timestamp();
        let anchor = roots
            .first()
            .and_then(|r| r.parent())
            .map(|p| p.to_path_buf())
            .unwrap_or_else(|| PathBuf::from("."));
        let q = quarantine_dir(&anchor, &stamp);
        fs::create_dir_all(&q)?;
        quarantine_removable(&members, &q)?;
        Some(q)
    } else {
        None
    };

    let v = verdict(&members, &roots, applied.as_deref());
    if args.json {
        println!("{}", serde_json::to_string_pretty(&v)?);
    } else {
        print_human(&v);
    }
    Ok(std::process::ExitCode::SUCCESS)
}

/// The **private** (non-shared) skills roots for a scope — the roots this migration empties.
///
/// Derived from the descriptor table by *difference*: every distinct resolved skills root that
/// is not the shared one. Deriving it rather than hardcoding two paths means the set shrinks to
/// empty on its own once the collapse lands, instead of naming directories that no longer exist.
pub fn default_private_roots(scope: crate::cli::Scope) -> Vec<PathBuf> {
    let shared = default_shared_root(scope);
    let mut out: Vec<PathBuf> = Vec::new();
    for d in crate::harness_desc::DESCRIPTORS {
        // claude-code's private root is DELIBERATELY EXCLUDED: it is not "unread", it is the one
        // root claude-code actually reads (`.agents/` occurs zero times in its binary). Pruning
        // it would delete a live deployment.
        if d.id == "claude-code" {
            continue;
        }
        let root = crate::dest::resolve_skills_dir(scope, d.id, None);
        if Some(&root) != shared.as_ref() && !out.contains(&root) {
            out.push(root);
        }
    }
    out
}

fn default_shared_root(scope: crate::cli::Scope) -> Option<PathBuf> {
    Some(crate::dest::resolve_skills_dir(scope, "agents", None))
}

fn timestamp() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    format!("{secs}")
}

fn print_human(v: &Value) {
    let n = |k: &str| v[k].as_array().map(|a| a.len()).unwrap_or(0);
    if v["dry_run"].as_bool().unwrap_or(true) {
        println!("prune-private: DRY RUN — nothing was written.");
    } else {
        println!(
            "prune-private: APPLIED — moved to quarantine {}",
            v["quarantine"].as_str().unwrap_or("?")
        );
        println!("  restore: {}", v["restore"].as_str().unwrap_or(""));
    }
    println!(
        "  delete {} · kept {} · undetermined {}",
        n("delete"),
        n("kept"),
        n("undetermined")
    );
    for e in v["delete"].as_array().into_iter().flatten() {
        println!("    [delete]       {}", e["path"].as_str().unwrap_or(""));
    }
    for e in v["kept"].as_array().into_iter().flatten() {
        let shadow = if e["shadows_shared_root"].as_bool().unwrap_or(false) {
            "  ⚠ SHADOWS the shared root — divergence hazard"
        } else {
            ""
        };
        println!(
            "    [{}] {}{}\n        {}",
            e["outcome"].as_str().unwrap_or(""),
            e["path"].as_str().unwrap_or(""),
            shadow,
            e["reason"].as_str().unwrap_or("")
        );
    }
    for e in v["undetermined"].as_array().into_iter().flatten() {
        println!(
            "    [undetermined] {}\n        {}",
            e["path"].as_str().unwrap_or(""),
            e["reason"].as_str().unwrap_or("")
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::os::unix::fs::symlink;

    /// A skills-root fixture built in a temp dir. Mirrors the plan-055 Issue 1.1 RED baseline
    /// **exactly** — one member per outcome — so the test and the recorded baseline are the same
    /// experiment rather than two similar ones.
    struct Fixture {
        root: PathBuf,
    }

    impl Fixture {
        fn new(tag: &str) -> Self {
            let root = std::env::temp_dir().join(format!(
                "yf-prune-private-{tag}-{}-{}",
                std::process::id(),
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .map(|d| d.as_nanos())
                    .unwrap_or(0)
            ));
            fs::create_dir_all(&root).unwrap();
            Fixture { root }
        }

        /// A skill dir with the given body and, optionally, an injected marker whose `tree=` is
        /// either the true recomputed hash (unmodified) or a deliberate lie (modified).
        fn skill(&self, name: &str, body: &str, marker_kind: MarkerKind) -> PathBuf {
            let dir = self.root.join(name);
            fs::create_dir_all(&dir).unwrap();
            let skill_md = format!("---\nname: {name}\n---\n{body}");
            fs::write(dir.join("SKILL.md"), &skill_md).unwrap();
            match marker_kind {
                MarkerKind::None => {}
                MarkerKind::Malformed => {
                    let marked = skill_md.replace(
                        "---\n",
                        "---\n<!-- yf-skills: this line has no v= or tree= -->\n",
                    );
                    // replace() hits the opening fence too; rewrite deterministically instead.
                    let _ = marked;
                    let text = format!(
                        "---\nname: {name}\n---\n<!-- yf-skills: no parseable fields -->\n{body}"
                    );
                    fs::write(dir.join("SKILL.md"), text).unwrap();
                }
                MarkerKind::Truthful | MarkerKind::Lying => {
                    // Inject with a placeholder, recompute the real (marker-stripped) hash, then
                    // re-inject either it or a lie.
                    let placeholder = crate::marker::inject_marker(&skill_md, "test", &"0".repeat(64));
                    fs::write(dir.join("SKILL.md"), placeholder).unwrap();
                    let real = crate::marker::deployed_tree_hash(&dir).unwrap();
                    let tree = if matches!(marker_kind, MarkerKind::Truthful) {
                        real
                    } else {
                        "f".repeat(64)
                    };
                    let text = crate::marker::inject_marker(&skill_md, "test", &tree);
                    fs::write(dir.join("SKILL.md"), text).unwrap();
                }
            }
            dir
        }
    }

    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.root);
        }
    }

    enum MarkerKind {
        Truthful,
        Lying,
        Malformed,
        None,
    }

    fn outcome_of(members: &[Member], name: &str) -> Outcome {
        members
            .iter()
            .find(|m| m.name == name)
            .unwrap_or_else(|| panic!("member {name} was NOT ENUMERATED — that is the defect"))
            .outcome
    }

    // REQ-YF-MARK-006 / SC5 — all FOUR outcomes are distinguished, and the three non-removable
    // ones are KEPT. The assertion that matters most is the last one: nothing but
    // `owned-and-unmodified` is ever removable.
    #[test]
    fn marker_gated_removal_four_outcomes() {
        let f = Fixture::new("four");
        f.skill("owned-clean", "# clean\n", MarkerKind::Truthful);
        f.skill("owned-edited", "# edited\n", MarkerKind::Lying);
        f.skill("operator-notes", "# hand placed\n", MarkerKind::None);
        symlink(f.root.join("owned-clean"), f.root.join("linked")).unwrap();

        let members = classify_root(&f.root, None).unwrap();
        assert_eq!(members.len(), 4, "all four members must be enumerated");

        assert_eq!(outcome_of(&members, "owned-clean"), Outcome::OwnedAndUnmodified);
        assert_eq!(outcome_of(&members, "owned-edited"), Outcome::OwnedButModified);
        assert_eq!(outcome_of(&members, "operator-notes"), Outcome::NoMarker);
        assert_eq!(outcome_of(&members, "linked"), Outcome::Undetermined);

        // The conservative-keep invariant, stated as an assertion rather than as prose.
        let removable: Vec<&str> = members
            .iter()
            .filter(|m| m.outcome.is_removable())
            .map(|m| m.name.as_str())
            .collect();
        assert_eq!(
            removable,
            ["owned-clean"],
            "exactly one outcome is removable; everything else is kept"
        );

        // The verdict's three populations are DISJOINT — an undetermined member must not also
        // appear under `kept`, or the gate reads one member as two findings.
        let v = verdict(&members, &[f.root.clone()], None);
        assert_eq!(v["delete"].as_array().unwrap().len(), 1);
        assert_eq!(v["kept"].as_array().unwrap().len(), 2);
        assert_eq!(v["undetermined"].as_array().unwrap().len(), 1);
        assert!(v["dry_run"].as_bool().unwrap());
    }

    // REQ-YF-MARK-006 / SC6 — the DEFAULT invocation performs NO deletion. Asserted over the
    // filesystem, not over a flag: a dry-run that sets `dry_run: true` while removing a
    // directory would pass a flag assertion.
    #[test]
    fn remover_default_is_dry_run() {
        let f = Fixture::new("dryrun");
        let clean = f.skill("owned-clean", "# clean\n", MarkerKind::Truthful);

        let members = classify_root(&f.root, None).unwrap();
        let v = verdict(&members, &[f.root.clone()], None);

        assert!(v["dry_run"].as_bool().unwrap());
        assert_eq!(v["delete"].as_array().unwrap().len(), 1);
        assert!(
            clean.is_dir(),
            "the default path must not remove anything — the directory is still there"
        );
        assert!(clean.join("SKILL.md").is_file());
    }

    // REQ-YF-MARK-006 / SC7 — the enumerator sees a directory that is NOT in the embedded skill
    // set. This is the case `status` is structurally blind to, and it is the reason Epic 1
    // exists at all.
    #[test]
    fn enumerator_sees_foreign_directory() {
        let f = Fixture::new("foreign");
        f.skill("definitely-not-an-embedded-yf-skill", "# hand placed\n", MarkerKind::None);

        let found = enumerate_root(&f.root).unwrap();
        assert_eq!(found.len(), 1);
        assert_eq!(
            found[0].0.file_name().unwrap(),
            "definitely-not-an-embedded-yf-skill"
        );

        // And it is classified as foreign rather than silently ignored.
        let members = classify_root(&f.root, None).unwrap();
        assert_eq!(
            outcome_of(&members, "definitely-not-an-embedded-yf-skill"),
            Outcome::NoMarker
        );
    }

    // REQ-YF-MARK-006 — a MALFORMED marker is `undetermined`, NOT `no-marker`. The two are
    // different facts: "there is no marker" and "there is a marker we could not read". This is
    // the assertion that keeps the fourth outcome from collapsing into the third.
    #[test]
    fn malformed_marker_is_undetermined_not_foreign() {
        let f = Fixture::new("malformed");
        f.skill("broken-marker", "# body\n", MarkerKind::Malformed);
        let members = classify_root(&f.root, None).unwrap();
        assert_eq!(outcome_of(&members, "broken-marker"), Outcome::Undetermined);
        assert!(members[0].reason.contains("MALFORMED"));
    }

    // REQ-YF-MARK-006 — an unreadable/absent SKILL.md is `undetermined`.
    #[test]
    fn unreadable_member_is_undetermined() {
        let f = Fixture::new("unreadable");
        fs::create_dir_all(f.root.join("no-skill-md")).unwrap();
        let members = classify_root(&f.root, None).unwrap();
        assert_eq!(outcome_of(&members, "no-skill-md"), Outcome::Undetermined);
    }

    // REQ-YF-MARK-006 — an EMPTY root yields an empty verdict, and an ABSENT root is `Ok`, not
    // an error: a private tree that has already been migrated away is a legitimate state.
    #[test]
    fn empty_and_absent_roots_are_not_errors() {
        let f = Fixture::new("empty");
        assert!(enumerate_root(&f.root).unwrap().is_empty());
        let absent = f.root.join("nope").join("still-nope");
        assert!(enumerate_root(&absent).unwrap().is_empty());
    }

    // D-2f — a KEPT directory whose name also exists in the shared root is flagged as a live
    // divergence hazard. A REMOVABLE one is not: it is about to stop existing.
    #[test]
    fn kept_directory_shadowing_shared_root_is_flagged() {
        let f = Fixture::new("shadow");
        let shared = f.root.join("__shared");
        fs::create_dir_all(shared.join("owned-edited")).unwrap();
        fs::create_dir_all(shared.join("owned-clean")).unwrap();
        f.skill("owned-edited", "# edited\n", MarkerKind::Lying);
        f.skill("owned-clean", "# clean\n", MarkerKind::Truthful);

        let members = classify_root(&f.root, Some(&shared)).unwrap();
        let edited = members.iter().find(|m| m.name == "owned-edited").unwrap();
        let clean = members.iter().find(|m| m.name == "owned-clean").unwrap();
        assert!(edited.shadows_shared_root, "a kept shadowing copy is the hazard");
        assert!(
            !clean.shadows_shared_root,
            "a removable copy is not flagged — it is about to stop existing"
        );
    }

    // REQ-YF-MARK-006 — `apply` MOVES to quarantine and NEVER unlinks, and the moved tree is
    // byte-identical. This is the requirement's reversibility clause, asserted.
    #[test]
    fn apply_quarantines_rather_than_unlinking() {
        let f = Fixture::new("quarantine");
        let clean = f.skill("owned-clean", "# clean\n", MarkerKind::Truthful);
        let kept = f.skill("operator-notes", "# hand placed\n", MarkerKind::None);
        let before = fs::read_to_string(clean.join("SKILL.md")).unwrap();

        let members = classify_root(&f.root, None).unwrap();
        let q = f.root.join(".q");
        let moved = quarantine_removable(&members, &q).unwrap();

        assert_eq!(moved.len(), 1, "only the removable outcome is moved");
        assert!(!clean.exists(), "the origin is gone from the skills root");
        assert!(kept.is_dir(), "a kept member is untouched");
        assert!(moved[0].is_dir(), "the tree still EXISTS — it was moved, not unlinked");
        assert_eq!(
            fs::read_to_string(moved[0].join("SKILL.md")).unwrap(),
            before,
            "the quarantined copy is byte-identical"
        );
        // The origin is recorded, so the restore is mechanical rather than reconstructed.
        let origin = fs::read_to_string(moved[0].parent().unwrap().join(".origin")).unwrap();
        assert_eq!(PathBuf::from(origin), f.root);
    }

    // REQ-YF-MARK-006 — claude-code's root is NEVER a prune target. It is not an unread private
    // root; it is the one root claude-code actually reads, so pruning it would delete a live
    // deployment rather than a stale one.
    #[test]
    fn claude_code_root_is_never_a_prune_target() {
        for scope in [crate::cli::Scope::User, crate::cli::Scope::Project] {
            let roots = default_private_roots(scope);
            let claude = crate::dest::resolve_skills_dir(scope, "claude-code", None);
            assert!(
                !roots.contains(&claude),
                "claude-code's root must never be pruned ({scope:?})"
            );
        }
    }
}
