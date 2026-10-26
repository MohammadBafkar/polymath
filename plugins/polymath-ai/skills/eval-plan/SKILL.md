---
name: eval-plan
description: Design an evaluation for an LLM feature — task type, dataset shape, automated vs human rubric, regression set, decision threshold.
---

# eval-plan

> Pin down what "good" means before you ship. Output is an eval plan that tells you when to release and when to hold.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A new LLM feature is being built.
- A prompt change is being proposed and you need to know if it's an improvement.
- A model upgrade (between Anthropic versions, or across vendors) is on the table.

Not this when: you are designing the agent or prompt itself (`polymath-ai:agent-design`, `polymath-ai:prompt-engineer`) or a product A/B test on users (`polymath-data:run-experiment`). This skill builds the offline/online eval that judges them.

## Inputs

- The feature in English.
- Decision the eval must support: ship vs. hold? canary vs. rollout? regression vs. improvement?

## Procedure

1. **Classify the task**:
   - **Reference task** — there is a right answer. Use exact match / F1 / a programmatic checker (unit test, schema validation, execution result).
   - **Reference-free** — no single right answer. Use rubric scoring (human or LLM-as-judge).
   - **Pairwise** — A is better than B. Use win-rate.
   - **Agentic** — multi-step tool use. Score the outcome (task achieved, verified in the end state) *and* the trajectory (right tools, valid args, no unsafe or wasted steps, within step/cost budget).
2. **Build a dataset** with three slices:
   - **Smoke**: ~20 examples, fast feedback during development.
   - **Regression**: ~100–300 examples covering known-good behaviors. Failure on regression blocks ship.
   - **Frontier**: ~50 hard cases that probably aren't solved yet; tracks ceiling.
   Keep a **held-out** portion you never look at while iterating on the prompt — tuning against the whole set overfits it, and the score stops predicting production.
3. **Rubric**:
   - **Reference-free**: define 3–5 dimensions (e.g. correctness, completeness, format adherence, harmlessness). Each on a Likert scale or pass/fail. **Independent dimensions only** — overlapping rubrics hide failure modes.
   - **LLM-as-judge**: pin the judge model and the rubric prompt. Validate that the judge agrees with humans on a calibration set; re-validate when the judge changes. Control the known judge biases: randomize A/B position (and score both orders), don't reward length, and don't let a model grade its own outputs without a human-calibrated check.
4. **Account for nondeterminism**:
   - Measure the noise floor first: run the *unchanged* baseline twice; a delta smaller than that gap is noise.
   - Run each example k times (e.g. k = 3–5), or at temperature 0 where the provider honors it, and define pass as "passes ≥ m of k". A single stochastic run of a "100% must pass" slice will flake.
5. **Decision threshold**:
   - "Ship if regression slice passes 100% (≥ 4 of 5 runs per example) AND smoke ≥ 85% AND no critical-severity miss." Pick numbers; document them; defend them.
   - For pairwise: ship when the 95% confidence interval of the win-rate (ties excluded, reported separately) is above 0.5 — e.g. ≥ 114 wins out of 200 decisive comparisons (57%). A raw 55% at N = 200 is not distinguishable from a coin flip. Compute the verdict with the bundled script, never by eye:
     `python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/eval-plan/scripts/winrate.py" --wins 114 --losses 86 --ties 23`
6. **Failure-mode tracking** — every wrong example is tagged with a root cause category. Patterns inform the next prompt iteration.

## Output

```text
Eval plan: <feature>

Task type: reference-free with LLM-as-judge.

Dataset:
  smoke      — 20 examples (curated by hand; updated weekly).
  regression — 200 examples (drawn from prior bugs + golden behaviors);
               40 held out, never used while iterating.
  frontier   — 50 examples (hard / ambiguous / under-specified).

Noise floor: baseline vs baseline re-run = 2.1 pts on smoke → deltas < 3 pts are noise.
Runs: k = 5 per example; pass = ≥ 4 of 5.

Rubric (LLM judge):
  - correctness:     pass / fail
  - completeness:    pass / fail
  - format:          pass / fail (refusal also counts as fail)
  - harmlessness:    pass / fail
  Independent axes; majority-pass is not an aggregate score.
  Judge: pinned model + prompt; position randomized; calibrated vs humans.

Decision thresholds:
  Ship      — regression 100% (≥ 4/5 runs) on correctness AND format; smoke
              ≥ 85% on all four axes; no harmlessness fail anywhere.
  Hold      — anything else.
  Canary    — ship at 10% for 48h with thresholds in dashboards.

Failure-mode taxonomy:
  R1 wrong retrieval, R2 right retrieval / wrong synthesis,
  R3 hallucination, R4 format violation, R5 over-refusal.

Re-validation cadence:
  Judge prompt or model change → re-run human-vs-judge agreement on
  a 50-example calibration set; agreement must stay ≥ 0.8 Cohen's κ.
```

## Anti-patterns to avoid

- A single "quality score" that hides which axis is regressing.
- LLM-as-judge with no human calibration, or with a fixed A/B position.
- Eval data drawn only from production happy paths (you'll never see the frontier).
- Declaring a win on a delta smaller than the run-to-run noise floor.
- Iterating the prompt against the same examples you report on.
- Moving the threshold to make a release fit.
