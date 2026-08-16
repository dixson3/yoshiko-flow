---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-debug-release-parity
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
---

# E3 — Debug/release embed parity, and the actual mechanism of #137

**Question.** What breaks if debug and release embed `skills/` consistently, and which
direction of consistency is acceptable?

**Headline.** The experiment answered its question, and in doing so **partially refuted
the root cause stated in #137 and in `AGENTS.md`**. That refutation is the more important
result.

## #137's real mechanism is an ADDITIONS-ONLY blind spot

`AGENTS.md:74-78` claims *"an incremental release rebuild does not observe `skills/`
edits"*. Measured, that is **false for two of the three edit kinds**:

| Edit under `skills/` | `cargo build --release` | New content in binary? |
| :-- | :-- | :-: |
| **Modify** an existing file | `Compiling yf … Finished in 5.65s` | **yes** |
| **Delete** a file | recompiles, 7.43s | **yes** |
| **Add** a new file | `Finished … in 0.21s` — **no recompile** | **NO** |

rust-embed emits `include_bytes!`, which rustc records in dep-info — so modifications and
deletions *are* observed. Only **additions** are missed, because discovering a new path
requires macro re-expansion.

**The blind spot is profile-independent.** Reproduced in debug with `debug-embed` enabled:
new file added → `Finished in 0.16s`, file absent from output. It is a property of
rust-embed's dependency tracking, not of the release profile.

**Consequence for the plan: making the profiles consistent does not fix #137.** It would
*import the bug into the dev loop*.

## D2 is measured — and its repaired form works

Plan decision D2 rejected issue direction 1 on the reasoning that emitting any
`rerun-if-changed` disables cargo's default "re-run on any package change", making the git
hash stale. **Both halves of that reasoning are now measured:**

- **Naive one-liner regresses the dirty flag, as predicted.** With only
  `rerun-if-changed=../skills`, `touch yf/src/main.rs` recompiles the crate but `build.rs`
  does **not** re-run (verified with a file-appending probe counter — stayed at 1). This is
  exactly the failure `build.rs:51-58` warns about.
- **The compound form restores it.** Adding `rerun-if-changed=src` and
  `rerun-if-changed=Cargo.toml` alongside `../skills` makes `build.rs` re-run on **both** a
  `src` touch and a `skills/` change (probe counter incremented in both cases).
- **And it closes the blind spot.** With `rerun-if-changed=../skills`, a *new* skills file
  triggers a release recompile and lands in the binary.

So direction 1 **as worded in the issue** is indeed wrong, but **direction 1 repaired** is
a measured, working, ~zero-cost fix for the actual defect.

## Direction B (release reads from disk) is impossible, not a trade-off

Refuted on four independent grounds:

1. Contradicts **REQ-YF-EMBED-001** verbatim (`SPEC.md:425-426`, *"no network or repo
   clone required to install"*) and **REQ-YF-EMBED-002** (*"from the binary alone"*).
2. Distribution is a bare binary — `Cargo.toml:37` `installers = ["shell", "homebrew"]`;
   **REQ-YF-SELF-002** describes `self update` extracting *"the inner binary"*. There is no
   `skills/` payload in the artifact and nowhere to put one.
3. **GR-011** — small, dependency-light binary; everything `yf` owns must ship inside it.
4. A Homebrew or `curl|sh` user has no checkout, so `skills install` would read nothing.

Record as **refuted, not deferred**.

## Direction A (debug also bakes) — safe, cheap, but insufficient

- **Breaks zero tests.** Full suite with `debug-embed` on: **358 passed** (lib) + 2
  (`flow_install_e2e`) + 4 (`harness_cross_e2e`), 0 failed.
- **Costs:** +1.03 MB binary (25.16 → 26.19 MB, +4.1%); +0.07s per crate recompile
  (1.34 → 1.41s, ~5%).
- **Real ergonomic cost:** today a `skills/`-only edit costs **zero** rebuild; under
  Direction A every skills edit forces a ~1.3s `yf` recompile before `./target/debug/yf`
  reflects it.
- **It is the spec-conformant direction.** Under the status quo the debug binary literally
  does **not** satisfy REQ-YF-EMBED-001/002 — it needs a repo clone at runtime. **The
  asymmetry is a latent spec violation in the debug profile.**

## The documentation is already wrong in four places — in the opposite direction

Exactly **one** paragraph in the repo relies on the current behavior — `AGENTS.md:74-84`,
and it relies on it for a *convenience* claim, not a correctness one. Meanwhile four places
already assert the **opposite** (that debug bakes in), and are wrong today:

- `TESTING.md:80` — `cargo build   # re-embeds the MODIFIED ../skills`
- `skills/yf-plan/test-harness/bootstrap.sh:50-51` — *"rust-embed bakes `../skills` at
  compile time … a rebuild is REQUIRED"*
- `skills/yf-plan/test-harness/README.md:17-20` — *"The bytes the resolver loads were
  frozen into the `yf` binary at its last `cargo build`"*
- `yf/src/embed.rs:3-4` — profile-unqualified *"compiled into the binary at build time"*

Direction A would make all four true. Nothing in `web/`, `README.md`, `docs/`, or CI
depends on the asymmetry.

## CI never exercises the shipping embed path

**No test depends on the asymmetry, and no test can currently detect a stale embed.**
`cargo test --workspace` (the `CHANGE-VALIDATION.md` row and `.github/workflows/ci.yml:47`)
builds **debug** — so the embed unit tests, including the REQ-YF-EMBED-003 frontmatter
integrity test, and both e2e suites assert against the **on-disk** tree, not the baked one.

**The #137 class of defect is structurally invisible to the entire test suite.**

## Recommendation (E3's own)

Ship **C1 + C2**; treat Direction A as an optional follow-on.

- **C1 (must)** — compound `rerun-if-changed` (`../skills`, `src`, `Cargo.toml`) in
  `build.rs`, amending the `build.rs:51-58` rationale. This is the actual fix for #137, in
  the profile that ships. Cost ≈ zero.
- **C2 (should)** — add a cargo feature `embed-in-debug = ["rust-embed/debug-embed"]`
  (measured to build clean, 26,184,912 B) plus one CI job
  `cargo test --workspace --features embed-in-debug`. **This is the only proposed change
  that would have caught #137 automatically.**
- **C3 — a debug runtime banner: rejected.** Advertises a behavior that is not the defect,
  adds noise, would have prevented nothing.
- **Docs (must, regardless of direction)** — `AGENTS.md:74-78`'s causal claim is
  measurably wrong and is the sentence that would send a future reader to the wrong fix.

If the "make them consistent" decision is held fixed: Direction A is the only viable
direction, is safe, and **must be paired with C1** or it silently regresses the dev loop
(it imports the addition blind spot into `cargo test`).

## Housekeeping

Worktree returned clean (`git status --porcelain` empty); nothing committed or pushed;
`~/.claude` and `~/.local/bin` untouched.
