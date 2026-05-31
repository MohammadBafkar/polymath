---
name: new-command
description: Scaffold a thin /slash-command alias file inside an existing plugin via new-command.sh. Not a capability or workflow.
---

# /new-command

Scaffold a new command via `${CLAUDE_PLUGIN_ROOT}/bin/new-command.sh <plugin-bare-name> <command-name>`. Produces a ≤ 20-LOC thin-alias markdown file at `plugins/polymath-<plugin>/commands/<command>.md`. Use this when the command should be a one-liner pointing at a skill or a bundled script; promote to a skill when the procedure grows past 20 lines.
