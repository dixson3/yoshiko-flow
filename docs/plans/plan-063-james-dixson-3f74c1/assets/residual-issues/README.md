# Residual findings — plan-063 Issue 6.1

Everything this plan **found and did not fix**, drafted here as issue bodies before filing.
Filing is an outward-facing write (`gh issue create`), so it is proposed here and performed
only on operator authorization; SC16 records the resulting URLs.

Each file is one issue body, ready for `gh issue create --body-file -`.

| Draft | Title | Severity | Source |
| :-- | :-- | :-- | :-- |
| [r1-unpushed-laundering.md](r1-unpushed-laundering.md) | L16 launders an unreadable unpushed count into `"0"` | med | EXP-003 |
| [r2-l14-cwd.md](r2-l14-cwd.md) | L14's `bd list` is the only close-chain subprocess launched without `cwd=ctx.root` | med | EXP-003 |
| [r3-l8-l15-injectability.md](r3-l8-l15-injectability.md) | L8–L15 use bare `subprocess.run`, so the rehearsal must replace whole steps | high | EXP-002 rec 5b |
| [r4-331-residue.md](r4-331-residue.md) | Third consecutive plan hand-cuts its execute branch under `execute.worktree: false` | high | this plan's Issue 0.7 |
| [r5-amendment-log-undercount.md](r5-amendment-log-undercount.md) | `check_amendment_log`'s success line under-counts `n_impl` | low | measured this plan |
| [r6-apply-preamble-untested.md](r6-apply-preamble-untested.md) | The `--apply` CLI preamble has zero test coverage | high | EXP-002, pass-3 Missing 1 |
| [r7-executor-bookkeeping-unwrapped.md](r7-executor-bookkeeping-unwrapped.md) | The executor's own bookkeeping is outside REQ-LAND-030's wrapper | med | pass-3 C34 |
| [r8-return-shape-fidelity.md](r8-return-shape-fidelity.md) | No RETURN-shape fidelity check exists | high | pass-3 C35 |

## Local beads (filed) and the upstream proposal (NOT filed)

Each draft is filed as a **local bead** — a reversible, non-outward-facing write this session is
authorized to make. The **upstream** `gh issue create` is an outward-facing write and is
**proposed only**; SC16 records the URLs once the operator authorizes it.

| Draft | Local bead | Priority |
| :-- | :-- | --: |
| `r1` | `yf-2atf` | — |
| `r2` | `yf-i127` | — |
| `r3` | `yf-9yb0` | — |
| `r4` | `yf-f7lq` | — |
| `r5` | `yf-6xqf` | — |
| `r6` | `yf-acrn` | — |
| `r7` | `yf-pyqn` | — |
| `r8` | `yf-gdx4` | — |

**Proposed upstream commands** (run only on authorization; per AGENTS.md always `--body-file -`
fed by a quoted heredoc, never `--body '...'`):

```bash
gh issue create --title "L16 launders an unreadable unpushed count into \"0\" — a failed measurement reads as green" \
  --body-file "docs/plans/plan-063-james-dixson-3f74c1/assets/residual-issues/r1-unpushed-laundering.md"    # then: bd update yf-2atf --external-ref <url>
gh issue create --title "L14's bd list is the only close-chain subprocess launched without cwd=ctx.root" \
  --body-file "docs/plans/plan-063-james-dixson-3f74c1/assets/residual-issues/r2-l14-cwd.md"    # then: bd update yf-i127 --external-ref <url>
gh issue create --title "L8-L15 use bare subprocess.run, so the rehearsal must replace whole steps and three of fifteen are never exercised" \
  --body-file "docs/plans/plan-063-james-dixson-3f74c1/assets/residual-issues/r3-l8-l15-injectability.md"    # then: bd update yf-9yb0 --external-ref <url>
gh issue create --title "land is still incompatible with execute.worktree: false — a THIRD consecutive plan hand-cut its execute branch (#331 residue)" \
  --body-file "docs/plans/plan-063-james-dixson-3f74c1/assets/residual-issues/r4-331-residue.md"    # then: bd update yf-f7lq --external-ref <url>
gh issue create --title "check_amendment_log's success line under-counts n_impl" \
  --body-file "docs/plans/plan-063-james-dixson-3f74c1/assets/residual-issues/r5-amendment-log-undercount.md"    # then: bd update yf-6xqf --external-ref <url>
gh issue create --title "the land --apply CLI preamble has ZERO test coverage, including recover()'s four-way branch" \
  --body-file "docs/plans/plan-063-james-dixson-3f74c1/assets/residual-issues/r6-apply-preamble-untested.md"    # then: bd update yf-acrn --external-ref <url>
gh issue create --title "REQ-LAND-030's wrapper covers step dispatch only — the executor's own bookkeeping can still raise a bare traceback" \
  --body-file "docs/plans/plan-063-james-dixson-3f74c1/assets/residual-issues/r7-executor-bookkeeping-unwrapped.md"    # then: bd update yf-pyqn --external-ref <url>
gh issue create --title "no RETURN-shape fidelity check exists — check_mock_fidelity binds the argument axis only" \
  --body-file "docs/plans/plan-063-james-dixson-3f74c1/assets/residual-issues/r8-return-shape-fidelity.md"    # then: bd update yf-gdx4 --external-ref <url>
```

**The `--external-ref` stamp is not optional.** A `gh issue create` that records no
`external_ref` leaves an issue nothing can ever map back to a bead — which is exactly the
condition `upstream.py closable` is blind to, and why the always-loaded upstream rule routes
every upstream write through `/yf-beads-upstream` rather than a hand-run `gh`.
