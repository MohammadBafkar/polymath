# Quality dashboard

How the catalog's quality signals get measured and where the artifacts
land.

## What gets measured

| Surface                          | Source                                                              | Cadence                                  |
| -------------------------------- | ------------------------------------------------------------------- | ---------------------------------------- |
| Conformance pass rate per plugin | [`tools/conformance.sh --all`](../tools/conformance.sh)             | every PR (golden-tests.yml)              |
| Skill-triggering pass rate       | [`tools/skill-triggering.py run`](../tools/skill-triggering.py)     | scheduled + `/evaluate` (evaluation.yml) |
| Bakeoff regex deltas             | [`tools/bakeoff.py run`](../tools/bakeoff.py)                       | scheduled + `/evaluate` (evaluation.yml) |
| Bakeoff LLM-judge deltas         | [`tools/bakeoff.py run --judge`](../tools/bakeoff.py)               | manual / `/evaluate` with judge flag     |
| Judge calibration drift          | [`tools/bakeoff.py calibrate`](../tools/bakeoff.py)                 | nightly (when `include_judge=true`)      |
| Token budget                     | [`tools/token-budget.sh`](../tools/token-budget.sh)                 | every PR (token-budget.yml)              |

## Where artifacts land

Per-run JSON reports under `.pdata/bakeoff/<case-id>.json`:

```json
{
  "case": "...",
  "title": "...",
  "baseline_score": 6,
  "polymath_score": 9,
  "delta": 3,
  "threshold": { "minimum_polymath_score": 8, "minimum_delta": 2 },
  "results": {
    "baseline": { "score": 6, "rubric": [...], "output": "..." },
    "polymath": { "score": 9, "rubric": [...], "output": "..." }
  },
  "judge": {
    "baseline_score": 7,
    "polymath_score": 9,
    "delta": 2
  }
}
```

The `evaluation.yml` workflow uploads the `.pdata/bakeoff/` tree as a
GitHub Actions artifact (`evaluation-<run_id>`, 30-day retention).

## Promotion criteria (stable readiness)

A plugin reaches `stable` when it has:

1. **A passing bakeoff scenario** — at least one bakeoff case scoring
   ≥ 8 with delta ≥ 2 over baseline. Both the regex and judge scorers
   must agree when `--judge` is enabled. URL recorded in the ledger as
   `live_bakeoff_run`.
2. **A passing skill-triggering test** — at least one skill-triggering
   test exercising three trigger phrasings. URL recorded as
   `live_trigger_run`.
3. **Conformance OK** at the head of `main`.
4. **At least one external user** — a real adopter beyond the
   maintainer. Surfaced via a tracked issue, fork, or PR citing the
   plugin's files. URL recorded as `external_user_url`.
5. **Connector / infra plugins additionally need distinct-value proof.**
   Primary-source evidence (bakeoff case, side-by-side artifact, or
   documented workflow-shape gap) that Polymath adds workflow,
   critique, safety, or artifact value beyond the official MCP / CLI /
   LSP / docs surface. URL recorded as `distinct_value_url`. Per
   [docs/INTEGRATION-POLICY.md](INTEGRATION-POLICY.md), connector/infra
   plugins are now **eligible for `stable` only after distinct-value
   proof plus the normal stable gates** — they no longer "stay
   experimental" by policy.
6. **A CHANGELOG entry** records the promotion. URL recorded as
   `promotion_pr`, anchor as `changelog_entry`.

All six receipts are stored per plugin in
[`registry/stability-evidence.json`](../registry/stability-evidence.json)
and enforced by
[`tools/check-stability-evidence.py`](../tools/check-stability-evidence.py)
(rule `STABILITY-1`). The human-facing view of the ledger is
[`docs/STABILITY-ROADMAP.md`](STABILITY-ROADMAP.md).

The first three rows are CI-mechanical; rows 4–6 are asserted by hand
when the evidence is published.

## How `/evaluate` works

In a PR comment, type `/evaluate`. The workflow at
[`.github/workflows/evaluation.yml`](../.github/workflows/evaluation.yml.disabled)
triggers a live bakeoff + skill-triggering run, uploads the JSON
reports as an artifact, and posts a summary table back as a PR
comment.

> **Note:** this workflow is currently **disabled** (renamed to
> `evaluation.yml.disabled`) to avoid Claude API cost. `/evaluate` will
> not trigger until it is renamed back to `evaluation.yml`.

The job opts in to the LLM judge when the workflow's `include_judge`
input is `true` (manual dispatch) — the regex scorer runs by default.

## Manually inspecting a run

```bash
# Re-run any case locally (requires CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY).
python3 tools/bakeoff.py run <case-id> --out-dir .pdata/bakeoff
# With the LLM judge as well:
python3 tools/bakeoff.py run <case-id> --judge --out-dir .pdata/bakeoff

# Calibrate the judge against frozen human-blind gold scores.
python3 tools/bakeoff.py calibrate

# List skill-triggering tests + their expected invocations.
python3 tools/skill-triggering.py list

# Run skill-triggering tests live (requires Claude CLI).
python3 tools/skill-triggering.py run --timeout 180
```
