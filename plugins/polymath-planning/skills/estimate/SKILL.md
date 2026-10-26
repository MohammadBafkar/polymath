---
name: estimate
description: Estimate a work breakdown with a lightweight three-point method (optimistic, expected, pessimistic); surfaces uncertainty rather than a single date.
---

# estimate

> Three-point (PERT-style) estimates per step. The point isn't a date; it's calibrating uncertainty.

## When to use

- A work breakdown exists and stakeholders need a sense of when.
- The user says "how long will this take?".

## Inputs

- A work breakdown (output of `work-breakdown` or any equivalent list).
- Assumed assignee or team (for skill calibration).

## Procedure

1. For each step, ask three questions:
   - **Optimistic** (~10%): everything goes right.
   - **Expected** (~50%): typical run.
   - **Pessimistic** (~90%): known knowns go wrong.
2. Compute per step: mean `μ = (O + 4E + P) / 6` and spread `σ ≈ (P − O) / 2.56` (O and P are 10th/90th percentiles, so classic PERT's `/6` would understate σ).
3. Aggregate: the total mean is the sum of step means along the critical path; the total spread is the root-sum-square `σ_total = √(Σ σ²)`, and the 80% interval is `μ_total ± 1.28 σ_total`. Steps that share a cause of delay (same unknown, same team) are correlated — widen the interval rather than trusting the root-sum-square. **Summing all the O's and all the P's is not a confidence interval**: everything going right (or wrong) at once is far less likely than 10%.
4. Report uncertainty explicitly. If `P / O > 3`, the step is poorly scoped — decompose it further before estimating.

## Output

```text
Estimate: <goal>

Per-step (hours):
  Step                  O    E    P    Mean   σ
  1. …                  2    4    8    4.3    2.3
  2. …                  1    2    8    2.8    2.7   ← P/O > 3, decompose
  …

Critical path mean: <Σμ> h ≈ <calendar days at the team's focus hours/day>
80% interval: <Σμ − 1.28·σ_total> .. <Σμ + 1.28·σ_total> h   (σ_total = √Σσ²; correlated risks widen it)
```

## Quality bar

- Estimates in hours, not story points. Story points hide uncertainty rather than surface it.
- Any step with `P / O > 3` is flagged for decomposition; don't silently commit to it.
- Calendar conversion uses the team's actual focus-hours-per-day (not 8).
