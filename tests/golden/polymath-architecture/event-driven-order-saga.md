---
plugin: polymath-architecture
scenario: event-driven-order-saga
expect:
  invoked:
    - polymath-architecture:event-driven-design
  output_matches:
    - "(outbox|transactional outbox)"
    - "(saga|compensat)"
    - "(idempoten|dedup)"
  not_invoked:
    - polymath-backend:api-design-rest
timeout_seconds: 120
---

# Prompt

> Design the order-fulfilment flow across our order, payment, and
> inventory services. Placing an order must capture payment and
> reserve stock; any step can fail. Right now each service writes its
> row and publishes a Kafka message in the same code block.

Use polymath-architecture:event-driven-design.

# Acceptance

- The dual-write (DB + Kafka in one block) is flagged and replaced with the transactional outbox pattern.
- A saga is designed with a compensating action per step (refund payment, release stock).
- Consumers are made idempotent with a named dedup key; at-least-once + reordering assumed.
- Choreography-vs-orchestration choice is stated with a reason.
- Events are business facts (OrderPlaced, PaymentCaptured), not table change-logs.
