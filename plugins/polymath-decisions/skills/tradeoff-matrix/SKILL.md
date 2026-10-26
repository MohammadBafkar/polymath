---
name: tradeoff-matrix
description: Score options against weighted criteria; surfaces where the numeric ranking disagrees with the gut call and names the tie-breaker.
---

# tradeoff-matrix

> Pin a decision's criteria + weights + scores. Output is a matrix and an honest discussion of what's not captured by the numbers.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Two or more reasonable options for a decision.
- The team is going in circles because everyone weights criteria differently.
- A workflow's decision-support step needs a structured comparison.

## Inputs

- The question being decided (one sentence).
- The candidate options.
- Optional: candidate criteria + weights from the caller. Weights are the decision-owner's priorities: when they are absent and nobody can answer (unattended run), propose them, label the weight column `proposed`, and say so in the summary.
- Scores come from evidence in the inputs; a score you had to guess carries `?` (`4?`).

## Procedure

1. Read [`Tradeoff-matrix.md`](../../templates/Tradeoff-matrix.md).
2. **Slug** from the question: a workflow's `${workflow.slug}` wins; otherwise lowercase it, replace each run of characters outside `a-z0-9` with `-`, trim `-` at the ends, and cut to ≤ 60 characters at a `-`. An existing file at the target path is updated in place (show the diff), never duplicated.
3. Pick **criteria** — 3–6 that genuinely differentiate, each with a weight (1–5) and a one-line rationale — and **score** each option 1–5 per criterion.
4. **Compute with the bundled script — never by hand.** It prints the per-cell math (`w × s = v`), totals, ranking, non-differentiating criteria, and the full sensitivity sweep (every weight ±1 and every score ±1):

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/tradeoff-matrix/scripts/weigh.py" <<'CSV'
   criterion,weight,A. In-memory,B. Redis,C. Postgres
   Latency (P99),5,5,5,3
   Operational burden,4,5,3,4
   CSV
   ```

   Re-cut or drop any criterion it lists as non-differentiating, then re-run.
5. Draft `docs/decisions/<slug>-tradeoff.md` from the template, pasting the script's table, ranking, and sensitivity lines verbatim:
   - **Criteria** — table of criterion, weight, rationale.
   - **Options × criteria** — the script's table.
   - **Sensitivity check** — the script's lines. Every criterion it says the decision hinges on needs evidence, not opinion; a flip on a GUESSED score means the decision is not ready.
   - **Discussion** — where the numeric ranking disagrees with the gut call, name the tie-breaker explicitly. Often the "missing criterion" is named here.
   - **Recommendation** — the option that wins after discussion (which may not be the highest scorer).
   - **What would change the answer** — name the future condition that would flip the choice.

## Quality bar

- Criteria differentiate the options. Re-cut any criterion that every option scores the same on.
- Weights have a one-line rationale.
- Math is shown per cell and every total and sensitivity line came from the script; no "Option B: 7/10" hand-waves.
- If the recommendation contradicts the numeric ranking, the tie-breaker is named explicitly.
- The sensitivity check is stated: either "no single ±1 change flips the winner" or the criterion the decision hinges on.

## Output

- File: `docs/decisions/<slug>-tradeoff.md`.
- One-line summary listing the chosen option + the tie-breaker (if any).

## Anti-patterns to avoid

- Choosing criteria to make a preferred option win ("retrofitting").
- Anything scored 5 across all options.
- Hidden weights inside a single "fit" score.
- Recommendation that picks the lowest-scoring option without explaining why.
