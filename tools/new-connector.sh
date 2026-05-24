#!/usr/bin/env bash
# Scaffold a new polymath-connector-<service> plugin.
#
# Usage: tools/new-connector.sh <service> [description]
#   service is the bare name, e.g. "slack" → polymath-connector-slack.
#
# Generates plugin.json (with userConfig.apiKey), .mcp.json (stub),
# hooks/ directory, references/<service>-tools.md template, plus README
# and CHANGELOG.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <service> [description]" >&2
  exit 1
fi

service="$1"
description="${2:-${service^} connector — MCP server + event-driven hooks + skills.}"

if [[ "$service" == polymath-connector-* ]]; then
  name="$service"
  service="${service#polymath-connector-}"
elif [[ "$service" == polymath-* ]]; then
  echo "error: service must not start with 'polymath-' (will be prefixed automatically)" >&2
  exit 1
else
  name="polymath-connector-$service"
fi

root="$(cd "$(dirname "$0")/.." && pwd)"
plugin_dir="$root/plugins/$name"

if [[ -d "$plugin_dir" ]]; then
  echo "error: $plugin_dir already exists" >&2
  exit 1
fi

upper_service="$(echo "$service" | tr '[:lower:]' '[:upper:]' | tr '-' '_')"
config_envvar="POLYMATH_CONNECTOR_${upper_service}_APIKEY"

mkdir -p "$plugin_dir/.claude-plugin" "$plugin_dir/hooks/scripts" "$plugin_dir/skills" "$plugin_dir/references"

cat > "$plugin_dir/.claude-plugin/plugin.json" <<JSON
{
  "name": "$name",
  "version": "0.1.0",
  "description": "$description",
  "license": "Apache-2.0",
  "dependencies": ["polymath-core"],
  "keywords": ["connector", "$service", "mcp"],
  "userConfig": {
    "apiKey": {
      "type": "string",
      "title": "$service API key",
      "description": "Credential for the $service API. Use a service-account key where possible.",
      "sensitive": true,
      "required": true
    }
  }
}
JSON

cat > "$plugin_dir/.mcp.json" <<JSON
{
  "mcpServers": {
    "$service": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@vendor/$service-mcp-server"],
      "env": {
        "${upper_service}_API_KEY": "\${${config_envvar}}"
      }
    }
  }
}
JSON

cat > "$plugin_dir/hooks/hooks.json" <<JSON
{
  "hooks": {}
}
JSON

cat > "$plugin_dir/references/$service-tools.md" <<MD
# $service MCP tools (reference)

Default server: \`@vendor/$service-mcp-server\` (replace with the actual server).

Auth: \`${upper_service}_API_KEY\` from \`userConfig.apiKey\`.

## Tools exposed

- TODO — list the tools the MCP exposes once a concrete server is chosen.

## Token scope

- Use a service-account credential, not a user's personal key.
- Rotate regularly via \`claude plugin install --config apiKey=<new>\`.

## Anti-patterns

- TODO — service-specific footguns to call out.
MD

cat > "$plugin_dir/README.md" <<MD
# $name

$description

## What it ships

- MCP server (TODO: confirm canonical server).
- Skills: TODO.
- Hooks: TODO.
- Reference: [\`references/$service-tools.md\`](references/$service-tools.md).

## Installation

\`\`\`bash
claude plugin install $name@polymath --config apiKey=<value>
\`\`\`

## Dependencies

- \`polymath-core\`

## License

Apache-2.0.
MD

cat > "$plugin_dir/CHANGELOG.md" <<MD
# Changelog — $name

## [Unreleased]

### Added

- Initial scaffold via \`tools/new-connector.sh\`. Replace stub \`.mcp.json\`, add skills, and verify with \`polymath-author:validate-plugin\`.
MD

echo "Scaffolded $plugin_dir"
echo "Next steps:"
echo "  1. Replace .mcp.json command+args with the real upstream MCP server"
echo "  2. Add userConfig fields if more than apiKey is needed (jiraUrl, datadogSite, ...)"
echo "  3. Add at least one hook script + one skill"
echo "  4. Fill references/$service-tools.md with actual tool list"
echo "  5. Register in .claude-plugin/marketplace.json"
echo "  6. Run polymath-author:validate-plugin"
