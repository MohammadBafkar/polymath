---
plugin: polymath-scalability
scenario: system-design-notifications
expect:
  invoked:
    - polymath-scalability:system-design
  output_matches:
    - "(queue|Kafka|outbox)"
    - "(idempot)"
    - "(rate limit|bulkhead|priorit)"
timeout_seconds: 120
---

# Prompt

> Design a notification service (push, email, SMS) for 20M users with campaign bursts to 40k/s. Transactional notifications must arrive within 5 seconds. Give me the architecture and trade-offs.

Use polymath-scalability:system-design.

# Acceptance

- Numeric targets and capacity before components.
- Priority isolation of transactional vs marketing traffic.
- Failure modes with user-visible behavior; alternatives and reversal triggers.
