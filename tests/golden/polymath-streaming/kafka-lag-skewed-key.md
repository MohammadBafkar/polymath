---
plugin: polymath-streaming
scenario: kafka-lag-skewed-key
expect:
  invoked:
    - polymath-streaming:kafka-performance-tuning
  output_matches:
    - "(skew|hot partition|key)"
    - "(batch|max.poll|commit)"
    - "(rebalance|cooperative|static)"
timeout_seconds: 120
---

# Prompt

> Our Kafka consumer group has 18 minutes of lag, brokers look idle, 24 consumers on 24 partitions, and one partition holds a third of the messages because we key by country. What do we do?

Use polymath-streaming:kafka-performance-tuning.

# Acceptance

- Identifies the consumer/key skew as the limit, not the brokers.
- Batching of per-record side effects; key change as a versioned migration.
