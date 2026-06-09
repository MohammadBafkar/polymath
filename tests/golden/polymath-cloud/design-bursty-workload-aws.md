---
plugin: polymath-cloud
scenario: design-bursty-workload
expect:
  invoked:
    - polymath-cloud:design-aws-pattern
  output_matches:
    - "(Lambda|ECS|EKS|Fargate)"
    - "(DynamoDB|RDS|Aurora|S3)"
    - "(flip|runner.up|threshold)"
timeout_seconds: 60
---

# Prompt

> Pick an AWS pattern for a bursty, stateless service that processes
> JSON refund events. Peak ~500 RPS, idle 70% of the day, task ~500ms.

Use polymath-cloud:design-aws-pattern.

# Acceptance

- Workload characterized quantitatively (RPS, latency, duration).
- A primary choice + runner-up + flip conditions.
- Cost driver named per primitive.
- Ops shape (logs/tracing/errors) covered.
