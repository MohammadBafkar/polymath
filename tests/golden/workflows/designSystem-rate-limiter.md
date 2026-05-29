---
workflow: designSystem
scenario: designSystem-rate-limiter
expect:
  output_matches:
    - "docs/design/.*-deliberation.md"
    - "docs/(architecture|rfcs)/"
    - "docs/adrs/"
    - "docs/design/.*-challenge.md"
    - "([Aa]ssumption|[Uu]nknown|[Ee]vidence)"
  timeout_seconds: 300
---

# Prompt

> Design a rate limiter for the /login endpoint. We don't yet know peak traffic
> or whether we can rely on a shared Redis.
>
> Run `/polymath-flows:run-workflow designSystem subject="Rate limiter for /login" scope=medium assumptions="peak rps unknown; shared Redis availability unconfirmed"`.

# Acceptance

- The orient step lists what is not yet known from the codebase.
- The cynefin frame sets the expected confidence of the recommendation.
- The deliberation labels facts vs assumptions and names the spike that would resolve each assumption.
- The design doc (architecture-doc or rfc) carries explicit Assumptions / Open Unknowns / Evidence sections.
- STRIDE runs, or is skipped with a one-line justification for small scope.
- An ADR records rejected alternatives; the red-team names the single evidence that would reverse the design.
