# Notion MCP tools (reference)

Default server: `@notionhq/mcp-server` (or any community Notion MCP server with the same tool shape).

Auth: `NOTION_TOKEN` from `userConfig`. Use an **internal integration** secret, not an OAuth token; share only specific parent pages with it.

## Tools exposed (subset)

### Read

- `pages.get` — fetch page metadata + properties.
- `pages.children.list` — list child blocks (paginated).
- `blocks.get` — read a single block.
- `databases.get` / `databases.query` — read a database schema + rows.
- `search` — workspace-wide search (limited to pages shared with the integration).

### Write

- `pages.create` — new page under a parent (page or database).
- `pages.update` — update properties + archive state. Does not edit content blocks.
- `blocks.children.append` — append blocks to a page.
- `blocks.update` — change a single block's content.
- `blocks.delete` — archive a block (Notion has no hard delete via API).
- `comments.create` — leave a comment on a page or block.

## Integration scope

Notion integrations only see pages explicitly shared with them. Scope by:

- Sharing a single parent page (e.g. an `Engineering` workspace section) with the integration — avoid sharing the workspace root.
- Issuing one integration per use case (sync vs. read-only docs vs. database automation).
- Rotating the secret when the integration's blast radius changes.

## Common pitfalls

- Notion's "rich text" is a list of runs with inline formatting; appending plain strings strips formatting. Always build rich-text arrays for non-trivial content.
- Block order is preserved but block IDs change when blocks are deleted/recreated. Do not store block IDs as long-term identifiers; use page IDs + structural offsets instead.
- `archived: true` on a page acts like soft-delete; archived pages disappear from search but still respond to direct reads. Empty trash from the Notion UI for permanent delete.
- API rate limit is ~3 requests/sec per integration. Bulk syncs need backoff.
- Database properties have schema-enforced types; setting `type: select` to a value that's not in the option list silently fails on some property variants.
