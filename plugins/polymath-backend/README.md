# polymath-backend

Backend craft for the Polymath marketplace. Database/runtime/language-agnostic patterns.

## What it ships

- Skills: `api-design-rest`, `db-schema`, `migration-plan`, `review-migration`, `audit-pg-config`.
- Commands: `/review-migration`, `/audit-config` (thin aliases).

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
