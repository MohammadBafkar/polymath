---
plugin: polymath-streaming
scenario: lake-layout-adls
expect:
  invoked:
    - polymath-streaming:data-lake-layout
  output_matches:
    - "(Delta|Iceberg|Parquet)"
    - "(small files|compaction|file siz)"
    - "(lifecycle|tier|zone)"
timeout_seconds: 120
---

# Prompt

> Lay out our new ADLS Gen2 data lake for clickstream and orders, queried by Spark and Trino. Event Hubs Capture lands Avro every 5 minutes. Pick formats, partitioning, and compaction.

Use polymath-streaming:data-lake-layout.

# Acceptance

- Zones with distinct access and retention.
- File size targets and sparing partitioning.
- Lifecycle tiers and erasure path.
