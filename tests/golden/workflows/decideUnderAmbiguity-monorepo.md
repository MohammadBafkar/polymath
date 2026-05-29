---
workflow: decideUnderAmbiguity
scenario: decideUnderAmbiguity-monorepo
expect:
  output_matches:
    - "docs/decisions/.*-evidence.md"
    - "docs/decisions/.*-tradeoff.md"
    - "docs/decisions/.*-daci.md"
    - "docs/adrs/"
    - "([Uu]nknown|[Aa]ssumption)"
  timeout_seconds: 240
---

# Prompt

> Decide whether we should move our three services into a monorepo. We have
> incomplete data on CI cost and team workflow impact.
>
> Run `/polymath-flows:run-workflow decideUnderAmbiguity decision="Move the three services into a monorepo"`.

# Acceptance

- The cynefin frame classifies the decision context.
- An evidence ledger separates facts from assumptions from unknowns, and per
  unknown names the evidence that would change the answer and the reversibility.
- A weighted tradeoff matrix compares the options and names the tie-breaker.
- The red-team step names which objections should block versus be accepted.
- A DACI names one Approver (≠ Driver) and a real deadline.
- An ADR is recorded with an "Open questions / revisit triggers" section.
