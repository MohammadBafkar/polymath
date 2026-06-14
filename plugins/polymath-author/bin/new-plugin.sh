#!/usr/bin/env bash
# Scaffold a new Polymath plugin directory.
#
# Usage: /polymath-author:new-plugin <plugin-name> [description]  (bin/new-plugin.sh)
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

# Locate the *caller's* marketplace root, not this plugin's bin/.
# Walk up from $PWD looking for .claude-plugin/marketplace.json (the
# caller's marketplace). Fall back to $POLYMATH_PROJECT_DIR, then the legacy
# $CLAUDE_PROJECT_DIR, then to $PWD.
find_marketplace_root() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/.claude-plugin/marketplace.json" ]]; then
      printf '%s' "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  if [[ -n "${POLYMATH_PROJECT_DIR:-}" && -f "${POLYMATH_PROJECT_DIR}/.claude-plugin/marketplace.json" ]]; then
    printf '%s' "$POLYMATH_PROJECT_DIR"
    return 0
  fi
  if [[ -n "${CLAUDE_PROJECT_DIR:-}" && -f "${CLAUDE_PROJECT_DIR}/.claude-plugin/marketplace.json" ]]; then
    printf '%s' "$CLAUDE_PROJECT_DIR"
    return 0
  fi
  printf '%s' "$PWD"
}
root="$(find_marketplace_root)"
plugin_dir="$root/plugins/$full"

if [[ -d "$plugin_dir" ]]; then
  echo "error: $plugin_dir already exists" >&2
  exit 1
fi

# Pre-create only the surfaces every plugin has. agents/ and hooks/ are
# "only when justified" (see AGENTS.md) — scaffolding empty
# dirs for them contradicts the skill-only default and leaves cruft. Add them
# via new-skill/new-command or by hand when a plugin actually earns one.
mkdir -p "$plugin_dir/.claude-plugin" "$plugin_dir/skills" "$plugin_dir/commands" "$plugin_dir/tests"

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
echo "  2. Add skills/commands under $plugin_dir/ (agents/hooks only when justified)"
echo "  3. Register in ALL THREE of these or conformance fails:"
echo "       - .claude-plugin/marketplace.json   (Claude's catalog)"
echo "       - registry/polymath-catalog.json    (status: experimental|beta|stable — MANIFEST-3)"
echo "       - registry/stability-evidence.json  (evidence ledger entry — STABILITY-1)"
echo "  4. If it ships .mcp.json or bindings/: add a row to docs/INTEGRATION-POLICY.md (INTEGRATION-2)"
echo "  5. Run: tools/conformance.sh plugins/$full"
