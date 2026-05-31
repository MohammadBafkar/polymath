---
name: test-strategy
description: Design a layered test strategy (pyramid) for a feature or repo; recommends unit/integration/e2e split and the cheapest set that covers the acceptance criteria. Plans layers; doesn't write tests.
---

# test-strategy

> Propose the smallest test pyramid that covers a feature's acceptance criteria. Output is a short strategy doc, not test code.

## When to use

- A new feature or repo needs a deliberate test plan.
- A workflow invokes `polymath-qa:test-strategy`.
- The user asks "what should we test here?".

## Inputs

- PRD path (preferred) or feature description.
- Repo test infrastructure (detect via `feature-dev`'s signals).

## Procedure

1. Read the PRD's **Acceptance criteria**. Each criterion is one root test obligation.
2. Classify each criterion by the cheapest layer that can verify it:
   - **Unit** — pure logic, deterministic, fast (< 100ms). Default.
   - **Integration** — touches one external boundary (DB, queue, HTTP).
   - **E2E** — exercises the full deployed system.
3. Apply the heuristic: 70/20/10 unit/integration/e2e by count. Anything above that needs a justification line.
4. For each criterion, name the test case headline ("rejects 6th login attempt in 60s window") and the layer.
5. Call out gaps:
   - Acceptance criteria with no plausible test.
   - Behaviors not in the PRD but visible in the diff.

## Output

```text
Test strategy: <feature>

Layer  Count  Justification
unit            <n>  …
integration     <n>  …
e2e             <n>  …

Per-criterion plan:
  AC1: <headline> — unit
  AC2: <headline> — integration (touches Redis)
  …

Gaps:
  - No test plan for the rate-limit reset path (PRD §3.2).
```

## Quality bar

- No mock-heavy unit test for behavior that crosses a boundary; bump it to integration.
- No e2e test for behavior that a unit test would already cover.
- Each "integration" or "e2e" classification cites the boundary it crosses.
