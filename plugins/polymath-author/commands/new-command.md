---
name: new-command
description: Scaffold a new slash command inside a plugin via the bundled new-command.sh.
---

# /new-command

Scaffold a new command via `${CLAUDE_PLUGIN_ROOT}/bin/new-command.sh <plugin-bare-name> <command-name>`. Produces a ≤ 20-LOC thin-alias markdown file at `plugins/polymath-<plugin>/commands/<command>.md`. Use this when the command should be a one-liner pointing at a skill or a bundled script; promote to a skill when the procedure grows past 20 lines.
