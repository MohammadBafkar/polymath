# MCP reuse — detect and reuse the host agent's MCP servers

**Detection:** [`tools/mcp-registry.py`](../tools/mcp-registry.py) · **Policy config:** `.polymath/project.yaml` `mcp:` (schema: [`registry/schemas/project.schema.json`](../registry/schemas/project.schema.json)) · **Skill entry point:** `polymath-core:mcp-bridge`

## Why this exists

Polymath ships `.mcp.json` per connector plugin — the Claude Code plugin
convention. Other agents (Cursor, Gemini CLI, OpenCode, Codex, VS Code) do not
read plugin `.mcp.json` files, expand different env-var syntaxes, and store
their own MCP config at different paths and scopes. Two failure modes follow:

1. **Duplicate servers.** When a user's host agent already has e.g. a datadog
   MCP registered, polymath's own `.mcp.json` launches a second one —
   duplicate tools, duplicate context, name collisions
   (`plugin:polymath-observability:datadog` vs the user's `datadog`).
2. **Dead exports.** The exported bundle's MCP configs used one syntax
   (Claude Code's `${VAR:-}`); on other hosts they were inert until hand-repaired.

The reuse layer closes both: polymath **detects** MCP servers already
registered in the **current host agent**, **matches** them against connector
providers by identity, and **reuses** the host's server instead of registering
a duplicate. The plugin-shipped `.mcp.json` becomes the fallback, not the
default.

## The host-only invariant

Polymath takes MCPs from **where it has been added** — the agent it is
running inside right now. A server registered in a *different* agent is
**never** a substitute: when polymath runs in Cursor, an OpenCode datadog
server is invisible to it, because those tools are not in the Cursor
session's tool list. Resolution therefore:

1. Detects the current host from **in-session env markers** (each agent sets
   these in its own session and in the child processes it spawns, which
   includes hook scripts):

   | Host | Markers |
   | --- | --- |
   | Claude Code | `CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`, `CLAUDE_SESSION_ID` |
   | Cursor | `CURSOR_AGENT`, `CURSOR_TRACE_ID`, `CURSOR_SESSION_ID` |
   | Gemini CLI | `GEMINI_CLI`, `GEMINI_PROJECT_DIR` |
   | OpenCode | `OPENCODE`, `OPENCODE_PID`, `OPENCODE_CLIENT` |
   | Codex | `CODEX_THREAD_ID`, `CODEX_SANDBOX` |
   | VS Code | `VSCODE_PID`, `VSCODE_CWD`, `VSCODE_GIT_ASKPASS_MAIN` |

2. Scans **only that host's** config locations.
3. When detection fails (no marker — e.g. a plain shell), providers resolve
   to the plugin fallback; nothing is ever reused from another host.

`tools/mcp-registry.py scan --all-hosts` inspects every agent's configs for
diagnostics, and labels the output as not-reusable-here.

## The policy

Set once in `.polymath/project.yaml`:

```yaml
mcp:
  policy: reuse-host            # default — the current host's server wins
  # serverOverrides: { datadog: dd-prod }     # optional pin (or `plugin`)
```

| Value | Behavior |
| --- | --- |
| `reuse-host` (default) | A server registered in the CURRENT host matching the provider's identity wins; the plugin-shipped server stays idle. |
| `prefer-plugin` | The plugin-shipped `.mcp.json` server wins (e.g. for version pinning); the host's servers are the fallback. |

`serverOverrides` pins per provider: a value of `plugin` forces the
plugin-shipped server; any other value is a current-host server name to look
for by exact name (falling back to the plugin when absent).

## How detection works

`tools/mcp-registry.py scan` parses the **current host's** config locations
(host detected from in-session env markers, see the host-only invariant
above) into one normalized inventory (transport, command/args or URL, env
**key names only** — values are redacted, scanned configs frequently hold
literal tokens):

| Host | Project scope | User scope |
| --- | --- | --- |
| Claude Code | `.mcp.json` | `~/.claude.json` (user + per-project local) |
| Cursor | `.cursor/mcp.json` | `~/.cursor/mcp.json` |
| Gemini CLI | `.gemini/settings.json` | `~/.gemini/settings.json` |
| OpenCode | `opencode.json(c)` | `~/.config/opencode/opencode.json(c)` |
| Codex | `.codex/config.toml` (trusted) | `~/.codex/config.toml` |
| VS Code | `.vscode/mcp.json` | — |

Scope precedence is each host's own (Claude Code local > project > user; Cursor
project > global; Gemini system > workspace > user; OpenCode managed > project
> global > remote). The inventory records scope so the availability map can
prefer correctly. Only the current host is scanned; `--all-hosts` is the
explicit cross-host diagnostics view.

## How matching works

Every connector binding (`bindings/<provider>/binding.json`, `kind: mcp`)
declares a provider-identity `mcp` block — the machine-readable contract
(`MCP-BINDING` conformance gate requires it):

```json
"mcp": {
  "serverAliases": ["datadog", "dd"],
  "packages": ["@datadog/mcp-server", "datadog-mcp"],
  "remoteUrls": ["https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"],
  "envKeys": ["DD_API_KEY", "DD_APP_KEY", "DD_SITE"]
}
```

A host-registered server belongs to the provider when it matches by (current
host only):

1. **name** — the server key is one of `serverAliases` (e.g. the user's
   `datadog` server in OpenCode),
2. **url** — its remote endpoint equals one of `remoteUrls` (scheme/host/path
   canonicalized; different path or query = different server), or
3. **package** — its stdio launch args contain one of `packages`
   (e.g. `npx -y @datadog/mcp-server`).

## The session resolution

The polymath-core SessionStart hook runs the scan + match (current host only)
and persists the resolution into `project-context.json` under `mcpResolution`:

```json
{
  "policy": "reuse-host",
  "detectedHost": "opencode",
  "providers": {
    "datadog": {
      "capability": "observability",
      "plugin": "polymath-observability",
      "source": "host",
      "server": "datadog",
      "host": "opencode",
      "scope": "user",
      "matchSignal": "name",
      "toolPrefix": "datadog_"
    }
  }
}
```

Per provider: `source: host` (use the current host's server; `toolPrefix`
names the tool naming), `source: plugin` (the plugin-shipped server backs the
skill), `source: none` (credentials unconfigured — degrade gracefully).
`detectedHost: null` means no agent was detected — everything resolves to the
plugin fallback, never to another host's server. Skills carry a one-line
**MCP binding** preamble pointing at this snapshot, so the agent binds to the
right server instead of registering a duplicate.

## Rendering host-correct configs

When no host server exists and the user wants one, `render` emits
host-correct fragments — wrapper key, env syntax, and command shape per host:

```bash
python3 tools/mcp-registry.py render --plugin polymath-observability --target cursor
```

| Host | Wrapper | Env expansion | Command shape |
| --- | --- | --- | --- |
| Claude Code | `mcpServers` | `${VAR:-default}` | `"command": "npx"`, `"args": [...]` |
| Cursor | `mcpServers` | `${env:VAR}` | same |
| Gemini CLI | `mcpServers` | `${VAR}` | same (+ `httpUrl` for remote) |
| OpenCode | `mcp` (v2: `mcp.servers`) | `{env:VAR}` | `"command": ["npx", ...]`, local/remote types |
| Codex | `[mcp_servers.<n>]` TOML | none — `env_vars` forwards names | `command = "..."` |
| VS Code | `servers` | `${VAR}` | same as Claude Code |

Security invariants: a render never copies a literal secret between hosts —
fragments reference env vars only; `ensure`-style writes always show the
fragment first and respect each host's trust model (Codex trusted projects,
Claude Code project approval). The exporter materializes all host renders
into `dist/agents-skills/_polymath/mcp/<host>/` alongside the canonical
aggregate.

