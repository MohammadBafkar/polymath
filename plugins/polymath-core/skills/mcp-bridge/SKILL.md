---
name: mcp-bridge
description: Detect MCP servers already registered in the CURRENT host agent (Claude Code, Cursor, Gemini CLI, OpenCode, Codex, VS Code) and reuse them for Polymath connectors instead of installing duplicates.
---

# mcp-bridge

> Resolve each Polymath connector provider against MCP servers the user's
> CURRENT host agent ALREADY has registered. Reuse wins by default: the
> host's server carries its own auth and tool list, so a polymath duplicate
> is wasted context at best and a name collision at worst. HOST-ONLY: a
> server registered in a DIFFERENT agent is not reusable — its tools are not
> in this session's tool list — so only the current host's configs are
> scanned, detected from in-session env markers.

## When to use

- Setting up Polymath in a repo where the agent already has e.g. Datadog or Atlassian MCPs registered.
- A connector skill failed with a tool error and the user asks which server backs it.
- The SessionStart hook said "reusing … MCP server(s)" and the user wants the full picture.
- Before registering a polymath connector server into a host config (to avoid a duplicate).
- To inspect what OTHER agents have registered (diagnostics only — `scan --all-hosts`).

## Resolution policy

Set in `.polymath/project.yaml` (see docs/MCP-REUSE.md):

```yaml
mcp:
  policy: reuse-host          # default — the current host's server wins
  # serverOverrides: { datadog: dd-prod }   # optional pin (or `plugin`)
```

- `reuse-host` (default): a server registered in the CURRENT host matching the provider's identity wins; plugins never auto-register anything — with no match the provider resolves to `none`.
- `prefer-plugin`: the provider's `mcp/servers.json` template names the intended server (e.g. for version pinning); the host's copy is only usable once registered under that name.
- A `serverOverrides` value of `plugin` pins the template's server name; any other value pins a current-host server by exact name. A pin that matches nothing resolves to `none` with a note — never a silent fallback.

## Procedure

1. **Scan the current host's inventory** (redacted — env/header values are never printed):
   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT}/skills/mcp-bridge/scripts/mcp-registry scan"
   ```
   (From inside the marketplace repo: `python3 tools/mcp-registry.py scan`.)
   The host is detected from in-session env markers; when detection fails nothing is scanned and every provider resolves to `none` (nothing is reused, nothing is auto-registered). Add `--all-hosts` to inspect other agents' configs — diagnostics only, those servers are not reusable in this session. Add `--json` for machine-readable output.
2. **Reconcile providers against the inventory**:
   ```bash
   python3 tools/mcp-registry.py match
   ```
   Each `kind=mcp` binding (the provider identity lives in `bindings/<provider>/binding.json` `mcp` block) is matched by server-name alias, npm package, or remote URL endpoint — against the current host only. Report per provider: **reuse** (name the host server + scope) or **none** (nothing registered here — do not install without asking).
3. **Read the session resolution (advisory)** — the SessionStart hook may persist it to
   `${POLYMATH_PLUGIN_DATA}/polymath-core/project-context.json` under `mcpResolution`.
   The scan reads host config files only, so it can miss servers the host loads
   from elsewhere (claude.ai connectors, extension-supplied servers). Connector
   skills therefore treat **the session's own tool list as authoritative**: if the
   host has a server for the provider, use its tools; if not, work without MCP
   and ask before helping install the vendor's server (the plugin template renders
   a host-correct fragment). Plugins never auto-register MCP servers.
4. **If the host has no matching server and the user asks for one**, render a
   host-correct fragment (correct wrapper key, env syntax, command shape):
   ```bash
   python3 tools/mcp-registry.py render --plugin polymath-observability --target cursor
   ```
   Fragments reference env vars only — never write a secret into a config. Show the fragment, name the file it belongs in (`.cursor/mcp.json`, `~/.gemini/settings.json`, `~/.codex/config.toml`, …), and let the user apply it.
5. **Health-check** when something looks off:
   ```bash
   python3 tools/mcp-registry.py doctor
   ```
   Reports cross-scope duplicate server names, placeholder packages without a host match, and reused servers with unset env vars.

## Host config locations

| Host | Project scope | User scope |
| --- | --- | --- |
| Claude Code | `.mcp.json` | `~/.claude.json` (user + per-project local) |
| Cursor | `.cursor/mcp.json` | `~/.cursor/mcp.json` |
| Gemini CLI | `.gemini/settings.json` | `~/.gemini/settings.json` |
| OpenCode | `opencode.json(c)` | `~/.config/opencode/opencode.json(c)` |
| Codex | `.codex/config.toml` (trusted) | `~/.codex/config.toml` |
| VS Code | `.vscode/mcp.json` | — |

## Quality bar

- Never print or copy env/header values — key names only, always.
- Never write into a host config without showing the fragment first.
- Only the CURRENT host's servers are reusable; never map a provider onto a server registered in a different agent.
- Prefer reuse; never register or launch a polymath copy unprompted — the plugin template exists for the opt-in install path only.

## Output

```text
provider                   capability               reuse  host server
datadog                    observability            yes    datadog (opencode/user, matched by name)
jira                       issue_tracker            yes    atlassian-rovo (cursor/user, matched by name)
slack                      incident_comms           no     (nothing registered in this host — do not install without asking)

2/16 mcp-bound provider(s) resolved from host-registered servers.
```

