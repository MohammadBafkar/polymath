# Portability — using Polymath skills outside Claude Code

Polymath's [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json)
declares conformance with the
[agentskills.io v1.0](https://agentskills.io) open standard for the
`SKILL.md` format. This page documents the practical export path and,
just as importantly, **what does not port**.

## TL;DR

Skills port. Everything else (commands, hooks, MCP config, workflows,
agents, artifact JSON schemas) is Claude-Code-specific and does
**not** port via the SKILL.md standard.

A subset of skills *reference* a Claude-only surface in their body — a
connector's MCP server, the SessionStart project-context snapshot, or the
polymath-flows runner. The file still copies, but those steps cannot run on a
generic host, so the exporter marks each skill `portable` or `claude-coupled`
in `manifest.json` and prepends a one-line portability banner to every
`claude-coupled` SKILL.md. The export fails closed (`tools/export-agents-skills.py`
returns non-zero) if a coupled skill is missing its banner or any cross-skill /
`../` link did not get rewritten to the flat bundle layout.

```bash
# From a Polymath checkout:
python3 tools/export-agents-skills.py --clean
# → dist/agents-skills/<plugin>-<skill>/SKILL.md
# → dist/agents-skills/manifest.json
```

Drop the contents of `dist/agents-skills/` into whichever well-known
directory your harness reads from (table below). Run the harness; it
will pick up the skills.

## What ports vs. what doesn't

| Surface | Ports to other agents? | Why |
| --- | --- | --- |
| `skills/<slug>/SKILL.md` | **Yes** | agentskills.io v1.0 standard. |
| `skills/<slug>/references/` | **Yes** | Copied alongside the SKILL.md. |
| `skills/<slug>/scripts/` | **Yes** | Copied alongside; activation depends on harness. |
| Plugin `templates/<file>` | **Yes**, on-demand | Copied when a skill body links them via `../../templates/`. Links are rewritten to `templates/<file>` relative to the exported skill. |
| `commands/<slug>.md` | No | Slash commands are a Claude Code surface. Each target harness has its own syntax (Cursor uses `.cursor/rules/*.mdc`, Codex uses its own slash registry). |
| `agents/<role>.md` | No | Subagents are Claude Code's forked-context mechanism. |
| `hooks/hooks.json` | No | Event-driven gates are Claude-Code-only. |
| `.mcp.json` | No | The Model Context Protocol server *can* be used by other clients, but the `.mcp.json` discovery layout is Claude-Code-specific. Configure the MCP server directly in your client (Codex: `codex mcp add`; Cursor: `mcp.json`). |
| `workflows/*.yaml` | No | The polymath-flows runner is a Polymath executable. |
| `bin/<exe>` | No | Plugin-shipped binaries are Claude Code's plugin surface. |
| `shared/schemas/artifacts/*.json` | No | Polymath's artifact validation tooling is not portable; the schemas themselves are public and can be reused by any JSON-schema validator. |
| `.polymath/project.yaml` | No | Loaded by polymath-core's SessionStart hook into a snapshot at `${CLAUDE_PLUGIN_DATA}/polymath-core/project-context.json`. Other harnesses have their own per-project conventions. |

## Target harnesses

Confirmed clients of the agentskills.io v1.0 standard as of May 2026
(per [agentskills.io](https://agentskills.io)). Each lists its own
discovery paths in its docs; the column below names the path that
back-compat-reads SKILL.md unchanged.

| Harness | Discovery path | Source |
| --- | --- | --- |
| **Claude Code** (local) | `~/.claude/skills/` or `<repo>/.claude/skills/` | [code.claude.com/docs](https://code.claude.com/docs/en/skills) |
| **Codex CLI** | `<repo>/.agents/skills/` or `<repo>/.codex/skills/` or `~/.agents/skills/` | [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills/) |
| **Cursor** | `<repo>/.cursor/skills/`, `<repo>/.agents/skills/`, or back-compat `<repo>/.claude/skills/` and `<repo>/.codex/skills/` | [cursor.com/docs/skills](https://cursor.com/docs/skills) |
| **GitHub Copilot / VS Code** | `<repo>/.github/skills/`, `<repo>/.claude/skills/`, or `<repo>/.agents/skills/`; user-level at `~/.copilot/skills/` | [docs.github.com/copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| **Gemini CLI** | `<repo>/.agents/skills/` (verify against current docs) | [agentskills.io clients](https://agentskills.io) |
| **Goose / OpenCode / Roo Code / Amp / JetBrains Junie / others** | See vendor docs from the [agentskills.io clients page](https://agentskills.io). |

The lowest-common-denominator drop point is `.agents/skills/` — every
harness on the list above reads from it.

## Concrete steps

### 1. Generate the bundle

```bash
python3 tools/export-agents-skills.py --clean
```

This writes `dist/agents-skills/` with one directory per skill. Each
directory's `SKILL.md` has its frontmatter `name:` rewritten to
`<plugin>-<skill>` so two plugins shipping a skill with the same slug
(today: `file-bug-from-incident` in `polymath-connector-jira` and
`-linear`) don't collide.

### 2. Drop into your target harness

Pick the right destination directory from the table above. For most
harnesses:

```bash
# Codex CLI / Cursor / Copilot project-scoped
mkdir -p .agents
cp -R /path/to/polymath/dist/agents-skills .agents/skills

# Cursor user-scoped, alternative drop
mkdir -p .cursor
cp -R /path/to/polymath/dist/agents-skills .cursor/skills
```

The `manifest.json` in the bundle lets you recover the source mapping
(namespaced name → `<plugin>:<skill>`) if you need to cite or update
a specific skill.

### 3. Verify activation

Start your target harness and prompt with one of the trigger phrases
from `tests/skill-triggering/`. The host should select the matching
namespaced skill. If activation does not happen, check the harness's
own SKILL.md discovery logs — frontmatter parsing differs by vendor.

## What this does NOT do

- **No live test against every listed harness.** As of the most recent
  Polymath bakeoff run, only Claude Code is exercised against the full
  skill set. Other harnesses are presumed-compatible by virtue of the
  agentskills.io v1.0 contract; cross-vendor parity is *unverified*
  and contributions are welcome.
- **No automated re-import.** The exported `<plugin>-<skill>` slugs do
  not feed back into Polymath's bakeoff or skill-triggering tests; the
  tests still use the in-tree `polymath-<plugin>:<skill>` invocation
  form.
- **No vendor-specific frontmatter extensions.** Some harnesses (e.g.
  VS Code) document optional fields (`argument-hint`,
  `user-invocable`, `context: fork`). Polymath does not emit these
  today. If a target harness requires them, add a vendor-specific
  post-export rewrite step in your own toolchain.

## Open questions

- **Continue.dev / Aider** are not listed on agentskills.io's clients
  page as of May 2026. Exported skills may still be usable as plain
  Markdown context, but discovery semantics are vendor-specific.
- **Frontmatter `name` length**: agentskills.io v1.0 does not document
  a hard upper bound. Polymath's longest namespaced name today is
  ~50 characters; if a target harness imposes a stricter limit,
  shorten via a custom post-export step.
- **Description budget**: vendors report different SKILL.md discovery
  budgets (Codex ~8K characters). Polymath's per-skill description is
  ≤ 200 characters by `tools/lint-skills.sh`, well below any
  documented budget.
