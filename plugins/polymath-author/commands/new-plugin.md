---
name: new-plugin
description: Scaffold a new top-level Polymath plugin (plugin.json, README, CHANGELOG) via new-plugin.sh. Not for adding a skill or command to an existing plugin.
---

# /new-plugin

Scaffold a new plugin via `${CLAUDE_PLUGIN_ROOT}/bin/new-plugin.sh <name>`. Pass the bare name (the script prepends `polymath-`). The vendored scaffolder walks up from the cwd to find the caller's marketplace root, so it works inside any project where `polymath-author` is installed.

After scaffolding, register the plugin in `.claude-plugin/marketplace.json` and run `polymath-author:validate-plugin`.
