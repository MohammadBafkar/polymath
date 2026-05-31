# Polymath frontmatter cheatsheet

The four frontmatter shapes you'll need to author. Keep this side-by-side
while writing.

## 1. plugin.json (every plugin)

```jsonc
{
  "name": "polymath-<bare-name>",
  "version": "0.1.0",
  "description": "<≤ 200 chars; imperative verb first; says what kind of work>",
  "license": "MIT",
  "author": {
    "name": "<your name or team>",
    "url": "https://github.com/<org>/<repo>"
  },
  "dependencies": ["polymath-core"],
  "keywords": ["<tag>", "<tag>"],

  // optional, connector plugins only:
  "userConfig": {
    "<key>": {
      "type": "string",
      "title": "<short label>",
      "description": "<longer help>",
      "sensitive": true,        // for credentials
      "required": true
    }
  }
}
```

`claude plugin validate --strict` enforces:

- `name` matches the parent directory.
- `description` is present.
- `userConfig.<key>.title` is present (added 2026-05; missing title was a real
  connector gotcha that bit early adopters).

## 2. SKILL.md (every skill)

```yaml
---
name: <kebab-case>
description: <≤ 200 chars; imperative verb first; trigger conditions in plain language>
---
```

Body shape: see [`skill-style-guide.md`](skill-style-guide.md).

## 3. commands/<name>.md (thin aliases)

```yaml
---
name: <kebab-case>
description: <≤ 200 chars; what the command does + the skill it aliases>
---

# /<name>

<≤ 20 lines>. Point at the canonical skill. Don't duplicate its procedure.
```

Treat commands as thin aliases. If a command grows beyond 20 lines, promote
it to a skill (move to `skills/<name>/SKILL.md`) and keep the command as the
alias.

## 4. templates/ (plugins that ship artifact templates)

A plugin owns its templates in `plugins/<plugin>/templates/`. Each template
is a Markdown (or YAML) file with `{{placeholder}}` fields that the skill
fills in. Skills reference templates by relative path:

```markdown
1. Read [`PRD.md`](../../templates/PRD.md).
```

The plugin templates have frontmatter that the corresponding artifact schema
(`shared/schemas/artifacts/<Artifact>.schema.json`) validates via the
`artifactValid` `mustPass` check in a workflow.

## 5. hooks/hooks.json (plugins that ship hooks)

```jsonc
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/<script>.sh"
          }
        ]
      }
    ]
  }
}
```

Hook scripts read the tool-input JSON payload from stdin. Exit codes:

- `0` — allow + continue (stdout is shown as context).
- `2` — block; stdout becomes the user-visible reason.

Use `${CLAUDE_PLUGIN_ROOT}` to refer to your plugin's directory at runtime.
Use `${CLAUDE_PLUGIN_DATA}` to write per-plugin state (paused workflows,
queue.json, etc.).

## 6. .mcp.json (connector plugins)

```jsonc
{
  "mcpServers": {
    "<name>": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@vendor/mcp-server"],
      "env": {
        "API_KEY": "${POLYMATH_CONNECTOR_<UPPER>_<USERCONFIGKEY>}"
      }
    }
  }
}
```

`userConfig` values are exposed to the MCP server's `env` via
`${POLYMATH_<UPPER-SNAKE>_<USERCONFIGKEY>}` substitution.
