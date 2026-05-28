---
name: new-plugin
description: Scaffold a new Polymath plugin via the bundled new-plugin.sh.
---

# /new-plugin

Scaffold a new plugin via `${CLAUDE_PLUGIN_ROOT}/bin/new-plugin.sh <name>`. Pass the bare name (the script prepends `polymath-`). The vendored scaffolder walks up from the cwd to find the caller's marketplace root, so it works inside any project where `polymath-author` is installed.

After scaffolding, register the plugin in `.claude-plugin/marketplace.json` and run `polymath-author:validate-plugin`.
