---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 1, reading] REVISE: the FULL row tests the OLD installed descriptions (runs at L3, pre-redeploy); as specified FULL almost never passes (~0.17 at 95% per-run reliability); a skill at <=1024 that misses an intent has no rating; 14 concerns, 4 high"
plan: plan-072-james-dixson-bae8de
pass: 1
mode: reading
---
# Plan Red-Team: plan-072-james-dixson-bae8de

## Verdict: REVISE
**Mode:** reading

## Strengths
- SPEC-first ordering is concrete. Issue 0.1 cuts the execute branch before any SPEC commit, and SC1b tests the ordering from git ancestry instead of trusting the order of the epic list.
- EXP-005 caught the most dangerous silent failure: Claude Code (CC) shadows a project skill copy with the user-scope install, so a trim could be "verified" against the text it replaces. The plan turns that into a required verification step (R2, Issue 2.1).
- The D3 cost is stated up front, the operator's acceptance is recorded, and "INCONCLUSIVE, never PASS" is written into REQ-SKAUTH-062.
- The trigger threshold (≥0.5 over ≥3 reps) comes from measured run-to-run noise (cc O1 went 2/3), not from a guess.
- The EXP-003 scoring in `~/.cache/plan072-eval/rescore.py` reproduces `assets/exp-003/rescored.txt` byte for byte (CC 59/63, pi 57/63).
- The plan checkers pass: doc_lint, plan_extract `--strict`, gate_consistency and audit all exit 0.
- A nested `claude -p` run from inside an agent session works (exit 0), so the capability-gate probe and the FULL row are not blocked by nesting.

