---
name: estimate
description: Apply a lightweight three-point estimate (optimistic, expected, pessimistic) to a work breakdown; surfaces uncertainty rather than a single date.
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
2. Compute the PERT mean per step: `(O + 4E + P) / 6`. Sum the means for the critical path; sum the optimistic and pessimistic to get a range.
3. Report uncertainty explicitly. If `P / O > 3`, the step is poorly scoped — decompose it further before estimating.

## Output

```text
Estimate: <goal>

Per-step (hours):
  Step                  O    E    P    Mean
  1. …                  2    4    8    4.3
  2. …                  1    2    8    2.8   ← P/O > 3, decompose
  …

Critical path mean: <total> h ≈ <calendar days>
Range (90% confidence): <opt sum> .. <pess sum> h
```

## Quality bar

- Estimates in hours, not story points. Story points hide uncertainty rather than surface it.
- Any step with `P / O > 3` is flagged for decomposition; don't silently commit to it.
- Calendar conversion uses the team's actual focus-hours-per-day (not 8).
