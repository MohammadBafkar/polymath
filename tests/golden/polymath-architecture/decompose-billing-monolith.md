---
plugin: polymath-architecture
scenario: decompose-billing-monolith
expect:
  invoked:
    - polymath-architecture:service-decomposition
  output_matches:
    - "(strangler)"
    - "(characterization test|seam)"
    - "(data ownership|own its data|shared database)"
  not_invoked:
    - polymath-engineering:feature-dev
timeout_seconds: 120
---

# Prompt

> Our billing monolith is hard to deploy — every change re-ships the
> whole app. Leadership wants to "move to microservices". Help me
> decide what to extract first and how, without a big-bang rewrite.

Use polymath-architecture:service-decomposition.

# Acceptance

- Keep-modular-monolith is considered and chosen-or-rejected against a concrete forcing function (independent deploy cadence here).
- Extraction candidates are ranked by value ÷ risk with a data-ownership note; shared-database boundaries are rejected.
- A strangler-fig sequence is proposed (facade + incremental migration), not a rewrite.
- Characterization tests are required before extraction to preserve behavior.
- The added distributed-systems cost is named.
