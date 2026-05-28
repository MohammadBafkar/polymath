---
plugin: polymath-writing
skill: adr
trigger_prompts:
  - "write an ADR for choosing Postgres over MySQL"
  - "draft an architecture decision record about adopting OpenTelemetry"
  - "I need a Nygard-format ADR explaining why we picked Kafka over RabbitMQ"
must_invoke:
  - polymath-writing:adr
allow_invoke:
  - polymath-decisions:*
  - polymath-thinking:*
  - polymath-core:*
---

# Why this test exists

ADR ⇒ Architecture Decision Record ⇒ Michael Nygard format. The third
prompt names Nygard explicitly so a description that lost "Nygard" is
caught.
