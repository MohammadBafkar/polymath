#!/usr/bin/env bash
# Scaffold a new command (thin alias) inside a Polymath plugin.
#
# Usage: tools/new-command.sh <plugin-name> <command-name> [description]
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <plugin-name> <command-name> [description]" >&2
  exit 1
fi

plugin="$1"
cmd="$2"
description="${3:-Replace this description.}"

if [[ "$plugin" != polymath-* ]]; then
  plugin="polymath-$plugin"
fi

root="$(cd "$(dirname "$0")/.." && pwd)"
cmd_file="$root/plugins/$plugin/commands/$cmd.md"

if [[ ! -d "$root/plugins/$plugin" ]]; then
  echo "error: plugin $plugin does not exist" >&2
  exit 1
fi
if [[ -f "$cmd_file" ]]; then
  echo "error: $cmd_file already exists" >&2
  exit 1
fi

mkdir -p "$(dirname "$cmd_file")"

cat > "$cmd_file" <<MD
---
name: $cmd
description: $description
---

# /$cmd

> Replace this with what the command does. Keep ≤ 20 lines if this is an alias.
MD

echo "Scaffolded $cmd_file"
