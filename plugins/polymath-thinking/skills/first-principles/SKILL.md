---
name: first-principles
description: Reason from first principles — strip to fundamentals, drop inherited assumptions, rebuild from bedrock. Decompose-to-fundamentals, not option generation (brainstorm) or framing (problem-framing).
---

# first-principles

> Stop reasoning by analogy ("everyone does it this way"). Strip the problem to what must be true, then rebuild — that's where the non-obvious answer lives.

## When to use

- A constraint or cost is treated as fixed "because that's how it's done" and you suspect it's inherited, not fundamental.
- A 10x (not 10%) rethink is wanted; conventional approaches have plateaued.
- A workflow invokes `polymath-thinking:first-principles`.

This *decomposes to fundamentals*. It is not generating many options (`polymath-thinking:brainstorm`), framing the problem (`polymath-thinking:problem-framing`), or incident root-cause (`polymath-thinking:5-whys`).

## Procedure

1. **State the conventional approach** and the assumptions it rests on — list them explicitly.
2. **Test each assumption**: is it a law (physics, math, economics, regulation) or a convention/analogy someone could change? Tag every assumption.
3. **Keep only the bedrock** — the constraints that are genuinely fundamental. Discard the conventions.
4. **Rebuild** a solution from the bedrock up, ignoring how it's "normally" done.
5. **Quantify** where you can — fundamentals are often numeric (material cost, latency floor, unit economics); a first-principles argument with numbers beats one with adjectives.
6. **Compare** the rebuilt approach to the conventional one; name what the convention was costing.
7. Output: the assumption ledger (fundamental vs convention), the bedrock, and the rebuilt approach with its quantified advantage.

## Quality bar

- Every assumption is tagged fundamental (law) or convention (changeable), with reasoning.
- The rebuild starts from the bedrock, not from a tweak of the conventional approach.
- Fundamentals are quantified where the domain allows.
- The output names at least one inherited assumption that turned out to be optional.
