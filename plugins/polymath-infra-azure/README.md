# polymath-infra-azure

Azure write-side infrastructure craft for the Polymath marketplace.

## What it ships

- Skills: `design-azure-pattern` — compute (Functions / Container Apps / App Service / AKS), database (Azure SQL / Cosmos DB / Postgres Flex), storage, messaging, networking with cost driver + flip conditions.
- Command: `/polymath-infra-azure:design`.

## Pairs with

- `polymath-connector-azure` — read-side resource inspection.
- `polymath-connector-terraform` — review plan output before apply.

## Installation

```bash
claude plugin install polymath-infra-azure@polymath
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
