---
name: mcp-bridge
description: Find MCP servers already registered in the CURRENT host agent and map Polymath connector providers onto them instead of installing duplicates.
---

# mcp-bridge

> Resolve each Polymath connector provider against MCP servers the user's
> CURRENT host agent ALREADY has registered. Reuse wins by default: the
> host's server carries its own auth and tool list, so a polymath duplicate
> is wasted context at best and a name collision at worst. HOST-ONLY: a
> server registered in a DIFFERENT agent is not reusable — its tools are not
> in this session's tool list — so only the current host's configs are
> scanned, detected from in-session env markers.

**Mode:** deterministic — same inputs, same output. Follow the steps and the output shape exactly; compute with the named script or tool, never by estimate; add nothing the shape does not ask for.

## When to use

- Setting up Polymath in a repo where the agent already has e.g. Datadog or Atlassian MCPs registered.
- A connector skill failed with a tool error and the user asks which server backs it.
- The SessionStart hook said "reusing … MCP server(s)" and the user wants the full picture.
- Before registering a polymath connector server into a host config (to avoid a duplicate).
- To inspect what OTHER agents have registered (diagnostics only — `scan --all-hosts`).

## Inputs

- The provider(s) the user cares about (optional, default: every provider the scan or bindings mention).
- This session's own tool list — authoritative; the config scan is advisory.
- `.polymath/project.yaml` `mcp:` policy (optional, default `reuse-host`).

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

The registry CLI ships bundled with this skill at
`${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/mcp-bridge/scripts/mcp-registry`.

`scan` works anywhere. `match`, `render`, and `doctor` read every plugin's
`bindings/<provider>/binding.json` and `mcp/servers.json`, so they only see
providers when run from a Polymath marketplace checkout (`python3 tools/mcp-registry.py …`
at its root). From an installed plugin they report `0/0 provider(s)` — that
means "bindings not visible here", **not** "nothing to reuse". Never present
that line as a resolution.

1. **Check your own tool list first.** It is the authoritative answer: if a
   server for the provider is loaded (possibly under another name — a claude.ai
   connector appears as `mcp__claude_ai_<Name>__*`), it is reusable. The config
   scan below can miss servers the host loads from elsewhere.
2. **Scan the current host's inventory** (redacted — env/header values are never printed):
   ```bash
   python3 "${POLYMATH_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}/skills/mcp-bridge/scripts/mcp-registry" scan            # add --json for machine-readable output
   ```
   The host is detected from in-session env markers; when detection fails nothing is scanned and every provider resolves to `none` (nothing is reused, nothing is auto-registered). `--all-hosts` inspects other agents' configs — diagnostics only, those servers are not reusable in this session.
3. **Reconcile providers against the inventory.** In a marketplace checkout run
   `python3 tools/mcp-registry.py match` — each `kind=mcp` binding is matched by
   server-name alias, npm package, or remote URL against the current host only.
   Elsewhere, match by hand: compare the scan's server names/packages/URLs with
   the provider names the user cares about. Report per provider: **reuse** (host
   server + scope) or **none** (nothing registered here — do not install without asking).
4. **Read the session resolution (advisory).** The SessionStart hook may persist
   `mcpResolution` into the project-context snapshot (located per
   `polymath-core:project-context`). It is built from the same config scan, so
   the tool list from step 1 still wins on disagreement.
5. **If the host has no matching server and the user asks for one**, render a
   host-correct fragment (marketplace checkout:
   `python3 tools/mcp-registry.py render --plugin polymath-observability --target cursor`;
   otherwise point the user at that plugin's `mcp/servers.json` template and the
   vendor's install docs). Fragments reference env vars only — never write a
   secret into a config. Show the fragment, name the file it belongs in
   (`.cursor/mcp.json`, `~/.gemini/settings.json`, `~/.codex/config.toml`, …),
   and let the user apply it.
6. **Health-check** when something looks off (marketplace checkout:
   `python3 tools/mcp-registry.py doctor`): cross-scope duplicate server names,
   placeholder packages without a host match, reused servers with unset env vars.

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
- A `0/0 provider(s)` line from an installed copy is reported as "bindings not visible", never as "no servers to reuse".

## Output

```text
provider                   capability               reuse  host server
datadog                    observability            yes    datadog (opencode/user, matched by name)
jira                       issue_tracker            yes    atlassian-rovo (cursor/user, matched by name)
slack                      incident_comms           no     (nothing registered in this host — do not install without asking)

2/16 mcp-bound provider(s) resolved from host-registered servers.
```
