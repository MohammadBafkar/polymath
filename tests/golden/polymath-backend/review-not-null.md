---
plugin: polymath-backend
scenario: review-not-null
expect:
  invoked:
    - polymath-backend:review-migration
  output_matches:
    - "(ACCESS EXCLUSIVE|lock)"
    - "(NOT NULL|NOT VALID|VALIDATE)"
    - "(lock_timeout|CONCURRENTLY|backfill)"
timeout_seconds: 60
---

# Prompt

> Review a migration that adds a NOT NULL column to a 50M-row table:
> ALTER TABLE refunds ADD COLUMN currency text;
> ALTER TABLE refunds ALTER COLUMN currency SET DEFAULT 'USD';
> ALTER TABLE refunds ALTER COLUMN currency SET NOT NULL;

Use polymath-backend:review-migration.

# Acceptance

- Per-statement lock classification.
- SET NOT NULL on 50M rows flagged as unsafe.
- Multi-step rollout (NOT VALID → backfill → VALIDATE → SET NOT NULL) proposed.
- lock_timeout recommendation surfaces.