## Tool naming per host

MCP tools are exposed under different prefixes; skills reference them via the
`toolPrefix` from the resolution snapshot rather than hardcoding:

| Host | Tool naming |
| --- | --- |
| Claude Code | `mcp__<server>__<tool>` |
| Cursor / VS Code | server-prefixed (`mcp__<server>__<tool>` shape) |
| Gemini CLI | `mcp_<server>_<tool>` |
| OpenCode | `<server>_<tool>` (v2 code-mode wraps them) |
| Codex | server namespaced per its client |

Avoid `_` in server aliases on Gemini CLI — its policy engine parses the FQN
on the first underscore after `mcp_`.

## Health checks

```bash
python3 tools/mcp-registry.py doctor
```

Reports: cross-scope duplicate server names within a host, placeholder
packages with no host-registered match (the dead-on-install case — reuse is
also the primary working path for the disclosed-placeholder connectors, see
[INTEGRATION-POLICY § 4.2](INTEGRATION-POLICY.md)), and reused servers whose
referenced env vars are unset.

## For connector authors

1. Ship `.mcp.json` as today (Claude Code shape, `${POLYMATH_CONNECTOR_*:-}` env defaults).
2. Declare the provider identity in each `kind: mcp` binding — `serverAliases` (the names the vendor's docs use), `packages` (what the official server launches), `remoteUrls` (hosted endpoint if any), `envKeys` (server-native env names). `MCP-BINDING` fails a binding without at least one match signal.
3. Skills bound to the connector carry the MCP-binding preamble (see any shipped connector skill for the shape).
4. Update the [host matrix](#the-policy) and this doc when a new host or transport lands.
