# polymath-connector-stripe

Stripe connector for the Polymath marketplace. Read-mostly triage for charges, refunds, and disputes.

## What it ships

- MCP server: Stripe MCP server (default: `@stripe/mcp-server`) via `npx`.
- Skills: `refund-or-dispute-triage` — classify by ID prefix, read lifecycle, propose an explicit API action for operator approval. Never auto-refunds.
- Reference: [`references/stripe-tools.md`](references/stripe-tools.md).

## Installation

```bash
claude plugin install polymath-connector-stripe@polymath \
  --config stripeApiKey=rk_live_xxx \
  --config stripeMode=live
```

Default mode is `test`. Live mode triage is permitted but mutating actions are surfaced for human approval, not auto-executed.

## Dependencies

- `polymath-core`

## License

Apache-2.0.
