#!/usr/bin/env bash
# Scaffold a new Polymath plugin directory.
#
# Usage: tools/new-plugin.sh <plugin-name> [description]
#   plugin-name is the bare name, e.g. "qa" or "security". The script prepends "polymath-".
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <plugin-name> [description]" >&2
  exit 1
fi

name="$1"
description="${2:-Replace this description before submitting.}"

if [[ "$name" == polymath-* ]]; then
  full="$name"
else
  full="polymath-$name"
fi

root="$(cd "$(dirname "$0")/.." && pwd)"
plugin_dir="$root/plugins/$full"

if [[ -d "$plugin_dir" ]]; then
  echo "error: $plugin_dir already exists" >&2
  exit 1
fi

mkdir -p "$plugin_dir/.claude-plugin" "$plugin_dir/skills" "$plugin_dir/commands" "$plugin_dir/agents" "$plugin_dir/hooks/scripts" "$plugin_dir/tests"

cat > "$plugin_dir/.claude-plugin/plugin.json" <<JSON
{
  "name": "$full",
  "version": "0.1.0",
  "description": "$description",
  "license": "MIT",
  "metadata": {
    "category": "TODO",
    "tags": []
  }
}
JSON

cat > "$plugin_dir/README.md" <<MD
# $full

$description

## What it ships

- Skills: TODO
- Commands: TODO
- Agents: TODO
- Hooks: TODO

## Installation

\`\`\`bash
claude plugin install $full@polymath
\`\`\`

## Author

See \`docs/PLUGIN-AUTHORING.md\` in the marketplace root for plugin authoring conventions.
MD

cat > "$plugin_dir/CHANGELOG.md" <<MD
# Changelog — $full

## [Unreleased]

### Added

- Initial scaffold.
MD

echo "Scaffolded $plugin_dir"
echo "Next steps:"
echo "  1. Edit $plugin_dir/.claude-plugin/plugin.json"
echo "  2. Add skills/commands/agents under $plugin_dir/"
echo "  3. Register in .claude-plugin/marketplace.json"
