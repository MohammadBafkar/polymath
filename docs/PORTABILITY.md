# Portability - using Polymath outside Claude Code

Polymath's source tree is still a Claude Code marketplace because Claude Code
defines the plugin manifest shape in `.claude-plugin/`. The portable output is
the generated bundle from `tools/export-agents-skills.py`.

The exporter is evidence-backed by the live tree: it walks every plugin and
materializes skills, commands, subagents, hooks, MCP config, templates, scripts,
and path contracts into `dist/agents-skills/`. The generated `manifest.json`
records the exact counts and source paths for the current checkout.

```bash
python3 tools/export-agents-skills.py --clean
# -> dist/agents-skills/<plugin>-<skill>/SKILL.md
# -> dist/agents-skills/<plugin>-command-<command>/SKILL.md
# -> dist/agents-skills/<plugin>-agent-<agent>/SKILL.md
# -> dist/agents-skills/_polymath/{support,hooks,mcp}/...
# -> dist/agents-skills/_polymath/hooks/run-hook.py   (runnable hook dispatcher)
# -> dist/agents-skills/manifest.json

python3 tools/export-agents-skills.py --check
# temp build + lint + manifest validation + reference-host load, no dist/ writes

python3 tools/export-agents-skills.py --install .agents/skills
# export, copy the bundle into a target host's discovery directory, and
# host-load-verify the deployed copy in place
```

Every run ends with a reference agentskills.io host-load pass: each exported
skill is loaded the way a compliant host would (frontmatter parsed, `name` +
`description` required) and every relative and `_polymath/` reference is
resolved against the bundle on disk. The build fails closed if any skill is
unloadable or any referenced script/template is missing. This is a stand-in for
a live host — it proves the bundle is loadable and self-contained, short of
installing each proprietary agent.

## What Ports

| Surface | Export result | Activation outside Claude Code |
| --- | --- | --- |
| `skills/<slug>/SKILL.md` | Native `SKILL.md`, namespaced as `<plugin>-<skill>` | Automatic on hosts that implement agentskills.io. |
| `skills/<slug>/references/` | Copied beside the exported skill | Available to the skill body. |
| `skills/<slug>/scripts/` | Copied beside the exported skill | Runnable when the host permits local scripts. |
| `commands/<slug>.md` | Converted to `<plugin>-command-<slug>/SKILL.md` | Invoked as a skill. Slash-command syntax is host-specific and is not preserved. |
| `agents/<role>.md` | Converted to `<plugin>-agent-<role>/SKILL.md` | Invoked as a skill. Forked-context execution depends on the target host. |
| `templates/` | All plugin templates copied to `_polymath/support/<plugin>/templates/`; referenced templates are also copied into the skill directory | Usable by instructions and scripts. |
| Plugin `bin/` scripts | Copied to `_polymath/support/<plugin>/bin/` | Runnable by path from exported instructions. |
| Hook scripts | Copied to `_polymath/support/<plugin>/hooks/scripts/` | Runnable by a target-host hook adapter. |
| `hooks/hooks.json` | Normalized to `_polymath/hooks/<plugin>.hooks.json`, plus a runnable `_polymath/hooks/run-hook.py` dispatcher | The host calls `run-hook.py <Event> [matcher]` on its lifecycle events; the dispatcher matches and runs the right commands. Only the event-name mapping is host-specific. |
| `.mcp.json` | Per-plugin files, aggregate `_polymath/mcp/mcp.json` (canonical Claude-Code shape), and per-host renders under `_polymath/mcp/<host>/` (cursor, gemini-cli, opencode, codex, vscode) with each host's wrapper key and env syntax. Prefer reuse first: `tools/mcp-registry.py scan` detects servers already registered in the host agent and `polymath-core:mcp-bridge` maps providers onto them — the plugin-shipped config is the fallback when the host has no matching server. | Client-specific MCP wiring required only when no host server matches. See [`docs/MCP-REUSE.md`](MCP-REUSE.md). |
| `workflows/*.yaml` | Copied with the `polymath-flow` runner under `_polymath/support/polymath-flows/` | Runnable explicitly with the bundled runner. No non-Claude host auto-discovers these workflows today. |

## Portable Paths

Exported instructions use Polymath-owned path variables:

| Purpose | Portable variable | Default |
| --- | --- | --- |
| Plugin support root | `POLYMATH_PLUGIN_ROOT` | `_polymath/support/<plugin>/` in the bundle |
| Mutable data | `POLYMATH_DATA_DIR` | `~/.polymath/data` |
| User/team config | `POLYMATH_CONFIG_DIR` | `~/.polymath` |
| Project root | `POLYMATH_PROJECT_DIR` | `$PWD` |

