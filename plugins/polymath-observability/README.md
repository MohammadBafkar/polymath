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
  `bindings/<provider>/binding.json` + an `mcp/servers.json` server template
  (rendered to your host's MCP config only when you opt in; if your agent
  already has the provider's MCP registered, it is reused — nothing is
  auto-added). Configure only the providers you use
  (`.polymath/capabilities.yaml`); the rest stay idle.

<!-- mcp-package-status -->
> ⚠️ **Some MCP packages not yet published.** The server templates
> (`mcp/servers.json`) name `@datadog/mcp-server`, `@grafana/mcp-server`,
> `@honeycomb/mcp-server`, and `@elastic/mcp-server`, which do **not** resolve
> on npm as of 2026-06-08 (Sentry's `@sentry/mcp-server` does). If you opt in to
> installing a rendered fragment, substitute the real command for the
> provider(s) you use first. If your host agent already has the provider's MCP
> registered, it is reused and no template is needed. See
> [`docs/INTEGRATION-POLICY.md` §4.2](../../docs/INTEGRATION-POLICY.md).
<!-- /mcp-package-status -->

## Installation

```bash
claude plugin install polymath-observability@polymath
```

MCP servers are not auto-registered. If your agent already has the provider's
MCP registered (Datadog, Grafana, Sentry, …), the skills use it. Otherwise run
`python3 tools/mcp-registry.py render --plugin polymath-observability --target <your-host>`
and apply the fragments for the providers you use to your host's MCP config.

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
