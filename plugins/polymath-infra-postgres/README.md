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

<!-- connector-policy:start -->
## Connector policy disclosure

Auto-generated from [`docs/CONNECTOR-POLICY.md`](../../docs/CONNECTOR-POLICY.md)
by `tools/sync-connector-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** Postgres official docs + several DB MCPs
- **Polymath value:** Schema + migration plan workflow shape
- **Sunset trigger:** Demote when an official Postgres MCP ships migration-plan workflow.
- **Status:** `experimental`
<!-- connector-policy:end -->

## License

Apache-2.0.
