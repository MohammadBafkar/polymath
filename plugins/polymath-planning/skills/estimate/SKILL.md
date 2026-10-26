---
name: estimate
description: Estimate a work breakdown with a lightweight three-point method (optimistic, expected, pessimistic); surfaces uncertainty rather than a single date.
---

# estimate

> Three-point (PERT-style) estimates per step. The point isn't a date; it's calibrating uncertainty.

**Mode:** deterministic — same inputs, same output. Follow the steps and the output shape exactly; compute with the named script or tool, never by estimate; add nothing the shape does not ask for.

## When to use

- A work breakdown exists and stakeholders need a sense of when.
- The user says "how long will this take?".

## Inputs

- A work breakdown (required) — output of `polymath-planning:work-breakdown` or any list of steps. None given: stop and ask for one (or run `work-breakdown` first); never estimate an undecomposed goal.
- O / E / P hours per step (required) — from the people doing the work. Unattended run (workflow step, subagent): draft them yourself, append `?` to every drafted number, and title the output **DRAFT — numbers not confirmed by the team**.
- Which steps are on the critical path (optional, default: all — sequential).
- Team focus hours per working day (optional, default 5; never assume 8).

## Procedure

1. For each step, collect three numbers in hours:
   - **Optimistic** (~10th percentile): everything goes right.
   - **Expected** (~50th): typical run.
   - **Pessimistic** (~90th): known knowns go wrong.
2. **Compute with the bundled script — never by hand.** It applies per step `μ = (O + 4E + P) / 6` and `σ = (P − O) / 2.56` (O and P are 10th/90th percentiles, so classic PERT's `/6` would understate σ), sums the critical-path means, root-sum-squares the critical-path σ, and reports the 80% interval `μ ± 1.28 σ_total`:

   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/estimate/scripts/pert.py" \
     --goal "<goal>" --focus-hours 5 <<'CSV'
   step,o,e,p,critical
   Write the migration,2,4,8,y
   Add the limiter middleware,1,2,8,y
   Update the runbook,1,1,2,n
   CSV
   ```

   Exit 2 means bad input (e.g. O > E): fix the row, never the arithmetic.
3. Paste the script output verbatim. Do not re-round, re-order, or "correct" it.
4. Act on its flags: any step with `P / O > 3` is poorly scoped — decompose it and re-run before anyone commits to the total. Steps that share a cause of delay (same unknown, same team) are correlated: say so, because the interval assumes independence and is too narrow for them. **Summing all the O's and all the P's is not a confidence interval.**
5. Write the result to `docs/plans/<slug>-estimate.md` when a plan exists for it (same slug as the plan); otherwise return it inline.

## Output

The script's block, verbatim, then one line of correlation notes:

```text
Estimate: Rate-limit /login

Per-step (hours):
  Step                               O     E     P    Mean      σ
  1. Write the migration             2     4     8     4.3    2.3   ← P/O > 3, decompose
  2. Add the limiter middleware      1     2     8     2.8    2.7   ← P/O > 3, decompose
  3. Update the runbook              1     1     2     1.2    0.4   ← off critical path

Critical path mean: 7.2 h ≈ 1.4 working days at 5 focus h/day
80% interval: 2.6 .. 11.8 h  (0.5 .. 2.4 days; σ_total = 3.6 h, independent steps — correlated risks widen it)
Decompose before committing: Write the migration, Add the limiter middleware

Correlated risks: steps 1–2 share the unknown "does the gateway expose client IP?" — treat 11.8 h as optimistic.
```

## Quality bar

- Every number in the output came from the script; none was computed or adjusted in prose.
- Estimates in hours, not story points. Story points hide uncertainty rather than surface it.
- Any step with `P / O > 3` is flagged for decomposition; don't silently commit to it.
- Calendar conversion uses the team's actual focus hours per day (not 8).
- Drafted (unconfirmed) numbers carry `?` and the DRAFT title — never presented as the team's estimate.
