# Slack MCP tools (reference)

Default server: `@modelcontextprotocol/server-slack`. Swap `command`+`args` for any community Slack MCP server with the same tool shape.

Auth: `SLACK_BOT_TOKEN` (xoxb-…) from `userConfig.slackBotToken`. The MCP server can also accept `SLACK_TEAM_ID` to scope queries to one workspace; leave blank to use the bot's default workspace.

## Tools exposed (subset; verify against your installed server version)

### Read

- `conversations_list` — list public + private channels the bot has access to.
- `conversations_history` — read messages in a channel/thread.
- `conversations_replies` — read a thread.
- `users_list` / `users_info` — resolve user IDs to names.

### Write

- `chat_postMessage` — post a new message. Required: `channel` (ID, not name). Optional: `thread_ts`, `text` (fallback), `blocks` (rich).
- `chat_update` — edit a message (within the edit window).
- `reactions_add` — emoji reaction (useful for "ack" patterns).
- `files_uploadV2` — attach files / snippets.

## Bot scopes (Slack OAuth)

For the skills in this plugin, the bot needs:

- `chat:write` — required, for posting.
- `chat:write.public` — to post into channels the bot hasn't been invited to (rarely; prefer invitation).
- `channels:read`, `groups:read`, `im:read`, `mpim:read` — to list and resolve channels.
- `users:read` — to resolve `@mentions` to user IDs.
- `reactions:write` — for ack patterns.

Avoid: `admin:*`, `users:read.email`, `files:write` unless the workflow genuinely needs them.

## Common pitfalls

- Some Slack tools require channel **ID** (`C0XXXXXX`), not name. Resolve via `conversations_list` first and cache.
- Threading requires the **parent's `ts`**, not a permalink. Save the root `ts` as a step artifact.
- Rate limits: Tier-2 (`chat_postMessage`) allows ~20 req/min per workspace. Don't bulk-post.
- The `text` field is what shows in mobile push notifications and screen readers. Don't put PII there.
