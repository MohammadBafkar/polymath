# polymath-infra-postgres

PostgreSQL craft for the Polymath marketplace.

## What it ships

- Skills:
  - `review-migration` — per-statement lock classification, multi-step NOT NULL / FK rollout patterns, CONCURRENTLY discipline, lock_timeout recommendations.
  - `audit-pg-config` — memory + connections + WAL + autovacuum + logging tuning.
- Commands: `/polymath-infra-postgres:review-migration`, `/polymath-infra-postgres:audit-config`.

## Installation

```bash
claude plugin install polymath-infra-postgres@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
