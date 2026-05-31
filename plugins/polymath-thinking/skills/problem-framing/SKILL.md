---
name: problem-framing
description: Frame the problem before any solution — symptom vs root need, who/what/why, constraints, premature-solution bias. A problem statement, not options (brainstorm) or root-cause (5-whys).
---

# problem-framing

> Most bad solutions are answers to badly-framed problems. Pin down what we're actually solving, and for whom, before anyone proposes how.

## When to use

- A request arrives already shaped as a solution ("we need feature X") and you suspect the underlying need is unexamined.
- The start of any non-trivial effort, before brainstorming or planning.
- A workflow invokes `polymath-thinking:problem-framing`.

This *frames* the problem. It is not generating options (`polymath-thinking:brainstorm`), root-causing an incident (`polymath-thinking:5-whys`), or running the full decide loop (`polymath-thinking:deliberate`).

## Procedure

1. **Restate as a problem, not a solution.** If the input is "build X", ask what becomes possible / what pain disappears when X exists — that's the problem.
2. **Who** has it — the specific actor, not "users". **What** they can't do today. **Why** it matters (the cost of leaving it unsolved).
3. **Evidence** — what tells us this problem is real and worth solving (data, quotes, frequency). Mark assumptions vs facts.
4. **Constraints & non-goals** — what any solution must respect; what we're explicitly not solving.
5. **Surface premature-solution bias** — name the solution everyone already has in mind and set it aside so it doesn't constrain framing.
6. **Success signal** — how we'd know the problem is solved, independent of any particular solution.
7. Output a tight problem statement: who/what/why, evidence, constraints, non-goals, success signal — handoff-ready for `brainstorm` or `polymath-product:prd`.

## Quality bar

- The statement describes a problem and need, with zero solution baked in.
- A specific actor is named (not "users" / "the business").
- Evidence is cited and assumptions are flagged separately from facts.
- A solution-independent success signal is stated.
