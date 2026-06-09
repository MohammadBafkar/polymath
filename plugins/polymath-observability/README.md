# polymath-observability

Observability concept plugin for the Polymath marketplace — both the design
**discipline** and the **integration** for querying observability vendors, in
one plugin (the `observability` capability).

## What it ships

- **Design skills:** `logging-strategy`, `tracing-strategy-otel`,
  `metrics-design` (RED/USE) — how to design what you emit.
- **Integration skills:** `dashboard-snapshot`, `trace-investigate`,
  `log-search`, `query-during-incident`, `author-monitor`, `triage-error` —
  how to investigate what you've emitted, across providers.
- **Providers:** Datadog, Grafana, Honeycomb, Elastic, Sentry — each via a
  `bindings/<provider>/binding.json` + a `.mcp.json` server. Configure only the
  providers you use (`.polymath/capabilities.yaml`); the rest stay idle.

<!-- mcp-package-status -->
> ⚠️ **Some MCP packages not yet published.** `@datadog/mcp-server`,
> `@grafana/mcp-server`, `@honeycomb/mcp-server`, and `@elastic/mcp-server` do
> **not** resolve on npm as of 2026-06-08 (Sentry's `@sentry/mcp-server` does).
> Substitute the real command for the provider(s) you use in `.mcp.json` before
> relying on them. See [`docs/INTEGRATION-POLICY.md` §4.2](../../docs/INTEGRATION-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-observability@polymath
```

## Dependencies

- `polymath-core`

<!-- integration-policy:start -->
## Integration policy disclosure

Auto-generated from [`docs/INTEGRATION-POLICY.md`](../../docs/INTEGRATION-POLICY.md)
by `tools/sync-integration-policy.py`. Do not edit by hand —
edit the policy table and re-run the script.

- **Official surface:** `observability` — Datadog, Grafana, Honeycomb, Elastic, Sentry (merged with the observability design discipline)
- **Polymath value:** RED/USE + logging + tracing design **and** snapshot / trace-walk / bounded-scan / incident-query / monitor-authoring / error-triage across providers
- **Sunset trigger:** Demote a provider when its upstream MCP ships postmortem-evidence + investigative templates.
- **Status:** `experimental`
<!-- integration-policy:end -->

## License

MIT.
