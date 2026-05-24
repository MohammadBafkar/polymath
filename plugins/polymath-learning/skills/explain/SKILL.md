---
name: explain
description: Explain a concept at a specified audience tier (ELI5 / curious-undergrad / experienced-peer / domain-expert); pick the analogy and abandon it before it lies.
---

# explain

> Explanations fail when the audience tier is implicit. Pick the tier first, then the analogy, then the where-the-analogy-breaks.

## When to use

- The user asks "explain X" or "how does Y work?".
- A workflow needs to teach a concept before a decision.
- Onboarding a new contributor on an unfamiliar area.

## Inputs

- The concept (required).
- Audience tier (required; one of: `eli5`, `curious-undergrad`, `experienced-peer`, `domain-expert`).
- Optional: domain context (what the audience already knows).

## Procedure

1. **Pin the tier**. Each tier has a different contract:
   - **ELI5**: a 5-year-old hears it and gets the *vibe*. Concrete objects, one analogy, no jargon. Accept that detail is lost.
   - **Curious undergrad**: 1–2 paragraphs. One analogy, one limit of the analogy, one terminology bridge.
   - **Experienced peer**: skip the analogy. Compare to something they already know in this domain. Cite the mechanism, not the metaphor.
   - **Domain expert**: zero analogy. Talk about the specific thing — what's load-bearing, what's a footgun, what's commonly misunderstood.
2. **For ELI5 and undergrad**: pick the analogy. Then immediately state where it breaks. An analogy that doesn't disclose its limits will mislead the learner.
3. **For peer and expert**: pick a single reference point in their existing knowledge. "Like X but Y" beats invented metaphor.
4. **One concept per pass**. If you need to explain a prerequisite first, stop and explain the prerequisite alone first.

## Output

```text
explain: <concept> — tier: <ELI5 | undergrad | peer | expert>

[content following the tier contract]

[For ELI5 / undergrad only] Where the analogy breaks:
  - <one or two specific limits>
```

## Quality bar

- Tier is named at the top.
- ELI5 / undergrad → analogy + its limit.
- Peer / expert → no invented metaphor; reference existing knowledge.
- One concept per explanation. If a prerequisite is needed, surface it.

## Anti-patterns to avoid

- ELI5 that drops jargon ("it's like a hash table"). Not 5-year-old.
- Expert explanation that wastes time on prerequisites the expert already knows.
- Analogy without limits ("the kernel is like a librarian"). Misleads.
- Trying to cover multiple concepts in one explanation; the audience leaves with none.
