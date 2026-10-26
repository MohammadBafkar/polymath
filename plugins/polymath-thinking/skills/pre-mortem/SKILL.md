---
name: pre-mortem
description: Frame the project as already failed and list the most plausible reasons why, so they can be mitigated before launch; not adversarial critique (red-team).
---

# pre-mortem

> Inverse postmortem. Imagine the future failure; list why; mitigate.

**Mode:** generative — diverge before converging. Produce genuinely different options first (the obvious answer is one candidate, not the answer), then narrow with stated criteria.

## When to use

- Before committing to a non-trivial plan (Gary Klein's "prospective hindsight").
- A workflow includes a planning step and the user wants risk uncovering before implementation.

## Inputs

- The plan or PRD under review (required). None given: ask for it.
- Optionally: a timeline (default: the plan's own launch date + 30 days).

## Procedure

1. Say "It is now <timeline> and the project failed."
2. Generate 6–10 specific failure *stories* — each a plausible narrative of how it went wrong, not a risk category. Imagine them before judging them. Range across:
   - Technical (it didn't scale, the migration broke prod, the dependency was abandoned).
   - Organizational (the team owner left, priorities shifted, blocked on another team).
   - User (no adoption, hostile feedback, used it in an unintended way).
   - Operational (alert fatigue, runbook never updated, on-call missed it).
3. For each, rate likelihood and impact as L / M / H, with a one-line reason drawn from the plan.
4. **Pick the top 3 mechanically:** score L=1, M=2, H=3; rank by likelihood × impact, ties broken by higher impact, then by list order. Propose a concrete mitigation for each, and the earliest signal that it is happening.

## Output

```text
Pre-mortem: <plan>

Failure modes:
  1. Technical: …            (likelihood: M, impact: H)
  2. Organizational: …       (likelihood: L, impact: H)
  …

Top 3 (likelihood × impact, ties → impact):
  - <failure mode> (M×H = 6): mitigation: … · early signal: …
  - <failure mode> (H×M = 6): mitigation: … · early signal: …
  - <failure mode> (L×H = 3): mitigation: … · early signal: …
```

## Quality bar

- Specific failure modes — "scaling problems" is not specific; "the rate-limiter store grows linearly per IP" is.
- At least one failure mode in each of the four ranges above.
- Mitigations are concrete (a code change, a guardrail, a deferred decision), not "be more careful".
