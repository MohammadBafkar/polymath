# polymath-connector-elastic

Elasticsearch connector for the Polymath marketplace. Bounded log search with PII redaction and cross-index hints.

## What it ships

- MCP server: Elasticsearch MCP server (default: `@elastic/mcp-server`) via `npx`.
- Skills: `log-search` — typed time-bounded queries, capped count + top buckets + 10-sample evidence + cross-index hint.
- Reference: [`references/elastic-tools.md`](references/elastic-tools.md).

## Installation

```bash
claude plugin install polymath-connector-elastic@polymath \
  --config elasticEndpoint=https://search.example.com:9200 \
  --config elasticApiKey=<key>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
