# polymath-backend

Backend craft for the Polymath marketplace. Database/runtime/language-agnostic patterns.

## What it ships

- Skills: `api-design-rest`, `api-versioning`, `db-schema`, `migration-plan`, `review-migration`, `audit-pg-config`.
- Commands: `/audit-config` (alias over `audit-pg-config`). `review-migration` is invoked directly as `/polymath-backend:review-migration`.

`api-versioning` (strategy for evolving a shipped API — mechanism, breaking-change rules, consumer-driven contracts, deprecation path) sits next to `api-design-rest`; the deprecation *notice* and *migration guide* artifacts stay in `polymath-release`.

`review-migration` and `audit-pg-config` (Postgres migration safety + config
audit) live next to `db-schema` and `migration-plan` rather than in a separate
one-decision install.

## Installation

```bash
claude plugin install polymath-backend@polymath
```

## Dependencies

- `polymath-core`
- `polymath-engineering`

## License

MIT.
