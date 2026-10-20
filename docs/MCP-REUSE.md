# MCP reuse — the host agent's MCP servers are the default

**Detection:** [`tools/mcp-registry.py`](../tools/mcp-registry.py) · **Policy config:** `.polymath/project.yaml` `mcp:` (schema: [`registry/schemas/project.schema.json`](../registry/schemas/project.schema.json)) · **Skill entry point:** `polymath-core:mcp-bridge`

## The model

Polymath does **not** add MCP servers. The host agent — Claude Code, Cursor,
Gemini CLI, OpenCode, Codex, VS Code — owns MCP registration: if a server for
a provider is needed, the user adds it in their host, with their credentials
and their transport. Polymath **detects** what the current host already has
registered, **matches** those servers against connector providers by
identity, and **reuses** them. Connector plugins ship their server
definitions as render **templates** (`mcp/servers.json`), never as an
auto-registered config.

This reverses the earlier design, which shipped a plugin-root `.mcp.json`
per connector (the Claude Code plugin convention). That file was
auto-registered at session start and produced two recurring failures:

1. **Duplicate servers.** When the host agent already had e.g. a datadog
   MCP registered, polymath's own `.mcp.json` launched a second one —
   duplicate tools, duplicate context, name collisions
   (`plugin:polymath-observability:datadog` vs the user's `datadog`).
2. **Dead or degraded servers.** Most of the shipped `npx` packages were
   placeholders that never resolved (the server never started), and the
   rest started without credentials and failed their own auth — neither
   state ever helped.

Consequently there is no plugin `.mcp.json` anywhere in the marketplace: a
Claude Code plugin that ships one gets its servers auto-registered, which is
exactly the default this design forbids. The template keeps the canonical
Claude-Code shape (see below) but is a render input only.

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
3. When detection fails (no marker — e.g. a plain shell), nothing is reused;
   providers resolve to `none`. Nothing is ever reused from another host.

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
| `reuse-host` (default) | A server registered in the CURRENT host matching the provider's identity wins. With no match the provider resolves to `none` — the skill degrades gracefully and asks before installing anything; nothing launches by default. |
| `prefer-plugin` | The provider's `mcp/servers.json` template names the intended server (e.g. for version pinning); the host's copy is only usable once registered under that name. |

`serverOverrides` pins per provider: a value of `plugin` pins the
template's server name; any other value is a current-host server name to
look for by exact name. A pin that matches nothing resolves to `none` with
a note — it never falls back to launching something unasked.

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

Per provider, `source` is one of:

- `host` — use the current host's server; `toolPrefix` names the tool
  naming. This is the normal case (and the result of every explicit pin
  that matched).
- `none` — no matching server in this host. The skill degrades gracefully
  (design guidance without tool calls) and, when tooling is essential,
  asks the user to register the vendor's server — offering to render the
  host-correct fragment from the plugin's template. Nothing launches or is
  installed without the user's go-ahead. A `note` names the pinned server
  when a `serverOverrides` pin did not match (including a `plugin` pin —
  the template's server name is not registered in this host yet).

`detectedHost: null` means no agent was detected — nothing is reused, every
provider resolves to `none`. Skills carry a one-line **MCP binding**
preamble pointing at this snapshot, so the agent binds to a server that
actually exists in this session instead of registering a duplicate.

## Rendering host-correct configs (opt-in install)

When no host server exists and the user asks for one, `render` emits
host-correct fragments — wrapper key, env syntax, and command shape per
host — from the plugin's `mcp/servers.json` template:

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

The exported agentskills bundle materializes all host renders into
`dist/agents-skills/_polymath/mcp/<host>/` alongside the per-plugin
templates — so the opt-in install is a copy, not a translation exercise.

Security invariants: a render never copies a literal secret between hosts —
fragments reference env vars only; `ensure`-style writes always show the
fragment first and respect each host's trust model (Codex trusted projects,
Claude Code project approval).

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

Reports: cross-scope duplicate server names within a host, template packages
with no npm resolution and no host-registered match (the reuse path is the
primary working route for disclosed-placeholder packages, see
[INTEGRATION-POLICY § 4.2](INTEGRATION-POLICY.md)), and reused servers whose
referenced env vars are unset.

## For connector authors

1. Ship the server definition as `mcp/servers.json` (Claude Code shape,
   `${POLYMATH_CONNECTOR_*:-}` env placeholders) — a render template, never
   an auto-registered `.mcp.json`. A plugin `.mcp.json` would be
   auto-registered by Claude Code and defeat the reuse-first model.
2. Declare the provider identity in each `kind: mcp` binding — `serverAliases` (the names the vendor's docs use), `packages` (what the official server launches), `remoteUrls` (hosted endpoint if any), `envKeys` (server-native env names). `MCP-BINDING` fails a binding without at least one match signal.
3. Skills bound to the connector carry the MCP-binding preamble (see any shipped connector skill for the shape).
4. Update the [host matrix](#the-policy) and this doc when a new host or transport lands.
