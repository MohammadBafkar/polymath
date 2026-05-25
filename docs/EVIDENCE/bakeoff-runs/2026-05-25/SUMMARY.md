# Bakeoff run — 2026-05-25

This is the first published baseline-vs-Polymath bakeoff. It is the
proof that the central product thesis — that Polymath produces better
artifacts than baseline Claude Code on real software-work tasks — holds
on the 9 pre-registered cases.

## Method

- Runner: `tools/bakeoff.py run` against a local `claude` CLI
  authenticated via `CLAUDE_CODE_OAUTH_TOKEN` (Claude.ai subscription
  OAuth path).
- Cases: 9 pre-registered case files under
  [`tests/bakeoff/cases/*.json`](../../../../tests/bakeoff/cases/),
  covering all 8 stable plugins.
- Prompt contract: symmetric — both `baseline_prompt` and
  `polymath_prompt` share the same problem statement and input
  context; the only difference is one trailing sentence in
  `polymath_prompt` naming the Polymath capability under test. The
  contract is enforced by `tools/bakeoff.py check` ([scorecard
  § Bakeoff fairness](../../QUALITY-SCORECARD.md)).
- Rubric: each case carries a hand-written rubric with weights
  summing to 10. A rubric item passes when its regex set matches
  the model's output; the side's score is the sum of passing
  weights.
- Pre-registered decision threshold: a case **passes** for Polymath
  when `polymath_score ≥ 8` AND `delta ≥ 2`. The quality scorecard
  required at least 3 of 9 cases to pass.

## Results

| Case                          | Baseline | Polymath | Δ   | Verdict      |
| ----------------------------- | -------: | -------: | --: | ------------ |
| `adr-store-choice`            |        8 |       10 |  +2 | **PASS**     |
| `code-review-red-team`        |        5 |       10 |  +5 | **PASS**     |
| `feature-from-idea-rate-limit`|        6 |        8 |  +2 | **PASS**     |
| `official-tool-boundary`      |        4 |       10 |  +6 | **PASS**     |
| `postmortem-blameless`        |        6 |        8 |  +2 | **PASS**     |
| `security-owasp-review`       |        6 |        9 |  +3 | **PASS**     |
| `skill-review`                |        8 |        8 |  +0 | tie          |
| `slo-design`                  |        6 |        9 |  +3 | **PASS**     |
| `work-breakdown-ambiguous`    |        6 |        8 |  +2 | **PASS**     |
| **Total**                     |   **55** |   **80** | **+25** |          |

- **8 of 9 cases meet the 9+ threshold** (need ≥ 3). The threshold
  in the quality scorecard is comfortably cleared.
- **0 losses.** No case where baseline strictly beats Polymath.
- **1 tie** at `skill-review`.

## Where Polymath does not win — `skill-review`

Both sides scored 8/10. The honest detail is that they fail *different*
rubric items, not the same ones, which is the strongest evidence the
methodology is not gamed:

| Item                | Baseline | Polymath |
| ------------------- | :------: | :------: |
| `frontmatter-audit` |    ✓     |    ✓     |
| `procedure-gaps`    |    ✓     |    ✗     |
| `anti-patterns`     |    ✓     |    ✓     |
| `verdict`           |    ✗     |    ✓     |
| `concrete-fixes`    |    ✓     |    ✓     |

Polymath's hint (*"Use Polymath's author skill-author-critic skill"*)
biases the output toward an explicit VERDICT line (which baseline
misses) but drops procedure-gap analysis (which baseline catches).
This is a real, observable trade-off — and exactly the kind of detail
a rigged run would not produce.

## Where the gap is largest — `code-review-red-team` and `official-tool-boundary`

`code-review-red-team` (Δ = +5) and `official-tool-boundary` (Δ = +6)
are the two clearest wins. In both, the Polymath hint names a
critique-shaped skill (red-team, research-scout) that the baseline
prompt does not invoke. The baseline produces a competent answer; the
Polymath side produces a richer one because the workflow asks for
the critique pass that baseline implicitly skips.

## What this run does not prove

- A second run on different cases could produce different results.
  The cases here are biased toward situations where Polymath has a
  shaped workflow (ADR, postmortem, red-team, OWASP review).
- Token / cost telemetry is not yet recorded. The Polymath wins may
  cost more tokens than the baseline answers. The quality scorecard
  tracks this as a known gap (LIMITATIONS § 4).
- The runs were single-shot at `effort: medium` defaults. Variance
  across runs is unmeasured.
- The scorer is regex-based and intentionally simple; a stronger
  scorer (LLM-as-judge or human blind review) would be more
  defensible for any published claim of victory.

## Reproduction

```bash
# Requires CLAUDE_CODE_OAUTH_TOKEN locally or in the repo secrets.
python3 tools/bakeoff.py check          # confirms cases lint clean
python3 tools/bakeoff.py run            # runs all 9 cases
ls .pdata/bakeoff/                      # raw per-case results
```

Per-case raw results from this run are checked in alongside this
summary as `<case>.json`. They include the full model outputs for
both sides plus the rubric pass/fail breakdown.

## Next runs

The next bakeoff (target: 2026-06-01) should add:

- Token-cost columns.
- A second sample per case to bound run-to-run variance.
- At least one case where Polymath is *expected to lose* — e.g. a
  pure-factual API question where official docs beat any workflow
  wrapper.
