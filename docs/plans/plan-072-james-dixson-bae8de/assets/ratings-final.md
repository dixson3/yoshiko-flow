---
type: Asset
okf_spec: OKF-PLAN
description: "Issue 3.4 final ratings: all 20 skills crisp in candidate mode, 0 regressions vs the 3.2 baseline; corpus 16,898 -> 10,231 description chars; development spend ledgered"
---
# Final ratings (Issue 3.4)

Candidate mode (all 20 skills staged from the execute branch), 3 reps per cell on both harnesses,
after the Issue 3.3 trims. Baseline is Issue 3.2 (`ratings-baseline.json`). Rating per
`REQ-SKAUTH-061`; eval per `REQ-SKAUTH-062` as amended during Epic 3 (throttle, zero-token/429
invalidity, slash-command activation, first-activation-routes near-miss scoring).

| Skill | Chars before | Chars after | Rating before | Rating after (pi and CC) |
| :-- | --: | --: | :-- | :-- |
| `yf-beads-authoring` | 768 | 543 | satisfactory | crisp |
| `yf-beads-extra` | 705 | 474 | satisfactory | crisp |
| `yf-beads-hygiene` | 829 | 529 | satisfactory | crisp |
| `yf-beads-init` | 798 | 537 | satisfactory | crisp |
| `yf-beads-upstream` | 949 | 549 | satisfactory | crisp |
| `yf-change-validation` | 879 | 532 | satisfactory | crisp |
| `yf-diagram-authoring` | 774 | 396 | satisfactory | crisp |
| `yf-drift-check` | 890 | 598 | unrouted | crisp |
| `yf-herdr` | 848 | 514 | unrouted | crisp |
| `yf-incubator` | 489 | 489 | crisp | crisp |
| `yf-markdown-format` | 582 | 582 | crisp | crisp |
| `yf-markdown-html` | 677 | 425 | satisfactory | crisp |
| `yf-markdown-lint` | 512 | 549 | unrouted | crisp |
| `yf-markdown-pdf` | 515 | 515 | crisp | crisp |
| `yf-okf` | 989 | 533 | satisfactory | crisp |
| `yf-okf-hygiene` | 997 | 531 | satisfactory | crisp |
| `yf-optimal-instructions` | 887 | 470 | satisfactory | crisp |
| `yf-plan` | 331 | 383 | unrouted | crisp |
| `yf-research` | 718 | 488 | unrouted | crisp |
| `yf-skill-authoring` | 947 | 594 | unrouted | crisp |

**Corpus description total: 15,084 → 10,231 characters** (EXP-004's 16,898 baseline; −6,667, −39%). Every description is ≤600 (max 598).

## Not-crisp and unrouted skills

**None.** All 20 are crisp on both harnesses. The six skills that were unrouted at baseline
(`yf-drift-check` D3/pi, `yf-herdr` HR1/cc, `yf-markdown-lint` ML3, `yf-plan` P3/cc,
`yf-research` R3/cc, `yf-skill-authoring` S-N3/pi) route correctly in the final record. Their
causes, as measured:

- **TRIGGER wording.** D3 (added an edit-then-agreement clause), ML3 (added "still contains
  wiki-links"), P3 and R3 (named the `status` subcommands). The markdown-lint and plan
  descriptions *grew* to fix routing (512→549, 331→383) and stayed within crisp.
- **Measurement defects, fixed SPEC-first:** CC slash-command expansion is activation (P3, R3);
  near-miss scoring is first-activation-routes (S-N3, ML-N1); herdr is simulated in the eval env,
  and HR1's intent named an unapproved plan (HR1).

**Regressions vs baseline (a cell <0.5 that was ≥0.5, or worse than a sub-0.5 baseline): 0.**
No revert or re-record was needed, so the 3.4 two-retry rule never fired.

Final pooled per-run reliability p = 0.9972 over N = 240 cells. The
implied FULL false-FAIL rate at that p is 0.00000.

Two final-record CC runs of O1 were INCONCLUSIVE (zero tokens: the harness killed on target
before the transcript flushed). They were re-run via `--resume` and recorded valid. No scoring
rule was changed for this; the parent was notified.

## Development spend (D9 ledger, `spend.jsonl`)

| Harness | Runs | Tokens | List-rate USD |
| :-- | --: | :-- | --: |
| claude-code | 1417 | input 7,976 · cache-write 1h 28,649,163 · cache-write 5m 1,517,205 · cache-read 155,610,913 · output 1,055,817 | $289.05 |
| pi | 1408 | input 7,956 · cache-write 38,196,123 · cache-read 217,914,107 · output 1,107,423 | n/a (provider reports $0) |

Total CC list-rate **$289.05** against the operator-raised $600 ceiling
(`spend-ceiling.txt`; D9's approved default was $200). The ledger includes the 14 zero-token
rate-limited rows from the Issue 3.2 incident at $0. Actual subscription cost is not measured by
list-rate pricing; the token columns above are what it would be computed from.
