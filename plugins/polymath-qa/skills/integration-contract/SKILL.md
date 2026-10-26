---
name: integration-contract
description: Design integration/contract tests for a service boundary — consumer-driven contracts, stub-vs-hit, fixtures, failure modes. Boundary tests, not unit tests (unit-tests) or the plan (test-strategy).
---

# integration-contract

> Test the seams between components and services — where unit tests can't reach and full e2e is too slow and flaky.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A service talks to another service, a DB, a queue, or an external API and you need confidence at that boundary.
- You want consumer-driven contract tests so a provider change can't silently break a consumer.
- A workflow invokes `polymath-qa:integration-contract`.

This designs *boundary* tests. It is not unit testing (`polymath-qa:unit-tests`), the cross-layer plan (`polymath-qa:test-strategy`), or smell review (`polymath-qa:test-smell`).

## Inputs

- The boundary under test: the components/services and the contract (schema, endpoints, messages).
- Which side you own (consumer, provider, or both).
- Available test doubles / sandboxes / ephemeral environments. Unknown: inspect the repo (testcontainers, docker-compose, Pact/contract config) before assuming none exist.

## Procedure

1. **Map the boundary** — list every interaction (request/response, event, query) and its contract.
2. **Stub vs hit** — decide per dependency: stub third-party + nondeterministic; hit owned infra via an ephemeral instance or testcontainer. State the rule you applied.
3. **Contract tests** — for each interaction, pin the schema/shape both sides agree on; consumer-driven where you own the consumer. A provider change that breaks the contract must fail a test.
4. **Failure modes** — cover timeout, 5xx, malformed payload, partial write, retry/idempotency, not just the happy path.
5. **Fixtures/data** — define deterministic setup + teardown; no shared mutable state between tests.
6. List the tests with their boundary, stub/hit decision, and the failure mode each covers.

## Output

A test plan per boundary, then the test files written in the repo's conventions:

```text
Boundary: orders-service → payments-api (we own the consumer)

Interaction                      Stub/hit  Why                                  Tests
POST /v1/charges                 stub      third-party, nondeterministic        contract: request/response schema pinned (Pact)
                                                                                 failure: timeout 2s → order stays PENDING, retried
                                                                                 failure: 5xx → no double charge on retry (idempotency key)
                                                                                 failure: malformed body → 502 to caller, alert logged
orders DB (Postgres)             hit       owned; testcontainers postgres:16   partial write: crash between insert + outbox → no orphan
order.created event (Kafka)      hit       owned; testcontainers kafka          contract: event schema v3 validated against registry

Fixtures: per-test schema + truncate on teardown; no shared rows.
Run: make test-integration   (needs Docker)
```

## Quality bar

- Every owned boundary has a contract test that fails on a breaking change.
- Each test states stub-vs-hit and why; nondeterministic dependencies are stubbed.
- At least the timeout + error + malformed-input failure modes are covered, not only success.
