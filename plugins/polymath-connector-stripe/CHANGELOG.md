# Changelog — polymath-connector-stripe

## [Unreleased]

### Added

- Initial v0.1 components: `.mcp.json` referencing a Stripe MCP server; `refund-or-dispute-triage` skill (charge/refund/dispute classification by ID prefix, lifecycle replay via events.list, customer-comms-safe summary, operator-approval gate for mutations); `references/stripe-tools.md`.
- `userConfig.stripeApiKey` (sensitive; `rk_…` restricted key required) and `userConfig.stripeMode` (default `test`).
