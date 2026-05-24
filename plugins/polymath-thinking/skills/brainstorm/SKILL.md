---
name: brainstorm
description: Generate divergent ideas (≥ 10) for a problem before converging; quantity beats quality in the divergent phase.
---

# brainstorm

> Divergent-converge brainstorm. Output is a list of distinct ideas, then a short convergence note.

## When to use

- The user says "brainstorm", "what are our options?", "give me some ideas".
- A workflow needs an exploration step before committing to one direction.

## Inputs

- The problem statement (one paragraph max).
- Constraints, if any (time, budget, tech stack).

## Procedure

1. **Diverge** — generate at least 10 distinct ideas. Range across:
   - The default / industry-standard approach.
   - Cheaper, lower-quality alternatives.
   - Higher-investment, higher-payoff alternatives.
   - "Why not do nothing?" (always include).
   - Inversion: "what would make the problem worse?" → invert.
2. Keep each idea to one line. No evaluation yet.
3. **Converge** — pick the top 2 and say why, in two sentences. Note one risk per pick.

## Output

```text
Brainstorm: <problem>

Ideas:
  1. …
  2. …
  …
  10. Do nothing — accept the cost and revisit in a month.
  …

Top 2:
  - <idea X> — chosen because …. Risk: ….
  - <idea Y> — chosen because …. Risk: ….
```

## Anti-patterns to avoid

- Stopping at 3 ideas.
- Converging mid-divergence.
- Generating slight variations of one idea ("X with config A", "X with config B") — those count as one.
