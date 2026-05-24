# Stripe MCP tools (reference)

Default server: `@stripe/mcp-server` (or any community Stripe MCP server with the same tool shape).

Auth: `STRIPE_API_KEY` from `userConfig`. **Use a restricted key (`rk_…`)**, not a secret key (`sk_…`). Restricted keys scope to specific resource × action pairs and live alongside the secret key in Stripe's API dashboard.

## Tools exposed (subset)

### Read

- `charges.retrieve` / `charges.list`
- `payment_intents.retrieve` / `list`
- `refunds.retrieve` / `list`
- `disputes.retrieve` / `list`
- `customers.retrieve` (PII-bearing — handle output carefully)
- `events.list` (lifecycle timeline)

### Write (use sparingly; require operator approval)

- `refunds.create` — issues a real refund. Operator-only.
- `disputes.update` — attaches evidence to a chargeback. Operator-only.
- `payment_intents.cancel` — cancels an uncaptured intent. Operator-only.

## Key scope

Stripe restricted keys can be scoped to resources × actions. Recommended scopes for triage:

- `charges`: read
- `payment_intents`: read
- `refunds`: read (NOT write; refunds via separate operator-approved flow)
- `disputes`: read (and write only if this connector handles evidence)
- `events`: read

## Common pitfalls

- Stripe responses include `customer.email`, `customer.name`, `billing_details.*`. Treat as PII; redact in any output that may leave the connector.
- `charges.refunded = true` does not mean fully refunded. Check `amount_refunded` vs `amount`.
- `events.list` is paginated; without `limit=100` you may miss earlier lifecycle entries.
- Test-mode and live-mode objects share neither IDs nor data; `ch_test_…` in live mode is a not-found.
- API version is fixed per restricted key at the time of creation. Older keys may return older response shapes.
