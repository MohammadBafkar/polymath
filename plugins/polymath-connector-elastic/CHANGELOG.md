# Changelog — polymath-connector-elastic

## [Unreleased]

### Added

- Initial v0.1 components: `.mcp.json` referencing an Elasticsearch MCP server; `log-search` skill (refuses `*` patterns + unbounded ranges, `track_total_hits=10000` cap, PII redaction, cross-index `trace.id` hint); `references/elastic-tools.md`.
- `userConfig.elasticEndpoint` and `userConfig.elasticApiKey` (sensitive).