## Concerns
| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | measured: `cmp ~/.claude/skills/yf-okf/SKILL.md skills/yf-okf/SKILL.md` → exit 1 (installed copy carries yf stamp lines); `plan_manager.py _validate_merged` runs `change_validation.py run --tier full` at land L3, before redeploy | **The FULL-tier row does not test the branch.** Issue 2.4 wires the row as `--mode installed`, and installed mode reads the deployed skills in `~/.claude/skills` and `~/.agents/skills`, not the checkout. FULL runs at L3, on the merged tree, **before** the redeploy (AGENTS.md: redeploy is the last step). So every landing, including this plan's own, evaluates the **old installed descriptions**. A trim that breaks routing passes FULL and then ships. This breaks CHANGE-VALIDATION §1 ("A RECIPE ROW MUST BE SATISFIABLE FROM THE BRANCH UNDER TEST"), and it is the same failure R2 exists to prevent. R4 also contradicts itself: it says the row "runs installed mode after deploy (Issue 5.3)", but SC12 and 2.4 run it at L3. | Make the recipe row `--mode candidate`, staging from the checkout under test. Use installed mode only for the post-deploy check (5.3, SC10). Correct R4. |
| C2 | high | measured: `python3 rescore.py` → exit 0, rows `D3 … pi 0/3`, `O1 … pi 0/3`, `O2 … cc 0/3`; binomial computation from the same data | **As specified, the FULL gate will almost always fail.** A cell passes at ≥2/3. Across 20 skills × ~6 intents × 2 harnesses (240 cells), even 95% per-run reliability gives P(all cells pass) ≈ 0.17; at 90% it is ≈ 0.001. The baseline already has three cells at 0/3. Every future plan's landing would fail FULL most of the time, and each retry costs about 2.4 h and $55–90+. That makes D3 impractical to run, which is a defect in how the plan implements D3, not a challenge to D3 itself. | Define the FULL row's verdict against the **recorded rating** in `triggers.json`, for example "no intent regresses from its recorded rate by more than a stated margin". Or re-run only failing cells before declaring FAIL. State the expected false-FAIL rate in REQ-SKAUTH-062. |
| C3 | high | measured: same rescore output shows yf-drift-check (pi D3 0/3) and yf-optimal-instructions (pi O1 0/3, cc O2 0/3) failing an intent at ≤1024 chars | **The rating scheme has a state with no name.** D1 defines crisp (≤600 + all intents), satisfactory (≤1024 + all intents) and loose (>1024). A skill that is ≤1024 but misses an intent is none of the three, and two skills are in that state today. SC7 (`--max-rating satisfactory`) and D6 (decline → "accepted as satisfactory") have nothing to say about it. D6 lets the operator relabel such a skill satisfactory, which contradicts D1's definition. | Add a fourth state (e.g. "unrouted" / fails-fidelity) to REQ-SKAUTH-061. Say whether an operator decision can accept it, and how SC7, SC8 and the FULL row treat it. |
| C4 | high | measured: `test -d docs/plans/plan-072-james-dixson-bae8de/assets/exp-003/raw` → exit 1; bundled `rescore.py` → `TOTAL cc: 0/0`; raw streams exist only in `~/.cache/plan072-eval/raw` (127 files, 30 MB) | **SC4 / Issue 2.2 cannot be met as written.** The detector tests "must reproduce `assets/exp-003/rescored.txt` exactly", but the raw streams they would read are not in the bundle or the repo. A shipped test under `scripts/checks/` also cannot depend on `~/.cache` or on a primary-side plan-folder path (CHANGE-VALIDATION §1). | In Issue 2.2, commit a trimmed fixture set (tool-call events only, with the ≤6-call cutoff applied) under `scripts/checks/fixtures/`, and assert the per-intent totals rather than comparing a text file. |
| C5 | medium-high | measured: `MD.findall('/x/clone-pi/skills/yf-okf/SKILL.md')` → `[]`; `…/.claude/skills/yf-okf/SKILL.md` → `['yf-okf']` | **The pi candidate mode may not see activations at all.** The detector only credits `.agents` or `.claude/skills/<n>/` paths, and it deliberately ignores the repo's own `skills/<n>/`. pi candidate mode is `--no-skills --skill <dir>`. If `<dir>` is the clone's `skills/<n>`, which is the natural choice, every pi activation is invisible: trigger intents all fail and near-misses all pass. The plan does not say where pi candidates are staged. | In REQ-SKAUTH-062, make the candidate staging root an explicit detector input. Stage pi candidates under a path the detector recognizes. Add a 2.2 test: a pi stream reading the staged SKILL.md counts as an activation. |
| C6 | medium-high | measured: one live call (clone-cc, candidate `.claude/skills/{yf-okf,yf-okf-hygiene}` + `--setting-sources project`, intent K1) → exit 0, init `permissionMode: default`, tool 1 `Skill yf-okf` returned error "Execute skill: yf-okf", `yf skill-dir` Bash call needed approval, 18 turns, $0.73 | **EXP-005 implication 4 does not hold.** `--setting-sources project` drops the user `bypassPermissions` setting, and in `-p` mode the **Skill tool itself is denied**. Detection still works because the `tool_use` event is emitted. But the `yf skill-dir` path, 11 of the 50 CC passes in EXP-001, is blocked. Near-miss runs also run into permission walls. So candidate mode does not measure the same behaviour as installed mode. | In candidate mode, pass `--permission-mode bypassPermissions` (or an explicit `--allowedTools`). Have the harness read `permissionMode` from the init event and return INCONCLUSIVE if it is unexpected. |
| C7 | medium-high | measured: `grep -n capture_output change_validation.py` (line ~785 `capture_output=True`); spike `run_command({'cmd':"sh -c 'exit 4'"})` → status `fail`, returncode 4 | **INCONCLUSIVE and progress output are both lost at tier level.** The engine treats any non-zero exit as `fail`, so the eval's exit 4 shows up as FAIL, not INCONCLUSIVE. The engine also stops at the first failure, which skips every later row. That contradicts R5's "matching `change_validation.py`'s fail-closed contract". The engine also captures output until the row finishes, so R1's "progress output" never reaches the operator during the 2.4 h row. | Either amend yf-change-validation (SPEC-first, in that skill) to map exit 4 to inconclusive and stream output, or restate R1/R5 honestly. Put the eval row **last** in the FULL list and give it an explicit `timeout`. |
| C8 | medium | measured: `run-cc.jsonl` near-miss mean 42.5 s (n=9) vs trigger 20.4 s; completed-run costs $0.05–0.41; the live candidate call cost $0.73 | **The cost figure the operator re-confirmed D3 on is about 30% low.** The 23.6 s/run mean comes from a set that was 14% near-misses. D3's intent sets are about 50% near-misses, which gives ≈31 s/run, ≈3.1 h CC wall, and higher cost. Epic 3 (the 3.1 baseline plus a candidate re-rate for every trim attempt across 20 skills) has no budget at all. | Re-project with the 50% mix and state the number in D3/R1. Budget Epic 3 (runs per trim attempt × attempts), or scope each re-rate to the edited skill plus its named siblings. |
| C9 | medium | measured: `uv run scripts/check_frontmatter.py` → exit 0 today | **SC2 already passes before any work (#384).** It cannot tell a finished Issue 1.1 from an untouched tree. | Add a clause that the tagged rule exists, e.g. `grep -q REQ-YF-EMBED-007 scripts/check_frontmatter.py`, or rely on SC3's negative controls and say so. |
| C10 | medium | inferred: DAG 1.1←0.3 but 3.2←1.1,3.1←2.1,2.3; `frontmatter` FAST row is scoped by the `scripts/check_frontmatter.py` glob | **The tree is red for most of the plan.** R6 says 1.1 lands in the same change-set as the five trims, but the DAG lets 1.1 close long before 3.2, which waits on the whole eval harness and baseline. The FAST `frontmatter` row stays red through Epic 2. | Make 1.1 and the ≤1024 trims one bead (trim to the cap first, rate afterwards), or make 1.1 depend on 3.2. R6 also says "SC3" where it means SC2. |
| C11 | medium | measured: CC init event keys include `skills` (names only); `'Constructs, manages' in json.dumps(init)` → False. pi `message_start` does carry the description text | **R2's verification has no mechanism on CC.** pi can hash the description out of its own stream, but CC's stream exposes only skill names. The plan's alternative, "a tools-off quote", is an extra paid run and a model quote, not a hash. | In REQ-SKAUTH-062, specify the CC check: e.g. init `skills` ⊆ staged set + staged-file sha256 + `--setting-sources project` asserted. Keep the tools-off quote as a sampled check, not the per-run one. |
| C12 | low-medium | measured: after `cp -R` of candidates into `clone-cc/.claude/skills/`, `git status --porcelain` printed nothing (repo `.claude/.gitignore` is `*`) | **Staged candidates survive the reset.** The runner's reset (`git clean -fdq`, no `-x`) leaves ignored `.claude/skills/` in place, so a previous candidate set carries into the next run. | Clear the staging directory explicitly at each reset, and include it in the verification. |
| C13 | low-medium | inferred: D4 stores "last measured result" in `triggers.json` | **Nothing says whether the FULL row writes `triggers.json`.** If it does, validate-merged dirties the merged tree between merge and push. If it does not, nothing keeps the stored rating fresh. | State it: the FULL row is read-only, and only an explicit `--record` run in a plan writes. |
| C14 | low | measured: descriptions have len == UTF-16 length for all 20 (uv/pyyaml scan) | pi measures JS string length (UTF-16 units), Python measures code points. They agree today, but would diverge on astral characters. | Pin the unit in REQ-YF-EMBED-007. |

## Measurements
| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| doc_lint | `uv run $SKILL_DIR/scripts/doc_lint.py --path …/plan.md --json` | 0 | PASS, 0 findings |
| plan_extract | `uv run $SKILL_DIR/scripts/plan_extract.py … --json --strict` | 0 | 6 epics, 22 issues, 0 unparsed |
| gate_consistency | `uv run $SKILL_DIR/scripts/gate_consistency.py … --json` | 0 | PASS |
| audit | `plan_manager.py audit … --json-output` | 0 | |
| rescore reproduce | `python3 ~/.cache/plan072-eval/rescore.py \| diff - assets/exp-003/rescored.txt` | 0 | identical |
| bundled rescore | `python3 assets/exp-003/rescore.py` | 0 | `0/0`: no raw/ in bundle (C4) |
| SC2 pre-work | `uv run scripts/check_frontmatter.py` | 0 | green before work (C9) |
| SC1/3/4/6/11 pre-work | per Verification cell | 1/2/2/1/1 | not-yet-dischargeable, as expected |
| engine exit-4 mapping | spike importing `change_validation.run_command` in mktemp | 0 | `exit 4` → `fail` (C7) |
| nested CC | `CLAUDECODE=1 claude -p "Reply ok."` | 0 | nesting works |
| CC candidate live | `claude -p <K1> --setting-sources project --output-format stream-json --verbose` in clone-cc | 0 | permissionMode default; Skill denied; $0.73 (C6). Staging removed, clone clean |

## Missing
- A verdict rule for the FULL row that tolerates a known-noisy per-cell measurement (C2), and a named state for "≤1024 but fails fidelity" (C3).
- A spend estimate for Epic 3's iterative trim-and-re-rate loop (C8).
- Whether the FULL row writes `triggers.json` (C13).
- An explicit `timeout` column value for the eval recipe row, and its position in the list (last).
- EXP-003's recommendation to "re-run D3/O1/O2 on pi with only the description wording changed" before trimming was not carried into Epic 3. That check is the evidence that wording, not the rules aggregate, is the right lever.

## Gate Assessment
- **Capability gate (harness auth):** the probe works (a nested `claude -p` measured exit 0). It is frontloaded correctly, and it blocks 3.1 and 2.4, which transitively covers the rest of the live work.
- **Split-decisions gate:** mid-DAG, and legitimately so, because it depends on what Epic 3 measures. Its instructions need a branch for the unnamed rating state (C3).
- **Upstream-writes gate:** a class-level consent, frontloaded with the Start Gate. Sound.
- **No gate on live spend.** D3 covers what the FULL tier costs, not what Epic 3's development runs cost. Consider folding a stated spend ceiling into the Start Gate's instructions (C8).

## Upstream Assessment
- **#407 include:** correct. Issues 0.3, 1.1 and 3.2 resolve it, and the Resolved By column matches.
- **#302 exclude with an evidence comment (5.5):** reasonable. The comment is covered by the upstream-writes gate.
- **#189 exclude:** justified. The plan adds tests only for its own new rules.
- **Follow-on for the rules-aggregate asymmetry (5.4):** correctly kept out of scope, since fixing it would change what the evals measure.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | | | unresolved |
| C2 | high | | | unresolved |
| C3 | high | | | unresolved |
| C4 | high | | | unresolved |
| C5 | medium-high | | | unresolved |
| C6 | medium-high | | | unresolved |
| C7 | medium-high | | | unresolved |
| C8 | medium | | | unresolved |
| C9 | medium | | | unresolved |
| C10 | medium | | | unresolved |
| C11 | medium | | | unresolved |
| C12 | low-medium | | | unresolved |
| C13 | low-medium | | | unresolved |
| C14 | low | | | unresolved |
