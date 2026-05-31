---
name: pre-mortem
description: Imagine the project has already failed; list the most plausible reasons why so they can be mitigated before launch. Imagines failure pre-launch; not adversarial critique (red-team).
---

# pre-mortem

> Inverse postmortem. Imagine the future failure; list why; mitigate.

## When to use

- Before committing to a non-trivial plan (Gary Klein's "prospective hindsight").
- A workflow includes a planning step and the user wants risk uncovering before implementation.

## Inputs

- The plan or PRD under review.
- Optionally: a timeline ("in 30 days").

## Procedure

1. Say "It is now <timeline> and the project failed."
2. Generate 6–10 specific failure modes. Range across:
   - Technical (it didn't scale, the migration broke prod, the dependency was abandoned).
   - Organizational (the team owner left, priorities shifted, blocked on another team).
   - User (no adoption, hostile feedback, used it in an unintended way).
   - Operational (alert fatigue, runbook never updated, on-call missed it).
3. For each, rate likelihood (low/medium/high) and impact (low/medium/high).
4. Pick the top 3 by likelihood × impact. Propose a concrete mitigation for each.

## Output

```text
Pre-mortem: <plan>

Failure modes:
  1. Technical: …            (likelihood: M, impact: H)
  2. Organizational: …       (likelihood: L, impact: H)
  …

Top 3:
  - <failure mode>: mitigation: …
  - <failure mode>: mitigation: …
  - <failure mode>: mitigation: …
```

## Quality bar

- Specific failure modes — "scaling problems" is not specific; "the rate-limiter store grows linearly per IP" is.
- At least one failure mode in each of the four ranges above.
- Mitigations are concrete (a code change, a guardrail, a deferred decision), not "be more careful".
