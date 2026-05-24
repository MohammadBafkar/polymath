# polymath-connector-notion

Notion connector for the Polymath marketplace. Mirrors repo Markdown into Notion pages with drift detection.

## What it ships

- MCP server: Notion MCP server (default: `@notionhq/mcp-server`) via `npx`.
- Skills: `sync-doc-to-notion` — Markdown → Notion blocks, repo source-of-truth backlink, sync-key dedupe, drift detection before overwrite.
- Reference: [`references/notion-tools.md`](references/notion-tools.md).

## Installation

```bash
claude plugin install polymath-connector-notion@polymath \
  --config notionToken=<secret> \
  --config notionRootPageId=<page-id>
```

## Dependencies

- `polymath-core`

## License

Apache-2.0.
