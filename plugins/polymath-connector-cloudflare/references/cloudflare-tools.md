# Cloudflare MCP tools (reference)

Default server: `@cloudflare/mcp-server` (or any community Cloudflare MCP server with the same tool shape).

Auth: `CLOUDFLARE_API_TOKEN` from `userConfig`. **Use scoped API tokens**, not Global API Keys (which carry full account access and cannot be scoped).

## Tools exposed (subset)

### Read

- `zones.list` / `zones.get`
- `dns_records.list` — DNS records for a zone.
- `analytics.dashboard` — aggregated traffic + status.
- `graphql.query` — GraphQL Analytics API (httpRequestsAdaptive, firewallEventsAdaptive, etc.).
- `workers.list` / `workers.get`
- `workers.tail` — live tail of worker invocations (short window).
- `firewall.rules.list`
- `accounts.get`

### Write (operator-approval territory)

- `dns_records.update` — change a DNS record.
- `firewall.rules.update` — modify a WAF rule.
- `workers.upload` — deploy a worker.

## Token scope

Recommended scopes for triage:

- Zone → Read on the zones you triage.
- Zone → Analytics: Read.
- Account → Workers Scripts: Read (for tail + listing).
- Account → Firewall Services: Read.

Do not grant Edit/Delete on triage tokens. Mutating actions go through a separate operator-only token.

## Common pitfalls

- "Cloudflare proxied" status (`proxied=true`) means the orange cloud. Records with `proxied=false` bypass the CDN/WAF entirely — silently dropping you back to origin-direct.
- The Analytics API has two flavors: REST (eventually consistent, ~1 min lag) and GraphQL (near real-time but more rate-limited). For incident triage, prefer GraphQL.
- `workers.tail` shows live invocations only — historical worker errors need Workers Analytics or your own logging sink.
- WAF rule IDs are stable per rule but the same rule can be deployed across multiple zones with different IDs. Don't compare ruleIds across zones.
- Cloudflare's "Source IP" in logs is the *client* IP after Cloudflare proxying; for actual origin server IPs use the `CF-Connecting-IP` header upstream rather than tracing Cloudflare's outbound IPs.
