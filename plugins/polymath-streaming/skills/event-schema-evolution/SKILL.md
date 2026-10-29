---
name: event-schema-evolution
description: Evolve event schemas safely — registry, Avro/Protobuf compatibility modes, upgrade order, breaking-change playbook, CI contract checks.
---

# event-schema-evolution

> A published event is a public API with an unknown set of consumers and a very long memory. Evolve it additively, enforce compatibility in CI, and when you must break it, version and migrate on purpose.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- Defining the schema and versioning policy for a new event stream or topic.
- A producer wants to add, rename, remove, or retype a field and you must know who breaks.
- Consumers crash on deserialization after a deploy, or the lake/warehouse schema drifts from the stream.

Not this when: you're designing the business event catalog and sagas — `polymath-architecture:event-driven-design`; REST/HTTP API versioning — `polymath-backend:api-versioning`; topic partitioning and delivery — `streaming-design`.

## Inputs

- The event(s): producer owner, known consumers (services, stream jobs, lake ingestion), serialization format and registry in use.
- Retention/replay: how long old events live and whether consumers replay from the beginning (old schemas must stay readable for as long as old data exists).
- The proposed change and why; deployment independence (can all consumers and producers deploy in lockstep? usually not).
- Downstream sinks: lake/warehouse tables, search indexes, caches that materialize the schema.

## Procedure

1. **Pick a schema-first format with a registry.** Avro (compact, strong evolution rules via writer/reader schema resolution), Protobuf (field numbers, wide language support), or JSON Schema (human-friendly, weaker evolution guarantees). Register schemas in a registry (Confluent Schema Registry, Apicurio, Azure Schema Registry, AWS Glue Schema Registry); messages carry a schema ID, not the schema. Untyped JSON with no registry means breaks are found in production.
2. **Standardize the envelope**: `event_id` (unique, for idempotency), `event_type`, `schema_version`, `occurred_at` (event time), `producer`, `correlation_id`/`trace` context, and the `subject`/entity key. Keep the payload business-meaningful and past tense (`polymath-architecture:event-driven-design`). Avoid leaking internal table structure.
3. **Choose the compatibility mode per subject** and enforce it in the registry:
   - **BACKWARD** (consumers on the new schema can read old data) — upgrade **consumers first**; the default and right for most streams, and required if consumers replay old events.
   - **FORWARD** (old consumers can read new data) — upgrade **producers first**.
   - **FULL** (both) — safest when upgrade order is uncontrolled; the most restrictive.
   - **\*_TRANSITIVE** variants check against all prior versions, not just the latest — use whenever old data persists (retained topics, lake history).
   - **NONE** only for deliberately versioned-by-topic contracts.
4. **Apply the safe-change rules** (format-specific):
   - Add fields as **optional with a default** (Avro default; Protobuf new field number, optional); consumers must ignore unknown fields (tolerant reader).
   - Never reuse or renumber Protobuf field numbers; `reserved` the removed ones. In Avro, removal is only safe for fields that had a default; renames need `aliases`.
   - Don't change a field's type or meaning in place (e.g. cents → dollars, enum value semantics). Widening (int → long) may be allowed by the format but check each language's consumers.
   - Enums: adding values breaks consumers that don't handle unknowns — define a default/`UNKNOWN` symbol up front.
   - Required fields are forever; make new fields optional.
5. **Breaking change playbook** (when compatible evolution isn't possible): **expand → migrate → contract.** (a) Publish the new shape alongside the old — a new event type/version or new topic (`orders.order-events.v2`) with **dual publishing** for a defined window (via the outbox so both stay consistent); (b) migrate consumers one at a time, tracking who reads v1 (consumer-group lag/metrics, registry usage); (c) stop v1 only after the last consumer migrates and the deprecation date has passed (`polymath-release:deprecation-plan`); (d) archive or `upcast` old events for replay. Never "just deploy" a breaking schema to a shared topic.
6. **Handle history.** Event-sourced or long-retention streams need **upcasters** (convert old versions to the current shape at read time) or a one-time rewrite into a new topic. Lake ingestion maps schema changes explicitly (Delta `mergeSchema`/Iceberg schema evolution) with a policy: additive columns auto-evolve; type changes and drops go through review (`data-lake-layout`).
7. **Automate the guard in CI.** On every schema PR: registry compatibility check against the latest (or all) versions; contract tests with consumer-driven expectations (Pact-style) or a sample of real consumers' deserializers; fail on incompatible change; require an owner approval for a mode change. Generate code (types) from the registry so producers and consumers can't drift.
8. **Govern.** Naming and subject strategy (topic-name vs record-name subjects — pick one deliberately), ownership and a contact per schema, documentation of fields and semantics, PII tagging (and encryption/tokenization of those fields), a deprecation policy with dates, and a deserialization-failure path (poison message → DLQ, with schema ID logged) so one bad schema doesn't stall a partition (`polymath-streaming:streaming-design`).
9. **Monitor**: deserialization error rate per consumer, registry compatibility rejections, count of active schema versions in flight, consumers still on deprecated versions.

## Output

```text
Schema evolution plan: orders.order-events (Avro, Confluent registry, 30-day retention, lake bronze replays full history)

Change requested: split `total` (decimal dollars) into `amount_minor` (int cents) + `currency`.
Assessment: BREAKING (type and unit change; consumers: fulfillment, billing, analytics-sink, fraud — 4 known [VERIFY: registry/consumer-group audit]).
Mode: BACKWARD_TRANSITIVE (history replayed) — current subject compatible; this change is not.
Plan (expand → migrate → contract)
  1. Add optional `amount_minor` (default null) and `currency` (default null) to v3 — compatible; producer writes BOTH `total` and new fields (derived consistently in one place).
  2. Consumers migrate to the new fields on their own schedule; contract tests assert `amount_minor == round(total*100)` during the window.
  3. Window: 60 days; track readers of `total` via consumer metrics. Deprecation notice + dates sent to owners.
  4. v4 removes `total` after the last consumer migrates; lake bronze keeps v1–v3 via mergeSchema; upcaster maps total → amount_minor for replay.
Envelope: event_id, event_type=OrderPlaced, schema_version, occurred_at, correlation_id, order_id (key) — unchanged.
CI: compatibility check on PR (BACKWARD_TRANSITIVE) + consumer contract tests; owner approval needed to change mode.
Rollback: stop writing new fields (they are optional) — consumers fall back to `total`.
Unknowns: [TBD: unregistered consumers reading raw topic], [VERIFY: rounding rule for fractional currencies].
```

## Quality bar

- The compatibility mode matches the real upgrade order and retention (transitive when old data persists) and is enforced by the registry, not by convention.
- Breaking changes follow expand → migrate → contract with a dated window and a way to see who still reads the old shape.
- Additive changes are optional-with-default, enums have an unknown default, and removed field IDs are reserved.
- CI blocks incompatible schemas and runs consumer contract tests.
- Replay/history and downstream tables are addressed, not just live consumers.

## Anti-patterns to avoid

- Changing the meaning or unit of a field while keeping its name and type.
- Deploying a schema change straight to a shared topic "because all consumers are ours" — until one isn't.
- Untyped JSON events with no registry.
- Reusing Protobuf field numbers or making new fields required.
- Choosing BACKWARD (non-transitive) when consumers replay months of history.
- Dual-publishing v1 and v2 forever with no deprecation date.
