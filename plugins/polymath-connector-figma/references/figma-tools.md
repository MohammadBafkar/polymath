# Figma MCP tools (reference)

Default server: `@figma/mcp-server` (or any community Figma MCP server with the same tool shape).

Auth: `FIGMA_ACCESS_TOKEN` from `userConfig`. Prefer team-scoped tokens; personal tokens carry the user's full Figma scope.

## Tools exposed (subset)

### Read

- `file.get` — file metadata, last-edited info.
- `file.getNode` — single node (frame, group, component) with children + styles.
- `file.getImage` — render a node to PNG/SVG/PDF. Useful for design QA, not for spec extraction.
- `file.getStyles` — published styles (color, text, effect, grid).
- `components.list` — published components in a team library.
- `comments.list` — file-level comments and threads.

### Write

Figma's REST API is overwhelmingly read-only for design data; published-library mutations require Figma plugins, not API. Most "write" intent is better served by `comments.create` for asynchronous design feedback.

- `comments.create` — leave a comment on a file (optionally pinned to coordinates).

## Token scope

Figma personal access tokens have full account scope. Reduce blast radius by:

- Issuing per-org tokens, not per-user, where the workspace supports it.
- Rotating after each handoff cycle for external collaborators.
- Never embedding tokens in plain text — Polymath stores via `userConfig.sensitive: true`.

## Common pitfalls

- A Figma file URL without `?node-id=` points to the whole file. `file.getNode` requires the node ID; refuse to spec from a file-root URL.
- Detached component instances look identical to attached ones in renders, but their styles/tokens drift. Always check the `componentId` field.
- `file.getImage` produces a rasterized snapshot; do not use it as a spec source — it loses tokens, states, and component metadata.
- Library components don't carry their token names through to a consumer file unless the consumer publishes the library. Resolve tokens through the publishing library, not the consumer file.
