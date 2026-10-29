---
plugin: polymath-database
scenario: retention-plan-payments
expect:
  invoked:
    - polymath-database:data-retention-archiving
  output_matches:
    - "(partition|detach|drop)"
    - "(legal hold|erasure|delete)"
    - "(restore test|restore)"
timeout_seconds: 120
---

# Prompt

> Our ledger table is 4 TB and growing, backups take 9 hours, and we also have Kafka topics and a data lake holding the same payment data. Design retention and archiving, including GDPR erasure.

Use polymath-database:data-retention-archiving.

# Acceptance

- Retention periods come from the owner (marked TBD), not invented.
- Partition-drop purge instead of mass DELETE.
- Deletion reaches every derived copy; legal hold honored by the purge job.
- Archive restore test scheduled.