Runtime scripts prefer `POLYMATH_*` variables and `.polymath/` paths. They keep
`CLAUDE_*` variables and `.claude/` lookup as compatibility fallbacks for
existing Claude Code installs. The exporter lints generated `SKILL.md` files so
Claude-specific path tokens such as `CLAUDE_PLUGIN_ROOT`,
`CLAUDE_PLUGIN_DATA`, `CLAUDE_CONFIG_DIR`, `CLAUDE_PROJECT_DIR`, and
`~/.claude/plugins/data` do not survive in portable instructions.

## Bundle Layout

```text
dist/agents-skills/
  manifest.json
  PORTABILITY.md
  polymath-core-route/SKILL.md
  polymath-core-command-route/SKILL.md
  polymath-thinking-agent-architecture-critic/SKILL.md
  _polymath/
    support/<plugin>/
      templates/
      bin/
      hooks/
    hooks/<plugin>.hooks.json
    mcp/<plugin>.mcp.json
    mcp/mcp.json
```

The top-level directories with `SKILL.md` are the discoverable units. The
`_polymath/` directory is support material for scripts, templates, hook
adapters, MCP client configuration, and provenance.

## Target Harnesses

How each agent consumes the bundle differs. The table records the mechanism and
whether it has been run against the live agent in this repo.

| Harness | Skill discovery | Verified |
| --- | --- | --- |
| Gemini CLI | Native `gemini skills` discovers `~/.agents/skills/` (user) and project `.agents/skills/` (trusted folder). Install with `gemini skills link <path>` / `gemini skills install <src>`. Hooks: `gemini hooks migrate` (from Claude Code). MCP: `gemini mcp add`. | Yes — Gemini CLI 0.41 loaded all 212 exported skills, each `[Enabled]`; `gemini mcp add` accepted the exported stdio MCP shape. |
| Codex CLI | No native skill auto-discovery (no `skills` subcommand). Reference skills from `AGENTS.md`; register integrations with `codex plugin` and `codex mcp`. | Partial — Codex 0.139 confirmed to have `plugin`/`mcp`/`AGENTS.md`, not skill discovery. |
| GitHub Copilot CLI | MCP-based tools (`--add-github-mcp-*`) and custom `--agent`; reads `AGENTS.md`. | Not run. |
| Cursor | `.cursor/rules` and `AGENTS.md`; `.agents/skills/` for agentskills.io-aware versions. | Not run (GUI agent; CLI is the editor launcher). |
| Claude Code | `.claude/skills/` or installed marketplace plugins. | Native. |

The lowest-friction cross-host path is `~/.agents/skills/` (user scope) or
`.agents/skills/` (project scope), which Gemini CLI discovers natively.

```bash
python3 /path/to/polymath/tools/export-agents-skills.py --install ~/.agents/skills
# Gemini then discovers every skill:
gemini skills list        # -> 212 polymath-* skills, Enabled

# or, manually:
python3 tools/export-agents-skills.py --clean
mkdir -p .agents
cp -R /path/to/polymath/dist/agents-skills .agents/skills
```

## Honest Limits

- The exporter validates structure, link rewriting, path rewriting, manifest
  consistency, and a reference-host load of the deployed bundle. The bundle has
  been run against the live Gemini CLI (all 212 skills loaded and `[Enabled]`;
  MCP add accepted). Codex, Copilot, and Cursor have not been live-run end to
  end; for those the table above records the documented consumption mechanism,
  and the reference-host load is a spec-conformant stand-in.
- Hooks ship with a runnable `run-hook.py` dispatcher, so they execute on any
  host that can call a command on a lifecycle event. The remaining host-specific
  step is wiring that host's events (`SessionStart`, `UserPromptSubmit`,
  `PreToolUse`, `PostToolUse`, `Stop`) to invoke the dispatcher — payload shapes
  still differ by host.
- MCP server definitions are exported (canonical aggregate + per-host renders
  under `_polymath/mcp/<host>/` with each host's wrapper key and env syntax).
  Prefer reuse: `tools/mcp-registry.py scan` + `match` detect servers already
  registered in the host agent and map providers onto them before any install.
  Credentials and client registration remain target-host concerns.
- Converted subagents run as ordinary skills unless the target host has an
  equivalent forked-context/subagent feature.
- Claude-coupled skills are still exported, but they carry a banner naming the
  required surface, such as MCP, project-context data, hooks, or
  `polymath-flow`.
