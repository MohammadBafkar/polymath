---
plugin: polymath-cloud
scenario: design-container-app
expect:
  invoked:
    - polymath-cloud:design-azure-pattern
  output_matches:
    - "(Container Apps|Functions|App Service|AKS)"
    - "(Cosmos|Azure SQL|Postgres)"
    - "(flip|runner|cost)"
timeout_seconds: 60
---

# Prompt

> Pick an Azure pattern for a bursty, containerized service that
> processes refund events. Peak ~500 RPS. Team already publishes
> Docker images.

Use polymath-cloud:design-azure-pattern.

# Acceptance

- Workload characterized quantitatively.
- Primary + runner-up + flip conditions.
- Cost driver named.
- Ops shape covered.
