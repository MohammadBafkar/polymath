# Changelog — polymath-connector-cloudflare

## [Unreleased]

### Added

- Initial v0.1 components: `.mcp.json` referencing a Cloudflare MCP server; `edge-incident-triage` skill (status histogram + origin/worker/edge bucketing + WAF/DNS sanity + CF-Ray sample for downstream filtering); `references/cloudflare-tools.md`.
- `userConfig.cloudflareApiToken` (sensitive; scoped token, not Global API Key) and `userConfig.cloudflareAccountId`.
